(() => {
 'use strict';
 const motion=matchMedia('(prefers-reduced-motion: reduce)');
 document.querySelectorAll('[data-offer-carousel]').forEach(section=>{
  const rail=section.querySelector('.offer-grid'),prev=section.querySelector('[data-offers-prev]'),next=section.querySelector('[data-offers-next]');
  const sync=()=>{prev.disabled=rail.scrollLeft<2;next.disabled=rail.scrollLeft>=rail.scrollWidth-rail.clientWidth-2;};
  const move=n=>{const card=rail.querySelector('.offer-card');if(card)rail.scrollBy({left:n*(card.getBoundingClientRect().width+parseFloat(getComputedStyle(rail).gap)),behavior:motion.matches?'instant':'smooth'});};
  prev.addEventListener('click',()=>move(-1));next.addEventListener('click',()=>move(1));rail.addEventListener('scroll',sync,{passive:true});addEventListener('resize',sync);
  rail.addEventListener('keydown',e=>{if(e.target!==rail)return;if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();move(e.key==='ArrowRight'?1:-1);}else if(e.key==='Home'||e.key==='End'){e.preventDefault();rail.scrollTo({left:e.key==='Home'?0:rail.scrollWidth,behavior:motion.matches?'instant':'smooth'});}});sync();
 });
 const list=document.querySelector('[data-offers-list]');if(!list)return;
 const cards=[...list.querySelectorAll('.offer-card')],filters=[...document.querySelectorAll('[data-offer-filter]')],sort=document.querySelector('[data-offer-sort]'),status=document.querySelector('[data-offer-status]');let country='all';
 function update(){
  [...cards].sort((a,b)=>sort.value==='price'?Number(a.dataset.price)-Number(b.dataset.price):a.dataset.date.localeCompare(b.dataset.date)).forEach(card=>list.append(card));
  cards.forEach(card=>card.hidden=country!=='all'&&card.dataset.country!==country);
  if(status)status.textContent='Показано: '+cards.filter(c=>!c.hidden).length;
 }
 filters.forEach(button=>button.addEventListener('click',()=>{country=button.dataset.offerFilter;filters.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));update();}));sort.addEventListener('change',update);update();
})();
