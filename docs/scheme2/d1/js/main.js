/* Mango Travel: manual navigation, local forms and explicit messenger actions. No storage or API. */
(() => {
 'use strict';
 const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
 const motion=matchMedia('(prefers-reduced-motion: reduce)'),config=JSON.parse($('#online-config')?.textContent||'{}'),openers=new WeakMap();
 const goal=name=>document.dispatchEvent(new CustomEvent('mango:goal',{detail:{name,page:document.body.dataset.page||'index.html'}}));
 const request=$('#request-dialog'),quiz=$('#quiz-dialog'),fallback=$('#messenger-fallback');let toastTimer;
 const scroll=node=>node?.scrollIntoView({behavior:motion.matches?'instant':'smooth',block:'start'});
 function sticky(){const button=$('[data-mobile-contact]'),cover=$('[data-hero],[data-inner-cover]'),footer=$('footer'),end=$('[data-end-contact],.rest-end');if(!button)return;const visible=n=>n&&n.getBoundingClientRect().top<innerHeight&&n.getBoundingClientRect().bottom>0;button.hidden=innerWidth>=768||!cover||cover.getBoundingClientRect().bottom>90||visible(footer)||visible(end)||!!$('dialog[open]')||!$('#mobile-nav')?.hidden;}
 addEventListener('scroll',sticky,{passive:true});addEventListener('resize',sticky);document.addEventListener('d1:navstate',sticky);
 function open(dialog,opener){window.D1Nav?.close();openers.set(dialog,opener||document.activeElement);if(!dialog.open)dialog.showModal();$('button:not(:disabled),input:not([type=hidden]):not(:disabled),a[href]',dialog)?.focus({preventScroll:true});sticky();}
 $$('dialog').forEach(dialog=>{
  dialog.addEventListener('close',()=>{openers.get(dialog)?.focus({preventScroll:true});sticky();});
  dialog.addEventListener('click',e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();});
  dialog.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const controls=$$('button:not(:disabled),a[href],input:not(:disabled),textarea:not(:disabled),select:not(:disabled)',dialog).filter(n=>n.getClientRects().length&&!n.closest('[hidden]'));if(!controls.length)return;const first=controls[0],last=controls.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
 });
 function resetCard(box){const form=$('form',box),success=$('[data-local-success],[data-rest-success]',box);if(form){form.hidden=false;form.reset();$$('[aria-invalid]',form).forEach(n=>n.removeAttribute('aria-invalid'));const err=$('[data-local-error],[data-rest-error]',form);if(err)err.textContent='';}if(success)success.hidden=true;}
 function openRequest(button){resetCard(request);const title=button.textContent.trim(),topic=button.dataset.topic||button.dataset.contactTopic||(button.dataset.hotelMessage?config.topic+' · Отель: '+button.dataset.hotelMessage:config.topic)||title;$('#request-title').textContent=title;request.querySelector('[name=topic]').value=topic;request.dataset.message=config.context;open(request,button);}
 function syncDates(){if(!quiz)return;const form=$('form',quiz),known=$('[name=when]:checked',form)?.value==='Знаю даты',pair=$('[data-known-dates]',form);pair.hidden=!known;$$('input',pair).forEach(i=>{i.disabled=!known;if(!known)i.value='';});}
 function openQuiz(button){resetCard(quiz);$$('[data-channel-status]',quiz).forEach(n=>n.hidden=true);$$('[name=preference]',quiz).forEach(n=>n.checked=n.value===button.dataset.preselect);syncDates();open(quiz,button);}
 // Every hero transition is initiated by a visitor. There is no timer or progress animation.
 const hero=$('[data-hero]');
 if(hero){const slides=$$('.hero-slide',hero);let index=0,start;
  function show(i){index=(i+slides.length)%slides.length;slides.forEach((s,n)=>{s.classList.toggle('is-active',n===index);s.inert=n!==index;s.setAttribute('aria-hidden',String(n!==index));});$('[data-hero-count]',hero).textContent=String(index+1);$('[data-hero-next-topic]',hero).textContent=slides[(index+1)%slides.length].dataset.slideAccent;}
  $('[data-hero-prev]',hero).addEventListener('click',()=>show(index-1));$('[data-hero-next]',hero).addEventListener('click',()=>show(index+1));
  hero.addEventListener('pointerdown',e=>{if(e.pointerType==='touch')start={x:e.clientX,y:e.clientY};});hero.addEventListener('pointerup',e=>{if(!start)return;const x=e.clientX-start.x,y=e.clientY-start.y;start=null;if(Math.abs(x)>50&&Math.abs(x)>Math.abs(y)*1.25)show(index+(x<0?1:-1));});hero.addEventListener('pointercancel',()=>start=null);
  hero.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();show(index+(e.key==='ArrowRight'?1:-1));}});show(0);
 }
 const toggle=$('[data-rest-toggle]');if(toggle){toggle.disabled=false;toggle.addEventListener('click',()=>{const more=$('#more-rest'),on=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(on));$('[data-rest-toggle-label]').hidden=on;$('[data-rest-less-label]').hidden=!on;$('[data-rest-chevron]').textContent=on?'⌃':'⌄';more.hidden=!on;more.classList.toggle('is-expanded',on);});}
 const mask=value=>{let d=value.replace(/\D/g,'');if(!d)return'';if(d[0]==='8')d='7'+d.slice(1);if(d[0]!=='7')d='7'+d;d=d.slice(0,11);return'+7'+(d.length>1?' ('+d.slice(1,4):'')+(d.length>4?') '+d.slice(4,7):'')+(d.length>7?'-'+d.slice(7,9):'')+(d.length>9?'-'+d.slice(9,11):'');};
 $$('[data-local-form]').forEach(form=>{
  const guard=$('[data-form-guard]',form),phone=$('[name=phone]',form),consent=$('[name=consent]',form),error=$('[data-local-error],[data-rest-error]',form),submit=$('button[type=submit]',form);guard.disabled=false;submit.disabled=false;
  phone.addEventListener('input',()=>phone.value=mask(phone.value));form.addEventListener('input',()=>{error.textContent='';$$('[aria-invalid]',form).forEach(n=>n.removeAttribute('aria-invalid'));});form.addEventListener('change',syncDates);
  form.addEventListener('submit',e=>{e.preventDefault();let invalid,message;if(!/^7\d{10}$/.test(phone.value.replace(/\D/g,''))){invalid=phone;message='Укажите телефон полностью.';}else if(!consent.checked){invalid=consent;message='Пожалуйста, отметьте согласие на обработку данных.';}else if(form.matches('[data-help-form]')&&form.elements.from.value&&form.elements.to.value&&form.elements.from.value>form.elements.to.value){invalid=form.elements.to;message='Дата «По» должна быть не раньше даты «С».';}if(invalid){error.textContent=message;invalid.setAttribute('aria-invalid','true');invalid.focus();return;}
   const parent=form.closest('dialog,.rest-inquiry,.country-inquiry'),success=$('[data-local-success],[data-rest-success]',parent);form.reset();syncDates();form.hidden=true;success.hidden=false;success.focus({preventScroll:true});goal('request_complete');
  });
 });
 function textFor(button){let text=button.dataset.message||config.context||'Здравствуйте! Хочу обсудить поездку.';const box=button.closest('dialog,.rest-inquiry,.country-inquiry'),form=box?.querySelector('form');if(!form)return text;const labels={topic:'Тема',phone:'Ваш телефон',wishes:'Пожелания',travellers:'Кто едет',when:'Когда',preference:'Что ближе',budget:'Бюджет',from:'С',to:'По'};const lines=[];for(const[name,value]of new FormData(form)){if(name==='consent'||!String(value).trim())continue;const field=form.elements.namedItem(name),element=field instanceof RadioNodeList?field[0]:field;lines.push((labels[name]||element?.closest('label')?.querySelector('span')?.textContent||name)+': '+(element?.tagName==='SELECT'?element.selectedOptions[0]?.textContent:value));}const choice=box.querySelector('[data-choice-output]');if(choice&&!choice.hidden)lines.push(choice.textContent);return text+(lines.length?'\n\n'+lines.join('\n'):'');}
 function copyFeedback(button,text){let status=button.closest('dialog')?.querySelector('[data-channel-status]');if(!status){const box=$('.toast');status=$('p',box);box.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>box.hidden=true,6500);}status.textContent=text;status.hidden=false;}
 function copyFallback(text,button){$('[data-fallback-text]',fallback).value=text;$('[data-copy-status]',fallback).textContent='';open(fallback,button);$('[data-fallback-text]',fallback).focus();}
 async function messenger(button){const text=textFor(button),channel=button.dataset.messenger;if(channel==='Telegram'){const user=(config.telegramUsername||'').replace(/^@/,'');if(!user){copyFallback(text,button);return;}window.open('https://t.me/'+encodeURIComponent(user)+'?text='+encodeURIComponent(text),'_blank','noopener');return;}
  let target;try{if(/^https?:/.test(config.max||'')){target=window.open('about:blank','_blank');if(target)target.opener=null;}if(!navigator.clipboard?.writeText)throw Error();await navigator.clipboard.writeText(text);copyFeedback(button,'Текст скопирован — вставьте его в чат');if(target)target.location.href=config.max;}catch{target?.close();copyFallback(text,button);}
 }
 function selectRest(value){const top=$('#rest-inquiry-top');resetCard(top);const output=$('[data-choice-output]',top);output.hidden=!value;output.textContent=output.dataset.prefix+value;scroll(top);$('input:not([type=hidden]):not([type=checkbox])',top).focus({preventScroll:true});}
 const tabs=$$('[data-hotel-tab]'),panels=$$('[data-hotel-panel]');function hotelTab(country){tabs.forEach(t=>{const on=t.dataset.hotelTab===country;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;});panels.forEach(p=>p.hidden=p.dataset.hotelPanel!==country);}
 if(tabs[0])hotelTab(tabs[0].dataset.hotelTab);tabs.forEach((t,i)=>{t.addEventListener('click',e=>{e.preventDefault();hotelTab(t.dataset.hotelTab);});t.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const n=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;hotelTab(tabs[n].dataset.hotelTab);tabs[n].focus();});});
 const anchors=$$('[data-rest-anchor]');function activeAnchor(){let current=anchors[0];anchors.forEach(a=>{if($(a.getAttribute('href'))?.getBoundingClientRect().top<170)current=a;});anchors.forEach(a=>a===current?a.setAttribute('aria-current','location'):a.removeAttribute('aria-current'));}if(anchors.length){addEventListener('scroll',activeAnchor,{passive:true});activeAnchor();}
 $$('[data-filter]').forEach(b=>b.addEventListener('click',()=>{const section=b.closest('section');$$('[data-filter]',section).forEach(n=>n.setAttribute('aria-pressed',String(n===b)));const items=$$('[data-filter-item]',section);items.forEach(n=>n.hidden=b.dataset.filter!=='Все'&&!n.dataset.categories.split('|').includes(b.dataset.filter));const status=$('[data-filter-status]',section);if(status)status.textContent='Показано: '+items.filter(n=>!n.hidden).length;}));
 document.addEventListener('click',e=>{
  const action=e.target.closest('[data-goal]');if(action&&!action.disabled)goal(action.dataset.goal);
  const close=e.target.closest('[data-dialog-close],[data-close]');if(close){close.closest('dialog')?.close();return;}
  const msg=e.target.closest('[data-messenger]');if(msg){e.preventDefault();messenger(msg);return;}
  const req=e.target.closest('[data-request],[data-hotel-message]');if(req){e.preventDefault();openRequest(req);return;}
  const help=e.target.closest('[data-quiz-open]');if(help){e.preventDefault();openQuiz(help);return;}
  const rest=e.target.closest('[data-rest-select]');if(rest){e.preventDefault();selectRest(rest.dataset.restSelect);return;}
  const hotels=e.target.closest('[data-country-hotels]');if(hotels){e.preventDefault();hotelTab(hotels.dataset.countryHotels);scroll($('#hotels'));return;}
  if(e.target.closest('[data-copy-message]')){const input=$('[data-fallback-text]',fallback),status=$('[data-copy-status]',fallback);(async()=>{try{await navigator.clipboard.writeText(input.value);status.textContent='Текст скопирован — вставьте его в чат';}catch{input.focus();input.select();status.textContent='Выделите и скопируйте текст вручную.';}})();}
 });
 $$('[data-quiz-open],[data-request]').forEach(b=>b.disabled=false);
  // Neutral partner slots: slow desktop scroll, touch rail on phones.
  const rail = $('[data-partner-rail]'), partnerPause = $('[data-partner-pause]');
  if(rail&&partnerPause){
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

  syncPartners();}

 window.MangoUI={open,resetCard,messenger,textFor};
 syncDates();sticky();
})();
