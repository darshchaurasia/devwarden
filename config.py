"""Read user settings and select private storage paths."""
import json
import os
import shlex
from pathlib import Path


def user_path(variable, fallback):
    """Return an absolute path from an environment variable or fallback."""
    return Path(os.environ.get(variable, fallback)).expanduser().resolve()


CONFIG_DIR = user_path('DEVWARDEN_CONFIG_DIR', Path.home() / '.config/devwarden')
STATE_DIR = user_path('DEVWARDEN_STATE_DIR', Path.home() / '.local/state/devwarden')
SETTINGS = CONFIG_DIR / 'settings.json'
SMTP = CONFIG_DIR / 'smtp.json'


def read_env(path):
    """Read literal KEY=VALUE entries without shell execution or expansion."""
    values = {}
    if not path.exists():
        return values
    for number, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        key, separator, value = line.partition('=')
        if not separator or not key.startswith('DEVWARDEN_') or not key.replace('_', '').isalnum():
            raise ValueError(f'Invalid environment entry on line {number}.')
        parts = shlex.split(value, comments=True)
        if len(parts) > 1:
            raise ValueError(f'Quote values with spaces on line {number}.')
        values[key] = parts[0] if parts else ''
    return values


LOCAL_ENV = Path(__file__).resolve().parent / '.env'
ENV_FILE = LOCAL_ENV if LOCAL_ENV.exists() else CONFIG_DIR / '.env'
for _key, _value in read_env(ENV_FILE).items():
    os.environ.setdefault(_key, _value)


def load_settings():
    """Read settings without creating files or using personal defaults."""
    settings = json.loads(SETTINGS.read_text()) if SETTINGS.exists() else {}
    if not isinstance(settings, dict):
        raise ValueError('Settings must be a JSON object.')
    settings.setdefault('root', str(Path.home() / 'code'))
    settings.setdefault('calendar', 'Fri *-*-* 06:00:00')
    settings.setdefault('retention_days', 90)
    for key in ('root', 'calendar', 'retention_days'):
        value = os.environ.get('DEVWARDEN_' + key.upper())
        if value:
            settings[key] = int(value) if key == 'retention_days' else value
    if not isinstance(settings.get('retention_days'), int) or settings['retention_days'] < 1:
        raise ValueError('Retention days must be a positive integer.')
    if not isinstance(settings, dict) or not isinstance(settings.get('root'), str):
        raise ValueError('Settings must contain a repository root path.')
    return settings


def save_private(path, value):
    """Write a JSON file atomically with access restricted to its owner."""
    import tempfile
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.settings-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def mail_settings(path=SMTP):
    """Combine private SMTP settings with nonempty environment overrides."""
    values = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(values, dict):
        raise ValueError('SMTP settings must be a JSON object.')
    for key in ('host', 'port', 'security', 'sender', 'recipient', 'username', 'password'):
        value = os.environ.get('DEVWARDEN_SMTP_' + key.upper())
        if value:
            values[key] = int(value) if key == 'port' else value
    if not values.get('sender') and not values.get('recipient'):
        return None
    values.setdefault('host', 'smtp.gmail.com')
    values.setdefault('port', 465)
    values.setdefault('security', 'ssl')
    values.setdefault('username', values.get('sender', ''))
    return values
