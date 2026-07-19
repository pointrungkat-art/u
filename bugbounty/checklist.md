# XC Bug Bounty Checklist

> Gunakan hanya pada program bug bounty resmi / target yang sudah ada izin tertulis.

---

## Recon

- [ ] WHOIS + DNS enumeration
- [ ] Subdomain enumeration (amass, subfinder, assetfinder)
- [ ] Port scan (nmap top 1000)
- [ ] Tech stack detection (whatweb, wappalyzer)
- [ ] Google dorking (`site:target.com filetype:pdf`, `inurl:admin`, dll)
- [ ] Cek robots.txt, sitemap.xml
- [ ] JS file enumeration (linkfinder, getJS)
- [ ] Wayback Machine (`web.archive.org`)
- [ ] Certificate transparency (`crt.sh/?q=%.target.com`)

---

## Authentication

- [ ] Default credentials
- [ ] Username enumeration (timing attack / error message)
- [ ] Brute force (cek rate limiting dulu)
- [ ] Password reset flow — token predictable?
- [ ] MFA bypass
- [ ] OAuth misconfiguration (redirect_uri, state param)
- [ ] JWT — `alg:none`, weak secret, `kid` injection

---

## Injection

- [ ] SQL Injection (manual + sqlmap)
- [ ] XSS — reflected, stored, DOM-based
- [ ] SSTI (Server-Side Template Injection)
- [ ] Command Injection
- [ ] XXE (XML External Entity)
- [ ] LDAP Injection
- [ ] NoSQL Injection

---

## Access Control

- [ ] IDOR (Insecure Direct Object Reference) — ganti ID di URL/body
- [ ] Privilege escalation (user → admin)
- [ ] Horizontal privilege escalation (akses data user lain)
- [ ] Missing auth pada endpoint sensitif
- [ ] Mass assignment

---

## Business Logic

- [ ] Negative price / quantity
- [ ] Coupon/promo abuse
- [ ] Race condition (beli 1 bayar 2x, dll)
- [ ] Workflow bypass (skip step pembayaran, dll)
- [ ] Account takeover via email change

---

## File Upload

- [ ] Upload ekstensi berbahaya (.php, .jsp, .svg)
- [ ] MIME type bypass
- [ ] Path traversal di nama file
- [ ] File storage location (bisa diakses publik?)

---

## API

- [ ] Undocumented endpoint (JS file, Swagger, Postman collection bocor)
- [ ] HTTP method bypass (GET → PUT/DELETE)
- [ ] Mass assignment lewat API
- [ ] GraphQL introspection aktif di production
- [ ] Rate limiting

---

## Infrastructure

- [ ] Subdomain takeover (CNAME pointing ke service yang sudah dihapus)
- [ ] Open redirect
- [ ] SSRF (Server-Side Request Forgery)
- [ ] CORS misconfiguration
- [ ] Host header injection
- [ ] HTTP Request Smuggling
- [ ] Clickjacking (X-Frame-Options missing)

---

## Info Disclosure

- [ ] Stack trace / debug info bocor
- [ ] `.git` folder exposed (`/.git/config`)
- [ ] `.env` file accessible
- [ ] Backup file (`/backup.zip`, `/db.sql`, dll)
- [ ] API key di JS file / source code
- [ ] Directory listing aktif

---

## Useful Tools

| Tool | Fungsi |
|------|--------|
| `nmap` | Port scan |
| `subfinder` / `amass` | Subdomain enum |
| `ffuf` / `dirsearch` | Directory brute |
| `sqlmap` | SQL injection |
| `burpsuite` | Intercept + manual test |
| `nuclei` | Template-based vuln scan |
| `linkfinder` | Extract URL dari JS |
| `ghauri` | Advanced SQLi |
| `dalfox` | XSS scanner |

---

## Report Template

```
Title   : [Vuln Type] di [Endpoint/Feature]
Severity: Critical / High / Medium / Low / Informational
CVSS    : (optional)

Description:
[Jelaskan vuln secara singkat]

Steps to Reproduce:
1. 
2. 
3. 

Impact:
[Apa dampaknya kalau dieksploitasi]

PoC:
[Screenshot / payload / request-response]

Suggested Fix:
[Rekomendasi perbaikan]
```
