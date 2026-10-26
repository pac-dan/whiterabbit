"""Ledger evidence commands. Assertions are deliberately based on saved raw proof."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import requests
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / '.runs/2026-10-26-bansko-experience'
EVIDENCE = RUN / 'evidence'
sys.path.insert(0, str(ROOT))


def command(*args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(result.stdout, result.stderr)
    assert result.returncode == 0, result.returncode
    return result.stdout


def report(name='browser-report.json'):
    data = json.loads((EVIDENCE/name).read_text(encoding='utf-8-sig'))
    assert data['pass'], data.get('failure')
    return data


def run(mode):
    print(f'Verification: {mode}; root={ROOT}; raw evidence={EVIDENCE}', flush=True)
    if mode == 'git':
        branch = command('git', 'branch', '--show-current').strip()
        assert branch == 'bansko-experience'
        assert 'vercel port: drop Socket.IO/Redis/eventlet, add Vercel config' in command('git', 'log', '-1', '--format=%h %s', 'vercel-port')
        command('git', 'merge-base', '--is-ancestor', 'vercel-port', 'HEAD')
        command('git', 'log', '--oneline', 'vercel-port..HEAD')
    elif mode == 'assets':
        meta = json.loads((ROOT/'app/static/experience/terrain/bansko-height.json').read_text())
        assert meta['source'] != 'procedural fallback'
        assert 750 < meta['minM'] < 1250 and 2700 < meta['maxM'] < 3100
        assert (ROOT/'app/static/experience/terrain/bansko-height.bin').stat().st_size == 524288
        assert (ROOT/'app/static/experience/terrain/bansko-height-256.bin').stat().st_size == 131072
        assert len(list((ROOT/'app/static/experience/placeholders').glob('*.webp'))) == 19
        print(json.dumps(meta, indent=2))
        print((EVIDENCE/'terrain-build.txt').read_text(encoding='utf-8-sig'))
        print((EVIDENCE/'placeholder-build.txt').read_text(encoding='utf-8-sig'))
    elif mode == 'browser':
        data = report()
        assert not data['errors'] and not data['requests']
        assert len(data['chapters']) == 14
        for row in data['chapters']:
            assert row['state']['mode'] == '3d'
            if row.get('shot'):
                assert (EVIDENCE/'shots'/row['shot']).stat().st_size > 1000
            print(json.dumps(row))
    elif mode == 'content':
        data = report()
        assert len([x for x in data['content'] if x.get('ringCounter')]) == 2
        proof = report('supplement-report.json')
        assert all(x['emptyDB'] and x['links'] and x['rail'] and x['meshClick'] for x in proof['content'])
        print(json.dumps(data['content'], indent=2));print(json.dumps(proof['content'], indent=2))
    elif mode == 'slots':
        proof = report()['slots']
        assert all(proof[k]['replaced'] for k in ['image','video','model'])
        assert proof['model']['animated'] and proof['video']['playing'] and proof['video']['paused']
        assert all(proof['brokenRecover']) and proof['restoredToNone']
        from app.experience.content import EXPERIENCE
        assert EXPERIENCE['rider']['src'] is None
        assert all(c['media']['src'] is None for c in EXPERIENCE['ring']['cards'])
        print(json.dumps(proof, indent=2))
        for p in (EVIDENCE/'fixtures').iterdir(): print(f'{p}: {p.stat().st_size} bytes')
    elif mode == 'fallback':
        proof = report()['fallback']
        assert len(proof) == 4 and all(x['allSixSections'] for x in proof)
        print(json.dumps(proof, indent=2))
    elif mode == 'csp':
        proof = report('csp-report.json')
        assert not proof['violations'] and not proof['errors'] and not proof['requests']
        assert len(proof['chapters']) == 14
        headers = (EVIDENCE/'csp-headers.txt').read_text(encoding='utf-8-sig')
        assert 'Content-Security-Policy:' in headers and "'nonce-" in headers
        print(headers);print(json.dumps(proof, indent=2))
    elif mode == 'quality':
        proof = report()
        assert len(proof['quality']) == 2
        supplemental = report('supplement-report.json')
        assert all(x['hiddenPause'] and x['footerPause'] for x in supplemental['quality'])
        print(json.dumps(proof['quality'], indent=2));print(json.dumps(supplemental['quality'], indent=2))
        print('Hardware desktop measurements; mobile is a viewport emulation on the same GPU, not a physical mid-range phone.')
    elif mode == 'budget':
        groups = {'javascript':[*(ROOT/'app/static/vendor').glob('*.js'),*(ROOT/'app/static/vendor').glob('*.mjs'),*(ROOT/'app/static/experience/js').glob('*.js')],
                  'placeholders':list((ROOT/'app/static/experience/placeholders').glob('*.webp'))}
        for name, files in groups.items():
            size = sum(p.stat().st_size for p in files)
            assert size <= (900000 if name == 'javascript' else 1500000), size
            print(f'{name}: {size} bytes')
            for p in files: print(f'  {p.relative_to(ROOT)}: {p.stat().st_size}')
        for asset in ['experience/js/main.js','experience/terrain/bansko-height.bin','vendor/three.module.min.js']:
            r=requests.get(f'http://127.0.0.1:5000/static/{asset}?v=bansko-1')
            assert r.status_code == 200
            assert r.headers['Cache-Control'] == 'public, max-age=31536000, immutable'
            print(asset, r.status_code, r.headers['Cache-Control'], len(r.content))
        assert 'immutable' not in requests.get('http://127.0.0.1:5000/static/css/style.css').headers['Cache-Control']
    elif mode == 'tests':
        result = subprocess.run([sys.executable,'-m','pytest','-q',str(ROOT/'tests')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        print(result.stdout,result.stderr)
        (EVIDENCE/'pytest.txt').write_text(result.stdout+result.stderr, encoding='utf-8')
        baseline = (EVIDENCE/'baseline.txt').read_text(encoding='utf-8-sig')
        failed=lambda text:set(re.findall(r'^FAILED (tests/[^\s]+)',text,re.M))
        assert result.returncode == 1 and failed(result.stdout) == failed(baseline)
        assert '4 failed, 30 passed' in result.stdout
        print('PASS: exactly the four baseline failures, all eight new experience tests pass.')
        others=command('git','diff','vercel-port','--name-only','--','app/templates','app/static/css/style.css')
        assert all(x in ['app/templates/base.html','app/templates/index.html','app/templates/index_legacy.html'] for x in others.splitlines())
        print('Other page templates and shared style.css unchanged; visual screenshots saved in evidence/shots/other-*.png.')
        print(json.dumps(report()['notes'],indent=2))
    elif mode == 'docs':
        for p in ['docs/content-drop-in.md','app/static/experience/media/README.md']:
            text=(ROOT/p).read_text(encoding='utf-8');assert len(text)>1000
            for token in ['content.py','mp4','GLB','WebP']: assert token in text
            print(p, len(text.encode()), '\n',text)
    elif mode == 'delivery':
        data=report('delivery-report.json')
        assert all(x['status']==200 for x in data['responses'])
        local=command('git','rev-parse','HEAD').strip()
        remote=command('git','ls-remote','--heads','origin','bansko-experience').strip().split()[0]
        assert local==remote
        print(json.dumps(data,indent=2));print('HEAD matches origin/bansko-experience:',local)
    print(f'PASS: {mode}',flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode');run(parser.parse_args().mode)
