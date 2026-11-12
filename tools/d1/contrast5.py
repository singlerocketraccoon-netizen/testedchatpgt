#!/usr/bin/env python3
"""Sample text/background contrast on all home slides and nine country covers."""
import asyncio,json,threading,tempfile,math,io
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from PIL import Image
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';PAGES=[{'path':'index.html','type':'home'}]+[{'path':'napravleniya/'+c['slug']+'/index.html','type':'country'}for c in json.loads((R/'tools/d1/data.json').read_text())['countries']if c['published']]+[{'path':'otdyh/'+p['slug']+'/index.html','type':'holiday'}for p in json.loads((R/'tools/d1/data.json').read_text())['rest_pages']];T=Path(tempfile.mkdtemp());(T/'travel').symlink_to(R/'docs',target_is_directory=True)
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(T),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();U=f'http://127.0.0.1:{server.server_port}/travel/scheme2/d1/'
COLLECT='''()=>{const rgba=s=>{const v=s.match(/[\\d.]+/g)?.map(Number)||[0,0,0,0];return[v[0],v[1],v[2],v.length>3?v[3]:1];},mix=(a,b)=>{const alpha=a[3]+b[3]*(1-a[3]);return alpha?[0,1,2].map(i=>(a[i]*a[3]+b[i]*b[3]*(1-a[3]))/alpha).concat(alpha):[0,0,0,0];};const out=[];const walk=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let t;while(t=walk.nextNode()){if(!t.textContent.trim())continue;const e=t.parentElement;if(!e||e.closest('script,style,svg,[hidden],[inert],[aria-hidden="true"],.sr-only'))continue;const range=document.createRange();range.selectNodeContents(t);const rects=[...range.getClientRects()].filter(r=>r.width>1&&r.height>1);if(!rects.length)continue;const st=getComputedStyle(e);if(st.visibility!=='visible')continue;let bg=[0,0,0,0],kind=e.closest('.d1-header:not(.is-compact):not(.is-solid):not(.is-menu-open)')?'photo':'flat',opacity=1;for(let n=e;n;n=n.parentElement){const c=getComputedStyle(n);opacity*=Number(c.opacity);if(bg[3]<.999){if(n.matches('.hero-slide,.hero-shell,.country-cover,.country-hero,.rest-cover'))kind='photo';else if(c.backgroundImage!=='none'&&kind==='flat')kind='gradient';bg=mix(bg,rgba(c.backgroundColor));}}if(opacity===0)continue;if(bg[3]<1)bg=mix(bg,[255,255,255,1]);const f=rgba(st.color);f[3]*=opacity;out.push({text:t.textContent.trim().slice(0,100),cls:e.className||e.tagName,kind,bg: bg.slice(0,3),fg:f,size:parseFloat(st.fontSize),weight:parseInt(st.fontWeight)||400,disabled:!!e.closest(':disabled'),rects:rects.map(r=>({x:r.x,y:r.y,w:r.width,h:r.height}))});}return out;}'''
def lum(c):
 v=[x/255 for x in c];return sum(w*(x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4)for w,x in zip([.2126,.7152,.0722],v))
def ratio(a,b):x,y=sorted([lum(a),lum(b)]);return(y+.05)/(x+.05)
def getratio(f,b):return ratio([f[i]*f[3]+b[i]*(1-f[3])for i in range(3)],b)
report={'viewports':[],'flat_checks':0,'flat_failures':[],'photo_checks':0,'photo_failures':[],'photo_minima':[],'errors':[],'resources':[]}
async def photo(page,rows,width,path,label):
 rows=[r for r in rows if r['kind']=='photo'and any(v['y']>=0 and v['y']+v['h']<=900 for v in r['rects'])]
 style=await page.add_style_tag(content='body * { color:transparent!important; -webkit-text-fill-color:transparent!important; text-shadow:none!important; }')
 shot=await page.screenshot();await style.evaluate('e=>e.remove()');im=Image.open(io.BytesIO(shot)).convert('RGB');worst=99
 for row in rows:
  scores=[]
  for rect in row['rects']:
   if rect['y']<0 or rect['y']+rect['h']>900:continue
   for fx in [.05,.2,.4,.6,.8,.95]:
    for fy in [.3,.5,.7]:
     x=min(width-1,max(0,int(rect['x']+rect['w']*fx)));y=min(899,max(0,int(rect['y']+rect['h']*fy)));scores.append(getratio(row['fg'],im.getpixel((x,y))))
  if not scores:continue
  score=min(scores);limit=3 if row['size']>=24 or row['size']>=18.66 and row['weight']>=700 else 4.5;worst=min(worst,score);report['photo_checks']+=1
  if score+0.01<limit:report['photo_failures'].append({'path':path,'width':width,'state':label,'text':row['text'],'cls':row['cls'],'ratio':round(score,2),'required':limit})
 report['photo_minima'].append({'path':path,'width':width,'state':label,'minimum':round(worst,2)})
async def main():
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in[360,768,1280,1440]:
   page=await b.new_page(viewport={'width':width,'height':900},reduced_motion='reduce');page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('response',lambda r:report['resources'].append([r.status,r.url])if r.status>=400 else None)
   for rec in PAGES:
    path=rec['path'];await page.goto(U+path,wait_until='load');await page.evaluate('document.fonts.ready');rows=await page.evaluate(COLLECT)
    geom=await page.evaluate('''()=>{const h=document.querySelector('[data-site-header]'),l=h.querySelector('.brand'),r=l.getBoundingClientRect();return{doc:document.documentElement.scrollWidth,logoCenter:r.x+r.width/2,logoHeight:r.height,footerHeight:document.querySelector('.site-footer .brand img').getBoundingClientRect().height};}''');assert geom['doc']==width,(width,path,geom);assert abs(geom['logoHeight']-(68 if width>=1440 else 64 if width>=1280 else 44))<.1,(width,path,geom);assert abs(geom['footerHeight']-56)<.1
    if width>=1024:assert abs(geom['logoCenter']-width/2)<.1
    for row in rows:
     if row['kind']!='flat' or row['disabled']:continue
     score=getratio(row['fg'],row['bg']);limit=3 if row['size']>=24 or row['size']>=18.66 and row['weight']>=700 else 4.5;report['flat_checks']+=1
     if score+.01<limit:report['flat_failures'].append({'path':path,'width':width,'text':row['text'],'cls':row['cls'],'ratio':round(score,2),'required':limit,'fg':row['fg'],'bg':row['bg']})
    if width in[360,768,1280,1440]and(path=='index.html'or rec['type']=='country'or path.startswith('otdyh/')):
     await page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')");await page.evaluate('Promise.all([...document.images].map(i=>i.decode()))');await photo(page,await page.evaluate(COLLECT),width,path,'initial')
     if path=='index.html':
      for i in[1,2,3]:
       await page.locator('[data-hero-next]').click();await page.wait_for_timeout(40);assert await page.locator('[data-hero-count]').text_content()==str(i+1);await photo(page,await page.evaluate(COLLECT),width,path,'slide '+str(i+1))
    await page.evaluate('scrollTo(0,240)');await page.wait_for_timeout(40);height=await page.locator('[data-site-header] .brand').evaluate('e=>e.getBoundingClientRect().height');assert abs(height-(68 if width>=1440 else 64 if width>=1280 else 44))<.1,(width,path,height);report['viewports'].append({'width':width,'path':path,'logo':geom['logoHeight'],'compact':height,'footer':geom['footerHeight']})
   print('Audited',width,flush=True);await page.close()
  await b.close()
 (S/'STAGE7_CONTRAST.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k]for k in['flat_checks','flat_failures','photo_checks','photo_failures','errors','resources']},ensure_ascii=False,indent=2))
try:
 asyncio.run(main())
 assert not any(report[k]for k in ['flat_failures','photo_failures','errors','resources']),report
finally:server.shutdown()
