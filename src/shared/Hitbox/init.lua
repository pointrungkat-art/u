--!strict
--[[
	Hitbox
	Sistem hitbox berbasis spatial query (GetPartBoundsInBox / GetPartBoundsInRadius).
	Lebih akurat & anti-bocor dibanding Touched event.

	Cara pakai singkat:

		local Hitbox = require(ReplicatedStorage.Shared.Hitbox)

		local hb = Hitbox.new({
			Shape = "Box",
			Size = Vector3.new(6, 6, 6),
			Ignore = { attackerCharacter },
			Debounce = 0.5,
		})

		hb.OnHit:Connect(function(humanoid, hitPart, character)
			humanoid:TakeDamage(25)
		end)

		-- Ikutkan hitbox ke CFrame senjata setiap frame selama aktif:
		hb:Start(function()
			return weaponPart.CFrame
		end)

		task.wait(0.3)
		hb:Stop()

	Author: (project pointrungkat-art/u)
--]]

local RunService = game:GetService("RunService")

--// Signal ringan (biar gak butuh dependency eksternal) //--
type Connection = {
	Disconnect: (self: Connection) -> (),
}

local Signal = {}
Signal.__index = Signal

function Signal.new()
	return setmetatable({ _handlers = {} }, Signal)
end

function Signal:Connect(fn: (...any) -> ()): Connection
	local handlers = self._handlers
	handlers[fn] = true
	return {
		Disconnect = function()
			handlers[fn] = nil
		end,
	}
end

function Signal:Fire(...: any)
	for fn in pairs(self._handlers) do
		task.spawn(fn, ...)
	end
end

function Signal:Destroy()
	table.clear(self._handlers)
end

--// Konfigurasi //--
export type Shape = "Box" | "Sphere"

export type HitboxConfig = {
	Shape: Shape?, -- "Box" (default) atau "Sphere"
	Size: Vector3?, -- ukuran box (dipakai kalau Shape = "Box")
	Radius: number?, -- radius sphere (dipakai kalau Shape = "Sphere")
	Ignore: { Instance }?, -- Instance yang diabaikan (mis. karakter penyerang)
	Debounce: number?, -- jeda (detik) sebelum humanoid yang sama bisa kena lagi. 0 = tiap frame
	MaxHits: number?, -- batas jumlah target yang bisa kena per aktivasi (nil = tak terbatas)
	Visualize: boolean?, -- true untuk menampilkan hitbox (debug)
}

--// Kelas Hitbox //--
local Hitbox = {}
Hitbox.__index = Hitbox

export type Hitbox = typeof(setmetatable(
	{} :: {
		Shape: Shape,
		Size: Vector3,
		Radius: number,
		Debounce: number,
		MaxHits: number?,
		Visualize: boolean,
		OnHit: typeof(Signal.new()),
		_params: OverlapParams,
		_active: boolean,
		_hitCount: number,
		_lastHit: { [Humanoid]: number },
		_connection: RBXScriptConnection?,
		_adornment: Instance?,
	},
	Hitbox
))

function Hitbox.new(config: HitboxConfig): Hitbox
	config = config or {}

	local params = OverlapParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = config.Ignore or {}

	local self = setmetatable({
		Shape = config.Shape or "Box",
		Size = config.Size or Vector3.new(5, 5, 5),
		Radius = config.Radius or 5,
		Debounce = config.Debounce or 0,
		MaxHits = config.MaxHits,
		Visualize = config.Visualize or false,

		OnHit = Signal.new(),

		_params = params,
		_active = false,
		_hitCount = 0,
		_lastHit = {},
		_connection = nil,
		_adornment = nil,
	}, Hitbox)

	return self :: any
end

-- Tambah instance ke daftar abaikan (mis. karakter penyerang, tembok tertentu).
function Hitbox:AddToIgnore(instance: Instance)
	local list = self._params.FilterDescendantsInstances
	table.insert(list, instance)
	self._params.FilterDescendantsInstances = list
end

-- Ganti seluruh daftar abaikan sekaligus.
function Hitbox:SetIgnoreList(list: { Instance })
	self._params.FilterDescendantsInstances = list
end

-- Satu kali pengecekan pada CFrame tertentu. Berguna untuk hit instan (mis. tembakan).
function Hitbox:Query(cframe: CFrame): { Humanoid }
	local parts: { BasePart }
	if self.Shape == "Sphere" then
		parts = workspace:GetPartBoundsInRadius(cframe.Position, self.Radius, self._params)
	else
		parts = workspace:GetPartBoundsInBox(cframe, self.Size, self._params)
	end

	local hitThisPass: { [Humanoid]: boolean } = {}
	local hitList: { Humanoid } = {}

	for _, part in ipairs(parts) do
		local character = part.Parent
		if not character then
			continue
		end

		local humanoid = character:FindFirstChildOfClass("Humanoid")
		if not humanoid or humanoid.Health <= 0 then
			continue
		end

		-- hindari kena berkali-kali dari beberapa part di karakter yang sama
		if hitThisPass[humanoid] then
			continue
		end

		-- debounce per-humanoid
		local now = os.clock()
		local last = self._lastHit[humanoid]
		if last and (now - last) < self.Debounce then
			continue
		end

		-- batas maksimum target
		if self.MaxHits and self._hitCount >= self.MaxHits then
			break
		end

		hitThisPass[humanoid] = true
		self._lastHit[humanoid] = now
		self._hitCount += 1
		table.insert(hitList, humanoid)

		self.OnHit:Fire(humanoid, part, character)
	end

	return hitList
end

-- Aktifkan hitbox yang mengikuti CFrame. `getCFrame` dipanggil tiap frame.
function Hitbox:Start(getCFrame: () -> CFrame)
	if self._active then
		return
	end
	self._active = true
	self._hitCount = 0

	self._connection = RunService.Heartbeat:Connect(function()
		local cframe = getCFrame()
		if not cframe then
			return
		end

		if self.Visualize then
			self:_updateVisual(cframe)
		end

		self:Query(cframe)
	end)
end

-- Matikan hitbox. Reset state debounce & hit count untuk aktivasi berikutnya.
function Hitbox:Stop()
	if not self._active then
		return
	end
	self._active = false
	self._hitCount = 0
	table.clear(self._lastHit)

	if self._connection then
		self._connection:Disconnect()
		self._connection = nil
	end

	if self._adornment then
		self._adornment:Destroy()
		self._adornment = nil
	end
end

-- Visualisasi hitbox untuk debugging.
function Hitbox:_updateVisual(cframe: CFrame)
	local adornment = self._adornment :: any
	if not adornment then
		if self.Shape == "Sphere" then
			adornment = Instance.new("SphereHandleAdornment")
			adornment.Radius = self.Radius
		else
			adornment = Instance.new("BoxHandleAdornment")
			adornment.Size = self.Size
		end
		adornment.Color3 = Color3.fromRGB(255, 60, 60)
		adornment.Transparency = 0.6
		adornment.AlwaysOnTop = true
		adornment.ZIndex = 1
		adornment.Adornee = workspace.Terrain
		adornment.Parent = workspace.Terrain
		self._adornment = adornment
	end
	adornment.CFrame = cframe
end

-- Bersihkan total (panggil saat objek tidak dipakai lagi).
function Hitbox:Destroy()
	self:Stop()
	self.OnHit:Destroy()
end

return Hitbox
