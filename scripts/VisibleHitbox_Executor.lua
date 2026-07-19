-- VisibleHitbox + ESP | Combat Testing Script
-- Private server testing only
-- [H] Hitbox  [G] Size  [D] Dmg Popup  [E] ESP  [T] Tracer

local Players          = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local RunService       = game:GetService("RunService")

local LP     = Players.LocalPlayer
local Camera = workspace.CurrentCamera

-- ══════════════════════════════════════════
--              KONFIGURASI
-- ══════════════════════════════════════════

local Config = {
    -- Hitbox
    EnemyColor    = Color3.fromRGB(255, 60,  60),
    SelfColor     = Color3.fromRGB(60,  255, 100),
    LineThickness = 0.05,
    SurfaceTransp = 0.80,
    FillTransp    = 0.55,

    Sizes = {
        Vector3.new(3.5, 5.5, 2),
        Vector3.new(5,   6,   3),
        Vector3.new(7,   7,   5),
    },
    SizeIndex = 2,

    -- Info
    ShowHealth    = true,
    ShowDistance  = true,
    ShowDamageNum = true,
    ShowHitEffect = true,

    -- ESP
    ESPEnabled    = true,
    TracerEnabled = true,

    -- Chams warna
    ChamsFillEnemy   = Color3.fromRGB(255, 50,  50),
    ChamsFillSelf    = Color3.fromRGB(50,  255, 100),
    ChamsOutEnemy    = Color3.fromRGB(255, 150, 150),
    ChamsOutSelf     = Color3.fromRGB(150, 255, 180),
    ChamsFillTransp  = 0.55,
    ChamsOutTransp   = 0,

    -- Tracer
    TracerColorEnemy = Color3.fromRGB(255, 70,  70),
    TracerColorSelf  = Color3.fromRGB(70,  255, 110),
    TracerThickness  = 1.5,
    TracerOrigin     = "Bottom",  -- "Bottom" | "Center"
}

-- ══════════════════════════════════════════
--              STATE
-- ══════════════════════════════════════════

local hitboxEnabled = true
local registry      = {}   -- [character] = { box, sel, billboard, highlight }
local tracerFrames  = {}   -- [character] = Frame
local frameCount    = 0
local lastFPSTime   = tick()

-- ══════════════════════════════════════════
--              GUI SETUP
-- ══════════════════════════════════════════

if LP.PlayerGui:FindFirstChild("HitboxTestUI") then
    LP.PlayerGui:FindFirstChild("HitboxTestUI"):Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name           = "HitboxTestUI"
ScreenGui.ResetOnSpawn   = false
ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
ScreenGui.Parent         = LP.PlayerGui

-- Container full-screen untuk tracer (di belakang semua UI)
local TracerContainer = Instance.new("Frame")
TracerContainer.Name                   = "TracerContainer"
TracerContainer.Size                   = UDim2.new(1, 0, 1, 0)
TracerContainer.BackgroundTransparency = 1
TracerContainer.BorderSizePixel        = 0
TracerContainer.ZIndex                 = 1
TracerContainer.Parent                 = ScreenGui

-- Panel HUD
local Panel = Instance.new("Frame")
Panel.Name                   = "Panel"
Panel.Size                   = UDim2.new(0, 225, 0, 270)
Panel.Position               = UDim2.new(0, 12, 0, 12)
Panel.BackgroundColor3       = Color3.fromRGB(10, 10, 10)
Panel.BackgroundTransparency = 0.3
Panel.BorderSizePixel        = 0
Panel.ZIndex                 = 10
Panel.Parent                 = ScreenGui
Instance.new("UICorner", Panel).CornerRadius = UDim.new(0, 10)

local Stroke = Instance.new("UIStroke")
Stroke.Color     = Color3.fromRGB(255, 60, 60)
Stroke.Thickness = 1.5
Stroke.Parent    = Panel

local Title = Instance.new("TextLabel")
Title.Size                   = UDim2.new(1, 0, 0, 32)
Title.BackgroundColor3       = Color3.fromRGB(255, 60, 60)
Title.BackgroundTransparency = 0
Title.BorderSizePixel        = 0
Title.Text                   = "  HITBOX + ESP TESTER"
Title.TextColor3             = Color3.fromRGB(255, 255, 255)
Title.Font                   = Enum.Font.GothamBold
Title.TextSize               = 12
Title.TextXAlignment         = Enum.TextXAlignment.Left
Title.ZIndex                 = 11
Title.Parent                 = Panel
Instance.new("UICorner", Title).CornerRadius = UDim.new(0, 10)

local function makeDivider(yPos, label)
    local div = Instance.new("TextLabel")
    div.Size                   = UDim2.new(1, -16, 0, 18)
    div.Position               = UDim2.new(0, 8, 0, yPos)
    div.BackgroundTransparency = 1
    div.Text                   = "── " .. label .. " ──"
    div.TextColor3             = Color3.fromRGB(100, 100, 100)
    div.Font                   = Enum.Font.Gotham
    div.TextSize               = 10
    div.TextXAlignment         = Enum.TextXAlignment.Left
    div.ZIndex                 = 11
    div.Parent                 = Panel
end

local function makeRow(yPos, label)
    local row = Instance.new("Frame")
    row.Size                   = UDim2.new(1, -16, 0, 22)
    row.Position               = UDim2.new(0, 8, 0, yPos)
    row.BackgroundTransparency = 1
    row.ZIndex                 = 11
    row.Parent                 = Panel

    local lbl = Instance.new("TextLabel")
    lbl.Size                   = UDim2.new(0.62, 0, 1, 0)
    lbl.BackgroundTransparency = 1
    lbl.Text                   = label
    lbl.TextColor3             = Color3.fromRGB(160, 160, 160)
    lbl.Font                   = Enum.Font.Gotham
    lbl.TextSize               = 11
    lbl.TextXAlignment         = Enum.TextXAlignment.Left
    lbl.ZIndex                 = 11
    lbl.Parent                 = row

    local val = Instance.new("TextLabel")
    val.Size                   = UDim2.new(0.38, 0, 1, 0)
    val.Position               = UDim2.new(0.62, 0, 0, 0)
    val.BackgroundTransparency = 1
    val.Text                   = "-"
    val.TextColor3             = Color3.fromRGB(255, 255, 255)
    val.Font                   = Enum.Font.GothamBold
    val.TextSize               = 11
    val.TextXAlignment         = Enum.TextXAlignment.Right
    val.ZIndex                 = 11
    val.Parent                 = row

    return val
end

makeDivider(36,  "HITBOX")
local RowHitbox  = makeRow(54,  "[H] Hitbox")
local RowSize    = makeRow(76,  "[G] Size")
local RowDmgNum  = makeRow(98,  "[D] Dmg Popup")

makeDivider(126, "ESP")
local RowESP     = makeRow(144, "[E] Chams")
local RowTracer  = makeRow(166, "[T] Tracer")

makeDivider(194, "INFO")
local RowPlayers = makeRow(212, "Players")
local RowFPS     = makeRow(234, "FPS")

-- Toast
local Toast = Instance.new("Frame")
Toast.Name                   = "Toast"
Toast.Size                   = UDim2.new(0, 310, 0, 38)
Toast.Position               = UDim2.new(0.5, -155, 0, 12)
Toast.BackgroundColor3       = Color3.fromRGB(10, 10, 10)
Toast.BackgroundTransparency = 0.2
Toast.BorderSizePixel        = 0
Toast.Visible                = false
Toast.ZIndex                 = 20
Toast.Parent                 = ScreenGui
Instance.new("UICorner", Toast).CornerRadius = UDim.new(0, 8)

local ToastLabel = Instance.new("TextLabel")
ToastLabel.Size                   = UDim2.new(1, 0, 1, 0)
ToastLabel.BackgroundTransparency = 1
ToastLabel.TextColor3             = Color3.fromRGB(255, 255, 255)
ToastLabel.Font                   = Enum.Font.GothamBold
ToastLabel.TextSize               = 13
ToastLabel.ZIndex                 = 21
ToastLabel.Parent                 = Toast

local toastThread
local function showToast(text, color)
    ToastLabel.Text        = text
    Toast.BackgroundColor3 = color or Color3.fromRGB(30, 30, 30)
    Toast.Visible          = true
    if toastThread then task.cancel(toastThread) end
    toastThread = task.delay(2.5, function() Toast.Visible = false end)
end

-- ══════════════════════════════════════════
--           DAMAGE NUMBER POPUP
-- ══════════════════════════════════════════

local DMG_COLORS = {
    [1]   = Color3.fromRGB(225, 225, 225),
    [50]  = Color3.fromRGB(255, 210, 50),
    [100] = Color3.fromRGB(255, 90,  50),
    [150] = Color3.fromRGB(210, 50,  255),
}

local function getDmgColor(dmg)
    if dmg >= 150 then return DMG_COLORS[150]
    elseif dmg >= 100 then return DMG_COLORS[100]
    elseif dmg >= 50  then return DMG_COLORS[50]
    else return DMG_COLORS[1] end
end

local function showDamageNumber(root, dmg)
    if not Config.ShowDamageNum or not root or not root.Parent then return end

    local bb = Instance.new("BillboardGui")
    bb.Adornee     = root
    bb.Size        = UDim2.new(0, 90, 0, 45)
    bb.StudsOffset = Vector3.new(math.random(-3, 3), math.random(3, 6), 0)
    bb.AlwaysOnTop = true
    bb.Parent      = workspace

    local lbl = Instance.new("TextLabel")
    lbl.Size                   = UDim2.new(1, 0, 1, 0)
    lbl.BackgroundTransparency = 1
    lbl.Text                   = "-" .. dmg
    lbl.TextColor3             = getDmgColor(dmg)
    lbl.Font                   = Enum.Font.GothamBold
    lbl.TextSize               = dmg >= 100 and 22 or 16
    lbl.TextStrokeTransparency = 0.3
    lbl.Parent                 = bb

    local startOffset = bb.StudsOffset
    local t = 0
    local conn
    conn = RunService.RenderStepped:Connect(function(dt)
        t = t + dt
        if t >= 0.85 then
            conn:Disconnect()
            if bb and bb.Parent then bb:Destroy() end
            return
        end
        bb.StudsOffset       = startOffset + Vector3.new(0, t * 3.5, 0)
        local alpha          = math.clamp((t - 0.4) / 0.45, 0, 1)
        lbl.TextTransparency = alpha
        lbl.TextStrokeTransparency = 0.3 + alpha * 0.7
    end)
end

-- ══════════════════════════════════════════
--            HIT EFFECT
-- ══════════════════════════════════════════

local function showHitEffect(position)
    if not Config.ShowHitEffect then return end

    local ring = Instance.new("Part")
    ring.Shape        = Enum.PartType.Ball
    ring.Size         = Vector3.new(0.6, 0.6, 0.6)
    ring.CFrame       = CFrame.new(position + Vector3.new(
        math.random(-10, 10) * 0.1, math.random(0, 15) * 0.1, math.random(-10, 10) * 0.1
    ))
    ring.Anchored     = true
    ring.CanCollide   = false
    ring.CanTouch     = false
    ring.CanQuery     = false
    ring.CastShadow   = false
    ring.Material     = Enum.Material.Neon
    ring.Color        = Color3.fromRGB(255, 210, 60)
    ring.Transparency = 0.1
    ring.Parent       = workspace

    local t = 0
    local conn
    conn = RunService.RenderStepped:Connect(function(dt)
        t = t + dt
        if t >= 0.22 then
            conn:Disconnect()
            if ring and ring.Parent then ring:Destroy() end
            return
        end
        local alpha    = t / 0.22
        local newSize  = 0.6 + alpha * 2.4
        ring.Size         = Vector3.new(newSize, newSize, newSize)
        ring.Transparency = alpha
    end)
end

-- ══════════════════════════════════════════
--           TRACER LINES
-- ══════════════════════════════════════════

local function getTracerOrigin()
    local vp = Camera.ViewportSize
    if Config.TracerOrigin == "Center" then
        return Vector2.new(vp.X / 2, vp.Y / 2)
    end
    return Vector2.new(vp.X / 2, vp.Y)
end

local function getOrCreateTracer(character, color)
    if tracerFrames[character] and tracerFrames[character].Parent then
        return tracerFrames[character]
    end

    local line = Instance.new("Frame")
    line.Name                   = "Tracer_" .. character.Name
    line.AnchorPoint            = Vector2.new(0, 0.5)
    line.BackgroundColor3       = color
    line.BackgroundTransparency = 0.25
    line.BorderSizePixel        = 0
    line.ZIndex                 = 2
    line.Parent                 = TracerContainer

    Instance.new("UICorner", line).CornerRadius = UDim.new(1, 0)

    tracerFrames[character] = line
    return line
end

local function removeTracer(character)
    local line = tracerFrames[character]
    if line and line.Parent then line:Destroy() end
    tracerFrames[character] = nil
end

local function updateTracers()
    if not Config.TracerEnabled then
        for _, line in pairs(tracerFrames) do
            if line and line.Parent then line.Visible = false end
        end
        return
    end

    local origin = getTracerOrigin()

    for _, player in ipairs(Players:GetPlayers()) do
        local char = player.Character
        if not char then continue end

        local root = char:FindFirstChild("HumanoidRootPart")
        if not root then continue end

        local humanoid = char:FindFirstChildWhichIsA("Humanoid")
        if not humanoid or humanoid.Health <= 0 then
            removeTracer(char)
            continue
        end

        local screenPos, onScreen = Camera:WorldToViewportPoint(root.Position)
        local color = player == LP and Config.TracerColorSelf or Config.TracerColorEnemy
        local line  = getOrCreateTracer(char, color)

        if not onScreen then
            line.Visible = false
            continue
        end

        line.Visible = true

        local target  = Vector2.new(screenPos.X, screenPos.Y)
        local delta   = target - origin
        local dist    = delta.Magnitude
        local angle   = math.deg(math.atan2(delta.Y, delta.X))

        line.Size     = UDim2.new(0, dist, 0, Config.TracerThickness)
        line.Position = UDim2.new(0, origin.X, 0, origin.Y)
        line.Rotation = angle
    end

    -- Cleanup tracers for chars that no longer exist
    for char, line in pairs(tracerFrames) do
        if not char.Parent then
            removeTracer(char)
        end
    end
end

-- ══════════════════════════════════════════
--           CHAMS (HIGHLIGHT)
-- ══════════════════════════════════════════

local function addChams(character, isSelf)
    -- Hapus highlight lama kalau ada
    local old = character:FindFirstChildWhichIsA("Highlight")
    if old then old:Destroy() end

    if not Config.ESPEnabled then return end

    local hl = Instance.new("Highlight")
    hl.Adornee           = character
    hl.FillColor         = isSelf and Config.ChamsFillSelf   or Config.ChamsFillEnemy
    hl.OutlineColor      = isSelf and Config.ChamsOutSelf    or Config.ChamsOutEnemy
    hl.FillTransparency  = Config.ChamsFillTransp
    hl.OutlineTransparency = Config.ChamsOutTransp
    hl.DepthMode         = Enum.HighlightDepthMode.AlwaysOnTop
    hl.Enabled           = Config.ESPEnabled
    hl.Parent            = character
    return hl
end

local function setChamsAll(enabled)
    for _, player in ipairs(Players:GetPlayers()) do
        local char = player.Character
        if not char then continue end
        local hl = char:FindFirstChildWhichIsA("Highlight")
        if hl then hl.Enabled = enabled end
    end
end

-- ══════════════════════════════════════════
--          HITBOX VISUAL PER KARAKTER
-- ══════════════════════════════════════════

local function removeHitbox(character)
    local entry = registry[character]
    if not entry then return end
    for _, obj in ipairs(entry) do
        if obj and obj.Parent then obj:Destroy() end
    end
    registry[character] = nil
end

local function addHitbox(character, color, isSelf)
    if registry[character] then removeHitbox(character) end

    local root = character:FindFirstChild("HumanoidRootPart")
        or character:WaitForChild("HumanoidRootPart", 5)
    if not root then return end

    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    if not humanoid or humanoid.Health <= 0 then return end

    local size = Config.Sizes[Config.SizeIndex]

    -- Hitbox part
    local box = Instance.new("Part")
    box.Name          = "HB_Visual"
    box.Size          = size
    box.Color         = color
    box.Material      = Enum.Material.Neon
    box.Transparency  = hitboxEnabled and Config.FillTransp or 1
    box.CanCollide    = false
    box.CanTouch      = false
    box.CanQuery      = false
    box.Anchored      = false
    box.CastShadow    = false
    box.Parent        = character

    local weld = Instance.new("WeldConstraint")
    weld.Part0  = root
    weld.Part1  = box
    weld.Parent = box
    box.CFrame  = root.CFrame + Vector3.new(0, 0.25, 0)

    -- Wireframe
    local sel = Instance.new("SelectionBox")
    sel.Adornee             = box
    sel.Color3              = color
    sel.LineThickness       = Config.LineThickness
    sel.SurfaceColor3       = color
    sel.SurfaceTransparency = Config.SurfaceTransp
    sel.Visible             = hitboxEnabled
    sel.Parent              = box

    -- Billboard: nama + HP bar + info
    local billboard = Instance.new("BillboardGui")
    billboard.Name        = "HB_Billboard"
    billboard.Adornee     = root
    billboard.Size        = UDim2.new(0, 180, 0, 70)
    billboard.StudsOffset = Vector3.new(0, 4, 0)
    billboard.AlwaysOnTop = true
    billboard.Enabled     = hitboxEnabled
    billboard.Parent      = character

    local nameLabel = Instance.new("TextLabel")
    nameLabel.Size                   = UDim2.new(1, 0, 0, 20)
    nameLabel.BackgroundTransparency = 1
    nameLabel.Text                   = character.Name
    nameLabel.TextColor3             = color
    nameLabel.Font                   = Enum.Font.GothamBold
    nameLabel.TextSize               = 13
    nameLabel.TextStrokeTransparency = 0.4
    nameLabel.Parent                 = billboard

    -- HP bar background
    local hpBg = Instance.new("Frame")
    hpBg.Size                   = UDim2.new(1, 0, 0, 7)
    hpBg.Position               = UDim2.new(0, 0, 0, 22)
    hpBg.BackgroundColor3       = Color3.fromRGB(40, 40, 40)
    hpBg.BackgroundTransparency = 0.3
    hpBg.BorderSizePixel        = 0
    hpBg.Parent                 = billboard
    Instance.new("UICorner", hpBg).CornerRadius = UDim.new(1, 0)

    -- HP bar fill
    local hpFill = Instance.new("Frame")
    hpFill.Name                 = "Fill"
    hpFill.Size                 = UDim2.new(1, 0, 1, 0)
    hpFill.BackgroundColor3     = Color3.fromRGB(80, 255, 100)
    hpFill.BackgroundTransparency = 0
    hpFill.BorderSizePixel      = 0
    hpFill.Parent               = hpBg
    Instance.new("UICorner", hpFill).CornerRadius = UDim.new(1, 0)

    -- Info label (HP teks + jarak)
    local infoLabel = Instance.new("TextLabel")
    infoLabel.Name                   = "Info"
    infoLabel.Size                   = UDim2.new(1, 0, 0, 20)
    infoLabel.Position               = UDim2.new(0, 0, 0, 34)
    infoLabel.BackgroundTransparency = 1
    infoLabel.TextColor3             = Color3.fromRGB(210, 210, 210)
    infoLabel.Font                   = Enum.Font.Gotham
    infoLabel.TextSize               = 11
    infoLabel.TextStrokeTransparency = 0.5
    infoLabel.Parent                 = billboard

    -- Chams
    local hl = addChams(character, isSelf)

    registry[character] = { box, sel, billboard, hl }

    -- Update per frame
    local connRender
    connRender = RunService.RenderStepped:Connect(function()
        if not box.Parent or not root.Parent then
            connRender:Disconnect()
            return
        end

        local hp     = humanoid.Health
        local maxhp  = humanoid.MaxHealth
        local ratio  = maxhp > 0 and math.clamp(hp / maxhp, 0, 1) or 0
        local dist   = math.floor((Camera.CFrame.Position - root.Position).Magnitude)

        -- HP bar fill + warna
        hpFill.Size          = UDim2.new(ratio, 0, 1, 0)
        hpFill.BackgroundColor3 = Color3.fromRGB(
            math.floor(255 * (1 - ratio)),
            math.floor(255 * ratio),
            50
        )

        -- Info teks
        local parts = {}
        if Config.ShowHealth then
            table.insert(parts, math.floor(hp) .. "/" .. math.floor(maxhp) .. " HP")
        end
        if Config.ShowDistance then table.insert(parts, dist .. "m") end
        infoLabel.Text = table.concat(parts, "  ·  ")
    end)

    -- Damage number + hit effect
    local lastHP = humanoid.Health
    humanoid.HealthChanged:Connect(function(newHP)
        local dmg = math.floor(lastHP - newHP)
        lastHP = newHP
        if dmg <= 0 then return end
        showDamageNumber(root, dmg)
        showHitEffect(root.Position)
    end)

    -- Cleanup
    humanoid.Died:Connect(function()
        connRender:Disconnect()
        task.delay(4, function()
            removeHitbox(character)
            removeTracer(character)
        end)
    end)
    character.AncestryChanged:Connect(function(_, parent)
        if not parent then
            connRender:Disconnect()
            removeHitbox(character)
            removeTracer(character)
        end
    end)
end

-- ══════════════════════════════════════════
--           TOGGLE & REFRESH
-- ══════════════════════════════════════════

local function refreshAll()
    for character in pairs(registry) do removeHitbox(character) end
    for character in pairs(tracerFrames) do removeTracer(character) end

    for _, player in ipairs(Players:GetPlayers()) do
        if player.Character then
            local isSelf = player == LP
            local color  = isSelf and Config.SelfColor or Config.EnemyColor
            addHitbox(player.Character, color, isSelf)
        end
    end
end

local function toggleHitbox()
    hitboxEnabled = not hitboxEnabled
    for _, entry in pairs(registry) do
        local box, sel, bb = entry[1], entry[2], entry[3]
        if box and box.Parent then box.Transparency = hitboxEnabled and Config.FillTransp or 1 end
        if sel and sel.Parent then sel.Visible = hitboxEnabled end
        if bb  and bb.Parent  then bb.Enabled  = hitboxEnabled end
    end
    RowHitbox.Text       = hitboxEnabled and "ON" or "OFF"
    RowHitbox.TextColor3 = hitboxEnabled and Color3.fromRGB(60, 255, 100) or Color3.fromRGB(255, 80, 80)
    showToast("Hitbox  " .. (hitboxEnabled and "ON" or "OFF"),
        hitboxEnabled and Color3.fromRGB(20, 80, 30) or Color3.fromRGB(80, 20, 20))
end

local function cycleSize()
    Config.SizeIndex = (Config.SizeIndex % #Config.Sizes) + 1
    RowSize.Text     = Config.SizeIndex == 1 and "Tight" or Config.SizeIndex == 2 and "Normal" or "Wide"
    showToast("Size → " .. RowSize.Text, Color3.fromRGB(20, 50, 90))
    refreshAll()
end

local function toggleDamageNum()
    Config.ShowDamageNum = not Config.ShowDamageNum
    Config.ShowHitEffect = Config.ShowDamageNum
    RowDmgNum.Text       = Config.ShowDamageNum and "ON" or "OFF"
    RowDmgNum.TextColor3 = Config.ShowDamageNum and Color3.fromRGB(60, 255, 100) or Color3.fromRGB(255, 80, 80)
    showToast("Dmg Popup  " .. (Config.ShowDamageNum and "ON" or "OFF"),
        Config.ShowDamageNum and Color3.fromRGB(20, 80, 30) or Color3.fromRGB(80, 20, 20))
end

local function toggleESP()
    Config.ESPEnabled = not Config.ESPEnabled
    setChamsAll(Config.ESPEnabled)
    RowESP.Text       = Config.ESPEnabled and "ON" or "OFF"
    RowESP.TextColor3 = Config.ESPEnabled and Color3.fromRGB(60, 255, 100) or Color3.fromRGB(255, 80, 80)
    showToast("Chams  " .. (Config.ESPEnabled and "ON" or "OFF"),
        Config.ESPEnabled and Color3.fromRGB(20, 80, 30) or Color3.fromRGB(80, 20, 20))
end

local function toggleTracer()
    Config.TracerEnabled = not Config.TracerEnabled
    if not Config.TracerEnabled then
        for _, line in pairs(tracerFrames) do
            if line and line.Parent then line.Visible = false end
        end
    end
    RowTracer.Text       = Config.TracerEnabled and "ON" or "OFF"
    RowTracer.TextColor3 = Config.TracerEnabled and Color3.fromRGB(60, 255, 100) or Color3.fromRGB(255, 80, 80)
    showToast("Tracer  " .. (Config.TracerEnabled and "ON" or "OFF"),
        Config.TracerEnabled and Color3.fromRGB(20, 80, 30) or Color3.fromRGB(80, 20, 20))
end

-- ══════════════════════════════════════════
--           INPUT
-- ══════════════════════════════════════════

UserInputService.InputBegan:Connect(function(input, gp)
    if gp then return end
    if input.KeyCode == Enum.KeyCode.H then toggleHitbox()   end
    if input.KeyCode == Enum.KeyCode.G then cycleSize()      end
    if input.KeyCode == Enum.KeyCode.D then toggleDamageNum() end
    if input.KeyCode == Enum.KeyCode.E then toggleESP()      end
    if input.KeyCode == Enum.KeyCode.T then toggleTracer()   end
end)

-- ══════════════════════════════════════════
--           PLAYER TRACKING
-- ══════════════════════════════════════════

local function onPlayer(player)
    local isSelf = player == LP
    local color  = isSelf and Config.SelfColor or Config.EnemyColor
    local function onChar(char)
        task.delay(0.4, function() addHitbox(char, color, isSelf) end)
    end
    if player.Character then onChar(player.Character) end
    player.CharacterAdded:Connect(onChar)
end

for _, p in ipairs(Players:GetPlayers()) do onPlayer(p) end
Players.PlayerAdded:Connect(onPlayer)
Players.PlayerRemoving:Connect(function(p)
    if p.Character then
        removeHitbox(p.Character)
        removeTracer(p.Character)
    end
end)

-- ══════════════════════════════════════════
--           MAIN LOOP
-- ══════════════════════════════════════════

RunService.RenderStepped:Connect(function()
    -- Tracer update
    updateTracers()

    -- FPS
    frameCount = frameCount + 1
    local now  = tick()
    if now - lastFPSTime >= 0.5 then
        local fps = math.floor(frameCount / (now - lastFPSTime))
        RowFPS.Text       = fps .. " fps"
        RowFPS.TextColor3 = fps >= 55
            and Color3.fromRGB(60, 255, 100)
            or fps >= 30
            and Color3.fromRGB(255, 200, 50)
            or Color3.fromRGB(255, 80, 80)
        frameCount  = 0
        lastFPSTime = now
    end

    RowPlayers.Text = #Players:GetPlayers() .. " online"
end)

-- ══════════════════════════════════════════
--           INIT
-- ══════════════════════════════════════════

local ON_C  = Color3.fromRGB(60, 255, 100)
local OFF_C = Color3.fromRGB(255, 80, 80)

RowHitbox.Text       = "ON"  ; RowHitbox.TextColor3  = ON_C
RowSize.Text         = "Normal"
RowDmgNum.Text       = "ON"  ; RowDmgNum.TextColor3   = ON_C
RowESP.Text          = "ON"  ; RowESP.TextColor3       = ON_C
RowTracer.Text       = "ON"  ; RowTracer.TextColor3    = ON_C

showToast("Loaded!  H·G·D·E·T", Color3.fromRGB(20, 60, 110))
print("[HitboxESP] H:hitbox  G:size  D:dmg  E:chams  T:tracer")
