"""Schema 12.11 revision 2. Shared static forms and chrome; no client HTML generation."""
from datetime import datetime,date
from zoneinfo import ZoneInfo
import json,re,hashlib
import stage4 as old
import country as country_module
MONTHS=country_module.MONTHS
HIDDEN=['topic','page','utm_source','utm_medium','utm_campaign','utm_content','utm_term']
TITLES={'pick':'Расскажите о поездке','offer':'Уточнить цену и наличие','service':'Расскажите, чем помочь'}
SUCCESS='Спасибо за обращение! Менеджер свяжется с Вами по указанному номеру.'
SERVICE_OLD={'paketnye-tury':'packages','individualnye-tury':'custom','ekskursionnye-tury':'tours','kruizy':'cruises','oteli':'hotels','aviabilety':'tickets','zhd-bilety':'tickets','avtobusnye-bilety':'tickets','transfery':'transfer','strahovanie':'insurance','vip-zaly':'airport','fast-track':'airport','vizy':'visas'}

def now():return datetime.now(ZoneInfo('Europe/Moscow')).date()
def configure(c):
 global C,D,E,I,U,L,ED,S
 C=c;D=c['DATA'];E=c['E'];I=c['icon'];U=c['url'];L=c['link'];ED=c['editable'];S=c['section']
 assert hashlib.sha256((C['ROOT']/'mango-structure-12-11-v2.html').read_bytes()).hexdigest()==D['schema6_sha256'],'Approved revision 2 changed'
 D['countries'].sort(key=lambda x:x['name']);c['COUNTRIES']=[x for x in D['countries']if x['published']]
 for item in D['countries']:
  if not item['published']:(C['SITE']/('napravleniya/'+item['slug']+'/index.html')).unlink(missing_ok=True)
 for root in ['uslugi','voprosy']:
  for p in(C['SITE']/root).rglob('*.html'):
   if root=='voprosy'or p.parent!=C['SITE']/root:p.unlink()
 for path in list(D['pages']):
  if path.startswith('predlozheniya/')and path!='predlozheniya/index.html':del D['pages'][path]
 c.update(header=header,footer=footer,contact=end_form,active_offers=active_offers,offer=offer_card)
 country_module.form=lambda c,path,place:form(path,'country:'+c['slug'],place,classes='country-inquiry',attrs='data-country-inquiry="'+place+'"')
 country_module.action=country_action;country_module.offers=country_offers
 old.active_offers=active_offers;old.offer_topic=offer_label

def published_countries():return [c for c in D['countries']if c['published']]
def active_offers(country=None,on=None):
 published={x['slug']for x in published_countries()};today=(on or now()).isoformat()
 return [o for o in D['offers']if o['published']and o['country']in published and o['showUntil']>=today and(country is None or o['country']==country)]
def kind(key):
 if key.startswith('offer:'):return 'offer'
 if key.startswith('service:'):return 'pick'if next(s for s in D['services']if s['id']==key.split(':')[1])['group']=='travel'else'service'
 return 'service'if key in['contact','passport']else'pick'
def page_topic(path):
 if path=='index.html':return 'home'
 if path.startswith('napravleniya/')and path!='napravleniya/index.html':return 'country:'+path.split('/')[1]
 if path=='otdyh/kruizy/index.html':return 'holiday:cruises'
 if path.startswith('otdyh/'):return 'holiday:'+path.split('/')[1]
 if path.startswith('predlozheniya/')and path!='predlozheniya/index.html':return 'offer:'+path.split('/')[1]
 if path.startswith('uslugi/'):return 'contact'
 if path=='o-nas/kontakty/index.html':return 'contact'
 if path.startswith('zagranpasport/'):return 'passport'
 return 'home'
def country_by(slug):return next(c for c in D['countries']if c['slug']==slug)
def offer_label(o):
 c=country_by(o['country']);return c['name']+' · '+o['resort']+' · '+o['hotel']+' · '+dates(o)+' · вылет из города '+o['departure_city']
def dates(o):return C['human_date'](o['departure_date'])+' — '+C['human_date'](o['return_date'])
def short_dates(o):
 a=date.fromisoformat(o['departure_date']);b=date.fromisoformat(o['return_date'])
 if(a.year,a.month)==(b.year,b.month):return str(a.day)+'–'+str(b.day)+' '+C['MONTH_NAMES'][a.month-1]+' '+str(a.year)
 return dates(o)
def holiday_key(name):return next((p['slug']for p in D['rest_pages']if p['accent']==name),next((c['slug']for c in D['home_rest']['cards']if c['label']==name),name))
def topic(key):
 bits=key.split(':');category=bits[0];identifier=bits[1]if len(bits)>1 else''
 if category=='slide':
  s=D['slides'][int(identifier)];return s['name'],s['msg']
 if category=='holiday':
  if identifier=='cruises'and len(bits)>3:
   p=D['cruise_page'];detail=p['types'][int(bits[3])]['title'];return p['accent']+' · '+detail,p['message']+'. '+detail
  p=next((p for p in D['rest_pages']if p['slug']==identifier),None)
  if p:
   title=p['accent'];extra=[]
   if len(bits)>3:
    if bits[2]=='type':extra=[p['types'][int(bits[3])]['title']]
    elif bits[2]=='country':extra=[next(c['name']for c in p['countries']if c['slug']==bits[3])]
    elif bits[2]=='hotel':
     c,h=next((c,h)for c in p['countries']for h in p['hotels'][c['slug']]if h['id']==bits[3]);extra=[c['name']]if p['mode']=='routes'else[c['name'],h['name']]
   return ' · '.join([title]+extra),p['message']+('. '+'. '.join([title]+extra)if extra else'')
  card=next((c for c in D['home_rest']['cards']if c['slug']==identifier),None);name=card['label']if card else identifier;h=next((h for h in D['schema6']['holidays']if h['name']==name),None);msg=h['msg']if h and not h['msg'].startswith('[')else'Здравствуйте! Интересует раздел «'+name+'»';return name,msg
 if category=='country':
  c=country_by(identifier);return c['name'],'Здравствуйте! Хочу поехать '+c['cases']['to']
 if category in['resort','hotel','route','price']:
  c=country_by(identifier);itemid=bits[2]if len(bits)>2 else''
  if category=='resort':
   r=next(r for r in c['resorts']if r['id']==itemid);phrase='в '+r['loc']if c['slug']=='egipet'or r.get('loc')!=r['name']else('на атолле «'if c['resortLabel']=='Атолл'else'на курорте «')+r['name']+'»';return c['name']+' · '+r['name'],'Здравствуйте! Интересует отдых '+phrase
  if category=='hotel':
   h=next(h for h in c['hotels']if h['id']==itemid);r=next(r for r in c['resorts']if r['id']==h['resort']);return h['name']+' · '+r['name'],'Здравствуйте! Интересует отель '+h['name']
  if category=='route':
   r=next((r for r in c['routes']if r['id']==itemid),{'name':'Свой маршрут'});return c['name']+' · '+r['name'],'Здравствуйте! Хочу обсудить маршрут по '+c['cases']['through']+'. '+r['name']+'.'
  return c['name']+' · цена на мои даты','Здравствуйте! Хочу узнать цену тура '+c['cases']['to']+' на мои даты'
 if category=='offer':
  o=next(o for o in D['offers']if o['id']==identifier);return offer_label(o),'Здравствуйте! Хочу уточнить цену и наличие тура. '+offer_label(o)
 if category=='service':
  s=next(x for x in D['services']if x['id']==identifier);return s['title'],'Здравствуйте! Интересует услуга: '+s['title']
 if key=='contact':return '','Здравствуйте! Хочу обратиться в Mango Travel'
 if key=='passport':return 'Срок действия загранпаспорта','Здравствуйте! Хочу уточнить требования к сроку действия загранпаспорта'
 return '','Здравствуйте! Хочу подобрать путешествие'
def action(label,key='home',goal='request',cls='btn btn-primary'):
 title,msg=topic(key);return f'<button type="button" class="{cls}" data-open-form="{E(key)}" data-goal="{goal}" {ED(goal+".label")}>{E(label)}</button>'
def channels(key,goal='message'):
 title,msg=topic(key);return '<div class="messenger-actions" data-channel-topic="'+E(key)+'">'+''.join('<a class="btn btn-outline" href="#" data-messenger="'+channel+'" data-topic-key="'+E(key)+'" data-goal="'+goal+'_'+channel.lower()+'" '+ED('contacts.'+('max'if channel=='MAX'else'telegramUsername'))+'>'+I('i-max'if channel=='MAX'else'i-telegram')+'<span>'+channel+'</span></a>'for channel in['MAX','Telegram'])+'</div>'
def month_options():
 t=now();return '<option value="">Пока не определились</option>'+''.join('<option value="'+str(t.year+(t.month-1+i)//12)+'-'+str((t.month-1+i)%12+1).zfill(2)+'">'+MONTHS[(t.month-1+i)%12]+' '+str(t.year+(t.month-1+i)//12)+'</option>'for i in range(24))
def field(label,control,cls=''):return '<label class="field-label '+cls+'"><span>'+label+'</span>'+control+'</label>'
def travel_fields(family=False,phone=""):
 return field('Месяц и год поездки','<select name="month" data-goal="form_month">'+month_options()+'</select>','form-month')+field('Город вылета','<input name="city" autocomplete="address-level2" maxlength="100">','form-city')+field('Кто едет','<select name="who" data-goal="form_who"><option value="">Выберите</option>'+''.join('<option'+(' selected'if family and label=='С детьми'else'')+'>'+label+'</option>'for label in['Один взрослый','Двое взрослых','С детьми','Другой состав'])+'</select>','form-travelers')+phone+'<label class="field-label form-wide" data-ages'+(''if family else' hidden')+'><span>Состав поездки и возраст детей</span><input name="ages" maxlength="160"'+(''if family else' disabled')+'></label>'
def consent(path,goal):return '<div class="unified-consent"><label class="consent"><input name="consent" type="checkbox" required><span>'+L(path,'o-nas/dokumenty/soglasie/index.html','Согласие на обработку персональных данных',goal+'_consent',extra='target="_blank" rel="noopener"')+'</span></label>'+L(path,'o-nas/dokumenty/politika/index.html','Политика',goal+'_policy',extra='target="_blank" rel="noopener"')+'</div>'
def form(path,key='home',place='end',mode=None,heading=True,classes='',attrs=''):
 mode=mode or kind(key);title,contextmsg=topic(key);family=key=='holiday:otdyh-s-detmi';goal='form_'+place+'_'+mode
 hidden=''.join('<input type="hidden" name="'+n+'" value="'+E(key if n=='topic'else path if n=='page'else'')+'">'for n in HIDDEN)
 phone=field('Телефон','<input name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" required maxlength="18">','form-phone')
 fields=phone if mode=='offer'else field('Что нужно организовать','<textarea name="task" rows="3" maxlength="1500"></textarea>','form-wide')+phone if mode=='service'else travel_fields(family,phone)
 optional='<details class="unified-options"><summary data-goal="'+goal+'_options">Изменить параметры тура</summary><div class="unified-grid">'+travel_fields()+field('Уточнения','<textarea name="task" rows="2" maxlength="1500"></textarea>','form-wide')+'</div></details>'if mode=='offer'else''if mode=='service'else'<details class="unified-options"><summary data-goal="'+goal+'_options">Даты и бюджет, по желанию</summary><div class="unified-grid">'+field('Даты поездки','<input name="dates" maxlength="100">')+field('Бюджет на всю поездку','<input name="budget" maxlength="100">')+'</div></details>'
 submit=TITLES['offer']if mode=='offer'else'Отправить обращение'if mode=='service'else'Получить варианты'
 return f'<!-- component: discussion-form --><div class="unified-card {classes}" data-unified-card {attrs} {ED(goal)}><h3 class="unified-title"'+(' hidden'if not heading else'')+'>'+TITLES[mode]+'</h3><p class="unified-context" data-form-context'+(' hidden'if not title else'')+'>'+E(title)+'</p><p class="unified-viewed" data-viewed-month hidden></p><form class="unified-form" data-unified-form data-mode="'+mode+'" data-topic="'+E(key)+'"'+(' data-end-form'if place in['end','bottom']else'')+' novalidate><fieldset data-form-guard disabled><legend class="sr-only">'+TITLES[mode]+'</legend>'+hidden+'<div class="unified-grid">'+fields+'</div>'+optional+consent(path,goal)+'<p class="form-error" data-form-error role="alert"></p><button type="submit" class="btn btn-primary" data-goal="'+goal+'_submit">'+submit+'</button></fieldset><p class="channel-caption">Или напишите в мессенджер</p>'+channels(key,goal)+'</form><div class="form-success" data-form-success role="status" tabindex="-1" hidden><p>'+SUCCESS+'</p></div><noscript><p><a href="tel:+78512299547" data-goal="'+goal+'_nojs">+7 (8512) 29-95-47</a></p></noscript></div><!-- /component: discussion-form -->'
def end_form(path,prefill=''):return '<section class="section" id="contact"><div class="container shared-end-form">'+form(path,page_topic(path))+'</div></section>'
def country_action(c,label,kind='country',item=None,key='country_request',cls='btn btn-primary'):
 typed='offer:'+item['id']if kind=='offer'else kind+':'+c['slug']+(':'+item['id']if item and 'id'in item and kind in['resort','hotel','route']else':custom'if kind=='route'else'')
 return action(label,typed,key,cls)
def service_link(path,s,goal):return L(path,'uslugi/index.html#'+s['id'],E(s['title']),goal+'_'+s['id'])
def menu_content(path,kind,mobile=False):
 if kind=='countries':return L(path,'napravleniya/index.html','Все страны →','menu_countries_all','menu-all')+'<div class="menu-country-columns">'+''.join(L(path,'napravleniya/'+c['slug']+'/index.html',E(c['name']),'menu_country_'+c['slug'])for c in published_countries())+'</div>'
 if kind=='services':return L(path,'uslugi/index.html','Все услуги →','menu_services_all','menu-all')+'<div class="menu-service-columns">'+''.join('<div><p class="dropdown-label">'+title+'</p>'+''.join(service_link(path,s,'menu_service')for s in D['services']if s['group']==group)+'</div>'for group,title in[('travel','Путешествия'),('extras','Для поездки')])+'</div>'
 items=[('О нас','o-nas/index.html'),('Отзывы','o-nas/otzyvy/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html')]
 return ''.join(L(path,target,label,'menu_about_'+str(i))for i,(label,target)in enumerate(items))
def dropdown(path,name,kind):return '<div class="nav-dropdown menu-'+kind+(' nav-compact'if kind=='about'else'')+'"><button type="button" data-nav-toggle aria-expanded="false" aria-controls="nav-'+kind+'" data-goal="nav_'+kind+'_toggle" disabled>'+name+I('i-down')+'</button><div class="dropdown-panel" id="nav-'+kind+'" hidden>'+menu_content(path,kind)+'</div></div>'
def header(path,photo=False):
 mobile=L(path,'index.html','Главная','mobile_home')+''.join('<details class="mobile-group"><summary data-goal="mobile_'+kind+'">'+label+I('i-down')+'</summary><div class="mobile-submenu">'+menu_content(path,kind,True)+'</div></details>'for label,kind in[('Страны','countries'),('Услуги','services')])+L(path,'predlozheniya/index.html','Актуальные предложения','mobile_offers')+L(path,'kak-my-rabotaem/index.html','Как мы работаем','mobile_work')+'<details class="mobile-group"><summary data-goal="mobile_about">О нас'+I('i-down')+'</summary><div class="mobile-submenu">'+menu_content(path,'about',True)+'</div></details>'+L(path,'o-nas/kontakty/index.html','Контакты','mobile_contacts')+'<div class="mobile-menu-contact"><a class="btn btn-primary" href="tel:+78512299547" data-goal="mobile_call">Позвонить</a>'+channels(page_topic(path),'mobile_menu')+'</div>'
 return '<!-- component: header --><header class="site-header d1-header'+(' is-solid'if not photo else'')+'" data-site-header><div class="header-inner"><nav class="nav-left" aria-label="Страны и услуги">'+dropdown(path,'Страны','countries')+dropdown(path,'Услуги','services')+'</nav>'+L(path,'index.html','<img class="logo-dark" src="'+C['brand_path'](path,'logo')+'" alt="Mango Travel" width="1193" height="440"><img class="logo-light" src="'+C['brand_path'](path,'light')+'" alt="" aria-hidden="true" width="1193" height="440">','home','brand','aria-label="Mango Travel — главная" data-editable="brand.logo"')+'<div class="header-right"><nav class="nav-about" aria-label="О компании">'+L(path,'kak-my-rabotaem/index.html','Как мы работаем','nav_work')+dropdown(path,'О нас','about')+'</nav><div class="header-contacts"><a class="header-phone icon-control" href="tel:+78512299547" aria-label="Позвонить: +7 (8512) 29-95-47" data-goal="header_phone">'+I('i-phone')+'<span>+7 (8512) 29-95-47</span></a>'+''.join('<a class="icon-control" href="#" data-messenger="'+ch+'" data-topic-key="'+E(page_topic(path))+'" aria-label="Написать в '+ch+'" data-goal="header_'+ch.lower()+'">'+I('i-max'if ch=='MAX'else'i-telegram')+'</a>'for ch in['MAX','Telegram'])+'<button type="button" class="icon-control menu-toggle" aria-controls="mobile-nav" aria-expanded="false" aria-label="Открыть меню" data-menu data-goal="menu_toggle" disabled>'+I('i-menu')+'<span>Меню</span></button></div></div></div><nav class="mobile-nav" id="mobile-nav" aria-label="Мобильное меню" hidden>'+mobile+'</nav><noscript><p class="nav-nojs">'+L(path,'napravleniya/index.html','Страны','nojs_countries')+' · '+L(path,'uslugi/index.html','Услуги','nojs_services')+'</p></noscript></header><!-- /component: header -->'
def holiday_link(path,card,goal):
 return L(path,card['target'],E(card['label']),goal)
def footer(path,home=False):
 company=[('Как мы работаем','kak-my-rabotaem/index.html'),('О нас','o-nas/index.html'),('Отзывы','o-nas/otzyvy/index.html'),('Вопросы','index.html#home-faq'),('Актуальные предложения','predlozheniya/index.html'),('Проверить срок действия загранпаспорта','zagranpasport/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html')]
 contacts='<div><h2>Контакты</h2><div class="footer-contacts" data-editable="contacts.footer"><a href="tel:+78512299547" data-goal="phone_footer">+7 (8512) 29-95-47</a><a href="tel:+78512299527" data-goal="phone_footer_secondary">+7 (8512) 29-95-27</a><a href="mailto:man.go.travel@mail.ru" data-goal="email_footer">man.go.travel@mail.ru</a></div><div class="footer-channels">'+''.join('<a href="'+E(D['contacts'][key])+'" data-goal="footer_channel_'+name+'" '+ED('contacts.'+key)+'>Канал в '+label+'</a>'for name,label,key in[('max','MAX','maxChannel'),('telegram','Telegram','telegramChannel')])+'</div></div>'
 return '<!-- component: footer --><footer class="site-footer"><div class="container"><div class="footer-grid footer-six"><div>'+L(path,'index.html','<img src="'+C['brand_path'](path,'light')+'" alt="Mango Travel" width="1193" height="440" loading="lazy">','footer_home','brand','aria-label="Mango Travel — главная" data-editable="brand.wordmark"')+'</div><nav aria-label="Страны"><h2>Страны</h2>'+''.join(L(path,'napravleniya/'+c['slug']+'/index.html',E(c['name']),'footer_country_'+c['slug'])for c in published_countries())+'</nav><nav aria-label="Отдых"><h2>Отдых</h2>'+''.join(holiday_link(path,c,'footer_holiday_'+c.get('goal_slug',c['slug']))for c in D['home_rest']['cards'])+'</nav><nav aria-label="Компания"><h2>Компания</h2>'+''.join(L(path,target,label,'footer_company_'+str(i))for i,(label,target)in enumerate(company))+'</nav>'+contacts+'</div><div class="footer-bottom"><span>© 2026 Mango Travel</span></div></div></footer><!-- /component: footer -->'

def offer_card(path,o):
 c=country_by(o['country']);key='offers.'+o['id'];price=f'{o["price_from"]:,}'.replace(',',' ');content=C['image'](path,o['photo'],o['hotel'],key=key+'.photo')+'<div class="ticket-body"><p class="ticket-dates">'+short_dates(o)+' · '+E(o['departure_city'])+'</p><h3>'+E(o['hotel'])+'</h3><p>'+E(c['name'])+' · '+E(o['resort'])+'</p><p>'+E(o['meals'])+f' · {o["nights"]} ночей</p><p class="ticket-price"><span class="ticket-price-value">от '+price+' ₽</span><small>за двоих</small></p><p class="ticket-price-date">Цена на '+C['human_date'](o['price_date'])+'</p><span class="ticket-link">Условия тура →</span></div>'
 return '<!-- component: offer-card --><article class="offer-card ticket-vertical" data-offer-id="'+o['id']+'" data-country="'+o['country']+'" data-price="'+str(o['price_from'])+'" data-date="'+o['departure_date']+'" '+ED(key,True)+'>'+L(path,'predlozheniya/'+o['id']+'/index.html',content,'offer_open_'+o['id'],'ticket-link-cover','data-track-offer="'+o['id']+'"')+'</article><!-- /component: offer-card -->'
def country_offers(c,path):
 rows=active_offers(c['slug'])[:4]if c['showOffers']else[]
 return country_module.section(c,'offers','Актуальные предложения','<div class="tickets-grid">'+''.join(offer_card(path,o)for o in rows)+'</div>')if rows else''
def country_summary(c):return (c.get('flightSummary')+' из Москвы'if c.get('flightSummary')else'Время перелёта уточняется')+' · '+(c.get('seasonSummary')or'Сезон уточняется')
def country_tile(path,c,heading='h3'):
 return '<!-- component: direction-card --><article class="country-index-card" '+ED('countries.'+c['slug']+'.card',True)+'>'+L(path,'napravleniya/'+c['slug']+'/index.html',country_module.photo(path,c['heroPhoto'],c['alt'],'countries.'+c['slug']+'.heroPhoto')+'<div><'+heading+'>'+E(c['name'])+'</'+heading+'><p class="country-flight-season" '+ED('countries.'+c['slug']+'.summary',True)+'>'+E(country_summary(c))+'</p><span>Перейти к стране →</span></div>','country_'+c['slug'])+'</article><!-- /component: direction-card -->'
def countries_index():
 path='napravleniya/index.html';C['emit'](path,'Страны — Mango Travel','Выберите страну, чтобы узнать о сезоне, курортах и особенностях поездки.','Страны','Выберите страну, чтобы узнать о сезоне, курортах и особенностях поездки.',S('','<div class="country-index-grid">'+''.join(country_tile(path,c,'h2')for c in published_countries())+'</div>'),[('Страны',None)],raw=True,assets=['css/country.css'])
def hero():
 slides=old.visible_slides();cards=''
 for i,s in enumerate(slides):
  tag='h1'if i==0 else'h2';key='slides.'+s['id'];cards+='<article class="hero-slide'+(' is-active'if i==0 else'')+'" data-slide-name="'+E(s['name'])+'" aria-hidden="'+str(i!=0).lower()+'"'+(' inert'if i else'')+'>'+C['image']('index.html',s['photo'],s['alt'],False,key=key+'.photo')+'<div class="hero-copy"><p class="hero-accent" '+ED(key+'.accent',i==1)+'>'+E(s['accent'])+'</p><'+tag+' '+ED(key+'.title')+'>'+E(s['title'])+'</'+tag+'><p '+ED(key+'.description')+'>'+E(s['description'])+'</p>'+action(s['button'],s['topic'],'hero_'+s['id']).replace('data-open-form=','data-hero-cta data-open-form=')+'</div></article>'
 from online import years_in_tourism,years_label
 years=years_in_tourism();return '<!-- component: hero --><section class="hero-shell" data-hero data-inner-cover data-home-block="01"><div class="hero-slides">'+cards+'</div><div class="hero-controls"><button class="icon-btn" type="button" data-hero-prev data-goal="hero_previous" aria-label="Предыдущий слайд">'+I('i-arrow-left')+'</button><span><span data-hero-count>1</span> / '+str(len(slides))+'</span><button class="icon-btn" type="button" data-hero-next data-goal="hero_next" aria-label="Следующий слайд">'+I('i-arrow')+'</button><span class="hero-next-topic" data-hero-next-topic>Далее: '+E(slides[1]['name'])+'</span></div><div class="trust-line">'+L('index.html','o-nas/index.html',str(years)+' '+years_label(years)+' в туризме →','trust_company')+L('index.html','kak-my-rabotaem/index.html#support','Сопровождение в поездке →','trust_support')+L('index.html','o-nas/otzyvy/index.html','Отзывы клиентов →','trust_reviews')+'</div></section><!-- /component: hero -->'
def faq_html():
 return '<div class="faq-list">'+''.join('<details class="faq-item" '+ED('faq.'+str(i))+'><summary data-goal="faq_'+str(i)+'">'+E(f['q'])+I('i-plus')+'</summary><p>'+faq_answer(f['a'])+'</p></details>'for i,f in enumerate(D['schema6']['faq']))+'</div>'
def faq_answer(a):return re.sub(r'<button[^>]*data-anchor="([^"]+)"[^>]*>(.*?)</button>',lambda m:L('index.html','kak-my-rabotaem/index.html#'+m[1],m[2],'faq_work_'+m[1],'text-link'),a)
def home():
 path='index.html';body=C['home_rest']();featured=[o for o in active_offers()if o['featured']][:4]
 if featured:body+=old.home_section('Актуальные предложения','<div class="tickets-grid">'+''.join(offer_card(path,o)for o in featured)+'</div>','offers','03',L(path,'predlozheniya/index.html','Все предложения →','home_offers_all','text-link'))
 countries=[country_by(slug)for slug in D['home_country_order']if country_by(slug)['published']][:6]
 body+=old.home_section('Страны','<div class="home-countries-six">'+''.join(country_tile(path,c)for c in countries)+'</div>','directions','04',L(path,'napravleniya/index.html','Все страны →','home_countries_all','text-link'))
 steps=''.join(L(path,'kak-my-rabotaem/index.html#'+s['id'],'<span class="step-number">'+str(i+1)+'</span><h3>'+E(s['title'])+'</h3><p>'+E(s['text'])+'</p>','home_work_'+s['id'],'step')for i,s in enumerate(D['home_process']))
 cost='Подбор путешествия, помощь в подготовке к поездке и сопровождение до возвращения домой уже входят в стоимость тура.'
 body+=old.home_section('Как мы работаем','<div class="work-card-grid">'+steps+'</div><p class="work-cost-line" '+ED('home.cost',True)+'>'+cost+'</p>','process','05',L(path,'kak-my-rabotaem/index.html','Подробнее о нашей работе →','home_work_all','text-link'))
 body+=old.home_section('Команда',old.people(path,True),'team','06',L(path,'o-nas/index.html','Познакомиться с нами →','home_team_all','text-link'))
 body+=old.home_section('Отзывы клиентов',old.platforms()+old.reviews_grid(True),'voices','07',L(path,'o-nas/otzyvy/index.html','Все отзывы →','home_reviews_all','text-link'))
 body+=old.home_section('Частые вопросы',faq_html(),'home-faq','08')
 direct='<div class="direct-card"><h3>Связаться напрямую</h3><a href="tel:+78512299547" data-goal="home_phone">+7 (8512) 29-95-47</a>'+channels('home','home_direct')+hours()+'</div>'
 body+=old.home_section('Связь','<div class="unified-end-grid">'+direct+form(path,'home')+'</div>','contact','09')
 body+=re.search(r'<section class="section partners-section".*?</section>',C['HOME'],re.S)[0]
 questions=[(f['q'],re.sub('<[^>]+>','',f['a']))for f in D['schema6']['faq']]
 C['emit'](path,'Mango Travel — турагентство в Астрахани','Путешествия с персональным менеджером: подбор, подготовка и сопровождение. Mango Travel — работаем онлайн по всей России.',D['slides'][0]['title'],'',body,[],photo=(D['slides'][0]['photo'],'Отдых'),cover_override=hero(),contact_override='',raw=True,page_class='stage4-home stage6-home',questions=questions,assets=['css/country.css','css/offers.css'])
 C['PAGES'][-1]['type']='home'
def hours():return '<p class="contact-hours" '+ED('contacts.hours',True)+'>'+E(D['contacts']['hours'])+'</p>'
def band(title,key='home',label='Обсудить поездку'):return '<section class="section final-band"><div class="container"><div class="final-band-panel"><h2>'+E(title)+'</h2>'+action(label,key,'final_request')+'</div></div></section>'
def services():
 path='uslugi/index.html';body='<div class="container services-accordion-columns">'
 for group,title in[('travel','Путешествия'),('extras','Для поездки')]:
  body+='<section class="service-accordion-group"><h2>'+title+'</h2>'
  for s in D['services']:
   if s['group']!=group:continue
   key='service:'+s['id'];target=key
   cta=L(path,'napravleniya/index.html',s['action'],'service_packages','btn btn-primary')if s['id']=='packages'else L(path,'otdyh/kruizy/index.html',s['action'],'service_request_'+s['id'],'btn btn-primary')if s['id']=='cruises'else L(path,'otdyh/'+('svoj-marshrut'if s['id']=='custom'else'ekskursionnye-tury')+'/index.html',s['action'],'service_request_'+s['id'],'btn btn-primary')if s['id']in['custom','tours']else action(s['action'],target,'service_request_'+s['id'])
   body+='<details class="service-accordion" id="'+s['id']+'" '+ED('services.'+s['id'],True)+'><summary data-goal="service_expand_'+s['id']+'">'+I('i-mood-compass')+'<span>'+E(s['title'])+'</span>'+I('i-plus')+'</summary><div><p>'+E(s['text'])+'</p>'+cta+'</div></details>'
  body+='</section>'
 body+='</div>';C['emit'](path,'Услуги — Mango Travel','Выберите, с чем Вам нужна помощь. Путешествия и организация поездки с Mango Travel.','Услуги','Выберите, с чем Вам нужна помощь.',body,[('Услуги',None)],contact_override='',raw=True)

def offers_pages():
 path='predlozheniya/index.html';rows=active_offers();countries=[c for c in published_countries()if any(o['country']==c['slug']for o in rows)]
 toolbar='<div class="offers-toolbar"><div class="filter-chips" role="group" aria-label="Фильтр по стране">'+''.join('<button type="button" data-offer-filter="'+slug+'" aria-pressed="'+str(i==0).lower()+'" data-goal="offers_filter_'+slug+'">'+E(name)+'</button>'for i,(slug,name)in enumerate([('all','Все')]+[(c['slug'],c['name'])for c in countries]))+'</div><label class="field-label"><span>Сортировка</span><select data-offer-sort data-goal="offers_sort"><option value="date">По дате вылета</option><option value="price">Сначала дешевле</option></select></label></div>'
 body=S('',toolbar+'<p class="sr-only" data-offer-status aria-live="polite"></p><div class="tickets-grid catalogue-tickets" data-offers-list>'+''.join(offer_card(path,o)for o in rows)+'</div>')if rows else''
 body+=band('Не нашли подходящий вариант?'if rows else'Подберём поездку под Ваши даты')
 C['emit'](path,'Актуальные предложения — Mango Travel','Актуальные предложения Mango Travel: даты, отели и условия тура за двоих. Уточните цену и наличие у менеджера.','Актуальные предложения','Все действующие предложения в одном разделе.',body,[('Предложения',None)],contact_override='',raw=True)
 active={o['id']for o in rows}
 for p in(C['SITE']/'predlozheniya').glob('*/index.html'):
  if p.parent.name not in active:p.unlink()
 for o in rows:
  path='predlozheniya/'+o['id']+'/index.html';c=country_by(o['country']);price=f'{o["price_from"]:,}'.replace(',',' ')
  visuals='<div class="offer-detail-photos">'+C['image'](path,o['photo'],o['hotel'],False,key='offers.'+o['id']+'.photo')+country_module.photo(path,o['room_photo'],'Фото номера','offers.'+o['id']+'.room_photo')+'</div>'
  details='<dl class="offer-conditions">'+''.join('<div><dt>'+label+'</dt><dd>'+E(value)+'</dd></div>'for label,value in[('Даты',dates(o)+f' · {o["nights"]} ночей'),('Перелёт','Город вылета — '+o['departure_city']+'. '+o['flight']),('Номер',o['room']),('Питание',o['meals']),('В стоимости',' · '.join(o['includes']))])+'</dl>'
  body=S('',visuals+'<div class="offer-detail-summary" '+ED('offers.'+o['id'],True)+'><p class="eyebrow">'+E(c['name'])+' · '+E(o['resort'])+'</p>'+details+'<p class="offer-detail-price">от '+price+' ₽ за двоих</p><p class="ticket-price-date">Цена на '+C['human_date'](o['price_date'])+'</p>'+action('Уточнить цену и наличие','offer:'+o['id'],'offer_inquiry_'+o['id'])+'</div><div class="offer-back-links">'+L(path,'predlozheniya/index.html','← Все предложения','offer_back_all','text-link')+(L(path,'napravleniya/'+c['slug']+'/index.html#offers','← К предложениям '+c['cases']['of'],'offer_back_country','text-link')if c['showOffers']else'')+'</div>')
  C['emit'](path,o['hotel']+' · '+c['name']+' — Mango Travel','Условия тура: '+offer_label(o)+'. Цена на '+C['human_date'](o['price_date'])+'.',o['hotel'],'',body,[('Предложения','predlozheniya/index.html'),(o['hotel'],None)],contact_override='',raw=True,page_class='offer-detail-page')

def extra_pages():
 path='kak-my-rabotaem/index.html';intro=''.join('<p '+ED('work.intro.'+str(i))+'>'+E(t)+'</p>'for i,t in enumerate(D['work']['intro']));cover='<section class="inner-cover" data-inner-cover><div class="container">'+C['crumb'](path,[('Как мы работаем',None)])+'<div class="article-column"><h1>Как мы работаем</h1><div class="approved-intro">'+intro+'</div></div></div></section>'
 body=''.join('<section class="section approved-section" id="'+s['id']+'" '+ED('work.'+s['id'],s.get('needsApproval',False))+'><div><div class="article-column"><h2>'+E(s['title'])+'</h2>'+''.join('<p>'+E(p)+'</p>'for p in s['paragraphs'])+'</div></div></section>'for s in D['work']['sections'])
 body='<div class="container work-layout"><div class="work-body">'+body+'</div><aside class="work-toc" aria-label="Оглавление"><p>Как мы работаем</p>'+''.join('<a href="#'+s['id']+'" data-work-anchor data-goal="work_anchor_'+s['id']+'">'+E(s['title'])+'</a>'for s in D['work']['sections'])+'</aside></div>'+band(D['work']['finalTitle'])
 C['emit'](path,'Как мы работаем — Mango Travel','Как мы подбираем путешествие, готовим документы и сопровождаем Вас до возвращения домой. Mango Travel.','Как мы работаем','',body,[('Как мы работаем',None)],cover_override=cover,contact_override='',raw=True)
 path='o-nas/index.html';company='<div class="company-layout">'+C['illustrative_photo'](path,'hero-lake.webp','Озеро и горы','about.photo').replace('<img ','<img data-needs-approval="photo" ')+ '<div><h3>Кто мы и как относимся к Вашему отдыху</h3><div class="editorial-text" '+ED('about.copy',True)+'><p>Мы работаем в туризме с 2010 года, а с 2017 года — под брендом Mango Travel.</p><p>'+E(D['contacts']['location'])+'</p><p>У каждого клиента есть персональный менеджер. Сравниваем предложения разных туроператоров и обсуждаем условия до выбора поездки.</p></div>'+L(path,'kak-my-rabotaem/index.html','Как мы работаем →','about_work','text-link')+'</div></div>'
 body='<section class="section inner-section about-unified" id="company"><span class="section-anchor" id="team" aria-hidden="true"></span><div class="container"><p class="eyebrow" '+ED('about.eyebrow')+'>Работаем в туризме с 2010 года</p><h2 '+ED('about.title')+'>Кто мы и как относимся к Вашему отдыху</h2>'+company.replace('<h3>Кто мы и как относимся к Вашему отдыху</h3>','')+old.people(path)+'</div></section>'+band('Давайте познакомимся')
 C['emit'](path,'О нас — Mango Travel','О компании и команде Mango Travel: работаем в туризме с 2010 года. Персональный менеджер и забота о Вашем отдыхе.','О нас','',body,[('О нас',None)],about=True,contact_override='',raw=True)
 path='o-nas/komanda/index.html';(C['SITE']/path).write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Команда — Mango Travel</title><meta name="description" content="Команда Mango Travel на странице О нас."><meta http-equiv="refresh" content="0;url=../index.html#team"><link rel="canonical" href="https://devfriends.ru/o-nas/#team">'+C['brand_icons'](path)+'</head><body><h1>Команда Mango Travel</h1><a href="../index.html#team" data-goal="team_redirect">Познакомиться с командой →</a></body></html>\n');C['PAGES'].append({'path':path,'title':'Команда → О нас','type':'redirect'})
 path='o-nas/otzyvy/index.html';C['emit'](path,'Отзывы клиентов — Mango Travel','Отзывы клиентов Mango Travel с указанием автора, даты и площадки.','Отзывы клиентов','',S('',old.platforms()+old.reviews_grid())+band('Расскажите о своей поездке — подберём для Вас'),[('О нас','o-nas/index.html'),('Отзывы',None)],about=True,contact_override='',raw=True)
 path='o-nas/kontakty/index.html';direct='<article class="info-card"><h2>Напишите или позвоните</h2><div class="direct-contacts"><a href="tel:+78512299547" data-goal="contacts_phone">+7 (8512) 29-95-47</a><a href="tel:+78512299527" data-goal="contacts_secondary">+7 (8512) 29-95-27</a>'+channels('contact','contacts')+'<a href="mailto:man.go.travel@mail.ru" data-goal="contacts_email">man.go.travel@mail.ru</a><p '+ED('contacts.location')+'>'+E(D['contacts']['location'])+'</p>'+hours()+'</div></article>'
 C['emit'](path,'Контакты — Mango Travel','Телефоны, MAX, Telegram, email и обращение в Mango Travel. Астрахань: работаем онлайн по всей России.','Контакты','',S('','<div class="unified-end-grid">'+direct+form(path,'contact')+'</div>'),[('О нас','o-nas/index.html'),('Контакты',None)],about=True,contact_override='',raw=True)
 import stage11
 stage11.documents()
 for slug,title in [('politika','Политика обработки персональных данных'),('soglasie','Согласие на обработку персональных данных')]:
  path='o-nas/dokumenty/'+slug+'/index.html';C['emit'](path,('Политика обработки данных'if slug=='politika'else'Согласие на обработку данных')+' — Mango Travel','Персональные данные: '+('политика обработки.'if slug=='politika'else'согласие на обработку.')+' Документ требует юридического согласования.',title,'',S('',D['legal_body'][slug]),[('О нас','o-nas/index.html'),('Документы','o-nas/dokumenty/index.html'),(title,None)],about=True,contact_override='',raw=True)
 path='zagranpasport/index.html';intro='Для проверки понадобятся страна, гражданство, даты поездки и срок действия паспорта.';body=S('','<div class="passport-placeholder" '+ED('passport.calculator',True)+'><p>Напишите менеджеру — сообщение с темой уже подготовлено.</p>'+action('Уточнить у менеджера','passport','passport_request')+'</div>')
 C['emit'](path,'Проверить срок загранпаспорта — Mango Travel',intro,'Проверить срок действия загранпаспорта',intro,body,[('Загранпаспорт',None)],contact_override='',raw=True)
 C['emit']('404.html','Страница не найдена — Mango Travel','Выберите раздел или обратитесь в Mango Travel.','Страница не найдена','Давайте найдём нужную страницу.',S('',L('404.html','index.html','На главную →','404_home','text-link')),[('Страница не найдена',None)],contact_override='',raw=True)
 offers_pages()
 path='pages.html';body=S('Страницы сайта','<div class="page-directory">'+''.join(L(path,p['path'],E(p['title'])+' <small>'+p['path']+'</small>','directory_'+str(i))for i,p in enumerate(C['PAGES']))+'</div>');C['emit'](path,'Страницы сайта — Mango Travel','Техническое оглавление страниц Mango Travel.','Страницы сайта','',body,[('Страницы',None)],contact_override='',raw=True)
def quiz(path):
 groups=''
 for name,title,options in[('who','Кто едет?',[('Вдвоём','Вдвоём'),('С детьми','С детьми'),('Компанией','Компанией'),('Один','Один')]),('when','Когда хотите поехать?',[(x,x)for x in['Весна','Лето','Осень','Зима']]+[('dates','Знаю даты'),('Пока не знаю','Пока не знаю')]),('what','Что Вам ближе?',[(x,x)for x in['Море','Горы','Города','Пока не знаю']])]:
  groups+='<fieldset class="selection-question"><legend>'+title+'</legend><div class="selection-chips">'+''.join('<label class="selection-chip"><input type="radio" name="'+name+'" value="'+value+'" data-goal="quiz_'+name+'_'+str(i)+'"><span>'+label+'</span></label>'for i,(value,label)in enumerate(options))+'</div>'
  if name=='when':groups+='<label class="field-label" data-quiz-year hidden><span>Год поездки</span><select name="year" disabled data-goal="quiz_year">'+''.join('<option>'+str(now().year+i)+'</option>'for i in range(3))+'</select></label><div class="unified-grid" data-quiz-dates hidden>'+field('С','<input type="date" name="from" disabled>')+field('По','<input type="date" name="to" disabled>')+'</div>'
  groups+='</fieldset>'
 hidden=''.join('<input type="hidden" name="'+n+'" value="'+('quiz'if n=='topic'else E(path)if n=='page'else'')+'">'for n in HIDDEN)
 return '<dialog id="quiz-dialog" class="quiz-dialog selection-dialog" aria-modal="true" aria-labelledby="quiz-title"><div class="dialog-top"><h2 id="quiz-title">Помогите выбрать</h2><button class="icon-btn" type="button" data-dialog-close data-goal="quiz_close" aria-label="Закрыть подбор">'+I('i-close')+'</button></div><p class="quiz-intro">Ответьте на три вопроса. Менеджер предложит варианты с учётом Ваших пожеланий.</p><div class="unified-card unified-quiz" data-unified-card><form class="unified-form" data-unified-form data-mode="pick" data-topic="quiz" data-quiz-form novalidate><fieldset data-form-guard disabled><legend class="sr-only">Пожелания к поездке</legend>'+hidden+groups+'<div class="unified-grid">'+field('Бюджет на всю поездку, по желанию','<input name="budget" maxlength="100">')+field('Телефон','<input type="tel" name="phone" autocomplete="tel" inputmode="tel" required maxlength="18" placeholder="+7 (___) ___-__-__">')+'</div>'+consent(path,'quiz')+'<p class="form-error" data-form-error role="alert"></p><button type="submit" class="btn btn-primary" data-goal="quiz_submit">Получить варианты</button></fieldset><p class="channel-caption">Или напишите в мессенджер</p>'+channels('quiz','quiz')+'</form><div class="form-success" data-form-success role="status" tabindex="-1" hidden><p>'+SUCCESS+'</p></div></div></dialog>'
def topic_map(path):
 keys=['home','contact','passport','quiz']+['slide:'+str(i)for i in range(4)]+['holiday:'+card['slug']for card in D['home_rest']['cards']]+['holiday:'+p['slug']for p in D['rest_pages']]+['offer:'+o['id']for o in active_offers()]+['service:'+s['id']for s in D['services']]
 if path=='otdyh/kruizy/index.html':keys+=['holiday:cruises:option:'+str(i)for i in range(len(D['cruise_page']['types']))]
 for c in published_countries():
  keys+=['country:'+c['slug'],'price:'+c['slug'],'route:'+c['slug']+':custom']
  for group,kind_ in[('resorts','resort'),('hotels','hotel'),('routes','route')]:keys += [kind_+':'+c['slug']+':'+item['id']for item in c[group]]
 for p in D['rest_pages']:
  if path!='otdyh/'+p['slug']+'/index.html':continue
  prefix='holiday:'+p['slug'];keys += [prefix+':type:'+str(i)for i in range(len(p['types']))]+[prefix+':country:'+c['slug']for c in p['countries']]+[prefix+':hotel:'+h['id']for group in p['hotels'].values()for h in group]
 return {key:{'title':topic(key)[0],'message':topic(key)[1],'kind':kind(key)}for key in keys}
def mobile_panel(path):
 key=page_topic(path);label='Подобрать круиз'if path=='otdyh/kruizy/index.html'else'Подобрать путешествие'if path=='index.html'else'Подобрать тур'if key.startswith('country:')else'Подобрать отдых'if key.startswith('holiday:')else'Связаться с нами'if key in['contact','passport']else'Обсудить поездку'
 return '<div class="mobile-contact unified-mobile-panel" data-mobile-contact hidden>'+action(label,key,'mobile_primary')+channels(key,'mobile_channel')+'</div>'
def finish(path):
 p=C['SITE']/path;h=p.read_text()
 if next(x for x in C['PAGES']if x['path']==path)['type']=='redirect':return
 h=h.replace('Шарм-эш-Шейх','Шарм-эль-Шейх').replace('#plans-on-trip','#trip-plans')
 h=h.replace('<h2 ></h2>','');h=re.sub(r'<div class="section-head">\s*</div>','',h)
 # Site links are actual relative URLs, never the sketch's single-file router.
 def href(m):
  v=m[1]
  if re.match(r'[a-z]+:|//',v):return m[0]
  if 'voprosy/'in v:return 'href="'+U(path,'index.html#home-faq')+'"'
  match=re.search(r'uslugi/([^/]+)/index.html',v)
  if match and match[1]in SERVICE_OLD:return 'href="'+U(path,'uslugi/index.html#'+SERVICE_OLD[match[1]])+'"'
  return m[0]
 h=re.sub(r'href="([^"]+)"',href,h)
 # Retire previous modal forms and previous floating panels as complete components.
 h=re.sub(r'<dialog\b[^>]*id="(?:request-dialog|quiz-dialog)".*?</dialog>','',h,flags=re.S)
 start=h.find('<div class="mobile-contact')
 if start>=0:
  depth=0;end=None
  for m in re.finditer(r'</?div\b[^>]*>',h[start:]):
   depth+=-1 if m[0].startswith('</')else 1
   if depth==0:end=start+m.end();break
  h=h[:start]+mobile_panel(path)+h[end:]
 topics=topic_map(path);pagekey=page_topic(path)
 # Legacy holiday links keep their approved copy and selection behavior.
 def attributes(m):
  tag,attrs,content=m[1],m[2],m[3]
  if 'data-quiz-open'in attrs and re.search(r'data-goal="mood_',attrs):
   slug=re.search(r'data-goal="mood_([^"]+)"',attrs)[1];attrs=attrs.replace('data-quiz-open','data-open-form="holiday:'+slug+'"').replace('href="#quiz-dialog"','href="#request-dialog"')
  if 'data-rest-select'in attrs:
   value=re.search(r'data-rest-select="([^"]+)"',attrs)[1];key=pagekey+':choice:'+str(len(topics));base=topic(pagekey);topics[key]={'title':base[0]+' · '+value,'message':base[1]+'. '+value,'kind':'pick'};attrs+=' data-choice-topic="'+key+'"'
  if 'data-hotel-message'in attrs:
   value=re.search(r'data-hotel-message="([^"]+)"',attrs)[1];key=pagekey+':hotel:'+str(len(topics));base=topic(pagekey);topics[key]={'title':base[0]+' · '+value,'message':base[1]+'. '+value,'kind':'pick'};attrs+=' data-open-form="'+key+'"'
  if 'data-messenger='in attrs and'data-topic-key='not in attrs:attrs+=' data-topic-key="'+E(pagekey)+'"'
  if 'data-request'in attrs and'data-open-form'not in attrs:attrs=re.sub(r'\sdata-request(?:="[^"]*")?','',attrs)+' data-open-form="'+pagekey+'"'
  return '<'+tag+attrs+'>'+content+'</'+tag+'>'
 h=re.sub(r'<(a|button)\b([^>]*)>(.*?)</\1>',attributes,h,flags=re.S)
 def schema_hours(m):
  obj=json.loads(m[1])
  for entry in obj.get('@graph',[]):
   if entry.get('@type')=='TravelAgency':entry.pop('openingHoursSpecification',None)
  return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False)+'</script>'
 h=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema_hours,h,flags=re.S)
 h=h.replace('</head>',f'<link rel="stylesheet" href="{U(path,"css/stage6.css")}"></head>')
 dialog='<dialog class="request-dialog unified-dialog" id="request-dialog" aria-modal="true" aria-labelledby="request-title"><div class="dialog-top"><h2 id="request-title">Расскажите о поездке</h2><button type="button" class="icon-btn" data-dialog-close data-goal="request_close" aria-label="Закрыть обращение">'+I('i-close')+'</button></div>'+''.join('<div data-form-pane="'+mode+'"'+(' hidden'if mode!='pick'else'')+'>'+form(path,'contact'if mode=='service'else'home','dialog',mode,False)+'</div>'for mode in['pick','offer','service'])+'</dialog>'
 config={'topics':topics,'topic':pagekey,'path':path,'telegramUsername':D['contacts']['telegramUsername'],'max':D['contacts']['max'],'year':now().year,'month':now().month}
 h=h.replace('</body>',dialog+(quiz(path)if path=='index.html'else'')+'<script type="application/json" id="app-config">'+json.dumps(config,ensure_ascii=False).replace('<','\\u003c')+'</script></body>')
 p.write_text(h)
