-- XZ Hub v1.0 | RPG Farming Booster
-- Auto Farm + Auto Collect + ESP (Enemy/Item) + Auto Quest + Auto Chest
-- Delta Android Compatible
-- loadstring(game:HttpGet("https://raw.githubusercontent.com/pointrungkat-art/u/main/XZ.lua"))()

local Players         = game:GetService("Players")
local RunService      = game:GetService("RunService")
local TweenService    = game:GetService("TweenService")
local TeleportService = game:GetService("TeleportService")
local HttpService     = game:GetService("HttpService")
local VirtualUser     = game:GetService("VirtualUser")
local UIS             = game:GetService("UserInputService")

local lp     = Players.LocalPlayer
local Camera = workspace.CurrentCamera

local VALID_KEY = "XZRPG"

local State = {
    EnemyESP   = false,
    ItemESP    = false,
    AutoFarm   = false,
    AutoCollect= false,
    AutoQuest  = false,
    AutoChest  = false,
    AutoHop    = false,
}

-- ┌─────────────────────────┐
-- │         COLORS          │
-- └─────────────────────────┘
local C = {
    BG      = Color3.fromRGB(5,  18,  8),
    Panel   = Color3.fromRGB(10, 32, 14),
    Row     = Color3.fromRGB(12, 38, 16),
    Accent  = Color3.fromRGB(40,  180, 80),
    Bright  = Color3.fromRGB(80,  230, 120),
    Text    = Color3.fromRGB(200, 240, 210),
    Sub     = Color3.fromRGB(100, 165, 115),
    Off     = Color3.fromRGB(30,  60,  35),
    Success = Color3.fromRGB(70,  220, 130),
    Error   = Color3.fromRGB(255, 65,  90),
    Warn    = Color3.fromRGB(255, 210, 50),
    Gold    = Color3.fromRGB(255, 200, 50),
}

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name           = "XZHub"
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
keyLogo.Text                 = "⚔ XZ Hub ⚔"
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
MainFrame.Size             = UDim2.new(0, 230, 0, 600)
MainFrame.Position         = UDim2.new(0.5, -115, 0.5, -300)
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
TitleLabel.Text                 = "⚔ XZ Hub v1.0 — RPG"
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
StatusLabel.Text                 = "⚔ XZ Hub Ready"
StatusLabel.TextColor3           = C.Bright
StatusLabel.TextSize             = 11
StatusLabel.Font                 = Enum.Font.Gotham
StatusLabel.TextXAlignment       = Enum.TextXAlignment.Left

local function setStatus(text, color)
    StatusLabel.Text       = "⚔ " .. text
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
        Size     = UDim2.new(0, 230, 0, 600),
        Position = UDim2.new(0.5, -115, 0.5, -300),
    }):Play()
    task.wait(2)
    setStatus("XZ Hub Ready")
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
-- │   KEYWORDS & UTILS      │
-- └─────────────────────────┘
local MOB_KW   = {"mob","enemy","npc","boss","monster","zombie","bandit","pirate",
    "skeleton","demon","slime","golem","dragon","ghost","witch","guard","soldier",
    "wolf","bear","spider","vampire","orc","troll","goblin","wyrm","titan"}
local ITEM_KW  = {"drop","loot","item","coin","gold","gem","ore","wood","stone",
    "material","crystal","potion","scroll","weapon","armor","equipment","reward",
    "pickup","bag","chest","crate","treasure","gift","shard","token","badge"}
local CHEST_KW = {"chest","crate","treasure","box","barrel","jar","vault"}
local QUEST_KW = {"quest","mission","task","npc","villager","merchant","king","mayor",
    "captain","elder","master","trainer","giver","officer","guide","companion"}

local function nameHas(obj, kws)
    local n = obj.Name:lower()
    for _, k in ipairs(kws) do if n:find(k) then return true end end
    return false
end

local function tpTo(pos)
    local r = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
    if r then r.CFrame = CFrame.new(pos + Vector3.new(0, 4, 0)) end
end

local function fireAll(obj)
    for _, v in ipairs(obj:GetDescendants()) do
        if v:IsA("RemoteEvent") or v:IsA("RemoteFunction") then
            pcall(function() v:FireServer() end)
        end
    end
end

local function scanWorkspace(kws)
    local res = {}
    local function scan(parent)
        for _, o in ipairs(parent:GetChildren()) do
            if (o:IsA("Model") or o:IsA("BasePart")) and nameHas(o, kws) then
                local r = o:IsA("Model") and (o.PrimaryPart or o:FindFirstChildWhichIsA("BasePart")) or o
                if r then table.insert(res, {obj=o, pos=r.Position}) end
            end
            scan(o)
        end
    end
    scan(workspace)
    return res
end

-- Sort by distance from player
local function sortByDist(list)
    local hrp = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
    if not hrp then return list end
    table.sort(list, function(a, b)
        return (a.pos - hrp.Position).Magnitude < (b.pos - hrp.Position).Magnitude
    end)
    return list
end

-- ┌─────────────────────────┐
-- │       ENEMY ESP         │
-- └─────────────────────────┘
local EnemyESPObjs = {}
local function newDraw(t, p)
    local d = Drawing.new(t)
    for k, v in next, p do d[k] = v end
    return d
end

local function getOrMakeESP(key)
    if not EnemyESPObjs[key] then
        EnemyESPObjs[key] = {
            Box  = newDraw("Square",{Color=Color3.fromRGB(255,80,80),Thickness=1.5,Visible=false,Filled=false}),
            Bar  = newDraw("Line",{Color=Color3.fromRGB(255,80,80),Thickness=3,Visible=false}),
            BarBg= newDraw("Line",{Color=Color3.fromRGB(60,0,0),Thickness=3,Visible=false}),
            Name = newDraw("Text",{Color=Color3.fromRGB(255,180,180),Size=10,Outline=true,Font=2,Visible=false}),
        }
    end
    return EnemyESPObjs[key]
end

-- ┌─────────────────────────┐
-- │        ITEM ESP         │
-- └─────────────────────────┘
local ItemESPObjs = {}

local function getOrMakeItemESP(key)
    if not ItemESPObjs[key] then
        ItemESPObjs[key] = {
            Label = newDraw("Text",{Color=C.Gold,Size=11,Outline=true,Font=2,Visible=false}),
            Tracer= newDraw("Line",{Color=C.Gold,Thickness=1,Visible=false}),
        }
    end
    return ItemESPObjs[key]
end

local function cleanESPCache()
    local keep = {}
    for _, o in ipairs(workspace:GetDescendants()) do
        if (o:IsA("Model") or o:IsA("BasePart")) and nameHas(o, ITEM_KW) then
            keep[tostring(o)] = true
        end
    end
    for k, v in pairs(ItemESPObjs) do
        if not keep[k] then
            for _, d in pairs(v) do d.Visible=false end
        end
    end
end

-- ┌─────────────────────────┐
-- │       AUTO FARM         │
-- └─────────────────────────┘
local function runAutoFarm()
    while State.AutoFarm do
        local mobs = scanWorkspace(MOB_KW)
        if #mobs == 0 then
            setStatus("No mobs found nearby...", C.Sub)
            task.wait(3)
        else
            mobs = sortByDist(mobs)
            for i, mob in ipairs(mobs) do
                if not State.AutoFarm then break end
                setStatus(string.format("Farming: %s (%d/%d)", mob.obj.Name, i, #mobs), C.Bright)
                tpTo(mob.pos)
                task.wait(0.5)
                -- Try attack remotes
                for _, v in ipairs(mob.obj:GetDescendants()) do
                    if v:IsA("RemoteEvent") then
                        local n = v.Name:lower()
                        if n:find("attack") or n:find("hit") or n:find("damage") or n:find("kill") then
                            pcall(function() v:FireServer(mob.obj) end)
                        end
                    end
                end
                fireAll(mob.obj)
                task.wait(0.6)
            end
        end
        task.wait(1)
    end
end

-- ┌─────────────────────────┐
-- │      AUTO COLLECT       │
-- └─────────────────────────┘
local collectConn
local function runAutoCollect()
    local function collectObj(obj)
        local r = obj:IsA("Model") and (obj.PrimaryPart or obj:FindFirstChildWhichIsA("BasePart")) or obj
        if not r then return end
        tpTo(r.Position)
        task.wait(0.3)
        local pp = obj:FindFirstChildWhichIsA("ProximityPrompt", true)
        if pp then pcall(function() fireproximityprompt(pp) end) task.wait(0.2) end
        fireAll(obj)
    end
    local function scanAndCollect()
        local items = scanWorkspace(ITEM_KW)
        items = sortByDist(items)
        for _, item in ipairs(items) do
            if not State.AutoCollect then return end
            setStatus("Collecting: " .. item.obj.Name, C.Gold)
            collectObj(item.obj)
            task.wait(0.4)
        end
    end
    collectConn = workspace.ChildAdded:Connect(function(c)
        if not State.AutoCollect then return end
        task.wait(0.5)
        if (c:IsA("Model") or c:IsA("BasePart")) and nameHas(c, ITEM_KW) then
            setStatus("Item spawned: " .. c.Name, C.Gold)
            task.wait(0.2)
            collectObj(c)
        end
    end)
    while State.AutoCollect do
        scanAndCollect()
        setStatus("AutoCollect: Watching...", C.Sub)
        task.wait(8)
    end
    if collectConn then collectConn:Disconnect() collectConn = nil end
end

-- ┌─────────────────────────┐
-- │       AUTO QUEST        │
-- └─────────────────────────┘
local function runAutoQuest()
    while State.AutoQuest do
        local npcs = scanWorkspace(QUEST_KW)
        if #npcs == 0 then
            setStatus("No quest NPCs found...", C.Sub)
            task.wait(5)
        else
            npcs = sortByDist(npcs)
            for i, npc in ipairs(npcs) do
                if not State.AutoQuest then break end
                setStatus(string.format("Quest NPC: %s (%d/%d)", npc.obj.Name, i, #npcs), C.Bright)
                tpTo(npc.pos)
                task.wait(0.5)
                -- Interact with proximity prompts
                local pp = npc.obj:FindFirstChildWhichIsA("ProximityPrompt", true)
                if pp then pcall(function() fireproximityprompt(pp) end) task.wait(0.3) end
                -- Try quest remotes
                for _, v in ipairs(npc.obj:GetDescendants()) do
                    if v:IsA("RemoteEvent") or v:IsA("RemoteFunction") then
                        local n = v.Name:lower()
                        if n:find("quest") or n:find("accept") or n:find("talk") or n:find("complete") then
                            pcall(function() v:FireServer(npc.obj) end)
                        end
                    end
                end
                task.wait(0.8)
            end
            setStatus("Quest round done! Re-scanning...", C.Success)
            task.wait(10)
        end
    end
end

-- ┌─────────────────────────┐
-- │       AUTO CHEST        │
-- └─────────────────────────┘
local function getServers()
    local ok,res=pcall(function() return game:HttpGet(string.format("https://games.roblox.com/v1/games/%d/servers/Public?sortOrder=Asc&limit=100",game.PlaceId)) end)
    if not ok then return nil end
    local ok2,data=pcall(function() return HttpService:JSONDecode(res) end)
    if not ok2 or not data or not data.data then return nil end
    return data.data
end

local function hopServer()
    local servers = getServers() if not servers then return end
    local cur = game.JobId ; local picked
    for _, s in ipairs(servers) do if s.id~=cur and (s.playing or 0)>=1 then picked=s break end end
    if not picked then for _, s in ipairs(servers) do if s.id~=cur then picked=s break end end end
    if picked then
        setStatus("Hopping server...", C.Warn) task.wait(1)
        TeleportService:TeleportToPlaceInstance(game.PlaceId, picked.id, lp)
    end
end

local function runAutoChest()
    while State.AutoChest do
        local chests = scanWorkspace(CHEST_KW)
        if #chests == 0 then
            setStatus("No chests found, hopping...", C.Warn)
            task.wait(2) hopServer() task.wait(5)
        else
            chests = sortByDist(chests)
            setStatus(string.format("Found %d chests!", #chests), C.Success)
            for i, c in ipairs(chests) do
                if not State.AutoChest then break end
                setStatus(string.format("Chest %d/%d — %s", i, #chests, c.obj.Name), C.Bright)
                tpTo(c.pos) task.wait(0.5)
                local pp = c.obj:FindFirstChildWhichIsA("ProximityPrompt", true)
                if pp then pcall(function() fireproximityprompt(pp) end) task.wait(0.3) end
                fireAll(c.obj) task.wait(0.5)
            end
            if State.AutoChest then setStatus("Chests done! Hopping...", C.Warn) task.wait(1.5) hopServer() task.wait(5) end
        end
    end
end

local HOP_INTERVAL = 300
local hopElapsed   = 0

-- ┌─────────────────────────┐
-- │       RENDER LOOP       │
-- └─────────────────────────┘
RunService.RenderStepped:Connect(function(dt)
    local vp = Camera.ViewportSize
    local cx, cy = vp.X/2, vp.Y/2
    local lpR = lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")

    -- Enemy ESP (scan NPCs/mobs in workspace)
    if State.EnemyESP then
        local mobs = scanWorkspace(MOB_KW)
        local seen = {}
        for _, mob in ipairs(mobs) do
            local r = mob.obj:IsA("Model") and (mob.obj.PrimaryPart or mob.obj:FindFirstChildWhichIsA("BasePart")) or mob.obj
            if not r then continue end
            local sp, onScreen = Camera:WorldToViewportPoint(r.Position)
            if not onScreen or sp.Z <= 0 then continue end
            local key = tostring(mob.obj)
            seen[key] = true
            local esp = getOrMakeESP(key)
            local dist = lpR and (lpR.Position - r.Position).Magnitude or 0
            -- Box (square)
            local size = 300 / sp.Z
            esp.Box.Position  = Vector2.new(sp.X - size/2, sp.Y - size)
            esp.Box.Size      = Vector2.new(size, size * 2)
            esp.Box.Visible   = true
            -- HP bar if Humanoid exists
            local hum = mob.obj:FindFirstChildOfClass("Humanoid")
            if hum then
                local ratio = math.clamp(hum.Health / math.max(hum.MaxHealth, 1), 0, 1)
                local bx = sp.X - size/2 - 5
                local by1 = sp.Y - size ; local by2 = sp.Y + size
                esp.BarBg.From=Vector2.new(bx,by1) esp.BarBg.To=Vector2.new(bx,by2) esp.BarBg.Visible=true
                local barMid = by1 + (by2-by1)*(1-ratio)
                esp.Bar.From=Vector2.new(bx,barMid) esp.Bar.To=Vector2.new(bx,by2) esp.Bar.Visible=true
                esp.Bar.Color = ratio>0.5 and Color3.fromRGB(70,220,130) or ratio>0.25 and Color3.fromRGB(255,195,50) or Color3.fromRGB(255,65,90)
            end
            esp.Name.Text=mob.obj.Name..string.format(" [%.0fm]",dist/5)
            esp.Name.Position=Vector2.new(sp.X, sp.Y - size - 14) esp.Name.Visible=true
        end
        for k, v in pairs(EnemyESPObjs) do
            if not seen[k] then for _, d in pairs(v) do d.Visible=false end end
        end
    else
        for _, v in pairs(EnemyESPObjs) do for _, d in pairs(v) do d.Visible=false end end
    end

    -- Item ESP
    if State.ItemESP then
        local items = scanWorkspace(ITEM_KW)
        local seen = {}
        for _, item in ipairs(items) do
            local r = item.obj:IsA("Model") and (item.obj.PrimaryPart or item.obj:FindFirstChildWhichIsA("BasePart")) or item.obj
            if not r then continue end
            local sp, onScreen = Camera:WorldToViewportPoint(r.Position)
            if not onScreen or sp.Z <= 0 then continue end
            local key = tostring(item.obj)
            seen[key] = true
            local esp = getOrMakeItemESP(key)
            local dist = lpR and (lpR.Position - r.Position).Magnitude or 0
            esp.Label.Text = item.obj.Name .. string.format(" (%.0fm)", dist/5)
            esp.Label.Position = Vector2.new(sp.X, sp.Y - 8)
            esp.Label.Visible = true
            esp.Tracer.From = Vector2.new(cx, vp.Y)
            esp.Tracer.To   = Vector2.new(sp.X, sp.Y)
            esp.Tracer.Visible = true
        end
        for k, v in pairs(ItemESPObjs) do
            if not seen[k] then for _, d in pairs(v) do d.Visible=false end end
        end
    else
        for _, v in pairs(ItemESPObjs) do for _, d in pairs(v) do d.Visible=false end end
    end

    -- Auto Hop timer
    if State.AutoHop then
        hopElapsed += dt
        if hopElapsed >= HOP_INTERVAL then hopElapsed = 0 task.spawn(hopServer) end
    else hopElapsed = 0 end
end)

lp.Idled:Connect(function() VirtualUser:CaptureController() VirtualUser:ClickButton2(Vector2.new()) end)

-- ┌─────────────────────────┐
-- │         TOGGLES         │
-- └─────────────────────────┘
createToggle("Enemy ESP","Highlight mob/enemy + HP bar",1,function(on)
    State.EnemyESP=on
    if not on then for _,v in pairs(EnemyESPObjs) do for _,d in pairs(v) do d.Visible=false end end end
    setStatus(on and "Enemy ESP ON" or "Enemy ESP OFF", on and C.Success or C.Error)
end)
createToggle("Item ESP","Highlight drops & loot + tracer",2,function(on)
    State.ItemESP=on
    if not on then for _,v in pairs(ItemESPObjs) do for _,d in pairs(v) do d.Visible=false end end end
    setStatus(on and "Item ESP ON" or "Item ESP OFF", on and C.Success or C.Error)
end)
createToggle("Auto Farm","TP ke mob terdekat & serang otomatis",3,function(on)
    State.AutoFarm=on
    if on then task.spawn(runAutoFarm) end
    setStatus(on and "Auto Farm ON" or "Auto Farm OFF", on and C.Success or C.Error)
end)
createToggle("Auto Collect","Auto ambil drop & loot dari lantai",4,function(on)
    State.AutoCollect=on
    if on then task.spawn(runAutoCollect)
    else if collectConn then collectConn:Disconnect() collectConn=nil end end
    setStatus(on and "Auto Collect ON" or "Auto Collect OFF", on and C.Success or C.Error)
end)
createToggle("Auto Quest","TP ke NPC quest & interact otomatis",5,function(on)
    State.AutoQuest=on
    if on then task.spawn(runAutoQuest) end
    setStatus(on and "Auto Quest ON" or "Auto Quest OFF", on and C.Success or C.Error)
end)
createToggle("Auto Chest","Collect chest → hop server jika kosong",6,function(on)
    State.AutoChest=on
    if on then task.spawn(runAutoChest) end
    setStatus(on and "Auto Chest ON" or "Auto Chest OFF", on and C.Success or C.Error)
end)
createToggle("Auto Hop","Pindah server tiap 5 menit + anti-AFK",7,function(on)
    State.AutoHop=on ; hopElapsed=0
    setStatus(on and "Auto Hop ON" or "Auto Hop OFF", on and C.Success or C.Error)
end)

print("[XZ Hub] v1.0 RPG Loaded!")
