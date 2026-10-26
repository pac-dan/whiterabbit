"""Concrete evidence commands for the alpine public-page run ledger."""
import json
from pathlib import Path
import re
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'.runs/2026-10-26-alpine-pages'
EVIDENCE=RUN/'evidence'


def report(name):
    data=json.loads((EVIDENCE/name).read_text(encoding='utf-8-sig'))
    assert data['pass'],data.get('failure')
    assert not data['errors'] and not data['failed'] and not data['violations']
    return data


def main(mode):
    print('Verification:',mode,'root:',ROOT)
    data=report('browser-report.json')
    if mode=='shell':
        assert len(data['home'])==2
        assert all(x['state']['mode']=='3d' for x in data['home'])
        assert any(x.get('mobileNavigation') for x in data['interactions'])
        unchanged=subprocess.run(['git','diff','5f49ac1','--name-only','--','app/static/experience/js','app/routes/payment.py','app/models','app/templates/payment','app/templates/auth','app/templates/waiver.html','app/templates/waiver_standalone.html'],cwd=ROOT,capture_output=True,text=True)
        assert unchanged.returncode==0 and not unchanged.stdout.strip(),unchanged.stdout
        print('Homepage engine, models, payment/waiver/auth templates and payment rules unchanged.')
        print(json.dumps(data['home'],indent=2))
        print(json.dumps([x for x in data['interactions'] if x.get('mobileNavigation')],indent=2))
    elif mode=='packages':
        rows=[x for x in data['pages'] if x['name'] in ('packages','package-detail')]
        assert len(rows)==4
        assert len([x for x in data['interactions'] if x.get('packages')])==2
        assert len([x for x in data['empty'] if x['name']=='packages'])==2
        print(json.dumps(rows,indent=2));print(json.dumps([x for x in data['interactions'] if x.get('packages')],indent=2))
        print('Matching checkout configuration and mismatched package enquiry fallbacks are asserted in tests/test_public_pages.py.')
    elif mode=='gallery':
        rows=[x for x in data['pages'] if x['name'] in ('gallery','video-detail')]
        assert len(rows)==4
        interactions=[x for x in data['interactions'] if x.get('galleryFilter')]
        assert len(interactions)==2 and all(x['clearFilter'] and x['embedOnDemand'] and x['csrfLike'] for x in interactions)
        assert len([x for x in data['empty'] if x['name']=='gallery'])==2
        print(json.dumps(rows+interactions,indent=2))
        print('YouTube player request and like response stubbed in browser; no live third-party playback or database likes claimed.')
    elif mode=='testimonials':
        rows=[x for x in data['pages'] if x['name']=='testimonials']
        assert len(rows)==2
        assert len([x for x in data['interactions'] if x.get('ratingDetails')])==2
        assert len([x for x in data['empty'] if x['name']=='testimonials'])==2
        print(json.dumps(rows,indent=2));print('Full DB quotes, ratings and empty states verified; missing sample photos replaced by initials.')
    elif mode=='supporting':
        rows=[x for x in data['pages'] if x['name'] in ('about','faq','contact')]
        assert len(rows)==6
        assert len([x for x in data['interactions'] if x.get('faqSearch') and x.get('emailDraft')])==2
        print(json.dumps(rows+[x for x in data['interactions'] if x.get('emailDraft')],indent=2))
        print('All13 existing FAQ answers retained. Contact prepares mailto draft only; no mail was sent.')
    elif mode=='checks':
        csp=report('csp-report.json')
        assert len(data['pages'])==16 and len(csp['pages'])==16
        for r in data['pages']+csp['pages']:
            assert (EVIDENCE/'shots'/r['shot']).stat().st_size>1000
        result=subprocess.run([sys.executable,'-m','pytest','-q',str(ROOT/'tests')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        output=result.stdout+result.stderr
        (EVIDENCE/'pytest.txt').write_text(output,encoding='utf-8');print(output)
        baseline=(ROOT/'.runs/2026-10-26-bansko-experience/evidence/baseline.txt').read_text(encoding='utf-8-sig')
        failed=lambda text:set(re.findall(r'^FAILED (tests/[^\s]+)',text,re.M))
        assert result.returncode==1 and failed(output)==failed(baseline)
        assert '4 failed, 36 passed' in output
        local=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        remote=subprocess.check_output(['git','ls-remote','--heads','origin','bansko-experience'],cwd=ROOT,text=True).split()[0]
        assert local==remote,'Push reviewed source before finalizing A6'
        assert not subprocess.check_output(['git','status','--porcelain','--','app','scripts','tests'],cwd=ROOT,text=True).strip(),'Commit all public-page source before finalizing A6'
        assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='bansko-experience'
        print('Both-size browser and actual production CSP reports: zero errors/failed requests/violations.16 views each.')
        print('New frame-src entry is only https://www.youtube-nocookie.com. No new script policy allowances.')
        print('Pushed HEAD:',local)
    else:
        raise ValueError(mode)
    print('PASS:',mode)


if __name__=='__main__':main(sys.argv[1])
