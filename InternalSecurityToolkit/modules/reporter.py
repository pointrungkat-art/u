"""Reporter — compile findings to JSON + terminal output with ANSI colors"""
import json, datetime, os, re

COLORS = {
    "CRITICAL": "\033[1;91m",  # bold bright red
    "HIGH":     "\033[1;31m",  # bold red
    "MEDIUM":   "\033[1;33m",  # bold yellow
    "LOW":      "\033[0;36m",  # cyan
    "INFO":     "\033[0;37m",  # white
    "RESET":    "\033[0m",
    "BOLD":     "\033[1m",
    "DIM":      "\033[2m",
    "GREEN":    "\033[1;32m",
    "PURPLE":   "\033[1;35m",
    "BLUE":     "\033[1;34m",
}

SEVERITY_ORDER = {"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3,"INFO":4}

BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║  ██╗   ██╗██╗██████╗ ██╗   ██╗███████╗    ██╗      █████╗  ║
║  ██║   ██║██║██╔══██╗██║   ██║██╔════╝    ██║     ██╔══██╗ ║
║  ██║   ██║██║██████╔╝██║   ██║███████╗    ██║     ███████║ ║
║  ╚██╗ ██╔╝██║██╔══██╗██║   ██║╚════██║    ██║     ██╔══██║ ║
║   ╚████╔╝ ██║██║  ██║╚██████╔╝███████║    ███████╗██║  ██║ ║
║    ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚══════╝╚═╝  ╚═╝ ║
╠══════════════════════════════════════════════════════════════╣
║  🔬  VIRUS LAB  ·  INTERNAL SECURITY TOOLKIT  ·  REPORT    ║
╚══════════════════════════════════════════════════════════════╝
"""

def c(color, text):
    return f"{COLORS.get(color,'')}{text}{COLORS['RESET']}"

def severity_badge(sev):
    badges = {
        "CRITICAL": c("CRITICAL", "[ CRITICAL ]"),
        "HIGH":     c("HIGH",     "[   HIGH   ]"),
        "MEDIUM":   c("MEDIUM",   "[  MEDIUM  ]"),
        "LOW":      c("LOW",      "[   LOW    ]"),
        "INFO":     c("INFO",     "[   INFO   ]"),
    }
    return badges.get(sev, f"[{sev:^9}]")

def count_by_severity(findings):
    counts = {"CRITICAL":0,"HIGH":0,"MEDIUM":0,"LOW":0,"INFO":0}
    for f in findings:
        sev = f.get("severity","INFO")
        counts[sev] = counts.get(sev, 0) + 1
    return counts

def severity_bar(counts):
    parts = []
    for sev in ["CRITICAL","HIGH","MEDIUM","LOW","INFO"]:
        n = counts.get(sev, 0)
        if n:
            parts.append(c(sev if sev != "INFO" else "DIM", f"{sev}:{n}"))
    return "  ".join(parts) if parts else c("DIM","No findings")

def print_report(results, target):
    print(c("PURPLE", BANNER))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(c("BOLD", f"  TARGET  : {target}"))
    print(c("BOLD", f"  DATE    : {now}"))
    print()

    all_findings = []
    module_results = {}
    for res in results:
        mod = res.get("module","?")
        findings = res.get("findings",[])
        module_results[mod] = res
        all_findings.extend(findings)

    # Sort findings by severity
    all_findings.sort(key=lambda f: SEVERITY_ORDER.get(f.get("severity","INFO"), 4))

    counts = count_by_severity(all_findings)
    total = sum(counts.values())

    print(c("BOLD", "  ┌─ SEVERITY SUMMARY ──────────────────────────────────────────┐"))
    print(f"  │  {severity_bar(counts)}")
    print(f"  │  Total findings: {c('BOLD', str(total))}")
    print(c("BOLD", "  └──────────────────────────────────────────────────────────────┘"))
    print()

    # Module summaries
    print(c("BLUE", "  ┌─ MODULE RESULTS ─────────────────────────────────────────────┐"))
    for mod, res in module_results.items():
        n = len(res.get("findings",[]))
        extra = ""
        if mod == "portscanner":
            extra = f"  open_ports={res.get('open_ports',[])}"
        elif mod == "recon":
            extra = f"  ips={res.get('ips',[])}"
        elif mod == "apifuzz":
            extra = f"  endpoints={len(res.get('endpoints_found',[]))}"
        print(f"  │  {c('BOLD', mod.upper()):<30} findings={n}{extra}")
    print(c("BLUE", "  └──────────────────────────────────────────────────────────────┘"))
    print()

    if not all_findings:
        print(c("GREEN", "  ✅  No findings. Target appears hardened."))
        return

    # Print findings grouped by severity
    print(c("BOLD", "  ┌─ FINDINGS ───────────────────────────────────────────────────┐"))
    current_sev = None
    for i, f in enumerate(all_findings):
        sev = f.get("severity","INFO")
        if sev != current_sev:
            current_sev = sev
            print(f"  │")
            print(f"  │  {severity_badge(sev)}")
        ftype = f.get("type","?")
        value = f.get("value") or f.get("param") or f.get("endpoint") or f.get("port","")
        note = f.get("note","")
        evidence = f.get("evidence","")
        print(f"  │    [{i+1:02d}] {c('BOLD', ftype.upper())}")
        if value:
            print(f"  │        value   : {str(value)[:80]}")
        if note:
            print(f"  │        note    : {note}")
        if evidence:
            ev_clean = re.sub(r'\s+',' ', evidence.strip())[:120]
            print(f"  │        evidence: {c('DIM', ev_clean)}")
        payload = f.get("payload","")
        if payload:
            print(f"  │        payload : {c('MEDIUM', payload[:100])}")
        print(f"  │")
    print(c("BOLD", "  └──────────────────────────────────────────────────────────────┘"))
    print()

def save_json(results, target, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_target = re.sub(r'[^\w\-.]', '_', re.sub(r'^https?://','',target))
    filename = f"{output_dir}/{safe_target}-{ts}.json"
    report = {
        "target": target,
        "timestamp": datetime.datetime.now().isoformat(),
        "modules": results,
        "summary": {
            "total_findings": sum(len(r.get("findings",[])) for r in results),
            "by_severity": count_by_severity(
                [f for r in results for f in r.get("findings",[])]
            ),
        }
    }
    with open(filename, "w") as fh:
        json.dump(report, fh, indent=2, default=str)
    return filename

def generate(results, target, save=True):
    print_report(results, target)
    if save:
        path = save_json(results, target)
        print(c("GREEN", f"  💾  Report saved: {path}"))
        print()
    return path if save else None
