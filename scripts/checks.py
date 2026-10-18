#!/usr/bin/env python3
"""Run native Git hooks and validate Conventional Commit subjects."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

SUBJECT = re.compile(
    r'(?:feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)'
    r'(?:\([a-z0-9][a-z0-9._/-]*\))?!?: [^\s].*')


def git(*args):
    """Read Git output and fail when a command cannot complete."""
    return subprocess.check_output(['git', *args], text=True).strip()


def check_message(message):
    """Require a typed subject, a concise summary, and a separate body."""
    lines = message.strip().splitlines()
    if not lines or not SUBJECT.fullmatch(lines[0]) or len(lines[0]) > 72:
        raise ValueError('Use a Conventional Commit subject of at most 72 characters, '
                         'such as feat(hooks): validate commits before push.')
    if len(lines) > 1 and lines[1].strip():
        raise ValueError('Put a blank line between the commit subject and body.')


def test_tree(tree):
    """Test an exported Git tree. Do not include unstaged files."""
    with tempfile.TemporaryDirectory(prefix='devwarden-check-') as directory:
        archive = subprocess.check_output(['git', 'archive', tree])
        subprocess.run(['tar', '-x', '-C', directory], input=archive, check=True)
        # Hook-local Git variables must not redirect the isolated test repositories.
        environment = dict(os.environ)
        for name in git('rev-parse', '--local-env-vars').splitlines():
            environment.pop(name, None)
        for name in list(environment):
            if name.startswith('DEVWARDEN_'):
                environment.pop(name)
        environment.update(DEVWARDEN_CONFIG_DIR=str(Path(directory) / '.test-config'),
                           DEVWARDEN_STATE_DIR=str(Path(directory) / '.test-state'))
        subprocess.run([sys.executable, 'scripts/test.py'], cwd=directory,
                       env=environment, check=True)


def pre_push(stream):
    """Validate new commit messages. Test each commit at the end of a pushed branch."""
    tested = set()
    for line in stream:
        _, local, _, remote = line.split()
        if set(local) == {'0'} or local in tested:
            continue
        if set(remote) != {'0'} and subprocess.run(
                ['git', 'cat-file', '-e', remote + '^{commit}'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            commits = git('rev-list', local, '^' + remote).splitlines()
        else:
            commits = git('rev-list', local, '--not', '--remotes').splitlines()
        for commit in commits:
            check_message(git('show', '-s', '--format=%B', commit))
        test_tree(local)
        tested.add(local)


def main():
    """Install local hooks or dispatch one Git hook without network access."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'pre-commit', 'commit-msg', 'pre-push', 'ci'))
    parser.add_argument('hook_args', nargs='*')
    args = parser.parse_args()
    try:
        if args.action == 'install':
            git('config', '--local', 'core.hooksPath', '.githooks')
            print('Enabled pre-commit, commit-msg, and pre-push hooks for this clone.')
        elif args.action == 'commit-msg':
            if len(args.hook_args) != 1:
                raise ValueError('The commit-msg hook requires a message file.')
            check_message(Path(args.hook_args[0]).read_text())
        elif args.action == 'ci':
            for commit in git('rev-list', 'HEAD').splitlines():
                check_message(git('show', '-s', '--format=%B', commit))
            if os.environ.get('PR_TITLE'):
                check_message(os.environ['PR_TITLE'])
        elif args.action == 'pre-commit':
            subprocess.run(['git', 'diff', '--cached', '--check'], check=True)
            test_tree(git('write-tree'))
        else:
            pre_push(sys.stdin)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'DevWarden hook failed: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
