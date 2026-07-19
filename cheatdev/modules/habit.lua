--[[
  CHEAT DEV — modules/habit.lua
  Habit/Macro system: record player CFrame paths, replay as daily routines.
  Patrol presets auto-hunt fruits / chests / enemies by name tag.
--]]

return function(Core)
    local S   = Core.Services
    local U   = Core.Utils
    local Cfg = Core.Config

    local Habit = {}

    local _habits    = {}          -- { name → { frames={cf,dt}, count } }
    local _recording = false
    local _recName   = nil
    local _recFrames = {}
    local _recTimer  = 0
    local _playing   = false
    local _curHabit  = nil

    local REC_INTERVAL = 0.5      -- seconds between waypoint captures

    -- ── Recording ─────────────────────────────────────────────────
    function Habit.Record(name)
        if _recording then
            Core.Log("HABIT", "Already recording — stop first", "WARN"); return
        end
        _recName   = name or ("hab_" .. math.floor(os.clock()))
        _recFrames = {}
        _recording = true
        _recTimer  = 0
        Core.Log("HABIT", "🔴 Recording [" .. _recName .. "] — move around!", "WARN")
    end

    function Habit.StopRec()
        if not _recording then return end
        _recording = false
        _habits[_recName] = { frames = _recFrames, count = #_recFrames }
        Core.Log("HABIT", "⏹ Saved [" .. _recName .. "] — " .. #_recFrames .. " waypoints", "OK")
    end

    -- ── Playback ──────────────────────────────────────────────────
    function Habit.Stop()
        _playing  = false
        _curHabit = nil
        Core.Log("HABIT", "⏹ Stopped", "INFO")
    end

    function Habit.Play(name, loops)
        local hab = _habits[name]
        if not hab or #hab.frames == 0 then
            Core.Log("HABIT", "Not found: " .. tostring(name), "ERR"); return
        end
        Habit.Stop()
        _playing  = true
        _curHabit = name
        loops = loops or 0

        task.spawn(function()
            local done = 0
            while _playing do
                for _, wp in ipairs(hab.frames) do
                    if not _playing then return end
                    U.TP(wp.cf)
                    task.wait(wp.dt or 0.5)
                end
                done = done + 1
                if loops > 0 and done >= loops then break end
                task.wait(0.2)
            end
            Habit.Stop()
        end)
        Core.Log("HABIT", "▶ Playing [" .. name .. "] loops=" .. (loops == 0 and "∞" or tostring(loops)), "OK")
    end

    function Habit.PlayLast(loops)
        local last = nil
        for k in pairs(_habits) do last = k end
        if last then
            Habit.Play(last, loops)
        else
            Core.Log("HABIT", "No recorded habits yet — hit Record first", "WARN")
        end
    end

    -- ── Patrol Presets ────────────────────────────────────────────
    local function patrol(tags, hopAfter)
        Habit.Stop()
        _playing  = true
        _curHabit = "patrol:" .. table.concat(tags, "|")

        task.spawn(function()
            while _playing do
                local r = U.GetRoot()
                if not r then task.wait(1); continue end

                local found = false
                for _, obj in ipairs(workspace:GetDescendants()) do
                    if not _playing then return end
                    for _, tag in ipairs(tags) do
                        if obj.Name:lower():find(tag:lower()) then
                            local part = obj:IsA("BasePart") and obj
                                or (obj:IsA("Model") and (obj.PrimaryPart or obj:FindFirstChildWhichIsA("BasePart")))
                            if part and (r.Position - part.Position).Magnitude < 2000 then
                                U.TP(CFrame.new(part.Position + Vector3.new(0, 3, 0)))
                                found = true
                                task.wait(1.2)
                                break
                            end
                        end
                    end
                end

                if hopAfter and not found then
                    Core.Log("HABIT", "Patrol done — hopping server", "INFO")
                    pcall(function()
                        S.TeleportService:TeleportToPlaceInstance(game.PlaceId, game.JobId)
                    end)
                    task.wait(5)
                elseif not found then
                    task.wait(2)
                end
                task.wait(0.3)
            end
        end)

        Core.Log("HABIT", "🗺 Patrol [" .. table.concat(tags, ",") .. "] started", "OK")
    end

    Habit.Patrol = {
        Fruit  = function() patrol(Cfg.FRUIT.tags,  true) end,
        Chest  = function() patrol(Cfg.CHEST.tags,  true) end,
        Custom = patrol,
    }

    -- ── Waypoint capture (RenderStepped) ─────────────────────────
    S.RunService.RenderStepped:Connect(function(dt)
        if not _recording then return end
        _recTimer = _recTimer + dt
        if _recTimer >= REC_INTERVAL then
            _recTimer = 0
            local r = U.GetRoot()
            if r then
                table.insert(_recFrames, { cf = r.CFrame, dt = REC_INTERVAL })
            end
        end
    end)

    -- ── Status helpers ────────────────────────────────────────────
    function Habit.IsRec()     return _recording         end
    function Habit.IsPlaying() return _playing           end
    function Habit.CurHabit()  return _curHabit          end
    function Habit.RecCount()  return #_recFrames        end
    function Habit.ListNames()
        local t = {}
        for k in pairs(_habits) do table.insert(t, k) end
        return t
    end

    Habit.Disable = Habit.Stop

    Core.Register("Habit", Habit)
    Core.Log("HABIT", "✅ Habit system ready — Record / Play / Patrol", "OK")
    return Habit
end
