# XC Hub — Roblox Script Hub

Script hub untuk Roblox, diload via executor **Delta Android**.

> **Setiap sesi baru:** selalu baca `CLAUDE.md` dulu buat konteks lengkap project ini.

---

## Load Script

```lua
-- XC Hub (utama — semua fitur)
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/Hub.lua"))()

-- Standalone scripts
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/ESP.lua"))()
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/AutoHop.lua"))()
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/Crosshair.lua"))()
```

**Key Hub:** `CAESAR`

---

## Fitur XC Hub

| Toggle | Deskripsi |
|--------|-----------|
| ESP | Box hitbox ringan — 4 Drawing object per player |
| Auto Hop | Pindah server tiap 5 menit + anti-AFK |
| Auto Chest | Collect semua chest → auto hop server |
| Auto Fruit | Detect & collect devil fruit (Blox Fruits) |
| Crosshair | Custom crosshair + aim assist + hitmarker |
| Enemy Only Aim | Aim assist khusus musuh (default ON) |
| Silent Aim | Snap instan ke musuh saat tap/klik — twin dari Aim Assist |

---

## Struktur Repo

```
Hub.lua                              ← XC Hub utama
ESP.lua                              ← ESP standalone
AutoHop.lua                          ← Auto hop standalone
Crosshair.lua                        ← Crosshair standalone
scripts/
  VisibleHitbox_Executor.lua         ← Combat testing tool (private server)
src/
  shared/HitboxModule.lua
  client/HitboxVisualizer.client.lua
  server/HitboxService.server.lua
default.project.json                 ← Rojo sync config
CLAUDE.md                            ← Memo project — baca ini tiap sesi baru!
```

---

## Catatan

- 🔥 = langsung gas, no judge, no tanya
- Cek `CLAUDE.md` untuk config, rules kolaborasi, dan konteks lengkap
