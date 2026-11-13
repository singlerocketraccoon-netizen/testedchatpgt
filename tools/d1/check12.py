"""Stage 12: navigation geometry, orphan rows, independent accordions and preserved copy."""
from pathlib import Path
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import asyncio,json,hashlib,subprocess,threading,sys,re
from playwright.async_api import async_playwright
from engines7 import launch
from geometry11 import GEOMETRY
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';PAGES=json.loads((R/'tools/d1/pages.json').read_text());WIDTHS=[360,390,768,1024,1280,1366,1440,1920,2560]
class Copy(HTMLParser):
 def __init__(self,text):super().__init__();self.parts=[];self.skip=0;self.feed(text)
 def handle_starttag(self,t,a):
  if t in['svg','script','style']:self.skip+=1
 def handle_endtag(self,t):
  if t in['svg','script','style']:self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
 def text(self):return ' '.join(' '.join(self.parts).split())
def sha(b):return hashlib.sha256(b).hexdigest()
report={'stage':12,'widths':WIDTHS,'engines':{},'failures':[],'errors':[],'resources':[],'menus':[],'accordion_checks':0,'orphan_rows':0,'photo_checks':0,'mood_checks':0,'row_checks':0}
lock=json.loads((R/'tools/d1/stage12-preservation.json').read_text());assert sha((R/'tools/d1/data.json').read_bytes())==lock['data']
for path,digest in lock['assets'].items():assert sha((S/path).read_bytes())==digest,path
for path,expected in lock['pages'].items():
 text=(S/path).read_text();assert sha(Copy(text).text().encode())==expected['copy'],('Copy changed',path)
 assert sha(re.search(r'<header\b.*?</header>',text,re.S)[0].encode())==expected['header'],('Header markup changed',path)
 assert sha(re.search(r'<!-- component: footer -->.*?<!-- /component: footer -->',text,re.S)[0].encode())==expected['footer'],('Footer changed',path)
report['preservation']='Existing copy except one authorised document caption; JSON, palette, fonts, logo, header/mobile markup and footer unchanged'
if '--skip-build'not in sys.argv:
 checked=subprocess.run([sys.executable,str(R/'tools/d1/check11.py'),'--static'],check=True,capture_output=True,text=True);report['static']=json.loads(checked.stdout)
 if '--static'in sys.argv:print(json.dumps(report,ensure_ascii=False));sys.exit()
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(R/'docs'),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
EXTRA=r'''()=>{
 const rect=e=>e.getBoundingClientRect(),shown=e=>e.getClientRects().length&&!e.closest('[hidden],[inert],dialog:not([open])'),$=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],fail=[];let orphan=0,photos=0,moods=0;
 const grids=new Set($$('.equal-card').map(c=>c.parentElement));
 for(const g of grids){const a=[...g.children].filter(shown);if(a.length<3||getComputedStyle(g).display!=='grid')continue;const first=rect(a[0]).top,cols=a.filter(c=>Math.abs(rect(c).top-first)<2).length,last=a.at(-1),bottom=rect(last).top,lastRow=a.filter(c=>Math.abs(rect(c).top-bottom)<2);if(innerWidth>=1280&&a.length===7&&cols!==4)fail.push({kind:'seven-columns',grid:g.className,cols});if(cols>1&&lastRow.length===1){orphan++;const width=rect(g).width;if(!last.classList.contains('is-orphan-card')||Math.abs(rect(last).width-width)>2)fail.push({kind:'orphan-row',grid:g.className,count:a.length,cols,width,last:rect(last).width});const target=last.matches('.country-index-card')?last.firstElementChild:last;if(getComputedStyle(target).gridTemplateColumns.split(' ').length!==2)fail.push({kind:'orphan-horizontal',grid:g.className});}}
 const mood=$('#moods>.container>.rest-grid');if(mood&&innerWidth>=1024){const a=$$('.rest-card',mood),offsets=a.map(c=>({icon:rect($('.rest-symbol .icon',c)).left-rect(c).left,title:rect($('.rest-label',c)).left-rect(c).left,subtitle:rect($('.rest-card-subtitle',c)).left-rect(c).left,arrow:rect(c).right-rect($('.rest-caption>.icon',c)).right}));for(const k of['icon','title','subtitle','arrow']){const v=offsets.map(x=>x[k]);if(Math.max(...v)-Math.min(...v)>1)fail.push({kind:'mood-left',key:k,offsets});}moods++;}
 const gallery=$('.offer-detail-photos');if(gallery){photos++;const [photo,placeholder]=[...gallery.children],p=rect(photo),z=rect(placeholder),s=getComputedStyle(placeholder);if(Math.abs(p.height-z.height)>1||s.backgroundImage==='none'||parseFloat(s.borderTopWidth)!==1||parseFloat(s.borderTopLeftRadius)<=0||s.alignItems!=='center'||s.justifyContent!=='center'||!$('svg',placeholder))fail.push({kind:'photo-placeholder',p:p.height,z:z.height,bg:s.backgroundImage,border:s.borderTopWidth});if(innerWidth>=768&&Math.abs(p.width/z.width-2)>.02)fail.push({kind:'photo-ratio',p:p.width,z:z.width});if(innerWidth<768&&z.top<p.bottom+19)fail.push({kind:'photo-stack',p:p.bottom,z:z.top});}
 return{fail,orphan,photos,moods};
}'''
async def accordions(page,path,width):
 return await page.evaluate('''async()=>{const rows=[],fail=[],r=e=>e.getBoundingClientRect();for(const root of document.querySelectorAll('[data-independent-accordion]')){const cols=[...root.querySelectorAll(':scope>[data-accordion-column]')],items=[...root.querySelectorAll('details')];if(innerWidth<1024){const order=[...root.children].filter(x=>x.tagName==='DETAILS').map(e=>+e.dataset.accordionOrder);if(order.some((x,i)=>x!==i)||order.length!==items.length||cols.some(c=>!c.hidden))fail.push({kind:'accordion-mobile-order',order});continue;}if(cols.length!==2||cols.some(c=>c.hidden))fail.push({kind:'accordion-columns'});for(let c=0;c<2;c++)if([...cols[c].children].some((e,i)=>+e.dataset.accordionOrder!==i*2+c))fail.push({kind:'accordion-order',column:c});for(const e of items){const s=getComputedStyle(e);if(parseFloat(s.borderTopWidth)!==0||parseFloat(s.borderBottomWidth)!==1)fail.push({kind:'accordion-lines',top:s.borderTopWidth,bottom:s.borderBottomWidth});}const first=cols[0].firstElementChild,right=[...cols[1].children],before=right.map(e=>r(e).top);if(first){const was=first.open;first.open=true;await new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)));const after=right.map(e=>r(e).top);if(before.some((y,i)=>Math.abs(y-after[i])>1))fail.push({kind:'accordion-independent',before,after});first.open=was;rows.push({items:items.length,before,after});}}return{rows,fail};}''')
async def menus(browser,engine):
 for width in[1024,1280,1440,1920,2560]:
  ctx=await browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');p=await ctx.new_page();await p.goto(BASE+'index.html');await p.evaluate('document.fonts.ready')
  for scrolled in[False,True]:
   await p.keyboard.press('Escape');await p.mouse.move(0,500);await p.evaluate('(y)=>scrollTo(0,y)',500 if scrolled else 0);await p.wait_for_timeout(80)
   for key in['countries','services','about']:
    button=p.locator('[aria-controls="nav-'+key+'"]');await button.hover();await p.wait_for_timeout(40);panel=p.locator('#nav-'+key);assert await panel.is_visible(),(engine,width,key,'not open')
    got=await p.evaluate('''key=>{const h=document.querySelector('[data-site-header]').getBoundingClientRect(),g=document.querySelector('[aria-controls="nav-'+key+'"]').getBoundingClientRect(),p=document.querySelector('#nav-'+key),r=p.getBoundingClientRect(),logo=document.querySelector('.d1-header .brand').getBoundingClientRect(),s=getComputedStyle(p);return{gap:r.top-h.bottom,left:r.left,right:r.right,logoIntersection:r.left<logo.right&&r.right>logo.left&&r.top<logo.bottom&&r.bottom>logo.top,radii:[s.borderTopLeftRadius,s.borderTopRightRadius,s.borderBottomLeftRadius,s.borderBottomRightRadius],token:getComputedStyle(document.documentElement).getPropertyValue('--radius-card').trim(),max:parseFloat(s.maxHeight),height:h.height,border:s.borderTopWidth,shadow:s.boxShadow,aboutDelta:r.right-g.right,buttonX:g.left+g.width/2,bridgeY:h.bottom+5,panelY:r.top+16};}''',key)
    assert abs(got['gap']-10)<=1 and not got['logoIntersection']and got['left']>=0 and got['right']<=width+1,(engine,width,key,scrolled,got)
    assert len(set(got['radii']))==1 and got['radii'][0]==got['token'] and got['border']=='1px'and'18px 40px'in got['shadow'],(engine,width,key,got)
    assert abs(got['max']-(900-got['height']-24))<=1,(engine,width,key,got)
    if key=='about':assert abs(got['aboutDelta'])<=1,(engine,width,got)
    await p.mouse.move(got['buttonX'],got['bridgeY'],steps=12);await p.wait_for_timeout(240);assert await panel.is_visible(),(engine,width,key,scrolled,'bridge closed')
    await p.mouse.move(got['buttonX'],got['panelY'],steps=5);await p.wait_for_timeout(240);assert await panel.is_visible(),(engine,width,key,scrolled,'panel closed')
    await button.focus();await p.keyboard.press('ArrowDown');assert await panel.locator('a').first.evaluate('e=>e===document.activeElement');await p.keyboard.press('Escape');assert not await panel.is_visible();assert await button.evaluate('e=>e===document.activeElement')
    report['menus'].append(dict(engine=engine,width=width,scrolled=scrolled,menu=key,**got))
  await ctx.close()
async def interactions(browser,engine):
 ctx=await browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');p=await ctx.new_page();await p.goto(BASE+'otdyh/otdyh-s-detmi/index.html');await p.evaluate('document.fonts.ready');first=p.locator('#checks [data-accordion-order="0"]');summary=first.locator('summary');await summary.focus();await p.keyboard.press('Enter');assert await first.get_attribute('open')is not None
 await p.set_viewport_size({'width':390,'height':900});await p.wait_for_timeout(100);assert await first.get_attribute('open')is not None;assert await summary.evaluate('e=>e===document.activeElement');assert not(await accordions(p,'',390))['fail']
 await p.set_viewport_size({'width':1440,'height':900});await p.wait_for_timeout(100);assert await first.get_attribute('open')is not None;assert await summary.evaluate('e=>e===document.activeElement');assert not(await accordions(p,'',1440))['fail']
 for w in[768,1024,1280,1440,1920]:
  await p.set_viewport_size({'width':w,'height':900});await p.goto(BASE+'napravleniya/egipet/index.html');await p.evaluate('document.fonts.ready');await p.locator('[data-more-resorts]').click();await p.evaluate('MangoLayout.refresh()');result=await p.evaluate(EXTRA);assert not result['fail'],(engine,w,'expanded resorts',result)
  before=await p.locator('[data-resort-card=sharm],[data-resort-card=gouna]').evaluate_all('els=>els.map(e=>e.getBoundingClientRect().height)');await p.locator('[data-resort-card=hurghada] summary').click();after=await p.locator('[data-resort-card=sharm],[data-resort-card=gouna]').evaluate_all('els=>els.map(e=>e.getBoundingClientRect().height)');assert all(abs(a-b)<=1 for a,b in zip(before,after)),(engine,w,before,after)
 await p.set_viewport_size({'width':390,'height':900});await p.goto(BASE+'index.html');await p.locator('[data-menu]').click();assert await p.locator('#mobile-nav').is_visible();await p.locator('#mobile-nav .mobile-group').first.locator('summary').click();assert await p.locator('#mobile-nav .mobile-group').first.get_attribute('open')is not None;await p.keyboard.press('Escape');assert not await p.locator('#mobile-nav').is_visible();await ctx.close()
 touch=await browser.new_context(viewport={'width':1280,'height':900},has_touch=True,reduced_motion='reduce');p=await touch.new_page();await p.goto(BASE+'index.html');await p.evaluate('document.fonts.ready');await p.wait_for_timeout(100)
 for key in['countries','services','about']:
  button=p.locator('[aria-controls="nav-'+key+'"]');await button.tap();assert await p.locator('#nav-'+key).is_visible();await button.tap();assert not await p.locator('#nav-'+key).is_visible(),(engine,key,'second touch did not close')
 await touch.close();report.setdefault('interactions',[]).append(dict(engine=engine,responsive_accordion_focus='passed',expanded_resort_grids='passed',independent_resorts='passed',mobile_menu='passed',touch_menus='passed'))
async def main():
 names=['chromium','firefox','webkit'];widths=WIDTHS
 if '--engine'in sys.argv:names=[sys.argv[sys.argv.index('--engine')+1]]
 if '--width'in sys.argv:widths=[int(x)for x in sys.argv[sys.argv.index('--width')+1].split(',')]
 async with async_playwright()as pw:
  for name in names:
   b=await launch(pw,name);report['engines'][name]={'version':b.version,'cases':0}
   for w in widths:
    ctx=await b.new_context(viewport={'width':w,'height':900},reduced_motion='reduce');p=await ctx.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)));p.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None);p.on('response',lambda r:report['resources'].append([r.status,r.url])if r.status>=400 else None)
    for row in PAGES:
     await p.goto(BASE+row['path'])
     if row['type']=='redirect':await p.wait_for_url('**/o-nas/index.html#team')
     await p.evaluate('''async()=>{await document.fonts.ready;window.MangoLayout?.refresh();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}''');g=await p.evaluate(GEOMETRY);x=await p.evaluate(EXTRA);a=await accordions(p,row['path'],w);fail=g['fail']+x['fail']+a['fail']
     if row['path']in['o-nas/dokumenty/rekvizity/index.html','o-nas/dokumenty/politika/index.html','o-nas/dokumenty/soglasie/index.html']:assert await p.locator('.section-tabs [aria-current=true]').inner_text()=='Документы'
     if row['path']=='o-nas/dokumenty/index.html':assert await p.locator('.document-card').first.locator('p').count()==0 and await p.locator('.document-card p').count()==3
     if fail:report['failures'].append(dict(engine=name,width=w,page=row['path'],failures=fail))
     report['accordion_checks']+=len(a['rows']);report['orphan_rows']+=x['orphan'];report['photo_checks']+=x['photos'];report['mood_checks']+=x['moods'];report['row_checks']+=len(g['rows']);report['engines'][name]['cases']+=1
    await ctx.close();print(name,w,'complete;',len(report['failures']),'failures',flush=True);(S/'QA12.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
   if '--no-menus'not in sys.argv:await menus(b,name);await interactions(b,name)
   await b.close()
 report['status']='passed'if not report['failures']and not report['errors']and not report['resources']else'failed';assert report['status']=='passed',(len(report['failures']),report['errors'],report['resources']);print('Stage 12 passed',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown();(S/'QA12.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
