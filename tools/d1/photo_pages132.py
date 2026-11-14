"""Public unique-photo credits and private review reports, all generated statically."""
import json,re

def build(C,uses,registry):
 E=C['E'];U=C['url'];S=C['SITE'];path='PHOTOS13_1.html';arrow='<svg class="external-photo-link" aria-hidden="true" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 18 18 6M6 6h12v12"/></svg>'
 unique={u['asset']:u for u in uses if u['asset']};assets=[]
 for asset,use in unique.items():
  entry=registry.get(asset[1:]if asset.startswith('@')else'../../../assets/img/'+asset,{})
  if entry.get('asset_kind')!='photo':continue
  assets.append((asset,entry,use))
 def src(asset,page):return U(page,'img/'+asset[1:]if asset.startswith('@')else'../../assets/img/'+asset)
 def picture(asset,entry,page):
  width,height=C['DATA']['image_dimensions'][asset];return '<img src="'+src(asset,page)+'" alt="'+E(entry.get('alt','Путешествие'))+'" width="'+str(width)+'" height="'+str(height)+'" loading="lazy" decoding="async" data-editable="photoCredits.'+E(asset)+'.image">'
 def license_link(entry,goal):
  license=entry.get('license',{});return '<a href="'+E(license.get('url',''))+'" target="_blank" rel="noopener" data-goal="'+goal+'">'+E(license.get('name',''))+arrow+'</a>'
 rows=''
 for i,(asset,entry,use)in enumerate(assets):
  author=entry.get('author')or entry.get('photographer')or entry.get('provider','');caption=entry.get('caption')or entry.get('alt')or use['alt'];rows+='<article class="photo-credit-row" data-editable="photoCredits.'+str(i)+'">'+picture(asset,entry,path)+'<h2>'+E(caption)+'</h2><div class="photo-credit-author"><span>Автор</span><a href="'+E(entry['url'])+'" target="_blank" rel="noopener" data-goal="photo_credit_source">'+E(author)+' ↗</a></div><div class="photo-credit-license"><span>Лицензия</span>'+license_link(entry,'photo_credit_license')+'</div></article>'
 cover='<section class="inner-cover" data-inner-cover><div class="container">'+C['crumb'](path,[('Фото и лицензии',None)])+'<h1 data-editable="photoCredits.title">Фото и лицензии</h1><p class="inner-lead" data-editable="photoCredits.intro">Авторы фотографий, которые Вы видите на сайте, и условия их использования.</p></div></section>'
 body='<section class="section photo-credits-section"><div class="container"><div class="photo-credit-head" aria-hidden="true"><span>Фотография</span><span>Что изображено</span><span>Автор</span><span>Лицензия</span></div><div class="photo-credits-list">'+rows+'</div><p class="photo-changes" data-editable="photoCredits.changes">Фотографии уменьшены и сжаты для сайта. Кадрирование в карточках не меняет изображённое место.</p></div></section>'
 C['emit'](path,'Фото и лицензии — Mango Travel','Авторы фотографий сайта Mango Travel и ссылки на лицензии их использования.','Фото и лицензии','',body,[('Фото и лицензии',None)],cover_override=cover,contact_override='',raw=True,page_class='photo-credits-page')
 # Technical directory only; the private reports are intentionally absent from public navigation.
 directory=S/'pages.html';html=directory.read_text();html=re.sub(r'(<div class="page-directory">)(.*?)(</div>)',lambda m:m[1]+m[2]+C['link']('pages.html',path,'Фото и лицензии <small>'+path+'</small>','directory_photo_credits')+m[3],html,flags=re.S);directory.write_text(html)
 def shell(title,content):return '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+E(title)+'</title>'+C['brand_icons']('PHOTOS13_2.html')+'<link rel="stylesheet" href="css/tokens.css"><link rel="stylesheet" href="css/fonts.css"><link rel="stylesheet" href="css/base.css"><link rel="stylesheet" href="css/photo-inventory.css"></head><body><main class="photo-inventory"><h1>'+E(title)+'</h1>'+content+'</main></body></html>\n'
 grid=''
 for asset,entry,use in assets:grid+='<figure>'+picture(asset,entry,'PHOTOS13_2.html')+'<figcaption><strong>'+E(entry.get('caption')or entry.get('alt')or use['alt'])+'</strong><span>'+E(entry.get('author')or entry.get('provider',''))+'</span>'+license_link(entry,'qa_photo_license')+'</figcaption></figure>'
 (S/'PHOTOS13_2.html').write_text(shell('Фото · проверка качества','<div class="qa-photo-grid">'+grid+'</div>'))
 table=''
 for u in uses:
  asset=u['asset'];image=picture(asset,registry.get(asset[1:]if asset.startswith('@')else'../../../assets/img/'+asset,{}),'QA_PHOTO_USAGE13_2.html')if asset else'<span>Обложка без фото</span>'
  table+='<tr><td>'+E(u['path'])+'</td><th scope="row">'+E(u['title'])+'</th><td>'+image+'</td><td>'+E(u['key'])+'</td></tr>'
 (S/'QA_PHOTO_USAGE13_2.html').write_text(shell('Фото · таблица использований','<table><thead><tr><th>Страница</th><th>Карточка</th><th>Фото</th><th>Ключ данных</th></tr></thead><tbody>'+table+'</tbody></table>'))
 (S/'PHOTOS13_2.json').write_text(json.dumps({'unique':len(assets),'uses':uses},ensure_ascii=False,indent=2)+'\n')
