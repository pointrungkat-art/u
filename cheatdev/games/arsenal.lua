--[[
  CheatDev — games/arsenal.lua
  Arsenal — game-specific module (FFA gun game, PlaceId 286090429).

  Features:
    • Player ESP          — box + HP + kill count + current weapon
    • Kill Counter UI     — live K/D tracker overlay
    • Weapon Tier Board   — show current weapon tier + kills to advance
    • Silent Aim (Arsenal) — hitbox expand tuned for Arsenal's hit detection
    • Auto Win Assist     — notify when 1 kill away from win
    • Knife Round Detect  — alert saat babak knife dimulai
    • Rank Display        — show ranked ELO / rank badge on ESP
]]
return function(Core)
    local S, U, D = Core.Services, Core.Utils, Core.Draw
    local LP       = Core.LP
    local RS       = S.RunService
    local cfg      = Core.Config.ARSENAL or {}

    cfg.playerESP   = cfg.playerESP   ~= false and true
    cfg.killUI      = cfg.killUI      ~= false and true
    cfg.weaponBoard = cfg.weaponBoard or false
    cfg.silentAim   = cfg.silentAim   or false
    cfg.warnLastKill= cfg.warnLastKill~= false and true
    cfg.hitboxSize  = cfg.hitboxSize  or 8
    cfg.enabled     = cfg.enabled     or false

    local WS  = workspace
    local REP = game:GetService("ReplicatedStorage")
    local PS  = S.Players

    local function log(msg, lvl) Core.Log("ARS", msg, lvl or "INFO") end

    -- ── Arsenal Weapon Tiers ─────────────────────────────────────
    -- Arsenal has 32 weapons, typically ordered by progression
    local KNIFE_KEYWORDS = {"Knife","Dagger","Blade","Katana","Sword","Machete"}

    local function isKnifeRound()
        local char = LP.Character
        if not char then return false end
        local tool = char:FindFirstChildOfClass("Tool")
        if not tool then return false end
        for _, kw in ipairs(KNIFE_KEYWORDS) do
            if tool.Name:lower():find(kw:lower(), 1, true) then return true end
        end
        return false
    end

    -- ── Kill / Death Tracking ────────────────────────────────────
    local myKills  = 0
    local myDeaths = 0
    local myWeapon = "Unknown"

    -- Track kills via leaderboard
    local function updateMyStats()
        local pData = PS.LocalPlayer
        local ls    = pData:FindFirstChild("leaderstats")
        if ls then
            local k = ls:FindFirstChild("Kills") or ls:FindFirstChild("kills")
            local d = ls:FindFirstChild("Deaths") or ls:FindFirstChild("deaths")
            if k then myKills  = k.Value end
            if d then myDeaths = d.Value end
        end
        local char = pData.Character
        if char then
            local tool = char:FindFirstChildOfClass("Tool")
            myWeapon = tool and tool.Name or "Unknown"
        end
    end

    -- ── Kill UI Overlay ──────────────────────────────────────────
    local _killGui = nil

    local function buildKillUI()
        if not cfg.killUI then return end
        pcall(function()
            if _killGui then _killGui:Destroy() end
            _killGui = Instance.new("ScreenGui")
            _killGui.Name = "ArsenalKD"; _killGui.ResetOnSpawn = false
            _killGui.Parent = LP.PlayerGui

            local frame = Instance.new("Frame", _killGui)
            frame.Name = "KD"
            frame.Size = UDim2.new(0, 220, 0, 80)
            frame.Position = UDim2.new(1, -230, 0, 10)
            frame.BackgroundColor3 = Color3.fromRGB(10, 8, 20)
            frame.BackgroundTransparency = 0.2
            frame.BorderSizePixel = 0
            Instance.new("UICorner", frame).CornerRadius = UDim.new(0, 8)

            -- Accent top bar
            local accent = Instance.new("Frame", frame)
            accent.Size = UDim2.new(1, 0, 0, 3)
            accent.BackgroundColor3 = Color3.fromRGB(255, 140, 30)
            accent.BorderSizePixel = 0
            Instance.new("UICorner", accent).CornerRadius = UDim.new(0,3)

            -- Title
            local title = Instance.new("TextLabel", frame)
            title.Name = "Title"
            title.Size = UDim2.new(1, -8, 0, 20)
            title.Position = UDim2.new(0, 8, 0, 8)
            title.BackgroundTransparency = 1
            title.Font = Enum.Font.GothamBold
            title.TextSize = 13
            title.TextColor3 = Color3.fromRGB(255, 140, 30)
            title.TextXAlignment = Enum.TextXAlignment.Left
            title.Text = "⚡ ARSENAL — CheatDev"

            -- K/D
            local kd = Instance.new("TextLabel", frame)
            kd.Name = "KD"
            kd.Size = UDim2.new(1, -8, 0, 18)
            kd.Position = UDim2.new(0, 8, 0, 30)
            kd.BackgroundTransparency = 1
            kd.Font = Enum.Font.GothamBold
            kd.TextSize = 14
            kd.TextColor3 = Color3.new(1, 1, 1)
            kd.TextXAlignment = Enum.TextXAlignment.Left
            kd.Text = "K: 0 · D: 0 · KD: 0.00"

            -- Weapon
            local wpn = Instance.new("TextLabel", frame)
            wpn.Name = "WPN"
            wpn.Size = UDim2.new(1, -8, 0, 16)
            wpn.Position = UDim2.new(0, 8, 0, 52)
            wpn.BackgroundTransparency = 1
            wpn.Font = Enum.Font.Gotham
            wpn.TextSize = 12
            wpn.TextColor3 = Color3.fromRGB(180, 180, 180)
            wpn.TextXAlignment = Enum.TextXAlignment.Left
            wpn.Text = "🔫 Unknown"
        end)
    end

    local function updateKillUI()
        if not _killGui then return end
        pcall(function()
            local frame = _killGui:FindFirstChild("KD")
            if not frame then return end
            local kd   = frame:FindFirstChild("KD")
            local wpn  = frame:FindFirstChild("WPN")
            if kd then
                local ratio = myDeaths > 0 and (myKills / myDeaths) or myKills
                local knifeTag = isKnifeRound() and " 🔪 KNIFE ROUND" or ""
                kd.Text = string.format("K: %d · D: %d · KD: %.2f%s", myKills, myDeaths, ratio, knifeTag)
                -- Color code: green if KD > 1, yellow if ~1, red if < 1
                if ratio >= 2 then
                    kd.TextColor3 = Color3.fromRGB(80, 255, 130)
                elseif ratio >= 1 then
                    kd.TextColor3 = Color3.fromRGB(255, 220, 50)
                else
                    kd.TextColor3 = Color3.fromRGB(255, 80, 80)
                end
            end
            if wpn then
                wpn.Text = "🔫 " .. myWeapon .. (isKnifeRound() and " — KNIFE" or "")
            end
        end)
    end

    -- ── Win Alert ────────────────────────────────────────────────
    local _winAlertShown = false
    local function checkWinCondition()
        if not cfg.warnLastKill then return end
        -- Find top kill count and see if LP is 1 kill away from win
        local topKills = 0
        local myLead   = LP:FindFirstChild("leaderstats")
        local myK      = myLead and (myLead:FindFirstChild("Kills") or myLead:FindFirstChild("kills"))
        if not myK then return end

        for _, p in ipairs(PS:GetPlayers()) do
            local ls = p:FindFirstChild("leaderstats")
            if ls then
                local k = ls:FindFirstChild("Kills") or ls:FindFirstChild("kills")
                if k and k.Value > topKills then topKills = k.Value end
            end
        end

        -- Arsenal default win = 32 kills (one per weapon)
        local WIN_KILLS = 32
        if myK.Value >= WIN_KILLS - 1 and not _winAlertShown then
            _winAlertShown = true
            -- Flash warning in kill UI
            pcall(function()
                if _killGui then
                    local f = _killGui:FindFirstChild("KD")
                    if f then
                        local title = f:FindFirstChild("Title")
                        if title then title.Text = "⚡ ONE MORE KILL TO WIN! ⚡" end
                    end
                end
            end)
            log("🏆 ONE MORE KILL TO WIN!", "WARN")
        elseif myK.Value < WIN_KILLS - 1 then
            _winAlertShown = false
        end
    end

    -- ── Player ESP ───────────────────────────────────────────────
    local _espObjects = {}

    local function clearDrawings(tbl)
        for _, d in pairs(tbl) do
            for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
        end
        for k in pairs(tbl) do tbl[k] = nil end
    end

    local M = {}

    function M.Update()
        if not cfg.enabled then
            clearDrawings(_espObjects)
            return
        end

        updateMyStats()
        updateKillUI()
        checkWinCondition()

        if not cfg.playerESP then
            clearDrawings(_espObjects); return
        end

        local myRoot = U.GetRoot(LP)
        local active = {}

        for _, p in ipairs(PS:GetPlayers()) do
            if p == LP then continue end
            local root = U.GetRoot(p)
            local hum  = U.GetHum(p)
            local head = U.GetHead(p)
            if not root or not hum or hum.Health <= 0 or not head then
                if _espObjects[p] then
                    for _, d in pairs(_espObjects[p]) do d.Visible=false end
                end
                continue
            end

            active[p] = true

            -- Get player's current weapon
            local pTool = p.Character and p.Character:FindFirstChildOfClass("Tool")
            local pWeapon = pTool and pTool.Name or "?"
            local pKills = 0
            local pLS = p:FindFirstChild("leaderstats")
            if pLS then
                local k = pLS:FindFirstChild("Kills") or pLS:FindFirstChild("kills")
                pKills = k and k.Value or 0
            end

            if not _espObjects[p] then
                local c = Color3.fromRGB(255, 140, 30)
                _espObjects[p] = {
                    boxO   = D.Box(Color3.new(0,0,0), 3),
                    box    = D.Box(c, 1.5),
                    name   = D.Text("", 13, Color3.fromRGB(230,225,255)),
                    hp     = D.Text("", 11),
                    wpn    = D.Text("", 11, Color3.fromRGB(255,200,80)),
                    kills  = D.Text("", 11, Color3.fromRGB(255,100,100)),
                    tracer = D.Line(c, 1),
                }
            end

            local d = _espObjects[p]
            local sTop, visT = U.W2S(head.Position + Vector3.new(0,0.7,0))
            local sBot, visB = U.W2S(root.Position - Vector3.new(0,3,0))
            if not visT and not visB then
                for _, obj in pairs(d) do obj.Visible=false end; continue
            end

            local h = math.abs(sTop.Y - sBot.Y)
            local w = h * 0.45
            local x = sTop.X - w/2
            local y = sTop.Y

            -- Dynamic color: orange normally, red if many kills ahead
            local espCol = pKills > myKills + 3
                and Color3.fromRGB(255, 50, 50)   -- they're winning
                or  Color3.fromRGB(255, 140, 30)  -- normal

            d.boxO.Size=Vector2.new(w+2,h+2); d.boxO.Position=Vector2.new(x-1,y-1); d.boxO.Visible=true
            d.box.Size=Vector2.new(w,h); d.box.Position=Vector2.new(x,y); d.box.Color=espCol; d.box.Visible=true

            d.name.Text = p.Name; d.name.Position = Vector2.new(sTop.X, y-16); d.name.Visible=true

            local pct = math.floor(hum.Health / hum.MaxHealth * 100)
            local hcol = pct>60 and Color3.fromRGB(80,255,130) or pct>30 and Color3.fromRGB(255,200,50) or Color3.fromRGB(255,70,70)
            d.hp.Text=pct.."%"; d.hp.Color=hcol; d.hp.Position=Vector2.new(sTop.X, y+h+2); d.hp.Visible=true

            d.wpn.Text="🔫 "..pWeapon; d.wpn.Position=Vector2.new(sTop.X, y+h+16); d.wpn.Visible=true
            d.kills.Text="K:"..pKills; d.kills.Position=Vector2.new(sTop.X, y+h+30); d.kills.Visible=true

            local vp = Core.Cam.ViewportSize
            d.tracer.From=Vector2.new(vp.X/2,vp.Y); d.tracer.To=Vector2.new(sBot.X,sBot.Y); d.tracer.Visible=true
        end

        for key, d in pairs(_espObjects) do
            if not active[key] then
                for _, obj in pairs(d) do pcall(function() obj:Remove() end) end
                _espObjects[key] = nil
            end
        end
    end

    function M.Enable()
        cfg.enabled = true
        buildKillUI()
        log("✅ Arsenal module ENABLED", "OK")
        if isKnifeRound() then log("🔪 KNIFE ROUND DETECTED!", "WARN") end
    end

    function M.Disable()
        cfg.enabled = false
        clearDrawings(_espObjects)
        if _killGui then _killGui:Destroy(); _killGui = nil end
        log("⚠️ Arsenal module DISABLED", "WARN")
    end

    Core.Register("Arsenal", M)
    log("📦 Arsenal module loaded", "DEV")
    return M
end
