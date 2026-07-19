--[[
  CHEAT DEV — core.lua
  Engine utama: services, utils, event bus, logger, module registry.
  Semua module load dari sini.
--]]

local Core = {}

-- ── Services ──────────────────────────────────────────────────────
Core.Services = {
    Players          = game:GetService("Players"),
    RunService       = game:GetService("RunService"),
    UserInputService = game:GetService("UserInputService"),
    TweenService     = game:GetService("TweenService"),
    HttpService      = game:GetService("HttpService"),
    TeleportService  = game:GetService("TeleportService"),
    Lighting         = game:GetService("Lighting"),
}

local S  = Core.Services
Core.LP  = S.Players.LocalPlayer
Core.Cam = workspace.CurrentCamera

-- ── Config (live, mutable) ────────────────────────────────────────
Core.Config = loadstring(game:HttpGet(
    "https://raw.githubusercontent.com/pointrungkat-art/u/main/cheatdev/config.lua"
))() or {}

-- ── Event Bus ────────────────────────────────────────────────────
local _listeners = {}
function Core.On(event, fn)
    _listeners[event] = _listeners[event] or {}
    table.insert(_listeners[event], fn)
end
function Core.Emit(event, ...)
    for _, fn in ipairs(_listeners[event] or {}) do
        pcall(fn, ...)
    end
end

-- ── Logger ────────────────────────────────────────────────────────
local LOG_COLOR = {
    INFO = "\27[36m", WARN = "\27[33m", ERR = "\27[31m",
    DEV  = "\27[35m", OK   = "\27[32m", RESET = "\27[0m",
}
function Core.Log(tag, msg, level)
    level = level or "INFO"
    local prefix = string.format("[CD:%s] ", tag)
    print(LOG_COLOR[level] or "", prefix, msg, LOG_COLOR.RESET or "")
    Core.Emit("log", {tag=tag, msg=msg, level=level, time=os.clock()})
end

-- ── Module Registry ───────────────────────────────────────────────
local _modules = {}
function Core.Register(name, mod)
    _modules[name] = mod
    Core.Log("CORE", "Module registered: "..name, "DEV")
end
function Core.GetModule(name) return _modules[name] end
function Core.AllModules()    return _modules end

-- ── Utils ─────────────────────────────────────────────────────────
local Utils = {}
Core.Utils = Utils

function Utils.GetChar(player)
    player = player or Core.LP
    return player.Character
end
function Utils.GetRoot(player)
    local c = Utils.GetChar(player)
    return c and c:FindFirstChild("HumanoidRootPart")
end
function Utils.GetHead(player)
    local c = Utils.GetChar(player)
    return c and c:FindFirstChild("Head")
end
function Utils.GetHum(player)
    local c = Utils.GetChar(player)
    return c and c:FindFirstChildOfClass("Humanoid")
end
function Utils.IsAlive(player)
    local h = Utils.GetHum(player)
    return h and h.Health > 0
end
function Utils.IsEnemy(player)
    if not Core.LP.Team or not player.Team then return true end
    return player.Team ~= Core.LP.Team
end
function Utils.W2S(pos)
    local sp, vis = Core.Cam:WorldToScreenPoint(pos)
    return Vector2.new(sp.X, sp.Y), vis, sp.Z
end
function Utils.Dist(a, b)
    if typeof(a) == "Vector3" and typeof(b) == "Vector3" then
        return (a - b).Magnitude
    end
    local ra = Utils.GetRoot(a)
    local rb = Utils.GetRoot(b)
    if ra and rb then return (ra.Position - rb.Position).Magnitude end
    return math.huge
end
function Utils.TP(cf)
    local root = Utils.GetRoot()
    if root then root.CFrame = cf end
end
function Utils.SafeCall(fn, ...)
    local ok, err = pcall(fn, ...)
    if not ok then Core.Log("SAFE", tostring(err), "ERR") end
    return ok
end
function Utils.Tween(inst, props, t, style)
    S.TweenService:Create(inst,
        TweenInfo.new(t or 0.25, style or Enum.EasingStyle.Quad), props):Play()
end
function Utils.Color(r,g,b) return Color3.fromRGB(r,g,b) end
function Utils.Lerp(a,b,t)  return a + (b-a)*t end

-- ── Drawing Factory ───────────────────────────────────────────────
local Draw = {}
Core.Draw = Draw

function Draw.Box(col, thick, filled)
    local d = Drawing.new("Square")
    d.Color     = col or Utils.Color(180,80,255)
    d.Thickness = thick or 1.5
    d.Filled    = filled or false
    d.Visible   = false
    return d
end
function Draw.Line(col, thick)
    local d = Drawing.new("Line")
    d.Color     = col or Utils.Color(80,200,255)
    d.Thickness = thick or 1
    d.Visible   = false
    return d
end
function Draw.Text(txt, sz, col, center, outline)
    local d = Drawing.new("Text")
    d.Text         = txt or ""
    d.Size         = sz or 13
    d.Color        = col or Utils.Color(230,225,255)
    d.Center       = center ~= false
    d.Outline      = outline ~= false
    d.OutlineColor = Color3.new(0,0,0)
    d.Visible      = false
    return d
end
function Draw.Circle(r, col, thick, filled)
    local d = Drawing.new("Circle")
    d.Radius    = r or 60
    d.Color     = col or Utils.Color(180,80,255)
    d.Thickness = thick or 1.5
    d.Filled    = filled or false
    d.Visible   = false
    return d
end
function Draw.Triangle(col, thick, filled)
    local d = Drawing.new("Triangle")
    d.Color     = col or Utils.Color(255,80,160)
    d.Thickness = thick or 1.5
    d.Filled    = filled or false
    d.Visible   = false
    return d
end
function Draw.Quad(col, thick, filled)
    local d = Drawing.new("Quad")
    d.Color     = col or Utils.Color(180,80,255)
    d.Thickness = thick or 1.5
    d.Filled    = filled or false
    d.Visible   = false
    return d
end

-- ── Panic Button — matiin semua module sekaligus ──────────────────
function Core.Panic()
    for name, mod in pairs(_modules) do
        if mod.Disable then pcall(mod.Disable, mod) end
    end
    Core.Log("PANIC", "🚨 All modules disabled — clean exit!", "WARN")
    Core.Emit("panic")
end

-- ── Hotkey watcher ────────────────────────────────────────────────
local _hotkeys = {}
function Core.Hotkey(keyName, fn)
    _hotkeys[keyName] = fn
end
S.UserInputService.InputBegan:Connect(function(inp, gpe)
    if gpe then return end
    local kn = inp.KeyCode.Name
    if _hotkeys[kn] then pcall(_hotkeys[kn]) end
end)

Core.Log("CORE", "⚡ Core engine ready — Dev Mode standby", "OK")
return Core
