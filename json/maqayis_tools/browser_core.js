(function (root) {
  'use strict';
  const collator = new Intl.Collator('ar');
  function normalize(value) {
    return String(value || '').normalize('NFKC').toLowerCase()
      .replace(/[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed\u0640]/g, '')
      .replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/\s+/g, ' ').trim();
  }
  function letterFor(heading) { return normalize(heading).charAt(0); }
  function prepare(entries) {
    return entries.map(entry => ({...entry,
      normalizedHeading: normalize(entry.heading),
      compactHeading: normalize(entry.heading).replace(/\s+/g, ''),
      expandedHeading: normalize(entry.heading.replace(/(.)\u0651/gu, '$1$1')),
      normalizedText: normalize(entry.text),
      letter: letterFor(entry.heading),
    })).sort((a,b) => collator.compare(a.heading,b.heading));
  }
  function search(entries, query, scope, letter) {
    const normalized = normalize(query);
    const compact = normalized.replace(/\s+/g, '');
    const tokens = normalized.split(' ').filter(Boolean);
    const matches = [];
    for (const entry of entries) {
      if (letter && entry.letter !== letter) continue;
      const headMatch = !normalized || entry.normalizedHeading.includes(normalized) || entry.compactHeading.includes(compact) || entry.expandedHeading.replace(/\s+/g, '').includes(compact);
      const bodyMatch = !!normalized && tokens.every(token => entry.normalizedText.includes(token));
      if (normalized && !(scope === 'headwords' ? headMatch : scope === 'definitions' ? bodyMatch : headMatch || bodyMatch)) continue;
      let rank = 4;
      if (!normalized) rank = 0;
      else if (scope !== 'definitions') {
        if (entry.compactHeading === compact || entry.expandedHeading.replace(/\s+/g, '') === compact) rank = 0;
        else if (entry.compactHeading.startsWith(compact) || entry.expandedHeading.replace(/\s+/g, '').startsWith(compact)) rank = 1;
        else if (headMatch) rank = 2;
      }
      matches.push({entry, rank});
    }
    return matches.sort((a,b) => a.rank-b.rank || collator.compare(a.entry.heading,b.entry.heading)).map(item => item.entry);
  }
  const api = {normalize, prepare, search, letterFor};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.Maqayis = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
