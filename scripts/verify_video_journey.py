"""Verify raw regressions and delivery artifacts; never converts missing proof to pass."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runs/2026-10-26-video-journey/evidence'


def read(path):
    raw=path.read_bytes()
    return raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--delivery',action='store_true')
    args=parser.parse_args()
    if args.delivery:
        head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip()
        assert branch=='bansko-experience'
        assert subprocess.check_output(['git','show','81a6c48:app/static/experience/js/main.js'])
        guide=(ROOT/'docs/video-journey.md').read_text()
        assert all(x in guide for x in ['cues','framing','procedural','--group seeking','Still View'])
        tracked=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],text=True)
        assert not tracked.strip(), tracked
        required=['app/static/experience/js/procedural.js','app/static/experience/js/video-clock.js',
                  'app/static/experience/js/video-journey.js','app/static/experience/media/bansko-journey-v2.mp4',
                  'app/static/experience/media/bansko-journey-poster.webp','app/static/experience/media/bansko-town-poster.webp',
                  'docs/video-journey.md','scripts/build_journey_video.py','scripts/check_video_journey.mjs',
                  'scripts/verify_video_journey.py','tests/test_experience.py']
        subprocess.run(['git','ls-files','--error-unmatch',*required],capture_output=True,text=True,check=True)
        print(json.dumps(dict(pass_=True,head=head,branch=branch,previous_engine='81a6c48',guide='docs/video-journey.md',tracked_clean=True,required_tracked=required),indent=2))
        return
    pytest=read(OUT/'pytest.txt')
    failures=re.findall(r'^FAILED (\S+)',pytest,re.M)
    expected=['tests/test_models.py::TestPackageModel::test_create_package','tests/test_routes.py::TestAuthRoutes::test_register_page','tests/test_routes.py::TestBookingRoutes::test_booking_index','tests/test_routes.py::TestBookingRoutes::test_new_booking_requires_auth']
    assert sorted(failures)==sorted(expected), failures
    assert '4 failed, 38 passed' in pytest and 'skipped' not in pytest
    files=list((ROOT/'app/static/experience/js').glob('*.js'))+list((ROOT/'app/static/vendor').rglob('*.js'))+list((ROOT/'app/static/vendor').rglob('*.mjs'))
    total=sum(p.stat().st_size for p in files)
    assert total<=900000,total
    for p in files:
        check=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
        assert check.returncode==0,check.stderr
    url='http://127.0.0.1:5000/static/experience/media/bansko-journey-v2.mp4?v=bansko-video-2'
    response=requests.get(url,headers={'Range':'bytes=0-1023'},timeout=20)
    assert response.status_code==206 and len(response.content)==1024
    assert response.headers['Cache-Control']=='public, max-age=31536000, immutable'
    assert response.headers['Content-Type'].startswith('video/mp4')
    assert response.headers['Content-Range'].startswith('bytes 0-1023/')
    pages={}
    for route in ['/packages','/gallery','/testimonials','/about','/faq','/contact','/auth/login']:
        r=requests.get('http://127.0.0.1:5000'+route,timeout=20)
        assert r.status_code==200,(route,r.status_code)
        pages[route]=r.status_code
    print(json.dumps(dict(pass_=True,pytest={'passed':38,'known_failures':failures},runtime_js_bytes=total,
                         media_range=dict(status=response.status_code,headers=dict(response.headers)),pages=pages),indent=2))


if __name__=='__main__':
    main()
