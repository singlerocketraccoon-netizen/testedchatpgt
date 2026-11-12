(() => {
 'use strict';
 const links=[...document.querySelectorAll('[data-work-anchor]')];
 if(!links.length)return;
 function update(){let active=links[0];links.forEach(a=>{const el=document.querySelector(a.getAttribute('href'));if(el&&el.getBoundingClientRect().top<=180)active=a;});links.forEach(a=>a===active?a.setAttribute('aria-current','location'):a.removeAttribute('aria-current'));}
 addEventListener('scroll',update,{passive:true});update();
})();
