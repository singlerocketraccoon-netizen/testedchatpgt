"""Read approved copy without editorial normalization; Python standard library."""
from pathlib import Path
import ast,hashlib,re
ROOT=Path(__file__).resolve().parents[2]

def approved():
 slider=(ROOT/'glavnyj-slajder.md').read_text();work=(ROOT/'kak-my-rabotaem.md').read_text();scheme=(ROOT/'mango-structure-11-11.html').read_text()
 slides=[]
 for number,body in re.findall(r'^# Слайд (\d+)\s*\n(.*?)(?=^# |\Z)',slider,re.M|re.S):
  fields={k:v.strip()for k,v in re.findall(r'^(Акцент|Заголовок|Описание|Кнопка|Фото): (.+)$',body,re.M)}
  slides.append({'id':'slide-'+number,'accent':fields['Акцент'],'title':fields['Заголовок'],'description':fields['Описание'],'button':fields['Кнопка'],'photoBrief':fields['Фото']})
 intro=work.split('### ',1)[0];intro=[p.strip()for p in intro.split('\n\n')if p.strip()and not p.startswith('#')and not p.startswith('Текст утверждён')]
 parts=[]
 for anchor,(title,body)in zip(['plans','choice','hotel','prepare','plans-on-trip','support','experience','cost'],re.findall(r'^### ([^\n]+)\n(.*?)(?=^### |\Z)',work,re.M|re.S)):
  parts.append({'id':anchor,'title':title.strip(),'paragraphs':[p.strip()for p in body.strip().split('\n\n')if p.strip()]})
 titles=ast.literal_eval(re.search(r'const faqTitles=(\[.*?\]);',scheme,re.S)[1]);answers=ast.literal_eval(re.search(r'const faqContent=(\[.*?\]);',scheme,re.S)[1])
 assert len(slides)==4 and len(intro)==2 and len(parts)==8 and len(titles)==len(answers)==6,'Approved source structure is incomplete'
 sources={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()for name in['glavnyj-slajder.md','kak-my-rabotaem.md','mango-structure-11-11.html']}
 return {'slides':slides,'work':{'intro':intro,'sections':parts,'finalTitle':'Расскажите, каким Вы представляете свой отдых.'},'faq':list(map(list,zip(titles,answers))),'sources':sources}
