"""Stage 8 current pages and country interaction details; JPEG 75."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from html import escape as E
import asyncio,json,threading,re,sys,os
from PIL import Image
from engines7 import launch
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';OUT=S/'screens/pages';OUT.mkdir(parents=True,exist_ok=True)
PAGES=[p for p in json.loads((R/'tools/d1/pages.json').read_text())if p['path']not in['pages.html','accent-options.html']]
report={'format':'JPEG','quality':75,'reduced_motion':'reduce','scroll_down_and_back':True,'fonts_ready':True,'extra_wait_ms':500,'page_count':len(PAGES),'captures':[],'errors':[]}
partial=bool(sys.argv[1:])
if partial or os.environ.get('D1_SCREEN_DESKTOP_ONLY'):report=json.loads((S/'SCREENS_QA.json').read_text())
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R/'docs'),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
def slug(path):return path.removesuffix('index.html').strip('/').removesuffix('.html').replace('/','-')or'index'
async def prepare(page):
 await page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
 await page.evaluate("""async()=>{const pause=()=>new Promise(r=>setTimeout(r,20));for(let y=0;y<document.documentElement.scrollHeight-innerHeight;y+=innerHeight*.9){scrollTo(0,y);await pause();}scrollTo(0,document.documentElement.scrollHeight);await pause();scrollTo(0,0);await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));}""")
 await page.wait_for_timeout(500);await page.mouse.move(0,0)
async def take(browser,engine,path,title,width,file,locator=None,state=None):
 context=await browser.new_context(viewport={'width':width,'height':844 if width==390 else 900},device_scale_factor=2 if width==390 else 1,reduced_motion='reduce',locale='ru-RU');page=await context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None);await page.goto(BASE+path,wait_until='load')
 if path=='o-nas/komanda/index.html':await page.wait_for_url('**/o-nas/index.html#team')
 await prepare(page);
 if state:await state(page)
 assert await page.evaluate('document.documentElement.scrollWidth')==width,(path,width)
 if locator and locator!='.d1-header':await page.add_style_tag(content='.d1-header,.mobile-contact,.skip-link{visibility:hidden!important}')
 if locator:await page.locator(locator).screenshot(path=str(OUT/file),type='jpeg',quality=75)
 else:await page.screenshot(path=str(OUT/file),type='jpeg',quality=75,full_page=True)
 image=Image.open(OUT/file);report['captures']=[r for r in report['captures']if r['file']!=file];report['captures'].append(dict(page=path,title=title,file=file,width=width,engine=engine,device_scale_factor=2 if width==390 else 1,pixel_width=image.width,pixel_height=image.height,kind='component'if locator else'page'))
 await context.close()
def gallery():
 groups={}
 for c in report['captures']:groups.setdefault((c['page'],c['title']),[]).append(c)
 cards=''
 for i,((path,title),captures)in enumerate(groups.items()):
  cards+='<article class="gallery-card" data-gallery-item data-title="'+E(title,quote=True)+'"><h2><a href="../../'+path+'" data-goal="gallery_page_'+str(i)+'">'+E(title)+'</a></h2><p>'+E(path)+'</p><div class="gallery-shots">'+''.join('<a href="'+c['file']+'" data-goal="gallery_shot_'+str(i)+'_'+str(c['width'])+'"><span>'+str(c['width'])+' px · '+c['engine']+' ↗</span><img src="'+c['file']+'" alt="'+E(title,quote=True)+' — '+str(c['width'])+' px" width="'+str(c['pixel_width'])+'" height="'+str(c['pixel_height'])+'"'+(' class="gallery-header-shot"'if c['kind']=='component'else'')+' loading="lazy"></a>'for c in captures)+'</div></article>'
 html='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="Снимки страниц Mango Travel после этапа 8: компьютер, телефон и сравнение движков."><title>Галерея страниц — Mango Travel</title>'+''.join('<link rel="stylesheet" href="../../css/'+n+'.css">'for n in['tokens','fonts','base','gallery'])+'<script defer src="../../js/gallery.js"></script></head><body class="gallery-page"><main class="gallery-main"><header><h1>Страницы Mango Travel</h1><p>'+str(len(PAGES))+' адресов · '+str(len(report['captures']))+' снимков</p><label>Найти страницу<input type="search" data-gallery-search autocomplete="off"></label></header>'+cards+'</main></body></html>\n'
 (OUT/'index.html').write_text(html)
async def main():
 async with async_playwright()as p:
  browser=await launch(p,'chromium')
  for row in [r for r in PAGES if not partial or r['path']in sys.argv[1:]]:
   for width in([1440]if os.environ.get('D1_SCREEN_DESKTOP_ONLY')else[390,1440]):await take(browser,'Chromium',row['path'],row['title'],width,slug(row['path'])+'-'+str(width)+'.jpg')
   print('Captured',row['path'],flush=True)
  if not partial:
   for width in[1024,1280,1440,1920]:await take(browser,'Chromium','index.html','Шапка',width,'shapka-'+str(width)+'.jpg','.d1-header')
  if not partial:
   for width in [390,1440]:
    await take(browser,'Chromium','napravleniya/egipet/index.html','Египет · хлебные крошки',width,'egipet-kroshki-'+str(width)+'.jpg','.breadcrumbs')
    async def expanded_resort(page):
     await page.locator('[data-resort-card=hurghada] details').evaluate('e=>e.open=true');await page.locator('#resorts').scroll_into_view_if_needed();await page.wait_for_timeout(500)
    async def climate_table(page):
     await page.locator('[data-weather-resort]').select_option('gouna');await page.locator('[data-weather-month="3"]').click();await page.locator('.country-weather-table').evaluate('e=>e.open=true');await page.locator('#season').scroll_into_view_if_needed();await page.wait_for_timeout(500)
    await take(browser,'Chromium','napravleniya/egipet/index.html','Египет · раскрытый курорт',width,'egipet-kurort-'+str(width)+'.jpg','#resorts',expanded_resort)
    await take(browser,'Chromium','napravleniya/egipet/index.html','Египет · климатическая таблица',width,'egipet-klimat-'+str(width)+'.jpg','#season',climate_table)
  await browser.close()
  if not partial:
   browser=await launch(p,'webkit')
   for width in[390,1440]:await take(browser,'WebKit','index.html','Главная · WebKit',width,'index-webkit-'+str(width)+'.jpg')
   await browser.close()
 assert not report['errors'],report['errors'];wanted={r['file']for r in report['captures']}
 for f in OUT.glob('*.jpg'):
  if f.name not in wanted:f.unlink()
 report['screenshot_count']=len(report['captures']);gallery();(S/'SCREENS_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Gallery',len(PAGES),'pages,',len(report['captures']),'JPEG')
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown()
