# Hacking XC Hub — Findings Log

## admin-cbt.code.app.web.id / pb.app.web.id · 2026-07-20 🔥 JACKPOT

**Total:** 8 findings &nbsp;|&nbsp; 3 Critical &nbsp;·&nbsp; 3 High &nbsp;·&nbsp; 2 Medium
**Stack:** PocketBase + GitHub Pages SPA
**Backend:** `https://pb.app.web.id` (discovered via JS decompile)
**Report:** [`report-pb.app.web.id.html`](report-pb.app.web.id.html)

---

### 🔴 CRITICAL

| # | Finding |
|---|---------|
| C-01 | **Unauthenticated Mass Data Read** — SEMUA koleksi PocketBase terbuka tanpa auth. DataUsers 1,816 records (email guru + kode sekolah), DataUjian 4,675 records (semua data ujian + email guru), DataPengawas (password plaintext), DataJawaban (jawaban & skor siswa) — semuanya bisa diambil dengan `curl` biasa. |
| C-02 | **Unauthenticated Write — Fake Proctor Created** — POST ke DataPengawas dan DataUsers berhasil tanpa token. Akun pengawas palsu berhasil dibuat real-time selama pentest. |
| C-03 | **Plaintext Password Storage** — DataPengawas menyimpan password dalam field biasa tanpa hashing. Terekspos langsung via API. `Nurul:Nurul12345` confirmed dari response. |

---

### 🟠 HIGH

| # | Finding |
|---|---------|
| H-01 | **Admin Panel Exposed** — `https://pb.app.web.id/_/` mengembalikan 200 OK. GUI PocketBase superadmin dapat diakses publik, auth endpoint terbuka untuk brute force tanpa lockout. |
| H-02 | **Client-Side Role Control** — Role auth dikontrol via `localStorage.userType`. Ubah ke `"admin"` di DevTools → privilege escalation langsung di SPA. |
| H-03 | **JWT di localStorage** — Token PocketBase disimpan plaintext di `localStorage.pocketbase_auth`. XSS → steal token → full account takeover. |

---

### 🟡 MEDIUM

| # | Finding |
|---|---------|
| M-01 | **WAF Bypass — 14 Teknik Berhasil** — WAF (GitHub CDN) bypass dengan Localhost spoof, Internal IP spoof, User-Agent spoofing (Googlebot, Bingbot), Cache bypass, dll. |
| M-02 | **Encrypted Answer Key Exposed** — DataKunci menyimpan kunci jawaban (base64/encrypted) yang dapat diambil tanpa auth. |

---

### Attack Impact Chain
```
curl (no auth)
  → GET DataPengawas → password plaintext Nurul:Nurul12345
  → POST DataPengawas → fake proctor injected, langsung aktif
  → GET DataUjian → 4,675 kode ujian + email guru terekspos
  → GET DataUsers → 1,816 email guru + kode sekolah
  → localStorage.userType = "admin" → privilege escalation di SPA
```

---

*Hacking XC Hub · Responsible Disclosure · 2026-07-20*

---

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

---

## banuacokelat.com — Full Blackbox [2026-08-02]

**Target:** https://banuacokelat.com/
**IP:** 103.153.3.23 (PT Dewa Bisnis Digital, Jakarta — shared hosting)
**Stack:** WordPress + PHP 7.4.33 + LiteSpeed + WooCommerce + Elementor

### 🔴 HIGH

**[H1] No Rate Limit on wp-login.php — Brute Force Terbuka**
- `/wp-login.php` tidak ada CAPTCHA, tidak ada lockout, tidak ada Wordfence
- Username confirmed: `bacokadmin` (via REST API + author redirect + error message)
- Attack: hydra / python script → wordlist → crack password → wp-admin access → plugin upload RCE
- Evidence: 3 rapid login attempts semua 200, tidak ada lockout/delay

**[H2] Username Enumeration — 3 Vector Sekaligus**
- REST API: `GET /wp-json/wp/v2/users` → leak `id:1, slug:bacokadmin, name:bacokadmin`
- Author redirect: `/?author=1` → redirect ke `/author/bacokadmin/`
- Login error: error message beda antara user valid vs invalid ("kata sandi tidak cocok" vs "tidak ada akun")
- Password reset: `/wp-login.php?action=lostpassword` juga beda response untuk user valid/invalid

**[H3] PHP 7.4.33 EOL — No Security Patches**
- PHP 7.4 end of life Desember 2022
- Tidak ada security update sejak 3+ tahun
- Header exposed: `x-powered-by: PHP/7.4.33`

### 🟡 MEDIUM

**[M1] WP REST API User Endpoint Terbuka (Unauthenticated)**
- `GET /wp-json/wp/v2/users` → expose full user list tanpa auth
- Data leaked: id, name, slug, link

**[M2] Upload Directories Accessible — 22 Folder Terbuka**
- `/wp-content/uploads/` + semua subfolder 2024-2026 return 200
- Risk: file sensitif yang di-upload bisa langsung diakses

**[M3] Member Area Attack Surface**
- Endpoints: `/member-area/orders`, `/member-area/profile`, `/member-area/dashboard`
- Belum di-test IDOR pada order/profile endpoints

**[M4] xmlrpc.php Exposed**
- Accessible tapi blocked di network level untuk brute force
- Potential: pingback abuse, SSRF via pingback

### 🔵 INFO
- LiteSpeed bot protection aktif di beberapa path
- Shared hosting: 20+ domain lain di IP yang sama
- Plugin: WooCommerce 10.9.3, Elementor 4.2.1, CF7, Jetpack, Yoast, Akismet
- Satu-satunya admin: `bacokadmin` (ID:1)

### Next Steps
1. Brute force `bacokadmin` dengan wordlist Indonesia (nama+angka common)
2. Test IDOR di `/member-area/orders?id=X`
3. Check Elementor 4.2.1 CVE database
4. Upload dir — scan file-file yang ada
