#!/usr/bin/env python3
"""Run DevWarden from a source checkout without installing Python packages."""
from pathlib import Path
import sys

# Resolve the checkout path so this launcher works from any current directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from devwarden.cli import main

if __name__ == '__main__':
    main()
