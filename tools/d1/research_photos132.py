"""Development-only photo research. Candidates never enter the site without review."""
from pathlib import Path
from PIL import Image,ImageOps,ImageStat,ImageFilter
from html import unescape
import urllib.request,urllib.parse,json,re,hashlib,io,time,sys
R=Path(__file__).resolve().parents[2];OUT=Path('/tmp/stage132/candidates');OUT.mkdir(parents=True,exist_ok=True);CACHE=Path('/tmp/stage132/search');CACHE.mkdir(parents=True,exist_ok=True)
QUERIES={
'belek':('Белек','Belek beach Turkey'),'belarus':('Мирский замок, Беларусь','Mir Castle Belarus'),'rossiya':('Казань, Россия','Kazan Kremlin panorama'), 'cappadocia':('Каппадокия','Cappadocia hot air balloons'),
'hikkaduwa':('Хиккадува','Hikkaduwa beach'),'jimbaran':('Джимбаран','Jimbaran beach Bali'),'nusa-dua':('Нуса-Дуа','Nusa Dua beach'),'samui':('Самуи','Ko Samui beach landscape'),'abu-dhabi':('Абу-Даби','Abu Dhabi Corniche daytime'),'baa':('Атолл Баа','Baa Atoll Maldives'),
'neutral-hotel':('Отель у моря — иллюстрация','beach hotel resort pool'), 'kemer':('Кемер','Kemer Turkey'), 'side':('Сиде','Side Antalya temple'), 'alamein':('Эль-Аламейн','El Alamein beach'), 'phuket':('Пхукет','Phuket beach landscape'), 'ras-al-khaimah':('Рас-эль-Хайма','Ras Al Khaimah beach'),
'north-male':('Северный Мале','North Male Atoll Maldives'),'south-male':('Южный Мале','South Male Atoll Maldives'),'gruziya':('Казбеги, Грузия','Kazbegi Georgia mountains'),'tanzaniya':('Серенгети, Танзания','Serengeti landscape Tanzania'),
'mountain-russia':('Красная Поляна, Россия','Krasnaya Polyana mountains'),'mountain-turkey':('Эрджиес, Турция','Erciyes ski resort'),'abu-dabbab':('Морская черепаха под водой','sea turtle underwater Red Sea'),'sinai':('Гора Моисея, Синай','Mount Sinai summit Egypt'),
'mountain-hotel-1':('Горный отель — иллюстрация','mountain chalet hotel summer'),'mountain-hotel-2':('Горный отель зимой — иллюстрация','Alpine hotel snow chalet'),'mountain-hotel-3':('Отель среди гор — иллюстрация','mountain resort hotel Alps'),
'paris-day':('Париж','Eiffel Tower blue sky'),'great-wall':('Великая Китайская стена','Great Wall China landscape'),'dubai':('Дубай','Dubai skyline daytime'), 'phu-quoc':('Фукуок','Phu Quoc beach landscape'),'nha-trang':('Нячанг','Nha Trang beach panorama'), 'seminyak':('Семиньяк','Seminyak beach Bali'), 'antalya':('Анталья','Antalya harbour panorama'), 'fethiye':('Фетхие','Fethiye Oludeniz beach'), 'kusadasi':('Кушадасы','Kusadasi harbour'),
'family-beach':('Семейный отдых у моря','family beach seaside holiday'),'breakfast':('Завтрак у моря — иллюстрация','breakfast terrace sea'), 'river-cruise':('Речной круиз по Волге','Volga river cruise ship sunny'), 'sea-hotel-2':('Отель у моря — иллюстрация','resort pool sea view')}
QUERIES.update({'scenic-road':('Дорога среди гор — иллюстрация','Georgia mountain road landscape'),'sea-cruise-day':('Морской круиз — иллюстрация','cruise ship Caribbean aerial'),'maldives-day':('Мальдивы','Maldives beach landscape')})
QUERIES.update({'baa-resort':('Атолл Баа','Royal Island Maldives panoramio'),'north-male-resort':('Северный Мале','Thulusdhoo Maldives panoramio'),'alamein-marina':('Эль-Аламейн','Marina Egypt beach panoramio'),'jimbaran-day':('Джимбаран','Jimbaran Bali panoramio -sunset -night')})
def get(url):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MangoTravelDesign/1.0 (website image attribution)'}),timeout=35)as r:return r.read()
  except Exception as e:
   if attempt==2:raise
   time.sleep(35 if '429'in str(e)else 2)
def plain(t):return unescape(re.sub('<[^>]+>','',t)).strip()
def search(key,query):
 path=CACHE/(key+'.json')
 if path.exists():return json.loads(path.read_text())
 time.sleep(6)
 q={'action':'query','format':'json','generator':'search','gsrsearch':query+' filetype:bitmap','gsrnamespace':6,'gsrlimit':50,'prop':'imageinfo','iiprop':'url|size|extmetadata','iiurlwidth':1280}
 d=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(q)));path.write_text(json.dumps(d));return d

def candidates(key,alt,query):
 d=search(key,query);result=[]
 for p in sorted(d.get('query',{}).get('pages',{}).values(),key=lambda p:p.get('index',999)):
  i=p.get('imageinfo',[{}])[0];m=i.get('extmetadata',{});license=m.get('LicenseShortName',{}).get('value','');title=p['title'];description=plain(m.get('ImageDescription',{}).get('value',''))
  if not(license=='CC0'or license.startswith('CC BY ')and'SA'not in license):continue
  if i.get('width',0)<1200 or not 1.25<=i.get('width',1)/max(i.get('height',1),1)<=2.9:continue
  if re.search(r'\b(map|flag|logo|portrait|painting|drawing|stamp|statue|handkerchief|watermark|signboard|postcard|conference|astronaut)\b',title,re.I):continue
  # Reuse a downloaded candidate only when its Commons source has not changed.
  stamp=hashlib.sha256(title.encode()).hexdigest()[:10];file=key+'-'+stamp+'.webp';meta=OUT/(file+'.json')
  try:
   if meta.exists():entry=json.loads(meta.read_text())
   else:
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(get(i.get('thumburl',i['url']))))).convert('RGB')
    luminance=ImageStat.Stat(im.convert('L')).mean[0]
    sharpness=ImageStat.Stat(im.convert('L').resize((600,round(im.height*600/im.width))).filter(ImageFilter.FIND_EDGES)).var[0]
    if luminance<98:continue
    im=im.resize((1200,round(im.height*1200/im.width)),Image.Resampling.LANCZOS)
    for quality in [86,80,74,68,60,52]:
     buf=io.BytesIO();im.save(buf,format='WEBP',quality=quality,method=6)
     if len(buf.getvalue())<=200000:break
    if len(buf.getvalue())>200000:continue
    (OUT/file).write_bytes(buf.getvalue());entry={'candidate':file,'file':'place-'+key+'.webp','url':i['descriptionurl'],'download_url':i.get('thumburl',i['url']),'author':plain(m.get('Artist',{}).get('value','')),'license':{'name':license,'url':m.get('LicenseUrl',{}).get('value','https://creativecommons.org/publicdomain/zero/1.0/'),'commercial_use':True,'attribution_required':license!='CC0'},'alt':alt,'commons_title':title,'description':description,'width':im.width,'height':im.height,'original_width':i['width'],'original_height':i['height'],'luminance':round(luminance,2),'edge_variance':round(sharpness,2),'bytes':len(buf.getvalue()),'sha256':hashlib.sha256(buf.getvalue()).hexdigest(),'provider':'Wikimedia Commons','asset_kind':'photo','checked':'2026-11-14','changes':'Resized to 1200 px and compressed to WebP; no AI generation or alteration of the depicted place.'};meta.write_text(json.dumps(entry,ensure_ascii=False,indent=2))
   result.append(entry)
   if len(result)>=4:break
  except Exception as e:print('candidate failed',key,str(e)[:60],flush=True)
 return result
if __name__=='__main__':
 reportfile=Path('/tmp/stage132/candidates.json');report=json.loads(reportfile.read_text())if reportfile.exists()else{}
 keys=sys.argv[1:]or list(QUERIES)
 for key in keys:
  if key in report:continue
  alt,query=QUERIES[key]
  try:report[key]=candidates(key,alt,query)
  except Exception as e:report[key]=[];print(key,'ERROR',e,flush=True)
  reportfile.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(key,len(report[key]),flush=True)
