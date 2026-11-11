const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function setup(){
 const html=fs.readFileSync('src/root.html','utf8');
 assert.match(html,/<script src="js\/root.js\?/);
 assert(!/<script>/.test(html));
 const node={addEventListener(){}};
 const context=vm.createContext({document:{getElementById:()=>node,addEventListener(){}},window:{},
  localStorage:{getItem:()=>null},QuranUtils:{loadJSON:()=>new Promise(()=>{})},console});
 vm.runInContext(fs.readFileSync('src/js/root.js','utf8'),context);
 vm.runInContext(`
  suraData={1:{name:'One',start:1,end:2,nAyah:2},2:{name:'Two',start:3,end:3,nAyah:1}};
  combinedQuranData={1:{arabic:'كَتَبَ الرَّحْمَةَ',en:'He wrote mercy'},2:{arabic:'عَلِمَ',en:'He knew'},3:{arabic:'كِتَاب',en:'A book'}};
  rootWordsData={'كتب':{Word:{'كتب':{Verses:[{Key:'1',ID:'1:1:1'}]},'كتاب':{Verses:[{Key:'3',ID:'2:1:1'}]}}}};
  buildSuraRangesForSearch();buildVerseRefIndexForSearch();
 `,context);
 return expr=>JSON.parse(JSON.stringify(vm.runInContext(expr,context)));
}
test('external root script preserves reference search and invalid-reference handling',()=>{
 const run=setup();
 assert.deepEqual(run("searchRefToVerseObjects('2:1')"),[{Key:'0',ID:'2:1:1'}]);
 assert.deepEqual(run("searchRefToVerseObjects('2:2')"),[]);
});
test('external root script preserves Arabic, English, root and word searches',()=>{
 const run=setup();
 assert.equal(run("searchArabicToVerseObjects('كتب')")[0].ID,'1:1:1');
 assert.equal(run("searchEnglishToVerseObjects('BOOK')")[0].ID,'2:1:1');
 assert.equal(run("searchRootWordsRootToVerseObjects('كتب')").length,2);
 assert.equal(run("searchRootWordsWordToVerseObjects('كِتاب')")[0].ID,'2:1:1');
});
