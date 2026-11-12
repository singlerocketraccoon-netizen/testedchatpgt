#!/usr/bin/env python3
"""Refresh stage 5 pages and all four hero slides; retain other unchanged captures."""
import asyncio,json,sys
from pathlib import Path
from playwright.async_api import async_playwright
import screens as s
s.report=json.loads((s.SITE/'SCREENS_QA.json').read_text())
s.report['captures']=[r for r in s.report['captures']if not any('/'+x+'/'in r['page']for x in['tunis','greciya','kipr','bolgariya'])]
s.DETAILS += [{'path':'index.html','title':'Главная · слайд '+str(i),'file_slug':'glavnaya-slayd-'+str(i)}for i in range(1,5)]
s.GALLERY=s.PAGES+s.DETAILS
paths=['index.html','kak-my-rabotaem/index.html','napravleniya/index.html']+[p['path']for p in s.PAGES if p['path'].startswith('napravleniya/')and p['path']!='napravleniya/index.html']
if len(sys.argv)>1:paths=sys.argv[1:]
async def main():
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for path in paths:
   for width in[390,1440]:
    ctx=await b.new_context(viewport={'width':width,'height':844 if width==390 else 900},device_scale_factor=2 if width==390 else 1,reduced_motion='reduce',is_mobile=width==390,has_touch=width==390,locale='ru-RU');page=await ctx.new_page();page.on('pageerror',lambda e:s.report['errors'].append(str(e)));await page.goto(s.ORIGIN+path,wait_until='networkidle');await s.prepare(page)
    assert await page.evaluate('document.documentElement.scrollWidth')==width,path
    file=s.slug(path)+'-'+str(width)+'.jpg';s.report['captures']=[r for r in s.report['captures']if r['file']!=file];await page.screenshot(path=str(s.OUT/file),full_page=True,type='jpeg',quality=75);s.record(path,file,width,'page')
    if path=='index.html':
     for i in range(1,5):
      await s.prepare(page);file='glavnaya-slayd-'+str(i)+'-'+str(width)+'.jpg';s.report['captures']=[r for r in s.report['captures']if r['file']!=file];await page.screenshot(path=str(s.OUT/file),type='jpeg',quality=75);s.record(path,file,width,'hero_slide');await page.locator('[data-hero-next]').click()
    await ctx.close()
   print('Captured',path,flush=True)
  await b.close()
 assert not s.report['errors'];s.report.update(page_count=len(s.PAGES),detail_count=len(s.DETAILS)*2,screenshot_count=len(s.report['captures']),stage5_refreshed=sorted(set(s.report.get("stage5_refreshed",[])+paths)))
 wanted={r['file']for r in s.report['captures']}
 for p in s.OUT.glob('*.jpg'):
  if p.name not in wanted:p.unlink()
 s.gallery();(s.SITE/'SCREENS_QA.json').write_text(json.dumps(s.report,ensure_ascii=False,indent=2)+'\n');print('Gallery:',len(s.PAGES),'pages,',len(s.report['captures']),'JPEG')
if __name__=='__main__':
 try:asyncio.run(main())
 finally:s.server.shutdown()
