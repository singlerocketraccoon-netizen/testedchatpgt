/* This comparison stays on the first cover; controls select its four original images. */
(() => {
  'use strict';
  const images = [
    ['../../assets/img/hero-sand.webp', 'Море и песчаный берег', 1600, 1064],
    ['../../assets/img/hero-resort.webp', 'Курорт и бассейн', 1600, 1600],
    ['../../assets/img/mood-family.webp', 'Семья на морском берегу', 900, 600],
    ['../../assets/img/hero-lake.webp', 'Озеро в окружении гор', 1600, 1067]
  ];
  document.querySelectorAll('[data-accent-preview]').forEach(cover => {
    let index = 0;
    const image = cover.querySelector('.hero-slide > img');
    const count = cover.querySelector('[data-hero-count]');
    const move = delta => {
      index = (index + delta + images.length) % images.length;
      image.src = images[index][0]; image.alt = images[index][1];
      image.width = images[index][2]; image.height = images[index][3];
      if (count) count.textContent = index + 1;
    };
    cover.querySelector('[data-preview-prev]')?.addEventListener('click', () => move(-1));
    cover.querySelector('[data-preview-next]')?.addEventListener('click', () => move(1));
    const pause = cover.querySelector('[data-preview-pause]');
    if (pause) { pause.disabled = true; pause.setAttribute('aria-label', 'Сравнение начертаний: автосмена выключена'); }
  });
  document.addEventListener('click', event => {
    const link = event.target.closest('[data-messenger]');
    if (!link) return;
    event.preventDefault(); window.location.href = 'index.html#contact';
  });
})();
