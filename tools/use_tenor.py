#!/usr/bin/env python3
"""Build the banner directly from the original Steam black-hole GIF
(~/Desktop/tenor.gif) — no procedural recreation. Frames are cropped to
banner shape, upscaled, given a mild left darkening for text legibility,
and re-encoded as animated WebP with the GIF's own per-frame timing.

  python3 use_tenor.py --test     # single composed frame preview
  python3 use_tenor.py            # full banner -> assets/header.webp
"""
import argparse, os, sys, subprocess, glob
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from blackhole import build_overlay
from PIL import Image

SRC = "/home/Asttr0/Desktop/tenor.gif"
SCRATCH = "/tmp/claude-1000/-home-Asttr0/43a44ef5-16be-4a71-8ba3-baf770331005/scratchpad"
OUT = "/home/Asttr0/github-profile/assets/header.webp"
W, H = 840, 280
CROP_Y0 = 24            # source band: y0 .. y0 + W_src*(H/W)
F32 = np.float32

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1); return t * t * (3 - 2 * t)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    a = ap.parse_args()

    # coalesced frames via ffmpeg (handles GIF disposal correctly)
    fdir = SCRATCH + "/tenor_frames"
    os.makedirs(fdir, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", SRC, "-vsync", "0",
                    fdir + "/t%02d.png"], check=True)
    paths = sorted(glob.glob(fdir + "/t*.png"))

    # per-frame durations from the GIF itself
    g = Image.open(SRC)
    durs = []
    for i in range(g.n_frames):
        g.seek(i); durs.append(g.info.get("duration", 30))
    assert len(paths) == len(durs), (len(paths), len(durs))

    sw, sh = Image.open(paths[0]).size
    band_h = round(sw * H / W)                       # source band height
    y0 = min(CROP_Y0, sh - band_h)

    ov = build_overlay(W, H)
    xs = (np.arange(W) / W).astype(F32)
    leftdark = (smoothstep(0.03, 0.48, xs)[None, :, None] * 0.52 + 0.48)

    frames = []
    for p in paths:
        im = Image.open(p).convert("RGB").crop((0, y0, sw, y0 + band_h))
        im = im.resize((W, H), Image.LANCZOS)
        arr = np.asarray(im, F32) * leftdark
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
        frames.append(Image.alpha_composite(im, ov).convert("RGB"))

    if a.test:
        frames[0].save(SCRATCH + "/tenor_test.png")
        print("wrote tenor_test.png"); return

    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=durs, loop=0, quality=90, method=6)
    print(f"wrote {OUT} ({os.path.getsize(OUT)//1024} KB, "
          f"{len(frames)} frames, {sum(durs)/1000:.2f}s loop)")

if __name__ == "__main__":
    main()
