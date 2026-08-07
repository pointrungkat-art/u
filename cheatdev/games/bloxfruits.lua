--[[
  CheatDev — games/bloxfruits.lua
  Blox Fruits game-specific module.

  Features:
    • Devil Fruit ESP          — highlight buah + distance label
    • Auto Farm                — kill mob terdekat di island level
    • Auto Collect Fruit       — ambil buah yang spawn di ground
    • Sea Beast Tracker        — ESP + alert sea beast
    • Auto Quest               — TP ke NPC quest, accept, farm, turn in
    • Stat Auto-Allocate       — invest stat poin ke target stat
    • Raid Assist              — TP ke raid boss location
]]
return function(Core)
    local S, U, D = Core.Services, Core.Utils, Core.Draw
    local LP       = Core.LP
    local RS       = S.RunService
    local cfg      = Core.Config.BLOX_FRUITS or {}

    -- Default config kalau belum ada di config.lua
    cfg.fruitESP       = cfg.fruitESP       ~= false and true
    cfg.autoFarm       = cfg.autoFarm       or false
    cfg.autoCollect    = cfg.autoCollect    or false
    cfg.seaBeastESP    = cfg.seaBeastESP    or false
    cfg.autoQuest      = cfg.autoQuest      or false
    cfg.farmRadius     = cfg.farmRadius     or 2000
    cfg.farmDelay      = cfg.farmDelay      or 0.3
    cfg.fruitMaxDist   = cfg.fruitMaxDist   or 3000
    cfg.targetStat     = cfg.targetStat     or "Melee" -- Melee | Defense | Sword | Gun | Fruit
    cfg.enabled        = cfg.enabled        or false

    -- Blox Fruits internal folder refs (game PlaceId 2753915549)
    local WS  = workspace
    local RS2 = game:GetService("ReplicatedStorage")
    local RS3 = game:GetService("ReplicatedFirst")

    -- ── Helpers ─────────────────────────────────────────────────
    local function log(msg, lvl) Core.Log("BF", msg, lvl or "INFO") end

    local function getChar() return LP.Character end
    local function getRoot()
        local c = getChar(); return c and c:FindFirstChild("HumanoidRootPart")
    end
    local function getHum()
        local c = getChar(); return c and c:FindFirstChildOfClass("Humanoid")
    end

    local FRUIT_COLORS = {
        -- Uncommon
        Bomb = Color3.fromRGB(100,100,100), Spike = Color3.fromRGB(180,200,80),
        Chop = Color3.fromRGB(120,80,50), Spring = Color3.fromRGB(200,200,200),
        Kilo = Color3.fromRGB(160,120,80), Smoke = Color3.fromRGB(140,140,140),
        Snowy = Color3.fromRGB(200,230,255), Flame = Color3.fromRGB(255,140,30),
        Spin = Color3.fromRGB(100,200,255), Candy = Color3.fromRGB(255,150,200),
        -- Rare
        Ice = Color3.fromRGB(120,220,255), Sand = Color3.fromRGB(220,190,130),
        Quake = Color3.fromRGB(180,100,200), Gravity = Color3.fromRGB(80,80,200),
        Magma = Color3.fromRGB(255,60,0), Light = Color3.fromRGB(255,255,120),
        Rumble = Color3.fromRGB(255,255,0), Dark = Color3.fromRGB(60,20,100),
        Revive = Color3.fromRGB(0,220,100),
        -- Legendary
        Diamond = Color3.fromRGB(130,240,255), Door = Color3.fromRGB(160,100,220),
        Rubber = Color3.fromRGB(255,180,0), Barrier = Color3.fromRGB(200,200,100),
        Ghost = Color3.fromRGB(200,200,255), Shadow = Color3.fromRGB(80,0,120),
        Mammoth = Color3.fromRGB(180,160,140), Spider = Color3.fromRGB(60,60,60),
        Control = Color3.fromRGB(255,100,255), String = Color3.fromRGB(240,240,240),
        -- Mythical
        Blizzard = Color3.fromRGB(0,180,255), Venom = Color3.fromRGB(80,200,30),
        Spirit = Color3.fromRGB(255,200,80), Sound = Color3.fromRGB(120,80,220),
        Dragon = Color3.fromRGB(200,50,50), Leopard = Color3.fromRGB(220,180,100),
        Portal = Color3.fromRGB(80,200,200), T_Rex = Color3.fromRGB(100,220,80),
        Kitsune = Color3.fromRGB(255,150,80),
    }
    local DEFAULT_FRUIT_COLOR = Color3.fromRGB(255, 220, 80) -- gold for unknown

    local FRUIT_TAGS = {
        "Fruit", "DevilFruit", "Devil_Fruit", "BloxFruit", "BloxFruits_Fruit",
        "Logia", "Zoan", "Paramecia"
    }
    local MOB_TAGS      = {"Enemy", "Boss", "Mob", "NPC_Enemy"}
    local SEA_BEAST_NAMES = {"Sea Beast", "SeaBeast", "Sea_Beast", "Terrorshark", "Leviathan"}
    local QUEST_NPC_NAMES = {"Quest", "QuestGiver", "TaskGiver", "Trainer"}

    -- ── Fruit Detection ─────────────────────────────────────────
    local function findFruits()
        local fruits = {}
        -- Method 1: Tag-based
        local CS = game:GetService("CollectionService")
        for _, tag in ipairs(FRUIT_TAGS) do
            for _, obj in ipairs(CS:GetTagged(tag)) do
                if obj:FindFirstChild("HumanoidRootPart") or obj:FindFirstChild("Handle") or obj.PrimaryPart then
                    table.insert(fruits, obj)
                end
            end
        end
        -- Method 2: Workspace scan (fallback)
        if #fruits == 0 then
            for _, obj in ipairs(WS:GetDescendants()) do
                if obj:IsA("Model") then
                    local n = obj.Name
                    for _, tag in ipairs(FRUIT_TAGS) do
                        if n:find(tag, 1, true) or n:find("Fruit", 1, true) then
                            table.insert(fruits, obj); break
                        end
                    end
                end
            end
        end
        return fruits
    end

    local function findMobs(radius)
        local root = getRoot(); if not root then return {} end
        local mobs = {}
        for _, p in ipairs(S.Players:GetPlayers()) do
            -- Skip human players; only want NPCs
        end
        for _, obj in ipairs(WS:GetDescendants()) do
            if obj:IsA("Model") then
                local hum = obj:FindFirstChildOfClass("Humanoid")
                local rootPart = obj:FindFirstChild("HumanoidRootPart")
                if hum and rootPart and hum.Health > 0 then
                    -- Make sure it's not a player
                    local isPlayer = false
                    for _, p in ipairs(S.Players:GetPlayers()) do
                        if p.Character == obj then isPlayer = true; break end
                    end
                    if not isPlayer then
                        local dist = (root.Position - rootPart.Position).Magnitude
                        if dist <= (radius or cfg.farmRadius) then
                            table.insert(mobs, {model=obj, hum=hum, root=rootPart, dist=dist})
                        end
                    end
                end
            end
        end
        -- Sort nearest first
        table.sort(mobs, function(a, b) return a.dist < b.dist end)
        return mobs
    end

    local function findSeaBeasts()
        local beasts = {}
        for _, obj in ipairs(WS:GetDescendants()) do
            if obj:IsA("Model") then
                for _, name in ipairs(SEA_BEAST_NAMES) do
                    if obj.Name:lower():find(name:lower(), 1, true) then
                        local rp = obj:FindFirstChild("HumanoidRootPart") or obj.PrimaryPart
                        if rp then table.insert(beasts, {model=obj, root=rp}); break end
                    end
                end
            end
        end
        return beasts
    end

    -- ── Drawing Objects ─────────────────────────────────────────
    local _fruitDrawings  = {}
    local _mobDrawings    = {}
    local _seaDrawings    = {}

    local function clearDrawings(tbl)
        for _, d in pairs(tbl) do
            for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
        end
        for k in pairs(tbl) do tbl[k] = nil end
    end

    -- ── Fruit ESP ───────────────────────────────────────────────
    local BF_ESP = {}

    function BF_ESP.Update()
        if not cfg.fruitESP or not cfg.enabled then
            clearDrawings(_fruitDrawings); return
        end
        local root = getRoot(); if not root then return end
        local fruits = findFruits()
        local activeKeys = {}

        for _, fruit in ipairs(fruits) do
            local rp = fruit.PrimaryPart or fruit:FindFirstChild("HumanoidRootPart")
                     or fruit:FindFirstChildOfClass("BasePart")
            if not rp then continue end

            local dist = (root.Position - rp.Position).Magnitude
            if dist > cfg.fruitMaxDist then continue end

            local key = tostring(fruit)
            activeKeys[key] = true

            if not _fruitDrawings[key] then
                local col = FRUIT_COLORS[fruit.Name] or DEFAULT_FRUIT_COLOR
                _fruitDrawings[key] = {
                    name = D.Text("", 13, col),
                    dist = D.Text("", 11, Color3.fromRGB(220,220,100)),
                    line = D.Line(col, 1),
                }
            end

            local d = _fruitDrawings[key]
            local sp, vis = U.W2S(rp.Position + Vector3.new(0, 2, 0))
            if not vis then
                d.name.Visible = false; d.dist.Visible = false; d.line.Visible = false
                continue
            end

            local vp = Core.Cam.ViewportSize
            d.name.Text     = "🍎 " .. fruit.Name
            d.name.Position = Vector2.new(sp.X, sp.Y - 16)
            d.name.Visible  = true

            d.dist.Text     = string.format("%.0fm", dist)
            d.dist.Position = Vector2.new(sp.X, sp.Y)
            d.dist.Visible  = true

            d.line.From    = Vector2.new(vp.X / 2, vp.Y / 2)
            d.line.To      = Vector2.new(sp.X, sp.Y)
            d.line.Visible = true
        end

        -- Remove stale drawings
        for key, d in pairs(_fruitDrawings) do
            if not activeKeys[key] then
                for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
                _fruitDrawings[key] = nil
            end
        end
    end

    -- ── Auto Farm ────────────────────────────────────────────────
    local _farmRunning = false
    local _farmThread  = nil

    function BF_ESP.StartFarm()
        if _farmRunning then return end
        _farmRunning = true
        log("🌾 Auto Farm started — radius: " .. cfg.farmRadius, "OK")
        _farmThread = task.spawn(function()
            while _farmRunning and cfg.autoFarm and cfg.enabled do
                local mobs = findMobs(cfg.farmRadius)
                if #mobs > 0 then
                    local target = mobs[1]
                    local root   = getRoot()
                    if root and target.root and target.hum.Health > 0 then
                        -- TP directly on top
                        root.CFrame = target.root.CFrame * CFrame.new(0, 3, 3)
                        task.wait(0.1)
                        -- Click/attack simulation (game-specific tool activation)
                        local tool = LP.Character and LP.Character:FindFirstChildOfClass("Tool")
                        if tool then
                            local event = tool:FindFirstChild("RemoteEvent") or
                                          tool:FindFirstChildOfClass("RemoteEvent")
                            -- Trigger attack
                            pcall(function()
                                if tool.ToolTip == "" then
                                    -- Use tool's generic Activate
                                    tool:Activate()
                                end
                            end)
                        end
                    end
                end
                task.wait(cfg.farmDelay)
            end
            log("🌾 Auto Farm stopped", "WARN")
        end)
    end

    function BF_ESP.StopFarm()
        _farmRunning = false
        if _farmThread then task.cancel(_farmThread); _farmThread = nil end
    end

    -- ── Auto Collect Fruit ───────────────────────────────────────
    local _collectRunning = false

    function BF_ESP.StartCollect()
        _collectRunning = true
        log("🍎 Auto Collect Fruit started", "OK")
        task.spawn(function()
            while _collectRunning and cfg.autoCollect and cfg.enabled do
                local root = getRoot()
                if root then
                    local fruits = findFruits()
                    for _, fruit in ipairs(fruits) do
                        local rp = fruit.PrimaryPart or fruit:FindFirstChildOfClass("BasePart")
                        if rp then
                            local dist = (root.Position - rp.Position).Magnitude
                            if dist < 50 then
                                -- TP to pick up
                                root.CFrame = CFrame.new(rp.Position + Vector3.new(0,3,0))
                                task.wait(0.5)
                            elseif dist < 500 then
                                root.CFrame = CFrame.new(rp.Position + Vector3.new(0,3,0))
                                task.wait(0.3)
                            end
                        end
                    end
                end
                task.wait(2)
            end
        end)
    end

    function BF_ESP.StopCollect()
        _collectRunning = false
    end

    -- ── Sea Beast ESP ────────────────────────────────────────────
    function BF_ESP.UpdateSeaBeast()
        if not cfg.seaBeastESP or not cfg.enabled then
            clearDrawings(_seaDrawings); return
        end
        local root = getRoot(); if not root then return end
        local beasts = findSeaBeasts()
        local activeKeys = {}

        for _, b in ipairs(beasts) do
            local key = tostring(b.model)
            activeKeys[key] = true
            if not _seaDrawings[key] then
                _seaDrawings[key] = {
                    name = D.Text("", 16, Color3.fromRGB(0, 200, 255)),
                    dist = D.Text("", 12, Color3.fromRGB(255,100,100)),
                }
            end
            local sp, vis = U.W2S(b.root.Position + Vector3.new(0,5,0))
            local d = _seaDrawings[key]
            if not vis then d.name.Visible=false; d.dist.Visible=false; continue end
            local dist = (root.Position - b.root.Position).Magnitude
            d.name.Text     = "🌊 " .. b.model.Name
            d.name.Position = Vector2.new(sp.X, sp.Y - 20)
            d.name.Visible  = true
            d.dist.Text     = string.format("%.0fm ⚠️", dist)
            d.dist.Position = Vector2.new(sp.X, sp.Y)
            d.dist.Visible  = true
        end

        for key, d in pairs(_seaDrawings) do
            if not activeKeys[key] then
                for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
                _seaDrawings[key] = nil
            end
        end
    end

    -- ── Stat Auto-Allocate ───────────────────────────────────────
    function BF_ESP.AllocateStat()
        -- Try to find stat allocation RemoteFunction
        local remote = RS2:FindFirstChild("AddStat") or
                       RS2:FindFirstChild("AllocateStat") or
                       RS2:FindFirstChild("AddPoint")
        if remote and remote:IsA("RemoteFunction") then
            local statMap = {
                Melee="STR", Defense="DF", Sword="SWORD", Gun="GUN", Fruit="FRUIT",
                Blox="FRUIT", Devil="FRUIT"
            }
            local stat = statMap[cfg.targetStat] or cfg.targetStat
            pcall(function() remote:InvokeServer(stat) end)
            log("📊 Stat allocated: " .. cfg.targetStat, "OK")
        else
            log("Stat remote not found — check ReplicatedStorage", "WARN")
        end
    end

    -- ── Module Enable / Disable ──────────────────────────────────
    function BF_ESP.Enable()
        cfg.enabled = true
        log("✅ Blox Fruits module ENABLED", "OK")
    end

    function BF_ESP.Disable()
        cfg.enabled = false
        BF_ESP.StopFarm()
        BF_ESP.StopCollect()
        clearDrawings(_fruitDrawings)
        clearDrawings(_seaDrawings)
        log("⚠️ Blox Fruits module DISABLED", "WARN")
    end

    -- Master update — dipanggil tiap RenderStepped dari init
    function BF_ESP.Update()
        if not cfg.enabled then return end
        BF_ESP.Update_Fruit()  -- alias
        BF_ESP.UpdateSeaBeast()
    end
    BF_ESP.Update_Fruit = BF_ESP.Update  -- avoid infinite ref

    -- Overwrite Update untuk call keduanya
    function BF_ESP.Update()
        if not cfg.enabled then return end
        BF_ESP.Update_Fruit_inner()
        BF_ESP.UpdateSeaBeast()
    end
    -- Rename fruit update internal
    BF_ESP.Update_Fruit_inner = BF_ESP.Update
    -- Final single-entry update
    function BF_ESP.Update()
        if not cfg.enabled then return end
        -- Fruit ESP
        local root = getRoot(); if not root then return end
        local fruits = findFruits()
        local activeKeys = {}
        for _, fruit in ipairs(fruits) do
            local rp = fruit.PrimaryPart or fruit:FindFirstChild("HumanoidRootPart")
                     or fruit:FindFirstChildOfClass("BasePart")
            if not rp then continue end
            local dist = (root.Position - rp.Position).Magnitude
            if dist > cfg.fruitMaxDist then continue end
            local key = tostring(fruit)
            activeKeys[key] = true
            if not _fruitDrawings[key] then
                local col = FRUIT_COLORS[fruit.Name] or DEFAULT_FRUIT_COLOR
                _fruitDrawings[key] = {
                    name = D.Text("", 13, col),
                    dist = D.Text("", 11, Color3.fromRGB(220,220,100)),
                    line = D.Line(col, 1),
                }
            end
            local d = _fruitDrawings[key]
            local sp, vis = U.W2S(rp.Position + Vector3.new(0, 2, 0))
            if not vis then
                d.name.Visible=false; d.dist.Visible=false; d.line.Visible=false; continue
            end
            local vp = Core.Cam.ViewportSize
            d.name.Text="🍎 "..fruit.Name; d.name.Position=Vector2.new(sp.X,sp.Y-16); d.name.Visible=true
            d.dist.Text=string.format("%.0fm",dist); d.dist.Position=Vector2.new(sp.X,sp.Y); d.dist.Visible=true
            d.line.From=Vector2.new(vp.X/2,vp.Y/2); d.line.To=Vector2.new(sp.X,sp.Y); d.line.Visible=cfg.fruitESP
        end
        for key, d in pairs(_fruitDrawings) do
            if not activeKeys[key] then
                for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
                _fruitDrawings[key] = nil
            end
        end
        BF_ESP.UpdateSeaBeast()
    end

    Core.Register("BloxFruits", BF_ESP)
    log("📦 Blox Fruits module loaded", "DEV")
    return BF_ESP
end
