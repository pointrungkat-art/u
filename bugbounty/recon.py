#!/usr/bin/env python3
# XC BugBounty Recon Tool v1.1
# Gunakan hanya pada target yang sudah ada izin (bug bounty program / authorized)

import sys, socket, datetime, subprocess
import requests
import dns.resolver

BANNER = """
╔══════════════════════════════════════════╗
║      XC Bug Bounty Recon Tool v1.1      ║
║   Authorized / Bug Bounty targets only  ║
╚══════════════════════════════════════════╝
"""

SUBDOMAINS = [
    "www","mail","api","admin","dev","staging","test","app","portal",
    "vpn","ftp","m","cdn","blog","shop","static","assets","media",
    "login","auth","oauth","dashboard","panel","manage","console",
    "beta","demo","support","help","docs","status","monitor",
]

def section(title):
    print(f"\n{'═'*46}")
    print(f"  {title}")
    print('═'*46)

def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        return r.stdout.strip() or r.stderr.strip() or "[-] no output"
    except subprocess.TimeoutExpired:
        return "[!] timeout"
    except Exception as e:
        return f"[!] error: {e}"

def dns_lookup(target):
    section("DNS Records")
    for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        try:
            answers = dns.resolver.resolve(target, rtype)
            for r in answers:
                print(f"  {rtype:6} → {r}")
        except Exception:
            pass

def ip_info(target):
    section("IP Address")
    try:
        ip = socket.gethostbyname(target)
        print(f"  IP : {ip}")
        try:
            resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=8)
            d = resp.json()
            print(f"  Org: {d.get('org','?')}")
            print(f"  Loc: {d.get('city','?')}, {d.get('country','?')}")
        except Exception:
            pass
    except Exception:
        print("  [!] Gagal resolve IP")

def http_headers(target):
    section("HTTP Headers")
    for scheme in ["https", "http"]:
        try:
            r = requests.head(f"{scheme}://{target}", timeout=8, allow_redirects=True)
            print(f"  Status  : {r.status_code}")
            print(f"  Final URL: {r.url}")
            interesting = ["server","x-powered-by","x-frame-options","content-security-policy",
                           "strict-transport-security","x-content-type-options","set-cookie","location"]
            for h in interesting:
                if h in r.headers:
                    print(f"  {h}: {r.headers[h][:120]}")
            break
        except Exception:
            continue

def subdomain_enum(target):
    section(f"Subdomain Brute ({len(SUBDOMAINS)} wordlist)")
    found = []
    for sub in SUBDOMAINS:
        full = f"{sub}.{target}"
        try:
            socket.gethostbyname(full)
            found.append(full)
            print(f"  [+] {full}")
        except Exception:
            pass
    if not found:
        print("  [-] Tidak ada subdomain ditemukan")
    return found

def robots_sitemap(target):
    section("robots.txt & sitemap.xml")
    for path in ["/robots.txt", "/sitemap.xml", "/sitemap_index.xml"]:
        try:
            r = requests.get(f"https://{target}{path}", timeout=8)
            if r.status_code == 200:
                print(f"\n  [{path}] — {len(r.text)} chars")
                print("  " + "\n  ".join(r.text.strip().splitlines()[:15]))
            else:
                print(f"  [{path}] → {r.status_code}")
        except Exception:
            print(f"  [{path}] → error")

def juicy_paths(target):
    section("Juicy Path Check")
    paths = [
        "/.git/config", "/.env", "/config.php", "/wp-config.php",
        "/phpinfo.php", "/admin", "/administrator", "/login",
        "/api/v1", "/api/v2", "/swagger", "/swagger-ui.html",
        "/actuator", "/actuator/env", "/.well-known/security.txt",
        "/backup.zip", "/backup.sql", "/dump.sql",
    ]
    for path in paths:
        try:
            r = requests.get(f"https://{target}{path}", timeout=6, allow_redirects=False)
            status = r.status_code
            if status in [200, 301, 302, 403]:
                flag = "🔥" if status == 200 else "→"
                print(f"  {flag} [{status}] {path}")
        except Exception:
            pass

def recon(target):
    print(BANNER)
    print(f"  Target : {target}")
    print(f"  Waktu  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    dns_lookup(target)
    ip_info(target)
    http_headers(target)
    subdomain_enum(target)
    robots_sitemap(target)
    juicy_paths(target)

    section("Recon Selesai!")
    print("  Next step: manual test, Burp Suite, atau run checklist.md\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage  : python3 recon.py <domain>")
        print(f"Contoh : python3 recon.py example.com")
        sys.exit(1)
    recon(sys.argv[1].replace("https://","").replace("http://","").strip("/"))
