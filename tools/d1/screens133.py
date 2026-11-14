"""Stage 13.3: viewport-height covers, navigation and matching section width."""
import asyncio,json
from PIL import Image
import screens13 as m
from playwright.async_api import async_playwright
from engines7 import launch
m.OUT=m.S/'screens/stage13-3';m.OUT.mkdir(parents=True,exist_ok=True)
m.PAGES=[('index.html','Главная','glavnaya'),('napravleniya/egipet/index.html','Египет','egipet'),('otdyh/otdyh-s-detmi/index.html','Отдых с детьми','deti')]
m.report.update(stage='13.3',captures=[])
async def main():
 async with async_playwright()as pw:
  b=await launch(pw,'chromium')
  for path,title,key in m.PAGES:
   for w,h in[(1366,768),(1920,1080),(2560,1336)]:await m.take(b,path,title+' · первый экран',key,w,h)
  await m.take(b,'index.html','Главная · первый экран телефона','glavnaya',390,844)
  await m.take(b,'index.html','Отдых, который Вам по душе · ширина секции','otdyh',1920,1080,locator='#moods')
  # Crop the actual header from the first-screen capture; its layout stays untouched.
  im=Image.open(m.OUT/'glavnaya-1920x1080.jpg');im.crop((0,0,1920,88)).save(m.OUT/'shapka-1920x1080.jpg',quality=75)
  m.report['captures'].append(dict(page='index.html',title='Шапка главной',file='shapka-1920x1080.jpg',width=1920,height=1080,pixel_width=1920,pixel_height=88,device_scale_factor=1,full_page=False))
  await b.close()
 assert not m.report['errors'],m.report['errors'];m.report['status']='passed';(m.S/'SCREENS13_3.json').write_text(json.dumps(m.report,ensure_ascii=False,indent=2)+'\n');m.gallery();p=m.OUT/'index.html';p.write_text(p.read_text().replace('Этап 13','Этап 13.3').replace('Пять страниц на восьми экранах, полные страницы для компьютера и дополнительные состояния.','Первые экраны на трёх размерах компьютера, главная на телефоне, шапка и ширина блока отдыха.'));print(len(m.report['captures']),'JPEG passed',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:m.server.shutdown()
