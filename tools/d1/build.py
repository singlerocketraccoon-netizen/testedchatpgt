#!/usr/bin/env python3
"""Build the d1 static site. Python stdlib; no network, frameworks or build dependencies."""
from pathlib import Path
from string import Template
from html import escape
import json,re,os
ROOT=Path(__file__).resolve().parents[2];TOOLS=Path(__file__).resolve().parent;SITE=ROOT/'docs/scheme2/d1';DATA=json.loads((TOOLS/'data.json').read_text());HOME=(TOOLS/'templates/home-source.html').read_text();COUNTRIES=DATA['countries'];SERVICES=DATA['services'];PAGES=[]
E=lambda s:escape(str(s),quote=True)
def formal(s):
 for a,b in [('вариантов','предложений'),('вариантами','предложениями'),('вариантам','предложениям'),('варианты','предложения'),('вариант','предложение')]:s=s.replace(a,b)
 for a,b in [('вам','Вам'),('вас','Вас'),('вами','Вами'),('ваш','Ваш'),('ваши','Ваши'),('вашим','Вашим'),('вашего','Вашего'),('ваше','Ваше'),('ваших','Ваших')]:s=re.sub(r'\b'+a+r'\b',b,s)
 return s
def url(path,target='index.html'):
 return os.path.relpath(SITE/target,(SITE/path).parent).replace(os.sep,'/')
def icon(name):return f'<svg class="icon" aria-hidden="true"><use href="#{name}"></use></svg>'
def link(path,target,label,goal,cls='',extra=''):
 return f'<a href="{url(path,target)}" class="{cls}" data-goal="{goal}" {extra}>{label}</a>'
def editable(key,approval=False):return f'data-editable="{key}"'+(' data-needs-approval="owner-review"'if approval else'')
def section(title,body,key='',cls=''):
 return f'<section class="section inner-section {cls}"><div class="container"><div class="section-head"><h2 {editable(key)if key else""}>{title}</h2></div>{body}</div></section>'
def card(title,text,key,ico='i-mood-compass',approval=False):
 return f'<article class="info-card" {editable(key,approval)}>{icon(ico)}<h3>{title}</h3><p>{text}</p></article>'
EXTRA_ICONS={
'i-message':'<path d="M21 12a8 8 0 0 1-8 8H5l-3 2V6a4 4 0 0 1 4-4h11a4 4 0 0 1 4 4v6ZM7 8h10M7 12h7"/>',
'i-lounge':'<path d="M5 11V6a3 3 0 0 1 3-3h8a3 3 0 0 1 3 3v5M5 11a2 2 0 0 0-2 2v5h18v-5a2 2 0 0 0-4 0v2H7v-2a2 2 0 0 0-2-2ZM6 18v3m12-3v3"/>',
'i-ship':'<path d="M4 10h16l-2 8H6l-2-8Zm3 0V6h10v4M10 6V3h4v3M2 21c3-2 4 2 7 0s4 2 7 0 4 2 6 0"/>',
'i-plane':'<path d="m3 10 7 1 4-8 3 1-2 8 6 3-1 2-7-1-4 5-2-1 2-5-7-3 1-2Z"/>',
'i-train':'<rect x="5" y="3" width="14" height="16" rx="3"/><path d="M5 10h14M12 3v7M7 19l-2 3m12-3 2 3M8 15h1m6 0h1"/>',
'i-bus':'<rect x="4" y="3" width="16" height="16" rx="3"/><path d="M4 11h16M12 3v8M7 15h1m8 0h1M7 19v3m10-3v3M1 8v5m22-5v5"/>',
'i-car':'<path d="m5 10 2-6h10l2 6M3 10h18v9H3v-9ZM6 19v3m12-3v3M6 14h2m8 0h2"/>',
'i-shield':'<path d="m12 2 8 3v6c0 5-4 8-8 11-4-3-8-6-8-11V5l8-3Zm-4 9 3 3 5-6"/>',
'i-file':'<path d="M6 2h8l5 5v15H6V2Zm8 0v6h5M9 12h7m-7 4h7"/>',
'i-pin':'<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
'i-calendar':'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 2v6m10-6v6M3 11h18m-14 4h2m4 0h2"/>'}
SPRITE=re.search(r'<svg class="sprite".*?</svg>',HOME,re.S)[0];SPRITE=SPRITE.replace('</svg>',''.join(f'<symbol id="{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">{v}</symbol>'for k,v in EXTRA_ICONS.items())+'</svg>')
def brand_path(path,key):return url(path,'img/'+DATA['branding'][key])

def brand_icons(path):
 b=DATA['branding']
 return f'<link rel="icon" type="image/png" sizes="32x32" href="{url(path,"img/"+b["favicon"])}"><link rel="icon" type="image/png" sizes="512x512" href="{url(path,"img/"+b["icon512"])}"><link rel="icon" type="image/svg+xml" href="{url(path,"img/"+b["mark"])}"><link rel="apple-touch-icon" sizes="180x180" href="{url(path,"img/"+b["apple"])}">'

def navitems(path,kind):
 if kind=='countries':return ''.join(link(path,f'napravleniya/{c["slug"]}/index.html',E(c['name']),'nav_country_'+c['slug'])for c in COUNTRIES)
 if kind=='services':return ''.join(link(path,f'uslugi/{s["slug"]}/index.html',icon(s['icon'])+E(s['name']),'nav_service_'+s['slug'])for s in SERVICES)
 return ''.join(link(path,t,label,'nav_about_'+str(i))for i,(label,t)in enumerate([('О нас','o-nas/index.html'),('Команда','o-nas/komanda/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html'),('Отзывы','o-nas/otzyvy/index.html')]))
def dropdown(path,label,kind):
 title={'countries':'Страны','services':'Услуги','about':'Об агентстве'}[kind];alltarget={'countries':'napravleniya/index.html','services':'uslugi/index.html','about':'o-nas/index.html'}[kind]
 return f'<div class="nav-dropdown"><button type="button" data-nav-toggle aria-expanded="false" aria-controls="nav-{kind}" data-goal="nav_{kind}_toggle" disabled>{label}{icon("i-down")}</button><div class="dropdown-panel" id="nav-{kind}" hidden><p class="dropdown-label">{title}</p><div class="dropdown-grid">{navitems(path,kind)}</div>{link(path,alltarget,"Все страны →"if kind=="countries"else"Все услуги →"if kind=="services"else"Об агентстве →","nav_"+kind+"_all","text-link")}</div></div>'
def header(path,photo=False):
 groups=''.join(f'<details class="mobile-group"><summary data-goal="mobile_{kind}">{name}{icon("i-down")}</summary><div class="mobile-submenu">{navitems(path,kind)}{link(path,target,"Все страны →"if kind=="countries"else"Все услуги →"if kind=="services"else"О нас →","mobile_"+kind+"_all")}</div></details>'for name,kind,target in [('Страны','countries','napravleniya/index.html'),('Услуги','services','uslugi/index.html'),('О нас','about','o-nas/index.html')])
 return f'''<!-- component: header --><header class="site-header d1-header{' is-solid'if not photo else''}" data-site-header><div class="header-inner"><nav class="nav-left" aria-label="Страны и услуги">{dropdown(path,'Страны','countries')}{dropdown(path,'Услуги','services')}</nav><a href="{url(path)}" class="brand" data-goal="home" data-editable="brand.logo" aria-label="Манго Путешествия — главная"><img class="logo-dark" src="{brand_path(path,'logo')}" alt="Манго Путешествия" width="1193" height="440"><img class="logo-light" src="{brand_path(path,'light')}" alt="" aria-hidden="true" width="1193" height="440"></a><nav class="nav-about" aria-label="Об агентстве">{link(path,'kak-my-rabotaem/index.html','Как мы работаем','nav_process')}{dropdown(path,'О нас','about')}</nav><div class="header-contacts"><a class="header-phone icon-control" href="tel:+78512299547" aria-label="Позвонить: +7 (8512) 29-95-47" data-goal="phone_header" data-editable="contacts.primaryPhone">{icon('i-phone')}<span>+7 (8512) 29-95-47</span></a><a class="icon-control" href="#" aria-label="Написать в MAX" data-messenger="MAX" data-goal="messenger_max_header" data-editable="contacts.max">{icon('i-max')}</a><a class="icon-control" href="#" aria-label="Написать в Telegram" data-messenger="Telegram" data-goal="messenger_telegram_header" data-editable="contacts.telegram">{icon('i-telegram')}</a><button type="button" class="icon-control menu-toggle" aria-label="Открыть меню" aria-controls="mobile-nav" aria-expanded="false" data-menu data-goal="menu_toggle" disabled>{icon('i-menu')}</button></div></div><nav id="mobile-nav" class="mobile-nav" aria-label="Мобильное меню" hidden>{groups}{link(path,'kak-my-rabotaem/index.html','Как мы работаем','mobile_process','mobile-direct-link')}<p class="mobile-contact-caption">Обсудим Ваш отдых</p><a class="mobile-contact-number" href="tel:+78512299547" data-goal="mobile_phone">+7 (8512) 29-95-47</a></nav><noscript><p class="nav-nojs">{link(path,'napravleniya/index.html','Страны','nojs_directions')} · {link(path,'uslugi/index.html','Услуги','nojs_services')} · {link(path,'o-nas/index.html','О нас','nojs_about')}</p></noscript></header><!-- /component: header -->'''
URL_MAP={'../../napravleniya/index.html':'napravleniya/index.html','../../otzyvy/index.html':'o-nas/otzyvy/index.html','../../o-nas/index.html':'o-nas/index.html','../../rekvizity/index.html':'o-nas/dokumenty/index.html','../../dokumenty/index.html':'o-nas/dokumenty/index.html','../../politika-konfidencialnosti/index.html':'o-nas/dokumenty/politika/index.html','../../soglasie/index.html':'o-nas/dokumenty/soglasie/index.html','#directions':'napravleniya/index.html','#process':'kak-my-rabotaem/index.html','#team':'o-nas/index.html','#voices':'o-nas/otzyvy/index.html'}
def remap(s,path,home=False):
 for old,new in URL_MAP.items():s=s.replace('href="'+old+'"','href="'+url(path,new)+'"')
 return s
FOOTER=re.search(r'<!-- component: footer -->.*?<!-- /component: footer -->',HOME,re.S)[0]
def footer(path,home=False):
 f=FOOTER;f=re.sub(r'<span class="brand-name">.*?</span>',f'<img src="{brand_path(path,"light")}" alt="Манго Путешествия" width="1193" height="440" loading="lazy">',f,count=1,flags=re.S)
 f=f.replace('href="index.html"','href="'+url(path)+'"');f=re.sub(r'<button class="nav-link" type="button" data-services-open data-goal="footer_services" disabled>Услуги</button>',link(path,'uslugi/index.html','Услуги','footer_services','nav-link'),f)
 f=f.replace('data-goal="footer_directions">Страны</a>','data-goal="footer_directions">Страны</a>'+link(path,"predlozheniya/index.html","Предложения","footer_offers"))
 f=remap(f,path);return f if home else f.replace(' data-home-block="11"','')
CONTACT=re.search(r'<!-- component: discussion-form -->.*?<!-- /component: discussion-form -->',HOME,re.S)[0]
SHEET=re.search(r'<dialog class="contact-dialog".*?</dialog>',HOME,re.S)[0]
TOAST=re.search(r'<div class="toast".*?</div>',HOME,re.S)[0]
MOBILE=re.search(r'<div class="mobile-contact".*?</div>',HOME,re.S)[0]
def contact(path,prefill=''):
 s=formal(remap(CONTACT,path)).replace(' data-home-block="09"','');s=s.replace('name="destination" type="text"','name="destination" type="text" value="'+E(prefill)+'"');s=s.replace('data-discussion-form novalidate','data-discussion-form data-prefill="'+E(prefill)+'" novalidate');return s

def image(path,name,alt,lazy=True,cls='',key='media'):
 target='img/'+name[1:]if name.startswith('@')else'../../assets/img/'+name
 w,h=DATA['image_dimensions'][name]
 return f'<img src="{url(path,target)}" alt="{E(alt)}" width="{w}" height="{h}"'+(' loading="lazy"'if lazy else' fetchpriority="high"')+f' decoding="async" class="{cls}" data-editable="{key}">'
def crumb(path,items):
 return '<nav class="breadcrumbs" aria-label="Хлебные крошки"><ol>'+''.join('<li>'+ (link(path,target,E(label),'breadcrumb_'+str(i))if target else f'<span aria-current="page">{E(label)}</span>')+'</li>'for i,(label,target)in enumerate([('Главная','index.html')]+items))+'</ol></nav>'
def aboutnav(path):
 return '<nav class="section-tabs" aria-label="Раздел об агентстве">'+''.join(link(path,target,label,'about_tab_'+str(i),extra='aria-current="page"'if path==target else'')for i,(label,target)in enumerate([('О нас','o-nas/index.html'),('Команда','o-nas/komanda/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html'),('Отзывы','o-nas/otzyvy/index.html')]))+'</nav>'
def faq(items,key):
 return '<div class="faq-list">'+''.join(f'<details class="faq-item" {editable(key+"."+str(i),True)}><summary data-goal="{key}_question_{i}">{E(q)}{icon("i-plus")}</summary><p>{E(a)}</p></details>'for i,(q,a)in enumerate(items))+'</div>'
def agency():return {'@type':'TravelAgency','@id':'https://devfriends.ru/#agency','name':'Манго Путешествия','telephone':['+7-8512-29-95-47','+7-8512-29-95-27'],'email':'man.go.travel@mail.ru','address':{'@type':'PostalAddress','addressLocality':'Астрахань','streetAddress':'ул. Кирова, 14, ТЦ «Арбат», 1 этаж','addressCountry':'RU'},'openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday'],'opens':'10:00','closes':'19:00'},{'@type':'OpeningHoursSpecification','dayOfWeek':'Saturday','opens':'10:00','closes':'15:00'}]}
def emit(path,title,description,h1,intro,body,items,prefill='',photo=None,questions=None,about=False,approval_intro=False,raw=False,cover_override=None,contact_override=None,page_class='',page_script='js/inner.js',assets=None):
 metadata=DATA.get('page_overrides',{}).get(path,{})
 title=metadata.get('title',title);description=metadata.get('description',description);display_h1=metadata.get('h1',h1)
 assert len(title)<=60,(path,title,len(title));assert len(description)<=160
 canonical='https://devfriends.ru/'+(''if path=='index.html'else path.removesuffix('index.html'))
 graph=[{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':label,'item':'https://devfriends.ru/'+target.replace('index.html','')}for i,(label,target)in enumerate([('Главная','index.html')]+[(a,b or path)for a,b in items])]}]
 if about:graph.append(agency())
 if questions:graph.append({'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}}for q,a in questions]})
 head=f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#F6F1E9"><title>{E(title)}</title><meta name="description" content="{E(description)}"><meta name="robots" content="noindex,follow"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://devfriends.ru/img/icon-512.png">{brand_icons(path)}<link rel="stylesheet" href="{url(path,'css/fonts.css')}"><link rel="stylesheet" href="{url(path,'css/main.css')}"><link rel="stylesheet" href="{url(path,'css/navigation.css')}"><link rel="stylesheet" href="{url(path,'css/inner.css')}"><script defer src="{url(path,'js/navigation.js')}"></script><script defer src="{url(path,page_script)}"></script><script type="application/ld+json">{json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False)}</script></head><body class="inner-page{' inner-plain'if not photo else''}{' legal-page'if '/dokumenty/politika/'in path or '/dokumenty/soglasie/'in path else''}{' '+page_class if page_class else''}" data-page="{E(path)}">'''
 introtext=f'<p class="inner-lead" {editable(path+".intro",approval_intro)}>{intro}</p>'
 if photo:
  cover=f'<section class="country-cover" data-inner-cover>{image(path,photo[0],photo[1],False,key=path+".hero")}<div class="container">{crumb(path,items)}<div class="country-title"><p class="eyebrow">Отдых в Вашем ритме</p><h1 {editable(path+".title")}>{display_h1}</h1>{introtext}<a class="btn btn-primary" href="#contact" data-goal="country_contact">Обсудить поездку {icon("i-arrow")}</a></div></div></section>'
 else:cover=f'<section class="inner-cover" data-inner-cover><div class="container">{crumb(path,items)}<h1 {editable(path+".title")}>{display_h1}</h1>{introtext}</div></section>'
 if cover_override is not None:cover=cover_override
 if assets:
  head=head.replace('</head>',''.join((f'<script defer src="{url(path,a)}"></script>'if a.endswith('.js')else f'<link rel="stylesheet" href="{url(path,a)}">')for a in assets)+'</head>')
 tabs=f'<div class="container">{aboutnav(path)}</div>'if about else''
 sheet=formal(remap(SHEET,path));html=head+SPRITE+header(path,bool(photo))+'<a class="skip-link" href="#main" data-goal="skip_content">К содержимому</a><main id="main">'+cover+tabs+body+(contact_override if contact_override is not None else contact(path,prefill))+'</main>'+footer(path)+MOBILE+sheet+TOAST+'</body></html>\n'
 out=SITE/path;out.parent.mkdir(parents=True,exist_ok=True);rendered=html if raw else formal(html)
 for review in DATA['reviews']:rendered=rendered.replace(E(formal(review['text'])),E(review['text']))
 out.write_text(rendered);PAGES.append({'path':path,'title':h1,'type':'country'if photo else'page'})

def countrycard(path,c):
 tags='|'.join(c['tags']);return f'<!-- component: direction-card --><article class="country-card" data-filter-item data-categories="{E(tags)}" {editable("countries."+c["slug"])}>{link(path,"napravleniya/"+c["slug"]+"/index.html",image(path,c["image"],c["alt"])+f"<div class=\"country-card-body\"><h3>{c['name']}</h3><p>{c['intro']}</p><p class=\"country-months\">Месяцы для отдыха: "+', '.join(['янв','фев','мар','апр','май','июн','июл','авг','сен','окт','ноя','дек'][i]for i,v in enumerate(c['months'])if v=='good')+f"</p><span class=\"country-price\" data-needs-approval=\"price\">от {c['price']:,} ₽ <small>за двоих</small></span></div>".replace(',', ' '),'country_'+c['slug'])}</article><!-- /component: direction-card -->'
def filters(values,key):
 return '<div class="filter-chips" role="group" aria-label="Фильтр">'+''.join(f'<button type="button" data-filter="{E(v)}" aria-pressed="{"true"if i==0 else"false"}" data-goal="{key}_filter" {editable(key+".filters."+str(i))}>{E(v)}</button>'for i,v in enumerate(['Все']+values))+'</div>'
MONTH_NAMES=['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
def human_date(value):
 year,month,day=map(int,value.split('-'));return f'{day} {MONTH_NAMES[month-1]} {year}'
def active_offers(country=None):return [o for o in DATA['offers']if o['active']and(country is None or o['country']==country)]
def offer(path,o):
 c=next(c for c in COUNTRIES if c['slug']==o['country']);key='offers.'+o['id'];title=f'{c["name"]} · {o["resort"]} · {o["hotel"]} · {o["stars"]}★';topic=title+' · '+human_date(o['departure_date'])+f' · {o["nights"]} ночей · вылет: '+o['departure_city'];price=f'{o["price_from"]:,}'.replace(',',' ')
 return f'<!-- component: offer-card --><article class="offer-card" role="listitem" data-offer-id="{E(o["id"])}" data-country="{o["country"]}" data-price="{o["price_from"]}" data-date="{o["departure_date"]}" {editable(key,True)}><a class="offer-link" href="#contact" data-offer="{E(topic)}" data-contact-topic="{E(topic)}" data-goal="offer_discuss">{image(path,o["photo"],c["name"]+" — формат отдыха",key=key+".photo")}<div class="offer-body"><h3 {editable(key+".title")}>{E(title)}</h3><p class="offer-meta" {editable(key+".details")}><time datetime="{o["departure_date"]}">{human_date(o["departure_date"])}</time> · {o["nights"]} ночей · {E(o["departure_city"])}</p><p class="offer-price" {editable(key+".price",True)}>от {price} ₽ <small>за двоих</small></p><p class="price-date" {editable(key+".priceDate",True)}>Цена на {human_date(o["price_date"])}, актуальную уточнит менеджер</p><span class="offer-action">Обсудить поездку {icon("i-arrow")}</span></div></a></article><!-- /component: offer-card -->'
def home_offers():
 controls=f'<div class="offer-controls"><button type="button" class="icon-btn" data-offers-prev aria-label="Предыдущие предложения" aria-controls="home-offers" data-goal="offers_previous" disabled>{icon("i-arrow-left")}</button><button type="button" class="icon-btn" data-offers-next aria-label="Следующие предложения" aria-controls="home-offers" data-goal="offers_next" disabled>{icon("i-arrow")}</button></div>'
 return '<section class="section offers-section home-offer-carousel" data-home-block="03" id="offers" data-offer-carousel><div class="container"><div class="section-head"><h2 data-editable="home.sections.03.title">Актуальные предложения</h2>'+controls+'</div><div class="offer-grid scroll-rail" id="home-offers" role="list" aria-label="Актуальные предложения" tabindex="0">'+''.join(offer('index.html',o)for o in active_offers())+'</div>'+link('index.html','predlozheniya/index.html','Все предложения →','all_offers','text-link offers-all')+'</div></section>'
def offers_page():
 path='predlozheniya/index.html';rows=active_offers();countries=[c for c in COUNTRIES if any(o['country']==c['slug']for o in rows)]
 chips='<div class="filter-chips" role="group" aria-label="Страна">'+''.join(f'<button type="button" data-offer-filter="{value}" aria-pressed="{str(i==0).lower()}" data-goal="offers_filter_{value}" {editable("offers.filters."+value)}>{E(label)}</button>'for i,(value,label)in enumerate([('all','Все')]+[(c['slug'],c['name'])for c in countries]))+'</div>'
 sort='<label class="field-label offers-sort"><span>Сортировка</span><select data-offer-sort data-goal="offers_sort"><option value="date">По дате вылета</option><option value="price">Сначала дешевле</option></select></label>'
 body='<section class="section inner-section offers-list-section"><div class="container"><div class="offers-toolbar">'+chips+sort+'</div><p class="sr-only" data-offer-status aria-live="polite"></p><div class="offer-grid offers-catalog" data-offers-list role="list">'+''.join(offer(path,o)for o in sorted(rows,key=lambda o:o['departure_date']))+'</div></div></section>'
 emit(path,'Предложения туров из Астрахани — Манго','Туры из Астрахани и других городов вылета: сравните страны, даты и цены. Обсудите выбранную поездку с персональным менеджером.','Актуальные предложения','Выберите страну и удобные даты — детали обсудим с Вашим менеджером.',body,[('Предложения',None)],'Хочу обсудить предложение',assets=['css/offers.css','js/offers.js'])

def country(c):
 slug=c['slug'];path=f'napravleniya/{slug}/index.html';key='countries.'+slug
 facts=[('Столица',c['capital'],False),('Валюта',c['currency'],False),('Язык',c['language'],False),('Виза','Проверим правила въезда',True),('Перелёт','Зависит от маршрута',True),('Время',c['time']+' от Астрахани'if c['time']!='Как в Астрахани'else c['time'],True)]
 body='<section class="facts-strip"><div class="container fact-grid">'+''.join(f'<div {editable(key+".facts."+str(i),a)}><span>{label}</span><strong>{value}</strong></div>'for i,(label,value,a)in enumerate(facts))+'</div></section>'
 months=['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек'];states={'good':'Комфортно','hot':'Жарко','shoulder':'Межсезонье'}
 body+=section('Когда ехать','<p class="section-description" '+editable(key+'.season')+'>'+c['season']+'</p><div class="month-scale">'+''.join(f'<div class="month {state}" aria-label="{month}: {states[state]}" {editable(key+".months."+str(i))}><span>{month}</span><i aria-hidden="true"></i><small>{states[state]}</small></div>'for i,(month,state)in enumerate(zip(months,c['months'])))+'</div><p class="season-legend">Комфортно · Жарко · Межсезонье</p>',key+'.seasonTitle')
 body+=section('Курорты и места','<div class="info-grid">'+''.join(card(name,['Для поездки к морю и прогулок.','Обсудим расположение отеля и привычный ритм отдыха.','Выберем формат под Ваш маршрут.'][i],key+'.resorts.'+str(i),'i-pin',True)for i,name in enumerate(c['resorts']))+'</div>',key+'.resortsTitle')
 if DATA.get('show_country_offers') and active_offers(slug):body+=section('Актуальные предложения','<div class="offer-grid" role="list">'+''.join(offer(path,o)for o in active_offers(slug))+'</div>',key+'.offersTitle','cream-section')
 body+=section('Что важно знать','<div class="info-grid">'+card('Документы','До оплаты проверим правила въезда для Вашего гражданства и документа. Требования могут изменяться.',key+'.visa','i-file',True)+card('Дорога','Вылет и стыковки подбираются на даты поездки. Астрахань, Волгоград, Москва, Краснодар и Ростов-на-Дону — города для проверки маршрутов.',key+'.flight','i-plane',True)+card('Бюджет','Сравнивайте весь состав поездки: питание, дорогу, багаж и переезды. Цену подтвердим перед оформлением.',key+'.budget','i-mood-cloche',True)+'</div>')
 questions=[(f'Когда планировать поездку {c["preposition"]} {c["accusative"]}?',c['season']),('Нужна ли виза?','Проверим актуальные требования к въезду для Вашего гражданства и паспорта перед бронированием.'),('Можно ли вылететь из Астрахани?','Проверим маршруты на Ваши даты. При необходимости сравним другие разрешённые города вылета; прямой рейс заранее не обещаем.')]
 body+=section('Вопросы о поездке',faq(questions,key+'.faq'))
 body+=section('Обсудим Ваш маршрут',f'<div class="inline-contact"><p>Персональный менеджер поможет сравнить варианты.</p><a class="text-link" href="#contact" data-goal="country_selection">Подобрать тур {c["preposition"]} {c["accusative"]} →</a><a href="#" data-messenger="MAX" data-goal="country_max">MAX</a><a href="#" data-messenger="Telegram" data-goal="country_telegram">Telegram</a></div>')
 body+=section('Другие направления','<div class="related-links">'+''.join(link(path,'napravleniya/'+v['slug']+'/index.html',v['name']+' →','related_country_'+v['slug'])for v in COUNTRIES if v['slug']!=slug)+'</div>')
 emit(path,f'Туры {c["preposition"]} {c["accusative"]} из Астрахани — Манго',f'Отдых {c["preposition"]} {c["locative"]}: сезоны, курорты и подбор поездки в Астрахани. Обсудите даты, маршрут и отель с персональным менеджером.',f'Туры {c["preposition"]} {c["accusative"]}',c['intro'],body,[('Страны','napravleniya/index.html'),(c['name'],None)],c['name'],photo=(c['image'],c['alt']),questions=questions)

def service(s):
 slug=s['slug'];path=f'uslugi/{slug}/index.html';key='services.'+slug
 body=section('Кому подходит','<div class="editorial-text" '+editable(key+'.audience',True)+'><p>'+s['audience']+'</p></div>')
 body+=section('Что делаем мы','<div class="info-grid">'+''.join(card(str(i+1).zfill(2),txt,key+'.actions.'+str(i),s['icon'],True)for i,txt in enumerate(s['actions']))+'</div>','', 'cream-section')
 body+=section('Как проходит','<ol class="service-steps">'+''.join(f'<li {editable(key+".steps."+str(i),True)}><span>0{i+1}</span><h3>{txt}</h3><p>{["Расскажите о датах, маршруте и важных деталях.","Сравним доступные варианты и разберём условия.","Проверим детали перед подтверждением и оплатой."][i]}</p></li>'for i,txt in enumerate(s['steps']))+'</ol>')
 body+=section('Почему с нами','<div class="info-grid">'+card('Ваш менеджер','Один персональный менеджер ведёт Ваш запрос.',key+'.why.manager','i-mood-family')+card('Разные предложения','Не зависим от одного туроператора.',key+'.why.choice','i-mood-compass')+card('Понятные условия','Цены как у туроператоров, без скрытых доплат.',key+'.why.price','i-file')+'</div>')
 body+=section('Стоимость','<div class="price-note" '+editable(key+'.price')+'><h3>Рассчитаем под Ваш запрос</h3><p>Назовите даты и важные детали — обсудим состав и условия до оформления.</p><a href="#contact" class="text-link" data-goal="service_price">Узнать условия →</a></div>','', 'cream-section')
 questions=[(s['question'],s['answer']),('С чего начать?','Оставьте контакт и кратко опишите запрос. Персональный менеджер обсудит с Вами даты, пожелания и следующие шаги.'),('Можно ли оформить дистанционно?','Обсудить запрос можно в MAX, Telegram или по телефону. Порядок оформления и документы согласуем отдельно.')]
 body+=section('Частые вопросы',faq(questions,key+'.faq'))
 body+=section('Другие услуги','<div class="related-links">'+''.join(link(path,'uslugi/'+v['slug']+'/index.html',icon(v['icon'])+v['name'],'related_service_'+v['slug'])for v in SERVICES if v['slug']!=slug)+'</div>')
 emit(path,s['name']+' в Астрахани — Манго Путешествия',s['intro']+' Подбор и обсуждение условий с персональным менеджером в Астрахани.',s['name'],s['intro'],body,[('Услуги','uslugi/index.html'),(s['name'],None)],s['name'],questions=questions,approval_intro=True)


def home_rest():
 path='index.html';rest=DATA['home_rest']
 def restcard(c,i):
  key='home.rest.cards.'+str(i);target='#quiz-dialog'if c.get('choice')else url(path,c['target'])
  extra=' data-quiz-open'+(' data-preselect="'+E(c['preselect'])+'"'if c.get('preselect')else'')if c.get('choice')else(' data-future-page'if c.get('future')else'')
  return f'<!-- component: mood-card --><a class="mood-choice rest-card" href="{target}" data-goal="mood_{c["slug"]}" {editable(key)}{extra}><div class="rest-photo">{image(path,c["image"],c["alt"],key=key+".photo")}</div><span class="rest-caption"><span class="rest-symbol" {editable(key+".icon")} data-icon="{c["icon"]}">{icon(c["icon"])}</span><span class="rest-copy"><span class="rest-label" {editable(key+".label")}>{E(c["label"])}</span><span class="rest-card-subtitle" {editable(key+".subtitle")}>{E(c["subtitle"])}</span></span>{icon('i-arrow')}</span></a><!-- /component: mood-card -->'
 cards=[restcard(c,i)for i,c in enumerate(rest['cards'])]
 return f'<section class="section mood-section rest-section" data-home-block="02" id="moods"><div class="container"><div class="section-head"><h2 {editable("home.sections.02.title")}>{E(rest["title"])}</h2><p class="mood-subtitle" {editable("home.sections.02.subtitle")}>{E(rest["subtitle"])}</p></div><div class="mood-grid rest-grid">'+''.join(cards[:6])+f'</div><div class="mood-more" id="more-rest" hidden><div class="mood-grid rest-grid">'+''.join(cards[6:])+f'</div></div><div class="rest-actions"><button type="button" class="rest-pill rest-pill-outline" data-rest-toggle data-goal="rest_more" aria-expanded="false" aria-controls="more-rest" disabled><span data-rest-toggle-label {editable("home.rest.more")}>{E(rest["more_label"])}</span><span data-rest-less-label {editable("home.rest.less")} hidden>{E(rest["less_label"])}</span><span data-rest-chevron aria-hidden="true">⌄</span></button><button type="button" class="rest-pill rest-pill-primary" data-quiz-open data-goal="rest_help" {editable("home.rest.help")} disabled>{E(rest["help_label"])}</button></div><noscript><p class="small-note">Обсудить отдых можно по телефону <a href="tel:+78512299547" data-goal="rest_noscript_phone">+7 (8512) 29-95-47</a>.</p></noscript></div></section>'

def selection_dialog():
 q=DATA['selection'];groups=''
 for group in q['questions']:
  key='selection.'+group['name']
  groups+=f'<fieldset class="selection-question"><legend {editable(key+".title")}>{E(group["title"])}</legend><div class="selection-chips">'+''.join(f'<label class="selection-chip"><input type="radio" name="{group["name"]}" value="{E(answer)}" data-goal="selection_{group["name"]}_{i}"><span {editable(key+".options."+str(i))}>{E(answer)}</span></label>'for i,answer in enumerate(group['options']))+'</div></fieldset>'
  if group['name']=='when':groups+=f'<label class="field-label selection-dates" data-selection-dates hidden><span {editable("selection.dates")}>{E(q["dates_label"])}</span><input name="dates" data-editable="selection.datesInput" type="text" placeholder="Например, 10–20 июля" maxlength="80" disabled></label>'
 return f'<!-- component: selection-dialog --><dialog class="quiz-dialog selection-dialog" data-editable="selection" id="quiz-dialog" aria-modal="true" aria-labelledby="quiz-title"><div class="dialog-top"><span class="eyebrow" {editable("selection.eyebrow")}>{E(q["eyebrow"])}</span><button type="button" class="icon-btn" data-goal="quiz_close" data-close aria-label="Закрыть окно подбора">{icon("i-close")}</button></div><h2 id="quiz-title" {editable("selection.title")}>{E(q["title"])}</h2><form data-quiz-form novalidate><fieldset data-quiz-guard disabled><legend class="sr-only" {editable("selection.legend")}>Ваши пожелания к путешествию</legend>{groups}<div class="selection-fields"><label class="field-label"><span {editable("selection.budget")}>{E(q["budget_label"])}</span><input name="budget" data-editable="selection.budgetInput" type="text" inputmode="numeric" placeholder="На всех путешественников, ₽" maxlength="30"></label><label class="field-label"><span {editable("selection.phone")}>{E(q["phone_label"])}</span><input name="phone" data-editable="selection.phoneInput" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required maxlength="18" aria-describedby="selection-phone-hint"><small class="field-hint" id="selection-phone-hint" {editable("selection.phoneHint")}>Телефон для связи с Вами</small></label></div><label class="consent selection-consent"><input type="checkbox" name="consent" required><span {editable("selection.consent")}>Даю <a href="o-nas/dokumenty/soglasie/index.html" target="_blank" rel="noopener" data-goal="quiz_consent_read">согласие на обработку персональных данных</a></span></label><p class="form-error" id="quiz-error" role="alert" data-selection-error data-editable="selection.error" data-error-phone="Укажите телефон полностью." data-error-consent="Пожалуйста, отметьте согласие на обработку данных."></p><button class="btn btn-primary selection-submit" type="submit" data-quiz-submit data-goal="quiz_submit" {editable("selection.submit")} disabled>{E(q["submit_label"])} {icon("i-arrow")}</button></fieldset></form><p class="selection-channels"><span {editable("selection.channels")}>{E(q["channels_label"])}</span> <a href="#" data-messenger="MAX" data-goal="selection_max" {editable("selection.links.max")}>MAX</a> · <a href="#" data-messenger="Telegram" data-goal="selection_telegram" {editable("selection.links.telegram")}>Telegram</a></p><noscript><p>Позвоните нам: <a href="tel:+78512299547" data-goal="selection_noscript_phone">+7 (8512) 29-95-47</a></p></noscript><div class="form-success" data-quiz-success role="status" tabindex="-1" hidden>{icon("i-check-circle")}<p {editable("selection.success")}>{E(q["success"])}</p><button type="button" class="btn btn-primary" data-goal="quiz_success_close" data-close {editable("selection.close")}>Закрыть</button></div></dialog><!-- /component: selection-dialog -->'

def home_steps():
 return ''.join(f'<article class="step" id="process-{i+1}" {editable("process."+str(i))}><span class="step-number">{i+1}</span><h3 {editable("process."+str(i)+".title")}>{E(step["title"])}</h3><p {editable("process."+str(i)+".text")}>{E(step["text"])}</p></article>'for i,step in enumerate(DATA['home_process'])).replace('id="process-4"','id="process-support"')

def ratings_strip(path,large=False):
 return '<div class="review-platforms'+(' review-platforms-large'if large else'')+'" aria-label="Отзывы на картах">'+''.join(f'<div class="review-platform"><a class="review-platform-link" href="{E(p["url"])}" data-review-platform="{p["slug"]}" data-goal="reviews_{p["slug"]}" {editable("reviews.platforms."+p["slug"]+".link")}>{icon("i-arrow-up")}<span {editable("reviews.platforms."+p["slug"]+".label")}>{E(p["label"])}</span></a><span class="review-platform-rating" {editable("reviews.platforms."+p["slug"]+".rating")}>{E(p["rating"])}</span></div>'for p in DATA['review_platforms'])+'</div>'

def build():
 from online import configure,finalize,services_index,years_in_tourism,years_label
 configure(globals())
 # Assemble the approved home slots, process steps and common navigation.
 home=HOME.replace('<!-- slot: years-in-tourism -->',str(years_in_tourism())+' '+years_label(years_in_tourism())+' в туризме').replace('<!-- slot: home-rest -->',home_rest()).replace('<!-- slot: home-offers -->',home_offers()).replace('<!-- slot: process-steps -->',home_steps()).replace('<!-- slot: selection-dialog -->',selection_dialog());home=re.sub(r'<!-- component: header -->.*?<!-- /component: header -->',header('index.html',True),home,flags=re.S);home=re.sub(r'<svg class="sprite".*?</svg>',SPRITE,home,count=1,flags=re.S);home=re.sub(r'<!-- component: footer -->.*?<!-- /component: footer -->',footer('index.html',True),home,flags=re.S);home=remap(home,'index.html',True)
 # Only the approved home sections change; preserve their surrounding components.
 home=home.replace('<div class="review-grid scroll-rail">',ratings_strip('index.html')+'<div class="review-grid scroll-rail">',1)
 home=home.replace('</head>','<link rel="stylesheet" href="css/offers.css"><script defer src="js/offers.js"></script></head>')
 home=home.replace('<link rel="icon" href="../../assets/img/favicon.svg" type="image/svg+xml">',brand_icons('index.html'))
 home=home.replace('#f3eee4','#F6F1E9')
 home=home.replace('<script defer src="js/main.js"></script>','<link rel="stylesheet" href="css/navigation.css"><script defer src="js/navigation.js"></script><script defer src="js/main.js"></script>');
 def safe_image(match):
  tag=match[0]
  for r in DATA.get('photo_replacements',[]):
   if 'src="../../assets/img/'+r['original']+'"'in tag:
    tag=tag.replace('src="../../assets/img/'+r['original']+'"','src="img/'+r['file']+'"')
    tag=re.sub(r'width="\d+"','width="'+str(r['width'])+'"',tag);tag=re.sub(r'height="\d+"','height="'+str(r['height'])+'"',tag)
  return tag
 home=re.sub(r'<img\b[^>]*>',safe_image,home)
 (SITE/'index.html').write_text(home);PAGES.append({'path':'index.html','title':'Главная','type':'home'})
 path='napravleniya/index.html';body=section('Найдите свой формат',filters(['Пляж','Экскурсии','Экзотика'],'countries')+'<p class="filter-status sr-only" data-filter-status aria-live="polite"></p><div class="country-grid">'+''.join(countrycard(path,c)for c in COUNTRIES)+'</div>')
 emit(path,'Страны отдыха из Астрахани — Манго','Турция, Египет, ОАЭ, Таиланд и другие направления. Сравните сезоны и формат отдыха с персональным менеджером в Астрахани.','Страны','Начните с моря, новых мест или спокойного ритма. Даты и маршрут подберём вместе.',body,[('Страны',None)],'Выбираю направление')
 for c in COUNTRIES:country(c)
 services_index()
 for s in SERVICES:service(s)
 offers_page()
 from rest import build_rest_pages
 build_rest_pages(globals())
 from brand import build_brand_guide
 build_brand_guide(globals())
 extras()
 for page in PAGES:finalize(page['path'])
 registry={(SITE/'img'/r['file']).resolve():r for r in json.loads((SITE/'img/sources.json').read_text())}
 for record in PAGES:
  page=SITE/record['path']
  for tag in re.findall(r'<img\b[^>]*>',page.read_text()):
   src=re.search(r'src="([^"]+)"',tag)[1];asset=(page.parent/src).resolve();entry=registry.get(asset)
   assert entry and entry.get('license'),f'Missing photo/brand source and license: {src}'
   if entry.get('asset_kind')=='photo':assert entry.get('active') and entry['license'].get('commercial_use'),f'Photo use is not cleared: {src}'
 (TOOLS/'pages.json').write_text(json.dumps(PAGES,ensure_ascii=False,indent=2)+'\n')
 print('Built',len(PAGES),'HTML pages')

def extras():
 from online import about_pages
 about_pages()
 path='o-nas/dokumenty/index.html';body=section('Документы для знакомства','<div class="document-grid">'+''.join(link(path,target,icon('i-file')+f'<h3>{label}</h3><span>Читать документ →</span>','document_'+str(i),'document-card',editable('documents.'+str(i),True))for i,(label,target)in enumerate([('Политика конфиденциальности','o-nas/dokumenty/politika/index.html'),('Согласие на обработку персональных данных','o-nas/dokumenty/soglasie/index.html')]))+'<a href="#contact" class="document-card" data-contact-topic="Запрос образца договора" data-goal="contract_request" '+editable('documents.contract',True)+'>'+icon('i-file')+'<h3>Образец договора</h3><span>Запросить у менеджера →</span></a></div>')
 body+=section('Реквизиты','<dl class="details-list" '+editable('company.details',True)+'><div><dt>Наименование</dt><dd>Данные организации уточнит менеджер</dd></div><div><dt>ИНН</dt><dd>Уточните у менеджера</dd></div><div><dt>ОГРНИП / ОГРН</dt><dd>Уточните у менеджера</dd></div><div class="legal-address"><dt>Юридический адрес</dt><dd data-editable="contacts.legalAddress" data-needs-approval="legal-address">Юридический адрес уточняется</dd></div></dl>')
 emit(path,'Документы турагентства в Астрахани — Манго','Политика, согласие на обработку персональных данных и запрос образца договора. Документы Манго Путешествия в Астрахани.','Понятные документы','Условия поездки и порядок оформления обсуждаем до оплаты.',body,[('О нас','o-nas/index.html'),('Документы',None)],'Вопрос по документам и договору',about=True,approval_intro=True)
 for slug,title in [('politika','Политика конфиденциальности'),('soglasie','Согласие на обработку персональных данных')]:
  path=f'o-nas/dokumenty/{slug}/index.html'
  texts=[('Статус документа','Текст служит основой для юридической редакции. До публикации необходимо указать сведения об операторе, правовые основания, сроки хранения и порядок обращений. Неокончательная редакция.'),('Какие сведения используются','В обращении могут быть указаны имя или контакт для связи, направление поездки, даты и пожелания. Владелец сайта определяет окончательный перечень данных и цели их обработки.'),('Цели и основания','Обсуждение запроса клиента и подготовка предложения о поездке. Правовые основания, состав поручений и сведения о получателях требуют юридического согласования.'),('Ваши права','Порядок доступа, уточнения и удаления данных, а также отзыва согласия необходимо привести в соответствие с действующими требованиями. Для обсуждения обращения: man.go.travel@mail.ru.'),('Оператор и сроки','Реквизиты оператора, сроки обработки и хранения, условия прекращения обработки и способы направления обращений заполняются после юридической проверки.')]
  body=section('Условия документа','<article class="legal-copy" '+editable('legal.'+slug,True)+'>'+''.join(f'<h3>{h}</h3><p>{t}</p>'for h,t in texts)+'</article>')
  emit(path,('Политика конфиденциальности — Манго, Астрахань'if slug=='politika'else'Согласие на обработку данных — Манго, Астрахань'),('Политика работы с персональными данными посетителей Манго Путешествия в Астрахани. Основа для юридического согласования.'if slug=='politika'else'Согласие на обработку данных для обращения в Манго Путешествия, Астрахань. Основа для юридического согласования.'),title,'Порядок работы с обращениями и персональными данными.',body,[('О нас','o-nas/index.html'),('Документы','o-nas/dokumenty/index.html'),(title,None)],'Вопрос о персональных данных',about=True,approval_intro=True)
 path='o-nas/otzyvy/index.html';cards=''
 for i,r in enumerate(DATA['reviews']):
  cards+=f'<!-- component: review-card --><article class="review-card full-review" data-filter-item data-categories="{r["destination"]}" {editable("reviews."+str(i),i==0)}><blockquote>{E(r["text"])}</blockquote><p class="review-author">{r["name"]}</p><p class="review-destination">{r["destination"]}</p><p class="review-meta"><span>{r["date"]}</span> · <a href="{r["source"]}" target="_blank" rel="noopener" data-goal="review_source_{i}" {editable("reviews."+str(i)+".source")}>Источник ↗</a></p></article><!-- /component: review-card -->'
 body=section('Слова после путешествия',ratings_strip(path,True)+filters([r['destination']for r in DATA['reviews']],'reviews')+'<p class="filter-status sr-only" data-filter-status aria-live="polite"></p><div class="reviews-list">'+cards+'</div>')
 body+=section('Впечатления на картах','<div class="rating-grid"><div class="rating-placeholder" '+editable('ratings.yandex',True)+'>'+icon('i-pin')+'<h3>Яндекс Карты</h3><p>Отзывы и фотографии путешественников</p></div><div class="rating-placeholder" '+editable('ratings.2gis',True)+'>'+icon('i-pin')+'<h3>2ГИС</h3><p>Впечатления о знакомстве с агентством</p></div></div><a href="#contact" class="btn btn-primary" data-contact-topic="Хочу оставить отзыв о поездке" data-goal="leave_review">Оставить отзыв</a>')
 emit(path,'Отзывы о турагентстве в Астрахани — Манго','Реальные отзывы туристов Манго Путешествия: Италия и Швейцария, ОАЭ, Иордания. Обсудите поездку с менеджером в Астрахани.','Отзывы о путешествиях','Личные впечатления тех, кто уже вернулся домой.',body,[('О нас','o-nas/index.html'),('Отзывы',None)],'Хочу поделиться впечатлениями',about=True)
 path='kak-my-rabotaem/index.html';steps=[('Обсуждаем пожелания','Расскажите о датах, бюджете, городе вылета и том, что важно в отдыхе.'),('Подбираем и согласуем','Сравним предложения разных туроператоров и обсудим различия.'),('Бронирование и договор','Проверим состав поездки и согласуем условия оформления.'),('Оплата','Обсудим порядок оплаты и, если нужно, условия рассрочки.'),('Документы и подготовка','Разберём документы на поездку и вопросы перед отправлением.'),('Сопровождение в поездке','Ваш персональный менеджер остаётся точкой связи по запросу.'),('Возвращение домой','Будем рады услышать, как прошёл отдых и что хочется учесть в следующий раз.')]
 body=section('От разговора до возвращения','<ol class="timeline" '+editable('process.steps',True)+'>'+''.join(f'<li'+(' id="soprovozhdenie"'if i==5 else'')+f'><span class="timeline-number">0{i+1}</span><div><h3>{h}</h3><p>{t}</p></div></li>'for i,(h,t)in enumerate(steps))+'</ol>')
 body+=section('Встречные шаги','<div class="editorial-grid"><article class="info-card" '+editable('process.we',True)+'><h3>Что делаем мы</h3><p>Сравниваем предложения, объясняем условия и согласуем детали поездки.</p></article><article class="info-card" '+editable('process.you',True)+'><h3>Что нужно от Вас</h3><p>Пожелания, актуальные данные путешественников и внимательная проверка согласованных условий.</p></article></div>')
 body+=section('Оплата и договор','<div class="editorial-text" '+editable('process.payment',True)+'><p>Состав поездки, стоимость и порядок оплаты согласуем перед оформлением. Возможна рассрочка; условия уточняются для конкретного запроса.</p><p>Попросите менеджера объяснить ограничения тарифа, порядок изменений и отмены. Образец договора можно запросить до принятия решения.</p>'+link(path,'o-nas/dokumenty/index.html','Посмотреть документы →','process_documents','text-link')+'</div>')
 questions=[('Можно ли начать подбор онлайн?','Да, обсудить пожелания можно по телефону, в MAX или Telegram. Порядок оформления согласуем отдельно.'),('Можно ли оплатить в рассрочку?','Рассрочка доступна. Конкретные условия и порядок оформления менеджер уточнит под Вашу поездку.'),('Что делать, если изменятся планы?','Свяжитесь с менеджером. Возможность изменений и расходы зависят от условий бронирования и поставщиков.')]
 body+=section('Частые вопросы',faq(questions,'process.faq'))
 emit(path,'Как мы работаем — Манго Путешествия, Астрахань','Как проходит подбор и оформление поездки в Манго Путешествия: обсуждение, предложения, договор, оплата и подготовка. Турагентство в Астрахани.','Спокойно, шаг за шагом','От первого разговора до возвращения домой — с персональным менеджером.',body,[('Как мы работаем',None)],'Хочу обсудить порядок подбора',questions=questions,approval_intro=True)
 path='404.html';body=section('Продолжим с понятного места','<div class="related-links">'+link(path,'index.html','На главную →','404_home')+link(path,'napravleniya/index.html','Выбрать направление →','404_countries')+link(path,'uslugi/index.html','Все услуги →','404_services')+'</div>')
 emit(path,'Страница не найдена — Манго Путешествия','Страница не найдена. Вернитесь к направлениям или свяжитесь с Манго Путешествия в Астрахани.','Здесь маршрут меняется','Такой страницы нет. Давайте найдём нужную или обсудим Ваш вопрос.',body,[('Страница не найдена',None)],'Нужна помощь с поиском страницы')
 path='pages.html';entries=PAGES.copy();body=section('Страницы сайта','<div class="page-directory">'+''.join(link(path,p['path'],p['title']+' <small>'+p['path']+'</small>','directory_'+str(i))for i,p in enumerate(entries))+'</div>')
 emit(path,'Страницы сайта — Манго Путешествия, Астрахань','Техническое оглавление страниц Манго Путешествия в Астрахани.','Страницы сайта','Навигация для просмотра и проверки.',body,[('Страницы',None)],'Вопрос о сайте')

def team_content(path):
 people=DATA['team_members'];count=len(people);cards=''
 for i,p in enumerate(people):
  key='team.'+str(i)
  cards+=f'<!-- component: team-card --><article class="team-travel-card" role="listitem" {editable(key)}><div class="team-travel-media">{image(path,p["photo"],p["photo_alt"],key=key+".photo")}<span class="team-initials" {editable(key+".initials")}>{E(p["initials"])}</span></div><div class="team-travel-body"><h3 {editable(key+".name")}>{E(p["name"])}</h3><p class="team-travel-role" {editable(key+".role")}>{E(p["role"])}</p><p class="team-expertise" {editable(key+".countries",p.get("expertise_needs_approval",False))}>{E(p["expertise"])}</p><div class="team-travel-channels"><a href="{E(p["max"])}" data-messenger="MAX" data-goal="team_detail_max_{i}" {editable(key+".links.max")}>{icon("i-max")}<span>MAX</span></a><a href="{E(p["telegram"])}" data-messenger="Telegram" data-goal="team_detail_telegram_{i}" {editable(key+".links.telegram")}>{icon("i-telegram")}<span>Telegram</span></a></div></div></article><!-- /component: team-card -->'
 columns=max(1,min(count,4))
 body=f'<section class="section inner-section team-picker{" is-carousel"if count>4 else""}" data-team-collection style="--team-columns:{columns}"><div class="container"><div class="section-head team-picker-head"><h2 id="team-picker-title" {editable("team.section.title")}>Поможем с выбором</h2><p {editable("team.section.subtitle")}>Поддержим на всех этапах путешествия — от выбора тура до возвращения домой</p></div></div><div class="team-travel-frame"><div class="team-travel-list" id="team-travel-list" data-team-list role="list" aria-labelledby="team-picker-title">{cards}</div><div class="team-travel-arrows" data-team-arrows hidden><button class="icon-btn" type="button" data-team-prev data-goal="team_previous" aria-label="Предыдущая карточка" aria-controls="team-travel-list" disabled>{icon("i-arrow-left")}</button><button class="icon-btn" type="button" data-team-next data-goal="team_next" aria-label="Следующая карточка" aria-controls="team-travel-list" disabled>{icon("i-arrow")}</button></div></div><div class="container"><p class="team-picker-note" {editable("team.personal")}>Каждого клиента ведёт один менеджер — от выбора тура до возвращения домой</p></div></section>'
 return body

if __name__=='__main__':build()
