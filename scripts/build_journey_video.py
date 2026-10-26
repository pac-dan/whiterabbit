"""One-time silent scroll-seek derivative. Requires ffmpeg, never edits the input.

Set FFMPEG to a binary path; --source overrides the owner's original file.
No encoder or Node build is required on Vercel.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / '.runs/2026-10-26-video-journey'
MEDIA = ROOT / 'app/static/experience/media'
DEFAULT = Path('C:/Users/Dan/dan_file/higgs/davinci_create_a_photorealistic__approximately_9sec.mp4')


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    binary = os.getenv('FFMPEG') or shutil.which('ffmpeg')
    if not binary:
        binary = next((RUN / 'tools/imageio_ffmpeg/binaries').glob('*.exe'), None)
    if not binary:
        raise SystemExit('Set FFMPEG to an ffmpeg binary; not needed at runtime.')
    source_hash = hashlib.sha256(args.source.read_bytes()).hexdigest()
    output = MEDIA / 'bansko-journey-v2.mp4'
    base = [str(binary), '-hide_banner', '-loglevel', 'error', '-y']
    commands = []
    if not args.verify:
        MEDIA.mkdir(parents=True, exist_ok=True)
        commands.append(base + ['-i', str(args.source), '-map', '0:v:0', '-an', '-c:v', 'libx264',
                               '-preset', 'slow', '-crf', '25', '-maxrate', '3200k', '-bufsize', '3200k', '-pix_fmt', 'yuv420p',
                               '-g', '6', '-keyint_min', '6', '-sc_threshold', '0', '-bf', '0',
                               '-movflags', '+faststart', str(output)])
        for name, time in [('bansko-journey-poster.webp', '0'), ('bansko-town-poster.webp', '8.95')]:
            commands.append(base + ['-ss', time, '-i', str(args.source), '-frames:v', '1',
                                    '-c:v', 'libwebp', '-quality', '85', str(MEDIA / name)])
        for command in commands:
            subprocess.run(command, check=True)
    assert source_hash == hashlib.sha256(args.source.read_bytes()).hexdigest()
    info = subprocess.run([str(binary), '-hide_banner', '-i', str(output)], capture_output=True, text=True).stderr
    assert 'Audio:' not in info
    assert '1280x720' in info and '24 fps' in info and 'h264' in info
    raw = output.read_bytes()
    assert len(raw) < 4_000_000, 'Keep the whole movie below the Flask/Vercel response budget'
    assert raw.index(b'moov') < raw.index(b'mdat'), 'fast-start moov must precede media'
    frames = subprocess.run([str(binary), '-hide_banner', '-i', str(output), '-vf', 'showinfo',
                             '-f', 'null', '-'], capture_output=True, text=True, check=True).stderr
    keys = [int(x) for x in re.findall(r'n:\s*(\d+).*?iskey:1', frames)]
    assert len(keys) >= 35 and max(b-a for a,b in zip(keys,keys[1:])) <= 6
    report = dict(pass_=True, source_sha256=source_hash, source_bytes=args.source.stat().st_size,
                  derivative_bytes=len(raw), encoding=info, keyframes=keys,
                  max_keyframe_interval_frames=6, fast_start=True, audio=False,
                  files={p.name:p.stat().st_size for p in MEDIA.glob('bansko-*')}, commands=commands)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
