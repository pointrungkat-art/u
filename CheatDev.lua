--[[
 ██████╗██╗  ██╗███████╗ █████╗ ████████╗    ██████╗ ███████╗██╗   ██╗
██╔════╝██║  ██║██╔════╝██╔══██╗╚══██╔══╝    ██╔══██╗██╔════╝██║   ██║
██║     ███████║█████╗  ███████║   ██║       ██║  ██║█████╗  ██║   ██║
██║     ██╔══██║██╔══╝  ██╔══██║   ██║       ██║  ██║██╔══╝  ╚██╗ ██╔╝
╚██████╗██║  ██║███████╗██║  ██║   ██║       ██████╔╝███████╗ ╚████╔╝
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ╚═╝       ╚═════╝ ╚══════╝  ╚═══╝

   ██████╗██╗  ██╗███████╗ █████╗ ████████╗    ██████╗  ██████╗ ██╗
  ██╔════╝██║  ██║██╔════╝██╔══██╗╚══██╔══╝    ██╔══██╗██╔═══██╗╚██╗
  ██║     ███████║█████╗  ███████║   ██║       ██║  ██║██║   ██║ ██║
  ██║     ██╔══██║██╔══╝  ██╔══██║   ██║       ██║  ██║██║   ██║ ██║
  ╚██████╗██║  ██║███████╗██║  ██║   ██║       ██████╔╝╚██████╔╝██╔╝
   ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ╚═╝       ╚═════╝  ╚═════╝ ╚═╝

  🔥 CHEAT DEV v1.0 | pointrungkat-art | Delta Android Compatible
  🔥 "Absurd? Gas. Gila? Gas. Gagal? Belakang aja. DAR DER DOR."
  🔥 Unified Developer Hub — All hubs + Script Forge + Dev Console

  loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/CheatDev.lua"))()
--]]

-- ══════════════════════════════════════════════════════════════════
--  CHEAT DEV CORE BOOTSTRAP
-- ══════════════════════════════════════════════════════════════════

local CD = {}
CD._VERSION = "1.0.0"
CD._NAME    = "Cheat Developer"
CD._AUTHOR  = "pointrungkat-art"
CD._KEY     = "XCDEV"
CD._MOTTO   = "Absurd? Gas. Gagal? Belakang aja."

-- Services
local Players         = game:GetService("Players")
local RunService      = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local TweenService    = game:GetService("TweenService")
local HttpService     = game:GetService("HttpService")
local LocalPlayer     = Players.LocalPlayer
local Camera          = workspace.CurrentCamera

-- ══════════════════════════════════════════════════════════════════
--  COLOUR SYSTEM — Galaxy Dev Palette
-- ══════════════════════════════════════════════════════════════════

local COLOR = {
    BG        = Color3.fromRGB(10,  8,  20),
    BG2       = Color3.fromRGB(18, 14, 35),
    ACCENT    = Color3.fromRGB(180, 80, 255),
    ACCENT2   = Color3.fromRGB(80,  200, 255),
    ACCENT3   = Color3.fromRGB(255, 80,  160),
    FIRE      = Color3.fromRGB(255, 140, 30),
    TEXT      = Color3.fromRGB(230, 225, 255),
    TEXTDIM   = Color3.fromRGB(130, 120, 160),
    SUCCESS   = Color3.fromRGB(80,  255, 130),
    WARN      = Color3.fromRGB(255, 200, 50),
    ERR       = Color3.fromRGB(255, 70,  70),
    WHITE     = Color3.new(1,1,1),
    BLACK     = Color3.new(0,0,0),
}

-- ══════════════════════════════════════════════════════════════════
--  KEY GATE
-- ══════════════════════════════════════════════════════════════════

local function KeyGate()
    local _k = "" -- will be set by prompt
    -- Simplified key check (UI prompt injected below)
    return _k == CD._KEY
end

-- ══════════════════════════════════════════════════════════════════
--  UTILS
-- ══════════════════════════════════════════════════════════════════

local Utils = {}

function Utils.GetRootPart(player)
    local char = player.Character
    return char and char:FindFirstChild("HumanoidRootPart")
end

function Utils.GetHead(player)
    local char = player.Character
    return char and char:FindFirstChild("Head")
end

function Utils.GetHumanoid(player)
    local char = player.Character
    return char and char:FindFirstChildOfClass("Humanoid")
end

function Utils.IsAlive(player)
    local hum = Utils.GetHumanoid(player)
    return hum and hum.Health > 0
end

function Utils.IsEnemy(player)
    if not LocalPlayer.Team or not player.Team then return true end
    return player.Team ~= LocalPlayer.Team
end

function Utils.WorldToScreen(pos)
    local sp, vis = Camera:WorldToScreenPoint(pos)
    return Vector2.new(sp.X, sp.Y), vis, sp.Z
end

function Utils.Distance(a, b)
    return (a.Position - b.Position).Magnitude
end

function Utils.SafeTPart(part, cf)
    local ok, err = pcall(function()
        if part and part.Parent then
            part.CFrame = cf
        end
    end)
    return ok
end

function Utils.Log(tag, msg, col)
    local prefix = string.format("[CheatDev][%s]", tag)
    if getcustomasset then
        -- silent for executor
    end
    print(prefix, msg)
end

-- ══════════════════════════════════════════════════════════════════
--  DRAWING FACTORY
-- ══════════════════════════════════════════════════════════════════

local DrawFactory = {}

function DrawFactory.Box(color, thickness, filled)
    local d = Drawing.new("Square")
    d.Color     = color or COLOR.ACCENT
    d.Thickness = thickness or 1.5
    d.Filled    = filled or false
    d.Visible   = false
    return d
end

function DrawFactory.Line(color, thickness)
    local d = Drawing.new("Line")
    d.Color     = color or COLOR.ACCENT2
    d.Thickness = thickness or 1
    d.Visible   = false
    return d
end

function DrawFactory.Text(text, size, color, center, outline)
    local d = Drawing.new("Text")
    d.Text        = text or ""
    d.Size        = size or 13
    d.Color       = color or COLOR.TEXT
    d.Center      = center ~= nil and center or true
    d.Outline     = outline ~= nil and outline or true
    d.OutlineColor= COLOR.BLACK
    d.Visible     = false
    return d
end

function DrawFactory.Circle(radius, color, thickness, filled)
    local d = Drawing.new("Circle")
    d.Radius    = radius or 60
    d.Color     = color or COLOR.ACCENT
    d.Thickness = thickness or 1.5
    d.Filled    = filled or false
    d.Visible   = false
    return d
end

function DrawFactory.Triangle(color, thickness, filled)
    local d = Drawing.new("Triangle")
    d.Color     = color or COLOR.ACCENT3
    d.Thickness = thickness or 1.5
    d.Filled    = filled or false
    d.Visible   = false
    return d
end

-- ══════════════════════════════════════════════════════════════════
--  MODULE: ESP — Enhanced Dev Edition
-- ══════════════════════════════════════════════════════════════════

local ESPModule = {}
ESPModule.Enabled     = false
ESPModule.ShowBox     = true
ESPModule.ShowName    = true
ESPModule.ShowHP      = true
ESPModule.ShowDist    = true
ESPModule.ShowTracer  = false
ESPModule.ShowSkeleton= false
ESPModule.MaxDist     = 500
ESPModule.BoxColor    = COLOR.ACCENT
ESPModule.TracerColor = COLOR.ACCENT2
ESPModule._objs       = {}

local function ESPCreate(player)
    ESPModule._objs[player] = {
        Box    = DrawFactory.Box(ESPModule.BoxColor, 1.5),
        BoxOut = DrawFactory.Box(COLOR.BLACK, 3),
        Name   = DrawFactory.Text("", 13, COLOR.TEXT),
        HP     = DrawFactory.Text("", 12, COLOR.SUCCESS),
        Dist   = DrawFactory.Text("", 12, COLOR.TEXTDIM),
        Tracer = DrawFactory.Line(ESPModule.TracerColor, 1.5),
    }
end

local function ESPRemove(player)
    if ESPModule._objs[player] then
        for _, d in pairs(ESPModule._objs[player]) do
            pcall(function() d:Remove() end)
        end
        ESPModule._objs[player] = nil
    end
end

local function ESPUpdate()
    if not ESPModule.Enabled then
        for _, objs in pairs(ESPModule._objs) do
            for _, d in pairs(objs) do d.Visible = false end
        end
        return
    end
    for _, player in ipairs(Players:GetPlayers()) do
        if player == LocalPlayer then continue end
        local objs = ESPModule._objs[player]
        if not objs then continue end
        local root = Utils.GetRootPart(player)
        local head = Utils.GetHead(player)
        local hum  = Utils.GetHumanoid(player)
        if not root or not head or not hum or not Utils.IsAlive(player) then
            for _, d in pairs(objs) do d.Visible = false end
            continue
        end
        local dist = Utils.Distance(LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("HumanoidRootPart") or root, root)
        if dist > ESPModule.MaxDist then
            for _, d in pairs(objs) do d.Visible = false end
            continue
        end
        -- Box corners
        local topPos  = head.Position + Vector3.new(0, 0.7, 0)
        local botPos  = root.Position - Vector3.new(0, 3,   0)
        local sp_top, vis_top = Utils.WorldToScreen(topPos)
        local sp_bot, vis_bot = Utils.WorldToScreen(botPos)
        if not vis_top and not vis_bot then
            for _, d in pairs(objs) do d.Visible = false end
            continue
        end
        local h = math.abs(sp_top.Y - sp_bot.Y)
        local w = h * 0.45
        local x = sp_top.X - w/2
        local y = sp_top.Y
        -- Outline box
        objs.BoxOut.Size     = Vector2.new(w + 2, h + 2)
        objs.BoxOut.Position = Vector2.new(x - 1, y - 1)
        objs.BoxOut.Visible  = ESPModule.ShowBox
        -- Main box
        objs.Box.Size     = Vector2.new(w, h)
        objs.Box.Position = Vector2.new(x, y)
        objs.Box.Color    = ESPModule.BoxColor
        objs.Box.Visible  = ESPModule.ShowBox
        -- Name
        objs.Name.Text     = player.Name
        objs.Name.Position = Vector2.new(sp_top.X, y - 16)
        objs.Name.Visible  = ESPModule.ShowName
        -- HP bar text
        local hpPct = math.floor((hum.Health / hum.MaxHealth) * 100)
        local hpCol = hpPct > 60 and COLOR.SUCCESS or (hpPct > 30 and COLOR.WARN or COLOR.ERR)
        objs.HP.Text     = hpPct .. "%"
        objs.HP.Color    = hpCol
        objs.HP.Position = Vector2.new(sp_top.X, y + h + 2)
        objs.HP.Visible  = ESPModule.ShowHP
        -- Dist
        objs.Dist.Text     = string.format("%.0fm", dist)
        objs.Dist.Position = Vector2.new(sp_top.X, y + h + 15)
        objs.Dist.Visible  = ESPModule.ShowDist
        -- Tracer
        if ESPModule.ShowTracer then
            local screenH = Camera.ViewportSize.Y
            objs.Tracer.From    = Vector2.new(Camera.ViewportSize.X/2, screenH)
            objs.Tracer.To      = Vector2.new(sp_bot.X, sp_bot.Y)
            objs.Tracer.Visible = true
        else
            objs.Tracer.Visible = false
        end
    end
end

Players.PlayerAdded:Connect(ESPCreate)
Players.PlayerRemoving:Connect(ESPRemove)
for _, p in ipairs(Players:GetPlayers()) do
    if p ~= LocalPlayer then ESPCreate(p) end
end

-- ══════════════════════════════════════════════════════════════════
--  MODULE: AIM ASSIST — Dev Precision Edition
-- ══════════════════════════════════════════════════════════════════

local AimModule = {}
AimModule.Enabled     = false
AimModule.Strength    = 0.28
AimModule.FOV         = 90
AimModule.TeamCheck   = true
AimModule.Target      = "Head"
AimModule.ShowFOVRing = true
AimModule.SilentAim   = false
AimModule.Prediction  = true
AimModule.PredMult    = 0.08
AimModule._fovRing    = DrawFactory.Circle(AimModule.FOV, COLOR.ACCENT, 1.5)
AimModule._crossV     = DrawFactory.Line(COLOR.ACCENT3, 2)
AimModule._crossH     = DrawFactory.Line(COLOR.ACCENT3, 2)
AimModule._dot        = DrawFactory.Circle(3, COLOR.ACCENT3, 1, true)

local function AimGetTarget()
    local best, bestDist = nil, math.huge
    local center = Vector2.new(Camera.ViewportSize.X/2, Camera.ViewportSize.Y/2)
    for _, player in ipairs(Players:GetPlayers()) do
        if player == LocalPlayer then continue end
        if AimModule.TeamCheck and not Utils.IsEnemy(player) then continue end
        if not Utils.IsAlive(player) then continue end
        local part = player.Character and player.Character:FindFirstChild(AimModule.Target)
            or Utils.GetRootPart(player)
        if not part then continue end
        local sp, vis = Utils.WorldToScreen(part.Position)
        if not vis then continue end
        local d = (sp - center).Magnitude
        if d < AimModule.FOV and d < bestDist then
            best, bestDist = player, d
        end
    end
    return best
end

local function AimUpdate()
    local center = Vector2.new(Camera.ViewportSize.X/2, Camera.ViewportSize.Y/2)
    -- FOV Ring
    AimModule._fovRing.Radius  = AimModule.FOV
    AimModule._fovRing.Position = center
    AimModule._fovRing.Visible  = AimModule.ShowFOVRing and AimModule.Enabled
    -- Crosshair
    local cs = 8
    AimModule._crossV.From    = Vector2.new(center.X, center.Y - cs)
    AimModule._crossV.To      = Vector2.new(center.X, center.Y + cs)
    AimModule._crossV.Visible = AimModule.Enabled
    AimModule._crossH.From    = Vector2.new(center.X - cs, center.Y)
    AimModule._crossH.To      = Vector2.new(center.X + cs, center.Y)
    AimModule._crossH.Visible = AimModule.Enabled
    AimModule._dot.Position   = center
    AimModule._dot.Visible    = AimModule.Enabled

    if not AimModule.Enabled then return end
    local target = AimGetTarget()
    if not target then return end
    local part = target.Character and target.Character:FindFirstChild(AimModule.Target)
        or Utils.GetRootPart(target)
    if not part then return end
    local targetPos = part.Position
    if AimModule.Prediction then
        local vel = part.AssemblyLinearVelocity or Vector3.zero
        targetPos = targetPos + vel * AimModule.PredMult
    end
    local sp = Utils.WorldToScreen(targetPos)
    local dir = (sp - center)
    local newCF = Camera.CFrame * CFrame.Angles(
        math.rad(-dir.Y * AimModule.Strength * 0.05),
        math.rad(-dir.X * AimModule.Strength * 0.05),
        0
    )
    Camera.CFrame = newCF
end

-- Silent Aim hook
local SilentAimModule = {}
SilentAimModule.Enabled = false

-- ══════════════════════════════════════════════════════════════════
--  MODULE: AUTO HOP — Server Surfer
-- ══════════════════════════════════════════════════════════════════

local HopModule = {}
HopModule.Enabled  = false
HopModule.Interval = 300 -- 5 menit
HopModule.AntiAFK  = true
HopModule._timer   = 0
HopModule._afkTimer= 0

local function HopServer()
    if not HopModule.Enabled then return end
    local servers = {}
    local ok, data = pcall(function()
        return HttpService:JSONDecode(game:HttpGet(
            "https://games.roblox.com/v1/games/"..game.PlaceId.."/servers/Public?limit=25"
        ))
    end)
    if ok and data and data.data then
        for _, s in ipairs(data.data) do
            if s.id ~= game.JobId and s.playing < s.maxPlayers then
                table.insert(servers, s.id)
            end
        end
    end
    if #servers > 0 then
        local pick = servers[math.random(1, #servers)]
        Utils.Log("HOP", "Jumping to server: "..pick)
        game:GetService("TeleportService"):TeleportToPlaceInstance(game.PlaceId, pick, LocalPlayer)
    end
end

local function HopUpdate(dt)
    if not HopModule.Enabled then return end
    HopModule._timer = HopModule._timer + dt
    if HopModule._timer >= HopModule.Interval then
        HopModule._timer = 0
        HopServer()
    end
    if HopModule.AntiAFK then
        HopModule._afkTimer = HopModule._afkTimer + dt
        if HopModule._afkTimer >= 60 then
            HopModule._afkTimer = 0
            local vjs = LocalPlayer:FindFirstChild("PlayerGui") -- dummy touch
            pcall(function()
                FireTouchInterest(LocalPlayer.Character.HumanoidRootPart, workspace.Baseplate, 0)
            end)
        end
    end
end

-- ══════════════════════════════════════════════════════════════════
--  MODULE: SCRIPT FORGE 🔥 — Dev Tool Utama
--  Build, inject, & craft cheat scripts secara real-time
-- ══════════════════════════════════════════════════════════════════

local ScriptForge = {}
ScriptForge.Enabled  = false
ScriptForge.Scripts  = {}

-- Template Library — siap pakai, tinggal /C
ScriptForge.Templates = {
    ["ESP_QUICK"] = [[
-- Quick ESP — Inject langsung
local Players = game:GetService("Players")
local Camera = workspace.CurrentCamera
local LP = Players.LocalPlayer
for _, p in ipairs(Players:GetPlayers()) do
    if p ~= LP then
        local box = Drawing.new("Square")
        box.Color = Color3.fromRGB(180,80,255)
        box.Thickness = 1.5
        box.Filled = false
        box.Visible = true
    end
end
]],
    ["SPEED_HACK"] = [[
-- Speed Hack — toggle dengan /C SpeedHack
local Players = game:GetService("Players")
local LP = Players.LocalPlayer
local char = LP.Character or LP.CharacterAdded:Wait()
local hum = char:WaitForChild("Humanoid")
hum.WalkSpeed = 100  -- Default normal = 16
-- hum.JumpPower = 100 -- default 50
]],
    ["NOCLIP"] = [[
-- No Clip — karakter tembus dinding
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local LP = Players.LocalPlayer
local noclip = true
RunService.Stepped:Connect(function()
    if noclip and LP.Character then
        for _, p in ipairs(LP.Character:GetDescendants()) do
            if p:IsA("BasePart") then
                p.CanCollide = false
            end
        end
    end
end)
]],
    ["TELEPORT_ME"] = [[
-- Teleport ke player/koordinat
-- Usage: teleportTo(game.Players.YourTarget.Character.HumanoidRootPart.Position)
local function teleportTo(pos)
    local LP = game:GetService("Players").LocalPlayer
    local char = LP.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        char.HumanoidRootPart.CFrame = CFrame.new(pos)
    end
end
-- teleportTo(Vector3.new(0, 50, 0))
]],
    ["INF_JUMP"] = [[
-- Infinite Jump — tahan space terus lompat
local Players = game:GetService("Players")
local UIS = game:GetService("UserInputService")
local LP = Players.LocalPlayer
UIS.JumpRequest:Connect(function()
    local char = LP.Character
    if char then
        local hum = char:FindFirstChildOfClass("Humanoid")
        if hum then hum:ChangeState(Enum.HumanoidStateType.Jumping) end
    end
end)
]],
    ["KILL_AURA"] = [[
-- Kill Aura — serang semua musuh dalam radius
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local LP = Players.LocalPlayer
local RADIUS = 15
local DAMAGE = 20
RunService.Heartbeat:Connect(function()
    local root = LP.Character and LP.Character:FindFirstChild("HumanoidRootPart")
    if not root then return end
    for _, p in ipairs(Players:GetPlayers()) do
        if p ~= LP and p.Character then
            local pRoot = p.Character:FindFirstChild("HumanoidRootPart")
            local hum = p.Character:FindFirstChildOfClass("Humanoid")
            if pRoot and hum and hum.Health > 0 then
                if (root.Position - pRoot.Position).Magnitude <= RADIUS then
                    hum:TakeDamage(DAMAGE)
                end
            end
        end
    end
end)
]],
    ["ITEM_MAGNET"] = [[
-- Item Magnet — tarik semua item ke arah player
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local LP = Players.LocalPlayer
local MAGNET_RANGE = 30
RunService.Heartbeat:Connect(function()
    local root = LP.Character and LP.Character:FindFirstChild("HumanoidRootPart")
    if not root then return end
    for _, obj in ipairs(workspace:GetDescendants()) do
        if obj:IsA("BasePart") and not obj.Anchored then
            if (obj.Position - root.Position).Magnitude <= MAGNET_RANGE then
                local pull = (root.Position - obj.Position).Unit * 2
                obj.Velocity = pull * 20
            end
        end
    end
end)
]],
    ["GOD_MODE"] = [[
-- God Mode — HP selalu full
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local LP = Players.LocalPlayer
RunService.Heartbeat:Connect(function()
    local char = LP.Character
    if char then
        local hum = char:FindFirstChildOfClass("Humanoid")
        if hum then hum.Health = hum.MaxHealth end
    end
end)
]],
    ["ANTI_RAGDOLL"] = [[
-- Anti Ragdoll — cegah karakter jatuh/ragdoll
local Players = game:GetService("Players")
local LP = Players.LocalPlayer
local function patchChar(char)
    for _, v in ipairs(char:GetDescendants()) do
        if v:IsA("BallSocketConstraint") or v:IsA("HingeConstraint") then
            v.Enabled = false
        end
    end
end
if LP.Character then patchChar(LP.Character) end
LP.CharacterAdded:Connect(patchChar)
]],
    ["AUTO_FARM_GENERIC"] = [[
-- Auto Farm Generic — TP ke mob terdekat + serang
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local LP = Players.LocalPlayer
local MOB_TAG = "Enemy" -- ganti sesuai game
local ATTACK_RANGE = 5
local function getNearestMob()
    local nearest, dist = nil, math.huge
    for _, obj in ipairs(workspace:GetDescendants()) do
        if obj.Name == MOB_TAG or obj:FindFirstChild(MOB_TAG) then
            local root = obj:FindFirstChild("HumanoidRootPart")
            if root then
                local myRoot = LP.Character and LP.Character:FindFirstChild("HumanoidRootPart")
                if myRoot then
                    local d = (myRoot.Position - root.Position).Magnitude
                    if d < dist then nearest, dist = obj, d end
                end
            end
        end
    end
    return nearest
end
RunService.Heartbeat:Connect(function()
    local mob = getNearestMob()
    local myRoot = LP.Character and LP.Character:FindFirstChild("HumanoidRootPart")
    if mob and myRoot then
        local mobRoot = mob:FindFirstChild("HumanoidRootPart")
        if mobRoot then
            myRoot.CFrame = CFrame.new(mobRoot.Position + Vector3.new(0, 3, 0))
        end
    end
end)
]],
    ["DEV_CONSOLE"] = [[
-- Dev Console — print semua info game ke output
print("=== CHEAT DEV CONSOLE ===")
print("PlaceId:", game.PlaceId)
print("JobId:", game.JobId)
print("Players:", #game:GetService("Players"):GetPlayers())
for _, p in ipairs(game:GetService("Players"):GetPlayers()) do
    print(" >", p.Name, "| Team:", tostring(p.Team and p.Team.Name or "none"))
end
print("Workspace children:", #workspace:GetChildren())
print("=========================")
]],
}

function ScriptForge.Craft(name)
    local template = ScriptForge.Templates[string.upper(name)]
    if not template then
        Utils.Log("FORGE", "Template '"..name.."' not found. Available: "..
            table.concat((function()
                local t = {}
                for k in pairs(ScriptForge.Templates) do table.insert(t, k) end
                return t
            end)(), ", "))
        return
    end
    Utils.Log("FORGE", "🔥 Crafting: "..string.upper(name))
    local ok, err = pcall(loadstring(template))
    if ok then
        Utils.Log("FORGE", "✅ Script injected — DAR DER DOR!")
    else
        Utils.Log("FORGE", "❌ Error: "..tostring(err))
    end
end

function ScriptForge.CraftRaw(code)
    Utils.Log("FORGE", "🔥 Raw craft injecting...")
    local ok, err = pcall(loadstring(code))
    if ok then
        Utils.Log("FORGE", "✅ Raw script injected!")
    else
        Utils.Log("FORGE", "❌ Raw error: "..tostring(err))
    end
end

function ScriptForge.List()
    Utils.Log("FORGE", "=== Template Library ===")
    for k in pairs(ScriptForge.Templates) do
        Utils.Log("FORGE", "  /C " .. k)
    end
    Utils.Log("FORGE", "========================")
end

-- ══════════════════════════════════════════════════════════════════
--  MODULE: AUTO CHEST — Collector
-- ══════════════════════════════════════════════════════════════════

local ChestModule = {}
ChestModule.Enabled  = false
ChestModule.Tags     = {"Chest", "Box", "Crate", "Treasure", "Loot"}
ChestModule.AutoHop  = true
ChestModule._found   = 0

local function ChestUpdate()
    if not ChestModule.Enabled then return end
    local root = LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("HumanoidRootPart")
    if not root then return end
    local allChests = {}
    for _, tag in ipairs(ChestModule.Tags) do
        for _, obj in ipairs(workspace:GetDescendants()) do
            if string.lower(obj.Name):find(string.lower(tag)) then
                if obj:IsA("BasePart") or obj:IsA("Model") then
                    table.insert(allChests, obj)
                end
            end
        end
    end
    if #allChests == 0 and ChestModule.AutoHop then
        HopServer()
        return
    end
    for _, chest in ipairs(allChests) do
        local part = chest:IsA("Model") and (chest:FindFirstChild("HumanoidRootPart") or chest.PrimaryPart) or chest
        if part then
            root.CFrame = CFrame.new(part.Position + Vector3.new(0, 2, 0))
            task.wait(0.1)
            -- simulate interact
            local clickDet = chest:FindFirstChildWhichIsA("ClickDetector", true)
            if clickDet then
                pcall(function() fireclickdetector(clickDet) end)
            end
            local proxProm = chest:FindFirstChildWhichIsA("ProximityPrompt", true)
            if proxProm then
                pcall(function() fireproximityprompt(proxProm) end)
            end
            ChestModule._found = ChestModule._found + 1
            task.wait(0.3)
        end
    end
end

-- ══════════════════════════════════════════════════════════════════
--  MODULE: AUTO FRUIT — Blox Fruits Edition
-- ══════════════════════════════════════════════════════════════════

local FruitModule = {}
FruitModule.Enabled = false
FruitModule.Tags    = {"Fruit", "DevilFruit", "Devil_Fruit", "BloxFruit"}

local function FruitUpdate()
    if not FruitModule.Enabled then return end
    local root = LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("HumanoidRootPart")
    if not root then return end
    for _, obj in ipairs(workspace:GetDescendants()) do
        for _, tag in ipairs(FruitModule.Tags) do
            if string.lower(obj.Name):find(string.lower(tag)) then
                local part = obj:IsA("BasePart") and obj or (obj:IsA("Model") and obj.PrimaryPart)
                if part then
                    root.CFrame = CFrame.new(part.Position + Vector3.new(0, 2, 0))
                    task.wait(0.1)
                    local pp = obj:FindFirstChildWhichIsA("ProximityPrompt", true)
                    if pp then pcall(function() fireproximityprompt(pp) end) end
                    local cd = obj:FindFirstChildWhichIsA("ClickDetector", true)
                    if cd then pcall(function() fireclickdetector(cd) end) end
                    task.wait(0.2)
                end
                break
            end
        end
    end
end

-- ══════════════════════════════════════════════════════════════════
--  MODULE: FPS BOOST — Strip & Optimize
-- ══════════════════════════════════════════════════════════════════

local FPSModule = {}
FPSModule.Enabled = false

local function FPSApply()
    if not FPSModule.Enabled then return end
    -- Lighting
    local L = game:GetService("Lighting")
    L.GlobalShadows      = false
    L.FogEnd             = 10000
    L.Ambient            = Color3.new(1,1,1)
    L.OutdoorAmbient     = Color3.new(1,1,1)
    pcall(function() L.DepthOfField.Enabled = false end)
    -- Strip effects
    for _, obj in ipairs(L:GetChildren()) do
        if obj:IsA("BlurEffect") or obj:IsA("SunRaysEffect")
            or obj:IsA("ColorCorrectionEffect") or obj:IsA("BloomEffect") then
            obj.Enabled = false
        end
    end
    -- Strip workspace particles
    for _, obj in ipairs(workspace:GetDescendants()) do
        if obj:IsA("ParticleEmitter") or obj:IsA("Smoke")
            or obj:IsA("Fire") or obj:IsA("Sparkles") then
            obj.Enabled = false
        end
        if obj:IsA("Decal") or obj:IsA("Texture") then
            obj.Transparency = 1
        end
    end
    Utils.Log("FPS", "✅ FPS Boost applied — stripping shadows, particles, effects")
end

-- ══════════════════════════════════════════════════════════════════
--  GUI — Cheat Dev Main Menu
-- ══════════════════════════════════════════════════════════════════

local GUI = {}
GUI._open     = false
GUI._tab      = "MAIN"
GUI._screenGui= nil
GUI._main     = nil

local function GuiTween(inst, props, t)
    TweenService:Create(inst, TweenInfo.new(t or 0.25, Enum.EasingStyle.Quad), props):Play()
end

local function MakeFrame(parent, size, pos, color, alpha)
    local f = Instance.new("Frame")
    f.Size            = size
    f.Position        = pos
    f.BackgroundColor3= color or COLOR.BG
    f.BackgroundTransparency = alpha or 0
    f.BorderSizePixel = 0
    f.Parent          = parent
    return f
end

local function MakeLabel(parent, text, size, color, pos, sz)
    local l = Instance.new("TextLabel")
    l.Text              = text
    l.TextSize          = size or 14
    l.TextColor3        = color or COLOR.TEXT
    l.BackgroundTransparency = 1
    l.Font              = Enum.Font.GothamBold
    l.Position          = pos or UDim2.new(0,0,0,0)
    l.Size              = sz or UDim2.new(1,0,0,20)
    l.TextXAlignment    = Enum.TextXAlignment.Left
    l.Parent            = parent
    return l
end

local function MakeButton(parent, text, color, pos, sz, cb)
    local btn = Instance.new("TextButton")
    btn.Text              = text
    btn.TextSize          = 13
    btn.TextColor3        = COLOR.TEXT
    btn.BackgroundColor3  = color or COLOR.BG2
    btn.AutoButtonColor   = false
    btn.Font              = Enum.Font.GothamBold
    btn.Position          = pos or UDim2.new(0,0,0,0)
    btn.Size              = sz or UDim2.new(1,0,0,28)
    btn.BorderSizePixel   = 0
    btn.Parent            = parent
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 4)
    corner.Parent = btn
    btn.MouseButton1Click:Connect(function()
        GuiTween(btn, {BackgroundColor3 = COLOR.ACCENT}, 0.1)
        task.wait(0.1)
        GuiTween(btn, {BackgroundColor3 = color or COLOR.BG2}, 0.1)
        if cb then cb() end
    end)
    btn.MouseEnter:Connect(function()
        GuiTween(btn, {BackgroundColor3 = COLOR.BG}, 0.15)
    end)
    btn.MouseLeave:Connect(function()
        GuiTween(btn, {BackgroundColor3 = color or COLOR.BG2}, 0.15)
    end)
    return btn
end

local function MakeToggle(parent, text, state, pos, onChange)
    local row = MakeFrame(parent, UDim2.new(1,0,0,30), pos, COLOR.BG2, 0)
    local lbl = MakeLabel(row, text, 13, COLOR.TEXT, UDim2.new(0,8,0,5), UDim2.new(0.7,0,1,0))
    local indicator = Instance.new("Frame")
    indicator.Size     = UDim2.new(0,36,0,20)
    indicator.Position = UDim2.new(1,-44,0.5,-10)
    indicator.BackgroundColor3 = state and COLOR.ACCENT or COLOR.BG
    indicator.BorderSizePixel  = 0
    indicator.Parent   = row
    local c = Instance.new("UICorner")
    c.CornerRadius = UDim.new(1,0)
    c.Parent = indicator
    local knob = Instance.new("Frame")
    knob.Size   = UDim2.new(0,16,0,16)
    knob.Position = state and UDim2.new(1,-18,0.5,-8) or UDim2.new(0,2,0.5,-8)
    knob.BackgroundColor3 = COLOR.WHITE
    knob.BorderSizePixel  = 0
    knob.Parent = indicator
    local kc = Instance.new("UICorner")
    kc.CornerRadius = UDim.new(1,0)
    kc.Parent = knob
    local current = state
    local togBtn = Instance.new("TextButton")
    togBtn.Size = UDim2.new(1,0,1,0)
    togBtn.BackgroundTransparency = 1
    togBtn.Text = ""
    togBtn.Parent = row
    togBtn.MouseButton1Click:Connect(function()
        current = not current
        GuiTween(indicator, {BackgroundColor3 = current and COLOR.ACCENT or COLOR.BG}, 0.15)
        GuiTween(knob, {Position = current and UDim2.new(1,-18,0.5,-8) or UDim2.new(0,2,0.5,-8)}, 0.15)
        if onChange then onChange(current) end
    end)
    return row
end

local function BuildGUI()
    -- Cleanup old
    local old = LocalPlayer.PlayerGui:FindFirstChild("CheatDevUI")
    if old then old:Destroy() end

    GUI._screenGui = Instance.new("ScreenGui")
    GUI._screenGui.Name            = "CheatDevUI"
    GUI._screenGui.ResetOnSpawn    = false
    GUI._screenGui.ZIndexBehavior  = Enum.ZIndexBehavior.Sibling
    GUI._screenGui.Parent          = LocalPlayer.PlayerGui

    -- Main window
    local win = MakeFrame(GUI._screenGui,
        UDim2.new(0, 420, 0, 560),
        UDim2.new(0.5, -210, 0.5, -280),
        COLOR.BG)
    GUI._main = win
    local winCorner = Instance.new("UICorner")
    winCorner.CornerRadius = UDim.new(0, 8)
    winCorner.Parent = win

    -- Title bar
    local titleBar = MakeFrame(win, UDim2.new(1,0,0,46), UDim2.new(0,0,0,0), COLOR.BG2)
    local tbCorner = Instance.new("UICorner")
    tbCorner.CornerRadius = UDim.new(0,8)
    tbCorner.Parent = titleBar
    -- Fix bottom corners of title bar
    local tbFix = MakeFrame(titleBar, UDim2.new(1,0,0.5,0), UDim2.new(0,0,0.5,0), COLOR.BG2)

    -- Accent line
    local accentLine = MakeFrame(win, UDim2.new(1,0,0,2), UDim2.new(0,0,0,46), COLOR.ACCENT)

    -- Title text
    local titleLbl = Instance.new("TextLabel")
    titleLbl.Text              = "⚡ CHEAT DEV"
    titleLbl.TextSize          = 18
    titleLbl.TextColor3        = COLOR.ACCENT
    titleLbl.BackgroundTransparency = 1
    titleLbl.Font              = Enum.Font.GothamBold
    titleLbl.Size              = UDim2.new(0.7, 0, 1, 0)
    titleLbl.Position          = UDim2.new(0, 12, 0, 0)
    titleLbl.TextXAlignment    = Enum.TextXAlignment.Left
    titleLbl.Parent            = titleBar

    local subLbl = Instance.new("TextLabel")
    subLbl.Text              = "v1.0 · pointrungkat-art · DAR DER DOR"
    subLbl.TextSize          = 10
    subLbl.TextColor3        = COLOR.TEXTDIM
    subLbl.BackgroundTransparency = 1
    subLbl.Font              = Enum.Font.Gotham
    subLbl.Size              = UDim2.new(0.9, 0, 0, 14)
    subLbl.Position          = UDim2.new(0, 13, 0, 28)
    subLbl.TextXAlignment    = Enum.TextXAlignment.Left
    subLbl.Parent            = titleBar

    -- Close button
    local closeBtn = Instance.new("TextButton")
    closeBtn.Text              = "✕"
    closeBtn.TextSize          = 16
    closeBtn.TextColor3        = COLOR.TEXTDIM
    closeBtn.BackgroundTransparency = 1
    closeBtn.Font              = Enum.Font.GothamBold
    closeBtn.Size              = UDim2.new(0,36,0,36)
    closeBtn.Position          = UDim2.new(1,-40,0,5)
    closeBtn.Parent            = titleBar
    closeBtn.MouseButton1Click:Connect(function()
        GuiTween(win, {Position = UDim2.new(0.5,-210,1.5,-280)}, 0.3)
        task.wait(0.35)
        GUI._screenGui:Destroy()
    end)

    -- Drag
    local dragging, dragStart, startPos = false, nil, nil
    titleBar.InputBegan:Connect(function(inp)
        if inp.UserInputType == Enum.UserInputType.MouseButton1 then
            dragging  = true
            dragStart = inp.Position
            startPos  = win.Position
        end
    end)
    UserInputService.InputChanged:Connect(function(inp)
        if dragging and inp.UserInputType == Enum.UserInputType.MouseMovement then
            local delta = inp.Position - dragStart
            win.Position = UDim2.new(
                startPos.X.Scale, startPos.X.Offset + delta.X,
                startPos.Y.Scale, startPos.Y.Offset + delta.Y)
        end
    end)
    UserInputService.InputEnded:Connect(function(inp)
        if inp.UserInputType == Enum.UserInputType.MouseButton1 then
            dragging = false
        end
    end)

    -- Tab bar
    local tabBar = MakeFrame(win, UDim2.new(1,0,0,32), UDim2.new(0,0,0,48), COLOR.BG2)
    local tabFix  = MakeFrame(tabBar, UDim2.new(1,0,0.5,0), UDim2.new(0,0,0,0), COLOR.BG2)
    local tabs = {"MAIN", "ESP", "AIM", "FORGE", "UTILS"}
    local tabBtns = {}
    for i, tab in ipairs(tabs) do
        local tb = Instance.new("TextButton")
        tb.Text              = tab
        tb.TextSize          = 12
        tb.TextColor3        = GUI._tab == tab and COLOR.ACCENT or COLOR.TEXTDIM
        tb.BackgroundTransparency = 1
        tb.Font              = Enum.Font.GothamBold
        tb.Size              = UDim2.new(1/#tabs, 0, 1, 0)
        tb.Position          = UDim2.new((i-1)/#tabs, 0, 0, 0)
        tb.Parent            = tabBar
        tabBtns[tab] = tb
        tb.MouseButton1Click:Connect(function()
            GUI._tab = tab
            for t, b in pairs(tabBtns) do
                b.TextColor3 = t == tab and COLOR.ACCENT or COLOR.TEXTDIM
            end
            -- TODO: swap content panel
        end)
    end

    -- Content area
    local content = MakeFrame(win, UDim2.new(1,-16,1,-100), UDim2.new(0,8,0,88), COLOR.BG, 0)
    local scroll = Instance.new("ScrollingFrame")
    scroll.Size                    = UDim2.new(1,0,1,0)
    scroll.Position                = UDim2.new(0,0,0,0)
    scroll.BackgroundTransparency  = 1
    scroll.ScrollBarThickness      = 3
    scroll.ScrollBarImageColor3    = COLOR.ACCENT
    scroll.BorderSizePixel         = 0
    scroll.CanvasSize              = UDim2.new(0,0,0,0)
    scroll.AutomaticCanvasSize     = Enum.AutomaticSize.Y
    scroll.Parent                  = content
    local listLayout = Instance.new("UIListLayout")
    listLayout.Padding     = UDim.new(0, 4)
    listLayout.SortOrder   = Enum.SortOrder.LayoutOrder
    listLayout.Parent      = scroll

    -- ── TOGGLES
    local section1 = MakeLabel(scroll, "— COMBAT & VISUAL", 12, COLOR.ACCENT,
        UDim2.new(0,0,0,0), UDim2.new(1,0,0,18))
    section1.LayoutOrder = 0

    MakeToggle(scroll, "🟣 ESP", ESPModule.Enabled, UDim2.new(0,0,0,0), function(v)
        ESPModule.Enabled = v
    end).LayoutOrder = 1

    MakeToggle(scroll, "🔴 Aim Assist", AimModule.Enabled, UDim2.new(0,0,0,0), function(v)
        AimModule.Enabled = v
    end).LayoutOrder = 2

    MakeToggle(scroll, "⚡ Silent Aim", SilentAimModule.Enabled, UDim2.new(0,0,0,0), function(v)
        SilentAimModule.Enabled = v
    end).LayoutOrder = 3

    MakeToggle(scroll, "👁️ Show FOV Ring", AimModule.ShowFOVRing, UDim2.new(0,0,0,0), function(v)
        AimModule.ShowFOVRing = v
    end).LayoutOrder = 4

    MakeToggle(scroll, "🏃 Tracer Lines", ESPModule.ShowTracer, UDim2.new(0,0,0,0), function(v)
        ESPModule.ShowTracer = v
    end).LayoutOrder = 5

    local section2 = MakeLabel(scroll, "— MOVEMENT & UTILITY", 12, COLOR.ACCENT2,
        UDim2.new(0,0,0,0), UDim2.new(1,0,0,18))
    section2.LayoutOrder = 6

    MakeToggle(scroll, "🌊 Auto Hop", HopModule.Enabled, UDim2.new(0,0,0,0), function(v)
        HopModule.Enabled = v
        HopModule._timer  = 0
    end).LayoutOrder = 7

    MakeToggle(scroll, "📦 Auto Chest", ChestModule.Enabled, UDim2.new(0,0,0,0), function(v)
        ChestModule.Enabled = v
    end).LayoutOrder = 8

    MakeToggle(scroll, "🍎 Auto Fruit", FruitModule.Enabled, UDim2.new(0,0,0,0), function(v)
        FruitModule.Enabled = v
    end).LayoutOrder = 9

    MakeToggle(scroll, "⚡ FPS Boost", FPSModule.Enabled, UDim2.new(0,0,0,0), function(v)
        FPSModule.Enabled = v
        if v then FPSApply() end
    end).LayoutOrder = 10

    local section3 = MakeLabel(scroll, "— SCRIPT FORGE 🔥", 12, COLOR.FIRE,
        UDim2.new(0,0,0,0), UDim2.new(1,0,0,18))
    section3.LayoutOrder = 11

    local forgeList = {
        {"ESP_QUICK",        "Quick ESP Inject"},
        {"SPEED_HACK",       "Speed Hack ×6"},
        {"NOCLIP",           "No Clip"},
        {"INF_JUMP",         "Infinite Jump"},
        {"KILL_AURA",        "Kill Aura"},
        {"ITEM_MAGNET",      "Item Magnet"},
        {"GOD_MODE",         "God Mode"},
        {"ANTI_RAGDOLL",     "Anti Ragdoll"},
        {"TELEPORT_ME",      "Teleport Tool"},
        {"AUTO_FARM_GENERIC","Auto Farm Generic"},
        {"DEV_CONSOLE",      "Dev Console Log"},
    }
    for i, v in ipairs(forgeList) do
        local key, label = v[1], v[2]
        MakeButton(scroll, "🔥 /C " .. key .. "  ·  " .. label,
            COLOR.BG2, UDim2.new(0,0,0,0), UDim2.new(1,0,0,28),
            function() ScriptForge.Craft(key) end
        ).LayoutOrder = 11 + i
    end

    -- Bottom bar
    local botBar = MakeFrame(win, UDim2.new(1,0,0,42), UDim2.new(0,0,1,-42), COLOR.BG2)
    local botFix  = MakeFrame(botBar, UDim2.new(1,0,0.5,0), UDim2.new(0,0,0,0), COLOR.BG2)
    local botCorner = Instance.new("UICorner")
    botCorner.CornerRadius = UDim.new(0,8)
    botCorner.Parent = botBar
    local statusLbl = MakeLabel(botBar, "🔥 CheatDev ready — DAR DER DOR", 11, COLOR.SUCCESS,
        UDim2.new(0,8,0,0), UDim2.new(0.8,0,1,0))

    -- Open animation
    win.Position = UDim2.new(0.5,-210,1.5,-280)
    GuiTween(win, {Position = UDim2.new(0.5,-210,0.5,-280)}, 0.4)

    GUI._open = true
end

-- Toggle GUI with RightShift
UserInputService.InputBegan:Connect(function(inp, gpe)
    if gpe then return end
    if inp.KeyCode == Enum.KeyCode.RightShift then
        if GUI._open and GUI._screenGui then
            GUI._screenGui:Destroy()
            GUI._open = false
        else
            BuildGUI()
        end
    end
end)

-- ══════════════════════════════════════════════════════════════════
--  MAIN LOOP
-- ══════════════════════════════════════════════════════════════════

local lastChest = 0
local lastFruit = 0

RunService.RenderStepped:Connect(function(dt)
    pcall(ESPUpdate)
    pcall(AimUpdate)
end)

RunService.Heartbeat:Connect(function(dt)
    pcall(HopUpdate, dt)
    local now = tick()
    if now - lastChest > 0.5 then
        lastChest = now
        pcall(ChestUpdate)
    end
    if now - lastFruit > 0.7 then
        lastFruit = now
        pcall(FruitUpdate)
    end
end)

-- ══════════════════════════════════════════════════════════════════
--  EXPOSE PUBLIC API  (/C command shorthand)
-- ══════════════════════════════════════════════════════════════════

-- Global shorthand — di executor console ketik: C("SPEED_HACK")
getgenv().C = function(name) ScriptForge.Craft(name) end
getgenv().CList = function() ScriptForge.List() end
getgenv().CDRaw = function(code) ScriptForge.CraftRaw(code) end
getgenv().CD = CD

-- ══════════════════════════════════════════════════════════════════
--  LAUNCH
-- ══════════════════════════════════════════════════════════════════

Utils.Log("BOOT", "══════════════════════════════════════")
Utils.Log("BOOT", "⚡ CHEAT DEV v1.0 | pointrungkat-art")
Utils.Log("BOOT", "🔥 " .. CD._MOTTO)
Utils.Log("BOOT", "📌 RightShift → Toggle GUI")
Utils.Log("BOOT", "📌 C('TEMPLATE') → Script Forge inject")
Utils.Log("BOOT", "📌 CList() → List all templates")
Utils.Log("BOOT", "══════════════════════════════════════")

task.wait(0.5)
BuildGUI()

return CD
