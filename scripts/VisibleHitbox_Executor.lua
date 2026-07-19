-- VisibleHitbox | Combat Testing Script
-- Untuk testing di private server game sendiri
-- [H] Hitbox toggle | [G] Ukuran hitbox | [D] Damage popup toggle

local Players          = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local RunService       = game:GetService("RunService")
local TweenService     = game:GetService("TweenService")

local LP     = Players.LocalPlayer
local Camera = workspace.CurrentCamera

-- ══════════════════════════════════════════
--              KONFIGURASI
-- ══════════════════════════════════════════

local Config = {
    EnemyColor    = Color3.fromRGB(255, 60,  60),
    SelfColor     = Color3.fromRGB(60,  255, 100),
    LineThickness = 0.05,
    SurfaceTransp = 0.80,
    FillTransp    = 0.55,

    Sizes = {
        Vector3.new(3.5, 5.5, 2),  -- Tight
        Vector3.new(5,   6,   3),  -- Normal
        Vector3.new(7,   7,   5),  -- Wide
    },
    SizeIndex = 2,

    ShowHealth    = true,
    ShowDistance  = true,
    ShowDamageNum = true,
    ShowHitEffect = true,
}

-- ══════════════════════════════════════════
--              STATE
-- ══════════════════════════════════════════

local hitboxEnabled = true
local registry      = {}
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

local Panel = Instance.new("Frame")
Panel.Name                   = "Panel"
Panel.Size                   = UDim2.new(0, 220, 0, 220)
Panel.Position               = UDim2.new(0, 12, 0, 12)
Panel.BackgroundColor3       = Color3.fromRGB(10, 10, 10)
Panel.BackgroundTransparency = 0.3
Panel.BorderSizePixel        = 0
Panel.Parent                 = ScreenGui
Instance.new("UICorner", Panel).CornerRadius = UDim.new(0, 10)

local Stroke = Instance.new("UIStroke")
Stroke.Color     = Color3.fromRGB(255, 60, 60)
Stroke.Thickness = 1.5
Stroke.Parent    = Panel

local Title = Instance.new("TextLabel")
Title.Size                 = UDim2.new(1, 0, 0, 32)
Title.BackgroundColor3     = Color3.fromRGB(255, 60, 60)
Title.BackgroundTransparency = 0
Title.BorderSizePixel      = 0
Title.Text                 = "  HITBOX TESTER"
Title.TextColor3           = Color3.fromRGB(255, 255, 255)
Title.Font                 = Enum.Font.GothamBold
Title.TextSize             = 13
Title.TextXAlignment       = Enum.TextXAlignment.Left
Title.Parent               = Panel
Instance.new("UICorner", Title).CornerRadius = UDim.new(0, 10)

local function makeRow(yPos, label)
    local row = Instance.new("Frame")
    row.Size                   = UDim2.new(1, -16, 0, 24)
    row.Position               = UDim2.new(0, 8, 0, yPos)
    row.BackgroundTransparency = 1
    row.Parent                 = Panel

    local lbl = Instance.new("TextLabel")
    lbl.Size                   = UDim2.new(0.6, 0, 1, 0)
    lbl.BackgroundTransparency = 1
    lbl.Text                   = label
    lbl.TextColor3             = Color3.fromRGB(160, 160, 160)
    lbl.Font                   = Enum.Font.Gotham
    lbl.TextSize               = 12
    lbl.TextXAlignment         = Enum.TextXAlignment.Left
    lbl.Parent                 = row

    local val = Instance.new("TextLabel")
    val.Size                   = UDim2.new(0.4, 0, 1, 0)
    val.Position               = UDim2.new(0.6, 0, 0, 0)
    val.BackgroundTransparency = 1
    val.Text                   = "-"
    val.TextColor3             = Color3.fromRGB(255, 255, 255)
    val.Font                   = Enum.Font.GothamBold
    val.TextSize               = 12
    val.TextXAlignment         = Enum.TextXAlignment.Right
    val.Parent                 = row

    return val
end

local RowHitbox  = makeRow(38,  "[H] Hitbox")
local RowSize    = makeRow(64,  "[G] Size")
local RowDmgNum  = makeRow(90,  "[D] Dmg Popup")
local RowPlayers = makeRow(116, "Players")
local RowFPS     = makeRow(142, "FPS")
local RowPing    = makeRow(168, "Ping")

-- Toast
local Toast = Instance.new("Frame")
Toast.Name                   = "Toast"
Toast.Size                   = UDim2.new(0, 300, 0, 40)
Toast.Position               = UDim2.new(0.5, -150, 0, 12)
Toast.BackgroundColor3       = Color3.fromRGB(10, 10, 10)
Toast.BackgroundTransparency = 0.2
Toast.BorderSizePixel        = 0
Toast.Visible                = false
Toast.Parent                 = ScreenGui
Instance.new("UICorner", Toast).CornerRadius = UDim.new(0, 10)

local ToastLabel = Instance.new("TextLabel")
ToastLabel.Size                   = UDim2.new(1, 0, 1, 0)
ToastLabel.BackgroundTransparency = 1
ToastLabel.TextColor3             = Color3.fromRGB(255, 255, 255)
ToastLabel.Font                   = Enum.Font.GothamBold
ToastLabel.TextSize               = 14
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
    [1]   = Color3.fromRGB(220, 220, 220),  -- putih  : damage kecil
    [50]  = Color3.fromRGB(255, 200, 50),   -- kuning : damage sedang
    [100] = Color3.fromRGB(255, 80,  50),   -- oranye : damage besar
    [150] = Color3.fromRGB(200, 50,  255),  -- ungu   : damage brutal
}

local function getDmgColor(dmg)
    if dmg >= 150 then return DMG_COLORS[150]
    elseif dmg >= 100 then return DMG_COLORS[100]
    elseif dmg >= 50  then return DMG_COLORS[50]
    else return DMG_COLORS[1] end
end

local function showDamageNumber(root, dmg)
    if not Config.ShowDamageNum then return end
    if not root or not root.Parent then return end

    local bb = Instance.new("BillboardGui")
    bb.Adornee    = root
    bb.Size       = UDim2.new(0, 90, 0, 45)
    -- Offset acak biar angka tidak tumpuk kalau kena multi-hit
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
    lbl.Parent                 = lbl.Parent or bb  -- langsung parent ke bb
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
        -- Float ke atas
        bb.StudsOffset = startOffset + Vector3.new(0, t * 3.5, 0)
        -- Fade mulai dari 0.4s
        local alpha = math.clamp((t - 0.4) / 0.45, 0, 1)
        lbl.TextTransparency       = alpha
        lbl.TextStrokeTransparency = 0.3 + alpha * 0.7
    end)
end

-- ══════════════════════════════════════════
--            HIT EFFECT (ringan)
-- ══════════════════════════════════════════

local function showHitEffect(position)
    if not Config.ShowHitEffect then return end

    -- Ring kecil yang expand + fade — zero physics, zero shadow
    local ring = Instance.new("Part")
    ring.Shape       = Enum.PartType.Ball
    ring.Size        = Vector3.new(0.6, 0.6, 0.6)
    ring.CFrame      = CFrame.new(position + Vector3.new(
        math.random(-10, 10) * 0.1,
        math.random(0, 15) * 0.1,
        math.random(-10, 10) * 0.1
    ))
    ring.Anchored    = true
    ring.CanCollide  = false
    ring.CanTouch    = false
    ring.CanQuery    = false
    ring.CastShadow  = false
    ring.Material    = Enum.Material.Neon
    ring.Color       = Color3.fromRGB(255, 210, 60)
    ring.Transparency = 0.1
    ring.Parent      = workspace

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

local function addHitbox(character, color)
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

    -- Billboard HP + jarak
    local billboard = Instance.new("BillboardGui")
    billboard.Name        = "HB_Billboard"
    billboard.Adornee     = root
    billboard.Size        = UDim2.new(0, 160, 0, 52)
    billboard.StudsOffset = Vector3.new(0, 3.5, 0)
    billboard.AlwaysOnTop = true
    billboard.Enabled     = hitboxEnabled
    billboard.Parent      = character

    local nameLabel = Instance.new("TextLabel")
    nameLabel.Size                   = UDim2.new(1, 0, 0.5, 0)
    nameLabel.BackgroundTransparency = 1
    nameLabel.Text                   = character.Name
    nameLabel.TextColor3             = color
    nameLabel.Font                   = Enum.Font.GothamBold
    nameLabel.TextSize               = 14
    nameLabel.TextStrokeTransparency = 0.5
    nameLabel.Parent                 = billboard

    local infoLabel = Instance.new("TextLabel")
    infoLabel.Name                   = "Info"
    infoLabel.Size                   = UDim2.new(1, 0, 0.5, 0)
    infoLabel.Position               = UDim2.new(0, 0, 0.5, 0)
    infoLabel.BackgroundTransparency = 1
    infoLabel.TextColor3             = Color3.fromRGB(210, 210, 210)
    infoLabel.Font                   = Enum.Font.Gotham
    infoLabel.TextSize               = 12
    infoLabel.TextStrokeTransparency = 0.6
    infoLabel.Parent                 = billboard

    registry[character] = { box, sel, billboard }

    -- Update info setiap frame
    local connRender
    connRender = RunService.RenderStepped:Connect(function()
        if not box.Parent or not root.Parent then
            connRender:Disconnect()
            return
        end
        local hp    = math.floor(humanoid.Health)
        local maxhp = math.floor(humanoid.MaxHealth)
        local dist  = math.floor((Camera.CFrame.Position - root.Position).Magnitude)
        local parts = {}
        if Config.ShowHealth   then table.insert(parts, "HP " .. hp .. "/" .. maxhp) end
        if Config.ShowDistance then table.insert(parts, dist .. "m") end
        infoLabel.Text = table.concat(parts, "  |  ")
    end)

    -- ─── Damage number + hit effect via HealthChanged ───
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
        task.delay(4, function() removeHitbox(character) end)
    end)
    character.AncestryChanged:Connect(function(_, parent)
        if not parent then
            connRender:Disconnect()
            removeHitbox(character)
        end
    end)
end

-- ══════════════════════════════════════════
--           TOGGLE & REFRESH
-- ══════════════════════════════════════════

local function refreshAll()
    for character in pairs(registry) do removeHitbox(character) end
    if not hitboxEnabled then return end
    for _, player in ipairs(Players:GetPlayers()) do
        if player.Character then
            local color = player == LP and Config.SelfColor or Config.EnemyColor
            addHitbox(player.Character, color)
        end
    end
end

local function toggleHitbox()
    hitboxEnabled = not hitboxEnabled
    for _, entry in pairs(registry) do
        local box, sel, bb = entry[1], entry[2], entry[3]
        if box and box.Parent then box.Transparency = hitboxEnabled and Config.FillTransp or 1 end
        if sel and sel.Parent then sel.Visible      = hitboxEnabled end
        if bb  and bb.Parent  then bb.Enabled       = hitboxEnabled end
    end
    RowHitbox.Text      = hitboxEnabled and "ON" or "OFF"
    RowHitbox.TextColor3 = hitboxEnabled
        and Color3.fromRGB(60, 255, 100)
        or  Color3.fromRGB(255, 80, 80)
    showToast(hitboxEnabled and "Hitbox  ON" or "Hitbox  OFF",
        hitboxEnabled and Color3.fromRGB(20, 80, 30) or Color3.fromRGB(80, 20, 20))
end

local function cycleSize()
    Config.SizeIndex = (Config.SizeIndex % #Config.Sizes) + 1
    RowSize.Text     = Config.SizeIndex == 1 and "Tight"
        or Config.SizeIndex == 2 and "Normal" or "Wide"
    showToast("Size → " .. RowSize.Text, Color3.fromRGB(20, 50, 90))
    refreshAll()
end

local function toggleDamageNum()
    Config.ShowDamageNum  = not Config.ShowDamageNum
    Config.ShowHitEffect  = Config.ShowDamageNum   -- keduanya satu toggle
    RowDmgNum.Text        = Config.ShowDamageNum and "ON" or "OFF"
    RowDmgNum.TextColor3  = Config.ShowDamageNum
        and Color3.fromRGB(60, 255, 100)
        or  Color3.fromRGB(255, 80, 80)
    showToast("Damage Popup  " .. (Config.ShowDamageNum and "ON" or "OFF"),
        Config.ShowDamageNum and Color3.fromRGB(20, 80, 30) or Color3.fromRGB(80, 20, 20))
end

-- ══════════════════════════════════════════
--           INPUT
-- ══════════════════════════════════════════

UserInputService.InputBegan:Connect(function(input, gp)
    if gp then return end
    if input.KeyCode == Enum.KeyCode.H then toggleHitbox()   end
    if input.KeyCode == Enum.KeyCode.G then cycleSize()      end
    if input.KeyCode == Enum.KeyCode.D then toggleDamageNum() end
end)

-- ══════════════════════════════════════════
--           PLAYER TRACKING
-- ══════════════════════════════════════════

local function onPlayer(player)
    local color = player == LP and Config.SelfColor or Config.EnemyColor
    local function onChar(char)
        task.delay(0.4, function() addHitbox(char, color) end)
    end
    if player.Character then onChar(player.Character) end
    player.CharacterAdded:Connect(onChar)
end

for _, p in ipairs(Players:GetPlayers()) do onPlayer(p) end
Players.PlayerAdded:Connect(onPlayer)
Players.PlayerRemoving:Connect(function(p)
    if p.Character then removeHitbox(p.Character) end
end)

-- ══════════════════════════════════════════
--           HUD UPDATE
-- ══════════════════════════════════════════

RunService.RenderStepped:Connect(function()
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

    local ok, ping = pcall(function()
        return game:GetService("Stats").Network.ServerStatsItem["Data Ping"]:GetValue()
    end)
    RowPing.Text = (ok and math.floor(ping) or "?") .. " ms"
end)

-- ══════════════════════════════════════════
--           INIT
-- ══════════════════════════════════════════

RowHitbox.Text       = "ON"
RowHitbox.TextColor3 = Color3.fromRGB(60, 255, 100)
RowSize.Text         = "Normal"
RowDmgNum.Text       = "ON"
RowDmgNum.TextColor3 = Color3.fromRGB(60, 255, 100)

showToast("Loaded!  [H] hitbox  [G] size  [D] dmg popup", Color3.fromRGB(20, 60, 100))
print("[HitboxTester] Ready — H: hitbox | G: size | D: damage popup")
