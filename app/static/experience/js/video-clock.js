// Exact seeks, one in flight. A fast jump replaces the destination, not a queue.
export function interpolate(points,x) {
    if(x<=points[0][0])return points[0][1];
    for(let i=1;i<points.length;i++)if(x<=points[i][0]){
        const [a,b]=points[i-1],[c,d]=points[i];
        return b+(d-b)*(x-a)/(c-a);
    }
    return points.at(-1)[1];
}
// Shape-preserving cubic: continuous speed at cue boundaries, exact flat holds.
// Harmonic interior slopes cannot overshoot or briefly rewind a rising cue.
export function createCueCurve(points){
    const widths=points.slice(1).map((p,i)=>p[0]-points[i][0]);
    const slopes=widths.map((h,i)=>(points[i+1][1]-points[i][1])/h);
    const tangents=points.map((_,i)=>{
        if(i===0||i===points.length-1)return 0;
        const a=slopes[i-1],b=slopes[i];
        if(a*b<=0)return 0;
        const w1=2*widths[i]+widths[i-1],w2=widths[i]+2*widths[i-1];
        return (w1+w2)/(w1/a+w2/b);
    });
    return x=>{
        if(x<=points[0][0])return points[0][1];
        for(let i=0;i<widths.length;i++)if(x<=points[i+1][0]){
            const h=widths[i],t=(x-points[i][0])/h,t2=t*t,t3=t2*t;
            return (2*t3-3*t2+1)*points[i][1]+(t3-2*t2+t)*h*tangents[i]
                +(-2*t3+3*t2)*points[i+1][1]+(t3-t2)*h*tangents[i+1];
        }
        return points.at(-1)[1];
    };
}
export function createVideoClock(video,config,onStatus) {
    let desired=0,issued=0,completed=0,maxPending=0,disposed=false;
    let pending=false,failed=false,ready=false,displayed=0,frameCallback=0,awaitingFrame=false,completedAt=0;
    const fps=config.fps||24,cue=createCueCurve(config.cues);
    const usableEnd=()=>Math.max(0,video.duration-Math.max(.06,1/(config.fps||24)));
    const status=()=>({ready,failed,duration:Number.isFinite(video.duration)?video.duration:0,
        desired,current:video.currentTime,displayed,seeking:pending,issued,completed,maxPending,paused:video.paused});
    const metadata=()=>{if(Number.isFinite(video.duration)&&video.duration>0){ready=true;onStatus('ready');}};
    const error=()=>{failed=true;pending=false;onStatus('error');};
    const pump=()=>{
        if(!ready||failed||disposed||pending||awaitingFrame||video.seeking||Math.abs(video.currentTime-desired)<.25/fps)return;
        pending=true;awaitingFrame=!!video.requestVideoFrameCallback;maxPending=Math.max(maxPending,1);issued++;
        try{video.currentTime=desired;}catch{error();}
    };
    // No queued historical destinations: on decode completion take the latest.
    const done=()=>{pending=false;completed++;completedAt=performance.now();if(!video.requestVideoFrameCallback)displayed=video.currentTime;pump();};
    const pause=()=>video.pause();
    video.addEventListener('loadedmetadata',metadata);
    video.addEventListener('error',error);
    video.addEventListener('seeked',done);
    video.addEventListener('play',pause);
    if(video.requestVideoFrameCallback){
        const frame=(_,meta)=>{displayed=meta.mediaTime;awaitingFrame=false;if(!disposed){frameCallback=video.requestVideoFrameCallback(frame);pump();}};
        frameCallback=video.requestVideoFrameCallback(frame);
    }
    video.muted=true;video.defaultMuted=true;video.loop=false;video.pause();
    return {
        update(progress,time=performance.now()){
            if(!ready||failed||disposed)return;
            const target=Math.max(0,cue(progress)*video.duration);
            // A source frame has one seek target, avoiding redundant same-frame decodes.
            desired=Math.min(Math.floor(usableEnd()*fps),Math.round(target*fps))/fps;
            // Let the compositor present a decoded frame before replacing it.
            // Some browsers omit callbacks for same-frame seeks; do not deadlock.
            if(awaitingFrame&&!pending&&time-completedAt>80)awaitingFrame=false;
            pump();
        },
        get state(){return status();},
        dispose(){disposed=true;video.pause();video.removeEventListener('loadedmetadata',metadata);
            video.removeEventListener('error',error);video.removeEventListener('seeked',done);video.removeEventListener('play',pause);
            if(frameCallback)video.cancelVideoFrameCallback(frameCallback);
            video.removeAttribute('src');video.load();}
    };
}
