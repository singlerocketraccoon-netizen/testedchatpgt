#!/usr/bin/env python3
"""Stage 5 acceptance: static output, responsive behavior and country data toggles."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import asyncio,json,re,subprocess,threading,copy,sys
from playwright.async_api import async_playwright
from content4 import approved
ROOT=Path(__file__).resolve().parents[2];SITE=ROOT/'docs/scheme2/d1';DATA=ROOT/'tools/d1/data.json';D=json.loads(DATA.read_text());PAGES=json.loads((ROOT/'tools/d1/pages.json').read_text());REMOVED=['tunis','greciya','kipr','bolgariya']
class H(HTMLParser):
 def __init__(self,h):super().__init__();self.tags=[];self.ids=[];self.feed(h)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if'id'in a:self.ids.append(a['id'])
cache={p.resolve():H(p.read_text())for p in SITE.rglob('*.html')}
report={'pages':len(PAGES),'links':0,'viewports':0,'errors':[],'resources':[],'scenarios':[]}
titles=[];descriptions=[]
for p,h in cache.items():
 raw=p.read_text()
 assert not re.search(r'napravleniya/(?:tunis|greciya|kipr|bolgariya)/|Тунис|Греци|Грецию|Кипр|Болгари',raw,re.I),p
 assert len(h.ids)==len(set(h.ids)),(p,'duplicate ids')
 for t,a in h.tags:
  if t in ['a','button','summary']:assert'data-goal'in a,(p,t,a)
  if t=='input'and a.get('name')=='consent':assert'checked'not in a
  for k in['href','src']:
   v=a.get(k,'');u=urlsplit(v)
   if not v or u.scheme or u.netloc:continue
   target=(p.parent/unquote(u.path)).resolve()if u.path else p
   assert not u.path.startswith('/')and target.is_file(),(p,v)
   if u.fragment and target.suffix=='.html':assert unquote(u.fragment)in cache[target].ids,(p,v)
   report['links']+=1
for row in PAGES:
 p=SITE/row['path'];h=p.read_text();parser=cache[p.resolve()]
 assert sum(t=='h1'for t,a in parser.tags)==1,row['path']
 title=re.search('<title>(.*?)</title>',h)[1];description=next(a['content']for t,a in parser.tags if t=='meta'and a.get('name')=='description');assert len(title)<=60 and len(description)<=160 and title and description; titles.append(title);descriptions.append(description)
 assert not re.search('WhatsApp|демо|прототип|lorem|здесь будет',h,re.I),row['path']
assert len(set(titles))==len(PAGES)and len(set(descriptions))==len(PAGES)
a=approved();work=(SITE/'kak-my-rabotaem/index.html').read_text()
for t in a['work']['intro']+[p for section in a['work']['sections']for p in section['paragraphs']]:assert t in work
report['approved_work_paragraphs']=19
egypt=next(c for c in D['countries']if c['slug']=='egipet')
source=(ROOT/'mango-country-page.html').read_text();raw=re.search(r'const resorts = (\[.*?\n  \]);',source,re.S)[1];original=json.loads(re.sub(r'\b([A-Za-z]+):',r'"\1":',raw))
for r in original:
 current=next(v for v in egypt['resorts']if v['id']==r['id'])
 for k,v in r.items():assert current[k]==v
report['egypt_source_exact']=True
assert [c['slug']for c in D['countries']]==['turciya','egipet','oae','tailand','maldivy','vetnam','shri-lanka','kitay','indoneziya']
assert 'show_country_offers'not in D
for c in D['countries']:
 assert len(c['hotels'])==3 and len(c['experiences'])==3 and len(c['alternatives'])==4
 assert set(c['essentials'])==set(['visa','flight','money','connection','rules','health'])
 for r in c['resorts']:
  for k in['air','water','windRain','monthNotes']:assert len(r[k])==12,(c['slug'],r['id'],k)
 html=(SITE/('napravleniya/'+c['slug']+'/index.html')).read_text()
 assert 'data-weather-table="'+c['resorts'][0]['id']+'"'in html and html.count('<tbody>')==len(c['resorts'])
 assert len(re.findall(r'\bdata-country-form(?:\s|>)',html))==3
assert [r['name']for r in next(c for c in D['countries']if c['slug']=='egipet')['resorts']]==['Хургада','Шарм-эш-Шейх','Марса-Алам','Эль-Гуна']
# Keep authored sections, services, footer and all unrelated home blocks unchanged.
old=Path('/tmp/stage5-before')
if old.exists():
 for p in PAGES:
  path=p['path'];f=old/path
  if not f.exists():continue
  current=(SITE/path).read_text();before=f.read_text()
  if path.startswith(('uslugi/','otdyh/')):
   body=lambda s:re.search(r'<main\b.*?</main>',s,re.S)[0]
   assert body(current)==body(before),('Protected main content',path)
  footer=lambda s:re.search(r'<!-- component: footer -->.*?<!-- /component: footer -->',s,re.S)
  if footer(current)and footer(before):assert footer(current)[0]==footer(before)[0],('Footer',path)
 home=(SITE/'index.html').read_text();before=(old/'index.html').read_text()
 for id in['moods','offers','process','team','voices','questions','contact']:
  section=lambda s:re.search(r'<section\b[^>]*id="'+id+r'".*?</section>',s,re.S)[0]
  assert section(home)==section(before),('Home block',id)
 report['protected_content_unchanged']=True
before={p['path']:(SITE/p['path']).read_bytes()for p in PAGES};subprocess.run(['python3',str(ROOT/'tools/d1/build.py')],check=True,capture_output=True);assert all((SITE/p).read_bytes()==b for p,b in before.items());report['deterministic_build']=True
if '--static'in sys.argv:
 print('Static checks passed:',report['pages'],'pages,',report['links'],'links');sys.exit(0)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/docs/scheme2/d1/'
async def run():
 async with async_playwright()as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in[360,768,1280,1440]:
   ctx=await b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce',permissions=['clipboard-read','clipboard-write']);page=await ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('response',lambda r:report['resources'].append(r.url)if r.status>=400 else None)
   for row in PAGES:
    await page.goto(BASE+row['path'],wait_until='load')
    if row['type']=='redirect':await page.wait_for_url('**/o-nas/index.html#team')
    await page.evaluate('document.fonts.ready');assert await page.evaluate('document.documentElement.scrollWidth')==width,(row['path'],width);report['viewports']+=1
   await page.goto(BASE+'napravleniya/egipet/index.html');await page.locator('[data-weather-resort]').select_option('sharm');await page.locator('[data-weather-month="7"]').click();assert await page.locator('[data-weather-air]').inner_text()=='+38 °C';assert await page.locator('[data-weather-water]').inner_text()=='+28 °C';assert await page.locator('[data-country-form] [name=month]').first.input_value()=='7'
   card=page.locator('[data-resort-card="hurghada"]');await card.locator('summary').click();await card.locator('[data-resort-hotels]').click();assert await page.locator('[data-hotel-filter]').input_value()=='hurghada';assert await page.locator('[data-hotel-card]:visible').count()==1;await card.locator('[data-resort-weather]').click();assert await page.locator('[data-weather-resort]').input_value()=='hurghada'
   await page.locator('[data-more-resorts]').click();assert await page.locator('[data-resort-card="gouna"]').is_visible();await page.locator('[data-hotel-filter]').select_option('gouna');assert await page.locator('[data-hotel-empty]').is_visible();await page.locator('[data-hotel-empty] button').click();assert await page.locator('#request-title').inner_text()=='Обсудим Вашу поездку';assert 'Эль-Гуна'in await page.locator('#request-dialog [name=topic]').input_value();await page.keyboard.press('Escape')
   await page.locator('[data-hotel-filter]').select_option('');trigger=page.locator('[data-country-hotel="hotel-1"]');await trigger.click();assert await page.locator('#hotel-1-dialog').is_visible();await page.locator('#hotel-1-dialog [data-country-request]').click();assert await page.locator('#request-title').inner_text()=='Запрос стоимости';form=page.locator('#request-dialog form');await form.locator('[name=travelers]').select_option(label='С детьми');assert await form.locator('[name=ages]').is_visible();await form.locator('[name=ages]').fill('Двое взрослых, ребёнок 6 лет');await form.locator('[name=phone]').fill('79991234567');await page.locator('#request-dialog [data-messenger=MAX]').click();await page.wait_for_timeout(100);text=await page.evaluate('navigator.clipboard.readText()');assert all(x in text for x in['Здравствуйте! Хочу уточнить цену на мои даты. Отель 1, Хургада.','Июль','Двое взрослых','999']);await form.locator('[name=consent]').check();await form.locator('button[type=submit]').click();assert await page.locator('#request-dialog [data-local-success]').is_visible();assert not await page.locator('[data-country-form] [name=phone]').first.input_value();await page.keyboard.press('Escape');assert await page.locator('#hotel-1-dialog [data-country-request]').evaluate('n=>n===document.activeElement');await page.keyboard.press('Escape');assert await trigger.evaluate('n=>n===document.activeElement')
   await page.locator('[data-country-format="routes"]').click();assert await page.locator('[data-country-panel="routes"]').is_visible();assert await page.locator('[data-alternatives-context]').inner_text()=='Ваши даты · города и маршруты';await page.locator('[data-country-panel="routes"] button').first.click();await page.locator('#request-dialog [data-messenger=MAX]').click();await page.wait_for_timeout(100);assert 'маршрут по Египту. Каир и пирамиды.'in await page.evaluate('navigator.clipboard.readText()');await page.keyboard.press('Escape')
   await page.locator('[href="#flight"][data-open-essential]').click();assert await page.locator('#flight').get_attribute('open')is not None
   if width==360:
    await page.goto(BASE+'napravleniya/egipet/index.html');await page.evaluate("scrollTo(0,document.querySelector('#season').offsetTop+150)");await page.locator('.country-mobile-panel').wait_for(state='visible');assert await page.locator('.country-mobile-panel [data-messenger]').evaluate_all('a=>a.map(n=>n.dataset.messenger)')==['MAX','Telegram'];await page.locator('.country-mobile-panel button').click();assert await page.locator('.country-mobile-panel').is_hidden();await page.keyboard.press('Escape');await page.locator('#inquiry .country-inquiry').scroll_into_view_if_needed();await page.wait_for_timeout(50);assert await page.locator('.country-mobile-panel').is_hidden()
   else:
    if width>=1024:
     await page.goto(BASE+'kak-my-rabotaem/index.html');await page.locator('[data-work-anchor][href="#support"]').click();await page.wait_for_timeout(100);assert await page.locator('.work-toc [aria-current]').get_attribute('href')=='#support';await page.evaluate('scrollTo(0,0)');await page.locator('[aria-controls=nav-work]').focus();await page.keyboard.press('ArrowDown');assert await page.locator('#nav-work').is_visible();await page.keyboard.press('Escape');assert await page.locator('[aria-controls=nav-work]').evaluate('n=>n===document.activeElement')
   report['scenarios'].append({'width':width,'climate':True,'resort_links':True,'hotel_filter_and_modal':True,'country_form_and_message':True,'routes':True,'keyboard_focus':True});await ctx.close();print('Checked',width,flush=True)
  # Build-time visibility: false, no offers, and additional mobile rows.
  original=DATA.read_bytes()
  try:
   for mode in['disabled','empty','more']:
    d=json.loads(original);egypt=next(c for c in d['countries']if c['slug']=='egipet')
    if mode=='disabled':egypt['showOffers']=False
    elif mode=='empty':
     for o in d['offers']:
      if o['country']=='egipet':o['active']=False
    else:
     template=next(o for o in d['offers']if o['country']=='egipet')
     for i in range(3):o=copy.deepcopy(template);o['id']='qa-egypt-'+str(i);d['offers'].append(o)
    DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');subprocess.run(['python3',str(ROOT/'tools/d1/build.py')],check=True,capture_output=True)
    pg=await b.new_page(viewport={'width':360,'height':844},reduced_motion='reduce');await pg.goto(BASE+'napravleniya/egipet/index.html')
    assert await pg.locator('#price-strip').count()==1
    if mode=='more':
     assert await pg.locator('.country-offer:visible').count()==3;await pg.locator('[data-more-country-offers]').click();assert await pg.locator('.country-offer:visible').count()==4
    else:assert not await pg.locator('#offers,[data-country-anchor][href="#offers"]').count()
    await pg.close();report['scenarios'].append({'offers_fixture':mode,'passed':True})
  finally:
   DATA.write_bytes(original);subprocess.run(['python3',str(ROOT/'tools/d1/build.py')],check=True,capture_output=True)
  await b.close()
 assert not report['errors']and not report['resources'],report
 (SITE/'STAGE5_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Passed',report['pages'],'pages;',report['links'],'links;',report['viewports'],'viewports')
try:asyncio.run(run())
finally:server.shutdown()
