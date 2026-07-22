# Hall of Fame — XC Hacking Hub

> Setiap target yang masuk sini = udah di-DAR DER DOR sampai tuntas.

---

## Statistik

| Metric | Count |
|--------|-------|
| Target Hacked | 2 |
| Total Findings | 8 |
| Critical | 2 |
| High | 3 |
| Medium | 3 |

---

## #1 — shiroine.web.id

| Field | Detail |
|-------|--------|
| Target | `shiroine.web.id` |
| Date | 2026-07-19 |
| Type | Web App (WhatsApp Bot SaaS) |
| Stack | Node.js · Express · Midtrans Payment · REST API |
| Findings | **7** — 2 Critical · 2 High · 3 Medium |
| Status | Reported |

### Findings

| # | Severity | Finding | Impact |
|---|----------|---------|--------|
| F-01 | **CRITICAL** | Unauthenticated Price Manipulation | Beli paket Premium harga bebas — endpoint payment `create-transaction` tanpa auth, amount dari klien tanpa validasi server |
| F-06 | **CRITICAL** | Broken Authentication / Auth Bypass | `Authorization: Bearer null` bypass auth — server cek keberadaan header tapi tidak validasi isi |
| F-02 | **HIGH** | Server Key Metadata Leaked | Error response bocorkan prefix + panjang Midtrans server key |
| F-03 | **HIGH** | Webhook Signature Hash Partially Leaked | Error webhook expose 10 char pertama expected signature hash |
| F-07 | **HIGH** | Sensitive Data Exposure via Auth Bypass | Via F-06 → akses list owner/sub-owner + WhatsApp numbers + statistik internal bot (296.884+ pesan) |
| F-04 | **MEDIUM** | Midtrans Sandbox Mode on Production | Health endpoint publik konfirmasi payment gateway masih sandbox |
| F-05 | **MEDIUM** | Success Page Client-Side Only | Halaman sukses pembayaran bisa diakses tanpa verifikasi server |

### Kill Chain
```
Recon → Auth Bypass (Bearer null) → Data Exposure → Payment Manipulation → Full Compromise
```

---

## #2 — cloudways.com

| Field | Detail |
|-------|--------|
| Target | `cloudways.com` / `api.cloudways.com` |
| Date | 2026-07-20 |
| Program | Bugcrowd |
| Type | Cloud Hosting Platform (Managed) |
| Stack | AngularJS · Laravel · Cloudflare WAF · REST API |
| Findings | **1** — 1 High |
| Status | Reported |

### Findings

| # | Severity | Finding | Impact |
|---|----------|---------|--------|
| C-01 | **HIGH** | CORS Misconfiguration — Origin Reflection + Credentials | `api.cloudways.com` reflects arbitrary Origin header dengan `Access-Control-Allow-Credentials: true` + semua HTTP methods allowed. Endpoint `/api/v1/user/api` (API key management) vulnerable — attacker bisa steal API keys via malicious site jika victim logged in. Upgradeable ke CRITICAL jika XSS ditemukan di `*.cloudways.com` |

### Attack Surface Notes
- `toastr.js` renders `v.message` as raw HTML — potential stored XSS sink
- `$sce.trustAsHtml()` digunakan di confirmation dialogs — bypasses AngularJS sanitization
- `ng-bind-html` directive di templates — potential CSTI vector
- Cloudflare WAF memblokir sebagian besar XSS payloads

### Kill Chain
```
CORS Misconfig → Steal API Keys → Account Takeover (if chained with XSS)
```

---

## Legend

| Severity | Color | CVSS Range |
|----------|-------|------------|
| CRITICAL | 🔴 | 9.0 – 10.0 |
| HIGH | 🟠 | 7.0 – 8.9 |
| MEDIUM | 🟡 | 4.0 – 6.9 |
| LOW | 🔵 | 0.1 – 3.9 |
| INFO | ⚪ | 0.0 |

---

*XC Hacking Hub · Hall of Fame · Last updated: 2026-07-22*
