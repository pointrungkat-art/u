--[[
  CheatDev — modules/antidetect.lua
  Anti-ban & anti-detect suite untuk Roblox.

  Teknik aktif:
    1. Speed Desync     — WalkSpeed=16 di server, BodyVelocity actual movement
    2. TP Sanitizer     — interpolate teleport, jangan jump >80 studs sekaligus
    3. Remote Hook      — block kick/ban RemoteEvent dari anti-cheat
    4. Metamethod Guard — hook __namecall untuk intercept Kick() calls
    5. Sanity Clamp     — health/speed stay in believable range
    6. Cheat Signature  — randomise executor fingerprint patterns
    7. Anti-LogOut      — block game:Kick() pada LocalPlayer
]]
return function(Core)
    local S, U = Core.Services, Core.Utils
    local cfg  = Core.Config.ANTIDETECT
    local LP   = Core.LP
    local RS   = S.RunService

    -- ── Konstanta batas sanity ──────────────────────────────────
    local MAX_SAFE_SPEED  = 48   -- server biasanya kick > 50
    local MAX_SAFE_JUMP   = 90
    local MAX_TP_STEP     = 75   -- max studs per teleport step
    local KICK_KEYWORDS   = {"kick","ban","anticheat","ac","exploit","cheat","flag","detected"}

    -- ── State ───────────────────────────────────────────────────
    local M = {}
    local _bodyVel   = nil    -- BodyVelocity untuk speed desync
    local _hookConn  = {}     -- koneksi yang harus di-disconnect saat disable
    local _origSpeed = 16
    local _origJump  = 50
    local _blocked   = 0      -- counter remote yang diblock

    -- ── Helpers ─────────────────────────────────────────────────
    local function log(msg, level)
        Core.Log("ANTI", msg, level or "INFO")
    end

    local function isKickRemote(name)
        if not name then return false end
        local l = name:lower()
        for _, kw in ipairs(KICK_KEYWORDS) do
            if l:find(kw, 1, true) then return true end
        end
        return false
    end

    local function getRoot()
        local char = LP.Character
        return char and char:FindFirstChild("HumanoidRootPart")
    end

    local function getHum()
        local char = LP.Character
        return char and char:FindFirstChildOfClass("Humanoid")
    end

    -- ── 1. Speed Desync ─────────────────────────────────────────
    --  WalkSpeed di-set ke 16 (normal), gerak via BodyVelocity/LinearVelocity
    --  Server lihat WalkSpeed = 16 → tidak kick
    function M.ApplySpeedDesync(requestedSpeed)
        if not cfg.speedDesync or not cfg.enabled then return false end
        local root = getRoot(); if not root then return false end
        local hum  = getHum(); if not hum then return false end

        -- Pastikan WalkSpeed tetap di range aman
        hum.WalkSpeed = math.min(hum.WalkSpeed, MAX_SAFE_SPEED)
        hum.JumpPower = math.min(hum.JumpPower, MAX_SAFE_JUMP)

        -- Buat atau reuse BodyVelocity
        if not _bodyVel or not _bodyVel.Parent then
            _bodyVel = Instance.new("BodyVelocity")
            _bodyVel.MaxForce = Vector3.new(1e5, 0, 1e5)
            _bodyVel.P        = 1e4
            _bodyVel.Velocity = Vector3.new(0, 0, 0)
            _bodyVel.Parent   = root
        end

        -- Velocity direction based on input
        local moveDir = LP.Character and LP.Character.Humanoid.MoveDirection or Vector3.zero
        if moveDir.Magnitude > 0.1 then
            _bodyVel.Velocity = moveDir * requestedSpeed
        else
            _bodyVel.Velocity = Vector3.new(0, 0, 0)
        end
        return true
    end

    function M.ClearSpeedDesync()
        if _bodyVel then
            pcall(function() _bodyVel:Destroy() end)
            _bodyVel = nil
        end
        local hum = getHum()
        if hum then
            hum.WalkSpeed = _origSpeed
            hum.JumpPower = _origJump
        end
    end

    -- ── 2. Teleport Sanitizer ───────────────────────────────────
    --  Interpolasi TP dalam steps ≤ MAX_TP_STEP per langkah
    function M.SafeTP(targetCF, onDone)
        local root = getRoot(); if not root then return end
        local steps = cfg.tpSteps or 4
        local from  = root.CFrame
        local dist  = (targetCF.Position - from.Position).Magnitude
        -- Kalau dekat, langsung TP
        if dist <= MAX_TP_STEP or steps <= 1 then
            root.CFrame = targetCF
            if onDone then onDone() end
            return
        end
        -- Interpolate over steps
        task.spawn(function()
            for i = 1, steps do
                if not root or not root.Parent then return end
                root.CFrame = from:Lerp(targetCF, i / steps)
                task.wait(0.04)
            end
            if onDone then onDone() end
        end)
    end

    -- ── 3. Remote Hook — block kick remotes ─────────────────────
    function M.HookRemotes()
        if not cfg.remoteHook or not cfg.enabled then return end

        -- Hook semua RemoteEvent.FireServer
        local oldFireServer = game.ReplicatedStorage and true
        local mt = getrawmetatable and getrawmetatable(game)
        if not mt then
            log("Metamethod hook not available (no getrawmetatable)", "WARN")
            return
        end

        local oldNamecall = mt.__namecall
        local hookActive  = true

        -- Wrap __namecall untuk intercept :FireServer / :InvokeServer
        local ok = pcall(function()
            setreadonly(mt, false)
            mt.__namecall = newcclosure(function(self, ...)
                local method = getnamecallmethod()
                if hookActive and (method == "FireServer" or method == "InvokeServer") then
                    local name = tostring(self.Name or "")
                    if isKickRemote(name) then
                        _blocked = _blocked + 1
                        log(string.format("🛡️ Blocked remote: %s (%s) — total blocked: %d", name, method, _blocked), "WARN")
                        return  -- drop the call
                    end
                end
                return oldNamecall(self, ...)
            end)
            setreadonly(mt, true)
        end)

        if ok then
            log("✅ Remote hook active — kick remotes will be blocked", "OK")
            table.insert(_hookConn, function()
                hookActive = false
                pcall(function()
                    setreadonly(mt, false)
                    mt.__namcall = oldNamecall
                    setreadonly(mt, true)
                end)
            end)
        else
            log("Remote hook failed (setreadonly not available) — using scan approach", "WARN")
            M.ScanAndBlockRemotes()
        end
    end

    -- Fallback: scan ReplicatedStorage dan disconnect known kick remotes
    function M.ScanAndBlockRemotes()
        local function scanFolder(folder)
            if not folder then return end
            for _, obj in ipairs(folder:GetDescendants()) do
                if obj:IsA("RemoteEvent") and isKickRemote(obj.Name) then
                    -- Rebind ke noop
                    pcall(function()
                        obj.OnClientEvent:Connect(function()
                            log("🛡️ Noop remote event: " .. obj.Name, "WARN")
                        end)
                    end)
                    log("📌 Noop-ed suspicious remote: " .. obj.Name, "INFO")
                end
            end
        end
        scanFolder(game:GetService("ReplicatedStorage"))
        scanFolder(game:GetService("ReplicatedFirst"))
    end

    -- ── 4. Anti-Kick (LocalPlayer:Kick block) ───────────────────
    function M.HookKick()
        if not cfg.antiKick or not cfg.enabled then return end
        local mt = getrawmetatable and getrawmetatable(game)
        if not mt then return end

        local oldNC = mt.__namecall
        local ok = pcall(function()
            setreadonly(mt, false)
            mt.__namecall = newcclosure(function(self, ...)
                local method = getnamecallmethod()
                if method == "Kick" and self == LP then
                    log("🛡️ Kick() intercepted and blocked!", "WARN")
                    return  -- block kick
                end
                return oldNC(self, ...)
            end)
            setreadonly(mt, true)
        end)
        if ok then
            log("✅ Kick() hook active — LP:Kick() blocked", "OK")
        end
    end

    -- ── 5. Sanity Clamp loop ─────────────────────────────────────
    --  Tiap frame clamp health/speed agar tidak trigger server check
    local _sanityConn = nil
    function M.StartSanityLoop()
        if not cfg.sanityClamp or not cfg.enabled then return end
        if _sanityConn then _sanityConn:Disconnect() end
        _sanityConn = RS.Heartbeat:Connect(function()
            local hum = getHum()
            if not hum then return end
            -- Jangan biarkan speed/jump jauh di atas ambang aman
            if hum.WalkSpeed > MAX_SAFE_SPEED * 1.5 and not cfg.speedDesync then
                hum.WalkSpeed = MAX_SAFE_SPEED
            end
        end)
        table.insert(_hookConn, function()
            if _sanityConn then _sanityConn:Disconnect(); _sanityConn = nil end
        end)
    end

    -- ── 6. Cheat Signature Randomize ────────────────────────────
    --  Randomise identifiers yang biasa di-scan anti-cheat
    function M.RandomizeSignature()
        if not cfg.sigRandom then return end
        -- Rename LocalScript objects dengan random suffix
        local gs = LP:FindFirstChild("PlayerGui")
        if gs then
            for _, obj in ipairs(gs:GetDescendants()) do
                if obj:IsA("LocalScript") and obj.Name:find("Cheat") then
                    obj.Name = "Script_"..tostring(math.random(10000,99999))
                end
            end
        end
        log("🎲 Signature randomized", "DEV")
    end

    -- ── Status Reporter ──────────────────────────────────────────
    function M.Status()
        return string.format(
            "AntiDetect: %s | Speed=%s | Hook=%s | Sanity=%s | Blocked=%d",
            cfg.enabled and "ON" or "OFF",
            cfg.speedDesync and "DESYNC" or "DIRECT",
            cfg.remoteHook  and "ACTIVE" or "OFF",
            cfg.sanityClamp and "ON" or "OFF",
            _blocked
        )
    end

    -- ── Enable / Disable ─────────────────────────────────────────
    function M.Enable()
        cfg.enabled = true
        local hum = getHum()
        if hum then
            _origSpeed = hum.WalkSpeed
            _origJump  = hum.JumpPower
        end
        M.HookKick()
        M.HookRemotes()
        M.StartSanityLoop()
        M.RandomizeSignature()
        log("✅ Anti-Detect ENABLED — stealth mode ON 🛡️", "OK")
    end

    function M.Disable()
        cfg.enabled = false
        -- Cleanup semua hooks
        for _, cleanup in ipairs(_hookConn) do pcall(cleanup) end
        _hookConn = {}
        M.ClearSpeedDesync()
        log("⚠️ Anti-Detect DISABLED", "WARN")
    end

    function M.Update()
        -- Called tiap RenderStepped dari init.lua kalau mau live update
    end

    Core.Register("AntiDetect", M)
    log("📦 AntiDetect module loaded", "DEV")
    return M
end
