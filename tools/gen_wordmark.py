#!/usr/bin/env python3
"""Generate the animated neon ASCII ASTTR0 wordmark."""

from pathlib import Path

W, H = 1000, 270
MONO = "ui-monospace,'JetBrains Mono','Fira Code','Cascadia Mono',Menlo,Consolas,monospace"

GLYPHS = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "S": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
}

TEXT = "ASTTR0"
INK = ["@@", "##", "%%", "**", "++", "==", "@@"]
rows = []
for row in range(7):
    chunks = []
    for letter in TEXT:
        chunks.append("".join(INK[row] if bit == "1" else "  " for bit in GLYPHS[letter][row]))
    rows.append("   ".join(chunks))

ascii_rows = []
for index, line in enumerate(rows):
    y = 72 + index * 24
    ascii_rows.append(
        f'<text x="500" y="{y}" text-anchor="middle" xml:space="preserve" class="ascii r{index}">{line}</text>'
    )

trails = []
for index in range(10):
    y = 25 + index * 24
    trails.append(
        f'<path d="M {-160-index*23} {y} L {180+index*58} {y} L {260+index*58} {y-28}" '
        f'class="trail t{index}"/>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Animated neon ASCII wordmark reading ASTTR0">
  <defs>
    <linearGradient id="bg" x1="0" x2="1"><stop stop-color="#030407"/><stop offset=".5" stop-color="#070712"/><stop offset="1" stop-color="#030407"/></linearGradient>
    <linearGradient id="ink" x1="0" x2="1"><stop stop-color="#67e8f9"/><stop offset=".52" stop-color="#d8b4fe"/><stop offset="1" stop-color="#a7f3d0"/></linearGradient>
    <linearGradient id="beam" x1="0" x2="1"><stop stop-color="#67e8f9" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".65"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></linearGradient>
    <filter id="glow" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="reveal"><rect x="35" y="30" height="205" width="930"><animate attributeName="width" from="0" to="930" dur="1.35s" fill="freeze"/></rect></clipPath>
    <style>
      .ascii{{font-family:{MONO};font-size:19px;font-weight:800;fill:url(#ink);filter:url(#glow);letter-spacing:.5px}}
      .art{{animation:hover 5.2s ease-in-out infinite,flicker 9s steps(1,end) infinite;transform-origin:center}}
      .ghostA{{fill:#22d3ee;opacity:.15}} .ghostB{{fill:#a78bfa;opacity:.12}}
      .trail{{fill:none;stroke:#67e8f9;stroke-width:1;stroke-opacity:.16;stroke-dasharray:10 18;animation:flow 8s linear infinite}}
      .t1,.t4,.t7{{animation-duration:11s;stroke:#a78bfa}} .t2,.t5,.t8{{animation-duration:6.5s;stroke:#a7f3d0}}
      .beam{{animation:scan 4.6s ease-in-out infinite}}
      @keyframes hover{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}
      @keyframes flicker{{0%,17%,19%,53%,55%,100%{{opacity:1}}18%,54%{{opacity:.82}}}}
      @keyframes flow{{to{{stroke-dashoffset:-224}}}}
      @keyframes scan{{0%,12%{{transform:translateX(-280px);opacity:0}}35%{{opacity:1}}72%,100%{{transform:translateX(1180px);opacity:0}}}}
      @media (prefers-reduced-motion:reduce){{.art,.trail,.beam{{animation:none}}}}
    </style>
  </defs>
  <rect x="1" y="1" width="998" height="268" rx="18" fill="url(#bg)" stroke="#27243c"/>
  <g>{''.join(trails)}</g>
  <g clip-path="url(#reveal)">
    <g transform="translate(8 8)" class="ghostB">{''.join(ascii_rows)}</g>
    <g transform="translate(4 4)" class="ghostA">{''.join(ascii_rows)}</g>
    <g class="art">{''.join(ascii_rows)}</g>
  </g>
  <rect class="beam" x="0" y="22" width="170" height="220" fill="url(#beam)" opacity="0"/>
  <line x1="68" y1="244" x2="932" y2="244" stroke="#67e8f9" stroke-opacity=".18"/>
</svg>'''

out = Path(__file__).resolve().parent.parent / "assets" / "wordmark.svg"
out.write_text(svg, encoding="utf-8")
print("wrote", out, len(svg), "bytes")
