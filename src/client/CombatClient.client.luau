-- CombatClient.client.luau
-- Client-side input handler.
-- Tugasnya cuma satu: pas player tekan F, kirim sinyal attack ke server.
-- Semua logika hit & damage tetap di server (aman dari cheat).

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local remote = ReplicatedStorage:WaitForChild("CombatAttack")

local ATTACK_KEY = Enum.KeyCode.F

UserInputService.InputBegan:Connect(function(input, gameProcessed)
	if gameProcessed then
		return -- jangan trigger kalau lagi ngetik di chat, dll
	end
	if input.KeyCode == ATTACK_KEY then
		remote:FireServer()
	end
end)
