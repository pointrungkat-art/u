"""AOB / value scanner -- pattern scan, value hunt, freeze loop"""
import ctypes, ctypes.wintypes as wt, struct, re, threading, time

_k32 = ctypes.windll.kernel32

SCAN_START = 0x00400000
SCAN_END   = 0x7FFFFFFF

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress",       ctypes.c_void_p),
        ("AllocationBase",    ctypes.c_void_p),
        ("AllocationProtect", wt.DWORD),
        ("RegionSize",        ctypes.c_size_t),
        ("State",             wt.DWORD),
        ("Protect",           wt.DWORD),
        ("Type",              wt.DWORD),
    ]

def _readable_regions(handle, start=SCAN_START, end=SCAN_END):
    """Yield (base_addr, data) for all readable committed pages."""
    addr = start
    mbi  = MEMORY_BASIC_INFORMATION()
    size = ctypes.sizeof(mbi)
    READABLE = {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}  # page protection flags
    MEM_COMMIT = 0x1000

    while addr < end:
        ret = _k32.VirtualQueryEx(handle, ctypes.c_void_p(addr),
                                   ctypes.byref(mbi), size)
        if not ret:
            break
        region_end = addr + mbi.RegionSize
        if (mbi.State == MEM_COMMIT and
                (mbi.Protect & 0xFF) in READABLE and
                mbi.RegionSize > 0):
            buf  = (ctypes.c_byte * mbi.RegionSize)()
            read = ctypes.c_size_t(0)
            ok   = _k32.ReadProcessMemory(handle, ctypes.c_void_p(addr),
                                           buf, mbi.RegionSize, ctypes.byref(read))
            if ok and read.value:
                yield addr, bytes(buf[:read.value])
        addr = region_end

# ── AOB (Array of Bytes) scan ─────────────────────────────────────────────────

def _parse_aob(pattern_str):
    """Parse 'DE AD ?? BE EF' → list of (byte|None)."""
    tokens = pattern_str.upper().split()
    result = []
    for t in tokens:
        if t in ("??", "?"):
            result.append(None)
        else:
            result.append(int(t, 16))
    return result

def aob_scan(handle, pattern_str, first=True, start=SCAN_START, end=SCAN_END):
    """
    Scan process memory for AOB pattern.
    pattern_str: 'DE AD ?? BE EF' — ?? = wildcard
    Returns list of addresses (or first address if first=True).
    """
    pattern = _parse_aob(pattern_str)
    plen    = len(pattern)
    results = []

    for base, data in _readable_regions(handle, start, end):
        dlen = len(data)
        for i in range(dlen - plen + 1):
            if all(p is None or data[i+j] == p for j, p in enumerate(pattern)):
                results.append(base + i)
                if first:
                    return results
    return results

# ── Value scan ────────────────────────────────────────────────────────────────

def _pack_value(value, vtype):
    fmt = {"int32":"<i","uint32":"<I","int64":"<q","uint64":"<Q",
           "float":"<f","double":"<d","byte":"<B","int16":"<h","uint16":"<H"}
    f = fmt.get(vtype, "<i")
    return struct.pack(f, value)

def value_scan(handle, value, vtype="int32", start=SCAN_START, end=SCAN_END):
    """First scan — find all addresses containing value."""
    needle = _pack_value(value, vtype)
    size   = len(needle)
    results = []
    for base, data in _readable_regions(handle, start, end):
        i = 0
        while i <= len(data) - size:
            if data[i:i+size] == needle:
                results.append(base + i)
            i += 1
    return results

def next_scan(handle, prev_results, value, vtype="int32"):
    """Narrow down addresses — re-read and filter by new value."""
    from .mem import read_bytes
    needle  = _pack_value(value, vtype)
    size    = len(needle)
    refined = []
    for addr in prev_results:
        try:
            if read_bytes(handle, addr, size) == needle:
                refined.append(addr)
        except OSError:
            pass
    return refined

# ── Freeze (value locker) ─────────────────────────────────────────────────────

_freeze_threads = {}

def freeze(handle, addr, value, vtype="int32", interval=0.05):
    """Continuously write value to address (freeze/lock)."""
    from .mem import write_bytes
    data = _pack_value(value, vtype)
    stop = threading.Event()

    def _loop():
        while not stop.is_set():
            try: write_bytes(handle, addr, data)
            except: pass
            time.sleep(interval)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    _freeze_threads[addr] = (t, stop)
    print(f"[FREEZE] 0x{addr:X} = {value} ({vtype})")
    return stop

def unfreeze(addr):
    """Stop freezing an address."""
    if addr in _freeze_threads:
        _, stop = _freeze_threads.pop(addr)
        stop.set()
        print(f"[UNFREEZE] 0x{addr:X}")

def unfreeze_all():
    for addr in list(_freeze_threads):
        unfreeze(addr)

# ── Interactive scanner CLI ───────────────────────────────────────────────────

def interactive_scan(handle, vtype="int32"):
    """Interactive Cheat Engine-style scan loop."""
    addresses = None
    print(f"\n[SCAN] type={vtype}  (blank to skip next scan, 'q' to quit)\n")
    while True:
        raw = input("  value > ").strip()
        if raw.lower() == "q":
            break
        try:
            value = float(raw) if "float" in vtype or "double" in vtype else int(raw)
        except ValueError:
            print("  Invalid value — try again")
            continue

        if addresses is None:
            print(f"  Scanning for {value}...")
            addresses = value_scan(handle, value, vtype)
        else:
            print(f"  Narrowing {len(addresses)} addresses...")
            addresses = next_scan(handle, addresses, value, vtype)

        print(f"  Found: {len(addresses)} address(es)")
        if 0 < len(addresses) <= 20:
            for a in addresses:
                print(f"    0x{a:X}")
        elif len(addresses) == 0:
            print("  [!] Zero results — restart scan? (type new value or 'r' to reset)")
            if input("  > ").strip().lower() == "r":
                addresses = None

    return addresses or []
