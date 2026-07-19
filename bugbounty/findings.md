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
