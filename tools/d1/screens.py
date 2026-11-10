#!/usr/bin/env python3
"""Optional screenshot pass: Python Playwright + Chromium; JPEG 75, no source edits."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import asyncio,json,threading,tempfile,math,sys
from html import escape
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2];SITE=ROOT/'docs/scheme2/d1';OUT=SITE/'screens/pages';PAGES=json.loads((Path(__file__).parent/'pages.json').read_text());OUT.mkdir(parents=True,exist_ok=True)
TEMP=Path(tempfile.mkdtemp(prefix='d1-screens-'));(TEMP/'travel').symlink_to(ROOT/'docs',target_is_directory=True)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(TEMP),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();ORIGIN=f'http://127.0.0.1:{server.server_port}/travel/scheme2/d1/'
def slug(path):return path.removesuffix('index.html').strip('/').removesuffix('.html').replace('/','-')or'index'
async def prepare(page):
 await page.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
 for direction in ['down','up']:
  await page.evaluate("""async d=>{const wait=()=>new Promise(r=>setTimeout(r,35));const end=Math.max(document.documentElement.scrollHeight,document.body.scrollHeight)-innerHeight;if(d==='down'){for(let y=0;y<end;y+=innerHeight*.8){scrollTo({top:y,behavior:'instant'});await wait();}scrollTo({top:end,behavior:'instant'});}else{for(let y=scrollY;y>0;y-=innerHeight*.8){scrollTo({top:y,behavior:'instant'});await wait();}scrollTo({top:0,behavior:'instant'});}await wait();}""",direction)
 await page.evaluate("async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));await document.fonts.ready;}");await page.wait_for_timeout(120)
 assert await page.evaluate('scrollY')==0
 assert await page.evaluate('matchMedia("(prefers-reduced-motion: reduce)").matches')
def gallery():
 cards=''
 for i,p in enumerate(PAGES):
  name=slug(p['path']);cards+=f'<article data-gallery-item data-title="{escape(p["title"],quote=True)}"><h2><a href="../../{p["path"]}" data-goal="gallery_page_{i}">{escape(p["title"])}</a></h2><p>{p["path"]}</p><div class="shots">'+''.join(f'<a href="{name}-{w}.jpg" data-width="{w}" data-goal="gallery_image_{i}_{w}"><span>{w} px ↗</span><img src="{name}-{w}.jpg" alt="{escape(p["title"],quote=True)}, ширина {w} px" width="{w}" height="{next(x["height"]for x in report["captures"]if x["file"]==name+"-"+str(w)+".jpg")}" loading="lazy"></a>'for w in [390,1440])+'</div></article>'
 html='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="Галерея 33 страниц Манго Путешествия: полностраничные снимки на 390 и 1440 пикселей."><title>Галерея страниц — Манго Путешествия</title><link rel="stylesheet" href="../../css/fonts.css"><style>*{box-sizing:border-box}body{margin:0;background:#F3EEE4;color:#332D28;font:14px/1.6 Manrope,sans-serif}header{padding:32px 22px;border-bottom:1px solid #C9BEB0;background:#FAF7F1}h1{margin:0 0 12px;font:400 48px/1.1 'Cormorant Garamond',serif}header p{max-width:650px;color:#71665C}a{color:#984B33;text-decoration:none}a:hover{text-decoration:underline}:focus-visible{outline:3px solid #984B33;outline-offset:4px}.controls{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px}input,select{min-width:0;max-width:100%;min-height:44px;padding:10px 14px;border:1px solid #88745E;border-radius:10px;background:#FAF7F1;color:#332D28;font:inherit}input{flex:1;min-width:200px}.gallery{display:grid;gap:24px;padding:24px 22px;max-width:1440px;margin:auto}article{min-width:0;padding:20px;border:1px solid #C9BEB0;border-radius:18px;background:#FAF7F1}h2{margin:0;font:400 31px/1.15 'Cormorant Garamond',serif}article>p{overflow-wrap:anywhere;color:#71665C;font-size:10px}.shots{display:grid;grid-template-columns:1fr 1fr;gap:12px}.shots a{display:block;min-width:0}.shots span{display:block;margin:8px 0;font-size:11px}.shots img{display:block;width:100%;height:230px;object-fit:cover;object-position:top;border:1px solid #C9BEB0;border-radius:8px}[hidden]{display:none!important}.status{margin:0 22px;color:#71665C}@media(min-width:768px){header{padding:45px max(42px,calc((100vw - 1356px)/2))}.gallery{grid-template-columns:repeat(2,minmax(0,1fr));padding:32px 42px}.shots img{height:300px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}</style></head><body><header><h1>Манго · страницы сайта</h1><p>33 страницы в двух размерах. Откройте снимок, чтобы рассмотреть страницу целиком, или перейдите на саму страницу по её названию.</p><a href="../../pages.html" data-goal="gallery_directory">Оглавление страниц →</a><div class="controls"><input type="search" aria-label="Найти страницу" placeholder="Найти страницу"><select aria-label="Ширина снимков"><option value="all">Обе ширины</option><option value="390">Телефон · 390 px</option><option value="1440">Компьютер · 1440 px</option></select></div></header><p class="status" aria-live="polite"></p><main class="gallery">'''+cards+'''</main><script>(()=>{const search=document.querySelector('input'),width=document.querySelector('select'),cards=[...document.querySelectorAll('[data-gallery-item]')];function update(){let n=0;cards.forEach(c=>{c.hidden=!c.textContent.toLowerCase().includes(search.value.trim().toLowerCase());if(!c.hidden)n++;c.querySelectorAll('[data-width]').forEach(a=>a.hidden=width.value!=='all'&&a.dataset.width!==width.value);c.querySelector('.shots').style.gridTemplateColumns=width.value==='all'?'1fr 1fr':'1fr';});document.querySelector('.status').textContent='Страниц: '+n;}search.addEventListener('input',update);width.addEventListener('change',update);update();})();</script></body></html>'''
 (OUT/'index.html').write_text(html)
report={'format':'JPEG','quality':75,'reduced_motion':'reduce','scroll_down_and_back':True,'captures':[],'errors':[]}
if '--refresh-countries' in sys.argv or '--refresh-licensed' in sys.argv:report=json.loads((SITE/'SCREENS_QA.json').read_text());report['errors']=[]
async def main():
 async with async_playwright()as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for rec in PAGES:
   if '--refresh-countries' in sys.argv and rec['type']!='country':continue
   if '--refresh-licensed' in sys.argv and rec['path']not in ['index.html','napravleniya/index.html','napravleniya/turciya/index.html','napravleniya/vetnam/index.html','napravleniya/tunis/index.html','napravleniya/greciya/index.html']:continue
   for width in [390,1440]:
    ctx=await browser.new_context(viewport={'width':width,'height':844 if width==390 else 1000},device_scale_factor=1,reduced_motion='reduce',is_mobile=width==390,has_touch=width==390,locale='ru-RU');page=await ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None)
    await page.goto(ORIGIN+rec['path'],wait_until='networkidle');await prepare(page);assert await page.evaluate('document.documentElement.scrollWidth')==width,rec['path'];file=slug(rec['path'])+'-'+str(width)+'.jpg';height=await page.evaluate('Math.max(document.documentElement.scrollHeight,document.body.scrollHeight)');await page.screenshot(path=str(OUT/file),full_page=True,type='jpeg',quality=75);report['captures']=[x for x in report['captures']if x['file']!=file];report['captures'].append({'page':rec['path'],'file':file,'width':width,'height':height});await ctx.close()
   print('Captured',rec['path'],flush=True)
  gallery()
  for width in [390,1440]:
   page=await browser.new_page(viewport={'width':width,'height':844 if width==390 else 1000},reduced_motion='reduce');await page.goto(ORIGIN+'screens/pages/index.html',wait_until='networkidle');await prepare(page);await page.screenshot(path=str(OUT/f'screens-pages-{width}.jpg'),full_page=True,type='jpeg',quality=75);await page.close()
  await browser.close()
 assert not report['errors'],report['errors'];(SITE/'SCREENS_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Captured',len(report['captures']),'page screenshots, plus gallery')
try:asyncio.run(main())
finally:server.shutdown()
