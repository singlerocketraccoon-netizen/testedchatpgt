"""Reproducible stage-13 viewport matrix and visible-content acceptance."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from html.parser import HTMLParser
import asyncio,json,random,threading,sys,time,hashlib
from playwright.async_api import async_playwright
from engines7 import launch
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';PAGES=[p for p in json.loads((R/'tools/d1/pages.json').read_text())if p['type']!='redirect'];SEED=20261114
FIXED=[320,360,375,390,412,430,480,540,600,667,720,768,800,834,900,960,1024,1080,1100,1180,1200,1280,1366,1440,1536,1600,1680,1800,1920,2048,2560,3440];RANDOM=random.Random(SEED).sample([w for w in range(320,2561)if w not in FIXED],12)
SPECIAL=[(320,568),(360,640),(375,667),(667,375),(844,390),(932,430),(1024,600),(1280,600),(1280,720),(1366,768),(1440,700),(1536,864),(1920,800),(768,1024),(820,1180),(1024,1366),(1180,820),(3440,1440)];OTHER=[(390,844),(844,390),(768,1024),(1440,900)]
JS=r'''()=>{
 const fail=[],r=e=>e.getBoundingClientRect(),shown=e=>{if(!e||!e.getClientRects().length||e.closest('[hidden],[inert],dialog:not([open]),[aria-hidden=true],.sr-only,svg,script,style'))return false;for(let n=e;n;n=n.parentElement){const s=getComputedStyle(n);if(s.visibility==='hidden'||s.display==='none'||Number(s.opacity)===0)return false;if(n.tagName==='DETAILS'&&!n.open&&!n.querySelector(':scope>summary')?.contains(e))return false;}return true;};
 const clipped=(e,box)=>{for(let n=e.parentElement;n&&n!==document.body;n=n.parentElement){const s=getComputedStyle(n),b=r(n);if(['auto','scroll'].includes(s.overflowX)&&n.scrollWidth>n.clientWidth+1)return false;if(['hidden','clip'].includes(s.overflowX)&&(box.left<b.left-2||box.right>b.right+2))return true;if(['hidden','clip'].includes(s.overflowY)&&(box.top<b.top-2||box.bottom>b.bottom+2))return true;}return false;};
 if(document.documentElement.scrollWidth>innerWidth)fail.push({kind:'page-overflow',px:document.documentElement.scrollWidth-innerWidth});
 let textRects=0,targets=0;const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;
 while(node=walker.nextNode()){const e=node.parentElement;if(!node.textContent.trim()||!shown(e)||e.closest('option,select,textarea'))continue;const style=getComputedStyle(e);if(parseFloat(style.fontSize)<12-.05)fail.push({kind:'small-font',size:style.fontSize,text:node.textContent.trim().slice(0,60)});const range=document.createRange();range.selectNodeContents(node);for(const box of range.getClientRects()){if(box.width<.5||box.height<.5)continue;textRects++;if(clipped(e,box))fail.push({kind:'clipped-text',text:node.textContent.trim().slice(0,70),class:e.className});let rail=false;for(let n=e.parentElement;n&&n!==document.body;n=n.parentElement){const c=getComputedStyle(n);if(['auto','scroll'].includes(c.overflowX)&&n.scrollWidth>n.clientWidth+1){rail=true;break;}}if(!rail&&(box.left<-1||box.right>innerWidth+1))fail.push({kind:'text-outside',text:node.textContent.trim().slice(0,70),left:box.left,right:box.right});}}
 for(const e of document.querySelectorAll('button,a[href],summary,input:not([type=hidden]),select,textarea')){if(!shown(e))continue;let target=e;if(e.matches('input[type=checkbox],input[type=radio]'))target=e.closest('label')||e;const box=r(target);targets++;if(innerWidth<=1024&&(box.width<43||box.height<43))fail.push({kind:'small-target',tag:e.tagName,text:e.textContent.trim().slice(0,40)||e.name,width:box.width,height:box.height});if(e.matches('button,input,select,textarea')&&(e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2))fail.push({kind:'clipped-control',text:e.textContent.slice(0,50)||e.name,class:e.className});}
 for(const form of document.querySelectorAll('[data-unified-form]')){const controls=[...form.querySelectorAll('button,input:not([type=hidden]),select,textarea,a')].filter(shown);for(let i=0;i<controls.length;i++)for(let j=i+1;j<controls.length;j++){if(controls[i].contains(controls[j])||controls[j].contains(controls[i]))continue;const a=r(controls[i]),b=r(controls[j]);if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)fail.push({kind:'form-control-overlap',a:controls[i].textContent.slice(0,35)||controls[i].name,b:controls[j].textContent.slice(0,35)||controls[j].name});}}
 for(const control of document.querySelectorAll('button,a[href]')){
  if(!shown(control)||control.querySelector('img,.place-cover'))continue;const b=r(control),w=document.createTreeWalker(control,NodeFilter.SHOW_TEXT);let n;
  while(n=w.nextNode()){if(!n.textContent.trim()||!shown(n.parentElement)||n.parentElement.closest('svg,.sr-only'))continue;const range=document.createRange();range.selectNodeContents(n);for(const line of range.getClientRects())if(line.width>.5&&line.height>.5&&(line.left<b.left-1||line.right>b.right+1||line.top<b.top-1||line.bottom>b.bottom+1))fail.push({kind:'text-outside-control',text:n.textContent.trim().slice(0,60),class:control.className});}
 }
 const header=document.querySelector('.d1-header'),head=header?r(header):null;if(innerWidth>=1024&&header){const nodes=[...header.querySelectorAll('.nav-left>a,.nav-left>div,.nav-about>a,.nav-about>div,.header-contacts>.icon-control')].filter(shown),boxes=nodes.map(r),ys=boxes.map(b=>b.y+b.height/2);if(Math.max(...ys)-Math.min(...ys)>1)fail.push({kind:'header-row',centers:ys});const logo=r(header.querySelector('.brand'));for(let i=0;i<boxes.length;i++){const a=boxes[i];if(a.left<logo.right-1&&a.right>logo.left+1)fail.push({kind:'header-logo-overlap',label:nodes[i].textContent});if(a.left<-1||a.right>innerWidth+1)fail.push({kind:'header-outside'});for(let j=i+1;j<boxes.length;j++)if(a.left<boxes[j].right-1&&a.right>boxes[j].left+1)fail.push({kind:'header-items-overlap',a:nodes[i].textContent,b:nodes[j].textContent});}}
 const cover=document.querySelector('[data-inner-cover]'),hero=cover?.querySelector('.hero-slide.is-active'),h=hero?.querySelector('h1,h2')||cover?.querySelector('h1');const actions=[...(hero||cover||document).querySelectorAll('[data-hero-cta],[data-messenger],button[data-open-form],a[href="#cost"],a.btn')].filter(shown),action=actions[0];if(h){const b=r(h);if(b.top<(head?.bottom||0)-1||b.bottom>innerHeight+1)fail.push({kind:'h1-outside-first-screen',top:b.top,bottom:b.bottom,viewport:innerHeight});}if(action){const b=r(action);if(b.top<(head?.bottom||0)-1||b.bottom>innerHeight+1)fail.push({kind:'cta-outside-first-screen',text:action.textContent.trim(),top:b.top,bottom:b.bottom,viewport:innerHeight});}
 if(hero){const ctrl=r(cover.querySelector('.hero-controls')),copy=r(hero.querySelector('.hero-copy')),button=r(hero.querySelector('[data-hero-cta]'));if(button.bottom>ctrl.top+1)fail.push({kind:'hero-controls-overlap',button:button.bottom,controls:ctrl.top});}
 if(cover&&innerWidth===1366&&innerHeight===768||cover&&innerWidth===1536&&innerHeight===864){if(!hero&&r(cover).bottom>innerHeight*.82+1)fail.push({kind:'interior-cover-height',bottom:r(cover).bottom,max:innerHeight*.82});}
 const footer=document.querySelector('footer');if(footer){const height=r(footer).height,limit=innerWidth>=1024?380:innerWidth>=768?520:760;if(height>limit+1)fail.push({kind:'footer-height',height,limit});}
 for(const card of document.querySelectorAll('.messenger-card'))if(shown(card)&&innerWidth>=1024&&!card.querySelector('details[open]')&&r(card).height>521)fail.push({kind:'form-height',height:r(card).height});
 for(const card of document.querySelectorAll('.document-row'))if(shown(card)&&r(card).height>89)fail.push({kind:'document-row-height',height:r(card).height});


 for(const e of document.querySelectorAll('a,button,span,[role=tab]')){
  if(!shown(e)||!e.textContent.trim()||e.closest('svg,.sr-only'))continue;
  const s=getComputedStyle(e),box=r(e),radius=s.borderTopLeftRadius.endsWith('%')?parseFloat(s.borderTopLeftRadius)*Math.min(box.width,box.height)/100:parseFloat(s.borderTopLeftRadius);
  const tagged=/(?:^|[\s_-])(chip|chips|tab|tabs|pill)(?:[\s_-]|$)/i.test(e.className)||e.matches('[role=tab],.section-tabs>a,.filter-chips>button,.country-months>button');
  const pill=radius>=box.height/2-.5&&radius>0&&box.width>box.height*1.1;
  if((tagged||pill)&&box.height>0){
   if(parseFloat(s.paddingLeft)<11.99||parseFloat(s.paddingRight)<11.99)fail.push({kind:'pill-padding',class:e.className,text:e.textContent.trim().slice(0,60),left:s.paddingLeft,right:s.paddingRight,height:box.height});
   if(box.height<43.99)fail.push({kind:'pill-height',class:e.className,text:e.textContent.trim().slice(0,60),height:box.height});
  }
 }

 const cardSelector='.photo-credit-row,.messenger-card,.rest-age-item,.rest-check-item,.work-card-grid>a.step,.country-card-panel,.rest-selection-card,.rest-destination-card,.rest-format-card,.info-card,.service-extra-card,.service-travel-card,.ticket-link-cover,.mood-choice,.person-card,.document-row,.work-summary,.review-card,.country-index-card,.team-card';
 for(const card of document.querySelectorAll(cardSelector)){
  if(!shown(card))continue;const bounds=r(card),lines=[],walk=document.createTreeWalker(card,NodeFilter.SHOW_TEXT);let n;
  while(n=walk.nextNode()){
   const e=n.parentElement;if(!n.textContent.trim()||!shown(e)||e.closest(cardSelector)!==card||e.closest('svg,option,select,textarea,.sr-only'))continue;
   const range=document.createRange(),start=n.textContent.search(/\S/),end=n.textContent.search(/\s*$/);range.setStart(n,start);range.setEnd(n,end);
   for(const b of range.getClientRects()){
    if(b.width<.5||b.height<.5)continue;
    if(b.left<bounds.left-1||b.right>bounds.right+1||b.top<bounds.top-1||b.bottom>bounds.bottom+1)fail.push({kind:'text-outside-card',card:card.className,text:n.textContent.trim().slice(0,60),box:{left:b.left,right:b.right,top:b.top,bottom:b.bottom},bounds:{left:bounds.left,right:bounds.right,top:bounds.top,bottom:bounds.bottom}});
    const button=e.closest('a,button');if(button&&button!==card&&card.contains(button)){const bb=r(button);if(b.left<bb.left-1||b.right>bb.right+1||b.top<bb.top-1||b.bottom>bb.bottom+1)fail.push({kind:'text-outside-action',text:n.textContent.trim().slice(0,60)});}
    for(const previous of lines)if(previous.e!==e&&Math.min(b.right,previous.b.right)-Math.max(b.left,previous.b.left)>.5&&Math.min(b.bottom,previous.b.bottom)-Math.max(b.top,previous.b.top)>.5)fail.push({kind:'text-lines-overlap',card:card.className,a:previous.text,b:n.textContent.trim().slice(0,60)});
    lines.push({e,b,text:n.textContent.trim().slice(0,60)});
   }
  }
 }
 const compactPages=['o-nas/index.html','o-nas/otzyvy/index.html','o-nas/kontakty/index.html','o-nas/dokumenty/index.html','o-nas/dokumenty/rekvizity/index.html','napravleniya/index.html','predlozheniya/index.html','zagranpasport/index.html'];
 if(compactPages.includes(document.body.dataset.page)&&[390,1440].includes(innerWidth)){
  const cover=document.querySelector('[data-inner-cover]'),tabs=document.querySelector('.section-tabs'),start=document.querySelector('[data-content-start]');
  const headerContent=tabs||cover?.querySelector('.page-heading-grid')||cover?.querySelector('.container');
  const content=start?.querySelector('.container')?.firstElementChild;
  if(!headerContent||!content)fail.push({kind:'missing-content-boundary'});
  if(headerContent&&content){const headerBottom=tabs?Math.max(...[...tabs.querySelectorAll('a')].filter(shown).map(a=>r(a).bottom)):r(headerContent).bottom,gap=r(content).top-headerBottom,limit=innerWidth===1440?40:32;if(gap>limit+1)fail.push({kind:'page-content-gap',gap,limit});}
 }
 const walkRules=rules=>{for(const rule of rules){if(rule.cssRules)walkRules(rule.cssRules);if(!rule.selectorText||!rule.style)continue;if((/(^|[\s,>+~])\*(?=[\s,.:>+~]|$)/.test(rule.selectorText)||/\bmain\s+a\b/.test(rule.selectorText))&&['display','min-width','min-height'].some(p=>rule.style.getPropertyValue(p)))fail.push({kind:'forbidden-global-css',selector:rule.selectorText});}};
 for(const sheet of document.styleSheets)walkRules(sheet.cssRules);

 return{fail,textRects,targets};
}'''
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(R/'docs'),**kw)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start();BASE='http://127.0.0.1:'+str(server.server_port)+'/scheme2/d1/'
report={'stage':'13.2','seed':SEED,'random_widths':RANDOM,'fixed_widths':FIXED,'special':SPECIAL,'engines':{},'cases':0,'text_rects':0,'targets':0,'failures':[],'errors':[],'resources':[]}
def check_css_scope():
 import re
 for path in (S/'css').glob('*.css'):
  text=re.sub(r'/\*.*?\*/','',path.read_text(),flags=re.S)
  for selector,decl in re.findall(r'([^{}]+)\{([^{}]*)\}',text):
   if re.search(r'(^|[\s,>+~])\*(?=[\s,.:>+~]|$)|\bmain\s+a\b',selector) and re.search(r'(?:^|;)\s*(?:display|min-width|min-height)\s*:',decl):
    raise AssertionError(('Forbidden global sizing/display rule',str(path),selector))
 report['css_scope']='passed'
async def main():
 check_css_scope()
 quick='--quick'in sys.argv
 global PAGES
 if '--page'in sys.argv:PAGES=[p for p in PAGES if p['path']==sys.argv[sys.argv.index('--page')+1]]
 async with async_playwright()as pw:
  for engine in(['chromium']if quick else['chromium','firefox','webkit']):
   browser=await launch(pw,engine);matrix=[(w,900)for w in FIXED+RANDOM]+SPECIAL if engine=='chromium'else OTHER
   if quick:matrix=[(320,568),(390,844),(844,390),(1024,600),(1366,768),(1440,900)]
   report['engines'][engine]={'version':browser.version,'matrix':matrix,'cases':0}
   for w,h in matrix:
    ctx=await browser.new_context(viewport={'width':w,'height':h},reduced_motion='reduce');page=await ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('console',lambda m:report['errors'].append(m.text)if m.type=='error'else None);page.on('response',lambda r:report['resources'].append([r.status,r.url])if r.status>=400 else None)
    for p in PAGES:
     await page.goto(BASE+p['path']);await page.evaluate('''async()=>{await document.fonts.ready;window.MangoLayout?.refresh();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}''');x=await page.evaluate(JS);report['cases']+=1;report['engines'][engine]['cases']+=1;report['text_rects']+=x['textRects'];report['targets']+=x['targets']
     if x['fail']:report['failures'].append(dict(engine=engine,width=w,height=h,page=p['path'],failures=x['fail']))
     if p['path']=='index.html':
      for i in range(3):
       await page.locator('[data-hero-next]').click();x=await page.evaluate(JS)
       if x['fail']:report['failures'].append(dict(engine=engine,width=w,height=h,page=p['path'],slide=i+2,failures=x['fail']))
    await ctx.close();print(engine,w,h,'cases',report['cases'],'violations',sum(len(f['failures'])for f in report['failures']),flush=True);(S/('RESPONSIVE13_2_PATCH.json'if '--page'in sys.argv else'RESPONSIVE13_2_QUICK.json'if quick else'RESPONSIVE13_2.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
   await browser.close()
 report['status']='passed'if not report['failures']and not report['errors']and not report['resources']else'failed';report['violations']=sum(len(f['failures'])for f in report['failures'])+len(report['errors'])+len(report['resources']);assert report['status']=='passed',(report['violations'],len(report['errors']));print('0 нарушений',flush=True)
if __name__=='__main__':
 try:asyncio.run(main())
 finally:server.shutdown();(S/('RESPONSIVE13_2_PATCH.json'if '--page'in sys.argv else'RESPONSIVE13_2_QUICK.json'if'--quick'in sys.argv else'RESPONSIVE13_2.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
