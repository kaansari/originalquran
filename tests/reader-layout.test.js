const {test}=require('node:test');
const assert=require('node:assert/strict');
const {renderPage,fitLines,watchSize}=require('../src/js/reader-layout.js');
class Node {
  constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.style={};}
  appendChild(node){this.children.push(node);return node;}
  setAttribute(name,value){this[name]=value;}
}
const document={createElement:tag=>new Node(tag),createDocumentFragment:()=>new Node('fragment'),createTextNode:text=>Object.assign(new Node('text'),{textContent:text})};
const layout={basmallah:'بِسْمِ اللّٰهِ',pages:{'2':[
  {number:1,type:'surah_name',sura:2,centered:true},
  {number:2,type:'basmallah',centered:true},
  {number:3,type:'ayah',centered:false,tokens:[{text:'الف',ref:'2:1',wordId:5},{text:'۟',ref:'2:1'},{text:'باء',ref:'2:2',wordId:6}]}
]}};
test('source lines preserve heading, basmallah, marker and word order',()=>{
  const result=renderPage(document,layout,2,{'2':{name:'البقرة'}},(s,v)=>`verse/${s}/${v}`);
  assert.equal(result.children.length,3);
  assert.equal(result.children[0].textContent,'البقرة');
  assert.equal(result.children[1].textContent,'بِسْمِ اللّٰهِ');
  assert.deepEqual(result.children[2].children.map(n=>n.textContent),['الف',' ','۟',' ','باء']);
  assert.equal(result.children[2].children[0].dataset.wordId,5);
  assert.equal(result.children[2].children[2].href,'verse/2/1');
  assert.equal(result.children[2].children[2].dataset.wordId,undefined);
});
test('printed words carry their indexed English translation for the morphology popup',()=>{
  const rendered=renderPage(document,layout,2,{'2':{name:'البقرة'}},()=>'/ ',null,{5:'First meaning',6:'Second meaning'});
  const tokens=rendered.children[2].children.filter(n=>n.tag!=='text');
  assert.equal(tokens[0].dataset.en,'First meaning');
  assert.equal(tokens[2].dataset.en,'Second meaning');
  assert.equal(tokens[1].dataset.en,undefined);
});
test('only requested page tokens are rendered and split verse is preserved',()=>{
  const data={pages:{'1':[{number:1,type:'ayah',tokens:[{text:'الف',ref:'1:1',wordId:1}]}],
    '2':[{number:1,type:'ayah',tokens:[{text:'باء',ref:'1:1',wordId:2}]}]}};
  assert.equal(renderPage(document,data,2,{},()=>'/').children[0].children[0].textContent,'باء');
});
test('missing page fails rather than substituting a different layout',()=>{
  assert.throws(()=>renderPage(document,layout,3,{},()=>'/'),/Missing printed layout/);
});
test('verse selection highlights all its printed tokens across a mixed line',()=>{
  const rendered=renderPage(document,layout,2,{'2':{name:'البقرة'}},()=>'/','2:1');
  const words=rendered.children[2].children.filter(n=>n.tag!=='text');
  assert(words[0].className.includes('highlighted'));
  assert(words[1].className.includes('highlighted'));
  assert(!words[2].className.includes('highlighted'));
});
test('numbered printed slots retain intentional blank lines',()=>{
  const data={pages:{'1':[{number:3,type:'ayah',tokens:[{text:'الف',ref:'1:1',wordId:1}]}]}};
  const rendered=renderPage(document,data,1,{},()=>'/');
  assert.equal(rendered.className,'mushaf-lines');
  assert.equal(rendered.children[0].style.gridRow,'3');
});
test('merged printed token retains both morphology targets and its original text',()=>{
  const data={pages:{'1':[{number:1,type:'ayah',tokens:[{text:'اِلْ یَاسِیْنَ',ref:'37:130',parts:[{text:'اِلْ',wordId:10},{text:'یَاسِیْنَ',wordId:11}]}]}]}};
  const rendered=renderPage(document,data,1,{},()=>'/');
  const token=rendered.children[0].children[0];
  assert.deepEqual(token.children.filter(n=>n.tag!=='text').map(n=>n.dataset.wordId),[10,11]);
  assert.equal(token.children.map(n=>n.textContent).join(''),'اِلْ یَاسِیْنَ');
});
test('line fitting reduces overflow and restores the default size after widening',()=>{
  const previous=global.getComputedStyle;
  global.getComputedStyle=()=>({fontSize:'40px'});
  try {
    const line={style:{},clientWidth:200,get scrollWidth(){return Math.max(this.clientWidth,(parseFloat(this.style.fontSize)||40)*10);}};
    const hidden={style:{fontSize:'30px'},clientWidth:0};
    const container={querySelectorAll:()=>[line,hidden]};
    fitLines(container);
    assert(parseFloat(line.style.fontSize)<21);
    assert(line.scrollWidth<=line.clientWidth+1);
    assert.equal(hidden.style.fontSize,'30px');
    line.clientWidth=500;
    fitLines(container);
    assert.equal(line.style.fontSize,'');
  } finally {global.getComputedStyle=previous;}
});
test('printed lines leave mobile whole-page scaling in charge and clear old line sizes',()=>{
 const lines=[{style:{fontSize:'22px'}},{style:{fontSize:''}}];
 fitLines({closest:selector=>selector==='[data-fit-page="true"]'?{}:null,querySelectorAll:()=>lines});
 assert(lines.every(line=>line.style.fontSize===''));
});
test('RTL words fit even when scrollWidth omits their left-side overflow',()=>{
  const previous=global.getComputedStyle;
  global.getComputedStyle=()=>({fontSize:'40px',columnGap:'4px'});
  try {
    const line={style:{},clientWidth:240,scrollWidth:240};
    line.children=Array.from({length:4},()=>({getBoundingClientRect:()=>({width:(parseFloat(line.style.fontSize)||40)*3})}));
    fitLines({querySelectorAll:()=>[line]});
    assert(parseFloat(line.style.fontSize)<20);
    assert(line.children.reduce((n,c)=>n+c.getBoundingClientRect().width,12)<=241);
  } finally {global.getComputedStyle=previous;}
});
test('viewport and orientation changes schedule fitting without ResizeObserver',()=>{
  const events={},frames=[];
  const window={addEventListener:(n,f)=>{events[n]=f;},visualViewport:{addEventListener:(n,f)=>{events['viewport:'+n]=f;}},requestAnimationFrame:f=>frames.push(f)};
  let fitted=0;
  watchSize({querySelectorAll:()=>{fitted++;return [];}},window,null);
  events.orientationchange();events.resize();events['viewport:resize']();
  assert.equal(frames.length,1);
  frames.shift()();
  assert.equal(fitted,1);
});
test('height-only observer notifications do not refit and cause resize loops',()=>{
  let notify;const frames=[];
  class Observer {constructor(fn){notify=fn;}observe(){}}
  const window={addEventListener(){},requestAnimationFrame:f=>frames.push(f)};
  watchSize({querySelectorAll:()=>[]},window,Observer);
  notify([{contentRect:{width:320,height:800}}]);frames.shift()();
  notify([{contentRect:{width:320,height:700}}]);
  assert.equal(frames.length,0);
  notify([{contentRect:{width:500,height:700}}]);
  assert.equal(frames.length,1);
});
