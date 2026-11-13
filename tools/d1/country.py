"""Country pages, scheme 12.11 / Egypt revision 3. All content rendered into HTML."""
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,re
MONTHS=['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
SHORT=['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек']
QUESTIONS=[('entry','Нужна ли виза'),('flight','Сколько лететь и какая разница во времени'),('money','Какие деньги брать и как платить'),('mobile','Как быть со связью и интернетом'),('rules','Местные правила и привычки'),('health','Здоровье и страховка')]

def configure(ctx):
 global C,D,E,I,U,L,ED
 C=ctx;D=ctx['DATA'];E=ctx['E'];I=ctx['icon'];U=ctx['url'];L=ctx['link'];ED=ctx['editable']
 assert hashlib.sha256((ctx['ROOT']/D['country_source_file']).read_bytes()).hexdigest()==D['country_source_sha256'],'Country source changed: import approved copy first'
 p=C['SITE']/'CHECKLIST.md';s=p.read_text();s=re.sub(r'<!-- build:stage5-countries -->.*?<!-- /build:stage5-countries -->','',s,flags=re.S)
 lines=['<!-- build:stage8-countries -->','## Этап 8 · страны','', 'Египет: тексты редакции 3 из схемы 12.11 перенесены дословно, но остаются на утверждении. Все предварительные тексты, числа и даты отмечены `data-needs-approval`. Схема — источник редакции, а не подтверждение туристических фактов.','']
 for c in D['countries']:
  lines += ['### '+c['name'],'','- Утвердить вступление и описания: '+', '.join(r['name']for r in (c['routes']if c['placesMode']=='routes'else c['resorts']))+'.', '- '+('Сверить четыре климатических массива (воздух, вода, ветер), осадки, 24 подсказки месяцев и использование станции Хургады для Эль-Гуны, Макади-Бей, Сахл-Хашиша.'if c['slug']=='egipet'else'Предоставить помесячный климат, ветер/осадки и подсказки. Сейчас чисел нет; климатический блок скрыт.'), '- '+('Отели 1–3: заменить реальными отелями, подтвердить рекомендации, ограничения и фотографии.'if c['hotels']else'Предоставить отели, фотографии, рекомендации и ограничения; пустой блок скрыт.'), '- '+('Проверить шесть справочных ответов (особенно визы, платежи, SIM, страховка) и «Проверено: ноябрь 2026»; подтвердить четыре экскурсии и комбинированный маршрут.'if c['essentials']else'Предоставить шесть справочных ответов с датой проверки; пустые ответы скрыты.'), '- Нужны согласованный реальный отзыв, автор, дата и источник; без данных отзыв скрыт.', '- Сверить перелёт и сезон в карточках других стран, вступления и фотографии. Отсутствующие значения не заменены придуманными фактами.','']
 lines+=['<!-- /build:stage8-countries -->'];block='\n'.join(lines)
 if '<!-- build:stage8-countries -->'in s:s=re.sub(r'<!-- build:stage8-countries -->.*?<!-- /build:stage8-countries -->',lambda _:block,s,flags=re.S)
 else:s=s.rstrip()+'\n\n'+block+'\n'
 p.write_text(s)

def photo(path,name,alt,key,lazy=True):
 if name:return C['image'](path,name,alt,lazy,key=key)
 return '<div class="country-photo-placeholder" role="img" aria-label="'+E(alt)+'" '+ED(key,True)+'>'+I('i-mood-horizon')+'<span>'+E(alt)+'</span></div>'
def section(c,id,title,body):return '<section class="section country-section" id="'+id+'"><div class="container"><div class="section-head"><h2 '+ED('countries.'+c['slug']+'.'+id+'.title')+'>'+E(title)+'</h2></div>'+body+'</div></section>'
def temp(n):return '—'if n is None else('+'if n>=0 else'')+str(n)+' °C'
def weather_data(c,r):return c['climate'].get(r.get('w'),dict(air=[None]*12,water=[None]*12,wind=[None]*12,rain=''))
def note(c,r,month):return c['monthNotes'].get('alamein'if r.get('w')=='alamein'else'redSea',['Средние показатели для курорта добавляются при наполнении страницы.']*12)[month-1]
def weather_label(c,r,month):return r['name']+' · '+MONTHS[month-1]+' · средние многолетние данные'+(' · по данным метеостанции Хургады'if c['slug']=='egipet'and r['w']!=r['id']else'')
def has_climate(c):
 return any(isinstance(n,(int,float))and not isinstance(n,bool)for w in c.get('climate',{}).values()for field in ['air','water','wind']for n in w.get(field,[]))
def climate(c):
 rs=c['resorts'];r=rs[0];month=datetime.now(ZoneInfo('Europe/Moscow')).month;w=weather_data(c,r);key='countries.'+c['slug']+'.climate'
 select='<label class="field-label country-select"><span>'+E(c['resortLabel'])+'</span><select data-weather-resort data-goal="weather_resort">'+''.join('<option value="'+r['id']+'">'+E(r['name'])+'</option>'for r in rs)+'</select></label>'
 months='<div class="country-months" role="group" aria-label="Выбор месяца">'+''.join('<button type="button" data-weather-month="'+str(i)+'" aria-label="'+m+'" aria-pressed="'+str(i==month).lower()+'" data-goal="weather_month_'+str(i)+'">'+SHORT[i-1]+'</button>'for i,m in enumerate(MONTHS,1))+'</div>'
 nums=''.join('<p><strong data-weather-'+field+'>'+E(temp(w[field][month-1])if field!='wind'else'—'if w[field][month-1]is None else str(w[field][month-1])+' м/с')+'</strong><span>'+label+'</span></p>'for field,label in [('air','Воздух днём'),('water','Вода'),('wind','Ветер')])
 result='<div class="country-weather-result" aria-live="polite"><p data-weather-label>'+E(weather_label(c,r,month))+'</p><div class="country-temperature">'+nums+'</div><div data-weather-notes>'+''.join('<p data-weather-note="'+r['id']+'-'+str(i)+'"'+(''if r==rs[0]and i==month else' hidden')+'>'+E(note(c,r,i))+'</p>'for r in rs for i in range(1,13))+'</div></div>'
 tables=''
 for i,r in enumerate(rs):
  w=weather_data(c,r);rows=''.join('<tr><th scope="row">'+m+'</th><td>'+temp(w['air'][j])+'</td><td>'+temp(w['water'][j])+'</td><td>'+('—'if w['wind'][j]is None else str(w['wind'][j])+' м/с')+'</td></tr>'for j,m in enumerate(MONTHS))
  tables+='<div data-weather-table="'+r['id']+'"'+(' hidden'if i else'')+'><div class="table-scroll" tabindex="0" role="region" aria-label="Климат по месяцам"><table><caption>'+E(r['name'])+'</caption><thead><tr><th scope="col">Месяц</th><th scope="col">Воздух днём</th><th scope="col">Вода</th><th scope="col">Ветер</th></tr></thead><tbody>'+rows+'</tbody></table></div><p class="country-weather-foot">'+E(w['rain'])+(' 'if w['rain']else'')+'Средние многолетние данные. Ветер: до 5 м/с — слабый, 6–7 м/с — умеренный.</p></div>'
 intro='<p class="country-section-intro" '+ED(key+'.intro',True)+'>'+E(c['seasonIntro'])+'</p>'if c['seasonIntro']else''
 return section(c,'season','Когда ехать',intro+'<div class="country-weather" '+ED(key,True)+'>'+select+months+result+'<details class="country-weather-table"><summary data-goal="weather_table">Таблица по месяцам</summary>'+tables+'</details></div>')

def resorts(c,path):
 key='countries.'+c['slug'];cards='';routes=c['placesMode']=='routes';rows=c['routes']if routes else c['resorts']
 for i,r in enumerate(rows):
  if routes:
   cards+='<article class="country-card-panel" '+ED(key+'.routes.'+r['id'],True)+'>'+photo(path,r.get('photo'),'Фото: '+r['name'],key+'.routes.'+r['id']+'.photo')+'<div class="country-card-body"><h3>'+E(r['name'])+'</h3>'+(''.join('<p>'+E(r[f])+'</p>'for f in ['stops','pace']if r.get(f)and'·'not in r[f]))+action(c,'Обсудить маршрут','route',r,'country_route_'+r['id'],'text-link')+'</div></article>';continue
  fields=[('beach','Пляж и вход в море'),('mood','Атмосфера'),('road','Дорога'),('note','Что учесть')];facts=''.join('<div><dt>'+label+'</dt><dd>'+E(r.get(f)or r.get(dict(mood='atmosphere',road='transfer',note='feature').get(f,''))or'Уточним при подборе поездки.')+'</dd></div>'for f,label in fields)
  links=('<a href="#hotels" data-resort-hotels="'+r['id']+'" data-goal="resort_hotels_'+r['id']+'">Посмотреть отели</a>'if c['hotels']else'')+('<a href="#season" data-resort-weather="'+r['id']+'" data-goal="resort_weather_'+r['id']+'">Когда ехать</a>'if has_climate(c)else'')
  cards+='<article class="country-card-panel country-resort" data-resort-card="'+r['id']+'"'+(' data-extra-resort hidden'if i>=3 else'')+' '+ED(key+'.resorts.'+r['id'],True)+'><details><summary data-goal="resort_expand_'+r['id']+'">'+photo(path,r.get('photo'),'Фото курорта '+r['name'],key+'.resorts.'+r['id']+'.photo')+'<span>'+E(r['name'])+I('i-plus')+'</span></summary><div class="country-card-body"><dl class="country-resort-facts">'+facts+'</dl><div class="country-card-links">'+links+'</div></div></details><div class="country-card-body"><p>'+E(r['short'])+'</p>'+action(c,'Подобрать отдых здесь','resort',r,'resort_request_'+r['id'],'text-link')+'</div></article>'
 intro='<p class="country-section-intro" '+ED(key+'.resortsIntro',True)+'>'+E(c['resortsIntro'])+'</p>'if c['resortsIntro']else''
 more='<button type="button" class="btn btn-outline" data-more-resorts aria-expanded="false" aria-controls="country-resort-grid" data-goal="resorts_more">Все курорты</button>'if not routes and len(rows)>3 else''
 return section(c,'resorts','Города и маршруты'if routes else'Где отдыхать',intro+'<div class="country-grid" id="country-resort-grid">'+cards+'</div>'+more)

def hotelcopy(h):return ''.join('<p><strong>'+label+'</strong> '+E(h[f])+'</p>'for f,label in [('fit','Кому рекомендуем'),('good','Чем хорош'),('note','Что учесть')])
def hotels(c,path):
 if not c['hotels']:return '', ''
 key='countries.'+c['slug'];cards='';dialogs=''
 for h in c['hotels']:
  r=next(r for r in c['resorts']if r['id']==h['resort']);visual=photo(path,h['photos'][0]if h['photos']else None,'Фото '+h['name'],key+'.hotels.'+h['id']+'.photos')
  trigger='<button type="button" class="country-hotel-open" data-country-hotel="'+h['id']+'" data-goal="hotel_open_'+h['id']+'">'+visual+'<span>'+E(h['name'])+' →</span></button>'
  cards+='<article class="country-card-panel" data-hotel-card="'+r['id']+'" '+ED(key+'.hotels.'+h['id'],True)+'>'+trigger+'<div class="country-card-body"><p class="country-hotel-resort">'+E(r['name'])+'</p>'+hotelcopy(h)+action(c,'Узнать цену на мои даты','hotel',h,'hotel_request_'+h['id'],'text-link')+'</div></article>'
  dialogs+='<dialog class="country-hotel-dialog" id="'+h['id']+'-dialog" aria-modal="true" aria-labelledby="'+h['id']+'-title" '+ED(key+'.hotels.'+h['id'],True)+'><div class="dialog-top"><h2 id="'+h['id']+'-title">'+E(h['name'])+'</h2><button class="icon-btn" type="button" data-dialog-close data-goal="hotel_close_'+h['id']+'" aria-label="Закрыть отель">'+I('i-close')+'</button></div>'+visual+'<p>'+E(r['name'])+'</p>'+hotelcopy(h)+action(c,'Узнать цену на мои даты','hotel',h,'hotel_dialog_request_'+h['id'])+'</dialog>'
 tips='<div class="country-hotel-tips">'+''.join('<article class="info-card" '+ED(key+'.tips.'+str(i),True)+'><h3>'+E(t['title'])+'</h3><p>'+E(t['text'])+'</p></article>'for i,t in enumerate(c['tips']))+'</div>'if c['tips']else''
 select='<label class="field-label country-select"><span>'+E(c['resortLabel'])+'</span><select data-hotel-filter data-goal="country_hotel_filter"><option value="">Все курорты</option>'+''.join('<option value="'+r['id']+'">'+E(r['name'])+'</option>'for r in c['resorts'])+'</select></label>'
 empty='<div class="country-hotel-empty" data-hotel-empty hidden><h3>Отели этого курорта подберём под Ваши даты.</h3>'+action(c,'Обсудить отели курорта',key='hotel_empty_request')+'</div>'
 return section(c,'hotels','Отели '+c['cases']['in'],tips+select+'<div class="country-grid country-hotel-grid">'+cards+'</div>'+empty),dialogs

def country(c):
 import stage6 as shared
 path='napravleniya/'+c['slug']+'/index.html';key='countries.'+c['slug'];ess=c['essentials'];hasoffers=c['showOffers']and bool(C['active_offers'](c['slug']))
 facts=('<a href="#season" data-goal="country_season">Сезон по курортам</a>'if has_climate(c)else'')+('<a href="#flight" data-open-essential data-goal="country_flight">Перелёт и разница во времени</a><a href="#entry" data-open-essential data-goal="country_entry">Правила въезда</a>'if ess else'')
 cover='<section class="country-hero" data-inner-cover>'+photo(path,c['heroPhoto'],c['alt'],key+'.heroPhoto',False)+'<div class="container">'+C['crumb'](path,[('Страны','napravleniya/index.html'),(c['name'],None)])+'<div class="country-hero-grid"><div class="country-hero-copy"><p class="hero-accent" '+ED(key+'.name')+'>'+E(c['name'])+'</p><h1 '+ED(key+'.h1')+'>'+E(c['h1'])+'</h1><p class="country-subtitle" '+ED(key+'.subtitle',True)+'>'+E(c['subtitle'])+'</p><div class="country-hero-facts">'+facts+'</div><div class="country-mobile-hero">'+action(c,'Подобрать тур')+shared.channels('country:'+c['slug'],'country_hero')+'</div></div><div class="country-hero-form">'+form(c,path,'top')+'</div></div></div></section>'
 nav=([('season','Когда ехать')]if has_climate(c)else[])+[('resorts','Города и маршруты'if c['placesMode']=='routes'else'Курорты')]+([('offers','Предложения')]if hasoffers else[])+([('hotels','Отели')]if c['hotels']else[])+([('experiences','Чем заняться')]if c['experiences']else[])+([('essentials','Важно знать')]if ess else[])
 body='<nav class="country-page-nav" aria-label="На странице"><div class="container">'+''.join('<a href="#'+id+'" data-country-anchor data-goal="country_anchor_'+id+'">'+title+'</a>'for id,title in nav)+'</div></nav>'+(climate(c)if has_climate(c)else'')+resorts(c,path)+offers(c,path)
 body+='<div class="container"><div class="country-price-strip" id="price-strip"><div><h3>Другие даты или город вылета</h3><p>Менеджер уточнит стоимость под Ваши условия.</p></div><div class="country-strip-actions">'+action(c,'Узнать цену на мои даты','price',key='country_price_request')+shared.channels('price:'+c['slug'],'country_price')+'</div></div></div>'
 hotelbody,dialogs=hotels(c,path);body+=hotelbody
 if c['experiences']:
  cards=''
  for i,x in enumerate(c['experiences']):
   r=next((r for r in c['routes']if r['id']==x.get('routeId')),None)
   cards+='<article class="country-card-panel" '+ED(key+'.experiences.'+str(i),True)+'>'+photo(path,x.get('photo'),'Фото: '+x['title'],key+'.experiences.'+str(i)+'.photo')+'<div class="country-card-body"><h3>'+E(x['title'])+'</h3>'+('<p>'+E(x['text'])+'</p>'if x['text']else'')+(action(c,'Обсудить маршрут','route',r,'experience_route_'+str(i),'text-link')if r else'')+'</div></article>'
  combine='<div class="country-price-strip" '+ED(key+'.combine',True)+'><div><h3>Можно совместить</h3><p>'+E(c['combine'])+'</p></div><div class="country-strip-actions">'+action(c,'Обсудить маршрут','route',key='country_combine')+L(path,'otdyh/svoj-marshrut/index.html','Свой маршрут →','country_own_route','text-link')+'</div></div>'if c['combine']else''
  body+=section(c,'experiences','Чем заняться','<div class="country-experiences">'+cards+'</div>'+combine)
 if ess:
  body+=section(c,'essentials','Что важно знать до поездки',C['accordion_columns']('country-essentials',''.join('<details class="faq-item" id="'+id+'" '+ED(key+'.essentials.'+id,True)+'><summary data-goal="country_essential_'+id+'">'+title+I('i-plus')+'</summary><p>'+E(ess[id]['answer'])+'</p><p class="country-checked">Проверено: '+E(ess[id]['checkedDate'])+'</p></details>'for id,title in QUESTIONS if id in ess))+'<div class="country-passport-link">'+L(path,'zagranpasport/index.html','Проверить срок действия загранпаспорта →','country_passport','text-link')+'</div>')
 from online import years_in_tourism,years_label
 years=years_in_tourism();review=c['review'];reviewhtml=''
 if review:reviewhtml='<blockquote class="country-review" '+ED(key+'.review',True)+'><p>'+E(review['text'])+'</p><cite>'+E(review['name'])+' · '+E(review['date'])+' · <a href="'+E(review['source'])+'" data-goal="country_review_source">Источник ↗</a></cite></blockquote>'
 body+='<section class="section country-section" id="inquiry" data-end-contact><div class="container country-end-grid"><div><h2 '+ED(key+'.inquiry.title')+'>Отдых '+E(c['cases']['in'])+'</h2><p class="country-section-intro">Для начала нам хватит примерных дат и того, кто едет</p><div class="country-trust">'+L(path,'o-nas/index.html#company',str(years)+' '+years_label(years)+' в туризме','country_trust_company')+L(path,'kak-my-rabotaem/index.html#support','Сопровождение в поездке','country_trust_support')+L(path,'o-nas/otzyvy/index.html','Отзывы клиентов','country_trust_reviews')+'</div>'+reviewhtml+'</div>'+form(c,path,'bottom')+'</div></section>'
 alternatives=''
 for a in c['alternatives']:
  other=next(v for v in D['countries']if v['slug']==a['country']);flight='Время перелёта уточняется'if a['flight'].startswith('[')else a['flight']+' из Москвы';season='Сезон уточняется'if a['season'].startswith('[')else a['season']
  alternatives+='<article class="country-card-panel" '+ED(key+'.alternatives.'+a['country'],True)+'>'+L(path,'napravleniya/'+other['slug']+'/index.html',photo(path,other['heroPhoto'],other['alt'],'countries.'+other['slug']+'.heroPhoto')+'<h3>'+E(other['name'])+'</h3>','country_alternative_'+other['slug'])+'<p>'+E(flight+' · '+season)+'</p></article>'
 body+=section(c,'alternatives','Другие страны','<div class="country-alternatives">'+alternatives+'</div>')
 C['emit'](path,c['h1']+' — Mango Travel',c['subtitle'],c['h1'],'',body,[('Страны','napravleniya/index.html'),(c['name'],None)],photo=(c['heroPhoto']or D['countries'][0]['heroPhoto'],c['name']),questions=[(title,ess[id]['answer'])for id,title in QUESTIONS if id in ess],cover_override=cover,contact_override='',raw=True,page_class='country-page',assets=['css/country.css','js/country.js'])
 c['_dialogs']=dialogs

def finish(path):
 p=C['SITE']/path;h=p.read_text();c=next((c for c in D['countries']if path=='napravleniya/'+c['slug']+'/index.html'),None)
 if c:
  config={k:v for k,v in c.items()if not k.startswith('_')};config['monthNames']=MONTHS
  h=h.replace('</body>',c['_dialogs']+'<script type="application/json" id="country-config">'+json.dumps(config,ensure_ascii=False).replace('<','\\u003c')+'</script></body>')
 p.write_text(h)
