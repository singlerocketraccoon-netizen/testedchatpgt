import sys,asyncio,json,threading
from engines7 import launch
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1'
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/docs/scheme2/d1/'
async def main():
 rows=[]
 async with async_playwright()as p:
  for engine in ['chromium','firefox','webkit']:
   b=await launch(p,engine)
   for w in[360,390]:
    page=await b.new_page(viewport={'width':w,'height':844},reduced_motion='reduce')
    for path in ['index.html','otdyh/otdyh-s-detmi/index.html','napravleniya/egipet/index.html']:
     await page.goto(BASE+path);await page.evaluate('document.fonts.ready');await page.evaluate('scrollTo(0,2100)');await page.wait_for_timeout(100);box=page.locator('[data-mobile-contact]');assert await box.is_visible(),(engine,w,path)
     value=await box.evaluate('''e=>({height:e.getBoundingClientRect().height,buttons:[...e.querySelectorAll('.btn')].map(b=>({t:b.textContent.trim(),font:parseFloat(getComputedStyle(b).fontSize),h:b.getBoundingClientRect().height,w:b.getBoundingClientRect().width,over:b.scrollWidth-b.clientWidth}))})''');assert value['height']<=64 and all(v['font']>=16 and v['h']>=44 and v['w']>=44 and v['over']<=1 for v in value['buttons']),(engine,w,path,value)
     rows.append(dict(engine=engine,width=w,path=path,**value))
    await page.close()
   await b.close()
 (S/'STAGE7_PANELS_QA.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print('Passed',len(rows),'panel states')
asyncio.run(main());server.shutdown()
