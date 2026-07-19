-- HitboxService (Script)
-- Server-side hitbox registration, spatial detection, and damage application.
-- Clients fire RegisterHitbox to request a server-authoritative hitbox sweep.

local Players          = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local HitboxModule = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("HitboxModule"))

-- ─── remotes setup ───────────────────────────────────────────────────────────

local Remotes = ReplicatedStorage:FindFirstChild("Remotes")
if not Remotes then
	Remotes        = Instance.new("Folder")
	Remotes.Name   = "Remotes"
	Remotes.Parent = ReplicatedStorage
end

local function getOrCreate(class, name, parent)
	return parent:FindFirstChild(name) or (function()
		local inst = Instance.new(class)
		inst.Name   = name
		inst.Parent = parent
		return inst
	end)()
end

local RegisterHitbox = getOrCreate("RemoteEvent", "RegisterHitbox", Remotes)
local HitConfirm     = getOrCreate("RemoteEvent", "HitConfirm",     Remotes)

-- ─── config ──────────────────────────────────────────────────────────────────

local DAMAGE = {
	Light    = 12,
	Heavy    = 28,
	Finisher = 55,
}

local MAX_HITBOX_SIZE = Vector3.new(10, 10, 10)
local MIN_HITBOX_SIZE = Vector3.new(1,  1,  1)
local MAX_DURATION    = 0.5
local ATTACK_COOLDOWN = 0.25

local cooldowns = {}

-- ─── helpers ─────────────────────────────────────────────────────────────────

local function getPlayerFromCharacter(character)
	for _, p in ipairs(Players:GetPlayers()) do
		if p.Character == character then return p end
	end
end

local function clampVector(v, minV, maxV)
	return Vector3.new(
		math.clamp(v.X, minV.X, maxV.X),
		math.clamp(v.Y, minV.Y, maxV.Y),
		math.clamp(v.Z, minV.Z, maxV.Z)
	)
end

-- ─── main handler ────────────────────────────────────────────────────────────

--[[
	RegisterHitbox args from client:
	  attackType  (string)   : "Light" | "Heavy" | "Finisher"
	  size        (Vector3)  : desired hitbox size (clamped server-side)
	  duration    (number)   : active window in seconds (clamped)
]]
RegisterHitbox.OnServerEvent:Connect(function(player, attackType, size, duration)
	-- Cooldown guard
	local now = tick()
	if cooldowns[player] and now - cooldowns[player] < ATTACK_COOLDOWN then return end
	cooldowns[player] = now

	local character = player.Character
	if not character then return end

	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then return end

	-- Sanitize inputs
	attackType = (DAMAGE[attackType] and attackType) or "Light"

	local safeSize = clampVector(
		typeof(size) == "Vector3" and size or Vector3.new(5, 5, 5),
		MIN_HITBOX_SIZE,
		MAX_HITBOX_SIZE
	)

	local safeDuration = math.clamp(
		typeof(duration) == "number" and duration or 0.15,
		0.05,
		MAX_DURATION
	)

	-- Place hitbox in front of character
	local hitboxOffset = CFrame.new(0, 0, -(safeSize.Z / 2 + 2))

	local hitbox = HitboxModule.new({
		Size        = safeSize,
		Offset      = hitboxOffset,
		Duration    = safeDuration,
		Visualize   = false,        -- server part is invisible; client handles visuals
		Filter      = { character },
		HitCallback = function(hitCharacter, humanoid, _hitPart)
			if hitCharacter == character then return end

			local damage = DAMAGE[attackType]
			humanoid:TakeDamage(damage)

			-- Notify all clients so they can show hit-effects
			local hitPlayer = getPlayerFromCharacter(hitCharacter)
			HitConfirm:FireAllClients(player, hitPlayer or hitCharacter, attackType, damage)
		end,
	})

	hitbox:Start(root)
end)

-- ─── cleanup ─────────────────────────────────────────────────────────────────

Players.PlayerRemoving:Connect(function(player)
	cooldowns[player] = nil
end)

print("[HitboxService] Ready")
