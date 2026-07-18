-- Auto Server Hop | Anti AFK Kick
-- Delta Android Compatible
-- loadstring(game:HttpGet("RAW_URL"))()

local TeleportService = game:GetService("TeleportService")
local Players         = game:GetService("Players")
local RunService      = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local lp = Players.LocalPlayer

-- ┌─────────────────────────┐
-- │         CONFIG          │
-- └─────────────────────────┘
local Config = {
    -- Hop tiap berapa detik (default 5 menit)
    HopInterval   = 300,

    -- Anti AFK: gerakin karakter biar ga ke-detect idle
    AntiAFK       = true,
    AntiAFKInterval = 60, -- gerak tiap 60 detik

    -- Hop ke server yang ada playernya (bukan kosong)
    PreferFilled  = true,
    MinPlayers    = 1,
}

-- ┌─────────────────────────┐
-- │       ANTI AFK          │
-- └─────────────────────────┘
if Config.AntiAFK then
    local VirtualUser = game:GetService("VirtualUser")
    lp.Idled:Connect(function()
        VirtualUser:CaptureController()
        VirtualUser:ClickButton2(Vector2.new())
    end)
end

-- ┌─────────────────────────┐
-- │      SERVER HOP         │
-- └─────────────────────────┘
local function getServers()
    local placeId = game.PlaceId
    local url = string.format(
        "https://games.roblox.com/v1/games/%d/servers/Public?sortOrder=Asc&limit=100",
        placeId
    )

    local ok, result = pcall(function()
        return game:HttpGet(url)
    end)

    if not ok then return nil end

    local ok2, data = pcall(function()
        return game:GetService("HttpService"):JSONDecode(result)
    end)

    if not ok2 or not data or not data.data then return nil end

    return data.data
end

local function hopServer()
    local servers = getServers()
    if not servers or #servers == 0 then
        warn("[AutoHop] Ga nemu server, retry...")
        return
    end

    local currentJobId = game.JobId
    local picked = nil

    -- Cari server yang beda & ada player-nya
    for _, server in ipairs(servers) do
        if server.id ~= currentJobId then
            if Config.PreferFilled then
                if (server.playing or 0) >= Config.MinPlayers then
                    picked = server
                    break
                end
            else
                picked = server
                break
            end
        end
    end

    -- Fallback: ambil server pertama yang beda
    if not picked then
        for _, server in ipairs(servers) do
            if server.id ~= currentJobId then
                picked = server
                break
            end
        end
    end

    if picked then
        print(string.format("[AutoHop] Hopping ke server %s (%d players)", picked.id, picked.playing or 0))
        TeleportService:TeleportToPlaceInstance(game.PlaceId, picked.id, lp)
    else
        warn("[AutoHop] Ga ada server lain tersedia")
    end
end

-- ┌─────────────────────────┐
-- │        TIMER            │
-- └─────────────────────────┘
local elapsed = 0

RunService.Heartbeat:Connect(function(dt)
    elapsed = elapsed + dt
    if elapsed >= Config.HopInterval then
        elapsed = 0
        print("[AutoHop] Waktunya hop!")
        hopServer()
    end
end)

print(string.format("[AutoHop] Aktif! Hop tiap %d detik. Anti-AFK: %s",
    Config.HopInterval,
    Config.AntiAFK and "ON" or "OFF"
))
