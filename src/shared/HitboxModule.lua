-- HitboxModule
-- Core hitbox creation, spatial detection, and lifecycle management

local RunService = game:GetService("RunService")

local HitboxModule = {}
HitboxModule.__index = HitboxModule

local DEFAULT_SIZE        = Vector3.new(5, 5, 5)
local DEFAULT_COLOR       = Color3.fromRGB(255, 50, 50)
local DEFAULT_DURATION    = 0.15
local DEFAULT_TRANSPARENCY = 0.45

function HitboxModule.new(config)
	local self = setmetatable({}, HitboxModule)

	self.Size         = config.Size or DEFAULT_SIZE
	self.Offset       = config.Offset or CFrame.new()
	self.Duration     = config.Duration or DEFAULT_DURATION
	self.Color        = config.Color or DEFAULT_COLOR
	self.Visualize    = config.Visualize or false
	self.HitCallback  = config.HitCallback or function() end
	self.Filter       = config.Filter or {}

	self._part        = nil
	self._connection  = nil
	self._alreadyHit  = {}
	self._destroyed   = false

	return self
end

function HitboxModule:_buildPart(rootPart)
	local part = Instance.new("Part")
	part.Name             = "Hitbox"
	part.Size             = self.Size
	part.Anchored         = false
	part.CanCollide       = false
	part.CanTouch         = false
	part.CanQuery         = true
	part.Massless         = true
	part.CastShadow       = false
	part.Material         = Enum.Material.Neon
	part.Color            = self.Color
	part.Transparency     = self.Visualize and DEFAULT_TRANSPARENCY or 1

	-- Weld so it follows the root
	local weld = Instance.new("WeldConstraint")
	weld.Part0  = rootPart
	weld.Part1  = part
	weld.Parent = part

	part.CFrame = rootPart.CFrame * self.Offset
	part.Parent = workspace

	self._part = part
end

function HitboxModule:Start(rootPart)
	if self._destroyed then return end

	self:_buildPart(rootPart)

	local params = OverlapParams.new()
	params.FilterDescendantsInstances = self.Filter
	params.FilterType = Enum.RaycastFilterType.Exclude

	local startTime = tick()

	self._connection = RunService.Heartbeat:Connect(function()
		if self._destroyed then return end

		if tick() - startTime >= self.Duration then
			self:Destroy()
			return
		end

		if not self._part or not self._part.Parent then
			self:Destroy()
			return
		end

		local hits = workspace:GetPartsInPart(self._part, params)
		for _, hit in ipairs(hits) do
			local char = hit:FindFirstAncestorWhichIsA("Model")
			if char and not self._alreadyHit[char] then
				local humanoid = char:FindFirstChildWhichIsA("Humanoid")
				if humanoid and humanoid.Health > 0 then
					self._alreadyHit[char] = true
					self.HitCallback(char, humanoid, hit)
				end
			end
		end
	end)
end

function HitboxModule:Destroy()
	if self._destroyed then return end
	self._destroyed = true

	if self._connection then
		self._connection:Disconnect()
		self._connection = nil
	end

	if self._part and self._part.Parent then
		self._part:Destroy()
		self._part = nil
	end
end

return HitboxModule
