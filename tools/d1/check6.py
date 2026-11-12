#!/usr/bin/env python3
"""Acceptance checks for schema 12.11 v2. Development-only Playwright and Node."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from datetime import datetime
from zoneinfo import ZoneInfo
import asyncio,json,re,subprocess,threading,sys
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2];SITE=ROOT/'docs/scheme2/d1';DATA=ROOT/'tools/d1/data.json';D=json.loads(DATA.read_text());PAGES=json.loads((ROOT/'tools/d1/pages.json').read_text());YEAR=datetime.now(ZoneInfo('Europe/Moscow')).year
HIDDEN=['topic','page','utm_source','utm_medium','utm_campaign','utm_content','utm_term']
class HTML(HTMLParser):
 def __init__(self,h):super().__init__();self.tags=[];self.ids=[];self.parts=[];self.skip=0;self.feed(h)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if'id'in a:self.ids.append(a['id'])
  if t in['script','style','svg']:self.skip+=1
 def handle_endtag(self,t):
  if t in['script','style','svg']:self.skip-=1
 def handle_data(self,t):
  if not self.skip:self.parts.append(t)
report={'pages':len(PAGES),'links':0,'viewports':0,'errors':[],'resources':[],'scenarios':[]}
cache={p.resolve():HTML(p.read_text())for p in SITE.rglob('*.html')};paths=[SITE/p['path']for p in PAGES]
if '--gallery'in sys.argv:paths=list(SITE.rglob('*.html'))
for p in paths:
 h=p.read_text();a=cache[p.resolve()];assert 'Шарм-эш-Шейх'not in h,p;assert len(a.ids)==len(set(a.ids)),(p,'duplicate ids')
 for tag,attrs in a.tags:
  if tag in['a','button','summary']:assert'data-goal'in attrs,(p,tag,attrs)
  if tag=='input'and attrs.get('name')=='consent':assert'checked'not in attrs and'required'in attrs,p
  for name in['href','src']:
   v=attrs.get(name,'');u=urlsplit(v)
   if not v or u.scheme or u.netloc:continue
   assert not re.search(r'(?:^|/)uslugi/(?!index\.html)[^/#]+/|(?:^|/)voprosy/',u.path),(p,v)
   target=(p.parent/unquote(u.path)).resolve()if u.path else p.resolve();assert not u.path.startswith('/')and target.is_file(),(p,v)
   if u.fragment and target.suffix=='.html':assert unquote(u.fragment)in cache[target].ids,(p,v)
   report['links']+=1
for p in PAGES:
 h=(SITE/p['path']).read_text();a=cache[(SITE/p['path']).resolve()];assert sum(t=='h1'for t,attrs in a.tags)==1,p['path']
 assert not re.search('WhatsApp|демо|прототип|lorem',h,re.I),p['path']
 if p['path']!='zagranpasport/index.html':assert 'Здесь будет'not in h,p['path']
 for f in re.findall(r'<form\b.*?</form>',h,re.S):
  a=HTML(f);assert [attrs['name']for t,attrs in a.tags if t=='input'and attrs.get('type')=='hidden']==HIDDEN,p['path']
  assert any(t=='input'and at.get('name')=='phone'and at.get('type')=='tel'and at.get('autocomplete')=='tel'for t,at in a.tags)
  assert any(t=='fieldset'and'disabled'in at for t,at in a.tags)
  assert re.search(r'data-messenger="MAX".*data-messenger="Telegram"',f,re.S)
 title=re.search('<title>(.*?)</title>',h)[1];description=re.search(r'<meta name="description" content="([^"]+)"',h)[1];assert len(title)<=60 and len(description)<=160
source=json.loads(subprocess.check_output(['node',str(ROOT/'tools/d1/read_schema6.cjs')],cwd=ROOT));assert source==D['schema6'];home=(SITE/'index.html').read_text();services=(SITE/'uslugi/index.html').read_text()
for s in source['travel']+source['extras']:assert s['text']in services and s['action']in services
for s in source['slides']:assert s['msg']in home and s['name']in home
text=''.join(HTML(home).parts)
for f in source['faq']:assert f['q']in home and re.sub('<[^>]+>','',f['a'])in text
assert home.count('class="faq-item"')==4
assert len(D['offers'])==8 and sum(o['featured']for o in D['offers'])==4
assert all('published'in o and'active'not in o for o in D['offers'])
assert not(SITE/'voprosy/index.html').exists();assert not list((SITE/'uslugi').glob('*/index.html'))
backup=Path('/tmp/stage6-tools-before/data.json')
if backup.exists():
 before=json.loads(backup.read_text());assert D['rest_pages']==before['rest_pages'],'Authored holiday data changed'
 normalized=lambda v:json.dumps(v,ensure_ascii=False,sort_keys=True).replace('Шарм-эш-Шейх','Шарм-эль-Шейх')
 for c in D['countries']:
  b=next(v for v in before['countries']if v['slug']==c['slug'])
  for key in['h1','subtitle','heroPhoto','hotelsIntro','routes','hotels','experiences','essentials','review','alternatives']:assert normalized(c[key])==normalized(b[key]),(c['slug'],key)
  for r,br in zip(c['resorts'],b['resorts']):
   for key in br:assert normalized(r[key])==normalized(br[key]),(c['slug'],r['id'],key)
 for path in['img/logo-mango.svg','img/logo-mango-light.svg','css/fonts.css']:assert (SITE/path).read_bytes()==(Path('/tmp/stage6-before')/path).read_bytes()
report.update(source_copy_exact=True,protected_country_holiday_content=True)
before={p['path']:(SITE/p['path']).read_bytes()for p in PAGES};subprocess.run(['python3',str(ROOT/'tools/d1/build.py')],check=True,capture_output=True);assert all((SITE/p).read_bytes()==b for p,b in before.items());report['deterministic_build']=True
if '--static'in sys.argv:print('Static passed',report['pages'],'pages,',report['links'],'links');sys.exit(0)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/docs/scheme2/d1/'
async def run():
 async with async_playwright()as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in[360,390,768,1280,1440]:
   ctx=await browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce',permissions=['clipboard-read','clipboard-write']);page=await ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None);page.on('response',lambda r:report['resources'].append(r.url)if r.status>=400 else None)
   for row in PAGES:
    await page.goto(BASE+row['path'],wait_until='load')
    if row['type']=='redirect':await page.wait_for_url('**/o-nas/index.html#team')
    await page.evaluate('document.fonts.ready');assert await page.evaluate('document.documentElement.scrollWidth')==width,(row['path'],width);report['viewports']+=1
   await page.goto(BASE+'index.html?utm_source=acceptance&utm_campaign=stage6');await page.evaluate("window.__goals=[];document.addEventListener('mango:goal',e=>window.__goals.push(e.detail))")
   for i in range(4):
    btn=page.locator('.hero-slide.is-active [data-open-form]');key=await btn.get_attribute('data-open-form');await btn.click();assert await page.locator('#request-title').inner_text()=='Расскажите о поездке';f=page.locator('#request-dialog [data-form-pane=pick] form');assert await f.locator('[name=topic]').input_value()==key;assert await f.locator('[name=utm_source]').input_value()=='acceptance';assert await f.locator('[name=month] option').count()==25;await page.keyboard.press('Escape');assert await btn.evaluate('n=>n===document.activeElement');await page.locator('[data-hero-next]').click()
   await page.locator('.hero-slide.is-active [data-open-form]').click();f=page.locator('#request-dialog [data-form-pane=pick] form');await f.locator('[name=who]').select_option(label='С детьми');assert await f.locator('[name=ages]').is_visible();await f.locator('[name=ages]').fill('Двое взрослых, ребёнок 6 лет');await f.locator('[name=city]').fill('Астрахань');await f.locator('[name=phone]').fill('79991234567');await f.locator('[data-messenger=MAX]').click();await page.wait_for_timeout(80);message=await page.evaluate('navigator.clipboard.readText()');assert 'Город вылета — Астрахань'in message and'Кто едет — С детьми'in message;assert not any(x in message for x in['999','345','acceptance','utm_','topic','page:'])
   await f.locator('button[type=submit]').click();assert await f.locator('[name=consent]').get_attribute('aria-invalid')=='true';await f.locator('[name=consent]').check();await f.locator('button[type=submit]').click();assert await page.locator('#request-dialog [data-form-pane=pick] [data-form-success]').is_visible();events=await page.evaluate('window.__goals');assert any(x['name']=='form_success'and x['form_kind']=='pick'and x['topic']=='slide:0'for x in events);assert not any('999'in json.dumps(x)or'Астрахань'in json.dumps(x,ensure_ascii=False)for x in events);await page.keyboard.press('Escape')
   await page.locator('[data-goal=rest_help]').click();assert await page.locator('#quiz-title').inner_text()=='Помогите выбрать';q=page.locator('#quiz-dialog form');await q.get_by_label('Лето',exact=True).check();assert await q.locator('[name=year]').is_visible();await q.get_by_label('Знаю даты',exact=True).check();assert await q.locator('[name=from]').is_visible();assert await q.locator('[name=year]').is_hidden();await q.locator('[name=from]').fill('2027-07-20');await q.locator('[name=to]').fill('2027-07-10');await q.locator('[name=phone]').fill('79991234567');await q.locator('[name=consent]').check();await q.locator('button[type=submit]').click();assert await q.locator('[name=to]').get_attribute('aria-invalid')=='true';await page.keyboard.press('Escape')
   await page.goto(BASE+'predlozheniya/index.html');await page.locator('[data-offer-filter=egipet]').click();assert 'country=egipet'in page.url;assert await page.locator('[data-offers-list] .offer-card:visible').count()==4;await page.locator('[data-offers-list] .offer-card:visible a').first.click();await page.locator('[data-open-form^="offer:"]').first.click();assert await page.locator('#request-title').inner_text()=='Уточнить цену и наличие';f=page.locator('#request-dialog [data-form-pane=offer] form');assert await f.locator('[name=phone]').is_visible();assert await f.locator('[name=month]').is_hidden();await f.locator('summary').click();assert await f.locator('[name=month]').is_visible();await page.keyboard.press('Escape');await page.go_back();assert 'country=egipet'in page.url;assert await page.locator('[data-offer-filter=egipet]').get_attribute('aria-pressed')=='true'
   await page.goto(BASE+'uslugi/index.html#visas');assert await page.locator('#visas').get_attribute('open')is not None;await page.locator('#visas [data-open-form]').click();assert await page.locator('#request-title').inner_text()=='Расскажите, чем помочь';assert await page.locator('#request-dialog [data-form-pane=service] [name=task]').is_visible();await page.keyboard.press('Escape');await page.locator('#custom summary').click();await page.locator('#custom [data-open-form]').click();assert await page.locator('#request-title').inner_text()=='Расскажите о поездке';await page.keyboard.press('Escape')
   await page.goto(BASE+'napravleniya/egipet/index.html');await page.locator('[data-weather-month="1"]').click();assert await page.locator('[data-country-inquiry=bottom] [name=month]').input_value()==str(YEAR+1)+'-01';await page.locator('[data-resort-card=hurghada] summary').click();await page.locator('[data-resort-card=hurghada] [data-resort-hotels]').click();assert await page.locator('[data-hotel-filter]').input_value()=='hurghada';await page.locator('[data-country-hotel=hotel-1]').click();await page.locator('#hotel-1-dialog [data-open-form]').click();assert await page.locator('#request-title').inner_text()=='Расскажите о поездке';await page.keyboard.press('Escape');await page.keyboard.press('Escape')
   await page.goto(BASE+'otdyh/otdyh-s-detmi/index.html');assert await page.locator('#rest-inquiry-top [name=who]').input_value()=='С детьми';await page.locator('[data-rest-select]').first.click();assert await page.locator('#rest-inquiry-top [name=topic]').input_value()!='holiday:otdyh-s-detmi'
   if width in[360,390]:
    for path in['index.html','napravleniya/egipet/index.html','otdyh/otdyh-s-detmi/index.html','o-nas/kontakty/index.html','zagranpasport/index.html']:
     await page.goto(BASE+path);assert await page.locator('.header-contacts>a:visible').count()==0;await page.evaluate('scrollTo(0,1100)');await page.wait_for_timeout(80);panel=page.locator('[data-mobile-contact]')
     if await panel.is_hidden():await page.evaluate('scrollTo(0,1600)');await page.wait_for_timeout(80)
     if not await panel.is_hidden():
      box=await panel.bounding_box();assert box['height']<=64,(path,width,box);assert await panel.locator('[data-messenger]').evaluate_all('a=>a.map(x=>x.dataset.messenger)')==['MAX','Telegram'];await panel.locator('[data-open-form]').click();assert await panel.is_hidden();await page.keyboard.press('Escape')
     await page.evaluate('scrollTo(0,document.documentElement.scrollHeight)');await page.wait_for_timeout(80);assert await panel.is_hidden()
    await page.goto(BASE+'index.html');await page.locator('[data-menu]').focus();await page.keyboard.press('Enter');assert await page.locator('#mobile-nav').is_visible();await page.keyboard.press('Escape');assert await page.locator('[data-menu]').evaluate('n=>n===document.activeElement')
   report['scenarios'].append({'width':width,'forms':True,'messages_exclude_phone':True,'goals_exclude_contacts':True,'catalogue_return':True,'country_month':True,'keyboard':True});await ctx.close();print('Checked',width,flush=True)
  original=DATA.read_bytes()
  try:
   for mode in['offers_empty','featured_empty','country_unpublished','offers_expired']:
    d=json.loads(original)
    if mode=='country_unpublished':next(c for c in d['countries']if c['slug']=='egipet')['published']=False
    elif mode=='featured_empty':
     for o in d['offers']:o['featured']=False
    else:
     for o in d['offers']:
      if mode=='offers_empty':o['published']=False
      else:o['showUntil']='2000-01-01'
    DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');subprocess.run(['python3',str(ROOT/'tools/d1/build.py')],check=True,capture_output=True)
    pg=await browser.new_page();await pg.goto(BASE+'index.html')
    if mode=='country_unpublished':assert not(SITE/'napravleniya/egipet/index.html').exists();assert not await pg.locator('a[href*="napravleniya/egipet/"]').count()
    else:assert not await pg.locator('#offers').count()
    if mode in['offers_empty','offers_expired']:
     assert not list((SITE/'predlozheniya').glob('*/index.html'));await pg.goto(BASE+'predlozheniya/index.html');assert await pg.get_by_text('Подберём поездку под Ваши даты',exact=True).count();await pg.goto(BASE+'napravleniya/egipet/index.html');assert not await pg.locator('#offers,[href="#offers"]').count();assert await pg.locator('#price-strip').count()
    await pg.close();report['scenarios'].append({'fixture':mode,'passed':True})
  finally:
   DATA.write_bytes(original);subprocess.run(['python3',str(ROOT/'tools/d1/build.py')],check=True,capture_output=True)
  await browser.close()
 assert not report['errors']and not report['resources'],report
 (SITE/'STAGE6_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Passed',report['pages'],'pages,',report['links'],'links,',report['viewports'],'viewports')
try:asyncio.run(run())
finally:server.shutdown()
