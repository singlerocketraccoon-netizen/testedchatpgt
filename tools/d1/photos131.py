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
  if key in (D.get('photo132')or D['photo131'])['entries']and not (D.get('photo132')or D['photo131'])['entries'][key]['asset']:
   kw['photo']=None;kw['cover_override']=kw['cover_override'].replace('class="country-hero"','class="country-hero country-no-photo"')
  return original_emit(*args,**kw)
 ctx['emit']=emit

def render(path,name,alt,lazy,cls,key):
 entry=(D.get('photo132')or D.get('photo131',{})).get('entries',{}).get(key);label=entry['label']if entry else re.sub(r'^(Фото курорта |Фото: |Фото )','',alt)
 if entry:
  name=entry['asset'];alt=entry.get('alt',label)
 policy=D.get('photo132',{});mapped=policy.get('defaultAssets',{}).get(name)
 if mapped:
  name=mapped;alt=registry.get(name[1:]if name.startswith('@')else'../../../assets/img/'+name,{}).get('alt',alt)
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
 import photo_pages132
 photo_pages132.build(ctx,list(usage.values()),registry)
