#!/usr/bin/env python3
"""Generate the animated cathode-ray profile terminal used in the README."""

from pathlib import Path

W, H = 900, 420
T = 14.0
MONO = "ui-monospace,'JetBrains Mono','Fira Code','Cascadia Mono',Menlo,Consolas,monospace"
GREEN = "#9df7a7"
BRIGHT = "#d5ffd8"
DIM = "#5b9b62"
AMBER = "#f4c76b"


def key_time(seconds: float) -> str:
    return f"{max(0.0, min(seconds / T, 1.0)):.4f}"


def reveal(at: float) -> str:
    return (
        '<animate attributeName="opacity" values="0;0;1;1" '
        f'keyTimes="0;{key_time(at)};{key_time(at + 0.12)};1" '
        f'dur="{T}s" repeatCount="indefinite"/>'
    )


rows = [
    ("NAME", "Mohamed Taha Slimani"),
    ("ROLE", "Software Engineering Student"),
    ("LOCATION", "Morocco"),
    ("", ""),
    ("ABOUT", "I learn by building software and understanding how"),
    ("", "systems fit together, fail, and improve."),
    ("FOCUS", "algorithms · software design · secure applications"),
    ("BUILDING", "practical tools for real cybersecurity problems"),
    ("MINDSET", "curious · consistent · always learning"),
]

content = []
y = 108
delay = 1.1
for index, (label, value) in enumerate(rows):
    if not label and not value:
        y += 18
        continue
    label_text = f'<text x="48" y="{y}" class="label">{label}</text>' if label else ""
    value_x = 170 if label else 170
    content.append(
        f'<g opacity="1">{label_text}<text x="{value_x}" y="{y}" class="value">{value}</text>{reveal(delay)}</g>'
    )
    y += 29
    delay += 0.48

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Cathode terminal introduction for Mohamed Taha Slimani">
  <defs>
    <radialGradient id="glass" cx="50%" cy="42%" r="76%">
      <stop offset="0" stop-color="#102015"/>
      <stop offset="0.68" stop-color="#07100a"/>
      <stop offset="1" stop-color="#020503"/>
    </radialGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#b8ffc0" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#b8ffc0" stop-opacity="0.11"/>
      <stop offset="1" stop-color="#b8ffc0" stop-opacity="0"/>
    </linearGradient>
    <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="2" fill="#000" opacity="0.22"/>
    </pattern>
    <filter id="phosphor" x="-20%" y="-40%" width="140%" height="180%">
      <feGaussianBlur stdDeviation="1.8" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="screen"><rect x="18" y="18" width="864" height="384" rx="30"/></clipPath>
    <style>
      text{{font-family:{MONO}}}
      .label{{fill:{AMBER};font-size:14px;font-weight:700;letter-spacing:1.4px}}
      .value{{fill:{GREEN};font-size:16px;filter:url(#phosphor)}}
      .sweep{{animation:sweepDown 5.8s linear infinite}}
      .screenGlow{{animation:flicker 8s steps(1,end) infinite}}
      @keyframes sweepDown{{0%{{transform:translateY(-90px)}}100%{{transform:translateY(500px)}}}}
      @keyframes flicker{{0%,18%,22%,61%,64%,100%{{opacity:1}}20%,63%{{opacity:.965}}}}
      @media (prefers-reduced-motion:reduce){{.sweep,.screenGlow{{animation:none}}}}
    </style>
  </defs>

  <rect x="1" y="1" width="898" height="418" rx="38" fill="#171712" stroke="#35362e" stroke-width="2"/>
  <rect x="11" y="11" width="878" height="398" rx="34" fill="#080a07" stroke="#252a22" stroke-width="5"/>
  <g clip-path="url(#screen)" class="screenGlow">
    <rect x="18" y="18" width="864" height="384" rx="30" fill="url(#glass)"/>
    <ellipse cx="450" cy="205" rx="440" ry="207" fill="none" stroke="#9df7a7" stroke-opacity="0.055" stroke-width="18"/>

    <text x="48" y="56" fill="{DIM}" font-family="{MONO}" font-size="11" letter-spacing="2">COOL-RETRO PROFILE TERMINAL  /  CRT-01</text>
    <circle cx="846" cy="51" r="5" fill="{GREEN}" filter="url(#phosphor)">
      <animate attributeName="opacity" values="1;.45;1" dur="2.6s" repeatCount="indefinite"/>
    </circle>
    <text x="829" y="56" text-anchor="end" fill="{DIM}" font-family="{MONO}" font-size="11">ONLINE</text>
    <line x1="48" y1="75" x2="852" y2="75" stroke="{DIM}" stroke-opacity="0.42"/>

    <g opacity="1">
      <text x="48" y="91" fill="{BRIGHT}" font-family="{MONO}" font-size="13">PROFILE.EXE loaded successfully</text>
      {reveal(0.35)}
    </g>
    {''.join(content)}

    <g opacity="1">
      <text x="48" y="374" fill="{DIM}" font-family="{MONO}" font-size="14">READY</text>
      <rect x="102" y="359" width="10" height="18" fill="{GREEN}" filter="url(#phosphor)">
        <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/>
      </rect>
      {reveal(delay + 0.3)}
    </g>

    <rect x="18" y="18" width="864" height="384" fill="url(#scanlines)" opacity="0.58"/>
    <rect class="sweep" x="18" y="0" width="864" height="90" fill="url(#sweep)"/>
  </g>
</svg>'''

out = Path(__file__).resolve().parent.parent / "assets" / "whoami.svg"
out.write_text(svg, encoding="utf-8")
print("wrote", out, len(svg), "bytes")
