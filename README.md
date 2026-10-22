# CachyOS Mocha

**My personal desktop environment, built on Hyprland and Catppuccin Mocha.**

A complete, installable desktop setup for CachyOS by [norbertsawe](https://github.com/norbertsawe): translucent Waybar, mauve Rofi menus, green GTK/Kvantum accents, Kitty, Zsh/Powerlevel10k, matching utilities, and a dedicated **CachyOS Mocha** login session.

![Included Catppuccin wallpaper](share/cachyos-mocha/wallpapers/catppuccin.png)

Captured from my CachyOS workstation running **Hyprland 0.56.2**. Requires **Hyprland 0.55+**, which uses [Lua configuration](https://wiki.hypr.land/Configuring/Start/). This installs the desktop on an existing CachyOS system; it does not install the operating system or graphics drivers.

## Install everything

Run as your normal user, with sudo access and an internet connection:

```bash
sudo pacman -Syu --needed git python
git clone https://github.com/norbertsawe/cachyos-mocha.git ~/Projects/cachyos-mocha
cd ~/Projects/cachyos-mocha
./install.sh --yes
```

The script installs all packages in [`packages.txt`](packages.txt), backs up existing files, replaces the default configs, installs the theme assets, registers the login session, and configures services. `--yes` accepts pacman's package prompts; sudo may still request your password. Without `--yes`, pacman asks for confirmation.

**Choose “CachyOS Mocha” in Ly on tty2** (`Ctrl+Alt+F2`). The full installer starts Ly immediately with `sudo systemctl enable --now ly@tty2`. From a TTY, you can also launch `/usr/local/bin/cachyos-mocha-session` directly. The installer does not reload Hyprland or stop an existing graphical login manager, but starting Ly may switch the active virtual terminal.

The full setup includes:

- Hyprland, Waybar, Rofi, notifications, screen locking, screenshots, clipboard history, wallpaper selection, and a settings launcher.
- Kitty, Zsh, your captured Powerlevel10k prompt, Firefox, Chromium, Nemo, a calculator, archive tools, file thumbnails, and removable-drive support.
- Matching Mocha themes for GTK 3/4, Qt/Kvantum, Kitty, Ghostty, Alacritty, Fuzzel, Micro, Neovim, and btop; Bibata cursors and Papirus icons.
- PipeWire/WirePlumber audio, NetworkManager, Bluetooth tools, screen-sharing portals, and Ly on tty2.
- Your captured Cava, htop, editor, and alternate-terminal preferences.

The music shortcut opens Spotify Web, so the full install needs no AUR helper. Neovim downloads its plugins on first launch. Your login shell is unchanged; Kitty launches the configured Zsh directly.

## Configurations only

Already have the tools installed? Copy just the configurations and appearance assets:

```bash
git clone https://github.com/norbertsawe/cachyos-mocha.git ~/Projects/cachyos-mocha
cd ~/Projects/cachyos-mocha
./install.sh --config-only
```

`--configs-only` is an equivalent alias. This mode **never installs additional packages**, runs sudo, changes services, or registers a system login session. It backs up and replaces the selected configs (including shell settings), copies the themes/wallpaper/helpers, and refreshes the font cache if available. It needs Python 3 already installed. Tools you do not have stay uninstalled; install them yourself only if you want to use their configs.

Use `--config-only --minimal` to omit editor and alternate-terminal configs, or `--config-only --dry-run` to preview all destinations first. The usual backup and restore commands still apply.

## Installation controls

```bash
./install.sh --dry-run       # Preview files and service setup; change nothing
./install.sh --config-only   # Install all configs/assets; skip packages, services and login registration
./install.sh --minimal       # Omit editor/alternate-terminal configs; package bundle remains complete
./install.sh --no-services   # Install files/packages/session, leaving service states alone
./install.sh --no-session    # Skip the branded login entry and Ly activation
```

Clone outside the directories being replaced. Installation uses independent copies, so the repository can be moved later. Every reinstall makes a new backup. Existing `hypr/local.lua` overrides are preserved; other managed directories are replaced as a unit.

NetworkManager and Bluetooth are enabled automatically, together with user audio services. If another network service is active, it is kept and NetworkManager is not enabled. The previous graphical login manager is disabled for future boots without stopping its running session. The installer disables/stops `getty@tty2.service` to free tty2, then runs `sudo systemctl enable --now ly@tty2`, following [Ly’s systemd setup](https://github.com/fairyglade/ly#systemd). Explicitly masked network/Bluetooth/audio services stay masked. Choose `--no-services` to manage those yourself.

## Daily use

Right-click **Apps** on Waybar, launch **CachyOS Mocha Settings**, or press **Super+,** for wallpaper, audio, network, Bluetooth, configuration, and health tools. Left-click Apps to launch applications. The power button opens a menu with confirmation before logout, reboot, or shutdown.

| Keys | Action |
| --- | --- |
| `Super+Return` | Kitty / Zsh |
| `Super+Space` / `Super+Shift+Space` | Applications / run command |
| `Super+,` | Desktop settings |
| `Super+E` / `Super+B` / `Super+C` | Nemo / Firefox / Chromium |
| `Super+Shift+Return` | Calculator |
| `Super+M` | Spotify Web |
| `Super+Shift+E` / `Super+Shift+C` | Emoji / clipboard history |
| `Super+Shift+W` | Wallpaper picker |
| `Super+P` / `Super+Shift+P` | Window / region screenshot |
| `Super+Escape` | Session menu and lock |
| `Super+Q` | Close window |
| `Super+F` / `Super+Shift+F` | Maximize / toggle floating |
| `Super+H/J/K/L` | Focus left/down/up/right |
| `Super+Shift+H/J/K/L` | Move window |
| `Super+1…0` / `Super+Shift+1…0` | Workspace / move window to workspace |

Workspace 2 uses the scrolling layout; the others use dwindle. Audio, microphone, brightness, and media keys are configured. Clipboard history is stored locally by cliphist after login and is never included in this repository.

## Customize

Edit the installed files under `~/.config`. Put machine-specific settings in `~/.config/hypr/local.lua`, which survives reinstall:

```lua
hl.monitor({ output = "DP-1", mode = "1920x1080@60", position = "0x0", scale = "1" })
```

Default monitor settings use preferred modes; Waybar targets all monitors and detects backlight hardware. Modules requiring absent hardware may be unavailable: remove battery, brightness, or Bluetooth modules from `waybar/config.jsonc` if needed.

Add wallpaper images to `~/.local/share/cachyos-mocha/wallpapers` or `~/Pictures`, then use the picker. The last selection is restored on login. You can also run:

```bash
~/.local/bin/mocha-wallpaper /absolute/path/to/image.png
~/.local/bin/mocha-doctor
```

The installer respects `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, and `XDG_STATE_HOME`, including the GTK4 import. Helpers live in `~/.local/bin`; the system login wrapper lives in `/usr/local/bin`. GTK4 applications that enforce their own styling may differ. The bundled GTK port is archived upstream.

## Back up and restore

Every successful install prints its backup path and restore command:

```bash
./install.sh --restore ~/.local/state/cachyos-mocha/backups/<timestamp>
```

Backups include original configs, shell preferences, replaced theme assets, original symlinks, any replaced session files, and the previous states of configured services. Restore saves displaced files under `displaced-*`, restores the original files, removes destinations that were previously absent, and undoes service activation introduced by that install. System files and services require sudo during restore. Packages remain installed.

Restore multiple installs in reverse order. Each backup can be restored once. Log out and back in after restoration. Failed file installation rolls back already-replaced files. Browser profiles, passwords, shell history, clipboard contents, and unrelated personal app settings are excluded.

## Repository layout

```text
config/       Desktop, terminal, shell, and utility settings
bin/          Wallpaper, settings, session-menu, and health helpers
session/      CachyOS Mocha login entry and session environment
share/        Themes, cursors, current wallpaper, application launcher
scripts/      Installer, backups, service setup, and restore
packages.txt  Complete CachyOS package bundle
```

## Validation

```bash
python3 -m unittest discover -s tests -v
bash -n install.sh bin/* session/cachyos-mocha-session
Hyprland --verify-config -c "$PWD/config/hypr/hyprland.lua"
```

Tests use temporary homes/custom XDG paths and mocked system services to verify installation, repeated replacement, preserved overrides, symlink restoration, rollback, minimal mode, and respect for existing services. GitHub Actions runs installer tests and syntax checks. Hyprland's parser was checked locally on 0.56.2 and package names checked against CachyOS repositories. A fresh OS install, real system-service transitions, and every included app have not been tested end to end.

This is my independent personal desktop setup, unaffiliated with CachyOS, Hyprland, or Catppuccin. Third-party themes retain their licenses; see [credits and sources](THIRD_PARTY.md).
