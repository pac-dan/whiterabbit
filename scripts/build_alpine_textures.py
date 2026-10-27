"""Small original surface assets; no third-party texture/code or runtime noise filter."""
import hashlib
import json
import random
import struct
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'app/static/experience/textures'
RUN = ROOT / '.runs/2026-10-27-texture-smoothness'
OUT.mkdir(parents=True, exist_ok=True)
rng = random.Random(271026)
grain = Image.new('RGBA', (128, 128))
grain.putdata([(230, 244, 255, rng.choice([0, 0, 0, 1, 2, 3, 5])) for _ in range(128**2)])
grain.save(OUT / 'alpine-grain.png', optimize=True)

# Marching squares over the already committed, attributed Bansko elevation.
source = ROOT / 'app/static/experience/terrain/bansko-height-256.bin'
heights = struct.unpack('<65536H', source.read_bytes())
size, step = 768, 4
contours = Image.new('RGBA', (size, size))
draw = ImageDraw.Draw(contours)
segments = 0
for level in range(900, 2901, 100):
    for y in range(0, 252, step):
        for x in range(0, 252, step):
            corners = [(x,y),(x+step,y),(x+step,y+step),(x,y+step)]
            crosses = []
            for a,b in zip(corners, corners[1:]+corners[:1]):
                va,vb = heights[a[1]*256+a[0]],heights[b[1]*256+b[0]]
                if (va < level) != (vb < level):
                    t = (level-va)/(vb-va)
                    crosses.append(((a[0]+t*(b[0]-a[0]))*3, (a[1]+t*(b[1]-a[1]))*3))
            for i in range(0,len(crosses)-1,2):
                draw.line([crosses[i],crosses[i+1]], fill=(122,196,219,95 if level%500==0 else 52),width=2 if level%500==0 else 1)
                segments += 1
contours.save(OUT / 'bansko-contours.webp', lossless=True)
meta = json.loads((source.parent / 'bansko-height.json').read_text())
report = {'pass': True, 'seed': 271026, 'contour_segments': segments,
          'terrain_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'attribution': meta['attribution'], 'files': []}
for p in sorted(OUT.glob('*')):
    if p.suffix in ('.png','.webp'):
        with Image.open(p) as im:
            report['files'].append({'path':str(p),'bytes':p.stat().st_size,'size':im.size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert sum(x['bytes'] for x in report['files']) < 100000
(RUN / 'evidence').mkdir(parents=True, exist_ok=True)
(RUN / 'evidence/textures.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
