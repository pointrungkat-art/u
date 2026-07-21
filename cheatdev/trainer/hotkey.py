"""Global hotkey manager -- toggle cheats on/off via keyboard (Windows)"""
import ctypes, threading, time

_user32 = ctypes.windll.user32

# Virtual key codes (common)
VK = {
    "F1":0x70,"F2":0x71,"F3":0x72,"F4":0x73,"F5":0x74,"F6":0x75,
    "F7":0x76,"F8":0x77,"F9":0x78,"F10":0x79,"F11":0x7A,"F12":0x7B,
    "INS":0x2D,"DEL":0x2E,"HOME":0x24,"END":0x23,"PGUP":0x21,"PGDN":0x22,
    "NUM0":0x60,"NUM1":0x61,"NUM2":0x62,"NUM3":0x63,"NUM4":0x64,
    "NUM5":0x65,"NUM6":0x66,"NUM7":0x67,"NUM8":0x68,"NUM9":0x69,
    "NUMPAD_PLUS":0x6B,"NUMPAD_MINUS":0x6D,"NUMPAD_MUL":0x6A,"NUMPAD_DIV":0x6F,
    "CTRL":0x11,"SHIFT":0x10,"ALT":0x12,"CAPS":0x14,"ESC":0x1B,"SPACE":0x20,
}
for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    VK[c] = ord(c)
for i in range(10):
    VK[str(i)] = 0x30 + i

_bindings = {}   # key_str -> {"callback": fn, "toggle": bool, "state": bool, "name": str}
_running  = False
_thread   = None

def _normalize(key):
    return key.upper().replace(" ","")

def bind(key, callback, name="", toggle=True):
    """Bind key to callback. If toggle=True, callback receives new bool state."""
    _bindings[_normalize(key)] = {
        "vk": VK.get(_normalize(key), 0),
        "callback": callback,
        "toggle": toggle,
        "state": False,
        "name": name or key,
    }
    print(f"[HOTKEY] {key} -> {name or 'callback'} (toggle={toggle})")

def unbind(key):
    _bindings.pop(_normalize(key), None)

def unbind_all():
    _bindings.clear()

def _poll_loop(interval=0.05):
    global _running
    prev = {k: False for k in _bindings}
    while _running:
        for key, info in list(_bindings.items()):
            vk = info["vk"]
            if not vk:
                continue
            pressed = bool(_user32.GetAsyncKeyState(vk) & 0x8000)
            if pressed and not prev.get(key):
                if info["toggle"]:
                    info["state"] = not info["state"]
                    print(f"[HOTKEY] {info['name']} -> {'ON' if info['state'] else 'OFF'}")
                    info["callback"](info["state"])
                else:
                    info["callback"]()
            prev[key] = pressed
        time.sleep(interval)

def start():
    global _running, _thread
    if _running:
        return
    _running = True
    _thread  = threading.Thread(target=_poll_loop, daemon=True)
    _thread.start()
    print("[HOTKEY] Manager started")

def stop():
    global _running
    _running = False
    print("[HOTKEY] Manager stopped")

# ── Preset binding sets ───────────────────────────────────────────────────────

def bind_preset_trainer(callbacks):
    """
    callbacks: dict of feature_name -> fn(state)
    Default layout:
      F1=godmode  F2=inf_ammo  F3=speed  F4=noclip
      F5=esp      F6=freeze    F7=tp_me  F8=kill_aura
      INS=reset_all  DEL=exit
    """
    layout = {
        "F1":"godmode","F2":"inf_ammo","F3":"speed","F4":"noclip",
        "F5":"esp","F6":"freeze","F7":"tp_me","F8":"kill_aura",
    }
    for key, feat in layout.items():
        if feat in callbacks:
            bind(key, callbacks[feat], name=feat.upper(), toggle=True)
    if "reset_all" in callbacks:
        bind("INS", callbacks["reset_all"], name="RESET_ALL", toggle=False)
    if "exit" in callbacks:
        bind("DEL", callbacks["exit"], name="EXIT", toggle=False)
    start()
