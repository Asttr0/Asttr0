#!/usr/bin/env python3
"""Dark 'gravity vortex' black-hole banner — spiral light-streaks winding into a
black void. A fixed logarithmic-spiral streak texture is rotated a full 360° over
the loop, so the animation is perfectly seamless (frame N == frame 0). Rendering a
rotated texture is cheap, so we can afford high resolution and many frames.

  python3 vortex.py --test
  python3 vortex.py --frames 72 --out DIR
"""
import argparse, os, sys, math, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from blackhole import blur, build_overlay          # reuse bloom + text overlay
from PIL import Image

SCRATCH="/tmp/claude-1000/-home-Asttr0/43a44ef5-16be-4a71-8ba3-baf770331005/scratchpad"
F32=np.float32

def smoothstep(a,b,x):
    t=np.clip((x-a)/(b-a+1e-9),0,1); return t*t*(3-2*t)

def build_texture(S=1600, seed=3, tint=(0.82,0.88,1.0)):
    rng=np.random.default_rng(seed)
    y,x=np.mgrid[0:S,0:S].astype(F32); c=S/2
    dx=x-c; dy=y-c; r=np.hypot(dx,dy)+1e-3; phi=np.arctan2(dy,dx)
    pitch=0.36                                   # spiral tightness
    psi=(phi - np.log(r)/pitch) % (2*np.pi)
    # fine angular streaks: periodic 1D noise sampled by spiral phase
    M=2400; base=rng.random(M).astype(F32)
    k=5; base=np.convolve(np.concatenate([base[-k:],base,base[:k]]),np.ones(k)/k,'same')[k:-k]
    base=base**3.6                               # strong bias to black -> sparse bright arms
    streak=base[((psi/(2*np.pi))*M).astype(int)%M]
    # break arms into wisps (periodic in psi -> no seam)
    turb=np.zeros_like(r)
    for _ in range(6):
        f=int(rng.integers(1,4)); rf=rng.uniform(1.5,5.5); p=rng.uniform(0,6.28)
        turb+=np.sin(f*psi+rf*np.log(r)+p)
    streak*= (0.10+0.90*np.clip(0.5+0.5*turb/6,0,1))
    # radial envelope: black void -> streak band -> fade to black
    rin=S*0.055
    env=smoothstep(rin,rin*2.4,r)*np.exp(-(r/(S*0.195))**2)
    b=streak*env
    b*= (1+1.6*np.exp(-((r-S*0.105)/(S*0.05))**2))   # matter piling near the horizon
    b=np.clip(b*1.35,0,6)
    img=b[...,None]*np.array(tint,F32)
    img=img+0.4*blur(np.clip(img-0.5,0,None), r=max(2,S//280), passes=3)
    return img

def tonemap(img):
    x=np.clip(img,0,None); x=x/(1+0.8*x)
    return (np.power(np.clip(x,0,1),1/2.05)*255+0.5).astype(np.uint8)

def make_stars(W,H,seed=9):
    rng=np.random.default_rng(seed); a=np.zeros((H,W,3),F32)+np.array([3,3,8],F32)
    for n,lo,hi in [(150,.1,.35),(30,.4,.9)]:
        px=rng.integers(0,W,n); py=rng.integers(0,H,n); b=rng.uniform(lo,hi,n)*90
        a[py,px]+=b[:,None]*np.array([.8,.85,1.0],F32)
    return a

def compose(tex, ang, S, W,H, vx,vy, stars, ov, leftdark):
    rot=np.asarray(Image.fromarray(tex).rotate(ang, resample=Image.BICUBIC,
                   center=(S/2,S/2), fillcolor=(0,0,0)), F32)
    base=stars.copy(); ox,oy=vx-S//2, vy-S//2
    dy0,dx0=max(0,oy),max(0,ox); dy1,dx1=min(H,oy+S),min(W,ox+S)
    base[dy0:dy1,dx0:dx1]+= rot[dy0-oy:dy1-oy, dx0-ox:dx1-ox]
    base*=leftdark                                   # keep the text side dark
    im=Image.fromarray(np.clip(base,0,255).astype(np.uint8)).convert("RGBA")
    return Image.alpha_composite(im, ov).convert("RGB")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--test",action="store_true"); ap.add_argument("--frames",type=int,default=0)
    ap.add_argument("--out",default=SCRATCH+"/vframes")
    ap.add_argument("--w",type=int,default=1000); ap.add_argument("--h",type=int,default=300)
    ap.add_argument("--s",type=int,default=1600); ap.add_argument("--vx",type=float,default=0.76)
    a=ap.parse_args()
    S=a.s; W,H=a.w,a.h; vx,vy=int(W*a.vx),int(H*0.5)
    print("fonts ok; building texture…", flush=True)
    from PIL import ImageFilter
    tex=tonemap(build_texture(S))
    tex=np.asarray(Image.fromarray(tex).filter(ImageFilter.GaussianBlur(1.1)))  # soften -> smaller + closer to ref
    stars=make_stars(W,H); ov=build_overlay(W,H)
    xs=(np.arange(W)/W).astype(F32)
    leftdark=smoothstep(0.02,0.52,xs)[None,:,None]*0.72+0.28   # dark left -> full right
    if a.test:
        compose(tex, 24.0, S, W,H, vx,vy, stars, ov, leftdark).save(SCRATCH+"/vortex_test.png")
        print("wrote vortex_test.png"); return
    os.makedirs(a.out,exist_ok=True); t0=time.time()
    for i in range(a.frames):
        compose(tex, 360.0*i/a.frames, S, W,H, vx,vy, stars, ov, leftdark).save(f"{a.out}/f{i:03d}.png")
    print(f"{a.frames} frames in {time.time()-t0:.1f}s", flush=True)

if __name__=="__main__":
    main()
