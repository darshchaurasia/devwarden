"""Offline integration check: fast-forward, dirty checkout, and divergence."""
import tempfile
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
from devwarden import update


def run(*args):
    """Run the updater and save its output before mail delivery."""
    return subprocess.run(['git', *map(str, args)], check=True, capture_output=True, text=True).stdout.strip()


class UpdateTest(unittest.TestCase):
    """Check repository and report behavior with isolated test data."""
    def test_empty_remote_excluded_but_broken_default_is_error(self):
        """Check empty remote excluded but broken default is error."""
        with tempfile.TemporaryDirectory() as tmp, patch.object(update, 'github_origin', return_value=True):
            root = Path(tmp)
            remote, checkout = root / 'remote', root / 'checkout'
            run('init', '--bare', '--initial-branch=main', remote)
            run('clone', remote, checkout)
            status, detail = update.update(checkout, False)
            self.assertEqual(status, 'SKIP')
            self.assertIn('no branches', detail)
            run('-C', checkout, 'config', 'user.email', 'test@example.com')
            run('-C', checkout, 'config', 'user.name', 'Test')
            run('-C', checkout, 'commit', '--allow-empty', '-m', 'Initial commit')
            run('-C', checkout, 'push', 'origin', 'main')
            run('-C', remote, 'symbolic-ref', 'HEAD', 'refs/heads/missing')
            status, detail = update.update(checkout, False)
            self.assertEqual(status, 'ERROR')
            self.assertIn('has branches but no default branch', detail)

    def test_redacts_authentication_from_diagnostics(self):
        """Check redacts authentication from diagnostics."""
        self.assertEqual(update.redact('https://user:secret@github.com/owner/repo ghp_secret123'),
                         'https://[REDACTED]@github.com/owner/repo [REDACTED]')

    def test_preserves_local_work(self):
        """Check preserves local work."""
        with tempfile.TemporaryDirectory() as tmp, patch.object(update, 'github_origin', return_value=True):
            root = Path(tmp)
            remote, source, checkout = [root / name for name in ('remote', 'source', 'checkout')]
            run('init', '--bare', '--initial-branch=main', remote)
            run('clone', remote, source)
            for repo in (source,):
                run('-C', repo, 'config', 'user.email', 'test@example.com')
                run('-C', repo, 'config', 'user.name', 'Test')
            def commit(text):
                """Record and push a test change to a temporary remote."""
                (source / 'file').write_text(text)
                run('-C', source, 'add', 'file')
                run('-C', source, 'commit', '-m', text)
                run('-C', source, 'push', 'origin', 'main')
            commit('first')
            run('clone', remote, checkout)
            commit('second')
            self.assertEqual(update.update(checkout, True)[0], 'READY')
            self.assertEqual((checkout / 'file').read_text(), 'first')
            metadata = {}
            self.assertEqual(update.update(checkout, False, metadata)[0], 'UPDATED')
            self.assertEqual(metadata['commits'], 1)
            self.assertEqual(metadata['branch'], 'main')
            self.assertEqual(metadata['default_branch'], 'main')
            self.assertEqual((checkout / 'file').read_text(), 'second')
            run('-C', checkout, 'checkout', '-b', 'work-in-progress')
            feature_head = run('-C', checkout, 'rev-parse', 'HEAD')
            (checkout / 'untracked').write_text('keep this')
            (checkout / 'file').write_text('feature edit')
            run('-C', checkout, 'add', 'file')
            staged = run('-C', checkout, 'diff', '--cached')
            commit('feature-safe-update')
            self.assertEqual(update.update(checkout, False)[0], 'UPDATED')
            self.assertEqual(run('-C', checkout, 'branch', '--show-current'), 'work-in-progress')
            self.assertEqual((checkout / 'file').read_text(), 'feature edit')
            self.assertEqual((checkout / 'untracked').read_text(), 'keep this')
            self.assertEqual(run('-C', checkout, 'diff', '--cached'), staged)
            self.assertEqual(run('-C', checkout, 'rev-parse', 'main'), run('-C', source, 'rev-parse', 'main'))
            run('-C', checkout, 'restore', '--staged', 'file')
            run('-C', checkout, 'restore', 'file')
            (checkout / 'untracked').unlink()
            self.assertEqual(update.update(checkout, True)[0], 'READY')
            self.assertEqual(run('-C', checkout, 'branch', '--show-current'), 'work-in-progress')
            switched = {}
            self.assertEqual(update.update(checkout, False, switched)[0], 'CURRENT')
            self.assertEqual(switched['preserved_branch'], 'work-in-progress')
            self.assertEqual(run('-C', checkout, 'branch', '--show-current'), 'work-in-progress')
            self.assertEqual(run('-C', checkout, 'rev-parse', 'work-in-progress'), feature_head)
            run('-C', checkout, 'switch', 'main')
            (checkout / 'file').write_text('local work')
            self.assertEqual(update.update(checkout, False)[0], 'ERROR')
            self.assertEqual((checkout / 'file').read_text(), 'local work')
            run('-C', checkout, 'config', 'user.email', 'test@example.com')
            run('-C', checkout, 'config', 'user.name', 'Test')
            run('-C', checkout, 'commit', '-am', 'local')
            head = run('-C', checkout, 'rev-parse', 'HEAD')
            commit('third')
            self.assertEqual(update.update(checkout, False)[0], 'ERROR')
            diagnostics = {}
            self.assertEqual(update.update(checkout, False, diagnostics)[0], 'ERROR')
            self.assertEqual((diagnostics['ahead'], diagnostics['behind']), (1, 1))
            self.assertEqual(run('-C', checkout, 'rev-parse', 'HEAD'), head)
            run('-C', checkout, 'checkout', '-b', 'feature')
            self.assertEqual(update.update(checkout, False)[0], 'ERROR')


if __name__ == '__main__':
    unittest.main()
