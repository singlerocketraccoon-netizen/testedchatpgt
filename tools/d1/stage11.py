"""Owner stage 11: common navigation, review cards and legal-source page."""
import json,re
def configure(ctx):
 global C,D,E,I,U,L,ED
 C=ctx;D=ctx['DATA'];E=ctx['E'];I=ctx['icon'];U=ctx['url'];L=ctx['link'];ED=ctx['editable'];ctx.update(crumb=crumb,aboutnav=aboutnav)
 original=ctx['agency'];ctx['agency']=lambda:dict(original(),taxID=next(f['value']for f in D['requisites']['fields']if f['label']=='ИНН'))
 import stage4
 stage4.reviews_grid=reviews_grid

def crumb(path,items):
 rows='<li>'+L(path,'index.html','<span>← Главная</span>','breadcrumb_0','breadcrumb-home')+'</li>'
 for i,(label,target)in enumerate(items,1):rows+='<li>'+ (L(path,target,E(label),'breadcrumb_'+str(i))if target else'<span aria-current="page">'+E(label)+'</span>')+'</li>'
 return '<nav class="breadcrumbs" aria-label="Хлебные крошки"><ol>'+rows+'</ol></nav>'
def aboutnav(path):
 return '<nav class="section-tabs" aria-label="Раздел об агентстве">'+''.join(L(path,target,label,'about_tab_'+str(i),extra='aria-current="page"'if path==target else'aria-current="true"'if target=='o-nas/dokumenty/index.html'and path.startswith('o-nas/dokumenty/')else'')for i,(label,target)in enumerate([('О нас','o-nas/index.html'),('Отзывы','o-nas/otzyvy/index.html'),('Контакты','o-nas/kontakty/index.html'),('Документы','o-nas/dokumenty/index.html')]))+'</nav>'
def reviews_grid(home=False):
 cards=''
 for i,r in enumerate(D['reviews'][:3]):
  cards+='<!-- component: review-card --><article class="review-card" '+ED('reviews.'+str(i),i==0)+'><span class="review-quote" aria-hidden="true">«</span><blockquote>'+E(r['text'])+'</blockquote><div class="review-signature"><p class="review-author"><strong>'+E(r['name'])+'</strong></p><p class="review-destination">'+E(r['destination'])+'</p><p class="review-meta">'+E(r['date'])+' · <a href="'+E(r['source'])+'" data-goal="review_source_'+str(i)+'" '+ED('reviews.'+str(i)+'.source')+'>Источник ↗</a></p></div></article><!-- /component: review-card -->'
 return '<div class="stage4-review-grid">'+cards+'</div>'
def documents():
 path='o-nas/dokumenty/index.html';items=[('Реквизиты и реестр турагентов','o-nas/dokumenty/rekvizity/index.html'),('Документы для клиента','o-nas/dokumenty/index.html#client-documents'),('Политика обработки персональных данных','o-nas/dokumenty/politika/index.html'),('Согласие на обработку персональных данных','o-nas/dokumenty/soglasie/index.html')]
 cards=''.join('<article class="document-card"'+(' id="client-documents"'if i==1 else'')+' '+ED('documents.'+str(i),True)+'>'+I('i-file')+'<h2>'+title+'</h2>'+('<p>Место для актуального документа</p>'if i else'')+L(path,target,'Посмотреть →','document_'+str(i),'text-link')+'</article>'for i,(title,target)in enumerate(items))
 C['emit'](path,'Документы — Mango Travel','Реквизиты, выписка из реестра турагентов, документы для клиента и обработка персональных данных. Mango Travel.','Документы','',C['section']('','<div class="document-grid">'+cards+'</div>'),[('О нас','o-nas/index.html'),('Документы',None)],about=True,contact_override='',raw=True)
 requisites()
def external_label(label):
 return E(label[:-1])+'<span class="sr-only" aria-hidden="true">↗</span>'+I('i-arrow-up')if label.endswith('↗')else E(label)
def requisites():
 p=D['requisites'];path='o-nas/dokumenty/rekvizity/index.html';key='requisites';rows=''
 for i,f in enumerate(p['fields']):rows+='<div><dt>'+E(f['label'])+'</dt><dd'+(' class="pending"'if f['pending']else'')+' '+ED(key+'.fields.'+str(i),f['needsApproval'])+'>'+E(f['value'])+'</dd></div>'
 left='<section class="requisites-panel"><h2>Реквизиты агентства</h2><dl class="agency-requisites">'+rows+'</dl></section>'
 right='<section class="requisites-panel registry-panel"><h2>Номер в реестре турагентов</h2><p class="registry-number" '+ED(key+'.registryNumber')+'>'+E(p['registryNumber'])+'</p><p '+ED(key+'.registryHint')+'>'+E(p['registryHint'])+'</p><a href="'+E(p['registryUrl'])+'" class="btn registry-check" target="_blank" rel="noopener" data-goal="registry_check" '+ED(key+'.registryUrl')+'>'+external_label(p['registryLabel'])+'</a></section>'
 files='';dialogs=''
 for f in p['documents']:
  content='<span class="file-name">'+E(f['title'])+'</span><span class="file-format">PDF</span>'+I('i-arrow-up');attrs=ED(key+'.documents.'+f['id'])
  if f['url']:item='<a class="agency-file" href="'+E(f['url'])+'" target="_blank" rel="noopener" data-goal="agency_pdf_'+f['id']+'" '+attrs+'>'+content+'</a>'
  else:
   item='<button class="agency-file" type="button" data-agency-document="'+f['id']+'" data-goal="agency_pdf_'+f['id']+'" '+attrs+' disabled>'+content+'</button>'
   dialogs+='<dialog class="agency-file-dialog" id="agency-document-'+f['id']+'" aria-modal="true" aria-labelledby="agency-title-'+f['id']+'"><h2 id="agency-title-'+f['id']+'">'+E(f['title'])+'</h2><p>'+E(p['emptyPdfMessage'])+'</p><button class="btn btn-primary" type="button" data-dialog-close data-goal="agency_document_close_'+f['id']+'">Закрыть</button></dialog>'
  files+='<li>'+item+'</li>'
 fns='<a class="text-link agency-fns" href="'+E(p['fnsUrl'])+'" target="_blank" rel="noopener" data-goal="fns_check" '+ED(key+'.fnsUrl')+'>'+external_label(p['fnsLabel'])+'</a>'
 body=C['section']('','<div class="requisites-overview">'+left+right+'</div>')+C['section']('Документы агентства','<ul class="agency-files">'+files+'</ul>'+fns)+dialogs
 C['emit'](path,p['title']+' — Mango Travel',p['intro'],p['title'],p['intro'],body,[('О нас','o-nas/index.html'),('Документы','o-nas/dokumenty/index.html'),(p['title'],None)],about=True,contact_override='',raw=True,page_class='requisites-page',assets=['js/requisites.js'])
