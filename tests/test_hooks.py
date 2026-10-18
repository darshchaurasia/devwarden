"""Check commit subjects and the exact tree used by local Git hooks."""
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import checks


class HookTest(unittest.TestCase):
    """Reject malformed subjects and keep hooks tied to staged or pushed code."""

    def test_commit_subjects(self):
        """Accept standard types and reject ambiguous or oversized subjects."""
        for message in ('feat: add service', 'fix(smtp): retain failed mail',
                        'refactor!: change layout\n\nExplain the change.'):
            checks.check_message(message)
        for message in ('update things', 'bug: fix mail', 'feat; add hooks',
                        'feat: ', 'feat: ' + 'x' * 73, 'fix: mail\nNo blank line'):
            with self.assertRaises(ValueError):
                checks.check_message(message)

    def test_staged_snapshot(self):
        """Test staged code even when the working file contains different code."""
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            subprocess.run(['git', 'init', '-q', directory], check=True)
            (base / 'scripts').mkdir()
            script = base / 'scripts/test.py'
            script.write_text('import os\nassert "GIT_INDEX_FILE" not in os.environ\n')
            subprocess.run(['git', '-C', directory, 'add', '.'], check=True)
            tree = subprocess.check_output(['git', '-C', directory, 'write-tree'], text=True).strip()
            script.write_text('raise SystemExit(1)\n')
            original = subprocess.check_output
            def in_repository(args, **kwargs):
                """Read the staged tree from the isolated Git repository."""
                return original(['git', '-C', directory, *args[1:]], **kwargs)
            with patch.object(checks.subprocess, 'check_output', side_effect=in_repository), \
                    patch.dict(os.environ, GIT_INDEX_FILE=str(base / '.git/index')):
                checks.test_tree(tree)

    def test_push_deletions_and_duplicate_tips(self):
        """Skip deleted refs and run tests once when refs share a commit."""
        zero, sha = '0' * 40, 'a' * 40
        stream = io.StringIO(f'refs/heads/main {sha} refs/heads/main {zero}\n'
                             f'refs/heads/tag {sha} refs/heads/tag {zero}\n'
                             f'refs/heads/old {zero} refs/heads/old {sha}\n')
        with patch.object(checks, 'git', return_value=''), patch.object(checks, 'test_tree') as test:
            checks.pre_push(stream)
        test.assert_called_once_with(sha)


    def test_pre_push_accepts_git_arguments(self):
        """Accept Git's remote name and URL without requiring pending refs."""
        script = Path(__file__).resolve().parents[1] / 'scripts/checks.py'
        result = subprocess.run([sys.executable, str(script), 'pre-push',
                                 'origin', 'https://github.com/example/project.git'],
                                input='', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
