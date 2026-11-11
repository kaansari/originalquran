const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=()=>fs.readFileSync('src/writing.html','utf8');
test('writing page uses the shared paginated reader and keeps its writing fonts',()=>{
  const page=html();
  assert.match(page,/<script src="app.js\?/);
  for(const id of ['prev-page','next-page','page-number','sura-select','verse-select','translation-toggle','font-select']) {
    assert.equal([...page.matchAll(new RegExp(`id="${id}"`,'g'))].length,1,id);
  }
  assert.match(page,/<body class="site-writing">/);
  assert.match(page,/<option value="Qahiri">/);
  assert.match(page,/<option value="Amiri Quran">/);
});
class Element {
  constructor(tag='div') {this.tag=tag;this.children=[];this.events={};this.dataset={};this.style={};this.value='';this.textContent='';this.className='';this.attrs={};
    this.classList={add:(...names)=>{this.className+=' '+names.join(' ');},remove:(...names)=>{this.className=this.className.split(' ').filter(n=>!names.includes(n)).join(' ');},contains:name=>this.className.split(' ').includes(name)};
  }
  appendChild(child){if(child.tag==='fragment')this.children.push(...child.children);else this.children.push(child);return child;}
  replaceChildren(){this.children=[];}
  set innerHTML(value){this.children=[];this.html=value;}
  get innerHTML(){return this.html||'';}
  setAttribute(name,value){this.attrs[name]=value;}
  getAttribute(name){return this.attrs[name];}
  addEventListener(type,fn){(this.events[type]??=[]).push(fn);}
  emit(type){(this.events[type]||[]).forEach(fn=>fn({target:this}));}
  scrollIntoView(){}
}
async function setup(savedPage='1') {
  const source=html();assert.match(source,/<script src="app.js\?/);
  const nodes=new Map([...source.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
  const body=new Element('body'),events={},errors=[];
  const storage=new Map([['currentPage',savedPage],['translate','en']]);
  const walk=node=>[node,...node.children.flatMap(walk)];
  const document={body,getElementById:id=>nodes.get(id),querySelector:selector=>selector.includes('quran-words-file')?{content:'json/quran_words.json'}:null,
    createElement:tag=>new Element(tag),createDocumentFragment:()=>new Element('fragment'),createTextNode:text=>{const e=new Element('text');e.textContent=text;return e;},
    querySelectorAll:selector=>walk(nodes.get('quran-container')).filter(n=>n.classList.contains(selector.slice(1))),
    addEventListener(type,fn){(events[type]??=[]).push(fn);}};
  const data={
    'json/sura.json':{'1':{name:'Test surah',start:1,end:4,nAyah:4}},
    'json/combined_quran.json':Object.fromEntries([1,2,3,4].map(i=>[i,{start_word:i,end_word:i,en:`Translation ${i}`} ])),
    'json/quran_words.json':{1:'واحد',2:'اثنان',3:'ثلاثة',4:'أربعة'},
    'json/quran_morphology.json':{},'json/en-word.json':{},
    'json/pagination_map.json':[{page:1,from:'1:1',to:'1:2'},{page:2,from:'1:3',to:'1:4'}]
  };
  vm.runInNewContext(fs.readFileSync('src/app.js','utf8'),{
    document,window:{location:{pathname:'/writing.html'},dispatchEvent(){},SiteUI:{reportError:e=>errors.push(e)}},
    localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,String(value))},
    QuranUtils:{loadJSON:async url=>data[url]},Event,console:{log(){},error:(...e)=>errors.push(e)}
  });
  (events.DOMContentLoaded||[]).forEach(fn=>fn());
  await new Promise(setImmediate);
  assert.deepEqual(errors,[]);
  return {nodes,storage,verses:()=>walk(nodes.get('quran-container')).filter(n=>n.id?.startsWith('verse-')).map(n=>n.id)};
}
test('writing navigation renders one mapped page, saves position, and respects boundaries',async()=>{
  const h=await setup();
  assert.deepEqual(h.verses(),['verse-001001','verse-001002']);
  assert.equal(h.nodes.get('prev-page').disabled,true);
  h.nodes.get('next-page').emit('click');
  assert.deepEqual(h.verses(),['verse-001003','verse-001004']);
  assert.equal(h.nodes.get('next-page').disabled,true);
  assert.equal(h.storage.get('currentPage'),'2');
  h.nodes.get('prev-page').emit('click');
  assert.equal(h.nodes.get('page-number').textContent,'Page 1');
  const restored=await setup('2');assert.deepEqual(restored.verses(),['verse-001003','verse-001004']);
});
test('selecting a writing verse opens its page and translation toggle stays functional',async()=>{
  const h=await setup();
  h.nodes.get('verse-select').value='4';h.nodes.get('verse-select').emit('change');
  assert.equal(h.nodes.get('page-number').textContent,'Page 2');
  assert.deepEqual(h.verses(),['verse-001003','verse-001004']);
  h.nodes.get('translation-toggle').checked=false;h.nodes.get('translation-toggle').emit('change');
  assert.equal(h.storage.get('translate'),'notrans');
});
