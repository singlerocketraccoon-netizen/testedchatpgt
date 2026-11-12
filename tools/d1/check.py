#!/usr/bin/env python3
"""Acceptance checks for structure 11.11; Playwright is a development dependency only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote,parse_qs
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from datetime import date
import asyncio,hashlib,json,re,subprocess,threading
from playwright.async_api import async_playwright
from content4 import approved
import stage4
ROOT=Path(__file__).resolve().parents[2];SITE=ROOT/'docs/scheme2/d1';D=json.loads((ROOT/'tools/d1/data.json').read_text());PAGES=json.loads((ROOT/'tools/d1/pages.json').read_text());A=approved();stage4.D=D
class HTML(HTMLParser):
 def __init__(self,h):super().__init__();self.tags=[];self.ids=[];self.parts=[];self.skip=0;self.feed(h)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if'id'in a:self.ids.append(a['id'])
  if t in['script','style','svg']:self.skip+=1
 def handle_endtag(self,t):
  if t in['script','style','svg']:self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
def norm(s):return re.sub(r'\s+',' ',s).strip()
report={'pages':len(PAGES),'links':0,'approved_paragraphs':0,'approved_slide_fields':0,'viewports':0,'scenarios':[],'errors':[],'resource_errors':[]}
titles=[];descriptions=[]
for row in PAGES:
 f=SITE/row['path'];h=f.read_text();p=HTML(h)
 assert len(p.ids)==len(set(p.ids)),row['path'];assert sum(t=='h1'for t,a in p.tags)==1,row['path']
 assert 'Как Вам удобнее?'not in h and'#soprovozhdenie'not in h
 assert not re.search('WhatsApp|демо|прототип|lorem|здесь будет',h,re.I),row['path']
 if not row['path'].startswith('o-nas/dokumenty/'):assert 'Манго Путешествия'not in h,row['path']
 title=re.search('<title>(.*?)</title>',h)[1];description=next(a['content']for t,a in p.tags if t=='meta'and a.get('name')=='description');assert title and len(title)<=60 and description and len(description)<=160; titles.append(title);descriptions.append(description)
 for t,a in p.tags:
  if t in['a','button']:assert'data-goal'in a,(row['path'],t,a)
  if t=='input'and a.get('name')=='consent':assert'checked'not in a
  for k in['href','src']:
   v=a.get(k,'');u=urlsplit(v)
   if not v or u.scheme or u.netloc:continue
   target=(f.parent/unquote(u.path)).resolve()if u.path else f.resolve();assert not u.path.startswith('/')and target.is_file(),(row['path'],v)
   if u.fragment and target.suffix=='.html':assert unquote(u.fragment)in HTML(target.read_text()).ids,(row['path'],v)
   report['links']+=1
 if row['type']!='redirect':
  assert sum(t=='dialog'and a.get('id')=='request-dialog'for t,a in p.tags)==1,row['path']
  assert 'contact-dialog'not in h and'data-discussion-form'not in h,row['path']
assert len(set(titles))==len(PAGES) and len(set(descriptions))==len(PAGES)
work=norm(' '.join(HTML((SITE/'kak-my-rabotaem/index.html').read_text()).parts))
for text in A['work']['intro']+[p for s in A['work']['sections']for p in s['paragraphs']]:assert norm(text)in work,text;report['approved_paragraphs']+=1
home=norm(' '.join(HTML((SITE/'index.html').read_text()).parts))
for s in stage4.visible_slides():
 for k in['accent','title','description','button']:assert norm(s[k])in home,(s['id'],k);report['approved_slide_fields']+=1
assert len(stage4.visible_slides(date(2026,12,31)))==4 and len(stage4.visible_slides(date(2027,1,1)))==3
assert all(o['id']!='slide-2'for o in stage4.visible_slides(date(2027,1,1)))
assert not stage4.active_offers(on=date(2030,1,1));first=D['offers'][0];first['active']=False;assert first['id']not in[o['id']for o in stage4.active_offers()];first['active']=True
faq=(SITE/'voprosy/index.html').read_text();qdata=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',faq,re.S)[1]);q=next(n for n in qdata['@graph']if n['@type']=='FAQPage');assert len(q['mainEntity'])==6 and len({i['name']for i in q['mainEntity']})==6
for slug in['plans','choice','hotel','prepare','plans-on-trip','support','experience','cost']:assert f'id="{slug}"'in(SITE/'kak-my-rabotaem/index.html').read_text()
assert 'trust'not in D and'safe_payment'not in D and'process_source'not in D
before={p['path']:(SITE/p['path']).read_bytes()for p in PAGES};subprocess.run(['python3',str(ROOT/'tools/d1/build.py')],check=True,capture_output=True);assert all((SITE/p).read_bytes()==b for p,b in before.items())
report.update(approved_copy_exact=True,expiry_checks=True,faq_unique=True,deterministic_build=True)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/docs/scheme2/d1/'
async def run():
 async with async_playwright()as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in[360,768,1280,1440]:
   ctx=await browser.new_context(viewport={'width':width,'height':844 if width==360 else 900},reduced_motion='reduce',permissions=['clipboard-read','clipboard-write']);page=await ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('response',lambda r:report['resource_errors'].append(r.url)if r.status>=400 else None)
   for row in PAGES:
    await page.goto(BASE+row['path'],wait_until='load')
    if row['type']=='redirect':await page.wait_for_url('**/o-nas/index.html#team')
    await page.evaluate('document.fonts.ready');assert await page.evaluate('document.documentElement.scrollWidth')==width,(width,row['path']);report['viewports']+=1
    if row['type']=='redirect':continue
    assert await page.locator('#request-dialog form').count()==1
    assert await page.locator('#request-dialog [data-messenger]').evaluate_all('(a)=>a.map(n=>n.dataset.messenger)')==['MAX','Telegram']
    assert await page.locator('#request-dialog').evaluate("n=>n.querySelector('form').compareDocumentPosition(n.querySelector('.messenger-actions'))&Node.DOCUMENT_POSITION_FOLLOWING")
   await page.goto(BASE);await page.evaluate('document.fonts.ready');positions=[]
   for i in range(4):
    assert await page.locator('[data-hero-count]').inner_text()==str(i+1);positions.append(await page.locator('.hero-slide.is-active .btn').evaluate('e=>e.getBoundingClientRect().top'))
    await page.locator('[data-hero-next]').click()
   assert max(positions)-min(positions)<1,positions
   await page.wait_for_timeout(7600);assert await page.locator('[data-hero-count]').inner_text()=='1'
   assert not await page.locator('[data-hero-pause],[data-hero-dot],.hero-progress').count()
   await page.locator('.hero-slide.is-active [data-quiz-open]').click();assert await page.locator('#quiz-title').inner_text()=='Поможем выбрать отдых'
   await page.get_by_label('Знаю даты',exact=True).check();assert await page.locator('#quiz-dialog [name=from]').is_visible();assert await page.locator('#quiz-dialog [name=to]').is_visible();await page.locator('#quiz-dialog [name=from]').fill('2027-06-10');await page.locator('#quiz-dialog [name=to]').fill('2027-06-20');await page.locator('#quiz-dialog [name=phone]').fill('79991234567');await page.locator('#quiz-dialog [data-messenger=MAX]').click();await page.wait_for_timeout(100);text=await page.evaluate('navigator.clipboard.readText()');assert all(s in text for s in['2027-06-10','2027-06-20','999','Тема:'])
   await page.keyboard.press('Escape');assert await page.locator('.hero-slide.is-active [data-quiz-open]').evaluate('(n)=>n===document.activeElement')
   await page.locator('[data-hero-next]').click();button=page.locator('.hero-slide.is-active [data-request]');label=await button.inner_text();await button.click();assert await page.locator('#request-title').inner_text()==label;form=page.locator('[data-request-form]');await form.locator('button[type=submit]').click();assert await form.locator('[name=phone]').get_attribute('aria-invalid')=='true';await form.locator('[name=phone]').fill('79991234567');await form.locator('[name=wishes]').fill('Двое взрослых, июнь');await page.locator('#request-dialog [data-messenger=MAX]').click();await page.wait_for_timeout(100);text=await page.evaluate('navigator.clipboard.readText()');assert all(x in text for x in['Раннее бронирование','999','Двое взрослых']);await form.locator('[name=consent]').check();await form.locator('button[type=submit]').click();assert await page.locator('#request-dialog [data-local-success]').is_visible();assert not await form.locator('[name=phone]').input_value();await page.keyboard.press('Escape');assert await button.evaluate('(n)=>n===document.activeElement')
   await page.goto(BASE+'predlozheniya/index.html');await page.locator('.boarding-photo a').first.click();assert re.search('/predlozheniya/[^/]+/index.html',page.url);await page.locator('.offer-detail-grid [data-request]').click();assert 'ночей'in await page.locator('#request-dialog [name=topic]').input_value();await page.keyboard.press('Escape')
   await page.goto(BASE+'otdyh/otdyh-s-detmi/index.html');await page.locator('[data-rest-select]').first.click();assert await page.locator('#rest-inquiry-top input:not([type=hidden])').first.evaluate('(n)=>n===document.activeElement');assert await page.locator('#rest-inquiry-top').evaluate("n=>!!(n.querySelector('form').compareDocumentPosition(n.querySelector('.messenger-actions'))&Node.DOCUMENT_POSITION_FOLLOWING)")
   await page.locator('[data-hotel-message]').first.click();assert await page.locator('#request-dialog').is_visible();assert 'Отель:'in await page.locator('#request-dialog [name=topic]').input_value();await page.keyboard.press('Escape')
   if width==360:
    await page.goto(BASE);await page.evaluate("scrollTo(0,document.querySelector('[data-hero]').offsetHeight+80)");await page.locator('[data-mobile-contact]').wait_for(state='visible');await page.locator('[data-mobile-contact] button').click();assert await page.locator('#request-dialog').is_visible();await page.keyboard.press('Escape');await page.evaluate('scrollTo(0,document.documentElement.scrollHeight)');await page.wait_for_timeout(100);assert await page.locator('[data-mobile-contact]').is_hidden()
   report['scenarios'].append({'width':width,'manual_hero':True,'stable_button_position':True,'dialogs_keyboard_focus':True,'local_validation':True,'messenger_fields_and_topic':True,'offer_details':True,'rest_form_order':True})
   await ctx.close();print('Checked',width,flush=True)
  # Validate encoded Telegram context without leaving the local test server.
  ctx=await browser.new_context();page=await ctx.new_page()
  async def configured(route):
   response=await route.fetch();h=(await response.text()).replace('"telegramUsername": ""','"telegramUsername": "mango_test_account"');await route.fulfill(response=response,body=h)
  await page.route('**/docs/scheme2/d1/index.html',configured);await page.add_init_script("window.open=(url)=>{window.__opened=url;return null}");await page.goto(BASE+'index.html');await page.locator('.hero-slide.is-active [data-quiz-open]').click();await page.locator('#quiz-dialog [name=phone]').fill('79991234567');await page.locator('#quiz-dialog [data-messenger=Telegram]').click();u=await page.evaluate('window.__opened');assert u.startswith('https://t.me/mango_test_account?text=')and 'Ваш телефон'in parse_qs(urlsplit(u).query)['text'][0]
  await browser.close()
 assert not report['errors']and not report['resource_errors'],report
 (SITE/'STAGE4_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='scenarios'},ensure_ascii=False))
try:asyncio.run(run())
finally:server.shutdown()
