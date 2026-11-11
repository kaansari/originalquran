const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
test('long random verses render completely without translation and remain copyable',async()=>{
 const html=fs.readFileSync('src/random.html','utf8');
 const nodes=new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(m=>[m[1],{textContent:'',style:{},events:{},addEventListener(name,fn){this.events[name]=fn;}}]));
 const words=Object.fromEntries(Array.from({length:200},(_,i)=>[i+1,`كلمة${i+1}`]));
 const data={'json/sura.json':{1:{name:'Test',start:1,end:1}},'json/combined_quran.json':{1:{start_word:1,end_word:200}},'json/quran_words.json':words};
 const requests=[],errors=[];let copied;
 const context={document:{getElementById:id=>nodes.get(id)},window:{location:{search:'?verse=1',href:'https://example.com/random.html?verse=1'},SiteUI:{beginLoading:()=>()=>{},reportError:e=>errors.push(e)}},
 QuranUtils:{loadJSON:async url=>{requests.push(url);return data[url];}},URLSearchParams,
 navigator:{clipboard:{writeText:async text=>{copied=text;}}},setTimeout(){},console:{error:e=>errors.push(e)}};
 const source=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
 vm.runInNewContext(source,context);await new Promise(setImmediate);
 assert.deepEqual(errors,[]);
 assert.equal(nodes.get('verse').textContent,Object.values(words).join(' '));
 assert(!requests.includes('json/en-word.json'));
 assert(!nodes.has('en'));
 nodes.get('copy').events.click({preventDefault(){}});await new Promise(setImmediate);
 assert(copied.includes('كلمة200'));
 assert(nodes.get('tweet').href.startsWith('https://twitter.com/intent/tweet?'));
 assert(!html.includes('<svg'));
});
