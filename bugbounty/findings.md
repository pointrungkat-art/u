# Hacking XC Hub — Findings Log

## shiroine.web.id · 2026-07-19

**Total:** 7 findings &nbsp;|&nbsp; 2 Critical &nbsp;·&nbsp; 2 High &nbsp;·&nbsp; 3 Medium

---

### 🔴 CRITICAL

| # | Finding |
|---|---------|
| F-01 | **Unauthenticated Price Manipulation** — endpoint payment create-transaction tidak memerlukan auth dan menerima amount dari klien tanpa validasi sisi-server. Paket Premium apapun bisa dibeli dengan harga bebas. |
| F-06 | **Broken Authentication / Auth Bypass** — `Authorization: Bearer null` membypass autentikasi pada endpoint terproteksi. Server memeriksa keberadaan header tapi tidak memvalidasi isinya. |

---

### 🟠 HIGH

| # | Finding |
|---|---------|
| F-02 | **Server Key Metadata Leaked** — error response membocorkan prefix dan panjang Midtrans server key di field diagnostic. |
| F-03 | **Webhook Signature Hash Partially Leaked** — error message webhook menyertakan 10 karakter pertama dari expected signature hash. |
| F-07 | **Sensitive Data Exposure via Auth Bypass** — melalui F-06, attacker dapat mengakses daftar owner & sub-owner sistem beserta nomor WhatsApp, serta statistik internal bot (296.884+ pesan, traffic chart). |

---

### 🟡 MEDIUM

| # | Finding |
|---|---------|
| F-04 | **Midtrans Sandbox Mode Active on Production** — health endpoint publik mengkonfirmasi payment gateway masih berjalan di sandbox mode. |
| F-05 | **Success Page Client-Side Only** — halaman sukses pembayaran dapat diakses langsung tanpa verifikasi server-side. |

---

*Hacking XC Hub · Responsible Disclosure · 2026-07-19*


---

## https://sidegigx.id/ · 2026-07-19 14:54:43

**Total:** 6 findings &nbsp;|&nbsp; 1 Critical &nbsp;·&nbsp; 0 High &nbsp;·&nbsp; 2 Medium &nbsp;·&nbsp; 3 Low

### 🔴 CRITICAL

- **[JUICY_FILE]** `https://sidegigx.id/wp-config.php`
  - HTTP 403 → wp-config.php

### 🟡 MED

- **[JUICY_FILE]** `https://sidegigx.id/sitemap.xml`
  - HTTP 200 → sitemap.xml
  - Evidence: `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url>
<loc>https://sidegigx.id/</loc>
<lastmod>2026-07-19T13:18:11.078Z</lastmod>
<changefreq>weekly`
- **[JUICY_FILE]** `https://sidegigx.id/robots.txt`
  - HTTP 200 → robots.txt
  - Evidence: `# As a condition of accessing this website, you agree to abide by the following
# content signals:

# (a)  If a Content-Signal = yes, you may collect content for the corresponding
#      use.
# (b)  I`

### 🔵 LOW

- **[MISSING_SECURITY_HEADERS]** `https://sidegigx.id/`
  - Missing: X-Frame-Options, X-Content-Type-Options, Content-Security-Policy, Strict-Transport-Security, X-XSS-Protection, Referrer-Policy, Permissions-Policy
- **[TECH_LEAK]** `https://sidegigx.id/`
  - Server: cloudflare
- **[TECH_LEAK]** `https://sidegigx.id/`
  - X-Powered-By: Next.js



---

## https://sidegigx.id/ · 2026-07-19 23:18:07

**Total:** 7 findings &nbsp;|&nbsp; 1 Critical &nbsp;·&nbsp; 0 High &nbsp;·&nbsp; 3 Medium &nbsp;·&nbsp; 3 Low

### 🔴 CRITICAL

- **[JUICY_FILE]** `https://sidegigx.id/wp-config.php`
  - HTTP 403 → wp-config.php

### 🟡 MED

- **[JUICY_FILE]** `https://sidegigx.id/sitemap.xml`
  - HTTP 200 → sitemap.xml
  - Evidence: `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url>
<loc>https://sidegigx.id/</loc>
<lastmod>2026-07-19T22:22:07.710Z</lastmod>
<changefreq>weekly`
- **[JUICY_FILE]** `https://sidegigx.id/robots.txt`
  - HTTP 200 → robots.txt
  - Evidence: `# As a condition of accessing this website, you agree to abide by the following
# content signals:

# (a)  If a Content-Signal = yes, you may collect content for the corresponding
#      use.
# (b)  I`
- **[NO_RATE_LIMIT]** `https://sidegigx.id/`
  - 15 rapid requests — no 429/503 detected. Potential brute-force vector.

### 🔵 LOW

- **[MISSING_SECURITY_HEADERS]** `https://sidegigx.id/`
  - Missing: X-Frame-Options, X-Content-Type-Options, Content-Security-Policy, Strict-Transport-Security, X-XSS-Protection, Referrer-Policy, Permissions-Policy
- **[TECH_LEAK]** `https://sidegigx.id/`
  - Server: cloudflare
- **[TECH_LEAK]** `https://sidegigx.id/`
  - X-Powered-By: Next.js

