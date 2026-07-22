# Hall of Fame — XC Hacking Hub

> Setiap target yang masuk sini = udah di-DAR DER DOR sampai tuntas.
> No target is safe. No system is immune.

---

## Statistik

| Metric | Count |
|--------|-------|
| Target Hacked | **4** |
| Total Findings | **28** |
| Critical | **7** |
| High | **9** |
| Medium | **12** |
| JACKPOT Chains | **2** |

---

## Scoreboard

| # | Target | Date | Findings | Tier | Best Hit |
|---|--------|------|----------|------|----------|
| 1 | **BimaSoft (pb.app.web.id)** | 2026-07-20 | 3C · 3H · 2M | JACKPOT | Unauth read+write 1,816 emails + plaintext passwords |
| 2 | **shiroine.web.id** | 2026-07-19 | 2C · 2H · 3M | JACKPOT | Auth bypass `Bearer null` + price manipulation |
| 3 | **cbt.mimikridev.com** | 2026-07-22 | 2C · 3H · 7M | CRITICAL | IDOR delete+modify exam URLs across accounts |
| 4 | **cloudways.com** | 2026-07-20 | 1H | HIGH | CORS origin reflection + credential theft |

---

## #1 — BimaSoft / pb.app.web.id (JACKPOT)

| Field | Detail |
|-------|--------|
| Target | `admin-cbt.code.app.web.id` → `pb.app.web.id` (backend) |
| Owner | **BimaSoft** (`bimasoft.web.id`) |
| Date | 2026-07-20 |
| Type | CBT Platform (Computer Based Test) — ujian online sekolah |
| Stack | PocketBase · GitHub Pages SPA · Vue.js |
| Discovery | JS decompile `core-C3bGrs1O.js` → leaked backend URL |
| Findings | **8** — 3 Critical · 3 High · 2 Medium |
| Report | `bugbounty/report-pb.app.web.id.html` |
| Status | JACKPOT CONFIRMED |

### Findings

| # | Severity | Finding | Impact |
|---|----------|---------|--------|
| C-01 | **CRITICAL** | Unauthenticated Mass Data Read | SEMUA koleksi PocketBase terbuka tanpa auth — DataUsers **1,816** records (email guru + kode sekolah), DataUjian **4,675** records (data ujian + email guru), DataPengawas (password plaintext), DataJawaban (jawaban & skor siswa). Semua bisa diambil `curl` biasa |
| C-02 | **CRITICAL** | Unauthenticated Write — Fake Proctor Created | POST ke DataPengawas + DataUsers berhasil tanpa token. Akun pengawas palsu berhasil dibuat real-time selama pentest |
| C-03 | **CRITICAL** | Plaintext Password Storage | DataPengawas menyimpan password tanpa hashing. Terekspos langsung via API. Confirmed: `Nurul:Nurul12345` |
| H-01 | **HIGH** | Admin Panel Exposed | `pb.app.web.id/_/` returns 200 OK — PocketBase superadmin GUI publik, auth endpoint terbuka untuk brute force tanpa lockout |
| H-02 | **HIGH** | Client-Side Role Control | Role auth via `localStorage.userType` — ubah ke `"admin"` di DevTools → instant privilege escalation |
| H-03 | **HIGH** | JWT di localStorage | Token PocketBase plaintext di `localStorage.pocketbase_auth` — XSS → steal token → full account takeover |
| M-01 | **MEDIUM** | WAF Bypass — 14 Teknik Berhasil | GitHub CDN WAF bypass: Localhost spoof, Internal IP spoof, User-Agent spoofing (Googlebot, Bingbot), Cache bypass |
| M-02 | **MEDIUM** | Encrypted Answer Key Exposed | DataKunci — kunci jawaban (base64/encrypted) bisa diambil tanpa auth |

### Kill Chain
```
JS Decompile → Discover pb.app.web.id backend
  → curl (no auth) → GET DataPengawas → plaintext password Nurul:Nurul12345
  → POST DataPengawas → fake proctor injected, langsung aktif
  → GET DataUjian → 4,675 kode ujian + email guru
  → GET DataUsers → 1,816 email guru + kode sekolah
  → localStorage.userType = "admin" → privilege escalation
  → FULL SYSTEM COMPROMISE — read, write, impersonate, escalate
```

### Data Exposure Summary
- **1,816** guru/teacher emails + school codes
- **4,675** exam records + answer data
- Plaintext proctor passwords
- Student answer sheets + scores
- Encrypted answer keys

---

## #2 — shiroine.web.id (JACKPOT)

| Field | Detail |
|-------|--------|
| Target | `shiroine.web.id` |
| Date | 2026-07-19 |
| Type | Web App (WhatsApp Bot SaaS) |
| Stack | Node.js · Express · Midtrans Payment · REST API |
| Findings | **7** — 2 Critical · 2 High · 3 Medium |
| Status | JACKPOT CONFIRMED |

### Findings

| # | Severity | Finding | Impact |
|---|----------|---------|--------|
| F-01 | **CRITICAL** | Unauthenticated Price Manipulation | Endpoint payment `create-transaction` tanpa auth, amount dari klien tanpa validasi server — beli paket Premium harga bebas (Rp 0) |
| F-06 | **CRITICAL** | Broken Authentication / Auth Bypass | `Authorization: Bearer null` bypass auth — server cek keberadaan header tapi tidak validasi isi. Semua protected endpoint terbuka |
| F-02 | **HIGH** | Server Key Metadata Leaked | Error response bocorkan prefix + panjang Midtrans server key di field diagnostic |
| F-03 | **HIGH** | Webhook Signature Hash Partially Leaked | Error webhook expose 10 char pertama expected signature hash |
| F-07 | **HIGH** | Sensitive Data Exposure via Auth Bypass | Via F-06 → akses list owner & sub-owner + nomor WhatsApp + statistik internal bot (296.884+ pesan, traffic chart) |
| F-04 | **MEDIUM** | Midtrans Sandbox Mode on Production | Health endpoint publik konfirmasi payment gateway masih sandbox mode |
| F-05 | **MEDIUM** | Success Page Client-Side Only | Halaman sukses pembayaran bisa diakses tanpa verifikasi server-side |

### Kill Chain
```
Recon → Bearer null Auth Bypass → All Protected Endpoints Open
  → Owner/Sub-owner data + WA numbers exposed
  → Payment endpoint no auth → price manipulation → Rp 0 Premium
  → Server key metadata + webhook hash leaked
  → FULL COMPROMISE — data, payment, auth semua jebol
```

---

## #3 — cbt.mimikridev.com (CRITICAL)

| Field | Detail |
|-------|--------|
| Target | `cbt.mimikridev.com` |
| Owner | **mimikridev.com** |
| Date | 2026-07-22 |
| Type | CBT Platform (Exam Browser Client) — lock browser untuk ujian online |
| Stack | PHP · MySQL · LiteSpeed · Cloudflare · Materialize 5.0 |
| Server IP | `172.93.219.140` (leaked via PHP errors) |
| Findings | **12** — 2 Critical · 3 High · 7 Medium |
| Report | `bugbounty/report-cbt.mimikridev.com.html` |
| Status | CRITICAL CONFIRMED |

### Findings

| # | Severity | Finding | Impact |
|---|----------|---------|--------|
| C-01 | **CRITICAL** | IDOR — Cross-Account URL Delete (GET) | `url-del.php?id=<hex>` tanpa ownership check. User manapun bisa hapus exam URL milik sekolah lain. Confirmed: Account 2 hapus URL Account 1 |
| C-02 | **CRITICAL** | IDOR — Cross-Account URL Modify | `url-update.php?id=<hex>` tanpa ownership check. Exam URL bisa diubah ke phishing page. Confirmed: URL diubah ke "HACKED_BY_IDOR" |
| H-01 | **HIGH** | No CSRF Protection | Semua form tanpa CSRF token — settings, password change, URL CRUD |
| H-02 | **HIGH** | CSRF via GET Delete | URL deletion via GET — exploitable via `<img src>` tag |
| H-03 | **HIGH** | Broken Password Reset | `reset-password.php` accessible tanpa valid token, form tanpa hidden token field |
| M-01 | **MEDIUM** | Server Path + Internal IP | PHP errors expose `/www/wwwroot/172.93.219.140/cbt.mimikridev.com/` |
| M-02 | **MEDIUM** | SQL Error Disclosure | `mysqli_sql_exception` reveal database schema + column names |
| M-03 | **MEDIUM** | PHP Debug in Production | Deprecation, warnings, fatal errors semua visible |
| M-04 | **MEDIUM** | Missing Security Headers | No X-Frame-Options, CSP, HSTS — clickjacking possible |
| M-05 | **MEDIUM** | Session Cookie No Flags | PHPSESSID tanpa Secure, HttpOnly, SameSite |
| M-06 | **MEDIUM** | Predictable URL IDs | 6-char hex (16.7M space) — brute-forceable + IDOR = mass compromise |
| M-07 | **MEDIUM** | Open Registration | Account tanpa email verification — instant access |

### Kill Chain
```
Register account (no email verify) → Login
  → Brute-force 6-char hex URL IDs via url-update.php
  → IDOR: modify exam URLs → redirect students to phishing
  → Alternative: IDOR delete → destroy all exam URLs
  → CSRF: <img src=url-del.php?id=TARGET> → silent deletion
  → Mass exam hijack — redirect, delete, or disrupt at scale
```

---

## #4 — cloudways.com (Bugcrowd)

| Field | Detail |
|-------|--------|
| Target | `cloudways.com` / `api.cloudways.com` |
| Date | 2026-07-20 |
| Program | Bugcrowd |
| Type | Cloud Hosting Platform (Managed) |
| Stack | AngularJS · Laravel · Cloudflare WAF · REST API |
| Findings | **1** — 1 High |
| Status | Reported to Bugcrowd |

### Findings

| # | Severity | Finding | Impact |
|---|----------|---------|--------|
| C-01 | **HIGH** | CORS Misconfiguration — Origin Reflection + Credentials | `api.cloudways.com` reflects arbitrary Origin dengan `Access-Control-Allow-Credentials: true` + semua HTTP methods. Endpoint `/api/v1/user/api` (API key management) vulnerable — steal API keys via malicious site. Upgradeable ke CRITICAL jika XSS ditemukan |

### Attack Surface (Unexploited — Blocked by WAF)
- `toastr.js` renders `v.message` as raw HTML — potential stored XSS sink
- `$sce.trustAsHtml()` di confirmation dialogs — bypasses AngularJS sanitization
- `ng-bind-html` directive — potential CSTI vector
- Cloudflare WAF blocks most XSS payloads — need bypass

### Kill Chain
```
CORS Misconfig → Malicious Site → Steal API Keys → Account Takeover
(+ XSS chain = CRITICAL upgrade)
```

---

## Timeline

```
2026-07-19  shiroine.web.id     5 findings → +2 jackpot → 7 total (2C·2H·3M)
2026-07-20  pb.app.web.id       8 findings JACKPOT (3C·3H·2M) — BimaSoft owned
2026-07-20  cloudways.com       1 finding HIGH — CORS (Bugcrowd)
2026-07-22  cbt.mimikridev.com  12 findings CRITICAL (2C·3H·7M) — IDOR mass exam hijack
```

---

## Legend

| Tier | Meaning |
|------|---------|
| JACKPOT | Full system compromise — critical chain, multiple vectors, data exposed |
| CRITICAL | Single critical finding atau high-impact chain |
| HIGH | Significant vulnerability, exploitable tapi belum full chain |

| Severity | Icon | CVSS Range |
|----------|------|------------|
| CRITICAL | 🔴 | 9.0 – 10.0 |
| HIGH | 🟠 | 7.0 – 8.9 |
| MEDIUM | 🟡 | 4.0 – 6.9 |
| LOW | 🔵 | 0.1 – 3.9 |
| INFO | ⚪ | 0.0 |

---

*XC Hacking Hub · Hall of Fame · Last updated: 2026-07-22*
*No target is safe. DAR DER DOR.*
