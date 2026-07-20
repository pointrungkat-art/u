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
    ('recon',    'recon.py',   'Full recon — DNS, HTTP, WAF, tech, paths'),
    ('waf',      'waf.py',     'WAF bypass & real IP hunter'),
    ('cors',     'cors.py',    'CORS misconfiguration tester'),
    ('headers',  'headers.py', 'Security headers auditor'),
    ('jshunt',   'js_hunt.py', 'JS secret harvester (API keys, tokens)'),
    ('sqli',     'sqli.py',    'SQL injection fuzzer'),
]

MENU = f"""
{BOLD}TOOLS:{RST}
  {G}recon{RST}    <target>            — DNS + HTTP + WAF + tech fingerprint
  {G}waf{RST}      <target> [--full]   — WAF bypass attempts + real IP hunt
  {G}cors{RST}     <target> [--full]   — CORS misconfiguration test
  {G}headers{RST}  <target> [--full]   — Security headers audit + CSP analysis
  {G}jshunt{RST}   <target> [--inline] — JS secret harvester
  {G}sqli{RST}     <target> [--full]   — SQLi error/boolean/time fuzzer

{BOLD}EXAMPLES:{RST}
  {DIM}python3 xc.py recon https://target.com{RST}
  {DIM}python3 xc.py recon https://target.com --paths{RST}
  {DIM}python3 xc.py waf https://target.com/admin --full{RST}
  {DIM}python3 xc.py cors https://api.target.com --endpoints{RST}
  {DIM}python3 xc.py headers https://target.com --full{RST}
  {DIM}python3 xc.py jshunt https://target.com --inline{RST}
  {DIM}python3 xc.py sqli "https://target.com/page?id=1" --time{RST}

  {DIM}# Or run directly:{RST}
  {DIM}python3 recon.py https://target.com --full{RST}
  {DIM}python3 sqli.py "https://target.com/search?q=test" --full{RST}
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
