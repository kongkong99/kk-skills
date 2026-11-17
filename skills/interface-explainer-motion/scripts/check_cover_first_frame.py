#!/usr/bin/env python3
"""Use the bundled shared checker; this adapter is installed by the skill builder."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'shared/scripts/check_cover_first_frame.py'),
                   run_name='__main__')
