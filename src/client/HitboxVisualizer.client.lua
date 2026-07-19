-- HitboxVisualizer (LocalScript)
-- Renders visible hitbox outlines around all player characters.
-- Press H to toggle visibility on/off.

local Players          = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local RunService       = game:GetService("RunService")

local LocalPlayer = Players.LocalPlayer

local TOGGLE_KEY   = Enum.KeyCode.H

-- Colors
local COLOR_SELF  = Color3.fromRGB(50,  255, 80)   -- green  = yourself
local COLOR_ENEMY = Color3.fromRGB(255, 50,  50)   -- red    = others

-- Hitbox dimensions that match a standard R6/R15 character footprint
local HITBOX_SIZE = Vector3.new(4, 5.5, 2)
local HITBOX_OFFSET = Vector3.new(0, 0.25, 0)     -- slight upward shift from HRP

local SURFACE_TRANSPARENCY = 0.75
local LINE_THICKNESS        = 0.04

local visible    = true
local registry   = {}   -- [character] = { box: Part, sel: SelectionBox }

-- ─── helpers ─────────────────────────────────────────────────────────────────

local function applyVisibility(entry)
	if not entry then return end
	local box = entry.box
	local sel = entry.sel
	if box  and box.Parent  then box.Transparency  = visible and 0.5 or 1 end
	if sel  and sel.Parent  then sel.Visible       = visible end
end

local function removeEntry(character)
	local entry = registry[character]
	if not entry then return end
	if entry.box and entry.box.Parent then entry.box:Destroy() end
	registry[character] = nil
end

local function addHitbox(character, color)
	if registry[character] then return end

	-- Wait for HumanoidRootPart
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root then
		root = character:WaitForChild("HumanoidRootPart", 5)
	end
	if not root then return end

	local humanoid = character:FindFirstChildWhichIsA("Humanoid")
	if not humanoid then return end

	-- Visible part
	local box = Instance.new("Part")
	box.Name            = "VisibleHitbox"
	box.Size            = HITBOX_SIZE
	box.Color           = color
	box.Material        = Enum.Material.Neon
	box.Transparency    = visible and 0.5 or 1
	box.CanCollide      = false
	box.CanTouch        = false
	box.CanQuery        = false
	box.Anchored        = false
	box.CastShadow      = false
	box.Parent          = character

	local weld   = Instance.new("WeldConstraint")
	weld.Part0   = root
	weld.Part1   = box
	weld.Parent  = box
	box.CFrame   = root.CFrame + HITBOX_OFFSET

	-- Wireframe selection box overlay
	local sel = Instance.new("SelectionBox")
	sel.Adornee              = box
	sel.Color3               = color
	sel.LineThickness        = LINE_THICKNESS
	sel.SurfaceColor3        = color
	sel.SurfaceTransparency  = SURFACE_TRANSPARENCY
	sel.Visible              = visible
	sel.Parent               = box

	local entry = { box = box, sel = sel }
	registry[character] = entry

	-- Cleanup on death / removal
	humanoid.Died:Connect(function()
		task.delay(4, function() removeEntry(character) end)
	end)

	character.AncestryChanged:Connect(function(_, parent)
		if not parent then removeEntry(character) end
	end)
end

-- ─── notification UI ─────────────────────────────────────────────────────────

local function showToast(text)
	local gui = LocalPlayer.PlayerGui:FindFirstChild("HitboxGui")
	if not gui then
		gui = Instance.new("ScreenGui")
		gui.Name          = "HitboxGui"
		gui.ResetOnSpawn  = false
		gui.Parent        = LocalPlayer.PlayerGui
	end

	-- Remove old toast
	local old = gui:FindFirstChild("Toast")
	if old then old:Destroy() end

	local frame = Instance.new("Frame")
	frame.Name               = "Toast"
	frame.Size               = UDim2.new(0, 260, 0, 44)
	frame.Position           = UDim2.new(0.5, -130, 0, 16)
	frame.BackgroundColor3   = Color3.fromRGB(15, 15, 15)
	frame.BackgroundTransparency = 0.3
	frame.BorderSizePixel    = 0
	frame.Parent             = gui

	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 10)
	corner.Parent       = frame

	local label = Instance.new("TextLabel")
	label.Size            = UDim2.new(1, 0, 1, 0)
	label.BackgroundTransparency = 1
	label.TextColor3      = Color3.fromRGB(255, 255, 255)
	label.Font            = Enum.Font.GothamBold
	label.TextSize        = 15
	label.Text            = text
	label.Parent          = frame

	task.delay(2.5, function()
		if frame and frame.Parent then frame:Destroy() end
	end)
end

-- ─── toggle ──────────────────────────────────────────────────────────────────

local function toggle()
	visible = not visible
	for character in pairs(registry) do
		applyVisibility(registry[character])
	end
	showToast(visible and "Hitbox  ON  [H]" or "Hitbox  OFF  [H]")
end

UserInputService.InputBegan:Connect(function(input, processed)
	if processed then return end
	if input.KeyCode == TOGGLE_KEY then toggle() end
end)

-- ─── init all current & future players ───────────────────────────────────────

local function onPlayer(player)
	local color = player == LocalPlayer and COLOR_SELF or COLOR_ENEMY

	local function onCharacter(character)
		task.delay(0.3, function() addHitbox(character, color) end)
	end

	if player.Character then onCharacter(player.Character) end
	player.CharacterAdded:Connect(onCharacter)
end

for _, player in ipairs(Players:GetPlayers()) do
	onPlayer(player)
end
Players.PlayerAdded:Connect(onPlayer)
Players.PlayerRemoving:Connect(function(player)
	if player.Character then removeEntry(player.Character) end
end)

-- ─── periodic cleanup of stale entries ───────────────────────────────────────
RunService.Heartbeat:Connect(function()
	for character, entry in pairs(registry) do
		if not entry.box or not entry.box.Parent then
			registry[character] = nil
		end
	end
end)
