# Threat Simulation Framework — XC Internal Security Toolkit

## Overview

Toolkit ini mensimulasikan attack chain nyata dari perspektif attacker — mulai dari recon pasif sampai exploitation aktif, dijalankan terhadap infrastruktur sendiri untuk mengukur ketahanan sistem.

---

## Threat Scenarios

### TS-01 — External Attacker (Black Box)
**Simulasi:** Attacker tanpa info internal apapun mencoba masuk dari internet.

```
Phase 1: Passive Recon
  → DNS enumeration, IP discovery, ASN lookup
  → Certificate transparency (crt.sh)
  → Subdomain harvest

Phase 2: Active Recon
  → Port scan (TCP/UDP)
  → Service fingerprint + banner grab
  → WAF detection + bypass attempt
  → Tech stack identification

Phase 3: Attack Surface Mapping
  → HTTP endpoint discovery
  → JS bundle analysis → API endpoint leak
  → Robots.txt / sitemap traversal
  → Exposed files (.env, .git, config)

Phase 4: Exploitation Attempt
  → Auth mechanism analysis
  → Injection fuzzing (SQLi, CMDi, SSTI)
  → API auth bypass + IDOR
  → Sensitive data surface

Phase 5: Report
  → Severity classification (CRITICAL/HIGH/MED/LOW/INFO)
  → Evidence + PoC per finding
  → Remediation recommendation
```

---

### TS-02 — Insider Threat (Grey Box)
**Simulasi:** Attacker dengan akun valid (user biasa) mencoba privilege escalation.

```
Phase 1: Auth Analysis
  → Token structure (JWT decode, alg:none test)
  → Cookie flags (Secure, HttpOnly, SameSite)
  → Session fixation + hijacking attempt

Phase 2: Horizontal Privilege Escalation
  → IDOR — akses resource user lain
  → Mass assignment — inject field terlarang
  → API parameter tampering

Phase 3: Vertical Privilege Escalation
  → Role manipulation via token forge
  → Admin endpoint access dengan token user
  → Function-level access control bypass

Phase 4: Data Exfil Simulation
  → Sensitive field exposure per endpoint
  → PII surface mapping
  → Bulk data access (pagination abuse)
```

---

### TS-03 — API Security Assessment
**Simulasi:** Full REST/GraphQL API attack surface review.

```
Phase 1: API Discovery
  → Endpoint enumeration via JS decompile
  → OpenAPI/Swagger spec leak
  → GraphQL introspection

Phase 2: Auth & Rate Limit
  → Unauthenticated endpoint access
  → Rate limit bypass (header spoofing)
  → Token expiry + refresh abuse

Phase 3: Business Logic
  → Price manipulation
  → Quantity tampering
  → Order state machine abuse
  → Coupon/promo stacking

Phase 4: Injection
  → NoSQL injection (MongoDB operator)
  → GraphQL query depth attack
  → Parameter pollution
```

---

### TS-04 — Infrastructure Hardening Check
**Simulasi:** Review konfigurasi server dan network layer.

```
Phase 1: Network Surface
  → Open port inventory
  → Unnecessary service detection
  → Default credential check

Phase 2: Web Server Config
  → Security header audit
  → TLS/SSL configuration
  → CORS policy review
  → Error message information disclosure

Phase 3: Cloud Config (AWS/GCP/Azure)
  → S3 bucket public access
  → Metadata endpoint SSRF
  → IAM role over-permission
```

---

## Severity Matrix

| Level | CVSS | Contoh |
|-------|------|--------|
| **CRITICAL** | 9.0-10.0 | RCE, Unauth admin access, full data dump |
| **HIGH** | 7.0-8.9 | Auth bypass, SQLi, SSRF, IDOR mass |
| **MEDIUM** | 4.0-6.9 | Reflected XSS, info disclosure, weak auth |
| **LOW** | 1.0-3.9 | Missing headers, verbose errors |
| **INFO** | 0.0-0.9 | Tech stack exposure, open ports (filtered) |

---

## Output Format

Setiap simulasi menghasilkan:
- `output/<target>-<timestamp>.json` — machine-readable findings
- Terminal summary dengan severity color coding
- PoC command per finding (siap copy-paste untuk reproduce)
