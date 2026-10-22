# CachyOS Mocha

A personal Hyprland desktop for CachyOS, built around Catppuccin Mocha: a compact translucent Waybar, mauve Rofi launcher, green GTK and Kvantum accents, Kitty, and Bibata cursors.

![Included Catppuccin wallpaper](share/cachyos-mocha/wallpapers/catppuccin.png)

Captured from my CachyOS workstation with **Hyprland 0.56.2**. Uses the Lua configuration format; **Hyprland 0.55+ is required** ([configuration reference](https://wiki.hypr.land/Configuring/Start/)). This is a desktop configuration installer for an existing CachyOS installation, not an OS installer.

## Install

Run as your normal user in an existing CachyOS installation with Python 3, Git, sudo access, and a working network:

```bash
sudo pacman -Syu --needed git python
git clone https://github.com/norbertsawe/cachyos-mocha.git ~/Projects/cachyos-mocha
cd ~/Projects/cachyos-mocha
./install.sh
```

The installer updates the system and installs the packages listed in [`packages.txt`](packages.txt), using pacman's normal confirmation prompt. It stages the files, backs up existing destinations, then **replaces** the relevant configuration directories with independent copies. Existing `hypr/local.lua` overrides are preserved. It does not change your login manager or reload your current session. Log out and choose **Hyprland** at login after installation.

```bash
./install.sh --dry-run      # Preview destinations without changing anything
./install.sh --config-only  # Copy configs/assets; manage dependencies yourself
./install.sh --extras       # Also install the captured editor/utility configs
```

`--config-only` skips package and version checks. `--dry-run` also skips dependency installation. Clone outside the directories being replaced; `~/Projects/cachyos-mocha` is suitable. Re-running installation creates a new backup each time.

On a fresh installation, enable networking and Bluetooth if those services are not already enabled:

```bash
sudo systemctl enable --now NetworkManager.service
sudo systemctl enable --now bluetooth.service
```

Services are left under your control because an existing installation may use another network manager. Audio uses PipeWire/WirePlumber. Spotify is an optional application for `Super+M`; install it separately if wanted. Neovim's optional LazyVim setup downloads plugins on first launch.

## Included

| Component | Configuration |
| --- | --- |
| Hyprland | Lua config, dwindle layout, scrolling workspace 2, gestures, animations, portable monitor defaults |
| Waybar | Original Mocha CSS, workspaces, window title, audio/mic, brightness, CPU/RAM, Wi-Fi/Bluetooth, battery, clock, updates, lock, session menu |
| Rofi | Local Mocha theme, application/command launcher, clipboard and wallpaper menus |
| Kitty | Catppuccin Mocha, JetBrainsMono Nerd Font, mauve cursor trail |
| GTK 3/4 and GTK 2 settings | Bundled Catppuccin Mocha green theme, Papirus Dark icons |
| Qt 5/6 | Qt settings and bundled Catppuccin Mocha green Kvantum theme |
| Desktop | Bibata Modern Ice cursors, bundled current wallpaper, Mako notifications, working Hyprlock screen |
| Optional `--extras` | Captured btop, Cava, Micro, Neovim, Ghostty, Fuzzel, htop, Alacritty configs |

Optional configs preserve the workstation's app preferences; some still use other palettes. Browser profiles, shell history, credentials, clipboard contents, app sessions, and unrelated application settings are excluded.

Compared with the original snapshot, username-specific paths and display/backlight restrictions are removed, missing helper scripts are supplied, duplicate shortcuts are resolved, and stale Matugen/Noctalia GTK overrides are replaced with the selected GTK theme. Waybar's app button now uses Rofi. The power button opens a menu with confirmation for logout, reboot, and shutdown.

## Shortcuts

| Keys | Action |
| --- | --- |
| `Super+Return` | Kitty |
| `Super+Space` / `Super+Shift+Space` | Applications / run command |
| `Super+E` / `Super+B` / `Super+C` | Nemo / Firefox / Chromium |
| `Super+Shift+Return` | Calculator |
| `Super+Shift+E` / `Super+Shift+C` | Emoji / clipboard history |
| `Super+Shift+W` | Wallpaper picker |
| `Super+P` / `Super+Shift+P` | Window / region screenshot |
| `Super+Escape` | Session menu (lock, suspend, logout, reboot, shutdown) |
| `Super+Q` | Close window |
| `Super+F` / `Super+Shift+F` | Maximize / toggle floating |
| `Super+H/J/K/L` | Focus left/down/up/right |
| `Super+Shift+H/J/K/L` | Move window |
| `Super+1…0` / `Super+Shift+1…0` | Workspace / move window to workspace |

Clipboard history is stored locally by cliphist after login; it is never part of this repository.

## Customize

Edit files under `~/.config` after installation. Repository updates take effect only after running the installer again. Put monitor and other machine-specific overrides in `~/.config/hypr/local.lua`, which is preserved on reinstall:

```lua
hl.monitor({ output = "DP-1", mode = "1920x1080@60", position = "0x0", scale = "1" })
```

Default display settings use each monitor's preferred mode. Waybar applies to all displays and detects backlight hardware. Modules needing hardware (battery, brightness, Bluetooth) may be unavailable on desktops without it; remove those modules from `waybar/config.jsonc` if desired.

Add wallpapers to `~/.local/share/cachyos-mocha/wallpapers` or `~/Pictures`, then press `Super+Shift+W`. The selected wallpaper is remembered under `~/.local/state/cachyos-mocha`. You can also run:

```bash
~/.local/bin/mocha-wallpaper /absolute/path/to/image.png
```

The installer respects `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, and `XDG_STATE_HOME`, including GTK4's theme import. Scripts live in `~/.local/bin` and keybindings reference them directly. GTK4 applications that enforce their own styling may render differently. The bundled Catppuccin GTK port is archived upstream.

## Restore

Each successful install prints its backup location and restore command. Backups contain a manifest and the original files, including original symlinks:

```bash
./install.sh --restore ~/.local/state/cachyos-mocha/backups/<timestamp>
```

Restore saves the displaced installed files inside that backup's `displaced-*` directory, then puts the original configs back. Destinations that did not previously exist are removed. Restore backups in reverse installation order if undoing several installations. Each backup can be restored once. Packages remain installed; restore only affects captured files. Log out and back in afterward.

## Validation

```bash
python3 -m unittest discover -s tests -v
bash -n install.sh bin/*
Hyprland --verify-config -c "$PWD/config/hypr/hyprland.lua"
```

Installer tests use temporary homes and custom XDG directories to check dry runs, repeated installation, symlink preservation, local overrides, restore, optional configs, and rollback after an injected copy failure. GitHub Actions runs installer tests and syntax checks. Hyprland validation was run locally on 0.56.2; a fresh OS installation and every optional application have not been tested end to end.

## Credits

Personal configuration by [Norbert John Sawe](https://github.com/norbertsawe). This is an independent personal setup, unaffiliated with CachyOS, Hyprland, or Catppuccin. Third-party themes retain their own licenses; see [THIRD_PARTY.md](THIRD_PARTY.md) and [`licenses/`](licenses/).
