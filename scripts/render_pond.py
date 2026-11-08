#!/usr/bin/env python3
"""Composite the activity-generated transparent koi over a looping pond."""
from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'koi' / 'koi.gif'
DEST = ROOT / 'koi' / 'pond.gif'


def noise(seed, size, scale):
    rng = np.random.default_rng(seed)
    small = rng.integers(0, 256, (scale, scale), dtype=np.uint8)
    im = Image.fromarray(small).resize((size, size), Image.Resampling.BICUBIC)
    return np.asarray(im.filter(ImageFilter.GaussianBlur(size / scale / 3)), dtype=np.float32) / 255


def main():
    src = Image.open(SOURCE)
    width, height = src.size
    if width != height:
        raise ValueError('Expected a square koi animation')
    n = src.n_frames
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    u, v = x / width, y / height
    broad = noise(12, width, 8)
    fine = noise(73, width, 37)
    depth = np.clip(.52 + .35 * (v - .5) + .28 * (broad - .5), 0, 1)
    vignette = np.clip(1 - .45 * ((u - .5)**2 + (v - .5)**2), .7, 1)
    # Submerged stones, softened by depth and water, stay behind the fish.
    stones = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(stones)
    rng = np.random.default_rng(230)
    for _ in range(65):
        cx, cy = rng.integers(-25, width + 25, 2)
        rx, ry = rng.integers(7, 33), rng.integers(5, 23)
        draw.ellipse((int(cx-rx), int(cy-ry), int(cx+rx), int(cy+ry)), fill=int(rng.integers(12, 48)))
    stones = np.asarray(stones.filter(ImageFilter.GaussianBlur(5)), dtype=np.float32) / 255
    source_durations = []
    for i in range(n):
        src.seek(i)
        source_durations.append(src.info.get('duration', 70))
    frames, durations = [], []
    # Keep the source loop's timing but use every other frame to keep the
    # profile image small and friendly to browsers and GitHub's image proxy.
    for i in range(0, n, 2):
        src.seek(i)
        fish = src.convert('RGBA')
        durations.append(sum(source_durations[i:i+2]))
        t = 2 * math.pi * i / n
        # A periodic water surface: layered, warped wave normals and caustic ridges.
        warp = .7 * np.sin(8*u + 5*v + math.sin(t)) + .4 * (broad - .5)
        a = 19*u + 13*v + warp + 1.2*math.sin(t)
        b = 14*u - 22*v + 1.3*np.sin(5*v + 2*u) + 1.1*math.cos(t)
        c = 32*u + 7*v + .9*np.sin(7*v + math.sin(t)) - .7*math.sin(t)
        waves = .52*np.sin(a) + .30*np.sin(b) + .18*np.sin(c)
        glints = np.clip((np.sin(a)*.55 + np.sin(b)*.45 - .64) / .36, 0, 1)**2
        reflection = np.clip(.45 + .55*np.sin(4*u - 3*v + .3*math.sin(t)), 0, 1) * np.clip(1.25 - 1.3*v, 0, 1)
        box = fish.getchannel('A').getbbox()
        cx, cy = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2) if box else (width/2, height/2)
        distance = np.sqrt(((x-cx)*.85)**2 + ((y-cy)*1.15)**2)
        fish_ripples = np.sin(distance*.135 - t*2) * np.exp(-((distance-115)/85)**2)
        light = 9.0*waves + 22*glints + 9*reflection + 4*(fine-.5) + 4*fish_ripples
        r = (12 + 11*depth + light*.48 + 15*stones) * vignette
        g = (42 + 23*depth + light*.95 + 17*stones) * vignette
        bcol = (43 + 23*depth + light*1.10 + 12*stones) * vignette
        rgb = np.uint8(np.clip(np.stack((r,g,bcol), axis=-1), 0, 255))
        # Render above the 512px profile display size. Soften the original
        # pixel-art sprite before resampling so its hard square pixels don't
        # dominate the pond; interpolation cannot invent photographic detail.
        output_size = (768, 768)
        pond = Image.fromarray(rgb, 'RGB').resize(output_size, Image.Resampling.LANCZOS).convert('RGBA')
        fish = fish.filter(ImageFilter.GaussianBlur(.6)).resize(output_size, Image.Resampling.LANCZOS)
        # A faint diffuse shadow gives the fish contact with the water.
        alpha = fish.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda p: int(p * .23))
        shadow = Image.new('RGBA', fish.size, (0, 14, 18, 0))
        shadow.putalpha(alpha)
        pond.alpha_composite(shadow, (6, 10))
        pond.alpha_composite(fish)
        frames.append(pond.convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    DEST.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(DEST, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=False, disposal=2)
    print(f'Wrote {DEST}: {output_size[0]}x{output_size[1]}, {len(frames)} frames, {DEST.stat().st_size} bytes')


if __name__ == '__main__':
    main()
