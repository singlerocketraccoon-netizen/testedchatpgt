"""Requested stage-9 states only. Earlier gallery captures retain stage-8 labels."""
import asyncio,json
import screens8 as shots
from playwright.async_api import async_playwright
from engines7 import launch
shots.report=json.loads((shots.S/'SCREENS_QA.json').read_text());updated=[]
async def take(browser,path,title,width,file,locator=None,state=None):
 await shots.take(browser,'Chromium',path,title,width,file,locator,state);updated.append(file)
 for row in shots.report['captures']:
  if row['file']==file:row['stage']=9
async def main():
 async with async_playwright()as p:
  b=await launch(p,'chromium')
  async def hurghada(page):
   await page.locator('[data-resort-card=hurghada] details').evaluate('e=>e.open=true');await page.evaluate('scrollTo(0,0)');await page.wait_for_timeout(500)
  await take(b,'napravleniya/egipet/index.html','Египет · раскрытая Хургада · этап 9',1440,'napravleniya-egipet-1440.jpg',state=hurghada)
  await take(b,'napravleniya/egipet/index.html','Египет · карточки курортов · этап 9',1440,'egipet-kurort-1440.jpg','#resorts',hurghada)
  for slug,title in [('turciya','Турция'),('kitay','Китай')]:await take(b,'napravleniya/'+slug+'/index.html',title+' · этап 9',1440,'napravleniya-'+slug+'-1440.jpg')
  await take(b,'otdyh/svoj-marshrut/index.html','Свой маршрут · этап 9',1440,'otdyh-svoj-marshrut-1440.jpg')
  for width in[390,1440]:await take(b,'napravleniya/egipet/index.html','Строка согласия · этап 9',width,'soglasie-'+str(width)+'.jpg','[data-country-inquiry='+('top'if width==1440 else'bottom')+'] .unified-consent')
  for path,slug,title in [('index.html','glavnaya','Предложения на главной'),('napravleniya/egipet/index.html','egipet','Предложения Египта')]:await take(b,path,title+' · этап 9',390,'predlozheniya-'+slug+'-390.jpg','#offers')
  for width in[1024,1280]:await take(b,'index.html','Шапка · этап 9',width,'shapka-'+str(width)+'.jpg','.d1-header')
  await b.close()
 assert not shots.report['errors'],shots.report['errors'];shots.report['screenshot_count']=len(shots.report['captures']);shots.report['stage9_updated']=updated;shots.gallery()
 gallery=shots.OUT/'index.html';html=gallery.read_text().replace('после этапа 8: компьютер, телефон и сравнение движков.','Этап 9: обновлённые состояния и архив этапа 8.');html=html.replace('<label>Найти страницу','<p>Снимки с подписью «этап 9» обновлены. Остальные сохранены как архив этапа 8.</p><label>Найти страницу');gallery.write_text(html)
 (shots.S/'SCREENS_QA.json').write_text(json.dumps(shots.report,ensure_ascii=False,indent=2)+'\n');print('Stage 9:',len(updated),'captures; gallery:',shots.report['screenshot_count'])
if __name__=='__main__':
 try:asyncio.run(main())
 finally:shots.server.shutdown()
