const {test}=require('node:test');
const assert=require('node:assert/strict');
const {fitPage,createController}=require('../src/js/mobile-reader.js');
test('mobile fitting shrinks all content to the available area and grows again after resize',()=>{
 let scale=1;
 const page={clientHeight:600,clientWidth:320,scrollTop:40,scrollLeft:0,
  style:{setProperty:(name,value)=>{scale=Number(value);}},
  get scrollHeight(){return 1600*scale*scale+20;},get scrollWidth(){return 320;}};
 fitPage(page);
 assert(scale<1&&scale>0.5);
 assert(page.scrollHeight<=601);
 assert.equal(page.scrollTop,0);
 page.clientHeight=2000;fitPage(page);assert.equal(scale,1);
});
test('fitting handles horizontal overflow and waits when the viewport is not measurable',()=>{
 let scale=1;
 const page={clientHeight:600,clientWidth:300,style:{setProperty:(_,v)=>scale=Number(v)},scrollHeight:200,get scrollWidth(){return Math.max(300,600*scale);}};
 fitPage(page);assert(scale<=0.502);
 page.clientHeight=0;const before=scale;fitPage(page);assert.equal(scale,before);
});
test('whole-page fit detects Indian line overflow to the left even when scrollWidth omits it',()=>{
 let scale=1;
 const line={getBoundingClientRect:()=>({left:10,right:290}),children:[{getBoundingClientRect:()=>({left:290-600*scale,right:290})}]};
 const page={clientHeight:600,clientWidth:300,scrollHeight:200,scrollWidth:300,querySelectorAll:()=>[line],style:{setProperty:(_,v)=>scale=Number(v)}};
 fitPage(page);
 assert(scale<0.47);
 assert(line.children[0].getBoundingClientRect().left>=9);
});
class Node {
 constructor(className=''){this.className=className;this.children=[];this.dataset={};this.attrs={};this.hidden=false;this.properties={};this.style={setProperty:(n,v)=>this.properties[n]=v,removeProperty:n=>delete this.properties[n]};this.classList={add:n=>this.className+=' '+n,remove:n=>this.className=this.className.split(' ').filter(c=>c!==n).join(' ')};}
 insertBefore(node,before){if(node.parentNode)node.parentNode.children.splice(node.parentNode.children.indexOf(node),1);const at=before?this.children.indexOf(before):this.children.length;this.children.splice(at,0,node);node.parentNode=this;return node;}
 appendChild(node){return this.insertBefore(node,null);}
 get firstChild(){return this.children[0]||null;}
 get nextSibling(){return this.parentNode?.children[this.parentNode.children.indexOf(this)+1]||null;}
 setAttribute(n,v){this.attrs[n]=v;}
 querySelector(selector){for(const child of this.children){if(child.className.split(' ').includes(selector.slice(1)))return child;const result=child.querySelector(selector);if(result)return result;}return null;}
}
test('mobile docking moves original controls and heading, then restores the desktop nodes',()=>{
 const body=new Node(),header=new Node('site-masthead'),controls=new Node('site-page-controls'),filters=new Node('reader-filter-options'),page=new Node('page'),arabic=new Node('arabic-text-container'),heading=new Node('reader-page-heading');
 body.appendChild(header);body.appendChild(controls);body.appendChild(page);controls.appendChild(filters);page.appendChild(arabic);arabic.appendChild(heading);
 const media={matches:true,addEventListener(){}};
 const window={matchMedia:()=>media,addEventListener(){},innerHeight:800,requestAnimationFrame:()=>{}};
 const document={body,createComment:()=>new Node(),createElement:()=>new Node(),getElementById:id=>id==='quran-container'?page:heading,querySelector:s=>body.querySelector(s)};
 const controller=createController(document,window);
 const dock=body.querySelector('.mobile-reader-dock');
 assert.equal(heading.parentNode,dock);assert.equal(controls.parentNode,dock);assert.equal(header.parentNode,filters);
 assert.equal(heading.dataset.mobileDocked,'true');assert.equal(body.properties['--mobile-reader-height'],'800px');
 assert.equal(page.dataset.fitPage,'true');
 media.matches=false;controller.refresh();
 assert.equal(header.parentNode,body);assert.equal(controls.parentNode,body);assert.equal(heading.parentNode,arabic);
 assert.equal(heading.dataset.mobileDocked,undefined);assert.equal(dock.hidden,true);
 assert.equal(page.dataset.fitPage,undefined);
 media.matches=true;controller.refresh();assert.equal(heading.parentNode,dock);
 assert.equal(dock.children.filter(n=>n===heading).length,1);
});
