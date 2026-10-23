# Workstation capture — 2026-10-23

Compared the existing repository with the workstation's desktop configs. This refresh captures the following changes:

- Waybar: 38px bar, rounded outer corners, pastel module blocks, clock/date on the left, radio-style workspace indicators, and a compact set of system modules.
- Rofi: rounded Mocha launcher with larger text, padded entries, and colored selection states.
- Kitty: adjusted text spacing, padding, beam cursor, cursor trail, Powerline tabs, and explicit Mocha colors. Keeps the repository's Zsh launch setting.
- Hyprland: 5px inner/10px outer gaps, updated border/shadow opacity, and 24px cursor size.
- Hyprlock: smaller password field, clock/date labels, and colored password-check feedback. Uses the bundled JetBrains font and a solid Mocha fallback background.
- Shortcuts: Super+C for calculator, Super+Shift+B for Chromium, Super+W for locking, and frozen region screenshots. The existing calculator shortcut also works.

## Adjustments for installation

The live configuration is not a self-contained install. Its Waybar launches Wofi, while the repository already ships Rofi. The captured bar uses Rofi and retains right-click Apps for settings. Its power button opens the bundled confirmation menu.

The live Hyprland configuration references a missing `~/.local/bin/wallpaper-picker`, contains two Super+Shift+W bindings, and invokes `wpaperctl` without a captured setup. The repository keeps its working wallpaper helper and startup restoration. It also keeps notification, removable-drive, clipboard, and session startup support.

The live monitor is fixed to DP-1 at 1920×1080/60. The shared default continues to detect monitors; use `hypr/local.lua` for that workstation-specific setting. The installer preserves this override.

Spotify remains a web shortcut and the calculator remains Qalculate, matching the existing package bundle. This refresh does not introduce AUR dependencies.

## Differences retained for consistency

The follow-up capture also includes the workstation's Alacritty Noctalia palette, Tokyo Night btop selection (provided by the btop package), Fuzzel colors, generated GTK3 colors, Micro Macchiato preference, Qt widget style, Powerlevel10k prompt, and shell startup settings. The shell PATH is portable; application window geometry is excluded. Qt uses the bundled Papirus icons because the workstation's `char-white` icon theme is not available in the captured assets.

GTK4 on the workstation points to missing files under another user's home. The installer retains its valid bundled-theme import. Cursor settings retain the bundled Bibata theme rather than an unversioned `default` alias. Generated unused CSS, GTK bookmarks, application profiles, editor history, backup configs, and project-specific shell paths are excluded.

The screen-sharing portal retains its existing permission default rather than copying the workstation's automatic screencopy-token approval.

## Verification

- All nine installer/restore/service tests passed using temporary homes and mocked services.
- Hyprland 0.56.2 accepted the updated Lua configuration with `--verify-config`.
- Shell syntax and Git whitespace checks passed.

The updated visuals have not been launched as a separate desktop session. No live system settings were changed during this capture.
