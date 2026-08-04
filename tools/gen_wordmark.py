#!/usr/bin/env python3
"""Generate ASTTR0 in the requested FIGlet ANSI Shadow style."""

from pathlib import Path
from xml.sax.saxutils import escape

W, H = 1000, 205
MONO = "Consolas,'DejaVu Sans Mono','Courier New',monospace"

ART = [
    " █████╗ ███████╗████████╗████████╗██████╗  ██████╗ ",
    "██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔══██╗██╔═████╗",
    "███████║███████╗   ██║      ██║   ██████╔╝██║██╔██║",
    "██╔══██║╚════██║   ██║      ██║   ██╔══██╗████╔╝██║",
    "██║  ██║███████║   ██║      ██║   ██║  ██║╚██████╔╝",
    "╚═╝  ╚═╝╚══════╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ",
]

COL_W = 16.5
columns = max(len(line.rstrip()) for line in ART)
start_x = (W - columns * COL_W) / 2
cells = []
for row, line in enumerate(ART):
    for column, char in enumerate(line.rstrip()):
        if char == " ":
            continue
        x = start_x + (column + 0.5) * COL_W
        y = 38 + row * 29
        cells.append(
            f'<text x="{x:.2f}" y="{y}" text-anchor="middle">{escape(char)}</text>'
        )
rows = "".join(cells)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ASTTR0 rendered in FIGlet ANSI Shadow style">
  <defs>
    <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".025"/></pattern>
    <g id="ascii" fill="currentColor" font-family="{MONO}" font-size="28" font-weight="700">{rows}</g>
    <clipPath id="glitchTop"><rect x="0" y="48" width="1000" height="23"/></clipPath>
    <clipPath id="glitchBottom"><rect x="0" y="134" width="1000" height="20"/></clipPath>
    <style>
      .cyan{{color:#00d9ff;transform:translate(-2px,2px);animation:cyan 5.8s steps(1,end) infinite}}
      .yellow{{color:#ffe600;transform:translate(2px,1px);animation:yellow 6.3s steps(1,end) infinite}}
      .magenta{{color:#ff2d9b;transform:translate(3px,3px);animation:magenta 7.1s steps(1,end) infinite}}
      .main{{color:#f4f7fb;animation:flicker 8s steps(1,end) infinite}}
      .sliceA,.sliceB{{color:#f4f7fb;opacity:0;animation:glitch 6.7s steps(1,end) infinite}}
      .sliceB{{animation-delay:-2.2s}}
      @keyframes cyan{{0%,94%,100%{{transform:translate(-2px,2px)}}95%{{transform:translate(-4px,2px)}}96%{{transform:translate(-1px,2px)}}}}
      @keyframes yellow{{0%,91%,100%{{transform:translate(2px,1px)}}92%{{transform:translate(4px,1px)}}93%{{transform:translate(1px,1px)}}}}
      @keyframes magenta{{0%,96%,100%{{transform:translate(3px,3px)}}97%{{transform:translate(5px,3px)}}98%{{transform:translate(2px,3px)}}}}
      @keyframes flicker{{0%,18%,20%,71%,73%,100%{{opacity:1}}19%,72%{{opacity:.86}}}}
      @keyframes glitch{{0%,93%,97%,100%{{opacity:0;transform:translateX(0)}}94%{{opacity:.85;transform:translateX(-8px)}}95%{{opacity:.6;transform:translateX(6px)}}96%{{opacity:0}}}}
      @media (prefers-reduced-motion:reduce){{.cyan,.yellow,.magenta,.main,.sliceA,.sliceB{{animation:none}}}}
    </style>
  </defs>
  <rect width="1000" height="205" fill="#0d1117"/>
  <use href="#ascii" class="cyan"/><use href="#ascii" class="yellow"/><use href="#ascii" class="magenta"/><use href="#ascii" class="main"/>
  <use href="#ascii" class="sliceA" clip-path="url(#glitchTop)"/><use href="#ascii" class="sliceB" clip-path="url(#glitchBottom)"/>
  <rect width="1000" height="205" fill="url(#scanlines)"/>
</svg>'''

out = Path(__file__).resolve().parent.parent / "assets" / "asttr0-ansi-grid.svg"
out.write_text(svg, encoding="utf-8")
print("wrote", out, len(svg), "bytes")
