#!/usr/bin/env python3
# XC BugBounty Recon Tool
# Gunakan hanya pada target yang sudah ada izin (bug bounty program / authorized)

import subprocess, sys, os, socket, datetime

BANNER = """
╔══════════════════════════════════════╗
║       XC Bug Bounty Recon v1.0      ║
║   Authorized testing only — OPSEC   ║
╚══════════════════════════════════════╝
"""

def run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "[timeout]"
    except Exception as e:
        return f"[error: {e}]"

def section(title):
    print(f"\n{'='*44}")
    print(f"  {title}")
    print('='*44)

def recon(target):
    print(BANNER)
    print(f"[*] Target  : {target}")
    print(f"[*] Waktu   : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # DNS
    section("DNS Lookup")
    print(run(f"nslookup {target}"))

    # IP resolve
    section("IP Address")
    try:
        ip = socket.gethostbyname(target)
        print(f"IP: {ip}")
    except:
        print("[!] Gagal resolve IP")

    # WHOIS
    section("WHOIS")
    print(run(f"whois {target} 2>/dev/null | head -30"))

    # HTTP Headers
    section("HTTP Headers")
    print(run(f"curl -sI --max-time 10 https://{target}"))

    # Subdomain brute (wordlist kecil)
    section("Subdomain Check (quick)")
    subs = ["www","mail","api","admin","dev","staging","test","app","portal","vpn","ftp","m","cdn","blog","shop"]
    found = []
    for sub in subs:
        full = f"{sub}.{target}"
        try:
            socket.gethostbyname(full)
            found.append(full)
            print(f"  [+] {full}")
        except:
            pass
    if not found:
        print("  [-] Tidak ada subdomain ditemukan dari wordlist kecil")

    # Open ports (top 20)
    section("Port Scan — Top 20 (nmap)")
    print(run(f"nmap -T4 --top-ports 20 -oG - {target} 2>/dev/null | grep 'Ports:'"))

    # Tech detection
    section("Tech Stack (whatweb)")
    print(run(f"whatweb --no-errors -a 1 https://{target} 2>/dev/null"))

    # robots.txt
    section("robots.txt")
    print(run(f"curl -s --max-time 10 https://{target}/robots.txt"))

    # sitemap
    section("sitemap.xml")
    out = run(f"curl -s --max-time 10 https://{target}/sitemap.xml | head -20")
    print(out if out else "[-] Tidak ada sitemap")

    print(f"\n{'='*44}")
    print("  Recon selesai! Cek hasil di atas.")
    print('='*44)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 recon.py <target-domain>")
        print(f"Contoh: python3 recon.py example.com")
        sys.exit(1)
    recon(sys.argv[1])
