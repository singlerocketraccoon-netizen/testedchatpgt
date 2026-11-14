"""Import approved static source using only Python's HTML parser."""
from pathlib import Path
from html.parser import HTMLParser
import json,hashlib
class Node:
 def __init__(self,tag='',attrs=()):self.tag=tag;self.a=dict(attrs);self.children=[]
 def text(self):return ''.join(c.text()if isinstance(c,Node)else c for c in self.children).strip()
 def all(self,tag=None,cls=None):
  out=[]
  for c in self.children:
   if isinstance(c,Node):
    if(tag is None or c.tag==tag)and(cls is None or cls in c.a.get('class','').split()):out.append(c)
    out+=c.all(tag,cls)
  return out
 def one(self,tag=None,cls=None):return self.all(tag,cls)[0]
class Parser(HTMLParser):
 def __init__(self,s):super().__init__();self.root=Node();self.stack=[self.root];self.feed(s)
 def handle_starttag(self,t,a):
  n=Node(t,a);self.stack[-1].children.append(n)
  if t not in['img','br','hr','meta','link','input','source']:self.stack.append(n)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:self.stack=self.stack[:i];break
 def handle_data(self,s):self.stack[-1].children.append(s)
def summary_blocks(node):
 blocks=[]
 for n in node.children:
  if not isinstance(n,Node):continue
  classes=n.a.get('class','').split()
  if 'draft'in classes or 'photo'in classes:continue
  if n.tag=='h4':blocks.append({'type':'heading','text':n.text()})
  elif 'chips'in classes:blocks.append({'type':'chips','items':[c.text()for c in n.children if isinstance(c,Node)and c.tag in['span','button']]})
  elif n.tag in['ul','ol']or'flow'in classes:blocks.append({'type':'list','ordered':'flow'in classes,'items':[x.text()for x in n.all('li'if n.tag in['ul','ol']else'span')]})
  elif 'small'in classes:blocks.append({'type':'caption','text':n.text()})
  elif n.a.get('data-goto')=='Услуги':blocks.append({'type':'services'})
  elif 'row'in classes and n.all('button'):blocks.append({'type':'channels'})
  else:blocks+=summary_blocks(n)
 return blocks
def parse(source):
 r=Parser(source.read_text()).root;hero=r.one(cls='hero');route=r.one(cls='route');data={'source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'h1':hero.one('h1').text(),'intro':hero.one('p','lead').text(),'facts':[n.text().lstrip('✓').strip()for n in hero.all(cls='fact')],'stages':[]}
 for i,stage in enumerate(r.all('section','stage')):
  steps=[]
  for item in stage.all('article','step'):
   text=item.one(cls='txt');aside=item.one('aside');steps.append({'id':item.a['id'],'title':text.one('h3').text(),'paragraphs':[p.text()for p in text.all('p')],'summary':[{'title':n.text()}for n in aside.all('h4')],'chips':[n.text()for parent in aside.all(cls='chips')for n in parent.children if isinstance(n,Node)and n.tag in['span','button']],'checks':[n.text()for n in aside.all('li')],'flow':[n.text()for parent in aside.all(cls='flow')for n in parent.all('span')],'caption':next((n.text()for n in aside.all('span','small')),''),'summaryBlocks':summary_blocks(aside),'needsApproval':item.a['id']=='contract'})
  button=route.all('button')[i];data['stages'].append({'id':stage.a['id'],'title':stage.one('h2').text(),'caption':button.all('span')[-1].text(),'steps':steps})
 cost=r.one('section','cost');data['costTitle']=cost.one('h2').text();data['costText']=cost.one('p').text();data['finalTitle']=next(n for n in r.all('section')if n.a.get('id')=='contact').one('h2').text();return data
if __name__=='__main__':
 root=Path(__file__).resolve().parents[2];p=root/'tools/d1/data.json';d=json.loads(p.read_text());d['work13']=parse(root/'Mango_Travel_Kak_my_rabotaem_skhema.html');previous=d.get('layout13',{});d['layout13']={'servicePhotos':{'packages':'hero-resort.webp','custom':'@rest-road.webp','tours':'@rest-excursion-city.webp','cruises':'@rest-cruise.webp'},'photoPool':['hero-resort.webp','hero-sand.webp','mood-walk.webp','@summer-hotel.webp','hero-lake.webp','@maldives.webp','@vietnam-free.webp','@rest-road.webp'],'companyLine':d['contacts']['location']};d['layout13'].update(previous);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
