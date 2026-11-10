const {test} = require('node:test');
const assert = require('node:assert/strict');
const {createLoadTracker} = require('../src/site.js');
function setup() {
  let next = 0;
  const timers = new Map();
  const states = [];
  const tracker = createLoadTracker(state => states.push(state), {
    setTimeout(fn) {timers.set(++next, fn); return next;},
    clearTimeout(id) {timers.delete(id);}
  });
  return {tracker, states, tick() {const jobs = [...timers.values()]; timers.clear(); jobs.forEach(fn=>fn());}};
}
test('cached work finishes without showing a spinner', () => {
  const {tracker,states,tick} = setup();
  const done = tracker.begin(); done(); tick();
  assert.equal(states.some(s=>s.visible),false);
  assert.equal(tracker.snapshot().pending,0);
});
test('slow concurrent work stays visible until all operations finish', () => {
  const {tracker,tick} = setup();
  const first = tracker.begin(); const second = tracker.begin(); tick();
  assert.equal(tracker.snapshot().visible,true);
  first(); first();
  assert.equal(tracker.snapshot().pending,1);
  second();
  assert.equal(tracker.snapshot().visible,false);
});
test('failure stops animation and remains visible after other requests settle', () => {
  const {tracker,tick} = setup();
  const first = tracker.begin(); const second = tracker.begin(); tick();
  first(new Error('Network unavailable')); second();
  assert.equal(tracker.snapshot().error,'Network unavailable');
  assert.equal(tracker.snapshot().pending,0);
  assert.equal(tracker.snapshot().visible,true);
});
test('new work clears a previous error and can complete normally', () => {
  const {tracker} = setup();
  tracker.begin()(new Error('Failed'));
  const finish = tracker.begin(); finish();
  assert.equal(tracker.snapshot().error,null);
  assert.equal(tracker.snapshot().visible,false);
});
test('reported rendering errors persist with retry status', () => {
  const {tracker} = setup(); tracker.fail(new Error('Unable to render'));
  assert.equal(tracker.snapshot().error,'Unable to render');
  assert.equal(tracker.snapshot().visible,true);
});
