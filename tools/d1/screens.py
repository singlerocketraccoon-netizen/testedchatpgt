#!/usr/bin/env python3
"""Capture public d1 pages plus four home states; local Playwright, JPEG 75."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from html import escape
from build import brand_icons
import asyncio,json,threading,tempfile
from PIL import Image
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2];SITE=ROOT/'docs/scheme2/d1';OUT=SITE/'screens/pages'
PAGES=[p for p in json.loads((Path(__file__).parent/'pages.json').read_text())if p['path']not in['pages.html','accent-options.html']]
DETAILS=[{'path':'index.html#moods','title':'Главная · отдых, раскрытые карточки','file_slug':'glavnaya-blok-otdyh'},{'path':'index.html','title':'Главная · окно «Помогите выбрать»','file_slug':'glavnaya-okno-pomogite'}]
DETAILS.append({'path':'index.html#offers','title':'Главная · карусель предложений','file_slug':'glavnaya-karusel-predlozheniy'})
DETAILS.append({'path':'index.html','title':'Главная · окно «Обсудить поездку»','file_slug':'glavnaya-okno-obsudit'})
GALLERY=PAGES+DETAILS;OUT.mkdir(parents=True,exist_ok=True)
TEMP=Path(tempfile.mkdtemp(prefix='d1-screens-'));(TEMP/'travel').symlink_to(ROOT/'docs',target_is_directory=True)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(TEMP),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();ORIGIN=f'http://127.0.0.1:{server.server_port}/travel/scheme2/d1/'
def slug(path):return path.removesuffix('index.html').strip('/').removesuffix('.html').replace('/','-')or'index'
async def prepare(page):
 await page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
 for direction in ['down','up']:
  await page.evaluate("""async d=>{const wait=()=>new Promise(r=>setTimeout(r,25));const end=document.documentElement.scrollHeight-innerHeight;if(d==='down'){for(let y=0;y<end;y+=innerHeight*.8){scrollTo({top:y,behavior:'instant'});await wait();}scrollTo({top:end,behavior:'instant'});}else{for(let y=scrollY;y>0;y-=innerHeight*.8){scrollTo({top:y,behavior:'instant'});await wait();}scrollTo({top:0,behavior:'instant'});}await wait();}""",direction)
 await page.evaluate("async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));await document.fonts.ready;}");await page.wait_for_timeout(500);await page.mouse.move(0,0)
 assert await page.evaluate('scrollY')==0
 assert await page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
def gallery():
 cards=''
 for i,p in enumerate(GALLERY):
  name=p.get('file_slug',slug(p['path']));cards+=f'<article data-gallery-item data-title="{escape(p["title"],quote=True)}"><h2><a href="../../{p["path"]}" data-goal="gallery_page_{i}">{escape(p["title"])}</a></h2><p>{p["path"]}</p><div class="shots">'+''.join(f'<a href="{name}-{w}.jpg" data-width="{w}" data-goal="gallery_image_{i}_{w}"><span>{w} px ↗</span><img src="{name}-{w}.jpg" alt="{escape(p["title"],quote=True)}, ширина {w} px" width="{w}" height="{round(next(x["height"]for x in report["captures"]if x["file"]==name+"-"+str(w)+".jpg"))}" loading="lazy"></a>'for w in [390,1440])+'</div></article>'
 html='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="Галерея 37 страниц Mango Travel: полностраничные снимки на 390 и 1440 пикселей."><title>Галерея страниц — Mango Travel</title><link rel="stylesheet" href="../../css/fonts.css"><link rel="stylesheet" href="../../css/main.css"><style>*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:14px/1.6 Manrope,sans-serif}header{padding:32px 22px;border-bottom:1px solid var(--line);background:var(--cream)}h1{margin:0 0 12px;font:400 48px/1.1 'Cormorant Garamond',serif}.gallery-logo{width:auto;height:40px;margin-bottom:22px}header p{max-width:650px;color:var(--muted)}a{color:var(--clay);text-decoration:none}a:hover{text-decoration:underline}:focus-visible{outline:3px solid var(--clay);outline-offset:4px}.controls{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px}input,select{min-width:0;max-width:100%;min-height:44px;padding:10px 14px;border:1px solid var(--control);border-radius:10px;background:var(--cream);color:var(--ink);font:inherit}input{flex:1;min-width:200px}.gallery{display:grid;gap:24px;padding:24px 22px;max-width:1440px;margin:auto}article{min-width:0;padding:20px;border:1px solid var(--line);border-radius:18px;background:var(--cream)}h2{margin:0;font:400 31px/1.15 'Cormorant Garamond',serif}article>p{overflow-wrap:anywhere;color:var(--muted);font-size:10px}.shots{display:grid;grid-template-columns:1fr 1fr;gap:12px}.shots a{display:block;min-width:0}.shots span{display:block;margin:8px 0;font-size:11px}.shots img{display:block;width:100%;height:230px;object-fit:cover;object-position:top;border:1px solid var(--line);border-radius:8px}[hidden]{display:none!important}.status{margin:0 22px;color:var(--muted)}@media(min-width:768px){.gallery-logo{height:54px}header{padding:45px max(42px,calc((100vw - 1356px)/2))}.gallery{grid-template-columns:repeat(2,minmax(0,1fr));padding:32px 42px}.shots img{height:300px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}</style></head><body><header><img class="gallery-logo" src="../../img/logo-mango.svg" alt="Mango Travel" width="1193" height="440"><h1>Mango Travel · страницы сайта</h1><p>37 страницы в двух размерах. Откройте снимок, чтобы рассмотреть страницу целиком, или перейдите на саму страницу по её названию.</p><a href="../../pages.html" data-goal="gallery_directory">Оглавление страниц →</a><div class="controls"><input type="search" aria-label="Найти страницу" placeholder="Найти страницу"><select aria-label="Ширина снимков"><option value="all">Обе ширины</option><option value="390">Телефон · 390 px</option><option value="1440">Компьютер · 1440 px</option></select></div></header><p class="status" aria-live="polite"></p><main class="gallery">'''+cards+'''</main><script>(()=>{const search=document.querySelector('input'),width=document.querySelector('select'),cards=[...document.querySelectorAll('[data-gallery-item]')];function update(){let n=0;cards.forEach(c=>{c.hidden=!c.textContent.toLowerCase().includes(search.value.trim().toLowerCase());if(!c.hidden)n++;c.querySelectorAll('[data-width]').forEach(a=>a.hidden=width.value!=='all'&&a.dataset.width!==width.value);c.querySelector('.shots').style.gridTemplateColumns=width.value==='all'?'1fr 1fr':'1fr';});document.querySelector('.status').textContent='Подборок снимков: '+n;}search.addEventListener('input',update);width.addEventListener('change',update);update();})();</script></body></html>'''
 html=html.replace('37 страниц',str(len(PAGES))+' страниц').replace('37 страницы',str(len(PAGES))+' страниц')
 html=html.replace('</head>',brand_icons('screens/pages/index.html')+'</head>')
 (OUT/'index.html').write_text(html)
report={'format':'JPEG','quality':75,'reduced_motion':'reduce','scroll_down_and_back':True,'fonts_ready':True,'extra_wait_ms':500,'page_count':len(PAGES),'detail_count':len(DETAILS)*2,'captures':[],'errors':[]}
def record(path,file,width,kind):
 with Image.open(OUT/file)as im:pw,ph=im.size
 scale=2 if width==390 else 1
 assert pw==width*scale,(file,pw)
 report['captures'].append({'page':path,'file':file,'kind':kind,'width':width,'height':ph/scale,'device_scale_factor':scale,'pixel_width':pw,'pixel_height':ph})
async def main():
 async with async_playwright()as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for rec in PAGES:
   for width in [390,1440]:
    ctx=await browser.new_context(viewport={'width':width,'height':844 if width==390 else 1000},device_scale_factor=2 if width==390 else 1,reduced_motion='reduce',is_mobile=width==390,has_touch=width==390,locale='ru-RU');page=await ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None)
    await page.goto(ORIGIN+rec['path'],wait_until='networkidle');
    if rec.get('type')=='redirect':await page.wait_for_url('**/o-nas/index.html#team')
    await prepare(page);assert await page.evaluate('document.documentElement.scrollWidth')==width,rec['path'];file=slug(rec['path'])+'-'+str(width)+'.jpg';await page.screenshot(path=str(OUT/file),full_page=True,type='jpeg',quality=75);record(rec['path'],file,width,'page')
    if rec['path']=='index.html':
     await prepare(page);await page.locator('[data-rest-toggle]').click();await page.wait_for_timeout(500);await page.evaluate('document.activeElement.blur()');file='glavnaya-blok-otdyh-'+str(width)+'.jpg'
     await page.locator('.mood-section').screenshot(path=str(OUT/file),type='jpeg',quality=75,style='.d1-header,.mobile-contact,.skip-link { visibility: hidden !important; }');record('index.html#moods',file,width,'component')
     await prepare(page);await page.evaluate('document.activeElement.blur()');file='glavnaya-karusel-predlozheniy-'+str(width)+'.jpg';await page.locator('#offers').screenshot(path=str(OUT/file),type='jpeg',quality=75,style='.d1-header,.mobile-contact,.skip-link { visibility: hidden !important; }');record('index.html#offers',file,width,'component')
     await page.goto(ORIGIN,wait_until='networkidle');await prepare(page);await page.locator('.hero-slide.is-active [data-quiz-open]').click();await page.evaluate('document.fonts.ready');await page.wait_for_timeout(500);file='glavnaya-okno-pomogite-'+str(width)+'.jpg';await page.screenshot(path=str(OUT/file),type='jpeg',quality=75);record('index.html',file,width,'dialog')
     await page.keyboard.press('Escape');await page.locator('[data-hero-next]').click();await page.locator('.hero-slide.is-active [data-request]').click();await page.evaluate('document.fonts.ready');await page.wait_for_timeout(500);file='glavnaya-okno-obsudit-'+str(width)+'.jpg';await page.screenshot(path=str(OUT/file),type='jpeg',quality=75);record('index.html',file,width,'dialog')
    await ctx.close()
   print('Captured',rec['path'],flush=True)
  assert not report['errors'],report['errors']
  wanted={x['file']for x in report['captures']}
  for f in OUT.glob('*.jpg'):
   if f.name not in wanted:f.unlink()
  gallery();await browser.close()
 report['screenshot_count']=len(report['captures']);(SITE/'SCREENS_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Captured',len(PAGES),'pages and',len(report['captures']),'screenshots')
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown()
