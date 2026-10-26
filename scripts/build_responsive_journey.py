"""Create responsive seekable films from the original, never from another encode."""
import hashlib,json,os,re,shutil,subprocess
from pathlib import Path
from build_journey_video import ROOT, RUN, MEDIA, DEFAULT

binary=os.getenv('FFMPEG') or shutil.which('ffmpeg') or next((RUN/'tools/imageio_ffmpeg/binaries').glob('*.exe'))
run=ROOT/'.runs/2026-10-26-homepage-refinement/evidence'
run.mkdir(parents=True,exist_ok=True)
source_hash=hashlib.sha256(DEFAULT.read_bytes()).hexdigest()
report={'source':str(DEFAULT),'source_sha256':source_hash,'variants':[]}
for name,width,crf in [('bansko-descent-720-v3.mp4',1280,24),('bansko-descent-540-v3.mp4',960,23)]:
    output=MEDIA/name
    cmd=[str(binary),'-hide_banner','-loglevel','error','-y','-i',str(DEFAULT),'-map','0:v:0','-an',
         '-vf',f'scale={width}:-2','-c:v','libx264','-preset','slow','-crf',str(crf),'-g','12',
         '-keyint_min','12','-sc_threshold','0','-bf','0','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    subprocess.run(cmd,check=True)
    raw=output.read_bytes()
    assert len(raw)<4_000_000,(name,len(raw))
    assert raw.index(b'moov')<raw.index(b'mdat')
    info=subprocess.run([str(binary),'-hide_banner','-i',str(output)],capture_output=True,text=True).stderr
    assert 'Audio:' not in info
    report['variants'].append({'file':name,'bytes':len(raw),'width':width,'height':width*9//16,'gop_frames':12,'command':cmd,'encoding':info})
for name in ['bansko-journey-v2.mp4','bansko-descent-720-v3.mp4']:
    cmd=[str(binary),'-hide_banner','-i',str(DEFAULT),'-i',str(MEDIA/name),'-lavfi','ssim','-f','null','-']
    result=subprocess.run(cmd,capture_output=True,text=True,check=True)
    report.setdefault('source_similarity',[]).append({'file':name,'command':cmd,'ssim':re.findall(r'SSIM Y:.*',result.stderr)[-1]})
assert source_hash==hashlib.sha256(DEFAULT.read_bytes()).hexdigest()
report['pass']=True
print(json.dumps(report,indent=2))
