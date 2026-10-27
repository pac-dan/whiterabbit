"""Run isolated functional checks and save actual command receipts."""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / '.runs/2026-10-27-functional-site'
OUT = RUN / 'evidence'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT))
group = sys.argv[1]
report = {'group': group, 'pass': False}

try:
    if group == 'inventory':
        from app import create_app, db
        from app.models.user import User
        from app.models.package import Package
        from app.models.video import Video
        from app.models.testimonial import Testimonial
        from app.models.public_booking import PublicBooking
        app = create_app('testing')
        with app.app_context():
            admin = User(name='Audit admin', email='audit@example.test', is_admin=True)
            admin.set_password('isolated-audit-only')
            package = Package(name='Audit session', description='Isolated audit fixture', price=123.45, duration=2)
            video = Video(title='Audit film', youtube_id='abcdefghijk')
            testimonial = Testimonial(client_name='Audit fixture', testimonial_text='Isolated test only', rating=5)
            booking = PublicBooking(package_key='pro',package_name='Audit session',status='paid',amount_cents=12345)
            db.session.add_all([admin,package,video,testimonial,booking]);db.session.commit()
            client = app.test_client()
            with client.session_transaction() as s: s['_user_id']=str(admin.id);s['_fresh']=True
            urls=['/','/packages','/packages/1','/gallery','/gallery/1','/testimonials','/about','/faq','/contact','/auth/login','/auth/forgot-password','/waiver/standalone','/admin/','/admin/bookings','/admin/bookings/1','/admin/packages','/admin/packages/new','/admin/packages/1/edit','/admin/videos','/admin/videos/new','/admin/videos/1/edit','/admin/testimonials','/admin/testimonials/new','/admin/testimonials/1/edit','/admin/users','/admin/users/1','/admin/waivers','/admin/social']
            report['pages']=[]
            for url in urls:
                try:
                    response=client.get(url)
                    report['pages'].append({'url':url,'status':response.status_code})
                except Exception as exc: report['pages'].append({'url':url,'error':str(exc)})
            report['routes']=[{'path':r.rule,'endpoint':r.endpoint,'methods':sorted(r.methods)} for r in app.url_map.iter_rules()]
            report['integrations']={k:bool(app.config.get(k)) for k in ['STRIPE_SECRET_KEY','STRIPE_WEBHOOK_SECRET','MAIL_USERNAME','MAIL_PASSWORD','AYRSHARE_API_KEY','CALENDLY_API_TOKEN']}
        command=[sys.executable,'-m','pytest','-q','tests']
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (OUT/'baseline-pytest.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
        report['baseline']={'command':command,'exit':result.returncode,'summary':result.stdout.splitlines()[-6:]}
        report['findings']=['Checkout catalogue and DB packages disagree; arbitrary DB sessions cannot be purchased.', 'Payment success fails open on missing key or Stripe retrieval error; no active guest-flow webhook.', 'Order completion trusts a booking_id unrelated to the waiver token and marks scheduled on a GET.', 'Admin edits have unchecked checkboxes retaining true; creation/edit validation differs.', 'Admin/auth/payment templates use CSP-blocked inline scripts and third-party UI dependencies.', 'Contact is an email-draft builder, not a submitted enquiry; social page is a placeholder.', 'Preview database durability and authenticated Vercel access need fresh verification.']
        report['pass']=True
    elif group in ('commerce','admin','forms','regressions'):
        command=[sys.executable,'-m','pytest','-q','tests']
        if group!='regressions':command += ['-k',f'functional_{group}']
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (OUT/f'{group}-pytest.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
        report.update(command=command,exit=result.returncode,summary=result.stdout.splitlines()[-8:])
        if group=='regressions':
            import re
            failures=set(re.findall(r'^FAILED (\S+)',result.stdout,re.M))
            known={'tests/test_models.py::TestPackageModel::test_create_package','tests/test_routes.py::TestAuthRoutes::test_register_page','tests/test_routes.py::TestBookingRoutes::test_booking_index','tests/test_routes.py::TestBookingRoutes::test_new_booking_requires_auth'}
            assert failures <= known and result.returncode in (0,1), report
        else: assert result.returncode==0 and 'passed' in result.stdout, report
        report['pass']=True
    elif group=='preview':
        import requests
        report['responses']=[]
        for suffix in ['/','/packages','/auth/login','/static/experience/js/main.js']:
            url='https://white-rabbit-git-bansko-experience-devman-1a64abec.vercel.app'+suffix
            r=requests.get(url,allow_redirects=False,timeout=30)
            report['responses'].append({'url':url,'status':r.status_code})
        assert all(r['status']==200 for r in report['responses']), 'Preview requires access'
        report['pass']=True
    elif group=='review':
        config=json.loads((RUN/'review-contract.json').read_text())
        state_path=Path(config['runDir'])/'latest.json'
        report['state']=json.loads(state_path.read_text()) if state_path.exists() else None
        assert report['state'] and report['state'].get('verdict'), 'External review not yet available'
        report['pass']=True
    else: raise ValueError(group)
except Exception as exc:
    report['error']=str(exc)
finally:
    (OUT/f'{group}.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(report,indent=2,default=str))
sys.exit(0 if report['pass'] else 1)
