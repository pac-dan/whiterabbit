"""Evidence-backed acceptance gate for the applied homepage motion work."""
import json
from pathlib import Path
import re
import subprocess
import sys
import requests

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'.runs/2026-10-26-homepage-motion-polish'
OUT=RUN/'evidence'
sys.path.insert(0,str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

def read(path):
 raw=Path(path).read_bytes()
 return raw.decode('utf-16') if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else raw.decode('utf-8-sig')
def report(name):
 value=json.loads(read(OUT/name));assert value.get('pass'),value.get('failure')
 return value
def run(mode):
 result={'mode':mode,'pass':False}
 if mode=='framing':
  data=report('motion-browser.json');assert len(data['views'])==2
  for v in data['views']:
   assert len(v['framing'])==33
   for frame in v['framing']:
    b=frame['bounds'];assert b['left']>.08 and b['right']<.95
    assert b['top']>.12 and b['bottom']<(.53 if v['viewport']['width']<768 else .8)
  result['dense_samples']=sum(len(v['framing']) for v in data['views'])
  result['views']=[{'viewport':v['viewport'],'worst_bottom':max(x['bounds']['bottom'] for x in v['framing'])} for v in data['views']]
 elif mode=='rider':
  motion=report('motion-browser.json');m=motion['modules'];assert m['meshes']>=20 and m['poseChanges'] and m['poseReverses']
  assert all(abs(x-.035)<.0001 for x in m['contact'])
  slots=report('browser-report.json')['slots']
  assert all(slots[k]['replaced'] for k in ['image','video','model'])
  assert slots['video']['playing'] and slots['video']['paused'] and slots['model']['animated']
  assert all(slots['brokenRecover']) and slots['restoredToNone']
  blend=slots['model']['poseBlend'];assert blend['toe']>0 and blend['heel']<0 and blend['toe']==blend['reversed']
  from app.experience.content import EXPERIENCE
  assert EXPERIENCE['rider']['src'] is None and EXPERIENCE['rider']['poses'] is None
  result.update(meshes=m['meshes'],contact_samples=len(m['contact']),min_contact=min(m['contact']),max_contact=max(m['contact']),slots=slots)
 elif mode=='snow':
  modules=report('motion-browser.json')['modules'];assert modules['sprayReverses'] and modules['tracksReverse'] and modules['poseReverses']
  result['module_proof']=modules
 elif mode=='ring':
  m=report('motion-browser.json');assert all(v['ringRotates'] and v['ringLink'] for v in m['views'])
  proof=report('supplement-report.json');assert all(v['meshClick'] and v['links'] and v['rail'] for v in proof['content'])
  original=report('browser-report.json');assert len([x for x in original['content'] if x.get('ringCounter') and x.get('ringRotates')])==2
  result['content']=proof['content'];result['counter_and_rotation']=True
 elif mode=='chapters':
  data=report('motion-browser.json');assert not data['errors'] and not data['requests']
  assert len(data['views'])==2 and len(data['recordings'])==2
  for view in data['views']:
   assert len(view['chapters'])==6 and view['reverse']
   for chapter in view['chapters']:
    assert (OUT/'shots'/chapter['file']).stat().st_size>1000
   for label in ['rider-reverse','ring-reverse']:
    assert (OUT/f"shots/{view['viewport']['width']}x{view['viewport']['height']}-{label}.png").stat().st_size>1000
  for video in data['recordings']:assert Path(video['file']).stat().st_size>1000
  result['chapters']=[{'viewport':v['viewport'],'shots':[c['file'] for c in v['chapters']]} for v in data['views']];result['recordings']=data['recordings']
 elif mode=='compatibility':
  basic=report('browser-report.json');assert len(basic['fallback'])==4 and all(x['allSixSections'] for x in basic['fallback'])
  assert not basic['errors'] and not basic['requests']
  empty=report('supplement-report.json');assert all(x['emptyDB'] for x in empty['content'])
  csp=report('motion-csp.json');assert len(csp['views'])==2 and not csp['errors'] and not csp['requests'] and not csp['violations']
  pages=report('public/browser-report.json');assert not pages['errors'] and not pages['failed'] and not pages['violations']
  r=requests.get('http://127.0.0.1:5001/',headers={'X-Forwarded-Proto':'https'},timeout=15);assert r.status_code==200
  policy=r.headers['Content-Security-Policy'];assert "'nonce-" in policy
  (OUT/'csp-headers.txt').write_text('\n'.join(f'{k}: {v}' for k,v in r.headers.items()),encoding='utf-8')
  result.update(fallback=basic['fallback'],public_pages=len(pages['pages']),csp=policy,violations=csp['violations'])
 elif mode=='checks':
  log=read(OUT/'pytest.txt');baseline=read(ROOT/'.runs/2026-10-26-bansko-experience/evidence/baseline.txt')
  failed=lambda s:set(re.findall(r'^FAILED (tests/[^\s]+)',s,re.M))
  assert failed(log)==failed(baseline) and len(failed(log))==4 and '36 passed' in log
  assert not re.search(r'\d+ skipped',log)
  basic=report('browser-report.json');assert len(basic['quality'])==2 and all(q['forced']==1 and q['watchdog']['stepped'] for q in basic['quality'])
  supplement=report('supplement-report.json');assert all(q['hiddenPause'] and q['footerPause'] and q['wheelResume'] and q['performanceState']['firstFrameMs']<2500 for q in supplement['quality'])
  files=[*ROOT.glob('app/static/vendor/*.js'),*ROOT.glob('app/static/vendor/*.mjs'),*ROOT.glob('app/static/experience/js/*.js')]
  size=sum(p.stat().st_size for p in files);assert size<=900000,size
  placeholders=list(ROOT.glob('app/static/experience/placeholders/*.webp'));assert sum(p.stat().st_size for p in placeholders)<=1500000
  assert (ROOT/'app/static/experience/terrain/bansko-height.bin').stat().st_size<=520*1024
  caches=[]
  for name in ['experience/js/main.js','experience/terrain/bansko-height.bin','vendor/three.module.min.js']:
   r=requests.get('http://127.0.0.1:5000/static/'+name+'?v=bansko-3',timeout=15);assert r.status_code==200 and r.headers['Cache-Control']=='public, max-age=31536000, immutable';caches.append({'file':name,'cache':r.headers['Cache-Control']})
  result.update(failures=sorted(failed(log)),runtime_bytes=size,files={str(p.relative_to(ROOT)):p.stat().st_size for p in files},cache=caches,quality=supplement['quality'],note='Measured local Windows GPU; mobile viewport emulation is not physical-phone performance.')
 elif mode=='delivery':
  for file in ['docs/content-drop-in.md','app/static/experience/media/README.md']:
   text=read(ROOT/file);assert all(token in text for token in ['board_node','poses','height'])
  branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip();assert branch=='bansko-experience'
  head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
  remote=subprocess.check_output(['git','ls-remote','--heads','origin','bansko-experience'],cwd=ROOT,text=True).split()[0];assert head==remote
  assert not subprocess.check_output(['git','status','--porcelain','--','app','scripts','tests','docs/content-drop-in.md'],cwd=ROOT,text=True).strip()
  result.update(branch=branch,head=head,remote=remote,docs=['docs/content-drop-in.md','app/static/experience/media/README.md'])
 elif mode=='preview':
  data=json.loads(read(OUT/'preview-status.json'));assert data['pass'],data
  assert len(data['responses'])==3 and all(x['status']==200 for x in data['responses']);result.update(data)
 else:raise ValueError(mode)
 result['pass']=True
 return result

if __name__=='__main__':
 try: print(json.dumps(run(sys.argv[1]),indent=2))
 except Exception as e:
  import traceback
  print(json.dumps({'mode':sys.argv[1],'pass':False,'error':str(e),'traceback':traceback.format_exc()},indent=2));sys.exit(1)
