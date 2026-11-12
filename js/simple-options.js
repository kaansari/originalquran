/* Qahiri's dotless feature changes glyphs only, never the indexed word text. */
(() => {
  const toggle = document.getElementById('qahiri-dots-toggle');
  const control = document.getElementById('qahiri-dot-control');
  const font = document.getElementById('font-select');
  if (!toggle || !control || !font) return;
  const key = 'qahiriDots_simple.html';
  let saved;
  try { saved = localStorage.getItem(key); } catch {}
  toggle.checked = saved !== 'on';
  const apply = () => {
    document.body.setAttribute('data-qahiri-dots', toggle.checked ? 'off' : 'on');
    window.MobileReader?.fit();
  };
  const updateVisibility = () => { control.hidden = font.value !== 'Qahiri'; };
  toggle.addEventListener('change', () => {
    apply();
    try { localStorage.setItem(key, toggle.checked ? 'off' : 'on'); } catch {}
  });
  font.addEventListener('change', updateVisibility);
  window.addEventListener('quran:ready', updateVisibility);
  apply();
  updateVisibility();
})();
