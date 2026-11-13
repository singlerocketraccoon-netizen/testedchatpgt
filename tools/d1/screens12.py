"""Stage 12 current review pages and customer-requested details; JPEG 75."""
import asyncio,json,sys
import screens11 as shots
from playwright.async_api import async_playwright
from engines7 import launch
shots.report.update(stage=12,captures=[],errors=[])
async def main():
 if '--menus'in sys.argv:
  shots.report.update(json.loads((shots.S/'SCREENS_REVIEW_QA.json').read_text()));shots.report['captures']=[c for c in shots.report['captures']if not c['file'].startswith('stage12-menu-')]
 async with async_playwright()as pw:
  b=await launch(pw,'chromium')
  if '--menus'not in sys.argv:
   for row in shots.PAGES:
    for w in[390,1440]:await shots.capture(b,row['path'],row['title'],w,shots.slug(row['path'])+'-'+str(w)+'.jpg')
    print('Captured',row['path'],flush=True)
   for path,title in[('index.html','Главная'),('otdyh/otdyh-s-detmi/index.html','Отдых с детьми'),('otdyh/tishina-i-more/index.html','Тишина и море'),('napravleniya/egipet/index.html','Египет')]:await shots.capture(b,path,title,2560,shots.slug(path)+'-2560.jpg')
  for w in[1440,2560]:
   for key,title in[('countries','Страны'),('services','Услуги'),('about','О нас')]:
    async def opened(p,key=key):await p.locator('[aria-controls="nav-'+key+'"]').click();await p.locator('#nav-'+key).wait_for(state='visible')
    await shots.capture(b,'index.html','Меню '+title+' · этап 12',w,'stage12-menu-'+key+'-'+str(w)+'.jpg','@viewport',opened)
   async def compact(p):await p.evaluate('scrollTo(0,500)');await p.wait_for_timeout(100);await p.locator('[aria-controls="nav-services"]').click();await p.locator('#nav-services').wait_for(state='visible')
   # Viewport capture keeps the scrolled header state; full-page capture would scroll it back.
   await shots.capture(b,'index.html','Меню услуг после прокрутки · этап 12',w,'stage12-menu-services-scroll-'+str(w)+'.jpg','@viewport',compact)
  if '--menus'not in sys.argv:
   await shots.capture(b,'index.html','Отдых по душе · этап 12',1440,'stage12-otdyh-1440.jpg','#moods')
   for w in[1024,1440]:await shots.capture(b,'otdyh/tishina-i-more/index.html','Куда поехать за тишиной · этап 12',w,'stage12-tishina-strany-'+str(w)+'.jpg','#countries')
   for w in[390,1440]:await shots.capture(b,'predlozheniya/e1/index.html','Предложение e1 · этап 12',w,'stage12-e1-'+str(w)+'.jpg')
   for path,title,name in[('o-nas/dokumenty/index.html','Документы','dokumenty'),('o-nas/dokumenty/rekvizity/index.html','Реквизиты','rekvizity')]:await shots.capture(b,path,title+' · этап 12',1440,'stage12-'+name+'-1440.jpg')
   async def first(p):await p.locator('#checks [data-accordion-order="0"]').evaluate('e=>e.open=true')
   await shots.capture(b,'otdyh/otdyh-s-detmi/index.html','Что мы проверяем · этап 12',1440,'stage12-checks-1440.jpg','#checks',first)
  await b.close()
 assert not shots.report['errors'],shots.report['errors']
 full=[c for c in shots.report['captures']if c['directory']=='review'];details=[c for c in shots.report['captures']if c['directory']=='pages'];assert len(full)==88 and len(details)==16,(len(full),len(details))
 for c in shots.report['captures']:c['stage']=12
 shots.gallery(shots.OUT,full);f=shots.OUT/'index.html';f.write_text(f.read_text().replace('этапа 11','этапа 12'))
 prev=json.loads((shots.S/'SCREENS_QA.json').read_text());names={c['file']for c in details};old=[dict(c,title=c['title']if 'архив'in c['title']else c['title']+' · архив')for c in prev['captures']if c['file']not in names];prev['captures']=details+old;prev.update(stage12_updated=[c['file']for c in details],screenshot_count=len(prev['captures']));shots.gallery(shots.DETAIL,prev['captures'],True);f=shots.DETAIL/'index.html';f.write_text(f.read_text().replace('этапа 11','этапа 12'));(shots.S/'SCREENS_QA.json').write_text(json.dumps(prev,ensure_ascii=False,indent=2)+'\n')
 shots.report.update(full_page_count=len(full),detail_count=len(details),status='passed');(shots.S/'SCREENS_REVIEW_QA.json').write_text(json.dumps(shots.report,ensure_ascii=False,indent=2)+'\n');print('Screens:',len(full),'full,',len(details),'details',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:shots.server.shutdown()
