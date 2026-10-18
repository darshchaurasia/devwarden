#!/usr/bin/env python3
"""Install and control the repository update service for the current user."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from config import CONFIG_DIR, ENV_FILE, SETTINGS, SMTP, STATE_DIR, load_settings, read_env, save_private

SOURCE = Path(__file__).resolve().parent
APP = Path.home() / '.local/share/devwarden'
BIN = Path.home() / '.local/bin/devwarden'
UNITS = Path.home() / '.config/systemd/user'
UNIT_NAMES = ('devwarden.service', 'devwarden.timer',
              'devwarden-mail.service', 'devwarden-mail.timer')


def command(*args):
    """Run a command and stop if it fails."""
    return subprocess.run(args, check=True)


def unit_argument(value):
    """Quote one systemd argument without shell expansion."""
    if any(char in str(value) for char in '\n\r\x00'):
        raise ValueError('Unit paths must not contain newlines or null bytes.')
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%').replace('$', '$$') + '"'


def install(args):
    """Install runtime files and user units without copying credentials."""
    if not shutil.which('git') or not shutil.which('systemctl'):
        raise RuntimeError('Install Git and start a systemd user session first.')
    subprocess.run(['systemctl', '--user', 'show-environment'], check=True, capture_output=True)
    settings = load_settings()
    root = args.root or settings['root']
    calendar = args.calendar or settings['calendar']
    if not args.yes:
        root = input(f'Repository root [{root}]: ').strip() or root
        calendar = input(f'Calendar schedule [{calendar}]: ').strip() or calendar
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('The repository root must exist.')
    if any(char in calendar for char in '\n\r\x00'):
        raise ValueError('The schedule must be one line.')
    command('systemd-analyze', 'calendar', calendar)
    active = subprocess.run(['systemctl', '--user', 'show', 'devwarden.service',
                             '-p', 'ActiveState', '--value'], capture_output=True, text=True).stdout.strip()
    if active in ('active', 'activating', 'deactivating'):
        raise RuntimeError('Wait for the current updater run to finish before installation.')
    settings.update(root=str(root), calendar=calendar)
    save_private(SETTINGS, settings)
    STATE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    STATE_DIR.chmod(0o700)
    values = read_env(ENV_FILE)
    values.update(DEVWARDEN_ROOT=str(root), DEVWARDEN_CALENDAR=calendar)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    content = '# Private local settings. Do not commit this file.\n'
    content += ''.join(key + '=' + json.dumps(value) + '\n' for key, value in sorted(values.items()))
    private_env = CONFIG_DIR / '.env'
    private_env.write_text(content)
    private_env.chmod(0o600)
    # Keep legacy credentials in user storage; never copy them to the project.
    legacy = CONFIG_DIR / 'gmail.json'
    if legacy.exists() and not SMTP.exists():
        value = json.loads(legacy.read_text())
        save_private(SMTP, dict(host='smtp.gmail.com', port=465, security='ssl',
                               sender=value['sender'], recipient=value['sender'],
                               username=value['sender'], password=value['password']))
    APP.mkdir(parents=True, exist_ok=True, mode=0o700)
    for name in ('config.py', 'update.py', 'report.py', 'manage.py', *UNIT_NAMES):
        if SOURCE != APP:
            shutil.copy2(SOURCE / name, APP / name)
    BIN.parent.mkdir(parents=True, exist_ok=True)
    BIN.write_text('#!/usr/bin/env python3\nimport sys\nsys.path.insert(0, ' + repr(str(APP)) + ')\nfrom manage import main\nmain()\n')
    BIN.chmod(0o700)
    replacements = {'@PYTHON@': unit_argument(sys.executable),
                    '@APP@': unit_argument(str(APP)), '@CALENDAR@': calendar,
                    '@STATE@': unit_argument(str(STATE_DIR / 'current-log')),
                    '@CONFIG_ENV@': unit_argument('DEVWARDEN_CONFIG_DIR=' + str(CONFIG_DIR)),
                    '@STATE_ENV@': unit_argument('DEVWARDEN_STATE_DIR=' + str(STATE_DIR))}
    UNITS.mkdir(parents=True, exist_ok=True)
    for name in UNIT_NAMES:
        text = (APP / name).read_text()
        # Paths are inserted as individual quoted arguments, not shell commands.
        text = text.replace('@SCRIPT@', unit_argument(str(APP / 'report.py')))
        for key, value in replacements.items():
            text = text.replace(key, value)
        (UNITS / name).write_text(text)
    command('systemd-analyze', '--user', 'verify', *(str(UNITS / name) for name in UNIT_NAMES))
    command('systemctl', '--user', 'daemon-reload')
    command('systemctl', '--user', 'enable', '--now', 'devwarden.timer', 'devwarden-mail.timer')
    command('systemctl', '--user', 'restart', 'devwarden.timer', 'devwarden-mail.timer')
    print('Installed. Run ~/.local/bin/devwarden doctor to check the service.')


def doctor():
    """Show prerequisites and service state without printing secrets."""
    from config import mail_settings
    print('Python:', sys.version.split()[0])
    print('Git:', shutil.which('git') or 'not found')
    settings = load_settings()
    print('Repository root exists:', Path(settings['root']).expanduser().is_dir())
    print('Private configuration:', CONFIG_DIR)
    print('Email:', 'configured; run email-test to verify' if mail_settings() else 'off; local reports only')
    command('systemctl', '--user', 'list-timers', 'devwarden*', '--no-pager')
    subprocess.run(['loginctl', 'show-user', str(os.getuid()), '-p', 'Linger'], check=False)


def uninstall():
    """Remove the service and runtime but retain private settings and reports."""
    command('systemctl', '--user', 'disable', '--now', 'devwarden.timer', 'devwarden-mail.timer')
    command('systemctl', '--user', 'stop', 'devwarden.service', 'devwarden-mail.service')
    for name in UNIT_NAMES:
        (UNITS / name).unlink(missing_ok=True)
    command('systemctl', '--user', 'daemon-reload')
    BIN.unlink(missing_ok=True)
    if APP.exists():
        shutil.rmtree(APP)
    print('Removed the service. Private settings and reports were retained.')


def main():
    """Dispatch the public command interface."""
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    setup = sub.add_parser('setup', help='Install or update the user service')
    setup.add_argument('--root')
    setup.add_argument('--calendar')
    setup.add_argument('--yes', action='store_true', help='Use settings without prompts')
    for name in ('run', 'preview', 'status', 'logs', 'doctor', 'email-configure', 'email-test', 'email-retry', 'uninstall'):
        sub.add_parser(name)
    args = parser.parse_args()
    try:
        if args.action == 'setup':
            install(args)
        elif args.action == 'uninstall':
            uninstall()
        elif args.action == 'doctor':
            doctor()
        elif args.action == 'run':
            command('systemctl', '--user', 'start', '--no-block', 'devwarden.service')
            print('Started the service. Use devwarden logs to read results.')
        elif args.action == 'preview':
            command(sys.executable, str(SOURCE / 'update.py'), '--dry-run')
        elif args.action == 'status':
            command('systemctl', '--user', 'status', 'devwarden.service', '--no-pager')
        elif args.action == 'logs':
            command('journalctl', '--user', '-u', 'devwarden.service', '-u', 'devwarden-mail.service', '-n', '150', '--no-pager')
        else:
            action = {'email-configure': 'configure', 'email-test': 'test', 'email-retry': 'flush'}[args.action]
            command(sys.executable, str(SOURCE / 'report.py'), action)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
