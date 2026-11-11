const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
function setup(saved=null,blocked=false){
 const attrs={},values=new Map(saved?[['writingFontStyle',saved]]:[]);
 const select={value:'italic',addEventListener(type,fn){this.change=fn;}};
 vm.runInNewContext(fs.readFileSync('src/js/writing-options.js','utf8'),{
  document:{getElementById:()=>select,body:{setAttribute:(key,value)=>attrs[key]=value}},
  localStorage:{getItem:key=>{if(blocked)throw Error('Blocked');return values.get(key);},setItem:(key,value)=>{if(blocked)throw Error('Blocked');values.set(key,value);}}
 });
 return {attrs,values,select};
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
