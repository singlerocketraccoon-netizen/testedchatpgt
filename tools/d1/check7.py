"""Stage 7 acceptance: approved copy, static HTML, links, cross-engine layout and flows."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import asyncio,json,re,threading,subprocess,sys,hashlib
from engines7 import launch
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'docs/scheme2/d1';D=json.loads((ROOT/'tools/d1/data.json').read_text());PAGES=json.loads((ROOT/'tools/d1/pages.json').read_text());WIDTHS=[360,390,414,768,1024,1280,1366,1440,1536,1920]
class HTML(HTMLParser):
 def __init__(self,s):super().__init__();self.tags=[];self.parts=[];self.ids=[];self.skip=0;self.feed(s)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if'id'in a:self.ids.append(a['id'])
  if t in['script','style','svg']:self.skip+=1
 def handle_endtag(self,t):
  if t in['script','style','svg']:self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
norm=lambda s:re.sub(r'\s+',' ',s).strip()
report={'widths':WIDTHS,'engines':{},'approved_copy':{},'links':0,'errors':[],'layout':[],'scenarios':[]}
cache={p.resolve():HTML(p.read_text())for p in S.rglob('*.html')if'screens'not in p.parts};titles=[];descriptions=[]
for path,h in cache.items():
 assert len(h.ids)==len(set(h.ids)),(path,'duplicate ids')
 for tag,a in h.tags:
  for n in['href','src']:
   v=a.get(n,'');u=urlsplit(v)
   if not v or u.scheme or u.netloc:continue
   target=(path.parent/unquote(u.path)).resolve()if u.path else path
   assert not u.path.startswith('/')and target.is_file(),(path,v)
   if u.fragment and target.suffix=='.html':assert unquote(u.fragment)in cache[target].ids,(path,v)
   report['links']+=1
for row in PAGES:
 path=S/row['path'];raw=path.read_text();h=cache[path.resolve()];assert sum(t=='h1'for t,a in h.tags)==1,path
 for tag,attrs in h.tags:
  if tag in ['a','button','summary']:assert 'data-goal'in attrs,(path,tag,attrs)
 title=re.search('<title>(.*?)</title>',raw)[1];description=re.search(r'<meta name="description" content="([^"]*)"',raw)[1];assert len(title)<=60 and len(description)<=160; titles.append(title);descriptions.append(description)
 assert not re.search(r'WhatsApp|демо|прототип|lorem',raw,re.I),path
 for rawjson in re.findall(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S):json.loads(rawjson)
 for form in re.findall(r'<form\b.*?</form>',raw,re.S):
  a=HTML(form);hidden=[v['name']for t,v in a.tags if t=='input'and v.get('type')=='hidden'];assert hidden==['topic','page','utm_source','utm_medium','utm_campaign','utm_content','utm_term']
  assert any(t=='input'and a.get('name')=='consent'and'required'in a and'checked'not in a for t,a in a.tags)
assert len(set(titles))==len(titles);assert len(set(descriptions))==len(descriptions)
for p in D['rest_pages']:
 raw=(S/'otdyh'/p['slug']/'index.html').read_text();h=HTML(raw);text=norm(' '.join(h.parts));missing=[v for v in p['approved_paragraphs']if norm(v)not in text];assert not missing,(p['slug'],missing)
 assert not any(v in text for v in['Рабочий документ','Четыре небольшие карточки','Проверить перед публикацией','Отели выберем позже'])
 assert re.findall(r'data-rest-section="([^"]+)"',raw)==p['section_order'];assert 'rest-anchor-nav'not in raw
 report['approved_copy'][p['slug']]=len(p['approved_paragraphs'])
 # Independently read paragraphs from the approved Markdown snapshot, not the rendered fields.
 source=p['source_markdown'];root_source=ROOT/p['source_file'];assert not root_source.exists()or root_source.read_text().rstrip()==source.rstrip()
 assert hashlib.sha256(source.encode()).hexdigest()==p['source_sha256']
 blocks={int(n):v for n,v in re.findall(r'^# ([1-7])\. ([\s\S]*?)(?=^# |\Z)',source,re.M)};required=[]
 for n,body in blocks.items():
  paras=[v.strip()for v in re.split(r'\n\s*\n',body.split('\n',1)[1])if v.strip()]
  if n in[1,7]:required += [v.split(': ',1)[1]for v in paras if v.startswith(('Акцент:','Заголовок:','Описание:','Строка:'))]
  elif n==2:required += [v[2:]if v.startswith('- ')else v for v in paras if v.startswith(('- ','Например:'))]
  elif n==3:required += [v for v in paras if not v.startswith(('Три небольшие','Четыре небольшие','Фото:'))]
  elif n==4:
   required += [v.strip()for line in body.splitlines()if line.startswith('|')and not line.startswith(('|---','| Направление'))for v in line.strip('|').split('|')]
  elif n==5:
   required += re.findall(r'Строка связи: «([^»]+)»',body)+re.findall(r'например, «([^»]+)»',body)
  elif n==6:required += [v[2:]if v.startswith('- ')else v for v in paras]
 assert all(norm(v)in text for v in required),(p['slug'],[v for v in required if norm(v)not in text])
 report['approved_copy'][p['slug']]=len(required)
for p in(S/'css').glob('*.css'):
 if p.name=='tokens.css':continue
 assert not re.search(r'font-size\s*:\s*(?!var\()[^;{}]*\d(?:px|rem|vw)|font\s*:[^;{}]*\dpx',p.read_text()),p
assert not any((S/'css'/('stage'+str(i)+'.css')).exists()for i in[4,5,6])
before={str(p.relative_to(S)):p.read_bytes()for p in S.rglob('*.html')if'screens'not in p.parts};subprocess.run([sys.executable,str(ROOT/'tools/d1/build.py')],check=True,capture_output=True);assert before=={str(p.relative_to(S)):p.read_bytes()for p in S.rglob('*.html')if'screens'not in p.parts};report['deterministic_build']=True
if '--static'in sys.argv:print(json.dumps({k:v for k,v in report.items()if k in['approved_copy','links','deterministic_build']},ensure_ascii=False));sys.exit()
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/docs/scheme2/d1/'
CHECK=r'''()=>{
 const shown=e=>e.getClientRects().length&&!e.closest('script,style,svg,dialog:not([open]),[hidden]');const small=[],clipped=[],serif=[];
 for(const e of document.querySelectorAll('body *')){
  if(!shown(e)||![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;
  const s=getComputedStyle(e),size=parseFloat(s.fontSize);if(size<13)small.push([e.tagName,e.className,e.textContent.trim().slice(0,45),size]);
  if(s.fontFamily.includes('Cormorant')&&!e.closest('[aria-hidden=true]')&&(size<22||(size<32&&parseInt(s.fontWeight)<500)))serif.push([e.className,size,s.fontWeight]);
  if((e.matches('button,.btn,.rest-card,.person-card,.ticket-body')||e.getAttribute('data-test-fit'))&&(e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2))clipped.push([e.tagName,e.className,e.scrollWidth,e.clientWidth,e.scrollHeight,e.clientHeight]);
 }
 const h=[...document.querySelectorAll('.header-inner .brand,.nav-left,.nav-about,.header-contacts')].filter(shown).map(e=>{const r=e.getBoundingClientRect();return{n:e.className,x:r.x,w:r.width,y:r.y+r.height/2}});
 return{overflow:document.documentElement.scrollWidth-innerWidth,small,clipped,serif,header:h};
}'''
async def scenarios(browser,name,width):
 context=await browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');page=await context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 await page.goto(BASE+'otdyh/otdyh-s-detmi/index.html?country=egipet');await page.evaluate('document.fonts.ready');assert await page.locator('[data-rest-tab=egipet]').get_attribute('aria-selected')=='true'
 await page.locator('[data-rest-country=turciya]').click();assert await page.locator('[data-rest-panel=turciya]').is_visible();assert 'country=turciya'in page.url
 await page.locator('[data-rest-panel=turciya] [data-open-form]').first.click();assert await page.locator('#request-dialog').is_visible();assert await page.locator('#request-dialog [data-form-pane=pick] [data-form-context]').inner_text()=='Отдых с детьми · Турция · Отель 1';assert await page.locator('#request-dialog [name=who]').first.input_value()=='С детьми'
 await page.locator('#request-dialog [data-form-pane=pick] [name=city]').fill('Астрахань');await page.locator('#request-dialog [data-form-pane=pick] [name=phone]').fill('79991234567');await page.locator('#request-dialog [data-form-pane=pick] [data-messenger=Telegram]').click();message=await page.locator('[data-fallback-text]').input_value();assert 'Отдых с детьми. Турция. Отель 1'in message and 'Астрахань'in message and '999'not in message
 await page.keyboard.press('Escape');await page.keyboard.press('Escape');assert not await page.locator('#request-dialog').is_visible()
 await page.locator('[data-rest-panel=turciya] [data-rest-detail]').first.click();assert await page.locator('#rest-detail-turciya-1').is_visible();await page.keyboard.press('Escape')
 await page.locator('[data-rest-current-topic]').click();assert await page.locator('#request-dialog [data-form-pane=pick] [data-form-context]').inner_text()=='Отдых с детьми · Турция';await page.keyboard.press('Escape')
 await page.locator('[data-open-form="holiday:otdyh-s-detmi:country:egipet"]').first.click();assert await page.locator('#request-dialog [data-form-pane=pick] [data-form-context]').inner_text()=='Отдых с детьми · Египет';await page.keyboard.press('Escape')
 await page.locator('[data-rest-tab=egipet]').click();await page.locator('#checks details').first.evaluate('d=>d.open=true');await page.locator('#checks').scroll_into_view_if_needed();await page.wait_for_timeout(120);position=await page.evaluate('scrollY');await page.goto(BASE+'napravleniya/egipet/index.html');await page.go_back();await page.wait_for_timeout(150);assert await page.locator('[data-rest-tab=egipet]').get_attribute('aria-selected')=='true';assert await page.locator('#checks details').first.get_attribute('open')is not None;assert abs(await page.evaluate('scrollY')-position)<4,(name,width,'back position',position,await page.evaluate('scrollY'))
 await page.goto(BASE+'otdyh/svoj-marshrut/index.html');assert await page.locator('[data-rest-tabs]').count()==0;await page.locator('[data-rest-country=turciya]').click();await page.locator('#route-turciya [data-open-form]').click();assert 'Свой маршрут · Турция · Маршрут 1'==await page.locator('#request-dialog [data-form-pane=pick] [data-form-context]').inner_text();await page.keyboard.press('Escape')
 await page.goto(BASE+'index.html');await page.locator('[data-menu]'if width<1024 else'[aria-controls=nav-countries]').focus();await page.keyboard.press('Enter');assert await page.locator('#mobile-nav'if width<1024 else'#nav-countries').is_visible();await page.keyboard.press('Escape');assert await page.locator('[data-menu]'if width<1024 else'[aria-controls=nav-countries]').evaluate('e=>e===document.activeElement')
 assert not errors,errors;report['scenarios'].append({'engine':name,'width':width,'holiday_context_messenger_tabs_back_dialog_keyboard':'passed'});await context.close()
async def main():
 async with async_playwright()as p:
  for name in['chromium','firefox','webkit']:
   try:b=await launch(p,name)
   except Exception as e:report['engines'][name]={'status':'unavailable','reason':str(e)};continue
   report['engines'][name]={'status':'tested','version':b.version,'viewports':0}
   for width in WIDTHS:
    context=await b.new_context(viewport={'width':width,'height':844 if width<768 else 900},device_scale_factor=1.25 if width==1536 else 1,reduced_motion='reduce');page=await context.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None)
    for row in PAGES:
     await page.goto(BASE+row['path']);
     if row['type']=='redirect':await page.wait_for_url('**/o-nas/index.html#team')
     await page.evaluate('document.fonts.ready');value=await page.evaluate(CHECK)
     if width>=1024:
      logo=next(v for v in value['header']if v['n']=='brand');assert abs(logo['x']+logo['w']/2-width/2)<.2
      assert max(v['y']for v in value['header'])-min(v['y']for v in value['header'])<2
     if value['overflow']>0 or value['small']or value['clipped']or value['serif']:report['layout'].append({'engine':name,'width':width,'path':row['path'],**value})
     report['engines'][name]['viewports']+=1
    await context.close();print(name,width,'checked',flush=True)
   for width in[390,1440]:
    try:await scenarios(b,name,width)
    except Exception as e:report['errors'].append(name+' scenario '+str(width)+': '+str(e));print('SCENARIO ERROR',name,width,str(e),flush=True)
   # 200% desktop zoom corresponds to 640 CSS pixels in a 1280-pixel window.
   context=await b.new_context(viewport={'width':640,'height':450},device_scale_factor=2,reduced_motion='reduce');page=await context.new_page()
   for path in['index.html','otdyh/otdyh-s-detmi/index.html','o-nas/index.html']:
    await page.goto(BASE+path);value=await page.evaluate(CHECK)
    if value['overflow']>0 or value['small']or value['clipped']:report['layout'].append({'engine':name,'zoom':'200%','path':path,**value})
   await context.close();await b.close()
 (S/'STAGE7_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('RESULT',len(report['layout']),'layout findings',len(report['errors']),'errors',flush=True)
 assert not report['layout']and not report['errors']
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown()
