"""Stage 13.4: content-height internal covers on the requested viewports."""
import asyncio,json
import screens13 as m
from playwright.async_api import async_playwright
from engines7 import launch
m.OUT=m.S/'screens/stage13-4';m.OUT.mkdir(parents=True,exist_ok=True)
m.PAGES=[('napravleniya/egipet/index.html','Египет','egipet'),('otdyh/otdyh-s-detmi/index.html','Отдых с детьми','deti')]
m.report.update(stage='13.4',captures=[])
async def main():
 async with async_playwright()as pw:
  browser=await launch(pw,'chromium')
  for path,title,key in m.PAGES:
   for w,h in[(1366,768),(2560,1336)]:await m.take(browser,path,title+' · высота по содержимому',key,w,h)
  await browser.close()
 assert not m.report['errors'],m.report['errors'];m.report['status']='passed';(m.S/'SCREENS13_4.json').write_text(json.dumps(m.report,ensure_ascii=False,indent=2)+'\n');m.gallery();p=m.OUT/'index.html';p.write_text(p.read_text().replace('Этап 13','Этап 13.4').replace('Пять страниц на восьми экранах, полные страницы для компьютера и дополнительные состояния.','Обложки Египта и отдыха с детьми на 1366×768 и 2560×1336. Высота внутренних обложек снова определяется содержимым.'));print(len(m.report['captures']),'JPEG passed',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:m.server.shutdown()
