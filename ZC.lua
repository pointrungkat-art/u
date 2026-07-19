-- ZC Hub v1.0 | FPS Performance & Experience Booster
-- ESP Enhanced + Aim Assist + Silent Aim + No Recoil + FPS Boost
-- Delta Android Compatible
-- loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/ZC.lua"))()

local Players         = game:GetService("Players")
local RunService      = game:GetService("RunService")
local TweenService    = game:GetService("TweenService")
local UIS             = game:GetService("UserInputService")
local VirtualUser     = game:GetService("VirtualUser")
local Lighting        = game:GetService("Lighting")

local lp     = Players.LocalPlayer
local Camera = workspace.CurrentCamera

local VALID_KEY = "ZCFPS"

local State = {
    ESP       = false,
    Crosshair = false,
    AimAssist = false,
    SilentAim = false,
    NoRecoil  = false,
    FPSBoost  = false,
}

-- ┌─────────────────────────┐
-- │         COLORS          │
-- └─────────────────────────┘
local C = {
    BG      = Color3.fromRGB(5,  10, 22),
    Panel   = Color3.fromRGB(10, 16, 40),
    Row     = Color3.fromRGB(12, 20, 46),
    Accent  = Color3.fromRGB(30,  90, 220),
    Bright  = Color3.fromRGB(80, 160, 255),
    Text    = Color3.fromRGB(200, 215, 255),
    Sub     = Color3.fromRGB(100, 130, 185),
    Off     = Color3.fromRGB(30,  42,  78),
    Success = Color3.fromRGB(70,  220, 130),
    Error   = Color3.fromRGB(255, 65,  90),
    Warn    = Color3.fromRGB(255, 195, 50),
}

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name           = "ZCHub"
ScreenGui.ResetOnSpawn   = false
ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
ScreenGui.Parent         = game:GetService("CoreGui")

-- ┌─────────────────────────┐
-- │        KEY SCREEN       │
-- └─────────────────────────┘
local KeyFrame = Instance.new("Frame")
KeyFrame.Name             = "KeyScreen"
KeyFrame.Size             = UDim2.new(0, 260, 0, 210)
KeyFrame.Position         = UDim2.new(0.5, -130, 0.5, -105)
KeyFrame.BackgroundColor3 = C.BG
KeyFrame.BorderSizePixel  = 0
KeyFrame.Parent           = ScreenGui
Instance.new("UICorner", KeyFrame).CornerRadius = UDim.new(0, 14)

local keyStroke = Instance.new("UIStroke", KeyFrame)
keyStroke.Color     = C.Accent
keyStroke.Thickness = 1.5

local keyLine = Instance.new("Frame", KeyFrame)
keyLine.Size             = UDim2.new(0.5, 0, 0, 2)
keyLine.Position         = UDim2.new(0.25, 0, 0, 0)
keyLine.BackgroundColor3 = C.Bright
keyLine.BorderSizePixel  = 0
Instance.new("UICorner", keyLine).CornerRadius = UDim.new(1, 0)

local keyLogo = Instance.new("TextLabel", KeyFrame)
keyLogo.Size                 = UDim2.new(1, 0, 0, 36)
keyLogo.Position             = UDim2.new(0, 0, 0, 14)
keyLogo.BackgroundTransparency = 1
keyLogo.Text                 = "◈ ZC Hub ◈"
keyLogo.TextColor3           = C.Bright
keyLogo.TextSize             = 20
keyLogo.Font                 = Enum.Font.GothamBold

local keySub = Instance.new("TextLabel", KeyFrame)
keySub.Size                 = UDim2.new(1, 0, 0, 18)
keySub.Position             = UDim2.new(0, 0, 0, 50)
keySub.BackgroundTransparency = 1
keySub.Text                 = "Enter your key to continue"
keySub.TextColor3           = C.Sub
keySub.TextSize             = 11
keySub.Font                 = Enum.Font.Gotham

local keyBox = Instance.new("TextBox", KeyFrame)
keyBox.Size              = UDim2.new(0, 210, 0, 38)
keyBox.Position          = UDim2.new(0.5, -105, 0, 80)
keyBox.BackgroundColor3  = C.Panel
keyBox.BorderSizePixel   = 0
keyBox.Text              = ""
keyBox.PlaceholderText   = "Key..."
keyBox.PlaceholderColor3 = C.Sub
keyBox.TextColor3        = C.Text
keyBox.TextSize          = 14
keyBox.Font              = Enum.Font.GothamBold
keyBox.ClearTextOnFocus  = false
Instance.new("UICorner", keyBox).CornerRadius = UDim.new(0, 8)
Instance.new("UIStroke", keyBox).Color = C.Accent

local submitBtn = Instance.new("TextButton", KeyFrame)
submitBtn.Size             = UDim2.new(0, 210, 0, 38)
submitBtn.Position         = UDim2.new(0.5, -105, 0, 128)
submitBtn.BackgroundColor3 = C.Accent
submitBtn.BorderSizePixel  = 0
submitBtn.Text             = "UNLOCK"
submitBtn.TextColor3       = Color3.fromRGB(255, 255, 255)
submitBtn.TextSize         = 13
submitBtn.Font             = Enum.Font.GothamBold
Instance.new("UICorner", submitBtn).CornerRadius = UDim.new(0, 8)

local keyError = Instance.new("TextLabel", KeyFrame)
keyError.Size                 = UDim2.new(1, 0, 0, 20)
keyError.Position             = UDim2.new(0, 0, 0, 178)
keyError.BackgroundTransparency = 1
keyError.Text                 = ""
keyError.TextColor3           = C.Error
keyError.TextSize             = 11
keyError.Font                 = Enum.Font.Gotham

-- ┌─────────────────────────┐
-- │        MAIN HUB         │
-- └─────────────────────────┘
local MainFrame = Instance.new("Frame")
MainFrame.Name             = "MainHub"
MainFrame.Size             = UDim2.new(0, 230, 0, 530)
MainFrame.Position         = UDim2.new(0.5, -115, 0.5, -265)
MainFrame.BackgroundColor3 = C.BG
MainFrame.BorderSizePixel  = 0
MainFrame.Visible          = false
MainFrame.Parent           = ScreenGui
Instance.new("UICorner", MainFrame).CornerRadius = UDim.new(0, 12)

local mainStroke = Instance.new("UIStroke", MainFrame)
mainStroke.Color     = C.Accent
mainStroke.Thickness = 1.5

local TitleBar = Instance.new("Frame", MainFrame)
TitleBar.Size             = UDim2.new(1, 0, 0, 42)
TitleBar.BackgroundColor3 = C.Panel
TitleBar.BorderSizePixel  = 0
Instance.new("UICorner", TitleBar).CornerRadius = UDim.new(0, 12)

local topLine = Instance.new("Frame", TitleBar)
topLine.Size             = UDim2.new(0.55, 0, 0, 2)
topLine.Position         = UDim2.new(0.225, 0, 0, 0)
topLine.BackgroundColor3 = C.Bright
topLine.BorderSizePixel  = 0
Instance.new("UICorner", topLine).CornerRadius = UDim.new(1, 0)

local TitleLabel = Instance.new("TextLabel", TitleBar)
TitleLabel.Size                 = UDim2.new(1, -44, 1, 0)
TitleLabel.Position             = UDim2.new(0, 12, 0, 0)
TitleLabel.BackgroundTransparency = 1
TitleLabel.Text                 = "◈ ZC Hub v1.0 — FPS"
TitleLabel.TextColor3           = C.Bright
TitleLabel.TextSize             = 13
TitleLabel.Font                 = Enum.Font.GothamBold
TitleLabel.TextXAlignment       = Enum.TextXAlignment.Left

local CloseBtn = Instance.new("TextButton", TitleBar)
CloseBtn.Size             = UDim2.new(0, 26, 0, 26)
CloseBtn.Position         = UDim2.new(1, -32, 0.5, -13)
CloseBtn.BackgroundColor3 = Color3.fromRGB(140, 25, 55)
CloseBtn.Text             = "✕"
CloseBtn.TextColor3       = Color3.fromRGB(255, 255, 255)
CloseBtn.TextSize         = 12
CloseBtn.Font             = Enum.Font.GothamBold
Instance.new("UICorner", CloseBtn).CornerRadius = UDim.new(1, 0)
CloseBtn.MouseButton1Click:Connect(function() ScreenGui:Destroy() end)

-- Draggable
local dragging, dragStart, startPos
TitleBar.InputBegan:Connect(function(i)
    if i.UserInputType == Enum.UserInputType.Touch
    or i.UserInputType == Enum.UserInputType.MouseButton1 then
        dragging = true ; dragStart = i.Position ; startPos = MainFrame.Position
    end
end)
TitleBar.InputChanged:Connect(function(i)
    if dragging and (i.UserInputType == Enum.UserInputType.Touch
    or i.UserInputType == Enum.UserInputType.MouseMovement) then
        local d = i.Position - dragStart
        MainFrame.Position = UDim2.new(startPos.X.Scale, startPos.X.Offset+d.X, startPos.Y.Scale, startPos.Y.Offset+d.Y)
    end
end)
TitleBar.InputEnded:Connect(function(i)
    if i.UserInputType == Enum.UserInputType.Touch
    or i.UserInputType == Enum.UserInputType.MouseButton1 then
        dragging = false
    end
end)

local Content = Instance.new("Frame", MainFrame)
Content.Size                 = UDim2.new(1, -16, 1, -92)
Content.Position             = UDim2.new(0, 8, 0, 48)
Content.BackgroundTransparency = 1
local ULL = Instance.new("UIListLayout", Content)
ULL.Padding   = UDim.new(0, 6)
ULL.SortOrder = Enum.SortOrder.LayoutOrder

local StatusBar = Instance.new("Frame", MainFrame)
StatusBar.Size             = UDim2.new(1, -16, 0, 28)
StatusBar.Position         = UDim2.new(0, 8, 1, -34)
StatusBar.BackgroundColor3 = C.Panel
StatusBar.BorderSizePixel  = 0
Instance.new("UICorner", StatusBar).CornerRadius = UDim.new(0, 6)
local sStroke = Instance.new("UIStroke", StatusBar)
sStroke.Color = C.Off ; sStroke.Thickness = 1

local StatusLabel = Instance.new("TextLabel", StatusBar)
StatusLabel.Size                 = UDim2.new(1, -10, 1, 0)
StatusLabel.Position             = UDim2.new(0, 8, 0, 0)
StatusLabel.BackgroundTransparency = 1
StatusLabel.Text                 = "◈ ZC Hub Ready"
StatusLabel.TextColor3           = C.Bright
StatusLabel.TextSize             = 11
StatusLabel.Font                 = Enum.Font.Gotham
StatusLabel.TextXAlignment       = Enum.TextXAlignment.Left

local function setStatus(text, color)
    StatusLabel.Text       = "◈ " .. text
    StatusLabel.TextColor3 = color or C.Bright
end

local function createToggle(name, desc, order, onToggle, initVal)
    local Row = Instance.new("Frame", Content)
    Row.Size             = UDim2.new(1, 0, 0, 60)
    Row.BackgroundColor3 = C.Row
    Row.BorderSizePixel  = 0
    Row.LayoutOrder      = order
    Instance.new("UICorner", Row).CornerRadius = UDim.new(0, 8)
    local rStroke = Instance.new("UIStroke", Row)
    rStroke.Color = initVal and C.Accent or C.Off ; rStroke.Thickness = 1

    local NameLbl = Instance.new("TextLabel", Row)
    NameLbl.Size=UDim2.new(0.72,0,0,24) ; NameLbl.Position=UDim2.new(0,10,0,8)
    NameLbl.BackgroundTransparency=1 ; NameLbl.Text=name
    NameLbl.TextColor3=C.Text ; NameLbl.TextSize=13
    NameLbl.Font=Enum.Font.GothamBold ; NameLbl.TextXAlignment=Enum.TextXAlignment.Left

    local DescLbl = Instance.new("TextLabel", Row)
    DescLbl.Size=UDim2.new(0.72,0,0,18) ; DescLbl.Position=UDim2.new(0,10,0,32)
    DescLbl.BackgroundTransparency=1 ; DescLbl.Text=desc
    DescLbl.TextColor3=C.Sub ; DescLbl.TextSize=10
    DescLbl.Font=Enum.Font.Gotham ; DescLbl.TextXAlignment=Enum.TextXAlignment.Left

    local TBg = Instance.new("Frame", Row)
    TBg.Size=UDim2.new(0,46,0,25) ; TBg.Position=UDim2.new(1,-56,0.5,-12)
    TBg.BackgroundColor3=initVal and C.Accent or C.Off ; TBg.BorderSizePixel=0
    Instance.new("UICorner", TBg).CornerRadius = UDim.new(1, 0)

    local Circle = Instance.new("Frame", TBg)
    Circle.Size=UDim2.new(0,19,0,19)
    Circle.Position=initVal and UDim2.new(0,24,0.5,-9) or UDim2.new(0,3,0.5,-9)
    Circle.BackgroundColor3=initVal and C.Bright or C.Sub ; Circle.BorderSizePixel=0
    Instance.new("UICorner", Circle).CornerRadius = UDim.new(1, 0)

    local enabled = initVal or false
    local function setToggle(val)
        enabled = val
        TweenService:Create(Circle, TweenInfo.new(0.18), {
            Position=val and UDim2.new(0,24,0.5,-9) or UDim2.new(0,3,0.5,-9),
            BackgroundColor3=val and C.Bright or C.Sub,
        }):Play()
        TweenService:Create(TBg, TweenInfo.new(0.18), {BackgroundColor3=val and C.Accent or C.Off}):Play()
        TweenService:Create(rStroke, TweenInfo.new(0.2), {Color=val and C.Accent or C.Off}):Play()
        onToggle(val)
    end
    TBg.InputBegan:Connect(function(i)
        if i.UserInputType==Enum.UserInputType.Touch
        or i.UserInputType==Enum.UserInputType.MouseButton1 then
            setToggle(not enabled)
        end
    end)
    return setToggle
end

-- ┌─────────────────────────┐
-- │       KEY SYSTEM        │
-- └─────────────────────────┘
local function showHub()
    TweenService:Create(KeyFrame, TweenInfo.new(0.25, Enum.EasingStyle.Quad), {
        Size     = UDim2.new(0, 0, 0, 0),
        Position = UDim2.new(0.5, 0, 0.5, 0),
    }):Play()
    task.wait(0.25)
    KeyFrame:Destroy()
    MainFrame.Size     = UDim2.new(0, 0, 0, 0)
    MainFrame.Position = UDim2.new(0.5, 0, 0.5, 0)
    MainFrame.Visible  = true
    TweenService:Create(MainFrame, TweenInfo.new(0.3, Enum.EasingStyle.Back), {
        Size     = UDim2.new(0, 230, 0, 530),
        Position = UDim2.new(0.5, -115, 0.5, -265),
    }):Play()
    task.wait(2)
    setStatus("ZC Hub Ready")
end

local function checkKey()
    local input = keyBox.Text:upper():gsub("%s", "")
    if input == VALID_KEY then
        keyError.Text       = "✔ Key valid! Loading..."
        keyError.TextColor3 = C.Success
        TweenService:Create(submitBtn, TweenInfo.new(0.2), {BackgroundColor3=C.Success}):Play()
        task.wait(0.5)
        showHub()
    else
        keyError.Text       = "✕ Key salah, coba lagi!"
        keyError.TextColor3 = C.Error
        TweenService:Create(keyStroke, TweenInfo.new(0.1), {Color=C.Error}):Play()
        task.delay(0.15, function()
            TweenService:Create(keyStroke, TweenInfo.new(0.3), {Color=C.Accent}):Play()
        end)
        task.delay(2, function() keyError.Text = "" end)
    end
end

submitBtn.MouseButton1Click:Connect(checkKey)
keyBox.FocusLost:Connect(function(enter) if enter then checkKey() end end)

-- ┌─────────────────────────┐
-- │      ESP ENHANCED       │
-- └─────────────────────────┘
local ESPObjects = {}
local ESPCfg = {
    BoxColor    = Color3.fromRGB(80, 160, 255),
    BoxThick    = 1.5,
    BarColor    = Color3.fromRGB(70, 220, 130),
    BarBg       = Color3.fromRGB(20, 50, 20),
    NameColor   = Color3.fromRGB(200, 215, 255),
    DistColor   = Color3.fromRGB(120, 150, 210),
    MaxDist     = 1200,
}

local function newDraw(t, p)
    local d = Drawing.new(t)
    for k, v in next, p do d[k] = v end
    return d
end

local function mkESP(player)
    if player == lp then return end
    ESPObjects[player] = {
        BoxTop    = newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BoxBot    = newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BoxLeft   = newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BoxRight  = newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BarBg     = newDraw("Line",{Color=ESPCfg.BarBg,Thickness=4,Visible=false}),
        Bar       = newDraw("Line",{Color=ESPCfg.BarColor,Thickness=4,Visible=false}),
        Name      = newDraw("Text",{Color=ESPCfg.NameColor,Size=11,Outline=true,Font=2,Visible=false}),
        Dist      = newDraw("Text",{Color=ESPCfg.DistColor,Size=10,Outline=true,Font=2,Visible=false}),
    }
end

local function rmESP(p)
    if ESPObjects[p] then
        for _, o in next, ESPObjects[p] do o:Remove() end
        ESPObjects[p] = nil
    end
end

local function hideESP(e)
    for _, o in next, e do o.Visible = false end
end

for _, p in next, Players:GetPlayers() do mkESP(p) end
Players.PlayerAdded:Connect(mkESP)
Players.PlayerRemoving:Connect(rmESP)

-- ┌─────────────────────────┐
-- │   AIM + SILENT AIM      │
-- └─────────────────────────┘
local AimCfg = {
    FOV      = 90,
    Strength = 0.28,
    Target   = "Head",
    TeamCheck= true,
}
local SilentCfg = { FOV = 280, Target = "Head" }

local function getClosestAim(fovOv, tgtOv)
    local fov    = fovOv  or AimCfg.FOV
    local tgt    = tgtOv  or AimCfg.Target
    local vp     = Camera.ViewportSize
    local center = Vector2.new(vp.X/2, vp.Y/2)
    local bestD  = fov ; local bestPart = nil
    for _, player in ipairs(Players:GetPlayers()) do
        if player == lp then continue end
        if AimCfg.TeamCheck and player.Team == lp.Team then continue end
        local char = player.Character
        local hum  = char and char:FindFirstChildOfClass("Humanoid")
        if not (hum and hum.Health > 0) then continue end
        local part = char:FindFirstChild(tgt) if not part then continue end
        local sp, onScreen = Camera:WorldToViewportPoint(part.Position)
        if not onScreen or sp.Z <= 0 then continue end
        local dist = (Vector2.new(sp.X, sp.Y) - center).Magnitude
        if dist < bestD then bestD = dist ; bestPart = part end
    end
    return bestPart
end

UIS.InputBegan:Connect(function(input, gp)
    if gp then return end
    if input.UserInputType == Enum.UserInputType.MouseButton1
    or input.UserInputType == Enum.UserInputType.Touch then
        if not State.SilentAim then return end
        local tp = getClosestAim(SilentCfg.FOV, SilentCfg.Target)
        if tp then Camera.CFrame = CFrame.lookAt(Camera.CFrame.Position, tp.Position) end
    end
end)

-- ┌─────────────────────────┐
-- │        CROSSHAIR        │
-- └─────────────────────────┘
local CrossCfg = {
    Style      = "CrossDot",
    Color      = Color3.fromRGB(80, 200, 255),
    OutColor   = Color3.fromRGB(0, 0, 0),
    Outline    = true,
    Size       = 10, Thick = 1.5, Gap = 4, DotR = 2,
}
local HitCfg = { Color=Color3.fromRGB(80,200,255), Size=8, Thick=1.5, Duration=0.12 }
local fovCirc = Drawing.new("Circle")
fovCirc.Color = Color3.fromRGB(80,160,255) ; fovCirc.Thickness=1
fovCirc.Filled=false ; fovCirc.Radius=AimCfg.FOV ; fovCirc.Transparency=0.6 ; fovCirc.Visible=false

local function nl(c,t) local d=Drawing.new("Line") d.Color=c d.Thickness=t d.Visible=false return d end
local OL2=CrossCfg.Thick+2
local CL={
    oT=nl(CrossCfg.OutColor,OL2), oB=nl(CrossCfg.OutColor,OL2),
    oL=nl(CrossCfg.OutColor,OL2), oR=nl(CrossCfg.OutColor,OL2),
    T=nl(CrossCfg.Color,CrossCfg.Thick), B=nl(CrossCfg.Color,CrossCfg.Thick),
    L=nl(CrossCfg.Color,CrossCfg.Thick), R=nl(CrossCfg.Color,CrossCfg.Thick),
}
local function nc(c,t,f,r) local d=Drawing.new("Circle") d.Color=c d.Thickness=t or 1 d.Filled=f or false d.Radius=r or 5 d.Visible=false return d end
local chDotO=nc(CrossCfg.OutColor,1,true,CrossCfg.DotR+1.5)
local chDot =nc(CrossCfg.Color,1,true,CrossCfg.DotR)
local HM={oL1=nl(Color3.fromRGB(0,0,0),HitCfg.Thick+1.5),oL2=nl(Color3.fromRGB(0,0,0),HitCfg.Thick+1.5),l1=nl(HitCfg.Color,HitCfg.Thick),l2=nl(HitCfg.Color,HitCfg.Thick)}
local allCHObjs={CL.oT,CL.oB,CL.oL,CL.oR,CL.T,CL.B,CL.L,CL.R,chDotO,chDot,fovCirc,HM.oL1,HM.oL2,HM.l1,HM.l2}
local function hideAllCH() for _,o in ipairs(allCHObjs) do o.Visible=false end end

local function drawCH()
    if not State.Crosshair then hideAllCH() return end
    local vp=Camera.ViewportSize ; local cx,cy=vp.X/2,vp.Y/2
    local g,s=CrossCfg.Gap,CrossCfg.Size ; local ol=CrossCfg.Outline
    CL.oT.Visible=false CL.oB.Visible=false CL.oL.Visible=false CL.oR.Visible=false
    CL.T.Visible=false CL.B.Visible=false CL.L.Visible=false CL.R.Visible=false
    chDotO.Visible=false chDot.Visible=false
    if CrossCfg.Style=="Cross" or CrossCfg.Style=="CrossDot" then
        if ol then
            CL.oT.From=Vector2.new(cx,cy-g-s) CL.oT.To=Vector2.new(cx,cy-g) CL.oT.Visible=true
            CL.oB.From=Vector2.new(cx,cy+g) CL.oB.To=Vector2.new(cx,cy+g+s) CL.oB.Visible=true
            CL.oL.From=Vector2.new(cx-g-s,cy) CL.oL.To=Vector2.new(cx-g,cy) CL.oL.Visible=true
            CL.oR.From=Vector2.new(cx+g,cy) CL.oR.To=Vector2.new(cx+g+s,cy) CL.oR.Visible=true
        end
        CL.T.From=Vector2.new(cx,cy-g-s) CL.T.To=Vector2.new(cx,cy-g) CL.T.Visible=true
        CL.B.From=Vector2.new(cx,cy+g) CL.B.To=Vector2.new(cx,cy+g+s) CL.B.Visible=true
        CL.L.From=Vector2.new(cx-g-s,cy) CL.L.To=Vector2.new(cx-g,cy) CL.L.Visible=true
        CL.R.From=Vector2.new(cx+g,cy) CL.R.To=Vector2.new(cx+g+s,cy) CL.R.Visible=true
    end
    if CrossCfg.Style=="Dot" or CrossCfg.Style=="CrossDot" then
        if ol then chDotO.Position=Vector2.new(cx,cy) chDotO.Visible=true end
        chDot.Position=Vector2.new(cx,cy) chDot.Visible=true
    end
    -- FOV circle
    if State.AimAssist then
        fovCirc.Position=Vector2.new(cx,cy) fovCirc.Radius=AimCfg.FOV fovCirc.Visible=true
    else fovCirc.Visible=false end
end

local hitActive=false
local function showHitMarker()
    if hitActive then return end ; hitActive=true
    local vp=Camera.ViewportSize ; local cx,cy=vp.X/2,vp.Y/2 ; local s=HitCfg.Size
    HM.oL1.From=Vector2.new(cx-s,cy-s) HM.oL1.To=Vector2.new(cx+s,cy+s) HM.oL1.Visible=true
    HM.oL2.From=Vector2.new(cx+s,cy-s) HM.oL2.To=Vector2.new(cx-s,cy+s) HM.oL2.Visible=true
    HM.l1.From=Vector2.new(cx-s,cy-s) HM.l1.To=Vector2.new(cx+s,cy+s) HM.l1.Visible=true
    HM.l2.From=Vector2.new(cx+s,cy-s) HM.l2.To=Vector2.new(cx-s,cy+s) HM.l2.Visible=true
    task.delay(HitCfg.Duration, function()
        HM.oL1.Visible=false HM.oL2.Visible=false HM.l1.Visible=false HM.l2.Visible=false
        hitActive=false
    end)
end

local hmTracked={}
local function trackHM(player)
    if player==lp then return end
    local function onChar(char)
        local hum=char:WaitForChild("Humanoid")
        if hmTracked[player] then hmTracked[player]:Disconnect() end
        local prevHp=hum.Health
        hmTracked[player]=hum.HealthChanged:Connect(function(newHp)
            if not State.Crosshair then return end
            if newHp<prevHp then
                local lpR=lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
                local thR=char:FindFirstChild("HumanoidRootPart")
                if lpR and thR and (lpR.Position-thR.Position).Magnitude<300 then showHitMarker() end
            end
            prevHp=newHp
        end)
    end
    if player.Character then onChar(player.Character) end
    player.CharacterAdded:Connect(onChar)
end
for _, p in ipairs(Players:GetPlayers()) do trackHM(p) end
Players.PlayerAdded:Connect(trackHM)
Players.PlayerRemoving:Connect(function(p) if hmTracked[p] then hmTracked[p]:Disconnect() hmTracked[p]=nil end end)

-- ┌─────────────────────────┐
-- │        NO RECOIL        │
-- └─────────────────────────┘
local lastCF = Camera.CFrame
RunService.RenderStepped:Connect(function()
    if State.NoRecoil then
        local cur = Camera.CFrame
        local _, lastPitch, _ = lastCF:ToEulerAnglesYXZ()
        local _, curPitch, _  = cur:ToEulerAnglesYXZ()
        local kick = curPitch - lastPitch
        if kick > 0.008 then
            Camera.CFrame = cur * CFrame.Angles(-kick * 0.85, 0, 0)
        end
    end
    lastCF = Camera.CFrame
end)

-- ┌─────────────────────────┐
-- │        FPS BOOST        │
-- └─────────────────────────┘
local fpsOriginal = {}
local function applyFPSBoost(on)
    if on then
        fpsOriginal.GlobalShadows   = Lighting.GlobalShadows
        fpsOriginal.FogEnd          = Lighting.FogEnd
        fpsOriginal.Brightness      = Lighting.Brightness
        Lighting.GlobalShadows = false
        Lighting.FogEnd        = 100000
        for _, v in ipairs(Lighting:GetChildren()) do
            if v:IsA("BlurEffect") or v:IsA("DepthOfFieldEffect")
            or v:IsA("SunRaysEffect") or v:IsA("BloomEffect")
            or v:IsA("ColorCorrectionEffect") then
                v.Enabled = false
            end
        end
        for _, v in ipairs(workspace:GetDescendants()) do
            if v:IsA("ParticleEmitter") then v.Enabled = false end
            if v:IsA("Atmosphere") then v.Density = 0 end
        end
        setStatus("FPS Boost ON — visuals stripped", C.Success)
    else
        if fpsOriginal.GlobalShadows ~= nil then
            Lighting.GlobalShadows = fpsOriginal.GlobalShadows
        end
        if fpsOriginal.FogEnd then Lighting.FogEnd = fpsOriginal.FogEnd end
        for _, v in ipairs(Lighting:GetChildren()) do
            if v:IsA("BlurEffect") or v:IsA("DepthOfFieldEffect")
            or v:IsA("SunRaysEffect") or v:IsA("BloomEffect")
            or v:IsA("ColorCorrectionEffect") then
                v.Enabled = true
            end
        end
        for _, v in ipairs(workspace:GetDescendants()) do
            if v:IsA("ParticleEmitter") then v.Enabled = true end
        end
        setStatus("FPS Boost OFF — visuals restored", C.Warn)
    end
end

-- ┌─────────────────────────┐
-- │       RENDER LOOP       │
-- └─────────────────────────┘
RunService.RenderStepped:Connect(function()
    -- ESP
    if not State.ESP then
        for _, e in next, ESPObjects do hideESP(e) end
    else
        local vp = Camera.ViewportSize
        local lpR = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
        for player, esp in next, ESPObjects do
            local char  = player.Character
            local hum   = char and char:FindFirstChildOfClass("Humanoid")
            local root  = char and char:FindFirstChild("HumanoidRootPart")
            local head  = char and char:FindFirstChild("Head")
            if not (char and hum and root and head and hum.Health > 0) then hideESP(esp) continue end
            local dist  = lpR and (lpR.Position - root.Position).Magnitude or 0
            if dist > ESPCfg.MaxDist then hideESP(esp) continue end
            local rSP   = Camera:WorldToViewportPoint(root.Position)
            local hSP   = Camera:WorldToViewportPoint(head.Position + Vector3.new(0, 0.7, 0))
            if rSP.Z <= 0 then hideESP(esp) continue end
            local h  = math.abs(hSP.Y - rSP.Y) * 2 ; local w = h * 0.55
            local cx, cy = rSP.X, (hSP.Y + rSP.Y) / 2
            local x1,x2,y1,y2 = cx-w/2, cx+w/2, cy-h/2, cy+h/2
            -- Box
            esp.BoxTop.From=Vector2.new(x1,y1) esp.BoxTop.To=Vector2.new(x2,y1) esp.BoxTop.Visible=true
            esp.BoxBot.From=Vector2.new(x1,y2) esp.BoxBot.To=Vector2.new(x2,y2) esp.BoxBot.Visible=true
            esp.BoxLeft.From=Vector2.new(x1,y1) esp.BoxLeft.To=Vector2.new(x1,y2) esp.BoxLeft.Visible=true
            esp.BoxRight.From=Vector2.new(x2,y1) esp.BoxRight.To=Vector2.new(x2,y2) esp.BoxRight.Visible=true
            -- HP Bar
            local hpRatio = math.clamp(hum.Health / math.max(hum.MaxHealth, 1), 0, 1)
            local barX   = x1 - 6
            esp.BarBg.From=Vector2.new(barX,y1) esp.BarBg.To=Vector2.new(barX,y2) esp.BarBg.Visible=true
            local barH   = y1 + (y2-y1)*(1-hpRatio)
            esp.Bar.From=Vector2.new(barX,barH) esp.Bar.To=Vector2.new(barX,y2) esp.Bar.Visible=true
            local barColor = hpRatio>0.5 and Color3.fromRGB(70,220,130) or hpRatio>0.25 and Color3.fromRGB(255,195,50) or Color3.fromRGB(255,65,90)
            esp.Bar.Color=barColor
            -- Name + Distance
            esp.Name.Text=player.Name ; esp.Name.Position=Vector2.new(cx,y1-14) ; esp.Name.Visible=true
            esp.Dist.Text=string.format("%.0fm",dist/5) ; esp.Dist.Position=Vector2.new(cx,y2+2) ; esp.Dist.Visible=true
        end
    end
    -- Aim Assist
    if State.AimAssist then
        local tp = getClosestAim()
        if tp then
            local cur = Camera.CFrame
            Camera.CFrame = cur:Lerp(CFrame.lookAt(cur.Position, tp.Position), AimCfg.Strength)
        end
    end
    drawCH()
end)

lp.Idled:Connect(function() VirtualUser:CaptureController() VirtualUser:ClickButton2(Vector2.new()) end)

-- ┌─────────────────────────┐
-- │         TOGGLES         │
-- └─────────────────────────┘
createToggle("ESP","Box + HP Bar + Name + Distance",1,function(on)
    State.ESP=on
    if not on then for _,e in next,ESPObjects do hideESP(e) end end
    setStatus(on and "ESP ON" or "ESP OFF", on and C.Success or C.Error)
end)
createToggle("Crosshair","Custom CH + Hitmarker (Blue)",2,function(on)
    State.Crosshair=on
    if not on then hideAllCH() end
    setStatus(on and "Crosshair ON" or "Crosshair OFF", on and C.Success or C.Error)
end)
createToggle("Aim Assist","Smooth pull ke target + FOV ring",3,function(on)
    State.AimAssist=on
    if not on then fovCirc.Visible=false end
    setStatus(on and "Aim Assist ON" or "Aim Assist OFF", on and C.Success or C.Error)
end)
createToggle("Silent Aim","Snap instan ke musuh saat tap/klik",4,function(on)
    State.SilentAim=on
    setStatus(on and "Silent Aim ON" or "Silent Aim OFF", on and C.Success or C.Error)
end)
createToggle("No Recoil","Redam recoil kamera — anti kickback",5,function(on)
    State.NoRecoil=on
    setStatus(on and "No Recoil ON" or "No Recoil OFF", on and C.Success or C.Error)
end)
createToggle("FPS Boost","Strip shadows, particles & effects",6,function(on)
    State.FPSBoost=on
    applyFPSBoost(on)
end)

print("[ZC Hub] v1.0 FPS Loaded!")
