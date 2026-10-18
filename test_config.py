"""Check private settings and literal environment files."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import config
import manage


class ConfigTest(unittest.TestCase):
    """Check configuration boundaries without real credentials."""

    def test_env_is_literal(self):
        """Do not execute shell expressions from an environment file."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / '.env'
            path.write_text('DEVWARDEN_ROOT="~/source code"\nDEVWARDEN_CALENDAR="$(false)"\n')
            result = config.read_env(path)
            self.assertEqual(result['DEVWARDEN_ROOT'], '~/source code')
            self.assertEqual(result['DEVWARDEN_CALENDAR'], '$(false)')
            path.write_text('INVALID=entry\n')
            with self.assertRaises(ValueError):
                config.read_env(path)

    def test_private_file_and_mail_override(self):
        """Keep settings private and apply explicit mail overrides."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'smtp.json'
            config.save_private(path, dict(sender='sender@example.com', recipient='old@example.com'))
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(path.read_text())['sender'], 'sender@example.com')
            with patch.dict(os.environ, {'DEVWARDEN_SMTP_RECIPIENT': 'new@example.com'}):
                self.assertEqual(config.mail_settings(path)['recipient'], 'new@example.com')

    def test_systemd_paths_are_quoted(self):
        """Do not treat unit paths as shell commands or systemd specifiers."""
        self.assertEqual(manage.unit_argument('/tmp/path with % and $'), '"/tmp/path with %% and $$"')
        with self.assertRaises(ValueError):
            manage.unit_argument('/tmp/path\nExecStart=bad')


if __name__ == '__main__':
    unittest.main()
