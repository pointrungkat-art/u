# ui-engineering — CheatDev UI Design & Engineering Skill

> Build Roblox cheat UIs yang beautiful, responsive, dan fully functional.
> Galaxy/purple design language. Drawing API + ScreenGui. Semua komponen siap pakai.

## Design System — Galaxy Palette

```lua
local C = {
    BG      = Color3.fromRGB(10,   8,  20),   -- deep galaxy background
    BG2     = Color3.fromRGB(18,  14,  35),   -- card / panel
    BG3     = Color3.fromRGB(24,  20,  45),   -- input / secondary
    ACCENT  = Color3.fromRGB(180,  80, 255),   -- purple (primary accent)
    ACC2    = Color3.fromRGB(80,  200, 255),   -- cyan (secondary accent)
    FIRE    = Color3.fromRGB(255, 140,  30),   -- orange (action / alert)
    TEXT    = Color3.fromRGB(230, 225, 255),   -- primary text
    DIM     = Color3.fromRGB(120, 110, 150),   -- muted / placeholder
    OK      = Color3.fromRGB(80,  255, 130),   -- success green
    ERR     = Color3.fromRGB(255,  70,  70),   -- error red
    WARN    = Color3.fromRGB(255, 200,  50),   -- warning yellow
}
```

**Rule:** Selalu pakai token ini — jangan hardcode warna di component langsung.

---

## Typography Scale

```lua
-- Font: GothamBlack (display), GothamBold (heading/button), Gotham (body/dim)
-- Scale: Display=22+ · Heading=16-18 · Body=13-14 · Caption=10-12
-- Letter spacing untuk ALL-CAPS label: LetterSpacing = 2

-- Title besar
TextSize = 22; Font = Enum.Font.GothamBlack; TextColor3 = C.ACCENT

-- Section heading
TextSize = 16; Font = Enum.Font.GothamBold; TextColor3 = C.TEXT

-- Toggle label
TextSize = 13; Font = Enum.Font.GothamBold; TextColor3 = C.TEXT

-- Caption / status
TextSize = 11; Font = Enum.Font.Gotham; TextColor3 = C.DIM

-- ALL-CAPS label (input hint, section marker)
TextSize = 11; Font = Enum.Font.GothamBold; TextColor3 = C.DIM; LetterSpacing = 2
```

---

## Tween Helpers (wajib ada di setiap UI module)

```lua
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
```

---

## Core Components

### 1. Panel (Window Frame)
```lua
local function makePanel(parent, w, h, posX, posY)
    -- Card
    local card = Instance.new("Frame", parent)
    card.Size = UDim2.new(0, w, 0, h)
    card.Position = UDim2.new(posX, 0, posY, 0)
    card.BackgroundColor3 = C.BG2
    card.BorderSizePixel = 0
    Instance.new("UICorner", card).CornerRadius = UDim.new(0, 10)

    -- Glow border
    local glow = Instance.new("Frame", card)
    glow.Size = UDim2.new(1, 8, 1, 8)
    glow.Position = UDim2.new(0, -4, 0, -4)
    glow.BackgroundColor3 = C.ACCENT
    glow.BackgroundTransparency = 0.65
    glow.BorderSizePixel = 0
    glow.ZIndex = card.ZIndex - 1
    Instance.new("UICorner", glow).CornerRadius = UDim.new(0, 13)

    -- Top accent bar (3px)
    local bar = Instance.new("Frame", card)
    bar.Size = UDim2.new(1, 0, 0, 3)
    bar.BackgroundColor3 = C.ACCENT
    bar.BorderSizePixel = 0
    Instance.new("UICorner", bar).CornerRadius = UDim.new(0, 10)

    return card, glow
end
```

### 2. Draggable Title Bar
```lua
local function makeTitleBar(card, titleText, subtitleText, TW, UIS)
    local tbar = Instance.new("Frame", card)
    tbar.Size = UDim2.new(1, 0, 0, 46)
    tbar.BackgroundColor3 = C.BG3
    tbar.BorderSizePixel = 0
    Instance.new("UICorner", tbar).CornerRadius = UDim.new(0, 10)

    -- Cover bottom-radius of tbar with a fill
    local fix = Instance.new("Frame", tbar)
    fix.Size = UDim2.new(1, 0, 0.5, 0); fix.Position = UDim2.new(0,0,0.5,0)
    fix.BackgroundColor3 = C.BG3; fix.BorderSizePixel = 0

    local title = Instance.new("TextLabel", tbar)
    title.Size = UDim2.new(0.75, 0, 0, 22); title.Position = UDim2.new(0, 12, 0, 5)
    title.BackgroundTransparency = 1; title.Text = titleText
    title.TextSize = 16; title.Font = Enum.Font.GothamBold
    title.TextColor3 = C.ACCENT; title.TextXAlignment = Enum.TextXAlignment.Left

    local sub = Instance.new("TextLabel", tbar)
    sub.Size = UDim2.new(0.85, 0, 0, 14); sub.Position = UDim2.new(0, 13, 0, 28)
    sub.BackgroundTransparency = 1; sub.Text = subtitleText or ""
    sub.TextSize = 10; sub.Font = Enum.Font.Gotham
    sub.TextColor3 = C.DIM; sub.TextXAlignment = Enum.TextXAlignment.Left

    -- Drag logic
    local drag, ds, sp = false, nil, nil
    tbar.InputBegan:Connect(function(i)
        if i.UserInputType == Enum.UserInputType.MouseButton1 then
            drag=true; ds=i.Position; sp=card.Position
        end
    end)
    UIS.InputChanged:Connect(function(i)
        if drag and i.UserInputType==Enum.UserInputType.MouseMovement then
            local d=i.Position-ds
            card.Position=UDim2.new(sp.X.Scale,sp.X.Offset+d.X,sp.Y.Scale,sp.Y.Offset+d.Y)
        end
    end)
    UIS.InputEnded:Connect(function(i)
        if i.UserInputType==Enum.UserInputType.MouseButton1 then drag=false end
    end)

    return tbar
end
```

### 3. Toggle (Pill Switch)
```lua
local function makeToggle(parent, labelText, initState, order, TW, onChange)
    local row = Instance.new("Frame", parent)
    row.Size = UDim2.new(1, 0, 0, 32); row.BackgroundTransparency = 1
    row.LayoutOrder = order

    local bg = Instance.new("Frame", row)
    bg.Size = UDim2.new(1, 0, 1, 0); bg.BackgroundColor3 = C.BG3
    bg.BackgroundTransparency = 0.3; bg.BorderSizePixel = 0
    Instance.new("UICorner", bg).CornerRadius = UDim.new(0, 6)

    -- Label
    local lbl = Instance.new("TextLabel", bg)
    lbl.Size = UDim2.new(1, -60, 1, 0); lbl.Position = UDim2.new(0, 10, 0, 0)
    lbl.BackgroundTransparency = 1; lbl.Text = labelText
    lbl.TextSize = 13; lbl.Font = Enum.Font.GothamBold
    lbl.TextColor3 = C.TEXT; lbl.TextXAlignment = Enum.TextXAlignment.Left

    -- Pill
    local pill = Instance.new("Frame", bg)
    pill.Size = UDim2.new(0, 38, 0, 22)
    pill.Position = initState and UDim2.new(1,-46,0.5,-11) or UDim2.new(1,-84,0.5,-11)
    -- ^ Note: pill slides between two X offsets
    pill.BackgroundColor3 = initState and C.ACCENT or C.BG
    pill.BorderSizePixel = 0
    Instance.new("UICorner", pill).CornerRadius = UDim.new(1, 0)

    -- Wait — fixed positions:
    pill.Position = UDim2.new(1, -46, 0.5, -11)
    local ON_POS  = UDim2.new(1, -46, 0.5, -11)
    local OFF_POS = UDim2.new(1, -84, 0.5, -11)
    pill.Position = initState and ON_POS or OFF_POS
    pill.BackgroundColor3 = initState and C.ACCENT or Color3.fromRGB(40,35,55)

    -- Knob
    local knob = Instance.new("Frame", pill)
    knob.Size = UDim2.new(0, 18, 0, 18)
    knob.Position = initState and UDim2.new(1,-20,0.5,-9) or UDim2.new(0,2,0.5,-9)
    knob.BackgroundColor3 = Color3.new(1,1,1); knob.BorderSizePixel = 0
    Instance.new("UICorner", knob).CornerRadius = UDim.new(1, 0)

    local cur = initState
    local hit = Instance.new("TextButton", bg)
    hit.Size = UDim2.new(1,0,1,0); hit.BackgroundTransparency=1; hit.Text=""

    hit.MouseButton1Click:Connect(function()
        cur = not cur
        TW:Create(pill, TweenInfo.new(0.18, Enum.EasingStyle.Quad), {
            BackgroundColor3 = cur and C.ACCENT or Color3.fromRGB(40,35,55),
            Position = cur and ON_POS or OFF_POS,
        }):Play()
        TW:Create(knob, TweenInfo.new(0.18, Enum.EasingStyle.Quad), {
            Position = cur and UDim2.new(1,-20,0.5,-9) or UDim2.new(0,2,0.5,-9)
        }):Play()
        if onChange then onChange(cur) end
    end)

    return row, function() return cur end
end
```

### 4. Button
```lua
local function makeButton(parent, labelText, order, TW, callback, accent)
    local col = accent or C.ACCENT
    local btn = Instance.new("TextButton", parent)
    btn.Size = UDim2.new(1, 0, 0, 34); btn.LayoutOrder = order
    btn.BackgroundColor3 = col; btn.AutoButtonColor = false
    btn.BorderSizePixel = 0
    btn.Text = labelText; btn.TextSize = 13
    btn.Font = Enum.Font.GothamBold; btn.TextColor3 = Color3.new(1,1,1)
    Instance.new("UICorner", btn).CornerRadius = UDim.new(0, 6)

    btn.MouseEnter:Connect(function()
        TW:Create(btn, TweenInfo.new(0.12), {BackgroundColor3 = Color3.new(
            math.min(col.R+0.1,1), math.min(col.G+0.1,1), math.min(col.B+0.1,1)
        )}):Play()
    end)
    btn.MouseLeave:Connect(function()
        TW:Create(btn, TweenInfo.new(0.15), {BackgroundColor3 = col}):Play()
    end)
    btn.MouseButton1Click:Connect(function()
        TW:Create(btn, TweenInfo.new(0.08), {BackgroundColor3 = C.ACC2}):Play()
        task.wait(0.1)
        TW:Create(btn, TweenInfo.new(0.12), {BackgroundColor3 = col}):Play()
        if callback then callback() end
    end)
    return btn
end
```

### 5. Section Separator
```lua
local function makeSection(parent, text, order, col)
    local frame = Instance.new("Frame", parent)
    frame.Size = UDim2.new(1,0,0,24); frame.BackgroundTransparency=1
    frame.LayoutOrder = order

    local line = Instance.new("Frame", frame)
    line.Size = UDim2.new(1,0,0,1); line.Position = UDim2.new(0,0,0.5,0)
    line.BackgroundColor3 = col or C.ACCENT; line.BackgroundTransparency = 0.75
    line.BorderSizePixel = 0

    local lbl = Instance.new("TextLabel", frame)
    lbl.Size = UDim2.new(0,120,1,0); lbl.BackgroundColor3=C.BG2; lbl.BorderSizePixel=0
    lbl.TextSize=10; lbl.Font=Enum.Font.GothamBold
    lbl.TextColor3= col or C.ACCENT; lbl.Text="  "..text.."  "
    lbl.TextXAlignment=Enum.TextXAlignment.Center

    return frame
end
```

### 6. Input Field
```lua
local function makeInput(parent, placeholder, posY, masked)
    local bg = Instance.new("Frame", parent)
    bg.Size = UDim2.new(0.85, 0, 0, 46)
    bg.Position = UDim2.new(0.075, 0, 0, posY)
    bg.BackgroundColor3 = C.BG; bg.BackgroundTransparency = 0.15
    bg.BorderSizePixel = 0
    Instance.new("UICorner", bg).CornerRadius = UDim.new(0, 8)
    local stroke = Instance.new("UIStroke", bg)
    stroke.Color = C.ACCENT; stroke.Transparency = 0.6; stroke.Thickness = 1.5

    local field = Instance.new("TextBox", bg)
    field.Size = UDim2.new(1, -16, 1, 0); field.Position = UDim2.new(0, 12, 0, 0)
    field.BackgroundTransparency = 1; field.Text = ""
    field.PlaceholderText = placeholder; field.PlaceholderColor3 = C.DIM
    field.TextSize = 15; field.Font = Enum.Font.GothamBold
    field.TextColor3 = C.TEXT; field.TextXAlignment = Enum.TextXAlignment.Left
    field.ClearTextOnFocus = false

    field.Focused:Connect(function() stroke.Transparency = 0.15 end)
    field.FocusLost:Connect(function() stroke.Transparency = 0.6 end)

    return bg, field, stroke
end
```

### 7. Notification Toast
```lua
local function notify(playerGui, msg, level, duration)
    -- level: "ok" | "err" | "warn" | "info"
    local col = level=="ok" and C.OK or level=="err" and C.ERR or level=="warn" and C.WARN or C.ACC2

    local sg = playerGui:FindFirstChild("CDNotify") or (function()
        local g = Instance.new("ScreenGui", playerGui)
        g.Name = "CDNotify"; g.ResetOnSpawn = false
        local ll = Instance.new("UIListLayout", g)
        ll.SortOrder = Enum.SortOrder.LayoutOrder
        ll.VerticalAlignment = Enum.VerticalAlignment.Bottom
        ll.Padding = UDim.new(0, 6)
        local pad = Instance.new("UIPadding", g)
        pad.PaddingBottom = UDim.new(0, 16); pad.PaddingRight = UDim.new(0, 16)
        return g
    end)()

    local toast = Instance.new("Frame", sg)
    toast.Size = UDim2.new(0, 280, 0, 48)
    toast.BackgroundColor3 = C.BG2; toast.BackgroundTransparency = 0.1
    toast.BorderSizePixel = 0; toast.LayoutOrder = -os.clock()
    Instance.new("UICorner", toast).CornerRadius = UDim.new(0, 8)

    local accent = Instance.new("Frame", toast)
    accent.Size = UDim2.new(0, 4, 1, 0); accent.BackgroundColor3 = col
    accent.BorderSizePixel = 0
    Instance.new("UICorner", accent).CornerRadius = UDim.new(0, 4)

    local lbl = Instance.new("TextLabel", toast)
    lbl.Size = UDim2.new(1, -16, 1, 0); lbl.Position = UDim2.new(0, 12, 0, 0)
    lbl.BackgroundTransparency = 1; lbl.Text = msg
    lbl.TextSize = 13; lbl.Font = Enum.Font.GothamBold
    lbl.TextColor3 = C.TEXT; lbl.TextXAlignment = Enum.TextXAlignment.Left
    lbl.TextWrapped = true

    -- Slide in from right
    toast.Position = UDim2.new(1, 10, 0, 0)
    game:GetService("TweenService"):Create(toast, TweenInfo.new(0.25, Enum.EasingStyle.Back), {
        Position = UDim2.new(0, 0, 0, 0)
    }):Play()

    task.delay(duration or 3, function()
        game:GetService("TweenService"):Create(toast, TweenInfo.new(0.2), {
            BackgroundTransparency = 1,
            Position = UDim2.new(1, 10, 0, 0)
        }):Play()
        task.wait(0.25)
        toast:Destroy()
    end)
end
```

### 8. Scroll Content Area
```lua
local function makeScrollArea(parent, topOffset, bottomOffset)
    local clip = Instance.new("Frame", parent)
    clip.Size = UDim2.new(1, -16, 1, -(topOffset + bottomOffset))
    clip.Position = UDim2.new(0, 8, 0, topOffset)
    clip.BackgroundTransparency = 1; clip.ClipsDescendants = true

    local scroll = Instance.new("ScrollingFrame", clip)
    scroll.Size = UDim2.new(1, 0, 1, 0)
    scroll.BackgroundTransparency = 1; scroll.BorderSizePixel = 0
    scroll.ScrollBarThickness = 3
    scroll.ScrollBarImageColor3 = C.ACCENT
    scroll.AutomaticCanvasSize = Enum.AutomaticSize.Y
    scroll.CanvasSize = UDim2.new(0, 0, 0, 0)

    local ll = Instance.new("UIListLayout", scroll)
    ll.Padding = UDim.new(0, 3)
    ll.SortOrder = Enum.SortOrder.LayoutOrder

    local pad = Instance.new("UIPadding", scroll)
    pad.PaddingTop = UDim.new(0, 4); pad.PaddingBottom = UDim.new(0, 4)

    return scroll
end
```

---

## Animation Recipes

### Spring In (panel open)
```lua
-- Start off-screen top, spring bounce to center
card.Position = UDim2.new(0.5, -W/2, -0.7, 0)
TW:Create(card, TweenInfo.new(0.55, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
    Position = UDim2.new(0.5, -W/2, 0.5, -H/2)
}):Play()
```

### Slide Out (panel close)
```lua
TW:Create(card, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.In), {
    Position = UDim2.new(0.5, -W/2, 1.5, 0)
}):Play()
task.wait(0.35); sg:Destroy()
```

### Shake (wrong key / error)
```lua
local origPos = card.Position
local shakeSteps = {8, -12, 10, -8, 5, -3, 1, 0}
task.spawn(function()
    for _, offset in ipairs(shakeSteps) do
        card.Position = UDim2.new(0.5, -W/2 + offset, origPos.Y.Scale, origPos.Y.Offset)
        task.wait(0.04)
    end
    card.Position = origPos
end)
```

### Glow Pulse (ambient, idle)
```lua
task.spawn(function()
    while true do
        TW:Create(glowBorder, TweenInfo.new(1.4, Enum.EasingStyle.Sine), {BackgroundTransparency=0.5}):Play()
        task.wait(1.4)
        TW:Create(glowBorder, TweenInfo.new(1.4, Enum.EasingStyle.Sine), {BackgroundTransparency=0.78}):Play()
        task.wait(1.4)
    end
end)
```

### Press Ripple (button)
```lua
btn.MouseButton1Click:Connect(function()
    TW:Create(btn, TweenInfo.new(0.07), {BackgroundColor3 = C.ACC2}):Play()
    task.wait(0.1)
    TW:Create(btn, TweenInfo.new(0.15), {BackgroundColor3 = originalColor}):Play()
end)
```

---

## Verify Panel Recipe

Full verify panel → `cheatdev/ui/verifyPanel.lua`

```lua
-- Load dan gunakan:
local VP = loadstring(game:HttpGet(BASE.."ui/verifyPanel.lua"))()
VP(Core, function(passed)
    if passed then
        buildMainGUI()   -- proceed ke main UI
    end
end)
```

Features:
- Spring-in animation
- Masked key input dengan eye toggle
- Enter key support
- Error shake + red border
- Success green flash → auto close
- Ambient star twinkle background
- Glow pulse border

---

## Full Panel Template (copy-paste start)

```lua
-- Minimal scaffold buat panel baru
local function buildMyPanel(Core, TW, UIS, LP)
    local C = { --[[ palette tokens --]] }
    local sg = Instance.new("ScreenGui", LP.PlayerGui)
    sg.Name = "MyPanel"; sg.ResetOnSpawn = false

    -- Card
    local W, H = 360, 480
    local card = Instance.new("Frame", sg)
    card.Size = UDim2.new(0, W, 0, H)
    card.Position = UDim2.new(0.5, -W/2, -0.7, 0)  -- start above
    card.BackgroundColor3 = C.BG2; card.BorderSizePixel = 0
    Instance.new("UICorner", card).CornerRadius = UDim.new(0, 12)

    -- Spring in
    TW:Create(card, TweenInfo.new(0.55, Enum.EasingStyle.Back), {
        Position = UDim2.new(0.5, -W/2, 0.5, -H/2)
    }):Play()

    -- Title bar (draggable)
    -- ... (use makeTitleBar)

    -- Content scroll
    -- ... (use makeScrollArea)

    -- Populate with makeToggle / makeButton / makeSection

    return { destroy = function() sg:Destroy() end }
end
```

---

## Rules

1. **Selalu pakai palette tokens** — jangan hardcode hex
2. **UICorner di semua frame** — tidak ada sudut kotak
3. **UIStroke untuk focus/active state** — bukan warna background
4. **LayoutOrder integer ascending** — pakai counter `lo = lo + 1`
5. **ScrollingFrame + UIListLayout** — untuk list konten panjang
6. **ZIndex.Sibling** — untuk layering yang predictable
7. **task.spawn untuk animasi** — jangan block main thread
8. **pcall di semua event handler** — UI tidak boleh crash game
9. **ResetOnSpawn = false** — GUI survive respawn
10. **twPlay helper** — jangan inline `TW:Create(...):Play()` langsung

## When User Types `/ui` or `/panel`

1. Load palette tokens
2. Plan: window size, sections, components needed
3. Build: title bar (draggable) → scroll area → sections + toggles → buttons → bottom bar
4. Animate: spring-in open, slide-out close
5. Wire: setiap toggle connect ke Config, setiap button ke modul
6. Test: semua state (enabled/disabled/error) harus ada visual feedback
