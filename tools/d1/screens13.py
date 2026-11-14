"""Requested viewport evidence plus full desktop pages for design review."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from html import escape as E
import asyncio,json,threading,sys
from playwright.async_api import async_playwright
from engines7 import launch
from PIL import Image
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';OUT=S/'screens/stage13';OUT.mkdir(parents=True,exist_ok=True)
PAGES=[('index.html','Главная','glavnaya'),('uslugi/index.html','Услуги','uslugi'),('kak-my-rabotaem/index.html','Как мы работаем','kak-my-rabotaem'),('napravleniya/egipet/index.html','Египет','egipet'),('o-nas/kontakty/index.html','Контакты','kontakty')];SIZES=[(320,568),(390,844),(844,390),(768,1024),(1024,600),(1366,768),(1440,900),(2560,1440)]
report={'stage':13,'captures':[],'errors':[],'quality':75,'format':'JPEG','fonts_ready':True,'reduced_motion':'reduce','scroll_down_and_back':True,'extra_wait_ms':500}
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(R/'docs'),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
async def prepare(p):
 await p.evaluate('''async()=>{document.querySelectorAll('img').forEach(i=>i.loading='eager');for(let y=0;y<document.documentElement.scrollHeight-innerHeight;y+=innerHeight*.9){scrollTo(0,y);await new Promise(r=>setTimeout(r,15));}scrollTo(0,document.documentElement.scrollHeight);await new Promise(r=>setTimeout(r,15));scrollTo(0,0);await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));}''');await p.wait_for_timeout(500);await p.mouse.move(0,0);await p.evaluate('MangoLayout.refresh()');await p.wait_for_timeout(100)
async def take(b,path,title,name,w,h,full=False,state=None,locator=None):
 d=2 if w<=430 or h<=430 else 1;ctx=await b.new_context(viewport={'width':w,'height':h},device_scale_factor=d,reduced_motion='reduce',locale='ru-RU');p=await ctx.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)));p.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None);await p.goto(BASE+path);await prepare(p)
 if state:await state(p);await p.wait_for_timeout(200)
 file=name+'-'+str(w)+'x'+str(h)+('-full'if full else'')+'.jpg';assert await p.evaluate('document.documentElement.scrollWidth')==w,(path,w)
 if locator:
  await p.add_style_tag(content='.d1-header,.contact-dock{visibility:hidden!important}');await p.locator(locator).screenshot(path=str(OUT/file),type='jpeg',quality=75)
 else:await p.screenshot(path=str(OUT/file),type='jpeg',quality=75,full_page=full)
 im=Image.open(OUT/file);report['captures'].append(dict(page=path,title=title,file=file,width=w,height=h,pixel_width=im.width,pixel_height=im.height,device_scale_factor=d,full_page=full));await ctx.close()
def gallery():
 blocks=''
 for path,title,key in PAGES:
  items=[c for c in report['captures']if c['page']==path];blocks+='<article><h2><a href="../../'+path+'" data-goal="gallery_'+key+'">'+E(title)+'</a></h2><div class="shots">'+''.join('<a href="'+c['file']+'" data-goal="shot_'+str(i)+'"><span>'+E(c['title'])+' · '+str(c['width'])+' × '+str(c['height'])+(' · целиком'if c['full_page']else'')+'</span><img src="'+c['file']+'" alt="'+E(c['title'],quote=True)+'" width="'+str(c['pixel_width'])+'" height="'+str(c['pixel_height'])+'" loading="lazy"></a>'for i,c in enumerate(items))+'</div></article>'
 (OUT/'index.html').write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Этап 13 — просмотр страниц</title><link rel="stylesheet" href="../../css/tokens.css"><link rel="stylesheet" href="../../css/fonts.css"><style>body{margin:0;padding:20px;color:var(--ink);background:var(--paper);font:16px/1.6 var(--body)}main{max-width:1400px;margin:auto}h1,h2{font-family:var(--display);font-weight:400}h1{font-size:40px}h2{font-size:30px}a{color:inherit}article{margin-block:36px}.shots{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:18px}.shots>a{display:block;padding:12px;border:1px solid var(--line);border-radius:18px;text-decoration:none;background:var(--cream)}.shots span{display:block;min-height:48px;font-size:13px}.shots img{display:block;width:100%;height:300px;object-fit:contain;object-position:top}:focus-visible{outline:3px solid var(--clay)}</style></head><body><main><h1>Этап 13 · страницы и состояния</h1><p>Пять страниц на восьми экранах, полные страницы для компьютера и дополнительные состояния. Откройте снимок, чтобы увидеть его в исходном размере.</p>'+blocks+'</main></body></html>\n')
async def main():
 if '--desktop'in sys.argv:
  report.update(json.loads((S/'SCREENS13.json').read_text()));report['captures']=[c for c in report['captures']if c['width']<1280]
 async with async_playwright()as pw:
  b=await launch(pw,'chromium')
  for path,title,key in PAGES:
   for w,h in SIZES:
    if '--desktop'not in sys.argv or w>=1280:await take(b,path,title,key,w,h)
   await take(b,path,title,key,1440,900,True);print('Captured',path,flush=True)
  for w,h in[(1440,900),(2560,1440)]:
   async def menu(p):await p.locator('[aria-controls="nav-services"]').click();await p.wait_for_timeout(220);assert await p.locator('#nav-services').is_visible()
   await take(b,'index.html','Открытое меню «Услуги»','menu-uslugi',w,h,state=menu)
  async def expanded(p):await p.locator('.country-hero-form .unified-options').evaluate('e=>e.open=true')
  await take(b,'napravleniya/egipet/index.html','Форма с дополнительными полями','forma-details',1440,900,state=expanded,locator='.country-hero-form .messenger-card')
  async def dialog(p):await p.locator('.country-mobile-hero [data-open-form]').click();await p.locator('#request-dialog .unified-options:visible').evaluate('e=>e.open=true')
  if '--desktop'not in sys.argv:await take(b,'napravleniya/egipet/index.html','Окно с дополнительными полями','forma-dialog',390,844,state=dialog)
  await b.close()
 assert not report['errors'],report['errors'];assert len(report['captures'])==49;gallery();report['status']='passed';(S/'SCREENS13.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('49 JPEG captures passed',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown()
