(() => {
 'use strict';
 const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
 const form=$('[data-discussion-form]'), contact=$('#contact'), sticky=$('[data-mobile-contact]'), cover=$('[data-inner-cover]'), menu=$('#mobile-nav'), sheet=$('#contact-dialog');
 const update=()=>{if(sticky)sticky.hidden=innerWidth>=768||cover.getBoundingClientRect().bottom>90||(contact.getBoundingClientRect().top<innerHeight&&contact.getBoundingClientRect().bottom>0)||!menu.hidden||!!$('dialog[open]');};
 addEventListener('scroll',update,{passive:true});addEventListener('resize',update);document.addEventListener('d1:navstate',update);
 const motion=matchMedia('(prefers-reduced-motion: reduce)');
 const focusContact=topic=>{window.D1Nav?.close();sheet.close();const field=$('[name="destination"]',form);if(topic)field.value=topic;contact.scrollIntoView({behavior:motion.matches?'instant':'smooth'});$('[name="contact"]',form).focus({preventScroll:true});};
 let toastTimer;
 function syncMethod(){const input=$('[name="contact"]',form),nick=$('[name="method"]',form).value!=='Телефон';input.type=nick?'text':'tel';input.inputMode=nick?'text':'tel';input.autocomplete=nick?'off':'tel';input.placeholder=nick?'@username или телефон':'+7 (___) ___-__-__';$('.field-hint',form).textContent=nick?'Ваш username или телефон':'Телефон для связи с Вами';}
 function clear(){ $$('.form-error',form).forEach(e=>e.textContent='');$$('[aria-invalid]',form).forEach(e=>e.removeAttribute('aria-invalid')); }
 const validPhone=v=>/^\+?[\d\s()\-]+$/.test(v)&&/^\d{10,15}$/.test(v.replace(/\D/g,''));
 form.querySelector('[data-form-guard]').disabled=false;
 form.addEventListener('change',e=>{clear();if(e.target.name==='method')syncMethod();});form.addEventListener('input',clear);
 form.addEventListener('submit',e=>{e.preventDefault();clear();const input=$('[name="contact"]',form),consent=$('[name="consent"]',form),value=input.value.trim(),nick=$('[name="method"]',form).value!=='Телефон';let bad;
  if(!(validPhone(value)||(nick&&/^@[\p{L}\p{N}_]{3,64}$/u.test(value)))){bad=input;$('.form-error',form).textContent='Укажите телефон или username для выбранного способа связи.';}
  else if(!consent.checked){bad=consent;$('.form-error',form).textContent='Пожалуйста, отметьте согласие на обработку данных.';}
  if(bad){bad.setAttribute('aria-invalid','true');bad.focus();return;}
  form.reset();$$('input:not([type="checkbox"]),textarea',form).forEach(f=>f.value='');consent.checked=false;form.hidden=true;$('[data-form-success]').hidden=false;$('[data-form-success]').focus();update();
 });
 $('[data-form-reset]').addEventListener('click',()=>{form.hidden=false;$('[data-form-success]').hidden=true;form.reset();clear();syncMethod();$('[name="contact"]',form).focus();});syncMethod();
 $$('[data-contact-open]').forEach(b=>b.disabled=false);
 sheet.addEventListener('close',update);
 sheet.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const items=$$('a,button',sheet),first=items[0],last=items.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
 sheet.addEventListener('click',e=>{if(e.target===sheet){const r=sheet.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)sheet.close();}});
 document.addEventListener('click',e=>{
  const goal=e.target.closest('[data-goal]');if(goal&&!goal.disabled)document.dispatchEvent(new CustomEvent('mango:goal',{detail:{name:goal.dataset.goal,page:document.body.dataset.page}}));
  const messenger=e.target.closest('[data-messenger]');if(messenger){e.preventDefault();sheet.close();const toast=$('.toast');toast.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.hidden=true,6500);return;}
  if(e.target.closest('[data-contact-open]')){window.D1Nav?.close();sheet.showModal();sheet.querySelector('button').focus();update();return;}
  if(e.target.closest('[data-close]')){sheet.close();return;}
  if(e.target.closest('a[href^="tel:"]')){sheet.close();return;}
  const topic=e.target.closest('[data-contact-topic]');if(topic){e.preventDefault();focusContact(topic.dataset.contactTopic);return;}
  if(e.target.closest('[data-contact-form]')){e.preventDefault();focusContact();}
 });
 $$('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
  const section=button.closest('section');$$('[data-filter]',section).forEach(b=>b.setAttribute('aria-pressed',String(b===button)));let count=0;
  $$('[data-filter-item]',section).forEach(item=>{item.hidden=button.dataset.filter!=='Все'&&!item.dataset.categories.split('|').includes(button.dataset.filter);if(!item.hidden)count++;});const status=$('[data-filter-status]',section);if(status)status.textContent='Показано: '+count;
 }));
 $$('.team-detail-card').forEach(card=>{const details=$('.team-help',card);card.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse')details.open=true;});card.addEventListener('pointerleave',()=>{if(!card.contains(document.activeElement))details.open=false;});});
 update();
})();
