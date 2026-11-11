"""One data-driven template for the four approved holiday sections."""
from html import escape as esc

def build_rest_pages(ctx):
 data=ctx['DATA'];E=ctx['E'];image=ctx['image'];url=ctx['url'];link=ctx['link'];icon=ctx['icon'];ed=ctx['editable'];emit=ctx['emit'];crumb=ctx['crumb']
 from online import channel_links,page_settings
 for page in data['rest_pages']:
  order=page.get('section_order',data['rest_section_order']);slug=page['slug'];path=f'otdyh/{slug}/index.html';base='rest.'+slug
  def form(place):
   fields=''
   for i,label in enumerate(page['fields']):
    phone=label=='Телефон';name='phone'if phone else'field_'+str(i)
    fields+=f'<label class="field-label"><span {ed(base+".form.fields."+str(i))}>{E(label)}</span><input name="{name}" type="{"tel"if phone else"text"}"'+(' inputmode="tel" autocomplete="tel" maxlength="18" required'if phone else' maxlength="120"')+f' data-editable="{base}.form.input.{i}"></label>'
   return f'<!-- component: rest-form --><div class="rest-inquiry" id="rest-inquiry-{place}"><h2 {ed(base+".form.title")}>{E(page["form_title"])}</h2><p class="rest-section-badge" {ed(base+".form.section")}>Раздел: {E(page["accent"])}</p><p class="rest-chosen" data-choice-output data-prefix="Вы выбрали: " aria-live="polite" hidden></p>{channel_links(page["message"],"rest_"+place)}<p class="callback-caption" {ed(base+".form.callback")}>Удобнее звонок? Оставьте номер — перезвоним</p><form data-rest-form novalidate><fieldset data-rest-guard disabled><legend class="sr-only">{E(page["form_title"])}</legend><input type="hidden" name="topic" value="{E(page_settings(path)["topic"])}">{fields}<label class="consent" {ed(base+".consent",True)}><input type="checkbox" name="consent" required><span><a href="{url(path,"o-nas/dokumenty/soglasie/index.html")}" target="_blank" rel="noopener" data-goal="rest_consent_read">Согласие на обработку персональных данных</a></span></label><p class="form-error" role="alert" data-rest-error data-phone-error="Укажите телефон полностью." data-consent-error="Пожалуйста, отметьте согласие на обработку данных."></p><button type="submit" class="btn btn-primary" data-rest-submit data-goal="rest_submit" disabled>Подобрать отдых {icon("i-arrow")}</button></fieldset></form><div class="form-success" data-rest-success role="status" tabindex="-1" hidden>{icon("i-check-circle")}<p>Спасибо, менеджер свяжется с Вами</p></div><noscript><a href="tel:+78512299547" data-goal="rest_phone_nojs">+7 (8512) 29-95-47</a></noscript></div><!-- /component: rest-form -->'
  def contactline(text,part):
   return f'<div class="rest-contact-line"><p {ed(base+"."+part+".contact")}>{E(text)}</p><div>{channel_links(page["message"],"rest_"+part)}<a href="#rest-inquiry-top" class="text-link" data-rest-select="{E(page["accent"])}" data-goal="rest_{part}_select">Подобрать отдых {icon("i-arrow")}</a></div></div>'
  def section(part,title,body,cls=''):
   return f'<section class="section rest-content-section {cls}" id="{part}" data-rest-section><div class="container"><div class="section-head"><h2 {ed(base+"."+part+".title")}>{E(title)}</h2></div>{body}</div></section>'
  def checks():
   cards=''
   for i,c in enumerate(page['checks']):
    example=f'<aside class="rest-example" {ed(base+".checks."+str(i)+".example",True)}><strong>Например:</strong> <span>{E(c["example"])}</span></aside>'if c['example']else''
    cards+=f'<article class="rest-check-card" {ed(base+".checks."+str(i))}><span class="rest-check-number" aria-hidden="true">{i+1:02}</span><p>{E(c["text"])}</p>{example}</article>'
   return section('checks',page['checks_title'],'<div class="rest-check-grid">'+cards+'</div>'+contactline(page['checks_contact'],'checks'))
  def types():
   cards=''.join(f'<a href="#rest-inquiry-top" class="rest-type-card" data-rest-select="{E(t["title"])}" data-goal="rest_type_{i}" {ed(base+".types."+str(i),True)}><span class="rest-type-number" aria-hidden="true">0{i+1}</span><h3>{E(t["title"])}</h3><p>{E(t["text"])}</p>{icon("i-arrow")}</a>'for i,t in enumerate(page['types']))
   return section('types',page['types_title'],'<div class="rest-type-grid">'+cards+'</div>','rest-tonal')
  def countries():
   cards=''
   for i,c in enumerate(page['countries']):
    exists=any(v['slug']==c['slug']for v in data['countries']);name=link(path,'napravleniya/'+c['slug']+'/index.html',E(c['name']),'rest_country_'+c['slug'])if exists else E(c['name'])
    cards+=f'<article class="rest-country-card" {ed(base+".countries."+str(i),True)}><h3>{name}</h3><dl><div><dt>Сезон</dt><dd>{E(c["season"])}</dd></div><div><dt>Перелёт из Москвы</dt><dd>{E(c["flight"])}</dd></div></dl><p>{E(c["text"])}</p><div class="rest-country-actions"><a href="#hotels" class="text-link" data-country-hotels="{c["slug"]}" data-goal="rest_hotels_{c["slug"]}">Отели →</a><a href="#rest-inquiry-top" class="text-link" data-rest-select="{E(c["name"])}" data-goal="rest_country_select_{c["slug"]}">{E(c["select_label"])}</a></div></article>'
   note=f'<p class="rest-country-note" {ed(base+".countries.note",True)}>{E(page["countries_note"])}</p>'if page.get('countries_note')else''
   return section('countries',page['countries_title'],f'<p class="section-description" {ed(base+".countries.intro",True)}>{E(page["countries_intro"])}</p>'+note+'<div class="rest-country-grid">'+cards+'</div>')
  def hotels():
   tabs='';panels=''
   for i,c in enumerate(page['countries']):
    cs=c['slug'];tabs+=f'<a href="#hotels-{cs}" id="hotel-tab-{cs}" role="tab" aria-controls="hotels-{cs}" aria-selected="{str(i==0).lower()}" data-hotel-tab="{cs}" data-goal="rest_hotel_tab_{cs}">{E(c["name"])}</a>'
    cards=''
    for j,h in enumerate(page['hotels'][cs]):
     key=base+'.hotels.'+cs+'.'+str(j);photo=image(path,h['image'],h['name'],key=key+'.photo')if h['image']else f'<div class="rest-hotel-placeholder" role="img" aria-label="{E(h["name"])}" {ed(key+".photo")}>{icon("i-building")}</div>'
     cards+=f'<!-- component: hotel-card --><article class="rest-hotel-card" {ed(key,True)}>{photo}<div class="rest-hotel-body"><h3 {ed(key+".name")}>{E(h["name"])}</h3><p class="rest-hotel-value" {ed(key+".good")}><strong>Чем хорош:</strong> {E(h["good"] or "например, "+page["hotel_examples"][0])}</p><p class="rest-hotel-value" {ed(key+".note")}><strong>Что учесть:</strong> {E(h["note"] or "например, "+page["hotel_examples"][1])}</p><button type="button" class="text-link" data-hotel-message="{E(h["name"])}" data-goal="rest_hotel_price_{cs}_{j}">{E(page["hotel_labels"]["price"])}</button></div></article><!-- /component: hotel-card -->'
    panels+=f'<div class="rest-hotel-panel" id="hotels-{cs}" role="tabpanel" aria-labelledby="hotel-tab-{cs}" data-hotel-panel="{cs}" tabindex="0"><div class="rest-hotel-grid">{cards}</div></div>'
   return section('hotels',page['hotels_title'],'<div class="rest-hotel-tabs" role="tablist" aria-label="Страны отелей">'+tabs+'</div>'+panels+contactline(page['hotels_contact'],'hotels'),'rest-tonal')
  def questions():return section('faq',page['faq_title'],ctx['faq'](page['questions'],base+'.faq'))
  def final():return f'<section class="section rest-end" id="contact" data-rest-section><div class="container rest-end-grid"><div><h2 {ed(base+".end.title")}>{E(page["end_title"])}</h2><p {ed(base+".end.text")}>{E(page["end_text"])}</p></div>{form("bottom")}</div></section>'
  builders={'checks':checks,'types':types,'countries':countries,'hotels':hotels,'faq':questions,'final':final}
  labels={'checks':'Что проверяем','types':'Виды отдыха','countries':'Куда поехать','hotels':'Отели','faq':'Вопросы','final':'Подобрать отдых'}
  nav='<nav class="rest-anchor-nav" aria-label="На странице"><div class="container rest-anchor-rail">'+''.join(f'<a href="#{"contact"if part=="final"else part}" data-rest-anchor data-goal="rest_anchor_{part}">{labels[part]}</a>'for part in order)+'</div></nav>'
  cover=f'<section class="rest-cover" data-inner-cover>{image(path,page["hero_image"],page["accent"],False,key=base+".hero")}<div class="container">{crumb(path,[("Отдых по душе","index.html#moods"),(page["accent"],None)])}<div class="rest-cover-grid"><div class="rest-cover-copy"><p class="hero-accent" {ed(base+".accent")}>{E(page["accent"])}</p><h1 {ed(base+".h1")}>{E(page["h1"])}</h1><p {ed(base+".intro")}>{E(page["intro"])}</p></div>{form("top")}</div></div></section>'
  message=''
  body=nav+''.join(builders[part]()for part in order)
  emit(path,page['accent']+' из Астрахани — Манго',page['intro'][:157]+'…'if len(page['intro'])>160 else page['intro'],page['h1'],page['intro'],body,[('Отдых по душе','index.html#moods'),(page['accent'],None)],photo=(page['hero_image'],page['accent']),questions=page['questions'],raw=True,cover_override=cover,contact_override=message,page_class='rest-page',page_script='js/rest.js',assets=['css/rest.css'])
