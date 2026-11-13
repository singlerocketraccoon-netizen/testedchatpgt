#!/usr/bin/env python3
"""Run current stage-11 acceptance and dialog/control checks."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ['check11.py','controls11.py']:
 subprocess.run([sys.executable,str(root/script)],check=True)
