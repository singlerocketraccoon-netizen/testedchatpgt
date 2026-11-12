/* Scheme 2 · design 1. Vanilla JS; local validation, no data transmission. */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const goal = name => document.dispatchEvent(new CustomEvent('mango:goal', {detail: {name, page: 'scheme2-d1'}}));
  const header = $('[data-site-header]'), menu = $('#mobile-nav'), menuButton = $('[data-menu]');
  const contact = $('#contact'), sticky = $('[data-mobile-contact]'), hero = $('[data-hero]');
  const quiz = $('#quiz-dialog'), sheet = $('#contact-dialog');
  let scrollFrame, toastTimer;
  const closeMenu = (restore = false) => { window.D1Nav?.close(restore); updateSticky(); };
  document.addEventListener('d1:navstate', updateSticky);
  function updateSticky() {
    if (!sticky || !hero || !contact) return;
    const c = contact.getBoundingClientRect();
    const coverCutoff = header.getBoundingClientRect().height + 24;
    sticky.hidden = innerWidth >= 768 || hero.getBoundingClientRect().bottom > coverCutoff ||
      (c.top < innerHeight && c.bottom > 0) || !menu.hidden || !!$('dialog[open]');
  }
  function updateScroll() { updateSticky(); }
  function requestScroll() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(() => { scrollFrame = null; updateScroll(); });
  }
  addEventListener('scroll', requestScroll, {passive: true}); addEventListener('resize', requestScroll);
  if ('IntersectionObserver' in window) new IntersectionObserver(updateSticky).observe(contact);
  // Four-slide cover; manual navigation always pauses automatic changes.
  const slides = $$('.hero-slide', hero), count = $('[data-hero-count]', hero), pause = $('[data-hero-pause]', hero);
  let index = 0, userPaused = motion.matches, hovering = false, focused = false, visible = true, timer, pointerStart;
  function syncSlider() {
    clearTimeout(timer);
    const playing = !userPaused && !hovering && !focused && visible && !document.hidden && !$('dialog[open]');
    hero.classList.toggle('is-playing', playing);
    pause.setAttribute('aria-pressed', String(userPaused));
    pause.setAttribute('aria-label', userPaused ? 'Включить смену слайдов' : 'Остановить смену слайдов');
    $('use', pause).setAttribute('href', userPaused ? '#i-play' : '#i-pause');
    $('.hero-slides', hero).setAttribute('aria-live', userPaused ? 'polite' : 'off');
    if (playing) timer = setTimeout(() => showSlide(index + 1), 7000);
  }
  function showSlide(target, manual = false) {
    index = (target + slides.length) % slides.length;
    slides.forEach((slide, n) => {
      slide.classList.toggle('is-active', n === index); slide.inert = n !== index;
      slide.setAttribute('aria-hidden', String(n !== index));
    });
    count.textContent = String(index + 1); hero.style.setProperty('--slide-progress', (index + 1) / slides.length);
    $$('[data-hero-dot]', hero).forEach(dot => dot.setAttribute('aria-current', String(Number(dot.dataset.heroDot) === index))); if (manual) userPaused = true; syncSlider();
  }
  $('[data-hero-prev]', hero).addEventListener('click', () => showSlide(index - 1, true));
  $('[data-hero-next]', hero).addEventListener('click', () => showSlide(index + 1, true));
  $$('[data-hero-dot]', hero).forEach(dot => { dot.disabled = false; dot.addEventListener('click', () => showSlide(Number(dot.dataset.heroDot), true)); });
  pause.addEventListener('click', () => { userPaused = !userPaused; syncSlider(); });
  hero.addEventListener('mouseenter', () => { hovering = true; syncSlider(); });
  hero.addEventListener('mouseleave', () => { hovering = false; syncSlider(); });
  hero.addEventListener('focusin', () => { focused = true; syncSlider(); });
  hero.addEventListener('focusout', e => { focused = hero.contains(e.relatedTarget); syncSlider(); });
  hero.addEventListener('pointerdown', e => { if (e.pointerType === 'touch') pointerStart = {x: e.clientX, y: e.clientY}; });
  hero.addEventListener('pointerup', e => {
    if (!pointerStart || e.pointerType !== 'touch') return;
    const dx = e.clientX - pointerStart.x, dy = e.clientY - pointerStart.y; pointerStart = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.25) showSlide(index + (dx < 0 ? 1 : -1), true);
  });
  hero.addEventListener('pointercancel', () => { pointerStart = null; });
  hero.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); showSlide(index + (e.key === 'ArrowRight' ? 1 : -1), true); }
  });
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { visible = entries[0].isIntersecting; syncSlider(); }, {threshold: .1}).observe(hero);
  document.addEventListener('visibilitychange', syncSlider);
  motion.addEventListener('change', e => { if (e.matches) userPaused = true; syncSlider(); });
  // Native dialogs provide focus containment, Escape and restoration to the opener.
  function openDialog(dialog) {
    closeMenu(); if (!dialog.open) dialog.showModal();
    $('button:not(:disabled), a[href], input:not(:disabled)', dialog)?.focus({preventScroll: true});
    updateSticky(); syncSlider();
  }
  $$('dialog').forEach(dialog => {
    dialog.addEventListener('keydown', e => {
      if (e.key !== 'Tab') return;
      const controls = $$('a[href], button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled)', dialog)
        .filter(node => node.getClientRects().length && !node.closest('[hidden]'));
      if (!controls.length) { e.preventDefault(); return; }
      const first = controls[0], last = controls[controls.length - 1];
      if (e.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    dialog.addEventListener('click', e => {
      if (e.target !== dialog) return;
      const r = dialog.getBoundingClientRect();
      if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close();
    });
    dialog.addEventListener('close', () => { updateSticky(); syncSlider(); });
  });
  const phoneValid = value => /^\+?[\d\s()\-]+$/.test(value) && /^\d{10,15}$/.test(value.replace(/\D/g, ''));
  const nicknameValid = value => /^@[\p{L}\p{N}_]{3,64}$/u.test(value);
  function clearError(form) {
    $$('.form-error', form).forEach(n => { n.textContent = ''; });
    $$('[aria-invalid]', form).forEach(n => { n.removeAttribute('aria-invalid'); n.removeAttribute('aria-errormessage'); });
  }
  function syncMethod(form) {
    const nick = $('[name="method"]', form).value !== 'Телефон', input = $('[name="contact"]', form);
    input.type = nick ? 'text' : 'tel'; input.inputMode = nick ? 'text' : 'tel'; input.autocomplete = nick ? 'off' : 'tel';
    input.placeholder = nick ? '@ваш_ник или +7 (___) ___-__-__' : '+7 (___) ___-__-__';
    $('.field-hint', form).textContent = nick ? 'Телефон или @ник в выбранном мессенджере' : 'Телефон для связи с Вами'; clearError(form);
  }
  function validate(form) {
    clearError(form);
    const input = $('[name="contact"]', form), consent = $('[name="consent"]', form), method = $('[name="method"]', form).value;
    let field, message;
    if (!phoneValid(input.value.trim()) && !(method !== 'Телефон' && nicknameValid(input.value.trim()))) {
      field = input; message = method === 'Телефон' ? 'Укажите телефон: от 10 до 15 цифр.' : 'Укажите телефон или @ник для связи с Вами.';
    } else if (!consent.checked) { field = consent; message = 'Чтобы продолжить, нужно согласие на обработку данных.'; }
    if (!field) return true;
    const error = $('.form-error', form); error.textContent = message;
    field.setAttribute('aria-invalid', 'true'); field.setAttribute('aria-errormessage', error.id); field.focus(); return false;
  }
  const form = $('[data-discussion-form]'), success = $('[data-form-success]');
  $('[name="method"]', form).addEventListener('change', () => syncMethod(form));
  form.addEventListener('submit', e => {
    e.preventDefault(); if (!validate(form)) return;
    form.reset(); syncMethod(form); form.hidden = true; success.hidden = false; success.focus({preventScroll: true});
    goal('contact_complete'); updateSticky();
  });
  $('[data-form-reset]').addEventListener('click', () => {
    success.hidden = true; form.hidden = false; syncMethod(form); $('[name="contact"]', form).focus({preventScroll: true});
  });
  function openContact(prefill) {
    $$('dialog[open]').forEach(d => d.close()); closeMenu(); form.hidden = false; success.hidden = true;
    contact.scrollIntoView({behavior: motion.matches ? 'instant' : 'smooth', block: 'start'});
    const heading = $('h2', contact); heading.tabIndex = -1; heading.focus({preventScroll: true}); updateSticky();
  }
  syncMethod(form); $('[data-form-guard]', form).disabled = false;
  // One accessible selection form; answers stay in memory and are cleared locally.
  const poll = $('[data-quiz-form]'), pollSuccess = $('[data-quiz-success]');
  const submit = $('[data-quiz-submit]', poll), phone = $('[name="phone"]', poll), consent = $('[name="consent"]', poll);
  const dates = $('[data-selection-dates]', poll), datesInput = $('[name="dates"]', poll);
  const readyPhone = () => /^7\d{10}$/.test(phone.value.replace(/\D/g, ''));
  function syncPoll() {
    const known = $('[name="when"]:checked', poll)?.value === 'Знаю даты';
    dates.hidden = !known; datesInput.disabled = !known;
    if (!known) datesInput.value = '';
    submit.disabled = !readyPhone() || !consent.checked;
    clearError(poll);
  }
  function resetPoll() {
    poll.reset(); poll.hidden = false; pollSuccess.hidden = true;
    syncPoll();
  }
  function openPoll(preselect) {
    resetPoll();
    $$('[name="preference"]', poll).forEach(input => input.checked = input.value === preselect);
    openDialog(quiz);
  }
  function maskPhone(value) {
    let digits = value.replace(/\D/g, '');
    if (!digits) return '';
    if (digits[0] === '8') digits = '7' + digits.slice(1);
    if (digits[0] !== '7') digits = '7' + digits;
    digits = digits.slice(0, 11);
    let result = '+7';
    if (digits.length > 1) result += ' (' + digits.slice(1, 4);
    if (digits.length > 4) result += ') ' + digits.slice(4, 7);
    if (digits.length > 7) result += '-' + digits.slice(7, 9);
    if (digits.length > 9) result += '-' + digits.slice(9, 11);
    return result;
  }
  phone.addEventListener('beforeinput', e => {
    if (e.inputType !== 'deleteContentBackward' || phone.selectionStart !== phone.selectionEnd) return;
    const end = phone.selectionStart; let start = end - 1;
    while (start >= 0 && /\D/.test(phone.value[start])) start--;
    if (start >= 0 && start < end - 1) phone.setSelectionRange(start, end);
  });
  phone.addEventListener('input', () => {
    const old = phone.value, caret = phone.selectionStart, end = caret === old.length;
    const digitsBefore = old.slice(0, caret).replace(/\D/g, '').length;
    phone.value = maskPhone(old);
    if (!end) {
      let count = 0, pos = 0;
      while (pos < phone.value.length && count < digitsBefore) { if (/\d/.test(phone.value[pos])) count++; pos++; }
      phone.setSelectionRange(pos, pos);
    }
    syncPoll();
  });
  poll.addEventListener('change', syncPoll);
  poll.addEventListener('submit', e => {
    e.preventDefault(); clearError(poll);
    if (!readyPhone() || !consent.checked) {
      const error = $('[data-selection-error]', poll), field = readyPhone() ? consent : phone;
      error.textContent = readyPhone() ? error.dataset.errorConsent : error.dataset.errorPhone;
      field.setAttribute('aria-invalid', 'true'); field.setAttribute('aria-errormessage', error.id); field.focus(); return;
    }
    poll.reset(); syncPoll(); poll.hidden = true; pollSuccess.hidden = false;
    pollSuccess.focus({preventScroll: true}); goal('quiz_complete');
  });
  quiz.addEventListener('close', resetPoll);
  $('[data-quiz-guard]', poll).disabled = false; resetPoll();
  const moreToggle = $('[data-rest-toggle]'), more = $('#more-rest');
  let moreTimer, moreFrame;
  moreToggle.disabled = false;
  moreToggle.addEventListener('click', () => {
    const expanded = moreToggle.getAttribute('aria-expanded') !== 'true';
    clearTimeout(moreTimer); cancelAnimationFrame(moreFrame);
    moreToggle.setAttribute('aria-expanded', String(expanded));
    $('[data-rest-toggle-label]').hidden = expanded; $('[data-rest-less-label]').hidden = !expanded;
    $('[data-rest-chevron]').textContent = expanded ? '⌃' : '⌄';
    if (expanded) { more.hidden = false; moreFrame = requestAnimationFrame(() => more.classList.add('is-expanded')); }
    else { more.classList.remove('is-expanded'); moreTimer = setTimeout(() => { more.hidden = true; }, motion.matches ? 0 : 260); }
  });
  // Neutral partner slots: slow desktop scroll, touch rail on phones.
  const rail = $('[data-partner-rail]'), partnerPause = $('[data-partner-pause]');
  let partnerPaused = motion.matches, partnerHover = false, partnerFocus = false, partnerVisible = false, raf, lastTime = 0, partnerPosition = 0;
  function partnerPlaying() { return !partnerPaused && !partnerHover && !partnerFocus && partnerVisible && !document.hidden && !motion.matches && innerWidth >= 768; }
  function tick(time) {
    if (!partnerPlaying()) { raf = null; lastTime = 0; return; }
    const delta = Math.min(time - (lastTime || time), 50); lastTime = time;
    partnerPosition += delta * .018; rail.scrollLeft = partnerPosition;
    if (partnerPosition >= rail.scrollWidth - rail.clientWidth - 1) { partnerPosition = 0; rail.scrollLeft = 0; }
    raf = requestAnimationFrame(tick);
  }
  function syncPartners() {
    const playing = partnerPlaying();
    rail.classList.toggle('is-auto', !partnerPaused && !motion.matches && innerWidth >= 768);
    partnerPause.setAttribute('aria-pressed', String(partnerPaused));
    partnerPause.setAttribute('aria-label', partnerPaused ? 'Включить прокрутку партнёров' : 'Остановить прокрутку партнёров');
    $('use', partnerPause).setAttribute('href', partnerPaused ? '#i-play' : '#i-pause');
    if (playing && !raf) { partnerPosition = rail.scrollLeft; raf = requestAnimationFrame(tick); }
    if (!playing && raf) { cancelAnimationFrame(raf); raf = null; lastTime = 0; }
  }
  partnerPause.addEventListener('click', () => { partnerPaused = !partnerPaused; syncPartners(); });
  function movePartners(direction) {
    partnerPaused = true; syncPartners();
    const card = $('.partner-logo', rail);
    rail.scrollBy({left: (card.getBoundingClientRect().width + 18) * direction, behavior: motion.matches ? 'instant' : 'smooth'});
  }
  $('[data-partner-prev]').addEventListener('click', () => movePartners(-1));
  $('[data-partner-next]').addEventListener('click', () => movePartners(1));
  rail.addEventListener('mouseenter', () => { partnerHover = true; syncPartners(); });
  rail.addEventListener('mouseleave', () => { partnerHover = false; syncPartners(); });
  rail.addEventListener('focusin', () => { partnerFocus = true; syncPartners(); });
  rail.addEventListener('focusout', e => { partnerFocus = rail.contains(e.relatedTarget); syncPartners(); });
  ['pointerdown', 'wheel', 'keydown'].forEach(name => rail.addEventListener(name, () => { partnerPaused = true; syncPartners(); }, {passive: true}));
  if ('IntersectionObserver' in window) new IntersectionObserver(entries => { partnerVisible = entries[0].isIntersecting; syncPartners(); }).observe(rail);
  else partnerVisible = true;
  document.addEventListener('visibilitychange', syncPartners); addEventListener('resize', syncPartners);
  motion.addEventListener('change', e => { if (e.matches) partnerPaused = true; syncPartners(); });
  // Delegated actions carry goal names only, never contacts or form answers.
  document.addEventListener('click', e => {
    const action = e.target.closest('[data-goal]'); if (action && !action.disabled) goal(action.dataset.goal);
    const close = e.target.closest('[data-close]');
    if (close) { close.closest('dialog').close(); return; }
    const messenger = e.target.closest('[data-messenger]');
    if (messenger) {
      e.preventDefault(); messenger.closest('dialog')?.close();
      const node = $('.toast'); node.hidden = false; clearTimeout(toastTimer);
      toastTimer = setTimeout(() => { node.hidden = true; }, 6500); return;
    }
    e.target.closest('a[href^="tel:"]')?.closest('dialog')?.close();
    const quizAction = e.target.closest('[data-quiz-open]');
    if (quizAction) {
      e.preventDefault(); openPoll(quizAction.dataset.preselect || ''); return;
    }
    if (e.target.closest('[data-contact-open]')) { openDialog(sheet); return; }
    const offer = e.target.closest('[data-offer]');
    if (offer) { e.preventDefault(); openContact(offer.dataset.offer); return; }
    if (e.target.closest('[data-contact-form]')) { e.preventDefault(); openContact(); }
  });
  $$('[data-quiz-open], [data-contact-open], [data-menu], [data-hero-prev], [data-hero-next], [data-hero-pause], [data-partner-prev], [data-partner-next], [data-partner-pause]').forEach(b => { b.disabled = false; });
  showSlide(0); syncPartners(); updateScroll();
})();
