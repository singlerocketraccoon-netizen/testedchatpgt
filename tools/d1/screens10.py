"""Cruise page and request context; prior captures are kept as labelled archive."""
import asyncio,json
import screens8 as shots
from playwright.async_api import async_playwright
from engines7 import launch
shots.report=json.loads((shots.S/'SCREENS_QA.json').read_text());shots.report['page_count']=len(shots.PAGES);updated=[]
async def main():
 async with async_playwright()as p:
  b=await launch(p,'chromium')
  for width in[390,1440]:
   file='otdyh-kruizy-'+str(width)+'.jpg';await shots.take(b,'Chromium','otdyh/kruizy/index.html','Круизы · этап 10',width,file);updated.append(file)
   async def option(page):
    await page.locator('[data-goal=cruise_option_1]').click();await page.locator('#request-dialog').wait_for(state='visible');await page.wait_for_timeout(500)
   file='kruizy-okno-'+str(width)+'.jpg';await shots.take(b,'Chromium','otdyh/kruizy/index.html','Круизы · окно «Речной круиз» · этап 10',width,file,'#request-dialog',option);updated.append(file)
  await b.close()
 assert not shots.report['errors'],shots.report['errors']
 for c in shots.report['captures']:
  if c['file']in updated:c['stage']=10
 shots.report['stage10_updated']=updated;shots.report['screenshot_count']=len(shots.report['captures']);shots.gallery();page=shots.OUT/'index.html';s=page.read_text().replace('после этапа 8: компьютер, телефон и сравнение движков.','Круизы: этап 10, остальные снимки — архив этапов 8–9.').replace('<label>Найти страницу','<p>Круизы и окно с контекстом — этап 10. Остальные снимки сохранены как архив этапов 8–9.</p><label>Найти страницу');page.write_text(s);(shots.S/'SCREENS_QA.json').write_text(json.dumps(shots.report,ensure_ascii=False,indent=2)+'\n');print('Stage 10:',len(updated),'captures; gallery:',len(shots.report['captures']))
if __name__=='__main__':
 try:asyncio.run(main())
 finally:shots.server.shutdown()
