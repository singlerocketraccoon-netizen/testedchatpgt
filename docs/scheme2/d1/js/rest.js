(() => {
 'use strict';
 const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'),forms=$$('[data-rest-form]'),top=$('#rest-inquiry-top'),cover=$('[data-inner-cover]'),end=$('#contact'),sticky=$('[data-mobile-contact]'),menu=$('#mobile-nav'),sheet=$('#contact-dialog');
 let scrollFrame;
 const scrollToNode=node=>node.scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'start'});
 const phoneValid=input=>/^7\d{10}$/.test(input.value.replace(/\D/g,''));
 function mask(value){let d=value.replace(/\D/g,'');if(!d)return'';if(d[0]==='8')d='7'+d.slice(1);if(d[0]!=='7')d='7'+d;d=d.slice(0,11);return'+7'+(d.length>1?' ('+d.slice(1,4):'')+(d.length>4?') '+d.slice(4,7):'')+(d.length>7?'-'+d.slice(7,9):'')+(d.length>9?'-'+d.slice(9,11):'');}
 forms.forEach(form=>{
  const guard=$('[data-rest-guard]',form),phone=$('[name="phone"]',form),consent=$('[name="consent"]',form),submit=$('[data-rest-submit]',form),error=$('[data-rest-error]',form),card=form.closest('.rest-inquiry');guard.disabled=false;
  const clear=()=>{error.textContent='';$$('[aria-invalid]',form).forEach(n=>n.removeAttribute('aria-invalid'));};
  const sync=()=>{submit.disabled=!phoneValid(phone)||!consent.checked;clear();};
  phone.addEventListener('beforeinput',e=>{if(e.inputType!=='deleteContentBackward'||phone.selectionStart!==phone.selectionEnd)return;const end=phone.selectionStart;let start=end-1;while(start>=0&&/\D/.test(phone.value[start]))start--;if(start>=0&&start<end-1)phone.setSelectionRange(start,end);});
  phone.addEventListener('input',()=>{const value=phone.value,caret=phone.selectionStart,atEnd=caret===value.length,count=value.slice(0,caret).replace(/\D/g,'').length;phone.value=mask(value);if(!atEnd){let seen=0,pos=0;while(pos<phone.value.length&&seen<count){if(/\d/.test(phone.value[pos]))seen++;pos++;}phone.setSelectionRange(pos,pos);}sync();});form.addEventListener('change',sync);form.addEventListener('input',clear);
  form.addEventListener('submit',e=>{e.preventDefault();clear();if(!phoneValid(phone)||!consent.checked){const field=phoneValid(phone)?consent:phone;error.textContent=phoneValid(phone)?error.dataset.consentError:error.dataset.phoneError;field.setAttribute('aria-invalid','true');field.focus();return;}form.reset();sync();form.hidden=true;const success=$('[data-rest-success]',card);success.hidden=false;success.focus({preventScroll:true});document.dispatchEvent(new CustomEvent('mango:goal',{detail:{name:'rest_complete',page:document.body.dataset.page}}));updateSticky();});sync();
 });
 function select(choice){window.D1Nav?.close();const form=$('[data-rest-form]',top);form.hidden=false;$('[data-rest-success]',top).hidden=true;const output=$('[data-choice-output]',top);output.textContent=output.dataset.prefix+choice;output.hidden=!choice;scrollToNode(top);$('input:not([type="checkbox"]):not([type="hidden"])',form).focus({preventScroll:true});}
 const tabs=$$('[data-hotel-tab]'),panels=$$('[data-hotel-panel]');
 function activateHotel(country){tabs.forEach(t=>{const on=t.dataset.hotelTab===country;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;});panels.forEach(p=>p.hidden=p.dataset.hotelPanel!==country);}
 if(tabs[0])activateHotel(tabs[0].dataset.hotelTab);
 tabs.forEach((tab,i)=>{tab.addEventListener('click',e=>{e.preventDefault();activateHotel(tab.dataset.hotelTab);});tab.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const next=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;activateHotel(tabs[next].dataset.hotelTab);tabs[next].focus();});});
 function updateSticky(){sticky.hidden=innerWidth>=768||cover.getBoundingClientRect().bottom>90||(end.getBoundingClientRect().top<innerHeight&&end.getBoundingClientRect().bottom>0)||!menu.hidden||!!$('dialog[open]');}
 const anchors=$$('[data-rest-anchor]'),sections=anchors.map(a=>$(a.getAttribute('href')));
 function updateAnchors(){let current=0;sections.forEach((s,i)=>{if(s.getBoundingClientRect().top<=165)current=i;});anchors.forEach((a,i)=>{if(i===current)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}
 function update(){updateSticky();updateAnchors();}
 addEventListener('scroll',()=>{if(!scrollFrame)scrollFrame=requestAnimationFrame(()=>{scrollFrame=null;update();});},{passive:true});addEventListener('resize',update);document.addEventListener('d1:navstate',update);
 anchors.forEach(a=>a.addEventListener('click',e=>{e.preventDefault();scrollToNode($(a.getAttribute('href')));try{history.replaceState(null,'',a.getAttribute('href'));}catch{}}));
 [sheet].forEach(dialog=>{dialog.addEventListener('close',updateSticky);dialog.addEventListener('click',e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();});dialog.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const nodes=$$('button:not(:disabled),a[href],input:not(:disabled)',dialog).filter(n=>n.getClientRects().length&&!n.closest('[hidden]'));if(!nodes.length)return;const first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});});
 $$('[data-contact-open]').forEach(b=>b.disabled=false);
 document.addEventListener('click',async e=>{
  const goal=e.target.closest('[data-goal]');if(goal&&!goal.disabled)document.dispatchEvent(new CustomEvent('mango:goal',{detail:{name:goal.dataset.goal,page:document.body.dataset.page}}));
  const selection=e.target.closest('[data-rest-select]');if(selection){e.preventDefault();select(selection.dataset.restSelect);return;}
  const hotels=e.target.closest('[data-country-hotels]');if(hotels){e.preventDefault();activateHotel(hotels.dataset.countryHotels);scrollToNode($('#hotels'));return;}
  if(e.target.closest('[data-contact-open]')){window.D1Nav?.close();sheet.showModal();$('button',sheet).focus();updateSticky();return;}
  if(e.target.closest('[data-close]')){sheet.close();return;}
  if(e.target.closest('[data-contact-form]')){sheet.close();select('');return;}
  if(e.target.closest('a[href^="tel:"]'))e.target.closest('dialog')?.close();
 });
 update();
})();
