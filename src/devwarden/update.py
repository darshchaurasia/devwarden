#!/usr/bin/env python3
"""Update clean GitHub default branches in the selected repository folder."""
import argparse
import collections
import fcntl
import signal
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import tempfile

from .config import STATE_DIR, load_settings

ENV = dict({key: value for key, value in os.environ.items()
            if key != 'DEVWARDEN_SMTP_PASSWORD'}, GIT_TERMINAL_PROMPT='0',
           GIT_SSH_COMMAND='ssh -oBatchMode=yes -oConnectTimeout=20', GIT_LFS_SKIP_SMUDGE='1')


def redact(value):
    """Remove common credential forms from a diagnostic message."""
    value = re.sub(r'(https?://)[^/\s@]+@', r'\1[REDACTED]@', value)
    return re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)\b', '[REDACTED]', value)


def git(repo, *args, retry=False):
    """Run a Git command with a time limit and optional retries."""
    for attempt in range(3 if retry else 1):
        with subprocess.Popen(['git', '-C', str(repo), *args], env=ENV,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, start_new_session=True) as process:
            try:
                stdout, stderr = process.communicate(timeout=180)
                if process.returncode == 0:
                    return stdout.strip()
                error = f'exit {process.returncode}: ' + (stderr.strip() or stdout.strip())
            except subprocess.TimeoutExpired:
                # Kill the command group so a credential helper cannot outlive a retry.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.communicate()
                error = 'Git command timed out after 180 seconds'
        if retry and attempt < 2:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(redact(f'git {" ".join(args)}; attempts={attempt + 1}; {error[-1200:]}'))


def github_origin(url):
    """Examine whether an origin URL uses the supported GitHub host."""
    return bool(re.match(r'^(https?://(?:[^/@]+@)?github\.com/|ssh://(?:[^/@]+@)?github\.com/|git@github\.com:)', url))


def blockers(repo, branch=None):
    """Find local conditions that prevent a safe Git update."""
    current = git(repo, 'symbolic-ref', '-q', '--short', 'HEAD')
    if branch is not None and current != branch:
        return f'checked-out branch is {current}; required default branch is {branch}; not updated'
    for name in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer', 'BISECT_START', 'index.lock'):
        path = Path(git(repo, 'rev-parse', '--git-path', name))
        if not path.is_absolute():
            path = repo / path
        if path.exists():
            return f'Git operation or lock present: {name}'
    if git(repo, 'status', '--porcelain', '--untracked-files=normal'):
        return 'local changes or untracked files'
    return None


def optional(repo, *args):
    """Read optional Git data. Return an empty string if the command fails."""
    try:
        return git(repo, *args)
    except RuntimeError:
        return ''


def update_in_worktree(repo, branch, metadata):
    """Update the default branch. Keep the active development checkout unchanged."""
    target = f'refs/remotes/origin/{branch}'
    git(repo, 'fetch', '--no-tags', '--no-recurse-submodules', 'origin',
        f'+refs/heads/{branch}:{target}', retry=True)
    base = STATE_DIR / 'worktrees'
    base.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix='checkout-', dir=base))
    checkout = directory / 'repo'
    previous = metadata['branch']
    exists = optional(repo, 'show-ref', '--verify', f'refs/heads/{branch}')
    args = ('worktree', 'add', str(checkout), branch) if exists else (
        'worktree', 'add', '--track', '-b', branch, str(checkout), target)
    added = False
    try:
        git(repo, '-c', 'core.hooksPath=/dev/null', *args)
        added = True
        result = update(checkout, False, metadata)
        metadata['preserved_branch'] = previous
        return result
    finally:
        if added:
            # Do not force removal. Keep unexpected local files.
            git(repo, 'worktree', 'remove', str(checkout))
        if not checkout.exists():
            directory.rmdir()


def update(repo, dry_run, metadata=None):
    """Update a default branch. Keep local development work.

    Args:
        repo: Path to a Git working directory.
        dry_run: Examine update readiness. Do not fetch or change branches.
        metadata: Mutable report fields populated during the check.

    Returns:
        A status and a diagnostic description. Git failures raise RuntimeError.
    """
    metadata = metadata if metadata is not None else {}
    origin = optional(repo, 'remote', 'get-url', 'origin')
    metadata['branch'] = optional(repo, 'symbolic-ref', '-q', '--short', 'HEAD') or 'detached/unborn'
    match_url = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', origin)
    if match_url:
        metadata['url'] = 'https://github.com/' + match_url[1] + '/' + match_url[2]
    if not github_origin(origin):
        return 'SKIP', 'excluded: origin is not GitHub'
    # Ask the server for its current default branch. Do not assume main.
    remote = git(repo, 'ls-remote', '--symref', 'origin', 'HEAD', retry=True)
    match = re.search(r'^ref: refs/heads/(.+)\tHEAD$', remote, re.M)
    if not match:
        heads = git(repo, 'ls-remote', '--heads', 'origin', retry=True)
        if not heads:
            return 'SKIP', 'excluded: remote has no branches or code to update'
        return 'ERROR', 'remote has branches but no default branch'
    if not optional(repo, 'symbolic-ref', '-q', '--short', 'HEAD'):
        return 'ERROR', 'detached or unborn HEAD'
    branch = match[1]
    metadata['default_branch'] = branch
    # Missing config keys are normal; git config exits 1 for them.
    if optional(repo, 'config', '--get', 'core.sparseCheckout') == 'true':
        return 'ERROR', 'sparse checkout'
    reason = blockers(repo)
    if metadata['branch'] != branch:
        if reason and reason != 'local changes or untracked files':
            return 'ERROR', reason
        if dry_run:
            return 'READY', f'would update {branch} in a temporary worktree. Keep {metadata["branch"]} and its local files'
        return update_in_worktree(repo, branch, metadata)
    if reason:
        return 'ERROR', reason
    if dry_run:
        return 'READY', f'would fetch and fast-forward {branch}'
    target = f'refs/remotes/origin/{branch}'
    git(repo, 'fetch', '--no-tags', '--no-recurse-submodules', 'origin',
        f'+refs/heads/{branch}:{target}', retry=True)
    reason = blockers(repo, branch)
    if reason:
        return 'ERROR', reason
    behind, ahead = map(int, git(repo, 'rev-list', '--left-right', '--count', f'{target}...HEAD').split())
    metadata['ahead'] = ahead
    metadata['behind'] = behind
    if ahead:
        return 'ERROR', f'{ahead} local commits, {behind} remote commits; manual review required'
    if not behind:
        return 'CURRENT', branch
    before = git(repo, 'rev-parse', 'HEAD')
    after = git(repo, 'rev-parse', target)
    if metadata.get('url'):
        metadata['compare'] = metadata['url'] + '/compare/' + before + '...' + after
    metadata['commits'] = behind
    git(repo, '-c', 'core.hooksPath=/dev/null', 'merge', '--ff-only', '--no-edit', target)
    return 'UPDATED', f'{branch}: {behind} commits (submodules and LFS downloads are not updated)'


def main():
    """Read command arguments and start the selected local operation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(load_settings()['root']).expanduser())
    parser.add_argument('--dry-run', action='store_true', help='Examine readiness. Do not fetch or change checkouts')
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error('The repository root is not a directory.')
    state = STATE_DIR
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / 'lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Another updater is running.', flush=True)
            return 0
        counts = collections.Counter()
        for repo in sorted(args.root.iterdir()):
            if repo.is_symlink() or not repo.is_dir() or not (repo / '.git').exists():
                continue
            metadata = {'folder': repo.name}
            if (repo / '.no-auto-update').exists():
                status, detail = 'SKIP', 'excluded: .no-auto-update exists'
            else:
                try:
                    status, detail = update(repo, args.dry_run, metadata)
                except Exception as error:
                    status, detail = 'ERROR', str(error)
            detail = redact(detail)
            metadata['diagnostics'] = detail
            counts[status] += 1
            print('META ' + json.dumps(metadata), flush=True)
            print(f'{status} {repo.name}: {detail.replace(chr(10), " | ")}', flush=True)
        print('Summary: ' + ', '.join(f'{key}={value}' for key, value in sorted(counts.items())), flush=True)
        return int(bool(counts['ERROR']))


if __name__ == '__main__':
    os.umask(0o077)
    sys.exit(main())
