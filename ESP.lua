-- ESP Visible Hitbox | Delta Android Compatible
-- loadstring(game:HttpGet("RAW_URL"))()  <-- paste raw URL di executor

local Players   = game:GetService("Players")
local RunService = game:GetService("RunService")
local Camera    = workspace.CurrentCamera

local lp = Players.LocalPlayer

-- ┌─────────────────────────┐
-- │         CONFIG          │
-- └─────────────────────────┘
local Config = {
    Enabled     = true,

    -- Box
    Box         = true,
    BoxColor    = Color3.fromRGB(255, 50, 50),
    BoxThick    = 1.5,

    -- Tracer (line dari layar ke player)
    Tracer      = true,
    TracerColor = Color3.fromRGB(255, 255, 255),
    TracerThick = 1,
    TracerFrom  = "Bottom", -- "Bottom" / "Center" / "Top"

    -- Nama player
    Name        = true,
    NameColor   = Color3.fromRGB(255, 255, 255),

    -- Jarak
    Distance    = true,
    DistColor   = Color3.fromRGB(200, 200, 200),
    MaxDist     = 1000,

    -- Health bar
    HealthBar   = true,

    -- Skip teammate
    TeamCheck   = false,
}

-- ┌─────────────────────────┐
-- │      ESP OBJECTS        │
-- └─────────────────────────┘
local ESPObjects = {}

local function newDraw(type, props)
    local d = Drawing.new(type)
    for k, v in next, props do d[k] = v end
    return d
end

local function createESP(player)
    if player == lp then return end

    ESPObjects[player] = {
        -- 4 sisi box
        BoxTop    = newDraw("Line", {Color=Config.BoxColor, Thickness=Config.BoxThick, Visible=false}),
        BoxBottom = newDraw("Line", {Color=Config.BoxColor, Thickness=Config.BoxThick, Visible=false}),
        BoxLeft   = newDraw("Line", {Color=Config.BoxColor, Thickness=Config.BoxThick, Visible=false}),
        BoxRight  = newDraw("Line", {Color=Config.BoxColor, Thickness=Config.BoxThick, Visible=false}),

        -- Tracer line
        Tracer    = newDraw("Line", {Color=Config.TracerColor, Thickness=Config.TracerThick, Visible=false}),

        -- Nama
        Name      = newDraw("Text", {
            Text    = player.Name,
            Size    = 13,
            Color   = Config.NameColor,
            Center  = true,
            Outline = true,
            Visible = false,
        }),

        -- Jarak
        Distance  = newDraw("Text", {
            Size    = 12,
            Color   = Config.DistColor,
            Center  = true,
            Outline = true,
            Visible = false,
        }),

        -- Health bar (background + bar)
        HealthBG  = newDraw("Line", {Color=Color3.fromRGB(0,0,0), Thickness=4, Visible=false}),
        HealthBar = newDraw("Line", {Color=Color3.fromRGB(0,255,80), Thickness=3, Visible=false}),
    }
end

local function removeESP(player)
    if ESPObjects[player] then
        for _, obj in next, ESPObjects[player] do
            obj:Remove()
        end
        ESPObjects[player] = nil
    end
end

local function hideESP(esp)
    for _, obj in next, esp do
        obj.Visible = false
    end
end

-- ┌─────────────────────────┐
-- │       MAIN LOOP         │
-- └─────────────────────────┘
RunService.RenderStepped:Connect(function()
    if not Config.Enabled then
        for _, esp in next, ESPObjects do hideESP(esp) end
        return
    end

    local vpSize = Camera.ViewportSize
    local tracerOrigin
    if Config.TracerFrom == "Bottom" then
        tracerOrigin = Vector2.new(vpSize.X / 2, vpSize.Y)
    elseif Config.TracerFrom == "Center" then
        tracerOrigin = Vector2.new(vpSize.X / 2, vpSize.Y / 2)
    else
        tracerOrigin = Vector2.new(vpSize.X / 2, 0)
    end

    local lpChar = lp.Character
    local lpRoot = lpChar and lpChar:FindFirstChild("HumanoidRootPart")

    for player, esp in next, ESPObjects do
        local char = player.Character
        local hum  = char and char:FindFirstChildOfClass("Humanoid")
        local root = char and char:FindFirstChild("HumanoidRootPart")
        local head = char and char:FindFirstChild("Head")

        if not (char and hum and root and head and hum.Health > 0) then
            hideESP(esp)
            continue
        end

        if Config.TeamCheck and player.Team == lp.Team then
            hideESP(esp)
            continue
        end

        local dist = lpRoot and (lpRoot.Position - root.Position).Magnitude or 0
        if dist > Config.MaxDist then
            hideESP(esp)
            continue
        end

        -- Project 3D ke 2D (Drawing API otomatis tembus wall)
        local rootSP, _ = Camera:WorldToViewportPoint(root.Position)
        local headSP, _ = Camera:WorldToViewportPoint(head.Position + Vector3.new(0, 0.7, 0))

        -- Cek apakah player ada di depan kamera
        if rootSP.Z <= 0 then
            hideESP(esp)
            continue
        end

        -- Hitung ukuran box di layar
        local height = math.abs(headSP.Y - rootSP.Y) * 2
        local width  = height * 0.55

        local cx = rootSP.X
        local cy = (headSP.Y + rootSP.Y) / 2
        local x1, x2 = cx - width/2, cx + width/2
        local y1, y2 = cy - height/2, cy + height/2

        -- Box
        if Config.Box then
            esp.BoxTop.From    = Vector2.new(x1,y1) ; esp.BoxTop.To    = Vector2.new(x2,y1) ; esp.BoxTop.Visible    = true
            esp.BoxBottom.From = Vector2.new(x1,y2) ; esp.BoxBottom.To = Vector2.new(x2,y2) ; esp.BoxBottom.Visible = true
            esp.BoxLeft.From   = Vector2.new(x1,y1) ; esp.BoxLeft.To   = Vector2.new(x1,y2) ; esp.BoxLeft.Visible   = true
            esp.BoxRight.From  = Vector2.new(x2,y1) ; esp.BoxRight.To  = Vector2.new(x2,y2) ; esp.BoxRight.Visible  = true
        else
            esp.BoxTop.Visible=false ; esp.BoxBottom.Visible=false
            esp.BoxLeft.Visible=false ; esp.BoxRight.Visible=false
        end

        -- Tracer line
        if Config.Tracer then
            esp.Tracer.From    = tracerOrigin
            esp.Tracer.To      = Vector2.new(cx, y2)
            esp.Tracer.Visible = true
        else
            esp.Tracer.Visible = false
        end

        -- Nama
        if Config.Name then
            esp.Name.Position = Vector2.new(cx, y1 - 15)
            esp.Name.Visible  = true
        else
            esp.Name.Visible = false
        end

        -- Jarak
        if Config.Distance then
            esp.Distance.Text     = string.format("[%.0f]", dist)
            esp.Distance.Position = Vector2.new(cx, y2 + 2)
            esp.Distance.Visible  = true
        else
            esp.Distance.Visible = false
        end

        -- Health bar
        if Config.HealthBar then
            local hp   = math.clamp(hum.Health / hum.MaxHealth, 0, 1)
            local barX = x1 - 5
            esp.HealthBG.From    = Vector2.new(barX, y1)
            esp.HealthBG.To      = Vector2.new(barX, y2)
            esp.HealthBG.Visible = true
            esp.HealthBar.From   = Vector2.new(barX, y2)
            esp.HealthBar.To     = Vector2.new(barX, y2 - height * hp)
            esp.HealthBar.Color  = Color3.fromRGB(
                math.floor(255 * (1 - hp)),
                math.floor(255 * hp),
                0
            )
            esp.HealthBar.Visible = true
        else
            esp.HealthBG.Visible=false ; esp.HealthBar.Visible=false
        end
    end
end)

-- ┌─────────────────────────┐
-- │        EVENTS           │
-- └─────────────────────────┘
for _, p in next, Players:GetPlayers() do
    createESP(p)
end

Players.PlayerAdded:Connect(createESP)
Players.PlayerRemoving:Connect(removeESP)

print("[ESP] Loaded! Box + Tracer + HealthBar aktif")
