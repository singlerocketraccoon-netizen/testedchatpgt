"""Development-only browser launch helpers; no browser code reaches the site."""
from pathlib import Path
import os
if Path('/tmp/pw7').exists():os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH','/tmp/pw7')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/mango-browser-cache')
async def launch(p,name):
 if name=='chromium':return await p.chromium.launch(executable_path='/usr/bin/chromium'if Path('/usr/bin/chromium').exists()else None,args=['--no-sandbox','--disable-dev-shm-usage'])
 if name=='firefox':return await p.firefox.launch(timeout=20000,firefox_user_prefs={'security.sandbox.content.level':0,'gfx.webrender.force-disabled':True,'layers.acceleration.disabled':True})
 return await p.webkit.launch(timeout=20000)
