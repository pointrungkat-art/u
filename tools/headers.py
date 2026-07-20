#!/usr/bin/env python3
"""XC Headers — Security Headers Auditor"""

import sys, ssl, argparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{G}
╦ ╦╔═╗╔═╗╔╦╗╔═╗╦═╗╔═╗
╠═╣║╣ ╠═╣ ║║║╣ ╠╦╝╚═╗
╩ ╩╚═╝╩ ╩═╩╝╚═╝╩╚═╚═╝{RST}
{DIM}Security Headers Auditor — XC Hub{RST}
"""

SECURITY_HEADERS = {
    'Strict-Transport-Security': {
        'required': True,
        'desc': 'HSTS — forces HTTPS connections',
        'good': lambda v: 'max-age=' in v and int(v.split('max-age=')[1].split(';')[0].strip()) >= 31536000,
        'good_hint': 'max-age >= 31536000 (1 year) + includeSubDomains recommended',
        'bad_hint': 'Missing or short max-age → SSL stripping possible',
    },
    'Content-Security-Policy': {
        'required': True,
        'desc': 'CSP — prevents XSS & data injection',
        'good': lambda v: "default-src" in v or "script-src" in v,
        'good_hint': "Has default-src or script-src directive",
        'bad_hint': "Missing CSP → XSS attacks unmitigated",
    },
    'X-Frame-Options': {
        'required': True,
        'desc': 'Clickjacking protection',
        'good': lambda v: v.upper() in ('DENY', 'SAMEORIGIN'),
        'good_hint': 'DENY or SAMEORIGIN',
        'bad_hint': 'Missing → clickjacking possible',
    },
    'X-Content-Type-Options': {
        'required': True,
        'desc': 'MIME-type sniffing protection',
        'good': lambda v: v.lower() == 'nosniff',
        'good_hint': 'nosniff',
        'bad_hint': 'Missing → MIME-type confusion attacks',
    },
    'X-XSS-Protection': {
        'required': False,
        'desc': 'Legacy XSS filter (older browsers)',
        'good': lambda v: '1; mode=block' in v,
        'good_hint': '1; mode=block',
        'bad_hint': 'Informational only (deprecated in modern browsers)',
    },
    'Referrer-Policy': {
        'required': False,
        'desc': 'Controls referrer info sent to third parties',
        'good': lambda v: v.lower() in ('no-referrer', 'strict-origin', 'strict-origin-when-cross-origin', 'same-origin'),
        'good_hint': 'no-referrer or strict-origin-when-cross-origin',
        'bad_hint': 'Missing → referrer leaks to third parties',
    },
    'Permissions-Policy': {
        'required': False,
        'desc': 'Browser feature permissions (camera, mic, geolocation)',
        'good': lambda v: len(v) > 5,
        'good_hint': 'Policy defined',
        'bad_hint': 'Missing → browser features unrestricted',
    },
    'Access-Control-Allow-Origin': {
        'required': False,
        'desc': 'CORS policy',
        'good': lambda v: v != '*',
        'good_hint': 'Not wildcard',
        'bad_hint': 'Wildcard (*) allows any origin to read response',
    },
    'Cache-Control': {
        'required': False,
        'desc': 'Cache directives (sensitive pages)',
        'good': lambda v: 'no-store' in v or 'no-cache' in v,
        'good_hint': 'no-store or no-cache for sensitive resources',
        'bad_hint': 'Might cache sensitive responses',
    },
    'X-Permitted-Cross-Domain-Policies': {
        'required': False,
        'desc': 'Adobe Flash/PDF cross-domain policy',
        'good': lambda v: v.lower() == 'none',
        'good_hint': 'none',
        'bad_hint': 'May allow Flash cross-domain access',
    },
    'Expect-CT': {
        'required': False,
        'desc': 'Certificate Transparency enforcement (deprecated)',
        'good': lambda v: 'enforce' in v.lower(),
        'good_hint': 'enforce directive present',
        'bad_hint': 'Deprecated — CSP replaces this',
    },
    'Cross-Origin-Opener-Policy': {
        'required': False,
        'desc': 'COOP — isolates browsing context',
        'good': lambda v: 'same-origin' in v.lower(),
        'good_hint': 'same-origin',
        'bad_hint': 'Missing → XS-Leaks possible',
    },
    'Cross-Origin-Embedder-Policy': {
        'required': False,
        'desc': 'COEP — controls embedded resource loading',
        'good': lambda v: 'require-corp' in v.lower(),
        'good_hint': 'require-corp',
        'bad_hint': 'Missing → Spectre side-channel exposure',
    },
    'Cross-Origin-Resource-Policy': {
        'required': False,
        'desc': 'CORP — blocks cross-origin reads',
        'good': lambda v: v.lower() in ('same-origin', 'same-site'),
        'good_hint': 'same-origin or same-site',
        'bad_hint': 'Missing → Cross-Origin reads allowed',
    },
}

DANGEROUS_HEADERS = {
    'X-Powered-By': 'Exposes tech stack — remove it',
    'Server': 'Exposes server version — minimize it',
    'X-AspNet-Version': 'Exposes ASP.NET version — remove it',
    'X-AspNetMvc-Version': 'Exposes MVC version — remove it',
    'X-Generator': 'Exposes CMS/generator — remove it',
}

CSP_DANGEROUS = [
    ("'unsafe-inline'", "HIGH — allows inline JS/CSS → XSS"),
    ("'unsafe-eval'", "HIGH — allows eval() → XSS"),
    ("*", "MEDIUM — wildcard source"),
    ("data:", "MEDIUM — data: URI allowed"),
    ("http:", "MEDIUM — allows HTTP sources"),
]

def fetch(url, timeout=8):
    h = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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

def normalize_headers(hdrs):
    return {k.lower(): v for k, v in hdrs.items()}

def audit_security_headers(hdrs_raw):
    print(f"\n{BOLD}{B}━━━ SECURITY HEADER AUDIT ━━━{RST}")
    hdrs = normalize_headers(hdrs_raw)
    score = 0
    max_score = 0
    missing_required = []

    for name, cfg in SECURITY_HEADERS.items():
        key = name.lower()
        val = hdrs.get(key, '')
        if cfg['required']:
            max_score += 2
        else:
            max_score += 1

        if val:
            is_good = cfg['good'](val)
            if is_good:
                sym = f"{G}✓{RST}"
                score += 2 if cfg['required'] else 1
            else:
                sym = f"{Y}~{RST}"
                score += 1 if cfg['required'] else 0
            print(f"  {sym} {W}{name}{RST}")
            print(f"      Value: {DIM}{val[:120]}{RST}")
            if not is_good:
                print(f"      {Y}Hint: {cfg['good_hint']}{RST}")
        else:
            sym = f"{R}✗{RST}"
            print(f"  {sym} {W}{name}{RST} {DIM}(missing){RST}")
            print(f"      {R}{cfg['bad_hint']}{RST}")
            if cfg['required']:
                missing_required.append(name)

    pct = int(score / max_score * 100) if max_score else 0
    color = G if pct >= 80 else Y if pct >= 50 else R
    print(f"\n  Score: {color}{pct}%{RST} ({score}/{max_score})")
    return missing_required

def audit_csp(hdrs_raw):
    hdrs = normalize_headers(hdrs_raw)
    csp = hdrs.get('content-security-policy', '')
    if not csp:
        return
    print(f"\n{BOLD}{B}━━━ CSP DEEP ANALYSIS ━━━{RST}")
    print(f"  {DIM}{csp[:300]}{RST}\n")
    for pattern, severity in CSP_DANGEROUS:
        if pattern in csp:
            print(f"  {Y}[!]{RST} Found {C}{pattern}{RST} — {severity}")
    directives = csp.split(';')
    print(f"\n  Directives ({len(directives)}):")
    for d in directives:
        d = d.strip()
        if d:
            print(f"    {DIM}• {d}{RST}")

def audit_cookies(hdrs_raw):
    print(f"\n{BOLD}{B}━━━ COOKIE FLAGS ━━━{RST}")
    hdrs = normalize_headers(hdrs_raw)
    cookies = []
    for k, v in hdrs.items():
        if k == 'set-cookie':
            cookies.append(v)
    if not cookies:
        print(f"  {DIM}No Set-Cookie headers{RST}")
        return
    for cookie in cookies:
        name = cookie.split('=')[0]
        flags = cookie.lower()
        issues = []
        if 'httponly' not in flags: issues.append(f"{R}No HttpOnly{RST}")
        if 'secure' not in flags:  issues.append(f"{R}No Secure{RST}")
        if 'samesite' not in flags: issues.append(f"{Y}No SameSite{RST}")
        flag_str = ' | '.join(issues) if issues else f"{G}OK{RST}"
        print(f"  {W}{name}{RST} → {flag_str}")
        print(f"    {DIM}{cookie[:120]}{RST}")

def audit_dangerous_headers(hdrs_raw):
    print(f"\n{BOLD}{B}━━━ INFO-LEAKING HEADERS ━━━{RST}")
    hdrs = normalize_headers(hdrs_raw)
    found = False
    for name, hint in DANGEROUS_HEADERS.items():
        val = hdrs.get(name.lower(), '')
        if val:
            found = True
            print(f"  {Y}[!]{RST} {W}{name}{RST}: {val}")
            print(f"      {hint}")
    if not found:
        print(f"  {G}No dangerous info-leaking headers found{RST}")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC Security Headers Auditor')
    parser.add_argument('target', help='Target URL')
    parser.add_argument('--csp', action='store_true', help='Deep CSP analysis')
    parser.add_argument('--cookies', action='store_true', help='Cookie flag audit')
    parser.add_argument('--full', action='store_true', help='All checks')
    args = parser.parse_args()

    target = args.target
    if not target.startswith('http'):
        target = 'https://' + target

    print(f"{BOLD}Target:{RST} {W}{target}{RST}")
    status, hdrs = fetch(target)
    if not hdrs:
        print(f"{R}No response from target{RST}")
        sys.exit(1)
    print(f"Status: {status} | Headers received: {len(hdrs)}\n")

    missing = audit_security_headers(hdrs)
    audit_dangerous_headers(hdrs)

    if args.csp or args.full:
        audit_csp(hdrs)
    if args.cookies or args.full:
        audit_cookies(hdrs)

    if missing:
        print(f"\n{R}Missing required headers:{RST} {', '.join(missing)}")
    print(f"\n{DIM}Use --full for CSP deep dive + cookie audit.{RST}\n")

if __name__ == '__main__':
    main()
