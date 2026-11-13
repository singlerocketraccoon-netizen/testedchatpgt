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
GEOMETRY=r'''()=>{
 const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],rect=e=>e.getBoundingClientRect(),shown=e=>e.getClientRects().length&&!e.closest('[hidden],dialog:not([open]),[inert],svg'),fail=[],rows=[];
 function textRect(e,first=false){if(!e)return null;const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let n,parts=[];while(n=w.nextNode()){if(!n.textContent.trim()||n.parentElement.closest('svg,[aria-hidden=true]'))continue;const z=document.createRange();z.selectNodeContents(n);parts.push(...z.getClientRects());if(first&&parts.length)return parts[0];}return parts.length?{top:Math.min(...parts.map(x=>x.top)),bottom:Math.max(...parts.map(x=>x.bottom)),left:Math.min(...parts.map(x=>x.left)),right:Math.max(...parts.map(x=>x.right)),height:Math.max(...parts.map(x=>x.bottom))-Math.min(...parts.map(x=>x.top))}:null;}
 let cards=0,selects=0,cormorant=0;
 if(document.documentElement.scrollWidth>innerWidth)fail.push({kind:'overflow',value:document.documentElement.scrollWidth-innerWidth});
 for(const e of $$('button,.btn,select,.ticket-price-value'))if(shown(e)&&(e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2))fail.push({kind:'clipped',element:e.className,text:e.textContent.slice(0,45),width:e.clientWidth,scroll:e.scrollWidth});
 for(const e of $$('body *'))if(shown(e)&&getComputedStyle(e).fontFamily.includes('Cormorant')){cormorant++;if(!getComputedStyle(e).fontVariantNumeric.includes('lining-nums'))fail.push({kind:'numeric',class:e.className});}
 for(const e of $$('select'))if(shown(e)){selects++;const s=getComputedStyle(e);if(s.appearance!=='none'||parseFloat(s.paddingRight)!==44||!s.backgroundPosition.includes('16px')||!s.backgroundImage.includes('svg'))fail.push({kind:'select',class:e.className,appearance:s.appearance,padding:s.paddingRight,pos:s.backgroundPosition,image:s.backgroundImage});const ctx=document.createElement('canvas').getContext('2d');ctx.font=s.font;const chosen=e.options[e.selectedIndex]?.text||'',need=ctx.measureText(chosen).width+parseFloat(s.paddingLeft)+44;if(need>rect(e).width+1)fail.push({kind:'select-text',chosen,width:rect(e).width,need});}
 const crumbs=$$('.breadcrumbs li');if(innerWidth<768)for(const e of crumbs){const r=rect(e);if(r.left<-1||r.right>innerWidth+1)fail.push({kind:'breadcrumb-overflow',t:e.textContent,r:r.right});}
 const byParent=new Map();for(const c of $$('.equal-card').filter(shown)){let a=byParent.get(c.parentElement)||[];a.push(c);byParent.set(c.parentElement,a);cards++;}
 const ctaSelector='.ticket-link,.rest-destination-actions>:last-child,.country-card-body>.text-link,.rest-selection-body>.text-link,.rest-format-card>.text-link,.document-card>.text-link,.person-card .text-link,.review-signature,.country-index-card a>div:not(.country-photo-placeholder)>span:last-child';
 for(const [g,all]of byParent){const groups=[];for(const c of all){const y=rect(c).top;let row=groups.find(a=>Math.abs(a.y-y)<2);if(!row){row={y,c:[]};groups.push(row);}row.c.push(c);}
  for(const row of groups){if(row.c.length<2)continue;const heights=row.c.map(c=>rect(c).height),titles=row.c.map(c=>textRect(c.querySelector('h2,h3,.rest-label,.country-resort summary>span,.country-hotel-open>span'),true)).filter(Boolean),actions=row.c.map(c=>[...c.querySelectorAll(ctaSelector)].filter(shown).at(-1)).filter(Boolean),bottoms=actions.map(e=>rect(e).bottom),titleTops=titles.map(r=>r.top);const diff=a=>a.length?Math.max(...a)-Math.min(...a):0;
   const item={grid:g.className,count:row.c.length,heights:heights.map(n=>+n.toFixed(2)),heightDelta:diff(heights),titleDelta:diff(titleTops),actionDelta:diff(bottoms)};rows.push(item);
   if(innerWidth>=1024&&(item.heightDelta>1||item.titleDelta>1||item.actionDelta>1))fail.push({kind:'row',...item});
  }
 }
 const mood=$('.mood-subtitle');if(mood&&innerWidth>=1280){const r=rect(mood),h=rect($('.mood-section h2'));if(Math.abs(r.left+r.width/2-h.left-h.width/2)>2)fail.push({kind:'mood-subtitle',delta:r.left+r.width/2-h.left-h.width/2});}
 for(const card of $$('.rest-card').filter(shown)){const t=textRect($('.rest-label',card),true);if(!t)continue;for(const icon of $$('.rest-symbol .icon,.rest-caption>.icon',card)){const r=rect(icon),delta=r.top+r.height/2-t.top-t.height/2;if(Math.abs(delta)>2)fail.push({kind:'mood-icon',title:$('.rest-label',card).textContent,delta});}}
 const nums=$$('.country-temperature strong');if(nums.length){const tops=nums.map(e=>rect(e).top),sizes=nums.map(e=>getComputedStyle(e).fontSize),labels=$$('.country-temperature p>span').map(e=>textRect(e,true).top);if(new Set(sizes).size>1||Math.max(...tops)-Math.min(...tops)>1||Math.max(...labels)-Math.min(...labels)>1)fail.push({kind:'climate-alignment',tops,sizes,labels});}
 return{fail,rows,cards,selects,cormorant};
}'''
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
