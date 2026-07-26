#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  ██╗   ██╗██╗██████╗ ██╗   ██╗███████╗    ██╗      █████╗  ║
║  ██║   ██║██║██╔══██╗██║   ██║██╔════╝    ██║     ██╔══██╗ ║
║  ██║   ██║██║██████╔╝██║   ██║███████╗    ██║     ███████║ ║
║  ╚██╗ ██╔╝██║██╔══██╗██║   ██║╚════██║    ██║     ██╔══██║ ║
║   ╚████╔╝ ██║██║  ██║╚██████╔╝███████║    ███████╗██║  ██║ ║
║    ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚══════╝╚═╝  ╚═╝ ║
╠══════════════════════════════════════════════════════════════╣
║  🔬  VIRUS LAB  ·  INTERNAL SECURITY TOOLKIT  v1.0         ║
╚══════════════════════════════════════════════════════════════╝

  USAGE:
    python3 toolkit.py --target <url/ip>              # full scan
    python3 toolkit.py --target <url> --module recon  # single module
    python3 toolkit.py --target <url> --full          # deep scan
    python3 toolkit.py --target <url> --token <jwt>   # authenticated scan

  MODULES: recon | portscanner | webprobe | authtest | injector | apifuzz | benchmark | all
  BENCH VECTORS: http | api | tcp | udp | db | malformed

  BENCHMARK MODE:
    python3 toolkit.py --target <url> --bench
    python3 toolkit.py --target <url> --bench --vectors http api tcp
    python3 toolkit.py --target <url> --bench --concurrency 50 --duration 30
"""

import sys, os, argparse, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MODULES = {
    "recon":       "modules.recon",
    "portscanner": "modules.portscanner",
    "webprobe":    "modules.webprobe",
    "authtest":    "modules.authtest",
    "injector":    "modules.injector",
    "apifuzz":     "modules.apifuzz",
    "benchmark":   "modules.benchmark",
}

COLORS = {
    "RED":    "\033[1;31m",
    "YELLOW": "\033[1;33m",
    "GREEN":  "\033[1;32m",
    "CYAN":   "\033[1;36m",
    "PURPLE": "\033[1;35m",
    "BLUE":   "\033[1;34m",
    "BOLD":   "\033[1m",
    "DIM":    "\033[2m",
    "RESET":  "\033[0m",
}

def c(color, text):
    return f"{COLORS.get(color,'')}{text}{COLORS['RESET']}"

def banner():
    print(c("PURPLE", __doc__))

def status(msg, color="CYAN"):
    ts = time.strftime("%H:%M:%S")
    print(c("DIM", f"[{ts}]") + " " + c(color, msg))

def run_module(name, target, token=None, full=False):
    import importlib
    status(f"Running module: {name.upper()}", "YELLOW")
    try:
        mod = importlib.import_module(MODULES[name])
        if name == "apifuzz":
            result = mod.run(target, token=token, full=full)
        else:
            result = mod.run(target, full=full)
        n = len(result.get("findings", []))
        status(f"{name.upper()} done — {n} findings", "GREEN")
        return result
    except Exception as e:
        status(f"{name.upper()} ERROR: {e}", "RED")
        return {"module": name, "target": target, "findings": [], "error": str(e)}

def main():
    parser = argparse.ArgumentParser(
        description="VIRUS LAB — Internal Security Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--target", "-t", required=True,
                        help="Target URL or IP (e.g. https://example.com)")
    parser.add_argument("--module", "-m", default="all",
                        choices=list(MODULES.keys()) + ["all"],
                        help="Module to run (default: all)")
    parser.add_argument("--full", "-f", action="store_true",
                        help="Full/deep scan mode")
    parser.add_argument("--token", help="Bearer token for authenticated API tests")
    parser.add_argument("--no-save", action="store_true",
                        help="Don't save JSON report")
    parser.add_argument("--ports", nargs="+", type=int,
                        help="Custom ports for portscanner (e.g. --ports 80 443 8080)")
    # Benchmark mode
    parser.add_argument("--bench", "-b", action="store_true",
                        help="Run payload benchmark mode")
    parser.add_argument("--vectors", nargs="+",
                        choices=["http","api","tcp","udp","db","malformed"],
                        help="Benchmark vectors (default: all)")
    parser.add_argument("--concurrency", "-c", type=int, default=20,
                        help="Benchmark concurrency workers (default: 20)")
    parser.add_argument("--duration", "-d", type=int, default=10,
                        help="Benchmark duration per vector in seconds (default: 10)")
    args = parser.parse_args()

    banner()

    target = args.target
    if not target.startswith("http") and args.module not in ("portscanner",):
        target = "https://" + target

    t_start = time.time()

    # ── Benchmark mode ──────────────────────────────────────────────────────
    if args.bench or args.module == "benchmark":
        import importlib
        bmod = importlib.import_module("modules.benchmark")
        status("BENCHMARK MODE — payload barrage starting", "PURPLE")
        result = bmod.run(
            target,
            token=args.token,
            full=args.full,
            concurrency=args.concurrency,
            duration=args.duration,
            vectors=args.vectors,
        )
        elapsed = round(time.time() - t_start, 1)
        status(f"Benchmark complete in {elapsed}s", "GREEN")
        if not args.no_save:
            from modules import reporter
            reporter.save_json([result], target)
        return

    # ── Scan mode ───────────────────────────────────────────────────────────
    results = []

    if args.module == "all":
        order = ["recon","portscanner","webprobe","authtest","injector","apifuzz"]
        for mod in order:
            if mod == "portscanner" and args.ports:
                import importlib
                m = importlib.import_module(MODULES[mod])
                r = m.run(target, ports=args.ports, full=args.full)
                results.append(r)
                status(f"portscanner done — {len(r.get('findings',[]))} findings", "GREEN")
            else:
                results.append(run_module(mod, target, token=args.token, full=args.full))
    else:
        results.append(run_module(args.module, target, token=args.token, full=args.full))

    elapsed = round(time.time() - t_start, 1)
    status(f"Scan complete in {elapsed}s", "GREEN")
    print()

    from modules import reporter
    reporter.generate(results, target, save=not args.no_save)

if __name__ == "__main__":
    main()
