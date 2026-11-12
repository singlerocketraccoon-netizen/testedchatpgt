"""Import approved holiday copy once into data.json; no third-party dependency."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
FILES=['otdyh-s-detmi','tishina-i-more','plyazh-i-progulki','servis-i-kuhnya','ekskursionnye-tury','otel-radi-kotorogo-edut','gornyj-vozduh','svoj-marshrut']
def parse(slug,text,old,photo):
 blocks={int(n):v.strip() for n,v in re.findall(r'^# ([1-7])\. ([\s\S]*?)(?=^# |\Z)',text,re.M)}
 title=lambda n:blocks[n].split('\n',1)[0]
 paragraphs=lambda n:[p.strip() for p in re.split(r'\n\s*\n',blocks[n].split('\n',1)[1])if p.strip()]
 value=lambda label:re.search(r'^'+label+r': (.+)$',blocks[1],re.M)[1]
 checks=[]
 for p in paragraphs(2):
  if p.startswith('- '):checks.append({'text':p[2:],'example':''})
  elif p.startswith('Например:'):checks[-1]['example']=p
 types=[]
 for p in paragraphs(3):
  if ':'in p and not p.startswith(('Четыре','Три','Фото:')):
   a,b=p.split(':',1);types.append({'title':a.strip(),'text':b.strip()})
 country_slugs={'Россия':'rossiya','Беларусь':'belarus','Грузия':'gruziya','Армения':'armeniya','Азербайджан':'azerbaydzhan','Казахстан':'kazahstan','Танзания':'tanzaniya','Китай, остров Хайнань':'kitay','Китай':'kitay','Турция':'turciya','Египет':'egipet','ОАЭ':'oae','Таиланд':'tailand','Вьетнам':'vetnam','Мальдивы':'maldivy','Шри-Ланка':'shri-lanka','Индонезия':'indoneziya','Вьетнам и Камбоджа':'vetnam-kambodzha','Шри-Ланка и Мальдивы':'shri-lanka-maldivy','Грузия и Армения':'gruziya-armeniya'}
 countries=[]
 for line in blocks[4].splitlines():
  if not line.startswith('|')or line.startswith(('| Направление','|---')):continue
  name,season,flight,copy=[x.strip()for x in line.strip('|').split('|')]
  countries.append(dict(name=name,slug=country_slugs[name],season=season,flight=flight,text=copy))
 questions=[];q=None;answer=[]
 for p in paragraphs(6):
  if p.startswith('- '):
   if q:questions.append([q,'\n\n'.join(answer)])
   q=p[2:];answer=[]
  elif q:answer.append(p)
 if q:questions.append([q,'\n\n'.join(answer)])
 examples=re.findall(r'например, «([^»]+)»',blocks[5]);labels=re.findall(r'«(чем хорош[^»]*|что учесть)»',blocks[5])
 mode='routes'if slug=='svoj-marshrut'else'tours'if slug=='ekskursionnye-tury'else'hotels'
 checklist=text.split('# Проверить перед публикацией',1)[1].strip()
 # Instructional form/layout text is intentionally absent from the public copy audit.
 audit=[value('Акцент'),value('Заголовок'),value('Описание'),title(2),title(3),title(4),title(5),title(6)]
 for c in checks:audit.extend([c['text']]+([c['example']]if c['example']else[]))
 for t in types:audit.extend([t['title']+':',t['text']])
 for c in countries:audit.extend([c['name'],c['season'],c['flight'],c['text']])
 for q,a in questions:audit.extend([q,a])
 endtitle=re.search(r'^Заголовок: (.+)$',blocks[7],re.M)[1];endtext=re.search(r'^Строка: (.+)$',blocks[7],re.M)[1]
 contact=re.search(r'Строка связи: «([^»]+)»',blocks[5])[1];audit.extend([contact,endtitle,endtext])
 p=dict(slug=slug,source_file='razdel-'+slug+'.md',source_markdown=text,source_sha256=hashlib.sha256(text.encode()).hexdigest(),accent=value('Акцент'),h1=value('Заголовок'),intro=value('Описание'),message=re.search(r'с текстом «([^»]+)»',blocks[1])[1],checks_title=title(2),checks=checks,types_title=title(3),types=types,countries_title=title(4),countries=countries,hotels_title=title(5),hotels_contact=contact,faq_title=title(6),questions=questions,end_title=endtitle,end_text=endtext,checklist=checklist,hotel_examples=examples,hotel_good_label=(labels[0]if labels else'чем хорош').capitalize(),mode=mode,hero_image=photo,section_order=['types','countries','hotels','checks','faq','final'],approved_paragraphs=audit)
 # The introductory factual phrase precedes editorial instructions about buttons.
 intro=paragraphs(4)[0].split(' Кнопка')[0];p['countries_intro']=intro;audit.append(intro)
 p['hotels']={c['slug']:[dict(id=c['slug']+'-'+str(i+1),name=('Маршрут'if mode=='routes'else'Тур'if mode=='tours'else'Отель')+' '+str(i+1),place=c['name'],image=None,good=('например, '+examples[0])if examples else'Описание маршрута уточняется.',note=('например, '+examples[1])if len(examples)>1 else'',itinerary='Города и ночи уточняются.'if mode=='routes'else'Дни и города уточняются.'if mode=='tours'else'Курорт уточняется.')for i in range(1 if mode=='routes'else 3)]for c in countries}
 return p
def main(folder):
 path=ROOT/'tools/d1/data.json';d=json.loads(path.read_text());old={p['slug']:p for p in d['rest_pages']};photos={c['label']:c['image']for c in d['home_rest']['cards']};pages=[]
 for slug in FILES:
  text=(Path(folder)/('razdel-'+slug+'.md')).read_text();accent=re.search(r'^Акцент: (.+)$',text,re.M)[1];pages.append(parse(slug,text,old.get(slug),photos[accent]))
 d['rest_pages']=pages;d['rest_section_order']=['types','countries','hotels','checks','faq','final'];d['rest_country_links']=[c['slug']for c in d['countries']if c['published']]
 byname={p['accent']:p['slug']for p in pages}
 for card in d['home_rest']['cards']:
  if card['label']in byname:card['target']='otdyh/'+byname[card['label']]+'/index.html';card['slug']=byname[card['label']];card.pop('open_quiz',None)
 path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print('Imported',len(pages),'approved sections')
if __name__=='__main__':main(sys.argv[1]if len(sys.argv)>1 else ROOT)
