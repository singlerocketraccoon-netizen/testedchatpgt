"""Targeted numeric, select/dialog, icon and document URL acceptance."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import asyncio,json,threading,copy,sys
from engines7 import launch
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';WIDTHS=[360,390,768,1024,1280,1366,1440,1920,2560]
ICONS=r'''()=>{const result=[];for(const e of document.querySelectorAll('.btn,.text-link,[data-rest-toggle]')){if(!e.getClientRects().length||e.closest('[hidden],[inert],dialog:not([open])'))continue;const icons=[...e.querySelectorAll(':scope>.icon,:scope>[data-rest-chevron]>.icon')].filter(i=>{const r=i.getBoundingClientRect();return r.width>0&&r.height>0;});if(!icons.length)continue;const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT),rects=[];let n;while(n=walker.nextNode()){if(!n.textContent.trim()||n.parentElement.closest('svg,[aria-hidden=true]'))continue;const ns=getComputedStyle(n.parentElement);if(ns.display==='none'||ns.visibility==='hidden')continue;const z=document.createRange();z.selectNodeContents(n);rects.push(...[...z.getClientRects()].filter(r=>r.width>0&&r.height>0));}if(!rects.length)continue;const top=Math.min(...rects.map(r=>r.top)),bottom=Math.max(...rects.map(r=>r.bottom));for(const i of icons){const r=i.getBoundingClientRect();result.push({label:e.textContent.trim(),delta:r.top+r.height/2-(top+bottom)/2});}}return result;}'''
async def check(browser,name,base):
 rows=[]
 for width in WIDTHS:
  ctx=await browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');p=await ctx.new_page();await p.goto(base+'index.html');await p.evaluate('document.fonts.ready');await p.locator('[data-hero-cta]').first.click();await p.locator('#request-dialog').wait_for(state='visible')
  result=await p.locator('#request-dialog [data-form-pane=pick]').evaluate('''pane=>{const fail=[],selects=[];for(const e of pane.querySelectorAll('select')){const s=getComputedStyle(e),r=e.getBoundingClientRect(),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font=s.font;const need=ctx.measureText(e.options[e.selectedIndex].text).width+parseFloat(s.paddingLeft)+44;selects.push({width:r.width,need,appearance:s.appearance,right:s.backgroundPosition,padding:s.paddingRight});if(s.appearance!=='none'||s.paddingRight!=='44px'||!s.backgroundPosition.includes('16px')||need>r.width+1)fail.push(selects.at(-1));}return{fail,selects};}''');assert not result['fail'],(name,width,result)
  await p.keyboard.press('Escape');await p.locator('[data-rest-toggle]').click();await p.evaluate('MangoLayout.refresh()');icons=await p.evaluate(ICONS);assert all(abs(x['delta'])<=2 for x in icons),(name,width,icons)
  site_icons=0
  for row in [r for r in json.loads((R/'tools/d1/pages.json').read_text())if '--page'not in sys.argv or r['path']==sys.argv[sys.argv.index('--page')+1]]:
   await p.goto(base+row['path'])
   if row['type']=='redirect':await p.wait_for_url('**/o-nas/index.html#team')
   await p.evaluate('document.fonts.ready');measured=await p.evaluate(ICONS);bad=[x for x in measured if abs(x['delta'])>2];assert not bad,(name,width,row['path'],bad);site_icons+=len(measured)
  rows.append(dict(engine=name,width=width,selects=result['selects'],icons=icons,site_icons=site_icons));await ctx.close()
 return rows

def url_fixture():
 import stage11
 from html import escape
 real=json.loads((R/'tools/d1/data.json').read_text());captured=[]
 def link(path,target,label,goal,cls='',extra=''):return '<a href="'+target+'">'+label+'</a>'
 ctx=dict(DATA=copy.deepcopy(real),E=lambda x:escape(str(x),quote=True),icon=lambda name:'',url=lambda p,t:t,link=link,editable=lambda k,a=False:'data-editable="'+k+'"',agency=lambda:{},section=lambda t,b:'<h2>'+t+'</h2>'+b,emit=lambda *a,**kw:captured.append((a,kw)))
 stage11.configure(ctx);stage11.requisites();empty=captured[-1][0][5];assert empty.count('data-agency-document=')==5
 ctx['DATA']['requisites']['documents'][0]['url']='https://example.org/agency.pdf';stage11.requisites();filled=captured[-1][0][5];assert 'href="https://example.org/agency.pdf" target="_blank" rel="noopener"'in filled and filled.count('data-agency-document=')==4
 return dict(empty_urls='five keyboard-enabled dialogs',filled_url='ordinary PDF link, new tab, noopener',source_json_unchanged=True)
async def main():
 class Handler(SimpleHTTPRequestHandler):
  def __init__(self,*a,**kw):super().__init__(*a,directory=str(R/'docs'),**kw)
  def log_message(self,*a):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();report={'cases':[],'url_fixture':url_fixture()}
 try:
  async with async_playwright()as pw:
   for name in['chromium','firefox','webkit']:
    b=await launch(pw,name);report['cases']+=await check(b,name,'http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/');await b.close()
 finally:server.shutdown();(S/('QA11_REQUISITES.json'if '--page'in sys.argv else'QA11_CONTROLS.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('Passed',len(report['cases']),'dialog/select/icon cases and PDF URL fixture')
if __name__=='__main__':asyncio.run(main())
