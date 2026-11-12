#!/usr/bin/env python3
"""Navigation, modal focus and no-JS checks on extra responsive widths."""
import asyncio,json,threading
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2]/'docs/scheme2/d1';result={'page_urls':[],'header_keyboard':[],'dialog_tab_trap':True,'no_js_fieldset_disabled':True,'errors':[]}
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();URL=f'http://127.0.0.1:{server.server_port}/'
async def main():
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in[360,768,1024,1280,1440]:
   print('Extra width',width,flush=True)
   page=await b.new_page(viewport={'width':width,'height':900},reduced_motion='reduce');page.on('pageerror',lambda e:result['errors'].append(str(e)))
   for path in['index.html','napravleniya/vetnam/index.html','uslugi/kruizy/index.html','otdyh/otdyh-s-detmi/index.html','predlozheniya/turkey-antalya/index.html','voprosy/index.html']:
    await page.goto(URL+path);await page.evaluate('document.fonts.ready');assert await page.evaluate('document.documentElement.scrollWidth')==width

    if await page.locator('main [data-request]:not([inert] *)').count():
     await page.locator('main [data-request]:not([inert] *)').first.click();assert await page.locator('#request-dialog').is_visible();await page.keyboard.press('Escape')
    result['page_urls'].append({'width':width,'page':path})
   await page.goto(URL+'index.html')
   if width>=1024:
    nav=page.locator('[aria-controls=nav-work]');await nav.focus();await page.keyboard.press('ArrowDown');assert await page.locator('#nav-work').is_visible();assert await page.locator('#nav-work a').first.evaluate('n=>n===document.activeElement');await page.keyboard.press('Escape');assert await nav.evaluate('n=>n===document.activeElement')
    boxes=await page.evaluate("[...document.querySelectorAll('.nav-about,.header-contacts')].map(n=>{const r=n.getBoundingClientRect();return{x:r.x,right:r.right}})");assert boxes[0]['right']<boxes[1]['x'],(width,boxes)
   else:
    await page.locator('[data-menu]').focus();await page.keyboard.press('Enter');assert await page.locator('#mobile-nav').is_visible();await page.keyboard.press('Escape');assert await page.locator('[data-menu]').evaluate('n=>n===document.activeElement')
   result['header_keyboard'].append(width)
   await page.locator('.hero-slide.is-active [data-quiz-open]').click();await page.locator('#quiz-dialog [data-messenger=Telegram]').focus();await page.keyboard.press('Tab');assert await page.locator('#quiz-dialog [data-dialog-close]').evaluate('n=>n===document.activeElement');await page.keyboard.press('Shift+Tab');assert await page.locator('#quiz-dialog [data-messenger=Telegram]').evaluate('n=>n===document.activeElement');await page.mouse.click(1,1);assert not await page.locator('#quiz-dialog').is_visible();await page.close()
  ctx=await b.new_context(java_script_enabled=False);pg=await ctx.new_page();await pg.goto(URL+'otdyh/otdyh-s-detmi/index.html');assert await pg.locator('[data-form-guard]').first.get_attribute('disabled')is not None;assert await pg.locator('#rest-inquiry-top [name=phone]').is_disabled();await ctx.close();await b.close()
 assert not result['errors'];(R/'STAGE4_EXTRA_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Passed HTTP, header keyboard, tab trap, backdrop and no-JS checks')
try:asyncio.run(main())
finally:server.shutdown()
