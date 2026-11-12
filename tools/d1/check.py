#!/usr/bin/env python3
"""Run current design 1 acceptance, geometry and contrast checks (stage 6)."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ['hero_check.py','check6.py','return_check.py','contrast5.py']:
 subprocess.run([sys.executable,str(root/script)],check=True)
