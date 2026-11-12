"""Stage 8 acceptance: source copy, links, browser geometry and country interactions."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import asyncio,json,re,threading,subprocess,sys,hashlib
from engines7 import launch
from playwright.async_api import async_playwright
from import_country8 import source_data,copy_data
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'docs/scheme2/d1';D=json.loads((ROOT/'tools/d1/data.json').read_text());PAGES=json.loads((ROOT/'tools/d1/pages.json').read_text());WIDTHS=[360,390,768,1024,1280,1366,1440,1920]
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
report={'widths':WIDTHS,'engines':{},'approved_copy':{},'links':0,'errors':[],'geometry_failures':[],'width_exceptions':[],'scenarios':[],'header':[]}
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
  if tag in['a','button','summary']:assert 'data-goal'in attrs,(path,tag,attrs)
 title=re.search('<title>(.*?)</title>',raw)[1];desc=re.search(r'<meta name="description" content="([^"]*)"',raw)[1];assert len(title)<=60 and len(desc)<=160; titles.append(title);descriptions.append(desc)
 assert not re.search(r'WhatsApp|демо|прототип|lorem',raw,re.I),path
 for rawjson in re.findall(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S):json.loads(rawjson)
 for form in re.findall(r'<form\b.*?</form>',raw,re.S):
  a=HTML(form);hidden=[v['name']for t,v in a.tags if t=='input'and v.get('type')=='hidden'];assert hidden==['topic','page','utm_source','utm_medium','utm_campaign','utm_content','utm_term']
  assert any(t=='input'and a.get('name')=='consent'and'required'in a and'checked'not in a for t,a in a.tags)
assert len(set(titles))==len(titles);assert len(set(descriptions))==len(descriptions)
# Compare public copy with the external source, not merely with rendered JSON fields.
src=source_data();copy=copy_data();egypt=next(c for c in D['countries']if c['slug']=='egipet');raw=(S/'napravleniya/egipet/index.html').read_text();text=norm(' '.join(HTML(raw).parts));required=[copy[k]for k in['subtitle','seasonIntro','resortsIntro','combine']]+[v for r in src['resorts']for k,v in r.items()if k in['name','short','beach','mood','road','note']]+src['redSeaLines']+src['alameinLines']+[t[k]for t in copy['tips']for k in['title','text']]+[t[k]for t in copy['experiences']for k in['title','text']]+[t[k]for t in src['essentials']for k in['q','a']]
assert all(norm(v)in text for v in required),[v for v in required if norm(v)not in text];assert egypt['climate']==src['climate'];assert len(egypt['resorts'])==7
for r in egypt['resorts']:
 table=re.search(r'data-weather-table="'+r['id']+'".*?</table>',raw,re.S)[0];cells=[norm(' '.join(HTML(x).parts))for x in re.findall('<td>(.*?)</td>',table)]
 for i in range(12):assert cells[i*3:i*3+3]==['+'+str(src['climate'][r['w']]['air'][i])+' °C','+'+str(src['climate'][r['w']]['water'][i])+' °C',str(src['climate'][r['w']]['wind'][i])+' м/с']
report['approved_copy']['egypt']={'verbatim_passages':len(required),'climate_stations':4,'month_cells':7*12*3,'status':'passed'}
for p in D['rest_pages']:
 text=norm(' '.join(HTML((S/'otdyh'/p['slug']/'index.html').read_text()).parts));headings=[x['title'].rstrip(':.')for x in p['types']]+[x['text'].partition('. ')[0].rstrip(':.')for x in p['checks']]
 def heading_punctuation(s):
  for h in sorted(headings,key=len,reverse=True):s=s.replace(h+':',h).replace(h+'.',h)
  return norm(s)
 missing=[v for v in p['approved_paragraphs']if heading_punctuation(v)not in heading_punctuation(text)];assert not missing,(p['slug'],missing)
 report['approved_copy'][p['slug']]='passed (only heading terminal punctuation removed)'
before={str(p.relative_to(S)):p.read_bytes()for p in S.rglob('*.html')if'screens'not in p.parts};subprocess.run([sys.executable,str(ROOT/'tools/d1/build.py')],check=True,capture_output=True);assert before=={str(p.relative_to(S)):p.read_bytes()for p in S.rglob('*.html')if'screens'not in p.parts};report['deterministic_build']=True
from offers8 import check as check_offer_flags
report['offer_visibility']=check_offer_flags()
if '--static'in sys.argv:print(json.dumps(report,ensure_ascii=False));sys.exit()
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT/'docs'),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
GEOMETRY=r'''()=>{
 const shown=e=>e.getClientRects().length&&!e.closest('script,style,svg,dialog:not([open]),[hidden],[inert]');const r=e=>e.getBoundingClientRect();
 const clipped=[];for(const e of document.querySelectorAll('button,.btn,.rest-card,.person-card,select'))if(shown(e)&&(e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2))clipped.push([e.tagName,e.className,e.scrollWidth,e.clientWidth,e.scrollHeight,e.clientHeight]);
 const bread=[...document.querySelectorAll('.breadcrumbs li')].filter(shown).map(e=>{const el=e.querySelector('a,[aria-current]')||e,range=document.createRange();range.selectNodeContents(el);const a=range.getBoundingClientRect();return a.y+a.height/2;});
 const groups=[];if(innerWidth>=1024){const l=r(document.querySelector('.header-inner .brand')),left=r(document.querySelector('.nav-left')),right=r(document.querySelector('.nav-about'));groups.push({center:l.x+l.width/2-innerWidth/2,leftGap:l.x-left.right,rightGap:right.x-l.right,oneLine:[...document.querySelectorAll('.nav-left>*,.nav-about>*')].every(e=>r(e).height<=45)});}
 const blocks=[];if(innerWidth===1280||innerWidth===1920)for(const box of document.querySelectorAll('main .section>.container,main .inner-section>.container')){if(!shown(box)||['grid','flex'].includes(getComputedStyle(box).display))continue;const b=r(box),kids=[...box.children].filter(e=>shown(e)&&!e.matches('.section-head,h1,h2,h3,p,script,dialog')&&!e.classList.contains('country-passport-link'));for(const e of kids){const a=r(e),style=getComputedStyle(e);if(a.width<80)continue;const ratio=(a.right-b.left)/b.width,centered=Math.abs(a.x+a.width/2-b.x-b.width/2)<3;if(ratio<.85&&!centered)blocks.push({section:box.parentElement.id||box.parentElement.className,element:e.className||e.tagName,ratio,centered});}}
 const select=[];const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');for(const e of document.querySelectorAll('select[name=month]'))if(shown(e)){const s=getComputedStyle(e);ctx.font=s.font;const needed=ctx.measureText('Пока не определились').width+parseFloat(s.paddingLeft)+parseFloat(s.paddingRight)+22;if(needed>r(e).width+1)select.push({width:r(e).width,needed});}
 const forms=[...document.querySelectorAll('.country-hero-form,.rest-hero-form')].filter(shown).map(e=>({bottom:r(e.querySelector('button[type=submit]')).bottom}));return {overflow:document.documentElement.scrollWidth-innerWidth,clipped,bread,header:groups[0],blocks,select,forms};
}'''
async def flow(b,name,width):
 ctx=await b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');p=await ctx.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)));await p.goto(BASE+'napravleniya/egipet/index.html');await p.evaluate('document.fonts.ready')
 await p.locator('[data-weather-resort]').select_option('gouna');await p.locator('[data-weather-month="3"]').click();assert 'метеостанции Хургады'in await p.locator('[data-weather-label]').inner_text();assert await p.locator('[data-weather-air]').inner_text()=='+26 °C';assert await p.locator('[data-weather-wind]').inner_text()=='6 м/с';assert await p.locator('[data-weather-note="gouna-3"]').is_visible()
 await p.locator('[data-resort-card=gouna] summary').click();await p.locator('[data-resort-hotels=gouna]').click();assert await p.locator('[data-hotel-filter]').input_value()=='gouna';assert await p.locator('[data-hotel-empty]').is_visible()
 await p.locator('[data-resort-weather=gouna]').click();assert await p.locator('[data-weather-resort]').input_value()=='gouna';assert await p.locator('#season').evaluate('e=>e.getBoundingClientRect().top')>=0
 await p.locator('[data-more-resorts]').click();assert await p.locator('[data-resort-card=alamein]').is_visible();await p.locator('[data-more-resorts]').click();assert not await p.locator('[data-resort-card=alamein]').is_visible()
 await p.locator('[data-hotel-filter]').select_option('sharm');await p.locator('[data-country-hotel=hotel-2]').click();assert await p.locator('#hotel-2-dialog').is_visible();await p.keyboard.press('Escape');assert not await p.locator('#hotel-2-dialog').is_visible()
 await p.locator('[data-country-hotel=hotel-2]').click();await p.locator('#hotel-2-dialog [data-open-form]').click();assert await p.locator('#request-dialog').is_visible();await p.locator('#request-dialog [data-form-pane=pick] [name=city]').fill('Астрахань');await p.locator('#request-dialog [data-form-pane=pick] [name=phone]').fill('79991234567');await p.locator('#request-dialog [data-form-pane=pick] [data-messenger=Telegram]').click();msg=await p.locator('[data-fallback-text]').input_value();assert 'Здравствуйте! Интересует отель Отель 2'in msg and 'Астрахань'in msg and '999123'not in msg;await p.keyboard.press('Escape');await p.keyboard.press('Escape');await p.keyboard.press('Escape')
 for id in['entry','flight']:
  await p.locator('[href="#'+id+'"][data-open-essential]').click();assert await p.locator('#'+id).get_attribute('open')is not None
 for id in['season','resorts','offers','hotels','experiences','essentials']:
  await p.locator('[data-country-anchor][href="#'+id+'"]').click();await p.wait_for_timeout(100);assert await p.locator('[data-country-anchor][href="#'+id+'"]').get_attribute('aria-current')=='location',(name,width,id)
 if width<768:
  await p.locator('#hotels').scroll_into_view_if_needed();await p.wait_for_timeout(100);assert await p.locator('[data-mobile-contact]').is_visible();await p.locator('#inquiry form').scroll_into_view_if_needed();await p.wait_for_timeout(100);assert not await p.locator('[data-mobile-contact]').is_visible()
 await ctx.close();report['scenarios'].append(dict(engine=name,width=width,egypt='passed'))
async def main():
 async with async_playwright()as pw:
  for name in['chromium','firefox','webkit']:
   b=await launch(pw,name);report['engines'][name]={'version':b.version,'pages':0,'widths':WIDTHS}
   for width in WIDTHS:
    ctx=await b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');p=await ctx.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)));p.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None)
    for row in PAGES:
     await p.goto(BASE+row['path']);
     if row['type']=='redirect':await p.wait_for_url('**/o-nas/index.html#team')
     await p.evaluate('document.fonts.ready');result=await p.evaluate(GEOMETRY);entry=dict(engine=name,width=width,page=row['path'])
     errors={k:v for k,v in result.items()if k in['overflow','clipped','select']and v};bread=result['bread']
     if bread and max(bread)-min(bread)>1:errors['breadcrumbs']=bread
     if result['header']:
      h=result['header']
      if abs(h['center'])>2 or min(h['leftGap'],h['rightGap'])<32 or not h['oneLine']:errors['header']=h
     if width==1440 and any(x['bottom']>900 for x in result['forms']):errors['hero_cta']=result['forms']
     if errors:report['geometry_failures'].append(dict(**entry,errors=errors))
     if result['blocks']:report['width_exceptions'].append(dict(**entry,blocks=result['blocks']))
     report['engines'][name]['pages']+=1
    await ctx.close();print(name,width,'complete',len(report['geometry_failures']),'failures',flush=True)
   for width in[1024,1100,1200,1280,1366,1440,1920]:
    ctx=await b.new_context(viewport={'width':width,'height':900});p=await ctx.new_page();await p.goto(BASE+'index.html');await p.evaluate('document.fonts.ready');h=(await p.evaluate(GEOMETRY))['header'];report['header'].append(dict(engine=name,width=width,**h));assert abs(h['center'])<=2 and min(h['leftGap'],h['rightGap'])>=32 and h['oneLine'],h;await ctx.close()
   for width in[390,1440]:await flow(b,name,width)
   await b.close()
 report['status']='passed'if not report['errors']and not report['geometry_failures']else'failed';(S/'QA8.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert report['status']=='passed',(report['errors'],report['geometry_failures']);print('Stage 8 passed',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:
  server.shutdown();(S/'QA8.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
