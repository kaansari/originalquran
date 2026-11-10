'use strict';
const assert = require('node:assert/strict');
const { normalize, prepare, search, letterFor } = require('./browser_core.js');
assert.equal(normalize('إِبْرَاهِيمُ'), 'ابراهيم');
assert.equal(normalize('هُدَىٰ'), 'هدي');
assert.equal(normalize('رَحْـمَةٌ'), 'رحمة');
assert.equal(letterFor('أَبَّ'), 'ا');
const entries = prepare([
  { id:'a', heading:'رَحَمَ', text:'الرَّحْمَةُ والرِّقَّةُ.' },
  { id:'b', heading:'كَتَبَ', text:'ذكر الرحمة في الكتاب.' },
  { id:'c', heading:'أَبَّ', text:'المرعى والقصد.' },
  { id:'d', heading:'عَلَمَ', text:'' },
]);
assert.deepEqual(search(entries, 'رحم', 'all', '').map(e=>e.id), ['a','b']);
assert.deepEqual(search(entries, 'رَحْم', 'headwords', '').map(e=>e.id), ['a']);
assert.deepEqual(search(entries, 'ر ح م', 'headwords', '').map(e=>e.id), ['a']);
assert.deepEqual(search(entries, 'ابب', 'headwords', '').map(e=>e.id), ['c']);
assert.deepEqual(search(entries, 'الرحمة', 'definitions', '').map(e=>e.id), ['a','b']);
assert.deepEqual(search(entries, '', 'all', 'ع').map(e=>e.id), ['d']);
assert.equal(search(entries, 'no-match', 'all', '').length, 0);
const multiword = prepare([{id:'section',heading:'بَابُ الطَّاءِ فِي الْمُضَاعَفِ وَالْمُطَابِقِ',text:'عنوان.'}]);
assert.deepEqual(search(multiword, 'باب الطاء', 'headwords', '').map(e=>e.id), ['section']);
console.log('Dictionary search: normalization, doubled roots, ranking, scopes, letter filters, and missing text passed.');
