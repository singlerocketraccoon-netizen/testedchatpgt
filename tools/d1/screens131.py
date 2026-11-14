"""Stage 13.1 review evidence, using the shared font/image preparation."""
import asyncio,json,io
from PIL import Image
import screens13 as m
from playwright.async_api import async_playwright
from engines7 import launch
m.OUT=m.S/'screens/stage13-1';m.OUT.mkdir(parents=True,exist_ok=True)
m.PAGES=[('index.html','Главная','glavnaya'),('napravleniya/egipet/index.html','Египет','egipet'),('o-nas/index.html','О нас','o-nas'),('o-nas/kontakty/index.html','Контакты','kontakty'),('PHOTOS13_1.html','Фото и лицензии','photos')]
m.report.update(stage='13.1',captures=[])
async def prepare(page):
 await page.evaluate("""async()=>{document.querySelectorAll('img').forEach(i=>i.loading='eager');for(let y=0;y<document.documentElement.scrollHeight-innerHeight;y+=innerHeight*.9){scrollTo(0,y);await new Promise(r=>setTimeout(r,15));}scrollTo(0,document.documentElement.scrollHeight);scrollTo(0,0);await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));window.MangoLayout?.refresh();}""");await page.wait_for_timeout(500)
m.prepare=prepare
async def hide_nav(page):await page.add_style_tag(content='.country-page-nav{visibility:hidden!important}')
original_take=m.take
async def take(browser,path,title,name,w,h,full=False,state=None,locator=None):
 if not locator:return await original_take(browser,path,title,name,w,h,full,state,locator)
 scale=2 if w<=430 or h<=430 else 1
 ctx=await browser.new_context(viewport={'width':w,'height':h},device_scale_factor=scale,reduced_motion='reduce',locale='ru-RU');page=await ctx.new_page();page.on('pageerror',lambda e:m.report['errors'].append(str(e)));page.on('console',lambda msg:m.report['errors'].append(msg.text)if msg.type=='error'else None);await page.goto(m.BASE+path);await prepare(page)
 if state:await state(page)
 await page.add_style_tag(content='.d1-header,.contact-dock,.country-page-nav,.rest-page-nav{visibility:hidden!important}');await page.evaluate('scrollTo(0,0)');await page.wait_for_timeout(150);box=await page.locator(locator).bounding_box();raw=await page.screenshot(type='jpeg',quality=90,full_page=True);image=Image.open(io.BytesIO(raw));image=image.crop(tuple(round(v*scale)for v in[box['x'],box['y'],box['x']+box['width'],box['y']+box['height']]));file=name+'-'+str(w)+'x'+str(h)+'.jpg';image.save(m.OUT/file,format='JPEG',quality=75);m.report['captures'].append(dict(page=path,title=title,file=file,width=w,height=h,pixel_width=image.width,pixel_height=image.height,device_scale_factor=scale,full_page=False));await ctx.close()
m.take=take
async def main():
 async with async_playwright()as pw:
  b=await launch(pw,'chromium')
  for w in[1440,1024,768,390]:await m.take(b,'index.html','Как мы работаем на главной','glavnaya-process',w,900 if w>390 else 844,locator='#process')
  for id,title in[('resorts','Где отдыхать'),('experiences','Чем заняться')]:await m.take(b,'napravleniya/egipet/index.html',title,'egipet-'+id,1440,900,locator='#'+id,state=hide_nav)
  for path,name,title in[('o-nas/index.html','o-nas','О нас'),('o-nas/kontakty/index.html','kontakty','Контакты')]:
   for w,h in[(1440,900),(390,844)]:await m.take(b,path,title,name,w,h)
  await m.take(b,'napravleniya/egipet/index.html','Форма на ширине 960','forma',960,900,locator='#inquiry .messenger-card')
  await m.take(b,'index.html','Слайдер на коротком телефоне','slider',320,568)
  await m.take(b,'PHOTOS13_1.html','Фото и лицензии','photos',1440,900)
  await m.take(b,'PHOTOS13_1.html','Фото и лицензии целиком','photos',1440,900,True)
  await b.close()
 assert not m.report['errors'],m.report['errors'];m.report['status']='passed';(m.S/'SCREENS13_1.json').write_text(json.dumps(m.report,ensure_ascii=False,indent=2)+'\n');m.gallery();file=m.OUT/'index.html';html=file.read_text().replace('Этап 13','Этап 13.1').replace('Пять страниц на восьми экранах, полные страницы для компьютера и дополнительные состояния.','Исправленные этапы главной, фото Египта, верх внутренних страниц, форма и полный реестр изображений.');html=html.replace('</head>','<link rel="icon" type="image/svg+xml" href="../../img/logo-mango-mark.svg"></head>');file.write_text(html);print(len(m.report['captures']),'JPEG passed',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:m.server.shutdown()
