#!/usr/bin/env python3
"""Use the shared generator with the personal edition's asset directory."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    shared = runpy.run_path(str(root / 'shared/scripts/make_sfx.py'))
    shared['main'](default_output=root / 'assets/sfx')
