--!strict
-- Hitbox.luau
-- Sistem hitbox untuk combat system.
-- Pakai spatial query (workspace:GetPartBoundsInBox) biar akurat & konsisten,
-- BUKAN .Touched yang sering meleset/ketinggalan hit pas gerakan cepat.
--
-- Mode Debug bikin hitbox-nya KELIHATAN (part transparan warna merah)
-- jadi enak buat testing / tuning ukuran & posisi.
--
-- Contoh pakai:
--   local hb = Hitbox.new({
--       Size = Vector3.new(5, 5, 6),
--       AttachTo = root,                 -- ngikutin part ini tiap frame
--       Offset = CFrame.new(0, 0, -4),   -- geser ke depan karakter
--       Debug = true,                    -- tampilin visual
--       FilterList = { character },      -- ignore diri sendiri
--   })
--   hb:OnHit(function(humanoid, model)
--       humanoid:TakeDamage(10)
--   end)
--   hb:Start()
--   task.delay(0.25, function() hb:Destroy() end)

local RunService = game:GetService("RunService")

local Hitbox = {}
Hitbox.__index = Hitbox

export type Config = {
	Size: Vector3?,             -- ukuran kotak hitbox
	CFrame: CFrame?,            -- posisi statis (dipakai kalau ga ada AttachTo)
	AttachTo: BasePart?,        -- kalau diisi, hitbox ngikutin part ini
	Offset: CFrame?,            -- offset relatif ke AttachTo
	Debug: boolean?,            -- true = hitbox kelihatan
	FilterList: { Instance }?,  -- instance yang di-ignore (biasanya penyerang)
}

export type HitCallback = (humanoid: Humanoid, model: Model, part: BasePart) -> ()

function Hitbox.new(config: Config)
	local self = setmetatable({}, Hitbox)

	self.Size = config.Size or Vector3.new(5, 5, 5)
	self.CFrame = config.CFrame or CFrame.new()
	self.AttachTo = config.AttachTo
	self.Offset = config.Offset or CFrame.new()
	self.Debug = config.Debug or false

	self._connection = nil
	self._hitList = {} :: { [Humanoid]: boolean } -- humanoid yg udah kena, biar ga dobel
	self._callbacks = {} :: { HitCallback }
	self._visual = nil :: BasePart?

	-- Filter: exclude penyerang biar ga mukul diri sendiri
	self._params = OverlapParams.new()
	self._params.FilterType = Enum.RaycastFilterType.Exclude
	self._params.FilterDescendantsInstances = config.FilterList or {}

	return self
end

-- Daftarin callback yang jalan tiap kena target baru
function Hitbox:OnHit(callback: HitCallback)
	table.insert(self._callbacks, callback)
	return self
end

-- Hitung posisi hitbox sekarang (ngikutin AttachTo kalau ada)
function Hitbox:_getCFrame(): CFrame
	if self.AttachTo then
		return self.AttachTo.CFrame * self.Offset
	end
	return self.CFrame
end

-- Bikin part visual buat debug (transparan, ga nabrak apa-apa)
function Hitbox:_createVisual()
	local part = Instance.new("Part")
	part.Name = "HitboxVisual"
	part.Size = self.Size
	part.CFrame = self:_getCFrame()
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false -- penting: jangan sampe visual-nya ke-scan hitbox lain
	part.CanTouch = false
	part.Material = Enum.Material.ForceField
	part.Color = Color3.fromRGB(255, 60, 60)
	part.Transparency = 0.5
	part.Parent = workspace
	self._visual = part
end

-- Satu kali scan: cari humanoid di dalam kotak hitbox
function Hitbox:_scan()
	local cframe = self:_getCFrame()

	if self._visual then
		self._visual.CFrame = cframe
	end

	local parts = workspace:GetPartBoundsInBox(cframe, self.Size, self._params)

	for _, part in parts do
		local model = part:FindFirstAncestorOfClass("Model")
		if not model then
			continue
		end
		local humanoid = model:FindFirstChildOfClass("Humanoid")
		if humanoid and humanoid.Health > 0 and not self._hitList[humanoid] then
			self._hitList[humanoid] = true -- tandain biar ga dobel hit
			for _, cb in self._callbacks do
				task.spawn(cb, humanoid, model, part)
			end
		end
	end
end

-- Mulai deteksi (scan tiap frame)
function Hitbox:Start()
	if self._connection then
		return self
	end
	table.clear(self._hitList)

	if self.Debug then
		self:_createVisual()
	end

	self._connection = RunService.Heartbeat:Connect(function()
		self:_scan()
	end)
	return self
end

-- Berhenti deteksi + hapus visual
function Hitbox:Stop()
	if self._connection then
		self._connection:Disconnect()
		self._connection = nil
	end
	if self._visual then
		self._visual:Destroy()
		self._visual = nil
	end
	return self
end

-- Bersihin total (panggil ini kalau hitbox udah ga dipake)
function Hitbox:Destroy()
	self:Stop()
	table.clear(self._callbacks)
	table.clear(self._hitList)
end

return Hitbox
