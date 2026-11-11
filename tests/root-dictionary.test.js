const {test} = require('node:test');
const assert = require('node:assert/strict');
const {findEntries, definitionText, createLookup} = require('../src/js/root-dictionary.js');
const entries=[
  {id:'rahm',heading:'رَحْمٌ',available:true},
  {id:'rahman',heading:'رَحْمَان',available:true},
  {id:'abb',heading:'أَبَّ',available:true},
  {id:'missing',heading:'كَتَبَ',available:false}
];
test('exact root matching ignores vowels and tatweel without matching longer words',()=>{
  assert.deepEqual(findEntries(entries,'ر ح م').map(e=>e.id),['rahm']);
  assert.deepEqual(findEntries(entries,'رَحْـم').map(e=>e.id),['rahm']);
  assert.deepEqual(findEntries(entries,'ابب').map(e=>e.id),['abb']);
  assert.deepEqual(findEntries(entries,'ز ز ز'),[]);
});
test('Markdown source metadata is excluded and definition paragraphs preserved',()=>{
  assert.equal(definitionText('# رَحْمٌ\n\nDictionary: Ibn Faris\n\nSource: https://example.com/\n\nFirst paragraph.\n\nSecond paragraph.'),'First paragraph.\n\nSecond paragraph.');
  assert.throws(()=>definitionText('# Incomplete'),/definition/i);
});
test('index and definitions are reused across root selections',async()=>{
  let indexes=0,texts=0;const states=[];
  const lookup=createLookup({loadIndex:async()=>{indexes++;return {entries};},
    loadText:async()=>{texts++;return '# Heading\n\nSource: https://example.com\n\nDefinition';},
    onState:s=>states.push(s)});
  await lookup.select('رحم');await lookup.select('رحم');
  assert.equal(indexes,1);assert.equal(texts,1);
  assert.equal(states.at(-1).status,'ready');
  assert.equal(states.at(-1).entries[0].text,'Definition');
  await lookup.select('كتب');assert.equal(states.at(-1).status,'unavailable');
  await lookup.select('ززز');assert.equal(states.at(-1).status,'empty');
});
test('a slow previous selection cannot overwrite a newer selection',async()=>{
  let resolve;const states=[];
  const lookup=createLookup({loadIndex:async()=>({entries}),onState:s=>states.push(s),
    loadText:()=>new Promise(done=>resolve=done)});
  const pending=lookup.select('رحم');
  await new Promise(setImmediate);
  await lookup.select('ززز');
  resolve('Source: https://example.com\n\nDefinition');await pending;
  assert.equal(states.at(-1).root,'ززز');assert.equal(states.at(-1).status,'empty');
});
test('failed requests can be retried and clear the error state',async()=>{
  let attempts=0;const states=[];
  const lookup=createLookup({loadIndex:async()=>({entries}),onState:s=>states.push(s),
    loadText:async()=>{if(++attempts===1)throw new Error('Offline');return 'Source: https://example.com\n\nDefinition';}});
  await lookup.select('رحم');assert.equal(states.at(-1).status,'error');
  await lookup.select('رحم');assert.equal(states.at(-1).status,'ready');
});

test('a failed index fetch is retried on the next selection',async()=>{
  let attempts=0;const states=[];
  const lookup=createLookup({loadIndex:async()=>{if(++attempts===1)throw new Error('Offline');return {entries};},
    loadText:async()=> 'Source: https://example.com\n\nDefinition',onState:s=>states.push(s)});
  await lookup.select('رحم');assert.equal(states.at(-1).status,'error');
  await lookup.select('رحم');assert.equal(states.at(-1).status,'ready');
});
test('clearing a selection prevents a pending definition from reappearing',async()=>{
  let resolve;const states=[];
  const lookup=createLookup({loadIndex:async()=>({entries}),onState:s=>states.push(s),
    loadText:()=>new Promise(done=>resolve=done)});
  const pending=lookup.select('رحم');await new Promise(setImmediate);
  await lookup.select('');resolve('Source: https://example.com\n\nDefinition');await pending;
  assert.equal(states.at(-1).status,'hidden');
});
test('root page hooks dictionary updates for direct selection, letter browsing and saved roots',()=>{
  const vm=require('node:vm'),fs=require('node:fs');
  const html=fs.readFileSync('src/root.html','utf8');
  assert(html.indexOf('id="root-select"')<html.indexOf('id="root-definition"'));
  assert(html.indexOf('id="search-panel"')<html.indexOf('id="letter-container"'));
  assert(html.indexOf('id="letter-container"')<html.indexOf('id="root-select"'));
  const nodes=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],{
    value:'',innerHTML:'',events:{},appendChild(){},addEventListener(name,fn){this.events[name]=fn;}
  }]));
  const selections=[],saved=new Map();
  const context=vm.createContext({window:{RootDictionary:{show:root=>selections.push(root)}},
    document:{getElementById:id=>nodes.get(id),createElement:()=>({}),addEventListener(){}},
    localStorage:{getItem:key=>saved.get(key)||null,setItem:(key,value)=>saved.set(key,value)},
    QuranUtils:{loadJSON:()=>new Promise(()=>{})},console});
  const source=fs.readFileSync('src/js/root.js','utf8');
  vm.runInContext(source,context);
  vm.runInContext("rootWordsData={'رحم':{Word:{'رحمة':{}}},'رشد':{Word:{'رشد':{}}}};displayVerseData=()=>{};bindSelectListenersOnce();",context);
  nodes.get('root-select').value='رحم';nodes.get('root-select').events.change();
  assert.equal(selections.at(-1),'رحم');
  vm.runInContext("populateRootSelectorByLetter('ر')",context);
  assert(selections.length>1);
  saved.set('selectedRoot','رحم');vm.runInContext('loadSavedSelections()',context);
  assert.equal(selections.at(-1),'رحم');
});

test('definition disclosure expands, collapses and resets for a new root',()=>{
  const {setupDisclosure}=require('../src/js/root-dictionary.js');
  const content={attrs:{},setAttribute(name,value){this.attrs[name]=String(value);}};
  const toggle={attrs:{},hidden:true,textContent:'',setAttribute(name,value){this.attrs[name]=String(value);},addEventListener(type,fn){this.click=fn;}};
  const reset=setupDisclosure(content,toggle);
  reset(true);
  assert.equal(content.attrs['data-expanded'],'false');
  assert.equal(toggle.attrs['aria-expanded'],'false');
  assert.equal(toggle.hidden,false);
  toggle.click();
  assert.equal(content.attrs['data-expanded'],'true');
  assert.equal(toggle.textContent,'Less…');
  toggle.click();assert.equal(content.attrs['data-expanded'],'false');
  toggle.click();reset(true);
  assert.equal(content.attrs['data-expanded'],'false');
  assert.equal(toggle.textContent,'More…');
  reset(false);assert.equal(toggle.hidden,true);
});
