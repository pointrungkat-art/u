--[[  CheatDev — forge/builder.lua
      Script Forge engine — load templates, craft, list, raw inject
--]]
return function(Core, templates)
    local Forge = {}
    Forge.Templates = templates or {}

    function Forge.Craft(name)
        local key  = string.upper(name:match("^%s*(.-)%s*$"))
        local code = Forge.Templates[key]
        if not code then
            Core.Log("FORGE", "❌ Template not found: "..key, "ERR")
            Core.Log("FORGE", "Run CList() or /clist to see available templates", "WARN")
            return false
        end
        Core.Log("FORGE", "🔥 Crafting: "..key, "DEV")
        local fn, err = loadstring(code)
        if not fn then
            Core.Log("FORGE", "Compile error: "..tostring(err), "ERR")
            return false
        end
        local ok, runErr = pcall(fn)
        if ok then
            Core.Log("FORGE", "✅ "..key.." injected — DAR DER DOR!", "OK")
            return true
        else
            Core.Log("FORGE", "Runtime error: "..tostring(runErr), "ERR")
            return false
        end
    end

    function Forge.CraftRaw(code)
        Core.Log("FORGE", "🔥 Raw inject...", "DEV")
        local fn, err = loadstring(code)
        if not fn then
            Core.Log("FORGE", "Compile error: "..tostring(err), "ERR")
            return false
        end
        local ok, runErr = pcall(fn)
        if ok then
            Core.Log("FORGE", "✅ Raw injected!", "OK")
        else
            Core.Log("FORGE", "Runtime error: "..tostring(runErr), "ERR")
        end
        return ok
    end

    function Forge.List()
        local keys = {}
        for k in pairs(Forge.Templates) do table.insert(keys, k) end
        table.sort(keys)
        Core.Log("FORGE", "═══ Template Library ("..#keys..") ═══", "DEV")
        for i, k in ipairs(keys) do
            Core.Log("FORGE", string.format("  %02d. /C %-22s", i, k), "INFO")
        end
        Core.Log("FORGE", "═══════════════════════════════", "DEV")
    end

    function Forge.Add(name, code)
        Forge.Templates[string.upper(name)] = code
        Core.Log("FORGE", "➕ Template added: "..string.upper(name), "OK")
    end

    function Forge.Remove(name)
        Forge.Templates[string.upper(name)] = nil
        Core.Log("FORGE", "🗑️ Template removed: "..string.upper(name), "WARN")
    end

    -- Global shorthands
    getgenv().C     = function(name) return Forge.Craft(name) end
    getgenv().CList = function()     return Forge.List() end
    getgenv().CDRaw = function(code) return Forge.CraftRaw(code) end
    getgenv().CAdd  = function(n,c)  return Forge.Add(n,c) end

    Core.Register("Forge", Forge)
    Core.Log("FORGE", "Script Forge ready — "..#(function() local t={} for k in pairs(Forge.Templates) do t[#t+1]=k end return t end()).." templates loaded", "OK")
    return Forge
end
