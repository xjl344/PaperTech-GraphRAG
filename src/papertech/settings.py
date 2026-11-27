"""Explicit project-local settings; never log the environment or secret values."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def settings(root=ROOT):
    values = {}
    template = root / '.env.example'
    for path in (template, root / '.env'):
        if not path.exists():
            continue
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return {key: os.environ.get(key, value) for key, value in values.items()}
