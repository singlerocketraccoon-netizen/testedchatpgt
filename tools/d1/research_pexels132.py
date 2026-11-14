"""Development-only Pexels research; retain only public photo attribution fields."""
from pathlib import Path
from PIL import Image,ImageOps,ImageStat,ImageFilter
import urllib.request,urllib.parse,re,json,time,io,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path('/tmp/stage132/candidates');CACHE=Path('/tmp/stage132/pexels-search');CACHE.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/d1'));from research_photos132 import QUERIES
QUERIES.update({'lake':('Озеро Брайес, Италия','lake braies boat'),'breakfast':('Завтрак — иллюстрация','breakfast'),'belarus':('Мирский замок, Беларусь','Mir castle Belarus'),'cappadocia':('Каппадокия на рассвете','cappadocia sunrise'),'north-male':('Тулусду, Северный Мале','Thulusdhoo Maldives'),'south-male':('Маафуши, Южный Мале','Maafushi Maldives'),'baa':('Дараванду, атолл Баа','Dharavandhoo Maldives'),'family-beach':('Семейный отдых у моря','family on beach landscape'),'mountain-hotel-1':('Горный отель — иллюстрация','chalet mountain hotel'),'mountain-hotel-2':('Зимний горный отель — иллюстрация','alpine chalet snow'),'mountain-hotel-3':('Отель среди гор — иллюстрация','alpine hotel summer')})
def get(url):
 for retry in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)as r:return r.read()
  except Exception:
   if retry==2:raise
   time.sleep(3)
def find(key):
 label,query=QUERIES[key];cache=CACHE/(key+'.html')
 if cache.exists():s=cache.read_text()
 else:time.sleep(2);s=get('https://www.pexels.com/search/'+urllib.parse.quote(query,safe='')+'/').decode();cache.write_text(s)
 m=re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',s)
 if not m:return[]
 rows=json.loads(m[1])['props']['pageProps'].get('initialData',{}).get('data',[]);result=[]
 for row in rows:
  a=row.get('attributes',{});width=a.get('width',0);height=a.get('height',1);pid=str(a.get('id',''));license=a.get('license','')
  if width<1200 or not 1.25<width/max(height,1)<2.8 or license!='Pexels' or not a.get('published'):continue
  if key in ['baa','north-male','jimbaran','alamein']:
   proof=(a.get('description','')+' '+a.get('title','')+' '+' '.join(t['name']for t in a.get('tags',[]))).lower();terms={'baa':['baa','dharavandhoo','reethi','horubadhoo','hanifaru'],'north-male':['thulusdhoo','north male','bandos','meeru','dhiffushi','huraa','himmafushi'],'jimbaran':['jimbaran'],'alamein':['alamein','al alamayn']}[key]
   if not any(t in proof for t in terms):continue
  image=a['image']['large'].split('?')[0]+'?auto=compress&cs=tinysrgb&w=1280';candidate=key+'-pexels-'+pid+'.webp';meta=OUT/(candidate+'.json')
  if meta.exists():entry=json.loads(meta.read_text())
  else:
   try:
    im=ImageOps.exif_transpose(Image.open(io.BytesIO(get(image)))).convert('RGB');luma=ImageStat.Stat(im.convert('L')).mean[0]
    if luma<107:continue
    im=im.resize((1200,round(im.height*1200/im.width)),Image.Resampling.LANCZOS)
    for q in[86,80,74,68,60,52]:
     buf=io.BytesIO();im.save(buf,format='WEBP',quality=q,method=6)
     if len(buf.getvalue())<=200000:break
    if len(buf.getvalue())>200000:continue
    (OUT/candidate).write_bytes(buf.getvalue());user=a['user'];source='https://www.pexels.com/photo/'+a['slug']+'-'+pid+'/'
    entry={'candidate':candidate,'file':'place-'+key+'.webp','url':source,'download_url':image,'author':(user.get('first_name','')+' '+user.get('last_name','')).strip(),'license':{'name':'Pexels License','url':'https://www.pexels.com/license/','commercial_use':True,'attribution_required':False},'alt':label,'description':a.get('description')or a.get('alt')or a.get('title'),'source_title':a.get('title'),'source_tags':[t['name']for t in a.get('tags',[])],'width':im.width,'height':im.height,'original_width':width,'original_height':height,'luminance':round(luma,2),'bytes':len(buf.getvalue()),'sha256':hashlib.sha256(buf.getvalue()).hexdigest(),'provider':'Pexels','asset_kind':'photo','checked':'2026-11-14','changes':'Resized to 1200 px and compressed to WebP; no AI generation or alteration of the depicted place.'};meta.write_text(json.dumps(entry,ensure_ascii=False,indent=2))
   except Exception as e:print('candidate failed',key,str(e)[:60],flush=True);continue
  result.append(entry)
  if len(result)>=4:break
 return result
if __name__=='__main__':
 path=Path('/tmp/stage132/pexels-candidates.json');report=json.loads(path.read_text())if path.exists()else{}
 keys=sys.argv[1:]or ['belarus','cappadocia','hikkaduwa','jimbaran','abu-dhabi','baa','alamein','north-male','south-male','mountain-russia','mountain-turkey','abu-dabbab','sinai','mountain-hotel-1','mountain-hotel-2','mountain-hotel-3','family-beach','breakfast','dubai','great-wall','sea-cruise-day','scenic-road','maldives-day']
 for key in keys:
  if key in report:continue
  try:report[key]=find(key)
  except Exception as e:report[key]=[];print(key,'ERROR',e,flush=True)
  path.write_text(json.dumps(report,ensure_ascii=False,indent=2));print(key,len(report[key]),flush=True)
