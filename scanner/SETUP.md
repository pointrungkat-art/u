# XC Scanner — Setup di Android (Termux)

## Install

```bash
# 1. Install Termux dari F-Droid (bukan Play Store)
# 2. Buka Termux, jalankan:

pkg update && pkg upgrade
pkg install python
pip install requests

# 3. Izinkan akses storage
termux-setup-storage
```

## Download Scanner

```bash
curl -o ~/scanner.py https://raw.githubusercontent.com/pointrungkat-art/u/claude/halooo-ullmoe/scanner/scanner.py
```

## Cara Pakai

```bash
# Scan satu file
python ~/scanner.py ~/storage/downloads/namafile.apk

# Scan beberapa file sekaligus
python ~/scanner.py ~/storage/downloads/file1.apk ~/storage/downloads/file2.zip

# Scan semua APK di folder Downloads
python ~/scanner.py ~/storage/downloads/*.apk
```

## (Opsional) VirusTotal — Gratis

1. Daftar di [virustotal.com](https://www.virustotal.com)
2. Masuk → klik avatar → API Key → copy
3. Simpan key:

```bash
echo '{"virustotal_api_key":"PASTE_KEY_DISINI"}' > ~/.xcscan.json
```

Setelah itu scanner otomatis cek ke database 70+ antivirus.

## Arti Hasil Scan

| Hasil | Arti |
|---|---|
| `✓ AMAN` | Tidak ada ancaman, aman dibuka |
| `⚠ MENCURIGAKAN` | Hati-hati, cek dulu |
| `✕ BERBAHAYA` | JANGAN BUKA — hapus file |

## Yang Dicek

- **Signature scan** — pattern string keylogger di dalam file
- **APK permission** — izin berbahaya seperti akses keyboard, SMS, mic
- **Service berbahaya** — AccessibilityService, InputMethodService
- **VirusTotal** — cek hash ke database 70+ antivirus (butuh API key)
