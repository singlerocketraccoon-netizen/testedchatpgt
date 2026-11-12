#!/usr/bin/env python3
"""Run current design 1 acceptance, slide geometry and contrast checks (stage 8)."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ['check8.py','hero_check.py','contrast5.py','panels7.py']:
 subprocess.run([sys.executable,str(root/script)],check=True)
