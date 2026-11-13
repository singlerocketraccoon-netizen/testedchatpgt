"""Owner revision 11: static facts, contrast, typography and every rendered row."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import asyncio,json,re,hashlib,subprocess,sys,threading
from engines7 import launch
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';PAGES=json.loads((R/'tools/d1/pages.json').read_text());D=json.loads((R/'tools/d1/data.json').read_text());WIDTHS=[360,390,768,1024,1280,1366,1440,1920,2560]
class HTML(HTMLParser):
 def __init__(self,s):super().__init__();self.tags=[];self.ids=[];self.parts=[];self.skip=0;self.feed(s)
 def handle_starttag(self,t,a):
  a=dict(a);self.tags.append((t,a))
  if'id'in a:self.ids.append(a['id'])
  if t in['script','style','svg']:self.skip+=1
 def handle_endtag(self,t):
  if t in['script','style','svg']:self.skip-=1
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
def luminance(h):
 a=[int(h[i:i+2],16)/255 for i in[1,3,5]];a=[v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in a];return sum(x*y for x,y in zip(a,[.2126,.7152,.0722]))
def contrast(a,b):return (max(luminance(a),luminance(b))+.05)/(min(luminance(a),luminance(b))+.05)
report={'stage':11,'widths':WIDTHS,'errors':[],'failures':[],'engines':{},'links':0,'scenarios':[],'cards':0,'selects':0,'cormorant_nodes':0,'contrast':{},'row_diagnostics':[]}
for key,digest in json.loads((R/'tools/d1/content11-lock.json').read_text()).items():
 assert hashlib.sha256(json.dumps(D[key],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()==digest,('Changed existing content',key)
report['existing_content_unchanged']=True
old=re.compile(r'#(?:ae2928|8f2121)|\b(?:174[ ,]+41[ ,]+40|143[ ,]+33[ ,]+33)\b',re.I)
for p in list((S/'css').glob('*.css'))+list((S/'js').glob('*.js')):assert not old.search(p.read_text()),p
for bg in['#FFFFFF','#F6F1E9','#FAF7F1']:
 report['contrast'][bg]=contrast('#A9532B',bg);assert report['contrast'][bg]>=4.5
report['contrast']['sand_link']=contrast('#8C4322','#EDE4D8');assert report['contrast']['sand_link']>=4.5
cache={p.resolve():HTML(p.read_text())for p in S.rglob('*.html')if'screens'not in p.parts};titles=[];descs=[]
for path,h in cache.items():
 assert len(h.ids)==len(set(h.ids)),path
 for tag,a in h.tags:
  for attr in['href','src']:
   v=a.get(attr,'');u=urlsplit(v)
   if not v or u.scheme or u.netloc:continue
   target=(path.parent/unquote(u.path)).resolve()if u.path else path;assert not u.path.startswith('/')and target.is_file(),(path,v)
   if u.fragment and target.suffix=='.html':assert unquote(u.fragment)in cache[target].ids,(path,v)
   report['links']+=1
for row in PAGES:
 raw=(S/row['path']).read_text();h=cache[(S/row['path']).resolve()];assert sum(t=='h1'for t,a in h.tags)==1
 assert not re.search('WhatsApp|демо|прототип|lorem',raw,re.I),row['path']
 title=re.search('<title>(.*?)</title>',raw)[1];desc=re.search(r'<meta name="description" content="([^"]+)"',raw)[1];assert len(title)<=60 and len(desc)<=160;titles.append(title);descs.append(desc)
 for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S):json.loads(x)
assert len(set(titles))==len(titles)and len(set(descs))==len(descs)
req=S/'o-nas/dokumenty/rekvizity/index.html';raw=req.read_text();text=' '.join(HTML(raw).parts)
assert [f['value']for f in D['requisites']['fields']]==['ИП Зарщиков Михаил Юрьевич','301504796247','310301510600012','Добавим из карточки реквизитов','Добавим актуальные контакты','10:00–19:00 МСК']
assert D['requisites']['intro']=='Здесь можно проверить Mango Travel в официальных реестрах и ознакомиться с документами агентства.'
for f in D['requisites']['fields']:assert f['value']in text
for f in D['requisites']['documents']:assert f['title']in text
assert 'РТА 0020071'in text and 'https://ev.economy.gov.ru/lk_exp/registry/'in raw and 'https://egrul.nalog.ru/'in raw and '"taxID": "301504796247"'in raw
assert all(not f['url']for f in D['requisites']['documents'])
for r in D['reviews'][:3]:assert r['text']in (S/'o-nas/otzyvy/index.html').read_text()
if '--skip-build'not in sys.argv:
 before={str(p):p.read_bytes()for p in S.rglob('*.html')if'screens'not in p.parts};subprocess.run([sys.executable,str(R/'tools/d1/build.py')],check=True,capture_output=True);assert all(Path(p).read_bytes()==v for p,v in before.items());report['deterministic_build']=True
if '--static'in sys.argv:print(json.dumps(report,ensure_ascii=False));sys.exit()
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R/'docs'),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
from geometry11 import GEOMETRY
async def scenarios(browser,name):
 ctx=await browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');p=await ctx.new_page();await p.goto(BASE+'napravleniya/egipet/index.html');await p.evaluate('document.fonts.ready');await p.evaluate('MangoLayout.refresh()');before=await p.locator('[data-resort-card=sharm],[data-resort-card=gouna]').evaluate_all('a=>a.map(e=>e.getBoundingClientRect().height)');await p.locator('[data-resort-card=hurghada] summary').click();after=await p.locator('[data-resort-card=sharm],[data-resort-card=gouna]').evaluate_all('a=>a.map(e=>e.getBoundingClientRect().height)');assert all(abs(a-b)<=1 for a,b in zip(before,after)),(name,before,after)
 await p.goto(BASE+'o-nas/dokumenty/rekvizity/index.html');await p.locator('[data-agency-document]').first.click();assert await p.locator('#agency-document-agency-1').is_visible();await p.keyboard.press('Escape');assert not await p.locator('#agency-document-agency-1').is_visible()
 for path in ['o-nas/index.html','o-nas/otzyvy/index.html','o-nas/kontakty/index.html','o-nas/dokumenty/index.html']:
  await p.goto(BASE+path);tabs=p.locator('.section-tabs a');assert await tabs.count()==4;assert await p.locator('.section-tabs [aria-current=page]').count()==1;assert await p.locator('.section-tabs [aria-current=page]').get_attribute('href')=='index.html'
 report['scenarios'].append(dict(engine=name,closed_resorts={'before':before,'after':after},document_dialog_escape='passed',about_navigation='passed'));await ctx.close()
async def main():
 engines=['chromium','firefox','webkit'];widths=WIDTHS
 if '--engine'in sys.argv:engines=[sys.argv[sys.argv.index('--engine')+1]]
 if '--width'in sys.argv:widths=[int(s)for s in sys.argv[sys.argv.index('--width')+1].split(',')]
 async with async_playwright()as pw:
  for name in engines:
   b=await launch(pw,name);report['engines'][name]={'version':b.version,'cases':0}
   for width in widths:
    ctx=await b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');p=await ctx.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)));p.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None)
    for row in PAGES:
     await p.goto(BASE+row['path']);
     if row['type']=='redirect':await p.wait_for_url('**/o-nas/index.html#team')
     await p.evaluate('''async()=>{await document.fonts.ready;MangoLayout.refresh();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}''');result=await p.evaluate(GEOMETRY)
     if result['fail']:report['failures'].append(dict(engine=name,width=width,page=row['path'],failures=result['fail']))
     report['cards']+=result['cards'];report['selects']+=result['selects'];report['cormorant_nodes']+=result['cormorant'];report['engines'][name]['cases']+=1
     if result['fail']and width>=1024:report['row_diagnostics'].append(dict(engine=name,width=width,page=row['path'],rows=result['rows']))
    await ctx.close();(S/'QA11.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(name,width,'complete;',len(report['failures']),'failures',flush=True)
   await scenarios(b,name);await b.close()
 report['status']='passed'if not report['failures']and not report['errors']else'failed';assert report['status']=='passed',(len(report['failures']),report['errors']);print('Stage 11 passed',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown();(S/'QA11.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
