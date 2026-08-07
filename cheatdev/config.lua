--[[
  CHEAT DEV — config.lua
  Semua nilai config terpusat. Edit bebas, reload langsung apply.
--]]

return {

    META = {
        name    = "Cheat Developer",
        version = "2.0.0",
        key     = "XCDEV",
        author  = "pointrungkat-art",
        motto   = "Dev Mode ON — Semua Kode Libas. DAR DER DOR.",
    },

    ESP = {
        enabled      = false,
        showBox      = true,
        showName     = true,
        showHP       = true,
        showDist     = true,
        showTracer   = false,
        showSkeleton = false,
        maxDist      = 500,
        boxColor     = {180, 80,  255},
        tracerColor  = {80,  200, 255},
        nameColor    = {230, 225, 255},
        hpColorHigh  = {80,  255, 130},
        hpColorMid   = {255, 200, 50},
        hpColorLow   = {255, 70,  70},
    },

    AIM = {
        enabled      = false,
        strength     = 0.28,
        fov          = 90,
        teamCheck    = true,
        target       = "Head",   -- "Head" | "HumanoidRootPart"
        showFovRing  = true,
        prediction   = true,
        predMult     = 0.08,
        smoothing    = true,
        smoothFactor = 6,
    },

    SILENT_AIM = {
        enabled = false,
    },

    FLY = {
        enabled     = false,
        speed       = 60,
        sprintMult  = 2.5,
        floatHeight = 0,
    },

    SPEED = {
        enabled    = false,
        walkSpeed  = 80,
        jumpPower  = 80,
    },

    NOCLIP = {
        enabled = false,
    },

    KILL_AURA = {
        enabled    = false,
        radius     = 15,
        damage     = 30,
        rate       = 0.1,
    },

    HITBOX = {
        enabled = false,
        size    = 10,
    },

    GOD_MODE = {
        enabled = false,
    },

    ANTI_KICK = {
        enabled = false,
    },

    ANTI_RAGDOLL = {
        enabled = false,
    },

    INF_STAMINA = {
        enabled = false,
    },

    SPIN_BOT = {
        enabled = false,
        speed   = 25,
    },

    FLY_HACK = {
        enabled = false,
        speed   = 60,
    },

    HOP = {
        enabled  = false,
        interval = 300,
        antiAFK  = true,
    },

    CHEST = {
        enabled = false,
        autoHop = true,
        tags    = {"Chest","Box","Crate","Treasure","Loot"},
    },

    FRUIT = {
        enabled = false,
        tags    = {"Fruit","DevilFruit","Devil_Fruit","BloxFruit"},
    },

    RADAR = {
        enabled   = false,
        size      = 160,
        range     = 200,
        posX      = 0.85,
        posY      = 0.15,
        dotSize   = 5,
    },

    FPS = {
        enabled       = false,
        stripShadows  = true,
        stripParticles= true,
        stripDecals   = true,
        stripBloom    = true,
    },

    CROSSHAIR = {
        enabled  = false,
        style    = "CrossDot",  -- CrossDot | Cross | Dot | Circle | TShape | Dev
        color    = {180, 80, 255},
        size     = 10,
        hitmark  = true,
    },

    -- ── Anti-Ban / Anti-Detect ────────────────────────────────────
    ANTIDETECT = {
        enabled     = false,
        speedDesync = true,     -- WalkSpeed=16 di server, BodyVelocity actual
        remoteHook  = true,     -- block kick/ban RemoteEvent
        antiKick    = true,     -- hook LP:Kick() call
        sanityClamp = true,     -- clamp speed/health ke range aman
        sigRandom   = false,    -- randomise cheat signatures (aggressive)
        tpSteps     = 5,        -- jumlah steps interpolasi teleport
    },

    -- ── Blox Fruits ───────────────────────────────────────────────
    BLOX_FRUITS = {
        enabled      = false,
        fruitESP     = true,
        autoFarm     = false,
        autoCollect  = false,
        seaBeastESP  = false,
        autoQuest    = false,
        farmRadius   = 2000,
        farmDelay    = 0.3,
        fruitMaxDist = 3000,
        targetStat   = "Fruit",  -- Melee | Defense | Sword | Gun | Fruit
    },

    -- ── Murder Mystery 2 ─────────────────────────────────────────
    MM2 = {
        enabled     = false,
        roleESP     = true,
        weaponESP   = true,
        coinESP     = false,
        murderAlert = true,
        alertRadius = 40,
    },

    -- ── Arsenal ───────────────────────────────────────────────────
    ARSENAL = {
        enabled     = false,
        playerESP   = true,
        killUI      = true,
        weaponBoard = false,
        silentAim   = false,
        warnLastKill= true,
        hitboxSize  = 8,
    },

    DEVMODE = {
        logLevel    = "ALL",    -- ALL | INFO | WARN | ERR
        hotkeys = {
            toggleGUI    = "RightShift",
            toggleDevCon = "F2",
            panic        = "F9",   -- matiin semua sekaligus
            reload       = "F5",
        },
    },

}
