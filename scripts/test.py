#!/usr/bin/env python3
"""Run the complete offline test suite from a source checkout."""
from pathlib import Path
import sys
import unittest

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'src'))

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover(str(PROJECT / 'tests'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
