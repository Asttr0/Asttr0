#!/usr/bin/env python3
"""Black & white 'ink vortex' banner — thin hand-drawn-looking white streak lines
winding into a big off-center void, in the style of the classic Steam black-hole
artwork. Pure B&W, sparse, high contrast.

Seamless loop: a fixed log-spiral streak texture is rotated a full 360° over the
loop (frame N == frame 0). Texture is built at 2x and downscaled after rotation
for crisp anti-aliased lines.

  python3 inkvortex.py --test
  python3 inkvortex.py --frames 160 --start 0 --stride 1 --out DIR
"""
import argparse, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from blackhole import build_overlay          # reuse the text overlay
from PIL import Image

SCRATCH = "/tmp/claude-1000/-home-Asttr0/43a44ef5-16be-4a71-8ba3-baf770331005/scratchpad"
F32 = np.float32

def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1); return t * t * (3 - 2 * t)

def build_ink_texture(S=3200, seed=7):
    """Sparse thin spiral streaks: 1D profile of narrow gaussian spikes sampled
    by log-spiral phase, broken into segments by periodic turbulence."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:S, 0:S].astype(F32); c = S / 2
    dx = x - c; dy = y - c
    r = np.hypot(dx, dy) + 1e-3
    phi = np.arctan2(dy, dx)
    pitch = 0.30                                    # spiral tightness (lower = tighter wind)
    psi = (phi - np.log(r) / pitch) % (2 * np.pi)

    # --- 1D angular profile: sparse narrow spikes -> thin distinct lines ---
    M = 6000
    prof = np.zeros(M, F32)
    n_lines = 270
    pos = rng.uniform(0, M, n_lines)
    amp = rng.uniform(0.16, 1.25, n_lines) ** 2.2   # mostly faint, a few bright
    sig = rng.uniform(0.85, 1.7, n_lines)           # line thickness in samples
    idx = np.arange(M, dtype=F32)
    for p, a, s in zip(pos, amp, sig):
        d = np.abs(idx - p); d = np.minimum(d, M - d)          # periodic distance
        prof += a * np.exp(-(d / s) ** 2)
    # sample profile with linear interpolation (smooth AA lines)
    fpos = (psi / (2 * np.pi)) * M
    i0 = fpos.astype(np.int64) % M; f = fpos - np.floor(fpos)
    streak = prof[i0] * (1 - f) + prof[(i0 + 1) % M] * f

    # --- break lines into short star-trail dashes (periodic in psi -> no seam) ---
    turb = np.zeros_like(r)
    for _ in range(8):
        fq = int(rng.integers(3, 14)); rf = rng.uniform(6.0, 20.0); ph = rng.uniform(0, 6.28)
        turb += np.sin(fq * psi + rf * np.log(r) + ph)
    seg = np.clip(0.5 + 0.5 * turb / 8 * 4.0, 0, 1) ** 2.8     # hard gaps -> short dashes
    streak *= (0.02 + 0.98 * seg)

    # --- radial envelope: big black void -> streak band -> fade out ---
    rin = S * 0.085                                  # void (eye) radius
    env = smoothstep(rin, rin * 1.5, r) * np.exp(-(r / (S * 0.335)) ** 2.6)
    b = streak * env
    b *= (1 + 0.45 * np.exp(-((r - rin * 1.7) / (S * 0.05)) ** 2))   # rim pile-up
    return np.clip(b * 4.6, 0, 2.0)

def make_stars(W, H, seed=9):
    rng = np.random.default_rng(seed)
    a = np.zeros((H, W, 3), F32) + 2.0               # near-pure black
    for n, lo, hi in [(90, .08, .28), (18, .3, .7)]:
        px = rng.integers(0, W, n); py = rng.integers(0, H, n)
        b = rng.uniform(lo, hi, n) * 80
        a[py, px] += b[:, None]
    return a

def compose(tex_img, ang, W, H, vx, vy, squash, stars, ov, leftdark):
    S2 = tex_img.size[0]
    rot = tex_img.rotate(ang, resample=Image.BICUBIC, fillcolor=0)
    # squash to ellipse + 2x downscale in one resize (good AA on thin lines)
    Sw = S2 // 2; Sh = int(S2 * squash) // 2
    rot = rot.resize((Sw, Sh), Image.LANCZOS)
    rot = np.asarray(rot, F32)
    base = stars.copy()
    ox, oy = vx - Sw // 2, vy - Sh // 2
    dy0, dx0 = max(0, oy), max(0, ox); dy1, dx1 = min(H, oy + Sh), min(W, ox + Sw)
    base[dy0:dy1, dx0:dx1] += rot[dy0 - oy:dy1 - oy, dx0 - ox:dx1 - ox, None] * np.array([1.0, 1.0, 1.0], F32)
    base *= leftdark
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
    return Image.alpha_composite(im, ov).convert("RGB")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--frames", type=int, default=0)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--out", default=SCRATCH + "/ivframes")
    ap.add_argument("--w", type=int, default=1000); ap.add_argument("--h", type=int, default=300)
    ap.add_argument("--s", type=int, default=3200)
    ap.add_argument("--vx", type=float, default=0.72)
    ap.add_argument("--vy", type=float, default=0.40)
    ap.add_argument("--squash", type=float, default=0.50)
    a = ap.parse_args()
    W, H = a.w, a.h; vx, vy = int(W * a.vx), int(H * a.vy)
    print("building ink texture…", flush=True)
    tex = build_ink_texture(a.s)
    # tone map to 8-bit once; rotation happens on the uint8 image (cheap)
    t = np.power(np.clip(tex / (1 + 0.55 * tex), 0, 1), 1 / 1.9)
    t[t < 0.055] = 0                                  # kill speckle dust (webp bitrate)
    t8 = (t * 255 + 0.5).astype(np.uint8)
    from PIL import ImageFilter
    tex_img = Image.fromarray(t8, "L").filter(ImageFilter.GaussianBlur(0.5))
    stars = make_stars(W, H); ov = build_overlay(W, H)
    xs = (np.arange(W) / W).astype(F32)
    leftdark = smoothstep(0.02, 0.50, xs)[None, :, None] * 0.75 + 0.25
    if a.test:
        compose(tex_img, 24.0, W, H, vx, vy, a.squash, stars, ov, leftdark).save(SCRATCH + "/ink_test.png")
        print("wrote ink_test.png"); return
    os.makedirs(a.out, exist_ok=True); t0 = time.time()
    n = 0
    for i in range(a.start, a.frames, a.stride):
        compose(tex_img, 360.0 * i / a.frames, W, H, vx, vy, a.squash, stars, ov, leftdark).save(f"{a.out}/f{i:03d}.png")
        n += 1
    print(f"{n} frames in {time.time() - t0:.1f}s", flush=True)

if __name__ == "__main__":
    main()
