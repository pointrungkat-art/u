--[[  CheatDev — modules/combat.lua
      KillAura, HitboxExpand, AimAssist, SilentAim, AntiRagdoll, GodMode, AntiKick
--]]
return function(Core)
    local S, U, D = Core.Services, Core.Utils, Core.Draw
    local RS   = S.RunService
    local LP   = Core.LP
    local Cam  = Core.Cam
    local cfgA  = Core.Config.AIM
    local cfgSA = Core.Config.SILENT_AIM
    local cfgKA = Core.Config.KILL_AURA
    local cfgHB = Core.Config.HITBOX
    local cfgGM = Core.Config.GOD_MODE
    local cfgAK = Core.Config.ANTI_KICK
    local cfgAR = Core.Config.ANTI_RAGDOLL

    -- ── AIM ASSIST ───────────────────────────────────────────────
    local AimModule   = {}
    local _fovRing    = D.Circle(cfgA.fov, U.Color(180,80,255), 1.5)
    local _crossV     = D.Line(U.Color(255,80,160), 2)
    local _crossH     = D.Line(U.Color(255,80,160), 2)
    local _dot        = D.Circle(3, U.Color(255,80,160), 1, true)

    local function getTarget()
        local best, bestD = nil, math.huge
        local center = Vector2.new(Cam.ViewportSize.X/2, Cam.ViewportSize.Y/2)
        for _, p in ipairs(S.Players:GetPlayers()) do
            if p == LP then continue end
            if cfgA.teamCheck and not U.IsEnemy(p) then continue end
            if not U.IsAlive(p) then continue end
            local part = p.Character and p.Character:FindFirstChild(cfgA.target)
                      or U.GetRoot(p)
            if not part then continue end
            local sp, vis = U.W2S(part.Position)
            if not vis then continue end
            local d = (sp - center).Magnitude
            if d < cfgA.fov and d < bestD then best, bestD = p, d end
        end
        return best
    end

    function AimModule.Update()
        local center = Vector2.new(Cam.ViewportSize.X/2, Cam.ViewportSize.Y/2)
        _fovRing.Radius   = cfgA.fov
        _fovRing.Position = center
        _fovRing.Visible  = cfgA.showFovRing and cfgA.enabled
        local cs = 8
        _crossV.From = Vector2.new(center.X, center.Y-cs)
        _crossV.To   = Vector2.new(center.X, center.Y+cs)
        _crossH.From = Vector2.new(center.X-cs, center.Y)
        _crossH.To   = Vector2.new(center.X+cs, center.Y)
        _crossV.Visible = cfgA.enabled
        _crossH.Visible = cfgA.enabled
        _dot.Position   = center
        _dot.Visible    = cfgA.enabled
        if not cfgA.enabled then return end
        local target = getTarget()
        if not target then return end
        local part = target.Character and target.Character:FindFirstChild(cfgA.target)
                  or U.GetRoot(target)
        if not part then return end
        local pos = part.Position
        if cfgA.prediction then
            local vel = pcall(function() return part.AssemblyLinearVelocity end)
                and part.AssemblyLinearVelocity or Vector3.zero
            pos = pos + vel * cfgA.predMult
        end
        local sp = U.W2S(pos)
        local dir = sp - center
        if cfgA.smoothing then
            Cam.CFrame = Cam.CFrame * CFrame.Angles(
                math.rad(-dir.Y * cfgA.strength / cfgA.smoothFactor),
                math.rad(-dir.X * cfgA.strength / cfgA.smoothFactor),
                0)
        else
            Cam.CFrame = Cam.CFrame * CFrame.Angles(
                math.rad(-dir.Y * cfgA.strength * 0.05),
                math.rad(-dir.X * cfgA.strength * 0.05),
                0)
        end
    end
    function AimModule.Disable()
        cfgA.enabled = false
        _fovRing.Visible = false
        _crossV.Visible  = false
        _crossH.Visible  = false
        _dot.Visible     = false
    end

    -- ── SILENT AIM ───────────────────────────────────────────────
    local SilentModule = {}
    -- Hooks bullet/ray origin toward nearest target head
    local _saConn
    function SilentModule.Enable()
        cfgSA.enabled = true
        -- Silent aim via camera manipulation on tap
        _saConn = S.UserInputService.InputBegan:Connect(function(inp, gpe)
            if gpe or not cfgSA.enabled then return end
            if inp.UserInputType ~= Enum.UserInputType.Touch
            and inp.UserInputType ~= Enum.UserInputType.MouseButton1 then return end
            local target = getTarget()
            if not target then return end
            local head = U.GetHead(target)
            if not head then return end
            local sp = U.W2S(head.Position)
            local center = Vector2.new(Cam.ViewportSize.X/2, Cam.ViewportSize.Y/2)
            local dir = sp - center
            Cam.CFrame = Cam.CFrame * CFrame.Angles(
                math.rad(-dir.Y * 0.6),
                math.rad(-dir.X * 0.6),
                0)
        end)
        Core.Log("SILENT", "⚡ Silent Aim ON", "OK")
    end
    function SilentModule.Disable()
        cfgSA.enabled = false
        if _saConn then _saConn:Disconnect(); _saConn = nil end
        Core.Log("SILENT", "Silent Aim OFF", "INFO")
    end
    function SilentModule.Toggle()
        if cfgSA.enabled then SilentModule.Disable() else SilentModule.Enable() end
    end

    -- ── KILL AURA ────────────────────────────────────────────────
    local KillAuraModule = {}
    local _kaConn, _kaTimer = nil, 0
    function KillAuraModule.Enable()
        cfgKA.enabled = true
        _kaConn = RS.Heartbeat:Connect(function(dt)
            if not cfgKA.enabled then return end
            _kaTimer = _kaTimer + dt
            if _kaTimer < cfgKA.rate then return end
            _kaTimer = 0
            local myRoot = U.GetRoot()
            if not myRoot then return end
            for _, p in ipairs(S.Players:GetPlayers()) do
                if p == LP then continue end
                local pRoot = U.GetRoot(p)
                local hum   = U.GetHum(p)
                if pRoot and hum and hum.Health > 0 then
                    if (myRoot.Position - pRoot.Position).Magnitude <= cfgKA.radius then
                        hum:TakeDamage(cfgKA.damage)
                    end
                end
            end
        end)
        Core.Log("KILLAURA", "💀 Kill Aura ON — r:"..cfgKA.radius.." dmg:"..cfgKA.damage, "OK")
    end
    function KillAuraModule.Disable()
        cfgKA.enabled = false
        if _kaConn then _kaConn:Disconnect(); _kaConn = nil end
        Core.Log("KILLAURA", "Kill Aura OFF", "INFO")
    end
    function KillAuraModule.Toggle()
        if cfgKA.enabled then KillAuraModule.Disable() else KillAuraModule.Enable() end
    end

    -- ── HITBOX EXPAND ────────────────────────────────────────────
    local HitboxModule = {}
    local _hbConn
    function HitboxModule.Enable()
        cfgHB.enabled = true
        _hbConn = RS.Heartbeat:Connect(function()
            if not cfgHB.enabled then return end
            for _, p in ipairs(S.Players:GetPlayers()) do
                if p == LP then continue end
                local root = U.GetRoot(p)
                if root then
                    root.Size = Vector3.new(cfgHB.size, cfgHB.size, cfgHB.size)
                    root.Transparency = 0.9
                end
            end
        end)
        Core.Log("HITBOX", "🎯 Hitbox Expand ON — size:"..cfgHB.size, "OK")
    end
    function HitboxModule.Disable()
        cfgHB.enabled = false
        if _hbConn then _hbConn:Disconnect(); _hbConn = nil end
        for _, p in ipairs(S.Players:GetPlayers()) do
            if p ~= LP then
                local root = U.GetRoot(p)
                if root then root.Size = Vector3.new(2,2,1) end
            end
        end
        Core.Log("HITBOX", "Hitbox Expand OFF", "INFO")
    end
    function HitboxModule.Toggle()
        if cfgHB.enabled then HitboxModule.Disable() else HitboxModule.Enable() end
    end

    -- ── GOD MODE ─────────────────────────────────────────────────
    local GodModule = {}
    local _gmConn
    function GodModule.Enable()
        cfgGM.enabled = true
        _gmConn = RS.Heartbeat:Connect(function()
            if not cfgGM.enabled then return end
            local hum = U.GetHum()
            if hum then hum.Health = hum.MaxHealth end
        end)
        Core.Log("GOD", "🛡️ God Mode ON", "OK")
    end
    function GodModule.Disable()
        cfgGM.enabled = false
        if _gmConn then _gmConn:Disconnect(); _gmConn = nil end
        Core.Log("GOD", "God Mode OFF", "INFO")
    end
    function GodModule.Toggle()
        if cfgGM.enabled then GodModule.Disable() else GodModule.Enable() end
    end

    -- ── ANTI KICK ────────────────────────────────────────────────
    local AntiKickModule = {}
    function AntiKickModule.Enable()
        cfgAK.enabled = true
        local env = getfenv and getfenv() or _ENV
        env.game = setmetatable({}, {
            __index = function(_, k)
                if k == "Players" then
                    return setmetatable({}, {
                        __index = function(_, k2)
                            if k2 == "LocalPlayer" then
                                return setmetatable({}, {
                                    __index = LP,
                                    __newindex = function(_, k3, v)
                                        if k3 ~= "Kick" then LP[k3] = v end
                                    end,
                                })
                            end
                            return S.Players[k2]
                        end
                    })
                end
                return game[k]
            end
        })
        Core.Log("ANTIKICK", "🔒 Anti Kick ON (hook active)", "OK")
    end
    function AntiKickModule.Disable()
        cfgAK.enabled = false
        Core.Log("ANTIKICK", "Anti Kick OFF", "INFO")
    end
    function AntiKickModule.Toggle()
        if cfgAK.enabled then AntiKickModule.Disable() else AntiKickModule.Enable() end
    end

    -- ── ANTI RAGDOLL ─────────────────────────────────────────────
    local AntiRagdoll = {}
    local function patchChar(char)
        for _, v in ipairs(char:GetDescendants()) do
            if v:IsA("BallSocketConstraint") or v:IsA("HingeConstraint") then
                v.Enabled = false
            end
        end
    end
    function AntiRagdoll.Enable()
        cfgAR.enabled = true
        if LP.Character then patchChar(LP.Character) end
        LP.CharacterAdded:Connect(function(c) if cfgAR.enabled then patchChar(c) end end)
        Core.Log("ANTIRAG", "🦴 Anti Ragdoll ON", "OK")
    end
    function AntiRagdoll.Disable()
        cfgAR.enabled = false
        Core.Log("ANTIRAG", "Anti Ragdoll OFF", "INFO")
    end

    Core.Register("Aim",        AimModule)
    Core.Register("SilentAim",  SilentModule)
    Core.Register("KillAura",   KillAuraModule)
    Core.Register("Hitbox",     HitboxModule)
    Core.Register("GodMode",    GodModule)
    Core.Register("AntiKick",   AntiKickModule)
    Core.Register("AntiRagdoll",AntiRagdoll)

    return {
        Aim=AimModule, Silent=SilentModule, KillAura=KillAuraModule,
        Hitbox=HitboxModule, God=GodModule, AntiKick=AntiKickModule,
        AntiRagdoll=AntiRagdoll,
    }
end
