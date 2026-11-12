/* Country page controls. All cards, answers, tables and form fields are server-rendered HTML. */
(() => {
 'use strict';
 const dataNode=document.querySelector('#country-config');if(!dataNode)return;
 const c=JSON.parse(dataNode.textContent),$=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)],ui=window.MangoUI;
 const forms=$$('[data-country-form]'),request=$('#request-dialog'),weather=$('[data-weather-resort]'),hotelFilter=$('[data-hotel-filter]');
 let month=Number($('[data-weather-month][aria-pressed=true]').dataset.weatherMonth),monthChosen=false,format='beach',topic=c.name,message='Здравствуйте! Хочу поехать '+c.cases.to+'.',values={};
 const motion=matchMedia('(prefers-reduced-motion: reduce)');
 const scroll=n=>n.scrollIntoView({block:'start',behavior:motion.matches?'instant':'smooth'});
 const temp=n=>n==null?'—':(n>=0?'+':'')+n+' °C';
 function extras(form){const box=$('[data-extra-travelers]',form),on=['С детьми','Другой состав'].includes(form.elements.travelers.value);box.hidden=!on;$('input',box).disabled=!on;if(!on)$('input',box).value='';}
 function updateForms(){forms.forEach(form=>{form.elements.topic.value=topic;form.elements.month.value=monthChosen?String(month):'';const box=form.closest('.country-inquiry');$('[data-country-context]',box).textContent=topic;const note=$('[data-viewed-month]',box);note.hidden=!monthChosen;note.textContent=monthChosen?'Вы смотрели '+c.monthNames[month-1].toLowerCase()+'. Период можно выбрать ниже.':'';$$('[data-messenger]',box).forEach(a=>a.dataset.message=message);extras(form);});updateDirectMessages();}
 function updateDirectMessages(){const source=$('[data-country-inquiry=bottom] [data-messenger]');const text=ui.textFor(source);$$('.country-mobile-panel [data-messenger],.country-mobile-hero [data-messenger]').forEach(a=>a.dataset.message=text);}
 function alternatives(){const hint=$('[data-alternatives-context]');hint.textContent=format==='routes'?'Ваши даты · города и маршруты':c.monthNames[month-1]+' · отдых у моря';$$('[data-alternative-reason]').forEach(p=>{const item=c.alternatives.find(a=>a.country===p.dataset.alternativeReason);p.textContent=item.reasons?.[String(month)]?.[format]||c.alternativeSubtitles[item.country];});}
 function updateWeather(){const r=c.resorts.find(r=>r.id===weather.value)||c.resorts[0];$('[data-weather-label]').textContent=r.name+' · '+c.monthNames[month-1]+' · средние значения';$('[data-weather-air]').textContent=temp(r.air[month-1]);$('[data-weather-water]').textContent=temp(r.water[month-1]);$('[data-weather-note]').textContent=r.monthNotes[month-1]||'Средние показатели для курорта добавляются при наполнении страницы.';$$('[data-weather-month]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.weatherMonth)===month)));$$('[data-weather-table]').forEach(t=>t.hidden=t.dataset.weatherTable!==r.id);updateForms();alternatives();}
 function hotels(){let count=0;$$('[data-hotel-card]').forEach(card=>{card.hidden=!!hotelFilter.value&&card.dataset.hotelCard!==hotelFilter.value;if(!card.hidden)count++;});const empty=$('[data-hotel-empty]');empty.hidden=count>0;if(!count){const r=c.resorts.find(r=>r.id===hotelFilter.value),b=$('[data-country-request]',empty);b.dataset.countryRequest='resort';b.dataset.countryTopic=r?.name||c.name;b.dataset.countryMessage=r?'Здравствуйте! Хочу обсудить отдых. Курорт — '+r.name+'.':'Здравствуйте! Хочу поехать '+c.cases.to+'.';}}
 function sticky(){const panel=$('.country-mobile-panel'),cover=$('.country-hero'),end=$('#inquiry .country-inquiry'),footer=$('footer'),visible=n=>n.getBoundingClientRect().top<innerHeight&&n.getBoundingClientRect().bottom>0;panel.hidden=innerWidth>=768||cover.getBoundingClientRect().bottom>0||visible(end)||visible(footer)||!!$('dialog[open]')||!$('#mobile-nav').hidden;}
 function openRequest(b){topic=b.dataset.countryTopic||c.name;message=b.dataset.countryMessage||'Здравствуйте! Хочу поехать '+c.cases.to+'.';ui.resetCard(request);const form=$('form',request);Object.entries(values).forEach(([name,value])=>{if(form.elements[name])form.elements[name].value=value;});$('#request-title').textContent=b.textContent.includes('Узнать цену')?'Запрос стоимости':'Обсудим Вашу поездку';updateForms();ui.open(request,b);sticky();}
 forms.forEach(form=>{
  form.addEventListener('input',e=>{const field=e.target;if(!field.name||['consent','topic'].includes(field.name))return;values[field.name]=field.value;forms.filter(f=>f!==form).forEach(f=>{if(f.elements[field.name])f.elements[field.name].value=field.value;});updateDirectMessages();});
  form.addEventListener('change',e=>{if(e.target.name==='month'){monthChosen=!!e.target.value;if(monthChosen)month=Number(e.target.value);updateWeather();}if(e.target.name==='travelers')forms.forEach(extras);});
  form.addEventListener('submit',()=>{if(!form.hidden)return;values={};forms.filter(f=>f!==form).forEach(f=>{ui.resetCard(f.closest('.country-inquiry'));extras(f);});updateForms();});
 });
 weather.addEventListener('change',()=>{monthChosen=true;updateWeather();});hotelFilter.addEventListener('change',hotels);
 document.addEventListener('click',e=>{
  const b=e.target.closest('[data-country-request]');if(b){e.preventDefault();openRequest(b);return;}
  const m=e.target.closest('[data-weather-month]');if(m){month=Number(m.dataset.weatherMonth);monthChosen=true;updateWeather();return;}
  const formatButton=e.target.closest('[data-country-format]');if(formatButton){format=formatButton.dataset.countryFormat;$$('[data-country-format]').forEach(b=>b.setAttribute('aria-pressed',String(b===formatButton)));$$('[data-country-panel]').forEach(p=>p.hidden=p.dataset.countryPanel!==format);alternatives();return;}
  const more=e.target.closest('[data-more-resorts]');if(more){const open=more.getAttribute('aria-expanded')!=='true';more.setAttribute('aria-expanded',String(open));$$('[data-extra-resort]').forEach(r=>r.hidden=!open);more.textContent=open?'Свернуть курорты':'Все курорты';return;}
  const moreOffers=e.target.closest('[data-more-country-offers]');if(moreOffers){const open=moreOffers.getAttribute('aria-expanded')!=='true';moreOffers.setAttribute('aria-expanded',String(open));const cards=$$('[data-extra-country-offer]');cards.forEach(r=>r.classList.toggle('is-revealed',open));moreOffers.textContent=open?'Свернуть предложения':moreOffers.dataset.moreLabel;return;}
  const hotel=e.target.closest('[data-country-hotel]');if(hotel){ui.open($('#'+hotel.dataset.countryHotel+'-dialog'),hotel);sticky();return;}
  const hotelsLink=e.target.closest('[data-resort-hotels]');if(hotelsLink){e.preventDefault();hotelFilter.value=hotelsLink.dataset.resortHotels;hotels();scroll($('#hotels'));return;}
  const weatherLink=e.target.closest('[data-resort-weather]');if(weatherLink){e.preventDefault();weather.value=weatherLink.dataset.resortWeather;monthChosen=true;updateWeather();scroll($('#season'));return;}
  const essential=e.target.closest('[data-open-essential]');if(essential){e.preventDefault();const item=$(essential.getAttribute('href'));item.open=true;scroll(item);item.querySelector('summary').focus({preventScroll:true});}
 });
 function anchors(){let current;const links=$$('[data-country-anchor]');links.forEach(a=>{const s=$(a.getAttribute('href'));if(s.getBoundingClientRect().top<=190)current=a;});links.forEach(a=>a===current?a.setAttribute('aria-current','location'):a.removeAttribute('aria-current'));}
 addEventListener('scroll',()=>{sticky();anchors();},{passive:true});addEventListener('resize',sticky);document.addEventListener('d1:navstate',sticky);$$('dialog').forEach(d=>d.addEventListener('close',sticky));
 if(['#entry','#flight'].includes(location.hash))$(location.hash).open=true;
 updateWeather();hotels();sticky();anchors();
})();
