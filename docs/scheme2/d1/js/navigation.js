(() => {
  'use strict';
  const header = document.querySelector('[data-site-header]');
  if (!header) return;
  const menu = header.querySelector('#mobile-nav'), burger = header.querySelector('[data-menu]');
  const groups = [...header.querySelectorAll('.nav-dropdown')];
  const desktop = matchMedia('(min-width: 1024px)');
  let active = null, pinned = null, closing;
  const sync = () => {
    header.classList.toggle('is-menu-open', !!active || !menu.hidden);
    document.documentElement.classList.toggle('is-nav-open', !menu.hidden);
    document.dispatchEvent(new Event('d1:navstate'));
  };
  function closeDropdown(restore = false) {
    if (active) { const b = active.querySelector('[data-nav-toggle]'); b.setAttribute('aria-expanded', 'false'); active.querySelector('.dropdown-panel').hidden = true; if (restore) b.focus(); }
    active = null; pinned = null; sync();
  }
  function openDropdown(group) {
    if (!desktop.matches) return;
    clearTimeout(closing); if (active !== group) closeDropdown(); active = group;
    group.querySelector('[data-nav-toggle]').setAttribute('aria-expanded', 'true'); group.querySelector('.dropdown-panel').hidden = false; sync();
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
    group.addEventListener('pointerenter', e => { if (e.pointerType !== 'touch') openDropdown(group); });
    group.addEventListener('pointerleave', () => { closing = setTimeout(() => { if (!group.contains(document.activeElement) && pinned !== group) closeDropdown(); }, 180); });
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
  const update = () => header.classList.toggle('is-compact', scrollY > 80);
  addEventListener('scroll', update, {passive:true}); update();
})();
