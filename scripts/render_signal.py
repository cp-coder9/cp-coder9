#!/usr/bin/env python3
"""Draw a public GitHub profile signal card, without third-party badge services."""
import json
import os
import random
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
    w, h = 1200, 300
    im = Image.new('RGB', (w, h), '#15171c')
    d = ImageDraw.Draw(im)
    rng = random.Random(9127)
    # Rough brick, distressed painted layers and ink spatters; deterministic so
    # an unchanged snapshot does not create a meaningless daily commit.
    for y in range(0, h, 65):
        d.line((0, y, w, y), fill='#292a31', width=3)
        for x in range(-150 + (y // 65 % 2) * 140, w, 280):
            d.line((x, y, x, y+65), fill='#292a31', width=3)
    for _ in range(1600):
        x, y = rng.randrange(w), rng.randrange(h)
        color = rng.choice(('#202128', '#20232a', '#26272d', '#303038'))
        d.line((x, y, x + rng.randint(1, 15), y + rng.choice((0, 0, 1))), fill=color, width=1)
    paints = ('#fc4086', '#baff37', '#37dddf', '#ff9852')
    for _ in range(280):
        x, y = rng.randrange(w), rng.randrange(h)
        radius = rng.choices((1,2,3,5,8,13), (20,16,9,6,3,1))[0]
        d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=rng.choice(paints))
    d.polygon([(38,47),(396,25),(390,244),(42,268)], fill='#e42d75', outline='#0c0d10', width=7)
    d.polygon([(51,60),(370,41),(374,218),(47,245)], fill='#1b2025')
    d.text((73,61), 'THE', fill='#37dddf', stroke_width=2, stroke_fill='#08090a', font=font(37, True))
    d.text((69,104), 'SIGNAL', fill='#c2fa3c', stroke_width=3, stroke_fill='#08090a', font=font(59, True))
    d.text((73,190), 'PUBLIC / DAILY', fill='#f4f0dd', font=font(19, True))
    for i, (value, label) in enumerate(numbers):
        x = 415 + i * 250
        color = paints[i]
        d.polygon([(x+4,60),(x+213,49),(x+221,225),(x,235)], fill='#090b0f', outline=color, width=5)
        d.text((x+20,65), str(value), fill=color, stroke_width=2, stroke_fill='#050607', font=font(75, True))
        d.text((x+21,181), label, fill='#f1f0e9', font=font(16, True))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix('.tmp.png')
    im.save(tmp, format='PNG', optimize=True)
    tmp.replace(OUT)
    print('Rendered public GitHub signal:', ', '.join(f'{label}={value}' for value, label in numbers))


if __name__ == '__main__':
    main()
