"""Examine source documentation, local links, and the public source launcher."""
import ast
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote

PROJECT = Path(__file__).resolve().parents[1]


class ProjectTest(unittest.TestCase):
    """Keep the source layout and documentation usable after file moves."""

    def test_docstrings_and_syntax(self):
        """Require module, class, and function docstrings and Python 3.10 syntax."""
        for directory in ('src', 'scripts', 'tests'):
            for path in (PROJECT / directory).rglob('*.py'):
                tree = ast.parse(path.read_text(), filename=str(path), feature_version=(3, 10))
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                        self.assertTrue(ast.get_docstring(node), f'{path}:{getattr(node, "lineno", 1)}')

    def test_document_links(self):
        """Resolve relative Markdown links from each document's new location."""
        paths = [PROJECT / 'README.md', PROJECT / 'index.md']
        paths += list((PROJECT / 'docs').rglob('*.md'))
        paths += list((PROJECT / '.github').glob('*.md'))
        for path in paths:
            for target in re.findall(r'\]\(([^\s)]+)\)', path.read_text()):
                if target.startswith(('https:', 'http:', '#', 'mailto:')):
                    continue
                target = unquote(target.split('#', 1)[0])
                self.assertTrue((path.parent / target).exists(), f'{path}: {target}')

    def test_source_launcher_from_other_directory(self):
        """Launch help without relying on the user's working directory."""
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(PROJECT / 'scripts/devwarden.py'), '--help'],
                                    cwd=directory, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('email-test', result.stdout)
