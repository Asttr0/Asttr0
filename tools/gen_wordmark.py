#!/usr/bin/env python3
"""Generate the animated amber CRT/pixel ASTTR0 wordmark."""

from pathlib import Path

W, H = 1000, 250
TEXT = "ASTTR0"
GLYPHS = {
    "A": ["01110", "11011", "11011", "11111", "11011", "11011", "11011"],
    "S": ["11111", "11000", "11000", "11110", "00011", "00011", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "R": ["11110", "11011", "11011", "11110", "11100", "11010", "11011"],
    "0": ["01110", "11011", "11111", "11111", "11111", "11011", "01110"],
}

CELL_W, CELL_H = 23, 23
GAP_X, GAP_Y = 5, 4
LETTER_GAP = 18
glyph_w = 5 * CELL_W + 4 * GAP_X
art_w = len(TEXT) * glyph_w + (len(TEXT) - 1) * LETTER_GAP
art_h = 7 * CELL_H + 6 * GAP_Y
start_x = (W - art_w) // 2
start_y = (H - art_h) // 2


def cells(class_name: str, dx: int = 0, dy: int = 0) -> str:
    blocks = []
    x = start_x
    for letter in TEXT:
        for row, bits in enumerate(GLYPHS[letter]):
            for col, bit in enumerate(bits):
                if bit != "1":
                    continue
                bx = x + col * (CELL_W + GAP_X) + dx
                by = start_y + row * (CELL_H + GAP_Y) + dy
                blocks.append(
                    f'<g class="{class_name}"><rect x="{bx}" y="{by}" width="{CELL_W}" height="{CELL_H}" rx="2"/>'
                    f'<path d="M {bx + 3} {by + 5}H {bx + CELL_W - 4} M {bx + 4} {by + CELL_H - 5}H {bx + CELL_W - 5}"/></g>'
                )
        x += glyph_w + LETTER_GAP
    return "".join(blocks)


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Animated amber pixel wordmark reading ASTTR0">
  <defs>
    <radialGradient id="screen" cx="50%" cy="42%" r="78%">
      <stop offset="0" stop-color="#281709"/><stop offset=".72" stop-color="#160d07"/><stop offset="1" stop-color="#090604"/>
    </radialGradient>
    <linearGradient id="amber" x1="0" y1="0" x2="0" y2="1">
      <stop stop-color="#fff86a"/><stop offset=".48" stop-color="#ffe600"/><stop offset="1" stop-color="#ffb300"/>
    </linearGradient>
    <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".22"/></pattern>
    <filter id="bloom" x="-30%" y="-50%" width="160%" height="200%"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="soft" x="-30%" y="-50%" width="160%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>
    <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="18" result="n"/><feColorMatrix in="n" values="0 0 0 0 1 0 0 0 0 .58 0 0 0 0 0 0 0 0 .055 0"/></filter>
    <style>
      .shadow rect{{fill:#5a2700;opacity:.9}} .shadow path{{stroke:#9b4700;stroke-width:2;opacity:.7}}
      .pixel rect{{fill:url(#amber)}} .pixel path{{stroke:#fff57a;stroke-width:2;opacity:.72}}
      .word{{filter:url(#bloom);animation:flicker 6.4s steps(1,end) infinite}}
      .ghost{{filter:url(#soft);opacity:.48;animation:pulse 3.8s ease-in-out infinite}}
      .glitchA,.glitchB{{opacity:0;animation:glitch 7s steps(1,end) infinite}} .glitchB{{animation-delay:-2.4s}}
      .scan{{animation:scan 4.8s linear infinite}}
      @keyframes flicker{{0%,8%,10%,46%,48%,79%,81%,100%{{opacity:1}}9%,47%,80%{{opacity:.72}}}}
      @keyframes pulse{{0%,100%{{opacity:.34}}50%{{opacity:.62}}}}
      @keyframes glitch{{0%,92%,96%,100%{{opacity:0;transform:translateX(0)}}93%{{opacity:.8;transform:translateX(-10px)}}94%{{opacity:.45;transform:translateX(7px)}}95%{{opacity:0}}}}
      @keyframes scan{{from{{transform:translateY(-250px)}}to{{transform:translateY(500px)}}}}
      @media (prefers-reduced-motion:reduce){{.word,.ghost,.glitchA,.glitchB,.scan{{animation:none}}}}
    </style>
    <clipPath id="topSlice"><rect x="0" y="55" width="1000" height="28"/></clipPath>
    <clipPath id="lowerSlice"><rect x="0" y="165" width="1000" height="22"/></clipPath>
  </defs>
  <rect width="1000" height="250" rx="12" fill="url(#screen)"/>
  <g class="ghost">{cells('pixel', 0, 3)}</g>
  <g>{cells('shadow', 6, 5)}</g>
  <g class="word">{cells('pixel')}</g>
  <g class="glitchA" clip-path="url(#topSlice)">{cells('pixel')}</g>
  <g class="glitchB" clip-path="url(#lowerSlice)">{cells('pixel')}</g>
  <rect width="1000" height="250" fill="url(#scanlines)" opacity=".66"/>
  <rect class="scan" x="0" y="0" width="1000" height="42" fill="#fff57a" opacity=".035"/>
  <rect width="1000" height="250" rx="12" filter="url(#grain)" opacity=".34"/>
  <rect x="1" y="1" width="998" height="248" rx="12" fill="none" stroke="#3b2411" stroke-width="2"/>
</svg>'''

out = Path(__file__).resolve().parent.parent / "assets" / "asttr0-crt.svg"
out.write_text(svg, encoding="utf-8")
print("wrote", out, len(svg), "bytes")
