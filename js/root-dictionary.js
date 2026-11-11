/* Definitions for the selected Quran root, using the dictionary's own normalization. */
(function (global) {
  'use strict';
  const core = typeof module === 'object' && module.exports
    ? require('../json/maqayis_tools/browser_core.js') : global.Maqayis;

  function findEntries(entries, root) {
    const key = core.normalize(root).replace(/\s+/g, '');
    if (!key) return [];
    const prepared = entries.length && entries[0].compactHeading !== undefined ? entries : core.prepare(entries);
    return prepared.filter(entry => entry.compactHeading === key || entry.expandedHeading.replace(/\s+/g, '') === key);
  }
  function definitionText(markdown) {
    const match = String(markdown).match(/^Source:[^\r\n]*\r?\n\s*\r?\n([\s\S]*)/m);
    if (!match || !match[1].trim()) throw new Error('Missing dictionary definition.');
    return match[1].trim();
  }
  function createLookup({loadIndex, loadText, onState}) {
    let indexRequest, version = 0;
    const definitions = new Map();
    function getIndex() {
      if (!indexRequest) indexRequest = Promise.resolve().then(loadIndex)
        .then(data => core.prepare(data.entries))
        .catch(error => {indexRequest = null; throw error;});
      return indexRequest;
    }
    async function select(root) {
      const request = ++version;
      const emit = state => {if (request === version) onState({root, ...state});};
      if (!root) {emit({status:'hidden', entries:[]}); return;}
      emit({status:'loading', entries:[]});
      try {
        const matches = findEntries(await getIndex(), root);
        const results = await Promise.all(matches.map(async entry => {
          if (!entry.available) return {...entry, text:''};
          if (!/^[a-zA-Z0-9_-]+$/.test(entry.id)) throw new Error('Invalid dictionary entry ID.');
          if (!definitions.has(entry.id)) {
            const promise = entry.fallback ? Promise.resolve(entry.fallback)
              : Promise.resolve().then(() => loadText(entry.id)).then(definitionText);
            definitions.set(entry.id, promise.catch(error => {definitions.delete(entry.id); throw error;}));
          }
          return {...entry, text:await definitions.get(entry.id)};
        }));
        emit({status: !results.length ? 'empty' : results.some(entry=>entry.text) ? 'ready' : 'unavailable', entries:results});
      } catch (error) {emit({status:'error', entries:[], error});}
    }
    return {select};
  }
  function setupDisclosure(content, toggle) {
    let expanded = false;
    function update() {
      content.setAttribute('data-expanded', String(expanded));
      toggle.setAttribute('aria-expanded', String(expanded));
      toggle.textContent = expanded ? 'Less…' : 'More…';
    }
    toggle.addEventListener('click', () => {expanded = !expanded; update();});
    return hasDefinition => {
      expanded = false;
      toggle.hidden = !hasDefinition;
      update();
    };
  }
  const api = {findEntries, definitionText, createLookup, setupDisclosure};
  if (typeof module === 'object' && module.exports) {module.exports = api; return;}

  async function resource(url, json = false) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);
    try {
      const response = await fetch(url, {cache:'default', signal:controller.signal});
      if (!response.ok) throw new Error(`Dictionary request failed: HTTP ${response.status}`);
      return await (json ? response.json() : response.text());
    } finally {clearTimeout(timeout);}
  }
  let lookup;
  function show(root) {
    if (!lookup) {
      const panel = document.getElementById('root-definition');
      const content = document.getElementById('root-definition-content');
      const resetDisclosure = setupDisclosure(content, document.getElementById('root-definition-more'));
      const status = document.getElementById('root-definition-status');
      const retry = document.getElementById('root-definition-retry');
      retry.addEventListener('click', () => lookup.select(document.getElementById('root-select').value));
      lookup = createLookup({
        loadIndex:()=>resource('json/maqayis-root-index.json', true),
        loadText:id=>resource(`json/maqayis/entries/${id}.md`),
        onState(state) {
          panel.hidden = state.status === 'hidden';
          panel.setAttribute('aria-busy', String(state.status === 'loading'));
          document.getElementById('root-definition-root').textContent = state.root;
          content.replaceChildren();
          resetDisclosure(state.status === 'ready');
          retry.hidden = state.status !== 'error';
          status.textContent = ({loading:'Loading root definition…',
            empty:'No matching headword was found in Maqayis al-Lugha.',
            unavailable:'This headword is indexed, but its definition has not been downloaded yet.',
            error:'Unable to load the definition. Check your connection and try again.'})[state.status] || '';
          for (const entry of state.entries) {
            const article = document.createElement('article');
            const link = document.createElement('a');
            link.href = `maqayis.html#${encodeURIComponent(entry.id)}`;
            link.textContent = entry.heading;
            link.lang = 'ar'; link.dir = 'rtl';
            const heading = document.createElement('h3');heading.appendChild(link);article.appendChild(heading);
            const text = document.createElement('div');text.className = 'root-definition-text';
            text.lang = 'ar';text.dir = 'rtl';
            for (const paragraph of entry.text.split(/\n\s*\n/).filter(Boolean)) {
              const p = document.createElement('p');p.textContent = paragraph;text.appendChild(p);
            }
            if (!entry.text) {
              const p = document.createElement('p');p.textContent = 'Definition not yet downloaded. Open the dictionary entry for its original source.';article.appendChild(p);
            } else article.appendChild(text);
            content.appendChild(article);
          }
        }
      });
    }
    return lookup.select(root);
  }
  global.RootDictionary = Object.freeze({...api, show});
})(typeof globalThis !== 'undefined' ? globalThis : this);
