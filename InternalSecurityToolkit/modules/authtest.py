"""Auth tester — token analysis, session flags, login probe"""
import subprocess, re, json, base64, time

def curl(url, method="GET", data=None, headers=None, cookies=None, timeout=8):
    cmd = ["curl","-sk","--max-time",str(timeout),"-L"]
    if method != "GET": cmd += ["-X", method]
    if data: cmd += ["-d", json.dumps(data), "-H", "Content-Type: application/json"]
    if headers:
        for k,v in headers.items(): cmd += ["-H",f"{k}: {v}"]
    if cookies: cmd += ["-H", f"Cookie: {cookies}"]
    cmd += ["-w","\n__STATUS__%{http_code}",url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        parts = r.stdout.rsplit("__STATUS__",1)
        body = parts[0]
        code = int(parts[1]) if len(parts)>1 else 0
        return body, code
    except: return "", 0

def decode_jwt(token):
    parts = token.split(".")
    if len(parts) != 3: return None
    try:
        pad = lambda s: s + "=" * (-len(s) % 4)
        header = json.loads(base64.urlsafe_b64decode(pad(parts[0])))
        payload = json.loads(base64.urlsafe_b64decode(pad(parts[1])))
        return header, payload
    except: return None

def test_jwt_none(token):
    parts = token.split(".")
    if len(parts) != 3: return None
    try:
        pad = lambda s: s + "=" * (-len(s) % 4)
        payload = json.loads(base64.urlsafe_b64decode(pad(parts[1])))
        # forge header alg:none
        h = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b"=").decode()
        p = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
        return f"{h}.{p}."
    except: return None

def cookie_flags(cookie_header):
    issues = []
    cl = cookie_header.lower()
    if "httponly" not in cl: issues.append("Missing HttpOnly")
    if "secure" not in cl: issues.append("Missing Secure flag")
    if "samesite" not in cl: issues.append("Missing SameSite")
    return issues

def run(target, full=False):
    base = re.sub(r'/$','',target)
    findings = []

    # Cookie flags
    cmd = ["curl","-skI","--max-time","8",base]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        cookies = re.findall(r'(?i)set-cookie:\s*(.+)', r.stdout)
        for ck in cookies:
            issues = cookie_flags(ck)
            for issue in issues:
                findings.append({"type":"cookie_flag","value":issue,"severity":"MEDIUM","cookie":ck[:80]})
    except: pass

    # Common login endpoints
    login_eps = ["/login","/auth/login","/api/login","/api/auth/login",
                 "/user/login","/api/v1/login","/signin","/api/signin"]
    for ep in login_eps:
        _, code = curl(base+ep)
        if code in (200,405):
            findings.append({"type":"login_endpoint","value":ep,"status":code,"severity":"INFO"})

    # Default credentials test (jika ada login endpoint)
    default_creds = [
        ("admin","admin"),("admin","password"),("admin","123456"),
        ("root","root"),("test","test"),("admin","admin123"),
        ("administrator","administrator"),("user","user"),
    ]
    login_found = next((f["value"] for f in findings if f["type"]=="login_endpoint"),None)
    if login_found:
        for user, pwd in default_creds[:5]:
            body, code = curl(base+login_found, method="POST",
                              data={"username":user,"password":pwd,"email":f"{user}@test.com"})
            if code == 200 and any(k in body.lower() for k in ["token","dashboard","success","welcome"]):
                findings.append({"type":"default_creds","value":f"{user}:{pwd}",
                                 "severity":"CRITICAL","note":"Login berhasil dengan default credentials"})
            time.sleep(0.3)

    # Rate limit check
    if login_found:
        codes = []
        for _ in range(10):
            _, code = curl(base+login_found, method="POST",
                           data={"username":"test","password":"test"})
            codes.append(code)
        if all(c in (200,401,403) for c in codes) and 429 not in codes:
            findings.append({"type":"no_rate_limit","value":login_found,
                             "severity":"MEDIUM","note":"No rate limiting on login endpoint"})

    return {"module":"authtest","target":base,"findings":findings}
