/* Per-row card dimensions. Content remains static HTML; open details never resize neighbours. */
(() => {
 'use strict';
 const main=document.querySelector('main');if(!main)return;
 const selectors='.rest-grid,.tickets-grid,.country-index-grid,.country-grid,.country-alternatives,.country-experiences,.country-hotel-tips,.rest-format-grid,.rest-destination-grid,.rest-selection-grid,.people-grid,.stage4-review-grid,.document-grid';
 const $$=(s,r=document)=>[...r.querySelectorAll(s)],shown=e=>e.getClientRects().length&&!e.closest('[hidden],dialog:not([open]),[inert]');
 const mediaSelector=':scope>.place-cover,:scope>a>.place-cover,:scope>details>summary>.place-cover,:scope>.country-hotel-open>.place-cover,:scope>.rest-photo,:scope>img,:scope>.rest-photo-placeholder,:scope>.country-photo-placeholder,:scope>.rest-card-photo,:scope>.ticket-link-cover>img,:scope>a>img,:scope>a>.country-photo-placeholder,:scope>details>summary>img,:scope>details>summary>.country-photo-placeholder,:scope>.country-hotel-open>img,:scope>.country-hotel-open>.country-photo-placeholder';
 const titleSelector='h2,h3,.rest-label,.country-resort summary>span,.country-hotel-open>span';
 const accordionMedia=matchMedia('(min-width:1024px)');
 const accordions=$$('[data-independent-accordion]').map(root=>({root,items:[...root.children].filter(e=>e.tagName==='DETAILS'),columns:$$(':scope>[data-accordion-column]',root)}));
 function arrangeAccordions(){
  const focused=document.activeElement;
  for(const {root,items,columns}of accordions){
   if(accordionMedia.matches){items.forEach((item,i)=>columns[i%2].append(item));columns.forEach(c=>c.hidden=false);root.classList.add('has-independent-columns');}
   else{items.forEach(item=>root.insertBefore(item,columns[0]));columns.forEach(c=>c.hidden=true);root.classList.remove('has-independent-columns');}
  }
  if(focused&&accordions.some(({root})=>root.contains(focused)))focused.focus({preventScroll:true});
 }
 arrangeAccordions();accordionMedia.addEventListener('change',arrangeAccordions);
 let pending=false,running=false,lastWidth=0;
 function equalize(){
  if(running)return;running=true;pending=false;
  const grids=$$(selectors).filter(shown),opened=[];
  for(const g of grids)for(const card of [...g.children].filter(shown)){
   card.classList.add('equal-card');card.classList.remove('is-orphan-card');card.style.removeProperty('--equal-height');
   $$('.equal-prefix',card).forEach(t=>{t.style.removeProperty('min-height');t.classList.remove('equal-prefix');});
   $$('.equal-title',card).forEach(t=>{t.style.removeProperty('min-height');t.classList.remove('equal-title');});
   $$('.equal-media',card).forEach(m=>{m.style.removeProperty('height');m.classList.remove('equal-media');});
   $$('details[open]',card).forEach(d=>{opened.push(d);d.open=false;});
  }
  for(const g of grids){
   const cards=[...g.children].filter(shown);g.classList.toggle('card-grid-seven',cards.length===7);
   if(cards.length<3||getComputedStyle(g).display!=='grid')continue;
   const y=cards[0].getBoundingClientRect().top,columns=cards.filter(c=>Math.abs(c.getBoundingClientRect().top-y)<2).length;
   if(columns>1&&cards.length%columns===1)cards.at(-1).classList.add('is-orphan-card');
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
