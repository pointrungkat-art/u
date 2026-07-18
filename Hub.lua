-- Hub Script | ESP + AutoHop + AutoCollect Chest
-- Delta Android Compatible | Draggable GUI
-- loadstring(game:HttpGet("RAW_URL"))()

local Players        = game:GetService("Players")
local RunService     = game:GetService("RunService")
local TeleportService = game:GetService("TeleportService")
local TweenService   = game:GetService("TweenService")
local HttpService    = game:GetService("HttpService")
local VirtualUser    = game:GetService("VirtualUser")

local lp     = Players.LocalPlayer
local Camera = workspace.CurrentCamera

local State = { ESP = false, AutoHop = false, AutoChest = false }

-- ┌─────────────────────────┐
-- │           GUI           │
-- └─────────────────────────┘
local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name          = "HubScript"
ScreenGui.ResetOnSpawn  = false
ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
ScreenGui.Parent        = game:GetService("CoreGui")

local Main = Instance.new("Frame")
Main.Name            = "Main"
Main.Size            = UDim2.new(0, 230, 0, 290)
Main.Position        = UDim2.new(0.5, -115, 0.5, -145)
Main.BackgroundColor3 = Color3.fromRGB(15, 15, 25)
Main.BorderSizePixel = 0
Main.Parent          = ScreenGui
Instance.new("UICorner", Main).CornerRadius = UDim.new(0, 10)

-- Stroke
local stroke = Instance.new("UIStroke", Main)
stroke.Color     = Color3.fromRGB(80, 80, 140)
stroke.Thickness = 1.5

-- Title Bar
local TitleBar = Instance.new("Frame", Main)
TitleBar.Size            = UDim2.new(1, 0, 0, 38)
TitleBar.BackgroundColor3 = Color3.fromRGB(25, 25, 45)
TitleBar.BorderSizePixel = 0
Instance.new("UICorner", TitleBar).CornerRadius = UDim.new(0, 10)

local TitleLabel = Instance.new("TextLabel", TitleBar)
TitleLabel.Size              = UDim2.new(1, -44, 1, 0)
TitleLabel.Position          = UDim2.new(0, 12, 0, 0)
TitleLabel.BackgroundTransparency = 1
TitleLabel.Text              = "Hub Script v1.0"
TitleLabel.TextColor3        = Color3.fromRGB(200, 200, 255)
TitleLabel.TextSize          = 14
TitleLabel.Font              = Enum.Font.GothamBold
TitleLabel.TextXAlignment    = Enum.TextXAlignment.Left

local CloseBtn = Instance.new("TextButton", TitleBar)
CloseBtn.Size            = UDim2.new(0, 26, 0, 26)
CloseBtn.Position        = UDim2.new(1, -32, 0.5, -13)
CloseBtn.BackgroundColor3 = Color3.fromRGB(180, 40, 40)
CloseBtn.Text            = "x"
CloseBtn.TextColor3      = Color3.fromRGB(255,255,255)
CloseBtn.TextSize        = 13
CloseBtn.Font            = Enum.Font.GothamBold
Instance.new("UICorner", CloseBtn).CornerRadius = UDim.new(1, 0)
CloseBtn.MouseButton1Click:Connect(function() ScreenGui:Destroy() end)

-- Draggable
local dragging, dragStart, startPos
TitleBar.InputBegan:Connect(function(i)
    if i.UserInputType == Enum.UserInputType.Touch
    or i.UserInputType == Enum.UserInputType.MouseButton1 then
        dragging  = true
        dragStart = i.Position
        startPos  = Main.Position
    end
end)
TitleBar.InputChanged:Connect(function(i)
    if dragging and (i.UserInputType == Enum.UserInputType.Touch
    or i.UserInputType == Enum.UserInputType.MouseMovement) then
        local d = i.Position - dragStart
        Main.Position = UDim2.new(
            startPos.X.Scale, startPos.X.Offset + d.X,
            startPos.Y.Scale, startPos.Y.Offset + d.Y
        )
    end
end)
TitleBar.InputEnded:Connect(function(i)
    if i.UserInputType == Enum.UserInputType.Touch
    or i.UserInputType == Enum.UserInputType.MouseButton1 then
        dragging = false
    end
end)

-- Content
local Content = Instance.new("Frame", Main)
Content.Size               = UDim2.new(1, -16, 1, -88)
Content.Position           = UDim2.new(0, 8, 0, 44)
Content.BackgroundTransparency = 1
local ULL = Instance.new("UIListLayout", Content)
ULL.Padding      = UDim.new(0, 8)
ULL.SortOrder    = Enum.SortOrder.LayoutOrder

-- Status Bar
local StatusBar = Instance.new("Frame", Main)
StatusBar.Size            = UDim2.new(1, -16, 0, 28)
StatusBar.Position        = UDim2.new(0, 8, 1, -34)
StatusBar.BackgroundColor3 = Color3.fromRGB(25, 25, 45)
StatusBar.BorderSizePixel = 0
Instance.new("UICorner", StatusBar).CornerRadius = UDim.new(0, 6)

local StatusLabel = Instance.new("TextLabel", StatusBar)
StatusLabel.Size              = UDim2.new(1, -10, 1, 0)
StatusLabel.Position          = UDim2.new(0, 8, 0, 0)
StatusLabel.BackgroundTransparency = 1
StatusLabel.Text              = "● Ready"
StatusLabel.TextColor3        = Color3.fromRGB(100, 220, 100)
StatusLabel.TextSize          = 11
StatusLabel.Font              = Enum.Font.Gotham
StatusLabel.TextXAlignment    = Enum.TextXAlignment.Left

local function setStatus(text, color)
    StatusLabel.Text       = "● " .. text
    StatusLabel.TextColor3 = color or Color3.fromRGB(100, 220, 100)
end

-- Toggle creator
local function createToggle(name, desc, order, onToggle)
    local Row = Instance.new("Frame", Content)
    Row.Size            = UDim2.new(1, 0, 0, 62)
    Row.BackgroundColor3 = Color3.fromRGB(25, 25, 42)
    Row.BorderSizePixel = 0
    Row.LayoutOrder     = order
    Instance.new("UICorner", Row).CornerRadius = UDim.new(0, 7)

    local NameLbl = Instance.new("TextLabel", Row)
    NameLbl.Size              = UDim2.new(0.72, 0, 0, 24)
    NameLbl.Position          = UDim2.new(0, 10, 0, 8)
    NameLbl.BackgroundTransparency = 1
    NameLbl.Text              = name
    NameLbl.TextColor3        = Color3.fromRGB(230, 230, 255)
    NameLbl.TextSize          = 13
    NameLbl.Font              = Enum.Font.GothamBold
    NameLbl.TextXAlignment    = Enum.TextXAlignment.Left

    local DescLbl = Instance.new("TextLabel", Row)
    DescLbl.Size              = UDim2.new(0.72, 0, 0, 18)
    DescLbl.Position          = UDim2.new(0, 10, 0, 32)
    DescLbl.BackgroundTransparency = 1
    DescLbl.Text              = desc
    DescLbl.TextColor3        = Color3.fromRGB(120, 120, 160)
    DescLbl.TextSize          = 10
    DescLbl.Font              = Enum.Font.Gotham
    DescLbl.TextXAlignment    = Enum.TextXAlignment.Left

    local TBg = Instance.new("Frame", Row)
    TBg.Size            = UDim2.new(0, 46, 0, 25)
    TBg.Position        = UDim2.new(1, -56, 0.5, -12)
    TBg.BackgroundColor3 = Color3.fromRGB(55, 55, 80)
    TBg.BorderSizePixel = 0
    Instance.new("UICorner", TBg).CornerRadius = UDim.new(1, 0)

    local Circle = Instance.new("Frame", TBg)
    Circle.Size            = UDim2.new(0, 19, 0, 19)
    Circle.Position        = UDim2.new(0, 3, 0.5, -9)
    Circle.BackgroundColor3 = Color3.fromRGB(180, 180, 200)
    Circle.BorderSizePixel = 0
    Instance.new("UICorner", Circle).CornerRadius = UDim.new(1, 0)

    local enabled = false
    local function setToggle(val)
        enabled = val
        TweenService:Create(Circle, TweenInfo.new(0.18), {
            Position        = val and UDim2.new(0,24,0.5,-9) or UDim2.new(0,3,0.5,-9),
            BackgroundColor3 = val and Color3.fromRGB(80,220,80) or Color3.fromRGB(180,180,200),
        }):Play()
        TweenService:Create(TBg, TweenInfo.new(0.18), {
            BackgroundColor3 = val and Color3.fromRGB(30,90,30) or Color3.fromRGB(55,55,80),
        }):Play()
        onToggle(val)
    end

    TBg.InputBegan:Connect(function(i)
        if i.UserInputType == Enum.UserInputType.Touch
        or i.UserInputType == Enum.UserInputType.MouseButton1 then
            setToggle(not enabled)
        end
    end)

    return setToggle
end

-- ┌─────────────────────────┐
-- │         ESP             │
-- └─────────────────────────┘
local ESPObjects = {}
local ESPCfg = {
    BoxColor=Color3.fromRGB(255,50,50), BoxThick=1.5,
    TracerColor=Color3.fromRGB(255,255,255), TracerThick=1,
    NameColor=Color3.fromRGB(255,255,255),
    DistColor=Color3.fromRGB(200,200,200),
    MaxDist=1000,
}

local function newDraw(t, p)
    local d = Drawing.new(t)
    for k,v in next,p do d[k]=v end
    return d
end

local function mkESP(player)
    if player == lp then return end
    ESPObjects[player] = {
        BoxTop    = newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BoxBottom = newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BoxLeft   = newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        BoxRight  = newDraw("Line",{Color=ESPCfg.BoxColor,Thickness=ESPCfg.BoxThick,Visible=false}),
        Tracer    = newDraw("Line",{Color=ESPCfg.TracerColor,Thickness=ESPCfg.TracerThick,Visible=false}),
        Name      = newDraw("Text",{Text=player.Name,Size=13,Color=ESPCfg.NameColor,Center=true,Outline=true,Visible=false}),
        Distance  = newDraw("Text",{Size=12,Color=ESPCfg.DistColor,Center=true,Outline=true,Visible=false}),
        HealthBG  = newDraw("Line",{Color=Color3.fromRGB(0,0,0),Thickness=4,Visible=false}),
        HealthBar = newDraw("Line",{Color=Color3.fromRGB(0,255,80),Thickness=3,Visible=false}),
    }
end

local function rmESP(player)
    if ESPObjects[player] then
        for _,o in next,ESPObjects[player] do o:Remove() end
        ESPObjects[player] = nil
    end
end

local function hideESP(esp)
    for _,o in next,esp do o.Visible=false end
end

for _,p in next,Players:GetPlayers() do mkESP(p) end
Players.PlayerAdded:Connect(mkESP)
Players.PlayerRemoving:Connect(rmESP)

-- ┌─────────────────────────┐
-- │       AUTO HOP          │
-- └─────────────────────────┘
local HOP_INTERVAL = 300
local hopElapsed   = 0

local function getServers()
    local ok, res = pcall(function()
        return game:HttpGet(string.format(
            "https://games.roblox.com/v1/games/%d/servers/Public?sortOrder=Asc&limit=100",
            game.PlaceId
        ))
    end)
    if not ok then return nil end
    local ok2, data = pcall(function() return HttpService:JSONDecode(res) end)
    if not ok2 or not data or not data.data then return nil end
    return data.data
end

local function hopServer()
    local servers = getServers()
    if not servers then return end
    local cur = game.JobId
    local picked
    for _, s in ipairs(servers) do
        if s.id ~= cur and (s.playing or 0) >= 1 then
            picked = s break
        end
    end
    if not picked then
        for _, s in ipairs(servers) do
            if s.id ~= cur then picked = s break end
        end
    end
    if picked then
        setStatus("Hopping server...", Color3.fromRGB(255,200,50))
        task.wait(1)
        TeleportService:TeleportToPlaceInstance(game.PlaceId, picked.id, lp)
    end
end

-- ┌─────────────────────────┐
-- │    AUTO COLLECT CHEST   │
-- └─────────────────────────┘
local CHEST_KEYWORDS = {"chest", "treasure", "crate", "box"}

local function isChest(obj)
    local name = obj.Name:lower()
    for _, kw in ipairs(CHEST_KEYWORDS) do
        if name:find(kw) then return true end
    end
    return false
end

local function findChests()
    local results = {}
    local function scan(parent)
        for _, obj in ipairs(parent:GetChildren()) do
            if (obj:IsA("Model") or obj:IsA("BasePart")) and isChest(obj) then
                local root = obj:IsA("Model")
                    and (obj.PrimaryPart or obj:FindFirstChildWhichIsA("BasePart"))
                    or obj
                if root then
                    table.insert(results, {obj=obj, pos=root.Position})
                end
            end
            scan(obj)
        end
    end
    scan(workspace)
    return results
end

local function tpTo(pos)
    local char = lp.Character
    local root = char and char:FindFirstChild("HumanoidRootPart")
    if root then
        root.CFrame = CFrame.new(pos + Vector3.new(0, 4, 0))
    end
end

local function tryInteract(obj)
    -- touch all BaseParts
    for _, v in ipairs(obj:GetDescendants()) do
        if v:IsA("BasePart") then
            local char = lp.Character
            if char then
                local hrp = char:FindFirstChild("HumanoidRootPart")
                if hrp then
                    hrp.CFrame = CFrame.new(v.Position + Vector3.new(0,3,0))
                end
            end
        end
        -- fire any remotes found
        if v:IsA("RemoteEvent") or v:IsA("RemoteFunction") then
            pcall(function() v:FireServer() end)
        end
    end
end

local function runAutoChest()
    while State.AutoChest do
        local chests = findChests()
        if #chests == 0 then
            setStatus("No chests, hopping...", Color3.fromRGB(255,150,50))
            task.wait(2)
            hopServer()
            task.wait(5) -- tunggu teleport
        else
            setStatus(string.format("Found %d chests!", #chests), Color3.fromRGB(100,220,100))
            for i, c in ipairs(chests) do
                if not State.AutoChest then break end
                setStatus(string.format("Collecting %d / %d", i, #chests), Color3.fromRGB(100,180,255))
                tpTo(c.pos)
                task.wait(0.6)
                tryInteract(c.obj)
                task.wait(0.6)
            end
            if State.AutoChest then
                setStatus("All done! Hopping...", Color3.fromRGB(255,200,50))
                task.wait(1.5)
                hopServer()
                task.wait(5)
            end
        end
    end
end

-- ┌─────────────────────────┐
-- │      RENDER LOOP        │
-- └─────────────────────────┘
RunService.RenderStepped:Connect(function(dt)
    -- ESP
    if not State.ESP then
        for _, esp in next, ESPObjects do hideESP(esp) end
    else
        local vp  = Camera.ViewportSize
        local org = Vector2.new(vp.X/2, vp.Y)
        local lpR = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
        for player, esp in next, ESPObjects do
            local char = player.Character
            local hum  = char and char:FindFirstChildOfClass("Humanoid")
            local root = char and char:FindFirstChild("HumanoidRootPart")
            local head = char and char:FindFirstChild("Head")
            if not (char and hum and root and head and hum.Health > 0) then hideESP(esp) continue end
            local dist = lpR and (lpR.Position - root.Position).Magnitude or 0
            if dist > ESPCfg.MaxDist then hideESP(esp) continue end
            local rSP = Camera:WorldToViewportPoint(root.Position)
            local hSP = Camera:WorldToViewportPoint(head.Position + Vector3.new(0,0.7,0))
            if rSP.Z <= 0 then hideESP(esp) continue end
            local h  = math.abs(hSP.Y - rSP.Y) * 2
            local w  = h * 0.55
            local cx, cy = rSP.X, (hSP.Y + rSP.Y)/2
            local x1,x2,y1,y2 = cx-w/2, cx+w/2, cy-h/2, cy+h/2
            esp.BoxTop.From=Vector2.new(x1,y1);esp.BoxTop.To=Vector2.new(x2,y1);esp.BoxTop.Visible=true
            esp.BoxBottom.From=Vector2.new(x1,y2);esp.BoxBottom.To=Vector2.new(x2,y2);esp.BoxBottom.Visible=true
            esp.BoxLeft.From=Vector2.new(x1,y1);esp.BoxLeft.To=Vector2.new(x1,y2);esp.BoxLeft.Visible=true
            esp.BoxRight.From=Vector2.new(x2,y1);esp.BoxRight.To=Vector2.new(x2,y2);esp.BoxRight.Visible=true
            esp.Tracer.From=org;esp.Tracer.To=Vector2.new(cx,y2);esp.Tracer.Visible=true
            esp.Name.Position=Vector2.new(cx,y1-15);esp.Name.Visible=true
            esp.Distance.Text=string.format("[%.0f]",dist);esp.Distance.Position=Vector2.new(cx,y2+2);esp.Distance.Visible=true
            local hp=math.clamp(hum.Health/hum.MaxHealth,0,1)
            local bx=x1-5
            esp.HealthBG.From=Vector2.new(bx,y1);esp.HealthBG.To=Vector2.new(bx,y2);esp.HealthBG.Visible=true
            esp.HealthBar.From=Vector2.new(bx,y2);esp.HealthBar.To=Vector2.new(bx,y2-h*hp)
            esp.HealthBar.Color=Color3.fromRGB(math.floor(255*(1-hp)),math.floor(255*hp),0);esp.HealthBar.Visible=true
        end
    end
    -- AutoHop timer
    if State.AutoHop then
        hopElapsed += dt
        if hopElapsed >= HOP_INTERVAL then
            hopElapsed = 0
            task.spawn(hopServer)
        end
    else
        hopElapsed = 0
    end
end)

-- Anti AFK
lp.Idled:Connect(function()
    VirtualUser:CaptureController()
    VirtualUser:ClickButton2(Vector2.new())
end)

-- ┌─────────────────────────┐
-- │    REGISTER TOGGLES    │
-- └─────────────────────────┘
createToggle("ESP", "Wall-through + Tracer + HP bar", 1, function(on)
    State.ESP = on
    if not on then for _,esp in next,ESPObjects do hideESP(esp) end end
    setStatus(on and "ESP ON" or "ESP OFF", on and Color3.fromRGB(100,220,100) or Color3.fromRGB(200,80,80))
end)

createToggle("Auto Hop", "Pindah server tiap 5 menit", 2, function(on)
    State.AutoHop = on
    hopElapsed    = 0
    setStatus(on and "AutoHop ON" or "AutoHop OFF", on and Color3.fromRGB(100,220,100) or Color3.fromRGB(200,80,80))
end)

createToggle("Auto Collect Chest", "Kumpul chest → auto hop server", 3, function(on)
    State.AutoChest = on
    if on then
        task.spawn(runAutoChest)
    end
    setStatus(on and "AutoChest ON" or "AutoChest OFF", on and Color3.fromRGB(100,220,100) or Color3.fromRGB(200,80,80))
end)

setStatus("Hub loaded! Tap toggle untuk aktifin")
print("[Hub] Loaded! ESP + AutoHop + AutoChest")
