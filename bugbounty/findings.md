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

---

## cbt.mimikridev.com · 2026-07-22

**Total:** 12 findings &nbsp;|&nbsp; 2 Critical &nbsp;·&nbsp; 3 High &nbsp;·&nbsp; 7 Medium

**Stack:** PHP · MySQL · LiteSpeed · Cloudflare · Materialize 5.0
**Type:** CBT / Exam Browser Client Platform

---

### 🔴 CRITICAL

| # | Finding |
|---|---------|
| C-01 | **IDOR — Cross-Account URL Deletion via GET** — `url-del.php?id=<hex>` tidak memverifikasi kepemilikan. User manapun bisa hapus exam URL milik user lain. Confirmed: Account 2 berhasil hapus URL Account 1 (id: 8dceb6). |
| C-02 | **IDOR — Cross-Account URL Modification** — `url-update.php?id=<hex>` tanpa ownership check. User lain bisa ubah nama, link, timer exam URL milik sekolah lain. Confirmed: URL diubah ke "HACKED_BY_IDOR" → `https://hacked.example.com`. Impact: redirect siswa ke phishing page. |

---

### 🟠 HIGH

| # | Finding |
|---|---------|
| H-01 | **No CSRF Protection** — Semua form tanpa CSRF token: settings, password change, URL add/delete/update. Semua operasi state-changing exploitable via CSRF. |
| H-02 | **CSRF via GET on Delete** — URL deletion via GET request. Exploitable via `<img src>` tag — one-click silent deletion tanpa user consent. |
| H-03 | **Broken Password Reset** — `reset-password.php` accessible tanpa token. Form hanya punya password + cpassword, no hidden token field. Backend (process.php:789) expect token tapi form tidak kirim. |

---

### 🟡 MEDIUM

| # | Finding |
|---|---------|
| M-01 | **Server Path + Internal IP Disclosure** — PHP errors expose: `/www/wwwroot/172.93.219.140/cbt.mimikridev.com/` — full filesystem path + internal IP. |
| M-02 | **SQL Error Disclosure** — `mysqli_sql_exception: Column 'img_logo' cannot be null` di setting.php:52 — reveal database schema, column names, NOT NULL constraints. |
| M-03 | **PHP Debug in Production** — FILTER_SANITIZE_STRING deprecated, htmlspecialchars() warnings, Undefined array key notices semua visible di response. |
| M-04 | **Missing HTTP Security Headers** — No X-Frame-Options, CSP, X-Content-Type-Options, HSTS, Referrer-Policy, Permissions-Policy. Clickjacking possible. |
| M-05 | **Session Cookie Missing Flags** — Initial PHPSESSID tanpa Secure, HttpOnly, SameSite flags. |
| M-06 | **Predictable URL IDs** — 6-char hex IDs (16.7M possibilities) brute-forceable. Combined with IDOR = enumerate + modify semua URL di platform. |
| M-07 | **Open Registration Without Email Verification** — Account langsung aktif tanpa verifikasi email. |

---

*Hacking XC Hub · Security Assessment · 2026-07-22*

---

## tryout.ilmupedia.co.id — 2026-07-23

**Target:** Ilmupedia Tryout (UTBK/SNBT CBT platform by Telkomsel)  
**Assessment:** Full JACKPOT `/F`

| # | Severity | Title | Status |
|---|----------|-------|--------|
| 1 | CRITICAL | WhatsApp Login — No Rate Limit, Verification Code Exposed | Confirmed |
| 2 | CRITICAL | OTP Brute Force via Session Refresh (Rate Limit Bypass) | Confirmed |
| 3 | HIGH | CIAM Internal Error Disclosure (500 → service name leaked) | Confirmed |
| 4 | HIGH | Auth Tokens in localStorage (XSS → Full Account Takeover) | Confirmed |
| 5 | MEDIUM | Sentry DSN Exposed in Public JS Bundle | Confirmed |
| 6 | MEDIUM | WA Admin Bot Number Exposed in API Response (+6285172127033) | Confirmed |
| 7 | MEDIUM | Backend Stack Disclosure (Gunicorn/Python, AWS ALB/CF) | Confirmed |
| 8 | INFO | Public API Endpoints Expose Platform Metadata | Confirmed |

**Report:** `bugbounty/tryout.ilmupedia.co.id.md`
