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
        'gtk-3.0', 'gtk-4.0', 'mako', 'fontconfig', 'xdg-desktop-portal']
EXTRAS = ['btop', 'cava', 'micro', 'nvim', 'ghostty', 'fuzzel', 'htop', 'alacritty']

def exists(path):
    return path.exists() or path.is_symlink()

def move_file(src, target, privileged=False):
    if privileged:
        subprocess.run(['sudo', 'mkdir', '-p', str(target.parent)], check=True)
        subprocess.run(['sudo', 'mv', '--', str(src), str(target)], check=True)
    else:
        shutil.move(str(src), target)

def remove(path, privileged=False):
    if privileged:
        subprocess.run(['sudo', 'rm', '-rf', '--', str(path)], check=True)
        return

    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif exists(path):
        path.unlink()

def service_status(name, user=False):
    base = ['systemctl', *(['--user'] if user else [])]
    enabled = subprocess.run([*base, 'is-enabled', name], capture_output=True, text=True).stdout.strip()
    active = subprocess.run([*base, 'is-active', name], capture_output=True, text=True).stdout.strip()
    return enabled, active

def configure_services(backup, install_session):
    changes = []
    def enable(name, user=False):
        enabled, active = service_status(name, user)
        if enabled in ('masked', 'masked-runtime'):
            print(f'Keeping explicitly masked service: {name}')
            return
        changes.append({'name': name, 'user': user, 'enabled': enabled, 'active': active})
        (backup / 'services.json').write_text(json.dumps(changes, indent=2) + '\n')
        command = ['systemctl', *(['--user'] if user else []), 'enable', '--now', name]
        subprocess.run(command if user else ['sudo', *command], check=True)
    conflicting_network = any(service_status(name)[1] == 'active'
                              for name in ['systemd-networkd.service', 'connman.service', 'dhcpcd.service'])
    if conflicting_network:
        print('Keeping existing network service; NetworkManager was installed but not enabled.')
    else:
        enable('NetworkManager.service')
    enable('bluetooth.service')
    if install_session:
        def disable(name, stop=False):
            enabled, active = service_status(name)
            if enabled in ('masked', 'masked-runtime', 'not-found'):
                return
            changes.append({'name': name, 'user': False, 'enabled': enabled,
                            'active': active, 'action': 'disable'})
            (backup / 'services.json').write_text(json.dumps(changes, indent=2) + '\n')
            subprocess.run(['sudo', 'systemctl', 'disable', *(['--now'] if stop else []), name], check=True)
        manager = subprocess.run(['systemctl', 'show', '-p', 'Id', '--value',
                                  'display-manager.service'], capture_output=True, text=True)
        manager_name = (manager.stdout or '').strip()
        if manager.returncode == 0 and manager_name.endswith('.service') and manager_name != 'display-manager.service' and not manager_name.startswith('ly@'):
            # Keep the running desktop alive; prevent the old manager on next boot.
            disable(manager_name)
        disable('getty@tty2.service', stop=True)
        enable('ly@tty2')
    for name in ['pipewire.socket', 'pipewire-pulse.socket', 'wireplumber.service']:
        enable(name, user=True)

def restore_services(backup, dry_run=False):
    path = backup / 'services.json'
    if not path.exists():
        return
    for rec in reversed(json.loads(path.read_text())):
        command = ['systemctl', *(['--user'] if rec['user'] else [])]
        if not rec['user']:
            command.insert(0, 'sudo')
        if not dry_run:
            if rec.get('action') == 'disable':
                if rec['enabled'] in ('enabled', 'enabled-runtime'):
                    subprocess.run([*command, 'enable', *(['--runtime'] if rec['enabled'] == 'enabled-runtime' else []), rec['name']], check=False)
                if rec['active'] == 'active':
                    subprocess.run([*command, 'start', rec['name']], check=False)
                continue
            if rec['active'] != 'active':
                subprocess.run([*command, 'stop', rec['name']], check=False)
            if rec['enabled'] not in ('enabled', 'enabled-runtime', 'static', 'indirect', 'alias'):
                subprocess.run([*command, 'disable', rec['name']], check=False)
    if not dry_run:
        path.rename(backup / 'services-restored.json')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dry-run', action='store_true', help='print changes without writing or installing')
    ap.add_argument('--config-only', '--configs-only', dest='config_only', action='store_true',
                    help='copy configs/assets only; skip packages, services, login registration and version checks')
    ap.add_argument('--extras', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--minimal', action='store_true', help='omit editor and alternate-terminal configs')
    ap.add_argument('--no-services', action='store_true', help='leave system and audio services unchanged')
    ap.add_argument('--no-session', action='store_true', help='skip system-wide branded login session')
    ap.add_argument('--yes', action='store_true', help='pass --noconfirm to pacman for unattended installation')
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
        if (backup / 'RESTORED').exists() or (backup / 'ROLLED_BACK').exists():
            raise RuntimeError('This backup was already restored or rolled back.')
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
                move_file(target, displaced / str(i), rec.get('privileged', False))
            if rec['existed']:
                if not rec.get('privileged', False):
                    target.parent.mkdir(parents=True, exist_ok=True)
                move_file(backup / rec['saved'], target, rec.get('privileged', False))
        restore_services(backup, args.dry_run)
        (backup / 'RESTORED').touch()
        print(f'Restored. Replaced files saved in {displaced}. Log out and back in.')
        return
    pairs = [(ROOT / 'config' / name, config / name) for name in CORE + ([] if args.minimal else EXTRAS)]
    pairs += [(p, data / 'themes' / p.name) for p in (ROOT / 'share/themes').iterdir()]
    pairs += [(p, data / 'icons' / p.name) for p in (ROOT / 'share/icons').iterdir()]
    pairs += [(ROOT / 'config/gtkrc-2.0', home / '.gtkrc-2.0'),
              (ROOT / 'config/shell/zshrc', home / '.zshrc'),
              (ROOT / 'config/shell/p10k.zsh', home / '.p10k.zsh')]
    pairs += [(p, data / 'applications' / p.name) for p in (ROOT / 'share/applications').iterdir()]
    pairs += [(ROOT / 'share/cachyos-mocha', data / 'cachyos-mocha')]
    pairs += [(p, home / '.local/bin' / p.name) for p in sorted((ROOT / 'bin').iterdir())]
    if not args.config_only and not args.no_session:
        pairs += [(ROOT / 'session/cachyos-mocha.desktop', Path('/usr/share/wayland-sessions/cachyos-mocha.desktop')),
                  (ROOT / 'session/cachyos-mocha-session', Path('/usr/local/bin/cachyos-mocha-session'))]
    for src, target in pairs:
        if not src.exists():
            raise RuntimeError(f'Missing source: {src}')
        if target == ROOT or ROOT.is_relative_to(target.resolve()):
            raise RuntimeError('Clone outside the directories being replaced (for example ~/Projects/cachyos-mocha).')
        print(f'{src.relative_to(ROOT)} -> {target} (backup first)')
    if args.dry_run:
        if not args.config_only and not args.no_services:
            print('Services: configure NetworkManager, Bluetooth and user audio; disable the old login manager at boot, free tty2, and run sudo systemctl enable --now ly@tty2.')
        print('Dry run: no files, packages, services, or desktop settings changed.')
        return
    if not args.config_only:
        if not shutil.which('pacman'):
            raise RuntimeError('Default installation requires CachyOS/Arch with pacman.')
        packages = [line.strip() for line in (ROOT / 'packages.txt').read_text().splitlines()
                    if line.strip() and not line.startswith('#')]
        subprocess.run(['sudo', 'pacman', '-Syu', '--needed', *(['--noconfirm'] if args.yes else []), *packages], check=True)
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
                rec = {'target': str(target), 'saved': f'files/{i}', 'existed': exists(target), 'privileged': target.is_relative_to('/usr')}
                saved = backup / rec['saved']
                saved.parent.mkdir(exist_ok=True)
                if not rec['privileged']:
                    target.parent.mkdir(parents=True, exist_ok=True)
                if rec['existed']:
                    move_file(target, saved, rec['privileged'])
                records.append(rec)
                (backup / 'manifest.json').write_text(json.dumps(records, indent=2) + '\n')
                move_file(stage, target, rec['privileged'])
                if rec['privileged']:
                    subprocess.run(['sudo', 'chown', 'root:root', str(target)], check=True)
            if not args.config_only and not args.no_services:
                configure_services(backup, install_session=not args.no_session)
        except BaseException:
            restore_services(backup, False)
            for rec in reversed(records):
                target = Path(rec['target'])
                remove(target, rec.get('privileged', False))
                if rec['existed']:
                    move_file(backup / rec['saved'], target, rec.get('privileged', False))
            (backup / 'ROLLED_BACK').touch()
            raise
    if shutil.which('fc-cache'):
        subprocess.run(['fc-cache', '-f'], check=False)
    print(f'Installed. Backup: {backup}')
    print(f'Restore: ./install.sh --restore {backup}')
    if args.config_only or args.no_session:
        print('Log out and choose your existing Hyprland session to load the installed configs.')
    else:
        print('Select CachyOS Mocha in Ly on tty2 (Ctrl+Alt+F2).')
    print('Check desktop readiness with ~/.local/bin/mocha-doctor.')

if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f'Install failed: {error}')
