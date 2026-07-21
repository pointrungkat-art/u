#!/usr/bin/env python3
"""
CheatDev Overlay -- Transparent always-on-top ESP/info display
Uses tkinter (stdlib) -- no external deps.
Works on Windows/Linux/Mac.

Usage:
  python overlay.py                     -- demo overlay
  python overlay.py --game <proc_name>  -- live overlay reading game memory
  Import and use Overlay class directly for custom ESP.
"""
import tkinter as tk
import threading, time, sys, os, math

COLORS = {
    "esp_box":      "#FF0000",
    "esp_name":     "#FFFFFF",
    "esp_hp":       "#00FF00",
    "esp_dist":     "#FFFF00",
    "crosshair":    "#FF0000",
    "radar_bg":     "#1A1A1A",
    "radar_dot":    "#FF3333",
    "radar_self":   "#00FF88",
    "info_text":    "#00FF88",
    "info_bg":      "#000000",
    "warning":      "#FF4444",
    "skeleton":     "#FFFFFF",
    "tracer":       "#FF0000",
}

class Overlay:
    """Transparent always-on-top drawing canvas."""

    def __init__(self, width=None, height=None, title="CheatDev Overlay",
                 fps=60, transparent_color="black"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", transparent_color)
        self.root.overrideredirect(True)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.W = width  or sw
        self.H = height or sh
        self.root.geometry(f"{self.W}x{self.H}+0+0")
        self.root.configure(bg=transparent_color)
        # Pass click-through on Windows
        if sys.platform == "win32":
            import ctypes
            hwnd = ctypes.windll.user32.FindWindowW(None, title)
            GWL_EXSTYLE     = -20
            WS_EX_LAYERED   = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE,
                style | WS_EX_LAYERED | WS_EX_TRANSPARENT)

        self.canvas = tk.Canvas(self.root, width=self.W, height=self.H,
                                bg=transparent_color, highlightthickness=0)
        self.canvas.pack()
        self._fps     = fps
        self._delay   = int(1000 / fps)
        self._running = False
        self._items   = []
        self._draw_fn = None
        self._lock    = threading.Lock()

    # ── Draw primitives ───────────────────────────────────────────────────────

    def clear(self):
        self.canvas.delete("all")

    def box(self, x, y, w, h, color=COLORS["esp_box"], width=2, filled=False):
        fill = color if filled else ""
        self.canvas.create_rectangle(x, y, x+w, y+h,
                                      outline=color, fill=fill, width=width)

    def box_3d(self, x, y, w, h, color=COLORS["esp_box"], corner_len=6, width=2):
        """Corner-only box (cleaner ESP look)."""
        c = self.canvas.create_line
        cl = corner_len
        # top-left
        c(x,y, x+cl,y, fill=color, width=width)
        c(x,y, x,y+cl, fill=color, width=width)
        # top-right
        c(x+w,y, x+w-cl,y, fill=color, width=width)
        c(x+w,y, x+w,y+cl, fill=color, width=width)
        # bottom-left
        c(x,y+h, x+cl,y+h, fill=color, width=width)
        c(x,y+h, x,y+h-cl, fill=color, width=width)
        # bottom-right
        c(x+w,y+h, x+w-cl,y+h, fill=color, width=width)
        c(x+w,y+h, x+w,y+h-cl, fill=color, width=width)

    def text(self, x, y, txt, color=COLORS["info_text"], size=12, bold=False, anchor="nw"):
        weight = "bold" if bold else "normal"
        self.canvas.create_text(x, y, text=txt, fill=color,
                                  font=("Consolas", size, weight), anchor=anchor)

    def text_bg(self, x, y, txt, fg=COLORS["info_text"], bg=COLORS["info_bg"],
                size=11, padding=2):
        self.canvas.create_text(x, y, text=txt, fill=fg,
                                  font=("Consolas", size, "bold"), anchor="nw",
                                  tags="tbg")
        # simple background rectangle approximation
        char_w = size * 0.65
        self.canvas.create_rectangle(x-padding, y-padding,
                                      x + len(txt)*char_w + padding,
                                      y + size + padding,
                                      fill=bg, outline="", tags="tbg_rect")
        self.canvas.tag_lower("tbg_rect", "tbg")

    def line(self, x1, y1, x2, y2, color=COLORS["tracer"], width=1):
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

    def circle(self, cx, cy, r, color=COLORS["crosshair"], width=1, filled=False):
        fill = color if filled else ""
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                 outline=color, fill=fill, width=width)

    def hp_bar(self, x, y, w, h, hp_pct, bg="#333333"):
        self.canvas.create_rectangle(x, y, x+w, y+h, fill=bg, outline="")
        color = "#00FF00" if hp_pct > 0.5 else "#FFFF00" if hp_pct > 0.25 else "#FF0000"
        self.canvas.create_rectangle(x, y, x+int(w*hp_pct), y+h, fill=color, outline="")

    def crosshair(self, size=12, gap=3, color=COLORS["crosshair"],
                  style="cross", width=2):
        cx, cy = self.W // 2, self.H // 2
        if style == "cross":
            self.line(cx-size, cy, cx-gap, cy, color, width)
            self.line(cx+gap, cy, cx+size, cy, color, width)
            self.line(cx, cy-size, cx, cy-gap, color, width)
            self.line(cx, cy+gap, cx, cy+size, color, width)
        elif style == "dot":
            self.circle(cx, cy, 2, color, width=0, filled=True)
        elif style == "circle":
            self.circle(cx, cy, size, color, width)
        elif style == "crossdot":
            self.line(cx-size, cy, cx-gap, cy, color, width)
            self.line(cx+gap, cy, cx+size, cy, color, width)
            self.line(cx, cy-size, cx, cy-gap, color, width)
            self.line(cx, cy+gap, cx, cy+size, color, width)
            self.circle(cx, cy, 2, color, width=0, filled=True)
        elif style == "tshape":
            self.line(cx-size, cy, cx+size, cy, color, width)
            self.line(cx, cy-size, cx, cy, color, width)

    def radar(self, rx, ry, radius, entities, self_pos=(0,0,0), scale=0.5):
        """Mini radar circle with entity dots."""
        self.circle(rx, ry, radius, COLORS["radar_bg"], filled=True)
        self.circle(rx, ry, radius, "#444444", width=1)
        # self dot
        self.circle(rx, ry, 3, COLORS["radar_self"], filled=True)
        # entity dots
        sx, _, sz = self_pos
        for ent in entities:
            ex, _, ez = ent.get("pos", (0,0,0))
            dx = (ex - sx) * scale
            dz = (ez - sz) * scale
            dot_x = rx + dx
            dot_y = ry + dz
            dist2d = math.sqrt(dx**2 + dz**2)
            if dist2d <= radius:
                col = ent.get("color", COLORS["radar_dot"])
                self.circle(int(dot_x), int(dot_y), 3, col, filled=True)

    def esp_player(self, x, y, w, h, name="", hp_pct=1.0, dist=0,
                   team=False, tracer=True, box_style="corner"):
        """Full player ESP: box + name + HP bar + distance + tracer."""
        col = "#00AAFF" if team else COLORS["esp_box"]
        if box_style == "corner":
            self.box_3d(x, y, w, h, col)
        else:
            self.box(x, y, w, h, col)
        if name:
            self.text(x + w//2, y-16, name, COLORS["esp_name"], size=10, anchor="center")
        if dist:
            self.text(x + w//2, y-28, f"{int(dist)}m", COLORS["esp_dist"], size=9, anchor="center")
        self.hp_bar(x, y+h+2, w, 4, hp_pct)
        if tracer:
            self.line(self.W//2, self.H, x+w//2, y+h, col, width=1)

    def info_panel(self, x, y, lines, size=11):
        """HUD info panel — list of (label, value) or plain strings."""
        for i, item in enumerate(lines):
            if isinstance(item, (list, tuple)) and len(item) == 2:
                label, val = item
                self.text(x, y + i*(size+4), f"{label}: ", "#888888", size=size)
                self.text(x + len(str(label))*7 + 2, y + i*(size+4), str(val),
                          COLORS["info_text"], size=size)
            else:
                self.text(x, y + i*(size+4), str(item), COLORS["info_text"], size=size)

    # ── Loop ─────────────────────────────────────────────────────────────────

    def set_draw(self, fn):
        """Set the draw callback fn(overlay) called each frame."""
        self._draw_fn = fn

    def _tick(self):
        if not self._running:
            return
        self.clear()
        if self._draw_fn:
            try:
                self._draw_fn(self)
            except Exception as e:
                self.text(10, 10, f"[ERR] {e}", "#FF4444", size=10)
        self.root.after(self._delay, self._tick)

    def run(self):
        self._running = True
        self.root.after(self._delay, self._tick)
        self.root.mainloop()

    def stop(self):
        self._running = False
        self.root.destroy()


# ── Demo + standalone ─────────────────────────────────────────────────────────

def demo_draw(ov):
    """Demo overlay — shows all ESP features."""
    t = time.time()

    # Fake player ESP
    ov.esp_player(200, 150, 60, 120, name="Enemy_01", hp_pct=0.72, dist=45)
    ov.esp_player(400, 200, 50, 100, name="Enemy_02", hp_pct=0.30, dist=78, box_style="full")
    ov.esp_player(600, 100, 55, 110, name="TeamMate", hp_pct=1.0, dist=12, team=True, tracer=False)

    # Crosshair
    ov.crosshair(style="crossdot", color="#FF2222", size=10)

    # Radar (bottom-left)
    fake_entities = [
        {"pos": (10, 0, 5),  "color": "#FF3333"},
        {"pos": (-8, 0, 12), "color": "#FF3333"},
        {"pos": (3, 0, -6),  "color": "#00FF88"},
    ]
    ov.radar(80, ov.H-80, 70, fake_entities, self_pos=(0,0,0), scale=3)

    # Info panel (top-left)
    ov.info_panel(10, 10, [
        ("FPS",     "144"),
        ("Players", "3"),
        ("Mode",    "CheatDev v2"),
        ("ESP",     "ON"),
        ("AimBot",  "ON" if int(t*2) % 2 == 0 else "ON"),
    ])

    # Watermark
    ov.text(ov.W - 180, 10, "CheatDev Overlay", "#444444", size=10)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", help="Game process (enables live memory read)")
    parser.add_argument("--fps",  type=int, default=60)
    parser.add_argument("--demo", action="store_true", default=True)
    args = parser.parse_args()

    ov = Overlay(fps=args.fps)
    ov.set_draw(demo_draw)
    print("[OVERLAY] Starting — Ctrl+C or close window to exit")
    ov.run()
