# Combat Game — Testing Toolkit

Roblox combat game project. Testing tools dijalankan via executor di private server.

## Script Utama

`scripts/VisibleHitbox_Executor.lua` — load via:
```lua
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/claude/yoo-bosku-b3l26m/scripts/VisibleHitbox_Executor.lua"))()
```

## Fitur

| Fitur | Key | Keterangan |
|-------|-----|------------|
| Visible Hitbox | `H` | Box + wireframe per karakter. Hijau=self, Merah=enemy |
| Hitbox Size | `G` | Cycle: Tight / Normal / Wide |
| Damage Popup | `D` | Angka damage float + hit effect sphere |
| Chams (ESP) | `E` | Highlight tembus dinding via DepthMode.AlwaysOnTop |
| Tracer | `T` | Garis dari bawah layar ke posisi player |

**Billboard per karakter:** Nama · HP bar (hijau→merah) · HP teks · Jarak

**Damage color:** ⚪ kecil → 🟡 50+ → 🟠 100+ → 🟣 150+

## Struktur Repo

```
scripts/
  VisibleHitbox_Executor.lua   ← executor script (self-contained)
src/
  shared/HitboxModule.lua      ← core hitbox logic (Rojo)
  client/HitboxVisualizer.client.lua
  server/HitboxService.server.lua
default.project.json           ← Rojo sync config
```

## Catatan

- Branch aktif: `claude/yoo-bosku-b3l26m`
- 🔥 = langsung gas, no judge, no tanya
