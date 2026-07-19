#!/usr/bin/env python3
# XC Scanner - Anti Keylogger File Scanner
# Android (Termux) Compatible
# Usage: python scanner.py <file> [file2 ...]

import os, sys, hashlib, zipfile, json, re
from pathlib import Path

# ┌─────────────────────────────────────┐
# │         KEYLOGGER SIGNATURES        │
# └─────────────────────────────────────┘
SIGNATURES = [
    # Windows keylogger APIs
    b"GetAsyncKeyState", b"SetWindowsHookEx", b"WH_KEYBOARD_LL", b"WH_KEYBOARD",
    b"GetKeyState", b"keylogger", b"keystroke", b"keyCapture",
    # Python keylogger libs
    b"pynput.keyboard", b"pyHook", b"keyboard.on_press", b"keyboard.hook",
    # Android keylogger patterns
    b"android.permission.READ_INPUT_STATE", b"KeyEvent.ACTION_DOWN",
    b"onKeyDown", b"dispatchKeyEvent",
    # Exfil patterns
    b"smtp.gmail.com", b"sendmail", b"upload_keylog", b"send_log",
]

# ┌─────────────────────────────────────┐
# │      APK DANGEROUS PERMISSIONS      │
# └─────────────────────────────────────┘
APK_PERMS = {
    "READ_INPUT_STATE":           ("CRITICAL", "Bisa baca semua input keyboard"),
    "BIND_ACCESSIBILITY_SERVICE": ("HIGH",     "Bisa monitor semua aktivitas layar"),
    "BIND_INPUT_METHOD":          ("HIGH",     "Bisa intercept keyboard"),
    "CAPTURE_SECURE_VIDEO_OUTPUT":("HIGH",     "Bisa capture layar"),
    "READ_FRAME_BUFFER":          ("HIGH",     "Bisa baca konten layar"),
    "REQUEST_INSTALL_PACKAGES":   ("HIGH",     "Bisa install app lain diam-diam"),
    "RECORD_AUDIO":               ("MEDIUM",   "Bisa rekam mikrofon"),
    "RECEIVE_BOOT_COMPLETED":     ("MEDIUM",   "Autorun saat HP nyala"),
    "READ_CONTACTS":              ("MEDIUM",   "Baca kontak"),
    "READ_CALL_LOG":              ("MEDIUM",   "Baca log panggilan"),
    "ACCESS_FINE_LOCATION":       ("MEDIUM",   "Lacak lokasi GPS"),
    "READ_SMS":                   ("HIGH",     "Baca SMS — rawan OTP theft"),
    "RECEIVE_SMS":                ("HIGH",     "Intercept SMS masuk"),
    "PROCESS_OUTGOING_CALLS":     ("HIGH",     "Monitor panggilan keluar"),
}

THREAT_WEIGHT = {"CRITICAL": 5, "HIGH": 3, "MEDIUM": 1}

# ┌─────────────────────────────────────┐
# │             COLORS                  │
# └─────────────────────────────────────┘
R = "\033[0m"
RED  = "\033[91m"; YLW = "\033[93m"; GRN = "\033[92m"
CYN  = "\033[96m"; PRP = "\033[95m"; BLD = "\033[1m"


def banner():
    print(f"""{PRP}{BLD}
 ██╗  ██╗ ██████╗    ███████╗ ██████╗ █████╗ ███╗
 ╚██╗██╔╝██╔════╝    ██╔════╝██╔════╝██╔══██╗████╗
  ╚███╔╝ ██║         ███████╗██║     ███████║██╔██╗
  ██╔██╗ ██║         ╚════██║██║     ██╔══██║██║╚██╗
 ██╔╝╚██╗╚██████╗    ███████║╚██████╗██║  ██║██║  ╚╝
 ╚═╝  ╚═╝ ╚═════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝
{R}{CYN}    Anti-Keylogger File Scanner | by XC{R}
""")


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sig_scan(path):
    hits = []
    try:
        with open(path, "rb") as f:
            data = f.read()
        data_low = data.lower()
        for sig in SIGNATURES:
            if sig.lower() in data_low:
                hits.append(sig.decode(errors="replace"))
    except Exception:
        pass
    return hits


def apk_scan(path):
    perms_found = {}
    services = []
    try:
        with zipfile.ZipFile(path, "r") as z:
            names = z.namelist()
            if "AndroidManifest.xml" not in names:
                return perms_found, services
            manifest = z.read("AndroidManifest.xml").decode(errors="replace")
            for perm, (lvl, desc) in APK_PERMS.items():
                if perm in manifest:
                    perms_found[perm] = (lvl, desc)
            if "AccessibilityService" in manifest:
                services.append("AccessibilityService — bisa baca semua teks di layar")
            if "InputMethodService" in manifest:
                services.append("InputMethodService — bisa capture input keyboard")
            if "DeviceAdminReceiver" in manifest:
                services.append("DeviceAdminReceiver — minta hak admin perangkat")
    except Exception as e:
        services.append(f"Gagal baca APK: {e}")
    return perms_found, services


def vt_check(sha256, api_key):
    try:
        import requests
        r = requests.get(
            f"https://www.virustotal.com/api/v3/files/{sha256}",
            headers={"x-apikey": api_key},
            timeout=12
        )
        if r.status_code == 404:
            return None, "File belum pernah di-scan di VirusTotal"
        if r.status_code != 200:
            return None, f"VT error {r.status_code}"
        stats = r.json()["data"]["attributes"]["last_analysis_stats"]
        return stats, None
    except ImportError:
        return None, "pip install requests dulu"
    except Exception as e:
        return None, str(e)


def scan(path, api_key=None):
    p = Path(path)
    if not p.exists():
        print(f"{RED}✕ File tidak ditemukan: {path}{R}")
        return

    print(f"\n{CYN}{'━'*52}{R}")
    print(f"{BLD}  FILE : {p.name}{R}")
    print(f"  SIZE : {p.stat().st_size:,} bytes")

    sha = file_hash(p)
    print(f"  SHA256: {sha[:40]}...")
    print(f"{CYN}{'━'*52}{R}")

    threat = 0
    findings = []

    # [1] Signature scan
    print(f"\n{BLD}[1] Signature Scan{R}")
    hits = sig_scan(p)
    if hits:
        for h in hits:
            print(f"  {RED}⚠  {h}{R}")
            threat += 2
            findings.append(f"Sig: {h}")
    else:
        print(f"  {GRN}✓  Tidak ada pattern mencurigakan{R}")

    # [2] APK scan
    if p.suffix.lower() == ".apk":
        print(f"\n{BLD}[2] APK Permission Scan{R}")
        perms, svcs = apk_scan(p)
        if perms:
            for perm, (lvl, desc) in perms.items():
                color = RED if lvl in ("CRITICAL", "HIGH") else YLW
                print(f"  {color}[{lvl}] {perm}{R}")
                print(f"         → {desc}")
                threat += THREAT_WEIGHT[lvl]
                findings.append(f"{lvl}: {perm}")
        else:
            print(f"  {GRN}✓  Tidak ada permission berbahaya{R}")
        if svcs:
            for s in svcs:
                print(f"  {RED}⚠  {s}{R}")
                threat += 3
                findings.append(f"Service: {s}")
    else:
        print(f"\n{BLD}[2] APK Scan{R}  {YLW}(dilewat, bukan .apk){R}")

    # [3] VirusTotal
    print(f"\n{BLD}[3] VirusTotal{R}", end="")
    if api_key:
        print()
        stats, err = vt_check(sha, api_key)
        if err:
            print(f"  {YLW}⚠  {err}{R}")
        elif stats:
            mal  = stats.get("malicious", 0)
            sus  = stats.get("suspicious", 0)
            tot  = sum(stats.values())
            if mal > 0:
                print(f"  {RED}✕  {mal}/{tot} engine deteksi MALICIOUS!{R}")
                threat += mal * 3
                findings.append(f"VT malicious: {mal}/{tot}")
            elif sus > 0:
                print(f"  {YLW}⚠  {sus}/{tot} engine deteksi SUSPICIOUS{R}")
                threat += sus
                findings.append(f"VT suspicious: {sus}/{tot}")
            else:
                print(f"  {GRN}✓  0/{tot} — Clean{R}")
    else:
        print(f"  {YLW}(skip — tambah VT API key di config){R}")

    # ┌─ Verdict ─┐
    print(f"\n{BLD}{'━'*52}")
    if threat == 0:
        print(f"  {GRN}✓  AMAN — Tidak ada ancaman terdeteksi{R}")
    elif threat < 4:
        print(f"  {YLW}⚠  MENCURIGAKAN  (score: {threat}){R}")
        print(f"     Hati-hati, cek manual sebelum dibuka")
    else:
        print(f"  {RED}✕  BERBAHAYA  (score: {threat}){R}")
        print(f"     JANGAN BUKA — hapus file ini!")
    if findings:
        print(f"\n  Temuan:")
        for f in findings:
            print(f"    • {f}")
    print(f"{BLD}{'━'*52}{R}\n")


def load_config():
    cfg_path = Path.home() / ".xcscan.json"
    if cfg_path.exists():
        with open(cfg_path) as f:
            return json.load(f)
    return {}


def main():
    banner()
    cfg = load_config()
    api_key = cfg.get("virustotal_api_key")

    if not api_key:
        print(f"{YLW}Tips: Daftar gratis di virustotal.com → dapat API key")
        print(f"Simpan: echo '{{\"virustotal_api_key\":\"ISI_KEY_DISINI\"}}' > ~/.xcscan.json{R}\n")

    if len(sys.argv) < 2:
        print(f"Usage: python scanner.py <file> [file2 ...]")
        print(f"Contoh: python scanner.py ~/storage/downloads/app.apk")
        sys.exit(0)

    for target in sys.argv[1:]:
        scan(target, api_key)


if __name__ == "__main__":
    main()
