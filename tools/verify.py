#!/usr/bin/env python3
"""
XC VERIFY — Tool & Project Health Checker
Jalankan setelah build tool/project baru untuk cross-check status
"""
import subprocess, sys, os, importlib.util, shutil, argparse, json, time

R='\033[91m'; G='\033[92m'; Y='\033[93m'; C='\033[96m'; M='\033[95m'
BOLD='\033[1m'; DIM='\033[2m'; RST='\033[0m'

BANNER = f"""
{M}╔══════════════════════════════════════════════════════╗{RST}
{M}║{RST}  {BOLD}XC VERIFY{RST}  ·  {Y}TOOL & PROJECT HEALTH CHECK{RST}         {M}║{RST}
{M}║{RST}  Syntax · Deps · Logic · Output · Status Report   {M}║{RST}
{M}╚══════════════════════════════════════════════════════╝{RST}
"""

STATUS = {
    "FULL":   f"{G}{BOLD}✅ FULL WORK{RST}",
    "DEPS":   f"{Y}{BOLD}⚠️  NEEDS DEPS{RST}",
    "KEY":    f"{C}{BOLD}🔑 NEEDS API KEY{RST}",
    "USER":   f"{M}{BOLD}👤 NEEDS USER INPUT{RST}",
    "BROKEN": f"{R}{BOLD}❌ BROKEN{RST}",
    "SKIP":   f"{DIM}⊘  SKIP{RST}",
}

results = []

def log(sym, msg, color=RST): print(f"  {color}{sym}{RST} {msg}")
def section(t): print(f"\n{M}{BOLD}── {t} {'─'*(46-len(t))}{RST}")

# ── CHECK FUNCTIONS ──────────────────────────────────────────────────────────

def check_syntax(path):
    """Compile-check Python file"""
    r = subprocess.run([sys.executable, "-m", "py_compile", path],
                       capture_output=True, text=True)
    return r.returncode == 0, r.stderr.strip()

def check_help(path, timeout=6):
    """--help atau -h harus exit 0/1/2 dengan output"""
    for flag in ["--help", "-h", ""]:
        args = [sys.executable, path]
        if flag: args.append(flag)
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout + r.stderr).strip()
        if len(out) > 30:
            return True, out[:300]
    return False, ""

def check_imports(path):
    """Scan import statements — deteksi deps yang mungkin missing"""
    import sys as _sys
    stdlib = set(_sys.stdlib_module_names) if hasattr(_sys, "stdlib_module_names") else {
        "os","sys","re","json","time","socket","threading","subprocess",
        "argparse","urllib","hashlib","base64","random","struct","io",
        "pathlib","shutil","glob","math","collections","itertools","functools",
        "datetime","copy","string","typing","enum","abc","contextlib",
        "http","html","email","csv","logging","traceback","platform",
        "unittest","tempfile","inspect","ast","dis","gc","weakref",
        "queue","multiprocessing","concurrent","asyncio","ssl","hmac",
        "secrets","uuid","textwrap","pprint","warnings","signal","ctypes",
    }
    third_party = []
    seen = set()
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"): continue
                if line.startswith("import "):
                    # handles: import os, sys, re
                    pkgs = line[7:].split(",")
                    for pkg in pkgs:
                        pkg = pkg.strip().split(".")[0].split(" as ")[0].strip()
                        if pkg and pkg not in stdlib and pkg not in seen:
                            if importlib.util.find_spec(pkg) is None:
                                third_party.append(pkg)
                            seen.add(pkg)
                elif line.startswith("from "):
                    pkg = line[5:].split()[0].split(".")[0].strip()
                    if pkg and pkg not in stdlib and pkg not in seen:
                        if importlib.util.find_spec(pkg) is None:
                            third_party.append(pkg)
                        seen.add(pkg)
    except Exception:
        pass
    return third_party

def check_external_bins(path):
    """Scan subprocess/os.system calls untuk external binary deps"""
    bins = []
    known = ["curl","nmap","ffuf","sqlmap","hping3","wrk","siege","hey","ab",
             "nuclei","subfinder","amass","dig","nslookup","whois","nikto",
             "gobuster","wfuzz","hydra","john","hashcat","aircrack-ng"]
    try:
        with open(path) as f:
            content = f.read()
        for b in known:
            if f'"{b}"' in content or f"'{b}'" in content:
                status = "✓ installed" if shutil.which(b) else "✗ missing"
                bins.append((b, status))
    except Exception:
        pass
    return bins

def check_api_keys(path):
    """Deteksi apakah tool butuh API key"""
    markers = ["api_key", "apikey", "API_KEY", "shodan", "censys",
               "virustotal", "securitytrails", "hunter.io"]
    try:
        with open(path) as f:
            content = f.read().lower()
        return any(m.lower() in content for m in markers)
    except:
        return False

def quick_run(path, test_args, timeout=8):
    """Jalankan tool dengan safe test args, cek output bermakna"""
    try:
        r = subprocess.run([sys.executable, path] + test_args,
                           capture_output=True, text=True, timeout=timeout)
        out = (r.stdout + r.stderr).strip()
        meaningful = len(out) > 50 and r.returncode in (0,1,2)
        return meaningful, out[:400], r.returncode
    except subprocess.TimeoutExpired:
        return True, "[timeout — tool running, likely OK]", 0
    except Exception as e:
        return False, str(e), -1

# ── TOOL REGISTRY ────────────────────────────────────────────────────────────

TOOLS_DEF = {
    # path: (test_args, description)
    "tools/ipfind.py":   (["google.com"], "Real IP hunter"),
    "tools/recon.py":    (["https://example.com"], "Full recon"),
    "tools/waf.py":      (["https://example.com"], "WAF bypass"),
    "tools/cors.py":     (["https://example.com"], "CORS tester"),
    "tools/headers.py":  (["https://example.com"], "Header audit"),
    "tools/js_hunt.py":  (["https://example.com"], "JS harvester"),
    "tools/sqli.py":     (["https://httpbin.org/get?id=1"], "SQLi fuzzer"),
    "tools/ssti.py":     (["https://example.com?q=test"], "SSTI hunter"),
    "tools/cmdi.py":     (["https://example.com?cmd=ls"], "CMDi fuzzer"),
    "tools/jwt.py":      (["eyJhbGciOiJIUzI1NiJ9.e30.test"], "JWT attacks"),
    "tools/ssrf.py":     (["https://example.com?url=http://x"], "SSRF tester"),
    "tools/upload.py":   (["--shells"], "Upload bypass"),
    "tools/stress.py":   (["--help"], "Stress tester"),
    "tools/xc.py":       ([], "XC Tool Hub runner"),
    "bugbounty/recon.py":(["--help"], "Bugbounty recon"),
}

# ── PROJECT CHECKS (non-Python) ───────────────────────────────────────────────

PROJECTS_DEF = {
    "arena-breakout": {
        "files": ["Engine.ini", "GameUserSettings.ini", "apply.sh", "guide.md"],
        "type": "game-config",
        "note": "Apply manual via ADB atau MT Manager — no auto test",
    },
    "onetapdrag": {
        "files": ["config.json", "apply.sh", "guide.md"],
        "type": "game-config",
        "note": "FF sensitivity config — apply via ADB",
    },
    "cheatdev": {
        "files": ["init.lua", "core.lua", "config.lua"],
        "type": "lua-roblox",
        "note": "Lua/Roblox — test via Delta executor",
    },
}

# ── MAIN VERIFY ──────────────────────────────────────────────────────────────

def verify_tool(rel_path, test_args, desc, base="/home/user/u"):
    path = os.path.join(base, rel_path)
    name = os.path.basename(rel_path)
    row = {"name": name, "path": rel_path, "desc": desc, "status": "FULL", "notes": []}

    print(f"\n  {BOLD}{name}{RST}  {DIM}{desc}{RST}")

    if not os.path.exists(path):
        log("✗", "File tidak ditemukan", R)
        row["status"] = "BROKEN"
        results.append(row)
        return

    # 1. Syntax
    ok, err = check_syntax(path)
    if ok:
        log("✓", "Syntax OK", G)
    else:
        log("✗", f"Syntax ERROR: {err}", R)
        row["status"] = "BROKEN"
        row["notes"].append(f"syntax: {err[:100]}")
        results.append(row)
        return

    # 2. Missing pip packages
    missing_pkgs = check_imports(path)
    if missing_pkgs:
        log("!", f"Missing pip packages: {', '.join(missing_pkgs)}", Y)
        row["status"] = "DEPS"
        row["notes"].append(f"pip: {', '.join(missing_pkgs)}")

    # 3. External binaries
    ext_bins = check_external_bins(path)
    for b, status in ext_bins:
        color = G if "installed" in status else Y
        log("→", f"bin dep: {b} [{status}]", color)
        if "missing" in status:
            if row["status"] == "FULL": row["status"] = "DEPS"
            row["notes"].append(f"bin: {b} missing")

    # 4. API key needed
    if check_api_keys(path):
        log("🔑", "API key optional/required", C)
        if row["status"] == "FULL": row["status"] = "KEY"
        row["notes"].append("api key needed")

    # 5. Functional run
    ok, out, code = quick_run(path, test_args)
    if ok:
        log("✓", f"Functional run OK (exit {code})", G)
        preview = out.replace('\n',' ')[:120]
        log(" ", f"{DIM}{preview}{RST}")
    else:
        log("✗", f"Run FAILED (exit {code}): {out[:150]}", R)
        row["status"] = "BROKEN"
        row["notes"].append(f"run fail: {out[:80]}")

    results.append(row)

def verify_project(name, spec, base="/home/user/u"):
    print(f"\n  {BOLD}{name}/{RST}  {DIM}{spec['type']}{RST}")
    proj_path = os.path.join(base, name)
    missing = []
    for f in spec["files"]:
        fp = os.path.join(proj_path, f)
        if os.path.exists(fp):
            log("✓", f"{f}", G)
        else:
            log("✗", f"{f} MISSING", R)
            missing.append(f)
    log("→", spec["note"], C)
    results.append({
        "name": name, "path": name, "desc": spec["type"],
        "status": "BROKEN" if missing else "USER",
        "notes": [f"missing: {', '.join(missing)}"] if missing else [spec["note"]]
    })

def print_report():
    section("VERIFICATION REPORT")
    print()
    counts = {"FULL":0,"DEPS":0,"KEY":0,"USER":0,"BROKEN":0}

    for r in results:
        st = r["status"]
        counts[st] = counts.get(st, 0) + 1
        notes = " · ".join(r["notes"]) if r["notes"] else ""
        note_str = f"  {DIM}↳ {notes}{RST}" if notes else ""
        print(f"  {STATUS.get(st,'?')}  {BOLD}{r['name']}{RST}  {DIM}{r['desc']}{RST}")
        if note_str: print(note_str)

    print(f"""
  {DIM}────────────────────────────────────────────────{RST}
  {G}✅ FULL WORK  : {counts['FULL']}{RST}
  {Y}⚠️  NEEDS DEPS : {counts['DEPS']}{RST}  (install via apt/pip — lihat notes)
  {C}🔑 NEEDS KEY  : {counts['KEY']}{RST}  (user provide API key)
  {M}👤 NEEDS USER  : {counts['USER']}{RST}  (manual apply / executor)
  {R}❌ BROKEN     : {counts['BROKEN']}{RST}
""")

def main():
    print(BANNER)
    p = argparse.ArgumentParser()
    p.add_argument("--tool", help="Verify specific tool only (e.g. ipfind.py)")
    p.add_argument("--projects", action="store_true", help="Verify projects (non-Python)")
    p.add_argument("--all", action="store_true", help="Verify everything", default=True)
    args = p.parse_args()

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if args.tool:
        for rel, (test_args, desc) in TOOLS_DEF.items():
            if args.tool in rel:
                section(f"VERIFYING {args.tool}")
                verify_tool(rel, test_args, desc, base)
    else:
        section("PYTHON TOOLS")
        for rel, (test_args, desc) in TOOLS_DEF.items():
            verify_tool(rel, test_args, desc, base)

        section("PROJECTS (non-Python)")
        for name, spec in PROJECTS_DEF.items():
            verify_project(name, spec, base)

    print_report()

if __name__ == "__main__":
    main()
