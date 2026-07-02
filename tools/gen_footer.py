#!/usr/bin/env python3
"""Generate an animated 'singularity' footer strip (self-hosted SVG).
Matter-streaks fall into a pulsing core across a dark horizon. SMIL + CSS
animations both animate when the SVG is embedded as an <img> on GitHub."""
import random, math
random.seed(11)
W, H = 1200, 150
CX, CY = W / 2, H / 2

def stars(n):
    out = []
    for _ in range(n):
        x, y = round(random.uniform(0, W), 1), round(random.uniform(0, H), 1)
        if abs(x - CX) < 90 and abs(y - CY) < 30:
            continue
        r = round(random.uniform(0.4, 1.4), 2)
        dur = round(random.uniform(2.4, 6), 2); dl = round(random.uniform(-6, 0), 2)
        b = round(random.uniform(.2, .5), 2); pk = round(random.uniform(.7, 1), 2)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#dfe9ff" opacity="{b}">'
                   f'<animate attributeName="opacity" values="{b};{pk};{b}" dur="{dur}s" '
                   f'begin="{dl}s" repeatCount="indefinite"/></circle>')
    return "\n    ".join(out)

def streaks(n):
    out = []
    cols = ["#8bd6ff", "#a678ff", "#e879f9", "#ffffff", "#67e8f9"]
    for _ in range(n):
        ang = random.uniform(0, 2 * math.pi)
        r0 = random.uniform(W * 0.30, W * 0.52)
        sx, sy = CX + math.cos(ang) * r0, CY + math.sin(ang) * r0 * 0.42
        # end just outside the core
        r1 = random.uniform(58, 74)
        ex, ey = CX + math.cos(ang) * r1, CY + math.sin(ang) * r1 * 0.42
        ln = random.uniform(14, 30)
        ux, uy = (CX - sx), (CY - sy)
        m = math.hypot(ux, uy) + 1e-6; ux, uy = ux / m, uy / m
        col = random.choice(cols)
        dur = round(random.uniform(2.2, 4.2), 2); beg = round(-random.uniform(0, dur), 2)
        w = round(random.uniform(1.0, 2.0), 1)
        out.append(
            f'<g opacity="0"><line x1="0" y1="0" x2="{ux*ln:.1f}" y2="{uy*ln:.1f}" '
            f'stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="{sx:.1f} {sy:.1f}" to="{ex:.1f} {ey:.1f}" dur="{dur}s" begin="{beg}s" '
            f'repeatCount="indefinite" keyTimes="0;1" calcMode="spline" keySplines="0.4 0 1 1"/>'
            f'<animate attributeName="opacity" values="0;0.9;0" dur="{dur}s" begin="{beg}s" '
            f'repeatCount="indefinite"/></g>')
    return "\n    ".join(out)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" aria-label="singularity">
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="75%">
      <stop offset="0%" stop-color="#0b0b1e"/><stop offset="60%" stop-color="#070713"/><stop offset="100%" stop-color="#040409"/>
    </radialGradient>
    <radialGradient id="core" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff"/><stop offset="30%" stop-color="#a5f3fc"/>
      <stop offset="60%" stop-color="#a678ff" stop-opacity="0.7"/><stop offset="100%" stop-color="#7c3aed" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="hz" x1="0" x2="1">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity="0"/><stop offset="50%" stop-color="#a5f3fc" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#e879f9" stop-opacity="0"/>
    </linearGradient>
    <filter id="b"><feGaussianBlur stdDeviation="2.2"/></filter>
    <style>@keyframes pulse{{0%,100%{{opacity:.75;transform:scale(1)}}50%{{opacity:1;transform:scale(1.12)}}}}
      .core{{transform-box:fill-box;transform-origin:center;animation:pulse 3.4s ease-in-out infinite}}
      @media (prefers-reduced-motion:reduce){{.core{{animation:none}}}}</style>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g>
    {stars(70)}
  </g>
  <line x1="90" y1="{CY}" x2="{W-90}" y2="{CY}" stroke="url(#hz)" stroke-width="2.6" filter="url(#b)"/>
  <line x1="230" y1="{CY}" x2="{W-230}" y2="{CY}" stroke="url(#hz)" stroke-width="1"/>
  <g>
    {streaks(44)}
  </g>
  <ellipse class="core" cx="{CX}" cy="{CY}" rx="132" ry="26" fill="url(#core)" filter="url(#b)"/>
  <circle cx="{CX}" cy="{CY}" r="13" fill="#05060c"/>
  <circle cx="{CX}" cy="{CY}" r="13" fill="none" stroke="#a5f3fc" stroke-width="1.4" opacity="0.8" filter="url(#b)"/>
</svg>'''

open("/home/Asttr0/github-profile/assets/footer.svg", "w").write(svg)
print("wrote assets/footer.svg", len(svg), "bytes")
