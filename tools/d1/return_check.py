#!/usr/bin/env python3
"""Catalogue back-navigation and end-form panel checks."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.async_api import async_playwright
import asyncio,json,threading
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1'
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/docs/scheme2/d1/'
async def main():
 report=[]
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in[360,390,1440]:
   page=await b.new_page(viewport={'width':width,'height':844 if width<768 else 900},reduced_motion='reduce');await page.goto(base+'predlozheniya/index.html');await page.locator('[data-offer-filter=egipet]').click();card=page.locator('[data-offers-list] .offer-card:visible a').nth(2);await card.scroll_into_view_if_needed();before=await page.evaluate('scrollY');await card.click();await page.go_back();await page.evaluate('document.fonts.ready');await page.wait_for_timeout(150);after=await page.evaluate('scrollY');assert abs(before-after)<3,(width,before,after);assert await page.locator('[data-offer-filter=egipet]').get_attribute('aria-pressed')=='true'
   await page.goto(base+'index.html');await page.locator('main [data-end-form]').last.scroll_into_view_if_needed();await page.wait_for_timeout(80);assert await page.locator('[data-mobile-contact]').is_hidden();report.append({'width':width,'scroll_before':before,'scroll_after':after,'filter_restored':True,'hidden_at_end_form':True});await page.close()
  await b.close()
 (S/'STAGE6_RETURN_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report)
try:asyncio.run(main())
finally:server.shutdown()
