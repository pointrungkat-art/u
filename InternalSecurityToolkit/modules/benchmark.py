"""Benchmark Runner — HTTP, API, TCP, UDP, DB — full payload barrage with metrics"""
import socket, threading, time, json, re, subprocess, concurrent.futures, statistics
from modules import payloadgen

COLORS = {
    "RED":    "\033[1;31m", "YELLOW": "\033[1;33m", "GREEN":  "\033[1;32m",
    "CYAN":   "\033[1;36m", "PURPLE": "\033[1;35m", "BLUE":   "\033[1;34m",
    "BOLD":   "\033[1m",    "DIM":    "\033[2m",    "RESET":  "\033[0m",
}
def c(col, txt): return f"{COLORS.get(col,'')}{txt}{COLORS['RESET']}"
def log(msg, col="CYAN"):
    print(c("DIM", f"[{time.strftime('%H:%M:%S')}]") + " " + c(col, msg))

# ── Metrics ───────────────────────────────────────────────────────────────────

class Metrics:
    def __init__(self):
        self._lock   = threading.Lock()
        self.latencies = []
        self.status_codes = {}
        self.errors   = 0
        self.success  = 0
        self.total    = 0

    def record(self, latency_ms, status=0, error=False):
        with self._lock:
            self.total += 1
            if error:
                self.errors += 1
            else:
                self.success += 1
                self.latencies.append(latency_ms)
                self.status_codes[status] = self.status_codes.get(status, 0) + 1

    def summary(self, elapsed_s):
        lat = sorted(self.latencies)
        def pct(p):
            if not lat: return 0
            idx = max(0, int(len(lat) * p / 100) - 1)
            return round(lat[idx], 2)
        return {
            "total":      self.total,
            "success":    self.success,
            "errors":     self.errors,
            "error_rate": round(self.errors / max(self.total, 1) * 100, 2),
            "rps":        round(self.total / max(elapsed_s, 0.001), 2),
            "latency_ms": {
                "min":  round(min(lat), 2) if lat else 0,
                "mean": round(statistics.mean(lat), 2) if lat else 0,
                "p50":  pct(50),
                "p95":  pct(95),
                "p99":  pct(99),
                "max":  round(max(lat), 2) if lat else 0,
            },
            "status_codes": self.status_codes,
        }

# ── HTTP benchmark ────────────────────────────────────────────────────────────

def _http_request(url, method, body, content_type, headers, timeout):
    cmd = ["curl","-sk","--max-time",str(timeout),"-L","-X",method]
    if body:
        cmd += ["-d", body if isinstance(body,str) else body.decode(errors='replace'),
                "-H", f"Content-Type: {content_type}"]
    for k,v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    cmd += ["-w", "\n__STATUS__%{http_code}__TIME__%{time_total}", "-o", "/dev/null", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+2)
        m = re.search(r"__STATUS__(\d+)__TIME__([0-9.]+)", r.stdout)
        if m:
            return int(m.group(1)), round(float(m.group(2)) * 1000, 2)
        return 0, 0.0
    except:
        return 0, 0.0

def bench_http(target, concurrency=20, duration=10, payloads=None, method="GET"):
    base = re.sub(r'/$','',target)
    log(f"HTTP benchmark → {base}  workers={concurrency}  duration={duration}s", "YELLOW")
    pool  = payloads or payloadgen.http_payloads(30)
    met   = Metrics()
    stop  = threading.Event()
    pool_cycle = pool * (1000 // max(len(pool), 1) + 1)

    def worker(idx):
        i = idx
        while not stop.is_set():
            ct, body = pool_cycle[i % len(pool_cycle)]
            t0 = time.time()
            code, _ = _http_request(base, method, body, ct, {}, timeout=8)
            lat = (time.time() - t0) * 1000
            met.record(lat, code, error=(code == 0))
            i += concurrency

    t_start = time.time()
    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(concurrency)]
    for t in threads: t.start()
    time.sleep(duration)
    stop.set()
    for t in threads: t.join(timeout=2)
    elapsed = time.time() - t_start

    s = met.summary(elapsed)
    log(f"HTTP done — rps={s['rps']}  p99={s['latency_ms']['p99']}ms  err={s['error_rate']}%", "GREEN")
    return {"vector":"http","target":base,"config":{"concurrency":concurrency,"duration":duration},"metrics":s}

# ── API benchmark ─────────────────────────────────────────────────────────────

def bench_api(target, token=None, concurrency=15, duration=10):
    base  = re.sub(r'/$','',target)
    log(f"API benchmark → {base}  workers={concurrency}  duration={duration}s", "YELLOW")
    met   = Metrics()
    stop  = threading.Event()
    pl    = payloadgen.api_payloads()
    auth  = {"Authorization": f"Bearer {token}"} if token else {}

    # Build a flat task list: (method, endpoint, body, headers)
    tasks = []
    rest_eps = ["/api/users","/api/products","/api/orders","/api/profile","/api/me"]
    for ep in rest_eps:
        tasks.append(("GET",  base+ep, None, auth))
        tasks.append(("POST", base+ep, json.dumps(payloadgen.api_rest_payload("POST")), {**auth,"Content-Type":"application/json"}))
    for ma in pl["mass_assign"]:
        tasks.append(("POST", base+"/api/register", json.dumps(ma), {"Content-Type":"application/json"}))
    for ah in pl["auth_bypass"]:
        tasks.append(("GET", base+"/api/admin", None, ah))
    for gql in pl["graphql"][:4]:
        tasks.append(("POST", base+"/graphql", gql, {"Content-Type":"application/json"}))
    for uid in pl["idor_ids"][:10]:
        tasks.append(("GET", base+f"/api/users/{uid}", None, auth))

    def worker(idx):
        i = idx
        while not stop.is_set():
            method, url, body, hdrs = tasks[i % len(tasks)]
            t0 = time.time()
            code, _ = _http_request(url, method, body, "application/json", hdrs, timeout=8)
            lat = (time.time() - t0) * 1000
            met.record(lat, code, error=(code == 0))
            i += concurrency

    t_start = time.time()
    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(concurrency)]
    for t in threads: t.start()
    time.sleep(duration)
    stop.set()
    for t in threads: t.join(timeout=2)

    s = met.summary(time.time() - t_start)
    log(f"API done — rps={s['rps']}  p99={s['latency_ms']['p99']}ms  err={s['error_rate']}%", "GREEN")
    return {"vector":"api","target":base,"config":{"concurrency":concurrency,"duration":duration},"metrics":s}

# ── TCP benchmark ─────────────────────────────────────────────────────────────

def bench_tcp(host, port=80, concurrency=50, duration=10, payload_size=256):
    log(f"TCP benchmark → {host}:{port}  workers={concurrency}  duration={duration}s", "YELLOW")
    met  = Metrics()
    stop = threading.Event()
    pl   = payloadgen.net_payloads(host)

    def worker():
        payloads = pl["http_get"] + pl["tcp"]
        i = 0
        while not stop.is_set():
            payload = payloads[i % len(payloads)]
            t0 = time.time()
            try:
                s = socket.socket()
                s.settimeout(5)
                s.connect((host, port))
                s.sendall(payload)
                try: s.recv(1024)
                except: pass
                s.close()
                lat = (time.time() - t0) * 1000
                met.record(lat, 200)
            except Exception:
                lat = (time.time() - t0) * 1000
                met.record(lat, error=True)
            i += 1

    t_start = time.time()
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(concurrency)]
    for t in threads: t.start()
    time.sleep(duration)
    stop.set()
    for t in threads: t.join(timeout=2)

    s = met.summary(time.time() - t_start)
    log(f"TCP done — rps={s['rps']}  p99={s['latency_ms']['p99']}ms  err={s['error_rate']}%", "GREEN")
    return {"vector":"tcp","target":f"{host}:{port}","config":{"concurrency":concurrency,"duration":duration},"metrics":s}

# ── UDP benchmark ─────────────────────────────────────────────────────────────

def bench_udp(host, port=53, concurrency=30, duration=10):
    log(f"UDP benchmark → {host}:{port}  workers={concurrency}  duration={duration}s", "YELLOW")
    met  = Metrics()
    stop = threading.Event()
    payloads = payloadgen.net_udp_payloads()

    def worker():
        i = 0
        while not stop.is_set():
            data = payloads[i % len(payloads)]
            t0 = time.time()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(2)
                s.sendto(data, (host, port))
                try: s.recvfrom(1024)
                except: pass
                s.close()
                lat = (time.time() - t0) * 1000
                met.record(lat, 200)
            except Exception:
                met.record(0, error=True)
            i += 1

    t_start = time.time()
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(concurrency)]
    for t in threads: t.start()
    time.sleep(duration)
    stop.set()
    for t in threads: t.join(timeout=2)

    s = met.summary(time.time() - t_start)
    log(f"UDP done — rps={s['rps']}  p99={s['latency_ms']['p99']}ms  err={s['error_rate']}%", "GREEN")
    return {"vector":"udp","target":f"{host}:{port}","config":{"concurrency":concurrency,"duration":duration},"metrics":s}

# ── DB (via API) benchmark ────────────────────────────────────────────────────

def bench_db(target, concurrency=10, duration=10, token=None):
    base = re.sub(r'/$','',target)
    log(f"DB benchmark (via API) → {base}  workers={concurrency}  duration={duration}s", "YELLOW")
    met  = Metrics()
    stop = threading.Event()
    auth = {"Authorization": f"Bearer {token}"} if token else {}
    pl   = payloadgen.db_payloads()

    # DB-heavy endpoints to hit
    db_tasks = []
    for p in pl["sql"]:
        db_tasks.append(("POST", base+"/api/query",  json.dumps(p), {**auth,"Content-Type":"application/json"}))
        db_tasks.append(("GET",  base+f"/api/search?q={list(p.values())[0]}", None, auth))
    for p in pl["nosql"]:
        db_tasks.append(("POST", base+"/api/users/search", json.dumps(p), {**auth,"Content-Type":"application/json"}))
    # pagination stress
    for offset in [0, 1000, 10000, 100000]:
        db_tasks.append(("GET", base+f"/api/logs?limit=100&offset={offset}", None, auth))

    def worker(idx):
        i = idx
        while not stop.is_set():
            method, url, body, hdrs = db_tasks[i % len(db_tasks)]
            t0 = time.time()
            code, _ = _http_request(url, method, body, "application/json", hdrs, timeout=10)
            lat = (time.time() - t0) * 1000
            met.record(lat, code, error=(code == 0))
            i += concurrency

    t_start = time.time()
    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(concurrency)]
    for t in threads: t.start()
    time.sleep(duration)
    stop.set()
    for t in threads: t.join(timeout=2)

    s = met.summary(time.time() - t_start)
    log(f"DB done — rps={s['rps']}  p99={s['latency_ms']['p99']}ms  err={s['error_rate']}%", "GREEN")
    return {"vector":"db","target":base,"config":{"concurrency":concurrency,"duration":duration},"metrics":s}

# ── Robustness / malformed ────────────────────────────────────────────────────

def bench_malformed(target):
    base  = re.sub(r'/$','',target)
    host  = re.sub(r'^https?://','',base).split('/')[0].split(':')[0]
    try:
        port = int(base.split(':')[-1]) if ':' in base.split('/')[-1] else (443 if base.startswith('https') else 80)
    except:
        port = 80
    log(f"Malformed payload probe → {host}:{port}", "YELLOW")
    results = []
    for payload in payloadgen.net_malformed_packets():
        t0 = time.time()
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect((host, port))
            s.sendall(payload)
            resp = b""
            try: resp = s.recv(512)
            except: pass
            s.close()
            lat = round((time.time()-t0)*1000, 2)
            results.append({
                "payload_size": len(payload),
                "payload_hex":  payload[:16].hex(),
                "latency_ms":   lat,
                "response_size":len(resp),
                "response_hex": resp[:32].hex(),
                "status":       "responded",
            })
        except Exception as e:
            results.append({
                "payload_size": len(payload),
                "payload_hex":  payload[:16].hex(),
                "status":       f"error:{type(e).__name__}",
            })
    log(f"Malformed done — {len(results)} probes sent", "GREEN")
    return {"vector":"malformed","target":f"{host}:{port}","results":results}

# ── Combo runner ──────────────────────────────────────────────────────────────

def print_metrics_table(results):
    print()
    print(c("BOLD", "  ┌─ BENCHMARK RESULTS ────────────────────────────────────────────────┐"))
    for r in results:
        vec = r.get("vector","?").upper()
        tgt = r.get("target","?")
        if "metrics" in r:
            m   = r["metrics"]
            lat = m["latency_ms"]
            print(f"  │  {c('PURPLE',vec):<30} target={tgt}")
            print(f"  │    rps={c('GREEN',str(m['rps']))}  "
                  f"p50={lat['p50']}ms  p95={lat['p95']}ms  p99={c('YELLOW',str(lat['p99'])+'ms')}  "
                  f"err={c('RED' if m['error_rate']>5 else 'GREEN', str(m['error_rate'])+'%')}")
            if m["status_codes"]:
                codes = "  ".join(f"{k}:{v}" for k,v in sorted(m["status_codes"].items()))
                print(f"  │    codes: {c('DIM',codes)}")
        elif "results" in r:
            ok  = sum(1 for x in r["results"] if x.get("status") == "responded")
            tot = len(r["results"])
            print(f"  │  {c('PURPLE',vec):<30} {ok}/{tot} payloads responded")
        print(f"  │")
    print(c("BOLD", "  └────────────────────────────────────────────────────────────────────┘"))
    print()

def run(target, token=None, full=False,
        concurrency=20, duration=10, vectors=None):
    """
    vectors: list of "http","api","tcp","udp","db","malformed"
             or None = all
    """
    base = re.sub(r'/$','',target)
    if not base.startswith("http"):
        base = "https://" + base
    host = re.sub(r'^https?://','',base).split('/')[0].split(':')[0]

    try: ip = socket.gethostbyname(host)
    except: ip = host

    active = vectors or ["http","api","tcp","udp","db","malformed"]
    results = []

    if "http" in active:
        results.append(bench_http(base, concurrency=concurrency, duration=duration))
    if "api" in active:
        results.append(bench_api(base, token=token, concurrency=concurrency//2, duration=duration))
    if "tcp" in active:
        port = 443 if base.startswith("https") else 80
        results.append(bench_tcp(ip, port=port, concurrency=concurrency*2, duration=duration))
    if "udp" in active:
        results.append(bench_udp(ip, port=53, concurrency=concurrency, duration=duration//2))
    if "db" in active:
        results.append(bench_db(base, token=token, concurrency=concurrency//2, duration=duration))
    if "malformed" in active:
        results.append(bench_malformed(base))

    print_metrics_table(results)
    return {"module":"benchmark","target":base,"results":results}
