#!/usr/bin/env python3
"""Current stage-13 acceptance and complete responsive matrix."""
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent
for script in ['check13.py', 'check_responsive.py']:
    subprocess.run([sys.executable, str(root / script)], check=True)
