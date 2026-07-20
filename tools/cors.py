#!/usr/bin/env python3
"""XC CORS — CORS Misconfiguration Tester"""

import sys, ssl, time, argparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{C}
╔═╗╔═╗╦═╗╔═╗
║  ║ ║╠╦╝╚═╗
╚═╝╚═╝╩╚═╚═╝{RST}
{DIM}CORS Misconfiguration Tester — XC Hub{RST}
"""

ORIGINS_TO_TEST = [
    ('null origin',                 'null'),
    ('attacker.com',                'https://attacker.com'),
    ('evil.com',                    'https://evil.com'),
    ('prefix match',                'https://targetprefixattacker.com'),
    ('suffix match',                'https://attackertarget.com'),
    ('subdomain wildcard',          'https://evil.target.com'),
    ('HTTP downgrade',              'http://target.com'),
    ('localhost',                   'http://localhost'),
    ('localhost:8080',              'http://localhost:8080'),
    ('127.0.0.1',                   'http://127.0.0.1'),
    ('unicode bypass',              'https://target。com'),
    ('dot bypass',                  'https://target.com.evil.com'),
    ('trusted prefix + evil suffix','https://target.com.attacker.com'),
    ('XSS chain (data:)',           'data://target.com'),
    ('file:// origin',              'file://target.com'),
    ('blank + path',                'https://target.com/../evil'),
]

ENDPOINTS_TO_CHECK = [
    '/', '/api', '/api/v1', '/api/v2', '/api/user', '/api/users',
    '/api/profile', '/api/me', '/api/data', '/graphql',
    '/auth', '/login', '/oauth', '/token',
]

CRIT_MSGS = {
    'reflect+creds': f"{R}CRITICAL{RST} — Origin reflected + Credentials: true → full account takeover risk",
    'reflect':       f"{Y}HIGH{RST} — Origin reflected in ACAO without credentials check",
    'wildcard':      f"{Y}MEDIUM{RST} — Wildcard (*) with no credentials",
    'wildcard+creds':f"{R}CRITICAL{RST} — Wildcard (*) + Allow-Credentials (misconfigured browser behaviour varies)",
    'null+creds':    f"{R}CRITICAL{RST} — null origin + Credentials: true → sandboxed iframe exploit",
}

def fetch(url, origin, timeout=8):
    h = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Origin': origin,
        'Accept': '*/*',
    }
    req = Request(url, headers=h)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, dict(r.headers)
    except HTTPError as e:
        return e.code, dict(e.headers)
    except Exception as e:
        return None, {}

def fetch_preflight(url, origin, method='GET', timeout=8):
    h = {
        'User-Agent': 'Mozilla/5.0',
        'Origin': origin,
        'Access-Control-Request-Method': method,
        'Access-Control-Request-Headers': 'Content-Type, Authorization',
    }
    req = Request(url, method='OPTIONS', headers=h)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, dict(r.headers)
    except HTTPError as e:
        return e.code, dict(e.headers)
    except Exception as e:
        return None, {}

def analyze(origin, status, hdrs, label=''):
    acao = hdrs.get('Access-Control-Allow-Origin', hdrs.get('access-control-allow-origin', ''))
    acac = hdrs.get('Access-Control-Allow-Credentials', hdrs.get('access-control-allow-credentials', '')).lower()
    acam = hdrs.get('Access-Control-Allow-Methods', hdrs.get('access-control-allow-methods', ''))
    acah = hdrs.get('Access-Control-Allow-Headers', hdrs.get('access-control-allow-headers', ''))

    if not acao:
        return None

    creds = acac == 'true'
    reflected = acao == origin
    wildcard = acao == '*'
    null_origin = origin == 'null' and acao == 'null'

    finding = None
    if (reflected or null_origin) and creds:
        finding = 'reflect+creds' if not null_origin else 'null+creds'
    elif reflected:
        finding = 'reflect'
    elif wildcard and creds:
        finding = 'wildcard+creds'
    elif wildcard:
        finding = 'wildcard'

    return {'acao': acao, 'creds': creds, 'finding': finding, 'methods': acam}

def test_endpoint(base_url, path='/'):
    url = base_url.rstrip('/') + path
    print(f"\n{BOLD}Endpoint: {W}{path}{RST}")
    findings = []
    for label, origin in ORIGINS_TO_TEST:
        status, hdrs = fetch(url, origin)
        result = analyze(origin, status, hdrs, label)
        if result and result['finding']:
            severity = result['finding']
            msg = CRIT_MSGS.get(severity, '')
            print(f"  {R}[!]{RST} {label}")
            print(f"      Origin sent:  {C}{origin}{RST}")
            print(f"      ACAO returned:{C}{result['acao']}{RST}")
            print(f"      Allow-Creds:  {C}{result['creds']}{RST}")
            print(f"      {msg}")
            findings.append({'endpoint': path, 'origin': origin, 'finding': severity})
        elif result and result['acao']:
            print(f"  {DIM}[~] {label} → ACAO: {result['acao']}{RST}")
        time.sleep(0.1)
    return findings

def preflight_test(base_url):
    print(f"\n{BOLD}{B}━━━ PREFLIGHT (OPTIONS) TEST ━━━{RST}")
    methods = ['PUT', 'DELETE', 'PATCH', 'CONNECT', 'TRACE']
    for method in methods:
        status, hdrs = fetch_preflight(base_url, 'https://attacker.com', method)
        acao = hdrs.get('Access-Control-Allow-Origin', hdrs.get('access-control-allow-origin', ''))
        acam = hdrs.get('Access-Control-Allow-Methods', hdrs.get('access-control-allow-methods', ''))
        if status in (200, 204):
            print(f"  {Y}[!]{RST} OPTIONS {method} → {status} | ACAO: {acao} | Methods: {acam}")
        time.sleep(0.1)

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC CORS Tester')
    parser.add_argument('target', help='Target URL (e.g. https://api.example.com)')
    parser.add_argument('--endpoints', action='store_true', help='Test multiple common API endpoints')
    parser.add_argument('--preflight', action='store_true', help='Test OPTIONS preflight')
    parser.add_argument('--full', action='store_true', help='Full test')
    args = parser.parse_args()

    target = args.target
    if not target.startswith('http'):
        target = 'https://' + target

    print(f"{BOLD}Target:{RST} {W}{target}{RST}\n")

    all_findings = []
    print(f"{BOLD}{B}━━━ CORS ORIGIN REFLECTION TEST ━━━{RST}")
    all_findings += test_endpoint(target, '/')

    if args.endpoints or args.full:
        for ep in ENDPOINTS_TO_CHECK[1:]:
            all_findings += test_endpoint(target, ep)

    if args.preflight or args.full:
        preflight_test(target)

    print(f"\n{BOLD}━━━ SUMMARY ━━━{RST}")
    if all_findings:
        crits = [f for f in all_findings if 'creds' in f['finding']]
        print(f"  Total findings: {len(all_findings)}")
        print(f"  Critical (with creds): {R}{len(crits)}{RST}")
        for f in all_findings:
            print(f"  {Y}→{RST} [{f['finding']}] {f['endpoint']} — origin: {f['origin']}")
    else:
        print(f"  {G}No CORS misconfigurations found{RST}")

    print(f"\n{DIM}Use --full for all endpoints + preflight tests.{RST}\n")

if __name__ == '__main__':
    main()
