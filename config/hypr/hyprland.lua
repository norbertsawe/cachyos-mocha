-- CachyOS Mocha: captured workstation configuration.
-- Refer to the wiki for more information.
-- https://wiki.hypr.land/Configuring/Start/

-- Please note not all available settings / options are set here.
-- For a full list, see the wiki

-- You can (and should!!) split this configuration into multiple files
-- Create your files separately and then require them like this:
-- require("myColors")

------------------
---- MONITORS ----
------------------

-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = "1" })

---------------------
---- MY PROGRAMS ----
---------------------

-- Set programs that you use
local terminal = "kitty"
local fileManager = "nemo"
local browser = "firefox"
local chrome = "chromium"
local music = "spotify"
local notion = "xdg-open https://notion.so"
local ai = "xdg-open https://chatgpt.com"

-- rofi
local launcher = "rofi -show drun -show-icons"
local runner = "rofi -show run"
local calculator = "qalculate-gtk"
local emojiSearch = "rofi -modi emoji -show emoji"
local clipboardHistory = "cliphist list | rofi -dmenu | cliphist decode | wl-copy"

-------------------
---- AUTOSTART ----
-------------------

-- See https://wiki.hypr.land/Configuring/Basics/Autostart/

-- Autostart necessary processes (like notifications daemons, status bars, etc.)
-- Or execute your favorite apps at launch like this:
--
hl.on("hyprland.start", function()
	hl.exec_cmd("~/.local/bin/mocha-wallpaper --restore")
	hl.exec_cmd("mako")
	hl.exec_cmd("waybar")
	hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")

	--hl.exec_cmd("udiskie &")
	hl.exec_cmd("hyprctl setcursor Bibata-Modern-Ice 30")
	hl.exec_cmd("playerctld daemon")
	hl.exec_cmd("wl-paste --watch cliphist store")
	--hl.exec_cmd("kitty --class 'desktop-term' -e pfetch")
end)
-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Environment-variables/

hl.env("XCURSOR_SIZE", "30")
hl.env("HYPRCURSOR_SIZE", "30")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
hl.env("QT_STYLE_OVERRIDE", "kvantum")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
-----------------------
----- PERMISSIONS -----
-----------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Permissions/
-- Please note permission changes here require a Hyprland restart and are not applied on-the-fly
-- for security reasons

-- hl.config({
--   ecosystem = {
--     enforce_permissions = true,
--   },
-- })

-- hl.permission("/usr/(bin|local/bin)/grim", "screencopy", "allow")
-- hl.permission("/usr/(lib|libexec|lib64)/xdg-desktop-portal-hyprland", "screencopy", "allow")
-- hl.permission("/usr/(bin|local/bin)/hyprpm", "plugin", "allow")

-----------------------
---- LOOK AND FEEL ----
-----------------------

-- Refer to https://wiki.hypr.land/Configuring/Basics/Variables/
-----------------------
---- LOOK AND FEEL ----
-----------------------

-- Fixed Catppuccin Mocha palette.
local colors = {
    active_border = "rgba(cba6f7ee)",
    inactive_border = "rgba(313244aa)",
}

hl.config({
	general = {
		gaps_in = 3,
		gaps_out = 6,

		border_size = 3,
		col = { active_border = colors.active_border, inactive_border = colors.inactive_border },
		resize_on_border = false,
		allow_tearing = false,
		float_gaps = -1,
		layout = "dwindle",
	},

	decoration = {
		rounding = 6,
		rounding_power = 2,
		active_opacity = 1,
		inactive_opacity = 1,

		shadow = {
			enabled = true,
			range = 4,
			render_power = 3,
			color = "rgba(11111b1a)",
		},

		blur = {
			enabled = false,
			size = 3,
			passes = 1,
			vibrancy = 0.1696,
		},
	},

	animations = {
		enabled = true,
	},
})

-- Default curves and animations, see https://wiki.hypr.land/Configuring/Advanced-and-Cool/Animations/
hl.curve("easeOutQuint", { type = "bezier", points = { { 0.23, 1 }, { 0.32, 1 } } })
hl.curve("easeInOutCubic", { type = "bezier", points = { { 0.65, 0.05 }, { 0.36, 1 } } })
hl.curve("linear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.curve("almostLinear", { type = "bezier", points = { { 0.5, 0.5 }, { 0.75, 1 } } })
hl.curve("quick", { type = "bezier", points = { { 0.15, 0 }, { 0.1, 1 } } })

-- Default springs
hl.curve("easy", { type = "spring", mass = 1, stiffness = 71.2633, dampening = 15.8273644 })

hl.animation({ leaf = "global", enabled = true, speed = 10, bezier = "default" })
hl.animation({ leaf = "border", enabled = true, speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows", enabled = true, speed = 4.79, spring = "easy" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 4.1, spring = "easy", style = "popin 87%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.49, bezier = "linear", style = "popin 87%" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade", enabled = true, speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "layers", enabled = true, speed = 3.81, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 4, bezier = "easeOutQuint", style = "fade" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 1.5, bezier = "linear", style = "fade" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 1.79, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.39, bezier = "almostLinear" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesIn", enabled = true, speed = 1.21, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "zoomFactor", enabled = true, speed = 7, bezier = "quick" })

-- Ref https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/
-- "Smart gaps" / "No gaps when only"
-- uncomment all if you wish to use that.
-- hl.workspace_rule({ workspace = "w[tv1]", gaps_out = 0, gaps_in = 0 })
-- hl.workspace_rule({ workspace = "f[1]",   gaps_out = 0, gaps_in = 0 })
-- hl.window_rule({
--     name  = "no-gaps-wtv1",
--     match = { float = false, workspace = "w[tv1]" },
--     border_size = 0,
--     rounding    = 0,
-- })
-- hl.window_rule({
--     name  = "no-gaps-f1",
--     match = { float = false, workspace = "f[1]" },
--     border_size = 0,
--     rounding    = 0,
-- })
-- Desktop Background Terminal Window Rules
--hl.window_rule({
  --  name = "desktop-terminal-background",
  --  match = { class = "^desktop-term$" },
  --  float = true,
  --  size = { 850, 500 },
  --  center = true,
  --  pin = true,
  --  no_focus = true,
  --  no_initial_focus = true,
--})

-- See https://wiki.hypr.land/Configuring/Layouts/Dwindle-Layout/ for more
hl.config({
	dwindle = {
		preserve_split = true, -- You probably want this
	},
})

-- See https://wiki.hypr.land/Configuring/Layouts/Master-Layout/ for more
hl.config({
	master = {
		new_status = "master",
	},
})

-- See https://wiki.hypr.land/Configuring/Layouts/Scrolling-Layout/ for more
hl.config({
	scrolling = {
		fullscreen_on_one_column = true,
	},
})

----------------
----  MISC  ----
----------------

hl.config({
	misc = {
		force_default_wallpaper = 0, -- Set to 0 or 1 to disable the anime mascot wallpapers
		disable_hyprland_logo = false, -- If true disables the random hyprland logo / anime girl background. :(
	},
})

---------------
---- INPUT ----
---------------

hl.config({
	input = {
		kb_layout = "us",
		kb_variant = "",
		kb_model = "",
		kb_options = "",
		kb_rules = "",

		repeat_rate = 25,
		repeat_delay = 300,

		follow_mouse = 1,

		sensitivity = 0, -- -1.0 - 1.0, 0 means no modification.

		touchpad = {
			natural_scroll = false,
			scroll_factor = 0.2, -- make scrolling with touchpad slower
		},
	},
})

hl.gesture({
	fingers = 3,
	direction = "horizontal",
	action = "workspace",
})

-- Example per-device config
-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Devices/ for more
hl.device({
	name = "epic-mouse-v1",
	sensitivity = -0.5,
})

---------------------
---- KEYBINDINGS ----
---------------------

local mainMod = "SUPER" -- Sets "Windows" key as main modifier
local secondMod = "SUPER + SHIFT" -- Sets "Windows" + "SHIFT" key as second modifier

-- Example binds, see https://wiki.hypr.land/Configuring/Basics/Binds/ for more
hl.bind(mainMod .. " + Q", hl.dsp.window.close())

-- rofi menus
hl.bind(mainMod .. " + Space", hl.dsp.exec_cmd(launcher))
hl.bind(secondMod .. " + Space", hl.dsp.exec_cmd(runner))
hl.bind(secondMod .. " + Return", hl.dsp.exec_cmd(calculator))
hl.bind(secondMod .. " + E", hl.dsp.exec_cmd(emojiSearch))
hl.bind(secondMod .. " + C", hl.dsp.exec_cmd(clipboardHistory))

-- apps
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd(browser))
hl.bind(mainMod .. " + C", hl.dsp.exec_cmd(chrome))
hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + M", hl.dsp.exec_cmd(music))
hl.bind(mainMod .. " + N", hl.dsp.exec_cmd(notion))
hl.bind(mainMod .. " + A", hl.dsp.exec_cmd(ai))
-- Super + Shift + W to launch a wallpaper selector
hl.bind(secondMod .. " + W", hl.dsp.exec_cmd("~/.local/bin/mocha-wallpaper"))

--locking screen using hyprlock

--screenshots using hyprshot
hl.bind(mainMod .. " + P", hl.dsp.exec_cmd("hyprshot --mode window"))
hl.bind(secondMod .. " + P", hl.dsp.exec_cmd("hyprshot --mode region"))

-- hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + O", hl.dsp.layout("togglesplit")) -- dwindle only

-- Move focus with mainMod + arrow keys
-- hl.bind(mainMod .. " + h", hl.dsp.focus({ direction = "left" }))
-- hl.bind(mainMod .. " + l", hl.dsp.focus({ direction = "right" }))

local function workspaceIsScrolling()
	return hl.get_active_workspace().tiled_layout == "scrolling"
end

hl.bind(mainMod .. " + l", function()
	if workspaceIsScrolling() then
		hl.dispatch(hl.dsp.layout("focus r"))
	else
		hl.dispatch(hl.dsp.focus({ direction = "right" }))
	end
end)

hl.bind(mainMod .. " + h", function()
	if workspaceIsScrolling() then
		hl.dispatch(hl.dsp.layout("focus l"))
	else
		hl.dispatch(hl.dsp.focus({ direction = "left" }))
	end
end)

local function workspaceIsMonocle()
	return hl.get_active_workspace().tiled_layout == "monocle"
end

hl.bind(mainMod .. " + j", function()
	if workspaceIsMonocle() then
		hl.dispatch(hl.dsp.layout("cyclenext"))
	else
		hl.dispatch(hl.dsp.focus({ direction = "down" }))
	end
end)

hl.bind(mainMod .. " + k", function()
	if workspaceIsMonocle() then
		hl.dispatch(hl.dsp.layout("cycleprev"))
	else
		hl.dispatch(hl.dsp.focus({ direction = "up" }))
	end
end)

-- Move window  with secondMod + arrow keys
-- hl.bind(secondMod .. " + h", hl.dsp.window.move({ direction = "left" }))
-- hl.bind(secondMod .. " + l", hl.dsp.window.move({ direction = "right" }))
hl.bind(secondMod .. " + k", hl.dsp.window.move({ direction = "up" }))
hl.bind(secondMod .. " + j", hl.dsp.window.move({ direction = "down" }))

hl.bind(secondMod .. " + l", function()
	if workspaceIsScrolling() then
		hl.dispatch(hl.dsp.layout("swapcol r"))
	else
		hl.dispatch(hl.dsp.window.move({ direction = "right" }))
	end
end)

hl.bind(secondMod .. " + h", function()
	if workspaceIsScrolling() then
		hl.dispatch(hl.dsp.layout("swapcol l"))
	else
		hl.dispatch(hl.dsp.window.move({ direction = "left" }))
	end
end)

-- Toggle window maximization
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen({ mode = "maximized" }))
-- toggle floating
hl.bind(secondMod .. " + F", hl.dsp.window.float({ action = "toggle" }))

-- Switch workspaces with mainMod + [0-9]
-- Move active window to a workspace with mainMod + SHIFT + [0-9]
for i = 1, 10 do
	local key = i % 10 -- 10 maps to key 0
	hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = i }))
	hl.bind(secondMod .. " + " .. key, hl.dsp.window.move({ workspace = i }))
end

-- Example special workspace (scratchpad)
hl.bind(mainMod .. " + S", hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))

-- Scroll through existing workspaces with mainMod + scroll
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))

-- Move/resize windows with mainMod + LMB/RMB and dragging
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Submaps

-- power binds
hl.bind(mainMod .. " + Escape", hl.dsp.exec_cmd("~/.local/bin/mocha-power"))

-- Laptop multimedia keys for volume and LCD brightness
hl.bind(
	"XF86AudioRaiseVolume",
	hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioLowerVolume",
	hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioMute",
	hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioMicMute",
	hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),
	{ locked = true, repeating = true }
)
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"), { locked = true, repeating = true })

-- Requires playerctl
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })

--------------------------------
---- WINDOWS AND WORKSPACES ----
--------------------------------

-- Workspace rules
hl.workspace_rule({
	workspace = "2",
	layout = "scrolling",
})

-- See https://wiki.hypr.land/Configuring/Basics/Window-Rules/
-- and https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/

-- Example window rules that are useful

hl.window_rule({
	-- Ignore maximize requests from all apps. You'll probably like this.
	name = "suppress-maximize-events",
	match = { class = ".*" },

	suppress_event = "maximize",
})

hl.window_rule({
	-- Fix some dragging issues with XWayland
	name = "fix-xwayland-drags",
	match = {
		class = "^$",
		title = "^$",
		xwayland = true,
		float = true,
		fullscreen = false,
		pin = false,
	},

	no_focus = true,
})

hl.window_rule({
	name = "kitty",
	match = { class = "com.mitchellh.kitty" },

	-- opacity = "0.9 override 0.8 override",
})

-- Layer rules also return a handle.
-- local overlayLayerRule = hl.layer_rule({
--     name  = "no-anim-overlay",
--     match = { namespace = "^my-overlay$" },
--     no_anim = true,
-- })
-- overlayLayerRule:set_enabled(false)

-- Hyprland-run windowrule
hl.window_rule({
	name = "move-hyprland-run",
	match = { class = "hyprland-run" },

	move = "20 monitor_h-120",
	float = true,
})

-- Machine-specific changes belong in local.lua (preserved by the installer).
local local_config = (os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")) .. "/hypr/local.lua"
local f = io.open(local_config, "r")
if f then f:close(); dofile(local_config) end
