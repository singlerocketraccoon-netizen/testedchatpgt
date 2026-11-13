/* This notice deliberately uses ES5 syntax and no modern CSS. */
(function () {
 if (!document.documentMode) return;
 var box=document.createElement('div');
 box.setAttribute('role','alert');
 box.style.cssText='position:fixed;left:0;right:0;top:0;bottom:0;z-index:99999;padding:40px;background:#FAF7F1;color:#332D28;font:18px/1.6 Arial,sans-serif;overflow:auto;';
 var text=document.createElement('p');text.appendChild(document.createTextNode('Internet Explorer больше не поддерживается. Откройте сайт в Microsoft Edge, Яндекс Браузере или Chrome'));box.appendChild(text);
 var items=[['Позвонить: +7 (8512) 29-95-47','tel:+78512299547'],['MAX','tel:+78512299547'],['Telegram','tel:+78512299547']];
 for(var i=0;i<items.length;i++){var line=document.createElement('p');var a=document.createElement('a');a.href=items[i][1];a.setAttribute('data-goal','legacy_contact_'+i);a.style.cssText='display:inline-block;padding:12px 0;color:#A9532B;';a.appendChild(document.createTextNode(items[i][0]));line.appendChild(a);box.appendChild(line);}
 document.body.appendChild(box);
}());
