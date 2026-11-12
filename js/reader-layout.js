/* Optional printed-line adapter. A reader selects its files through HTML metadata. */
((root) => {
  function renderPage(document, layout, page, suras, verseURL, highlightRef = null, englishWords = {}) {
    const lines = layout.pages?.[page];
    if (!Array.isArray(lines) || !lines.length) throw new Error(`Missing printed layout for page ${page}`);
    const fragment = document.createElement('div');
    fragment.className = 'mushaf-lines';
    for (const line of lines) {
      const element = document.createElement('div');
      element.className = `mushaf-line arabic${line.centered ? ' mushaf-centered' : ''}`;
      element.dataset.line = line.number;
      element.style.gridRow = String(line.number);
      element.setAttribute('dir', 'rtl');
      if (line.type === 'surah_name') {
        element.className += ' mushaf-surah';
        element.textContent = suras[line.sura].name;
      } else if (line.type === 'basmallah') {
        element.textContent = layout.basmallah;
      } else if (line.type === 'ayah') {
        for (const [index, token] of line.tokens.entries()) {
          if (index) element.appendChild(document.createTextNode(' '));
          if (token.parts) {
            const group = document.createElement('span');
            group.className = 'mushaf-token';
            for (const [partIndex, part] of token.parts.entries()) {
              if (partIndex) group.appendChild(document.createTextNode(' '));
              const word = document.createElement('span');
              word.className = `word${token.ref === highlightRef ? ' highlighted' : ''}`;
              word.textContent = part.text;
              word.dataset.wordId = part.wordId;
              word.dataset.en = englishWords[part.wordId] || '';
              word.dataset.verse = token.ref;
              group.appendChild(word);
            }
            element.appendChild(group);
            continue;
          }
          const word = document.createElement(token.wordId ? 'span' : 'a');
          word.textContent = token.text;
          word.dataset.verse = token.ref;
          if (token.wordId) {
            word.className = 'word';
            word.dataset.wordId = token.wordId;
            word.dataset.en = englishWords[token.wordId] || '';
          } else {
            word.className = 'verse-link';
            word.href = verseURL(...token.ref.split(':').map(Number));
            word.target = '_blank';
            word.rel = 'noopener noreferrer';
            word.setAttribute('aria-label', `Verse ${token.ref}`);
          }
          if (token.ref === highlightRef) word.className += ' highlighted';
          element.appendChild(word);
        }
      } else {
        throw new Error(`Unknown printed line type: ${line.type}`);
      }
      fragment.appendChild(element);
    }
    return fragment;
  }

  // Fit whole source lines after the actual font has loaded, including on resize.
  // Never trim text, insert invented breaks or transform the reading surface.
  function fitLines(container) {
    if (container.closest?.('[data-fit-page="true"]')) {
      // A full-page fit scales every printed line together, preserving 15 rows.
      for (const line of container.querySelectorAll('.mushaf-line')) {
        if (line.style.fontSize) line.style.fontSize = '';
      }
      return;
    }
    for (const line of container.querySelectorAll('.mushaf-line')) {
      if (!line.clientWidth) continue;
      line.style.fontSize = '';
      let size = parseFloat(getComputedStyle(line).fontSize);
      const contentWidth = () => {
        const children = Array.from(line.children || []);
        const gap = parseFloat(getComputedStyle(line).columnGap) || 0;
        // Measure the actual flex items too: RTL overflow can extend to the
        // left without increasing the scrollable width reported by WebKit.
        const wordsWidth = children.reduce((width, child) => width + child.getBoundingClientRect().width, 0)
          + Math.max(0, children.length - 1) * gap;
        return Math.max(line.scrollWidth, wordsWidth);
      };
      for (let attempt = 0; attempt < 8 && contentWidth() > line.clientWidth + 1; attempt++) {
        size *= line.clientWidth / contentWidth();
        line.style.fontSize = `${Math.max(1, size - 0.1)}px`;
      }
    }
  }

  function watchSize(container, window, Observer) {
    let pending = false, previousWidth;
    const schedule = () => {
      if (pending) return;
      pending = true;
      window.requestAnimationFrame(() => {
        pending = false;
        fitLines(container);
      });
    };
    window.addEventListener('resize', schedule);
    window.addEventListener('orientationchange', schedule);
    window.addEventListener('pageshow', schedule);
    window.visualViewport?.addEventListener('resize', schedule);
    if (Observer) {
      new Observer(entries => {
        const width = entries[0]?.contentRect.width;
        if (!width || width === previousWidth) return;
        previousWidth = width;
        schedule();
      }).observe(container);
    }
  }

  const api = Object.freeze({renderPage, fitLines, watchSize});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ReaderLayout = api;
})(globalThis);
