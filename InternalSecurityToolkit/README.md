# XC Internal Security Toolkit

> Full-stack penetration testing & threat simulation framework — internal use.

## Stack
- Python 3 (stdlib + curl) — no heavy deps
- Modular: tiap komponen berdiri sendiri
- Output: terminal ANSI + JSON report di `output/`

## Struktur

```
InternalSecurityToolkit/
├── README.md
├── AUTHORIZED_USE_ONLY.txt
├── toolkit.py              ← entry point utama
├── modules/
│   ├── recon.py            ← surface recon + fingerprint
│   ├── portscanner.py      ← TCP port scanner + banner grab
│   ├── webprobe.py         ← HTTP attack surface mapper
│   ├── authtest.py         ← auth mechanism tester
│   ├── injector.py         ← injection fuzzer (SQLi, CMDi, SSTI)
│   ├── apifuzz.py          ← REST/GraphQL API fuzzer
│   └── reporter.py         ← JSON + terminal report generator
├── docs/
│   └── THREAT_SIMULATION.md
└── output/                 ← hasil scan tersimpan di sini
```

## Usage

```bash
# Full scan satu target
python3 toolkit.py --target https://target.com --full

# Mode spesifik
python3 toolkit.py --target https://target.com --module recon
python3 toolkit.py --target https://target.com --module portscanner --ports 80,443,8080,8443
python3 toolkit.py --target https://target.com --module webprobe
python3 toolkit.py --target https://target.com --module authtest
python3 toolkit.py --target https://target.com --module injector
python3 toolkit.py --target https://target.com --module apifuzz

# Output ke file
python3 toolkit.py --target https://target.com --full --output output/report.json
```

## Modules

| Module | Fungsi |
|--------|--------|
| `recon` | DNS, IP, ASN, geo, CDN detect, subdomain harvest |
| `portscanner` | TCP scan, banner grab, service detect |
| `webprobe` | HTTP headers, WAF, tech stack, path discovery, JS analysis |
| `authtest` | Login brute, token analysis, session fixation, cookie flags |
| `injector` | SQLi, CMDi, SSTI, XSS, path traversal, XXE |
| `apifuzz` | REST endpoint discovery, auth bypass, IDOR, rate limit |
| `reporter` | Compile semua findings → JSON + terminal summary |
