#!/usr/bin/env python3
"""
CheatDev Trainer -- Universal game trainer builder
Attach to any game process, R/W memory, scan values, bind hotkeys.

Usage:
  python trainer.py --game <process_name>
  python trainer.py --game <process_name> --aob "DE AD ?? BE EF"
  python trainer.py --game <process_name> --addr 0x1A2B3C --val 9999 --type int32
  python trainer.py --game <process_name> --scan --type float
  python trainer.py --list
"""
import sys, os, argparse, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BANNER = r"""
  ____  _   _ _____    _  _____ ____  _______   __
 / ___|| | | | ____|  / \|_   _|  _ \| ____\ \ / /
| |    | |_| |  _|   / _ \ | | | | | |  _|  \ V /
| |___ |  _  | |___ / ___ \| | | |_| | |___  | |
 \____||_| |_|_____/_/   \_\_| |____/|_____| |_|

 C H E A T D E V  T R A I N E R  --  ALL GAME  ALL COST
"""

COLORS = {
    "R": "\033[1;31m","Y": "\033[1;33m","G": "\033[1;32m",
    "C": "\033[1;36m","P": "\033[1;35m","B": "\033[1;34m",
    "W": "\033[1m",   "D": "\033[2m",   "X": "\033[0m",
}
def c(col, txt): return f"{COLORS.get(col,'')}{txt}{COLORS['X']}"

def check_windows():
    if sys.platform != "win32":
        print(c("Y", "[!] Trainer requires Windows (uses WinAPI ctypes)"))
        print(c("D", "    Build your game config here, run on Windows target."))
        return False
    return True

def do_list():
    if not check_windows(): return
    from trainer.proc import list_processes
    procs = list_processes()
    print(c("W", "\n  PID     PROCESS"))
    print(c("D", "  " + "-" * 40))
    for pid, name in sorted(procs, key=lambda x: x[1].lower()):
        print(f"  {pid:<8}{name}")

def do_attach(game_name):
    from trainer.proc import attach
    return attach(game_name)

def do_aob(ctx, pattern, first=True):
    from trainer.scan import aob_scan
    print(c("Y", f"[*] AOB scan: '{pattern}'"))
    results = aob_scan(ctx["handle"], pattern, first=first)
    if results:
        for a in results:
            print(c("G", f"    FOUND: 0x{a:X}"))
    else:
        print(c("R", "    Not found"))
    return results

def do_write(ctx, addr, value, vtype="int32"):
    from trainer import mem
    if isinstance(addr, str):
        addr = int(addr, 16)
    fns = {
        "int8": lambda: mem.write_int(ctx["handle"], addr, int(value), 8),
        "int16": lambda: mem.write_int(ctx["handle"], addr, int(value), 16),
        "int32": lambda: mem.write_int(ctx["handle"], addr, int(value), 32),
        "int64": lambda: mem.write_int(ctx["handle"], addr, int(value), 64),
        "float": lambda: mem.write_float(ctx["handle"], addr, float(value)),
        "double": lambda: mem.write_float(ctx["handle"], addr, float(value), double=True),
        "bool": lambda: mem.write_bool(ctx["handle"], addr, bool(int(value))),
        "nop": lambda: mem.nop(ctx["handle"], addr, int(value)),
    }
    fns.get(vtype, fns["int32"])()
    print(c("G", f"[+] Wrote {value} ({vtype}) -> 0x{addr:X}"))

def do_read(ctx, addr, vtype="int32"):
    from trainer import mem
    if isinstance(addr, str):
        addr = int(addr, 16)
    val = {
        "int32": lambda: mem.read_int(ctx["handle"], addr, 32),
        "int64": lambda: mem.read_int(ctx["handle"], addr, 64),
        "float": lambda: mem.read_float(ctx["handle"], addr),
        "double": lambda: mem.read_float(ctx["handle"], addr, double=True),
        "string": lambda: mem.read_string(ctx["handle"], addr),
        "bool": lambda: mem.read_bool(ctx["handle"], addr),
        "vec3": lambda: mem.read_vec3(ctx["handle"], addr),
    }.get(vtype, lambda: mem.read_int(ctx["handle"], addr, 32))()
    print(c("C", f"[0x{addr:X}] = {val}"))
    return val

def do_scan(ctx, vtype="int32"):
    from trainer.scan import interactive_scan
    results = interactive_scan(ctx["handle"], vtype)
    return results

def do_freeze(ctx, addr, value, vtype="int32"):
    from trainer.scan import freeze
    if isinstance(addr, str):
        addr = int(addr, 16)
    return freeze(ctx["handle"], addr, value, vtype)

def do_pointer(ctx, base_name, static_off, offsets, vtype="int32"):
    """Resolve pointer chain and read value."""
    from trainer import mem
    base = ctx.get("base") or 0
    if base_name.startswith("0x"):
        base = int(base_name, 16)
    addr = mem.resolve_pointer(ctx["handle"], base, [static_off] + list(offsets))
    print(c("C", f"[PTR] resolved to 0x{addr:X}"))
    return do_read(ctx, addr, vtype)

# ── Interactive REPL ──────────────────────────────────────────────────────────

HELP_REPL = """
  Commands:
    read  <addr> [type]          -- read value (types: int32 int64 float double bool vec3 string)
    write <addr> <val> [type]    -- write value
    scan  [type]                 -- interactive value scan (CE-style)
    aob   <pattern>              -- AOB scan ("DE AD ?? BE EF")
    freeze <addr> <val> [type]   -- freeze/lock value
    ptr   <base_off> <off1> ...  -- resolve + read pointer chain
    nop   <addr> <size>          -- NOP patch (disable instruction)
    info                         -- show attached process info
    help                         -- this message
    exit / q                     -- detach and quit
"""

def repl(ctx):
    print(c("G", f"\n[REPL] Attached to {ctx['name']} PID={ctx['pid']}"))
    print(c("D", HELP_REPL))
    while True:
        try:
            raw = input(c("P", "  trainer> ")).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw: continue
        parts = raw.split()
        cmd   = parts[0].lower()

        try:
            if cmd in ("exit","q","quit"):
                break
            elif cmd == "info":
                print(f"  name={ctx['name']}  pid={ctx['pid']}  base=0x{ctx.get('base') or 0:X}")
            elif cmd == "help":
                print(HELP_REPL)
            elif cmd == "read":
                do_read(ctx, parts[1], parts[2] if len(parts)>2 else "int32")
            elif cmd == "write":
                do_write(ctx, parts[1], parts[2], parts[3] if len(parts)>3 else "int32")
            elif cmd == "scan":
                do_scan(ctx, parts[1] if len(parts)>1 else "int32")
            elif cmd == "aob":
                do_aob(ctx, " ".join(parts[1:]))
            elif cmd == "freeze":
                do_freeze(ctx, parts[1], int(parts[2]), parts[3] if len(parts)>3 else "int32")
            elif cmd == "nop":
                do_write(ctx, parts[1], parts[2] if len(parts)>2 else "1", "nop")
            elif cmd == "ptr":
                offs = [int(o, 16) for o in parts[2:]]
                do_pointer(ctx, parts[1], offs[0], offs[1:])
            else:
                print(c("Y", f"  Unknown command: {cmd}  (type 'help')"))
        except (IndexError, ValueError) as e:
            print(c("R", f"  Error: {e}"))
        except OSError as e:
            print(c("R", f"  OS Error: {e}"))

def main():
    print(c("P", BANNER))
    parser = argparse.ArgumentParser(description="CheatDev Trainer — Universal game memory tool")
    parser.add_argument("--game",   "-g", help="Game process name (e.g. 'RobloxPlayer' 'UnityGame')")
    parser.add_argument("--list",   "-l", action="store_true", help="List all running processes")
    parser.add_argument("--aob",          help="AOB pattern scan after attach")
    parser.add_argument("--addr",         help="Address to read/write (hex)")
    parser.add_argument("--val",          help="Value to write")
    parser.add_argument("--type",   "-T", default="int32",
                        choices=["int8","int16","int32","int64","float","double","bool","string","vec3","nop"],
                        help="Value type (default: int32)")
    parser.add_argument("--scan",   "-s", action="store_true", help="Interactive value scan mode")
    parser.add_argument("--freeze", "-f", action="store_true", help="Freeze value at --addr to --val")
    parser.add_argument("--repl",   "-r", action="store_true", help="Open interactive REPL (default if no other action)")
    args = parser.parse_args()

    if args.list:
        do_list()
        return

    if not args.game:
        parser.print_help()
        return

    if not check_windows():
        print(c("D", f"\n  Game target: {args.game}"))
        if args.aob:
            print(c("D", f"  AOB pattern: {args.aob}"))
        print(c("Y", "\n  Run this on Windows with the game open.\n"))
        return

    ctx = do_attach(args.game)

    if args.aob:
        do_aob(ctx, args.aob)
    elif args.scan:
        do_scan(ctx, args.type)
    elif args.addr and args.val:
        if args.freeze:
            stop_evt = do_freeze(ctx, args.addr, int(args.val), args.type)
            print(c("D", "  [CTRL+C to unfreeze and exit]"))
            try:
                while True: time.sleep(0.1)
            except KeyboardInterrupt:
                stop_evt.set()
    elif args.addr:
        do_read(ctx, args.addr, args.type)
    else:
        repl(ctx)

if __name__ == "__main__":
    main()
