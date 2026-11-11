from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote,parse_qs
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import asyncio,threading,json,re,hashlib,subprocess
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2];SITE=ROOT/'docs/scheme2/d1';D=json.loads((ROOT/'tools/d1/data.json').read_text());PAGES=json.loads((ROOT/'tools/d1/pages.json').read_text())
class HTML(HTMLParser):
 def __init__(self,h):super().__init__();self.tags=[];self.ids=[];self.feed(h)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if'id'in a:self.ids.append(a['id'])
import online
online.D=D
assert online.years_in_tourism(2026)==16 and online.years_in_tourism(2027)==17
for value,heading in[('', 'Страны'),('Здравствуйте! Страны','Страны'),('Страны','Страны'),('Здравствуйте! АстраханиПутешествия','Страны')]:
 try:online.validate_message(value,heading)
 except AssertionError:pass
 else:raise AssertionError('Message guard accepted invalid input: '+value)
checks=0;titles=[];descriptions=[]
for rec in PAGES:
 f=SITE/rec['path'];h=f.read_text();p=HTML(h)
 assert len(p.ids)==len(set(p.ids)),f
 online.MessageValidator().check(h)
 assert 'messengerText'in D['pages'][rec['path']]
 assert not re.search('services-dialog|Визы и страхование|Туры в рассрочку|Отели по контрактным ценам|Горнолыжные, автобусные и лечебные туры',h,re.I),f
 assert sum(t=='h1'for t,a in p.tags)==1,f
 assert not re.search('Арбат|Кирова|Как добраться|Наш офис|streetAddress|WhatsApp|демо|прототип|lorem|здесь будет',h,re.I),f
 title=re.search('<title>(.*?)</title>',h)[1];description=next(a['content']for t,a in p.tags if t=='meta'and a.get('name')=='description');assert len(title)<=60 and len(description)<=160
 titles.append(title);descriptions.append(description)
 for t,a in p.tags:
  if t in['a','button']:assert'data-goal'in a,(f,t,a)
  if t=='input'and a.get('name')=='consent':assert'checked'not in a
  for k in['src','href']:
   value=a.get(k,'');u=urlsplit(value)
   if not value or u.scheme or u.netloc:continue
   target=(f.parent/unquote(u.path)).resolve()if u.path else f.resolve()
   assert not u.path.startswith('/')and target.is_file(),(f,value)
   if u.fragment and target.suffix=='.html':assert unquote(u.fragment)in HTML(target.read_text()).ids,(f,value)
   checks+=1
 assert 'komanda/index.html'not in h or rec['path']=='pages.html',f
assert len(set(titles))==len(PAGES)and len(set(descriptions))==len(PAGES)
for p in D['rest_pages']:
 h=(SITE/'otdyh'/p['slug']/'index.html').read_text()
 for field in p['fields']:assert field in h
 for q,a in p['questions']:assert q in h and a in h
assert len(re.findall('boarding-pass',(SITE/'index.html').read_text()))==6
assert 'boarding-pass'not in (SITE/'o-nas/index.html').read_text()
before={r['path']:hashlib.sha256((SITE/r['path']).read_bytes()).hexdigest()for r in PAGES};subprocess.run(['python','tools/d1/build.py'],check=True,capture_output=True);assert all(hashlib.sha256((SITE/p).read_bytes()).hexdigest()==sha for p,sha in before.items())
report={'message_guard_negative_cases':4,'dynamic_year_test':True,'pages':len(PAGES),'links_and_resources':checks,'unique_metadata':True,'online_only':True,'empty_consents':True,'source_rest_fields_and_faq_preserved':True,'deterministic_build':True,'viewport_checks':0,'service_heights':[],'scenarios':[],'errors':[],'bad_resources':[]}
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();BASE=f'http://127.0.0.1:{server.server_port}/docs/scheme2/d1/'
async def main():
 async with async_playwright()as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in[360,768,1280,1440]:
   ctx=await browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce',permissions=['clipboard-read','clipboard-write']);page=await ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('response',lambda r:report['bad_resources'].append(r.url)if r.status>=400 else None)
   for row in PAGES:
    await page.goto(BASE+row['path']);
    if row.get('type')=='redirect':await page.wait_for_url('**/o-nas/index.html#komanda')
    await page.evaluate('document.fonts.ready');assert await page.evaluate('document.documentElement.scrollWidth')==width,(row['path'],width)
    if row['path'].startswith('uslugi/')and row['path']!='uslugi/index.html':
     height=await page.locator('footer').evaluate('(e)=>e.getBoundingClientRect().top+scrollY')
     if width==1440:assert height<=1170,(row['path'],height);report['service_heights'].append({'page':row['path'],'width':width,'height':height})
    if row.get('type')!='redirect':
     expected=D['pages'][row['path']]['messengerText']
     messages=await page.locator('[data-message]').evaluate_all('(nodes)=>nodes.filter(n=>!n.closest(".boarding-pass")).map(n=>n.dataset.message)')
     assert all(x==expected for x in messages),(row['path'],messages,expected)
     inputs=await page.locator('[name="destination"]').evaluate_all('(nodes)=>nodes.map(n=>n.value)')
     country=next((c for c in D['countries']if row['path']=='napravleniya/'+c['slug']+'/index.html'),None)
     assert all(v==(country['name']if country else'')for v in inputs),(row['path'],inputs)
     topics=await page.locator('form [name="topic"]').evaluate_all('(nodes)=>nodes.map(n=>n.value)')
     assert topics and all(v==D['pages'][row['path']]['topic']for v in topics),(row['path'],topics)
     for form in await page.locator('form:has([name="consent"])').all():
      assert await form.evaluate("f=>!!(f.querySelector('[name=consent]').compareDocumentPosition(f.querySelector('button[type=submit]'))&Node.DOCUMENT_POSITION_FOLLOWING)")
     assert await page.locator('[data-mobile-contact] use').get_attribute('href')=='#i-message'
     if width<768:assert await page.evaluate('parseFloat(getComputedStyle(document.body).paddingBottom)')>=80
     if row['path']=='o-nas/index.html':
      assert await page.locator('.year-card').count()==0
      assert await page.locator('.trust-card').count()==sum(t.get('valueFrom')=='foundedYear'or bool(str(t.get('value')if t.get('value')is not None else'').strip())for t in D['trust'])
      heights=await page.locator('.team-travel-card').evaluate_all('(nodes)=>nodes.map(n=>n.getBoundingClientRect().height)');assert max(heights)-min(heights)<1,heights
      buttons=await page.locator('.team-travel-channels').evaluate_all('(nodes)=>nodes.map(n=>n.getBoundingClientRect().bottom)');assert max(buttons)-min(buttons)<1,buttons
      assert await page.locator('.team-picker-head').evaluate("e=>getComputedStyle(e).textAlign")=='left'
      assert not await page.get_by_role('heading',name='На связи в поездке',exact=True).count()
     if row['path']=='o-nas/kontakty/index.html':
      assert await page.locator('main .contact-section').count()==0
      assert await page.locator('main [data-discussion-form]').count()==1
      assert not await page.locator('details#contact').evaluate('(n)=>n.open')
     if row['path']=='index.html':
      assert await page.locator('.manager-badge').count()==0
      for strip in await page.locator('.contact-strip').all():
       assert await strip.locator('a').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.messenger||"phone")')==['Telegram','MAX','phone']
       if width<768:
        widths=await strip.locator('.btn').evaluate_all('(nodes)=>nodes.map(n=>n.getBoundingClientRect().width)');assert abs(widths[0]-widths[1])<1
     if row['path'].startswith('otdyh/'):
      for line in await page.locator('.rest-contact-line').all():
       assert await line.locator('.btn-primary').count()==1
       assert await line.locator('.btn-outline').count()==1
       assert await line.locator('[data-rest-select].text-link').count()==1
    report['viewport_checks']+=1
   # Real click paths, without any external navigation or backend request.
   await page.goto(BASE);await page.locator('.hero-slide.is-active [data-quiz-open]').click()
   await page.get_by_label('С детьми',exact=True).check();await page.get_by_label('Знаю даты',exact=True).check();await page.locator('[name=dates]').fill('10–20 июля');await page.get_by_label('Горы',exact=True).check();await page.locator('[name=budget]').fill('250000');assert await page.locator('#quiz-dialog').evaluate("e=>e.querySelector('[name=budget]').closest('label').getBoundingClientRect().top-e.querySelector('[name=preference]').closest('fieldset').querySelector('.selection-chips').getBoundingClientRect().bottom")>=20
   await page.locator('#quiz-dialog [data-messenger=Telegram]').click();await page.locator('#messenger-fallback').wait_for(state='visible');text=await page.locator('[data-fallback-text]').input_value();assert 'Страница:'not in text;assert all(x in text for x in['С детьми','10–20 июля','Горы','250000']),text
   await page.keyboard.press('Escape');assert not await page.locator('#messenger-fallback').evaluate('(e)=>e.open');assert await page.locator('#quiz-dialog [data-messenger=Telegram]').evaluate('(e)=>e===document.activeElement');await page.keyboard.press('Escape')
   await page.locator('.hero-slide.is-active [data-quiz-open]').click();await page.locator('#quiz-dialog [data-messenger=MAX]').click();await page.wait_for_timeout(50);assert 'Текст скопирован' in await page.locator('#quiz-dialog [data-channel-status]').inner_text();assert await page.locator('#quiz-dialog [data-channel-status]').is_visible();clip=await page.evaluate('navigator.clipboard.readText()');assert D['pages']['index.html']['messengerText']in clip
   await page.keyboard.press('Escape')
   await page.goto(BASE+'otdyh/otdyh-s-detmi/index.html');await page.locator('[data-rest-select]').first.click();assert await page.locator('#rest-inquiry-top input:not([type=hidden])').first.evaluate('(n)=>n===document.activeElement');await page.locator('#rest-inquiry-top [data-messenger=MAX]').click();await page.wait_for_timeout(50);clip=await page.evaluate('navigator.clipboard.readText()');assert 'Вы выбрали:'in clip;assert 'Страница:'not in clip
   # Clipboard failure opens the only message dialog, and permits manual selection.
   await page.evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:()=>Promise.reject(Error('denied'))}})")
   await page.locator('[data-hotel-message]').first.click();await page.locator('#messenger-fallback').wait_for(state='visible');text=await page.locator('[data-fallback-text]').input_value();assert 'Отель:'in text;await page.locator('[data-fallback-copy]').click();assert 'вручную'in await page.locator('[data-fallback-status]').inner_text();await page.keyboard.press('Escape')
   await page.goto(BASE+'uslugi/kruizy/index.html');await page.locator('summary').last.click();form=page.locator('[data-discussion-form]');await form.locator('[name=contact]').fill('+7 999 123-45-67');await form.locator('[name=consent]').check();await form.locator('button[type=submit]').click();assert await page.locator('[data-form-success]').is_visible()
   await page.goto(BASE+'predlozheniya/index.html');await page.locator('[data-offer-filter=vetnam]').click();assert await page.locator('.boarding-pass:visible').count()==1;await page.locator('[data-offer-sort]').select_option('price')
   report['scenarios'].append({'width':width,'selection_context':True,'max_copy':True,'rest_selection_context':True,'clipboard_fallback':True,'callback_form':True,'offers_filter_sort':True})
   await ctx.close()
  # Configured URL generation: inject actual-looking settings into response HTML, never source files.
  ctx=await browser.new_context();page=await ctx.new_page()
  async def patched(route):
   response=await route.fetch();h=await response.text();h=h.replace('"telegramUsername": ""','"telegramUsername": "mango_test_account"').replace('"max": "#"','"max": "https://example.com/max"');await route.fulfill(response=response,body=h)
  await page.route('**/docs/scheme2/d1/index.html',patched)
  await page.add_init_script("window.open=(url)=>{window.__opened=url;return null}")
  await page.goto(BASE+'index.html');await page.locator('.boarding-pass [data-messenger]').first.click();value=await page.evaluate('window.__opened');assert value.startswith('https://t.me/mango_test_account?text=');assert 'Анталья'in parse_qs(urlsplit(value).query)['text'][0]
  report['configured_telegram_url_verified']=True
  await ctx.close()
  # 1366 × 768 is the stricter compact-service constraint.
  ctx=await browser.new_context(viewport={'width':1366,'height':768});page=await ctx.new_page()
  for s in D['services']:
   await page.goto(BASE+'uslugi/'+s['slug']+'/index.html');height=await page.locator('footer').evaluate('(e)=>e.getBoundingClientRect().top+scrollY');assert height<=998.4,(s['slug'],height);report['service_heights'].append({'page':s['slug'],'width':1366,'height':height})
  await browser.close()
 assert not report['errors'],report['errors'];assert not report['bad_resources'],report['bad_resources']
 (SITE/'STAGE31_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['service_heights','scenarios']},ensure_ascii=False),flush=True)
try:asyncio.run(main())
finally:server.shutdown()
