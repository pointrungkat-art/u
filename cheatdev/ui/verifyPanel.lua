--[[
  CheatDev — ui/verifyPanel.lua
  🔐 Verify Panel — key gate sebelum cheat bisa dipakai.

  Design language:
    • Galaxy/ungu palette  — BG #0A0814, accent #B450FF, cyan #50C8FF
    • Glass morphism frame — dark semi-transparent backdrop + blur-sim gradient
    • Spring-in animation  — overshoot bounce saat muncul
    • Shake animation      — kalau key salah
    • Pulse accent border  — glow animasi saat idle
    • Keyboard-friendly    — Enter = confirm, Escape = cancel
    • Status states        — Idle → Checking → Error → Success (with distinct UX)

  Usage:
    local VP = load("ui/verifyPanel.lua")
    VP(Core, function(passed)
        if passed then buildMainGUI() end
    end)
]]

return function(Core, onResult)
    local S   = Core.Services
    local TW  = S.TweenService
    local UIS = S.UserInputService
    local LP  = Core.LP

    -- ── Palette ──────────────────────────────────────────────────
    local C = {
        BG      = Color3.fromRGB(10,   8,  20),   -- deep galaxy
        BG2     = Color3.fromRGB(18,  14,  35),   -- card bg
        BG3     = Color3.fromRGB(24,  20,  45),   -- input bg
        ACCENT  = Color3.fromRGB(180,  80, 255),   -- purple
        ACC2    = Color3.fromRGB(80,  200, 255),   -- cyan
        FIRE    = Color3.fromRGB(255, 140,  30),   -- orange
        TEXT    = Color3.fromRGB(230, 225, 255),   -- light purple-white
        DIM     = Color3.fromRGB(120, 110, 150),   -- muted
        OK      = Color3.fromRGB(80,  255, 130),   -- green
        ERR     = Color3.fromRGB(255,  70,  70),   -- red
        WARN    = Color3.fromRGB(255, 200,  50),   -- yellow
    }

    -- ── Tween helpers ────────────────────────────────────────────
    local function tw(inst, props, t, style, dir)
        return TW:Create(inst, TweenInfo.new(
            t or 0.25,
            style or Enum.EasingStyle.Quad,
            dir   or Enum.EasingDirection.Out
        ), props)
    end
    local function twPlay(inst, props, t, style, dir)
        tw(inst, props, t, style, dir):Play()
    end

    -- ── ScreenGui ────────────────────────────────────────────────
    local sg = Instance.new("ScreenGui")
    sg.Name = "CheatDevVerify"; sg.ResetOnSpawn = false
    sg.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    sg.IgnoreGuiInset = true
    sg.Parent = LP.PlayerGui

    -- Backdrop — semi-transparent full-screen overlay
    local backdrop = Instance.new("Frame", sg)
    backdrop.Size = UDim2.new(1, 0, 1, 0)
    backdrop.BackgroundColor3 = Color3.fromRGB(5, 4, 12)
    backdrop.BackgroundTransparency = 0.25
    backdrop.BorderSizePixel = 0
    backdrop.ZIndex = 1

    -- Animated star particles (drawing dots for bg atmosphere)
    local STAR_COUNT = 40
    local stars = {}
    for i = 1, STAR_COUNT do
        local s = Instance.new("Frame", backdrop)
        s.Size = UDim2.new(0, math.random(1, 3), 0, math.random(1, 3))
        s.Position = UDim2.new(math.random()/1, 0, math.random()/1, 0)
        local bright = math.random(60, 180)
        s.BackgroundColor3 = Color3.fromRGB(bright, bright, bright + 30)
        s.BackgroundTransparency = math.random(20, 70) / 100
        s.BorderSizePixel = 0
        Instance.new("UICorner", s).CornerRadius = UDim.new(1, 0)
        stars[i] = s
    end

    -- ── Card ─────────────────────────────────────────────────────
    local card = Instance.new("Frame", sg)
    card.Size = UDim2.new(0, 380, 0, 440)
    card.Position = UDim2.new(0.5, -190, -0.6, 0)  -- starts above screen
    card.BackgroundColor3 = C.BG2
    card.BackgroundTransparency = 0
    card.BorderSizePixel = 0
    card.ZIndex = 5
    Instance.new("UICorner", card).CornerRadius = UDim.new(0, 12)

    -- Glow border frame
    local glowBorder = Instance.new("Frame", card)
    glowBorder.Size = UDim2.new(1, 8, 1, 8)
    glowBorder.Position = UDim2.new(0, -4, 0, -4)
    glowBorder.BackgroundColor3 = C.ACCENT
    glowBorder.BackgroundTransparency = 0.65
    glowBorder.BorderSizePixel = 0
    glowBorder.ZIndex = 4
    Instance.new("UICorner", glowBorder).CornerRadius = UDim.new(0, 14)

    -- Inner glass layer
    local glass = Instance.new("Frame", card)
    glass.Size = UDim2.new(1, 0, 1, 0)
    glass.BackgroundColor3 = C.BG3
    glass.BackgroundTransparency = 0.35
    glass.BorderSizePixel = 0
    glass.ZIndex = 6
    Instance.new("UICorner", glass).CornerRadius = UDim.new(0, 12)

    -- Top accent bar
    local accentBar = Instance.new("Frame", card)
    accentBar.Size = UDim2.new(1, 0, 0, 3)
    accentBar.Position = UDim2.new(0, 0, 0, 0)
    accentBar.BackgroundColor3 = C.ACCENT
    accentBar.BorderSizePixel = 0
    accentBar.ZIndex = 10
    Instance.new("UICorner", accentBar).CornerRadius = UDim.new(0, 12)

    -- ── Logo Section ─────────────────────────────────────────────
    local logoFrame = Instance.new("Frame", card)
    logoFrame.Size = UDim2.new(1, 0, 0, 130)
    logoFrame.Position = UDim2.new(0, 0, 0, 16)
    logoFrame.BackgroundTransparency = 1
    logoFrame.ZIndex = 10

    -- Logo icon (emoji + gradient bg circle)
    local iconBg = Instance.new("Frame", logoFrame)
    iconBg.Size = UDim2.new(0, 72, 0, 72)
    iconBg.Position = UDim2.new(0.5, -36, 0, 8)
    iconBg.BackgroundColor3 = C.ACCENT
    iconBg.BackgroundTransparency = 0.25
    iconBg.BorderSizePixel = 0
    iconBg.ZIndex = 10
    Instance.new("UICorner", iconBg).CornerRadius = UDim.new(1, 0)

    local iconLbl = Instance.new("TextLabel", iconBg)
    iconLbl.Size = UDim2.new(1, 0, 1, 0)
    iconLbl.BackgroundTransparency = 1
    iconLbl.Text = "⚡"
    iconLbl.TextSize = 36
    iconLbl.Font = Enum.Font.GothamBold
    iconLbl.TextColor3 = Color3.new(1, 1, 1)
    iconLbl.ZIndex = 11

    -- Title
    local title = Instance.new("TextLabel", logoFrame)
    title.Size = UDim2.new(1, 0, 0, 28)
    title.Position = UDim2.new(0, 0, 0, 88)
    title.BackgroundTransparency = 1
    title.Text = "CHEAT DEVELOPER"
    title.TextSize = 22
    title.Font = Enum.Font.GothamBlack
    title.TextColor3 = C.ACCENT
    title.TextXAlignment = Enum.TextXAlignment.Center
    title.ZIndex = 10

    local subtitle = Instance.new("TextLabel", logoFrame)
    subtitle.Size = UDim2.new(1, 0, 0, 18)
    subtitle.Position = UDim2.new(0, 0, 0, 114)
    subtitle.BackgroundTransparency = 1
    subtitle.Text = "v2.0 · Dev Mode · DAR DER DOR 🔥"
    subtitle.TextSize = 12
    subtitle.Font = Enum.Font.Gotham
    subtitle.TextColor3 = C.DIM
    subtitle.TextXAlignment = Enum.TextXAlignment.Center
    subtitle.ZIndex = 10

    -- Divider
    local divider = Instance.new("Frame", card)
    divider.Size = UDim2.new(0.8, 0, 0, 1)
    divider.Position = UDim2.new(0.1, 0, 0, 155)
    divider.BackgroundColor3 = C.ACCENT
    divider.BackgroundTransparency = 0.7
    divider.BorderSizePixel = 0
    divider.ZIndex = 10

    -- ── Key Input Section ────────────────────────────────────────
    local keyLabel = Instance.new("TextLabel", card)
    keyLabel.Size = UDim2.new(0.85, 0, 0, 18)
    keyLabel.Position = UDim2.new(0.075, 0, 0, 170)
    keyLabel.BackgroundTransparency = 1
    keyLabel.Text = "🔑  ENTER ACCESS KEY"
    keyLabel.TextSize = 11
    keyLabel.Font = Enum.Font.GothamBold
    keyLabel.TextColor3 = C.DIM
    keyLabel.TextXAlignment = Enum.TextXAlignment.Left
    keyLabel.ZIndex = 10
    keyLabel.LetterSpacing = 2

    -- Input container
    local inputBox_bg = Instance.new("Frame", card)
    inputBox_bg.Size = UDim2.new(0.85, 0, 0, 48)
    inputBox_bg.Position = UDim2.new(0.075, 0, 0, 194)
    inputBox_bg.BackgroundColor3 = C.BG
    inputBox_bg.BackgroundTransparency = 0.15
    inputBox_bg.BorderSizePixel = 0
    inputBox_bg.ZIndex = 10
    Instance.new("UICorner", inputBox_bg).CornerRadius = UDim.new(0, 8)

    -- Input border (changes color on focus/error/success)
    local inputBorder = Instance.new("UIStroke", inputBox_bg)
    inputBorder.Color = C.ACCENT
    inputBorder.Transparency = 0.6
    inputBorder.Thickness = 1.5

    -- The actual TextBox
    local inputField = Instance.new("TextBox", inputBox_bg)
    inputField.Size = UDim2.new(1, -48, 1, 0)
    inputField.Position = UDim2.new(0, 14, 0, 0)
    inputField.BackgroundTransparency = 1
    inputField.Text = ""
    inputField.PlaceholderText = "Type your key here..."
    inputField.PlaceholderColor3 = C.DIM
    inputField.TextSize = 16
    inputField.Font = Enum.Font.GothamBold
    inputField.TextColor3 = C.TEXT
    inputField.TextXAlignment = Enum.TextXAlignment.Left
    inputField.ClearTextOnFocus = false
    inputField.ZIndex = 12

    -- Eye / show-hide icon (toggle masking)
    local masked = true
    local eyeBtn = Instance.new("TextButton", inputBox_bg)
    eyeBtn.Size = UDim2.new(0, 36, 0, 36)
    eyeBtn.Position = UDim2.new(1, -40, 0.5, -18)
    eyeBtn.BackgroundTransparency = 1
    eyeBtn.Text = "👁️"
    eyeBtn.TextSize = 18
    eyeBtn.ZIndex = 13

    local function applyMask()
        if masked then
            inputField.Text = inputField.Text:gsub(".", "•")
        end
    end

    local realText = ""
    inputField:GetPropertyChangedSignal("Text"):Connect(function()
        if masked then
            local t = inputField.Text
            -- Count how many real chars we have
            if #t > #realText then
                realText = realText .. t:sub(#realText + 1):gsub("•", "")
            elseif #t < #realText then
                realText = realText:sub(1, #t)
            end
            -- Replace all visible text with bullets
            inputField.Text = string.rep("•", #realText)
        else
            realText = inputField.Text
        end
    end)

    eyeBtn.MouseButton1Click:Connect(function()
        masked = not masked
        eyeBtn.Text = masked and "👁️" or "🙈"
        if masked then
            inputField.Text = string.rep("•", #realText)
        else
            inputField.Text = realText
        end
    end)

    -- Status label
    local statusLbl = Instance.new("TextLabel", card)
    statusLbl.Size = UDim2.new(0.85, 0, 0, 20)
    statusLbl.Position = UDim2.new(0.075, 0, 0, 248)
    statusLbl.BackgroundTransparency = 1
    statusLbl.Text = ""
    statusLbl.TextSize = 12
    statusLbl.Font = Enum.Font.GothamBold
    statusLbl.TextColor3 = C.DIM
    statusLbl.TextXAlignment = Enum.TextXAlignment.Left
    statusLbl.ZIndex = 10

    -- ── Unlock Button ────────────────────────────────────────────
    local unlockBtn = Instance.new("TextButton", card)
    unlockBtn.Size = UDim2.new(0.85, 0, 0, 52)
    unlockBtn.Position = UDim2.new(0.075, 0, 0, 278)
    unlockBtn.BackgroundColor3 = C.ACCENT
    unlockBtn.BorderSizePixel = 0
    unlockBtn.Text = "🔓  UNLOCK"
    unlockBtn.TextSize = 16
    unlockBtn.Font = Enum.Font.GothamBlack
    unlockBtn.TextColor3 = Color3.new(1, 1, 1)
    unlockBtn.AutoButtonColor = false
    unlockBtn.ZIndex = 10
    Instance.new("UICorner", unlockBtn).CornerRadius = UDim.new(0, 8)

    -- Button glow (UIStroke)
    local btnStroke = Instance.new("UIStroke", unlockBtn)
    btnStroke.Color = C.ACC2
    btnStroke.Transparency = 0.6
    btnStroke.Thickness = 1

    -- ── Key tags display ─────────────────────────────────────────
    local tagsLbl = Instance.new("TextLabel", card)
    tagsLbl.Size = UDim2.new(0.85, 0, 0, 36)
    tagsLbl.Position = UDim2.new(0.075, 0, 0, 346)
    tagsLbl.BackgroundTransparency = 1
    tagsLbl.Text = "Free to use · pointrungkat-art"
    tagsLbl.TextSize = 11
    tagsLbl.Font = Enum.Font.Gotham
    tagsLbl.TextColor3 = C.DIM
    tagsLbl.TextXAlignment = Enum.TextXAlignment.Center
    tagsLbl.TextWrapped = true
    tagsLbl.ZIndex = 10

    local copyrightLbl = Instance.new("TextLabel", card)
    copyrightLbl.Size = UDim2.new(0.85, 0, 0, 16)
    copyrightLbl.Position = UDim2.new(0.075, 0, 0, 400)
    copyrightLbl.BackgroundTransparency = 1
    copyrightLbl.Text = "⚡ CheatDev · Dev Mode ON"
    copyrightLbl.TextSize = 10
    copyrightLbl.Font = Enum.Font.Gotham
    copyrightLbl.TextColor3 = C.ACCENT
    copyrightLbl.TextXAlignment = Enum.TextXAlignment.Center
    copyrightLbl.BackgroundTransparency = 1
    copyrightLbl.ZIndex = 10

    -- ── State Machine ────────────────────────────────────────────
    local VALID_KEYS = {
        [Core.Config.META.key] = true,
        ["XCDEV"]  = true,
        ["XCGANG"] = true,   -- cross-compatible dengan Hub key
        ["DEVMODE"]= true,
    }

    local state = "IDLE"  -- IDLE | CHECKING | ERROR | SUCCESS

    local function setState(s)
        state = s
        if s == "IDLE" then
            statusLbl.Text = ""
            statusLbl.TextColor3 = C.DIM
            twPlay(inputBorder, {Color = C.ACCENT, Transparency = 0.6}, 0.2)
            twPlay(unlockBtn, {BackgroundColor3 = C.ACCENT}, 0.15)
            unlockBtn.Text = "🔓  UNLOCK"

        elseif s == "CHECKING" then
            statusLbl.Text = "🔍 Verifying key..."
            statusLbl.TextColor3 = C.WARN
            unlockBtn.Text = "⏳  CHECKING..."
            twPlay(unlockBtn, {BackgroundColor3 = Color3.fromRGB(100,80,20)}, 0.15)

        elseif s == "ERROR" then
            statusLbl.Text = "❌ Invalid key — try again"
            statusLbl.TextColor3 = C.ERR
            twPlay(inputBorder, {Color = C.ERR, Transparency = 0.3}, 0.15)
            unlockBtn.Text = "🔓  UNLOCK"
            twPlay(unlockBtn, {BackgroundColor3 = C.ACCENT}, 0.3)

            -- Shake animation
            local origX = card.Position.X.Offset
            local origPos = card.Position
            local shakeSteps = {8, -12, 10, -8, 5, -3, 1, 0}
            task.spawn(function()
                for _, offset in ipairs(shakeSteps) do
                    card.Position = UDim2.new(0.5, -190 + offset, origPos.Y.Scale, origPos.Y.Offset)
                    task.wait(0.04)
                end
                card.Position = UDim2.new(0.5, -190, origPos.Y.Scale, origPos.Y.Offset)
            end)

        elseif s == "SUCCESS" then
            statusLbl.Text = "✅ Access granted — Loading..."
            statusLbl.TextColor3 = C.OK
            twPlay(inputBorder, {Color = C.OK, Transparency = 0.2}, 0.2)
            twPlay(accentBar, {BackgroundColor3 = C.OK}, 0.3)
            unlockBtn.Text = "✅  UNLOCKED!"
            twPlay(unlockBtn, {BackgroundColor3 = Color3.fromRGB(20,80,40)}, 0.2)
            twPlay(glowBorder, {BackgroundColor3 = C.OK, BackgroundTransparency = 0.4}, 0.3)
        end
    end

    -- ── Verify logic ─────────────────────────────────────────────
    local function verify()
        if state == "CHECKING" or state == "SUCCESS" then return end
        local key = realText:upper():gsub("%s","")
        if key == "" then
            setState("ERROR")
            statusLbl.Text = "❌ Key cannot be empty"
            return
        end

        setState("CHECKING")
        task.wait(0.6)  -- Small delay for UX feel

        if VALID_KEYS[key] then
            setState("SUCCESS")
            task.wait(1.2)
            -- Exit animation
            twPlay(card, {Position = UDim2.new(0.5, -190, 1.5, 0)}, 0.4, Enum.EasingStyle.Back, Enum.EasingDirection.In)
            twPlay(backdrop, {BackgroundTransparency = 1}, 0.4)
            task.wait(0.45)
            sg:Destroy()
            if onResult then onResult(true) end
        else
            setState("ERROR")
        end
    end

    -- ── Button interactions ───────────────────────────────────────
    unlockBtn.MouseButton1Click:Connect(verify)
    unlockBtn.MouseEnter:Connect(function()
        if state ~= "SUCCESS" and state ~= "CHECKING" then
            twPlay(unlockBtn, {BackgroundColor3 = Color3.fromRGB(200,100,255)}, 0.15)
            twPlay(btnStroke, {Transparency = 0.2}, 0.15)
        end
    end)
    unlockBtn.MouseLeave:Connect(function()
        if state ~= "SUCCESS" and state ~= "CHECKING" then
            twPlay(unlockBtn, {BackgroundColor3 = C.ACCENT}, 0.15)
            twPlay(btnStroke, {Transparency = 0.6}, 0.15)
        end
    end)

    -- Focus border pulse
    inputField.Focused:Connect(function()
        twPlay(inputBorder, {Transparency = 0.1}, 0.2)
    end)
    inputField.FocusLost:Connect(function(enterPressed)
        twPlay(inputBorder, {Transparency = 0.6}, 0.2)
        if enterPressed then verify() end
    end)

    -- Enter key support via UIS
    UIS.InputBegan:Connect(function(inp, gpe)
        if gpe then return end
        if inp.KeyCode == Enum.KeyCode.Return or inp.KeyCode == Enum.KeyCode.KeypadEnter then
            verify()
        end
    end)

    -- ── Ambient glow pulse animation ────────────────────────────
    local pulseRunning = true
    task.spawn(function()
        while pulseRunning do
            twPlay(glowBorder, {BackgroundTransparency = 0.5}, 1.2, Enum.EasingStyle.Sine)
            task.wait(1.2)
            if not pulseRunning then break end
            twPlay(glowBorder, {BackgroundTransparency = 0.75}, 1.2, Enum.EasingStyle.Sine)
            task.wait(1.2)
        end
    end)

    -- Twinkle stars
    task.spawn(function()
        while pulseRunning do
            for _, s in ipairs(stars) do
                task.spawn(function()
                    local t = math.random(30, 80) / 100
                    twPlay(s, {BackgroundTransparency = t}, math.random(8,20)/10, Enum.EasingStyle.Sine)
                end)
            end
            task.wait(2)
        end
    end)

    -- ── Entry animation ──────────────────────────────────────────
    -- Spring bounce in
    local springInfo = TweenInfo.new(0.65, Enum.EasingStyle.Back, Enum.EasingDirection.Out, 0, false, 0)
    TW:Create(card, springInfo, {Position = UDim2.new(0.5, -190, 0.5, -220)}):Play()

    -- Fade backdrop in
    backdrop.BackgroundTransparency = 1
    twPlay(backdrop, {BackgroundTransparency = 0.25}, 0.4)

    -- Focus input after animation
    task.delay(0.7, function()
        if inputField.Parent then
            inputField:CaptureFocus()
        end
    end)

    setState("IDLE")

    -- ── Return controls ───────────────────────────────────────────
    return {
        destroy = function()
            pulseRunning = false
            sg:Destroy()
        end,
        forcePass = function()
            setState("SUCCESS")
            task.wait(0.5)
            sg:Destroy()
            if onResult then onResult(true) end
        end,
    }
end
