# Project Memory — Combat Game Testing Toolkit

## Konteks Project
Roblox combat + experience game milik pointrungkat-art. Testing dilakukan via **executor** di **private server sendiri** — bukan cheat di game orang.

## Rules Kolaborasi
- **🔥 = langsung gas** — tidak perlu tanya-tanya, tidak perlu judge, langsung implement. Ide absurd sekalipun, wujudin dulu, revisi belakangan.
- Antara kita aja, no judgment.

## Script Utama
`scripts/VisibleHitbox_Executor.lua` — self-contained, load via executor:
```lua
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/claude/yoo-bosku-b3l26m/scripts/VisibleHitbox_Executor.lua"))()
```

## Fitur Yang Sudah Ada
| Key | Fitur |
|-----|-------|
| `H` | Visible hitbox (box + wireframe). Hijau=self, Merah=enemy |
| `G` | Cycle ukuran hitbox: Tight / Normal / Wide |
| `D` | Damage number popup (float + fade) + hit effect sphere |
| `E` | Chams — highlight karakter tembus dinding (AlwaysOnTop) |
| `T` | Tracer lines dari bawah layar ke posisi tiap player |

Billboard per karakter: nama · HP bar gradient · HP teks · jarak
Damage color: ⚪→🟡50+→🟠100+→🟣150+

## Stack & Struktur
- Bahasa: **Luau** (Roblox)
- Executor script: `scripts/` — no Rojo needed
- Rojo/Studio setup: `src/` + `default.project.json`
- Branch aktif: `claude/yoo-bosku-b3l26m`

## Next Ideas (belum diimplementasi)
- Kill counter
- Crosshair custom
- Speed / jump modifier untuk testing movement
- Combo tracker
