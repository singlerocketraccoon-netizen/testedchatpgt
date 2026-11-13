#!/usr/bin/env python3
"""Current stage-12 acceptance, including text clipping checks."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for script in ['check12.py','clipping12.py']:
 subprocess.run([sys.executable,str(root/script)],check=True)
