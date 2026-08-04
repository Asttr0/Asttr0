#!/usr/bin/env python3
"""Generate the three animated project cards used by the profile README."""

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "assets" / "projects"
ROOT.mkdir(parents=True, exist_ok=True)

PROJECTS = [
    {
        "file": "authztrace.svg",
        "number": "01",
        "name": "AuthzTrace",
        "lines": ["Authorization contract testing", "for REST APIs"],
        "tags": ["PYTHON", "CLI", "CI / SARIF"],
        "accent": "#67e8f9",
        "icon": '<circle cx="426" cy="79" r="27"/><path d="M426 106v46m0-18h28m-28 9h18"/><circle cx="426" cy="79" r="7"/>',
    },
    {
        "file": "impeccable-board.svg",
        "number": "02",
        "name": "Impeccable Board",
        "lines": ["End-to-end encrypted", "collaborative decision space"],
        "tags": ["TYPESCRIPT", "E2EE", "WEBSOCKETS"],
        "accent": "#c4b5fd",
        "icon": '<rect x="390" y="52" width="72" height="72" rx="12"/><path d="M407 73h38M407 89h25M407 105h31"/>',
    },
    {
        "file": "tracks4hacks.svg",
        "number": "03",
        "name": "tracks4hacks",
        "lines": ["Real-time correlation from", "offensive action to telemetry"],
        "tags": ["REACT", "TYPESCRIPT", "SSE / WEBGL"],
        "accent": "#a7f3d0",
        "icon": '<path d="M385 111c25-55 48 31 72-25s42 16 62-17"/><circle cx="385" cy="111" r="5"/><circle cx="457" cy="86" r="5"/><circle cx="519" cy="69" r="5"/>',
    },
]


for project in PROJECTS:
    pills = []
    x = 34
    for tag in project["tags"]:
        width = 24 + len(tag) * 7.1
        pills.append(
            f'<rect x="{x}" y="236" width="{width:.0f}" height="28" rx="14" fill="#ffffff" fill-opacity=".045" stroke="{project["accent"]}" stroke-opacity=".28"/>'
            f'<text x="{x + width/2:.1f}" y="254" text-anchor="middle" class="tag">{escape(tag)}</text>'
        )
        x += width + 10

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 550 300" width="550" height="300" role="img" aria-label="{escape(project['name'])} project card">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#0d1117"/><stop offset="1" stop-color="#100d1d"/></linearGradient>
    <linearGradient id="edge" x1="0" x2="1"><stop stop-color="{project['accent']}" stop-opacity="0"/><stop offset=".5" stop-color="{project['accent']}"/><stop offset="1" stop-color="{project['accent']}" stop-opacity="0"/></linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <style>
      text{{font-family:ui-monospace,'JetBrains Mono','Fira Code',Menlo,Consolas,monospace}}
      .eyebrow{{fill:{project['accent']};font-size:12px;font-weight:700;letter-spacing:2px}}
      .name{{fill:#f4f4f5;font-size:29px;font-weight:800}}
      .desc{{fill:#a1a1aa;font-size:15px}} .tag{{fill:#d4d4d8;font-size:10px;font-weight:700}}
      .icon{{fill:none;stroke:{project['accent']};stroke-width:3;stroke-linecap:round;stroke-linejoin:round;filter:url(#glow);animation:float 4.8s ease-in-out infinite}}
      .edge{{animation:trace 4s linear infinite}} .dot{{animation:pulse 2.2s ease-in-out infinite}}
      @keyframes trace{{to{{stroke-dashoffset:-180}}}} @keyframes float{{50%{{transform:translateY(-6px)}}}}
      @keyframes pulse{{50%{{opacity:.35}}}} @media (prefers-reduced-motion:reduce){{.icon,.edge,.dot{{animation:none}}}}
    </style>
  </defs>
  <rect x="1" y="1" width="548" height="298" rx="18" fill="url(#bg)" stroke="#30363d"/>
  <path class="edge" d="M18 2H532" stroke="url(#edge)" stroke-width="3" stroke-dasharray="90 90"/>
  <circle class="dot" cx="38" cy="38" r="4" fill="{project['accent']}" filter="url(#glow)"/>
  <text x="52" y="43" class="eyebrow">FEATURED / {project['number']}</text>
  <g class="icon">{project['icon']}</g>
  <text x="34" y="112" class="name">{escape(project['name'])}</text>
  <text x="34" y="159" class="desc">{escape(project['lines'][0])}</text>
  <text x="34" y="182" class="desc">{escape(project['lines'][1])}</text>
  {''.join(pills)}
</svg>'''
    out = ROOT / project["file"]
    out.write_text(svg, encoding="utf-8")
    print("wrote", out)
