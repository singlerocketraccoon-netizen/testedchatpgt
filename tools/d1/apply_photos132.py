"""Record the reviewed photo manifest into generator data; no network in a build."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];S=R/'docs/scheme2/d1';p=R/'tools/d1/data.json';D=json.loads(p.read_text());M=json.loads((R/'tools/d1/photo-sources132.json').read_text());entries={}
# A cover is intentional when the exact place has no reviewed free photograph.
def add(key,label,asset=None,kind='place'):
 entries[key]={'label':label,'asset':asset,'kind':kind,'alt':next((v['alt']for v in M.values()if asset and asset=='@'+v.get('file','')),label)}
def pic(k):return '@'+M[k]['file']if'file'in M.get(k,{})else None
country_keys={'turciya':'antalya','egipet':'pyramids','oae':'dubai','tailand':'phuket','maldivy':'north-male','vetnam':'nha-trang','shri-lanka':'bentota','kitay':'hainan','indoneziya':'ubud'}
resorts={'turciya':['antalya','belek','kemer','side','alanya','bodrum','marmaris','fethiye','kusadasi'],'egipet':['hurghada','sharm','gouna','makadi','sahl','marsa','alamein'],'oae':['dubai','abu-dhabi','ras-al-khaimah'],'tailand':['phuket','khao-lak','samui'],'maldivy':['north-male','south-male','baa'],'vetnam':['nha-trang','phu-quoc','da-nang'],'shri-lanka':['bentota','hikkaduwa','unawatuna'],'kitay':['hainan'],'indoneziya':['nusa-dua','jimbaran','seminyak']}
known={'oae':'uae.webp','maldivy':'@maldives.webp','kitay':'@china-wall.webp'}
heroes={c['slug']:pic(country_keys[c['slug']])or known.get(c['slug'])or(pic('istanbul')if c['slug']=='turciya'else pic('khao-lak')if c['slug']=='tailand'else pic('nusa-dua')if c['slug']=='indoneziya'else None)for c in D['countries']}
routekeys={'cairo':'pyramids','luxor':'luxor','istanbul':'istanbul','cappadocia':'cappadocia','beijing':'beijing','shanghai':'shanghai','xian':'xian','hainan':'hainan','ubud':'ubud'}
neutral=[pic(k)for k in ['neutral-hotel','beach-hotel-2','beach-hotel-3','beach-hotel-4','beach-hotel-5','beach-hotel-6','neutral-pool-5','neutral-pool-6']]
mountain=[pic(k)for k in ['mountain-hotel-1','mountain-hotel-2','mountain-hotel-3']]
for c in D['countries']:
 base='countries.'+c['slug'];add(base+'.heroPhoto',c['name'],heroes[c['slug']]);
 for i,r in enumerate(c['resorts']):add(base+'.resorts.'+r['id']+'.photo',r['name'],pic(resorts[c['slug']][i]))
 for r in c['routes']:add(base+'.routes.'+r['id']+'.photo',r['name'],pic(routekeys.get(r['id'],''))or heroes[c['slug']]if r['id']in['combined','custom']else pic(routekeys.get(r['id'],'')))
 for i,x in enumerate(c['experiences']):
  keys=['pyramids','luxor','abu-dabbab','sinai']if c['slug']=='egipet'else['istanbul','cappadocia','']if c['slug']=='turciya'else['ubud']
  add(base+'.experiences.'+str(i)+'.photo',x['title'],pic(keys[i])or heroes[c['slug']])
 for i,h in enumerate(c['hotels']):add(base+'.hotels.'+h['id']+'.photos',h['name'],neutral[i%len(neutral)],'neutral-beach')
for r in D['rest_pages']+[D['cruise_page']]:
 base='rest.'+r['slug']
 for i,c in enumerate(r['countries']):
  asset=heroes.get(c['slug'])or pic(c['slug'])or pic('nha-trang')if c['slug']=='vetnam-kambodzha'else heroes.get(c['slug'])or pic(c['slug'])or pic('maldives-day')if c['slug']=='shri-lanka-maldivy'else heroes.get(c['slug'])or pic(c['slug'])or pic('gruziya')if c['slug']=='gruziya-armeniya'else heroes.get(c['slug'])or pic(c['slug']);asset=pic('mountain-russia')if r['slug']=='gornyj-vozduh'and c['slug']=='rossiya'else pic('mountain-turkey')if r['slug']=='gornyj-vozduh'and c['slug']=='turciya'else pic('great-wall')if r['slug']=='ekskursionnye-tury'and c['slug']=='kitay'else asset;add(base+'.countries.'+str(i)+'.photo',c['name'],asset)
  for j,h in enumerate(r['hotels'][c['slug']]):add(base+'.hotels.'+c['slug']+'.'+str(j)+'.photo',c['name']if r['mode']=='routes'else h['name'],asset if r['mode']in['routes','tours']else mountain[j%len(mountain)]if r['slug']=='gornyj-vozduh'else neutral[j%len(neutral)],'place'if r['mode']in['routes','tours']else'neutral-mountain'if r['slug']=='gornyj-vozduh'else'neutral-beach')
 if r['mode']=='cruises':
  for i,t in enumerate(r['types']):add(base+'.types.'+str(i)+'.photo',t['title'],pic(['sea-cruise','river-cruise','deck-cruise'][i]))
for i,o in enumerate(D['offers']):
 add('offers.'+o['id']+'.photo',o['hotel'],neutral[i%len(neutral)],'neutral-beach');add('offers.'+o['id']+'.room_photo','Номер отеля',neutral[(i+1)%len(neutral)],'neutral-beach')
D.pop('photo131',None)
D['photo132']={'entries':entries,'neutralPhotos':neutral,'mountainPhotos':mountain,'policy':'Exact place or intentional cover; never an unrelated recognisable place.'}
D['photo132']['defaultAssets']={'@rest-family.webp':pic('family-beach'),'mood-family.webp':pic('family-beach'),'hero-sand.webp':pic('maldives-day'),'mood-walk.webp':pic('antalya'),'mood-dining.webp':pic('breakfast'),'@rest-excursion-city.webp':pic('paris-day'),'hero-resort.webp':pic('beach-hotel-2'),'hero-lake.webp':pic('lake'),'@rest-cruise.webp':pic('sea-cruise'),'@rest-road.webp':pic('scenic-road'),'@summer-hotel.webp':pic('beach-hotel-6'),'@vietnam-free.webp':pic('neutral-hotel'),'@maldives.webp':pic('maldives-day'),'@antalya-free.webp':pic('antalya'),'uae.webp':pic('dubai')}
sourcefile=S/'img/sources.json';sources=json.loads(sourcefile.read_text());approved={v['file']for v in M.values()if'file'in v};byfile={r['file']:r for r in sources if not r['file'].startswith('place-')or r['file']in approved}
for v in M.values():
 if'file'in v:byfile[v['file']]=dict(v,active=True)
D['image_dimensions']={k:v for k,v in D['image_dimensions'].items()if not k.startswith('@place-')or k[1:]in approved}
for v in M.values():
 if'file'in v:D['image_dimensions']['@'+v['file']]=[v['width'],v['height']]
sourcefile.write_text(json.dumps(list(byfile.values()),ensure_ascii=False,indent=2)+'\n');p.write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n');print('Mapped',len(entries),'photo positions')
