#!/usr/bin/env python3
"""Generate a typing profile terminal from cool-retro-term's Default Amber preset."""

from pathlib import Path
from xml.sax.saxutils import escape

W, H = 900, 450
TOTAL = 18.0
HOLD_UNTIL = 17.25
MONO = "'Terminess Nerd Font Mono',Terminus,Consolas,'DejaVu Sans Mono',monospace"

LINES = [
    ("> Mohamed Taha Slimani", 74, "prompt"),
    ("Software Engineering Student · Morocco", 118, "text"),
    ("Learning systems. Building reliable software.", 190, "text"),
    ("Algorithms · full-stack engineering · secure applications", 234, "text"),
    ("Building practical tools for real cybersecurity problems.", 278, "text"),
]


def delay_for(char: str) -> float:
    if char in ".,:·":
        return 0.11
    if char == " ":
        return 0.035
    return 0.055


def fmt(values: list[float]) -> str:
    return ";".join(f"{value:.4f}" for value in values)


def typed_line(value: str, y: int, kind: str, start: float, index: int) -> tuple[str, float]:
    elapsed = start
    times = [0.0, start / TOTAL]
    widths = [0.0, 0.0]
    for position, char in enumerate(value, start=1):
        elapsed += delay_for(char)
        times.append(elapsed / TOTAL)
        widths.append(min(812.0, position * 12.0 + 4.0))

    final_width = min(820.0, len(value) * 12.0 + 20.0)
    times.extend([HOLD_UNTIL / TOTAL, 1.0])
    widths.extend([final_width, 0.0])
    width_values = ";".join(f"{width:.1f}" for width in widths)
    cursor_values = ";".join(f"{64 + width:.1f}" for width in widths)
    key_times = fmt(times)
    cursor_end = min(elapsed + 0.04, HOLD_UNTIL - 0.1)

    markup = f'''
      <clipPath id="typing{index}">
        <rect x="64" y="{y - 25}" width="0" height="33">
          <animate attributeName="width" values="{width_values}" keyTimes="{key_times}" calcMode="discrete" dur="{TOTAL}s" repeatCount="indefinite"/>
        </rect>
      </clipPath>
      <g clip-path="url(#typing{index})">
        <text x="65.2" y="{y}" class="chroma {kind}">{escape(value)}</text>
        <text x="64" y="{y}" class="{kind}">{escape(value)}</text>
      </g>
      <rect y="{y - 22}" width="11" height="24" fill="#f08619" filter="url(#bloom)" opacity="0">
        <animate attributeName="x" values="{cursor_values}" keyTimes="{key_times}" calcMode="discrete" dur="{TOTAL}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{start / TOTAL:.4f};{(start + 0.01) / TOTAL:.4f};{elapsed / TOTAL:.4f};{cursor_end / TOTAL:.4f};1" dur="{TOTAL}s" repeatCount="indefinite"/>
      </rect>'''
    return markup, elapsed


line_markup = []
start = 0.55
for index, (value, y, kind) in enumerate(LINES):
    markup, end = typed_line(value, y, kind, start, index)
    line_markup.append(markup)
    start = end + 0.38

finished = start - 0.38
content = "".join(line_markup).lstrip()

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Typing profile terminal using cool-retro-term Default Amber visuals">
  <defs>
    <radialGradient id="screen" cx="50%" cy="45%" r="73%"><stop offset="0" stop-color="#160b02"/><stop offset=".68" stop-color="#090401"/><stop offset="1" stop-color="#000"/></radialGradient>
    <radialGradient id="curve" cx="50%" cy="48%" r="68%"><stop offset=".58" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".72"/></radialGradient>
    <linearGradient id="glowingLine" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ff8100" stop-opacity="0"/><stop offset=".5" stop-color="#ffb132" stop-opacity=".10"/><stop offset="1" stop-color="#ff8100" stop-opacity="0"/></linearGradient>
    <pattern id="scanlines" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#000" opacity=".30"/></pattern>
    <filter id="bloom" x="-18%" y="-80%" width="136%" height="260%"><feGaussianBlur stdDeviation="2.4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="noise" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".78" numOctaves="2" seed="12"/><feColorMatrix values="0 0 0 0 1 0 0 0 0 .50 0 0 0 0 0 0 0 0 .045 0"/></filter>
    <clipPath id="screenClip"><rect x="24" y="18" width="852" height="414" rx="18"/></clipPath>
    <style>
      text{{font-family:{MONO};font-size:19px;font-weight:600;letter-spacing:.15px}}
      .text,.prompt{{fill:#f08619;filter:url(#bloom)}} .prompt{{fill:#ff9a1f}}
      .chroma{{fill:#ff3b00;opacity:.11;transform:translateX(1.2px)}}
      .terminalText{{animation:jitter 5.2s steps(1,end) infinite}}
      .flicker{{animation:flicker 7.8s steps(1,end) infinite}}
      @keyframes jitter{{0%,22%,24%,63%,65%,100%{{transform:translate(0)}}23%{{transform:translate(.7px,-.2px)}}64%{{transform:translate(-.5px,.2px)}}}}
      @keyframes flicker{{0%,14%,16%,58%,60%,100%{{opacity:1}}15%,59%{{opacity:.94}}}}
      @media (prefers-reduced-motion:reduce){{.terminalText,.flicker{{animation:none}}}}
    </style>
  </defs>
  <rect width="900" height="450" rx="13" fill="#020100"/>
  <g clip-path="url(#screenClip)" class="flicker">
    <rect x="24" y="18" width="852" height="414" rx="18" fill="url(#screen)"/>
    <g class="terminalText">
      {content}
      <g opacity="0">
        <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{finished / TOTAL:.4f};{(finished + 0.03) / TOTAL:.4f};{HOLD_UNTIL / TOTAL:.4f};1" dur="{TOTAL}s" repeatCount="indefinite"/>
        <text x="64" y="344" class="prompt">&gt;</text>
        <rect x="87" y="323" width="12" height="24" fill="#f08619" filter="url(#bloom)"/>
      </g>
    </g>
    <rect x="24" y="18" width="852" height="414" fill="url(#scanlines)" opacity=".82"/>
    <rect x="24" y="-66" width="852" height="66" fill="url(#glowingLine)">
      <animate attributeName="y" values="-66;450" dur="4.8s" repeatCount="indefinite"/>
    </rect>
    <rect x="24" y="-2" width="852" height="2" fill="#ffb132" opacity=".10">
      <animate attributeName="y" values="-2;448" dur="4.8s" begin=".15s" repeatCount="indefinite"/>
    </rect>
    <rect x="24" y="18" width="852" height="414" filter="url(#noise)" opacity=".22"/>
    <rect x="24" y="18" width="852" height="414" rx="18" fill="url(#curve)"/>
  </g>
  <rect x="18" y="12" width="864" height="426" rx="23" fill="none" stroke="#21170f" stroke-width="5"/>
  <path d="M40 20H860" stroke="#cfcfcf" stroke-opacity=".08"/>
</svg>'''

out = Path(__file__).resolve().parent.parent / "assets" / "about-default-amber-typing-scan.svg"
out.write_text(svg, encoding="utf-8")
print("wrote", out, len(svg), "bytes; typing completes at", f"{finished:.2f}s")
