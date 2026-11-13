"""Acceptance fixtures for 1–6 cards and live visibility changes; development only."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import asyncio,json,threading
from engines7 import launch
from playwright.async_api import async_playwright
async def check(browser,name,base):
 ctx=await browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');p=await ctx.new_page();await p.goto(base+'napravleniya/egipet/index.html');await p.evaluate('document.fonts.ready')
 result=await p.evaluate('''()=>{const host=document.createElement('div');host.className='container';document.querySelector('main').append(host);const grid=document.createElement('div');grid.className='country-grid';host.append(grid);const result=[];function measure(n,label){const visible=[...grid.children].filter(e=>!e.hidden),first=visible[0].getBoundingClientRect(),row=visible.filter(e=>Math.abs(e.getBoundingClientRect().top-first.top)<1),r=grid.getBoundingClientRect();return{count:n,state:label,first:row.length,expected:n<=4?n:3,coverage:(row.at(-1).getBoundingClientRect().right-r.left)/r.width};}for(let n=1;n<=6;n++){grid.replaceChildren();for(let i=0;i<n;i++){const a=document.createElement('article');a.className='country-card-panel';a.style.minHeight='80px';a.textContent='Карточка '+(i+1);grid.append(a);}result.push(measure(n,'initial'));}for(const n of[1,2,3,4,5,6]){[...grid.children].forEach((e,i)=>e.hidden=i>=n);result.push(measure(n,'visibility-change'));}host.remove();return result;}''')
 assert all(x['first']==x['expected']and x['coverage']>=.9 for x in result),(name,result);await ctx.close();return [dict(engine=name,**x)for x in result]
async def main():
 class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*a,**kw):super().__init__(*a,directory=str(Path(__file__).resolve().parents[2]/'docs'),**kw)
  def log_message(self,*a):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();result=[]
 try:
  async with async_playwright()as pw:
   for name in['chromium','firefox','webkit']:
    b=await launch(pw,name);result+=await check(b,name,'http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/');await b.close()
 finally:server.shutdown()
 (Path(__file__).resolve().parents[2]/'docs/scheme2/d1/QA9_CARDINALITY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Passed',len(result),'cardinality fixtures')
if __name__=='__main__':asyncio.run(main())
