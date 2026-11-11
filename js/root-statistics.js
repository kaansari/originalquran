/* Count actual word positions and distinct Quran verses, not morphology segments. */
(function (global) {
  'use strict';
  const cache = new WeakMap();
  const empty = () => ({occurrences:0, verses:0});
  function summarize(rootData, selectedWord) {
    if (!rootData || typeof rootData !== 'object') return {root:empty(), word:empty()};
    if (!cache.has(rootData)) {
      const rootTokens = new Set(), rootVerses = new Set(), words = new Map();
      for (const [word, details] of Object.entries(rootData.Word || {})) {
        const tokens = new Set(), verses = new Set();
        for (const entry of details.Verses || []) {
          const id = String(entry.ID || '');
          if (!/^\d+:\d+:\d+$/.test(id)) continue;
          const verse = id.split(':').slice(0,2).join(':');
          tokens.add(id); verses.add(verse);
          rootTokens.add(id); rootVerses.add(verse);
        }
        words.set(word, {occurrences:tokens.size, verses:verses.size});
      }
      cache.set(rootData, {root:{occurrences:rootTokens.size, verses:rootVerses.size}, words});
    }
    const counts = cache.get(rootData);
    return {root:counts.root, word:counts.words.get(selectedWord) || empty()};
  }
  function formatCount({occurrences, verses}) {
    return `${occurrences.toLocaleString('en')} occurrence${occurrences === 1 ? '' : 's'} in ${verses.toLocaleString('en')} verse${verses === 1 ? '' : 's'}`;
  }
  function show(rootData, selectedWord) {
    const counts = summarize(rootData, selectedWord);
    document.getElementById('root-statistics-count').textContent = formatCount(counts.root);
    document.getElementById('word-statistics-count').textContent = formatCount(counts.word);
    document.getElementById('selector-statistics').hidden = !rootData;
  }
  const api = {summarize, formatCount, show};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else global.RootStatistics = Object.freeze(api);
})(typeof globalThis !== 'undefined' ? globalThis : this);
