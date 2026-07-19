-- VisibleHitbox | Combat Testing Script
-- Untuk testing di private server game sendiri
-- Toggle: H = Hitbox | G = Hitbox Size | F = FPS Counter

local Players          = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local RunService       = game:GetService("RunService")
local TweenService     = game:GetService("TweenService")

local LP = Players.LocalPlayer
local Camera = workspace.CurrentCamera

-- ══════════════════════════════════════════
--              KONFIGURASI
-- ══════════════════════════════════════════

local Config = {
    -- Hitbox visual
    EnemyColor    = Color3.fromRGB(255, 60,  60),   -- merah = musuh
    SelfColor     = Color3.fromRGB(60,  255, 100),  -- hijau = diri sendiri
    LineThickness = 0.05,
    SurfaceTransp = 0.80,
    FillTransp    = 0.55,

    -- Ukuran hitbox (bisa diganti via G key)
    Sizes = {
        Vector3.new(3.5, 5.5, 2),   -- Tight (akurat)
        Vector3.new(5,   6,   3),   -- Normal
        Vector3.new(7,   7,   5),   -- Wide (buat testing range)
    },
    SizeIndex = 1,

    -- Fitur
    ShowName      = true,
    ShowHealth    = true,
    ShowDistance  = true,
    ShowFPS       = true,
}

-- ══════════════════════════════════════════
--              STATE
-- ══════════════════════════════════════════

local hitboxEnabled = true
local registry      = {}   -- [character] = { parts }
local fpsValues     = {}
local frameCount    = 0
local lastFPSTime   = tick()

-- ══════════════════════════════════════════
--              GUI SETUP
-- ══════════════════════════════════════════

-- Cleanup old GUI jika ada
if LP.PlayerGui:FindFirstChild("HitboxTestUI") then
    LP.PlayerGui:FindFirstChild("HitboxTestUI"):Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name           = "HitboxTestUI"
ScreenGui.ResetOnSpawn   = false
ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
ScreenGui.Parent         = LP.PlayerGui

-- Panel utama (kiri atas)
local Panel = Instance.new("Frame")
Panel.Name               = "Panel"
Panel.Size               = UDim2.new(0, 220, 0, 160)
Panel.Position           = UDim2.new(0, 12, 0, 12)
Panel.BackgroundColor3   = Color3.fromRGB(10, 10, 10)
Panel.BackgroundTransparency = 0.3
Panel.BorderSizePixel    = 0
Panel.Parent             = ScreenGui
Instance.new("UICorner", Panel).CornerRadius = UDim.new(0, 10)

local Stroke = Instance.new("UIStroke")
Stroke.Color     = Color3.fromRGB(255, 60, 60)
Stroke.Thickness = 1.5
Stroke.Parent    = Panel

local Title = Instance.new("TextLabel")
Title.Size            = UDim2.new(1, 0, 0, 32)
Title.BackgroundColor3 = Color3.fromRGB(255, 60, 60)
Title.BackgroundTransparency = 0
Title.BorderSizePixel = 0
Title.Text            = "  HITBOX TESTER"
Title.TextColor3      = Color3.fromRGB(255, 255, 255)
Title.Font            = Enum.Font.GothamBold
Title.TextSize        = 13
Title.TextXAlignment  = Enum.TextXAlignment.Left
Title.Parent          = Panel
Instance.new("UICorner", Title).CornerRadius = UDim.new(0, 10)

local function makeRow(yPos, label)
    local row = Instance.new("Frame")
    row.Size                     = UDim2.new(1, -16, 0, 24)
    row.Position                 = UDim2.new(0, 8, 0, yPos)
    row.BackgroundTransparency   = 1
    row.Parent                   = Panel

    local lbl = Instance.new("TextLabel")
    lbl.Size            = UDim2.new(0.55, 0, 1, 0)
    lbl.BackgroundTransparency = 1
    lbl.Text            = label
    lbl.TextColor3      = Color3.fromRGB(180, 180, 180)
    lbl.Font            = Enum.Font.Gotham
    lbl.TextSize        = 12
    lbl.TextXAlignment  = Enum.TextXAlignment.Left
    lbl.Parent          = row

    local val = Instance.new("TextLabel")
    val.Size            = UDim2.new(0.45, 0, 1, 0)
    val.Position        = UDim2.new(0.55, 0, 0, 0)
    val.BackgroundTransparency = 1
    val.Text            = "-"
    val.TextColor3      = Color3.fromRGB(255, 255, 255)
    val.Font            = Enum.Font.GothamBold
    val.TextSize        = 12
    val.TextXAlignment  = Enum.TextXAlignment.Right
    val.Parent          = row

    return val
end

local RowHitbox   = makeRow(38,  "[H] Hitbox")
local RowSize     = makeRow(64,  "[G] Size")
local RowPlayers  = makeRow(90,  "Players")
local RowFPS      = makeRow(116, "FPS")
local RowPing     = makeRow(140, "Ping")  -- row ini di luar frame kalau size 160, let me fix

-- Fix: jadikan panel lebih tinggi
Panel.Size = UDim2.new(0, 220, 0, 170)

-- Toast notification
local Toast = Instance.new("Frame")
Toast.Name                  = "Toast"
Toast.Size                  = UDim2.new(0, 280, 0, 40)
Toast.Position              = UDim2.new(0.5, -140, 0, 12)
Toast.BackgroundColor3      = Color3.fromRGB(10, 10, 10)
Toast.BackgroundTransparency = 0.2
Toast.BorderSizePixel       = 0
Toast.Visible               = false
Toast.Parent                = ScreenGui
Instance.new("UICorner", Toast).CornerRadius = UDim.new(0, 10)

local ToastLabel = Instance.new("TextLabel")
ToastLabel.Size              = UDim2.new(1, 0, 1, 0)
ToastLabel.BackgroundTransparency = 1
ToastLabel.TextColor3        = Color3.fromRGB(255, 255, 255)
ToastLabel.Font              = Enum.Font.GothamBold
ToastLabel.TextSize          = 14
ToastLabel.Parent            = Toast

local toastThread
local function showToast(text, color)
    ToastLabel.Text          = text
    Toast.BackgroundColor3   = color or Color3.fromRGB(30, 30, 30)
    Toast.Visible            = true

    if toastThread then task.cancel(toastThread) end
    toastThread = task.delay(2.5, function()
        Toast.Visible = false
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
    if not root then
        root = character:WaitForChild("HumanoidRootPart", 5)
    end
    if not root then return end

    local humanoid = character:FindFirstChildWhichIsA("Humanoid")
    if not humanoid or humanoid.Health <= 0 then return end

    local size = Config.Sizes[Config.SizeIndex]

    -- Main hitbox part
    local box = Instance.new("Part")
    box.Name              = "HB_Visual"
    box.Size              = size
    box.Color             = color
    box.Material          = Enum.Material.Neon
    box.Transparency      = hitboxEnabled and Config.FillTransp or 1
    box.CanCollide        = false
    box.CanTouch          = false
    box.CanQuery          = false
    box.Anchored          = false
    box.CastShadow        = false
    box.Parent            = character

    local weld = Instance.new("WeldConstraint")
    weld.Part0  = root
    weld.Part1  = box
    weld.Parent = box
    box.CFrame  = root.CFrame + Vector3.new(0, 0.25, 0)

    -- Wireframe outline
    local sel = Instance.new("SelectionBox")
    sel.Adornee             = box
    sel.Color3              = color
    sel.LineThickness       = Config.LineThickness
    sel.SurfaceColor3       = color
    sel.SurfaceTransparency = Config.SurfaceTransp
    sel.Visible             = hitboxEnabled
    sel.Parent              = box

    -- BillboardGui (nama + HP + jarak)
    local billboard = Instance.new("BillboardGui")
    billboard.Name           = "HB_Billboard"
    billboard.Adornee        = root
    billboard.Size           = UDim2.new(0, 160, 0, 52)
    billboard.StudsOffset    = Vector3.new(0, 3.5, 0)
    billboard.AlwaysOnTop    = true
    billboard.Enabled        = hitboxEnabled
    billboard.Parent         = character

    local nameLabel = Instance.new("TextLabel")
    nameLabel.Size              = UDim2.new(1, 0, 0.5, 0)
    nameLabel.BackgroundTransparency = 1
    nameLabel.Text              = character.Name
    nameLabel.TextColor3        = color
    nameLabel.Font              = Enum.Font.GothamBold
    nameLabel.TextSize          = 14
    nameLabel.TextStrokeTransparency = 0.5
    nameLabel.Parent            = billboard

    local infoLabel = Instance.new("TextLabel")
    infoLabel.Name              = "Info"
    infoLabel.Size              = UDim2.new(1, 0, 0.5, 0)
    infoLabel.Position          = UDim2.new(0, 0, 0.5, 0)
    infoLabel.BackgroundTransparency = 1
    infoLabel.TextColor3        = Color3.fromRGB(220, 220, 220)
    infoLabel.Font              = Enum.Font.Gotham
    infoLabel.TextSize          = 12
    infoLabel.TextStrokeTransparency = 0.6
    infoLabel.Parent            = billboard

    registry[character] = { box, sel, billboard }

    -- Update HP + distance setiap frame
    local conn
    conn = RunService.RenderStepped:Connect(function()
        if not box.Parent or not root.Parent then
            conn:Disconnect()
            return
        end

        local hp   = math.floor(humanoid.Health)
        local maxhp = math.floor(humanoid.MaxHealth)
        local dist = math.floor((Camera.CFrame.Position - root.Position).Magnitude)

        local parts = {}
        if Config.ShowHealth   then table.insert(parts, "HP " .. hp .. "/" .. maxhp) end
        if Config.ShowDistance then table.insert(parts, dist .. "m") end
        infoLabel.Text = table.concat(parts, "  |  ")
    end)

    -- Cleanup saat mati
    humanoid.Died:Connect(function()
        if conn then conn:Disconnect() end
        task.delay(4, function() removeHitbox(character) end)
    end)

    character.AncestryChanged:Connect(function(_, parent)
        if not parent then
            if conn then conn:Disconnect() end
            removeHitbox(character)
        end
    end)
end

-- ══════════════════════════════════════════
--           TOGGLE & REFRESH
-- ══════════════════════════════════════════

local function refreshAll()
    for character in pairs(registry) do
        removeHitbox(character)
    end
    if not hitboxEnabled then return end

    for _, player in ipairs(Players:GetPlayers()) do
        local char = player.Character
        if char then
            local color = player == LP and Config.SelfColor or Config.EnemyColor
            addHitbox(char, color)
        end
    end
end

local function toggleHitbox()
    hitboxEnabled = not hitboxEnabled
    for character, entry in pairs(registry) do
        local box = entry[1]
        local sel = entry[2]
        local bb  = entry[3]
        if box and box.Parent then
            box.Transparency = hitboxEnabled and Config.FillTransp or 1
        end
        if sel and sel.Parent then sel.Visible = hitboxEnabled end
        if bb  and bb.Parent  then bb.Enabled  = hitboxEnabled end
    end
    RowHitbox.Text     = hitboxEnabled and "ON" or "OFF"
    RowHitbox.TextColor3 = hitboxEnabled
        and Color3.fromRGB(60, 255, 100)
        or  Color3.fromRGB(255, 80, 80)

    showToast(
        hitboxEnabled and "Hitbox  ON" or "Hitbox  OFF",
        hitboxEnabled
            and Color3.fromRGB(20, 80, 30)
            or  Color3.fromRGB(80, 20, 20)
    )
end

local function cycleSize()
    Config.SizeIndex = (Config.SizeIndex % #Config.Sizes) + 1
    local s = Config.Sizes[Config.SizeIndex]
    RowSize.Text = Config.SizeIndex == 1 and "Tight"
        or Config.SizeIndex == 2 and "Normal"
        or "Wide"
    showToast("Hitbox Size → " .. RowSize.Text, Color3.fromRGB(20, 50, 90))
    refreshAll()
end

-- ══════════════════════════════════════════
--           INPUT HANDLER
-- ══════════════════════════════════════════

UserInputService.InputBegan:Connect(function(input, gp)
    if gp then return end
    if input.KeyCode == Enum.KeyCode.H then toggleHitbox() end
    if input.KeyCode == Enum.KeyCode.G then cycleSize() end
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
--           HUD UPDATE LOOP
-- ══════════════════════════════════════════

RunService.RenderStepped:Connect(function()
    -- FPS counter
    frameCount = frameCount + 1
    local now  = tick()
    if now - lastFPSTime >= 0.5 then
        local fps = math.floor(frameCount / (now - lastFPSTime))
        RowFPS.Text      = fps .. " fps"
        RowFPS.TextColor3 = fps >= 55
            and Color3.fromRGB(60, 255, 100)
            or fps >= 30
            and Color3.fromRGB(255, 200, 50)
            or Color3.fromRGB(255, 80, 80)
        frameCount  = 0
        lastFPSTime = now
    end

    -- Player count
    local count = #Players:GetPlayers()
    RowPlayers.Text = count .. " online"

    -- Ping
    local stats = LP:FindFirstChild("PlayerGui")
        and LP:FindFirstChildOfClass("PlayerScripts")
    -- Estimasi ping via workspace DistributedGameTime jika tidak ada stats object
    RowPing.Text = tostring(math.floor(workspace:GetServerTimeNow() % 1 * 0 +
        (game:GetService("Stats").Network.ServerStatsItem["Data Ping"] and
         game:GetService("Stats").Network.ServerStatsItem["Data Ping"]:GetValue() or 0)
    )) .. " ms"
end)

-- ══════════════════════════════════════════
--           INIT
-- ══════════════════════════════════════════

RowHitbox.Text      = "ON"
RowHitbox.TextColor3 = Color3.fromRGB(60, 255, 100)
RowSize.Text        = "Normal"
Config.SizeIndex    = 2

showToast("Hitbox Tester loaded! [H] toggle  [G] size", Color3.fromRGB(20, 60, 100))
print("[HitboxTester] Loaded — H: toggle | G: cycle size")
