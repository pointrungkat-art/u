#!/usr/bin/env python3
"""
XC IP FINDER — Lacak & Ungkap Real IP Target
DNS resolve · Cloudflare bypass · IP history · ASN · Geo · Reverse DNS
stdlib only + curl
"""
import sys, socket, json, urllib.request, urllib.parse, re, subprocess, argparse, time

R='\033[91m'; G='\033[92m'; Y='\033[93m'; C='\033[96m'; M='\033[95m'
BOLD='\033[1m'; DIM='\033[2m'; RST='\033[0m'

BANNER = f"""
{M}╔══════════════════════════════════════════════════════╗{RST}
{M}║{RST}  {BOLD}XC IP FINDER{RST}  ·  {Y}REAL IP HUNTER{RST}  ·  {R}JACKPOT MODE{RST}  {M}║{RST}
{M}║{RST}  DNS · CF Bypass · History · ASN · Geo · RevDNS    {M}║{RST}
{M}╚══════════════════════════════════════════════════════╝{RST}
"""

def tag(label, value, color=G): print(f"  {color}{BOLD}[{label}]{RST} {value}")
def section(title): print(f"\n{M}{BOLD}── {title} {'─'*(44-len(title))}{RST}")
def hit(msg): print(f"  {R}{BOLD}[JACKPOT]{RST} {Y}{msg}{RST}")

# ── CURL helper ─────────────────────────────────────────────────────────────

def curl(url, timeout=8, headers=None):
    cmd = ["curl", "-sL", "--max-time", str(timeout), "--insecure"]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        return r.stdout.strip()
    except Exception:
        return ""

# ── DNS over HTTPS ──────────────────────────────────────────────────────────

def doh_query(domain, qtype="A"):
    """Query DNS via Google DoH — no dig/nslookup needed"""
    url = f"https://dns.google/resolve?name={urllib.parse.quote(domain)}&type={qtype}"
    raw = curl(url)
    if not raw: return []
    try:
        data = json.loads(raw)
        answers = data.get("Answer", [])
        return [a["data"] for a in answers if a.get("type") in (
            {"A":1,"AAAA":28,"MX":15,"NS":2,"TXT":16,"CNAME":5,"SOA":6}.get(qtype, 999),
        )]
    except Exception:
        return []

def doh_all(domain):
    results = {}
    for qt in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        res = doh_query(domain, qt)
        if res:
            results[qt] = res
    return results

# ── SOCKET RESOLVE ──────────────────────────────────────────────────────────

def socket_resolve(host):
    try:
        infos = socket.getaddrinfo(host, None)
        ips = list(dict.fromkeys(i[4][0] for i in infos))
        return ips
    except Exception:
        return []

def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None

# ── CLOUDFLARE DETECTION ────────────────────────────────────────────────────

CF_RANGES = [
    "103.21.244.", "103.22.200.", "103.31.4.", "104.16.", "104.17.", "104.18.",
    "104.19.", "104.20.", "104.21.", "104.22.", "162.158.", "172.64.", "172.65.",
    "172.66.", "172.67.", "172.68.", "172.69.", "172.70.", "172.71.",
    "188.114.", "190.93.", "197.234.", "198.41.", "2606:4700"
]

def is_cloudflare(ip):
    return any(ip.startswith(r) for r in CF_RANGES)

def check_cf_headers(domain):
    raw = curl(f"http://{domain}", headers={"User-Agent": "Mozilla/5.0"})
    resp = curl(f"http://{domain}", timeout=5)
    # via response headers (need -I flag)
    cmd = ["curl", "-sI", "--max-time", "6", f"http://{domain}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        headers_raw = r.stdout.lower()
        return "cf-ray" in headers_raw or "cloudflare" in headers_raw
    except Exception:
        return False

# ── REAL IP BYPASS TECHNIQUES ───────────────────────────────────────────────

def spf_leak(domain):
    """SPF record kadang bocorkan real IP/server"""
    txts = doh_query(domain, "TXT")
    ips = []
    for txt in txts:
        if "spf" in txt.lower() or "v=spf" in txt.lower():
            # cari ip4: dan ip6:
            found = re.findall(r'ip[46]:([^\s]+)', txt)
            ips.extend(found)
    return ips

def mx_leak(domain):
    """MX record → mail server → bisa bocorkan hosting provider asli"""
    mx_records = doh_query(domain, "MX")
    mx_ips = []
    for mx in mx_records:
        mx_host = mx.split()[-1].rstrip(".")
        resolved = socket_resolve(mx_host)
        for ip in resolved:
            if not is_cloudflare(ip):
                mx_ips.append((mx_host, ip))
    return mx_ips

def subdomain_bruteforce(domain):
    """Common subdomain → mungkin expose real IP (bypass CDN)"""
    subs = [
        "direct", "direct-connect", "origin", "origin-www", "real",
        "backend", "api", "api2", "mail", "smtp", "ftp", "cpanel",
        "webmail", "admin", "staging", "dev", "test", "old", "beta",
        "vpn", "remote", "ssh", "git", "gitlab", "jenkins", "monitor",
        "status", "app", "portal", "ns1", "ns2", "mx", "autodiscover",
        "autoconfig", "panel", "plesk", "whm", "m", "mobile", "cdn",
        "assets", "static", "media", "img", "images", "upload",
    ]
    found = []
    for sub in subs:
        fqdn = f"{sub}.{domain}"
        ips = socket_resolve(fqdn)
        for ip in ips:
            if not is_cloudflare(ip):
                found.append((fqdn, ip))
                break
    return found

def crtsh_subdomains(domain):
    """crt.sh certificate transparency → subdomain harvest"""
    raw = curl(f"https://crt.sh/?q=%.{domain}&output=json", timeout=12)
    if not raw: return []
    try:
        data = json.loads(raw)
        names = set()
        for entry in data:
            for n in entry.get("name_value", "").split("\n"):
                n = n.strip().lstrip("*.")
                if n.endswith(domain) and n != domain:
                    names.add(n)
        return sorted(names)
    except Exception:
        return []

def hackertarget_iphist(domain):
    """HackerTarget free API — IP history"""
    raw = curl(f"https://api.hackertarget.com/hostsearch/?q={domain}", timeout=10)
    if not raw or "error" in raw.lower(): return []
    results = []
    for line in raw.strip().split("\n"):
        if "," in line:
            parts = line.split(",")
            if len(parts) >= 2:
                results.append((parts[0].strip(), parts[1].strip()))
    return results

def viewdns_iphist(domain):
    """ViewDNS IP history via scrape"""
    raw = curl(f"https://viewdns.info/iphistory/?domain={domain}", timeout=10,
               headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
    if not raw: return []
    ips = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', raw)
    # filter CF
    return [ip for ip in dict.fromkeys(ips) if not is_cloudflare(ip)]

# ── GEO & ASN ───────────────────────────────────────────────────────────────

def ip_info(ip):
    raw = curl(f"https://ipinfo.io/{ip}/json", timeout=8)
    if not raw: return {}
    try: return json.loads(raw)
    except: return {}

def shodan_lookup(ip, api_key=None):
    if not api_key: return None
    raw = curl(f"https://api.shodan.io/shodan/host/{ip}?key={api_key}", timeout=10)
    try: return json.loads(raw)
    except: return None

# ── PORT PEEK (cek port via timeout) ────────────────────────────────────────

def peek_ports(ip, ports=[80, 443, 22, 21, 8080, 8443, 3000, 3306, 5432, 6379, 27017]):
    open_ports = []
    for port in ports:
        try:
            s = socket.socket()
            s.settimeout(1.5)
            if s.connect_ex((ip, port)) == 0:
                open_ports.append(port)
            s.close()
        except Exception:
            pass
    return open_ports

# ── MAIN SCAN ───────────────────────────────────────────────────────────────

def run(domain, args):
    print(BANNER)
    print(f"  {BOLD}Target:{RST} {Y}{domain}{RST}\n")

    # strip http(s)://
    domain = re.sub(r'^https?://', '', domain).split('/')[0].split(':')[0]

    # ── 1. DNS Resolution
    section("DNS RESOLUTION")
    dns_all = doh_all(domain)
    main_ips = []

    for qtype, records in dns_all.items():
        for r in records:
            tag(qtype, r)
            if qtype == "A":
                main_ips.append(r)

    sock_ips = socket_resolve(domain)
    for ip in sock_ips:
        if ip not in main_ips:
            tag("SOCK", ip, C)
            main_ips.append(ip)

    if not main_ips:
        print(f"  {R}[!] Tidak bisa resolve {domain}{RST}")
        return

    # ── 2. Cloudflare check
    section("CDN / PROXY DETECTION")
    cf_detected = False
    for ip in main_ips:
        if is_cloudflare(ip):
            tag("CF", f"{ip} → {R}CLOUDFLARE DETECTED{RST}", Y)
            cf_detected = True
        else:
            tag("IP", f"{ip} → {G}DIRECT / NO CDN{RST}")

    if check_cf_headers(domain):
        tag("HDR", "cf-ray header present → confirmed Cloudflare", Y)
        cf_detected = True

    # ── 3. Real IP hunting (kalau CF)
    real_ips = []
    if cf_detected:
        section("REAL IP HUNTING (CF BYPASS)")

        # SPF leak
        spf = spf_leak(domain)
        if spf:
            for ip in spf:
                hit(f"SPF LEAK → {ip}")
                real_ips.append(ip)

        # MX leak
        mx = mx_leak(domain)
        if mx:
            for host, ip in mx:
                hit(f"MX LEAK → {host} → {ip}")
                real_ips.append(ip)

        # Subdomain brute
        print(f"\n  {DIM}Subdomain brute ({len(['direct','origin','api','mail','ftp','cpanel','webmail','admin','staging','dev','test','beta','app','portal'])} common)...{RST}")
        subs_hit = subdomain_bruteforce(domain)
        if subs_hit:
            for sub, ip in subs_hit:
                hit(f"SUBDOMAIN → {sub} → {ip}")
                real_ips.append(ip)

        # crt.sh → resolve
        if args.full:
            print(f"  {DIM}crt.sh harvest...{RST}")
            crt_subs = crtsh_subdomains(domain)
            if crt_subs:
                tag("CRT", f"{len(crt_subs)} subdomains found", C)
                for sub in crt_subs[:30]:
                    ips = socket_resolve(sub)
                    for ip in ips:
                        if not is_cloudflare(ip) and ip not in real_ips:
                            hit(f"CRT → {sub} → {ip}")
                            real_ips.append(ip)

        # IP history
        print(f"  {DIM}IP history lookup...{RST}")
        hist = hackertarget_iphist(domain)
        if hist:
            for sub, ip in hist[:20]:
                if not is_cloudflare(ip):
                    hit(f"HISTORY → {sub} → {ip}")
                    if ip not in real_ips: real_ips.append(ip)

        vdns = viewdns_iphist(domain)
        if vdns:
            for ip in vdns[:10]:
                if ip not in real_ips:
                    hit(f"VIEWDNS HISTORY → {ip}")
                    real_ips.append(ip)

    # ── 4. IP Info & Geo
    all_targets = list(dict.fromkeys(
        ([ip for ip in main_ips if not is_cloudflare(ip)] or main_ips) + real_ips
    ))

    section("IP INTEL & GEO")
    for ip in all_targets[:5]:
        info = ip_info(ip)
        if info:
            org  = info.get("org", "?")
            city = info.get("city", "?")
            country = info.get("country", "?")
            hostname = info.get("hostname", reverse_dns(ip) or "?")
            tag(ip, f"{country} · {city} · {org}", G)
            if hostname and hostname != "?":
                tag("↳", f"rDNS: {hostname}", DIM)

    # ── 5. Port peek
    section("OPEN PORTS (quick peek)")
    for ip in all_targets[:3]:
        ports = peek_ports(ip)
        if ports:
            tag(ip, f"OPEN: {', '.join(map(str, ports))}", C)
            if 22 in ports: hit(f"SSH terbuka di {ip}:22")
            if 3306 in ports: hit(f"MySQL exposed di {ip}:3306")
            if 6379 in ports: hit(f"Redis exposed di {ip}:6379")
            if 27017 in ports: hit(f"MongoDB exposed di {ip}:27017")
        else:
            tag(ip, "no common ports open / filtered", DIM)

    # ── 6. Reverse DNS
    section("REVERSE DNS")
    for ip in all_targets[:5]:
        rdns = reverse_dns(ip)
        if rdns:
            tag(ip, rdns, C)

    # ── 7. Summary
    section("SUMMARY")
    if real_ips:
        print(f"\n  {R}{BOLD}★ REAL IP CANDIDATES:{RST}")
        for ip in dict.fromkeys(real_ips):
            print(f"    {Y}{BOLD}→ {ip}{RST}")
    elif not cf_detected:
        print(f"\n  {G}{BOLD}★ DIRECT IP (no CDN):{RST}")
        for ip in main_ips:
            print(f"    {Y}{BOLD}→ {ip}{RST}")
    else:
        print(f"\n  {Y}[~] Cloudflare detected, real IP tidak ditemukan{RST}")
        print(f"  {DIM}Coba: --full untuk scan lebih dalam{RST}")

    print()

# ── ENTRY ────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="XC IP Finder — Real IP Hunter")
    p.add_argument("target", help="Domain atau IP (contoh: target.com)")
    p.add_argument("--full", action="store_true", help="Deep scan: crt.sh + more subdomains")
    p.add_argument("--shodan", metavar="KEY", help="Shodan API key untuk port/vuln intel")
    args = p.parse_args()
    run(args.target, args)

if __name__ == "__main__":
    main()
