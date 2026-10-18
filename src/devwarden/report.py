#!/usr/bin/env python3
"""Save update reports and deliver them through a configured SMTP account."""
import argparse
from datetime import datetime
from email.message import EmailMessage
import getpass
import fcntl
import json
import re
from html import escape
import os
from pathlib import Path
import smtplib
import ssl
import subprocess
import sys

from .config import SMTP, STATE_DIR, load_settings, mail_settings, save_private

STATE = STATE_DIR
CONFIG = SMTP


def configure():
    """Collect mail settings without placing secrets in command arguments."""
    sender = input('Sending email address: ').strip()
    recipient = input('Report recipient (Enter to use sender): ').strip() or sender
    host = input('SMTP host [smtp.gmail.com]: ').strip() or 'smtp.gmail.com'
    security = input('TLS mode: ssl or starttls [ssl]: ').strip() or 'ssl'
    port = int(input(f'SMTP port [{465 if security == "ssl" else 587}]: ').strip() or (465 if security == 'ssl' else 587))
    username = input('SMTP username (Enter to use sender): ').strip() or sender
    password = getpass.getpass('SMTP password or app password (hidden): ')
    if host == 'smtp.gmail.com':
        password = password.replace(' ', '')
    value = dict(sender=sender, recipient=recipient, host=host, port=port,
                 security=security, username=username, password=password)
    validate_mail(value)
    save_private(CONFIG, value)
    print('Saved private SMTP settings. Use devwarden email-test to test delivery.')


def validate_mail(value):
    """Reject invalid addresses and transport settings before use."""
    for key in ('sender', 'recipient'):
        address = value.get(key, '')
        if not isinstance(address, str) or not re.fullmatch(r'[^\s<>@]+@[^\s<>@]+', address):
            raise ValueError(f'Enter one valid {key} email address.')
    if value.get('security') not in ('ssl', 'starttls'):
        raise ValueError('SMTP requires ssl or starttls.')
    if not isinstance(value.get('port'), int) or not 1 <= value['port'] <= 65535:
        raise ValueError('SMTP port must be between 1 and 65535.')
    if not isinstance(value.get('host'), str) or not value['host'] or any(c.isspace() for c in value['host']):
        raise ValueError('Enter an SMTP host name.')


def error_guidance(detail):
    """Select a reason and recovery action with local text rules."""
    rules = [
        ('local commits', 'Local history differs from remote', 'Examine the local and remote commits. Keep local work before you change either history.'),
        ('checked-out branch', 'Different branch checked out', 'Finish your work. Switch to the default branch. Start the updater again.'),
        ('local changes', 'Uncommitted changes', 'Examine your changes. Save them in a commit or a Git stash. Start the updater again.'),
        ('default branch', 'Default branch unavailable', 'Examine the remote URL. Find the default branch on GitHub. An empty repository has no branch to update.'),
        ('detached or unborn', 'No checked-out branch', 'Keep local work first. Use git switch to select the default branch.'),
        ('Git operation or lock', 'Git operation or lock present', 'Examine the Git operation. Finish it if possible. Before you remove a stale lock, make sure its Git process has stopped.'),
        ('sparse checkout', 'Sparse checkout enabled', 'Examine the sparse checkout settings. Update the repository manually if necessary.'),
        ('timed out', 'Git command timed out', 'Examine the network connection and remote access. Start the updater again.'),
        ('Authentication', 'Authentication failed', 'Use gh auth status to examine the GitHub login. Make sure the Git credentials can access the repository.'),
        ('Permission denied', 'Access denied', 'Examine the GitHub credentials and repository permissions.'),
        ('Repository not found', 'Repository unavailable', 'Examine the origin URL. Make sure your account can access the repository.'),
        ('Could not resolve', 'DNS lookup failed', 'Examine the internet connection and DNS settings. Start the updater again.'),
    ]
    for needle, reason, action in rules:
        if needle.lower() in detail.lower():
            return reason, action
    return 'Update could not be completed', 'Examine the diagnostics and saved log. Correct the problem. Start the updater again.'


def table_columns(status, detail, metadata):
    """Build report columns from saved run metadata."""
    branch = metadata.get('branch', 'Not recorded')
    if metadata.get('preserved_branch'):
        branch += ' (default branch updated. Checkout stays on ' + metadata['preserved_branch'] + ')'
    if metadata.get('switched_from'):
        branch += ' (switched from ' + metadata['switched_from'] + ')'
    default = metadata.get('default_branch', 'Unknown')
    if status == 'ERROR':
        reason, action = error_guidance(detail)
        diagnostics = metadata.get('diagnostics', detail)
        if 'ahead' in metadata:
            diagnostics = f"Ahead: {metadata['ahead']}; behind: {metadata['behind']}. " + diagnostics
        return ['Branch (current → default)', 'Reason', 'Diagnostics', 'Suggested action'], [f'{branch} → {default}', reason, diagnostics, action]
    if status == 'UPDATED':
        match = re.match(r'(.+?): (\d+) commits?', detail)
        return ['Branch', 'Commits added', 'Changes'], [branch if metadata.get('branch') else (match[1] if match else branch), str(metadata.get('commits', match[2] if match else 'Not recorded')), metadata.get('compare', 'Not recorded')]
    if status == 'CURRENT':
        return ['Branch'], [branch if metadata.get('branch') else detail]
    return ['Reason' if status == 'SKIP' else 'Details'], [detail]


def html_value(value, label=None):
    """Escape a value or create a link to a validated GitHub URL."""
    if re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/compare/[0-9a-f]+\.\.\.[0-9a-f]+)?', value):
        return '<a href="' + escape(value, quote=True) + '">' + escape(label or value) + '</a>'
    return escape(value)


def result_match(line):
    """Read one repository result. Exclude explanations in the report header."""
    if line.startswith(('SKIP entries ', 'ERROR entries ')):
        return None
    return re.match(r'^(ERROR|SKIP|UPDATED|CURRENT|READY) (.+?): (.*)$', line)


def format_report(body):
    """Build grouped text and HTML reports from recorded results."""
    groups = {key: [] for key in ('ERROR', 'SKIP', 'UPDATED', 'CURRENT', 'READY')}
    extra = []
    metadata = {}
    for line in body.splitlines():
        if line.startswith('META '):
            try:
                record = json.loads(line[5:])
                metadata[record['folder']] = record
            except (ValueError, KeyError, TypeError):
                extra.append('The repository metadata cannot be read. Examine the raw log.')
            continue
        match = result_match(line)
        if match:
            status, name, detail = match.groups()
            detail = detail.replace(' (submodules and LFS downloads are not updated)', '')
            detail = re.sub(r'\b1 commits\b', '1 commit', detail)
            groups[status].append((name, detail))
        elif line and not line.startswith(('DevWarden', 'Time:', 'Service result:', 'Exit status:', 'Summary:', 'SKIP entries', 'ERROR entries')):
            extra.append(line)
    if not any(groups.values()):
        return body, '<pre style="white-space:pre-wrap">' + escape(body) + '</pre>'
    run_details = [line for line in body.splitlines() if line.startswith(('DevWarden on ', 'Time:', 'Service result:', 'Exit status:'))]
    complete = any(line.startswith('Summary:') for line in body.splitlines())
    summary = (f"{len(groups['UPDATED'])} updated · {len(groups['CURRENT'])} already current · "
               f"{len(groups['SKIP'])} excluded · {len(groups['ERROR'])} errors")
    text = ['DEVWARDEN UPDATE REPORT', summary, '', *run_details]
    html = ['<html><body style="font-family:Arial,sans-serif;color:#202124;max-width:900px;margin:24px auto;padding:16px">',
            '<h1 style="font-size:24px">DevWarden update report</h1>',
            '<p style="padding:16px;background:#eef3f8;border-radius:8px;font-size:16px">' + escape(summary) + '</p>',
            '<p style="color:#5f6368;line-height:1.6">' + '<br>'.join(escape(line) for line in run_details) + '</p>']
    if not complete:
        warning = 'Run did not finish. Counts include only the results recorded before the stop.'
        text.extend(['', warning])
        html.append('<p style="color:#b3261e"><strong>' + warning + '</strong></p>')
    sections = [('ERROR', 'Errors — action required'), ('SKIP', 'Excluded from updates'),
                ('UPDATED', 'Updated repositories'), ('CURRENT', 'Already up to date'), ('READY', 'Ready for update')]
    for status, title in sections:
        rows = groups[status]
        if not rows and status == 'READY':
            continue
        heading = f'{title} ({len(rows)})'
        text.extend(['', heading, '-' * len(heading)])
        html.append('<h2 style="font-size:18px;margin-top:28px">' + escape(heading) + '</h2>')
        if not rows:
            text.append('None.')
            html.append('<p>None.</p>')
            continue
        columns, _ = table_columns(status, rows[0][1], metadata.get(rows[0][0], {}))
        headers = ['Repository', *columns]
        html.append('<div style="overflow-x:auto"><table style="border-collapse:collapse;width:100%;font-size:14px"><tr>' + ''.join('<th style="text-align:left;padding:8px;border-bottom:2px solid #dadce0">' + escape(header) + '</th>' for header in headers) + '</tr>')
        for name, detail in rows:
            record = metadata.get(name, {})
            columns, values = table_columns(status, detail, record)
            text.append(f'- {name}: {detail}')
            if record.get('url'):
                text.append('  Repository: ' + record['url'])
            text.extend('  ' + key + ': ' + value for key, value in zip(columns, values))
            cells = [html_value(record.get('url', name), name)]
            cells.extend(html_value(value, 'View changes' if key == 'Changes' else None) for key, value in zip(columns, values))
            html.append('<tr>' + ''.join('<td style="padding:8px;border-bottom:1px solid #eee;vertical-align:top;white-space:pre-wrap;overflow-wrap:anywhere">' + cell + '</td>' for cell in cells) + '</tr>')
        html.append('</table></div>')
    if extra:
        text.extend(['', 'Additional diagnostics', *extra])
        html.append('<h2 style="font-size:18px">Additional diagnostics</h2><pre style="white-space:pre-wrap">' + escape('\n'.join(extra)) + '</pre>')
    note = ('The updater keeps local changes and commits. '
            'A development checkout stays on its branch with its local files. '
            'The updater updates the default branch in a different temporary worktree. '
            'The updater does not automatically reset branches or create a Git stash. '
            'It does not update submodules, LFS objects, or dependencies.')
    text.extend(['', 'Notes', note])
    html.append('<p style="margin-top:28px;color:#5f6368;font-size:12px">' + escape(note) + '</p></body></html>')
    return '\n'.join(text) + '\n', ''.join(html)


def report_subject(body):
    """Summarize recorded results in an email subject."""
    counts = dict.fromkeys(('UPDATED', 'SKIP', 'ERROR'), 0)
    for line in body.splitlines():
        match = result_match(line)
        if match and match[1] in counts:
            counts[match[1]] += 1
    incomplete = not any(line.startswith('Summary:') for line in body.splitlines())
    label = 'Run incomplete' if incomplete else ('Action needed' if counts['ERROR'] else 'Complete')
    return f"[DevWarden] {label} | {counts['UPDATED']} updated, {counts['SKIP']} excluded, {counts['ERROR']} errors"


def send(subject, body):
    """Send text and HTML alternatives over verified SMTP TLS.

    Args:
        subject: Email subject without private authentication data.
        body: Recorded run output used to build both report formats.

    SMTP exceptions propagate so the caller can keep the queued message.
    """
    config = mail_settings(CONFIG)
    if config is None:
        raise ValueError('Email is not configured. Run devwarden email-configure.')
    validate_mail(config)
    message = EmailMessage()
    message['From'] = config['sender']
    message['To'] = config['recipient']
    message['Subject'] = subject
    text, html = format_report(body)
    message.set_content(text)
    message.add_alternative(html, subtype='html')
    context = ssl.create_default_context()
    if config['security'] == 'ssl':
        connection = smtplib.SMTP_SSL(config['host'], config['port'], context=context, timeout=30)
    else:
        connection = smtplib.SMTP(config['host'], config['port'], timeout=30)
    with connection as smtp:
        if config['security'] == 'starttls':
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
        if config.get('username'):
            smtp.login(config['username'], config.get('password', ''), initial_response_ok=False)
        smtp.send_message(message)


def run():
    """Run the updater and save its output before mail delivery."""
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    cutoff = datetime.now().timestamp() - load_settings()['retention_days'] * 86400
    for old_log in STATE.glob('*.log'):
        if old_log.is_file() and old_log.stat().st_mtime < cutoff:
            old_log.unlink()
    stamp = datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%f%z')
    log = STATE / f'{stamp}.log'
    (STATE / 'current-log').write_text(str(log))
    with log.open('w') as output:
        output.write(f'DevWarden started {stamp}\n')
        output.flush()
        with subprocess.Popen([sys.executable, '-u', '-m', 'devwarden.update'],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as child:
            for line in child.stdout:
                output.write(line)
                output.flush()
                print(line, end='', flush=True)
            return child.wait()


def report():
    """Save the final report and queue it for optional delivery."""
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    result = os.environ.get('SERVICE_RESULT', 'unknown')
    pointer = STATE / 'current-log'
    log = Path(pointer.read_text().strip()) if pointer.exists() else None
    content = log.read_text() if log and log.exists() else 'There is no run log. Examine the systemd journal.'
    summary = next((line for line in reversed(content.splitlines()) if line.startswith('Summary:')), 'No summary: the updater possibly stopped before the end.')
    body = (f'DevWarden on {os.uname().nodename}\n'
            f'Time: {datetime.now().astimezone().isoformat()}\nService result: {result}\n'
            f'Exit status: {os.environ.get("EXIT_STATUS", "unknown")}\n{summary}\n\n'
            f'SKIP entries are excluded from the update scope.\n'
            f'ERROR entries need attention: the updater could not make sure that the default branch is current. The updater does not automatically reset branches or create a Git stash.\n\n{content}')
    text, html = format_report(body)
    (STATE / 'latest-report.txt').write_text(text)
    (STATE / 'latest-report.html').write_text(html)
    outbox = STATE / 'outbox'
    outbox.mkdir(exist_ok=True)
    pending = outbox / (datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%f%z') + '.txt')
    # Save before SMTP: failed delivery must leave a message for the retry timer.
    pending.write_text(body)
    return flush()


def flush():
    """Lock the queue before attempting report delivery."""
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (STATE / 'mail.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        return flush_locked()


def flush_locked():
    """Deliver queued reports and keep messages that cannot be sent."""
    if not list((STATE / 'outbox').glob('*.txt')):
        return 0
    if mail_settings(CONFIG) is None:
        print('Local reports saved. Email is not configured.', flush=True)
        return 0
    for pending in sorted((STATE / 'outbox').glob('*.txt')):
        body = pending.read_text()
        send(report_subject(body), body)
        # Remove only after the server accepts the complete message.
        pending.unlink()
        print('SMTP accepted the report.', flush=True)
    return 0


if __name__ == '__main__':
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['configure', 'test', 'run', 'report', 'flush'])
    command = parser.parse_args().command
    try:
        if command == 'test':
            send('[DevWarden] Test notification', 'Email delivery works. Weekly reports will include all repository results.')
            print('SMTP accepted the test email.')
        else:
            sys.exit(globals()[command]() or 0)
    except smtplib.SMTPAuthenticationError:
        print('SMTP authentication failed. Examine the account and password with devwarden email-configure.', file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)
