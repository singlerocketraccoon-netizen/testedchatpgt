"""Render country offer visibility fixtures without changing JSON or published pages."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def check():
 spec=importlib.util.spec_from_file_location('d1_fixture_build',ROOT/'tools/d1/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
 import stage4,country,stage6
 ctx=b.__dict__;stage4.configure(ctx);country.configure(ctx);stage6.configure(ctx)
 c=next(x for x in b.DATA['countries']if x['slug']=='egipet');emit=ctx['emit'];active=ctx['active_offers'];offers=stage6.D['offers'];seen=[];ctx['emit']=lambda *a,**kw:seen.append((a,kw));result=[]
 try:
  for enabled,empty in [(True,False),(False,False),(True,True)]:
   c['showOffers']=enabled;stage6.D['offers']=[]if empty else offers;country.country(c);html=seen[-1][0][5];has='id="offers"'in html;link='href="#offers"'in html;assert has==link==(enabled and not empty),(enabled,empty,has,link);assert 'id="price-strip"'in html;result.append(dict(showOffers=enabled,empty=empty,block=has,nav=link,price_strip=True))
 finally:ctx['emit']=emit;ctx['active_offers']=active;stage6.D['offers']=offers
 return result
if __name__=='__main__':print(check())
