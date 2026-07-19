--[[  CheatDev — modules/esp.lua  ]]
return function(Core)
    local S, U, D = Core.Services, Core.Utils, Core.Draw
    local cfg      = Core.Config.ESP
    local LP       = Core.LP
    local _objs    = {}

    local function create(p)
        _objs[p] = {
            boxOut = D.Box(Color3.new(0,0,0), 3),
            box    = D.Box(U.Color(table.unpack(cfg.boxColor)), 1.5),
            name   = D.Text("", 13, U.Color(table.unpack(cfg.nameColor))),
            hp     = D.Text("", 12),
            dist   = D.Text("", 11, U.Color(120,115,155)),
            tracer = D.Line(U.Color(table.unpack(cfg.tracerColor)), 1.5),
        }
    end
    local function remove(p)
        if _objs[p] then
            for _, d in pairs(_objs[p]) do pcall(function() d:Remove() end) end
            _objs[p] = nil
        end
    end

    S.Players.PlayerAdded:Connect(create)
    S.Players.PlayerRemoving:Connect(remove)
    for _, p in ipairs(S.Players:GetPlayers()) do
        if p ~= LP then create(p) end
    end

    local M = {}
    function M.Update()
        for _, p in ipairs(S.Players:GetPlayers()) do
            if p == LP then continue end
            local o = _objs[p]
            if not o then continue end
            if not cfg.enabled then
                for _, d in pairs(o) do d.Visible = false end
                continue
            end
            local root = U.GetRoot(p)
            local head = U.GetHead(p)
            local hum  = U.GetHum(p)
            if not root or not head or not hum or not U.IsAlive(p) then
                for _, d in pairs(o) do d.Visible = false end
                continue
            end
            local dist = U.Dist(U.GetRoot(LP) or root, root)
            if dist > cfg.maxDist then
                for _, d in pairs(o) do d.Visible = false end
                continue
            end
            local sTop, visT = U.W2S(head.Position + Vector3.new(0,0.7,0))
            local sBot, visB = U.W2S(root.Position - Vector3.new(0,3,0))
            if not visT and not visB then
                for _, d in pairs(o) do d.Visible = false end
                continue
            end
            local h = math.abs(sTop.Y - sBot.Y)
            local w = h * 0.45
            local x = sTop.X - w/2
            local y = sTop.Y
            o.boxOut.Size     = Vector2.new(w+2, h+2)
            o.boxOut.Position = Vector2.new(x-1, y-1)
            o.boxOut.Visible  = cfg.showBox
            o.box.Size        = Vector2.new(w, h)
            o.box.Position    = Vector2.new(x, y)
            o.box.Color       = U.Color(table.unpack(cfg.boxColor))
            o.box.Visible     = cfg.showBox
            o.name.Text       = p.Name
            o.name.Position   = Vector2.new(sTop.X, y - 16)
            o.name.Visible    = cfg.showName
            local pct  = math.floor(hum.Health / hum.MaxHealth * 100)
            local hcol = pct > 60 and U.Color(table.unpack(cfg.hpColorHigh))
                      or pct > 30 and U.Color(table.unpack(cfg.hpColorMid))
                      or              U.Color(table.unpack(cfg.hpColorLow))
            o.hp.Text     = pct.."%"
            o.hp.Color    = hcol
            o.hp.Position = Vector2.new(sTop.X, y + h + 2)
            o.hp.Visible  = cfg.showHP
            o.dist.Text     = string.format("%.0fm", dist)
            o.dist.Position = Vector2.new(sTop.X, y + h + 15)
            o.dist.Visible  = cfg.showDist
            if cfg.showTracer then
                local vp = Core.Cam.ViewportSize
                o.tracer.From    = Vector2.new(vp.X/2, vp.Y)
                o.tracer.To      = Vector2.new(sBot.X, sBot.Y)
                o.tracer.Visible = true
            else
                o.tracer.Visible = false
            end
        end
    end
    function M.Disable()
        cfg.enabled = false
        for _, o in pairs(_objs) do
            for _, d in pairs(o) do d.Visible = false end
        end
    end
    Core.Register("ESP", M)
    return M
end
