"""Country schema 8 rendered as static HTML. Shared by all nine destinations."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,re
MONTHS=['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
SHORT=['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек']
QUESTIONS=[('visa','Нужна ли виза','entry'),('flight','Сколько лететь и какая разница во времени','flight'),('money','Какие деньги брать и как платить','money'),('connection','Как быть со связью и интернетом','connection'),('rules','Местные правила и привычки','rules'),('health','Здоровье и страховка','health')]
REMOVED=['tunis','greciya','kipr','bolgariya']

def configure(c):
 global C,D,E,I,U,L,ED
 C=c;D=c['DATA'];E=c['E'];I=c['icon'];U=c['url'];L=c['link'];ED=c['editable']
 previous=c['dropdown']
 def dropdown(path,label,kind):
  if kind!='countries':return previous(path,label,kind)
  items=L(path,'napravleniya/index.html','Все страны →','nav_countries_all','country-menu-all')+c['navitems'](path,'countries')
  return '<div class="nav-dropdown nav-compact"><button type="button" data-nav-toggle aria-expanded="false" aria-controls="nav-countries" data-goal="nav_countries_toggle" disabled>Страны'+I('i-down')+'</button><div class="dropdown-panel" id="nav-countries" hidden><div class="dropdown-grid">'+items+'</div></div></div>'
 c['dropdown']=dropdown
 write_checklist()
 assert hashlib.sha256((c['ROOT']/'mango-country-page.html').read_bytes()).hexdigest()==D['country_source_sha256'],'Country source changed: update the approved data first'
 for slug in REMOVED:
  for p in(c['SITE']/'napravleniya'/slug).glob('*.html'):p.unlink()

def write_checklist():
 p=C['SITE']/'CHECKLIST.md';before=p.read_text().replace('# Перед публикацией · этап 4','# Перед публикацией · этапы 4–5')
 lines=['<!-- build:stage5-countries -->','## Этап 5 · что требуется по странам','', 'Все описания курортов, климат, отели, справка и рекомендации предварительные и помечены `data-needs-approval`. Источник Египта — редакция 8 схемы, а не проверенная туристическая справка. Даты проверки не придуманы.','']
 for c in D['countries']:
  lines += ['### '+c['name'], '', '- Курорты: '+', '.join(r['name']for r in c['resorts'])+'. Нужны утверждённые описания, особенности пляжа, атмосфера, дорога и ограничения; фотографии курортов.', '- Первый экран: '+('нужна фотография страны.'if not c['heroPhoto']else'подтвердить иллюстрацию и вступление; фото уже имеет запись об источнике и лицензии.'), '- Климат: '+('Хургада и Шарм-эль-Шейх — сверить массивы из схемы; для Марса-Алама и Эль-Гуны нужны температуры.'if c['slug']=='egipet'else'нужны 12 значений воздуха и воды по каждому курорту.')+' Для всех курортов нужны ветер/осадки и месячные подсказки.', '- Отели: подтвердить три настоящих отеля, курорт, фотографии, кому подходят, чем хороши и что учесть. Сейчас Отель 1–3 и «Уточняется».', '- Важно знать: шесть ответов (виза, перелёт/время, деньги, связь, правила, здоровье) и дата проверки каждого.', '- Отзыв: нужен реальный согласованный отзыв с автором, датой и источником. Пока отсутствует и не выводится.', '- Другие страны: '+', '.join(next(v['name']for v in D['countries']if v['slug']==a['country'])for a in c['alternatives'])+'. Нужны причины для каждого месяца и двух форматов; пока показаны вступления соответствующих стран.', '- '+('[Открыть страницу](napravleniya/'+c['slug']+'/index.html)'), '']
 lines += ['Существующий каталог предложений не переписывался. Проверьте согласованность названия курорта в египетском предложении с редакцией 8; даты, цена, питание и наличие по-прежнему требуют подтверждения.', '<!-- /build:stage5-countries -->']
 block='\n'.join(lines)
 if '<!-- build:stage5-countries -->'in before:before=re.sub(r'<!-- build:stage5-countries -->.*?<!-- /build:stage5-countries -->',lambda m:block,before,flags=re.S)
 else:before=before.rstrip()+'\n\n'+block+'\n'
 p.write_text(before)

def photo(path,name,alt,key,lazy=True):
 if name:return C['image'](path,name,alt,lazy,key=key).replace(' data-editable=', ' data-needs-approval="country-photo" data-editable=')
 return '<div class="country-photo-placeholder" role="img" aria-label="'+E(alt)+'" '+ED(key,True)+'>'+I('i-mood-horizon')+'<span>'+E(alt)+'</span></div>'
def button(label,kind='country',topic='',message='',key='country_request',cls='btn btn-primary'):
 return f'<button type="button" class="{cls}" data-country-request="{E(kind)}" data-country-topic="{E(topic)}" data-country-message="{E(message)}" data-goal="{key}" {ED(key+".label")}>{E(label)}</button>'
def context(c,kind='country',item=None):
 if kind=='resort':return item['name'],'Здравствуйте! Хочу обсудить отдых. Курорт — '+item['name']+'.'
 if kind=='hotel':
  resort=next(r['name']for r in c['resorts']if r['id']==item['resort']);return item['name']+' · '+resort,'Здравствуйте! Хочу уточнить цену на мои даты. '+item['name']+', '+resort+'.'
 if kind=='route':return item['name'],'Здравствуйте! Хочу обсудить маршрут по '+c['cases']['through']+'. '+item['name']+'.'
 if kind=='offer':
  from stage4 import offer_topic
  return offer_topic(item),'Здравствуйте! Интересует предложение '+item['hotel']+', '+item['resort']+', '+C['human_date'](item['departure_date'])+', '+item['departure_city']+'.'
 if kind=='price':return c['name']+' · цена на Ваши даты','Здравствуйте! Хочу уточнить цену поездки '+c['cases']['to']+' на мои даты.'
 return c['name'],'Здравствуйте! Хочу поехать '+c['cases']['to']+'.'
def action(c,label,kind='country',item=None,key='country_request',cls='btn btn-primary'):
 topic,message=context(c,kind,item);return button(label,kind,topic,message,key,cls)
def channels(c,key):
 from stage4 import channels as common
 return common(context(c)[1],key)
def form(c,path,place):
 key='countries.'+c['slug']+'.forms.'+place;topic,message=context(c)
 return f'''<!-- component: discussion-form --><div class="country-inquiry" data-country-inquiry="{place}" {ED(key)}><h3 {ED(key+'.title')}>Поможем выбрать отдых {E(c['cases']['in'])}</h3><p class="country-form-context" data-country-context {ED(key+'.context')}>{E(c['name'])}</p><p class="country-viewed-month" data-viewed-month hidden></p><form data-local-form data-country-form novalidate><fieldset data-form-guard disabled><legend class="sr-only">Ваши планы</legend><input type="hidden" name="topic" value="{E(topic)}"><div class="country-form-grid"><label class="field-label"><span>Когда планируете</span><select name="month" data-goal="country_form_month"><option value="">Пока не определились</option>'''+''.join(f'<option value="{i}">{m}</option>'for i,m in enumerate(MONTHS,1))+'''</select></label><label class="field-label"><span>Город вылета</span><input name="city" placeholder="Ваш город" maxlength="80"></label><label class="field-label"><span>Кто едет</span><select name="travelers" data-goal="country_form_travelers"><option value="">Выберите состав</option><option>Один взрослый</option><option>Двое взрослых</option><option>С детьми</option><option>Другой состав</option></select></label><label class="field-label"><span>Телефон</span><input name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" maxlength="18" required></label><label class="field-label country-form-wide" data-extra-travelers hidden><span>Количество взрослых и возраст детей, если едут</span><input name="ages" maxlength="160" disabled></label></div><details class="country-optional"><summary data-goal="country_form_optional">Даты и пожелания, по желанию</summary><label class="field-label"><span>Даты поездки</span><input name="dates" placeholder="Примерный диапазон" maxlength="120"></label><label class="field-label"><span>Бюджет на всю поездку</span><input name="budget" placeholder="Сумма или диапазон" maxlength="80"></label></details><div class="country-consent">'''+f'<label class="consent"><input name="consent" type="checkbox" required><span><a href="{U(path,"o-nas/dokumenty/soglasie/index.html")}" data-goal="country_consent_{place}">Согласие на обработку персональных данных</a></span></label>'+L(path,'o-nas/dokumenty/politika/index.html','Политика','country_policy_'+place)+f'''</div><p class="form-error" data-local-error role="alert"></p><button type="submit" class="btn btn-primary" data-goal="country_submit_{place}">Получить варианты</button></fieldset></form><div class="form-success" data-local-success role="status" tabindex="-1" hidden><p>Спасибо, менеджер свяжется с Вами</p></div><p class="channel-caption">Написать в мессенджере:</p>{channels(c,'country_'+place)}<noscript><p>Позвоните: <a href="tel:+78512299547" data-goal="country_nojs_{place}">+7 (8512) 29-95-47</a></p></noscript></div><!-- /component: discussion-form -->'''

def section(c,id,title,body):return f'<section class="section country-section" id="{id}"><div class="container"><div class="section-head"><h2 {ED("countries."+c["slug"]+"."+id+".title")}>{E(title)}</h2></div>{body}</div></section>'
def temp(v):return '—'if v is None else ('+'if v>=0 else'')+str(v)+' °C'
def climate(c):
 month=datetime.now(ZoneInfo('Europe/Moscow')).month;first=c['resorts'][0];key='countries.'+c['slug']+'.climate'
 select='<label class="field-label country-select"><span>'+c['resortLabel']+'</span><select data-weather-resort data-goal="weather_resort">'+''.join('<option value="'+r['id']+'">'+E(r['name'])+'</option>'for r in c['resorts'])+'</select></label>'
 buttons='<div class="country-months" aria-label="Выбор месяца">'+''.join(f'<button type="button" data-weather-month="{i}" aria-label="{m}" aria-pressed="{str(i==month).lower()}" data-goal="weather_month_{i}">{SHORT[i-1]}</button>'for i,m in enumerate(MONTHS,1))+'</div>'
 result='<div class="country-weather-result" aria-live="polite"><p data-weather-label>'+E(first['name'])+' · '+MONTHS[month-1]+' · средние значения</p><div class="country-temperature"><p><strong data-weather-air>'+temp(first['air'][month-1])+'</strong><span>Воздух днём</span></p><p><strong data-weather-water>'+temp(first['water'][month-1])+'</strong><span>Вода</span></p></div><p data-weather-note>'+E(first['monthNotes'][month-1])+'</p></div>'
 tables=''.join('<div data-weather-table="'+r['id']+'"'+(' hidden'if j else'')+'><table><caption>'+E(r['name'])+' · средние значения</caption><thead><tr><th scope="col">Месяц</th><th scope="col">Воздух</th><th scope="col">Вода</th><th scope="col">Ветер и осадки</th></tr></thead><tbody>'+''.join('<tr><th scope="row">'+m+'</th><td>'+temp(r['air'][i])+'</td><td>'+temp(r['water'][i])+'</td><td>'+E(r['windRain'][i]or'—')+'</td></tr>'for i,m in enumerate(MONTHS))+'</tbody></table></div>'for j,r in enumerate(c['resorts']))
 return section(c,'season','Когда ехать','<div class="country-weather" '+ED(key,True)+'>'+select+buttons+result+'<details class="country-weather-table"><summary data-goal="weather_table">Таблица по месяцам</summary><div class="table-scroll">'+tables+'</div></details></div>')

def resorts(c,path):
 cards='';key='countries.'+c['slug']
 for i,r in enumerate(c['resorts']):
  facts=''.join('<div><dt>'+label+'</dt><dd>'+E(r[field])+'</dd></div>'for field,label in [('beach','Пляж и вход в море'),('atmosphere','Атмосфера'),('transfer','Дорога'),('feature','Что учесть')])
  cards+=f'<article class="country-resort country-card-panel" data-resort-card="{r["id"]}"'+(' data-extra-resort hidden'if i>=3 else'')+' '+ED(key+'.resorts.'+r['id'],True)+'><details><summary data-goal="resort_expand_'+r['id']+'">'+photo(path,r['photo'],'Фото курорта '+r['name'],key+'.resorts.'+r['id']+'.photo')+'<span>'+E(r['name'])+I('i-plus')+'</span></summary><div class="country-card-body"><dl class="country-resort-facts">'+facts+'</dl><div class="country-card-links"><a href="#hotels" data-resort-hotels="'+r['id']+'" data-goal="resort_hotels_'+r['id']+'">Посмотреть отели</a><a href="#season" data-resort-weather="'+r['id']+'" data-goal="resort_weather_'+r['id']+'">Когда ехать</a></div></div></details><div class="country-card-body"><p>'+E(r['short'])+'</p>'+action(c,'Подобрать отдых здесь','resort',r,'resort_request_'+r['id'],'text-link')+'</div></article>'
 toggles='<div class="country-format" role="group" aria-label="Формат отдыха"><button type="button" data-country-format="beach" aria-pressed="true" data-goal="country_format_beach">'+('Атоллы'if c['resortLabel']=='Атолл'else'Курорты')+'</button><button type="button" data-country-format="routes" aria-pressed="false" data-goal="country_format_routes">Города и маршруты</button></div>'if c['routes']else''
 more='<button class="rest-pill rest-pill-outline" type="button" data-more-resorts aria-expanded="false" aria-controls="country-resort-grid" data-goal="resorts_more">Все курорты</button>'if len(c['resorts'])>3 else''
 routes='<div class="country-grid" data-country-panel="routes" hidden>'+''.join('<article class="country-card-panel" '+ED(key+'.routes.'+r['id'],True)+'>'+photo(path,r['photo'],'Фото маршрута '+r['name'],key+'.routes.'+r['id']+'.photo')+'<div class="country-card-body"><h3>'+E(r['name'])+'</h3><p>'+E(r['stops'])+'</p><p>'+E(r['pace'])+'</p>'+action(c,'Обсудить маршрут','route',r,'route_request_'+r['id'],'text-link')+'</div></article>'for r in c['routes'])+'</div>'if c['routes']else''
 return section(c,'resorts','Где отдыхать',toggles+'<div data-country-panel="beach"><div class="country-grid" id="country-resort-grid">'+cards+'</div>'+more+'</div>'+routes)

def offers(c,path):
 rows=C['active_offers'](c['slug'])if c['showOffers']else[]
 if not rows:return ''
 cards=''
 for i,o in enumerate(rows):
  target='predlozheniya/'+o['id']+'/index.html';key='offers.'+o['id'];price=f'{o["price_from"]:,}'.replace(',',' ')
  cards+='<article class="country-offer"'+(' data-extra-country-offer'if i>=3 else'')+' '+ED(key,True)+'>'+L(path,target,C['image'](path,o['photo'],o['hotel'],key=key+'.photo'),'country_offer_photo_'+o['id'],'country-offer-photo')+'<div class="country-offer-body"><h3>'+L(path,target,E(o['hotel']),'country_offer_detail_'+o['id'])+'</h3><p>'+E(o['resort'])+f' · {o["nights"]} ночей</p><p>'+C['human_date'](o['departure_date'])+' · '+E(o['departure_city'])+'</p><p>'+E(o['meals'])+'</p><p class="country-offer-price">от '+price+' ₽</p><p class="country-price-date">За 2 взрослых · на '+C['human_date'](o['price_date'])+'</p>'+action(c,'Уточнить тур','offer',o,'country_offer_request_'+o['id'],'text-link')+'</div></article>'
 count=len(rows)-3;word='предложение'if count%10==1 and count%100!=11 else'предложения'if count%10 in[2,3,4]and count%100 not in[12,13,14]else'предложений'
 more=f'<button class="rest-pill rest-pill-outline country-more-offers" data-more-label="Ещё {count} {word}" data-more-country-offers aria-expanded="false" aria-controls="country-offer-grid" data-goal="country_offers_more">Ещё {count} {word}</button>'if len(rows)>3 else''
 return section(c,'offers','Актуальные предложения','<div class="country-grid" id="country-offer-grid">'+cards+'</div>'+more)

def hotelcopy(h):return ''.join('<p><strong>'+label+'</strong> '+E(h[key])+'</p>'for key,label in [('fit','Кому рекомендуем'),('good','Чем хорош'),('note','Что учесть')])
def hotels(c,path):
 key='countries.'+c['slug'];cards='';dialogs=''
 for h in c['hotels']:
  r=next(r for r in c['resorts']if r['id']==h['resort']);ph=h['photos'][0]if h['photos']else None
  visual=photo(path,ph,'Фото '+h['name'],key+'.hotels.'+h['id']+'.photos')
  trigger='<button type="button" class="country-hotel-open" data-country-hotel="'+h['id']+'" data-goal="hotel_open_'+h['id']+'">'+visual+'<span>'+E(h['name'])+'</span></button>'
  cards+='<article class="country-card-panel" data-hotel-card="'+r['id']+'" '+ED(key+'.hotels.'+h['id'],True)+'>'+trigger+'<div class="country-card-body"><p class="country-hotel-resort">'+E(r['name'])+'</p>'+hotelcopy(h)+action(c,'Узнать цену на мои даты','hotel',h,'hotel_request_'+h['id'],'text-link')+'</div></article>'
  gallery=''.join(photo(path,p,'Фото '+h['name'],key+'.hotels.'+h['id']+'.photos.'+str(i))for i,p in enumerate(h['photos']))if h['photos']else visual
  dialogs+='<dialog class="country-hotel-dialog" id="'+h['id']+'-dialog" aria-modal="true" aria-labelledby="'+h['id']+'-title" '+ED(key+'.hotels.'+h['id'],True)+'><div class="dialog-top"><h2 id="'+h['id']+'-title">'+E(h['name'])+'</h2><button type="button" class="icon-btn" data-dialog-close data-goal="hotel_close_'+h['id']+'" aria-label="Закрыть отель">'+I('i-close')+'</button></div><div class="country-hotel-photos">'+gallery+'</div><p>'+E(r['name'])+'</p>'+hotelcopy(h)+action(c,'Узнать цену на мои даты','hotel',h,'hotel_dialog_request_'+h['id'])+'</dialog>'
 empty='<div class="country-hotel-empty" data-hotel-empty hidden><h3>Подберём отель для Вашей поездки.</h3>'+action(c,'Обсудить отели курорта',key='hotel_empty_request')+'</div>'
 select='<label class="field-label country-select"><span>'+c['resortLabel']+'</span><select data-hotel-filter data-goal="country_hotel_filter"><option value="">Все курорты</option>'+''.join('<option value="'+r['id']+'">'+E(r['name'])+'</option>'for r in c['resorts'])+'</select></label>'
 return section(c,'hotels','Отели '+c['cases']['in'],'<p class="country-section-intro" '+ED(key+'.hotelsIntro',True)+'>'+E(c['hotelsIntro'])+'</p>'+select+'<div class="country-grid country-hotel-grid">'+cards+'</div>'+empty),dialogs

def country(c):
 path='napravleniya/'+c['slug']+'/index.html';key='countries.'+c['slug'];topic,message=context(c);hasoffers=c['showOffers']and bool(C['active_offers'](c['slug']))
 cover='<section class="country-hero" data-inner-cover>'+photo(path,c['heroPhoto'],c['alt'],key+'.heroPhoto',False)+'<div class="container">'+C['crumb'](path,[('Страны','napravleniya/index.html'),(c['name'],None)])+'<div class="country-hero-grid"><div class="country-hero-copy"><p class="hero-accent" '+ED(key+'.name')+'>'+E(c['name'])+'</p><h1 '+ED(key+'.h1')+'>'+E(c['h1'])+'</h1><p class="country-subtitle" '+ED(key+'.subtitle',True)+'>'+E(c['subtitle'])+'</p><div class="country-hero-facts"><a href="#season" data-goal="country_season">Сезон по курортам</a><a href="#flight" data-open-essential data-goal="country_flight">Перелёт из Вашего города</a><a href="#entry" data-open-essential data-goal="country_entry">Правила въезда</a></div><div class="country-mobile-hero">'+action(c,'Подобрать тур')+channels(c,'country_hero')+'</div></div><div class="country-hero-form">'+form(c,path,'top')+'</div></div></div></section>'
 nav=[('season','Когда ехать'),('resorts','Курорты')]+([('offers','Предложения')]if hasoffers else[])+[('hotels','Отели'),('experiences','Чем заняться'),('essentials','Важно знать')]
 body='<nav class="country-page-nav" aria-label="На странице"><div class="container">'+''.join('<a href="#'+id+'" data-country-anchor data-goal="country_anchor_'+id+'">'+title+'</a>'for id,title in nav)+'</div></nav>'+climate(c)+resorts(c,path)+offers(c,path)
 body+='<div class="container"><div class="country-price-strip" id="price-strip"><div><h3>Другие даты или город вылета</h3><p>Менеджер уточнит стоимость под Ваши условия.</p></div>'+action(c,'Узнать цену на мои даты','price',key='country_price_request')+'</div></div>'
 hotelbody,dialogs=hotels(c,path);body+=hotelbody
 body+=section(c,'experiences','Чем заняться','<div class="country-grid">'+''.join('<article class="info-card" '+ED(key+'.experiences.'+str(i),True)+'><span class="eyebrow">0'+str(i+1)+'</span><h3>'+E(x['title'])+'</h3><p>'+E(x['text'])+'</p>'+(action(c,'Обсудить маршрут','route',{'name':'Свой маршрут'},'country_custom_route','text-link')if i==2 else'')+'</article>'for i,x in enumerate(c['experiences']))+'</div>')
 body+=section(c,'essentials','Что важно знать до поездки','<div class="faq-list">'+''.join('<details class="faq-item" id="'+id+'" '+ED(key+'.essentials.'+field,True)+'><summary data-goal="country_essential_'+field+'">'+title+I('i-plus')+'</summary><p>'+E(c['essentials'][field]['answer'])+'</p><p class="country-checked" '+ED(key+'.essentials.'+field+'.checkedDate',True)+'>Проверено · '+E(c['essentials'][field]['checkedDate']or'[дата]')+'</p></details>'for field,title,id in QUESTIONS)+'</div>')
 from online import years_in_tourism,years_label
 years=years_in_tourism();review=c['review'];reviewhtml=''
 if review:reviewhtml='<blockquote class="country-review" '+ED(key+'.review',True)+'><p>'+E(review['text'])+'</p><cite>'+E(review['name'])+' · '+E(review['date'])+' · <a href="'+E(review['source'])+'" data-goal="country_review_source">Источник ↗</a></cite></blockquote>'
 body+='<section class="section country-section" id="inquiry" data-end-contact><div class="container country-end-grid"><div><h2 '+ED(key+'.inquiry.title')+'>Обсудим Вашу поездку '+E(c['cases']['to'])+'</h2><p class="country-section-intro">Расскажите о планах. Уточним пожелания и предложим подходящие варианты.</p><div class="country-trust">'+L(path,'o-nas/index.html#company',str(years)+' '+years_label(years)+' в туризме','country_trust_company')+L(path,'kak-my-rabotaem/index.html#support','Сопровождение в поездке','country_trust_support')+L(path,'o-nas/otzyvy/index.html','Отзывы клиентов','country_trust_reviews')+'</div>'+reviewhtml+'</div>'+form(c,path,'bottom')+'</div></section>'
 alternatives=''
 for a in c['alternatives']:
  if not next(v for v in D['countries']if v['slug']==a['country']).get('published',True):continue
  other=next(v for v in D['countries']if v['slug']==a['country']);alternatives+='<article class="country-card-panel" '+ED(key+'.alternatives.'+a['country'],True)+'>'+L(path,'napravleniya/'+other['slug']+'/index.html',photo(path,other['heroPhoto'],other['alt'],'countries.'+other['slug']+'.heroPhoto')+'<h3>'+E(other['name'])+'</h3>','country_alternative_'+other['slug'])+'<p data-alternative-reason="'+other['slug']+'">'+E(other['subtitle'])+'</p></article>'
 body+=section(c,'alternatives','Другие страны','<p class="country-section-intro" data-alternatives-context>'+MONTHS[datetime.now(ZoneInfo('Europe/Moscow')).month-1]+' · отдых у моря</p><div class="country-alternatives">'+alternatives+'</div>')
 C['emit'](path,c['h1']+' — Mango Travel',c['subtitle'],c['h1'],'',body,[('Страны','napravleniya/index.html'),(c['name'],None)],photo=(c['heroPhoto']or D['countries'][0]['heroPhoto'],c['name']),questions=[(title,c['essentials'][field]['answer'])for field,title,id in QUESTIONS],cover_override=cover,contact_override='',raw=True,page_class='country-page',assets=['css/country.css','js/country.js'])
 c['_dialogs']=dialogs

def index():
 path='napravleniya/index.html';cards=''.join('<article class="country-index-card" '+ED('countries.'+c['slug']+'.card',True)+'>'+L(path,'napravleniya/'+c['slug']+'/index.html',photo(path,c['heroPhoto'],c['alt'],'countries.'+c['slug']+'.heroPhoto')+'<div><h2>'+E(c['name'])+'</h2><span>Перейти к стране →</span></div>','country_index_'+c['slug'])+'</article>'for c in D['countries'])
 C['emit'](path,'Страны — Mango Travel','Выберите страну, чтобы узнать о сезоне, курортах и особенностях поездки.','Страны','Выберите страну, чтобы узнать о сезоне, курортах и особенностях поездки.',C['section']('','<div class="country-index-grid">'+cards+'</div>'),[('Страны',None)],raw=True,assets=['css/country.css'])

def finish(path):
 p=C['SITE']/path;h=p.read_text();c=next((c for c in D['countries']if path=='napravleniya/'+c['slug']+'/index.html'),None)
 if c:
  dialog='<dialog class="request-dialog country-request-dialog" id="request-dialog" aria-modal="true" aria-labelledby="request-title"><div class="dialog-top"><h2 id="request-title">Обсудим Вашу поездку</h2><button class="icon-btn" type="button" data-dialog-close data-goal="country_request_close" aria-label="Закрыть обращение">'+I('i-close')+'</button></div>'+form(c,path,'dialog')+'</dialog>'
  h=re.sub(r'<dialog class="request-dialog".*?</dialog>',lambda _:dialog,h,flags=re.S)
  panel='<div class="mobile-contact country-mobile-panel" data-mobile-contact hidden>'+action(c,'Подобрать тур',key='country_mobile_request')+channels(c,'country_mobile')+'</div>'
  h=re.sub(r'<div class="mobile-contact".*?</div>',lambda _:panel,h,flags=re.S)
  config={k:v for k,v in c.items()if not k.startswith('_')};config['alternativeSubtitles']={x['slug']:x['subtitle']for x in D['countries']};config['monthNames']=MONTHS
  h=h.replace('</body>',c['_dialogs']+'<script type="application/json" id="country-config">'+json.dumps(config,ensure_ascii=False).replace('<','\\u003c')+'</script></body>')
 if path.startswith('predlozheniya/')and path.count('/')==2:
  offer=next((o for o in D['offers']if path=='predlozheniya/'+o['id']+'/index.html'),None)
  if offer:
   target=next(v for v in D['countries']if v['slug']==offer['country'])
   if target['showOffers']and C['active_offers'](target['slug']):h=h.replace('← Все предложения</a>','← Все предложения</a>'+L(path,'napravleniya/'+target['slug']+'/index.html#offers','← К предложениям '+target['cases']['of'],'offer_country_back','text-link offer-country-back'))
 p.write_text(h)
