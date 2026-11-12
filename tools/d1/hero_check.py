#!/usr/bin/env python3
"""Require 24 px between every slide heading and description, at each viewport."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import asyncio,json,threading
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2];SITE=ROOT/'docs/scheme2/d1'
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
async def run():
 rows=[]
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width,height in [(360,844),(768,900),(1280,900),(1440,900),(360,640)]:
   page=await b.new_page(viewport={'width':width,'height':height},reduced_motion='reduce');await page.goto(f'http://127.0.0.1:{server.server_port}/docs/scheme2/d1/index.html');await page.evaluate('document.fonts.ready');positions=[]
   for i in range(4):
    await page.evaluate('scrollTo(0,0)')
    r=await page.locator('.hero-slide.is-active .hero-copy').evaluate("e=>{const h=e.querySelector('h1,h2').getBoundingClientRect(),p=e.querySelector('p:not(.hero-accent)').getBoundingClientRect(),a=e.querySelector('.hero-accent').getBoundingClientRect(),b=e.querySelector('.btn').getBoundingClientRect();return{gap:p.top-h.bottom,button:b.top,accent:a.top,header:document.querySelector('header').getBoundingClientRect().bottom}}")
    assert r['gap']>=24-.01,(width,height,i+1,r);assert r['accent']>r['header'],(width,height,i+1,r);positions.append(r['button']);rows.append({'width':width,'height':height,'slide':i+1,**r});await page.locator('[data-hero-next]').click()
   assert max(positions)-min(positions)<1,(width,height,positions);await page.close()
  await b.close()
 (SITE/'STAGE7_HERO_QA.json').write_text(json.dumps({'minimum_gap':24,'measurements':rows},ensure_ascii=False,indent=2)+'\n');print('Passed',len(rows),'slide measurements')
try:asyncio.run(run())
finally:server.shutdown()
