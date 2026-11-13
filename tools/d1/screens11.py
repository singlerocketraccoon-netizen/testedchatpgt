"""Current stage-11 full-page review and focused acceptance captures."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from html import escape as E
import asyncio,json,threading,sys
from PIL import Image
from engines7 import launch
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';OUT=S/'screens/review';DETAIL=S/'screens/pages'
PAGES=[p for p in json.loads((R/'tools/d1/pages.json').read_text())if p['path']not in['pages.html','accent-options.html']]
report={'stage':11,'format':'JPEG','quality':75,'reduced_motion':'reduce','scroll_down_and_back':True,'fonts_ready':True,'extra_wait_ms':500,'page_count':len(PAGES),'captures':[],'errors':[]}
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R/'docs'),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
def slug(p):return p.removesuffix('index.html').strip('/').removesuffix('.html').replace('/','-')or'index'
async def ready(p):
 await p.evaluate('''async()=>{document.querySelectorAll('img').forEach(i=>i.loading='eager');const wait=()=>new Promise(r=>setTimeout(r,20));for(let y=0;y<document.documentElement.scrollHeight-innerHeight;y+=innerHeight*.9){scrollTo(0,y);await wait();}scrollTo(0,document.documentElement.scrollHeight);await wait();scrollTo(0,0);await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));}''');await p.wait_for_timeout(500);await p.mouse.move(0,0);await p.evaluate('window.MangoLayout?.refresh()');await p.wait_for_timeout(100)
async def capture(b,path,title,width,file,selector=None,state=None):
 ctx=await b.new_context(viewport={'width':width,'height':844 if width==390 else 900},device_scale_factor=2 if width==390 else 1,reduced_motion='reduce',locale='ru-RU');p=await ctx.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)));p.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None)
 await p.goto(BASE+path,wait_until='load')
 if path=='o-nas/komanda/index.html':await p.wait_for_url('**/o-nas/index.html#team')
 await ready(p)
 if state:await state(p);await p.evaluate('window.MangoLayout?.refresh()');await p.wait_for_timeout(150)
 assert await p.evaluate('document.documentElement.scrollWidth')==width,(path,width)
 dest=(DETAIL if selector or file.startswith(('stage11-','stage12-'))else OUT)/file;dest.parent.mkdir(parents=True,exist_ok=True)
 if selector and selector!='@viewport':
  await p.add_style_tag(content='.d1-header,.mobile-contact,.skip-link{visibility:hidden!important}');await p.locator(selector).screenshot(path=str(dest),type='jpeg',quality=75)
 elif selector=='@viewport':
  assert await p.locator('.dropdown-panel:visible').count()==1
  await p.screenshot(path=str(dest),type='jpeg',quality=75,full_page=False)
 else:await p.screenshot(path=str(dest),type='jpeg',quality=75,full_page=True)
 im=Image.open(dest);report['captures'].append(dict(page=path,title=title,file=file,width=width,engine='Chromium',device_scale_factor=2 if width==390 else 1,pixel_width=im.width,pixel_height=im.height,kind='component'if selector else'page',directory='pages'if dest.parent==DETAIL else'review',stage=report.get('stage',11)));await ctx.close()
def gallery(folder,items,archive=False):
 groups={}
 for c in items:groups.setdefault((c['page'],c['title']),[]).append(c)
 cards=''
 for i,((path,title),captures)in enumerate(groups.items()):
  cards+='<article class="gallery-card" data-gallery-item data-title="'+E(title,quote=True)+'"><h2><a href="../../'+path+'" data-goal="gallery_page_'+str(i)+'">'+E(title)+'</a></h2><p>'+E(path)+'</p><div class="gallery-shots">'+''.join('<a href="'+c['file']+'" data-goal="gallery_shot_'+str(i)+'_'+str(c['width'])+'"><span>'+str(c['width'])+' px ↗</span><img src="'+c['file']+'" alt="'+E(title,quote=True)+' — '+str(c['width'])+' px" width="'+str(c['pixel_width'])+'" height="'+str(c['pixel_height'])+'" loading="lazy"></a>'for c in captures)+'</div></article>'
 text=f"Текущие страницы после этапа {report.get('stage',11)}."if not archive else f"Детали этапа {report.get('stage',11)} и подписанный архив предыдущих этапов. Полный комплект текущих страниц — в соседней галерее."
 html='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="'+text+'"><title>Галерея страниц — Mango Travel</title>'+''.join('<link rel="stylesheet" href="../../css/'+n+'.css">'for n in['tokens','fonts','base','gallery'])+'<script defer src="../../js/gallery.js"></script></head><body class="gallery-page"><main class="gallery-main"><header><h1>Страницы Mango Travel</h1><p>'+text+'</p><p>'+str(len(items))+' снимков</p><a href="../'+('review'if archive else'pages')+'/index.html">'+('Все текущие страницы'if archive else'Детали и архив')+' →</a><label>Найти страницу<input type="search" data-gallery-search autocomplete="off"></label></header>'+cards+'</main></body></html>\n'
 (folder/'index.html').write_text(html)
async def main():
 if '--requisites'in sys.argv:
  report.update(json.loads((S/'SCREENS_REVIEW_QA.json').read_text()));path='o-nas/dokumenty/rekvizity/index.html';report['captures']=[c for c in report['captures']if c['page']!=path]
  async with async_playwright()as pw:
   b=await launch(pw,'chromium')
   async def document(p):await p.locator('[data-agency-document]').first.click();await p.locator('.agency-file-dialog[open]').wait_for(state='visible')
   for w in[390,1440]:
    await capture(b,path,'Реквизиты и реестр турагентов',w,slug(path)+'-'+str(w)+'.jpg')
    await capture(b,path,'Реквизиты · этап 11',w,'stage11-rekvizity-'+str(w)+'.jpg')
    await capture(b,path,'Окно документа · этап 11',w,'stage11-dokument-'+str(w)+'.jpg','.agency-file-dialog[open]',document)
   await capture(b,path,'Перенос крошек · этап 11',390,'stage11-kroshki-rekvizity-390.jpg','.breadcrumbs');await b.close()
  assert not report['errors'],report['errors'];gallery(OUT,[c for c in report['captures']if c['directory']=='review']);previous=json.loads((S/'SCREENS_QA.json').read_text());fresh=[c for c in report['captures']if c['directory']=='pages'and c['page']==path];names={c['file']for c in fresh};previous['captures']=[c for c in previous['captures']if c['file']not in names]+fresh;gallery(DETAIL,[c for c in previous['captures']if c.get('stage')==11]+[c for c in previous['captures']if c.get('stage')!=11],True);(S/'SCREENS_QA.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n');(S/'SCREENS_REVIEW_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return
 if '--page'in sys.argv:
  saved=json.loads((S/'SCREENS_REVIEW_QA.json').read_text());report.update(saved);paths=sys.argv[sys.argv.index('--page')+1:];report['captures']=[c for c in report['captures']if c['page']not in paths or c['directory']!='review']
  async with async_playwright()as pw:
   b=await launch(pw,'chromium')
   for row in PAGES:
    if row['path']in paths:
     for w in[390,1440]:await capture(b,row['path'],row['title'],w,slug(row['path'])+'-'+str(w)+'.jpg')
   await b.close()
  gallery(OUT,[c for c in report['captures']if c['directory']=='review']);(S/'SCREENS_REVIEW_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return
 async with async_playwright()as pw:
  b=await launch(pw,'chromium')
  for row in PAGES:
   for w in[390,1440]:await capture(b,row['path'],row['title'],w,slug(row['path'])+'-'+str(w)+'.jpg')
   print('Full',row['path'],flush=True)
  for path,title in[('index.html','Главная'),('otdyh/otdyh-s-detmi/index.html','Отдых с детьми'),('otdyh/tishina-i-more/index.html','Тишина и море'),('napravleniya/egipet/index.html','Египет')]:await capture(b,path,title,2560,slug(path)+'-2560.jpg')
  async def moods(p):await p.locator('[data-rest-toggle]').click()
  async def checks(p):await p.locator('#checks details').evaluate_all('els=>els.forEach(e=>e.open=true)')
  async def document(p):await p.locator('[data-agency-document]').first.click();await p.locator('.agency-file-dialog[open]').wait_for(state='visible')
  for w in[1440,2560]:await capture(b,'index.html','Отдых по душе · этап 11',w,'stage11-otdyh-'+str(w)+'.jpg','#moods',moods)
  for path,title,name,selector,state in[
   ('otdyh/otdyh-s-detmi/index.html','Куда поехать с детьми','deti-strany','#countries',None),
   ('otdyh/tishina-i-more/index.html','Тихий отдых бывает разным','tishina-formaty','#types',None),
   ('otdyh/otdyh-s-detmi/index.html','Что мы проверяем · раскрытые примеры','proverki','#checks',checks),
   ('napravleniya/egipet/index.html','Показатели Египта','egipet-cifry','.country-temperature',None),
   ('napravleniya/egipet/index.html','Своя стрелка select','select','#season .country-select',None),
  ]:await capture(b,path,title+' · этап 11',1440,'stage11-'+name+'-1440.jpg',selector,state)
  for w in[1440,390]:
   await capture(b,'o-nas/otzyvy/index.html','Отзывы · этап 11',w,'stage11-otzyvy-'+str(w)+'.jpg')
   await capture(b,'o-nas/dokumenty/rekvizity/index.html','Реквизиты · этап 11',w,'stage11-rekvizity-'+str(w)+'.jpg')
   await capture(b,'o-nas/dokumenty/rekvizity/index.html','Окно документа · этап 11',w,'stage11-dokument-'+str(w)+'.jpg','.agency-file-dialog[open]',document)
  for path,name in[('o-nas/dokumenty/rekvizity/index.html','rekvizity'),('otdyh/kruizy/index.html','kruizy')]:await capture(b,path,'Перенос крошек · этап 11',390,'stage11-kroshki-'+name+'-390.jpg','.breadcrumbs')
  await b.close()
 assert not report['errors'],report['errors']
 full=[c for c in report['captures']if c['directory']=='review'];wanted={c['file']for c in full}
 for f in OUT.glob('*.jpg'):
  if f.name not in wanted:f.unlink()
 gallery(OUT,full)
 previous=json.loads((S/'SCREENS_QA.json').read_text());detail=[c for c in report['captures']if c['directory']=='pages'];new={c['file']for c in detail};previous['captures']=[dict(c,title=c['title']+' · архив')for c in previous['captures']if c['file']not in new and c.get('stage')!=11]+detail;previous.update(stage11_updated=[c['file']for c in detail],screenshot_count=len(previous['captures']));gallery(DETAIL,detail+[c for c in previous['captures']if c.get('stage')!=11],True);(S/'SCREENS_QA.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n')
 report.update(full_page_count=len(full),detail_count=len(detail),status='passed');(S/'SCREENS_REVIEW_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Captured',len(full),'full pages and',len(detail),'details',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown()
