"""Run regression suite and require honest saved browser/encoding proof."""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / '.runs/2026-10-26-homepage-refinement'
OUT = RUN / 'evidence'
command = [sys.executable, '-m', 'pytest', '-q', 'tests']
result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
(OUT / 'pytest.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
failed = re.findall(r'^FAILED (\S+)', result.stdout, re.M)
known = {'tests/test_models.py::TestPackageModel::test_create_package',
         'tests/test_routes.py::TestAuthRoutes::test_register_page',
         'tests/test_routes.py::TestBookingRoutes::test_booking_index',
         'tests/test_routes.py::TestBookingRoutes::test_new_booking_requires_auth'}
reports = {}
for name in ['hero', 'journey', 'gallery', 'booking', 'accessibility', 'encoding', 'performance-after']:
    file = OUT / f'{name}.json'
    raw = file.read_bytes() if file.exists() else b'{}'
    data = json.loads(raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8-sig'))
    reports[name] = data.get('pass') is True
handoff = RUN / 'HANDOFF.md'
report = dict(command=command, pytest_exit=result.returncode, known_failures=sorted(known),
              actual_failures=failed, reports=reports, handoff=handoff.exists(),
              pass_=set(failed) == known and result.returncode == 1 and all(reports.values()) and handoff.exists())
report['pass'] = report.pop('pass_')
(OUT / 'regressions.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
sys.exit(0 if report['pass'] else 1)
