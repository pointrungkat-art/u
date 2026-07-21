"""Memory R/W -- ReadProcessMemory / WriteProcessMemory + pointer chain resolver"""
import ctypes, ctypes.wintypes as wt, struct

_k32 = ctypes.windll.kernel32

# ── Read ──────────────────────────────────────────────────────────────────────

def read_bytes(handle, addr, size):
    buf  = (ctypes.c_byte * size)()
    read = ctypes.c_size_t(0)
    ok   = _k32.ReadProcessMemory(handle, ctypes.c_void_p(addr),
                                   buf, size, ctypes.byref(read))
    if not ok:
        raise OSError(f"ReadProcessMemory failed at 0x{addr:X}")
    return bytes(buf[:read.value])

def read_int(handle, addr, bits=32, signed=False):
    size = bits // 8
    raw  = read_bytes(handle, addr, size)
    fmt  = {(8,False):"B",(8,True):"b",(16,False):"H",(16,True):"h",
             (32,False):"I",(32,True):"i",(64,False):"Q",(64,True):"q"}.get((bits,signed),"I")
    return struct.unpack_from(f"<{fmt}", raw)[0]

def read_float(handle, addr, double=False):
    raw = read_bytes(handle, addr, 8 if double else 4)
    return struct.unpack_from("<d" if double else "<f", raw)[0]

def read_string(handle, addr, max_len=256, encoding="utf-8"):
    raw = read_bytes(handle, addr, max_len)
    end = raw.find(b"\x00")
    return raw[:end if end >= 0 else max_len].decode(encoding, errors="replace")

def read_vec3(handle, addr):
    raw = read_bytes(handle, addr, 12)
    return struct.unpack_from("<fff", raw)

def read_vec2(handle, addr):
    raw = read_bytes(handle, addr, 8)
    return struct.unpack_from("<ff", raw)

def read_bool(handle, addr):
    return bool(read_int(handle, addr, 8))

# ── Write ─────────────────────────────────────────────────────────────────────

def write_bytes(handle, addr, data):
    buf  = (ctypes.c_byte * len(data))(*data)
    wrote = ctypes.c_size_t(0)
    ok   = _k32.WriteProcessMemory(handle, ctypes.c_void_p(addr),
                                    buf, len(data), ctypes.byref(wrote))
    if not ok:
        raise OSError(f"WriteProcessMemory failed at 0x{addr:X}")
    return wrote.value

def write_int(handle, addr, value, bits=32, signed=False):
    fmt = {(8,False):"B",(8,True):"b",(16,False):"H",(16,True):"h",
            (32,False):"I",(32,True):"i",(64,False):"Q",(64,True):"q"}.get((bits,signed),"I")
    write_bytes(handle, addr, struct.pack(f"<{fmt}", value))

def write_float(handle, addr, value, double=False):
    write_bytes(handle, addr, struct.pack("<d" if double else "<f", value))

def write_vec3(handle, addr, x, y, z):
    write_bytes(handle, addr, struct.pack("<fff", x, y, z))

def write_bool(handle, addr, value):
    write_int(handle, addr, int(bool(value)), 8)

def nop(handle, addr, size=1):
    """Patch bytes with NOPs (0x90) — disable instruction."""
    write_bytes(handle, addr, bytes([0x90] * size))

def patch_bytes(handle, addr, patch, restore=False, original=None):
    """Write patch bytes; optionally restore from original."""
    if restore and original:
        write_bytes(handle, addr, original)
    else:
        write_bytes(handle, addr, patch)

# ── Pointer chain ─────────────────────────────────────────────────────────────

def resolve_pointer(handle, base, offsets, ptr_size=8):
    """Follow pointer chain: base + offsets[0] → deref → + offsets[1] → ..."""
    addr = base
    for i, off in enumerate(offsets):
        addr += off
        if i < len(offsets) - 1:
            raw  = read_bytes(handle, addr, ptr_size)
            addr = int.from_bytes(raw, "little")
            if addr == 0:
                raise ValueError(f"Null pointer at offset chain index {i}")
    return addr

def multi_level_ptr(handle, base, static_offset, offsets, ptr_size=8):
    """Classic multi-level pointer: base + static_offset → chain."""
    return resolve_pointer(handle, base, [static_offset] + list(offsets), ptr_size)

# ── Memory protection ─────────────────────────────────────────────────────────

def virtual_protect(handle, addr, size, new_protect=0x40):
    """Change memory page protection (e.g. to PAGE_EXECUTE_READWRITE=0x40)."""
    old = wt.DWORD(0)
    ok  = _k32.VirtualProtectEx(handle, ctypes.c_void_p(addr),
                                  size, new_protect, ctypes.byref(old))
    return old.value if ok else None

def alloc_memory(handle, size, addr=None):
    """Allocate memory in target process (for code cave / shellcode)."""
    MEM_COMMIT_RESERVE = 0x3000
    PAGE_EXECUTE_RW    = 0x40
    return _k32.VirtualAllocEx(handle, ctypes.c_void_p(addr or 0),
                                 size, MEM_COMMIT_RESERVE, PAGE_EXECUTE_RW)

def free_memory(handle, addr):
    MEM_RELEASE = 0x8000
    _k32.VirtualFreeEx(handle, ctypes.c_void_p(addr), 0, MEM_RELEASE)
