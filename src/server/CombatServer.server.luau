-- CombatServer.server.luau
-- Server-side combat handler.
-- Nerima sinyal attack dari client, terus spawn hitbox di depan karakter.
-- Hitbox dijalanin di SERVER biar anti-cheat (client cuma minta, server yang mutusin).

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Hitbox = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Hitbox"))

-- Bikin RemoteEvent buat komunikasi client -> server
local remote = Instance.new("RemoteEvent")
remote.Name = "CombatAttack"
remote.Parent = ReplicatedStorage

local COOLDOWN = 0.6 -- jeda antar serangan (detik)
local DAMAGE = 10
local ACTIVE_TIME = 0.25 -- berapa lama hitbox aktif tiap swing
local lastAttack: { [Player]: number } = {}

remote.OnServerEvent:Connect(function(player)
	local char = player.Character
	if not char then
		return
	end
	local root = char:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not root then
		return
	end

	-- Cek cooldown
	local now = os.clock()
	if lastAttack[player] and now - lastAttack[player] < COOLDOWN then
		return
	end
	lastAttack[player] = now

	-- Bikin hitbox di depan karakter (visible buat testing)
	local hb = Hitbox.new({
		Size = Vector3.new(5, 5, 6),
		AttachTo = root,
		Offset = CFrame.new(0, 0, -4), -- 4 stud di depan
		Debug = true, -- << set false kalau ga mau kelihatan lagi
		FilterList = { char }, -- ignore diri sendiri
	})

	hb:OnHit(function(humanoid, model)
		print(("[Combat] %s mukul %s"):format(player.Name, model.Name))
		humanoid:TakeDamage(DAMAGE)
	end)

	hb:Start()
	task.delay(ACTIVE_TIME, function()
		hb:Destroy()
	end)
end)

-- Bersihin data pas player keluar
game:GetService("Players").PlayerRemoving:Connect(function(player)
	lastAttack[player] = nil
end)

print("[Combat] Server siap. Player tekan F buat nyerang.")
