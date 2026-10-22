#!/usr/bin/env python3
"""Install a reviewed snapshot; never execute as root."""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CORE = ['hypr', 'waybar', 'rofi', 'kitty', 'Kvantum', 'qt5ct', 'qt6ct',
        'gtk-3.0', 'gtk-4.0', 'mako', 'fontconfig']
EXTRAS = ['btop', 'cava', 'micro', 'nvim', 'ghostty', 'fuzzel', 'htop', 'alacritty']

def exists(path):
    return path.exists() or path.is_symlink()

def remove(path):
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif exists(path):
        path.unlink()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dry-run', action='store_true', help='print changes without writing or installing')
    ap.add_argument('--config-only', action='store_true', help='skip packages and version check')
    ap.add_argument('--extras', action='store_true', help='also install terminal/editor utility configs and packages')
    ap.add_argument('--restore', type=Path, metavar='BACKUP', help='restore a backup; save displaced files alongside it')
    args = ap.parse_args()
    if os.geteuid() == 0:
        ap.error('Run as your normal desktop user; only pacman uses sudo.')
    home = Path.home()
    config = Path(os.environ.get('XDG_CONFIG_HOME', home / '.config')).absolute()
    data = Path(os.environ.get('XDG_DATA_HOME', home / '.local/share')).absolute()
    state = Path(os.environ.get('XDG_STATE_HOME', home / '.local/state')).absolute()
    if args.restore:
        backup = args.restore.resolve()
        records = json.loads((backup / 'manifest.json').read_text())
        for rec in reversed(records):
            target = Path(rec['target'])
            saved = backup / rec['saved']
            if rec['existed'] and not exists(saved):
                raise RuntimeError(f'Missing backup: {saved}; this backup may already be restored')
            print(f'Restore {target}')
        if args.dry_run:
            return
        displaced = backup / ('displaced-' + datetime.datetime.now().strftime('%Y%m%dT%H%M%S%f'))
        displaced.mkdir()
        for i, rec in enumerate(reversed(records)):
            target = Path(rec['target'])
            if exists(target):
                shutil.move(str(target), displaced / str(i))
            if rec['existed']:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(backup / rec['saved']), target)
        print(f'Restored. Replaced files saved in {displaced}. Log out and back in.')
        return
    pairs = [(ROOT / 'config' / name, config / name) for name in CORE + (EXTRAS if args.extras else [])]
    pairs += [(p, data / 'themes' / p.name) for p in (ROOT / 'share/themes').iterdir()]
    pairs += [(p, data / 'icons' / p.name) for p in (ROOT / 'share/icons').iterdir()]
    pairs += [(ROOT / 'config/gtkrc-2.0', home / '.gtkrc-2.0')]
    pairs += [(ROOT / 'share/cachyos-mocha', data / 'cachyos-mocha')]
    pairs += [(p, home / '.local/bin' / p.name) for p in sorted((ROOT / 'bin').iterdir())]
    for src, target in pairs:
        if not src.exists():
            raise RuntimeError(f'Missing source: {src}')
        if target == ROOT or ROOT.is_relative_to(target.resolve()):
            raise RuntimeError('Clone outside the directories being replaced (for example ~/Projects/cachyos-mocha).')
        print(f'{src.relative_to(ROOT)} -> {target} (backup first)')
    if args.dry_run:
        print('Dry run: no files, packages, services, or desktop settings changed.')
        return
    if not args.config_only:
        if not shutil.which('pacman'):
            raise RuntimeError('Default installation requires CachyOS/Arch with pacman.')
        packages = [line.strip() for line in (ROOT / 'packages.txt').read_text().splitlines()
                    if line.strip() and not line.startswith('#')]
        if args.extras:
            packages += ['btop', 'cava', 'micro', 'neovim', 'ghostty', 'fuzzel', 'htop', 'alacritty']
        subprocess.run(['sudo', 'pacman', '-Syu', '--needed', *packages], check=True)
        version = subprocess.check_output(['Hyprland', '--version'], text=True, stderr=subprocess.STDOUT)
        match = re.search(r'Hyprland\s+(\d+)\.(\d+)', version)
        if not match or tuple(map(int, match.groups())) < (0, 55):
            raise RuntimeError('This Lua configuration requires Hyprland 0.55 or newer. No configs changed.')
    # Stage every file before touching any destination.
    state.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mocha-stage-', dir=state) as temp:
        staged = []
        for i, (src, target) in enumerate(pairs):
            stage = Path(temp) / str(i)
            if src.is_dir():
                shutil.copytree(src, stage)
            else:
                shutil.copy2(src, stage)
            if target == config / 'hypr' and (target / 'local.lua').is_file():
                shutil.copy2(target / 'local.lua', stage / 'local.lua')
            # GTK4 needs an absolute import when XDG paths differ from defaults.
            if target == config / 'gtk-4.0':
                uri = (data / 'themes/catppuccin-mocha-green-standard+default/gtk-4.0/gtk.css').as_uri()
                (stage / 'gtk.css').write_text(f'@import url("{uri}");\n')
            staged.append((stage, target))
        backup = state / 'cachyos-mocha/backups' / datetime.datetime.now().strftime('%Y%m%dT%H%M%S%f')
        backup.mkdir(parents=True)
        records = []
        try:
            for i, (stage, target) in enumerate(staged):
                rec = {'target': str(target), 'saved': f'files/{i}', 'existed': exists(target)}
                saved = backup / rec['saved']
                saved.parent.mkdir(exist_ok=True)
                target.parent.mkdir(parents=True, exist_ok=True)
                if rec['existed']:
                    shutil.move(str(target), saved)
                records.append(rec)
                (backup / 'manifest.json').write_text(json.dumps(records, indent=2) + '\n')
                shutil.move(str(stage), target)
        except BaseException:
            for rec in reversed(records):
                target = Path(rec['target'])
                remove(target)
                if rec['existed']:
                    shutil.move(str(backup / rec['saved']), target)
            raise
    if shutil.which('fc-cache'):
        subprocess.run(['fc-cache', '-f'], check=False)
    print(f'Installed. Backup: {backup}')
    print(f'Restore: ./install.sh --restore {backup}')
    print('Log out and select Hyprland at login. No running session was reloaded.')
    print('For Wi-Fi/Bluetooth, enable NetworkManager/bluetooth services if needed (see README).')

if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f'Install failed: {error}')
