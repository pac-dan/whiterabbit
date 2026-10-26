// Exact seeks, one in flight. A fast jump replaces the destination, not a queue.
export function interpolate(points,x) {
    if(x<=points[0][0])return points[0][1];
    for(let i=1;i<points.length;i++)if(x<=points[i][0]){
        const [a,b]=points[i-1],[c,d]=points[i];
        return b+(d-b)*(x-a)/(c-a);
    }
    return points.at(-1)[1];
}
export function createVideoClock(video,config,onStatus) {
    let desired=0,issued=0,completed=0,maxPending=0,lastIssued=-Infinity,disposed=false;
    let pending=false,failed=false,ready=false,displayed=0,frameCallback=0;
    const usableEnd=()=>Math.max(0,video.duration-Math.max(.06,1/(config.fps||24)));
    const status=()=>({ready,failed,duration:Number.isFinite(video.duration)?video.duration:0,
        desired,current:video.currentTime,displayed,seeking:pending,issued,completed,maxPending,paused:video.paused});
    const metadata=()=>{if(Number.isFinite(video.duration)&&video.duration>0){ready=true;onStatus('ready');}};
    const error=()=>{failed=true;pending=false;onStatus('error');};
    const done=()=>{pending=false;completed++;displayed=video.currentTime;};
    const pause=()=>video.pause();
    video.addEventListener('loadedmetadata',metadata);
    video.addEventListener('error',error);
    video.addEventListener('seeked',done);
    video.addEventListener('play',pause);
    if(video.requestVideoFrameCallback){
        const frame=(_,meta)=>{displayed=meta.mediaTime;if(!disposed)frameCallback=video.requestVideoFrameCallback(frame);};
        frameCallback=video.requestVideoFrameCallback(frame);
    }
    video.muted=true;video.defaultMuted=true;video.loop=false;video.pause();
    return {
        update(progress,time){
            if(!ready||failed||disposed)return;
            desired=Math.min(usableEnd(),Math.max(0,interpolate(config.cues,progress)*video.duration));
            if(!pending&&!video.seeking&&time-lastIssued>=32&&Math.abs(video.currentTime-desired)>.018){
                pending=true;maxPending=Math.max(maxPending,1);lastIssued=time;issued++;
                try{video.currentTime=desired;}catch{error();}
            }
        },
        get state(){return status();},
        dispose(){disposed=true;video.pause();video.removeEventListener('loadedmetadata',metadata);
            video.removeEventListener('error',error);video.removeEventListener('seeked',done);video.removeEventListener('play',pause);
            if(frameCallback)video.cancelVideoFrameCallback(frameCallback);
            video.removeAttribute('src');video.load();}
    };
}
