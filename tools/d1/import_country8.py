"""Explicit import of the approved revision-3 draft; normal builds need only stdlib."""
from pathlib import Path
from html import unescape
import json,re,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[2]
def source_data():
 return json.loads(subprocess.check_output(['node','tools/d1/read_schema8.cjs'],cwd=ROOT))
def copy_data():
 s=(ROOT/'mango-structure-12-11-v2.html').read_text();s=s[s.index('  function countryPage('):s.index('  function renderWeather(')]
 clean=lambda x:unescape(re.sub('<[^>]+>','',x)).strip()
 def intro(id):return clean(re.search(r'id="'+id+r'"[\s\S]*?<p class="intro">(.*?)</p>',s)[1])
 tips=[dict(title=clean(a),text=clean(b))for a,b in re.findall(r'<div class="tip"><h3>(.*?)</h3><p class="small">(.*?)</p></div>',s)]
 fragment=s[s.index('id="experiences"'):s.index('id="essentials"')]
 experiences=[dict(title=clean(a),text=clean(b),photo=None)for a,b in re.findall(r'<article class="card">.*?<h3>(.*?)</h3><p class="small">(.*?)</p>.*?</article>',fragment)]
 return dict(subtitle=clean(re.search(r'<h1>Туры в Египет</h1>\s*<p>(.*?)</p>',s)[1]),seasonIntro=intro('season'),resortsIntro=intro('resorts'),tips=tips,experiences=experiences,combine=clean(re.search(r'<h3>Можно совместить</h3><p class="small">(.*?)</p>',fragment)[1]))
if __name__=='__main__':
 dpath=ROOT/'tools/d1/data.json';D=json.loads(dpath.read_text());S=source_data();copy=copy_data();names={c['name']:c['slug']for c in D['countries']}
 for c in D['countries']:
  c['placesMode']='routes'if c['slug']=='kitay'else'resorts';c['climate']={};c['monthNotes']={};c['tips']=[];c['seasonIntro']='';c['resortsIntro']='';c['combine']=''
  for r in c['resorts']:
   r['w']=r['id']
   for old in ['air','water','wind','windRain','monthNotes']:r.pop(old,None)
  if c['slug']=='egipet':
   c.update(copy);c['resorts']=[dict(r,photo=None)for r in S['resorts']];c['climate']=S['climate'];c['monthNotes']={'redSea':S['redSeaLines'],'alamein':S['alameinLines']};c['hotels']=[dict(h,photos=[])for h in S['hotels']];c['essentials']={x['id']:dict(answer=x['a'],question=x['q'],checkedDate='ноябрь 2026')for x in S['essentials']};c['routes']=[dict(id=k,name=v,stops='',pace='',photo=None)for k,v in S['routes'].items()];c['alternatives']=[dict(country=names[a['name']],flight=a['flight'],season=a['season'])for a in S['egyptAlternatives']]
  else:
   c['hotels']=[];c['essentials']={};c['experiences']=[]
   if c['placesMode']=='routes':c['routes']+=[dict(id='hainan',name='остров Хайнань',stops='',pace='',photo=None)]
   elif c['routes']:c['experiences']=[dict(title=r['name'],text='',routeId=r['id'],photo=r.get('photo'))for r in c['routes']]
   others=[o for o in D['countries']if o['slug']!=c['slug']and o.get('published',True)][:4]
   c['alternatives']=[dict(country=o['slug'],flight=next(v['flight']for v in S['countries']if v['name']==o['name']),season=next(v['season']for v in S['countries']if v['name']==o['name']))for o in others]
 D['country_source_revision']='12.11 · Египет, редакция 3';D['country_source_sha256']=hashlib.sha256((ROOT/'mango-structure-12-11-v2.html').read_bytes()).hexdigest();D['country_source_file']='mango-structure-12-11-v2.html'
 dpath.write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
