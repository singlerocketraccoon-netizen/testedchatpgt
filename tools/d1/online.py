"""Online-first contact components and compact service layouts (stdlib only)."""
from html import unescape
from urllib.parse import quote
import re,json


def configure(c):
 global C,D,E,I,U,L,ED,S
 C=c;D=c['DATA'];E=c['E'];I=c['icon'];U=c['url'];L=c['link'];ED=c['editable'];S=c['section']
 c['contact']=contact;c['service']=service;c['selection_dialog']=selection_dialog
 c['agency']=agency;c['offer']=offer
 oldnav=c['navitems']
 def navitems(path,kind):
  if kind=='about':return ''.join(L(path,t,label,'nav_about_'+str(i))for i,(label,t)in enumerate([('О нас','o-nas/index.html'),('Отзывы','o-nas/otzyvy/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html')]))
  if kind!='services':return oldnav(path,kind)
  return ''.join('<div class="service-menu-group"><p>'+E(g['title'])+'</p>'+''.join(L(path,'uslugi/'+s['slug']+'/index.html',I(s['icon'])+E(s['name']),'nav_service_'+s['slug'])for slug in g['slugs']for s in D['services']if s['slug']==slug)+'</div>'for g in D['service_groups'])
 c['navitems']=navitems
 def aboutnav(path):return '<nav class="section-tabs" aria-label="Раздел об агентстве">'+''.join(L(path,t,l,'about_tab_'+str(i),extra='aria-current="page"'if path==t else'')for i,(l,t)in enumerate([('О нас','o-nas/index.html'),('Отзывы','o-nas/otzyvy/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html')]))+'</nav>'
 c['aboutnav']=aboutnav
 oldfooter=c['footer']
 def footer(path,home=False):
  f=oldfooter(path,home)
  channels='<div class="footer-channels">'+''.join(f'<a href="{E(D["contacts"][key])}" data-goal="footer_channel_{channel}" {ED("contacts."+key)}>Канал в {label}</a>'for channel,label,key in [('max','MAX','maxChannel'),('telegram','Telegram','telegramChannel')])+'</div>'
  f=re.sub(r'<div class="footer-channels">.*?</div>',channels,f,flags=re.S)
  f=re.sub(r'<span data-editable="contacts.footerAddress">.*?</span>','',f,flags=re.S)
  return f
 c['footer']=footer


def agency():
 a={'@type':'TravelAgency','@id':'https://devfriends.ru/#agency','name':'Манго Путешествия','telephone':['+7-8512-29-95-47','+7-8512-29-95-27'],'email':'man.go.travel@mail.ru','address':{'@type':'PostalAddress','addressLocality':'Астрахань','addressCountry':'RU'},'areaServed':'RU'}
 a['openingHoursSpecification']=[{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday'],'opens':'10:00','closes':'19:00'},{'@type':'OpeningHoursSpecification','dayOfWeek':'Saturday','opens':'10:00','closes':'15:00'}]
 return a

def channel_links(context,key,compact=False):
 user=D['contacts']['telegramUsername'].lstrip('@');tg='https://t.me/'+user+'?text='+quote(context)if user else'#'
 return '<div class="messenger-actions'+(' messenger-compact'if compact else'')+'">'+''.join(f'<a class="btn {"btn-primary"if ch=="Telegram"else"btn-outline"}" href="{E(href)}" data-messenger="{ch}" data-message="{E(context)}" data-goal="{key}_{ch.lower()}" {ED("contacts."+("telegramUsername"if ch=="Telegram"else"max"))}>{I("i-telegram"if ch=="Telegram"else"i-max")}<span>Написать в {ch}</span></a>'for ch,href in [('Telegram',tg),('MAX',D['contacts']['max'])])+'</div><p class="messenger-feedback" data-channel-status data-editable="contacts.copyFeedback" role="status" hidden>Текст скопирован — вставьте его в чат</p>'

def contact(path,prefill=''):
 # Keep the existing form contract and its local validation; messengers are primary.
 form=C['formal'](C['remap'](C['CONTACT'],path)).replace(' data-home-block="09"','')
 form=form.replace('name="destination" type="text"','name="destination" type="text" value="'+E(prefill)+'"')
 form=form.replace('data-discussion-form novalidate','data-discussion-form data-prefill="'+E(prefill)+'" novalidate')
 form=form.replace('<h3>Форма обращения</h3>',channel_links('Здравствуйте! '+(prefill or 'Хочу обсудить путешествие.'),'contact_main')+'<h3 class="callback-caption" data-editable="contacts.callback">Удобнее звонок? Оставьте номер — перезвоним</h3>')
 form=form.replace('<label class="field-label"><span>Удобный способ связи</span><select name="method"><option value="Телефон">Телефон</option><option>MAX</option><option>Telegram</option></select></label>','<label hidden><span>Способ связи</span><select name="method"><option value="Телефон">Телефон</option></select></label>')
 form=form.replace('<span>Контакт</span>','<span data-editable="contacts.phoneLabel">Телефон</span>').replace('Отправить запрос','Перезвоните мне')
 form=re.sub(r'<div class="direct-channels">.*?</div>','',form,flags=re.S)
 form=re.sub(r'<address.*?</address>',f'<p class="online-location" {ED("contacts.location")}>{E(D["contacts"]["location"])}</p>',form,flags=re.S)
 form=form.replace('Телефон для связи с вами','Телефон для связи с Вами').replace('Что для вас важно','Что для Вас важно')
 return form.replace('class="section contact-section"','class="section contact-section" data-editable="contacts.block"')

def selection_dialog():
 q=D['selection'];groups=''
 for group in q['questions']:
  key='selection.'+group['name'];groups+=f'<fieldset class="selection-question"><legend {ED(key+".title")}>{E(group["title"])}</legend><div class="selection-chips">'+''.join(f'<label class="selection-chip"><input type="radio" name="{group["name"]}" value="{E(a)}" data-goal="selection_{group["name"]}_{i}"><span {ED(key+".options."+str(i))}>{E(a)}</span></label>'for i,a in enumerate(group['options']))+'</div></fieldset>'
  if group['name']=='when':groups+='<label class="field-label selection-dates" data-selection-dates hidden><span data-editable="selection.dates">Даты</span><input name="dates" maxlength="80" disabled></label>'
 channels=channel_links('Здравствуйте! Помогите выбрать путешествие.','selection').replace('Написать в Telegram','Отправить в Telegram').replace('Написать в MAX','Отправить в MAX')
 return f'''<!-- component: selection-dialog --><dialog class="quiz-dialog selection-dialog" id="quiz-dialog" aria-modal="true" aria-labelledby="quiz-title"><div class="dialog-top"><span class="eyebrow" data-editable="selection.eyebrow">Подбор путешествия</span><button type="button" class="icon-btn" data-close data-goal="quiz_close" aria-label="Закрыть окно подбора">{I('i-close')}</button></div><h2 id="quiz-title" data-editable="selection.title">Помогите выбрать</h2><form data-quiz-form novalidate><fieldset data-quiz-guard disabled><legend class="sr-only">Ваши пожелания</legend>{groups}<label class="field-label"><span data-editable="selection.budget">Бюджет (по желанию)</span><input name="budget" maxlength="30" placeholder="На всех путешественников, ₽"></label>{channels}<details class="selection-callback"><summary data-goal="selection_callback" data-editable="selection.callback">Оставить телефон</summary><p class="callback-caption" data-editable="contacts.callback">Удобнее звонок? Оставьте номер — перезвоним</p><label class="field-label"><span data-editable="selection.phone">Телефон</span><input name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" maxlength="18" required></label><label class="consent"><input type="checkbox" name="consent" required><span>Даю <a href="o-nas/dokumenty/soglasie/index.html" target="_blank" rel="noopener" data-goal="quiz_consent_read" data-editable="selection.consent">согласие на обработку персональных данных</a></span></label><p class="form-error" id="quiz-error" role="alert" data-selection-error data-error-phone="Укажите телефон полностью." data-error-consent="Пожалуйста, отметьте согласие на обработку данных."></p><button class="btn btn-outline" type="submit" data-quiz-submit data-goal="quiz_submit" disabled data-editable="selection.submit">Перезвоните мне</button></details></fieldset></form><div class="form-success" data-quiz-success tabindex="-1" role="status" hidden><p data-editable="selection.success">Спасибо, менеджер свяжется с Вами</p><button class="btn btn-primary" type="button" data-close data-goal="quiz_success_close">Закрыть</button></div></dialog><!-- /component: selection-dialog -->'''

def service(s):
 path='uslugi/'+s['slug']+'/index.html';key='services.'+s['slug'];name='Бронирование отелей'if s['slug']=='oteli'else s['name']
 photo=s.get('image',D['countries'][0]['image'])
 # Only use a registered existing picture; image keys are data-driven for future replacement.
 if photo not in D['image_dimensions']:photo=D['countries'][0]['image']
 cover=f'<section class="inner-cover service-cover" data-inner-cover><div class="container">{C["crumb"](path,[("Услуги","uslugi/index.html"),(name,None)])}<div class="service-cover-grid"><div><p class="eyebrow" {ED(key+".label",True)}>Под Вашу поездку</p><h1 {ED(key+".title")}>{E(name)}</h1><p class="inner-lead" {ED(key+".intro",True)}>{E(s["intro"])}</p></div>{C["image"](path,photo,name,False,key=key+".image")}</div></div></section>'
 actions=s['actions']+(['Согласуем стоимость и условия до оформления']if len(s['actions'])<4 else[])
 important=[s['audience'],'Стоимость рассчитаем под Ваш запрос.','Условия подтвердим до оформления.']
 cols=''
 for j,(title,items,numbered)in enumerate([('Что делаем',actions,False),('Как заказать',s['steps'],True),('Важно знать',important,False)]):
  tag='ol'if numbered else'ul';cols+=f'<article class="service-column" {ED(key+".columns."+str(j),True)}><h2>{title}</h2><{tag}>'+''.join('<li>'+E(t)+'</li>'for t in items)+f'</{tag}></article>'
 body='<section class="service-content"><div class="container"><div class="service-columns">'+cols+'</div><div class="service-contact">'+channel_links('Здравствуйте! Интересует услуга «'+name+'».','service_'+s['slug'],True)+'<a href="tel:+78512299547" data-goal="service_phone">+7 (8512) 29-95-47</a></div>'
 questions=[(s['question'],s['answer']),('Как узнать стоимость?','Расскажите о датах и пожеланиях в Telegram или MAX. Рассчитаем под Ваш запрос.')]
 body+='<div class="service-faq">'+C['faq'](questions,key+'.faq')+'</div><nav class="service-related" aria-label="Другие услуги"><span>Другие услуги</span>'+''.join(L(path,'uslugi/'+v['slug']+'/index.html',E(v['name']),'related_service_'+v['slug'])for v in D['services']if v['slug']!=s['slug'])+'</nav></div></section>'
 callback='<details class="service-callback" id="contact"><summary class="container" data-goal="service_callback">Удобнее звонок? Оставьте номер — перезвоним</summary>'+contact(path,name).replace('id="contact"','id="service-contact-form"')+'</details>'
 C['emit'](path,name+' — Манго, Астрахань',s['intro']+' Обсудите запрос онлайн с персональным менеджером.',name,s['intro'],body,[('Услуги','uslugi/index.html'),(name,None)],name,questions=questions,approval_intro=True,cover_override=cover,contact_override=callback,page_class='compact-service')

def services_index():
 path='uslugi/index.html';body=''
 for i,g in enumerate(D['service_groups']):
  cards=''.join(L(path,'uslugi/'+s['slug']+'/index.html',I(s['icon'])+'<h3>'+E(s['name'])+'</h3><p>'+E(s['intro'])+'</p>','service_'+s['slug'],'service-card',ED('services.'+s['slug'],True))for slug in g['slugs']for s in D['services']if s['slug']==slug)
  if i==2:cards+='<a class="service-card service-future" href="#contact" data-goal="service_new" '+ED('services.additional',True)+'>'+I('i-plus')+'<h3>Другие пожелания</h3><p>Обсудим, что ещё нужно для Вашей поездки.</p></a>'
  body+=S(g['title'],'<div class="service-grid">'+cards+'</div>','services.group.'+str(i))
 C['emit'](path,'Услуги турагентства онлайн — Манго, Астрахань','Туры, билеты, бронирование и дополнительные услуги. Обсудите поездку онлайн с персональным менеджером Манго Путешествия.','Что нужно для Вашей поездки','От маршрута до деталей дороги — обсудим Ваш запрос онлайн.',body,[('Услуги',None)],'Услуги для поездки')


def about_pages():
 path='o-nas/index.html'
 body=S('В туризме с 2010 года','<div class="editorial-grid"><div class="editorial-text"><p '+ED('about.history')+'>Мы работаем в туризме с 2010 года, а с 2017 года — под брендом «Манго Путешествия».</p><p '+ED('contacts.location')+'>'+E(D['contacts']['location'])+'</p><p '+ED('about.approach')+'>У каждого клиента есть персональный менеджер. Сравниваем предложения разных туроператоров и обсуждаем условия до выбора поездки.</p></div><div class="year-card" '+ED('about.since')+'><strong>2010</strong><span>год начала работы в туризме</span></div></div>')
 facts=''.join('<article class="trust-card" '+ED('about.trust.'+str(i),True)+'>'+I(t['icon'])+'<strong class="trust-value'+(' is-empty'if not t['value']else'')+'" '+('aria-label="Значение ожидает подтверждения"'if not t['value']else'')+'>'+E(t['value'])+'</strong><p>'+E(t['label'])+'</p></article>'for i,t in enumerate(D['trust']))
 body+=S('С нами надёжно','<div class="trust-grid">'+facts+'</div>','about.trust.title','cream-section')
 body+=C['team_content'](path).replace('<section class="section inner-section team-picker','<section id="komanda" class="section inner-section team-picker')
 pay=''.join('<article class="payment-card" '+ED('about.payment.'+str(i),True)+'><span>0'+str(i+1)+'</span><h3>'+E(t['title'])+'</h3><p>'+E(t['text'])+'</p></article>'for i,t in enumerate(D['safe_payment']))
 body+=S('Безопасная оплата','<div class="payment-grid">'+pay+'</div>','about.payment.title')
 body+=S('Туроператоры-партнёры','<div class="online-partners">'+''.join('<div '+ED('about.partners.'+str(i),True)+'>'+I('i-shield')+'<span>Туроператор</span></div>'for i in range(4))+'</div>','about.partners.title','cream-section')
 body+=S('На связи в поездке','<div class="editorial-text" '+ED('about.support')+'><p>Один менеджер ведёт Ваш запрос от выбора тура до возвращения домой. Если в поездке возникает вопрос, свяжитесь с Вашим менеджером.</p></div>'+channel_links('Здравствуйте! У меня вопрос по поездке.','about_support'))
 C['emit'](path,'О нас — Манго Путешествия, Астрахань','В туризме с 2010 года. Персональный менеджер, команда и онлайн-подбор путешествий по всей России.','Манго — это люди','Путешествия начинаются с понятного разговора.',body,[('О нас',None)],'Знакомство с агентством',about=True)
 # Retain the former URL without duplicating the team or exposing a stale office page.
 p='o-nas/komanda/index.html';target='../index.html#komanda';html=f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Команда — Манго Путешествия</title><meta name="description" content="Команда Манго Путешествия на странице об агентстве."><meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="https://devfriends.ru/o-nas/#komanda">{C["brand_icons"](p)}</head><body><h1>Команда «Манго Путешествия»</h1><a href="{target}" data-goal="team_redirect">Познакомиться с командой →</a></body></html>\n'
 (C['SITE']/p).write_text(html);C['PAGES'].append({'path':p,'title':'Команда → О нас','type':'redirect'})
 path='o-nas/kontakty/index.html';body=S('Мы на связи',channel_links('Здравствуйте! Хочу обсудить путешествие.','contacts_primary')+'<div class="online-contact-details"><div><h3 '+ED('contacts.location')+'>'+E(D['contacts']['location'])+'</h3><p '+ED('contacts.hours')+'>Когда мы на связи:<br>Пн–Пт 10:00–19:00<br>Сб 10:00–15:00<br>Вс — выходной</p></div><div><a href="tel:+78512299547" data-goal="contacts_phone_1" '+ED('contacts.primaryPhone')+'>+7 (8512) 29-95-47</a><a href="tel:+78512299527" data-goal="contacts_phone_2" '+ED('contacts.secondaryPhone')+'>+7 (8512) 29-95-27</a><a href="mailto:man.go.travel@mail.ru" data-goal="contacts_email" '+ED('contacts.email')+'>man.go.travel@mail.ru</a></div></div>')
 C['emit'](path,'Контакты онлайн — Манго Путешествия, Астрахань','Telegram, MAX, телефоны и email Манго Путешествия. Работаем онлайн по всей России, Астрахань. Часы связи и обратный звонок.','Контакты «Манго Путешествия»','Напишите нам в Telegram или MAX — обсудим Вашу поездку.',body,[('О нас','o-nas/index.html'),('Контакты',None)],'Хочу связаться с агентством',about=True)


def finalize(path):
 file=C['SITE']/path;h=file.read_text()
 if path=='o-nas/komanda/index.html':return
 h=h.replace('o-nas/komanda/index.html','o-nas/index.html#komanda')
 # Only local references to the retired page, including nested relative paths.
 h=re.sub(r'href="([^"]*?)(?:\.\./)?komanda/index.html"',lambda m:'href="'+U(path,'o-nas/index.html')+'#komanda"',h)
 if path=='index.html':h=re.sub(r'<!-- component: discussion-form -->.*?<!-- /component: discussion-form -->',contact(path).replace('id="contact"','data-home-block="09" id="contact"'),h,flags=re.S)
 # All machine-readable agency records follow the online operation model.
 def schema(m):
  obj=json.loads(m[1])
  def visit(v):
   if isinstance(v,dict):
    if v.get('@type')=='TravelAgency':v.pop('geo',None);v['address']=agency()['address'];v['areaServed']='RU'
    for x in v.values():visit(x)
   elif isinstance(v,list):
    for x in v:visit(x)
  visit(obj);return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False)+'</script>'
 h=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,h,flags=re.S)
 # Assign a stable context to every existing messenger control; JS enriches it with choices.
 title=re.search(r'<h1\b[^>]*>(.*?)</h1>',h,re.S);context='Здравствуйте! '+re.sub('<[^>]*>','',unescape(title[1]if title else'Хочу обсудить путешествие.'))
 for page in D['rest_pages']:
  if path=='otdyh/'+page['slug']+'/index.html':context=page['message']
 def anchors(m):
  attrs,body=m[1],m[2]
  if 'data-messenger='not in attrs and'data-rest-message'not in attrs:return m[0]
  channel='Telegram'if 'Telegram'in body or'telegram'in attrs.lower()else'MAX'
  if 'data-messenger='not in attrs:attrs+=' data-messenger="'+channel+'"'
  attrs=re.sub(r'\sdata-rest-message(?:="[^"]*")?','',attrs)
  textmatch=re.search(r'data-message="([^"]*)"',attrs);text=unescape(textmatch[1])if textmatch else context
  if not textmatch:attrs+=' data-message="'+E(text)+'"'
  username=D['contacts']['telegramUsername'].lstrip('@')
  href='https://t.me/'+username+'?text='+quote(text)if channel=='Telegram'and username else D['contacts']['max']if channel=='MAX'else'#'
  attrs=re.sub(r'href="[^"]*"','href="'+E(href)+'"',attrs)
  if any(k in attrs for k in ['messenger_max_process','messenger_telegram_process','messenger_max_voices','messenger_telegram_voices','country_max','country_telegram']):
   attrs+=' class="btn '+('btn-primary'if channel=='Telegram'else'btn-outline')+'"';body=I('i-telegram'if channel=='Telegram'else'i-max')+'<span>Написать в '+channel+'</span>'
  return '<a'+attrs+'>'+body+'</a>'
 h=re.sub(r'<a\b([^>]*)>(.*?)</a>',anchors,h,flags=re.S)
 sheet='<dialog class="contact-dialog" id="contact-dialog" aria-modal="true" aria-labelledby="contact-title"><div class="dialog-top"><h2 id="contact-title">Как Вам удобнее?</h2><button type="button" class="icon-btn" data-close data-goal="contact_sheet_close" aria-label="Закрыть способы связи">'+I('i-close')+'</button></div><div class="contact-options">'+channel_links(context,'sheet')+'<a href="tel:+78512299547" data-goal="phone_sheet">Позвонить · +7 (8512) 29-95-47</a><a href="#contact" data-contact-form data-goal="sheet_form">Оставить телефон →</a></div></dialog>'
 h=re.sub(r'<dialog class="contact-dialog".*?</dialog>',sheet,h,flags=re.S)
 fallback='<dialog class="messenger-fallback" id="messenger-fallback" aria-modal="true" aria-labelledby="fallback-title"><div class="dialog-top"><h2 id="fallback-title">Сообщение менеджеру</h2><button class="icon-btn" type="button" data-fallback-close data-goal="message_close" aria-label="Закрыть сообщение">'+I('i-close')+'</button></div><p data-fallback-caption>Скопируйте текст и вставьте его в чат.</p><textarea readonly data-fallback-text aria-label="Текст сообщения" rows="6"></textarea><button class="btn btn-primary" type="button" data-fallback-copy data-goal="message_copy">Скопировать текст</button><p data-fallback-status role="status"></p><div class="fallback-channels">'+channel_links(context,'fallback')+'</div><a href="tel:+78512299547" data-goal="fallback_phone">+7 (8512) 29-95-47</a></dialog>'
 config={'telegramUsername':D['contacts']['telegramUsername'],'max':D['contacts']['max'],'context':context}
 h=h.replace('</head>',f'<link rel="stylesheet" href="{U(path,"css/online.css")}"><script defer src="{U(path,"js/online.js")}"></script></head>')
 h=h.replace('</body>',fallback+'<script type="application/json" id="online-config">'+json.dumps(config,ensure_ascii=False).replace('<','\\u003c')+'</script></body>')
 file.write_text(h)


def offer(path,o):
 country=next(t for t in D['countries']if t['slug']==o['country']);key='offers.'+o['id'];route=o['departure_city']+' → '+o['resort'];price=f'{o["price_from"]:,}'.replace(',',' ')
 context='Здравствуйте! Интересует тур: '+route+'. '+o['hotel']+f' {o["stars"]}★. Вылет '+C['human_date'](o['departure_date'])+f', {o["nights"]} ночей. От {price} ₽ за двоих. Уточните, пожалуйста, условия и наличие.'
 cta=channel_links(context,'offer_'+o['id'],True);cta=re.search(r'<a\b.*?</a>',cta,re.S)[0].replace('Написать в Telegram','Написать о туре')
 return f'''<!-- component: offer-card --><article class="offer-card boarding-pass" role="listitem" data-offer-id="{E(o['id'])}" data-country="{o['country']}" data-price="{o['price_from']}" data-date="{o['departure_date']}" {ED(key,True)}><div class="boarding-photo">{C['image'](path,o['photo'],country['name']+' · '+o['resort'],key=key+'.photo')}<span class="boarding-country" {ED(key+'.country')}>{E(country['name'])}</span></div><div class="boarding-info"><p class="boarding-kicker" {ED(key+'.label')}>Ваша поездка</p><h3 {ED(key+'.route')}>{E(o['departure_city'])} <span aria-hidden="true">→</span> {E(o['resort'])}</h3><p class="boarding-dates" {ED(key+'.details')}><time datetime="{o['departure_date']}">{C['human_date'](o['departure_date'])}</time> · {o['nights']} ночей</p><p class="boarding-hotel" {ED(key+'.hotel')}>{E(o['hotel'])} <span>{o['stars']}★</span></p><p class="offer-price" {ED(key+'.price',True)}>от {price} ₽ <small>за двоих</small></p><p class="price-date" {ED(key+'.priceDate',True)}>Цена на {C['human_date'](o['price_date'])}</p>{cta}<div class="boarding-barcode" aria-hidden="true"></div></div></article><!-- /component: offer-card -->'''
