-- Custom Crosshair | XC Hub
-- Delta Android Compatible
-- loadstring(game:HttpGet("RAW_URL"))()

local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Camera = workspace.CurrentCamera

-- ┌─────────────────────────┐
-- │         CONFIG          │
-- └─────────────────────────┘
local Config = {
    -- Style: "Cross" | "Dot" | "Circle" | "CrossDot" | "TShape"
    Style        = "CrossDot",

    Color        = Color3.fromRGB(255, 255, 255),  -- warna utama
    OutlineColor = Color3.fromRGB(0, 0, 0),        -- warna outline
    Outline      = true,                            -- outline on/off

    Size         = 10,   -- panjang garis (px)
    Thickness    = 1.5,  -- ketebalan garis
    Gap          = 4,    -- jarak garis dari tengah
    DotRadius    = 2,    -- ukuran dot tengah
    CircleRadius = 18,   -- radius kalau pake style Circle
}

-- ┌─────────────────────────┐
-- │       DRAWING OBJECTS   │
-- └─────────────────────────┘
local function newLine(color, thick)
    local d = Drawing.new("Line")
    d.Color     = color
    d.Thickness = thick
    d.Visible   = false
    return d
end
local function newCircle(color, thick, filled, radius)
    local d = Drawing.new("Circle")
    d.Color     = color
    d.Thickness = thick or 1
    d.Filled    = filled or false
    d.Radius    = radius or 5
    d.Visible   = false
    return d
end

-- Cross lines (8 = 4 outline + 4 main)
local OL = Config.Thickness + 2  -- outline thickness
local crossLines = {
    -- outline (digambar duluan / di belakang)
    oTop    = newLine(Config.OutlineColor, OL),
    oBot    = newLine(Config.OutlineColor, OL),
    oLeft   = newLine(Config.OutlineColor, OL),
    oRight  = newLine(Config.OutlineColor, OL),
    -- main
    top     = newLine(Config.Color, Config.Thickness),
    bot     = newLine(Config.Color, Config.Thickness),
    left    = newLine(Config.Color, Config.Thickness),
    right   = newLine(Config.Color, Config.Thickness),
}

-- Dot
local dotOut = newCircle(Config.OutlineColor, 1, true, Config.DotRadius + 1.5)
local dot    = newCircle(Config.Color, 1, true, Config.DotRadius)

-- Circle outline
local circleOut = newCircle(Config.OutlineColor, Config.Thickness + 1.5, false, Config.CircleRadius)
local circle    = newCircle(Config.Color, Config.Thickness, false, Config.CircleRadius)

-- T-Shape (top kiri kanan, no bottom)
local tLines = {
    oTop   = newLine(Config.OutlineColor, OL),
    oLeft  = newLine(Config.OutlineColor, OL),
    oRight = newLine(Config.OutlineColor, OL),
    top    = newLine(Config.Color, Config.Thickness),
    left   = newLine(Config.Color, Config.Thickness),
    right  = newLine(Config.Color, Config.Thickness),
}

local allObjects = {
    crossLines.oTop, crossLines.oBot, crossLines.oLeft, crossLines.oRight,
    crossLines.top, crossLines.bot, crossLines.left, crossLines.right,
    dotOut, dot, circleOut, circle,
    tLines.oTop, tLines.oLeft, tLines.oRight,
    tLines.top, tLines.left, tLines.right,
}

local function hideAll()
    for _, o in ipairs(allObjects) do o.Visible = false end
end

-- ┌─────────────────────────┐
-- │       RENDER LOGIC      │
-- └─────────────────────────┘
local function drawCrosshair()
    local vp  = Camera.ViewportSize
    local cx  = vp.X / 2
    local cy  = vp.Y / 2
    local g   = Config.Gap
    local s   = Config.Size
    local ol  = Config.Outline
    local ctr = Vector2.new(cx, cy)

    hideAll()

    local style = Config.Style

    -- === CROSS ===
    if style == "Cross" or style == "CrossDot" then
        -- outline
        if ol then
            crossLines.oTop.From=Vector2.new(cx,cy-g-s)   ; crossLines.oTop.To=Vector2.new(cx,cy-g)   ; crossLines.oTop.Visible=true
            crossLines.oBot.From=Vector2.new(cx,cy+g)     ; crossLines.oBot.To=Vector2.new(cx,cy+g+s) ; crossLines.oBot.Visible=true
            crossLines.oLeft.From=Vector2.new(cx-g-s,cy)  ; crossLines.oLeft.To=Vector2.new(cx-g,cy)  ; crossLines.oLeft.Visible=true
            crossLines.oRight.From=Vector2.new(cx+g,cy)   ; crossLines.oRight.To=Vector2.new(cx+g+s,cy); crossLines.oRight.Visible=true
        end
        -- main
        crossLines.top.From=Vector2.new(cx,cy-g-s)   ; crossLines.top.To=Vector2.new(cx,cy-g)    ; crossLines.top.Visible=true
        crossLines.bot.From=Vector2.new(cx,cy+g)     ; crossLines.bot.To=Vector2.new(cx,cy+g+s)  ; crossLines.bot.Visible=true
        crossLines.left.From=Vector2.new(cx-g-s,cy)  ; crossLines.left.To=Vector2.new(cx-g,cy)   ; crossLines.left.Visible=true
        crossLines.right.From=Vector2.new(cx+g,cy)   ; crossLines.right.To=Vector2.new(cx+g+s,cy); crossLines.right.Visible=true
    end

    -- === DOT ===
    if style == "Dot" or style == "CrossDot" then
        if ol then dotOut.Position=ctr ; dotOut.Visible=true end
        dot.Position=ctr ; dot.Visible=true
    end

    -- === CIRCLE ===
    if style == "Circle" then
        if ol then circleOut.Position=ctr ; circleOut.Visible=true end
        circle.Position=ctr ; circle.Visible=true
    end

    -- === T-SHAPE (no bottom line) ===
    if style == "TShape" then
        if ol then
            tLines.oTop.From=Vector2.new(cx,cy-g-s)  ; tLines.oTop.To=Vector2.new(cx,cy-g)   ; tLines.oTop.Visible=true
            tLines.oLeft.From=Vector2.new(cx-g-s,cy) ; tLines.oLeft.To=Vector2.new(cx-g,cy)  ; tLines.oLeft.Visible=true
            tLines.oRight.From=Vector2.new(cx+g,cy)  ; tLines.oRight.To=Vector2.new(cx+g+s,cy); tLines.oRight.Visible=true
        end
        tLines.top.From=Vector2.new(cx,cy-g-s)  ; tLines.top.To=Vector2.new(cx,cy-g)    ; tLines.top.Visible=true
        tLines.left.From=Vector2.new(cx-g-s,cy) ; tLines.left.To=Vector2.new(cx-g,cy)   ; tLines.left.Visible=true
        tLines.right.From=Vector2.new(cx+g,cy)  ; tLines.right.To=Vector2.new(cx+g+s,cy); tLines.right.Visible=true
    end
end

-- ┌─────────────────────────┐
-- │       STYLE PICKER GUI  │
-- └─────────────────────────┘
local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name           = "CrosshairGUI"
ScreenGui.ResetOnSpawn   = false
ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
ScreenGui.Parent         = game:GetService("CoreGui")

-- Kecil floating panel kiri bawah
local Panel = Instance.new("Frame", ScreenGui)
Panel.Size             = UDim2.new(0, 160, 0, 172)
Panel.Position         = UDim2.new(0, 10, 1, -182)
Panel.BackgroundColor3 = Color3.fromRGB(8, 5, 20)
Panel.BorderSizePixel  = 0
Instance.new("UICorner", Panel).CornerRadius = UDim.new(0, 10)
local pStroke = Instance.new("UIStroke", Panel)
pStroke.Color = Color3.fromRGB(130, 40, 220) ; pStroke.Thickness = 1.5

local PTitle = Instance.new("TextLabel", Panel)
PTitle.Size=UDim2.new(1,0,0,28) ; PTitle.BackgroundTransparency=1
PTitle.Text="✴ Crosshair" ; PTitle.TextColor3=Color3.fromRGB(185,90,255)
PTitle.TextSize=12 ; PTitle.Font=Enum.Font.GothamBold

local styles = {"CrossDot", "Cross", "Dot", "Circle", "TShape"}
local styleList = Instance.new("Frame", Panel)
styleList.Size=UDim2.new(1,-12,1,-34) ; styleList.Position=UDim2.new(0,6,0,30)
styleList.BackgroundTransparency=1
local sLayout = Instance.new("UIListLayout", styleList)
sLayout.Padding=UDim.new(0,4) ; sLayout.SortOrder=Enum.SortOrder.LayoutOrder

local styleBtns = {}
for i, sname in ipairs(styles) do
    local btn = Instance.new("TextButton", styleList)
    btn.Size             = UDim2.new(1, 0, 0, 24)
    btn.BackgroundColor3 = sname == Config.Style
        and Color3.fromRGB(130, 40, 220)
        or  Color3.fromRGB(20, 12, 46)
    btn.BorderSizePixel  = 0
    btn.Text             = sname
    btn.TextColor3       = Color3.fromRGB(220, 200, 255)
    btn.TextSize         = 11
    btn.Font             = Enum.Font.GothamBold
    btn.LayoutOrder      = i
    Instance.new("UICorner", btn).CornerRadius = UDim.new(0, 6)
    styleBtns[sname] = btn

    btn.MouseButton1Click:Connect(function()
        Config.Style = sname
        -- Reset semua button color
        for _, b in next, styleBtns do
            TweenService:Create(b, TweenInfo.new(0.15), {
                BackgroundColor3 = Color3.fromRGB(20, 12, 46)
            }):Play()
        end
        TweenService:Create(btn, TweenInfo.new(0.15), {
            BackgroundColor3 = Color3.fromRGB(130, 40, 220)
        }):Play()
    end)
end

-- ┌─────────────────────────┐
-- │      RENDER LOOP        │
-- └─────────────────────────┘
RunService.RenderStepped:Connect(drawCrosshair)

print("[Crosshair] Loaded! Style: " .. Config.Style)
