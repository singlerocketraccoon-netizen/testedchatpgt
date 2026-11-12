#!/usr/bin/env python3
"""Fresh gallery for every live page and the required schema 12.11 UI states."""
import asyncio,json,sys
from playwright.async_api import async_playwright
import screens as s
s.DETAILS=[{'path':'index.html','title':'Форма подбора в окне','file_slug':'forma-podbor'},{'path':'predlozheniya/e1/index.html','title':'Форма предложения в окне','file_slug':'forma-predlozhenie'},{'path':'uslugi/index.html#visas','title':'Форма услуги в окне','file_slug':'forma-usluga'},{'path':'index.html','title':'Помогите выбрать','file_slug':'okno-pomogite'},{'path':'index.html','title':'Меню: телефон и компьютер','file_slug':'menu'},{'path':'uslugi/index.html#visas','title':'Услуги · открытый пункт','file_slug':'uslugi-otkrytyy-punkt'}]+[{'path':'index.html','title':'Главная · слайд '+str(i),'file_slug':'glavnaya-slayd-'+str(i)}for i in range(1,5)]+[{'path':'index.html#moods','title':'Главная · все виды отдыха','file_slug':'glavnaya-otdyh'},{'path':'index.html#offers','title':'Главная · предложения','file_slug':'glavnaya-predlozheniya'}]
s.GALLERY=s.PAGES+s.DETAILS
s.report={'format':'JPEG','quality':75,'reduced_motion':'reduce','scroll_down_and_back':True,'fonts_ready':True,'extra_wait_ms':500,'page_count':len(s.PAGES),'detail_count':len(s.DETAILS)*2,'captures':[],'errors':[]}
partial=bool(sys.argv[1:])
if partial:s.report=json.loads((s.SITE/'SCREENS_QA.json').read_text())
async def context(browser,width):return await browser.new_context(viewport={'width':width,'height':900 if width==1440 else 844},device_scale_factor=2 if width==390 else 1,reduced_motion='reduce',is_mobile=width==390,has_touch=width==390,locale='ru-RU')
async def capture(page,path,file,width,full=True,locator=None):
 s.report['captures']=[r for r in s.report['captures']if r['file']!=file]
 await page.evaluate('document.fonts.ready');await page.wait_for_timeout(500);assert await page.evaluate('document.documentElement.scrollWidth')==width,path
 if locator:await page.locator(locator).screenshot(path=str(s.OUT/file),type='jpeg',quality=75,style='.d1-header,.mobile-contact,.skip-link { visibility:hidden!important; }')
 else:await page.screenshot(path=str(s.OUT/file),full_page=full,type='jpeg',quality=75)
 s.record(path,file,width,'page'if full and not locator else'component'if locator else'dialog')
async def main():
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for record in [r for r in s.PAGES if not partial or r['path']in sys.argv[1:]]:
   for width in[390,1440]:
    ctx=await context(b,width);page=await ctx.new_page();page.on('pageerror',lambda e:s.report['errors'].append(str(e)));page.on('console',lambda m:s.report['errors'].append(m.text)if m.type=='error'else None);await page.goto(s.ORIGIN+record['path'],wait_until='networkidle')
    if record['type']=='redirect':await page.wait_for_url('**/o-nas/index.html#team')
    await s.prepare(page);await capture(page,record['path'],s.slug(record['path'])+'-'+str(width)+'.jpg',width);await ctx.close()
   print('Captured',record['path'],flush=True)
  for record in ([]if partial else s.DETAILS):
   for width in[390,1440]:
    ctx=await context(b,width);page=await ctx.new_page();await page.goto(s.ORIGIN+record['path'],wait_until='networkidle');await s.prepare(page);slug=record['file_slug'];locator=None;full=False
    if slug=='forma-podbor':await page.locator('.hero-slide.is-active [data-open-form]').click()
    elif slug=='forma-predlozhenie':await page.locator('main [data-open-form^="offer:"]').first.click()
    elif slug=='forma-usluga':await page.locator('#visas summary').evaluate('n=>n.parentElement.open=true');await page.locator('#visas [data-open-form]').click()
    elif slug=='okno-pomogite':await page.locator('[data-goal=rest_help]').click()
    elif slug=='menu':await page.locator('[data-menu]'if width==390 else'[aria-controls=nav-countries]').click()
    elif slug=='uslugi-otkrytyy-punkt':await page.locator('#visas').evaluate('n=>n.open=true');full=True
    elif slug.startswith('glavnaya-slayd-'):
     for i in range(int(slug.rsplit('-',1)[1])-1):await page.locator('[data-hero-next]').click()
    elif slug=='glavnaya-otdyh':await page.locator('[data-rest-toggle]').click();locator='.mood-section'
    elif slug=='glavnaya-predlozheniya':locator='#offers'
    await capture(page,record['path'],slug+'-'+str(width)+'.jpg',width,full,locator);await ctx.close()
   print('Captured state',record['file_slug'],flush=True)
  await b.close()
 assert not s.report['errors'],s.report['errors'];wanted={r['file']for r in s.report['captures']}
 for p in s.OUT.glob('*.jpg'):
  if p.name not in wanted:p.unlink()
 s.gallery();s.report['screenshot_count']=len(s.report['captures']);(s.SITE/'SCREENS_QA.json').write_text(json.dumps(s.report,ensure_ascii=False,indent=2)+'\n');print('Gallery:',len(s.PAGES),'pages,',len(s.report['captures']),'JPEG')
if __name__=='__main__':
 try:asyncio.run(main())
 finally:s.server.shutdown()
