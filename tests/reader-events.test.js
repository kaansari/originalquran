const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
function element() {
  const values=new Set(), listeners={};
  return {style:{},checked:false,value:'',classList:{
    add(...items){items.forEach(item=>values.add(item));},
    remove(...items){items.forEach(item=>values.delete(item));},
    contains:item=>values.has(item)
  },addEventListener(type,fn){(listeners[type]??=[]).push(fn);},
  emit(type){(listeners[type]||[]).forEach(fn=>fn({target:this}));}};
}
for (const [filename,script] of [['index.html','app.js'],['page.html','app.js'],['warsh.html','app.js'],['quran.html','app_quran.js'],['root.html',null],['writing.html','app.js']]) {
  test(`${filename}: visible ${script ? "translation and font" : "translation"} controls retain their event handlers`,()=>{
    const html=fs.readFileSync(`src/${filename}`,'utf8');
    const nodes=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(match=>[match[1],element()]));
    const translated=element(), arabic=element(), body=element(), events={};
    const saved=new Map([['translate','en']]);
    const document={body,getElementById:id=>nodes.get(id)||null,
      querySelector:()=>({content:'json/quran_words.json'}),
      querySelectorAll:selector=>selector==='.translation'?[translated]:selector==='.arabic'?[arabic]:[],
      addEventListener(type,fn){(events[type]??=[]).push(fn);}};
    const window={location:{pathname:`/${filename}`},addEventListener(){}};
    const localStorage={getItem:key=>saved.get(key)||null,setItem:(key,value)=>saved.set(key,value)};
    const source=script?fs.readFileSync(`src/${script}`,'utf8'):[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(match=>match[1]).join('\n');
    vm.runInNewContext(source,{
      window,document,localStorage,QuranUtils:{loadJSON:()=>new Promise(()=>{})},
      console:{log(){},error(){}},URLSearchParams,Event
    });
    assert.equal(nodes.has('menu-toggle'),false);
    assert.equal(nodes.has('theme-toggle'),false);
    (events.DOMContentLoaded||[]).forEach(fn=>fn());
    const toggle=nodes.get('translation-toggle');
    assert.equal(toggle.checked,true);
    toggle.checked=false;toggle.emit('change');
    assert.equal(saved.get('translate'),'notrans');
    assert.equal(translated.style.display,'none');
    toggle.checked=true;toggle.emit('change');
    assert.equal(saved.get('translate'),'en');
    assert.equal(translated.style.display,'block');
    if (!script) return;
    const choice=filename==='writing.html'?'Amiri Quran':'Raqq';
    const font=nodes.get('font-select');font.value=choice;font.emit('change');
    assert(arabic.classList.contains(choice==='Raqq'?'font-raqq':'font-amiri'));
    assert([...saved.entries()].some(([key,value])=>key.startsWith('selectedFont_')&&value===choice));
  });
}
