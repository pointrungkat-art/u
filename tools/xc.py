#!/usr/bin/env python3
"""XC Hub — Hacking Tools Runner"""

import sys, os, subprocess

R='\033[91m'; G='\033[92m'; Y='\033[93m'; B='\033[94m'; M='\033[95m'; C='\033[96m'; W='\033[97m'; DIM='\033[2m'; BOLD='\033[1m'; RST='\033[0m'

BANNER = f"""
{M}██╗  ██╗ ██████╗    ██╗  ██╗██╗   ██╗██████╗ {RST}
{M}╚██╗██╔╝██╔════╝    ██║  ██║██║   ██║██╔══██╗{RST}
{M} ╚███╔╝ ██║         ███████║██║   ██║██████╔╝{RST}
{M} ██╔██╗ ██║         ██╔══██║██║   ██║██╔══██╗{RST}
{M}██╔╝ ██╗╚██████╗    ██║  ██║╚██████╔╝██████╔╝{RST}
{M}╚═╝  ╚═╝ ╚═════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ {RST}
{DIM}           Python Hacking Tools Suite{RST}

"""

TOOLS = [
    # Tier Base
    ('recon',    'recon.py',   'Full recon — DNS, HTTP, WAF, tech, paths'),
    ('waf',      'waf.py',     'WAF bypass & real IP hunter'),
    ('cors',     'cors.py',    'CORS misconfiguration tester'),
    ('headers',  'headers.py', 'Security headers auditor'),
    ('jshunt',   'js_hunt.py', 'JS secret harvester (API keys, tokens)'),
    ('sqli',     'sqli.py',    'SQL injection fuzzer'),
    # Tier S — RCE / Full Takeover
    ('ssti',     'ssti.py',    'SSTI hunter + RCE payload generator'),
    ('cmdi',     'cmdi.py',    'Command injection fuzzer (inline + time-based)'),
    ('jwt',      'jwt.py',     'JWT attacks — alg:none, brute, kid, RS256→HS256'),
    ('ssrf',     'ssrf.py',    'SSRF — internal service scan + bypass'),
    ('upload',   'upload.py',  'File upload bypass — ext/MIME/magic/SVG/dotfile'),
]

MENU = f"""
{BOLD}TIER BASE — RECON & ANALYSIS:{RST}
  {G}recon{RST}    <target>              — DNS + HTTP + WAF + tech fingerprint
  {G}waf{RST}      <target> [--full]     — WAF bypass + real IP hunt
  {G}cors{RST}     <target> [--full]     — CORS misconfiguration test
  {G}headers{RST}  <target> [--full]     — Security headers audit + CSP
  {G}jshunt{RST}   <target> [--inline]   — JS secret harvester
  {G}sqli{RST}     <target> [--full]     — SQLi error/boolean/time fuzzer

{BOLD}TIER S — RCE / FULL TAKEOVER:{RST}
  {R}ssti{RST}     <target> [--rce Jinja2] — SSTI detection + RCE payloads
  {R}cmdi{RST}     <target> [--full]       — Command injection inline + time-based
  {R}jwt{RST}      <token>  [--full]       — JWT alg:none, brute, kid, RS256→HS256
  {R}ssrf{RST}     <target> [--scan]       — SSRF + internal service scan
  {R}upload{RST}   <url>    [--full]       — File upload bypass → webshell

{BOLD}EXAMPLES:{RST}
  {DIM}python3 xc.py recon https://target.com --paths{RST}
  {DIM}python3 xc.py ssti "https://target.com/page?name=test"{RST}
  {DIM}python3 xc.py ssti <url> --rce Jinja2{RST}
  {DIM}python3 xc.py cmdi "https://target.com/ping?ip=1.1.1.1" --full{RST}
  {DIM}python3 xc.py jwt eyJhbGc... --full{RST}
  {DIM}python3 xc.py jwt eyJhbGc... --brute --wordlist secrets.txt{RST}
  {DIM}python3 xc.py ssrf "https://target.com/fetch?url=http://x" --scan{RST}
  {DIM}python3 xc.py upload https://target.com/upload --field file --full{RST}
  {DIM}python3 xc.py upload --shells{RST}
  {DIM}python3 xc.py sqli "https://target.com/search?q=test" --time --full{RST}
"""

def main():
    print(BANNER)
    if len(sys.argv) < 2:
        print(MENU)
        sys.exit(0)

    tool = sys.argv[1].lower()
    rest = sys.argv[2:]

    tool_map = {t[0]: t[1] for t in TOOLS}
    if tool not in tool_map:
        print(f"{R}Unknown tool: {tool}{RST}")
        print(f"Available: {', '.join(tool_map.keys())}")
        sys.exit(1)

    script = os.path.join(os.path.dirname(__file__), tool_map[tool])
    cmd = [sys.executable, script] + rest
    os.execv(sys.executable, cmd)

if __name__ == '__main__':
    main()
