const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
function setup(online=true){
 const clips=[],alerts=[],opened=[],saved=new Map(),listeners={},timers=[];
 let popup;
 const rootLink={textContent:'كتب',addEventListener(type,fn){this.click=fn;}};
 const document={readyState:'loading',addEventListener(type,fn){listeners[type]=fn;},removeEventListener(type){delete listeners[type];},
  body:{appendChild(node){popup=node;}},
  querySelector:()=>popup&&!popup.removed?popup:null,
  querySelectorAll:selector=>selector==='.clickable-root'?[rootLink]:[],
  createElement:()=>({style:{},dataset:{},attrs:{},setAttribute(k,v){this.attrs[k]=v;},getBoundingClientRect:()=>({width:100,height:100}),focus(){this.focused=true;},remove(){this.removed=true;}})};
 class Audio {
  constructor(src){this.src=src;this.events={};clips.push(this);}
  addEventListener(name,fn){this.events[name]=fn;}
  pause(){this.paused=true;}
  play(){return Promise.resolve();}
 }
 const window={scrollY:0,scrollX:0,innerWidth:800,innerHeight:600,alert:m=>alerts.push(m),open:url=>{opened.push(url);return {};},
  setTimeout:()=>1,clearTimeout(){}};
 vm.runInNewContext(fs.readFileSync('src/common.js','utf8'),{window,document,navigator:{onLine:online},Audio,console,AbortController,
  fetch:async()=>({ok:true,json:async()=>({})}),setTimeout:fn=>timers.push(fn),
  localStorage:{setItem:(k,v)=>saved.set(k,v)}});
 return {api:window.QuranUtils,clips,alerts,opened,saved,listeners,rootLink,timers,get popup(){return popup;}};
}
test('shared word audio URLs retain surah, verse and word padding',()=>{
 const h=setup();assert.equal(h.api.wordAudioURL('2:3:4'),'https://audios.quranwbw.com/words/2/002_003_004.mp3');
 assert.equal(h.api.wordAudioURL('bad'),null);
});
test('shared playback stops the previous clip and respects offline mode',async()=>{
 const h=setup();h.api.playAudio('https://example.com/a.mp3');h.api.playAudio('https://example.com/b.mp3');
 assert.equal(h.clips.length,2);assert(h.clips[0].paused);assert.equal(h.clips[0].currentTime,0);
 const offline=setup(false);offline.api.playAudio('https://example.com/a.mp3');
 assert.equal(offline.clips.length,0);assert.equal(offline.alerts.length,1);
});
test('shared popup escapes content and retains root navigation, audio and dismissal',()=>{
 const h=setup();const word={textContent:'<word>',getAttribute:()=>'<translation>',getBoundingClientRect:()=>({left:20,top:10,bottom:40})};
 h.api.showWordMorphologyPopup('12',word,{'12':{id:'2:3:4',words:{a:{word:'<script>',root:'كتب',lemma:'x',pos:'noun'}}}});
 assert(h.popup.innerHTML.includes('&lt;word&gt;'));
 assert(h.popup.innerHTML.includes('&lt;script&gt;'));
 assert.equal(h.popup.attrs.role,'dialog');assert(h.popup.focused);
 assert.equal(h.clips[0].src,'https://audios.quranwbw.com/words/2/002_003_004.mp3');
 h.timers.forEach(fn=>fn());h.rootLink.click();
 assert.equal(h.saved.get('selectedRoot'),'كتب');assert.equal(h.opened[0],'root.html');
 h.listeners.click({target:{closest:()=>null}});assert(h.popup.removed);
});
