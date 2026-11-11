// Keep an unfinished or unavailable edition explicit; never silently show a different script.
(() => {
  const notice = document.getElementById('indian-status');
  window.addEventListener('quran:ready', () => { notice.hidden = true; });
  window.addEventListener('quran:error', () => {
    notice.hidden = false;
    notice.textContent = 'Indian Quran could not load. Check your connection and try again.';
  });
})();
