--[[  CheatDev — forge/templates.lua
      Semua template Script Forge. Tambah bebas, gada batasnya.
      /C <NAME> → inject langsung. Makin absurd makin bagus.
--]]

return {

    -- ── VISUAL ───────────────────────────────────────────────────
    ESP_QUICK = [[
local P=game:GetService("Players"); local C=workspace.CurrentCamera; local LP=P.LocalPlayer
for _,p in ipairs(P:GetPlayers()) do
  if p~=LP then
    local b=Drawing.new("Square"); b.Color=Color3.fromRGB(180,80,255); b.Thickness=1.5; b.Filled=false; b.Visible=true
    local t=Drawing.new("Text"); t.Text=p.Name; t.Size=13; t.Color=Color3.new(1,1,1); t.Center=true; t.Outline=true; t.Visible=true
    game:GetService("RunService").RenderStepped:Connect(function()
      local r=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
      local h=p.Character and p.Character:FindFirstChild("Head")
      if not r or not h then b.Visible=false; t.Visible=false; return end
      local st,vt=C:WorldToScreenPoint(h.Position+Vector3.new(0,.7,0))
      local sb,vb=C:WorldToScreenPoint(r.Position-Vector3.new(0,3,0))
      if not vt and not vb then b.Visible=false; t.Visible=false; return end
      local hw=math.abs(st.Y-sb.Y)*.45
      b.Size=Vector2.new(hw*2,math.abs(st.Y-sb.Y)); b.Position=Vector2.new(st.X-hw,st.Y); b.Visible=true
      t.Position=Vector2.new(st.X,st.Y-16); t.Visible=true
    end)
  end
end; print("[CD] ESP_QUICK injected")
]],

    CHAMS = [[
-- Chams — warnain karakter musuh biar keliatan through wall
local P=game:GetService("Players"); local LP=P.LocalPlayer
local function chamsPlayer(p)
  local function apply(char)
    for _,v in ipairs(char:GetDescendants()) do
      if v:IsA("BasePart") then
        v.Material=Enum.Material.Neon
        v.Color=Color3.fromRGB(255,80,80)
        v.LocalTransparencyModifier=0
      end
    end
  end
  if p.Character then apply(p.Character) end
  p.CharacterAdded:Connect(apply)
end
for _,p in ipairs(P:GetPlayers()) do if p~=LP then chamsPlayer(p) end end
P.PlayerAdded:Connect(function(p) if p~=LP then chamsPlayer(p) end end)
print("[CD] CHAMS injected")
]],

    -- ── MOVEMENT ─────────────────────────────────────────────────
    SPEED_HACK = [[
local LP=game:GetService("Players").LocalPlayer
local h=LP.Character and LP.Character:FindFirstChildOfClass("Humanoid")
if h then h.WalkSpeed=100; h.JumpPower=80 end
LP.CharacterAdded:Connect(function(c)
  local hum=c:WaitForChild("Humanoid"); hum.WalkSpeed=100; hum.JumpPower=80
end); print("[CD] SPEED_HACK 100ws/80jp injected")
]],

    NOCLIP = [[
local RS=game:GetService("RunService"); local LP=game:GetService("Players").LocalPlayer
RS.Stepped:Connect(function()
  local c=LP.Character
  if c then for _,p in ipairs(c:GetDescendants()) do if p:IsA("BasePart") then p.CanCollide=false end end end
end); print("[CD] NOCLIP injected")
]],

    FLY_HACK = [[
local P=game:GetService("Players"); local UIS=game:GetService("UserInputService")
local RS=game:GetService("RunService"); local LP=P.LocalPlayer
local flying=true; local spd=80; local bp,bg
local function enable()
  local r=LP.Character and LP.Character:FindFirstChild("HumanoidRootPart")
  local h=LP.Character and LP.Character:FindFirstChildOfClass("Humanoid")
  if not r or not h then return end; h.PlatformStand=true
  bp=Instance.new("BodyPosition"); bp.MaxForce=Vector3.new(1e5,1e5,1e5); bp.Parent=r
  bg=Instance.new("BodyGyro"); bg.MaxTorque=Vector3.new(1e5,1e5,1e5); bg.Parent=r
  RS.RenderStepped:Connect(function()
    if not flying then return end
    local cf=workspace.CurrentCamera.CFrame; local d=Vector3.new(0,0,0)
    if UIS:IsKeyDown(Enum.KeyCode.W) then d=d+cf.LookVector end
    if UIS:IsKeyDown(Enum.KeyCode.S) then d=d-cf.LookVector end
    if UIS:IsKeyDown(Enum.KeyCode.A) then d=d-cf.RightVector end
    if UIS:IsKeyDown(Enum.KeyCode.D) then d=d+cf.RightVector end
    if UIS:IsKeyDown(Enum.KeyCode.Space) then d=d+Vector3.new(0,1,0) end
    if UIS:IsKeyDown(Enum.KeyCode.LeftControl) then d=d-Vector3.new(0,1,0) end
    if d.Magnitude>0 then d=d.Unit end
    local mul=UIS:IsKeyDown(Enum.KeyCode.LeftShift) and 2.5 or 1
    if r then bp.Position=r.Position+d*spd*mul*0.05; bg.CFrame=cf end
  end)
end; enable(); print("[CD] FLY_HACK ON — WASD+Space+Ctrl, LShift=sprint")
]],

    INF_JUMP = [[
local UIS=game:GetService("UserInputService"); local LP=game:GetService("Players").LocalPlayer
UIS.JumpRequest:Connect(function()
  local h=LP.Character and LP.Character:FindFirstChildOfClass("Humanoid")
  if h then h:ChangeState(Enum.HumanoidStateType.Jumping) end
end); print("[CD] INF_JUMP injected")
]],

    GRAVITY_MOD = [[
-- Gravity modifier — default Roblox = 196.2
workspace.Gravity=50  -- makin kecil makin float
print("[CD] GRAVITY_MOD — gravity set to 50 (float mode)")
]],

    LOW_GRAVITY = [[
workspace.Gravity=20; print("[CD] LOW_GRAVITY — moon mode")
]],

    ZERO_GRAVITY = [[
workspace.Gravity=0; print("[CD] ZERO_GRAVITY — space mode 🚀")
]],

    -- ── COMBAT ───────────────────────────────────────────────────
    KILL_AURA = [[
local P=game:GetService("Players"); local RS=game:GetService("RunService"); local LP=P.LocalPlayer
local RADIUS=20; local DMG=50; local timer=0
RS.Heartbeat:Connect(function(dt)
  timer=timer+dt; if timer<0.1 then return end; timer=0
  local r=LP.Character and LP.Character:FindFirstChild("HumanoidRootPart"); if not r then return end
  for _,p in ipairs(P:GetPlayers()) do
    if p~=LP and p.Character then
      local pr=p.Character:FindFirstChild("HumanoidRootPart"); local h=p.Character:FindFirstChildOfClass("Humanoid")
      if pr and h and h.Health>0 and (r.Position-pr.Position).Magnitude<=RADIUS then h:TakeDamage(DMG) end
    end
  end
end); print("[CD] KILL_AURA r:"..20 .." dmg:"..50)
]],

    HITBOX_EXPAND = [[
local P=game:GetService("Players"); local RS=game:GetService("RunService"); local LP=P.LocalPlayer
local SIZE=12
RS.Heartbeat:Connect(function()
  for _,p in ipairs(P:GetPlayers()) do
    if p~=LP and p.Character then
      local r=p.Character:FindFirstChild("HumanoidRootPart")
      if r then r.Size=Vector3.new(SIZE,SIZE,SIZE); r.Transparency=0.92 end
    end
  end
end); print("[CD] HITBOX_EXPAND size:"..12)
]],

    TP_KILL = [[
local P=game:GetService("Players"); local LP=P.LocalPlayer
for _,p in ipairs(P:GetPlayers()) do
  if p~=LP and p.Character then
    local pr=p.Character:FindFirstChild("HumanoidRootPart"); local h=p.Character:FindFirstChildOfClass("Humanoid")
    local mr=LP.Character and LP.Character:FindFirstChild("HumanoidRootPart")
    if pr and h and mr then mr.CFrame=pr.CFrame*CFrame.new(0,0,-2); task.wait(0.05); h.Health=0 end
    task.wait(0.2)
  end
end; print("[CD] TP_KILL executed")
]],

    FLING = [[
-- Fling semua player — absurd level
local P=game:GetService("Players"); local LP=P.LocalPlayer
for _,p in ipairs(P:GetPlayers()) do
  if p~=LP and p.Character then
    local r=p.Character:FindFirstChild("HumanoidRootPart")
    if r then r.AssemblyLinearVelocity=Vector3.new(math.random(-500,500),800,math.random(-500,500)) end
  end
end; print("[CD] FLING all players 🌪️")
]],

    -- ── UTILITY ──────────────────────────────────────────────────
    GOD_MODE = [[
local RS=game:GetService("RunService"); local LP=game:GetService("Players").LocalPlayer
RS.Heartbeat:Connect(function()
  local h=LP.Character and LP.Character:FindFirstChildOfClass("Humanoid")
  if h then h.Health=h.MaxHealth end
end); print("[CD] GOD_MODE — HP always full")
]],

    INF_STAMINA = [[
local RS=game:GetService("RunService"); local LP=game:GetService("Players").LocalPlayer
RS.Heartbeat:Connect(function()
  local c=LP.Character; if not c then return end
  for _,v in ipairs(c:GetDescendants()) do
    if v.Name:lower():find("stamina") or v.Name:lower():find("energy") then
      if v:IsA("NumberValue") or v:IsA("IntValue") then
        pcall(function() v.Value=v.Value>0 and v.Value or 100 end)
      end
    end
  end
end); print("[CD] INF_STAMINA injected")
]],

    ANTI_RAGDOLL = [[
local LP=game:GetService("Players").LocalPlayer
local function fix(c) for _,v in ipairs(c:GetDescendants()) do
  if v:IsA("BallSocketConstraint") or v:IsA("HingeConstraint") then v.Enabled=false end
end end
if LP.Character then fix(LP.Character) end
LP.CharacterAdded:Connect(fix); print("[CD] ANTI_RAGDOLL injected")
]],

    SPIN_BOT = [[
local RS=game:GetService("RunService"); local LP=game:GetService("Players").LocalPlayer
local a=0
RS.RenderStepped:Connect(function(dt)
  a=(a+30*dt)%360
  local r=LP.Character and LP.Character:FindFirstChild("HumanoidRootPart")
  if r then r.CFrame=CFrame.new(r.Position)*CFrame.Angles(0,math.rad(a),0) end
end); print("[CD] SPIN_BOT ON 🌀")
]],

    TELEPORT_ME = [[
local function tp(pos)
  local r=game:GetService("Players").LocalPlayer.Character and game:GetService("Players").LocalPlayer.Character:FindFirstChild("HumanoidRootPart")
  if r then r.CFrame=CFrame.new(pos) end
end
-- Usage: tp(Vector3.new(x,y,z))
-- Example: tp(Vector3.new(0,50,0))
print("[CD] TELEPORT_ME loaded — call tp(Vector3.new(x,y,z))")
]],

    ITEM_MAGNET = [[
local RS=game:GetService("RunService"); local LP=game:GetService("Players").LocalPlayer; local RANGE=40
RS.Heartbeat:Connect(function()
  local r=LP.Character and LP.Character:FindFirstChild("HumanoidRootPart"); if not r then return end
  for _,o in ipairs(workspace:GetDescendants()) do
    if o:IsA("BasePart") and not o.Anchored and (o.Position-r.Position).Magnitude<=RANGE then
      o.AssemblyLinearVelocity=(r.Position-o.Position).Unit*30
    end
  end
end); print("[CD] ITEM_MAGNET range:"..40)
]],

    -- ── FARMING ──────────────────────────────────────────────────
    AUTO_FARM_GENERIC = [[
local RS=game:GetService("RunService"); local LP=game:GetService("Players").LocalPlayer
local TAG="Enemy"; local running=true
RS.Heartbeat:Connect(function()
  if not running then return end
  local r=LP.Character and LP.Character:FindFirstChild("HumanoidRootPart"); if not r then return end
  local best,dist=nil,math.huge
  for _,o in ipairs(workspace:GetDescendants()) do
    if o.Name==TAG and o:FindFirstChild("HumanoidRootPart") then
      local d=(r.Position-o.HumanoidRootPart.Position).Magnitude
      if d<dist then best,dist=o,d end
    end
  end
  if best then r.CFrame=CFrame.new(best.HumanoidRootPart.Position+Vector3.new(0,3,0)) end
end)
print("[CD] AUTO_FARM_GENERIC — TAG="..TAG.." (edit TAG sesuai game)")
]],

    AUTO_QUEST = [[
local LP=game:GetService("Players").LocalPlayer; local RS=game:GetService("RunService")
local NPC_TAG="QuestNPC"
RS.Heartbeat:Connect(function()
  local r=LP.Character and LP.Character:FindFirstChild("HumanoidRootPart"); if not r then return end
  for _,o in ipairs(workspace:GetDescendants()) do
    if o.Name:find(NPC_TAG) then
      local part=o:IsA("Model") and (o.PrimaryPart or o:FindFirstChildWhichIsA("BasePart")) or o
      if part then
        r.CFrame=CFrame.new(part.Position+Vector3.new(0,2,0))
        local pp=o:FindFirstChildWhichIsA("ProximityPrompt",true)
        if pp then pcall(function() fireproximityprompt(pp) end) end
        task.wait(0.5)
      end
    end
  end
end); print("[CD] AUTO_QUEST injected — NPC_TAG="..NPC_TAG)
]],

    -- ── DEV TOOLS ────────────────────────────────────────────────
    DEV_CONSOLE = [[
print("════════ CHEAT DEV CONSOLE ════════")
print("Place   :", game.PlaceId)
print("Job     :", game.JobId)
print("Players :", #game:GetService("Players"):GetPlayers())
for _,p in ipairs(game:GetService("Players"):GetPlayers()) do
  local h=p.Character and p.Character:FindFirstChildOfClass("Humanoid")
  print(string.format("  %-20s HP:%-6s Team:%s",p.Name,
    h and math.floor(h.Health).."/"..math.floor(h.MaxHealth) or "dead",
    tostring(p.Team and p.Team.Name or "none")))
end
print("Workspace parts:", #workspace:GetDescendants())
print("Lighting effects:", #game:GetService("Lighting"):GetChildren())
print("═══════════════════════════════════")
]],

    REMOTE_SPY_LITE = [[
-- Remote Spy lite — log semua RemoteEvent/Function yang dipanggil
local lp=game:GetService("Players").LocalPlayer
local _call=Instance.new; local _fe={}
for _,v in ipairs(game:GetDescendants()) do
  if v:IsA("RemoteEvent") or v:IsA("RemoteFunction") then
    local oldFire=v.FireServer
    pcall(function()
      v.FireServer=function(self,...)
        print("[RemoteSpy]",v:GetFullName(), ...)
        return oldFire(self,...)
      end
    end)
    table.insert(_fe, v)
  end
end
print("[CD] REMOTE_SPY_LITE — watching", #_fe, "remotes")
]],

    EXECUTOR_INFO = [[
print("════ EXECUTOR INFO ════")
print("getgenv   :", type(getgenv))
print("gethui    :", type(gethui))
print("Drawing   :", type(Drawing))
print("loadstring:", type(loadstring))
print("HttpGet   :", type(game.HttpGet))
print("syn/fluxus:", syn and "syn" or fluxus and "fluxus" or "unknown")
print("======================")
]],

    CRASH_STUDIO = [[
-- Studio crash test — JANGAN di real game server!
-- Hanya untuk lokal/private testing
if not game:GetService("RunService"):IsStudio() then
  print("[CD] CRASH_STUDIO — only runs in Studio!"); return
end
for i=1,100000 do Instance.new("Part").Parent=workspace end
print("[CD] CRASH_STUDIO fired — RIP studio 💀")
]],

    INFINITE_YIELD = [[
-- Inject Infinite Yield admin console
loadstring(game:HttpGet("https://raw.githubusercontent.com/EdgeIY/infinite-yield/main/main.lua"))()
print("[CD] INFINITE_YIELD loading...")
]],

    DEX_EXPLORER = [[
-- Inject Dex Explorer
loadstring(game:HttpGet("https://raw.githubusercontent.com/infyiff/backup/main/dex.lua"))()
print("[CD] DEX_EXPLORER loading...")
]],

    DARK_DAGGER = [[
-- Dark Dagger GUI (generic)
loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/Hub.lua"))()
print("[CD] XC Hub loaded via DARK_DAGGER alias")
]],

    PRINT_ENV = [[
print("════ ENV DUMP ════")
for k,v in pairs(getgenv()) do
  if type(v)~="function" then print(k,"=",tostring(v)) end
end
print("=================")
]],

    -- ── ALL-GAME GENERIC (engine-agnostic Lua/script patterns) ────────────

    SPEED_INJECT = [[
-- Generic speed multiplier — works on many Roblox/Luau games
local LP = game:GetService("Players").LocalPlayer
local function applySpeed(mult)
  local char = LP.Character or LP.CharacterAdded:Wait()
  local hum = char:WaitForChild("Humanoid")
  hum.WalkSpeed = 16 * mult
  hum.JumpPower = 50 * mult * 0.5
  print(string.format("[CD] Speed x%.1f | Jump x%.1f", mult, mult*0.5))
end
LP.CharacterAdded:Connect(function() applySpeed(3) end)
if LP.Character then applySpeed(3) end
]],

    HITBOX_EXPANDER = [[
-- Hitbox expander — enlarges all enemy hitboxes for easier hits
local P = game:GetService("Players"); local LP = P.LocalPlayer
local SIZE = Vector3.new(12,12,12)  -- adjust size
local function expandHitbox(player)
  local function apply(char)
    for _, part in ipairs(char:GetDescendants()) do
      if part:IsA("BasePart") and part.Name ~= "HumanoidRootPart" then
        part.Size = SIZE
      end
    end
  end
  if player.Character then apply(player.Character) end
  player.CharacterAdded:Connect(apply)
end
for _, p in ipairs(P:GetPlayers()) do
  if p ~= LP then expandHitbox(p) end
end
P.PlayerAdded:Connect(function(p) if p ~= LP then expandHitbox(p) end end)
print("[CD] HITBOX_EXPANDER — size:", SIZE)
]],

    FULL_BRIGHT = [[
-- FullBright — max visibility in dark maps
local Lighting = game:GetService("Lighting")
Lighting.Brightness = 10
Lighting.ClockTime = 14
Lighting.FogEnd = 1e6
Lighting.GlobalShadows = false
for _, v in ipairs(Lighting:GetChildren()) do
  if v:IsA("BlurEffect") or v:IsA("ColorCorrectionEffect") or
     v:IsA("SunRaysEffect") or v:IsA("BloomEffect") then
    v.Enabled = false
  end
end
print("[CD] FULL_BRIGHT ON")
]],

    ANTI_AFK_PRO = [[
-- Anti-AFK + auto rejoin on kick
local VIM = game:GetService("VirtualInputManager")
local UIS = game:GetService("UserInputService")
local function nudge()
  VIM:SendKeyEvent(true,  Enum.KeyCode.W, false, game)
  task.wait(0.1)
  VIM:SendKeyEvent(false, Enum.KeyCode.W, false, game)
end
game:GetService("RunService").Heartbeat:Connect(function()
  if tick() % 60 < 0.016 then nudge() end
end)
-- Auto-close kick dialog
game:GetService("StarterGui"):SetCore("ResetButtonCallback", false)
print("[CD] ANTI_AFK_PRO — nudging every 60s")
]],

    BTOOLS_INJECT = [[
-- Building Tools inject (Studio-style in game)
local tl = Instance.new("HopperBin"); tl.BinType = Enum.BinType.GameTool
local bt = require(game:GetService("InsertService"):LoadAsset(142785488).GrabTool)
print("[CD] BTOOLS attempted (executor-dependent)")
]],

    SERVER_HOP_INSTANT = [[
-- Server hop to lowest population server
local TM = game:GetService("TeleportService")
local HS = game:GetService("HttpService")
local placeid = game.PlaceId
local ok, data = pcall(function()
  return HS:JSONDecode(game:HttpGet(
    "https://games.roblox.com/v1/games/"..placeid.."/servers/Public?sortOrder=Asc&limit=10"
  ))
end)
if ok and data and data.data then
  local servers = data.data
  table.sort(servers, function(a,b) return a.playing < b.playing end)
  for _, s in ipairs(servers) do
    if s.id ~= game.JobId then
      TM:TeleportToPlaceInstance(placeid, s.id)
      return
    end
  end
end
print("[CD] SERVER_HOP_INSTANT — no alternate server found")
]],

    UNLOCK_ALL_ANIMS = [[
-- Unlock all animations / override humanoid animator
local LP = game:GetService("Players").LocalPlayer
local function unlockAnims(char)
  local Animate = char:FindFirstChild("Animate")
  if Animate then Animate.Disabled = true end
  local hum = char:FindFirstChild("Humanoid")
  if hum then
    local ha = hum:FindFirstChildOfClass("Animator")
    if ha then ha:LoadAnimation(Instance.new("Animation")) end
  end
end
LP.CharacterAdded:Connect(unlockAnims)
if LP.Character then unlockAnims(LP.Character) end
print("[CD] UNLOCK_ALL_ANIMS — animator unhooked")
]],

    CAMLOCK = [[
-- Camera Lock — lock cam to nearest enemy head
local P = game:GetService("Players"); local LP = P.LocalPlayer
local C = workspace.CurrentCamera
local RS = game:GetService("RunService")
local function nearest()
  local best, dist = nil, math.huge
  for _, p in ipairs(P:GetPlayers()) do
    if p ~= LP and p.Character then
      local hr = p.Character:FindFirstChild("HumanoidRootPart")
      if hr then
        local d = (hr.Position - LP.Character.HumanoidRootPart.Position).Magnitude
        if d < dist then best,dist=p,d end
      end
    end
  end
  return best
end
RS.RenderStepped:Connect(function()
  local t = nearest()
  if t and t.Character then
    local head = t.Character:FindFirstChild("Head")
    if head then C.CFrame = CFrame.new(C.CFrame.Position, head.Position) end
  end
end)
print("[CD] CAMLOCK ON")
]],

    ESP_ITEMS = [[
-- Item/Drop ESP — highlight all items on map
local RS = game:GetService("RunService")
local C  = workspace.CurrentCamera
local tags = {"Value","Tool","Handle","Item","Drop","Loot","Pickup","Coin","Chest","Crate"}
local drawings = {}
RS.RenderStepped:Connect(function()
  for _, d in ipairs(drawings) do d:Remove() end
  drawings = {}
  for _, obj in ipairs(workspace:GetDescendants()) do
    for _, tag in ipairs(tags) do
      if obj.Name:lower():find(tag:lower()) and obj:IsA("BasePart") then
        local sp, vis = C:WorldToScreenPoint(obj.Position)
        if vis then
          local dot = Drawing.new("Circle")
          dot.Position = Vector2.new(sp.X, sp.Y)
          dot.Radius = 6; dot.Filled = true
          dot.Color = Color3.fromRGB(255,215,0)
          dot.Visible = true; dot.ZIndex = 5
          table.insert(drawings, dot)
          local lbl = Drawing.new("Text")
          lbl.Text = obj.Name
          lbl.Position = Vector2.new(sp.X+8, sp.Y-6)
          lbl.Size = 11; lbl.Color = Color3.new(1,1,0)
          lbl.Outline = true; lbl.Visible = true
          table.insert(drawings, lbl)
        end
        break
      end
    end
  end
end)
print("[CD] ESP_ITEMS — scanning for drops/loot")
]],

    TRIGGER_BOT = [[
-- TriggerBot — auto fire when crosshair on enemy (raycast-based)
local P   = game:GetService("Players"); local LP = P.LocalPlayer
local C   = workspace.CurrentCamera
local UIS = game:GetService("UserInputService")
local RS  = game:GetService("RunService")
local tool = nil
LP.CharacterAdded:Connect(function(char)
  char.ChildAdded:Connect(function(c) if c:IsA("Tool") then tool=c end end)
end)
RS.RenderStepped:Connect(function()
  if not tool then return end
  local ray = C:ScreenPointToRay(C.ViewportSize.X/2, C.ViewportSize.Y/2)
  local result = workspace:Raycast(ray.Origin, ray.Direction * 500)
  if result and result.Instance then
    local model = result.Instance:FindFirstAncestorOfClass("Model")
    local p = model and P:GetPlayerFromCharacter(model)
    if p and p ~= LP then
      if tool:FindFirstChild("RemoteEvent") then
        tool.RemoteEvent:FireServer()
      elseif tool:FindFirstChild("RemoteFunction") then
        tool.RemoteFunction:InvokeServer()
      end
    end
  end
end)
print("[CD] TRIGGER_BOT ON — auto fires on target")
]],

}
