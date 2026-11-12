#!/usr/bin/env python3
"""Run the current design 1 acceptance suite (stage 5)."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ['hero_check.py','check5.py','contrast5.py']:
 subprocess.run([sys.executable,str(root/script)],check=True)
