const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=(filename='writing.html')=>fs.readFileSync(`src/${filename}`,'utf8');
test('writing page uses the shared paginated reader and keeps its writing fonts',()=>{
  const page=html();
  assert.match(page,/<script src="app.js\?/);
  for(const id of ['prev-page','next-page','page-number','sura-select','verse-select','translation-toggle','font-select']) {
    assert.equal([...page.matchAll(new RegExp(`id="${id}"`,'g'))].length,1,id);
  }
  assert.match(page,/<body class="site-writing">/);
  assert.doesNotMatch(page,/<option value="Qahiri">/);
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
  querySelector(selector){return this.children.flatMap(function walk(n){return [n,...n.children.flatMap(walk)];}).find(n=>n.classList.contains(selector.slice(1)))||null;}
}
async function setup(savedPage='1',filename='writing.html',savedFont=null,pathname=`/${filename}`,realData=false,legacyOnly=false,printed=false) {
  let source=html(filename);assert.match(source,/<script src="app.js\?/);
  if(printed)source=source.replace('</head>','<meta name="quran-lines-file" content="json/test-lines.json"></head>');
  const nodes=new Map([...source.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],new Element()]));
  const heading=nodes.get('reader-page-heading');
  if(heading){const title=new Element('span');title.className='sura-name';title.appendChild(nodes.get('page-sura-title'));heading.appendChild(nodes.get('prev-page'));heading.appendChild(title);heading.appendChild(nodes.get('next-page'));}
  const body=new Element('body'),events={},errors=[];
  const storage=new Map([['currentPage',savedPage],['currentPageMadinah',savedPage],['writingPageMadinah',savedPage],['translate','en']]);
  const pageKey=source.match(/name="quran-page-storage-key" content="([^"]+)"/)?.[1];
  if(pageKey)storage.set(pageKey,savedPage);
  if(legacyOnly){storage.delete('currentPageMadinah');storage.set('selectedSura','1');storage.set('selectedVerse','1');}
  const fontKey=`selectedFont_${pathname.split('/').pop()||'home'}`;
  if(savedFont)storage.set(fontKey,savedFont);
  const fontMarkup=source.match(/<select id="font-select">([\s\S]*?)<\/select>/)[1];
  nodes.get('font-select').options=[...fontMarkup.matchAll(/value="([^"]+)"/g)].map(m=>({value:m[1]}));
  const walk=node=>[node,...node.children.flatMap(walk)];
  const fontRequests=[];
  const document={body,fonts:{load:async font=>{fontRequests.push(font);return [{}];}},getElementById:id=>nodes.get(id),querySelector:selector=>{if(selector==='#quran-container .arabic-text-container')return walk(nodes.get('quran-container')).find(n=>n.className==='arabic-text-container');const name=selector.match(/name="([^"]+)"/)?.[1];const m=source.match(new RegExp(`<meta name="${name}" content="([^"]+)"`));return m?{content:m[1]}:null;},
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
  data['json/quranic_words.json']=data['json/quran_words.json'];
  data['json/quranic_warsh_words.json']=data['json/quran_words.json'];
  data['json/pagination_madinah.json']=data['json/pagination_map.json'];
  data['json/sura.json']['5']={name:'Fifth',start:5,end:16,nAyah:12};
  for(let i=5;i<=16;i++){data['json/combined_quran.json'][i]={start_word:i,end_word:i,en:`Translation ${i}`};data['json/quran_words.json'][i]=`كلمة${i}`;}
  if(realData){
    for(const filename of ['sura.json','combined_quran.json','quran_words.json','en-word.json','pagination_madinah.json','pagination_map.json'])data[`json/${filename}`]=JSON.parse(fs.readFileSync(`src/json/${filename}`,'utf8'));
    const wordsPath=source.match(/name="quran-words-file" content="([^"]+)"/)[1];
    data[wordsPath]=JSON.parse(fs.readFileSync(`src/${wordsPath}`,'utf8'));
    for(const name of ['quran-pagination-file','quran-lines-file']){
      const path=source.match(new RegExp(`name="${name}" content="([^"]+)"`))?.[1];
      if(path)data[path]=JSON.parse(fs.readFileSync(`src/${path}`,'utf8'));
    }
  }
  const requests=[];
  data['json/test-lines.json']={pages:{'1':[{number:1,type:'ayah',tokens:[{text:'SOURCE FIRST',ref:'1:1',wordId:1}]}],
    '2':[{number:1,type:'ayah',tokens:[{text:'SOURCE SECOND',ref:'1:3',wordId:3}]}]}};
  vm.runInNewContext(fs.readFileSync('src/app.js','utf8'),{
    document,window:{location:{pathname},dispatchEvent(){},SiteUI:{reportError:e=>errors.push(e)}},
    localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,String(value))},
    ReaderLayout:{...require('../src/js/reader-layout.js'),fitLines(){}},
    QuranUtils:{loadJSON:async url=>{requests.push(url);return data[url];}},Event,console:{log(){},error:(...e)=>errors.push(e)}
  });
  (events.DOMContentLoaded||[]).forEach(fn=>fn());
  await new Promise(setImmediate);
  assert.deepEqual(errors,[]);
  return {nodes,storage,requests,fontRequests,content:()=>walk(nodes.get('quran-container')),verses:()=>walk(nodes.get('quran-container')).filter(n=>n.id?.startsWith('verse-')).map(n=>n.id)};
}
test('surah names follow font changes and retain that font after page navigation',async()=>{
  for(const filename of ['index.html','page.html','warsh.html','simple.html','writing.html']){
    const h=await setup('1',filename);
    const font=h.nodes.get('font-select');font.value='Raqq';font.emit('change');
    let headings=h.content().filter(n=>n.classList.contains('sura-name'));
    assert(headings.length,filename);
    assert(headings.every(n=>n.style.fontFamily==='var(--kufi-family)'),filename);
    const numbers=h.content().filter(n=>n.classList.contains('verse-link'));
    assert(numbers.length,filename);
    assert.deepEqual(numbers.map(n=>n.textContent),['﴿1﴾','﴿2﴾'],filename);
    assert(numbers.every(n=>n.style.fontFamily==='var(--kufi-family)'),filename);
    h.nodes.get('next-page').emit('click');
    headings=h.content().filter(n=>n.classList.contains('sura-name'));
    assert(headings.every(n=>n.style.fontFamily==='var(--kufi-family)'),filename);
    assert(h.content().filter(n=>n.classList.contains('verse-link')).every(n=>n.style.fontFamily==='var(--kufi-family)'),filename);
  }
});
test('Indian reader uses real printed pages, its own bookmark, matching font, and verse ranges',async()=>{
  const h=await setup('1','indian.html',null,'/indian.html',true);
  assert.equal(h.nodes.get('page-number').textContent,'Page 1 of 610');
  assert.deepEqual(h.fontRequests,['32px "IndoPak Nastaleeq"']);
  assert.equal(h.nodes.get('font-select').value,'IndoPak Nastaleeq');
  const english=JSON.parse(fs.readFileSync('src/json/en-word.json','utf8'));
  const firstWord=h.content().find(n=>Number(n.dataset.wordId)===1);
  assert.equal(firstWord.dataset.en,english['1']);
  assert.equal(h.content().filter(n=>n.className?.includes('mushaf-line arabic')).length,8);
  h.nodes.get('next-page').emit('click');
  assert.equal(h.storage.get('currentPageIndian'),'2');
  assert.equal(h.storage.get('currentPageMadinah'),'1');
  h.nodes.get('sura-select').value='5';h.nodes.get('sura-select').emit('change');
  assert(h.content().some(n=>n.className?.includes('highlighted')));
  h.nodes.get('reader-view').value='verses';h.nodes.get('reader-view').emit('change');
  h.nodes.get('verse-end-select').value='10';h.nodes.get('verse-end-select').emit('change');
  assert.equal(h.verses().length,10);
  const last=await setup('610','indian.html',null,'/indian.html',true);
  assert.equal(last.nodes.get('next-page').disabled,true);
  assert.equal(last.nodes.get('page-number').textContent,'Page 610 of 610');
});
test('optional printed layout replaces flowing page words and keeps range mode and arrows',async()=>{
  const h=await setup('1','index.html',null,'/index.html',false,false,true);
  assert(h.requests.includes('json/test-lines.json'));
  assert(h.content().some(n=>n.textContent==='SOURCE FIRST'));
  h.nodes.get('next-page').emit('click');
  assert(h.content().some(n=>n.textContent==='SOURCE SECOND'));
  assert.equal(h.content().filter(n=>n===h.nodes.get('reader-page-heading')).length,1);
  h.nodes.get('reader-view').value='verses';h.nodes.get('reader-view').emit('change');
  assert(!h.content().some(n=>n.className?.includes('mushaf-line')));
});
test('writing navigation renders one mapped page, saves position, and respects boundaries',async()=>{
  const h=await setup();
  assert.deepEqual(h.verses(),['verse-001001','verse-001002']);
  assert.equal(h.nodes.get('prev-page').disabled,true);
  assert(h.content().includes(h.nodes.get('reader-page-heading')));
  assert.equal(h.nodes.get('page-sura-title').textContent,'Test surah (1)');
  h.nodes.get('next-page').emit('click');
  assert.deepEqual(h.verses(),['verse-001003','verse-001004']);
  assert.equal(h.nodes.get('next-page').disabled,true);
  assert.equal(h.content().filter(n=>n===h.nodes.get('reader-page-heading')).length,1);
  assert(h.content().includes(h.nodes.get('prev-page')));
  assert.equal(h.storage.get('writingPageMadinah'),'2');
  h.nodes.get('prev-page').emit('click');
  assert.match(h.nodes.get('page-number').textContent,/^Page 1(?: of \d+)?$/);
  const restored=await setup('2');assert.deepEqual(restored.verses(),['verse-001003','verse-001004']);
});
test('selecting a writing verse opens its page and translation toggle stays functional',async()=>{
  const h=await setup();
  h.nodes.get('verse-select').value='4';h.nodes.get('verse-select').emit('change');
  assert.match(h.nodes.get('page-number').textContent,/^Page 2(?: of \d+)?$/);
  assert.deepEqual(h.verses(),['verse-001003','verse-001004']);
  h.nodes.get('translation-toggle').checked=false;h.nodes.get('translation-toggle').emit('change');
  assert.equal(h.storage.get('translate'),'notrans');
});

test('page selectors share the compact controls row and arrows belong to the verse container',()=>{
  for(const filename of ['index.html','page.html','warsh.html','writing.html']) {
    const page=fs.readFileSync(`src/${filename}`,'utf8');
    const controls=page.match(/<section class="site-page-controls"[\s\S]*?<\/section>/)?.[0];
    assert(controls?.includes('class="page-selectors"'),filename);
    const container=page.slice(page.indexOf('id="quran-container"'));
    assert(container.includes('id="prev-page"'),filename);
    assert(container.includes('id="next-page"'),filename);
    assert(container.includes('class="sura-name"'),filename);
  }
});

test('default home page is the Hafs reader with the same vowelled word data',()=>{
 const home=fs.readFileSync('src/index.html','utf8');
 const hafs=fs.readFileSync('src/page.html','utf8');
 assert.match(home,/<meta name="page-info" content="Eastern Reading">/);
 const source=s=>s.match(/<meta name="quran-words-file" content="([^"]+)"/)[1];
 assert.equal(source(home),source(hafs));
 assert.equal(source(home),'json/quranic_words.json');
});

test('Hafs defaults apply at both home URLs and replace unavailable old font choices',async()=>{
 for(const pathname of ['/index.html','/']) {
  const h=await setup('1','index.html','Qahiri',pathname);
  assert.equal(h.nodes.get('font-select').value,'Amiri Quran');
  assert.deepEqual(h.verses(),['verse-001001','verse-001002']);
 }
});

test('Old Quran preserves the previous home data and reader variants have the requested names',()=>{
 const simple=fs.readFileSync('src/simple.html','utf8');
 assert.match(simple,/<meta name="quran-words-file" content="json\/quran_words.json">/);
 assert.match(simple,/<meta name="page-info" content="Old Quran">/);
 const home=fs.readFileSync('src/index.html','utf8');
 assert.match(home,/<meta name="page-info" content="Eastern Reading">/);
 const western=fs.readFileSync('src/warsh.html','utf8');
 assert.match(western,/<meta name="page-info" content="Western Reading">/);
});

test('Old Quran defaults to Qahiri and applies it to text and headings',async()=>{
 const h=await setup('1','simple.html');
 assert.equal(h.nodes.get('font-select').value,'Qahiri');
 assert(h.content().filter(n=>n.classList.contains('arabic')).every(n=>n.style.fontFamily==='Qahiri, serif'));
 assert(h.content().filter(n=>n.classList.contains('sura-name')).every(n=>n.style.fontFamily==='Qahiri, serif'));
 assert.deepEqual(h.verses(),['verse-001001','verse-001002']);
});

test('Writing and Eastern Reading share the Mushaf map with separate bookmarks',async()=>{
 const h=await setup();
 assert(h.requests.includes('json/pagination_madinah.json'));
 assert(!h.requests.includes('json/pagination_map.json'));
 const other=await setup('1','index.html');
 assert(other.requests.includes('json/pagination_madinah.json'));
 assert.equal(other.storage.get('currentPageMadinah'),'1');
});
test('Writing can display exactly chapter 5 verses 1 through 10',async()=>{
 const h=await setup();
 h.nodes.get('reader-view').value='verses';h.nodes.get('reader-view').emit('change');
 h.nodes.get('sura-select').value='5';h.nodes.get('sura-select').emit('change');
 h.nodes.get('verse-end-select').value='10';h.nodes.get('verse-end-select').emit('change');
 assert.deepEqual(h.verses(),Array.from({length:10},(_,i)=>`verse-005${String(i+1).padStart(3,'0')}`));
 assert.equal(h.nodes.get('page-number').textContent,'Verses 5:1–10');
 assert.equal(h.nodes.get('prev-page').disabled,true);
 assert.equal(h.nodes.get('next-page').disabled,true);
 h.nodes.get('verse-select').value='3';h.nodes.get('verse-select').emit('change');
 assert.equal(h.verses().length,8);
 h.nodes.get('verse-end-select').value='1';h.nodes.get('verse-end-select').emit('change');
 assert.deepEqual(h.verses(),['verse-005001']);
});
test('Writing can return from a selected range to page navigation',async()=>{
 const h=await setup();
 h.nodes.get('reader-view').value='verses';h.nodes.get('reader-view').emit('change');
 h.nodes.get('verse-end-select').value='4';h.nodes.get('verse-end-select').emit('change');
 assert.equal(h.verses().length,4);
 h.nodes.get('reader-view').value='page';h.nodes.get('reader-view').emit('change');
 assert.equal(h.verses().length,2);
 assert.equal(h.nodes.get('next-page').disabled,false);
});

test('real Madinah data opens seven verses on page 1 and supports chapter 5 range and bookmark',async()=>{
 const h=await setup('1','writing.html',null,'/writing.html',true);
 assert.equal(h.nodes.get('page-number').textContent,'Page 1 of 604');
 assert.deepEqual(h.verses(),Array.from({length:7},(_,i)=>`verse-001${String(i+1).padStart(3,'0')}`));
 h.nodes.get('next-page').emit('click');
 assert.equal(h.nodes.get('page-number').textContent,'Page 2 of 604');
 assert.deepEqual(h.verses(),Array.from({length:5},(_,i)=>`verse-002${String(i+1).padStart(3,'0')}`));
 h.nodes.get('reader-view').value='verses';h.nodes.get('reader-view').emit('change');
 h.nodes.get('sura-select').value='5';h.nodes.get('sura-select').emit('change');
 h.nodes.get('verse-end-select').value='10';h.nodes.get('verse-end-select').emit('change');
 assert.deepEqual(h.verses(),Array.from({length:10},(_,i)=>`verse-005${String(i+1).padStart(3,'0')}`));
 assert.equal(h.storage.get('currentPage'),'1');
 const map=JSON.parse(fs.readFileSync('src/json/pagination_madinah.json','utf8'));
 const position=ref=>{const [s,v]=ref.split(':').map(Number);return s*1000+v;};
 const page=map.find(p=>position(p.from)<=5001&&position(p.to)>=5001).page;
 assert.equal(h.storage.get('writingPageMadinah'),String(page));
 h.nodes.get('reader-view').value='page';h.nodes.get('reader-view').emit('change');
 assert.equal(h.nodes.get('page-number').textContent,`Page ${page} of 604`);
});

test('all paginated reading pages use the same 604-page map and verse-range controls',()=>{
 for(const filename of ['index.html','page.html','warsh.html','simple.html','writing.html']){
  const page=fs.readFileSync(`src/${filename}`,'utf8');
  assert.match(page,/<meta name="quran-pagination-file" content="json\/pagination_madinah.json">/,filename);
  for(const id of ['reader-view','verse-select','verse-end-select'])assert(page.includes(`id="${id}"`),`${filename}: ${id}`);
 }
});

for(const filename of ['index.html','page.html','warsh.html','simple.html']){
 test(`${filename} uses actual 604-page boundaries and exact selected verse ranges`,async()=>{
  const h=await setup('1',filename,null,`/${filename}`,true);
  assert.equal(h.nodes.get('page-number').textContent,'Page 1 of 604');
  assert.equal(h.verses().length,7);
  h.nodes.get('next-page').emit('click');
  assert.deepEqual(h.verses(),Array.from({length:5},(_,i)=>`verse-002${String(i+1).padStart(3,'0')}`));
  h.nodes.get('reader-view').value='verses';h.nodes.get('reader-view').emit('change');
  h.nodes.get('sura-select').value='5';h.nodes.get('sura-select').emit('change');
  h.nodes.get('verse-end-select').value='10';h.nodes.get('verse-end-select').emit('change');
  assert.deepEqual(h.verses(),Array.from({length:10},(_,i)=>`verse-005${String(i+1).padStart(3,'0')}`));
  assert.equal(h.nodes.get('prev-page').disabled,true);
  assert.equal(h.nodes.get('next-page').disabled,true);
  h.nodes.get('reader-view').value='page';h.nodes.get('reader-view').emit('change');
  assert(h.nodes.get('page-number').textContent.startsWith('Page '));
  assert.equal(h.nodes.get('next-page').disabled,false);
 });
}

test('legacy arrow-navigation bookmarks migrate by verse instead of reusing old page numbers',async()=>{
 const h=await setup('100','index.html',null,'/index.html',true,true);
 const old=JSON.parse(fs.readFileSync('src/json/pagination_map.json','utf8')).find(p=>p.page===100);
 const [sura,verse]=old.from.split(':').map(Number);
 const pos=ref=>{const [s,v]=ref.split(':').map(Number);return s*1000+v;};
 const page=JSON.parse(fs.readFileSync('src/json/pagination_madinah.json','utf8')).find(p=>pos(p.from)<=pos(old.from)&&pos(p.to)>=pos(old.from));
 assert.equal(h.storage.get('currentPageMadinah'),String(page.page));
 assert(h.verses().includes(`verse-${String(sura).padStart(3,'0')}${String(verse).padStart(3,'0')}`));
 assert.equal(h.storage.get('currentPage'),'100');
 assert(h.requests.includes('json/pagination_map.json'));
});

test('retired Qahiri preferences migrate to supported defaults',async()=>{
 for(const page of ['writing.html']){
  const h=await setup('1',page,'Qahiri');
  assert.equal(h.nodes.get('font-select').value,'Amiri Quran');
  assert.equal(h.storage.get(`selectedFont_${page}`),'Amiri Quran');
 }
});
test('Eastern Reading exposes the same supported fonts as Full Chapters',()=>{
 const values=name=>[...html(name).match(/<select id="font-select">([\s\S]*?)<\/select>/)[1].matchAll(/value="([^"]+)"/g)].map(m=>m[1]);
 assert.deepEqual(values('index.html'),values('quran.html'));
 assert.deepEqual(values('page.html'),values('quran.html'));
 assert(!values('quran.html').includes('Qahiri'));
});

test('Old Quran restores Qahiri and keeps other explicitly saved font choices',async()=>{
 for(const font of ['Qahiri','Raqq','Amiri Quran']){
  const h=await setup('1','simple.html',font);
  assert.equal(h.nodes.get('font-select').value,font);
 }
});
