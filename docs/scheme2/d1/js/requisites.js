/* Empty URLs open a static, accessible dialog; populated URLs are ordinary PDF links. */
(() => {
 document.querySelectorAll('[data-agency-document]').forEach(button=>{
  button.disabled=false;
  button.addEventListener('click',()=>window.MangoUI.open(document.getElementById('agency-document-'+button.dataset.agencyDocument),button));
 });
})();
