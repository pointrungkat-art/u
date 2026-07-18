-- XC Hub v2.0 | Galaxy UI + Key System
-- ESP + AutoHop + AutoChest + AutoFruit
-- Delta Android Compatible
-- loadstring(game:HttpGet("RAW_URL"))()

local Players         = game:GetService("Players")
local RunService      = game:GetService("RunService")
local TeleportService = game:GetService("TeleportService")
local TweenService    = game:GetService("TweenService")
local HttpService     = game:GetService("HttpService")
local VirtualUser     = game:GetService("VirtualUser")

local lp     = Players.LocalPlayer
local Camera = workspace.CurrentCamera

local VALID_KEY = "CAESAR"

local State = {
    ESP       = false,
    AutoHop   = false,
    AutoChest = false,
    AutoFruit = false,
}

-- ┌─────────────────────────┐
-- │         COLORS          │
-- └─────────────────────────┘
local C = {
    BG      = Color3.fromRGB(8,  5,  20),
    Panel   = Color3.fromRGB(16, 10, 38),
    Row     = Color3.fromRGB(20, 12, 46),
    Accent  = Color3.fromRGB(130, 40, 220),
    Bright  = Color3.fromRGB(185, 90, 255),
    Text    = Color3.fromRGB(220, 200, 255),
    Sub     = Color3.fromRGB(130, 105, 180),
    Off     = Color3.fromRGB(50,  35,  78),
    Success = Color3.fromRGB(90,  220, 140),
    Error   = Color3.fromRGB(255, 70,  100),
    Warn    = Color3.fromRGB(255, 200, 60),
}

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name           = "XCHub"
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

-- Deco line top
local keyLine = Instance.new("Frame", KeyFrame)
keyLine.Size             = UDim2.new(0.5, 0, 0, 2)
keyLine.Position         = UDim2.new(0.25, 0, 0, 0)
keyLine.BackgroundColor3 = C.Bright
keyLine.BorderSizePixel  = 0
Instance.new("UICorner", keyLine).CornerRadius = UDim.new(1, 0)

-- Logo
local keyLogo = Instance.new("TextLabel", KeyFrame)
keyLogo.Size                 = UDim2.new(1, 0, 0, 36)
keyLogo.Position             = UDim2.new(0, 0, 0, 14)
keyLogo.BackgroundTransparency = 1
keyLogo.Text                 = "✴ XC Hub ✴"
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

-- Input box
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

-- Submit button
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

-- Error msg
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
MainFrame.Size             = UDim2.new(0, 230, 0, 370)
MainFrame.Position         = UDim2.new(0.5, -115, 0.5, -185)
MainFrame.BackgroundColor3 = C.BG
MainFrame.BorderSizePixel  = 0
MainFrame.Visible          = false
MainFrame.Parent           = ScreenGui
Instance.new("UICorner", MainFrame).CornerRadius = UDim.new(0, 12)

local mainStroke = Instance.new("UIStroke", MainFrame)
mainStroke.Color     = C.Accent
mainStroke.Thickness = 1.5

-- Title bar
local TitleBar = Instance.new("Frame", MainFrame)
TitleBar.Size             = UDim2.new(1, 0, 0, 42)
TitleBar.BackgroundColor3 = C.Panel
TitleBar.BorderSizePixel  = 0
Instance.new("UICorner", TitleBar).CornerRadius = UDim.new(0, 12)

-- Top deco line
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
TitleLabel.Text                 = "✴ XC Hub v2.0"
TitleLabel.TextColor3           = C.Bright
TitleLabel.TextSize             = 14
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

-- Content
local Content = Instance.new("Frame", MainFrame)
Content.Size                 = UDim2.new(1, -16, 1, -92)
Content.Position             = UDim2.new(0, 8, 0, 48)
Content.BackgroundTransparency = 1
local ULL = Instance.new("UIListLayout", Content)
ULL.Padding   = UDim.new(0, 6)
ULL.SortOrder = Enum.SortOrder.LayoutOrder

-- Status bar
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
StatusLabel.Text                 = "✴ XC Hub Ready"
StatusLabel.TextColor3           = C.Bright
StatusLabel.TextSize             = 11
StatusLabel.Font                 = Enum.Font.Gotham
StatusLabel.TextXAlignment       = Enum.TextXAlignment.Left

local function setStatus(text, color)
    StatusLabel.Text       = "✴ " .. text
    StatusLabel.TextColor3 = color or C.Bright
end

-- Toggle creator
local function createToggle(name, desc, order, onToggle)
    local Row = Instance.new("Frame", Content)
    Row.Size             = UDim2.new(1, 0, 0, 60)
    Row.BackgroundColor3 = C.Row
    Row.BorderSizePixel  = 0
    Row.LayoutOrder      = order
    Instance.new("UICorner", Row).CornerRadius = UDim.new(0, 8)
    local rStroke = Instance.new("UIStroke", Row)
    rStroke.Color = C.Off ; rStroke.Thickness = 1

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
    TBg.BackgroundColor3=C.Off ; TBg.BorderSizePixel=0
    Instance.new("UICorner", TBg).CornerRadius = UDim.new(1, 0)

    local Circle = Instance.new("Frame", TBg)
    Circle.Size=UDim2.new(0,19,0,19) ; Circle.Position=UDim2.new(0,3,0.5,-9)
    Circle.BackgroundColor3=C.Sub ; Circle.BorderSizePixel=0
    Instance.new("UICorner", Circle).CornerRadius = UDim.new(1, 0)

    local enabled = false
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
    MainFrame.Visible = true
    TweenService:Create(MainFrame, TweenInfo.new(0.3, Enum.EasingStyle.Back), {
        Size     = UDim2.new(0, 230, 0, 370),
        Position = UDim2.new(0.5, -115, 0.5, -185),
    }):Play()
    task.wait(2)
    setStatus("XC Hub Ready")
end

local function checkKey()
    local input = keyBox.Text:upper():gsub("%s", "")
    if input == VALID_KEY then
        keyError.Text    = "✔ Key valid! Loading..."
        keyError.TextColor3 = C.Success
        TweenService:Create(submitBtn, TweenInfo.new(0.2), {BackgroundColor3=C.Success}):Play()
        task.wait(0.5)
        showHub()
    else
        keyError.Text    = "✕ Key salah, coba lagi!"
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
-- │           ESP           │
-- └─────────────────────────┘
local ESPObjects = {}
local ESPCfg = {
    BoxColor=Color3.fromRGB(185,90,255), BoxThick=1.5,
    TracerColor=Color3.fromRGB(210,160,255), TracerThick=1,
    NameColor=Color3.fromRGB(220,200,255),
    DistColor=Color3.fromRGB(160,130,210),
    MaxDist=1000,
}
local function newDraw(t,p) local d=Drawing.new(t) for k,v in next,p do d[k]=v end return d end
local function mkESP(player)
    if player==lp then return end
    ESPObjects[player]={
        BoxTop=newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BoxBottom=newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BoxLeft=newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BoxRight=newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        Tracer=newDraw("Line",{Color=ESPCfg.TracerColor,Thickness=ESPCfg.TracerThick,Visible=false}),
        Name=newDraw("Text",{Text=player.Name,Size=13,Color=ESPCfg.NameColor,Center=true,Outline=true,Visible=false}),
        Distance=newDraw("Text",{Size=12,Color=ESPCfg.DistColor,Center=true,Outline=true,Visible=false}),
        HealthBG=newDraw("Line",{Color=Color3.fromRGB(0,0,0),Thickness=4,Visible=false}),
        HealthBar=newDraw("Line",{Color=Color3.fromRGB(90,255,140),Thickness=3,Visible=false}),
    }
end
local function rmESP(p) if ESPObjects[p] then for _,o in next,ESPObjects[p] do o:Remove() end ESPObjects[p]=nil end end
local function hideESP(e) for _,o in next,e do o.Visible=false end end
for _,p in next,Players:GetPlayers() do mkESP(p) end
Players.PlayerAdded:Connect(mkESP)
Players.PlayerRemoving:Connect(rmESP)

-- ┌─────────────────────────┐
-- │         AUTO HOP        │
-- └─────────────────────────┘
local HOP_INTERVAL = 300
local hopElapsed   = 0
local function getServers()
    local ok,res=pcall(function() return game:HttpGet(string.format("https://games.roblox.com/v1/games/%d/servers/Public?sortOrder=Asc&limit=100",game.PlaceId)) end)
    if not ok then return nil end
    local ok2,data=pcall(function() return HttpService:JSONDecode(res) end)
    if not ok2 or not data or not data.data then return nil end
    return data.data
end
local function hopServer()
    local servers=getServers() if not servers then return end
    local cur=game.JobId ; local picked
    for _,s in ipairs(servers) do if s.id~=cur and (s.playing or 0)>=1 then picked=s break end end
    if not picked then for _,s in ipairs(servers) do if s.id~=cur then picked=s break end end end
    if picked then
        setStatus("Hopping server...", C.Warn)
        task.wait(1)
        TeleportService:TeleportToPlaceInstance(game.PlaceId, picked.id, lp)
    end
end

-- ┌─────────────────────────┐
-- │  AUTO CHEST + FRUIT     │
-- └─────────────────────────┘
local CHEST_KW = {"chest","treasure","crate","box"}
local FRUIT_KW = {"fruit","devil","flame","ice","sand","dark","light","magma","quake",
    "human","buddha","love","spider","bird","bomb","spike","chop","smoke","string",
    "revive","door","paw","gravity","diamond","rubber","barrier","ghost","dough",
    "shadow","leopard","control","venom","soul","phoenix","dragon","mammoth",
    "sound","blizzard","rumble","pain","kitsune","toad","gas","t-rex"}

local function nameHas(obj, kws)
    local n=obj.Name:lower() for _,k in ipairs(kws) do if n:find(k) then return true end end return false
end
local function tpTo(pos)
    local r=lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
    if r then r.CFrame=CFrame.new(pos+Vector3.new(0,4,0)) end
end
local function fireAll(obj)
    for _,v in ipairs(obj:GetDescendants()) do
        if v:IsA("RemoteEvent") or v:IsA("RemoteFunction") then pcall(function() v:FireServer() end) end
    end
end
local function scanObjs(kws)
    local res={}
    local function scan(p) for _,o in ipairs(p:GetChildren()) do
        if (o:IsA("Model") or o:IsA("BasePart")) and nameHas(o,kws) then
            local r=o:IsA("Model") and (o.PrimaryPart or o:FindFirstChildWhichIsA("BasePart")) or o
            if r then table.insert(res,{obj=o,pos=r.Position}) end
        end
        scan(o)
    end end
    scan(workspace) return res
end

local function runAutoChest()
    while State.AutoChest do
        local list=scanObjs(CHEST_KW)
        if #list==0 then
            setStatus("No chests, hopping...",C.Warn) task.wait(2) hopServer() task.wait(5)
        else
            setStatus(string.format("Found %d chests!",#list),C.Success)
            for i,c in ipairs(list) do
                if not State.AutoChest then break end
                setStatus(string.format("Chest %d/%d",i,#list),C.Bright)
                tpTo(c.pos) task.wait(0.6) fireAll(c.obj) task.wait(0.6)
            end
            if State.AutoChest then setStatus("Done! Hopping...",C.Warn) task.wait(1.5) hopServer() task.wait(5) end
        end
    end
end

local fruitConn
local function runAutoFruit()
    local function collect(obj)
        local r=obj:IsA("Model") and (obj.PrimaryPart or obj:FindFirstChildWhichIsA("BasePart")) or obj
        if not r then return end
        tpTo(r.Position) task.wait(0.5)
        local pr=obj:FindFirstChildWhichIsA("ProximityPrompt",true)
        if pr then pcall(function() fireproximityprompt(pr) end) task.wait(0.4) end
        local hrp=lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
        if hrp then hrp.CFrame=CFrame.new(r.Position+Vector3.new(0,2,0)) task.wait(0.3) end
        fireAll(obj)
    end
    local function scan()
        for _,o in ipairs(workspace:GetChildren()) do
            if not State.AutoFruit then return end
            if (o:IsA("Model") or o:IsA("BasePart")) and nameHas(o,FRUIT_KW) then
                setStatus("Fruit: "..o.Name,Color3.fromRGB(255,220,80)) collect(o) task.wait(1)
            end
        end
    end
    fruitConn=workspace.ChildAdded:Connect(function(c)
        if not State.AutoFruit then return end
        task.wait(0.8)
        if (c:IsA("Model") or c:IsA("BasePart")) and nameHas(c,FRUIT_KW) then
            setStatus("Fruit spawned: "..c.Name,Color3.fromRGB(255,220,80)) task.wait(0.4) collect(c)
        end
    end)
    scan()
    while State.AutoFruit do
        setStatus("AutoFruit: Watching...",C.Sub) task.wait(15)
        if State.AutoFruit then scan() end
    end
    if fruitConn then fruitConn:Disconnect() fruitConn=nil end
end

-- ┌─────────────────────────┐
-- │       RENDER LOOP       │
-- └─────────────────────────┘
RunService.RenderStepped:Connect(function(dt)
    if not State.ESP then for _,e in next,ESPObjects do hideESP(e) end
    else
        local vp=Camera.ViewportSize
        local org=Vector2.new(vp.X/2,vp.Y)
        local lpR=lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
        for player,esp in next,ESPObjects do
            local char=player.Character
            local hum=char and char:FindFirstChildOfClass("Humanoid")
            local root=char and char:FindFirstChild("HumanoidRootPart")
            local head=char and char:FindFirstChild("Head")
            if not(char and hum and root and head and hum.Health>0) then hideESP(esp) continue end
            local dist=lpR and (lpR.Position-root.Position).Magnitude or 0
            if dist>ESPCfg.MaxDist then hideESP(esp) continue end
            local rSP=Camera:WorldToViewportPoint(root.Position)
            local hSP=Camera:WorldToViewportPoint(head.Position+Vector3.new(0,0.7,0))
            if rSP.Z<=0 then hideESP(esp) continue end
            local h=math.abs(hSP.Y-rSP.Y)*2 ; local w=h*0.55
            local cx,cy=rSP.X,(hSP.Y+rSP.Y)/2
            local x1,x2,y1,y2=cx-w/2,cx+w/2,cy-h/2,cy+h/2
            esp.BoxTop.From=Vector2.new(x1,y1);esp.BoxTop.To=Vector2.new(x2,y1);esp.BoxTop.Visible=true
            esp.BoxBottom.From=Vector2.new(x1,y2);esp.BoxBottom.To=Vector2.new(x2,y2);esp.BoxBottom.Visible=true
            esp.BoxLeft.From=Vector2.new(x1,y1);esp.BoxLeft.To=Vector2.new(x1,y2);esp.BoxLeft.Visible=true
            esp.BoxRight.From=Vector2.new(x2,y1);esp.BoxRight.To=Vector2.new(x2,y2);esp.BoxRight.Visible=true
            esp.Tracer.From=org;esp.Tracer.To=Vector2.new(cx,y2);esp.Tracer.Visible=true
            esp.Name.Position=Vector2.new(cx,y1-15);esp.Name.Visible=true
            esp.Distance.Text=string.format("[%.0f]",dist);esp.Distance.Position=Vector2.new(cx,y2+2);esp.Distance.Visible=true
            local hp=math.clamp(hum.Health/hum.MaxHealth,0,1) ; local bx=x1-5
            esp.HealthBG.From=Vector2.new(bx,y1);esp.HealthBG.To=Vector2.new(bx,y2);esp.HealthBG.Visible=true
            esp.HealthBar.From=Vector2.new(bx,y2);esp.HealthBar.To=Vector2.new(bx,y2-h*hp)
            esp.HealthBar.Color=Color3.fromRGB(math.floor(255*(1-hp)),math.floor(255*hp),80);esp.HealthBar.Visible=true
        end
    end
    if State.AutoHop then hopElapsed+=dt
        if hopElapsed>=HOP_INTERVAL then hopElapsed=0 task.spawn(hopServer) end
    else hopElapsed=0 end
end)

lp.Idled:Connect(function() VirtualUser:CaptureController() VirtualUser:ClickButton2(Vector2.new()) end)

-- ┌─────────────────────────┐
-- │        TOGGLES          │
-- └─────────────────────────┘
createToggle("ESP","Wall-through + Tracer + HP",1,function(on)
    State.ESP=on
    if not on then for _,e in next,ESPObjects do hideESP(e) end end
    setStatus(on and "ESP ON" or "ESP OFF", on and C.Success or C.Error)
end)
createToggle("Auto Hop","Pindah server tiap 5 menit",2,function(on)
    State.AutoHop=on ; hopElapsed=0
    setStatus(on and "AutoHop ON" or "AutoHop OFF", on and C.Success or C.Error)
end)
createToggle("Auto Chest","Collect chest → hop server",3,function(on)
    State.AutoChest=on
    if on then task.spawn(runAutoChest) end
    setStatus(on and "AutoChest ON" or "AutoChest OFF", on and C.Success or C.Error)
end)
createToggle("Auto Fruit","Detect & collect devil fruit",4,function(on)
    State.AutoFruit=on
    if on then task.spawn(runAutoFruit)
    else if fruitConn then fruitConn:Disconnect() fruitConn=nil end end
    setStatus(on and "AutoFruit ON" or "AutoFruit OFF", on and C.Success or C.Error)
end)

print("[XC Hub] v2.0 Loaded!")
