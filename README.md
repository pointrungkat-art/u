# Roblox Hitbox System

Sistem hitbox reusable untuk Roblox (Luau) berbasis **spatial query**
(`GetPartBoundsInBox` / `GetPartBoundsInRadius`) — lebih akurat dan
anti-bocor dibanding `Touched` event.

## Fitur

- 📦 Bentuk **Box** atau **Sphere**
- 🎯 Deteksi Humanoid otomatis + callback `OnHit`
- ⏱️ **Debounce** per-humanoid (target sama gak kena berkali-kali)
- 🔢 Batas jumlah target (`MaxHits`)
- 🚫 Daftar **ignore** (mis. karakter penyerang)
- 🐛 **Visualize** mode buat debugging
- ⚡ Mode instan (`:Query`) atau mengikuti CFrame (`:Start`/`:Stop`)
- 🧩 Full Luau typing, tanpa dependency eksternal

## Struktur

```
src/
├── shared/
│   └── Hitbox/
│       └── init.lua              -- ModuleScript utama (taruh di ReplicatedStorage.Shared)
└── server/
    └── HitboxExample.server.lua  -- Contoh pemakaian (taruh di ServerScriptService)
```

## Pemakaian Singkat

```lua
local Hitbox = require(ReplicatedStorage.Shared.Hitbox)

local hb = Hitbox.new({
    Shape = "Box",
    Size = Vector3.new(6, 6, 6),
    Ignore = { attackerCharacter },
    Debounce = 0.5,
})

hb.OnHit:Connect(function(humanoid, hitPart, character)
    humanoid:TakeDamage(25)
end)

-- Ikuti CFrame senjata selama aktif:
hb:Start(function()
    return weaponPart.CFrame
end)

task.wait(0.3)
hb:Destroy()
```

## API

| Method | Keterangan |
|--------|-----------|
| `Hitbox.new(config)` | Buat hitbox baru |
| `hb:Start(getCFrame)` | Aktifkan, ikuti CFrame tiap frame |
| `hb:Stop()` | Matikan (reset debounce) |
| `hb:Query(cframe)` | Cek sekali di CFrame tertentu (hit instan) |
| `hb:AddToIgnore(instance)` | Tambah instance ke daftar abaikan |
| `hb:SetIgnoreList(list)` | Ganti seluruh daftar abaikan |
| `hb:Destroy()` | Bersihkan total |
| `hb.OnHit:Connect(fn)` | `fn(humanoid, hitPart, character)` |

### Opsi config

| Opsi | Tipe | Default | Keterangan |
|------|------|---------|-----------|
| `Shape` | `"Box"` \| `"Sphere"` | `"Box"` | Bentuk hitbox |
| `Size` | `Vector3` | `5,5,5` | Ukuran box |
| `Radius` | `number` | `5` | Radius sphere |
| `Ignore` | `{Instance}` | `{}` | Instance yang diabaikan |
| `Debounce` | `number` | `0` | Jeda (detik) sebelum target sama kena lagi |
| `MaxHits` | `number?` | `nil` | Batas target per aktivasi |
| `Visualize` | `boolean` | `false` | Tampilkan hitbox (debug) |

> ⚠️ Jalankan deteksi hitbox di **server** untuk mencegah cheat (server-authoritative).
