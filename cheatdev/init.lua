--[[
 ██████╗██╗  ██╗███████╗ █████╗ ████████╗    ██████╗ ███████╗██╗   ██╗
██╔════╝██║  ██║██╔════╝██╔══██╗╚══██╔══╝    ██╔══██╗██╔════╝██║   ██║
██║     ███████║█████╗  ███████║   ██║       ██║  ██║█████╗  ██║   ██║
██║     ██╔══██║██╔══╝  ██╔══██║   ██║       ██║  ██║██╔══╝  ╚██╗ ██╔╝
╚██████╗██║  ██║███████╗██║  ██║   ██║       ██████╔╝███████╗ ╚████╔╝
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ╚═╝       ╚═════╝ ╚══════╝  ╚═══╝

  ██╗  ██╗ █████╗ ██████╗ ██╗████████╗ █████╗ ████████╗
  ██║  ██║██╔══██╗██╔══██╗██║╚══██╔══╝██╔══██╗╚══██╔══╝
  ███████║███████║██████╔╝██║   ██║   ███████║   ██║
  ██╔══██║██╔══██║██╔══██╗██║   ██║   ██╔══██║   ██║
  ██║  ██║██║  ██║██████╔╝██║   ██║   ██║  ██║   ██║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝

  🔥 CHEAT DEVELOPER v2.0 — HABITAT / DEV MODE WORKSPACE
  🔥 pointrungkat-art · Delta Android · DAR DER DOR
  🔥 "Masuk sini = Dev Mode ON. Semua kode libas. Gada yang gabisa."

  LOAD:
  loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/cheatdev/init.lua"))()

  HOTKEYS:
    RightShift → Main GUI
    F2         → Dev Console (command input + live log)
    F5         → Reload semua module
    F9         → PANIC — matiin semua sekaligus

  DEV CONSOLE COMMANDS:
    /c <template>        → inject script forge
    /clist               → list semua template
    /module <name> on    → aktifin module
    /module <name> off   → matiin module
    /panic               → emergency stop semua
    /lua <code>          → run raw lua
    /help                → tampilkan semua command
--]]

-- ══════════════════════════════════════════════════════════════════
--  BOOTSTRAP — Load semua dari GitHub raw
-- ══════════════════════════════════════════════════════════════════

local BASE = "https://raw.githubusercontent.com/pointrungkat-art/u/main/cheatdev/"

local function load(path)
    local ok, result = pcall(function()
        return loadstring(game:HttpGet(BASE..path))()
    end)
    if not ok then
        warn("[CheatDev] Failed to load "..path..": "..tostring(result))
        return nil
    end
    return result
end

-- ── 1. Core engine ──────────────────────────────────────────────
local Core = load("core.lua")
if not Core then error("[CheatDev] Core failed to load. Check internet.") end

-- ── 2. Config (already loaded inside core, but expose here) ─────
local Config = Core.Config

-- ── 3. Modules ──────────────────────────────────────────────────
local ESPMod   = load("modules/esp.lua")
local MoveMod  = load("modules/movement.lua")
local CombMod  = load("modules/combat.lua")
local VisMod   = load("modules/visual.lua")
local HabitMod = load("modules/habit.lua")

local ESP    = ESPMod   and ESPMod(Core)
local Move   = MoveMod  and MoveMod(Core)
local Combat = CombMod  and CombMod(Core)
local Visual = VisMod   and VisMod(Core)
local Habit  = HabitMod and HabitMod(Core)

-- ── 4. Script Forge ─────────────────────────────────────────────
local rawTemplates = load("forge/templates.lua")
local ForgeBuilder = load("forge/builder.lua")
local Forge = ForgeBuilder and ForgeBuilder(Core, rawTemplates)

-- ── 5. Dev Console ──────────────────────────────────────────────
local DevConLoader = load("ui/devConsole.lua")
local DevCon = DevConLoader and DevConLoader(Core, Forge)

-- ── 6. Main GUI ─────────────────────────────────────────────────
local S   = Core.Services
local U   = Core.Utils
local TW  = S.TweenService
local LP  = Core.LP

local COL = {
    BG     = Color3.fromRGB(10, 8, 20),
    BG2    = Color3.fromRGB(18, 14, 35),
    ACCENT = Color3.fromRGB(180, 80, 255),
    ACC2   = Color3.fromRGB(80,  200, 255),
    FIRE   = Color3.fromRGB(255, 140, 30),
    TEXT   = Color3.fromRGB(230, 225, 255),
    DIM    = Color3.fromRGB(120, 110, 150),
    OK     = Color3.fromRGB(80,  255, 130),
    ERR    = Color3.fromRGB(255, 70,  70),
}

local GUI = {}
GUI._open = false
GUI._sg   = nil

local function tw(inst, props, t)
    TW:Create(inst, TweenInfo.new(t or 0.25, Enum.EasingStyle.Quad), props):Play()
end

local function frame(p, sz, pos, col, alpha)
    local f = Instance.new("Frame")
    f.Size = sz; f.Position = pos
    f.BackgroundColor3 = col or COL.BG
    f.BackgroundTransparency = alpha or 0
    f.BorderSizePixel = 0; f.Parent = p
    return f
end
local function label(p, txt, sz, col, pos, fsz, xa)
    local l = Instance.new("TextLabel")
    l.Text = txt; l.TextSize = sz or 13; l.TextColor3 = col or COL.TEXT
    l.BackgroundTransparency = 1; l.Font = Enum.Font.GothamBold
    l.Position = pos or UDim2.new(0,0,0,0)
    l.Size = fsz or UDim2.new(1,0,0,20)
    l.TextXAlignment = xa or Enum.TextXAlignment.Left
    l.Parent = p; return l
end
local function toggle(parent, txt, initState, layoutOrder, onChange)
    local row = frame(parent, UDim2.new(1,0,0,30), UDim2.new(0,0,0,0), Color3.new(0,0,0), 1)
    row.LayoutOrder = layoutOrder
    local bg = frame(row, UDim2.new(1,0,1,0), UDim2.new(0,0,0,0), COL.BG2, 0.3)
    local bc = Instance.new("UICorner"); bc.CornerRadius = UDim.new(0,4); bc.Parent = bg
    label(bg, txt, 13, COL.TEXT, UDim2.new(0,8,0,5), UDim2.new(0.75,0,1,0))
    local pill = frame(bg, UDim2.new(0,36,0,20), UDim2.new(1,-44,0.5,-10), initState and COL.ACCENT or COL.BG)
    local pc = Instance.new("UICorner"); pc.CornerRadius = UDim.new(1,0); pc.Parent = pill
    local knob = frame(pill, UDim2.new(0,16,0,16), initState and UDim2.new(1,-18,0.5,-8) or UDim2.new(0,2,0.5,-8), Color3.new(1,1,1))
    local kc = Instance.new("UICorner"); kc.CornerRadius = UDim.new(1,0); kc.Parent = knob
    local cur = initState
    local tb = Instance.new("TextButton"); tb.Size=UDim2.new(1,0,1,0); tb.BackgroundTransparency=1; tb.Text=""; tb.Parent=bg
    tb.MouseButton1Click:Connect(function()
        cur = not cur
        tw(pill, {BackgroundColor3 = cur and COL.ACCENT or COL.BG}, 0.15)
        tw(knob, {Position = cur and UDim2.new(1,-18,0.5,-8) or UDim2.new(0,2,0.5,-8)}, 0.15)
        if onChange then onChange(cur) end
    end)
    return row
end
local function button(parent, txt, layoutOrder, cb, col)
    local btn = Instance.new("TextButton")
    btn.Text = txt; btn.TextSize = 12; btn.TextColor3 = COL.TEXT
    btn.BackgroundColor3 = col or COL.BG2; btn.AutoButtonColor = false
    btn.Font = Enum.Font.GothamBold; btn.BorderSizePixel = 0
    btn.Size = UDim2.new(1,0,0,28); btn.LayoutOrder = layoutOrder
    btn.Parent = parent
    local c = Instance.new("UICorner"); c.CornerRadius = UDim.new(0,4); c.Parent = btn
    btn.MouseButton1Click:Connect(function()
        tw(btn, {BackgroundColor3 = COL.ACCENT}, 0.08)
        task.wait(0.1)
        tw(btn, {BackgroundColor3 = col or COL.BG2}, 0.1)
        if cb then cb() end
    end)
    return btn
end

local function section(parent, txt, col, order)
    local l = label(parent, "— "..txt, 11, col or COL.ACCENT,
        UDim2.new(0,0,0,0), UDim2.new(1,0,0,18))
    l.LayoutOrder = order or 0
    return l
end

local function buildGUI()
    local old = LP.PlayerGui:FindFirstChild("CheatDevUI2")
    if old then old:Destroy() end
    GUI._sg = Instance.new("ScreenGui")
    GUI._sg.Name = "CheatDevUI2"; GUI._sg.ResetOnSpawn = false
    GUI._sg.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    GUI._sg.Parent = LP.PlayerGui

    -- Window
    local win = frame(GUI._sg, UDim2.new(0,400,0,580), UDim2.new(0.5,-200,0.5,-290), COL.BG)
    local wc = Instance.new("UICorner"); wc.CornerRadius = UDim.new(0,8); wc.Parent = win

    -- Glow border
    local border = frame(win, UDim2.new(1,4,1,4), UDim2.new(0,-2,0,-2), COL.ACCENT, 0.7)
    border.ZIndex = 0
    local bc2 = Instance.new("UICorner"); bc2.CornerRadius = UDim.new(0,9); bc2.Parent = border

    -- Title
    local tbar = frame(win, UDim2.new(1,0,0,44), UDim2.new(0,0,0,0), COL.BG2)
    local tbc = Instance.new("UICorner"); tbc.CornerRadius = UDim.new(0,8); tbc.Parent = tbar
    local tbfix = frame(tbar, UDim2.new(1,0,0.5,0), UDim2.new(0,0,0.5,0), COL.BG2)
    label(tbar, "⚡ CHEAT DEVELOPER", 17, COL.ACCENT, UDim2.new(0,12,0,4), UDim2.new(0.7,0,0,22))
    label(tbar, "v2.0 · DEV MODE ON · DAR DER DOR", 10, COL.DIM, UDim2.new(0,13,0,26), UDim2.new(0.9,0,0,14))
    local xbtn = Instance.new("TextButton"); xbtn.Text="✕"; xbtn.TextSize=15; xbtn.TextColor3=COL.DIM
    xbtn.BackgroundTransparency=1; xbtn.Font=Enum.Font.GothamBold
    xbtn.Size=UDim2.new(0,36,0,36); xbtn.Position=UDim2.new(1,-40,0,4); xbtn.Parent=tbar
    xbtn.MouseButton1Click:Connect(function()
        tw(win, {Position=UDim2.new(0.5,-200,1.5,0)}, 0.3)
        task.wait(0.35); GUI._sg:Destroy(); GUI._open=false
    end)

    -- Accent line
    local aline = frame(win, UDim2.new(1,0,0,2), UDim2.new(0,0,0,44), COL.ACCENT)

    -- Drag
    local drag, ds, sp = false, nil, nil
    tbar.InputBegan:Connect(function(i)
        if i.UserInputType==Enum.UserInputType.MouseButton1 then drag=true; ds=i.Position; sp=win.Position end
    end)
    S.UserInputService.InputChanged:Connect(function(i)
        if drag and i.UserInputType==Enum.UserInputType.MouseMovement then
            local d=i.Position-ds; win.Position=UDim2.new(sp.X.Scale,sp.X.Offset+d.X,sp.Y.Scale,sp.Y.Offset+d.Y)
        end
    end)
    S.UserInputService.InputEnded:Connect(function(i)
        if i.UserInputType==Enum.UserInputType.MouseButton1 then drag=false end
    end)

    -- Scroll content
    local content = frame(win, UDim2.new(1,-16,1,-100), UDim2.new(0,8,0,54))
    local scroll = Instance.new("ScrollingFrame")
    scroll.Size=UDim2.new(1,0,1,0); scroll.BackgroundTransparency=1
    scroll.ScrollBarThickness=3; scroll.ScrollBarImageColor3=COL.ACCENT
    scroll.BorderSizePixel=0; scroll.AutomaticCanvasSize=Enum.AutomaticSize.Y
    scroll.CanvasSize=UDim2.new(0,0,0,0); scroll.Parent=content
    local ll = Instance.new("UIListLayout"); ll.Padding=UDim.new(0,3); ll.SortOrder=Enum.SortOrder.LayoutOrder; ll.Parent=scroll
    local pad = Instance.new("UIPadding"); pad.PaddingTop=UDim.new(0,4); pad.Parent=scroll

    local lo = 0
    local function lo_()  lo=lo+1; return lo end

    section(scroll,"VISUAL",           COL.ACCENT,   lo_())
    toggle(scroll, "🟣 ESP",           Config.ESP.enabled,       lo_(), function(v) Config.ESP.enabled=v end)
    toggle(scroll, "👁️ Tracer Lines",  Config.ESP.showTracer,    lo_(), function(v) Config.ESP.showTracer=v end)
    toggle(scroll, "🎯 Crosshair Dev", Config.CROSSHAIR.enabled, lo_(), function(v) Config.CROSSHAIR.enabled=v; if v then Visual.Cross.Enable() else Visual.Cross.Disable() end end)
    toggle(scroll, "🗺️ Radar",         Config.RADAR.enabled,     lo_(), function(v) Config.RADAR.enabled=v end)
    toggle(scroll, "👻 Wallhack / X-Ray",false,                  lo_(), function(v) if v then Visual.Wallhack.Enable() else Visual.Wallhack.Disable() end end)
    toggle(scroll, "⚡ FPS Boost",     Config.FPS.enabled,       lo_(), function(v) if v then Visual.FPS.Apply() else Visual.FPS.Disable() end end)

    section(scroll,"COMBAT",           COL.ACCENT2,  lo_())
    toggle(scroll, "🔴 Aim Assist",    Config.AIM.enabled,        lo_(), function(v) Config.AIM.enabled=v end)
    toggle(scroll, "⚡ Silent Aim",    Config.SILENT_AIM.enabled, lo_(), function(v) if v then Combat.Silent.Enable() else Combat.Silent.Disable() end end)
    toggle(scroll, "💀 Kill Aura",     Config.KILL_AURA.enabled,  lo_(), function(v) if v then Combat.KillAura.Enable() else Combat.KillAura.Disable() end end)
    toggle(scroll, "🎯 Hitbox Expand", Config.HITBOX.enabled,     lo_(), function(v) if v then Combat.Hitbox.Enable() else Combat.Hitbox.Disable() end end)
    toggle(scroll, "🛡️ God Mode",      Config.GOD_MODE.enabled,   lo_(), function(v) if v then Combat.God.Enable() else Combat.God.Disable() end end)
    toggle(scroll, "🦴 Anti Ragdoll",  Config.ANTI_RAGDOLL.enabled,lo_(),function(v) if v then Combat.AntiRagdoll.Enable() end end)
    toggle(scroll, "🔒 Anti Kick",     Config.ANTI_KICK.enabled,  lo_(), function(v) if v then Combat.AntiKick.Enable() else Combat.AntiKick.Disable() end end)

    section(scroll,"MOVEMENT",         COL.FIRE,     lo_())
    toggle(scroll, "🛸 Fly Hack",      Config.FLY.enabled,    lo_(), function(v) Move.Fly.Toggle() end)
    toggle(scroll, "⚡ Speed Hack",    Config.SPEED.enabled,  lo_(), function(v) if v then Move.Speed.Enable() else Move.Speed.Disable() end end)
    toggle(scroll, "👻 No Clip",       Config.NOCLIP.enabled, lo_(), function(v) if v then Move.Noclip.Enable() else Move.Noclip.Disable() end end)
    toggle(scroll, "🦅 Infinite Jump", false,                 lo_(), function(v) if v then Move.InfJump.Enable() else Move.InfJump.Disable() end end)
    toggle(scroll, "🌀 Spin Bot",      Config.SPIN_BOT.enabled,lo_(),function(v) Move.Spin.Toggle() end)

    section(scroll,"FARMING",          Color3.fromRGB(80,255,160), lo_())
    toggle(scroll, "🌊 Auto Hop",      Config.HOP.enabled,   lo_(), function(v) Config.HOP.enabled=v end)
    toggle(scroll, "📦 Auto Chest",    Config.CHEST.enabled, lo_(), function(v) Config.CHEST.enabled=v end)
    toggle(scroll, "🍎 Auto Fruit",    Config.FRUIT.enabled, lo_(), function(v) Config.FRUIT.enabled=v end)
    button(scroll, "💀 TP Kill All",   lo_(), function() Move.TPKill.Run() end, Color3.fromRGB(80,20,20))

    section(scroll,"HABIT SYSTEM 🔁",  Color3.fromRGB(80,255,200), lo_())
    local habStatus = Instance.new("TextLabel")
    habStatus.Text = "⚫ Idle"; habStatus.TextSize = 11
    habStatus.TextColor3 = COL.DIM; habStatus.BackgroundTransparency = 1
    habStatus.Font = Enum.Font.GothamBold; habStatus.TextXAlignment = Enum.TextXAlignment.Left
    habStatus.Position = UDim2.new(0,8,0,0); habStatus.Size = UDim2.new(1,-16,0,18)
    habStatus.LayoutOrder = lo_(); habStatus.Parent = scroll
    task.spawn(function()
        while GUI._open do
            if Habit then
                if Habit.IsRec() then
                    habStatus.Text = "🔴 REC — " .. Habit.RecCount() .. " pts"
                    habStatus.TextColor3 = COL.ERR
                elseif Habit.IsPlaying() then
                    habStatus.Text = "▶ " .. (Habit.CurHabit() or "playing")
                    habStatus.TextColor3 = COL.OK
                else
                    habStatus.Text = "⚫ Idle"; habStatus.TextColor3 = COL.DIM
                end
            end
            task.wait(0.5)
        end
    end)
    toggle(scroll, "🔁 Enable Habit",    Config.HABIT.enabled, lo_(), function(v) Config.HABIT.enabled=v end)
    button(scroll, "⏺ Start Record",     lo_(), function() if Habit then Habit.Record("my_habit") end end)
    button(scroll, "⏹ Stop Record",      lo_(), function() if Habit then Habit.StopRec() end end)
    button(scroll, "▶ Play ∞ Loop",      lo_(), function() if Habit then Habit.PlayLast(0) end end)
    button(scroll, "▶ Play 1×",          lo_(), function() if Habit then Habit.PlayLast(1) end end)
    button(scroll, "⏹ Stop Habit",       lo_(), function() if Habit then Habit.Stop() end end)
    button(scroll, "🍎 Patrol Fruits",   lo_(), function() if Habit then Habit.Patrol.Fruit() end end, Color3.fromRGB(20,60,20))
    button(scroll, "📦 Patrol Chests",   lo_(), function() if Habit then Habit.Patrol.Chest() end end, Color3.fromRGB(30,20,60))

    section(scroll,"SCRIPT FORGE 🔥",  COL.FIRE,     lo_())
    local forgeTemplates = {
        "ESP_QUICK","CHAMS","SPEED_HACK","NOCLIP","FLY_HACK","INF_JUMP",
        "GRAVITY_MOD","LOW_GRAVITY","ZERO_GRAVITY","KILL_AURA","HITBOX_EXPAND",
        "TP_KILL","FLING","GOD_MODE","INF_STAMINA","ANTI_RAGDOLL","SPIN_BOT",
        "TELEPORT_ME","ITEM_MAGNET","AUTO_FARM_GENERIC","AUTO_QUEST",
        "HABIT_RECORDER","AUTO_PATROL",
        "DEV_CONSOLE","REMOTE_SPY_LITE","EXECUTOR_INFO","INFINITE_YIELD","DEX_EXPLORER",
    }
    for _, k in ipairs(forgeTemplates) do
        button(scroll, "🔥 /C "..k, lo_(), function() Forge.Craft(k) end)
    end

    section(scroll,"DEV TOOLS",        COL.ACCENT,   lo_())
    button(scroll, "🖥️ Open Dev Console (F2)", lo_(), function() DevCon.Toggle() end, COL.BG2)
    button(scroll, "🚨 PANIC — Disable All",   lo_(), function() Core.Panic() end, Color3.fromRGB(60,10,10))

    -- Bottom bar
    local bot = frame(win, UDim2.new(1,0,0,44), UDim2.new(0,0,1,-44), COL.BG2)
    local botfix = frame(bot, UDim2.new(1,0,0.5,0), UDim2.new(0,0,0,0), COL.BG2)
    local bc3 = Instance.new("UICorner"); bc3.CornerRadius = UDim.new(0,8); bc3.Parent = bot
    label(bot, "🔥 Dev Mode ON · RightShift=GUI · F2=Console · F9=Panic", 10, COL.DIM,
        UDim2.new(0,8,0,0), UDim2.new(1,0,1,0))

    -- Open anim
    win.Position = UDim2.new(0.5,-200,1.5,0)
    tw(win, {Position=UDim2.new(0.5,-200,0.5,-290)}, 0.45)
    GUI._open = true
end

-- ── Hotkeys ──────────────────────────────────────────────────────
Core.Hotkey("RightShift", function()
    if GUI._open and GUI._sg then
        GUI._sg:Destroy(); GUI._open=false
    else
        buildGUI()
    end
end)
Core.Hotkey("F9", function() Core.Panic() end)
Core.Hotkey("F5", function()
    Core.Log("RELOAD", "🔄 Reloading CheatDev...", "WARN")
    if GUI._sg then GUI._sg:Destroy() end
    if DevCon._gui then DevCon.Close() end
    task.wait(0.5)
    loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/cheatdev/init.lua"))()
end)

-- ── Main Loop ────────────────────────────────────────────────────
S.RunService.RenderStepped:Connect(function(dt)
    if ESP  then Core.Utils.SafeCall(ESP.Update) end
    if Combat and Combat.Aim then Core.Utils.SafeCall(Combat.Aim.Update) end
    if Visual and Visual.Radar then Core.Utils.SafeCall(Visual.Radar.Update) end
end)

-- ── Boot ─────────────────────────────────────────────────────────
Core.Log("BOOT","══════════════════════════════════════════", "OK")
Core.Log("BOOT","⚡ CHEAT DEVELOPER v2.0 — DEV HABITAT LOADED", "OK")
Core.Log("BOOT","🔥 "..Config.META.motto, "WARN")
Core.Log("BOOT","📌 RightShift → Main GUI", "INFO")
Core.Log("BOOT","📌 F2 → Dev Console", "INFO")
Core.Log("BOOT","📌 F9 → Panic Stop All", "INFO")
Core.Log("BOOT","📌 F5 → Hot Reload", "INFO")
Core.Log("BOOT","📌 C('template') → Script Forge", "INFO")
Core.Log("BOOT","📌 CList() → All templates", "INFO")
Core.Log("BOOT","══════════════════════════════════════════", "OK")

task.wait(0.8)
buildGUI()
DevCon.Open()

return { Core=Core, Forge=Forge, GUI=GUI, DevCon=DevCon, Habit=Habit }
