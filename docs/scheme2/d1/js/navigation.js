(() => {
  'use strict';
  const header = document.querySelector('[data-site-header]');
  if (!header) return;
  const menu = header.querySelector('#mobile-nav'), burger = header.querySelector('[data-menu]');
  const groups = [...header.querySelectorAll('.nav-dropdown')];
  const desktop = matchMedia('(min-width: 1024px)');
  let active = null, pinned = null, closing, opening;
  const fading=new WeakMap(),motion=matchMedia('(prefers-reduced-motion:reduce)');
  const sync = () => {
    header.classList.toggle('is-menu-open', !!active || !!header.querySelector('.dropdown-panel:not([hidden])') || !menu.hidden);
    document.documentElement.classList.toggle('is-nav-open', !menu.hidden);
    document.dispatchEvent(new Event('d1:navstate'));
  };
  function positionDropdown(group) {
    const panel=group.querySelector('.dropdown-panel'), h=header.getBoundingClientRect(), g=group.getBoundingClientRect(), width=panel.getBoundingClientRect().width;
    const desired=group.classList.contains('menu-about')?g.right-width:g.left;
    const left=Math.max(16,Math.min(desired,innerWidth-16-width));
    header.style.setProperty('--dropdown-header-height',h.height+'px');
    group.style.setProperty('--dropdown-top',(h.bottom-g.top+10)+'px');
    group.style.setProperty('--dropdown-shift',(left-g.left)+'px');
    group.style.setProperty('--dropdown-width',width+'px');
  }
  function closeDropdown(restore = false,immediate=false) {
    clearTimeout(closing);clearTimeout(opening);
    if(active){const group=active,b=group.querySelector('[data-nav-toggle]'),panel=group.querySelector('.dropdown-panel');b.setAttribute('aria-expanded','false');panel.classList.remove('is-visible');panel.inert=true;panel.setAttribute('aria-hidden','true');clearTimeout(fading.get(panel));const hide=()=>{panel.hidden=true;sync();};if(immediate||motion.matches)hide();else fading.set(panel,setTimeout(hide,150));if(restore)b.focus();}
    active=null;pinned=null;sync();
  }
  function openDropdown(group){
    if(!desktop.matches)return;clearTimeout(opening);clearTimeout(closing);if(active!==group)closeDropdown(false,true);active=group;
    const panel=group.querySelector('.dropdown-panel');clearTimeout(fading.get(panel));panel.hidden=false;panel.inert=false;panel.setAttribute('aria-hidden','false');group.querySelector('[data-nav-toggle]').setAttribute('aria-expanded','true');sync();positionDropdown(group);panel.getBoundingClientRect();panel.classList.add('is-visible');
  }
  function closeMobile(restore = false) {
    menu.hidden = true; burger.setAttribute('aria-expanded', 'false'); burger.setAttribute('aria-label', 'Открыть меню'); burger.querySelector('use').setAttribute('href', '#i-menu');
    menu.querySelectorAll('details').forEach(d => d.open = false); sync(); if (restore) burger.focus();
  }
  function close(restore = false) { closeDropdown(restore); closeMobile(restore); }
  window.D1Nav = {close};
  groups.forEach(group => {
    const button = group.querySelector('[data-nav-toggle]'); button.disabled = false;
    button.addEventListener('click', () => { if (active === group && pinned === group) closeDropdown(); else { openDropdown(group); pinned = group; } });
    button.addEventListener('keydown', e => { if (e.key === 'ArrowDown') { e.preventDefault(); openDropdown(group); group.querySelector('.dropdown-panel a').focus(); } });
    group.addEventListener('pointerenter',e=>{if(e.pointerType==='touch')return;clearTimeout(closing);clearTimeout(opening);if(active!==group)opening=setTimeout(()=>openDropdown(group),100);});
    group.addEventListener('pointerleave', e => {
      if(e.pointerType==='touch')return;
      clearTimeout(opening);clearTimeout(closing);
      closing = setTimeout(() => { if (active === group && !group.contains(document.activeElement) && pinned !== group) closeDropdown(); }, 200);
    });
    group.addEventListener('focusout', e => { if (!group.contains(e.relatedTarget)) closeDropdown(); });
  });
  burger.disabled = false;
  burger.addEventListener('click', () => {
    if (!menu.hidden) return closeMobile(true);
    closeDropdown(); menu.hidden = false; burger.setAttribute('aria-expanded', 'true'); burger.setAttribute('aria-label', 'Закрыть меню'); burger.querySelector('use').setAttribute('href', '#i-close'); sync();
    menu.querySelector('summary,a')?.focus();
  });
  menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => closeMobile()));
  document.addEventListener('keydown', e => {
    if (e.key !== 'Tab' || menu.hidden) return;
    const items = [...header.querySelectorAll('a,button,summary')].filter(n => n.getClientRects().length && !n.disabled);
    if (e.shiftKey && document.activeElement === items[0]) { e.preventDefault(); items.at(-1).focus(); }
    else if (!e.shiftKey && document.activeElement === items.at(-1)) { e.preventDefault(); items[0].focus(); }
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { if (!menu.hidden) closeMobile(true); else closeDropdown(true); } });
  document.addEventListener('click', e => { if (active && !header.contains(e.target)) closeDropdown(); });
  desktop.addEventListener('change', () => close());
  const update = () => { header.classList.toggle('is-compact', scrollY > 80); if(active)positionDropdown(active); };
  addEventListener('resize',()=>{if(active)positionDropdown(active);});
  if(window.ResizeObserver)new ResizeObserver(()=>{if(active)positionDropdown(active);}).observe(header);
  addEventListener('scroll', update, {passive:true}); update();
 let ratingTimer;
 document.addEventListener('click', e => {
  const link=e.target.closest('[data-review-platform]');
  if(!link || link.getAttribute('href')!=='#')return;
  e.preventDefault();const toast=document.querySelector('.toast');
  if(toast){toast.hidden=false;clearTimeout(ratingTimer);ratingTimer=setTimeout(()=>toast.hidden=true,6500);}
 });
})();
