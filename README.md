# u — Roblox Combat System

Combat system buat Roblox, dimulai dari **visible hitbox** untuk testing.

## Struktur

```
src/
├── shared/
│   └── Hitbox.luau              -> ReplicatedStorage.Shared.Hitbox (modul inti)
├── server/
│   └── CombatServer.server.luau -> ServerScriptService (logika hit & damage)
└── client/
    └── CombatClient.client.luau -> StarterPlayerScripts (input tombol F)
```

## Cara jalanin (Rojo + Studio)

1. Install [Rojo](https://rojo.space/) + plugin-nya di Studio.
2. Di folder ini jalanin:
   ```
   rojo serve
   ```
3. Di Studio, klik **Connect** lewat plugin Rojo.
4. Play (F5), lalu **tekan F** buat nyerang.

Hitbox bakal muncul sebagai **kotak merah transparan** di depan karakter.
Kalau kena player/NPC lain, di Output muncul log hit dan target kena damage.

## Tanpa Rojo (manual)

Copy manual ke Studio:
- `Hitbox.luau` -> ModuleScript di `ReplicatedStorage`, taro dalam Folder `Shared`
- `CombatServer.server.luau` -> Script di `ServerScriptService`
- `CombatClient.client.luau` -> LocalScript di `StarterPlayer > StarterPlayerScripts`

## Modul Hitbox

Pakai spatial query (`GetPartBoundsInBox`) — akurat & anti-miss, bukan `.Touched`.

```lua
local Hitbox = require(ReplicatedStorage.Shared.Hitbox)

local hb = Hitbox.new({
    Size = Vector3.new(5, 5, 6),
    AttachTo = root,               -- ngikutin part ini
    Offset = CFrame.new(0, 0, -4), -- geser ke depan
    Debug = true,                  -- tampilin hitbox (set false di produksi)
    FilterList = { character },    -- ignore penyerang
})

hb:OnHit(function(humanoid, model, part)
    humanoid:TakeDamage(10)
end)

hb:Start()
task.delay(0.25, function() hb:Destroy() end)
```

### API
| Method | Fungsi |
|---|---|
| `Hitbox.new(config)` | Bikin hitbox baru |
| `:OnHit(callback)` | Daftarin fungsi yang jalan pas kena target |
| `:Start()` | Mulai deteksi (scan tiap frame) |
| `:Stop()` | Berhenti deteksi + hapus visual |
| `:Destroy()` | Bersihin total |
