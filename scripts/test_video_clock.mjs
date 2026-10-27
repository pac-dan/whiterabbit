import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const source=await fs.readFile(new URL('../app/static/experience/js/video-clock.js',import.meta.url),'utf8');
const {createCueCurve,createVideoClock}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const cues=[[0,0],[.25,0],[.42,.15],[.80,.72],[1,.995],[1.1,.995]];
class Video extends EventTarget{
 duration=9.041667;paused=true;seeking=false;_time=0;requests=[];
 get currentTime(){return this._time;}
 set currentTime(t){assert.equal(this.seeking,false,'only one seek in flight');this.seeking=true;this._time=t;this.requests.push(t);}
 pause(){this.paused=true;}
 finish(){this.seeking=false;this.dispatchEvent(new Event('seeked'));}
 removeAttribute(){}load(){}
}
test('cue map preserves every anchor, flat hold, monotonicity and continuous speed',()=>{
 const f=createCueCurve(cues);for(const [x,y] of cues)assert.ok(Math.abs(f(x)-y)<1e-9);
 let last=0;for(let i=0;i<=11000;i++){const y=f(i/10000);assert.ok(y>=last-1e-10&&y<=.995+1e-10);last=y;}
 assert.equal(f(.2),0);assert.equal(f(1.05),.995);
 for(const [x] of cues.slice(1,-1)){const h=1e-6,left=(f(x)-f(x-h))/h,right=(f(x+h)-f(x))/h;assert.ok(Math.abs(left-right)<.001,`${x}: ${left} vs ${right}`);}
});
test('rapid scrolling keeps only newest destination, reverses and holds one exact source frame',()=>{
 const v=new Video(),clock=createVideoClock(v,{fps:24,cues},()=>{});v.dispatchEvent(new Event('loadedmetadata'));
 clock.update(.5);assert.equal(v.requests.length,1);clock.update(.9);clock.update(.3);assert.equal(v.requests.length,1);
 const latest=clock.state.desired;v.finish();assert.equal(v.requests.length,2);assert.equal(v.currentTime,latest);v.finish();
 for(let i=0;i<100;i++)clock.update(.3);assert.equal(v.requests.length,2,'held frame makes no new seeks');
 clock.update(1);v.finish();assert.ok(v.currentTime>8.9&&v.currentTime<v.duration);clock.update(0);v.finish();assert.equal(v.currentTime,0);
 for(const t of v.requests)assert.ok(Math.abs(t*24-Math.round(t*24))<1e-8);
 assert.equal(clock.state.maxPending,1);assert.equal(v.paused,true);clock.dispose();clock.update(.8);assert.equal(v.currentTime,0);
});
test('missing metadata and failed media cannot enqueue seeks',()=>{
 const v=new Video(),statuses=[],clock=createVideoClock(v,{fps:24,cues},s=>statuses.push(s));clock.update(.9);assert.equal(v.requests.length,0);
 v.dispatchEvent(new Event('loadedmetadata'));v.dispatchEvent(new Event('error'));clock.update(.9);assert.equal(v.requests.length,0);assert.equal(statuses.at(-1),'error');clock.dispose();
});
test('decoded frame is presented before replacement, with a bounded callback fallback',()=>{
 const v=new Video();let callback,cancelled=false;
 v.requestVideoFrameCallback=cb=>{callback=cb;return 1;};v.cancelVideoFrameCallback=()=>{cancelled=true;};
 const clock=createVideoClock(v,{fps:24,cues},()=>{});v.dispatchEvent(new Event('loadedmetadata'));
 clock.update(.5);clock.update(.7);v.finish();assert.equal(v.requests.length,1,'do not replace the unpresented decoded frame');
 callback(performance.now(),{mediaTime:v.currentTime});assert.equal(v.requests.length,2);v.finish();
 clock.update(.8,performance.now()+100);assert.equal(v.requests.length,3,'missing frame callback cannot stall subsequent seeks');
 clock.dispose();assert.ok(cancelled);
});
