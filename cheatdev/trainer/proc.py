"""Process manager -- attach, list, find game processes (Windows ctypes)"""
import ctypes, ctypes.wintypes as wt, struct, os, sys

# Windows API constants
TH32CS_SNAPPROCESS   = 0x00000002
TH32CS_SNAPMODULE    = 0x00000008
TH32CS_SNAPMODULE32  = 0x00000010
PROCESS_ALL_ACCESS   = 0x1F0FFF
PROCESS_VM_READ      = 0x0010
PROCESS_VM_WRITE     = 0x0020
PROCESS_VM_OPERATION = 0x0008
MEM_COMMIT           = 0x1000
MEM_RESERVE          = 0x2000
MEM_RELEASE          = 0x8000
PAGE_EXECUTE_READWRITE = 0x40
PAGE_READWRITE         = 0x04

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize",              wt.DWORD),
        ("cntUsage",            wt.DWORD),
        ("th32ProcessID",       wt.DWORD),
        ("th32DefaultHeapID",   ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID",        wt.DWORD),
        ("cntThreads",          wt.DWORD),
        ("th32ParentProcessID", wt.DWORD),
        ("pcPriClassBase",      ctypes.c_long),
        ("dwFlags",             wt.DWORD),
        ("szExeFile",           ctypes.c_char * 260),
    ]

class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize",        wt.DWORD),
        ("th32ModuleID",  wt.DWORD),
        ("th32ProcessID", wt.DWORD),
        ("GlblcntUsage",  wt.DWORD),
        ("ProccntUsage",  wt.DWORD),
        ("modBaseAddr",   ctypes.POINTER(wt.BYTE)),
        ("modBaseSize",   wt.DWORD),
        ("hModule",       wt.HMODULE),
        ("szModule",      ctypes.c_char * 256),
        ("szExePath",     ctypes.c_char * 260),
    ]

def _k32():
    return ctypes.windll.kernel32

def list_processes():
    """Return list of (pid, name) for all running processes."""
    k32   = _k32()
    snap  = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
    procs = []
    if k32.Process32First(snap, ctypes.byref(entry)):
        while True:
            procs.append((entry.th32ProcessID, entry.szExeFile.decode(errors="ignore")))
            if not k32.Process32Next(snap, ctypes.byref(entry)):
                break
    k32.CloseHandle(snap)
    return procs

def find_pid(name):
    """Find PID by process name (case-insensitive, partial match OK)."""
    name_l = name.lower()
    for pid, proc in list_processes():
        if name_l in proc.lower():
            return pid, proc
    return None, None

def open_process(pid, access=PROCESS_ALL_ACCESS):
    """Open process handle."""
    h = _k32().OpenProcess(access, False, pid)
    if not h:
        raise PermissionError(f"OpenProcess failed for PID {pid} — try as Admin")
    return h

def close_handle(handle):
    _k32().CloseHandle(handle)

def get_module_base(pid, module_name):
    """Get base address of a module (e.g. game .exe or .dll)."""
    k32  = _k32()
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
    entry = MODULEENTRY32()
    entry.dwSize = ctypes.sizeof(MODULEENTRY32)
    name_l = module_name.lower()
    base   = None
    if k32.Module32First(snap, ctypes.byref(entry)):
        while True:
            if name_l in entry.szModule.decode(errors="ignore").lower():
                base = ctypes.addressof(entry.modBaseAddr.contents)
                break
            if not k32.Module32Next(snap, ctypes.byref(entry)):
                break
    k32.CloseHandle(snap)
    return base

def attach(game_name):
    """Full attach flow: find process + open handle + get base."""
    pid, name = find_pid(game_name)
    if not pid:
        raise ProcessLookupError(f"Process '{game_name}' not found — is the game running?")
    handle = open_process(pid)
    base   = get_module_base(pid, name)
    print(f"[+] Attached: {name}  PID={pid}  base=0x{base or 0:X}")
    return {"pid": pid, "name": name, "handle": handle, "base": base}

# CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        pid, name = find_pid(q)
        if pid:
            print(f"FOUND: {name}  PID={pid}")
        else:
            print(f"Not found: {q}")
    else:
        procs = list_processes()
        for pid, name in sorted(procs, key=lambda x: x[1].lower()):
            print(f"  {pid:6d}  {name}")
