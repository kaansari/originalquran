/* Keep tracing style independent of the selected font and Quran page. */
(() => {
  'use strict';
  const select = document.getElementById('writing-style');
  if (!select) return;
  let saved;
  try { saved = localStorage.getItem('writingFontStyle'); } catch {}
  select.value = saved === 'normal' ? 'normal' : 'italic';
  const apply = () => document.body.setAttribute('data-writing-style', select.value);
  apply();
  select.addEventListener('change', () => {
    apply();
    try { localStorage.setItem('writingFontStyle', select.value); } catch {}
  });
})();
