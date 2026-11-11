const {test}=require('node:test');
const assert=require('node:assert/strict');
const {summarize,formatCount}=require('../src/js/root-statistics.js');
const data={RootCount:999,Word:{
 'كتب':{WordCount:999,VerseCount:999,Verses:[{ID:'2:2:1'},{ID:'2:2:2'},{ID:'2:3:1'},{ID:'2:3:1'}]},
 'كتاب':{Verses:[{ID:'2:2:3'},{ID:'3:2:1'}]}
}};
test('occurrences are unique tokens and verse totals are distinct across all root words',()=>{
 assert.deepEqual(summarize(data,'كتب'),{root:{occurrences:5,verses:3},word:{occurrences:3,verses:2}});
});
test('changing the word preserves root totals and updates only word counts',()=>{
 assert.deepEqual(summarize(data,'كتاب'),{root:{occurrences:5,verses:3},word:{occurrences:2,verses:2}});
});
test('absent root or word produces safe zero counts',()=>{
 assert.deepEqual(summarize(null,''),{root:{occurrences:0,verses:0},word:{occurrences:0,verses:0}});
 assert.deepEqual(summarize(data,'missing').word,{occurrences:0,verses:0});
});
test('labels distinguish singular occurrences and verses',()=>{
 assert.equal(formatCount({occurrences:1,verses:1}),'1 occurrence in 1 verse');
 assert.equal(formatCount({occurrences:30,verses:25}),'30 occurrences in 25 verses');
});

test('selector changes render root and word counts beneath the selectors',()=>{
 const fs=require('node:fs'),vm=require('node:vm');
 const html=fs.readFileSync('src/root.html','utf8');
 assert(html.indexOf('id="selector-statistics"')>html.indexOf('id="word-select"'));
 assert(html.indexOf('id="selector-statistics"')<html.indexOf('id="root-definition"'));
 const nodes=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],{value:'',textContent:'',hidden:true,events:{},
   addEventListener(type,fn){this.events[type]=fn;},querySelectorAll:()=>[]} ]));
 const context=vm.createContext({window:{},document:{getElementById:id=>nodes.get(id),addEventListener(){}},
  localStorage:{getItem:()=>null,setItem(){}},QuranUtils:{loadJSON:()=>new Promise(()=>{})},console});
 vm.runInContext(fs.readFileSync('src/js/root-statistics.js','utf8'),context);
 context.window.RootStatistics=context.RootStatistics;
 const script=fs.readFileSync('src/js/root.js','utf8');
 vm.runInContext(script,context);
 vm.runInContext(`rootWordsData={"root":${JSON.stringify(data)}};buildVerse=()=>'';bindSelectListenersOnce();`,context);
 nodes.get('root-select').value='root';nodes.get('word-select').value='كتب';
 nodes.get('word-select').events.change();
 assert.equal(nodes.get('root-statistics-count').textContent,'5 occurrences in 3 verses');
 assert.equal(nodes.get('word-statistics-count').textContent,'3 occurrences in 2 verses');
 assert.equal(nodes.get('selector-statistics').hidden,false);
 nodes.get('word-select').value='كتاب';nodes.get('word-select').events.change();
 assert.equal(nodes.get('word-statistics-count').textContent,'2 occurrences in 2 verses');
});
