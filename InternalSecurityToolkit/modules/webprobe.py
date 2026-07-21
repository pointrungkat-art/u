"""Web probe — headers, WAF, tech stack, path discovery, JS analysis"""
import subprocess, re, json

def curl(url, method="GET", headers=None, timeout=8, follow=True):
    cmd = ["curl","-sk","--max-time",str(timeout)]
    if follow: cmd.append("-L")
    if method != "GET": cmd += ["-X", method]
    if headers:
        for k,v in headers.items(): cmd += ["-H",f"{k}: {v}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        return r.stdout
    except: return ""

def curl_headers(url, timeout=8):
    cmd = ["curl","-skI","--max-time",str(timeout),url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        return r.stdout
    except: return ""

SECURITY_HEADERS = [
    "strict-transport-security","content-security-policy","x-frame-options",
    "x-content-type-options","referrer-policy","permissions-policy",
    "cross-origin-opener-policy","cross-origin-embedder-policy"
]

WAF_SIGS = {
    "cloudflare": ["cf-ray","cloudflare"],
    "aws-waf": ["awswaf","x-amzn-requestid"],
    "f5": ["bigip","f5","ts="],
    "akamai": ["akamai","x-akamai"],
    "sucuri": ["sucuri","x-sucuri"],
    "imperva": ["imperva","incapsula","visid_incap"],
}

TECH_SIGS = {
    "WordPress": ["wp-content","wp-json","wordpress"],
    "Laravel": ["laravel_session","x-powered-by: php","_token"],
    "Django": ["csrfmiddlewaretoken","django"],
    "Rails": ["x-powered-by: phusion passenger","_rails"],
    "React": ["__react","_react","reactroot"],
    "Vue": ["__vue","v-app","nuxt"],
    "Nuxt": ["nuxt","__nuxt"],
    "Next.js": ["__next","_next/static"],
    "Express": ["x-powered-by: express"],
    "Spring": ["jsessionid","x-application-context"],
    "PHP": ["x-powered-by: php", ".php"],
    "ASP.NET": ["__viewstate","asp.net","x-aspnet"],
    "PocketBase": ["pocketbase"],
}

PATHS = [
    "/.env","/.git/HEAD","/.git/config","/config.php","/config.json",
    "/config.yaml","/config.yml","/db.sql","/backup.zip","/backup.tar.gz",
    "/phpinfo.php","/info.php","/test.php","/debug","/debug.php",
    "/swagger.json","/openapi.json","/api-docs","/swagger-ui.html",
    "/graphql","/graphiql","/__graphql","/api/graphql",
    "/admin","/admin/","/wp-admin","/wp-login.php","/phpmyadmin",
    "/server-status","/server-info","/_/","/_admin",
    "/actuator","/actuator/health","/actuator/env","/actuator/beans",
    "/metrics","/health","/status","/ping",
    "/robots.txt","/sitemap.xml","/crossdomain.xml",
]

def run(target, full=False):
    base = re.sub(r'/$','',target)
    findings = []

    # Base request
    hdrs_raw = curl_headers(base)
    body = curl(base)
    hdrs_lower = hdrs_raw.lower()

    # Security headers
    for h in SECURITY_HEADERS:
        if h not in hdrs_lower:
            findings.append({"type":"missing_header","value":h,"severity":"LOW",
                             "note":f"Missing {h}"})

    # WAF detection
    waf_found = []
    for waf, sigs in WAF_SIGS.items():
        if any(s in hdrs_lower for s in sigs):
            waf_found.append(waf)
    if waf_found:
        findings.append({"type":"waf","value":", ".join(waf_found),"severity":"INFO"})

    # Tech stack
    combined = (hdrs_raw + body).lower()
    for tech, sigs in TECH_SIGS.items():
        if any(s.lower() in combined for s in sigs):
            findings.append({"type":"tech","value":tech,"severity":"INFO"})

    # X-Powered-By
    m = re.search(r'x-powered-by:\s*(.+)', hdrs_lower)
    if m:
        findings.append({"type":"info_disclosure","value":f"X-Powered-By: {m.group(1).strip()}","severity":"LOW"})

    # Server header
    m = re.search(r'\nserver:\s*(.+)', hdrs_lower)
    if m:
        findings.append({"type":"info_disclosure","value":f"Server: {m.group(1).strip()}","severity":"LOW"})

    # Path probe
    for path in PATHS:
        url = base + path
        cmd = ["curl","-sk","-o","/dev/null","-w","%{http_code}","--max-time","5",url]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=7)
            code = int(r.stdout.strip())
            if code in (200, 301, 302, 403):
                severity = "HIGH" if path in ["/.env","/.git/HEAD","/.git/config","/phpinfo.php",
                                               "/actuator/env","/swagger.json","/openapi.json"] else "MEDIUM" if code == 200 else "INFO"
                findings.append({"type":"path_found","value":path,"status":code,"severity":severity})
        except: pass

    # JS analysis — extract API endpoints
    js_urls = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', body)
    api_endpoints = []
    for js_url in js_urls[:5]:
        if not js_url.startswith("http"): js_url = base + js_url
        js_content = curl(js_url, timeout=10)
        eps = re.findall(r'"(/(?:api|v[0-9]|auth|user|admin|order|cart)[^"]{0,80})"', js_content)
        api_endpoints.extend(eps)
        keys = re.findall(r'(?:xnd_public|pk_live|sk_live|AIza)[A-Za-z0-9_\-]{20,}', js_content)
        for k in keys:
            findings.append({"type":"exposed_key","value":k[:60],"severity":"MEDIUM","note":"API key in JS bundle"})

    if api_endpoints:
        findings.append({"type":"api_endpoints","value":list(dict.fromkeys(api_endpoints))[:30],"severity":"INFO"})

    return {"module":"webprobe","target":base,"waf":waf_found,"findings":findings}
