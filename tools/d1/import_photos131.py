"""Development-only Commons import: reviewed queries, CC0/CC BY, resized WebP."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from PIL import Image,ImageOps
from html import unescape
import urllib.request,urllib.parse,json,re,hashlib,io,time
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/scheme2/d1/img';CACHE=Path('/tmp/stage131/search');CACHE.mkdir(parents=True,exist_ok=True)
QUERIES={
'hurghada':('Хургада','Hurghada Red Sea panorama'), 'sharm':('Шарм-эль-Шейх','Sharm el Sheikh sea coast'), 'gouna':('Эль-Гуна','El Gouna lagoon'), 'marsa':('Марса-Алам','Marsa Alam coast'), 'makadi':('Макади-Бей','Makadi Bay beach'), 'sahl':('Сахл-Хашиш','Sahl Hasheesh'), 'alamein':('Эль-Аламейн','El Alamein coast'),
'pyramids':('Пирамиды Гизы','Giza pyramids'), 'luxor':('Луксор','Luxor temple'), 'abu-dabbab':('Черепаха в Абу-Даббабе','Abu Dabbab turtle'), 'sinai':('Гора Моисея','Mount Sinai summit'),
'antalya':('Анталья','Antalya coast harbour'), 'belek':('Белек','Belek beach'), 'kemer':('Кемер','Kemer coast'), 'side':('Сиде','Side Turkey temple'), 'alanya':('Аланья','Alanya coast'), 'bodrum':('Бодрум','Bodrum harbour'), 'marmaris':('Мармарис','Marmaris bay'), 'fethiye':('Фетхие','Fethiye Oludeniz'), 'kusadasi':('Кушадасы','Kusadasi coast'), 'istanbul':('Стамбул','Istanbul Bosphorus'), 'cappadocia':('Каппадокия','Cappadocia balloons'),
'dubai':('Дубай','Dubai skyline'), 'abu-dhabi':('Абу-Даби','Abu Dhabi skyline'), 'ras-al-khaimah':('Рас-эль-Хайма','Ras Al Khaimah coast'),
'phuket':('Пхукет','Phuket beach'), 'khao-lak':('Као-Лак','Khao Lak beach'), 'samui':('Самуи','Ko Samui beach'),
'north-male':('Северный Мале','North Male Atoll'), 'south-male':('Южный Мале','South Male Atoll'), 'baa':('Атолл Баа','Baa Atoll'),
'nha-trang':('Нячанг','Nha Trang coast'), 'phu-quoc':('Фукуок','Phu Quoc beach'), 'da-nang':('Дананг','Da Nang beach'),
'bentota':('Бентота','Bentota beach'), 'hikkaduwa':('Хиккадува','Hikkaduwa beach'), 'unawatuna':('Унаватуна','Unawatuna beach'),
'hainan':('Санья, остров Хайнань','Sanya Hainan beach'), 'beijing':('Пекин','Beijing Forbidden City'), 'shanghai':('Шанхай','Shanghai skyline'), 'xian':('Сиань','Xian city wall'),
'nusa-dua':('Нуса-Дуа','Nusa Dua Bali beach'), 'jimbaran':('Джимбаран','Jimbaran beach'), 'seminyak':('Семиньяк','Seminyak beach'), 'ubud':('Убуд','Ubud rice terraces'),
'rossiya':('Россия','Saint Petersburg panorama'), 'belarus':('Беларусь','Minsk Belarus panorama'), 'gruziya':('Грузия','Tbilisi panorama'), 'tanzaniya':('Танзания','Tanzania Kilimanjaro landscape'), 'armeniya':('Армения','Armenia mountains'), 'azerbaydzhan':('Азербайджан','Azerbaijan Caucasus mountains'), 'kazahstan':('Казахстан','Kazakhstan Charyn canyon'),
'river-cruise':('Речной круиз по Волге','Volga river cruise ship'), 'sea-cruise':('Морской круиз','cruise ship sea'), 'deck-cruise':('Отдых на борту круизного лайнера','cruise ship pool deck')}
def get(url):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MangoTravelDesign/1.0 (website image attribution)'}),timeout=35)as r:return r.read()
  except Exception:
   if attempt==2:raise
   time.sleep(30 if '429' in str(__import__('sys').exception()) else 2)
def plain(s):return unescape(re.sub('<[^>]+>','',s)).strip()
def one(item):
 key,(alt,query)=item;cache=CACHE/(key+'.json')
 try:
  if cache.exists():d=json.loads(cache.read_text())
  else:
   time.sleep(8)
   q={'action':'query','format':'json','generator':'search','gsrsearch':query+' filetype:bitmap','gsrnamespace':6,'gsrlimit':25,'prop':'imageinfo','iiprop':'url|size|extmetadata','iiurlwidth':1200}
   d=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(q)));cache.write_text(json.dumps(d))
  pages=sorted(d.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',1000))
  for p in pages:
   info=p.get('imageinfo',[{}])[0];m=info.get('extmetadata',{});license=m.get('LicenseShortName',{}).get('value','');title=p['title']
   if not(license=='CC0'or license.startswith('CC BY ')and'SA'not in license):continue
   if info.get('width',0)<1200 or not .9<info.get('width',1)/max(info.get('height',1),1)<2.7:continue
   if re.search(r'\b(map|flag|logo|diagram|stamp|coat of arms)\b',title,re.I):continue
   try:
    raw=get(info.get('thumburl',info['url']));im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB');im=im.resize((1200,round(im.height*1200/im.width)),Image.Resampling.LANCZOS);buf=io.BytesIO()
    for quality in [82,76,68,60,50,40]:
     buf=io.BytesIO();im.save(buf,format='WEBP',quality=quality,method=6)
     if len(buf.getvalue())<=200000:break
    if len(buf.getvalue())>200000:continue
    filename='place-'+key+'.webp';(OUT/filename).write_bytes(buf.getvalue());return key,{'file':filename,'url':info['descriptionurl'],'download_url':info.get('thumburl',info['url']),'author':plain(m.get('Artist',{}).get('value','')),'license':{'name':license,'url':m.get('LicenseUrl',{}).get('value','https://creativecommons.org/publicdomain/zero/1.0/'),'attribution_required':license!='CC0','commercial_use':True},'alt':alt,'commons_title':title,'description':plain(m.get('ImageDescription',{}).get('value','')),'width':im.width,'height':im.height,'bytes':len(buf.getvalue()),'sha256':hashlib.sha256(buf.getvalue()).hexdigest(),'asset_kind':'photo','provider':'Wikimedia Commons','checked':'2026-11-14','changes':'Cropped only by CSS; resized to 1200 px and compressed to WebP.'}
   except Exception as e:print('candidate failed',key,str(e)[:80],flush=True)
  return key,{'missing':True,'alt':alt,'query':query}
 except Exception as e:return key,{'missing':True,'alt':alt,'error':str(e)}
if __name__=='__main__':
 manifest={};file=ROOT/'tools/d1/photo-sources131.json'
 if file.exists():manifest=json.loads(file.read_text())
 todo=[x for x in QUERIES.items()if x[0]not in manifest]
 with ThreadPoolExecutor(max_workers=1)as pool:
  for f in as_completed([pool.submit(one,x)for x in todo]):
   k,v=f.result();manifest[k]=v;file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(k,v.get('commons_title','COVER'),flush=True)
 print('Photos',sum('file'in x for x in manifest.values()),'covers',sum('missing'in x for x in manifest.values()),flush=True)
