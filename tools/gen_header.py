#!/usr/bin/env python3
"""Generate an animated deep-space / black-hole SVG header for the profile README.
Self-hosted (committed to the repo) so it never depends on a rate-limited service.
Animations use SMIL + CSS keyframes, both of which animate when the SVG is embedded
as an <img> on GitHub."""
import random, math

random.seed(42)  # deterministic output
W, H = 1200, 340
CX, CY = 892, 172           # black-hole centre
R = 168                     # accretion ring radius

def stars(n, xmax=W):
    out = []
    for _ in range(n):
        x = round(random.uniform(0, xmax), 1)
        y = round(random.uniform(0, H), 1)
        r = round(random.uniform(0.4, 1.7), 2)
        dur = round(random.uniform(2.2, 6.5), 2)
        delay = round(random.uniform(-6, 0), 2)
        base = round(random.uniform(0.15, 0.55), 2)
        peak = round(random.uniform(0.7, 1.0), 2)
        # dim stars that fall too close to the event horizon (they'd be "swallowed")
        if math.hypot(x - CX, y - CY) < 92:
            continue
        out.append((x, y, r, dur, delay, base, peak))
    return out

STARS = stars(180)

# orbiting hot-spots (matter clumps) inside the rotating disk group
HOTSPOTS = [
    (R,   0, 10, "#a5f3fc", 0.95),
    (-R,  0,  7, "#f0abfc", 0.85),
    (0,   R,  8, "#fde68a", 0.9),
    (R*0.72,  R*0.72, 5, "#67e8f9", 0.8),
    (-R*0.72, R*0.72, 6, "#e879f9", 0.75),
]

def star_svg(s):
    x, y, r, dur, delay, base, peak = s
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#eaf2ff" opacity="{base}">'
            f'<animate attributeName="opacity" values="{base};{peak};{base}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/></circle>')

def hotspot_svg(h):
    x, y, r, col, op = h
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="{op}" '
            f'filter="url(#soft)"/>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" aria-label="Mohamed Taha Slimani — Cybersecurity Enthusiast">
  <defs>
    <radialGradient id="space" cx="62%" cy="50%" r="85%">
      <stop offset="0%" stop-color="#0c1030"/>
      <stop offset="45%" stop-color="#070716"/>
      <stop offset="100%" stop-color="#020208"/>
    </radialGradient>
    <radialGradient id="ring" cx="50%" cy="50%" r="50%">
      <stop offset="0%"  stop-color="#000000" stop-opacity="0"/>
      <stop offset="62%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="74%" stop-color="#7c3aed" stop-opacity="0.35"/>
      <stop offset="86%" stop-color="#e879f9" stop-opacity="0.95"/>
      <stop offset="93%" stop-color="#fbbf24" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#e879f9" stop-opacity="0.55"/>
      <stop offset="55%" stop-color="#7c3aed" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="neb1" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#4f46e5" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#4f46e5" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="neb2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="horizon" cx="50%" cy="42%" r="60%">
      <stop offset="0%" stop-color="#000005"/>
      <stop offset="82%" stop-color="#000005"/>
      <stop offset="100%" stop-color="#0a0a1a"/>
    </radialGradient>
    <filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="3.4"/>
    </filter>
    <filter id="blurL" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="26"/>
    </filter>
    <style>
      @keyframes fadeUp {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:none; }} }}
      @keyframes shoot {{ 0% {{ opacity:0; transform:translate(0,0); }} 6% {{ opacity:1; }} 16% {{ opacity:0; transform:translate(240px,120px); }} 100% {{ opacity:0; transform:translate(240px,120px); }} }}
      .intro {{ animation:fadeUp 1s ease-out both; }}
      .intro.d1 {{ animation-delay:.15s; }} .intro.d2 {{ animation-delay:.35s; }} .intro.d3 {{ animation-delay:.55s; }}
      .shoot {{ animation:shoot 7s ease-in infinite; }}
      @media (prefers-reduced-motion: reduce) {{ .intro {{ animation:none; opacity:1; }} .shoot {{ display:none; }} }}
    </style>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#space)"/>
  <ellipse cx="300" cy="120" rx="360" ry="220" fill="url(#neb1)" filter="url(#blurL)" opacity="0.7"/>
  <ellipse cx="960" cy="250" rx="320" ry="200" fill="url(#neb2)" filter="url(#blurL)" opacity="0.6"/>

  <!-- starfield -->
  <g>
    {chr(10).join("    " + star_svg(s) for s in STARS)}
  </g>

  <!-- shooting star -->
  <g class="shoot" opacity="0">
    <line x1="120" y1="60" x2="150" y2="75" stroke="#a5f3fc" stroke-width="1.6" stroke-linecap="round"/>
  </g>

  <!-- BLACK HOLE -->
  <g>
    <!-- ambient accretion glow -->
    <ellipse cx="{CX}" cy="{CY}" rx="300" ry="120" fill="url(#glow)" opacity="0.9"/>

    <!-- tilted, spinning accretion disk -->
    <g transform="translate({CX} {CY}) rotate(-17)">
      <g transform="scale(1 0.4)">
        <g>
          <animateTransform attributeName="transform" type="rotate" from="0 0 0" to="360 0 0" dur="22s" repeatCount="indefinite"/>
          <circle cx="0" cy="0" r="{R+34}" fill="url(#ring)"/>
          {chr(10).join("          " + hotspot_svg(h) for h in HOTSPOTS)}
        </g>
      </g>
    </g>

    <!-- event horizon (round sphere, sits in front of disk centre) -->
    <circle cx="{CX}" cy="{CY}" r="66" fill="url(#horizon)"/>
    <circle cx="{CX}" cy="{CY}" r="66" fill="none" stroke="#22d3ee" stroke-width="1.5" opacity="0.55" filter="url(#soft)"/>

    <!-- photon ring / gravitational-lensing arc, drawn in front -->
    <g transform="translate({CX} {CY}) rotate(-17)">
      <ellipse cx="0" cy="0" rx="{R+30}" ry="{(R+30)*0.4:.1f}" fill="none" stroke="#c7f9ff" stroke-width="2.2" opacity="0.75" filter="url(#soft)"/>
    </g>
  </g>

  <!-- IDENTITY -->
  <g>
    <text class="intro d1" x="64" y="126" font-family="'Courier New', monospace" font-size="15" letter-spacing="5" fill="#67e8f9">CYBERSECURITY&#160;ENTHUSIAST</text>
    <text class="intro d2" x="60" y="184" font-family="'Trebuchet MS','Segoe UI',Arial,sans-serif" font-size="52" font-weight="700" fill="#f4f6ff">Mohamed Taha Slimani</text>
    <text class="intro d3" x="64" y="224" font-family="'Courier New', monospace" font-size="16" fill="#aab2d5">offensive &#215; defensive&#160;&#160;&#183;&#160;&#160;builder&#160;&#160;&#183;&#160;&#160;bug&#160;bounty&#160;&#183;&#160;htb</text>
    <g class="intro d3">
      <rect x="64" y="248" width="150" height="30" rx="15" fill="none" stroke="#7c3aed" stroke-opacity="0.6"/>
      <text x="139" y="268" text-anchor="middle" font-family="'Courier New', monospace" font-size="13" fill="#e879f9">@Asttr0</text>
    </g>
  </g>
</svg>'''

with open("/home/Asttr0/github-profile/assets/header.svg", "w") as f:
    f.write(svg)
print("wrote assets/header.svg", len(svg), "bytes,", len(STARS), "stars")
