-- XC Crosshair | Aim Assist + Hitmarker
-- Delta Android Compatible
-- loadstring(game:HttpGet("RAW_URL"))()

local Players    = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Camera     = workspace.CurrentCamera
local lp         = Players.LocalPlayer

-- ┌─────────────────────────┐
-- │    CROSSHAIR CONFIG      │
-- └─────────────────────────┘
local CrossConfig = {
    Style        = "CrossDot",  -- Cross | Dot | Circle | CrossDot | TShape
    Color        = Color3.fromRGB(255, 255, 255),
    OutlineColor = Color3.fromRGB(0, 0, 0),
    Outline      = true,
    Size         = 10,
    Thickness    = 1.5,
    Gap          = 4,
    DotRadius    = 2,
    CircleRadius = 18,
}

-- ┌─────────────────────────┐
-- │    AIM ASSIST CONFIG     │
-- └─────────────────────────┘
local AimConfig = {
    Enabled    = true,
    FOV        = 90,      -- radius deteksi dari crosshair (pixel)
    Strength   = 0.10,   -- kekuatan pull (0.05=sangat ringan, 0.2=kuat)
    Target     = "Head", -- "Head" / "HumanoidRootPart"
    ShowFOV    = false,  -- tampilkan lingkaran FOV
    TeamCheck  = false,  -- true = skip teammate
}

-- ┌─────────────────────────┐
-- │    HITMARKER CONFIG      │
-- └─────────────────────────┘
local HitConfig = {
    Enabled  = true,
    Color    = Color3.fromRGB(255, 60, 60),
    Size     = 8,     -- panjang garis X
    Thick    = 1.5,
    Duration = 0.12,  -- lama tampil (detik)
}

-- ┌─────────────────────────┐
-- │    DRAWING OBJECTS       │
-- └─────────────────────────┘
local function newLine(col, thick)
    local d=Drawing.new("Line") d.Color=col d.Thickness=thick d.Visible=false return d
end
local function newCirc(col, thick, fill, rad)
    local d=Drawing.new("Circle") d.Color=col d.Thickness=thick or 1
    d.Filled=fill or false d.Radius=rad or 5 d.Visible=false return d
end

local OL = CrossConfig.Thickness + 2

-- Crosshair lines
local CL = {
    oTop=newLine(CrossConfig.OutlineColor,OL), oBot=newLine(CrossConfig.OutlineColor,OL),
    oLeft=newLine(CrossConfig.OutlineColor,OL), oRight=newLine(CrossConfig.OutlineColor,OL),
    top=newLine(CrossConfig.Color,CrossConfig.Thickness), bot=newLine(CrossConfig.Color,CrossConfig.Thickness),
    left=newLine(CrossConfig.Color,CrossConfig.Thickness), right=newLine(CrossConfig.Color,CrossConfig.Thickness),
}
local TL = {
    oTop=newLine(CrossConfig.OutlineColor,OL), oLeft=newLine(CrossConfig.OutlineColor,OL), oRight=newLine(CrossConfig.OutlineColor,OL),
    top=newLine(CrossConfig.Color,CrossConfig.Thickness), left=newLine(CrossConfig.Color,CrossConfig.Thickness), right=newLine(CrossConfig.Color,CrossConfig.Thickness),
}
local dotOut  = newCirc(CrossConfig.OutlineColor,1,true,CrossConfig.DotRadius+1.5)
local dot     = newCirc(CrossConfig.Color,1,true,CrossConfig.DotRadius)
local circOut = newCirc(CrossConfig.OutlineColor,CrossConfig.Thickness+1.5,false,CrossConfig.CircleRadius)
local circ    = newCirc(CrossConfig.Color,CrossConfig.Thickness,false,CrossConfig.CircleRadius)

-- FOV circle
local fovCirc = newCirc(Color3.fromRGB(200,200,200), 1, false, AimConfig.FOV)
fovCirc.Transparency = 0.6

-- Hitmarker (X shape = 2 diagonal lines)
local HM = {
    oL1=newLine(Color3.fromRGB(0,0,0), HitConfig.Thick+1.5),
    oL2=newLine(Color3.fromRGB(0,0,0), HitConfig.Thick+1.5),
    l1=newLine(HitConfig.Color, HitConfig.Thick),
    l2=newLine(HitConfig.Color, HitConfig.Thick),
}

local allObjs = {
    CL.oTop,CL.oBot,CL.oLeft,CL.oRight,CL.top,CL.bot,CL.left,CL.right,
    TL.oTop,TL.oLeft,TL.oRight,TL.top,TL.left,TL.right,
    dotOut,dot,circOut,circ,fovCirc,
    HM.oL1,HM.oL2,HM.l1,HM.l2,
}
local function hideAll() for _,o in ipairs(allObjs) do o.Visible=false end end

-- ┌─────────────────────────┐
-- │      CROSSHAIR DRAW     │
-- └─────────────────────────┘
local function drawCrosshair()
    local vp=Camera.ViewportSize
    local cx,cy=vp.X/2,vp.Y/2
    local g,s=CrossConfig.Gap,CrossConfig.Size
    local ol=CrossConfig.Outline
    local ctr=Vector2.new(cx,cy)
    local style=CrossConfig.Style

    -- sembunyiin semua crosshair dulu (jangan hide hitmarker)
    CL.oTop.Visible=false CL.oBot.Visible=false CL.oLeft.Visible=false CL.oRight.Visible=false
    CL.top.Visible=false CL.bot.Visible=false CL.left.Visible=false CL.right.Visible=false
    TL.oTop.Visible=false TL.oLeft.Visible=false TL.oRight.Visible=false
    TL.top.Visible=false TL.left.Visible=false TL.right.Visible=false
    dotOut.Visible=false dot.Visible=false circOut.Visible=false circ.Visible=false

    if style=="Cross" or style=="CrossDot" then
        if ol then
            CL.oTop.From=Vector2.new(cx,cy-g-s) CL.oTop.To=Vector2.new(cx,cy-g) CL.oTop.Visible=true
            CL.oBot.From=Vector2.new(cx,cy+g) CL.oBot.To=Vector2.new(cx,cy+g+s) CL.oBot.Visible=true
            CL.oLeft.From=Vector2.new(cx-g-s,cy) CL.oLeft.To=Vector2.new(cx-g,cy) CL.oLeft.Visible=true
            CL.oRight.From=Vector2.new(cx+g,cy) CL.oRight.To=Vector2.new(cx+g+s,cy) CL.oRight.Visible=true
        end
        CL.top.From=Vector2.new(cx,cy-g-s) CL.top.To=Vector2.new(cx,cy-g) CL.top.Visible=true
        CL.bot.From=Vector2.new(cx,cy+g) CL.bot.To=Vector2.new(cx,cy+g+s) CL.bot.Visible=true
        CL.left.From=Vector2.new(cx-g-s,cy) CL.left.To=Vector2.new(cx-g,cy) CL.left.Visible=true
        CL.right.From=Vector2.new(cx+g,cy) CL.right.To=Vector2.new(cx+g+s,cy) CL.right.Visible=true
    end
    if style=="Dot" or style=="CrossDot" then
        if ol then dotOut.Position=ctr dotOut.Visible=true end
        dot.Position=ctr dot.Visible=true
    end
    if style=="Circle" then
        if ol then circOut.Position=ctr circOut.Visible=true end
        circ.Position=ctr circ.Visible=true
    end
    if style=="TShape" then
        if ol then
            TL.oTop.From=Vector2.new(cx,cy-g-s) TL.oTop.To=Vector2.new(cx,cy-g) TL.oTop.Visible=true
            TL.oLeft.From=Vector2.new(cx-g-s,cy) TL.oLeft.To=Vector2.new(cx-g,cy) TL.oLeft.Visible=true
            TL.oRight.From=Vector2.new(cx+g,cy) TL.oRight.To=Vector2.new(cx+g+s,cy) TL.oRight.Visible=true
        end
        TL.top.From=Vector2.new(cx,cy-g-s) TL.top.To=Vector2.new(cx,cy-g) TL.top.Visible=true
        TL.left.From=Vector2.new(cx-g-s,cy) TL.left.To=Vector2.new(cx-g,cy) TL.left.Visible=true
        TL.right.From=Vector2.new(cx+g,cy) TL.right.To=Vector2.new(cx+g+s,cy) TL.right.Visible=true
    end
end

-- ┌─────────────────────────┐
-- │       AIM ASSIST        │
-- └─────────────────────────┘
local function getClosest()
    local vp=Camera.ViewportSize
    local center=Vector2.new(vp.X/2,vp.Y/2)
    local bestDist=AimConfig.FOV
    local bestPart=nil

    for _,player in ipairs(Players:GetPlayers()) do
        if player==lp then continue end
        if AimConfig.TeamCheck and player.Team==lp.Team then continue end
        local char=player.Character
        local hum=char and char:FindFirstChildOfClass("Humanoid")
        if not(hum and hum.Health>0) then continue end
        local part=char:FindFirstChild(AimConfig.Target)
        if not part then continue end
        local sp,onScreen=Camera:WorldToViewportPoint(part.Position)
        if not onScreen or sp.Z<=0 then continue end
        local dist=(Vector2.new(sp.X,sp.Y)-center).Magnitude
        if dist<bestDist then bestDist=dist bestPart=part end
    end
    return bestPart
end

local function runAimAssist()
    if not AimConfig.Enabled then
        fovCirc.Visible=false return
    end
    local vp=Camera.ViewportSize
    local center=Vector2.new(vp.X/2,vp.Y/2)

    -- FOV circle visual
    if AimConfig.ShowFOV then
        fovCirc.Position=center fovCirc.Radius=AimConfig.FOV fovCirc.Visible=true
    else fovCirc.Visible=false end

    local targetPart=getClosest()
    if not targetPart then return end

    -- Soft pull: lerp camera ke arah target (bukan lock, cuma nempel halus)
    local cur=Camera.CFrame
    local lookAt=CFrame.lookAt(cur.Position, targetPart.Position)
    Camera.CFrame=cur:Lerp(lookAt, AimConfig.Strength)
end

-- ┌─────────────────────────┐
-- │       HITMARKER         │
-- └─────────────────────────┘
local hitActive=false
local function showHit()
    if hitActive then return end
    hitActive=true
    local vp=Camera.ViewportSize
    local cx,cy=vp.X/2,vp.Y/2
    local s=HitConfig.Size
    -- outline
    HM.oL1.From=Vector2.new(cx-s,cy-s) HM.oL1.To=Vector2.new(cx+s,cy+s) HM.oL1.Visible=true
    HM.oL2.From=Vector2.new(cx+s,cy-s) HM.oL2.To=Vector2.new(cx-s,cy+s) HM.oL2.Visible=true
    -- main X
    HM.l1.From=Vector2.new(cx-s,cy-s) HM.l1.To=Vector2.new(cx+s,cy+s) HM.l1.Visible=true
    HM.l2.From=Vector2.new(cx+s,cy-s) HM.l2.To=Vector2.new(cx-s,cy+s) HM.l2.Visible=true
    task.delay(HitConfig.Duration, function()
        HM.oL1.Visible=false HM.oL2.Visible=false
        HM.l1.Visible=false HM.l2.Visible=false
        hitActive=false
    end)
end

-- Detect hit: monitor health turun pada player di sekitar kita
local tracked={}
local function trackPlayer(player)
    if player==lp then return end
    local function onChar(char)
        local hum=char:WaitForChild("Humanoid")
        if tracked[player] then tracked[player]:Disconnect() end
        local prevHp=hum.Health
        tracked[player]=hum.HealthChanged:Connect(function(newHp)
            if not HitConfig.Enabled then return end
            if newHp<prevHp then
                local lpRoot=lp.Character and lp.Character:FindFirstChild("HumanoidRootPart")
                local theirRoot=char:FindFirstChild("HumanoidRootPart")
                if lpRoot and theirRoot then
                    if (lpRoot.Position-theirRoot.Position).Magnitude<300 then
                        showHit()
                    end
                end
            end
            prevHp=newHp
        end)
    end
    if player.Character then onChar(player.Character) end
    player.CharacterAdded:Connect(onChar)
end
for _,p in ipairs(Players:GetPlayers()) do trackPlayer(p) end
Players.PlayerAdded:Connect(trackPlayer)
Players.PlayerRemoving:Connect(function(p)
    if tracked[p] then tracked[p]:Disconnect() tracked[p]=nil end
end)

-- ┌─────────────────────────┐
-- │       CONTROL GUI       │
-- └─────────────────────────┘
local Gui=Instance.new("ScreenGui")
Gui.Name="XCCrosshair" Gui.ResetOnSpawn=false
Gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling
Gui.Parent=game:GetService("CoreGui")

local C={
    BG=Color3.fromRGB(8,5,20), Panel=Color3.fromRGB(16,10,38),
    Accent=Color3.fromRGB(130,40,220), Bright=Color3.fromRGB(185,90,255),
    Text=Color3.fromRGB(220,200,255), Sub=Color3.fromRGB(130,105,180),
    Off=Color3.fromRGB(50,35,78),
}

local Panel=Instance.new("Frame",Gui)
Panel.Size=UDim2.new(0,165,0,260)
Panel.Position=UDim2.new(0,10,1,1,-270)
Panel.BackgroundColor3=C.BG Panel.BorderSizePixel=0
Instance.new("UICorner",Panel).CornerRadius=UDim.new(0,10)
local ps=Instance.new("UIStroke",Panel) ps.Color=C.Accent ps.Thickness=1.5

local function label(parent, text, size, color, posY)
    local l=Instance.new("TextLabel",parent)
    l.Size=UDim2.new(1,0,0,size) l.Position=UDim2.new(0,0,0,posY)
    l.BackgroundTransparency=1 l.Text=text
    l.TextColor3=color l.TextSize=12 l.Font=Enum.Font.GothamBold
    return l
end

label(Panel,"✴ XC Crosshair",22,C.Bright,8)

-- Style buttons
local styles={"CrossDot","Cross","Dot","Circle","TShape"}
local styleBtns={}
local syFrame=Instance.new("Frame",Panel)
syFrame.Size=UDim2.new(1,-12,0,140) syFrame.Position=UDim2.new(0,6,0,32)
syFrame.BackgroundTransparency=1
local syList=Instance.new("UIListLayout",syFrame) syList.Padding=UDim.new(0,3)

for i,sty in ipairs(styles) do
    local btn=Instance.new("TextButton",syFrame)
    btn.Size=UDim2.new(1,0,0,22)
    btn.BackgroundColor3=sty==CrossConfig.Style and C.Accent or C.Panel
    btn.BorderSizePixel=0 btn.Text=sty btn.TextColor3=C.Text
    btn.TextSize=11 btn.Font=Enum.Font.GothamBold
    Instance.new("UICorner",btn).CornerRadius=UDim.new(0,5)
    styleBtns[sty]=btn
    btn.MouseButton1Click:Connect(function()
        CrossConfig.Style=sty
        for _,b in next,styleBtns do TweenService:Create(b,TweenInfo.new(0.15),{BackgroundColor3=C.Panel}):Play() end
        TweenService:Create(btn,TweenInfo.new(0.15),{BackgroundColor3=C.Accent}):Play()
    end)
end

-- Divider
local div=Instance.new("Frame",Panel)
div.Size=UDim2.new(0.85,0,0,1) div.Position=UDim2.new(0.075,0,0,178)
div.BackgroundColor3=C.Off div.BorderSizePixel=0

-- Toggle helper
local function makeToggle(parent, name, yPos, initVal, onChange)
    local row=Instance.new("Frame",parent)
    row.Size=UDim2.new(1,-12,0,28) row.Position=UDim2.new(0,6,0,yPos)
    row.BackgroundTransparency=1

    local lbl=Instance.new("TextLabel",row)
    lbl.Size=UDim2.new(0.65,0,1,0) lbl.BackgroundTransparency=1
    lbl.Text=name lbl.TextColor3=C.Text lbl.TextSize=11
    lbl.Font=Enum.Font.GothamBold lbl.TextXAlignment=Enum.TextXAlignment.Left

    local tbg=Instance.new("Frame",row)
    tbg.Size=UDim2.new(0,40,0,20) tbg.Position=UDim2.new(1,-42,0.5,-10)
    tbg.BackgroundColor3=initVal and C.Accent or C.Off tbg.BorderSizePixel=0
    Instance.new("UICorner",tbg).CornerRadius=UDim.new(1,0)

    local circ=Instance.new("Frame",tbg)
    circ.Size=UDim2.new(0,16,0,16) circ.Position=initVal and UDim2.new(0,22,0.5,-8) or UDim2.new(0,2,0.5,-8)
    circ.BackgroundColor3=initVal and C.Bright or C.Sub circ.BorderSizePixel=0
    Instance.new("UICorner",circ).CornerRadius=UDim.new(1,0)

    local on=initVal
    tbg.InputBegan:Connect(function(i)
        if i.UserInputType==Enum.UserInputType.Touch
        or i.UserInputType==Enum.UserInputType.MouseButton1 then
            on=not on
            TweenService:Create(circ,TweenInfo.new(0.15),{
                Position=on and UDim2.new(0,22,0.5,-8) or UDim2.new(0,2,0.5,-8),
                BackgroundColor3=on and C.Bright or C.Sub,
            }):Play()
            TweenService:Create(tbg,TweenInfo.new(0.15),{BackgroundColor3=on and C.Accent or C.Off}):Play()
            onChange(on)
        end
    end)
end

makeToggle(Panel,"Aim Assist",184,AimConfig.Enabled,function(v) AimConfig.Enabled=v end)
makeToggle(Panel,"Show FOV",216,AimConfig.ShowFOV,function(v) AimConfig.ShowFOV=v end)
makeToggle(Panel,"Hitmarker",216+32,HitConfig.Enabled,function(v) HitConfig.Enabled=v end)

-- ┌─────────────────────────┐
-- │      RENDER LOOP        │
-- └─────────────────────────┘
RunService.RenderStepped:Connect(function()
    drawCrosshair()
    runAimAssist()
end)

print("[XC Crosshair] Loaded! Aim Assist + Hitmarker aktif")
