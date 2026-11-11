const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
class Element {
 constructor(tag='div'){this.tag=tag;this.children=[];this.events={};this.dataset={};this.style={};this.value='';this.className='';this.attrs={};
 this.classList={add:(...v)=>this.className+=' '+v.join(' '),remove:(...v)=>this.className=this.className.split(' ').filter(x=>!v.includes(x)).join(' '),contains:v=>this.className.split(' ').includes(v)};}
 appendChild(n){n.tag==='fragment'?this.children.push(...n.children):this.children.push(n);return n;}
 replaceChildren(){this.children=[];}
 set innerHTML(v){this.children=[];this.html=v;}get innerHTML(){return this.html||'';}
 setAttribute(k,v){this.attrs[k]=v;}getAttribute(k){return this.attrs[k];}
 addEventListener(t,fn){(this.events[t]??=[]).push(fn);}emit(t){(this.events[t]||[]).forEach(fn=>fn({target:this}));}
 scrollIntoView(){this.scrolled=true;}
}
async function setup(verse='4'){
 const html=fs.readFileSync('src/quran.html','utf8');
 assert.match(html,/<script src="app.js\?/);
 const nodes=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
 const walk=n=>[n,...n.children.flatMap(walk)];
 const events={},errors=[],requests=[];
 const saved=new Map([['selectedSura','2'],['selectedVerse',verse],['currentPage','2'],['translate','en'],['selectedFont_/quran.html','Raqq']]);
 const meta=selector=>{const name=selector.match(/name="([^"]+)"/)?.[1];const match=html.match(new RegExp(`<meta name="${name}" content="([^"]+)"`));return match?{content:match[1]}:null;};
 const data={
  'json/sura.json':{1:{name:'First',start:1,end:2,nAyah:2},2:{name:'Second',start:3,end:6,nAyah:4}},
  'json/combined_harakat_quran.json':Object.fromEntries([1,2,3,4,5,6].map(i=>[i,{start_word:i,end_word:i,en:`Translation ${i}`} ])),
  'json/quran_harakat_words.json':{1:'أَ',2:'بَ',3:'تَ',4:'ثَ',5:'جَ',6:'حَ'},
  'json/quran_morphology.json':{},'json/en-word.json':{}
 };
 const document={body:new Element('body'),getElementById:id=>nodes.get(id),querySelector:meta,
  createElement:t=>new Element(t),createDocumentFragment:()=>new Element('fragment'),createTextNode:()=>new Element('text'),
  querySelectorAll:s=>walk(nodes.get('quran-container')).filter(n=>n.classList.contains(s.slice(1))),
  addEventListener(t,fn){(events[t]??=[]).push(fn);}};
 vm.runInNewContext(fs.readFileSync('src/app.js','utf8'),{document,
  window:{location:{pathname:'/quran.html'},dispatchEvent(){},SiteUI:{reportError:e=>errors.push(e)}},
  localStorage:{getItem:k=>saved.get(k)||null,setItem:(k,v)=>saved.set(k,String(v))},
  QuranUtils:{loadJSON:async url=>{requests.push(url);assert(url in data,url);return data[url];}},Event,console:{log(){},error:(...e)=>errors.push(e)}});
 (events.DOMContentLoaded||[]).forEach(fn=>fn());await new Promise(setImmediate);assert.deepEqual(errors,[]);
 return {nodes,saved,requests,all:()=>walk(nodes.get('quran-container')),verses:()=>walk(nodes.get('quran-container')).filter(n=>n.id?.startsWith('verse-'))};
}
test('full chapters use one shared reader, vowelled data, and no pagination download',async()=>{
 const h=await setup();
 assert.deepEqual(h.verses().map(n=>n.id),['verse-002001','verse-002002','verse-002003','verse-002004']);
 assert(!h.requests.includes('json/pagination_map.json'));
 assert.equal(h.saved.get('currentPage'),'2');
 assert(h.verses().at(-1).scrolled);
 assert(h.all().some(n=>n.classList.contains('font-raqq')));
 assert(h.all().some(n=>n.className==='verse-link'&&n.textContent==='۝٤'));
});
test('chapter switching and verse jumps keep complete chapters and local verse numbering',async()=>{
 const h=await setup();h.nodes.get('sura-select').value='1';h.nodes.get('sura-select').emit('change');
 assert.deepEqual(h.verses().map(n=>n.id),['verse-001001','verse-001002']);
 h.nodes.get('verse-select').value='2';h.nodes.get('verse-select').emit('change');
 assert.equal(h.saved.get('selectedVerse'),'2');assert.equal(h.verses().length,2);
 h.nodes.get('sura-select').value='2';h.nodes.get('sura-select').emit('change');
 assert.equal(Number(h.nodes.get('verse-select').value),1);
 h.nodes.get('translation-toggle').checked=false;h.nodes.get('translation-toggle').emit('change');
 assert(h.all().filter(n=>n.className==='translation').every(n=>n.style.display==='none'));
});

test('legacy global verse selections restore to their chapter-local verse',async()=>{
 const h=await setup('6');assert.equal(h.nodes.get('verse-select').value,4);
 assert(h.verses().at(-1).scrolled);
});

test('Full Chapters loads the original color Amiri face while writing keeps its tracing font',()=>{
 const page=fs.readFileSync('src/quran.html','utf8');
 assert.match(page,/https:\/\/fonts\.googleapis\.com\/css2\?family=Amiri\+Quran/);
 assert.match(page,/--amiri-family:\s*"Amiri Quran"/);
 assert.match(page,/font-palette:\s*normal/);
 const writing=fs.readFileSync('src/writing.html','utf8');
 assert(!writing.includes('fonts.googleapis.com'));
});
