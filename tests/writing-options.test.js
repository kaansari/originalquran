const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
function setup(saved=null,blocked=false,font="Amiri Quran"){
 const attrs={},values=new Map(saved?[['writingFontStyle',saved]]:[]);
 const select={value:'italic',addEventListener(type,fn){this.change=fn;}};
 const fontSelect={value:font,addEventListener(type,fn){this.change=fn;}};
 values.set('selectedFont_writing.html',font);
 const properties={};
 vm.runInNewContext(fs.readFileSync('src/js/writing-options.js','utf8'),{
  document:{getElementById:id=>id==='writing-style'?select:fontSelect,body:{setAttribute:(key,value)=>attrs[key]=value,style:{setProperty:(key,value)=>properties[key]=value}}},
  localStorage:{getItem:key=>{if(blocked)throw Error('Blocked');return values.get(key);},setItem:(key,value)=>{if(blocked)throw Error('Blocked');values.set(key,value);}}
 });
 return {attrs,values,select,fontSelect,properties};
}
test('writing starts italic and can switch to straight and back',()=>{
 const h=setup();assert.equal(h.attrs['data-writing-style'],'italic');
 h.select.value='normal';h.select.change();
 assert.equal(h.attrs['data-writing-style'],'normal');
 assert.equal(h.values.get('writingFontStyle'),'normal');
 h.select.value='italic';h.select.change();assert.equal(h.attrs['data-writing-style'],'italic');
});
test('saved straight preference is restored',()=>{
 const h=setup('normal');assert.equal(h.select.value,'normal');assert.equal(h.attrs['data-writing-style'],'normal');
});
test('style switching still works when storage is blocked',()=>{
 const h=setup(null,true);h.select.value='normal';h.select.change();assert.equal(h.attrs['data-writing-style'],'normal');
});

test('all writing fonts set the same family for the text and its line-height strut',()=>{
 const h=setup();
 for(const name of ['System Arabic','Raqq','Amiri','Noto Naskh Arabic','Noto Sans Arabic','Amiri Quran']) {
  h.fontSelect.value=name;h.fontSelect.change();
  assert.equal(h.attrs['data-writing-font'],name);
  assert(h.properties['--writing-font-family']);
 }
});
test('saved additional font is applied before chapter rendering',()=>{
 const h=setup(null,false,'Noto Naskh Arabic');
 assert.equal(h.attrs['data-writing-font'],'Noto Naskh Arabic');
 assert(h.properties['--writing-font-family'].includes('Noto Naskh Arabic'));
});

test('retired Qahiri writing preference falls back to Uthmani Hafs',()=>{
 const h=setup(null,false,'Qahiri');
 assert.equal(h.attrs['data-writing-font'],'Amiri Quran');
 assert(h.properties['--writing-font-family'].includes('hafs'));
});
