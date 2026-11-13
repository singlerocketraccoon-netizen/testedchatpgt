"""Stage 10: cruise source copy, preserved pages, links, and three-engine flows."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import asyncio,ast,hashlib,json,re,subprocess,sys,threading,copy
from engines7 import launch
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';D=json.loads((R/'tools/d1/data.json').read_text());PATH='otdyh/kruizy/index.html';NAME='Круизы по морям и рекам';WIDTHS=[360,390,768,1024,1280,1366,1440,1920]
class HTML(HTMLParser):
 def __init__(self,raw):super().__init__();self.tags=[];self.ids=[];self.parts=[];self.skip=0;self.feed(raw)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if'id'in a:self.ids.append(a['id'])
  if t in['script','style','svg']:self.skip+=1
 def handle_endtag(self,t):
  if t in['script','style','svg']:self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
def normalize(raw):
 raw=re.sub(r'<(?:a|button)\b[^>]*data-goal="service_request_cruises"[^>]*>.*?</(?:a|button)>','CRUISE_CTA',raw,flags=re.S)
 def a(m):
  v=m[0]
  return re.sub(r'href="[^"]*"','href="CRUISES"',v,count=1)if re.search(r'data-goal="(?:footer_holiday_cruises|mood_cruises)"',v)else v
 return re.sub(r'<a\b[^>]*>',a,raw)
report={'stage':10,'widths':WIDTHS,'engines':{},'errors':[],'failures':[],'scenarios':[],'links':0,'approval':'All cruise copy is a draft from the scheme; no approved docx.'}
frozen=json.loads((R/'tools/d1/stage10_preservation.json').read_text());data=copy.deepcopy(D);data.pop('cruise_page');next(c for c in data['home_rest']['cards']if c['slug']=='cruises')['target']='uslugi/index.html#cruises';assert hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True).encode()).hexdigest()==frozen['data_sha256']
for path,sha in frozen['html'].items():assert hashlib.sha256(normalize((S/path).read_text()).encode()).hexdigest()==sha,path
report['preserved_pages']=len(frozen['html']);report['other_pages_only_authorized_links_changed']=True
source=json.loads(subprocess.check_output(['node',str(R/'tools/d1/read_cruises10.cjs')],cwd=R));settings=source['settings'];p=D['cruise_page'];raw=(S/PATH).read_text();h=HTML(raw);text=re.sub(r'\s+',' ',' '.join(h.parts));required=[NAME,settings['intro'],settings['title']]+settings['items']+[v for pair in settings['checks']for v in pair]+['Что мы проверяем','Частые вопросы','Можно ли изменить предложенный вариант?','Да. Расскажите, какие условия Вам подходят, и мы скорректируем подборку.','Подобрать круиз','Расскажите, когда планируете поездку и что для Вас важно.','Обсудить вариант →']
assert all(v in text for v in required);assert p['intro']==settings['intro']and [x['title']for x in p['types']]==settings['items']and [[c['title'],c['text']]for c in p['checks']]==settings['checks'];assert p['message']==next(v['msg']for v in source['holidays']if v['name']==NAME)
reference=(R/'mango-structure-12-11-v2.html').read_text();assert all(v in reference for v in required);assert 'data-needs-approval'in raw;report['verbatim_passages']=len(required)
cache={f.resolve():HTML(f.read_text())for f in S.rglob('*.html')if'screens'not in f.parts};expected=(S/PATH).resolve();footers=menus=0
for f,doc in cache.items():
 assert len(doc.ids)==len(set(doc.ids)),f
 for tag,a in doc.tags:
  if tag in['button','a','summary']:assert 'data-goal'in a,(f,a)
  for attr in ['href','src']:
   v=a.get(attr,'');u=urlsplit(v)
   if not v or u.scheme or u.netloc:continue
   target=(f.parent/unquote(u.path)).resolve()if u.path else f;assert not u.path.startswith('/')and target.is_file(),(f,v)
   if u.fragment and target.suffix=='.html':assert unquote(u.fragment)in cache[target].ids,(f,v)
   report['links']+=1
  goal=a.get('data-goal','')
  if goal=='footer_holiday_cruises':assert (f.parent/a['href']).resolve()==expected;footers+=1
  if goal=='mood_cruises':assert (f.parent/a['href']).resolve()==expected
  if goal=='service_request_cruises':assert tag=='a'and(f.parent/a['href']).resolve()==expected
  if goal=='menu_service_cruises':assert(f.parent/urlsplit(a['href']).path).resolve()==S/'uslugi/index.html'and urlsplit(a['href']).fragment=='cruises';menus+=1
assert len([x for x in h.tags if x[0]=='h1'])==1;assert not re.search('WhatsApp|демо|прототип|lorem',raw,re.I)
for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S):
 graph=json.loads(s)['@graph'];assert any(x['@type']=='FAQPage'and len(x['mainEntity'])==1 for x in graph);assert any(x['@type']=='BreadcrumbList'for x in graph)
assert len(re.search('<title>(.*?)</title>',raw)[1])<=60 and len(re.search(r'<meta name="description" content="([^"]+)"',raw)[1])<=160
report['footer_links']=footers;report['service_menu_links_preserved']=menus
before={str(f):f.read_bytes()for f in S.rglob('*.html')if'screens'not in f.parts};subprocess.run([sys.executable,str(R/'tools/d1/build.py')],check=True,capture_output=True);assert all(Path(f).read_bytes()==v for f,v in before.items());report['deterministic_build']=True
# Shared geometry checks; no import of earlier acceptance runners with fixed data hashes.
module=ast.parse((R/'tools/d1/check8.py').read_text());GEOM=next(ast.literal_eval(n.value)for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='GEOMETRY'for t in n.targets))
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R/'docs'),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
async def scenario(browser,name,width):
 ctx=await browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');page=await ctx.new_page();await page.goto(BASE+PATH);await page.evaluate('document.fonts.ready')
 for i,item in enumerate(settings['items']):
  await page.locator('[data-goal=cruise_option_'+str(i)+']').click();pane=page.locator('#request-dialog [data-form-pane=pick]');assert await page.locator('#request-dialog').is_visible();assert await pane.locator('[data-form-context]').inner_text()==NAME+' · '+item
  await pane.locator('[name=city]').fill('Астрахань');await pane.locator('[name=phone]').fill('79991234567');await pane.locator('[data-messenger=Telegram]').click();message=await page.locator('[data-fallback-text]').input_value();assert 'Здравствуйте! Хочу подобрать круиз. '+item in message and 'Астрахань'in message and '9991234567'not in re.sub(r'\D','',message);await page.keyboard.press('Escape');await page.keyboard.press('Escape');assert not await page.locator('#request-dialog').is_visible()
 form=page.locator('#rest-inquiry-bottom');assert await form.locator('[data-form-context]').inner_text()==NAME
 await form.locator('[name=phone]').fill('79991234567');await form.locator('[type=submit]').click();assert await form.locator('[data-form-error]').inner_text();await form.locator('[name=consent]').check();await form.locator('[type=submit]').click();assert await form.locator('[data-form-success]').is_visible();assert not await form.locator('form').is_visible();assert await form.locator('[name=phone]').input_value()==''
 await page.goto(BASE+'index.html');await page.locator('[data-rest-toggle]').click();await page.locator('[data-goal=mood_cruises]').click();await page.wait_for_url('**/otdyh/kruizy/index.html')
 await page.goto(BASE+'uslugi/index.html#cruises');assert await page.locator('#cruises').get_attribute('open')is not None;await page.locator('[data-goal=service_request_cruises]').click();await page.wait_for_url('**/otdyh/kruizy/index.html')
 report['scenarios'].append(dict(engine=name,width=width,three_contexts_and_messenger='passed',phone_not_in_message=True,validation_and_local_result='passed',home_and_service_links='passed'));await ctx.close()
async def main():
 async with async_playwright()as pw:
  for name in ['chromium','firefox','webkit']:
   b=await launch(pw,name);report['engines'][name]={'version':b.version,'viewports':[]}
   for width in WIDTHS:
    ctx=await b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');page=await ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None);page.on('response',lambda r:report['errors'].append(str(r.status)+' '+r.url)if r.status>=400 else None);await page.goto(BASE+PATH);await page.evaluate('document.fonts.ready');g=await page.evaluate(GEOM)
    if g['overflow']or g['clipped']or g['select']or(max(g['bread'])-min(g['bread'])>1):report['failures'].append(dict(engine=name,width=width,geometry=g))
    layout=await page.evaluate('''()=>{const grid=document.querySelector('#types .rest-selection-grid'),cards=[...grid.children].map(e=>e.getBoundingClientRect()),r=grid.getBoundingClientRect(),cols=cards.filter(c=>Math.abs(c.top-cards[0].top)<1).length,checks=getComputedStyle(document.querySelector('.rest-check-list')).gridTemplateColumns.split(' ').length;return{cols,coverage:(cards[Math.min(cols,cards.length)-1].right-r.left)/r.width,checks};}''');assert layout['cols']==(3 if width>=1024 else 1 if width<600 else 2)and layout['coverage']>=.9 and layout['checks']==(2 if width>=1024 else 1),(name,width,layout)
    report['engines'][name]['viewports'].append(dict(width=width,layout=layout));await ctx.close()
   for width in[390,1440]:await scenario(b,name,width)
   await b.close()
 report['status']='passed'if not report['errors']and not report['failures']else'failed';assert report['status']=='passed',(report['errors'],report['failures']);print('Stage 10 passed: 24 viewports, 6 functional flows',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown();(S/'QA10.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
