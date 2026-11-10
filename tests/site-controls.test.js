const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
// A small DOM harness exercises events and preferences without browser dependencies.
class Element {
  constructor(tag, all) {
    this.tagName=tag; this.attrs={}; this.children=[]; this.events={}; this.checked=false;
    this.hidden=false; this.style={}; this.all=all; all.push(this);
    const values=new Set();
    this.classList={contains:name=>values.has(name),toggle(name,force){
      const enabled=force===undefined?!values.has(name):force;
      enabled?values.add(name):values.delete(name); return enabled;
    },add:name=>values.add(name)};
  }
  setAttribute(name,value){this.attrs[name]=String(value);}
  getAttribute(name){return this.attrs[name]??null;}
  removeAttribute(name){delete this.attrs[name];}
  set href(value){this.setAttribute('href',value);}
  get href(){return this.getAttribute('href');}
  append(...nodes){nodes.forEach(n=>{this.children.push(n);n.parent=this;});}
  appendChild(node){this.append(node);return node;}
  addEventListener(name,fn){(this.events[name]??=[]).push(fn);}
  dispatchEvent(event){event.target??=this; (this.events[event.type]||[]).forEach(fn=>fn(event));}
  click(){if(this.tagName==='input')this.checked=!this.checked;this.dispatchEvent({type:'click'});if(this.tagName==='input')this.dispatchEvent({type:'change'});}
  querySelectorAll(tag){return this.children.flatMap(node=>[...(node.tagName===tag?[node]:[]),...node.querySelectorAll(tag)]);}
}
function setup({dictionary=false,darkSystem=false,saved=null,base=''}={}) {
  const all=[], listeners={}, timers=new Map(), storage=new Map();
  if(saved)storage.set('theme',saved);
  const el=tag=>new Element(tag,all);
  const body=el('body'), html=el('html'), nav=el('nav');
  body.append(nav);
  if(dictionary)body.classList.add('site-dictionary');
  for(const href of ['index.html','root.html','maqayis.html','writing.html']){const a=el('a');a.href=base+href;nav.append(a);}
  const document={body,documentElement:html,readyState:'loading',createElement:el,
    getElementById:id=>all.find(e=>e.id===id)||null,
    querySelector:selector=>selector==='.site-toplinks'?nav:null,
    querySelectorAll:()=>all.filter(e=>e.className==='site-more'&&e.open),addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn)};
  const window={matchMedia:()=>({matches:darkSystem}),addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),location:{reload(){}},
    setTimeout(fn){const id=timers.size+1;timers.set(id,fn);return id;},clearTimeout:id=>timers.delete(id)};
  const localStorage={getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,value)};
  const context={window,document,location:{pathname:dictionary?'/originalquran/maqayis.html':'/originalquran/index.html'},localStorage,
    setTimeout:window.setTimeout,clearTimeout:window.clearTimeout,Event:class{constructor(type){this.type=type;}}};
  vm.runInNewContext(fs.readFileSync('src/site.js','utf8'),context);
  const emit=(name,event={})=>(listeners[name]||[]).forEach(fn=>fn(event));
  emit('DOMContentLoaded');
  return {window,document,body,nav,storage,emit,timers};
}
test('shared navigation marks the active page and exposes all existing reading modes',()=>{
  const h=setup();
  const links=h.nav.querySelectorAll('a');
  assert.equal(links.find(l=>l.href==='index.html').getAttribute('aria-current'),'page');
  for(const target of ['page.html','warsh.html','quran.html','random.html','writing_v2.html','raqq.html'])assert(links.some(l=>l.href===target));
});
test('theme button persists preference and synchronizes dictionary colors without hidden controls',()=>{
  const h=setup({dictionary:true});
  h.document.getElementById('site-theme-button').click();
  assert.equal(h.storage.get('theme'),'dark');
  assert(h.body.classList.contains('dark-theme'));
  assert(h.body.classList.contains('dark'));
  h.document.getElementById('site-theme-button').click();
  assert.equal(h.storage.get('theme'),'light');
  assert.equal(h.body.classList.contains('dark'),false);
});
test('system theme is used only when no explicit preference exists',()=>{
  assert(setup({darkSystem:true}).body.classList.contains('dark-theme'));
  assert.equal(setup({darkSystem:true,saved:'light'}).body.classList.contains('dark-theme'),false);
});
test('saved theme is restored without any settings checkbox',()=>{
  const h=setup({saved:'dark'});
  assert(h.body.classList.contains('dark-theme'));
  assert.equal(h.document.getElementById('site-theme-button').getAttribute('aria-pressed'),'true');
});
test('the remaining navigation dropdown closes with Escape',()=>{
  const h=setup();
  const more=h.nav.children.find(e=>e.tagName==='details');more.open=true;
  h.emit('keydown',{key:'Escape'});
  assert.equal(more.open,false);
});
test('storage changes apply the shared preference on an already open page',()=>{
  const h=setup({dictionary:true});
  h.storage.set('theme','dark');h.emit('storage',{key:'theme'});
  assert(h.body.classList.contains('dark'));
});
test('loading status and retry reflect actual work and recover after failure',()=>{
  const h=setup();const status=h.document.getElementById('site-status');
  const finish=h.window.SiteUI.beginLoading();
  assert.equal(status.hidden,true);
  [...h.timers.values()].forEach(fn=>fn());
  assert.equal(status.hidden,false);
  assert.equal(status.getAttribute('aria-busy'),'true');
  finish(new Error('Offline'));
  assert.equal(status.getAttribute('aria-busy'),'false');
  assert.equal(status.children[1].hidden,false);
  const retry=h.window.SiteUI.beginLoading();retry();
  assert.equal(status.hidden,true);
});

test('More links follow the site base for dictionary output in another folder',()=>{
  const h=setup({dictionary:true,base:'../site/'});
  assert(h.nav.querySelectorAll('a').some(link=>link.href==='../site/warsh.html'));
});

test('GitHub link stays available and absolute for custom dictionary output',()=>{
  const h=setup({dictionary:true,base:'../site/'});
  assert(h.nav.querySelectorAll('a').some(link=>link.href==='https://github.com/kaansari/originalquran'));
});
