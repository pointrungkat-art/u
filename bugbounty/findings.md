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

*Hacking XC Hub · Responsible Disclosure · 2026-07-19*
