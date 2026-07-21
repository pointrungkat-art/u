"""Recon module — DNS, IP, ASN, CDN, subdomain"""
import socket, json, subprocess, re

CF_RANGES = ["104.16.","104.17.","104.18.","104.19.","104.20.","104.21.",
             "172.64.","172.65.","172.66.","172.67.","172.68.","172.69.",
             "162.158.","188.114.","190.93.","197.234.","198.41."]

def curl(url, timeout=8):
    try:
        r = subprocess.run(["curl","-sk","--max-time",str(timeout),url],
                           capture_output=True,text=True,timeout=timeout+2)
        return r.stdout.strip()
    except: return ""

def doh(domain, qtype="A"):
    import urllib.parse
    raw = curl(f"https://dns.google/resolve?name={urllib.parse.quote(domain)}&type={qtype}")
    try:
        d = json.loads(raw)
        return [a["data"] for a in d.get("Answer",[])
                if a.get("type") in ({1:"A",28:"AAAA",15:"MX",2:"NS",16:"TXT"}.get(qtype,999),
                                     {"A":1,"AAAA":28,"MX":15,"NS":2,"TXT":16}.get(qtype,0))]
    except: return []

def is_cf(ip): return any(ip.startswith(r) for r in CF_RANGES)

def ip_info(ip):
    raw = curl(f"https://ipinfo.io/{ip}/json")
    try: return json.loads(raw)
    except: return {}

def spf_leak(domain):
    txts = doh(domain, "TXT")
    return [ip for t in txts for ip in re.findall(r'ip[46]:([^\s]+)',t)]

def subdomain_quick(domain):
    subs = ["www","api","admin","mail","ftp","dev","staging","test","origin","direct","app","portal"]
    found = []
    for s in subs:
        try:
            ips = [i[4][0] for i in socket.getaddrinfo(f"{s}.{domain}",None)]
            for ip in dict.fromkeys(ips):
                if not is_cf(ip): found.append((f"{s}.{domain}", ip))
        except: pass
    return found

def run(target, full=False):
    domain = re.sub(r'^https?://','',target).split('/')[0].split(':')[0]
    findings = []

    # DNS
    ips = list(dict.fromkeys(doh(domain,"A")))
    direct_ips = [ip for ip in ips if not is_cf(ip)]

    for ip in ips:
        info = ip_info(ip)
        findings.append({
            "type": "ip", "value": ip,
            "cdn": is_cf(ip),
            "org": info.get("org","?"),
            "country": info.get("country","?"),
            "city": info.get("city","?"),
        })

    # SPF leak
    for ip in spf_leak(domain):
        findings.append({"type":"spf_leak","value":ip,"severity":"INFO"})

    # Subdomains
    for sub, ip in subdomain_quick(domain):
        findings.append({"type":"subdomain","value":sub,"ip":ip,"severity":"INFO"})

    return {"module":"recon","domain":domain,"ips":ips,"direct_ips":direct_ips,"findings":findings}
