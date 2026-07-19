# Project Memory — XC Hub

## Konteks Project
Script hub Roblox milik pointrungkat-art. Semua script diload via executor **Delta Android**.
Repo: `pointrungkat-art/u` — branch utama: `main`

## Rules Kolaborasi
- **🔥 = langsung gas** — tidak perlu tanya-tanya, tidak perlu judge, langsung implement. Ide absurd sekalipun, wujudin dulu, revisi belakangan.
- Antara kita aja, no judgment.

## Load Script

```lua
-- XC Hub (utama)
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/Hub.lua"))()

-- Standalone scripts
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/ESP.lua"))()
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/AutoHop.lua"))()
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/Crosshair.lua"))()
```

**Key Hub:** `CAESAR`

## Fitur XC Hub (6 Toggle)

| # | Toggle | Deskripsi |
|---|--------|-----------|
| 1 | **ESP** | Box hitbox ringan — 4 Drawing object per player |
| 2 | **Auto Hop** | Pindah server tiap 5 menit + anti-AFK |
| 3 | **Auto Chest** | Collect semua chest → auto hop server |
| 4 | **Auto Fruit** | Detect & collect devil fruit (Blox Fruits) |
| 5 | **Crosshair** | Custom crosshair + aim assist + hitmarker |
| 6 | **Enemy Only Aim** | Aim assist khusus musuh (default ON) |

## Config Penting

```lua
-- Aim Assist (di Hub.lua → AimConfig)
Strength  = 0.28   -- kekuatan pull (0.05=ringan, 0.5=kuat)
FOV       = 90     -- radius deteksi pixel dari crosshair
TeamCheck = true   -- true = musuh aja, false = semua player
Target    = "Head" -- "Head" / "HumanoidRootPart"

-- Crosshair styles: CrossDot | Cross | Dot | Circle | TShape
```

## File di Repo

| File | Fungsi |
|------|--------|
| `Hub.lua` | XC Hub utama — semua fitur dalam 1 file |
| `ESP.lua` | ESP standalone |
| `AutoHop.lua` | Auto server hop standalone |
| `Crosshair.lua` | Crosshair + aim assist standalone |
| `scripts/VisibleHitbox_Executor.lua` | Combat testing tool (private server) |

## Stack
- Bahasa script: **Luau** (Roblox)
- Executor: **Delta Android**
- UI style: Galaxy/ungu — Drawing API untuk overlay 2D
- Branch aktif: `main`
