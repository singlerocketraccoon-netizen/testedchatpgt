"""Stage 13 shared components and source-driven services/process pages."""
import re,hashlib

def configure(ctx):
 global C,D,E,I,U,L,ED,shared,original_header,original_emit
 import stage6
 shared=stage6;C=ctx;D=ctx['DATA'];E=ctx['E'];I=ctx['icon'];U=ctx['url'];L=ctx['link'];ED=ctx['editable']
 source=C['ROOT']/D['work13']['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==D['work13']['sha256'],'Reimport approved process copy'
 original_header=ctx['header'];original_emit=ctx['emit'];original_image=ctx['image']
 def approved_image(*args,**kw):
  html=original_image(*args,**kw)
  return html.replace('<img ','<img data-needs-approval="photo" ',1)if kw.get('key')in D['layout13'].get('approvalPhotos',[])else html
 ctx['image']=approved_image
 ctx.update(header=header,footer=footer,emit=emit,illustrative_photo=illustrative_photo)
 shared.header=header;shared.footer=footer;shared.form=form;shared.mobile_panel=mobile_panel;shared.services=services;shared.quiz=quiz
 import stage11
 stage11.documents=documents
 import country
 country.photo=illustrative_photo
 import photos131
 photos131.configure(ctx)

def illustrative_photo(path,name,alt,key,lazy=True):
 from photos131 import photo
 return photo(path,name,alt,key,lazy)

def header(path,photo=False):
 h=original_header(path,photo);tag='<nav class="nav-left" aria-label="Страны и услуги">'
 home=L(path,'index.html','Главная','nav_home','nav-home',ED('navigation.home')+(' aria-current="page"'if path=='index.html'else''))
 return h.replace(tag,tag+home)

def channels(key,goal='message',large=False):
 s=shared.channels(key,goal)
 if large:
  s=s.replace('class="messenger-actions"','class="messenger-actions primary-channels"').replace('btn btn-outline','btn btn-primary')
  for ch in['MAX','Telegram']:s=s.replace('<span>'+ch+'</span>','<span>Написать в '+ch+'</span>')
 return s

def form(path,key='home',place='end',mode=None,heading=True,classes='',attrs=''):
 mode=mode or shared.kind(key);title,_=shared.topic(key);goal='form_'+place+'_'+mode
 hidden=''.join('<input type="hidden" name="'+n+'" value="'+E(key if n=='topic'else path if n=='page'else'')+'">'for n in shared.HIDDEN)
 phone=shared.field('Телефон','<input name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" required maxlength="18">','form-phone')
 fields=shared.travel_fields(key=='holiday:otdyh-s-detmi')+shared.field('Комментарий','<textarea name="task" rows="2" maxlength="1500"></textarea>','form-wide')+shared.field('Даты поездки','<input name="dates" maxlength="100">')+shared.field('Бюджет на всю поездку','<input name="budget" maxlength="100">')
 options='<details class="unified-options"><summary data-goal="'+goal+'_options" '+ED(goal+'.options')+'>Указать месяц, город и состав — по желанию</summary><div class="unified-grid">'+fields+'</div></details>'
 return '<!-- component: discussion-form --><div class="unified-card messenger-card '+classes+'" data-unified-card '+attrs+' '+ED(goal)+'><h3 class="unified-title"'+(' hidden'if not heading else'')+'>'+shared.TITLES[mode]+'</h3><p class="unified-context" data-form-context'+(' hidden'if not title else'')+'>'+E(title)+'</p><p class="unified-viewed" data-viewed-month hidden></p><form class="unified-form" data-unified-form data-mode="'+mode+'" data-topic="'+E(key)+'"'+(' data-end-form'if place in['end','bottom']else'')+' novalidate><p class="message-first-note" '+ED(goal+'.messengerNote')+'>Напишите менеджеру — сообщение с темой уже подготовлено.</p>'+channels(key,goal,True)+'<fieldset data-form-guard disabled><legend class="sr-only">'+shared.TITLES[mode]+'</legend>'+hidden+'<p class="callback-divider" '+ED(goal+'.callback')+'>или оставьте телефон — перезвоним</p><div class="callback-row">'+phone+'<button type="submit" class="btn btn-primary" data-goal="'+goal+'_submit" '+ED(goal+'.submit')+'>Перезвоните мне</button></div>'+shared.consent(path,goal)+'<p class="form-error" data-form-error role="alert"></p>'+options+'</fieldset></form><div class="form-success" data-form-success role="status" tabindex="-1" hidden><p>'+shared.SUCCESS+'</p></div><noscript><p><a href="tel:+78512299547" data-goal="'+goal+'_nojs">+7 (8512) 29-95-47</a></p></noscript></div><!-- /component: discussion-form -->'

def footer(path,home=False):
 b=C['brand_path'](path,'light');items=[('Страны','napravleniya/index.html'),('Услуги','uslugi/index.html'),('Актуальные предложения','predlozheniya/index.html'),('Как мы работаем','kak-my-rabotaem/index.html'),('О нас','o-nas/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html')]
 links=''.join(L(path,t,label,'footer_section_'+str(i))for i,(label,t)in enumerate(items));social=''
 for label,key,var in [('MAX','maxChannel','MAX_CHANNEL_URL'),('Telegram','telegramChannel','TELEGRAM_CHANNEL_URL')]:
  target=D['contacts'].get(key,'');target=target if target not in['','#']else C[var]
  social+='<a href="'+E(target or'#')+'" data-goal="footer_channel_'+label.lower()+'" '+ED('contacts.'+key)+(' data-needs-approval="channel-url"'if not target else'')+'>Наш канал в '+label+'</a>'
 return '<!-- component: footer --><footer class="site-footer compact-footer" data-editable="footer"><div class="container"><div class="compact-footer-grid"><div class="footer-brand">'+L(path,'index.html','<img src="'+b+'" alt="Mango Travel" width="1193" height="440" loading="lazy">','footer_home','brand')+'<p '+ED('footer.companyLine')+'>'+E(D['layout13']['companyLine'])+'</p></div><nav class="footer-sections" aria-label="Разделы"><h2>Разделы</h2><div>'+links+'</div></nav><div class="footer-contact"><h2>Контакты</h2><div><a href="tel:+78512299547" data-goal="footer_phone" '+ED('contacts.primaryPhone')+'>+7 (8512) 29-95-47</a><a href="tel:+78512299527" data-goal="footer_phone_secondary" '+ED('contacts.secondaryPhone')+'>+7 (8512) 29-95-27</a><a href="mailto:man.go.travel@mail.ru" data-goal="footer_email" '+ED('contacts.email')+'>man.go.travel@mail.ru</a><p '+ED('contacts.location')+'>Астрахань</p><p '+ED('contacts.hours',True)+'>'+E(D['contacts']['hours'])+'</p></div></div><nav class="footer-messengers" aria-label="Каналы"><h2>Мы в мессенджерах</h2>'+social+'</nav></div><div class="footer-bottom"><span>© 2026 Mango Travel</span>'+L(path,'PHOTOS13_1.html','Фото и лицензии','footer_photo_credits','footer-photo-credits')+L(path,'o-nas/dokumenty/politika/index.html','Политика конфиденциальности','footer_policy')+'</div></div></footer><!-- /component: footer -->'

def mobile_panel(path):
 key=shared.page_topic(path)
 return '<div class="mobile-contact contact-dock" data-mobile-contact hidden>'+''.join('<a class="dock-link" href="#" data-messenger="'+ch+'" data-topic-key="'+E(key)+'" data-goal="dock_'+ch.lower()+'" '+ED('contacts.'+ch.lower())+'>'+I('i-max'if ch=='MAX'else'i-telegram')+'<span>'+ch+'</span></a>'for ch in['MAX','Telegram'])+'<a class="dock-link" href="tel:+78512299547" data-goal="dock_call" '+ED('contacts.primaryPhone')+'>'+I('i-phone')+'<span>Позвонить</span></a></div>'

def services():
 path='uslugi/index.html';p=D['layout13'];cards='';tiles='';targets={'packages':('napravleniya/index.html','Посмотреть страны'),'custom':('otdyh/svoj-marshrut/index.html','Посмотреть форматы маршрутов'),'tours':('otdyh/ekskursionnye-tury/index.html','Посмотреть форматы поездок'),'cruises':('otdyh/kruizy/index.html','Посмотреть варианты круизов')};labels=['Подобрать тур','Обсудить маршрут','Подобрать экскурсионный тур','Подобрать круиз'];icons=['i-building','i-plane','i-car','i-file','i-shield','i-lounge','i-compass','i-heart']
 for i,s in enumerate(D['services']):
  key='service:'+s['id'];attrs=ED('services.'+s['id'],True)+' data-service-topic="'+key+'" id="'+s['id']+'"'
  if s['group']=='travel':
   target,label=targets[s['id']];cards+='<article class="service-travel-card" '+attrs+'>'+C['image'](path,p['servicePhotos'][s['id']],s['title'],key='services.'+s['id']+'.photo')+'<div><h3>'+E(s['title'])+'</h3><p>'+E(s['text'])+'</p>'+shared.action(labels[i],key,'service_request_'+s['id'])+L(path,target,label+' →','service_more_'+s['id'],'text-link')+'</div></article>'
  else:tiles+='<button class="service-extra-card" type="button" data-open-form="'+key+'" data-goal="service_'+s['id']+'" '+attrs+'>'+I(icons[i-4])+'<span><strong>'+E(s['title'])+'</strong><span>'+E(s['text'])+'</span></span>'+I('i-arrow')+'</button>'
 intro='Выберите, с чем Вам нужна помощь.';cover='<section class="inner-cover services-cover" data-inner-cover><div class="container">'+C['crumb'](path,[('Услуги',None)])+'<div class="services-intro"><div><h1 data-editable="services.h1">Услуги</h1><p class="inner-lead" '+ED('services.intro')+'>'+intro+'</p></div><div><p '+ED('services.fast')+'>Быстрее всего — написать менеджеру</p>'+channels('contact','services_hero')+'</div></div></div></section>'
 body=C['section']('Путешествия','<div class="service-travel-grid">'+cards+'</div>')+C['section']('Для поездки','<div class="service-extra-grid">'+tiles+'</div>')+'<section class="section service-help"><div class="container"><h2 '+ED('services.multiple')+'>Нужна помощь сразу с несколькими вопросами? Расскажите о своих планах.</h2>'+channels('contact','services_multiple')+'</div></section>'
 original_emit(path,'Услуги — Mango Travel','Выберите, с чем Вам нужна помощь. Путешествия и организация поездки с Mango Travel.','Услуги',intro,body,[('Услуги',None)],cover_override=cover,contact_override='',raw=True,page_class='services-page')

def work():
 w=D['work13'];path='kak-my-rabotaem/index.html';facts=''.join('<div '+ED('work13.facts.'+str(i),True)+'>'+I('i-check')+'<span>'+E(t)+'</span></div>'for i,t in enumerate(w['facts']))
 cover='<section class="inner-cover work-cover" data-inner-cover><div class="container">'+C['crumb'](path,[('Как мы работаем',None)])+'<div class="work-hero-grid"><div><h1 '+ED('work13.h1')+'>'+E(w['h1'])+'</h1><p class="inner-lead" '+ED('work13.intro',True)+'>'+E(w['intro'])+'</p><a class="text-link" href="#cost" data-goal="work_cost">'+E(w['costTitle'])+' ↓</a><div class="work-facts">'+facts+'</div></div>'+C['image'](path,'@summer-hotel.webp','Отель у воды',False,key='work13.heroPhoto')+'</div></div></section>'
 nav='<nav class="work-stepper" aria-label="Этапы поездки"><div class="container">'+''.join('<a href="#'+s['id']+'" data-work-stage-link="'+s['id']+'" data-goal="work_stage_'+str(i)+'" '+ED('work13.stages.'+str(i))+'><span class="work-circle">'+str(i+1)+'</span><span><strong>'+E(s['title'])+'</strong><small>'+E(s['caption'])+'</small></span></a>'for i,s in enumerate(w['stages']))+'</div></nav>';body=nav
 for i,s in enumerate(w['stages']):
  rows=''
  for step in s['steps']:
   summary=''
   service_map={'Экскурсии и мероприятия':'experiences','Индивидуальный трансфер':'transfer','Бизнес-залы':'airport'}
   for block in step['summaryBlocks']:
    kind=block['type']
    if kind=='heading':summary+='<h4>'+E(block['text'])+'</h4>'
    elif kind=='chips':summary+='<div class="work-chips">'+''.join(L(path,'uslugi/index.html#'+service_map[t],E(t),'work_service_'+service_map[t])if t in service_map else'<span>'+E(t)+'</span>'for t in block['items'])+'</div>'
    elif kind=='list':
     tag='ol'if block['ordered']else'ul';summary+='<'+tag+'>'+''.join('<li>'+E(t)+'</li>'for t in block['items'])+'</'+tag+'>'
    elif kind=='caption':summary+='<p '+ED('work13.selectionCaption',True)+'>'+E(block['text'])+'</p>'
    elif kind=='channels':summary+=channels('home','work_support')
    elif kind=='services':summary+=L(path,'uslugi/index.html','Все услуги →','work_services','text-link')
   if step['id']=='choice':summary=C['image'](path,'hero-resort.webp','Отель — иллюстрация к подборке',key='work13.selectionPhoto').replace('<img ','<img data-needs-approval="photo" ')+summary
   rows+='<article class="work-timeline-step" id="'+step['id']+'" '+ED('work13.steps.'+step['id'],step['needsApproval'])+'><div><h3>'+E(step['title'])+'</h3>'+''.join('<p>'+E(t)+'</p>'for t in step['paragraphs'])+'</div><aside class="work-summary'+(' keep-on-phone'if step['id']=='trip-plans'else'')+'">'+summary+'</aside></article>'
  body+='<section class="section work-stage" id="'+s['id']+'" data-work-stage '+ED('work13.stages.'+str(i))+'><div class="container"><h2>'+E(s['title'])+'</h2>'+rows+'</div></section>'
 body+='<section class="section work-cost" id="cost"><div class="container"><h2 '+ED('work13.costTitle')+'>'+E(w['costTitle'])+'</h2><p '+ED('work13.costText',True)+'>'+E(w['costText'])+'</p></div></section><section class="section" id="contact"><div class="container unified-end-grid"><div><h2 '+ED('work13.finalTitle')+'>'+E(w['finalTitle'])+'</h2>'+'</div>'+form(path,'home','end')+'</div></section>'
 # Preserve incoming anchors used by existing links.
 body=re.sub(r'(<article\b[^>]*\bid="support"[^>]*>)',r'\1<span id="soprovozhdenie" class="section-anchor" aria-hidden="true"></span>',body,count=1)
 return original_emit(path,'Как мы работаем — Mango Travel','Подбор, подготовка и сопровождение путешествия с персональным менеджером Mango Travel.','Как мы работаем','',body,[('Как мы работаем',None)],cover_override=cover,contact_override='',raw=True,page_class='process-page')

def emit(*args,**kw):
 if args[0]=='kak-my-rabotaem/index.html':return work()
 compact=['o-nas/index.html','o-nas/otzyvy/index.html','o-nas/kontakty/index.html','o-nas/dokumenty/index.html','o-nas/dokumenty/rekvizity/index.html','napravleniya/index.html','predlozheniya/index.html','zagranpasport/index.html']
 if args[0]in compact:
  kw['page_class']=(kw.get('page_class','')+' compact-content-page').strip()
  args=list(args);args[5]=re.sub(r'<section\b', '<section data-content-start',args[5],count=1)
  args[5]=re.sub(r'<div class="section-head"><h2[^>]*>\s*</h2></div>','',args[5])
 if kw.get('cover_override')is None and not kw.get('photo'):
  path=args[0];heading='<div><h1 '+ED(path+'.title')+'>'+E(args[3])+'</h1>'+('<p class="inner-lead">'+args[4]+'</p>'if args[4]else'')+'</div>'
  contact=''if kw.get('about')or path=='o-nas/kontakty/index.html'else'<div class="page-heading-contact"><p '+ED('cover.fast')+'>Быстрее всего — написать менеджеру</p>'+channels(shared.page_topic(path),'cover_message')+'</div>'
  kw['cover_override']='<section class="inner-cover" data-inner-cover><div class="container">'+C['crumb'](path,args[6])+'<div class="page-heading-grid">'+heading+contact+'</div></div></section>'
 return original_emit(*args,**kw)

def quiz(path):
 return '<dialog id="quiz-dialog" class="quiz-dialog selection-dialog" aria-modal="true" aria-labelledby="quiz-title"><div class="dialog-top"><h2 id="quiz-title">Помогите выбрать</h2><button class="icon-btn" type="button" data-dialog-close data-goal="quiz_close" aria-label="Закрыть">'+I('i-close')+'</button></div>'+form(path,'quiz','quiz',mode='pick',heading=False)+'</dialog>'

def documents():
 path='o-nas/dokumenty/index.html';items=[('Реквизиты и реестр турагентов','o-nas/dokumenty/rekvizity/index.html'),('Документы для клиента','o-nas/dokumenty/index.html#client-documents'),('Политика обработки персональных данных','o-nas/dokumenty/politika/index.html'),('Согласие на обработку персональных данных','o-nas/dokumenty/soglasie/index.html')];rows=''
 for i,(title,target)in enumerate(items):
  rows+=L(path,target,I('i-file')+'<span><strong>'+title+'</strong><small>'+('На согласовании'if i==1 else'Страница')+'</small></span>'+I('i-arrow-up'),'document_'+str(i),'document-card document-row',('id="client-documents" 'if i==1 else'')+ED('documents.'+str(i),i==1))
 emit(path,'Документы — Mango Travel','Реквизиты, выписка из реестра турагентов, документы для клиента и обработка персональных данных. Mango Travel.','Документы','',C['section']('','<div class="document-grid">'+rows+'</div>'),[('О нас','o-nas/index.html'),('Документы',None)],about=True,contact_override='',raw=True)
 import stage11
 stage11.requisites()
