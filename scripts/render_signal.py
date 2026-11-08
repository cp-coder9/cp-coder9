#!/usr/bin/env python3
"""Draw a public GitHub profile signal card, without third-party badge services."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'signal.png'


def font(size, bold=False):
    candidates = ([r'C:\Windows\Fonts\arialbd.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if bold else
                  [r'C:\Windows\Fonts\consola.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'])
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def main():
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'cp-coder9-profile-signal'}
    token = os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    with urlopen(Request('https://api.github.com/users/cp-coder9', headers=headers), timeout=30) as response:
        data = json.load(response)
    numbers = [(data['public_repos'], 'PUBLIC REPOS'), (data['followers'], 'FOLLOWERS'), (data['following'], 'FOLLOWING')]
    w, h = 1200, 260
    im = Image.new('RGB', (w, h), '#101218')
    d = ImageDraw.Draw(im)
    # A deliberately restrained poster-strip: typography remains legible at mobile width.
    d.rounded_rectangle((2, 2, w-3, h-3), radius=15, fill='#101218', outline='#3a3b46', width=3)
    d.polygon([(0, 0), (15, 0), (115, h), (100, h)], fill='#d5ff39')
    d.line((128, 29, 128, h-29), fill='#ff4778', width=4)
    d.text((156, 39), 'THE SIGNAL', fill='#f3f3ec', font=font(38, True))
    d.text((158, 101), 'PUBLIC / GITHUB', fill='#66d7d5', font=font(18))
    d.text((158, 139), 'PUBLIC COUNTS', fill='#b9bdc6', font=font(17))
    d.text((158, 166), 'REFRESHED DAILY', fill='#b9bdc6', font=font(17))
    d.line((440, 40, 440, 220), fill='#3a3b46', width=2)
    for i, (value, label) in enumerate(numbers):
        x = 480 + i * 235
        d.text((x+3, 52), str(value), fill=('#d5ff39', '#ff648b', '#75e8df')[i], font=font(70, True))
        d.text((x+3, 163), label, fill='#d6d8de', font=font(16))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix('.tmp.png')
    im.save(tmp, format='PNG', optimize=True)
    tmp.replace(OUT)
    print('Rendered public GitHub signal:', ', '.join(f'{label}={value}' for value, label in numbers))


if __name__ == '__main__':
    main()
