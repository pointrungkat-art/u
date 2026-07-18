--!strict
--[[
	HitboxExample
	Contoh pemakaian Hitbox untuk sistem serangan senjata sederhana.
	Taruh file ini di ServerScriptService.

	Alur:
		1. Pemain menekan tombol serang (dikirim lewat RemoteEvent).
		2. Server mengaktifkan hitbox mengikuti CFrame senjata selama durasi ayunan.
		3. Setiap Humanoid musuh yang masuk hitbox menerima damage.
--]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Hitbox = require(ReplicatedStorage.Shared.Hitbox)

local DAMAGE = 25
local SWING_DURATION = 0.35

-- Contoh: dipanggil saat pemain menyerang.
local function performAttack(player: Player)
	local character = player.Character
	if not character then
		return
	end

	local tool = character:FindFirstChildOfClass("Tool")
	local weapon = tool and tool:FindFirstChild("Handle") :: BasePart?
	if not weapon then
		return
	end

	local hb = Hitbox.new({
		Shape = "Box",
		Size = Vector3.new(4, 5, 6),
		Ignore = { character }, -- jangan kena diri sendiri
		Debounce = 1, -- target sama gak bisa kena 2x dalam 1 detik
		Visualize = true, -- matikan di produksi
	})

	hb.OnHit:Connect(function(humanoid: Humanoid, _hitPart: BasePart, hitChar: Instance)
		-- Contoh filter: jangan sakiti sesama tim (sesuaikan dengan sistemmu)
		local hitPlayer = game:GetService("Players"):GetPlayerFromCharacter(hitChar)
		if hitPlayer and hitPlayer.Team == player.Team and player.Team ~= nil then
			return
		end

		humanoid:TakeDamage(DAMAGE)
		print(("%s memukul %s (-%d HP)"):format(player.Name, hitChar.Name, DAMAGE))
	end)

	-- Hitbox mengikuti ujung senjata; geser sedikit ke depan handle.
	hb:Start(function()
		return weapon.CFrame * CFrame.new(0, 0, -2)
	end)

	task.delay(SWING_DURATION, function()
		hb:Destroy()
	end)
end

-- Contoh koneksi lewat RemoteEvent (buat RemoteEvent bernama "Attack" di ReplicatedStorage).
local attackRemote = ReplicatedStorage:FindFirstChild("Attack")
if attackRemote and attackRemote:IsA("RemoteEvent") then
	attackRemote.OnServerEvent:Connect(performAttack)
end

return nil
