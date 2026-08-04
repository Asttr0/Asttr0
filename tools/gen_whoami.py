#!/usr/bin/env python3
"""Generate a minimal animated amber cathode terminal profile."""

from pathlib import Path

W, H = 900, 400
MONO = "ui-monospace,'JetBrains Mono','Fira Code','Cascadia Mono',Menlo,Consolas,monospace"
TOTAL = 13

LINES = [
    ("> Mohamed Taha Slimani", 74, 1.0),
    ("  Software Engineering student · Morocco", 118, 2.5),
    ("  Learning systems. Building reliable software.", 190, 3.8),
    ("  Algorithms · full-stack engineering · secure applications", 234, 5.7),
    ("  Turning cybersecurity problems into practical tools.", 278, 8.0),
]


def typed_line(text: str, y: int, start: float) -> str:
    width = min(790, max(24, len(text) * 10.2))
    begin = start / TOTAL
    done = min((start + max(0.7, len(text) * 0.031)) / TOTAL, 0.88)
    reset = 0.965
    return f'''
      <g>
        <clipPath id="line{y}"><rect x="70" y="{y - 25}" height="34" width="0">
          <animate attributeName="width" values="0;0;{width:.1f};{width:.1f};0" keyTimes="0;{begin:.4f};{done:.4f};{reset};1" dur="{TOTAL}s" repeatCount="indefinite"/>
        </rect></clipPath>
        <text x="70" y="{y}" clip-path="url(#line{y})" class="line">{text}</text>
      </g>'''


content = "".join(typed_line(*line) for line in LINES).lstrip()


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Amber cathode terminal introduction for Mohamed Taha Slimani">
  <defs>
    <radialGradient id="glass" cx="50%" cy="43%" r="76%"><stop offset="0" stop-color="#2a1a0d"/><stop offset=".68" stop-color="#171008"/><stop offset="1" stop-color="#080604"/></radialGradient>
    <radialGradient id="reflection" cx="50%" cy="0" r="70%"><stop stop-color="#ffe95a" stop-opacity=".08"/><stop offset="1" stop-color="#ffe95a" stop-opacity="0"/></radialGradient>
    <radialGradient id="vignette" cx="50%" cy="48%" r="66%"><stop offset=".60" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".66"/></radialGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#fff56a" stop-opacity="0"/><stop offset=".5" stop-color="#fff56a" stop-opacity=".09"/><stop offset="1" stop-color="#fff56a" stop-opacity="0"/></linearGradient>
    <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".25"/></pattern>
    <filter id="phosphor" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="noise" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="3" seed="9"/><feColorMatrix values="0 0 0 0 1 0 0 0 0 .55 0 0 0 0 0 0 0 0 .06 0"/></filter>
    <clipPath id="screen"><rect x="24" y="20" width="852" height="360" rx="48"/></clipPath>
    <style>
      .line{{font-family:{MONO};font-size:19px;font-weight:650;fill:#ffe83a;filter:url(#phosphor);letter-spacing:.2px}}
      .cursor{{animation:blink .9s steps(1,end) infinite}} .sweep{{animation:sweep 5.2s linear infinite}} .screen{{animation:flicker 8s steps(1,end) infinite}}
      @keyframes blink{{50%{{opacity:0}}}} @keyframes sweep{{from{{transform:translateY(-100px)}}to{{transform:translateY(500px)}}}}
      @keyframes flicker{{0%,13%,15%,60%,62%,100%{{opacity:1}}14%,61%{{opacity:.97}}}}
      @media (prefers-reduced-motion:reduce){{.cursor,.sweep,.screen{{animation:none}}}}
    </style>
  </defs>
  <rect x="1" y="1" width="898" height="398" rx="56" fill="#0c0905" stroke="#332312" stroke-width="2"/>
  <g clip-path="url(#screen)" class="screen">
    <rect x="24" y="20" width="852" height="360" rx="48" fill="url(#glass)"/>
    <ellipse cx="450" cy="32" rx="380" ry="170" fill="url(#reflection)"/>
    {content}
    <g opacity="0">
      <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.76;.78;.965;1" dur="{TOTAL}s" repeatCount="indefinite"/>
      <text x="70" y="333" class="line">&gt;</text>
      <rect class="cursor" x="94" y="311" width="13" height="25" rx="1" fill="#ffe83a" filter="url(#phosphor)"/>
    </g>
    <rect x="24" y="20" width="852" height="360" fill="url(#scanlines)" opacity=".72"/>
    <rect class="sweep" x="24" y="0" width="852" height="80" fill="url(#sweep)"/>
    <rect x="24" y="20" width="852" height="360" filter="url(#noise)" opacity=".25"/>
    <rect x="24" y="20" width="852" height="360" rx="48" fill="url(#vignette)"/>
  </g>
  <rect x="18" y="14" width="864" height="372" rx="52" fill="none" stroke="#5c3b17" stroke-opacity=".58" stroke-width="5"/>
</svg>'''

out = Path(__file__).resolve().parent.parent / "assets" / "about-crt.svg"
out.write_text(svg, encoding="utf-8")
print("wrote", out, len(svg), "bytes")
