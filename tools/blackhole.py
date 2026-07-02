#!/usr/bin/env python3
"""Physically-based Schwarzschild black-hole banner renderer — "art" pass.

Backward ray-tracing of photon geodesics (d²u/dφ² + u = 3Mu², u=1/r, M=Rs/2).
Rays fall past the horizon (shadow), cross the accretion disk (emission with
Keplerian Doppler beaming + relativistic blue/red shift + temperature ramp), or
escape to a lensed multi-colour starfield. A photon ring is traced around the
silhouette in post, plus bloom, a cinematic vignette and a saturation grade.

Optimizations: float32, active-ray compaction, SSAA. Seamless loop.
"""
import argparse, os, math, time
import numpy as np

SCRATCH = "/tmp/claude-1000/-home-Asttr0/43a44ef5-16be-4a71-8ba3-baf770331005/scratchpad"
F32 = np.float32

def _ramp(stops):
    xs = np.array([s[0] for s in stops], F32); cs = np.array([s[1] for s in stops], F32)
    def f(t):
        t = np.clip(t, 0, 1); out = np.empty(t.shape + (3,), F32)
        for k in range(3): out[..., k] = np.interp(t, xs, cs[:, k])
        return out
    return f

DISK = _ramp([
    (0.00, (255, 255, 255)), (0.12, (198, 236, 255)), (0.30, (120, 176, 255)),
    (0.52, (176, 118, 255)), (0.72, (240,  92, 214)), (1.00, (255, 140,  58)),
])

# ---------------------------------------------------------------- star map
def build_starmap(SW=2600, SH=1300, seed=7):
    rng = np.random.default_rng(seed)
    img = np.zeros((SH, SW, 3), F32)
    yy, xx = np.mgrid[0:SH, 0:SW]
    # a few subtle, cooler nebula wisps — dark space between them so the hole leads
    spots = [(.68,.34,(.10,.17,.44)), (.88,.68,(.05,.26,.40)),
             (.56,.66,(.26,.10,.40)), (.78,.52,(.08,.13,.34))]
    for fx, fy, colc in spots:
        cx = SW*fx*rng.uniform(.98,1.02); cy = SH*fy*rng.uniform(.96,1.04)
        rad = SW*rng.uniform(.05,.10)
        col = np.array(colc, F32)*rng.uniform(.8,1.15)
        g = (np.exp(-(((xx-cx)**2+(yy-cy)**2)/(2*rad**2)))**1.7).astype(F32)  # sharp -> black between
        img += g[..., None]*col
    img *= 0.17
    # crisp stars (mostly white-blue), boosted to survive SSAA down-averaging
    for n, lo, hi, bw in [(9000,.35,1.25,0.0),(2600,1.1,2.7,0.22),(470,2.7,5.8,0.45)]:
        px = rng.integers(0, SW, n); py = rng.integers(0, SH, n)
        b = rng.uniform(lo, hi, n).astype(F32)
        tint = rng.uniform(.85,1.0,(n,3)).astype(F32); tint[:,2]=np.clip(tint[:,2]+.06,0,1)
        warm = rng.random(n) < 0.12                       # a few warm stars
        tint[warm] = tint[warm]*np.array([1.0,.8,.6],F32)
        img[py, px] += b[:, None]*tint
        if bw:
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                img[np.clip(py+dy,0,SH-1),np.clip(px+dx,0,SW-1)] += b[:,None]*tint*bw
    return np.clip(img, 0, 7).astype(F32)

def sample_stars(smap, dirs, roll):
    SH, SW, _ = smap.shape
    u = (0.5 + (np.arctan2(dirs[...,2], dirs[...,0]) + roll)/(2*math.pi)) % 1.0
    v = 0.5 - np.arcsin(np.clip(dirs[...,1],-1,1))/math.pi
    return smap[np.clip((v*SH).astype(np.int32),0,SH-1), np.clip((u*SW).astype(np.int32),0,SW-1)]

# ---------------------------------------------------------------- blur
def _box1d(a, r, ax):
    n = a.shape[ax]; pad=[(0,0)]*a.ndim; pad[ax]=(r+1,r)
    c = np.cumsum(np.pad(a, pad, mode='edge'), axis=ax)
    hi=[slice(None)]*a.ndim; lo=[slice(None)]*a.ndim
    hi[ax]=slice(2*r+1,2*r+1+n); lo[ax]=slice(0,n)
    return (c[tuple(hi)]-c[tuple(lo)])/(2*r+1)
def blur(a, r, passes=3):
    for _ in range(passes): a=_box1d(a,r,0); a=_box1d(a,r,1)
    return a

# ---------------------------------------------------------------- render
def render_scene(Wh, Hh, frac, smap, xoff):
    Rs=1.0; M=0.5; Rin,Rout=3.0,12.0; R_esc=60.0
    incl=math.radians(81.5); D=26.0; elev=math.pi/2-incl
    Cpos=np.array([0.,D*math.sin(elev),-D*math.cos(elev)],F32)
    fwd=-Cpos/np.linalg.norm(Cpos)
    right=np.cross(fwd,[0,1.,0]).astype(F32); right/=np.linalg.norm(right)
    up=np.cross(right,fwd).astype(F32); up/=np.linalg.norm(up)
    fov=math.radians(33.0); hh=math.tan(fov/2); asp=Wh/Hh
    gx,gy=np.meshgrid(((np.arange(Wh)+.5)/Wh*2-1).astype(F32),((np.arange(Hh)+.5)/Hh*2-1).astype(F32))
    d=fwd[None,None]+((gx+xoff)*asp*hh)[...,None]*right+(-gy*hh)[...,None]*up
    d/=np.linalg.norm(d,axis=-1,keepdims=True); d=d.reshape(-1,3).astype(F32); P=d.shape[0]
    e1=(Cpos/np.linalg.norm(Cpos)).astype(F32)
    nrm=np.cross(np.broadcast_to(Cpos,d.shape),d); nrm/=(np.linalg.norm(nrm,axis=-1,keepdims=True)+1e-9)
    e2=np.cross(nrm,np.broadcast_to(e1,d.shape)).astype(F32); e2/=(np.linalg.norm(e2,axis=-1,keepdims=True)+1e-9)
    d_e1=np.sum(d*e1,axis=-1); d_e2=np.sum(d*e2,axis=-1); d_e2=np.where(np.abs(d_e2)<1e-4,1e-4,d_e2)
    u=np.full(P,1.0/D,F32); dudp=(-u*d_e1/d_e2).astype(F32); phi=np.zeros(P,F32)
    prev=np.broadcast_to(Cpos,d.shape).astype(F32).copy()
    col=np.zeros((P,3),F32); trans=np.ones(P,F32); captured=np.zeros(P,bool)
    outdir=np.broadcast_to(fwd,d.shape).astype(F32).copy()
    Om=2*math.pi; yax=np.array([0,1.,0],F32); act=np.arange(P); N=320; dphi=F32((2.6*math.pi)/N)
    for _ in range(N):
        e2a=e2[act]; ua=u[act]; da=dudp[act]; pa=phi[act]; ppa=prev[act]
        ua=ua+da*dphi; da=da+(-ua+3*M*ua*ua)*dphi; pa=pa+dphi
        ua=np.clip(np.nan_to_num(ua,nan=1e-6),1e-6,1.6); da=np.clip(np.nan_to_num(da,nan=0.),-80,80)
        ra=1.0/ua; posa=ra[:,None]*(np.cos(pa)[:,None]*e1+np.sin(pa)[:,None]*e2a)
        cap=ra<=Rs*1.02; esc=(ra>R_esc)&(da<0)
        y0=ppa[:,1]; y1=posa[:,1]; cross=(y0*y1<0)&~cap&(trans[act]>0.02)
        if cross.any():
            ci=np.where(cross)[0]; t=(y0[ci]/(y0[ci]-y1[ci]+1e-9))[:,None]
            hp=ppa[ci]+(posa[ci]-ppa[ci])*t; rho=np.sqrt(hp[:,0]**2+hp[:,2]**2)
            good=(rho>=Rin)&(rho<=Rout)
            if good.any():
                ci=ci[good]; hp=hp[good]; rho=rho[good]; s=(rho-Rin)/(Rout-Rin)
                base=DISK(s)/255.0
                th=np.arctan2(hp[:,2],hp[:,0])
                swirl=(0.58+0.42*np.sin(3*th-Om*frac+2.3*np.log(rho+1e-3)))
                swirl*=(0.80+0.20*np.sin(7*th-2*Om*frac)); swirl*=(0.9+0.1*np.sin(13*th-3*Om*frac))
                bright=(Rin/(rho+1e-3))**1.35 + 0.6*np.exp(-((s-0.02)**2)/0.006)  # hot inner rim
                rhat=hp.copy(); rhat[:,1]=0; rhat/=(np.linalg.norm(rhat,axis=1,keepdims=True)+1e-9)
                vdir=np.cross(yax,rhat); beta=np.sqrt(M/(rho+1e-3))
                view=Cpos[None]-hp; view/=(np.linalg.norm(view,axis=1,keepdims=True)+1e-9)
                mu=np.sum(vdir*view,axis=1); dopp=(1.0/(1.0-np.clip(beta,0,.86)*mu))**3.4
                shift=np.clip(1.0+0.38*mu,0.55,1.45); base[:,2]*=shift; base[:,0]/=np.sqrt(shift)
                emis=np.clip(base*(bright*swirl*dopp*1.5)[:,None],0,32)
                op=np.clip(0.85*np.exp(-3.0*s),0.12,0.95); gi=act[ci]
                col[gi]+=emis*trans[gi][:,None]; trans[gi]*=(1-op)
        if esc.any():
            ei=np.where(esc)[0]; od=posa[ei]-ppa[ei]; od/=(np.linalg.norm(od,axis=1,keepdims=True)+1e-9)
            outdir[act[ei]]=od
        captured[act[cap]]=True
        u[act]=ua; dudp[act]=da; phi[act]=pa; prev[act]=posa
        act=act[~(cap|esc)]
        if act.size==0: break
    if act.size: outdir[act]=fwd
    stars=sample_stars(smap,np.nan_to_num(outdir),roll=0.14*math.sin(2*math.pi*frac))
    tw=1.0+0.10*np.sin(2*math.pi*frac+(outdir[:,0]+outdir[:,2])*40)
    col+=(~captured)[:,None]*trans[:,None]*stars*tw[:,None]
    return col.reshape(Hh,Wh,3), captured.reshape(Hh,Wh).astype(F32)

def post(img, cov, W, H):
    # photon ring around the silhouette (thin bright core + soft halo)
    gy,gx=np.gradient(cov); edge=np.sqrt(gx*gx+gy*gy); edge/=(edge.max()+1e-6)
    ringcol=np.array([0.85,0.95,1.0],F32)
    img=img+(edge**1.8)[...,None]*ringcol*2.6
    img=img+blur((edge**1.3)[...,None]*ringcol, r=max(2,W//150), passes=3)*1.2
    # bloom (smoother = more gaussian, fewer box halos)
    img=img+0.5*blur(np.clip(img-1.3,0,None), r=max(2,W//180), passes=4)
    # cinematic vignette focused on the hole (right of centre)
    ys,xs=np.mgrid[0:H,0:W].astype(F32); xs/=W; ys/=H
    vig=1-0.6*((xs-0.70)**2*0.6+(ys-0.5)**2*1.5); vig=np.clip(vig,0.4,1.0)
    return img*vig[...,None]

def tonemap(img, sat=1.5):
    x=np.clip(img,0,None); L=x.max(-1,keepdims=True); x=x*((L/(1+L))/(L+1e-6))
    g=x.mean(-1,keepdims=True); x=np.clip(g+(x-g)*sat,0,1)
    return (np.power(x,1/2.2)*255+0.5).astype(np.uint8)

def frame(W,H,frac,smap,xoff,SS):
    col,cov=render_scene(W*SS,H*SS,frac,smap,xoff)
    img=col.reshape(H,SS,W,SS,3).mean((1,3)); c=cov.reshape(H,SS,W,SS).mean((1,3))
    return tonemap(post(img,c,W,H))

# ---------------------------------------------------------------- text overlay
import glob as _glob
# bounded candidate paths (recursive glob only over the small /usr/share/fonts tree)
_DEJA="/home/Asttr0/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/*/files/share/fonts/truetype/dejavu"
_PROTON="/home/Asttr0/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Proton - Experimental/files/share/fonts"
_VSC="/home/Asttr0/.var/app/com.visualstudio.code/data/vscode/extensions/tomoki1207.pdf-1.2.2/lib/web/standard_fonts"
def _first(cands):
    for pat, rec in cands:
        hits=_glob.glob(pat, recursive=rec)
        if hits: return sorted(hits)[0]
    return None
NAME_FONT=_first([("/usr/share/fonts/**/DejaVuSans-Bold.ttf",True), (f"{_DEJA}/DejaVuSans-Bold.ttf",False),
                  (f"{_VSC}/LiberationSans-Bold.ttf",False), (f"{_PROTON}/arialbd.ttf",False)])
MONO_FONT=_first([("/usr/share/fonts/**/DejaVuSansMono.ttf",True), (f"{_DEJA}/DejaVuSansMono.ttf",False)])
MONO_BOLD=_first([("/usr/share/fonts/**/DejaVuSansMono-Bold.ttf",True), (f"{_DEJA}/DejaVuSansMono-Bold.ttf",False)]) or MONO_FONT

def build_overlay(W,H):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    txt=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(txt)
    x=int(W*0.055)
    nsz=int(H*0.155); esz=int(H*0.05); ssz=int(H*0.047); hsz=int(H*0.046)
    fn=ImageFont.truetype(NAME_FONT,nsz); fe=ImageFont.truetype(MONO_BOLD,esz)
    fs=ImageFont.truetype(MONO_FONT,ssz); fh=ImageFont.truetype(MONO_FONT,hsz)
    ny=int(H*0.5)-int(nsz*0.5)
    ex=x; ey=ny-esz-int(H*0.045)
    for ch in "CYBERSECURITY ENTHUSIAST":
        d.text((ex,ey),ch,font=fe,fill=(103,232,249,255)); ex+=d.textlength(ch,font=fe)+esz*0.30
    d.text((x,ny),"Mohamed Taha Slimani",font=fn,fill=(245,247,255,255))
    sy=ny+nsz+int(H*0.035)
    d.text((x,sy),"offensive × defensive   ·   builder   ·   bug bounty   ·   htb",font=fs,fill=(176,184,214,255))
    hy=sy+ssz+int(H*0.055); ht="@Asttr0"; hw=d.textlength(ht,font=fh); pad=int(H*0.032)
    d.rounded_rectangle([x,hy,x+hw+2*pad,hy+hsz+2*int(H*0.02)],radius=int(H*0.06),outline=(170,120,255,235),width=2)
    d.text((x+pad,hy+int(H*0.02)),ht,font=fh,fill=(226,170,255,255))
    # soft dark halo behind text for legibility over stars
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.paste((2,2,10,255),(0,0),txt.split()[3])
    sh=sh.filter(ImageFilter.GaussianBlur(max(2,int(H*0.018))))
    return Image.alpha_composite(sh,txt)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--test",action="store_true"); ap.add_argument("--frames",type=int,default=0)
    ap.add_argument("--out",default=SCRATCH+"/frames"); ap.add_argument("--w",type=int,default=1000)
    ap.add_argument("--h",type=int,default=300); ap.add_argument("--xoff",type=float,default=-0.46)
    ap.add_argument("--ss",type=int,default=2)
    ap.add_argument("--start",type=int,default=0); ap.add_argument("--stride",type=int,default=1)
    a=ap.parse_args()
    from PIL import Image
    smap=build_starmap(); ov=build_overlay(a.w,a.h)
    def compose(fr):
        im=Image.fromarray(fr).convert("RGBA"); return Image.alpha_composite(im,ov).convert("RGB")
    print("fonts:", NAME_FONT and os.path.basename(NAME_FONT), "/", MONO_FONT and os.path.basename(MONO_FONT))
    if a.test:
        compose(frame(a.w,a.h,0.18,smap,a.xoff,a.ss)).save(SCRATCH+"/bh_test.png")
        print("wrote bh_test.png"); return
    os.makedirs(a.out,exist_ok=True); t0=time.time()
    for i in range(a.start, a.frames, a.stride):
        compose(frame(a.w,a.h,i/a.frames,smap,a.xoff,a.ss)).save(f"{a.out}/f{i:03d}.png")
        print(f"frame {i} done  {time.time()-t0:.1f}s",flush=True)

if __name__=="__main__":
    main()
