--[[  CheatDev — ui/devConsole.lua
      Dev Console overlay — command input + live log + module status
      Hotkey: F2 toggle
--]]
return function(Core, Forge)
    local S, U = Core.Services, Core.Utils
    local TW   = S.TweenService
    local LP   = Core.LP

    local COL = {
        BG      = Color3.fromRGB(6, 4, 14),
        BG2     = Color3.fromRGB(14, 10, 28),
        ACCENT  = Color3.fromRGB(180, 80, 255),
        ACCENT2 = Color3.fromRGB(80, 200, 255),
        FIRE    = Color3.fromRGB(255, 140, 30),
        TEXT    = Color3.fromRGB(220, 215, 255),
        DIM     = Color3.fromRGB(110, 100, 140),
        OK      = Color3.fromRGB(80, 255, 130),
        ERR     = Color3.fromRGB(255, 70,  70),
        WARN    = Color3.fromRGB(255, 200, 50),
    }

    local DevCon = {}
    DevCon._open    = false
    DevCon._gui     = nil
    DevCon._logBuf  = {}
    DevCon.MaxLogs  = 60

    -- Listen to core logs
    Core.On("log", function(entry)
        table.insert(DevCon._logBuf, entry)
        if #DevCon._logBuf > DevCon.MaxLogs then
            table.remove(DevCon._logBuf, 1)
        end
        DevCon._refresh()
    end)

    local _logLabel = nil

    function DevCon._refresh()
        if not _logLabel then return end
        local lines = {}
        for i = math.max(1, #DevCon._logBuf - 14), #DevCon._logBuf do
            local e = DevCon._logBuf[i]
            if e then
                local tag   = string.format("[%s]", e.tag or "?")
                lines[#lines+1] = string.format("%-12s %s", tag, e.msg or "")
            end
        end
        _logLabel.Text = table.concat(lines, "\n")
    end

    local function tw(inst, props, t)
        TW:Create(inst, TweenInfo.new(t or 0.2, Enum.EasingStyle.Quad), props):Play()
    end

    local function buildConsole()
        local old = LP.PlayerGui:FindFirstChild("CDConsole")
        if old then old:Destroy() end

        local sg = Instance.new("ScreenGui")
        sg.Name         = "CDConsole"
        sg.ResetOnSpawn = false
        sg.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
        sg.Parent       = LP.PlayerGui
        DevCon._gui     = sg

        -- Main panel
        local panel = Instance.new("Frame")
        panel.Size              = UDim2.new(0, 480, 0, 340)
        panel.Position          = UDim2.new(0, 12, 0.5, -170)
        panel.BackgroundColor3  = COL.BG
        panel.BackgroundTransparency = 0.06
        panel.BorderSizePixel   = 0
        panel.Parent            = sg
        local pc = Instance.new("UICorner"); pc.CornerRadius = UDim.new(0,8); pc.Parent = panel

        -- Title bar
        local tbar = Instance.new("Frame")
        tbar.Size             = UDim2.new(1,0,0,36)
        tbar.BackgroundColor3 = COL.BG2
        tbar.BorderSizePixel  = 0
        tbar.Parent           = panel
        local tc = Instance.new("UICorner"); tc.CornerRadius = UDim.new(0,8); tc.Parent = tbar
        local tfix = Instance.new("Frame"); tfix.Size=UDim2.new(1,0,0.5,0); tfix.Position=UDim2.new(0,0,0.5,0); tfix.BackgroundColor3=COL.BG2; tfix.BorderSizePixel=0; tfix.Parent=tbar

        local title = Instance.new("TextLabel")
        title.Text  = "⚡ DEV CONSOLE  ·  CheatDev v2.0"
        title.TextSize  = 13
        title.TextColor3 = COL.ACCENT
        title.BackgroundTransparency = 1
        title.Font  = Enum.Font.GothamBold
        title.Size  = UDim2.new(0.85,0,1,0)
        title.Position = UDim2.new(0,10,0,0)
        title.TextXAlignment = Enum.TextXAlignment.Left
        title.Parent = tbar

        local closeBtn = Instance.new("TextButton")
        closeBtn.Text = "F2"
        closeBtn.TextSize = 11
        closeBtn.TextColor3 = COL.DIM
        closeBtn.BackgroundTransparency = 1
        closeBtn.Font = Enum.Font.GothamBold
        closeBtn.Size = UDim2.new(0,36,1,0)
        closeBtn.Position = UDim2.new(1,-40,0,0)
        closeBtn.Parent = tbar
        closeBtn.MouseButton1Click:Connect(function() DevCon.Close() end)

        -- Accent line
        local aline = Instance.new("Frame")
        aline.Size = UDim2.new(1,0,0,2); aline.Position = UDim2.new(0,0,0,36)
        aline.BackgroundColor3 = COL.ACCENT; aline.BorderSizePixel = 0; aline.Parent = panel

        -- Module status bar
        local statusBar = Instance.new("Frame")
        statusBar.Size = UDim2.new(1,-16,0,24); statusBar.Position = UDim2.new(0,8,0,44)
        statusBar.BackgroundTransparency = 1; statusBar.BorderSizePixel = 0; statusBar.Parent = panel
        local function statusDot(name, mod, cfg_key)
            local lbl = Instance.new("TextLabel")
            lbl.Text = "● "..name
            lbl.TextSize = 11
            lbl.TextColor3 = (Core.Config[cfg_key] and Core.Config[cfg_key].enabled) and COL.OK or COL.DIM
            lbl.BackgroundTransparency = 1
            lbl.Font = Enum.Font.Gotham
            lbl.AutomaticSize = Enum.AutomaticSize.X
            lbl.Size = UDim2.new(0,0,1,0)
            lbl.Parent = statusBar
            return lbl
        end
        local statusLayout = Instance.new("UIListLayout")
        statusLayout.FillDirection = Enum.FillDirection.Horizontal
        statusLayout.Padding = UDim.new(0,8)
        statusLayout.Parent = statusBar
        statusDot("ESP","ESP","ESP")
        statusDot("AIM","AIM","AIM")
        statusDot("FLY","FLY","FLY")
        statusDot("NC","NOCLIP","NOCLIP")
        statusDot("GOD","GOD","GOD_MODE")
        statusDot("KA","KILLAURA","KILL_AURA")

        -- Log area
        local logBG = Instance.new("Frame")
        logBG.Size = UDim2.new(1,-16,0,180); logBG.Position = UDim2.new(0,8,0,74)
        logBG.BackgroundColor3 = COL.BG2; logBG.BackgroundTransparency = 0.2
        logBG.BorderSizePixel = 0; logBG.Parent = panel
        local lgc = Instance.new("UICorner"); lgc.CornerRadius = UDim.new(0,4); lgc.Parent = logBG

        _logLabel = Instance.new("TextLabel")
        _logLabel.Size = UDim2.new(1,-8,1,-8); _logLabel.Position = UDim2.new(0,4,0,4)
        _logLabel.BackgroundTransparency = 1
        _logLabel.TextColor3 = COL.TEXT; _logLabel.TextSize = 11
        _logLabel.Font = Enum.Font.Code
        _logLabel.TextXAlignment = Enum.TextXAlignment.Left
        _logLabel.TextYAlignment = Enum.TextYAlignment.Top
        _logLabel.TextWrapped = true
        _logLabel.Text = "Dev Console ready. Type /help for commands."
        _logLabel.Parent = logBG
        DevCon._refresh()

        -- Input box
        local inputBG = Instance.new("Frame")
        inputBG.Size = UDim2.new(1,-16,0,32); inputBG.Position = UDim2.new(0,8,0,262)
        inputBG.BackgroundColor3 = COL.BG2; inputBG.BorderSizePixel = 0; inputBG.Parent = panel
        local ic = Instance.new("UICorner"); ic.CornerRadius = UDim.new(0,4); ic.Parent = inputBG

        local prompt = Instance.new("TextLabel")
        prompt.Text = "> "; prompt.TextSize = 13; prompt.TextColor3 = COL.ACCENT
        prompt.BackgroundTransparency = 1; prompt.Font = Enum.Font.Code
        prompt.Size = UDim2.new(0,20,1,0); prompt.Position = UDim2.new(0,6,0,0)
        prompt.Parent = inputBG

        local input = Instance.new("TextBox")
        input.PlaceholderText = "command  (e.g. /c speed_hack  /module esp on  /panic)"
        input.PlaceholderColor3 = COL.DIM
        input.Text = ""; input.TextSize = 13; input.TextColor3 = COL.TEXT
        input.BackgroundTransparency = 1; input.Font = Enum.Font.Code
        input.Size = UDim2.new(1,-32,1,0); input.Position = UDim2.new(0,26,0,0)
        input.TextXAlignment = Enum.TextXAlignment.Left
        input.ClearTextOnFocus = false; input.Parent = inputBG

        -- Run button
        local runBtn = Instance.new("TextButton")
        runBtn.Text = "▶"; runBtn.TextSize = 13; runBtn.TextColor3 = COL.FIRE
        runBtn.BackgroundColor3 = COL.BG; runBtn.BorderSizePixel = 0
        runBtn.Font = Enum.Font.GothamBold
        runBtn.Size = UDim2.new(0,32,0,32); runBtn.Position = UDim2.new(1,-40,0,262)
        local rc = Instance.new("UICorner"); rc.CornerRadius = UDim.new(0,4); rc.Parent = runBtn
        runBtn.Parent = panel

        local function runCmd(cmd)
            cmd = cmd:match("^%s*(.-)%s*$")
            if cmd == "" then return end
            Core.Log("CON", "> "..cmd, "DEV")
            -- parse
            local low = cmd:lower()
            if low == "/help" or low == "help" then
                Core.Log("HELP", "/c <template>  — inject script forge")
                Core.Log("HELP", "/clist          — list templates")
                Core.Log("HELP", "/module <name> <on|off|toggle>")
                Core.Log("HELP", "/panic          — disable all modules")
                Core.Log("HELP", "/cfg <key> <val>— edit config live")
                Core.Log("HELP", "/lua <code>     — run raw lua")
                Core.Log("HELP", "/clear          — clear logs")
            elseif low:sub(1,3) == "/c " or low:sub(1,2) == "c " then
                local name = cmd:match("[Cc]%s+(%S+)") or ""
                Forge.Craft(name)
            elseif low == "/clist" or low == "clist" then
                Forge.List()
            elseif low == "/panic" or low == "panic" then
                Core.Panic()
            elseif low == "/clear" then
                DevCon._logBuf = {}; DevCon._refresh()
            elseif low:sub(1,7) == "/module" then
                local name, action = cmd:match("/module%s+(%S+)%s+(%S+)")
                if name and action then
                    local mod = Core.GetModule(name) or Core.GetModule(name:gsub("^%l",string.upper))
                    if mod then
                        if action:lower()=="on"     and mod.Enable  then mod.Enable()  end
                        if action:lower()=="off"    and mod.Disable then mod.Disable() end
                        if action:lower()=="toggle" and mod.Toggle  then mod.Toggle()  end
                    else
                        Core.Log("CON", "Module not found: "..name, "ERR")
                    end
                end
            elseif low:sub(1,4) == "/lua" then
                local code = cmd:sub(5)
                local ok, err = pcall(loadstring(code))
                if not ok then Core.Log("LUA", tostring(err), "ERR") end
            elseif low:sub(1,4) == "/cfg" then
                Core.Log("CFG", "Live config edit — use /lua to modify Core.Config directly", "WARN")
            else
                -- try raw lua
                local ok, err = pcall(loadstring(cmd))
                if not ok then Core.Log("CON", "Unknown: "..cmd.." | "..tostring(err), "ERR") end
            end
            input.Text = ""
        end

        input.FocusLost:Connect(function(enter)
            if enter then runCmd(input.Text) end
        end)
        runBtn.MouseButton1Click:Connect(function()
            runCmd(input.Text)
        end)

        -- Drag
        local dragging, ds, sp = false, nil, nil
        tbar.InputBegan:Connect(function(i)
            if i.UserInputType == Enum.UserInputType.MouseButton1 then
                dragging = true; ds = i.Position; sp = panel.Position
            end
        end)
        S.UserInputService.InputChanged:Connect(function(i)
            if dragging and i.UserInputType == Enum.UserInputType.MouseMovement then
                local delta = i.Position - ds
                panel.Position = UDim2.new(sp.X.Scale, sp.X.Offset+delta.X, sp.Y.Scale, sp.Y.Offset+delta.Y)
            end
        end)
        S.UserInputService.InputEnded:Connect(function(i)
            if i.UserInputType == Enum.UserInputType.MouseButton1 then dragging = false end
        end)

        -- Open anim
        panel.Position = UDim2.new(-0.4, 0, 0.5, -170)
        tw(panel, {Position = UDim2.new(0, 12, 0.5, -170)}, 0.35)

        DevCon._open = true
        Core.Log("CON", "🔥 Dev Console OPEN — DAR DER DOR, semua kode libas!", "OK")
    end

    function DevCon.Open()
        if DevCon._open and DevCon._gui then return end
        buildConsole()
    end
    function DevCon.Close()
        if DevCon._gui then
            DevCon._gui:Destroy()
            DevCon._gui = nil
            _logLabel   = nil
        end
        DevCon._open = false
    end
    function DevCon.Toggle()
        if DevCon._open then DevCon.Close() else DevCon.Open() end
    end

    Core.Hotkey("F2", function() DevCon.Toggle() end)
    Core.Register("DevConsole", DevCon)
    return DevCon
end
