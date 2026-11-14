"""Static source, clean-copy reproducibility and stage-13 interactive scenarios."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from datetime import datetime,timedelta,timezone
import asyncio,json,re,hashlib,shutil,tempfile,subprocess,os,threading,sys
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.async_api import async_playwright
from engines7 import launch
from import_work13 import parse
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';D=json.loads((R/'tools/d1/data.json').read_text());PAGES=json.loads((R/'tools/d1/pages.json').read_text());report={'stage':13,'links':0,'engines':{},'scenarios':[]}
class HTML(HTMLParser):
 def __init__(self,s):super().__init__();self.tags=[];self.ids=[];self.text=[];self.skip=0;self.feed(s)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if'id'in a:self.ids.append(a['id'])
  if t in['script','style','svg']:self.skip+=1
 def handle_endtag(self,t):
  if t in['script','style','svg']:self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.text.append(s)
def static():
 assert parse(R/D['work13']['source'])==D['work13'],'Work source differs'
 cache={p.resolve():HTML(p.read_text())for p in S.rglob('*.html')if'screens'not in p.parts}
 for row in PAGES:
  path=S/row['path'];raw=path.read_text();h=cache[path.resolve()];assert len(h.ids)==len(set(h.ids)),row['path'];assert sum(t=='h1'for t,a in h.tags)==1,row['path'];assert not re.search('WhatsApp|демо|прототип|здесь будет|lorem',raw,re.I),row['path']
  for t,a in h.tags:
   if t=='input'and a.get('name')=='consent':assert'checked'not in a,row['path']
   if t=='img':
    assert all(k in a for k in['alt','width','height']),row['path']
    assert 'data-editable'in a or'logo-mango'in a.get('src',''),('Missing editable image/brand',row['path'])
   for attr in['href','src']:
    v=a.get(attr,'');u=urlsplit(v)
    if not v or u.scheme or u.netloc:continue
    target=(path.parent/unquote(u.path)).resolve()if u.path else path.resolve();assert not u.path.startswith('/')and target.is_file(),(row['path'],v)
    if u.fragment and target.suffix=='.html':assert unquote(u.fragment)in cache[target].ids,(row['path'],v)
    report['links']+=1
 work=' '.join(' '.join(cache[(S/'kak-my-rabotaem/index.html').resolve()].text).split());copy=D['work13']
 for text in [copy['intro'],copy['costText'],*copy['facts']]+[p for s in copy['stages']for step in s['steps']for p in step['paragraphs']]:assert text in work,text
 assert sum(len(s['steps'])for s in copy['stages'])==8
 report['source_exact']=True
 root=Path(tempfile.mkdtemp(prefix='mango13-clean-'));(root/'docs/scheme2').mkdir(parents=True);(root/'tools').mkdir()
 for p in R.iterdir():
  if p.is_file()and p.suffix.lower()in['.html','.md','.txt','.json','.svg','.png']:shutil.copy2(p,root/p.name)
 shutil.copytree(R/'tools/d1',root/'tools/d1',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(R/'docs/assets',root/'docs/assets');shutil.copytree(S,root/'docs/scheme2/d1',ignore=shutil.ignore_patterns('screens','__pycache__'))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');run=lambda:subprocess.run([sys.executable,str(root/'tools/d1/build.py')],check=True,capture_output=True,env=env)
 def snapshot():return{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in root.rglob('*')if p.is_file()}
 run();first=snapshot();run();second=snapshot();assert first==second,sorted(k for k in first.keys()|second.keys()if first.get(k)!=second.get(k));report['clean_rebuild']={'files':len(first),'changed':0}
 for row in PAGES:assert(S/row['path']).read_bytes()==(root/'docs/scheme2/d1'/row['path']).read_bytes(),('Clean output differs',row['path'])
 shutil.rmtree(root)
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(R/'docs'),**k)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
async def check(browser,engine):
 ctx=await browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');p=await ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 await p.goto(BASE+'uslugi/index.html');await p.evaluate('document.fonts.ready');assert await p.locator('.service-travel-card').count()==4 and await p.locator('.service-extra-card').count()==8
 for key in['packages','custom','tours','cruises','hotels','tickets','transfer','visas','insurance','airport','experiences','weddings']:
  button=p.locator('[data-goal="service_request_'+key+'"]')if key in['packages','custom','tours','cruises']else p.locator('[data-goal="service_'+key+'"]');await button.click();form=p.locator('#request-dialog [data-unified-form]:visible');assert await form.get_attribute('data-topic')=='service:'+key;await p.keyboard.press('Escape')
 await p.goto(BASE+'napravleniya/egipet/index.html');form=p.locator('.country-hero-form [data-unified-form]');await form.locator('details').evaluate('e=>e.open=true');await form.locator('[name=city]').fill('Астрахань');await form.locator('[name=who]').select_option(label='С детьми');assert await form.locator('[data-ages]').is_visible();await form.locator('[name=ages]').fill('2 взрослых, ребёнок 7 лет');await form.locator('[name=phone]').fill('9991234567');await form.locator('[data-messenger=Telegram]').click();text=await p.locator('[data-fallback-text]').input_value();assert'Египет'in text and'Астрахань'in text and'7 лет'in text and'999123'not in text
 await p.keyboard.press('Escape');await form.locator('button[type=submit]').click();assert await form.locator('[data-form-error]').inner_text();await form.locator('[name=consent]').check();await form.locator('button[type=submit]').click();assert await p.locator('.country-hero-form [data-form-success]').is_visible();assert not await form.locator('[name=consent]').is_checked();assert await form.locator('[name=phone]').input_value()==''
 await p.goto(BASE+'kak-my-rabotaem/index.html');await p.wait_for_timeout(80);assert await p.locator('[data-work-stage-link="stage-1"]').get_attribute('aria-current')=='step';await p.evaluate('scrollTo(0,document.documentElement.scrollHeight)');await p.wait_for_timeout(80);await p.evaluate('scrollTo(0,0)');await p.wait_for_timeout(80);assert await p.locator('[data-work-stage-link="stage-1"]').get_attribute('aria-current')=='step';assert await p.locator('.work-stage').count()==4 and await p.locator('.work-timeline-step').count()==8;assert await p.locator('#contract').get_attribute('data-needs-approval')=='owner-review';await p.locator('[data-work-stage-link="stage-3"]').click();await p.wait_for_timeout(150);assert await p.locator('[data-work-stage-link][aria-current]').count()==1 and await p.locator('[data-work-stage-link="stage-3"]').get_attribute('aria-current')=='step'
 await p.set_viewport_size({'width':390,'height':844});await p.goto(BASE+'index.html');await p.evaluate('scrollTo(0,document.querySelector("#moods").offsetTop+100)');await p.wait_for_timeout(150);assert await p.locator('.contact-dock').is_visible();await p.locator('footer').scroll_into_view_if_needed();await p.wait_for_timeout(100);assert not await p.locator('.contact-dock').is_visible();await p.locator('[data-end-form]').first.scroll_into_view_if_needed();await p.wait_for_timeout(100);assert not await p.locator('.contact-dock').is_visible()
 assert not errors,errors;await ctx.close();report['scenarios'].append(dict(engine=engine,service_topics=12,messenger_context_phone_excluded=True,callback_validation_and_clear=True,stepper=True,dock=True))
 # Controlled timers verify hover delay and fade delay without wall-clock flakiness.
 ctx=await browser.new_context(viewport={'width':1440,'height':900},reduced_motion='no-preference');p=await ctx.new_page();await p.goto(BASE+'index.html');await p.evaluate('document.fonts.ready');await p.clock.install(time=datetime(2030,1,1,tzinfo=timezone.utc));await p.clock.pause_at(datetime(2030,1,1,tzinfo=timezone.utc)+timedelta(seconds=10));g=p.locator('.menu-services');await g.dispatch_event('pointerenter',{'pointerType':'mouse'});await p.clock.fast_forward(99);assert await g.locator('button').first.get_attribute('aria-expanded')=='false';await p.clock.fast_forward(1);assert await g.locator('button').first.get_attribute('aria-expanded')=='true';assert await g.locator('.dropdown-panel').evaluate('e=>getComputedStyle(e).transitionDuration')=='0.2s';await g.dispatch_event('pointerleave',{'pointerType':'mouse'});await p.clock.fast_forward(199);assert await g.locator('button').first.get_attribute('aria-expanded')=='true';await p.clock.fast_forward(1);assert await g.locator('button').first.get_attribute('aria-expanded')=='false';await p.clock.fast_forward(150);assert not await g.locator('.dropdown-panel').is_visible();await ctx.close()
async def main():
 static();print('Static source/links and clean rebuild passed',flush=True)
 async with async_playwright()as pw:
  for engine in['chromium','firefox','webkit']:
   b=await launch(pw,engine);await check(b,engine);report['engines'][engine]=b.version;await b.close();print(engine,'scenarios passed',flush=True)
 report['status']='passed'
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown();(S/'QA13.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
