"""Build committed Bansko elevation assets from AWS Terrarium (no runtime API)."""
import argparse
import array
from concurrent.futures import ThreadPoolExecutor
import io
import json
import math
from pathlib import Path
import sys
import requests
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'app/static/experience/terrain'
BBOX = [23.38, 41.75, 23.51, 41.85]
ATTRIBUTION = ('Terrain: Mapzen / AWS Terrain Tiles. Produced using Copernicus data and '
               'information funded by the European Union - EU-DEM layers. Global SRTM '
               'and GMTED2010 courtesy of the U.S. Geological Survey. Elevations resampled. '
               'https://github.com/tilezen/joerd/blob/master/docs/attribution.md')

def tile(lon, lat, z=12):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n

def build(fallback=False):
    OUT.mkdir(parents=True, exist_ok=True)
    west, south, east, north = BBOX
    x0, y0 = tile(west, north)
    x1, y1 = tile(east, south)
    coords = [(x, y) for y in range(int(y0), int(y1) + 1) for x in range(int(x0), int(x1) + 1)]
    def fetch(coord):
        x, y = coord
        url = f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/12/{x}/{y}.png'
        response = requests.get(url, timeout=35)
        response.raise_for_status()
        print(f'{url}: {len(response.content)} bytes', flush=True)
        return x, y, Image.open(io.BytesIO(response.content)).convert('RGB')
    source = 'AWS Open Data Terrain Tiles / Terrarium, zoom 12'
    try:
        if fallback:
            raise RuntimeError('Explicit offline fallback')
        mosaic = Image.new('F', ((int(x1) - int(x0) + 1) * 256, (int(y1) - int(y0) + 1) * 256))
        with ThreadPoolExecutor(max_workers=6) as pool:
            for x, y, image in pool.map(fetch, coords):
                decoded = Image.new('F', (256, 256))
                decoded.putdata([r * 256 + g + b / 256 - 32768 for r, g, b in image.getdata()])
                mosaic.paste(decoded, ((x - int(x0)) * 256, (y - int(y0)) * 256))
        # Decode before resampling; RGB interpolation would corrupt Terrarium carries.
        height = mosaic.transform((512, 512), Image.Transform.EXTENT,
            ((x0 % 1) * 256, (y0 % 1) * 256, (x1 - int(x0)) * 256, (y1 - int(y0)) * 256), Image.Resampling.BILINEAR)
    except (requests.RequestException, RuntimeError) as exc:
        print(f'FETCH IMPOSSIBLE: {exc}; procedural fallback', flush=True)
        source = 'procedural fallback'
        height = Image.new('F', (512, 512))
        height.putdata([900 + 1800 * (1 - y/511) * (.65 + .35 * math.sin(x/65 + y/95)**2) for y in range(512) for x in range(512)])
    values = list(height.getdata())
    if source != 'procedural fallback':
        assert 750 < min(values) < 1250 and 2700 < max(values) < 3100, (min(values), max(values))
    for size in (512, 256):
        pixels = array.array('H', (max(0, round(v)) for v in height.resize((size, size), Image.Resampling.BILINEAR).getdata()))
        if sys.byteorder != 'little':
            pixels.byteswap()
        (OUT / ('bansko-height.bin' if size == 512 else 'bansko-height-256.bin')).write_bytes(pixels.tobytes())
    metadata = dict(width=512, height=512, minM=round(min(values)), maxM=round(max(values)), bbox=BBOX,
        metresPerPixelX=(east-west)*111320*math.cos(math.radians((north+south)/2))/511,
        metresPerPixelY=(north-south)*111320/511, source=source, attribution=ATTRIBUTION)
    (OUT / 'bansko-height.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    preview = Image.new('L', (512, 512))
    def sample(x, y): return values[max(0, min(511, y))*512 + max(0, min(511, x))]
    preview.putdata([int(max(0, min(255, 150 + (sample(x-1,y)-sample(x+1,y)) * 2 + (sample(x,y-1)-sample(x,y+1))))) for y in range(512) for x in range(512)])
    preview.filter(ImageFilter.GaussianBlur(.4)).save(OUT / 'preview.png')
    print(json.dumps(metadata, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline-fallback', action='store_true')
    build(parser.parse_args().offline_fallback)
