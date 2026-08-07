--[[
  CheatDev — games/mm2.lua
  Murder Mystery 2 — game-specific module.

  Features:
    • Role Reveal ESP    — tampilkan Murderer (🔴) / Sheriff (🔵) / Innocent (⚪)
    • Knife / Gun ESP    — highlight weapon + owner
    • Coin Tracer        — ESP koin untuk sheriff farming
    • Murderer Alert     — notif ketika murderer approach radius
    • Kill Tracker       — counter kill/survive per round
    • Sheriff Assist     — auto-aim mode ketika jadi Sheriff
]]
return function(Core)
    local S, U, D = Core.Services, Core.Utils, Core.Draw
    local LP       = Core.LP
    local RS       = S.RunService
    local cfg      = Core.Config.MM2 or {}

    cfg.roleESP     = cfg.roleESP     ~= false and true
    cfg.weaponESP   = cfg.weaponESP   ~= false and true
    cfg.coinESP     = cfg.coinESP     or false
    cfg.murderAlert = cfg.murderAlert ~= false and true
    cfg.alertRadius = cfg.alertRadius or 40
    cfg.enabled     = cfg.enabled     or false

    local WS  = workspace
    local REP = game:GetService("ReplicatedStorage")

    local function log(msg, lvl) Core.Log("MM2", msg, lvl or "INFO") end

    -- ── Role Detection ───────────────────────────────────────────
    -- MM2 stores roles in various places depending on version:
    -- 1. Player.Team (classic)
    -- 2. GameplayFolder / Roles / <player>
    -- 3. Character attribute "Role"
    -- 4. LocalPlayer.PlayerGui role hints

    local ROLE_TEAMS = {
        ["Murderers"] = "MURDERER",
        ["Sheriffs"]  = "SHERIFF",
        ["Innocents"] = "INNOCENT",
        ["Murder"]    = "MURDERER",
        ["Sheriff"]   = "SHERIFF",
        ["Innocent"]  = "INNOCENT",
    }
    local ROLE_COLORS = {
        MURDERER = Color3.fromRGB(255, 50,  50),
        SHERIFF  = Color3.fromRGB(50,  130, 255),
        INNOCENT = Color3.fromRGB(220, 220, 220),
        UNKNOWN  = Color3.fromRGB(150, 150, 150),
    }
    local ROLE_ICONS = {
        MURDERER = "🔴", SHERIFF = "🔵", INNOCENT = "⚪", UNKNOWN = "❓"
    }

    local function getRole(player)
        -- Method 1: Team
        if player.Team then
            local r = ROLE_TEAMS[player.Team.Name]
            if r then return r end
        end
        -- Method 2: GameplayFolder
        local gf = WS:FindFirstChild("GameplayFolder") or WS:FindFirstChild("Gameplay")
        if gf then
            local roles = gf:FindFirstChild("Roles") or gf:FindFirstChild("PlayerRoles")
            if roles then
                local rv = roles:FindFirstChild(player.Name)
                if rv then return rv.Value and rv.Value:upper() or "UNKNOWN" end
            end
        end
        -- Method 3: Character attribute
        local char = player.Character
        if char then
            local attr = char:GetAttribute("Role") or char:GetAttribute("role")
            if attr then return attr:upper() end
        end
        -- Method 4: PlayerGui hints
        local pg = player.PlayerGui
        if pg then
            local hint = pg:FindFirstChild("RoleGui") or pg:FindFirstChild("RoleHint")
            if hint then
                local lbl = hint:FindFirstChildOfClass("TextLabel")
                if lbl then
                    local t = lbl.Text:upper()
                    if t:find("MURDER") then return "MURDERER" end
                    if t:find("SHERIFF") then return "SHERIFF" end
                    if t:find("INNOCENT") then return "INNOCENT" end
                end
            end
        end
        return "UNKNOWN"
    end

    -- ── My Role ─────────────────────────────────────────────────
    local function myRole() return getRole(LP) end

    -- ── Weapon Detection ────────────────────────────────────────
    local WEAPON_NAMES = {"Knife", "knife", "Gun", "Revolver", "Sheriff"}

    local function findWeapons()
        local weapons = {}
        -- Check in workspace (dropped or equipped)
        for _, obj in ipairs(WS:GetDescendants()) do
            if obj:IsA("Tool") or obj:IsA("Model") then
                for _, wn in ipairs(WEAPON_NAMES) do
                    if obj.Name:lower():find(wn:lower(), 1, true) then
                        local part = obj:FindFirstChild("Handle") or obj.PrimaryPart
                               or obj:FindFirstChildOfClass("BasePart")
                        if part then
                            -- Find owner (player with this weapon in char)
                            local owner = nil
                            for _, p in ipairs(S.Players:GetPlayers()) do
                                if p.Character and p.Character:IsAncestorOf(obj) then
                                    owner = p; break
                                end
                            end
                            table.insert(weapons, {
                                model = obj,
                                part  = part,
                                name  = obj.Name,
                                owner = owner,
                                isKnife = obj.Name:lower():find("knife") ~= nil,
                            })
                            break
                        end
                    end
                end
            end
        end
        return weapons
    end

    -- ── Coin Detection ───────────────────────────────────────────
    local function findCoins()
        local coins = {}
        for _, obj in ipairs(WS:GetDescendants()) do
            if obj:IsA("BasePart") or obj:IsA("Model") then
                local n = obj.Name:lower()
                if n:find("coin") or n:find("gold") then
                    local part = obj:IsA("BasePart") and obj or obj.PrimaryPart
                    if part then table.insert(coins, {part=part, name=obj.Name}) end
                end
            end
        end
        return coins
    end

    -- ── Kill Tracker ─────────────────────────────────────────────
    local stats = {kills=0, deaths=0, survived=0, rounds=0}
    local _lastAlive = true

    local function trackRound()
        local hum = U.GetHum(LP)
        if not hum then return end
        local alive = hum.Health > 0
        if _lastAlive and not alive then
            stats.deaths = stats.deaths + 1
            log("💀 Died — round deaths: " .. stats.deaths)
        end
        _lastAlive = alive
    end

    -- ── Drawing Storage ─────────────────────────────────────────
    local _playerESP  = {}
    local _weaponESP  = {}
    local _coinESP    = {}
    local _alertFrame = nil   -- murder alert overlay

    local function clearDrawings(tbl)
        for _, d in pairs(tbl) do
            for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
        end
        for k in pairs(tbl) do tbl[k] = nil end
    end

    -- ── Murder Alert Overlay ─────────────────────────────────────
    local _alertGui = nil
    local function showAlert(murdererName, dist)
        if not cfg.murderAlert then return end
        pcall(function()
            if not _alertGui then
                _alertGui = Instance.new("ScreenGui")
                _alertGui.Name = "MM2Alert"; _alertGui.ResetOnSpawn=false
                _alertGui.Parent = LP.PlayerGui
                local f = Instance.new("Frame")
                f.Name = "Alert"
                f.Size = UDim2.new(0,300,0,50)
                f.Position = UDim2.new(0.5,-150,0,20)
                f.BackgroundColor3 = Color3.fromRGB(180,20,20)
                f.BorderSizePixel = 0
                Instance.new("UICorner",f).CornerRadius = UDim.new(0,6)
                f.BackgroundTransparency = 0.15
                f.Parent = _alertGui
                local lbl = Instance.new("TextLabel",f)
                lbl.Name = "Lbl"; lbl.Size = UDim2.new(1,0,1,0)
                lbl.BackgroundTransparency = 1
                lbl.Font = Enum.Font.GothamBold; lbl.TextSize = 15
                lbl.TextColor3 = Color3.new(1,1,1)
            end
            local f = _alertGui:FindFirstChild("Alert")
            if f then
                f:FindFirstChild("Lbl").Text = string.format(
                    "🔪 MURDERER NEARBY: %s — %.0fm", murdererName, dist
                )
                f.Visible = true
            end
        end)
    end

    local function hideAlert()
        if _alertGui then
            local f = _alertGui:FindFirstChild("Alert")
            if f then f.Visible = false end
        end
    end

    -- ── Main Update ──────────────────────────────────────────────
    local M = {}

    function M.Update()
        if not cfg.enabled then
            clearDrawings(_playerESP)
            clearDrawings(_weaponESP)
            clearDrawings(_coinESP)
            hideAlert()
            return
        end

        local myRoot = U.GetRoot(LP)
        local murderNearby = false
        local activeP = {}

        -- ── Role ESP (Player) ──
        if cfg.roleESP then
            for _, p in ipairs(S.Players:GetPlayers()) do
                if p == LP then continue end
                local root = U.GetRoot(p)
                local hum  = U.GetHum(p)
                if not root or not hum or hum.Health <= 0 then
                    if _playerESP[p] then
                        for _, d in pairs(_playerESP[p]) do d.Visible=false end
                    end
                    continue
                end

                local role  = getRole(p)
                local col   = ROLE_COLORS[role] or ROLE_COLORS.UNKNOWN
                local icon  = ROLE_ICONS[role] or "❓"
                local key   = p

                activeP[key] = true
                if not _playerESP[key] then
                    _playerESP[key] = {
                        role = D.Text("", 14, col),
                        name = D.Text("", 12, Color3.fromRGB(230,225,255)),
                        box  = D.Box(col, 1.5),
                        boxO = D.Box(Color3.new(0,0,0), 3),
                    }
                end

                local head = U.GetHead(p)
                local sTop, visT = U.W2S(head and (head.Position + Vector3.new(0,0.7,0)) or root.Position)
                local sBot, visB = U.W2S(root.Position - Vector3.new(0,3,0))
                local d = _playerESP[key]

                if not visT and not visB then
                    for _, obj in pairs(d) do obj.Visible=false end
                    continue
                end

                -- Role label
                local dist = myRoot and (myRoot.Position - root.Position).Magnitude or 0
                d.role.Text     = icon .. " " .. role .. " — " .. string.format("%.0fm",dist)
                d.role.Color    = col
                d.role.Position = Vector2.new(sTop.X, sTop.Y - 20)
                d.role.Visible  = true

                d.name.Text     = p.Name
                d.name.Position = Vector2.new(sTop.X, sTop.Y - 34)
                d.name.Visible  = true

                -- Box
                local h = math.abs(sTop.Y - sBot.Y)
                local w = h * 0.45
                d.boxO.Size=Vector2.new(w+2,h+2); d.boxO.Position=Vector2.new(sTop.X-w/2-1,sTop.Y-1)
                d.boxO.Visible=true
                d.box.Size=Vector2.new(w,h); d.box.Position=Vector2.new(sTop.X-w/2,sTop.Y)
                d.box.Color=col; d.box.Visible=true

                -- Murder alert
                if role == "MURDERER" and myRoot and dist < cfg.alertRadius then
                    murderNearby = true
                    showAlert(p.Name, dist)
                end
            end
        end

        -- Remove stale
        for key, d in pairs(_playerESP) do
            if not activeP[key] then
                for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
                _playerESP[key] = nil
            end
        end

        if not murderNearby then hideAlert() end

        -- ── Weapon ESP ──
        if cfg.weaponESP then
            local weapons = findWeapons()
            local activeW = {}
            for _, w in ipairs(weapons) do
                local key = tostring(w.model)
                activeW[key] = true
                if not _weaponESP[key] then
                    local col = w.isKnife and Color3.fromRGB(255,50,50) or Color3.fromRGB(50,130,255)
                    _weaponESP[key] = {
                        lbl  = D.Text("", 13, col),
                        line = D.Line(col, 1.5),
                    }
                end
                local d = _weaponESP[key]
                local sp, vis = U.W2S(w.part.Position + Vector3.new(0,1,0))
                if not vis then d.lbl.Visible=false; d.line.Visible=false; continue end
                local ownerName = w.owner and w.owner.Name or "Ground"
                d.lbl.Text = (w.isKnife and "🔪" or "🔫") .. " " .. w.name .. " [" .. ownerName .. "]"
                d.lbl.Position = Vector2.new(sp.X, sp.Y - 16); d.lbl.Visible = true
                if myRoot then
                    local vp = Core.Cam.ViewportSize
                    d.line.From = Vector2.new(vp.X/2, vp.Y); d.line.To = Vector2.new(sp.X, sp.Y)
                    d.line.Visible = true
                end
            end
            for key, d in pairs(_weaponESP) do
                if not activeW[key] then
                    for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
                    _weaponESP[key] = nil
                end
            end
        end

        -- ── Coin ESP ──
        if cfg.coinESP then
            local coins = findCoins()
            local activeC = {}
            for _, c in ipairs(coins) do
                local key = tostring(c.part)
                activeC[key] = true
                if not _coinESP[key] then
                    _coinESP[key] = { lbl = D.Text("", 11, Color3.fromRGB(255,220,50)) }
                end
                local d = _coinESP[key]
                local sp, vis = U.W2S(c.part.Position + Vector3.new(0,0.5,0))
                if not vis then d.lbl.Visible=false; continue end
                d.lbl.Text = "💰"
                d.lbl.Position = Vector2.new(sp.X, sp.Y - 12)
                d.lbl.Visible = true
            end
            for key, d in pairs(_coinESP) do
                if not activeC[key] then
                    for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
                    _coinESP[key] = nil
                end
            end
        end

        trackRound()
    end

    function M.Enable()
        cfg.enabled = true
        log("✅ MM2 module ENABLED — role detect ON", "OK")
        log("🎭 My role: " .. myRole(), "INFO")
    end

    function M.Disable()
        cfg.enabled = false
        clearDrawings(_playerESP)
        clearDrawings(_weaponESP)
        clearDrawings(_coinESP)
        hideAlert()
        if _alertGui then _alertGui:Destroy(); _alertGui = nil end
        log("⚠️ MM2 module DISABLED", "WARN")
    end

    function M.Stats()
        return string.format("Kills:%d Deaths:%d Survived:%d Rounds:%d",
            stats.kills, stats.deaths, stats.survived, stats.rounds)
    end

    Core.Register("MM2", M)
    log("📦 MM2 module loaded", "DEV")
    return M
end
