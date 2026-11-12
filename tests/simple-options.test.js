const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function setup(saved=null){
 const events={},attributes={},storage=new Map(saved?[['qahiriDots_simple.html',saved]]:[]);
 const checkbox={checked:true,addEventListener:(name,fn)=>checkbox[name]=fn};
 const font={value:'Qahiri',addEventListener:(name,fn)=>font[name]=fn};
 const label={hidden:false};let fits=0;
 vm.runInNewContext(fs.readFileSync('src/js/simple-options.js','utf8'),{
  document:{getElementById:id=>({'qahiri-dots-toggle':checkbox,'qahiri-dot-control':label,'font-select':font})[id],body:{setAttribute:(n,v)=>attributes[n]=v}},
  window:{addEventListener:(n,fn)=>events[n]=fn,MobileReader:{fit:()=>fits++}},
  localStorage:{getItem:n=>storage.get(n)||null,setItem:(n,v)=>storage.set(n,v)}
 });
 return {checkbox,font,label,attributes,storage,events,fits:()=>fits};
}
test('Qahiri starts dotless and the choice can be toggled and persisted',()=>{
 const h=setup();assert.equal(h.attributes['data-qahiri-dots'],'off');
 h.checkbox.checked=false;h.checkbox.change();
 assert.equal(h.attributes['data-qahiri-dots'],'on');assert.equal(h.storage.get('qahiriDots_simple.html'),'on');
 assert(h.fits()>0);
 h.checkbox.checked=true;h.checkbox.change();assert.equal(h.attributes['data-qahiri-dots'],'off');
});
test('saved dotted preference restores and the option is only available for Qahiri',()=>{
 const h=setup('on');assert.equal(h.checkbox.checked,false);
 h.font.value='Amiri Quran';h.events['quran:ready']();assert.equal(h.label.hidden,true);
 h.font.value='Qahiri';h.font.change();assert.equal(h.label.hidden,false);
 assert.equal(h.checkbox.checked,false);
});
