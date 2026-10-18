"""Examine local behavior without private data or network mail delivery."""
import tempfile
import os
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from devwarden import report


class ReportTest(unittest.TestCase):
    """Examine repository and report behavior with isolated test data."""
    def setUp(self):
        """Keep user mail environment settings out of isolated tests."""
        keys = ('host', 'port', 'security', 'sender', 'recipient', 'username', 'password')
        clean = {'DEVWARDEN_SMTP_' + key.upper(): '' for key in keys}
        environment = patch.dict(os.environ, clean)
        environment.start()
        self.addCleanup(environment.stop)

    def test_starttls_precedes_authentication(self):
        """Make sure that STARTTLS occurs before SMTP authentication."""
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / 'smtp.json'
            config.write_text(json.dumps(dict(sender='test@example.com', recipient='reader@example.com', username='test@example.com', password='test-only', host='smtp.example.com', port=587, security='starttls')))
            with patch.object(report, 'CONFIG', config), patch.object(report.smtplib, 'SMTP') as smtp:
                report.send('Test', 'Body')
                client = smtp.return_value.__enter__.return_value
                names = [call[0] for call in client.method_calls]
                self.assertLess(names.index('starttls'), names.index('login'))
                message = client.send_message.call_args.args[0]
                self.assertEqual(message['To'], 'reader@example.com')
                self.assertTrue(message.is_multipart())

    def test_invalid_mail_settings_rejected(self):
        """Make sure that invalid mail settings cause an error."""
        with self.assertRaises(ValueError):
            report.validate_mail(dict(sender='a@example.com\nBcc: x@example.com', recipient='b@example.com', host='smtp.example.com', port=465, security='ssl'))

    def test_diagnostic_columns_and_compare_links(self):
        """Examine the diagnostic columns and the links to GitHub changes."""
        record = {'folder': 'example', 'branch': 'main', 'default_branch': 'main',
                  'url': 'https://github.com/owner/example', 'ahead': 75, 'behind': 175,
                  'diagnostics': '75 local commits, 175 remote commits; manual review required'}
        body = 'META ' + json.dumps(record) + '\nERROR example: ' + record['diagnostics'] + '\nSummary: ERROR=1\n'
        text, html = report.format_report(body)
        for label in ('Branch (current → default)', 'Reason', 'Diagnostics', 'Suggested action'):
            self.assertIn(label, html)
        self.assertIn('Ahead: 75; behind: 175', text)
        self.assertIn('href="https://github.com/owner/example"', html)
        self.assertNotIn('META ', html)
        record.update(commits=3, compare='https://github.com/owner/example/compare/abc123...def456')
        body = 'META ' + json.dumps(record) + '\nUPDATED example: main: 3 commits\nSummary: UPDATED=1\n'
        text, html = report.format_report(body)
        self.assertIn('Commits added', html)
        self.assertIn('View changes</a>', html)

    def test_report_groups_results_and_escapes_html(self):
        """Examine report groups and HTML escaping."""
        body = ('DevWarden on example-host\nService result: success\n'
                'CURRENT current-repo: main\n'
                'UPDATED updated-repo: main: 1 commits (submodules and LFS downloads are not updated)\n'
                'SKIP skipped-repo: local changes <keep>\n'
                'ERROR failed-repo: permission denied\n'
                'Summary: CURRENT=1, SKIP=1, UPDATED=1, ERROR=1\n')
        text, html = report.format_report(body)
        self.assertLess(text.index('Errors —'), text.index('Updated repositories'))
        self.assertIn('Excluded from updates (1)', text)
        self.assertIn('main: 1 commit', text)
        self.assertNotIn('Summary:', text)
        self.assertNotIn('CURRENT current-repo', text)
        self.assertIn('&lt;keep&gt;', html)
        self.assertNotIn('<keep>', html)
        self.assertIn('Action needed', report.report_subject(body))
        partial, _ = report.format_report(body.rsplit('Summary:', 1)[0])
        self.assertIn('Run did not finish', partial)

    def test_authentication_waits_for_server_challenge(self):
        """Make sure that authentication waits for the SMTP server challenge."""
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / 'gmail.json'
            config.write_text(json.dumps(dict(sender='test@example.com', recipient='reader@example.com', username='test@example.com', password='test-only', host='smtp.example.com', port=465, security='ssl')))
            with patch.object(report, 'CONFIG', config), patch.object(report.smtplib, 'SMTP_SSL') as smtp:
                report.send('Test', 'Body')
                client = smtp.return_value.__enter__.return_value
                client.login.assert_called_once_with('test@example.com', 'test-only', initial_response_ok=False)
                client.send_message.assert_called_once()

    def test_failed_run_and_failed_delivery_are_preserved(self):
        """Make sure that delivery errors do not remove the run log or queued report."""
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            log = state / 'run.log'
            log.write_text('ERROR example: network unavailable\n')
            (state / 'current-log').write_text(str(log))
            config = state / 'gmail.json'
            config.write_text(json.dumps(dict(sender='test@example.com', recipient='reader@example.com')))
            with patch.object(report, 'STATE', state), patch.object(report, 'CONFIG', config), patch.dict('os.environ', {'SERVICE_RESULT': 'timeout', 'EXIT_STATUS': '15'}):
                with patch.object(report, 'send', side_effect=OSError('offline')):
                    with self.assertRaises(OSError):
                        report.report()
                self.assertIn('Service result: timeout', (state / 'latest-report.txt').read_text())
                self.assertIn('- example: network unavailable', (state / 'latest-report.txt').read_text())
                self.assertEqual(len(list((state / 'outbox').glob('*.txt'))), 1)
                with patch.object(report, 'send') as send:
                    self.assertEqual(report.flush(), 0)
                    send.assert_called_once()
                self.assertEqual(list((state / 'outbox').glob('*.txt')), [])
                self.assertTrue(log.exists())


if __name__ == '__main__':
    unittest.main()
