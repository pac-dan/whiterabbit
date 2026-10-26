"""Deterministic branded media slots, never production footage."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'app/static/experience/placeholders'

def create(name, size):
    w, h = size
    rng = random.Random(name)
    im = Image.new('RGB', size)
    px = im.load()
    for y in range(h):
        for x in range(w):
            t = y / h
            n = rng.randrange(0, 5)
            glow = max(0, 1 - abs(x/w - .5) * 2) * max(0, 1 - abs(t - .5) * 2)
            px[x, y] = (int(6+14*t+24*glow)+n, int(15+10*t+28*glow)+n, int(30+25*t+46*glow)+n)
    d = ImageDraw.Draw(im)
    for y in range(18, h-18):
        c = (int(139*y/h), int(212*(1-y/h)+92*y/h), 246)
        d.line((18,y,21,y),fill=c); d.line((w-22,y,w-19,y),fill=c)
    d.line((18,18,w-19,18), fill='#00d4ff',width=3)
    d.line((18,h-19,w-19,h-19), fill='#8b5cf6',width=3)
    # Abstract ridge / snowboard silhouette is deliberately understated.
    d.polygon([(0,h*.75),(w*.25,h*.48),(w*.45,h*.65),(w*.73,h*.37),(w,h*.64),(w,h),(0,h)],fill='#1a2b45')
    cx, cy = w*.52, h*.59
    d.ellipse((cx-14,cy-80,cx+14,cy-52),fill='#71849a')
    d.line([(cx,cy-51),(cx-16,cy-8),(cx+19,cy+27)],fill='#71849a',width=19)
    d.line([(cx-10,cy-30),(cx-44,cy-14)],fill='#71849a',width=11)
    d.line([(cx-18,cy-7),(cx-45,cy+29)],fill='#71849a',width=14)
    d.line([(cx-70,cy+38),(cx+48,cy+32)],fill='#00a0bb',width=10)
    font_path = Path('C:/Windows/Fonts/arial.ttf')
    font = ImageFont.truetype(str(font_path), round(w*.045)) if font_path.exists() else ImageFont.load_default()
    small = ImageFont.truetype(str(font_path), round(w*.022)) if font_path.exists() else font
    d.text((w*.08,h*.08),'M / C',font=font,fill='#d7f4ff')
    d.text((w*.08,h*.84),name.upper(),font=font,fill='#ecf6ff')
    d.text((w*.08,h*.9),'YOUR FOOTAGE GOES HERE',font=small,fill='#a3b7cc')
    path = OUT / f'{name.lower().replace(" ", "-")}.webp'
    im.save(path, quality=73, method=6)
    print(f'{path.relative_to(ROOT)}: {path.stat().st_size} bytes')

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for i in range(1,13): create(f'ring {i:02}', (720,1280))
    for i in range(1,4):
        create(f'gate {i}', (1200,1600))
        create(f'beat {i}', (720,1280))
    create('portal', (1200,1600))
