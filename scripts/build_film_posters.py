"""Extract honest portrait moments directly from the owner's original film."""
import hashlib
import json
import subprocess
from pathlib import Path
from build_journey_video import DEFAULT, ROOT, RUN

ffmpeg = next((RUN / 'tools/imageio_ffmpeg/binaries').glob('*.exe'))
folder = ROOT / 'app/static/experience/media/moments'
folder.mkdir(exist_ok=True)
source_hash = hashlib.sha256(DEFAULT.read_bytes()).hexdigest()
report = {'source': str(DEFAULT), 'source_sha256': source_hash, 'frames': []}
# Crop follows the source rider, then the warm town composition. No upscaling.
for i, (time, center) in enumerate([(0.5, .53), (2.4, .56), (4.7, .51), (6.9, .53), (8.7, .58)]):
    target = folder / f'moment-{i+1}.webp'
    x = round(1280*center-240)
    command = [str(ffmpeg), '-hide_banner', '-loglevel', 'error', '-y', '-ss', str(time),
               '-i', str(DEFAULT), '-frames:v', '1', '-vf', f'crop=480:720:{x}:0',
               '-c:v', 'libwebp', '-quality', '88', str(target)]
    subprocess.run(command, check=True)
    report['frames'].append({'time': time, 'crop_x': x, 'file': str(target),
                             'bytes': target.stat().st_size, 'command': command})
report['pass'] = source_hash == hashlib.sha256(DEFAULT.read_bytes()).hexdigest()
out = ROOT / '.runs/2026-10-26-gallery-motion/evidence'
out.mkdir(parents=True, exist_ok=True)
(out / 'posters.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
