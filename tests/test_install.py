"""Exercise real file replacement and recovery inside an isolated home."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.config = self.home / 'custom config'
        self.data = self.home / 'custom data'
        self.state = self.home / 'state'
        self.env = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(self.config),
                        XDG_DATA_HOME=str(self.data), XDG_STATE_HOME=str(self.state))
        self.config.mkdir()
        original = self.home / 'original-waybar'
        original.mkdir()
        (original / 'sentinel').write_text('original')
        (self.config / 'waybar').symlink_to(original, target_is_directory=True)
        (self.config / 'hypr').mkdir()
        (self.config / 'hypr/local.lua').write_text('-- personal monitor override\n')

    def run_installer(self, *args):
        return subprocess.run(['bash', str(ROOT / 'install.sh'), *args], env=self.env,
                              text=True, capture_output=True, check=True)

    def backup(self):
        return sorted((self.state / 'cachyos-mocha/backups').iterdir())[-1]

    def test_dry_run_writes_nothing(self):
        self.run_installer('--dry-run')
        self.assertFalse(self.state.exists())
        self.assertFalse(self.data.exists())
        self.assertTrue((self.config / 'waybar').is_symlink())

    def test_replace_repeat_restore_and_xdg_paths(self):
        self.run_installer('--config-only')
        first = self.backup()
        self.assertFalse((self.config / 'waybar').is_symlink())
        self.assertEqual((self.config / 'hypr/local.lua').read_text(), '-- personal monitor override\n')
        css = (self.config / 'gtk-4.0/gtk.css').read_text()
        self.assertIn((self.data / 'themes/catppuccin-mocha-green-standard+default/gtk-4.0/gtk.css').as_uri(), css)
        self.assertTrue(os.access(self.home / '.local/bin/mocha-wallpaper', os.X_OK))
        self.assertTrue((self.config / 'nvim/init.lua').exists())
        self.run_installer('--config-only')
        second = self.backup()
        self.assertNotEqual(first, second)
        self.run_installer('--restore', str(second))
        self.run_installer('--restore', str(first))
        self.assertTrue((self.config / 'waybar').is_symlink())
        self.assertEqual((self.config / 'waybar/sentinel').read_text(), 'original')
        self.assertFalse((self.config / 'kitty').exists())
        self.assertFalse((self.home / '.local/bin/mocha-wallpaper').exists())
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_installer('--restore', str(first))
        self.assertEqual((self.config / 'hypr/local.lua').read_text(), '-- personal monitor override\n')

    def test_minimal(self):
        self.run_installer('--config-only', '--minimal')
        self.assertFalse((self.config / 'nvim').exists())
        self.assertFalse((self.config / 'ghostty').exists())

    def test_failed_install_rolls_back(self):
        spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original_move = module.shutil.move
        def failing_move(src, dst, *args, **kwargs):
            if 'mocha-stage-' in str(src) and Path(dst) == self.config / 'waybar':
                raise OSError('simulated interrupted copy')
            return original_move(src, dst, *args, **kwargs)
        with patch.dict(os.environ, self.env), patch('sys.argv', ['install.py', '--config-only']), patch.object(module.shutil, 'move', side_effect=failing_move):
            with self.assertRaisesRegex(OSError, 'simulated'):
                module.main()
        self.assertTrue((self.config / 'waybar').is_symlink())
        self.assertEqual((self.config / 'waybar/sentinel').read_text(), 'original')
        self.assertEqual((self.config / 'hypr/local.lua').read_text(), '-- personal monitor override\n')


    def load_module(self):
        spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_configs_only_alias_never_installs_tools_or_changes_services(self):
        module = self.load_module()
        with patch.dict(os.environ, self.env), patch('sys.argv', ['install.py', '--configs-only']), patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as run, patch.object(module.subprocess, 'check_output', side_effect=AssertionError('No external version checks in configs-only mode')):
            module.main()
        calls = [c.args[0] for c in run.call_args_list]
        self.assertFalse(any(any(tool in c for tool in ['sudo', 'pacman', 'systemctl']) for c in calls))
        self.assertFalse(any(rec.get('privileged') for rec in json.loads((self.backup() / 'manifest.json').read_text())))
        self.assertFalse((self.backup() / 'services.json').exists())
        self.assertTrue((self.config / 'hypr/hyprland.lua').exists())
        self.assertTrue((self.data / 'cachyos-mocha/wallpapers/catppuccin.png').exists())

    def test_services_keep_existing_network_and_enable_ly_on_tty2(self):
        module = self.load_module()
        def status(name, user=False):
            if name == 'systemd-networkd.service':
                return 'enabled', 'active'
            return 'disabled', 'inactive'
        backup = self.home / 'service-backup'
        backup.mkdir()
        with patch.object(module, 'service_status', side_effect=status), patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as run:
            module.configure_services(backup, install_session=True)
        calls = [c.args[0] for c in run.call_args_list]
        self.assertFalse(any('NetworkManager.service' in c for c in calls))
        self.assertIn(['sudo', 'systemctl', 'enable', '--now', 'ly@tty2'], calls)
        self.assertIn(['sudo', 'systemctl', 'disable', '--now', 'getty@tty2.service'], calls)
        self.assertTrue(any('bluetooth.service' in c for c in calls))
        self.assertTrue(any('--user' in c and 'pipewire.socket' in c for c in calls))

    def test_login_manager_migration_and_restore(self):
        module = self.load_module()
        backup = self.home / 'login-backup'
        backup.mkdir()
        def run_command(command, **kwargs):
            stdout = 'sddm.service\n' if 'show' in command else ''
            return subprocess.CompletedProcess(command, 0, stdout=stdout)
        with patch.object(module, 'service_status', return_value=('enabled', 'active')), patch.object(module.subprocess, 'run', side_effect=run_command) as run:
            module.configure_services(backup, install_session=True)
            calls = [c.args[0] for c in run.call_args_list]
            self.assertIn(['sudo', 'systemctl', 'disable', 'sddm.service'], calls)
            self.assertFalse(any('stop' in c and 'sddm.service' in c for c in calls))
            run.reset_mock()
            module.restore_services(backup)
            calls = [c.args[0] for c in run.call_args_list]
            self.assertIn(['sudo', 'systemctl', 'enable', 'sddm.service'], calls)
            self.assertIn(['sudo', 'systemctl', 'start', 'getty@tty2.service'], calls)

    def test_no_session_skips_login_manager_changes(self):
        module = self.load_module()
        backup = self.home / 'no-session-backup'
        backup.mkdir()
        with patch.object(module, 'service_status', return_value=('disabled', 'inactive')), patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as run:
            module.configure_services(backup, install_session=False)
        calls = [c.args[0] for c in run.call_args_list]
        self.assertFalse(any('ly@tty2' in c or 'getty@tty2.service' in c for c in calls))

    def test_restore_services_keeps_preexisting_active_services(self):
        module = self.load_module()
        backup = self.home / 'service-backup'
        backup.mkdir()
        (backup / 'services.json').write_text(json.dumps([
            {'name': 'NetworkManager.service', 'user': False, 'enabled': 'enabled', 'active': 'active'},
            {'name': 'bluetooth.service', 'user': False, 'enabled': 'disabled', 'active': 'inactive'}]))
        with patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as run:
            module.restore_services(backup)
        calls = [c.args[0] for c in run.call_args_list]
        self.assertFalse(any('NetworkManager.service' in c for c in calls))
        self.assertTrue(any('stop' in c and 'bluetooth.service' in c for c in calls))
        self.assertTrue(any('disable' in c and 'bluetooth.service' in c for c in calls))

if __name__ == '__main__':
    unittest.main()
