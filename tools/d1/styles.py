"""Canonical styles and local font preload for every generated page."""
import re
def finish(ctx,path):
 p=ctx['SITE']/path;h=p.read_text();U=ctx['url']
 h=re.sub(r'<link\b(?=[^>]*rel="stylesheet")[^>]*>','',h)
 files=['tokens','fonts','base','layout','components','header']
 if path=='index.html':files+=['home','country','offers']
 elif path.startswith('napravleniya/'):files+=['country','offers']
 elif path.startswith('otdyh/'):files+=['rest']
 elif path.startswith('predlozheniya/'):files+=['offers']
 elif path=='styleguide.html':files+=['brand-guide']
 else:files+=['home'] # Shared people, reviews and process components.
 files+=['grids','refinements','revision13']
 styles=''.join('<link rel="stylesheet" href="'+U(path,'css/'+name+'.css')+'">'for name in files)
 fonts=['../../assets/fonts/manrope-2.woff2','../../assets/fonts/manrope-6.woff2','../../assets/fonts/cormorant-garamond-2.woff2','../../assets/fonts/cormorant-garamond-5.woff2']
 preload=''.join('<link rel="preload" href="'+U(path,f)+'" as="font" type="font/woff2" crossorigin>'for f in fonts)
 h=h.replace('</head>','<script defer src="'+U(path,'js/revision13.js')+'"></script>'+preload+styles+'<script defer src="'+U(path,'js/legacy.js')+'"></script><script defer src="'+U(path,'js/layout.js')+'"></script></head>')
 if path.startswith('otdyh/')and'js/rest.js'not in h:h=h.replace('</head>','<script defer src="'+U(path,'js/rest.js')+'"></script></head>')
 p.write_text(h)
