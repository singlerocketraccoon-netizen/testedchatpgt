/* Per-row card dimensions. Content remains static HTML; open details never resize neighbours. */
(() => {
 'use strict';
 const main=document.querySelector('main');if(!main)return;
 const selectors='.rest-grid,.tickets-grid,.country-index-grid,.country-grid,.country-alternatives,.country-experiences,.country-hotel-tips,.rest-format-grid,.rest-destination-grid,.rest-selection-grid,.people-grid,.stage4-review-grid,.document-grid';
 const $$=(s,r=document)=>[...r.querySelectorAll(s)],shown=e=>e.getClientRects().length&&!e.closest('[hidden],dialog:not([open]),[inert]');
 const mediaSelector=':scope>.rest-photo,:scope>img,:scope>.rest-photo-placeholder,:scope>.country-photo-placeholder,:scope>.rest-card-photo,:scope>.ticket-link-cover>img,:scope>a>img,:scope>a>.country-photo-placeholder,:scope>details>summary>img,:scope>details>summary>.country-photo-placeholder,:scope>.country-hotel-open>img,:scope>.country-hotel-open>.country-photo-placeholder';
 const titleSelector='h2,h3,.rest-label,.country-resort summary>span,.country-hotel-open>span';
 let pending=false,running=false,lastWidth=0;
 function equalize(){
  if(running)return;running=true;pending=false;
  const grids=$$(selectors).filter(shown),opened=[];
  for(const g of grids)for(const card of [...g.children].filter(shown)){
   card.classList.add('equal-card');card.style.removeProperty('--equal-height');
   $$('.equal-prefix',card).forEach(t=>{t.style.removeProperty('min-height');t.classList.remove('equal-prefix');});
   $$('.equal-title',card).forEach(t=>{t.style.removeProperty('min-height');t.classList.remove('equal-title');});
   $$('.equal-media',card).forEach(m=>{m.style.removeProperty('height');m.classList.remove('equal-media');});
   $$('details[open]',card).forEach(d=>{opened.push(d);d.open=false;});
  }
  for(const g of grids){
   const rows=[];
   for(const card of [...g.children].filter(shown)){const y=card.getBoundingClientRect().top;let row=rows.find(row=>Math.abs(row.y-y)<2);if(!row){row={y,cards:[]};rows.push(row);}row.cards.push(card);}
   for(const row of rows){
    const medias=row.cards.map(c=>c.querySelector(mediaSelector)).filter(Boolean),mh=Math.max(0,...medias.map(m=>m.getBoundingClientRect().height));
    medias.forEach(m=>{m.style.height=mh+'px';m.classList.add('equal-media');});
    const prefixes=row.cards.map(c=>c.querySelector('.ticket-dates')).filter(Boolean),ph=Math.max(0,...prefixes.map(t=>t.getBoundingClientRect().height));prefixes.forEach(t=>{t.classList.add('equal-prefix');t.style.minHeight=ph+'px';});
    const titles=row.cards.map(c=>c.querySelector(titleSelector)).filter(Boolean),th=Math.max(0,...titles.map(t=>t.getBoundingClientRect().height));
    titles.forEach(t=>{t.classList.add('equal-title');t.style.minHeight=th+'px';});
    const h=Math.max(...row.cards.map(c=>c.getBoundingClientRect().height));row.cards.forEach(c=>c.style.setProperty('--equal-height',h+'px'));
   }
  }
  opened.forEach(d=>d.open=true);lastWidth=innerWidth;running=false;document.dispatchEvent(new CustomEvent('mango:layoutready'));
 }
 function schedule(){if(pending||running)return;pending=true;requestAnimationFrame(equalize);}
 document.fonts.ready.then(schedule);addEventListener('resize',()=>{if(innerWidth!==lastWidth)schedule();});addEventListener('load',schedule);
 new MutationObserver(records=>{if(records.some(r=>r.type==='attributes'&&r.attributeName==='hidden'||r.type==='childList'&&r.addedNodes.length))schedule();}).observe(main,{subtree:true,childList:true,attributes:true,attributeFilter:['hidden']});
 window.MangoLayout={refresh:equalize,ready:()=>!pending&&!running};
})();
