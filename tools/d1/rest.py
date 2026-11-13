"""One static template for all eight approved holiday sections."""
def build_rest_pages(ctx):
 import stage6 as shared
 D=ctx['DATA'];E=ctx['E'];U=ctx['url'];L=ctx['link'];ED=ctx['editable'];I=ctx['icon'];image=ctx['image'];emit=ctx['emit']
 for p in D['rest_pages']:
  slug=p['slug'];path='otdyh/'+slug+'/index.html';base='rest.'+slug;topic='holiday:'+slug;dialogs=[];mode=p['mode']
  def button(label,key=topic,goal='rest_select',cls='btn btn-primary'):return shared.action(label,key,goal,cls)
  def photo(name,alt,key,lazy=True):return image(path,name,alt,lazy,key=key)if name else'<div class="rest-photo-placeholder" role="img" aria-label="'+E(alt)+'" '+ED(key,True)+'>'+I('i-mood-compass')+'</div>'
  def form(place):return shared.form(path,topic,place,classes='rest-inquiry',attrs='id="rest-inquiry-'+place+'"')
  def section(part,title,content,tonal=False):return '<section class="section rest-content-section'+(' rest-tonal'if tonal else'')+'" id="'+part+'" data-rest-section="'+part+'"><div class="container"><div class="section-head"><h2 '+ED(base+'.'+part+'.title')+'>'+E(title)+'</h2></div>'+content+'</div></section>'
  def types():
   cards=''
   for i,t in enumerate(p['types']):
    key=base+'.types.'+str(i);title=E(t['title'].rstrip(':.'));body='<p '+ED(key+'.text',True)+'>'+E(t['text'])+'</p>'
    if slug=='otdyh-s-detmi':cards+='<details class="rest-age-item" '+ED(key,True)+'><summary data-goal="rest_age_'+str(i)+'">'+title+I('i-plus')+'</summary>'+body+'</details>'
    else:cards+='<article class="rest-format-card" '+ED(key,True)+'><span class="rest-format-number" aria-hidden="true">'+str(i+1).zfill(2)+'</span><h3>'+title+'</h3>'+body+button('Обсудить вариант →',topic+':type:'+str(i),'rest_type_'+str(i),'text-link')+'</article>'
   return section('types',p['types_title'],'<div class="'+('rest-age-list'if slug=='otdyh-s-detmi'else'rest-format-grid')+'">'+cards+'</div>')
  def countries():
   cards=''
   for i,c in enumerate(p['countries']):
    key=base+'.countries.'+str(i);country=next((v for v in D['countries']if v['slug']==c['slug']and v['published']),None);name=L(path,'napravleniya/'+c['slug']+'/index.html',E(c['name']),'rest_country_'+c['slug'])if country else E(c['name'])
    label='Посмотреть маршрут →'if mode=='routes'else'Посмотреть туры →'if mode=='tours'else'Посмотреть отели →';target='route-'+c['slug']if mode=='routes'else'hotels'
    cards+='<article class="rest-destination-card" '+ED(key,True)+'>'+photo(country['heroPhoto']if country else None,c['name'],key+'.photo')+'<div class="rest-destination-body"><h3>'+name+'</h3><p '+ED(key+'.text',True)+'>'+E(c['text'])+'</p><p class="rest-travel-facts" '+ED(key+'.facts',True)+'><span>'+E(c['flight'])+'</span> из Москвы · <span>'+E(c['season'])+'</span></p><div class="rest-destination-actions"><a href="#'+target+'" class="text-link" data-rest-country="'+c['slug']+'" data-goal="rest_see_'+c['slug']+'">'+label+'</a>'+button('Обсудить маршрут'if mode=='routes'else'Подобрать поездку',topic+':country:'+c['slug'],'rest_country_pick_'+c['slug'],'text-link')+'</div></div></article>'
   return section('countries',p['countries_title'],'<p class="section-description" '+ED(base+'.countries.intro',True)+'>'+E(p['countries_intro'])+'</p><div class="rest-destination-grid">'+cards+'</div>')
  def hotels():
   tabs='';panels='';routecards=''
   for i,c in enumerate(p['countries']):
    cs=c['slug'];cards=''
    if mode!='routes':tabs+='<button type="button" id="rest-tab-'+cs+'" role="tab" aria-controls="rest-panel-'+cs+'" aria-selected="'+str(i==0).lower()+'" tabindex="'+('0'if i==0 else'-1')+'" data-rest-tab="'+cs+'" data-goal="rest_tab_'+cs+'">'+E(c['name'])+'</button>'
    for j,h in enumerate(p['hotels'][cs]):
     key=base+'.hotels.'+cs+'.'+str(j);typed=topic+':hotel:'+h['id'];label='Обсудить этот маршрут'if mode=='routes'else'Узнать цену на мои даты';pic=photo(h['image'],'Фото '+(c['name']if mode=='routes'else h['name']),key+'.photo')
     title='<h3 '+ED(key+'.name',True)+'><button class="rest-card-title" type="button" data-rest-detail="'+h['id']+'" data-goal="rest_detail_title_'+h['id']+'">'+E(c['name'] if mode=='routes' else h['name'])+'</button></h3>'
     content='<p class="rest-card-location" '+ED(key+'.place',True)+'>'+(E('Города и ночи уточняются')if mode=='routes'else E(c['name'])+' · '+E(h['itinerary']))+'</p><p '+ED(key+'.good',True)+'><strong>'+E(p['hotel_good_label'])+':</strong> '+E(h['good'])+'</p>'
     if h['note']:content+='<p '+ED(key+'.note',True)+'><strong>Что учесть:</strong> '+E(h['note'])+'</p>'
     cards+='<!-- component: hotel-card --><article class="rest-selection-card"'+(' id="route-'+cs+'"'if mode=='routes'else'')+' '+ED(key,True)+'><button type="button" class="rest-card-photo" data-rest-detail="'+h['id']+'" data-goal="rest_detail_photo_'+h['id']+'" aria-label="Подробнее: '+E(c['name'] if mode=='routes' else h['name'])+'">'+pic+'</button><div class="rest-selection-body">'+title+content+button(label,typed,'rest_price_'+h['id'],'text-link')+'</div></article><!-- /component: hotel-card -->'
     dialogs.append('<dialog class="rest-detail-dialog" id="rest-detail-'+h['id']+'" aria-modal="true" aria-labelledby="rest-detail-title-'+h['id']+'"><div class="dialog-top"><h2 id="rest-detail-title-'+h['id']+'">'+E(c['name'] if mode=='routes' else h['name'])+'</h2><button class="icon-btn" type="button" data-dialog-close data-goal="rest_detail_close_'+h['id']+'" aria-label="Закрыть">'+I('i-close')+'</button></div>'+pic+'<div class="rest-detail-copy">'+content+button(label,typed,'rest_detail_price_'+h['id'])+'</div></dialog>')
    if mode=='routes':routecards+=cards;continue
    panels+='<div'+(' id="rest-panel-'+cs+'" role="tabpanel" aria-labelledby="rest-tab-'+cs+'" data-rest-panel="'+cs+'" tabindex="0"'if mode!='routes'else'')+'><div class="rest-selection-grid'+(' rest-route-grid'if mode=='routes'else'')+'">'+cards+'</div></div>'
   if mode=='routes':panels='<div class="rest-selection-grid rest-route-grid">'+routecards+'</div>'
   tablist='<div class="rest-country-tabs" role="tablist" aria-label="Страна" data-rest-tabs>'+tabs+'</div>'if tabs else''
   line='<div class="rest-selection-contact"><p '+ED(base+'.hotels.contact')+'>'+E(p['hotels_contact'])+'</p><button type="button" class="text-link" data-open-form="'+(topic if mode=='routes'else topic+':country:'+p['countries'][0]['slug'])+'" data-rest-current-topic data-goal="rest_more_selection">Обсудить подбор →</button></div>'
   return section('hotels',p['hotels_title'],tablist+panels+line,True)
  def checks():
   rows=''
   for i,c in enumerate(p['checks']):
    label,sep,body=c['text'].partition('. ');label=label.rstrip(':.');example='<aside class="rest-example" '+ED(base+'.checks.'+str(i)+'.example',True)+'>'+E(c['example'])+'</aside>'if c['example']else''
    rows+='<details class="rest-check-item" '+ED(base+'.checks.'+str(i),True)+'><summary data-goal="rest_check_'+str(i)+'">'+E(label)+I('i-plus')+'</summary><div><p>'+E(body)+'</p>'+example+'</div></details>'
   return section('checks',p['checks_title'],'<div class="rest-check-list">'+rows+'</div>')
  def faq():return section('faq',p['faq_title'],ctx['faq'](p['questions'],base+'.faq'))
  def final():return '<section class="section rest-end" id="contact" data-rest-section="final"><div class="container rest-end-grid"><div><h2 '+ED(base+'.end.title')+'>'+E(p['end_title'])+'</h2><p '+ED(base+'.end.text')+'>'+E(p['end_text'])+'</p></div>'+form('bottom')+'</div></section>'
  actions='<div class="rest-hero-actions">'+button('Обсудить маршрут'if mode=='routes'else'Подобрать отдых',topic,'rest_hero_action')+shared.channels(topic,'rest_hero')+'</div>'
  cover='<section class="rest-cover" data-inner-cover>'+photo(p['hero_image'],p['accent'],base+'.hero',False)+'<div class="container">'+ctx['crumb'](path,[('Отдых по душе','index.html#moods'),(p['accent'],None)])+'<div class="rest-cover-grid"><div class="rest-cover-copy"><p class="hero-accent" '+ED(base+'.accent')+'>'+E(p['accent'])+'</p><h1 '+ED(base+'.h1')+'>'+E(p['h1'])+'</h1><p class="rest-lead" '+ED(base+'.intro',True)+'>'+E(p['intro'])+'</p>'+actions+'</div><div class="rest-hero-form">'+form('top')+'</div></div></div></section>'
  builders=dict(types=types,countries=countries,hotels=hotels,checks=checks,faq=faq,final=final);body=''.join(builders[k]()for k in p['section_order'])+''.join(dialogs)
  emit(path,p['accent']+' из Астрахани — Манго',p['intro'][:157]+'…'if len(p['intro'])>160 else p['intro'],p['h1'],p['intro'],body,[('Отдых по душе','index.html#moods'),(p['accent'],None)],photo=(p['hero_image'],p['accent']),questions=p['questions'],raw=True,cover_override=cover,contact_override='',page_class='rest-page rest-mode-'+mode,page_script='js/main.js',assets=['css/rest.css','js/rest.js'])
 checklist='# Отдых по душе — проверить перед публикацией\n\n'+''.join('## '+p['accent']+'\n\n'+p['checklist']+'\n\n'for p in D['rest_pages']);out=ctx['SITE']/'otdyh/CHECKLIST.md';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(checklist.rstrip()+'\n')
