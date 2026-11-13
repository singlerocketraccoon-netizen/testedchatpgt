"""Stage 9: unchanged copy, declarative card counts, geometry and interactions."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from html.parser import HTMLParser
import asyncio,ast,hashlib,json,subprocess,sys,threading,copy,importlib.util
from engines7 import launch
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';D=json.loads((R/'tools/d1/data.json').read_text());PAGES=json.loads((R/'tools/d1/pages.json').read_text());WIDTHS=[360,390,768,1024,1280,1366,1440,1920]
# A fingerprint of all stage-8 data, with only the allowed Hainan capitalization normalized.
def protected_hash(d):
 d=copy.deepcopy(d)
 for c in d['countries']:
  for route in c['routes']:
   if c['slug']=='kitay'and route['id']=='hainan':route['name']='остров Хайнань'
 return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
EXPECTED_DATA_SHA='c8667150dfe7b09fac33a0a52d04f082623389dd1bdeb02b42b9ffc503addcc2'
assert protected_hash(D)==EXPECTED_DATA_SHA,'Unexpected copy or data change outside paragraph 2'
report={'stage':9,'base':'8b4161ed81061a9557c139f47801a702ceb0b278','widths':WIDTHS,'engines':{},'errors':[],'failures':[],'header':[],'cards':[],'consent':{'checked':0,'same_row':0,'wrapped':0},'prices':0,'scenarios':[],'protected_data_sha256':EXPECTED_DATA_SHA}
static=subprocess.check_output([sys.executable,str(R/'tools/d1/check8.py'),'--static'],cwd=R,text=True);report['static']=json.loads(static)
# Reuse the general stage-8 geometry expression without importing/running its browser suite.
module=ast.parse((R/'tools/d1/check8.py').read_text());GENERAL=next(ast.literal_eval(n.value)for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='GEOMETRY'for t in n.targets))
GRID_SELECTOR=':is(.country-page,.rest-page) :is(.country-grid,.country-experiences,.country-alternatives,.country-hotel-tips,.tickets-grid,.rest-format-grid,.rest-destination-grid,.rest-selection-grid),.country-index-grid'
DETAILS_SELECTOR='.country-grid,.rest-age-list,.rest-check-list,.country-essentials,.services-accordion-columns'
EXTRA=r'''()=>{
 const r=e=>e.getBoundingClientRect(),shown=e=>e.getClientRects().length&&!e.closest('[hidden],dialog:not([open]),[inert]'),fail=[],cards=[],prices=[];let consent=0,same=0,wrapped=0;
 for(const g of document.querySelectorAll('GRID_SELECTOR')){if(!shown(g)||innerWidth<1024)continue;const all=[...g.children].filter(shown);if(!all.length)continue;const a=r(all[0]),first=all.filter(e=>Math.abs(r(e).top-a.top)<2),gr=r(g),right=Math.max(...first.map(e=>r(e).right)),coverage=(right-gr.left)/gr.width,expected=all.length<=4?all.length:3;if(first.length!==expected||coverage<.9)fail.push({kind:'grid',grid:g.className,count:all.length,first:first.length,expected,coverage});cards.push({grid:g.className,count:all.length,first:first.length,coverage});}
 for(const e of document.querySelectorAll('.ticket-price-value'))if(shown(e)){const range=document.createRange();range.selectNodeContents(e);const rects=[...range.getClientRects()];if(rects.length!==1||e.scrollWidth>e.clientWidth+1)fail.push({kind:'price',text:e.textContent,width:e.clientWidth,scroll:e.scrollWidth,lines:rects.length});const sub=e.nextElementSibling,s=getComputedStyle(sub);if(r(sub).top<r(e).bottom-1||parseFloat(s.fontSize)>14.1||s.color!==getComputedStyle(e.closest('.ticket-body').querySelector('.ticket-price-date')).color)fail.push({kind:'party-price',text:sub.textContent,font:s.fontSize,color:s.color});prices.push(e.textContent);}
 function measure(c){const links=[...c.querySelectorAll('a')];if(links.length!==2)return;const [a,b]=links,ar=r(a),br=r(b);if(!a.getClientRects().length||!b.getClientRects().length)return;consent++;if(ar.height<44||br.height<44)fail.push({kind:'consent-target',heights:[ar.height,br.height]});if(Math.abs(ar.top-br.top)<1){const tr=e=>{const z=document.createRange();z.selectNodeContents(e);return z.getClientRects()[0];},x=tr(a),y=tr(b);same++;if(Math.abs(x.y+x.height/2-y.y-y.height/2)>1)fail.push({kind:'consent',centers:[x.y+x.height/2,y.y+y.height/2]});}else wrapped++;}
 // Inspect every form, including the three hidden request panes and the quiz.
 const oldY=scrollY;for(const c of document.querySelectorAll('.unified-consent')){const changed=[];for(let n=c;n&&n!==document.body;n=n.parentElement){if(n.hidden){n.hidden=false;changed.push([n,'hidden']);}if(n.tagName==='DIALOG'&&!n.open){n.setAttribute('open','');changed.push([n,'open']);}}measure(c);for(const [n,k]of changed.reverse()){if(k==='hidden')n.hidden=true;else n.removeAttribute('open');}}scrollTo(0,oldY);
 let header=null;if(innerWidth>=1024){const list=[...document.querySelectorAll('.nav-about>a,.nav-about>.nav-dropdown>button,.header-contacts>.header-phone,.header-contacts>[data-messenger]')],gaps=list.slice(1).map((e,i)=>r(e).left-r(list[i]).right);const targets=[...document.querySelectorAll('.header-contacts>.icon-control')].filter(shown).map(e=>({width:r(e).width,height:r(e).height}));header={gaps,targets};if(targets.some(t=>t.width<24||t.height<44))fail.push({kind:'header-target',targets});if(gaps.some(n=>n<23.9)||Math.max(...gaps)-Math.min(...gaps)>1)fail.push({kind:'header-gaps',gaps});}
 return {fail,cards,consent,same,wrapped,prices:prices.length,header};
}'''.replace('GRID_SELECTOR',GRID_SELECTOR)
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R/'docs'),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
def climate_fixtures():
 spec=importlib.util.spec_from_file_location('d1_stage9_fixtures',R/'tools/d1/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
 import stage4,country,stage6
 ctx=b.__dict__;stage4.configure(ctx);country.configure(ctx);stage6.configure(ctx);c=next(c for c in b.DATA['countries']if c['slug']=='turciya');old=copy.deepcopy(c['climate']);emit=ctx['emit'];seen=[];ctx['emit']=lambda *a,**kw:seen.append((a,kw));result=[]
 for kind,climate in [('empty',{}),('null',{'resort-1':dict(air=[None]*12,water=[None]*12,wind=[None]*12,rain='')}),('numeric',{'resort-1':dict(air=[20]+[None]*11,water=[None]*12,wind=[None]*12,rain='')})]:
  c['climate']=climate;country.country(c);html=seen[-1][0][5];cover=seen[-1][1]['cover_override'];expected=kind=='numeric';assert ('id="season"'in html)==expected and ('href="#season"'in html)==expected and ('href="#season"'in cover)==expected;result.append(dict(data=kind,season=expected,nav=expected,hero=expected))
 c['climate']=old;ctx['emit']=emit;return result
report['climate_fixtures']=climate_fixtures()
for c in D['countries']:
 h=(S/'napravleniya'/c['slug']/'index.html').read_text();has=bool(c['climate']);assert ('id="season"'in h)==has
route=(S/'otdyh/svoj-marshrut/index.html').read_text();import re
assert all(v=='Города и ночи уточняются'for v in re.findall(r'<p class="rest-card-location"[^>]*>(.*?)</p>',route))
async def interactions(b,name):
 ctx=await b.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');p=await ctx.new_page();await p.goto(BASE+'napravleniya/egipet/index.html');await p.evaluate('document.fonts.ready');others=p.locator('[data-resort-card=sharm],[data-resort-card=gouna]');before=await others.evaluate_all('a=>a.map(e=>e.getBoundingClientRect().height)');await p.locator('[data-resort-card=hurghada] summary').click();after=await others.evaluate_all('a=>a.map(e=>e.getBoundingClientRect().height)');assert all(abs(a-b)<1 for a,b in zip(before,after)),(name,before,after)
 # Every actual grid containing details keeps neighbour heights, including other pages.
 await p.locator('[data-weather-resort]').select_option('gouna');await p.locator('[data-weather-month="3"]').click();assert 'метеостанции Хургады'in await p.locator('[data-weather-label]').inner_text();await p.locator('[data-resort-hotels=hurghada]').click();await p.locator('[data-country-hotel=hotel-1]').click();await p.keyboard.press('Escape');assert not await p.locator('#hotel-1-dialog').is_visible()
 await p.locator('[data-hotel-filter]').select_option('');await p.locator('[data-more-resorts]').click();x=await p.evaluate(EXTRA);assert not x['fail'],x['fail'];await p.locator('[data-hotel-filter]').select_option('marsa');x=await p.evaluate(EXTRA);assert not x['fail'],x['fail']
 for path in ['otdyh/otdyh-s-detmi/index.html','uslugi/index.html']:
  await p.goto(BASE+path);await p.evaluate('document.fonts.ready');result=await p.evaluate('''()=>{const result=[];for(const g of document.querySelectorAll('DETAILS_SELECTOR')){const details=[...g.children].filter(e=>e.matches('details')||e.querySelector('details'));if(details.length<2)continue;const a=details[0].matches('details')?details[0]:details[0].querySelector('details'),before=details.slice(1).map(e=>e.getBoundingClientRect().height);a.open=true;const after=details.slice(1).map(e=>e.getBoundingClientRect().height);a.open=false;result.push({grid:g.className,delta:after.map((n,i)=>n-before[i])});}return result;}'''.replace('DETAILS_SELECTOR',DETAILS_SELECTOR));assert all(all(abs(n)<1 for n in x['delta'])for x in result),result
 report['scenarios'].append(dict(engine=name,hurghada={'before':before,'after':after},climate_and_hotel='passed',visible_card_count='passed',details_grids='passed'));await ctx.close()
async def main():
 async with async_playwright()as pw:
  for name in ['chromium','firefox','webkit']:
   b=await launch(pw,name);report['engines'][name]={'version':b.version,'cases':0}
   for width in WIDTHS:
    ctx=await b.new_context(viewport={'width':width,'height':900},reduced_motion='reduce');p=await ctx.new_page();p.on('pageerror',lambda e:report['errors'].append(str(e)));p.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None)
    for row in PAGES:
     await p.goto(BASE+row['path']);
     if row['type']=='redirect':await p.wait_for_url('**/o-nas/index.html#team')
     await p.evaluate('document.fonts.ready');g=await p.evaluate(GENERAL);x=await p.evaluate(EXTRA);bad=list(x['fail'])
     if g['overflow']or g['clipped']or g['select']:bad.append({'kind':'general','overflow':g['overflow'],'clipped':g['clipped'],'select':g['select']})
     if g['header']and(abs(g['header']['center'])>2 or min(g['header']['leftGap'],g['header']['rightGap'])<32 or not g['header']['oneLine']):bad.append({'kind':'header',**g['header']})
     if bad:report['failures'].append(dict(engine=name,width=width,page=row['path'],failures=bad))
     if width in[1280,1920]:report['cards'].append(dict(engine=name,width=width,page=row['path'],grids=x['cards']))
     report['consent']['checked']+=x['consent'];report['consent']['same_row']+=x['same'];report['consent']['wrapped']+=x['wrapped'];report['prices']+=x['prices'];report['engines'][name]['cases']+=1
    await ctx.close();print(name,width,'complete;',len(report['failures']),'failures',flush=True)
   for width in [1024,1100,1200,1280,1366,1440,1920]:
    ctx=await b.new_context(viewport={'width':width,'height':900});p=await ctx.new_page();await p.goto(BASE+'index.html');await p.evaluate('document.fonts.ready');g=await p.evaluate(GENERAL);x=await p.evaluate(EXTRA);report['header'].append(dict(engine=name,width=width,**g['header'],**x['header']));assert not x['fail']and abs(g['header']['center'])<2 and min(g['header']['leftGap'],g['header']['rightGap'])>=32,(g,x);await ctx.close()
   await interactions(b,name)
   from cardinality9 import check as check_cardinality
   report.setdefault('cardinality',[]).extend(await check_cardinality(b,name,BASE));await b.close()
 report['status']='passed'if not report['errors']and not report['failures']else'failed';assert report['status']=='passed',(report['errors'],report['failures']);print('Stage 9 passed',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown();(S/'QA9.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
