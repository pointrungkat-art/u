--[[  CheatDev — modules/visual.lua
      Radar minimap, Crosshair dev-style, Wallhack (X-Ray), FPS Boost
--]]
return function(Core)
    local S, U, D = Core.Services, Core.Utils, Core.Draw
    local RS   = S.RunService
    local LP   = Core.LP
    local Cam  = Core.Cam
    local cfgR  = Core.Config.RADAR
    local cfgCH = Core.Config.CROSSHAIR
    local cfgFP = Core.Config.FPS

    -- ── RADAR MINIMAP ────────────────────────────────────────────
    local RadarModule = {}
    local _rBG, _rBorder, _rDot, _rLabel
    local _rPlayerDots = {}

    local function radarInit()
        local sz = cfgR.size
        local vp = Cam.ViewportSize
        local rx  = vp.X * cfgR.posX - sz/2
        local ry  = vp.Y * cfgR.posY - sz/2
        _rBG = Drawing.new("Square")
        _rBG.Size     = Vector2.new(sz, sz)
        _rBG.Position = Vector2.new(rx, ry)
        _rBG.Color    = Color3.fromRGB(8,6,18)
        _rBG.Transparency = 0.35
        _rBG.Filled   = true
        _rBG.Visible  = false
        _rBorder = Drawing.new("Square")
        _rBorder.Size      = Vector2.new(sz+2, sz+2)
        _rBorder.Position  = Vector2.new(rx-1, ry-1)
        _rBorder.Color     = Color3.fromRGB(180,80,255)
        _rBorder.Thickness = 1.5
        _rBorder.Filled    = false
        _rBorder.Visible   = false
        -- Self dot
        _rDot = Drawing.new("Circle")
        _rDot.Radius  = 4
        _rDot.Color   = Color3.fromRGB(80,255,130)
        _rDot.Filled  = true
        _rDot.Visible = false
        _rDot.Position = Vector2.new(rx + sz/2, ry + sz/2)
        _rLabel = D.Text("RADAR", 10, Color3.fromRGB(180,80,255))
        _rLabel.Position = Vector2.new(rx + sz/2, ry - 14)
        _rLabel.Visible  = false
    end
    radarInit()

    function RadarModule.Update()
        local sz = cfgR.size
        local vp = Cam.ViewportSize
        local rx = vp.X * cfgR.posX - sz/2
        local ry = vp.Y * cfgR.posY - sz/2
        local show = cfgR.enabled
        _rBG.Visible     = show
        _rBorder.Visible = show
        _rDot.Visible    = show
        _rLabel.Visible  = show
        _rBG.Position    = Vector2.new(rx, ry)
        _rBorder.Position = Vector2.new(rx-1, ry-1)
        _rDot.Position   = Vector2.new(rx + sz/2, ry + sz/2)
        _rLabel.Position = Vector2.new(rx + sz/2, ry - 14)
        for _, d in pairs(_rPlayerDots) do d.Visible = false end
        if not show then return end
        local myRoot = U.GetRoot()
        if not myRoot then return end
        local myCF   = myRoot.CFrame
        local half   = sz / 2
        local scale  = half / cfgR.range
        for _, p in ipairs(S.Players:GetPlayers()) do
            if p == LP then continue end
            local pRoot = U.GetRoot(p)
            if not pRoot then continue end
            local rel = myCF:PointToObjectSpace(pRoot.Position)
            local dx  = rel.X * scale
            local dz  = -rel.Z * scale
            if math.abs(dx) > half or math.abs(dz) > half then continue end
            local dot = _rPlayerDots[p]
            if not dot then
                dot = Drawing.new("Circle")
                dot.Radius  = cfgR.dotSize
                dot.Filled  = true
                dot.Visible = false
                _rPlayerDots[p] = dot
            end
            dot.Color    = U.IsEnemy(p) and Color3.fromRGB(255,70,70)
                                         or Color3.fromRGB(80,200,255)
            dot.Position = Vector2.new(rx + half + dx, ry + half + dz)
            dot.Visible  = true
        end
    end
    function RadarModule.Disable()
        cfgR.enabled = false
        _rBG.Visible = false; _rBorder.Visible = false
        _rDot.Visible = false; _rLabel.Visible = false
        for _, d in pairs(_rPlayerDots) do d.Visible = false end
    end
    S.Players.PlayerRemoving:Connect(function(p)
        if _rPlayerDots[p] then
            pcall(function() _rPlayerDots[p]:Remove() end)
            _rPlayerDots[p] = nil
        end
    end)

    -- ── CROSSHAIR DEV ────────────────────────────────────────────
    local CrossModule = {}
    local _ch = {}
    local function buildCross()
        for _, d in pairs(_ch) do pcall(function() d:Remove() end) end
        _ch = {}
        local vp     = Cam.ViewportSize
        local cx, cy = vp.X/2, vp.Y/2
        local col    = U.Color(table.unpack(cfgCH.color))
        local sz     = cfgCH.size
        local style  = cfgCH.style
        if style == "Cross" or style == "CrossDot" or style == "TShape" or style == "Dev" then
            local top = D.Line(col, 2); top.From = Vector2.new(cx, cy-sz); top.To = Vector2.new(cx, cy-(style=="TShape" and sz/2 or -1)); top.Visible = cfgCH.enabled; table.insert(_ch, top)
            local bot = D.Line(col, 2); bot.From = Vector2.new(cx, cy+sz); bot.To = Vector2.new(cx, cy+1); bot.Visible = cfgCH.enabled and style ~= "TShape"; table.insert(_ch, bot)
            local lft = D.Line(col, 2); lft.From = Vector2.new(cx-sz, cy); lft.To = Vector2.new(cx-1, cy); lft.Visible = cfgCH.enabled; table.insert(_ch, lft)
            local rgt = D.Line(col, 2); rgt.From = Vector2.new(cx+sz, cy); rgt.To = Vector2.new(cx+1, cy); rgt.Visible = cfgCH.enabled; table.insert(_ch, rgt)
        end
        if style == "CrossDot" or style == "Dot" or style == "Dev" then
            local dot = D.Circle(2, col, 1, true); dot.Position = Vector2.new(cx, cy); dot.Visible = cfgCH.enabled; table.insert(_ch, dot)
        end
        if style == "Circle" or style == "Dev" then
            local ring = D.Circle(sz, col, 1.5); ring.Position = Vector2.new(cx, cy); ring.Visible = cfgCH.enabled; table.insert(_ch, ring)
        end
        if style == "Dev" then
            -- corner brackets
            local function bracket(ox, oy, dx, dy)
                local b1 = D.Line(col, 2); b1.From = Vector2.new(cx+ox, cy+oy); b1.To = Vector2.new(cx+ox+dx*6, cy+oy); b1.Visible = cfgCH.enabled; table.insert(_ch, b1)
                local b2 = D.Line(col, 2); b2.From = Vector2.new(cx+ox, cy+oy); b2.To = Vector2.new(cx+ox, cy+oy+dy*6); b2.Visible = cfgCH.enabled; table.insert(_ch, b2)
            end
            local s = sz + 4
            bracket(-s,-s, 1, 1); bracket(s,-s,-1, 1)
            bracket(-s, s, 1,-1); bracket(s, s,-1,-1)
        end
    end
    function CrossModule.Enable()
        cfgCH.enabled = true
        buildCross()
        Core.Log("CROSS", "🎯 Crosshair ON — style:"..cfgCH.style, "OK")
    end
    function CrossModule.Disable()
        cfgCH.enabled = false
        for _, d in pairs(_ch) do d.Visible = false end
        Core.Log("CROSS", "Crosshair OFF", "INFO")
    end
    function CrossModule.Toggle()
        if cfgCH.enabled then CrossModule.Disable() else CrossModule.Enable() end
    end
    function CrossModule.SetStyle(s)
        cfgCH.style = s
        buildCross()
    end

    -- ── WALLHACK / X-RAY ─────────────────────────────────────────
    local WallhackModule = {}
    local _whConn, _wh_originals = nil, {}
    function WallhackModule.Enable()
        _whConn = RS.Heartbeat:Connect(function()
            for _, obj in ipairs(workspace:GetDescendants()) do
                if obj:IsA("BasePart") and not obj.Name:find("HumanoidRootPart")
                    and not obj.Name:find("Head") and not obj.Name:find("Torso") then
                    if not _wh_originals[obj] then
                        _wh_originals[obj] = obj.LocalTransparencyModifier
                    end
                    obj.LocalTransparencyModifier = 0.85
                end
            end
        end)
        Core.Log("WALLHACK", "👁️ X-Ray ON — walls transparent", "OK")
    end
    function WallhackModule.Disable()
        if _whConn then _whConn:Disconnect(); _whConn = nil end
        for obj, orig in pairs(_wh_originals) do
            pcall(function() obj.LocalTransparencyModifier = orig end)
        end
        _wh_originals = {}
        Core.Log("WALLHACK", "X-Ray OFF", "INFO")
    end
    function WallhackModule.Toggle()
        if _whConn then WallhackModule.Disable() else WallhackModule.Enable() end
    end

    -- ── FPS BOOST ────────────────────────────────────────────────
    local FPSModule = {}
    function FPSModule.Apply()
        cfgFP.enabled = true
        local L = S.Lighting
        L.GlobalShadows = false
        L.FogEnd        = 100000
        L.Ambient       = Color3.new(1,1,1)
        L.OutdoorAmbient= Color3.new(1,1,1)
        for _, e in ipairs(L:GetChildren()) do
            if e:IsA("BlurEffect") or e:IsA("SunRaysEffect")
            or e:IsA("ColorCorrectionEffect") or e:IsA("BloomEffect") then
                e.Enabled = false
            end
        end
        if cfgFP.stripParticles then
            for _, o in ipairs(workspace:GetDescendants()) do
                if o:IsA("ParticleEmitter") or o:IsA("Smoke")
                or o:IsA("Fire") or o:IsA("Sparkles") then
                    o.Enabled = false
                end
            end
        end
        if cfgFP.stripDecals then
            for _, o in ipairs(workspace:GetDescendants()) do
                if o:IsA("Decal") or o:IsA("Texture") then
                    o.Transparency = 1
                end
            end
        end
        Core.Log("FPS", "⚡ FPS Boost applied — stripped all effects", "OK")
    end
    function FPSModule.Disable() cfgFP.enabled = false end

    Core.Register("Radar",    RadarModule)
    Core.Register("Crosshair",CrossModule)
    Core.Register("Wallhack", WallhackModule)
    Core.Register("FPS",      FPSModule)

    return {
        Radar=RadarModule, Cross=CrossModule,
        Wallhack=WallhackModule, FPS=FPSModule,
    }
end
