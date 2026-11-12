/* Context goes only to the channel the visitor explicitly chooses. No storage or requests. */
(() => {
 'use strict';
 const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
 const node=$('#online-config');if(!node)return;
 const config=JSON.parse(node.textContent),fallback=$('#messenger-fallback');let toastTimer,opener;
 const goal=name=>document.dispatchEvent(new CustomEvent('mango:goal',{detail:{name,page:document.body.dataset.page||'index.html'}}));
 function messageFor(button){
  let text=button.dataset.message||config.context;
  if(button.dataset.hotelMessage)text+='\nОтель: '+button.dataset.hotelMessage;
  const form=button.closest('#quiz-dialog,.rest-inquiry,.form-column')?.querySelector('form');
  if(form){
   const lines=[];
   for(const [name,value] of new FormData(form)){
    if(!String(value).trim()||['phone','contact','consent','method','topic'].includes(name))continue;
    const input=form.elements.namedItem(name),element=input?.length?input[0]:input;
    const label={travellers:'Кто едет',when:'Когда',preference:'Что ближе',dates:'Даты',budget:'Бюджет',destination:'Направление и даты',wishes:'Пожелания'}[name]||element?.closest('label')?.querySelector('span')?.textContent||name;
    lines.push(label+': '+value);
   }
   const choice=button.closest('.rest-inquiry')?.querySelector('[data-choice-output]');if(choice&&!choice.hidden)lines.push(choice.textContent);
   if(lines.length)text+='\n\n'+lines.join('\n');
  }
  return text;
 }
 function toast(text){const dialog=$$('dialog[open]').at(-1),inline=dialog?.querySelector('[data-channel-status]'),box=inline||$('.toast');if(!box)return;(inline||$('p',box)).textContent=text;box.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>box.hidden=true,6500);}
 function showFallback(text,caption){
  opener=document.activeElement;$('[data-fallback-text]',fallback).value=text;$('[data-fallback-caption]',fallback).textContent=caption;$('[data-fallback-status]',fallback).textContent='';
  $$('[data-messenger]',fallback).forEach(a=>a.dataset.message=text);fallback.showModal();$('[data-fallback-text]',fallback).focus();
 }
 function allowed(url){try{return /^https?:$/.test(new URL(url).protocol);}catch{return false;}}
 async function openChannel(button){
  const channel=button.dataset.messenger||'Telegram',text=messageFor(button);goal(button.dataset.goal||'messenger_'+channel.toLowerCase());
  window.D1Nav?.close();
  if(channel==='Telegram'){
   const username=config.telegramUsername.replace(/^@/,'');
   if(!username){showFallback(text,'Адрес Telegram уточняется. Скопируйте сообщение или позвоните нам.');return;}
   const href='https://t.me/'+encodeURIComponent(username)+'?text='+encodeURIComponent(text);button.href=href;window.open(href,'_blank','noopener');return;
  }
  // Reserve a window during the user gesture; navigate only after successful copying.
  const target=allowed(config.max)?window.open('about:blank','_blank'):null;
  if(target)target.opener=null;
  try{
   if(!navigator.clipboard?.writeText)throw Error('clipboard unavailable');await navigator.clipboard.writeText(text);
   toast('Текст скопирован — вставьте его в чат');
   if(target)target.location.href=config.max;
  }catch{
   target?.close();showFallback(text,'Не удалось скопировать автоматически. Выделите текст или нажмите «Скопировать текст».');
  }
 }
 document.addEventListener('click',e=>{
  if(e.target.closest('[data-quiz-open]'))$$('[data-channel-status]').forEach(n=>n.hidden=true);
  const button=e.target.closest('[data-messenger],[data-hotel-message]');
  if(button){e.preventDefault();e.stopImmediatePropagation();openChannel(button);return;}
  if(e.target.closest('[data-fallback-close]')){fallback.close();return;}
  if(e.target.closest('[data-fallback-copy]')){
   e.preventDefault();const area=$('[data-fallback-text]',fallback),status=$('[data-fallback-status]',fallback);
   (async()=>{try{if(!navigator.clipboard?.writeText)throw Error();await navigator.clipboard.writeText(area.value);status.textContent='Текст скопирован — вставьте его в чат';}catch{area.focus();area.select();status.textContent='Выделите текст и скопируйте его вручную.';}})();return;
  }
  const formLink=e.target.closest('[data-contact-form],[data-contact-topic]');
  if(formLink){const details=$('details#contact');if(details)details.open=true;}
 },true);
 fallback.addEventListener('close',()=>opener?.focus({preventScroll:true}));
 fallback.addEventListener('click',e=>{if(e.target!==fallback)return;const r=fallback.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)fallback.close();});
 fallback.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const items=$$('a[href],button:not(:disabled),textarea',fallback).filter(n=>n.getClientRects().length),first=items[0],last=items.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
})();
