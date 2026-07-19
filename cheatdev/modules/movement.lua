--[[  CheatDev — modules/movement.lua
      Fly, Speed, Noclip, InfJump, SpinBot — semua gerak libas
--]]
return function(Core)
    local S, U = Core.Services, Core.Utils
    local UIS  = S.UserInputService
    local RS   = S.RunService
    local LP   = Core.LP
    local cfgF = Core.Config.FLY
    local cfgS = Core.Config.SPEED
    local cfgN = Core.Config.NOCLIP
    local cfgB = Core.Config.SPIN_BOT

    -- ── FLY ──────────────────────────────────────────────────────
    local FlyModule = {}
    local _flyConn, _flyBP

    local function flyTick()
        local root = U.GetRoot()
        local hum  = U.GetHum()
        if not root or not hum then return end
        hum.PlatformStand = true
        local spd = cfgF.speed
            * (UIS:IsKeyDown(Enum.KeyCode.LeftShift) and 2.5 or 1)
        local cf  = root.CFrame
        local dir = Vector3.new(0,0,0)
        if UIS:IsKeyDown(Enum.KeyCode.W) then dir = dir + cf.LookVector end
        if UIS:IsKeyDown(Enum.KeyCode.S) then dir = dir - cf.LookVector end
        if UIS:IsKeyDown(Enum.KeyCode.A) then dir = dir - cf.RightVector end
        if UIS:IsKeyDown(Enum.KeyCode.D) then dir = dir + cf.RightVector end
        if UIS:IsKeyDown(Enum.KeyCode.Space)    then dir = dir + Vector3.new(0,1,0) end
        if UIS:IsKeyDown(Enum.KeyCode.LeftControl) then dir = dir - Vector3.new(0,1,0) end
        if dir.Magnitude > 0 then dir = dir.Unit end
        if not _flyBP or not _flyBP.Parent then
            _flyBP = Instance.new("BodyPosition")
            _flyBP.MaxForce = Vector3.new(1e5,1e5,1e5)
            _flyBP.Parent   = root
        end
        _flyBP.Position = root.Position + dir * spd * 0.05
    end

    function FlyModule.Enable()
        cfgF.enabled = true
        _flyConn = RS.RenderStepped:Connect(flyTick)
        Core.Log("FLY", "🛸 Fly ON — WASD+Space+Ctrl, LShift = sprint", "OK")
    end
    function FlyModule.Disable()
        cfgF.enabled = false
        if _flyConn then _flyConn:Disconnect(); _flyConn = nil end
        if _flyBP    then _flyBP:Destroy();     _flyBP   = nil end
        local hum = U.GetHum()
        if hum then hum.PlatformStand = false end
        Core.Log("FLY", "Fly OFF", "INFO")
    end
    function FlyModule.Toggle()
        if cfgF.enabled then FlyModule.Disable() else FlyModule.Enable() end
    end

    -- ── SPEED HACK ───────────────────────────────────────────────
    local SpeedModule = {}
    function SpeedModule.Enable()
        cfgS.enabled = true
        local hum = U.GetHum()
        if hum then
            hum.WalkSpeed = cfgS.walkSpeed
            hum.JumpPower = cfgS.jumpPower
        end
        LP.CharacterAdded:Connect(function(char)
            local h = char:WaitForChild("Humanoid")
            if cfgS.enabled then
                h.WalkSpeed = cfgS.walkSpeed
                h.JumpPower = cfgS.jumpPower
            end
        end)
        Core.Log("SPEED", "⚡ Speed ON — WS:"..cfgS.walkSpeed.." JP:"..cfgS.jumpPower, "OK")
    end
    function SpeedModule.Disable()
        cfgS.enabled = false
        local hum = U.GetHum()
        if hum then hum.WalkSpeed = 16; hum.JumpPower = 50 end
        Core.Log("SPEED", "Speed OFF", "INFO")
    end
    function SpeedModule.Toggle()
        if cfgS.enabled then SpeedModule.Disable() else SpeedModule.Enable() end
    end
    function SpeedModule.SetSpeed(v)
        cfgS.walkSpeed = v
        local hum = U.GetHum()
        if hum and cfgS.enabled then hum.WalkSpeed = v end
    end

    -- ── NOCLIP ───────────────────────────────────────────────────
    local NoclipModule = {}
    local _ncConn
    function NoclipModule.Enable()
        cfgN.enabled = true
        _ncConn = RS.Stepped:Connect(function()
            if not cfgN.enabled then return end
            local char = U.GetChar()
            if char then
                for _, p in ipairs(char:GetDescendants()) do
                    if p:IsA("BasePart") then p.CanCollide = false end
                end
            end
        end)
        Core.Log("NOCLIP", "👻 Noclip ON — tembus semua", "OK")
    end
    function NoclipModule.Disable()
        cfgN.enabled = false
        if _ncConn then _ncConn:Disconnect(); _ncConn = nil end
        Core.Log("NOCLIP", "Noclip OFF", "INFO")
    end
    function NoclipModule.Toggle()
        if cfgN.enabled then NoclipModule.Disable() else NoclipModule.Enable() end
    end

    -- ── INF JUMP ─────────────────────────────────────────────────
    local InfJumpModule = {}
    local _ijConn
    function InfJumpModule.Enable()
        _ijConn = UIS.JumpRequest:Connect(function()
            local hum = U.GetHum()
            if hum then hum:ChangeState(Enum.HumanoidStateType.Jumping) end
        end)
        Core.Log("INFJUMP", "🦅 Infinite Jump ON", "OK")
    end
    function InfJumpModule.Disable()
        if _ijConn then _ijConn:Disconnect(); _ijConn = nil end
        Core.Log("INFJUMP", "Infinite Jump OFF", "INFO")
    end

    -- ── SPIN BOT ─────────────────────────────────────────────────
    local SpinModule = {}
    local _spinConn
    function SpinModule.Enable()
        cfgB.enabled = true
        local angle  = 0
        _spinConn = RS.RenderStepped:Connect(function(dt)
            if not cfgB.enabled then return end
            local root = U.GetRoot()
            if root then
                angle = (angle + cfgB.speed * dt) % 360
                root.CFrame = CFrame.new(root.Position)
                    * CFrame.Angles(0, math.rad(angle), 0)
            end
        end)
        Core.Log("SPIN", "🌀 SpinBot ON — speed:"..cfgB.speed, "OK")
    end
    function SpinModule.Disable()
        cfgB.enabled = false
        if _spinConn then _spinConn:Disconnect(); _spinConn = nil end
        Core.Log("SPIN", "SpinBot OFF", "INFO")
    end
    function SpinModule.Toggle()
        if cfgB.enabled then SpinModule.Disable() else SpinModule.Enable() end
    end

    -- ── TP KILL ──────────────────────────────────────────────────
    local TPKillModule = {}
    function TPKillModule.Run()
        for _, p in ipairs(S.Players:GetPlayers()) do
            if p ~= LP and U.IsAlive(p) then
                local pRoot = U.GetRoot(p)
                local myRoot = U.GetRoot()
                if pRoot and myRoot then
                    myRoot.CFrame = pRoot.CFrame * CFrame.new(0, 0, -2)
                    task.wait(0.05)
                    local hum = U.GetHum(p)
                    if hum then hum.Health = 0 end
                    Core.Log("TPKILL", "💀 Killed: "..p.Name, "OK")
                    task.wait(0.3)
                end
            end
        end
    end

    -- Register semua
    Core.Register("Fly",     FlyModule)
    Core.Register("Speed",   SpeedModule)
    Core.Register("Noclip",  NoclipModule)
    Core.Register("InfJump", InfJumpModule)
    Core.Register("SpinBot", SpinModule)
    Core.Register("TPKill",  TPKillModule)

    return {
        Fly=FlyModule, Speed=SpeedModule, Noclip=NoclipModule,
        InfJump=InfJumpModule, Spin=SpinModule, TPKill=TPKillModule,
    }
end
