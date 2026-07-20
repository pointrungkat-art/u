#!/usr/bin/env python3
"""XC JS Hunt — JavaScript Secret Harvester"""

import sys, ssl, re, time, argparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlparse, urljoin

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{M}
   ╦╔═╗  ╦ ╦╦ ╦╔╗╔╔╦╗
   ║╚═╗  ╠═╣║ ║║║║ ║
╚═╝╚═╝  ╩ ╩╚═╝╝╚╝ ╩ {RST}
{DIM}JavaScript Secret Harvester — XC Hub{RST}
"""

SECRET_PATTERNS = [
    ('AWS Access Key',       r'(?:AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}'),
    ('AWS Secret Key',       r'(?i)aws.{0,20}secret.{0,20}["\']([A-Za-z0-9/+=]{40})["\']'),
    ('Google API Key',       r'AIza[0-9A-Za-z\-_]{35}'),
    ('Google OAuth',         r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com'),
    ('Firebase URL',         r'https?://[a-z0-9-]+\.firebaseio\.com'),
    ('Firebase API Key',     r'(?i)firebase.{0,20}["\']([A-Za-z0-9_\-]{39})["\']'),
    ('GitHub Token',         r'ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82}'),
    ('GitHub OAuth',         r'gho_[A-Za-z0-9]{36}'),
    ('JWT Token',            r'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'),
    ('Bearer Token',         r'(?i)bearer\s+([A-Za-z0-9_\-\.]{20,})'),
    ('API Key generic',      r'(?i)api[_\-\s]?key[_\-\s]?[=:][_\-\s]?["\']([A-Za-z0-9_\-]{20,})["\']'),
    ('Secret generic',       r'(?i)(?:secret|passwd|password|token|auth)[_\-\s]?[=:][_\-\s]?["\']([A-Za-z0-9_\-!@#$%^&*]{8,})["\']'),
    ('Private Key',          r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----'),
    ('Slack Token',          r'xox[baprs]-[0-9a-zA-Z]{10,48}'),
    ('Slack Webhook',        r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+'),
    ('Stripe Key',           r'(?:pk|sk|rk)_(?:live|test)_[0-9a-zA-Z]{24,}'),
    ('Twilio Key',           r'SK[0-9a-fA-F]{32}'),
    ('Mailgun Key',          r'key-[0-9a-zA-Z]{32}'),
    ('SendGrid Key',         r'SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}'),
    ('Heroku API Key',       r'[hH]eroku.{0,30}[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'),
    ('Database URL',         r'(?i)(?:mongodb|mysql|postgres|postgresql|redis|amqp)://[^\s\'"<>]+'),
    ('Internal URL',         r'https?://(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)[^\s\'"<>]*'),
    ('IP Address',           r'\b(?:10|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b'),
    ('Email in code',        r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'),
    ('S3 Bucket',            r's3\.amazonaws\.com/[a-zA-Z0-9_\-\.]+|[a-zA-Z0-9_\-]+\.s3\.amazonaws\.com'),
    ('Hardcoded password',   r'(?i)(?:password|passwd|pwd)\s*[=:]\s*["\']([^"\']{4,})["\']'),
    ('Admin route',          r'(?i)["\'](?:/admin[^"\']*|/dashboard[^"\']*|/manage[^"\']*|/internal[^"\']*)["\']'),
    ('GraphQL endpoint',     r'(?i)["\'](?:/graphql[^"\']*|/api/graphql[^"\']*)["\']'),
    ('Debug/test endpoint',  r'(?i)["\'](?:/debug[^"\']*|/test[^"\']*|/dev[^"\']*|/staging[^"\']*)["\']'),
]

INTERESTING_VARS = [
    r'(?i)(?:apiUrl|baseUrl|apiEndpoint|backendUrl|serviceUrl)\s*[=:]\s*["\']([^"\']+)["\']',
    r'(?i)(?:clientId|client_id)\s*[=:]\s*["\']([^"\']{8,})["\']',
    r'(?i)(?:appId|app_id)\s*[=:]\s*["\']([^"\']{8,})["\']',
]

def fetch(url, timeout=10):
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
            return r.status, dict(r.headers), r.read(2*1024*1024).decode('utf-8', errors='ignore')
    except HTTPError as e:
        try: body = e.read(512).decode('utf-8', errors='ignore')
        except: body = ''
        return e.code, dict(e.headers), body
    except Exception as e:
        return None, {}, ''

def extract_js_urls(html, base_url):
    pattern = r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']'
    found = re.findall(pattern, html, re.IGNORECASE)
    urls = []
    for f in found:
        if f.startswith('http'):
            urls.append(f)
        else:
            urls.append(urljoin(base_url, f))
    return list(set(urls))

def extract_inline_js(html):
    pattern = r'<script[^>]*>(.*?)</script>'
    return re.findall(pattern, html, re.DOTALL | re.IGNORECASE)

def scan_content(content, source_name=''):
    findings = []
    for name, pattern in SECRET_PATTERNS:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match else ''
            if match and len(match) > 3:
                findings.append({'type': name, 'value': match[:200], 'source': source_name})
    for pattern in INTERESTING_VARS:
        matches = re.findall(pattern, content)
        for match in matches:
            if match and len(match) > 4:
                findings.append({'type': 'Interesting Variable', 'value': match[:200], 'source': source_name})
    return findings

def print_findings(findings, source):
    if not findings:
        print(f"  {DIM}No secrets found in {source}{RST}")
        return
    deduped = {}
    for f in findings:
        key = (f['type'], f['value'][:50])
        if key not in deduped:
            deduped[key] = f
    for f in deduped.values():
        color = R if any(x in f['type'] for x in ['Key', 'Secret', 'Token', 'Password', 'Private']) else Y
        print(f"  {color}[{f['type']}]{RST}")
        print(f"    {W}{f['value'][:120]}{RST}")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC JS Secret Hunter')
    parser.add_argument('target', help='Target URL')
    parser.add_argument('--inline', action='store_true', help='Also scan inline JS in HTML')
    parser.add_argument('--depth', type=int, default=0, help='Follow JS source maps (0=no)')
    parser.add_argument('--output', help='Save findings to file')
    args = parser.parse_args()

    target = args.target
    if not target.startswith('http'):
        target = 'https://' + target
    parsed = urlparse(target)

    print(f"{BOLD}Target:{RST} {W}{target}{RST}\n")
    print(f"{BOLD}{B}━━━ FETCHING BASE PAGE ━━━{RST}")
    status, hdrs, html = fetch(target)
    if not html:
        print(f"{R}No response{RST}")
        sys.exit(1)
    print(f"  Status: {status} | Size: {len(html)} bytes")

    js_urls = extract_js_urls(html, target)
    print(f"  Found {len(js_urls)} JS files")

    all_findings = []

    if args.inline:
        print(f"\n{BOLD}{B}━━━ INLINE JS SCAN ━━━{RST}")
        inline_scripts = extract_inline_js(html)
        inline_all = '\n'.join(inline_scripts)
        findings = scan_content(inline_all, 'inline')
        print_findings(findings, 'inline scripts')
        all_findings += findings

    print(f"\n{BOLD}{B}━━━ JS FILE SCAN ━━━{RST}")
    for js_url in js_urls:
        short = js_url.split('/')[-1][:60]
        print(f"\n  {C}→{RST} {short}")
        status, _, content = fetch(js_url)
        if status and content:
            print(f"    Size: {len(content)} bytes")
            findings = scan_content(content, js_url)
            print_findings(findings, short)
            all_findings += findings
        else:
            print(f"    {R}Failed ({status}){RST}")
        time.sleep(0.2)

    print(f"\n{BOLD}━━━ TOTAL FINDINGS: {len(all_findings)} ━━━{RST}")

    if args.output and all_findings:
        with open(args.output, 'w') as f:
            for finding in all_findings:
                f.write(f"[{finding['type']}] {finding['value']} | source: {finding['source']}\n")
        print(f"{G}Saved to {args.output}{RST}")

    print(f"\n{DIM}Use --inline for inline JS, --output FILE to save results.{RST}\n")

if __name__ == '__main__':
    main()
