/* Measured offsets and stage state; all content remains in HTML. */
(() => {
  'use strict';
  const header = document.querySelector('[data-site-header]');
  if (!header) return;
  const links = [...document.querySelectorAll('[data-work-stage-link]')];
  const sections = [...document.querySelectorAll('[data-work-stage]')];
  const stepper = document.querySelector('.work-stepper');
  let pending = false;
  const highlight = () => {
    pending = false;
    const edge = header.getBoundingClientRect().height + (stepper?.getBoundingClientRect().height || 0) + 24;
    const active = sections.filter(section => section.getBoundingClientRect().top <= edge).pop() || sections[0];
    links.forEach(link => link.dataset.workStageLink === active?.id
      ? link.setAttribute('aria-current', 'step') : link.removeAttribute('aria-current'));
  };
  const schedule = () => {
    if (!pending) { pending = true; requestAnimationFrame(highlight); }
  };
  const sync = () => {
    document.documentElement.style.setProperty('--measured-header', header.getBoundingClientRect().height + 'px');
    schedule();
  };
  sync();
  new ResizeObserver(sync).observe(header);
  if (sections.length) {
    new IntersectionObserver(schedule, {rootMargin: '-20% 0px -55% 0px'}).observe(sections[0]);
    addEventListener('scroll', schedule, {passive: true});
    addEventListener('resize', schedule);
    document.fonts.ready.then(schedule);
  }
  links.forEach(link => link.addEventListener('click', event => {
    const section = document.getElementById(link.dataset.workStageLink);
    if (!section) return;
    event.preventDefault();
    scrollTo({
      top: scrollY + section.getBoundingClientRect().top - header.getBoundingClientRect().height
        - (stepper?.getBoundingClientRect().height || 0) - 16,
      behavior: matchMedia('(prefers-reduced-motion:reduce)').matches ? 'auto' : 'smooth'
    });
  }));
})();
