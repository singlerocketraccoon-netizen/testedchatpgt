/* Holiday selection only. Shared forms, dialogs and messenger handling stay in main.js. */
(() => {
 'use strict';
 const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>Array.from(r.querySelectorAll(s));
 const tabs=$$('[data-rest-tab]'),panels=$$('[data-rest-panel]'),config=JSON.parse($('#app-config').textContent),prefix=config.topic;
 const reduce=matchMedia('(prefers-reduced-motion: reduce)');let frame,restoring=true,serial=0;history.scrollRestoration='manual';
 function save(state,url){try{history.replaceState(state,'',url);}catch(error){if(location.protocol!=='file:')throw error;}}
 function activate(country,write=true){
  if(!tabs.some(t=>t.dataset.restTab===country))return;
  tabs.forEach(t=>{const on=t.dataset.restTab===country;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;});panels.forEach(p=>p.hidden=p.dataset.restPanel!==country);
  $('[data-rest-current-topic]').dataset.openForm=prefix+':country:'+country;
  if(write){const u=new URL(location.href);u.searchParams.set('country',country);save(history.state,u);}
 }
 function snapshot(){if(restoring)return;const state={...(history.state||{}),d1Rest:{open:$$('main details[id][open]').map(d=>d.id),y:scrollY}};save(state,location.href);}
 async function restore(){
  const pass=++serial;restoring=true;
  if(tabs.length)activate(new URLSearchParams(location.search).get('country')||tabs[0].dataset.restTab,false);
  const state=history.state?.d1Rest;
  if(state)$$('main details[id]').forEach(d=>d.open=state.open.includes(d.id));
  await document.fonts.ready;
  requestAnimationFrame(()=>requestAnimationFrame(()=>{if(pass!==serial)return;if(state)scrollTo(0,state.y);requestAnimationFrame(()=>{restoring=false;snapshot();});}));
 }

 $$('main details').forEach((d,i)=>{if(!d.id)d.id='rest-detail-row-'+i;d.addEventListener('toggle',snapshot);});
 tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>activate(tab.dataset.restTab));tab.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const n=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;activate(tabs[n].dataset.restTab);tabs[n].focus();});});
 document.addEventListener('click',e=>{
  const country=e.target.closest('[data-rest-country]');if(country){e.preventDefault();activate(country.dataset.restCountry);document.querySelector(country.getAttribute('href')).scrollIntoView({behavior:reduce.matches?'auto':'smooth',block:'start'});}
  const detail=e.target.closest('[data-rest-detail]');if(detail){e.preventDefault();window.MangoUI.open(document.getElementById('rest-detail-'+detail.dataset.restDetail),detail);}
 });
 addEventListener('scroll',()=>{if(frame)return;frame=requestAnimationFrame(()=>{frame=null;snapshot();});},{passive:true});addEventListener('pagehide',snapshot);addEventListener('pageshow',restore);addEventListener('popstate',restore);restore();
})();
