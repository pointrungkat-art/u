#!/usr/bin/env python3
"""XC Recon — Master Reconnaissance Tool"""

import sys, socket, ssl, re, json, time, argparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{M}
╔═╗╔═╗ ╦═╗╔═╗╔═╗╔═╗╔╗╔
╠╦╝║╣  ║╔╝║╣ ║  ║ ║║║║
╩╚═╚═╝ ╩╚═╚═╝╚═╝╚═╝╝╚╝{RST}
{DIM}Master Recon Tool — XC Hub{RST}
"""

HEADERS_BASE = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

COMMON_PATHS = [
    '/robots.txt', '/sitemap.xml', '/.well-known/security.txt',
    '/admin', '/admin/', '/administrator', '/wp-admin', '/wp-login.php',
    '/login', '/dashboard', '/panel', '/cpanel', '/phpmyadmin',
    '/.git/HEAD', '/.git/config', '/.env', '/.htaccess',
    '/api', '/api/v1', '/api/v2', '/api/docs', '/swagger',
    '/swagger.json', '/openapi.json', '/graphql', '/graphiql',
    '/config.php', '/config.json', '/config.yml', '/config.yaml',
    '/backup', '/backup.zip', '/backup.tar.gz', '/db.sql',
    '/server-status', '/server-info', '/info.php', '/phpinfo.php',
    '/test', '/test.php', '/debug', '/debug.php',
    '/upload', '/uploads', '/files', '/static',
    '/actuator', '/actuator/health', '/actuator/env', '/actuator/mappings',
    '/.DS_Store', '/crossdomain.xml', '/clientaccesspolicy.xml',
]

TECH_SIGNATURES = {
    'WordPress': ['wp-content', 'wp-includes', 'WordPress'],
    'Drupal': ['Drupal', 'drupal'],
    'Joomla': ['Joomla', 'joomla'],
    'Laravel': ['laravel_session', 'Laravel'],
    'Django': ['csrftoken', 'django'],
    'Rails': ['_rails_session', 'X-Powered-By: Phusion Passenger'],
    'Express': ['X-Powered-By: Express'],
    'ASP.NET': ['ASP.NET', '__VIEWSTATE', 'X-Powered-By: ASP.NET'],
    'PHP': ['X-Powered-By: PHP', '.php'],
    'Nginx': ['nginx'],
    'Apache': ['Apache'],
    'Cloudflare': ['cf-ray', 'cloudflare', '__cfduid'],
    'AWS': ['x-amz', 'amazonaws'],
    'Shopify': ['myshopify', 'Shopify'],
    'React': ['__NEXT_DATA__', 'react'],
    'Vue': ['__vue__', 'vue'],
    'Angular': ['ng-version', 'angular'],
}

def log(tag, msg, color=W):
    print(f"{color}[{tag}]{RST} {msg}")

def ok(msg): log('+', msg, G)
def warn(msg): log('!', msg, Y)
def err(msg): log('-', msg, R)
def info(msg): log('*', msg, C)

def fetch(url, timeout=8, headers=None):
    h = {**HEADERS_BASE, **(headers or {})}
    req = Request(url, headers=h)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(1024*512).decode('utf-8', errors='ignore')
            return r.status, dict(r.headers), body
    except HTTPError as e:
        try:
            body = e.read(4096).decode('utf-8', errors='ignore')
        except:
            body = ''
        return e.code, dict(e.headers), body
    except Exception as e:
        return None, {}, str(e)

def dns_recon(host):
    print(f"\n{BOLD}{B}━━━ DNS RECON ━━━{RST}")
    try:
        ip = socket.gethostbyname(host)
        ok(f"A Record: {W}{ip}{RST}")
    except Exception as e:
        err(f"DNS lookup failed: {e}")
        ip = None
    try:
        results = socket.getaddrinfo(host, None)
        ips = list(set(r[4][0] for r in results))
        if len(ips) > 1:
            info(f"All IPs: {', '.join(ips)}")
    except: pass
    try:
        rev = socket.gethostbyaddr(ip)[0] if ip else None
        if rev: info(f"Reverse DNS: {W}{rev}{RST}")
    except: pass
    return ip

def http_probe(url):
    print(f"\n{BOLD}{B}━━━ HTTP PROBE ━━━{RST}")
    status, hdrs, body = fetch(url)
    if status is None:
        err(f"No response — {hdrs}")
        return None, {}, ''
    color = G if 200 <= status < 300 else Y if 300 <= status < 400 else R
    print(f"{color}  Status: {status}{RST}")
    interesting = ['server','x-powered-by','content-type','x-frame-options',
                   'x-xss-protection','content-security-policy','strict-transport-security',
                   'x-content-type-options','access-control-allow-origin','set-cookie',
                   'cf-ray','x-amz-request-id','x-cache','via','location']
    for k,v in hdrs.items():
        if k.lower() in interesting:
            print(f"  {C}{k}{RST}: {v}")
    return status, hdrs, body

def detect_waf(hdrs, body):
    print(f"\n{BOLD}{B}━━━ WAF DETECTION ━━━{RST}")
    waf_sigs = {
        'Cloudflare': ['cf-ray', 'cloudflare'],
        'AWS WAF': ['x-amzn-requestid', 'x-amz-cf-id'],
        'Akamai': ['akamai', 'x-akamai'],
        'Sucuri': ['x-sucuri-id', 'sucuri'],
        'ModSecurity': ['mod_security', 'NOYB'],
        'Incapsula': ['incap_ses', 'visid_incap'],
        'F5 BIG-IP': ['BigIP', 'F5'],
        'Imperva': ['imperva', '_px'],
        'Barracuda': ['barra_counter_session'],
    }
    found = []
    hdrs_lower = {k.lower(): v.lower() for k,v in hdrs.items()}
    body_lower = body.lower()
    for waf, sigs in waf_sigs.items():
        for sig in sigs:
            if sig.lower() in str(hdrs_lower) or sig.lower() in body_lower:
                found.append(waf)
                break
    if found:
        warn(f"WAF Detected: {', '.join(found)}")
    else:
        ok("No WAF signatures found")
    return found

def detect_tech(hdrs, body):
    print(f"\n{BOLD}{B}━━━ TECH FINGERPRINT ━━━{RST}")
    found = []
    hdrs_str = str(hdrs).lower()
    body_lower = body.lower()
    for tech, sigs in TECH_SIGNATURES.items():
        for sig in sigs:
            if sig.lower() in hdrs_str or sig.lower() in body_lower:
                found.append(tech)
                break
    if found:
        ok(f"Detected: {W}{', '.join(found)}{RST}")
    else:
        info("No tech signatures matched")
    return found

def path_probe(base_url):
    print(f"\n{BOLD}{B}━━━ PATH PROBE ━━━{RST}")
    hits = []
    base = base_url.rstrip('/')
    for path in COMMON_PATHS:
        url = base + path
        status, hdrs, body = fetch(url, timeout=5)
        if status and status not in (404, 429):
            color = G if status == 200 else Y if status in (301,302,403) else C
            print(f"  {color}{status}{RST} {path}")
            hits.append({'path': path, 'status': status})
        time.sleep(0.15)
    if not hits:
        info("No interesting paths found")
    return hits

def ssl_info(host):
    print(f"\n{BOLD}{B}━━━ SSL/TLS INFO ━━━{RST}")
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(5)
            s.connect((host, 443))
            cert = s.getpeercert()
            subj = dict(x[0] for x in cert.get('subject', []))
            issuer = dict(x[0] for x in cert.get('issuer', []))
            ok(f"CN: {subj.get('commonName','?')}")
            info(f"Issuer: {issuer.get('organizationName','?')}")
            info(f"Expires: {cert.get('notAfter','?')}")
            sans = [v for t,v in cert.get('subjectAltName', []) if t == 'DNS']
            if sans:
                info(f"SANs ({len(sans)}): {', '.join(sans[:8])}")
                if len(sans) > 8:
                    print(f"  {DIM}...and {len(sans)-8} more{RST}")
    except Exception as e:
        warn(f"SSL probe failed: {e}")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC Recon Tool')
    parser.add_argument('target', help='Target URL or domain')
    parser.add_argument('--paths', action='store_true', help='Probe common paths')
    parser.add_argument('--full', action='store_true', help='Full scan (all modules)')
    args = parser.parse_args()

    target = args.target
    if not target.startswith('http'):
        target = 'https://' + target
    parsed = urlparse(target)
    host = parsed.hostname

    print(f"{BOLD}Target:{RST} {W}{target}{RST}")
    print(f"{BOLD}Host:{RST}   {W}{host}{RST}\n")

    ip = dns_recon(host)
    ssl_info(host)
    status, hdrs, body = http_probe(target)
    if hdrs:
        detect_waf(hdrs, body)
        detect_tech(hdrs, body)
    if args.paths or args.full:
        path_probe(target)

    print(f"\n{DIM}Done. Use --paths for path probe, --full for everything.{RST}\n")

if __name__ == '__main__':
    main()
