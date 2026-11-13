"""Check text stays inside every measured card, including horizontal orphan cards."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import asyncio,json,threading
from playwright.async_api import async_playwright
from engines7 import launch
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';PAGES=json.loads((R/'tools/d1/pages.json').read_text());WIDTHS=[360,390,768,1024,1280,1366,1440,1920,2560]
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(R/'docs'),**k)
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=s.serve_forever,daemon=True).start();report={'stage':12,'cases':0,'cards':0,'text_rects':0,'failures':[],'errors':[]}
JS=r'''()=>{let cards=0,texts=0;const fail=[];for(const card of document.querySelectorAll('.equal-card')){if(!card.getClientRects().length||card.closest('[hidden],[inert]'))continue;cards++;const box=card.getBoundingClientRect(),walk=document.createTreeWalker(card,NodeFilter.SHOW_TEXT);let node;while(node=walk.nextNode()){if(!node.textContent.trim()||node.parentElement.closest('svg,[aria-hidden=true],.sr-only,[hidden],select'))continue;let unpainted=false;for(let e=node.parentElement;e&&e!==card;e=e.parentElement)if(e.tagName==='DETAILS'&&!e.open&&!e.querySelector(':scope>summary')?.contains(node))unpainted=true;if(unpainted)continue;const range=document.createRange();range.selectNodeContents(node);for(const r of range.getClientRects()){if(r.width<=0||r.height<=0)continue;texts++;if(r.left<box.left-2||r.right>box.right+2||r.top<box.top-2||r.bottom>box.bottom+2)fail.push({card:card.className,text:node.textContent.trim().slice(0,90),rect:{left:r.left,right:r.right,top:r.top,bottom:r.bottom},box:{left:box.left,right:box.right,top:box.top,bottom:box.bottom}});}}}return{cards,texts,fail};}'''
async def main():
 async with async_playwright()as pw:
  for name in['chromium','firefox','webkit']:
   b=await launch(pw,name)
   for w in WIDTHS:
    ctx=await b.new_context(viewport={'width':w,'height':900},reduced_motion='reduce');p=await ctx.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)))
    for row in PAGES:
     await p.goto('http://127.0.0.1:'+str(s.server_port)+'/scheme2/d1/'+row['path'])
     if row['type']=='redirect':await p.wait_for_url('**/o-nas/index.html#team')
     await p.evaluate('''async()=>{await document.fonts.ready;window.MangoLayout?.refresh();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}''');x=await p.evaluate(JS);report['cases']+=1;report['cards']+=x['cards'];report['text_rects']+=x['texts']
     if x['fail']:report['failures'].append(dict(engine=name,width=w,path=row['path'],fail=x['fail']))
    await ctx.close()
   await b.close();print(name,'done;',len(report['failures']),'failures',flush=True)
 report['status']='passed'if not report['errors']and not report['failures']else'failed';assert report['status']=='passed',(len(report['failures']),report['errors']);print('Card text clipping passed',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:s.shutdown();(S/'QA12_CLIPPING.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
