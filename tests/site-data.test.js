const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
function setup(fetch) {
  const completed = [], timers = new Map();
  let starts = 0, timerId = 0;
  const window = {
    SiteUI: {beginLoading() {starts++; return error=>completed.push(error);}},
    setTimeout(fn) {timers.set(++timerId,fn); return timerId;},
    clearTimeout(id) {timers.delete(id);}
  };
  const document = {readyState:'loading',addEventListener(){}};
  vm.runInNewContext(fs.readFileSync('src/common.js','utf8'),{window,document,fetch,AbortController,console});
  return {load:window.QuranUtils.loadJSON,completed,timers,get starts(){return starts;}};
}
test('JSON loader tracks parsing as well as fetching, and permits browser caching', async () => {
  let resolveJSON, requestOptions;
  const harness = setup(async (url,options)=>{
    requestOptions=options;
    return {ok:true,json:()=>new Promise(resolve=>resolveJSON=resolve)};
  });
  const request = harness.load('json/sura.json');
  await new Promise(setImmediate);
  assert.equal(harness.completed.length,0);
  resolveJSON({surah:1});
  assert.deepEqual(await request,{surah:1});
  assert.equal(requestOptions.cache,'default');
  assert.equal(harness.completed.length,1);
  assert.equal(harness.timers.size,0);
});
test('HTTP failure settles loading and preserves the rejection for application handlers',async()=>{
  const harness=setup(async()=>({ok:false,status:404}));
  await assert.rejects(harness.load('missing.json'),/HTTP 404/);
  assert.equal(harness.completed.length,1);
  assert.match(harness.completed[0].message,/404/);
  assert.equal(harness.timers.size,0);
});
test('invalid JSON also settles loading',async()=>{
  const harness=setup(async()=>({ok:true,json:async()=>{throw new Error('Invalid JSON');}}));
  await assert.rejects(harness.load('bad.json'),/Invalid JSON/);
  assert.equal(harness.completed.length,1);
});
test('stalled requests abort and leave no loading timer behind',async()=>{
  const harness=setup((url,options)=>new Promise((resolve,reject)=>{
    options.signal.addEventListener('abort',()=>reject(new Error('Aborted')));
  }));
  const request=harness.load('slow.json');
  [...harness.timers.values()][0]();
  await assert.rejects(request,/Aborted/);
  assert.equal(harness.completed.length,1);
  assert.equal(harness.timers.size,0);
});
