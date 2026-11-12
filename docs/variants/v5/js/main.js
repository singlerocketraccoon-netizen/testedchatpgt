/* Бутик-отель · vanilla JS. No requests, personal-data storage or external analytics. */
(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const header = $('[data-site-header]');
  const menu = $('#mobile-nav');
  const menuToggle = $('[data-menu]');
  const form = $('[data-discussion-form]');
  const discussion = $('#discuss');
  const selection = $('[data-mobile-selection]');
  const cover = $('[data-mobile-trigger]');
  const goal = name => document.dispatchEvent(new CustomEvent('mango:goal', {
    detail: {name, page: document.body.dataset.page || 'home-boutique-v5'}
  }));
  let toastTimer, scrollFrame, compact = false;

  function toast(message) {
    const node = $('.toast');
    if (!node) return;
    clearTimeout(toastTimer);
    node.textContent = message;
    node.hidden = false;
    toastTimer = setTimeout(() => { node.hidden = true; }, 6000);
  }

  // component: header
  function closeMenu(returnFocus = false) {
    if (!menu || !menuToggle) return;
    menu.hidden = true;
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.setAttribute('aria-label', 'Открыть меню');
    $('use', menuToggle)?.setAttribute('href', '#i-menu');
    if (returnFocus) menuToggle.focus();
    updateSelection();
  }
  menuToggle?.addEventListener('click', () => {
    if (!menu) return;
    const opening = menu.hidden;
    menu.hidden = !opening;
    menuToggle.setAttribute('aria-expanded', String(opening));
    menuToggle.setAttribute('aria-label', opening ? 'Закрыть меню' : 'Открыть меню');
    $('use', menuToggle)?.setAttribute('href', opening ? '#i-close' : '#i-menu');
    updateSelection();
  });
  if (menu) $$('a', menu).forEach(link => link.addEventListener('click', () => closeMenu()));
  matchMedia('(min-width: 1100px)').addEventListener('change', event => {
    if (event.matches) closeMenu();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu && !menu.hidden) closeMenu(true);
  });
  function updateHeader() {
    if (!compact && scrollY > 120) compact = true;
    if (compact && scrollY < 40) compact = false;
    header?.classList.toggle('is-compact', compact);
  }

  // component: hero
  $$('[data-hero]').forEach(root => {
    const slides = $$('.hero-slide', root);
    const previous = $('[data-hero-prev]', root);
    const next = $('[data-hero-next]', root);
    const pause = $('[data-hero-pause]', root);
    const count = $('[data-hero-count]', root);
    const progress = $('.slide-progress > span', root);
    const track = $('.hero-slides', root);
    if (!slides.length || !pause || !count || !track) return;
    let index = 0, userPaused = motion.matches, hovering = false;
    let focused = false, visible = true, timer, pointerStart;
    function sync() {
      clearTimeout(timer);
      const playing = !userPaused && !hovering && !focused && visible && !document.hidden;
      root.classList.toggle('is-playing', playing);
      root.classList.toggle('is-manual', userPaused);
      pause.setAttribute('aria-pressed', String(userPaused));
      pause.setAttribute('aria-label', userPaused ? 'Включить смену слайдов' : 'Остановить смену слайдов');
      $('use', pause)?.setAttribute('href', userPaused ? '#i-play' : '#i-pause');
      track.setAttribute('aria-live', userPaused ? 'polite' : 'off');
      if (playing) timer = setTimeout(() => show(index + 1), 7000);
    }
    function show(target, manual = false) {
      index = (target + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        slide.classList.toggle('is-active', i === index);
        slide.inert = i !== index;
        slide.setAttribute('aria-hidden', String(i !== index));
      });
      count.textContent = String(index + 1).padStart(2, '0');
      if (progress) {
        progress.style.animation = 'none';
        void progress.offsetWidth;
        progress.style.animation = '';
      }
      if (manual) userPaused = true;
      sync();
    }
    previous?.addEventListener('click', () => show(index - 1, true));
    next?.addEventListener('click', () => show(index + 1, true));
    pause.addEventListener('click', () => { userPaused = !userPaused; sync(); });
    root.addEventListener('mouseenter', () => { hovering = true; sync(); });
    root.addEventListener('mouseleave', () => { hovering = false; sync(); });
    root.addEventListener('focusin', () => { focused = true; sync(); });
    root.addEventListener('focusout', event => { focused = root.contains(event.relatedTarget); sync(); });
    root.addEventListener('pointerdown', event => {
      if (event.pointerType === 'touch') pointerStart = {x: event.clientX, y: event.clientY};
    });
    root.addEventListener('pointerup', event => {
      if (!pointerStart || event.pointerType !== 'touch') return;
      const dx = event.clientX - pointerStart.x;
      const dy = event.clientY - pointerStart.y;
      pointerStart = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.25) show(index + (dx < 0 ? 1 : -1), true);
    });
    root.addEventListener('pointercancel', () => { pointerStart = null; });
    root.addEventListener('keydown', event => {
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
        event.preventDefault();
        show(index + (event.key === 'ArrowRight' ? 1 : -1), true);
      }
    });
    document.addEventListener('visibilitychange', sync);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); }, {threshold: .1}).observe(root);
    }
    motion.addEventListener('change', event => { if (event.matches) userPaused = true; sync(); });
    show(0);
  });

  // component: mood-contents. HTML contains every image and caption.
  $$('.mood-grid').forEach(root => {
    const entries = $$('[data-mood-preview]', root);
    const choose = entry => entries.forEach(item => item.classList.toggle('is-active', item === entry));
    entries.forEach(entry => {
      entry.addEventListener('pointerenter', () => choose(entry));
      entry.addEventListener('focusin', () => choose(entry));
    });
  });

  // component: discussion-form. Validation is local; no submission or storage.
  function updateContactMethod() {
    if (!form) return;
    const method = $('[name="method"]:checked', form)?.value;
    const input = $('[name="contact"]', form);
    if (!input) return;
    const nickname = method === 'Telegram' || method === 'MAX';
    input.type = nickname ? 'text' : 'tel';
    input.inputMode = nickname ? 'text' : 'tel';
    input.autocomplete = nickname ? 'off' : 'tel';
    input.placeholder = nickname ? '@Ваш_ник или +7 (___) ___-__-__' : '+7 (___) ___-__-__';
    const phoneHint = $('[data-phone-hint]', form), nickHint = $('[data-nickname-hint]', form);
    if (phoneHint) phoneHint.hidden = nickname;
    if (nickHint) nickHint.hidden = !nickname;
    const error = $('.form-error', form);
    if (error) error.textContent = '';
    input.removeAttribute('aria-invalid');
    input.removeAttribute('aria-errormessage');
  }
  function setOffer(value) {
    if (!form) return;
    const field = $('[name="offer"]', form), caption = $('[data-selected-offer]', form);
    if (field) field.value = value;
    if (caption) { caption.textContent = value; caption.hidden = !value; }
  }
  const phoneValid = value => /^\+?[\d\s()\-]+$/.test(value) && /^\d{10,15}$/.test(value.replace(/\D/g, ''));
  const nicknameValid = value => /^@[\p{L}\p{N}_]{3,64}$/u.test(value);
  if (form && discussion) {
    const input = $('[name="contact"]', form);
    const consent = $('[name="consent"]', form);
    const error = $('.form-error', form);
    const success = $('[data-form-success]', discussion);
    if (input && consent && error && success) {
      $$('[name="method"]', form).forEach(radio => radio.addEventListener('change', updateContactMethod));
      form.addEventListener('submit', event => {
        event.preventDefault();
        const method = $('[name="method"]:checked', form)?.value;
        const nickname = method === 'Telegram' || method === 'MAX';
        const value = input.value.trim();
        $$('[aria-invalid]', form).forEach(field => {
          field.removeAttribute('aria-invalid'); field.removeAttribute('aria-errormessage');
        });
        let message = '', field;
        if (!phoneValid(value) && !(nickname && nicknameValid(value))) {
          message = nickname ? 'Укажите телефон или @ник, по которому можно связаться с Вами.' : 'Укажите телефон: от 10 до 15 цифр.';
          field = input;
        } else if (!consent.checked) {
          message = 'Чтобы продолжить, нужно Ваше согласие на обработку данных.';
          field = consent;
        }
        error.textContent = message;
        if (field) {
          field.setAttribute('aria-invalid', 'true');
          if (error.id) field.setAttribute('aria-errormessage', error.id);
          field.focus(); return;
        }
        form.reset(); setOffer(''); updateContactMethod();
        form.hidden = true; success.hidden = false; success.focus({preventScroll: true});
        goal('discussion_complete'); updateSelection();
      });
      $('[data-form-reset]', discussion)?.addEventListener('click', () => {
        success.hidden = true; form.hidden = false; updateContactMethod();
        input.focus({preventScroll: true}); updateSelection();
      });
      updateContactMethod();
      const guard = $('[data-form-guard]', form);
      if (guard) guard.disabled = false;
    }
  }

  function updateSelection() {
    if (!selection || !discussion) return;
    const rect = discussion.getBoundingClientRect();
    const atForm = rect.top < innerHeight && rect.bottom > 0;
    const passed = !cover || cover.getBoundingClientRect().bottom <= (header?.getBoundingClientRect().height || 66);
    selection.hidden = innerWidth >= 768 || !passed || atForm || (menu && !menu.hidden);
  }
  function requestScroll() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(() => {
      scrollFrame = null; updateHeader(); updateSelection();
    });
  }
  addEventListener('scroll', requestScroll, {passive: true});
  addEventListener('resize', requestScroll);
  if (discussion && 'IntersectionObserver' in window) new IntersectionObserver(updateSelection).observe(discussion);
  updateHeader(); updateSelection();

  document.addEventListener('click', event => {
    const target = event.target.closest('[data-goal]');
    if (target && !target.disabled) goal(target.dataset.goal);
    if (event.target.closest('[data-messenger]')) {
      event.preventDefault();
      toast('Этот способ связи пока недоступен. Позвоните: +7 (8512) 29-95-47.');
      return;
    }
    const action = event.target.closest('[data-discuss]');
    if (!action || !form || !discussion) return;
    event.preventDefault(); closeMenu();
    form.hidden = false;
    const success = $('[data-form-success]', discussion);
    if (success) success.hidden = true;
    if (action.dataset.offer) setOffer(action.dataset.offer);
    discussion.scrollIntoView({behavior: motion.matches ? 'instant' : 'smooth', block: 'start'});
    const heading = $('h2', discussion);
    if (heading) { heading.tabIndex = -1; heading.focus({preventScroll: true}); }
  });
})();
