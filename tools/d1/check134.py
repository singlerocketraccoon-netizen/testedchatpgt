"""Stage 13.4: unchanged scenarios plus country/rest geometry against stage 13.2."""
import asyncio,json,hashlib
import check133 as base

async def covers(browser,engine):
 ctx=await browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');page=await ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 fixture=(base.R/'tools/d1/fixtures/revision13-stage132.css').read_text()
 assert hashlib.sha256(fixture.encode()).hexdigest()=='9c0cdc640534ea2a82aaf07a73a53eefb3c78b8d67a794026df4d9f3bcfa0c23'
 paths=[p['path']for p in base.PAGES if p['path'].startswith(('napravleniya/','otdyh/'))and p['path']!='napravleniya/index.html']
 base.report.setdefault('cover_geometry',[]);base.report.setdefault('home_geometry',[])
 for w,h in[(1366,768),(1920,1080),(2560,1336)]:
  await page.set_viewport_size({'width':w,'height':h})
  for path in paths:
   await page.goto(base.BASE+path);await page.evaluate('document.fonts.ready');actual=await page.locator('.country-hero,.rest-cover').evaluate('e=>e.getBoundingClientRect().height')
   reference=await page.add_style_tag(content=fixture);expected=await page.locator('.country-hero,.rest-cover').evaluate('e=>e.getBoundingClientRect().height');await reference.evaluate('e=>e.remove()')
   assert abs(actual-expected)<=1 and abs(actual-h)>1,(engine,path,w,h,actual,expected)
   base.report['cover_geometry'].append(dict(engine=engine,page=path,width=w,height=h,actual=actual,stage132=expected,difference=actual-expected))
  await page.goto(base.BASE+'index.html');await page.evaluate('document.fonts.ready')
  for slide in range(4):
   actual=await page.locator('.hero-shell').evaluate('e=>e.getBoundingClientRect().height');assert abs(actual-h)<=1,(engine,w,h,slide,actual);result=await page.evaluate(base.responsive_js);assert not result['fail'],(engine,w,h,slide,result['fail']);base.report['home_geometry'].append(dict(engine=engine,width=w,height=h,slide=slide+1,actual=actual));await page.locator('[data-hero-next]').click()
 for w,h in[(390,844),(1024,600),(320,568),(844,390),(2560,1440)]:
  await page.set_viewport_size({'width':w,'height':h});await page.goto(base.BASE+'index.html');await page.evaluate('document.fonts.ready')
  for slide in range(4):
   result=await page.evaluate(base.responsive_js);assert not result['fail'],(engine,w,h,slide,result['fail']);await page.locator('[data-hero-next]').click()
 assert not errors,errors;await ctx.close()

base.covers=covers;base.report['stage']='13.4'
base.report['reference_css']={'commit':'03f6eecfa7bfb6f74ec05d500ee48c806c30599f','path':'docs/scheme2/d1/css/revision13.css','sha256':'9c0cdc640534ea2a82aaf07a73a53eefb3c78b8d67a794026df4d9f3bcfa0c23'}
if __name__=='__main__':
 try:asyncio.run(base.main())
 finally:base.server.shutdown();(base.S/'QA13_4.json').write_text(json.dumps(base.report,ensure_ascii=False,indent=2)+'\n')
