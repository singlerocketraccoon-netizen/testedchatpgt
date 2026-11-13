#!/usr/bin/env python3
"""Run current design 1 acceptance for the cruise section (stage 10)."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ['check10.py']:
 subprocess.run([sys.executable,str(root/script)],check=True)
