"""Check installation without changing a real user service manager."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from argparse import Namespace

from devwarden import cli


class InstallTest(unittest.TestCase):
    """Check generated units, migration, and repeat installation."""

    def test_install_is_private_and_repeatable(self):
        """Install into isolated paths and retain private mail settings."""
        with tempfile.TemporaryDirectory(prefix='repo updater ') as tmp:
            base = Path(tmp)
            cfg, state, app = base / 'config', base / 'state', base / 'runtime'
            cfg.mkdir()
            (cfg / 'gmail.json').write_text(json.dumps(dict(sender='test@example.com', password='test-only')))
            env = base / '.env'
            env.write_text('DEVWARDEN_ROOT="' + str(base) + '"\n')
            units, executable = base / 'units', base / 'bin/devwarden'
            paths = dict(CONFIG_DIR=cfg, STATE_DIR=state, APP=app,
                         BIN=executable, UNITS=units, SETTINGS=cfg / 'settings.json',
                         SMTP=cfg / 'smtp.json', ENV_FILE=env)
            result = subprocess.CompletedProcess([], 0, stdout='inactive\n', stderr='')
            with patch.multiple(cli, **paths), patch.object(cli, 'command'), patch.object(cli.subprocess, 'run', return_value=result), patch.object(cli, 'load_settings', return_value=dict(root=str(base), calendar='Fri *-*-* 06:00:00', retention_days=90)):
                args = Namespace(root=str(base), calendar=None, yes=True)
                cli.install(args)
                with patch.object(cli, "SOURCE", app / "src/devwarden"):
                    cli.install(args)
            result = subprocess.run([sys.executable, str(executable), "--help"],
                                    cwd=base, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("email-test", result.stdout)
            self.assertTrue(executable.exists())
            self.assertFalse((app / '.env').exists())
            self.assertFalse((app / 'smtp.json').exists())
            self.assertEqual((cfg / 'smtp.json').stat().st_mode & 0o777, 0o600)
            self.assertEqual((cfg / '.env').stat().st_mode & 0o777, 0o600)
            unit = (units / 'devwarden.service').read_text()
            self.assertIn('-m devwarden.report', unit)
            self.assertIn(str(app / 'src'), unit)
            self.assertIn('UMask=0077', unit)
            self.assertNotIn('@PYTHONPATH_ENV@', unit)
            self.assertTrue((app / 'src/devwarden/__init__.py').exists())
            self.assertNotIn('test-only', unit)
            self.assertEqual(json.loads((cfg / 'smtp.json').read_text())['recipient'], 'test@example.com')


if __name__ == '__main__':
    unittest.main()
