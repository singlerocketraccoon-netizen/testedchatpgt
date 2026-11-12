"""Approved 11.11 structure rendered with design 1 components, without client fetching."""
from datetime import datetime,date
from zoneinfo import ZoneInfo
from html import unescape
import json,re
import online
from content4 import approved


def today():return datetime.now(ZoneInfo('Europe/Moscow')).date()
def brand(s):
 protected='APPROVED_ACCENT_PHRASE'
 s=s.replace('Путешествия с Манго',protected).replace('Манго Путешествия','Mango Travel')
 s=re.sub(r'\bМанго\b','Mango Travel',s)
 return s.replace(protected,'Путешествия с Манго')

def configure(c):
 global C,D,E,I,U,L,ED,S,BASE_EMIT,BASE_NAV,BASE_FOOTER
 online.configure(c);C=c;D=c['DATA'];E=c['E'];I=c['icon'];U=c['url'];L=c['link'];ED=c['editable'];S=c['section'];BASE_EMIT=c['emit'];BASE_NAV=c['navitems'];BASE_FOOTER=c['footer']
 a=approved()
 for actual,wanted in zip(D['slides'],a['slides']):
  for k,v in wanted.items():assert actual[k]==v,('Approved slide differs',k)
 if not D.get('schema6'):assert D['work']==a['work'] and D['faq']==a['faq'],'Approved work/FAQ copy differs'
 for p,v in D['page_overrides'].items():
  for k in['title','description']:
   if k in v:v[k]=brand(v[k])[:(60 if k=='title'else 160)]
 c.update(header=header,navitems=navitems,aboutnav=aboutnav,footer=footer,contact=end_band,emit=emit,active_offers=active_offers,offer=offer,selection_dialog=selection_dialog,home_steps=home_steps)
 online.channel_links=channels
 # Preserve the legal operator text as content, rather than reconstructing it from branding.
 for path,title in [('o-nas/dokumenty/politika/index.html','Политика обработки персональных данных'),('o-nas/dokumenty/soglasie/index.html','Согласие на обработку персональных данных')]:
  D['pages'][path]['topic']='Страница: '+title

def settings(path):
 if path not in D['pages']:D['pages'][path]={'messengerText':'Здравствуйте! Хочу обсудить поездку.','topic':'Обсудить поездку'}
 return D['pages'][path]

def channels(context,key,compact=False):
 online.validate_message(context)
 username=D['contacts']['telegramUsername'].lstrip('@');tg='https://t.me/'+username+'?text='+online.quote(context)if username else'#'
 return '<div class="messenger-actions">'+''.join(f'<a class="btn btn-outline" href="{E(href)}" data-messenger="{name}" data-message="{E(context)}" data-goal="{key}_{name.lower()}" {ED("contacts."+("max"if name=="MAX"else"telegramUsername"))}>{I("i-max"if name=="MAX"else"i-telegram")}<span>{("Написать в "+name)if compact else name}</span></a>'for name,href in [('MAX',D['contacts']['max']),('Telegram',tg)])+'</div><p class="messenger-feedback" role="status" data-channel-status hidden>Текст скопирован — вставьте его в чат</p>'

def request_button(label='Обсудить поездку',topic='Обсудить поездку',key='request',cls='btn btn-primary'):
 return f'<button type="button" class="{cls}" data-request data-topic="{E(topic)}" data-goal="{key}" {ED(key+".label")}>{E(label)}</button>'

def end_band(path,prefill=''):
 title={'kak-my-rabotaem/index.html':D['work']['finalTitle'],'o-nas/index.html':'Давайте познакомимся','predlozheniya/index.html':'Не нашли подходящий вариант?','voprosy/index.html':'Остались вопросы?','o-nas/otzyvy/index.html':'Расскажите о своей поездке'}.get(path,'Обсудим Вашу поездку?')
 action=platforms(True)if path=='o-nas/otzyvy/index.html'else L(path,'o-nas/kontakty/index.html','Связаться с нами','faq_contact','btn btn-primary')if path=='voprosy/index.html'else request_button(topic=settings(path)['topic'],key='end_request')
 return '<section class="section final-band" id="contact" data-end-contact><div class="container"><div class="final-band-panel"><h2 '+ED(path+'.end.title')+'>'+E(title)+'</h2><div>'+action+'</div></div></div></section>'

def emit(path,title,description,h1,intro,body,items,*args,**kw):
 title=brand(title);description=brand(description)
 if len(title)>60:title=brand(h1)+' — Mango Travel'
 if len(title)>60:title=brand(h1)[:60]
 description=description[:160]
 kw['page_script']='js/main.js'
 if kw.get('page_class')=='compact-service':kw['contact_override']=end_band(path)
 return BASE_EMIT(path,title,description,h1,intro,body,items,*args,**kw)

WORK_LINKS=[('Весь процесс →',''),('Ваши планы','plans'),('Подбор и выбор','choice'),('Подготовка к поездке','prepare'),('Сопровождение в поездке','support'),('Сколько стоят наши услуги','cost')]
def navitems(path,kind):
 if kind=='work':return ''.join(L(path,'kak-my-rabotaem/index.html'+('#'+a if a else''),t,'nav_work_'+(a or'all'))for t,a in WORK_LINKS)
 if kind=='about':return ''.join(L(path,t,label,'nav_about_'+str(i))for i,(label,t)in enumerate([('О компании','o-nas/index.html#company'),('Команда','o-nas/index.html#team'),('Отзывы','o-nas/otzyvy/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html')]))
 return BASE_NAV(path,kind)
def dropdown(path,label,kind):
 return f'<div class="nav-dropdown nav-compact"><button type="button" data-nav-toggle aria-expanded="false" aria-controls="nav-{kind}" data-goal="nav_{kind}_toggle" disabled>{label}{I("i-down")}</button><div class="dropdown-panel" id="nav-{kind}" hidden><p class="dropdown-label">{label}</p><div class="dropdown-grid">{navitems(path,kind)}</div></div></div>'
def header(path,photo=False):
 groups=''.join(f'<details class="mobile-group"><summary data-goal="mobile_{kind}">{name}{I("i-down")}</summary><div class="mobile-submenu">{navitems(path,kind)}'+(L(path,target,'Все страны →'if kind=='countries'else'Все услуги →','mobile_'+kind+'_all')if target else'')+'</div></details>'for name,kind,target in [('Страны','countries','napravleniya/index.html'),('Услуги','services','uslugi/index.html'),('Как мы работаем','work',''),('О нас','about','')])
 return f'''<!-- component: header --><header class="site-header d1-header{' is-solid'if not photo else''}" data-site-header><div class="header-inner"><nav class="nav-left" aria-label="Страны и услуги">{C['dropdown'](path,'Страны','countries')}{C['dropdown'](path,'Услуги','services')}</nav><a href="{U(path)}" class="brand" data-goal="home" data-editable="brand.logo" aria-label="Mango Travel — главная"><img class="logo-dark" src="{C['brand_path'](path,'logo')}" alt="Mango Travel" width="1193" height="440"><img class="logo-light" src="{C['brand_path'](path,'light')}" alt="Mango Travel" aria-hidden="true" width="1193" height="440"></a><nav class="nav-about" aria-label="Об агентстве">{dropdown(path,'Как мы работаем','work')}{dropdown(path,'О нас','about')}</nav><div class="header-contacts"><a class="header-phone icon-control" href="tel:+78512299547" aria-label="Позвонить: +7 (8512) 29-95-47" data-goal="phone_header" {ED('contacts.primaryPhone')}>{I('i-phone')}<span>+7 (8512) 29-95-47</span></a><a class="icon-control" href="#" aria-label="Написать в MAX" data-messenger="MAX" data-goal="messenger_max_header" {ED('contacts.max')}>{I('i-max')}</a><a class="icon-control" href="#" aria-label="Написать в Telegram" data-messenger="Telegram" data-goal="messenger_telegram_header" {ED('contacts.telegramUsername')}>{I('i-telegram')}</a><button type="button" class="icon-control menu-toggle" aria-label="Открыть меню" aria-controls="mobile-nav" aria-expanded="false" data-menu data-goal="menu_toggle" disabled>{I('i-menu')}</button></div></div><nav id="mobile-nav" class="mobile-nav" aria-label="Мобильное меню" hidden>{groups}<p class="mobile-contact-caption">Обсудим Вашу поездку</p><a class="mobile-contact-number" href="tel:+78512299547" data-goal="mobile_phone">+7 (8512) 29-95-47</a></nav><noscript><p class="nav-nojs">{L(path,'napravleniya/index.html','Страны','nojs_countries')} · {L(path,'uslugi/index.html','Услуги','nojs_services')} · {L(path,'o-nas/index.html','О нас','nojs_about')}</p></noscript></header><!-- /component: header -->'''
def aboutnav(path):
 return '<nav class="section-tabs" aria-label="Раздел об агентстве">'+''.join(L(path,t,label,'about_tab_'+str(i))for i,(label,t)in enumerate([('Отзывы','o-nas/otzyvy/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html')]))+'</nav>'

def footer(path,home=False):
 f=BASE_FOOTER(path,home)
 return f.replace('data-goal="footer_process"', 'data-goal="footer_process"').replace('</nav><div><h2>Контакты</h2>',L(path,'voprosy/index.html','Частые вопросы','footer_faq')+'</nav><div><h2>Контакты</h2>',1)

def consent(path,key):return f'<label class="consent"><input type="checkbox" name="consent" required><span><a href="{U(path,"o-nas/dokumenty/soglasie/index.html")}" data-goal="{key}_consent" target="_blank" rel="noopener">Согласие на обработку персональных данных</a></span></label>'
def local_result():return '<div class="form-success" data-local-success role="status" tabindex="-1" hidden><p>Спасибо, менеджер свяжется с Вами</p></div>'
def request_dialog(path):
 return f'''<!-- component: discussion-form --><dialog class="request-dialog" id="request-dialog" aria-modal="true" aria-labelledby="request-title"><div class="dialog-top"><h2 id="request-title">Обсудить поездку</h2><button type="button" class="icon-btn" data-dialog-close aria-label="Закрыть окно" data-goal="request_close">{I('i-close')}</button></div><form data-local-form data-request-form novalidate><fieldset data-form-guard disabled><legend class="sr-only">Ваш запрос</legend><input type="hidden" name="topic" value="{E(settings(path)['topic'])}"><label class="field-label"><span>Ваш телефон</span><input type="tel" name="phone" required autocomplete="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" maxlength="18"></label><label class="field-label"><span>Пожелания, по желанию</span><textarea name="wishes" rows="3" placeholder="Даты, состав поездки, что важно" maxlength="1500"></textarea></label>{consent(path,'request')}<p class="form-error" data-local-error role="alert"></p><button type="submit" class="btn btn-primary" data-goal="request_submit">Отправить запрос</button></fieldset></form>{local_result()}<p class="channel-caption">Или напишите нам:</p>{channels(settings(path)['messengerText'],'request_dialog')}</dialog><!-- /component: discussion-form -->'''
def selection_dialog(path='index.html'):
 groups=''
 for group in D['selection']['questions']:
  name,title,values=group['name'],group['title'],group['options']
  groups+='<fieldset class="selection-question"><legend>'+title+'</legend><div class="selection-chips">'+''.join(f'<label class="selection-chip"><input type="radio" name="{name}" value="{E(v)}" data-goal="quiz_{name}_{i}"><span>{E(v)}</span></label>'for i,v in enumerate(values))+'</div>'
  if name=='when':groups+='<div class="date-pair" data-known-dates hidden><label class="field-label"><span>С</span><input type="date" name="from" disabled></label><label class="field-label"><span>По</span><input type="date" name="to" disabled></label></div>'
  groups+='</fieldset>'
 return f'''<dialog class="quiz-dialog selection-dialog" id="quiz-dialog" aria-modal="true" aria-labelledby="quiz-title"><div class="dialog-top"><h2 id="quiz-title">Поможем выбрать отдых</h2><button type="button" class="icon-btn" data-dialog-close aria-label="Закрыть подбор" data-goal="quiz_close">{I('i-close')}</button></div><form data-local-form data-help-form novalidate><fieldset data-form-guard disabled><legend class="sr-only">Пожелания к отдыху</legend><input type="hidden" name="topic" value="Подбор отдыха">{groups}<div class="selection-fields"><label class="field-label"><span>Бюджет, по желанию</span><input name="budget" placeholder="На всю поездку, ₽" maxlength="30"></label><label class="field-label"><span>Ваш телефон</span><input type="tel" name="phone" autocomplete="tel" inputmode="tel" required placeholder="+7 (___) ___-__-__" maxlength="18"></label></div>{consent(path,'quiz')}<p class="form-error" data-local-error role="alert"></p><button type="submit" class="btn btn-primary" data-goal="quiz_submit">Получить варианты</button></fieldset></form>{local_result()}<p class="channel-caption">Или напишите нам:</p>{channels(settings(path)['messengerText'],'quiz_dialog')}</dialog>'''

def visible_slides(on=None):return [s for s in D['slides']if not s.get('showUntil')or s['showUntil']>=(on or today()).isoformat()]
def active_offers(country=None,on=None):
 now=(on or today()).isoformat()
 return [o for o in D['offers']if o['active']and o['showUntil']>=now and(country is None or o['country']==country)]
def offer_topic(o):return o['departure_city']+' → '+o['resort']+' · '+C['human_date'](o['departure_date'])+f' · {o["nights"]} ночей · '+o['hotel']+f' {o["stars"]}★ · от '+f'{o["price_from"]:,}'.replace(',',' ')+' ₽ за двоих'
def offer(path,o):
 h=online.offer(path,o);target='predlozheniya/'+o['id']+'/index.html'
 h=h.replace(C['image'](path,o['photo'],next(c for c in D['countries']if c['slug']==o['country'])['name']+' · '+o['resort'],key='offers.'+o['id']+'.photo'),L(path,target,C['image'](path,o['photo'],next(c for c in D['countries']if c['slug']==o['country'])['name']+' · '+o['resort'],key='offers.'+o['id']+'.photo'),'offer_photo_'+o['id']))
 h=re.sub(r'(<p class="boarding-hotel"[^>]*>)(.*?)(</p>)',lambda m:m[1]+L(path,target,m[2],'offer_hotel_'+o['id'])+m[3],h)
 h=re.sub(r'<a class="btn btn-outline".*?</a>',lambda m:request_button('Уточнить тур',offer_topic(o),'offer_request_'+o['id'],cls='btn btn-outline'),h,count=1,flags=re.S)
 return h

def hero():
 path='index.html';slides=visible_slides();cards=''
 for i,s in enumerate(slides):
  title='h1'if i==0 else'h2';action=f'<button type="button" class="btn btn-primary" data-quiz-open data-goal="hero_quiz">{E(s["button"])}</button>'if s['id']=='slide-1'else request_button(s['button'],s.get('topic',s['accent']),'hero_request_'+s['id'])
  cards+=f'<article class="hero-slide{" is-active"if i==0 else""}" data-slide-accent="{E(s["accent"])}" aria-hidden="{str(i!=0).lower()}"'+(' inert'if i else'')+'>'+C['image'](path,s['photo'],s.get('alt',s['photoBrief']),False,key='slides.'+s['id']+'.photo')+f'<div class="hero-copy"><p class="hero-accent" {ED("slides."+s["id"]+".accent",s.get("needsApproval")is not None)}>{E(s["accent"])}</p><{title} {ED("slides."+s["id"]+".title")}>{E(s["title"])}</{title}><p {ED("slides."+s["id"]+".description")}>{E(s["description"])}</p>{action}</div></article>'

 return f'<!-- component: hero --><section class="hero-shell" data-hero data-inner-cover data-home-block="01" aria-label="Путешествия"><div class="hero-slides">{cards}</div><div class="hero-controls"><button type="button" class="icon-btn" data-hero-prev data-goal="hero_previous" aria-label="Предыдущий слайд">{I("i-arrow-left")}</button><span class="hero-count"><span data-hero-count>1</span> / {len(slides)}</span><button type="button" class="icon-btn" data-hero-next data-goal="hero_next" aria-label="Следующий слайд">{I("i-arrow")}</button><span class="hero-next-topic" data-hero-next-topic>{E(slides[1%len(slides)]["accent"])}</span></div><div class="trust-line">'+L(path,'o-nas/index.html#company',str(online.years_in_tourism())+' '+online.years_label(online.years_in_tourism())+' в туризме','trust_company')+L(path,'kak-my-rabotaem/index.html#support','Сопровождение в поездке','trust_support')+'<a href="#voices" data-goal="trust_reviews">Отзывы клиентов</a></div></section><!-- /component: hero -->'

def home_section(title,body,id,number,action='',cls=''):
 return f'<section class="section {cls}" id="{id}" data-home-block="{number}"><div class="container"><div class="section-head"><h2 {ED("home."+id+".title")}>{title}</h2>{action}</div>{body}</div></section>'
def home_steps():
 return ''.join(L('index.html','kak-my-rabotaem/index.html#'+s['id'],f'<span class="step-number">{i+1}</span><h3>{E(s["title"])}</h3><p>{E(s["text"])}</p>','home_work_'+s['id'],'step')for i,s in enumerate(D['home_process']))
def people(path,home=False):
 cards=''
 for i,p in enumerate(D['team_members']):
  cards+=f'<article class="person-card" {ED("team."+str(i),True)}><div class="person-avatar" role="img" aria-label="Инициалы менеджера" {ED("team."+str(i)+".photo")}><span>{E(p["initials"])}</span></div><div><h3>{E(p["name"])}</h3><p class="person-role">{E(p["role"])}</p><p>{E(p["help"]if home else p["expertise"])}</p>'+(L(path,'o-nas/index.html#team','Короткое знакомство →','person_'+str(i),'text-link')if home else'')+'</div></article>'
 return '<div class="people-grid">'+cards+'</div>'
def platforms(leave=False):
 return '<div class="review-platforms">'+''.join(f'<a href="{E(p["url"])}" class="review-platform-link" data-review-platform="{p["slug"]}" data-goal="reviews_{p["slug"]}" {ED("reviews.platforms."+p["slug"]+".url")}>{E(("Яндекс ↗"if p["slug"]=="yandex"else"2ГИС ↗")if leave else("Отзывы на Яндексе ↗"if p["slug"]=="yandex"else"Отзывы в 2ГИС ↗"))}</a>'for p in D['review_platforms'])+'</div>'
def reviews_grid(home=False):
 return '<div class="stage4-review-grid'+(' scroll-rail'if home else'')+'">'+''.join(f'<!-- component: review-card --><article class="review-card" {ED("reviews."+str(i),i==0)}><blockquote>{E(r["text"])}</blockquote><p class="review-author">{E(r["name"])}</p><p class="review-destination">{E(r["destination"])}</p><p class="review-meta">{E(r["date"])} · <a href="{E(r["source"])}" data-goal="review_source_{i}" {ED("reviews."+str(i)+".source")}>Источник ↗</a></p></article><!-- /component: review-card -->'for i,r in enumerate(D['reviews'][:3]))+'</div>'
def faq_html(rows,key):
 return '<div class="faq-list">'+''.join(f'<details class="faq-item" {ED(key+"."+str(i))}><summary data-goal="{key}_{i}">{E(q)}{I("i-plus")}</summary><p>{E(a)}</p></details>'for i,(q,a)in enumerate(rows))+'</div>'
def home_page():
 path='index.html';body=C['home_rest']()+C['home_offers']()
 countries=[next(c for c in D['countries']if c['slug']==slug)for slug in['turciya','egipet','oae','tailand','maldivy','vetnam']]
 cards=''.join('<!-- component: direction-card -->'+L(path,'napravleniya/'+c['slug']+'/index.html',C['image'](path,c['heroPhoto'],c['alt'],key='countries.'+c['slug']+'.heroPhoto')+'<span>'+E(c['name'])+' '+I('i-arrow')+'</span>','home_country_'+c['slug'],'home-country-card')+'<!-- /component: direction-card -->'for c in countries)
 body+=home_section('Страны','<div class="home-countries">'+cards+'</div>','directions','04',L(path,'napravleniya/index.html','Все страны →','home_countries','text-link'))
 body+=home_section('Как мы работаем','<div class="work-card-grid">'+home_steps()+'</div>','process','05',L(path,'kak-my-rabotaem/index.html','Подробнее о нашей работе →','home_work','text-link'))
 body+=home_section('Команда',people(path,True),'team','06',L(path,'o-nas/index.html#team','Познакомиться с нами →','home_team','text-link'))
 body+=home_section('Отзывы туристов',platforms()+reviews_grid(True),'voices','07',L(path,'o-nas/otzyvy/index.html','Все отзывы →','home_reviews','text-link'))
 body+=home_section('Частые вопросы',faq_html(D['faq'],'home_faq'),'questions','08',L(path,'voprosy/index.html','Все вопросы →','home_faq_all','text-link'))
 band='<div class="final-band-panel"><div><h3>Обсудим Вашу поездку?</h3><div class="home-direct-links"><a href="tel:+78512299547" data-goal="home_phone">+7 (8512) 29-95-47</a>'+channels(settings(path)['messengerText'],'home_contact')+'</div></div>'+request_button(key='home_request')+'</div>'
 body+=home_section('Связь',band,'contact','09')
 body+=re.search(r'<section class="section partners-section".*?</section>',C['HOME'],re.S)[0]
 emit(path,'Mango Travel — турагентство в Астрахани','Путешествия с персональным менеджером: подбор, подготовка и сопровождение. Mango Travel — работаем онлайн по всей России.',D['slides'][0]['title'],'',body,[],photo=(D['slides'][0]['photo'],'Отдых'),cover_override=hero(),contact_override='',raw=True,page_class='stage4-home',questions=D['faq'],assets=['css/offers.css','js/offers.js'])
 C['PAGES'][-1]['type']='home'

def offers_page():
 path='predlozheniya/index.html';rows=active_offers();countries=[c for c in D['countries']if any(o['country']==c['slug']for o in rows)]
 chips='<div class="filter-chips" role="group" aria-label="Страна">'+''.join(f'<button type="button" data-offer-filter="{v}" aria-pressed="{str(i==0).lower()}" data-goal="offers_filter_{v}">{E(t)}</button>'for i,(v,t)in enumerate([('all','Все')]+[(c['slug'],c['name'])for c in countries]))+'</div>'
 toolbar='<div class="offers-toolbar">'+chips+'<label class="field-label offers-sort"><span>Сортировка</span><select data-offer-sort data-goal="offers_sort"><option value="date">По дате вылета</option><option value="price">Сначала дешевле</option></select></label></div>'
 body=S('',toolbar+'<p class="sr-only" data-offer-status aria-live="polite"></p><div class="offer-grid offers-catalog" data-offers-list role="list">'+''.join(offer(path,o)for o in rows)+'</div>')
 emit(path,'Актуальные предложения — Mango Travel','Действующие предложения Mango Travel: маршруты, даты, отели и цены. Уточните условия поездки у персонального менеджера.','Актуальные предложения','Все действующие предложения в одном разделе.',body,[('Предложения',None)],raw=True,assets=['css/offers.css','js/offers.js'])
 active={o['id']for o in rows}
 for p in(C['SITE']/'predlozheniya').glob('*/index.html'):
  if p.parent.name not in active and'offer-detail-page'in p.read_text():p.unlink()
 for o in rows:
  path='predlozheniya/'+o['id']+'/index.html';country=next(c for c in D['countries']if c['slug']==o['country']);topic=offer_topic(o);settings(path)['topic']=topic;price=f'{o["price_from"]:,}'.replace(',',' ')
  cover='<section class="inner-cover offer-detail-cover" data-inner-cover><div class="container">'+C['crumb'](path,[('Предложения','predlozheniya/index.html'),(o['hotel'],None)])+f'<p class="eyebrow">{E(country["name"])} · {E(o["resort"])}</p><h1 {ED("offers."+o["id"]+".hotel",True)}>{E(o["hotel"])}</h1><div class="offer-detail-grid">'+C['image'](path,o['photo'],o['hotel'],False,key='offers.'+o['id']+'.photo')+'<div><p '+ED('offers.'+o['id']+'.details',True)+'>'+C['human_date'](o['departure_date'])+' · '+E(o['departure_city'])+f' · {o["nights"]} ночей · питание: '+E(o['meals'])+'</p><p '+ED('offers.'+o['id']+'.travellers',True)+'>'+E(o['travellers'])+' · цена на '+C['human_date'](o['price_date'])+'</p><p class="offer-detail-price" '+ED('offers.'+o['id']+'.price',True)+'>от '+price+' ₽</p>'+request_button('Уточнить предложение',topic,'offer_detail_request')+'</div></div></div></section>'
  body=S('Что входит и что учесть','<div class="offer-notes-grid">'+''.join('<article class="info-card" '+ED('offers.'+o['id']+'.'+key,True)+'><h3>'+title+'</h3>'+''.join('<p>'+E(v)+'</p>'for v in o[key])+'</article>'for key,title in [('includes','Что входит'),('notes','Что учесть')])+'</div>'+L(path,'predlozheniya/index.html','← Все предложения','offer_back','text-link'))
  emit(path,o['hotel']+' · '+o['resort']+' — Mango Travel','Предложение Mango Travel: '+topic+'. Уточните условия у менеджера.',o['hotel'],'',body,[('Предложения','predlozheniya/index.html'),(o['hotel'],None)],cover_override=cover,contact_override='',raw=True,page_class='offer-detail-page')

def extra_pages():
 path='kak-my-rabotaem/index.html';intro=''.join('<p '+ED('work.intro.'+str(i))+'>'+E(t)+'</p>'for i,t in enumerate(D['work']['intro']))
 cover='<section class="inner-cover" data-inner-cover><div class="container">'+C['crumb'](path,[('Как мы работаем',None)])+'<div class="article-column"><h1>Как мы работаем</h1><div class="approved-intro">'+intro+'</div></div></div></section>'
 body=''.join('<section class="section approved-section" id="'+s['id']+'"><div class="container"><div class="article-column"><h2 '+ED('work.'+s['id']+'.title')+'>'+E(s['title'])+'</h2>'+''.join('<p '+ED('work.'+s['id']+'.p.'+str(i))+'>'+E(p)+'</p>'for i,p in enumerate(s['paragraphs']))+'</div></div></section>'for s in D['work']['sections'])
 body='<div class="container work-layout"><div class="work-body">'+body.replace('<div class="container">','<div>')+'</div><aside class="work-toc" aria-label="Оглавление"><p>Как мы работаем</p>'+''.join('<a href="#'+v['id']+'" data-work-anchor data-goal="work_anchor_'+v['id']+'">'+E(v['title'])+'</a>'for v in D['work']['sections'])+'</aside></div>'
 emit(path,'Как мы работаем — Mango Travel','Подбор, подготовка и сопровождение путешествия с персональным менеджером Mango Travel. Как мы заботимся о Вашем отдыхе.','Как мы работаем','',body,[('Как мы работаем',None)],cover_override=cover,raw=True)
 path='o-nas/index.html';company='<div class="company-layout"><div class="company-placeholder" '+ED('about.photo',True)+' role="img" aria-label="Фото компании или команды"><span>MT</span></div><div><h3>Кто мы и как относимся к Вашему отдыху</h3><div class="editorial-text" '+ED('about.copy',True)+'><p>Мы работаем в туризме с 2010 года, а с 2017 года — под брендом Mango Travel.</p><p>'+E(D['contacts']['location'])+'</p><p>У каждого клиента есть персональный менеджер. Сравниваем предложения разных туроператоров и обсуждаем условия до выбора поездки.</p></div>'+L(path,'kak-my-rabotaem/index.html','Наш процесс работы →','about_process','text-link')+'</div></div>'
 body='<section class="section inner-section" id="company"><div class="container"><p class="eyebrow">Работаем в туризме с 2010 года</p><h2>О компании</h2>'+company+'</div></section><section class="section inner-section" id="team"><div class="container"><div class="section-head"><h2>Команда</h2></div>'+people(path)+'</div></section>'
 emit(path,'О нас — Mango Travel','О компании и команде Mango Travel: работаем в туризме с 2010 года. Персональный менеджер и забота о Вашем отдыхе.','О нас','',body,[('О нас',None)],about=True,raw=True)
 p='o-nas/komanda/index.html';(C['SITE']/p).write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Команда — Mango Travel</title><meta name="description" content="Команда Mango Travel на странице О нас."><meta http-equiv="refresh" content="0;url=../index.html#team"><link rel="canonical" href="https://devfriends.ru/o-nas/#team">'+C['brand_icons'](p)+'</head><body><h1>Команда Mango Travel</h1><a href="../index.html#team" data-goal="team_redirect">Познакомиться с командой →</a></body></html>\n');C['PAGES'].append({'path':p,'title':'Команда → О нас','type':'redirect'})
 path='o-nas/kontakty/index.html';body=S('','<div class="contact-cards"><article class="info-card"><h2>Напишите или позвоните</h2><div class="direct-contacts" '+ED('contacts.all')+'><a href="tel:+78512299547" data-goal="contacts_phone">+7 (8512) 29-95-47</a><a href="tel:+78512299527" data-goal="contacts_phone_secondary">+7 (8512) 29-95-27</a><a href="mailto:man.go.travel@mail.ru" data-goal="contacts_email">man.go.travel@mail.ru</a><p>'+E(D['contacts']['location'])+'</p><p>Пн–Пт 10:00–19:00<br>Сб 10:00–15:00 · Вс — выходной</p></div>'+channels(settings(path)['messengerText'],'contacts')+'</article><article class="info-card"><h2>Расскажите о планах</h2><p>Обсудим даты, состав поездки и то, что важно для Вашего отдыха.</p>'+request_button(key='contacts_request')+'</article></div>')
 emit(path,'Связь — Mango Travel','Телефоны, MAX, Telegram и обращение в Mango Travel. Астрахань: работаем онлайн по всей России.','Связь','',body,[('О нас','o-nas/index.html'),('Контакты',None)],about=True,contact_override='',raw=True)
 path='o-nas/otzyvy/index.html';emit(path,'Отзывы туристов — Mango Travel','Отзывы о путешествиях с Mango Travel: авторы и источники. Поделитесь впечатлениями на Яндексе или в 2ГИС.','Отзывы туристов','Реальные отзывы с указанием автора, даты и площадки.',S('',platforms()+reviews_grid()),[('О нас','o-nas/index.html'),('Отзывы',None)],about=True,raw=True)
 path='o-nas/dokumenty/index.html';cards=''
 for i,(title,target)in enumerate([('Реквизиты','#details'),('Документы для клиента','#client-documents'),('Политика обработки персональных данных','o-nas/dokumenty/politika/index.html'),('Согласие на обработку персональных данных','o-nas/dokumenty/soglasie/index.html')]):
  href=target if target.startswith('#')else U(path,target)
  cards+=f'<article class="document-card"'+(' id="client-documents"'if i==1 else'')+' '+ED('documents.'+str(i),True)+'>'+I('i-file')+'<h2>'+title+'</h2><p>Место для актуального документа</p><a class="text-link" href="'+href+'" data-goal="document_'+str(i)+'">Посмотреть →</a></article>'
 details=D['legal_details'];body=S('','<div class="document-grid">'+cards+'</div><div id="details" class="legal-details">'+details+'</div>')
 emit(path,'Документы — Mango Travel','Реквизиты, документы для клиента, политика и согласие на обработку персональных данных. Mango Travel.','Документы','',body,[('О нас','o-nas/index.html'),('Документы',None)],about=True,raw=True)
 for slug,title in [('politika','Политика обработки персональных данных'),('soglasie','Согласие на обработку персональных данных')]:
  path='o-nas/dokumenty/'+slug+'/index.html';emit(path,('Политика обработки данных'if slug=='politika'else'Согласие на обработку данных')+' — Mango Travel','Персональные данные: '+('политика обработки.'if slug=='politika'else'согласие на обработку.')+' Документ требует юридического согласования.',title,'',S('',D['legal_body'][slug]),[('О нас','o-nas/index.html'),('Документы','o-nas/dokumenty/index.html'),(title,None)],about=True,raw=True)
 path='voprosy/index.html';groups=[('selection','Подбор',[0,2]),('booking','Бронирование и оплата',[1,3]),('documents','Документы',[4]),('during-trip','В поездке',[5])];nav='<nav class="faq-group-nav" aria-label="Группы вопросов">'+''.join(f'<a href="#{id}" class="rest-pill rest-pill-outline" data-goal="faq_group_{id}">{title}</a>'for id,title,_ in groups)+'</nav>';body='<div class="container">'+nav+'</div>'+''.join(f'<section class="section inner-section" id="{id}"><div class="container"><div class="section-head"><h2>{title}</h2></div>'+faq_html([D['faq'][i]for i in indices],'faq_'+id)+'</div></section>'for id,title,indices in groups)
 emit(path,'Частые вопросы — Mango Travel','Ответы Mango Travel о подборе, бронировании, оплате, документах и помощи в поездке.','Частые вопросы','',body,[('Частые вопросы',None)],questions=D['faq'],raw=True)
 path='404.html';emit(path,'Страница не найдена — Mango Travel','Страница не найдена. Выберите раздел или свяжитесь с Mango Travel.','Страница не найдена','Давайте найдём нужную страницу.',S('',L(path,'index.html','На главную →','404_home','text-link')+' '+L(path,'o-nas/kontakty/index.html','Связаться с нами →','404_contact','text-link')),[('Страница не найдена',None)],raw=True)
 offers_page()
 path='pages.html';body=S('Страницы сайта','<div class="page-directory">'+''.join(L(path,p['path'],E(brand(p['title']))+' <small>'+p['path']+'</small>','directory_'+str(i))for i,p in enumerate(C['PAGES']))+'</div>');emit(path,'Страницы сайта — Mango Travel','Техническое оглавление страниц Mango Travel.','Страницы сайта','',body,[('Страницы',None)],raw=True)

def finalize(path):
 p=C['SITE']/path;h=p.read_text()
 if 'redirect'==next((x['type']for x in C['PAGES']if x['path']==path),''):return
 h=re.sub(r'<div class="section-head"><h2[^>]*>\s*</h2></div>','',h)
 h=h.replace('#soprovozhdenie','#support').replace('#komanda','#team')
 h=re.sub(r'<dialog class="contact-dialog".*?</dialog>','',h,flags=re.S)
 h=re.sub(r'<div class="mobile-contact".*?</div>',lambda m:'<div class="mobile-contact" data-mobile-contact hidden>'+request_button(topic=settings(path)['topic'],key='mobile_request').replace('>Обсудить поездку</button>','>'+I('i-message')+'Обсудить поездку</button>')+'</div>',h,flags=re.S)
 # Request actions formerly scrolled to the legacy end-of-page form.
 def actions(m):
  attrs,content=m[1],m[2]
  if'href="#contact"'in attrs and'data-rest-select'not in attrs:attrs+=' data-request data-topic="'+E(settings(path)['topic'])+'"'
  if'data-messenger='in attrs:
   text=re.search(r'data-message="([^"]*)"',attrs);value=brand(unescape(text[1]))if text else brand(settings(path)['messengerText'])
   attrs=re.sub(r'\sdata-message="[^"]*"','',attrs)+' data-message="'+E(value)+'"'
  return '<a'+attrs+'>'+content+'</a>'
 h=re.sub(r'<a\b([^>]*)>(.*?)</a>',actions,h,flags=re.S)
 h=h.replace('</head>',f'<link rel="stylesheet" href="{U(path,"css/online.css")}"><link rel="stylesheet" href="{U(path,"css/stage4.css")}"><link rel="stylesheet" href="{U(path,"css/stage5.css")}"><script defer src="{U(path,"js/stage5.js")}"></script></head>')
 backup='<dialog id="messenger-fallback" class="messenger-fallback" aria-modal="true" aria-labelledby="fallback-title"><div class="dialog-top"><h2 id="fallback-title">Сообщение менеджеру</h2><button type="button" class="icon-btn" data-dialog-close data-goal="fallback_close" aria-label="Закрыть сообщение">'+I('i-close')+'</button></div><p>Скопируйте текст и вставьте его в чат.</p><textarea data-fallback-text rows="6" readonly aria-label="Текст сообщения"></textarea><button type="button" class="btn btn-outline" data-copy-message data-goal="message_copy">Скопировать текст</button><p data-copy-status role="status"></p><a href="tel:+78512299547" data-goal="fallback_phone">+7 (8512) 29-95-47</a></dialog>'
 config={'telegramUsername':D['contacts']['telegramUsername'],'max':D['contacts']['max'],'context':brand(settings(path)['messengerText']),'topic':settings(path)['topic']}
 h=h.replace('</body>',request_dialog(path)+(selection_dialog(path)if path=='index.html'else'')+backup+'<script type="application/json" id="online-config">'+json.dumps(config,ensure_ascii=False).replace('<','\\u003c')+'</script></body>')
 # Leave legal operator text untouched, but rebrand navigation, metadata and logos.
 legal=[]
 if path.startswith('o-nas/dokumenty/'):
  h=re.sub(r'<(?:article class="legal-copy"|dl class="details-list")[\s\S]*?</(?:article|dl)>',lambda m:(legal.append(m[0])or'LEGAL_OPERATOR_'+str(len(legal)-1)),h)
 h=brand(h)
 for i,t in enumerate(legal):h=h.replace('LEGAL_OPERATOR_'+str(i),t)
 # Correct all schema agency names and keep online-only geography.
 def schema(m):
  obj=json.loads(m[1]);
  def visit(v):
   if isinstance(v,dict):
    if v.get('@type')=='TravelAgency':v['name']='Mango Travel';v['address']={'@type':'PostalAddress','addressLocality':'Астрахань','addressCountry':'RU'};v['areaServed']='RU'
    for x in v.values():visit(x)
   elif isinstance(v,list):
    for x in v:visit(x)
  visit(obj);return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False)+'</script>'
 h=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,h,flags=re.S)
 online.MessageValidator().check(h);p.write_text(h)
