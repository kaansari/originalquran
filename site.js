/* Shared site chrome and actual-work loading status. No page content is replaced. */
(function () {
  'use strict';
  function createLoadTracker(onChange, clock = globalThis) {
    let pending = 0, visible = false, error = null, timer;
    const snapshot = () => ({pending, visible, error});
    const emit = () => onChange(snapshot());
    function fail(reason) {
      error = reason?.message || String(reason || 'Unable to load this page.');
      visible = true;
      emit();
    }
    function begin() {
      if (pending === 0) {
        error = null;
        visible = false;
        timer = clock.setTimeout(() => { visible = true; emit(); }, 250);
      }
      pending++;
      emit();
      let finished = false;
      return reason => {
        if (finished) return;
        finished = true;
        pending--;
        if (reason) fail(reason);
        if (!pending) {
          clock.clearTimeout(timer);
          visible = Boolean(error);
        }
        emit();
      };
    }
    return {begin, fail, snapshot};
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {createLoadTracker};
    return;
  }

  let status, statusText, retry;
  const tracker = createLoadTracker(renderStatus);
  function renderStatus(state) {
    if (!status) return;
    status.hidden = !state.visible;
    status.classList.toggle('site-status-error', Boolean(state.error));
    status.setAttribute('aria-busy', String(state.pending > 0 && !state.error));
    statusText.textContent = state.error
      ? 'Unable to load this page. Check your connection and try again.'
      : 'Loading page content…';
    retry.hidden = !state.error;
  }
  function preferredTheme() {
    try {
      const saved = localStorage.getItem('theme');
      if (saved === 'dark' || saved === 'light') return saved;
    } catch {}
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function applyTheme(theme, save = false) {
    const dark = theme === 'dark';
    document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
    document.body.classList.toggle('dark-theme', dark);
    // The dictionary's existing scoped colors use this class.
    if (document.body.classList.contains('site-dictionary')) document.body.classList.toggle('dark', dark);
    const button = document.getElementById('site-theme-button');
    button?.setAttribute('aria-pressed', String(dark));
    button?.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
    if (button) button.textContent = dark ? 'Light mode' : 'Dark mode';
    if (save) try {localStorage.setItem('theme', theme);} catch {}
  }
  window.SiteUI = Object.freeze({
    beginLoading: () => tracker.begin(),
    reportError: error => tracker.fail(error),
    preferredTheme,
    applyTheme
  });
  function init() {
    status = document.createElement('div');
    status.id = 'site-status';
    status.hidden = true;
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    statusText = document.createElement('span');
    retry = document.createElement('button');
    retry.type = 'button';
    retry.textContent = 'Try again';
    retry.hidden = true;
    retry.addEventListener('click', () => window.location.reload());
    status.append(statusText, retry);
    document.body.appendChild(status);
    renderStatus(tracker.snapshot());

    const nav = document.querySelector('.site-toplinks');
    const filename = location.pathname.split('/').pop() || 'index.html';
    nav?.querySelectorAll('a').forEach(link => {
      if (link.getAttribute('href') === (filename === 'page.html' ? 'index.html' : filename)) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    if (nav) {
      const home = nav.querySelectorAll('a')[0]?.getAttribute('href') || 'index.html';
      const siteBase = home.slice(0, home.lastIndexOf('/') + 1);
      const more = document.createElement('details');
      more.className = 'site-more';
      const summary = document.createElement('summary');
      summary.textContent = 'More';
      const links = document.createElement('div');
      links.className = 'site-more-links';
      for (const [href, text] of [
        ['simple.html','Simple Quran'], ['warsh.html','Western Quran'],
        ['quran.html','Full Chapters'], ['random.html','Random verse'],
        ['https://github.com/kaansari/originalquran', 'GitHub repository']
      ]) {
        const link = document.createElement('a');
        link.href = href.startsWith('https://') ? href : siteBase + href; link.textContent = text;
        if (href === filename) link.setAttribute('aria-current','page');
        links.appendChild(link);
      }
      more.append(summary, links);
      const theme = document.createElement('button');
      theme.id = 'site-theme-button'; theme.type = 'button'; theme.className = 'site-quiet';
      theme.addEventListener('click', () => applyTheme(document.body.classList.contains('dark-theme') ? 'light' : 'dark', true));
      nav.append(more, theme);
    }
    applyTheme(preferredTheme());
    window.addEventListener('storage', event => {
      if (event.key === 'theme' || event.key === null) applyTheme(preferredTheme());
    });
    // Preserve existing selectors while giving every page the same accessible names.
    for (const [id, label] of Object.entries({
      'sura-select':'Surah', 'verse-select':'Verse', 'font-select':'Reading font',
      'prev-page':'Previous page', 'next-page':'Next page',
      'translation-toggle':'Show translation'
    })) document.getElementById(id)?.setAttribute('aria-label', label);
    const closeMenus = () => {
      document.querySelectorAll('.site-more[open]').forEach(menu => menu.open = false);
    };
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') closeMenus();
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.site-more')) closeMenus();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
