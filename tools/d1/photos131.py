"""Place-safe photo rendering and deterministic, attributed photo inventory."""
import re,json
from collections import defaultdict
def configure(ctx):
 global C,D,E,U,original_image,usage,registry
 C=ctx;D=ctx['DATA'];E=ctx['E'];U=ctx['url'];original_image=ctx['image'];usage={};registry={r['file']:r for r in json.loads((ctx['SITE']/'img/sources.json').read_text())}
 ctx['image']=image;ctx['illustrative_photo']=photo
 import country
 country.photo=photo
 # The default hero in a country must not pretend a cover is a photo.
 original_emit=ctx['emit']
 def emit(*args,**kw):
  path=args[0];key='countries.'+path.split('/')[1]+'.heroPhoto'if path.startswith('napravleniya/')and path.count('/')==2 else''
  if key in D['photo131']['entries']and not D['photo131']['entries'][key]['asset']:
   kw['photo']=None;kw['cover_override']=kw['cover_override'].replace('class="country-hero"','class="country-hero country-no-photo"')
  return original_emit(*args,**kw)
 ctx['emit']=emit

def render(path,name,alt,lazy,cls,key):
 entry=D.get('photo131',{}).get('entries',{}).get(key);label=entry['label']if entry else re.sub(r'^(Фото курорта |Фото: |Фото )','',alt)
 if entry:
  name=entry['asset'];alt=entry.get('alt',label)
 if not name:
  usage[(path,key)]={'path':path,'key':key,'title':label,'asset':None,'alt':label}
  return '<div class="place-cover '+E(cls)+'" data-editable="'+E(key)+'" data-needs-approval="photo" role="img" aria-label="'+E(label)+'">'+C['icon']('i-compass')+'<span>'+E(label)+'</span></div>'
 html=original_image(path,name,alt,lazy,cls,key)
 if entry:html=html.replace(' data-needs-approval="photo"','').replace('<img ','<img data-needs-approval="photo" ',1)
 usage[(path,key)]={'path':path,'key':key,'title':label,'asset':name,'alt':alt}
 return html

def image(path,name,alt,lazy=True,cls='',key='media'):return render(path,name,alt,lazy,cls,key)
def photo(path,name,alt,key,lazy=True):return render(path,name,alt,lazy,'',key)
def finish(ctx):
 path='PHOTOS13_1.html';rows=''
 for item in usage.values():
  a=item['asset'];entry=registry.get(a[1:]if a and a.startswith('@')else'../../../assets/img/'+a,{})if a else{}
  visual=('<img src="'+U(path,'img/'+a[1:]if a.startswith('@')else'../../assets/img/'+a)+'" alt="'+E(item['alt'])+'" width="120" height="80" loading="lazy">')if a else'<span class="photo-inventory-cover">'+ctx['icon']('i-compass')+'Обложка без фото</span>'
  license=entry.get('license',{});author=entry.get('author')or entry.get('photographer')or entry.get('provider','');source=entry.get('url','');licenseurl=license.get('url','')
  sourcehtml=('<a href="'+E(source)+'" data-goal="photo_source">'+E(author or'Источник')+' ↗</a>')if source else'—'
  licensehtml=('<a href="'+E(licenseurl)+'" data-goal="photo_license">'+E(license.get('name',''))+'</a>')if licenseurl else'Не требуется'
  rows+='<tr><td><a href="'+U(path,item['path'])+'" data-goal="photo_page">'+E(item['path'])+'</a></td><th scope="row">'+E(item['title'])+'</th><td>'+visual+'</td><td>'+sourcehtml+'</td><td>'+licensehtml+'</td></tr>'
 html='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Фото и лицензии — Mango Travel</title><meta name="robots" content="noindex,follow"><link rel="stylesheet" href="css/fonts.css"><link rel="stylesheet" href="css/tokens.css"><link rel="stylesheet" href="css/base.css"><link rel="stylesheet" href="css/photo-inventory.css"></head><body><main class="photo-inventory"><a class="text-link" href="index.html" data-goal="photos_home">← Главная</a><h1>Фото и лицензии</h1><p>Изображения мест и нейтральные иллюстрации отелей. Обложка без фото означает, что подходящий свободный снимок пока не выбран. Все новые фото с Commons уменьшены до 1200 px и сжаты в WebP; авторство и ссылки приведены ниже.</p><table><caption>Страница · заголовок карточки · фото · источник · лицензия</caption><thead><tr><th>Страница</th><th>Заголовок карточки</th><th>Фото</th><th>Источник / автор</th><th>Лицензия</th></tr></thead><tbody>'+rows+'</tbody></table></main></body></html>\n'
 html=html.replace('</head>',ctx['brand_icons'](path)+'</head>')
 (ctx['SITE']/path).write_text(html)
 (ctx['SITE']/'PHOTOS13_1.json').write_text(json.dumps(list(usage.values()),ensure_ascii=False,indent=2)+'\n')
