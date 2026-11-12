/* Keep tracing style independent of the selected font and Quran page. */
(() => {
  'use strict';
  const families = {
    'Amiri Quran': 'hafs, serif',
    'System Arabic': '"Geeza Pro", "Traditional Arabic", Tahoma, Arial, sans-serif',
    'Raqq': 'Raqq, serif',
    'Amiri': 'Amiri, serif',
    'Noto Naskh Arabic': '"Noto Naskh Arabic", "Geeza Pro", serif',
    'Noto Sans Arabic': '"Noto Sans Arabic", Tahoma, sans-serif'
  };
  const fontSelect = document.getElementById('font-select');
  if (fontSelect) {
    let savedFont;
    try { savedFont = localStorage.getItem('selectedFont_writing.html'); } catch {}
    fontSelect.value = Object.hasOwn(families, savedFont) ? savedFont : 'Amiri Quran';
    const applyFont = () => {
      const name = Object.hasOwn(families, fontSelect.value) ? fontSelect.value : 'Amiri Quran';
      document.body.setAttribute('data-writing-font', name);
      document.body.style.setProperty('--writing-font-family', families[name]);
    };
    applyFont();
    // The shared reader continues to save the font selection.
    fontSelect.addEventListener('change', applyFont);
  }
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
