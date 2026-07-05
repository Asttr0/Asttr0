#!/usr/bin/env python3
"""Generate assets/whoami.svg — an animated terminal that 'types' a whoami +
self-scan session on an infinite loop. Pure SMIL/CSS, so it animates when
embedded as an <img> in the GitHub README (scripts are stripped, animations
are not). All reveal times live on a common T-second clock so the loop is
perfectly periodic."""

W, H = 860, 470
T = 15.0                # loop duration (s)
PAD_X = 26              # left padding of terminal body
TOP = 74                # first baseline y
LH = 27                 # line height
FS = 15                 # font size
CW = 9.0                # monospace advance at 15px (0.6em)
MONO = "ui-monospace,'JetBrains Mono','Fira Code','Cascadia Code',Menlo,Consolas,monospace"

# palette (matches the cosmic README theme)
C_USER = "#9fef00"      # user@host  (HTB green)
C_PATH = "#a78bfa"      # ~
C_GRAY = "#8b949e"
C_DIM  = "#484f58"
C_CMD  = "#e6edf3"
C_LBL  = "#22d3ee"
C_VAL  = "#c9d1d9"
C_OK   = "#9fef00"
C_WARN = "#e879f9"

parts = []

def k(t):  # keyTime on the loop clock
    return f"{max(0.0, min(t / T, 1.0)):.4f}"

def reveal(t, dur=0.06):
    """opacity 0 until t, then 1 (snaps back to 0 at loop restart)."""
    return (f'<animate attributeName="opacity" values="0;0;1;1" '
            f'keyTimes="0;{k(t)};{k(t + dur)};1" dur="{T}s" repeatCount="indefinite"/>')

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def prompt_spans(x, y):
    """asttr0@singularity:~$  — every char on the same CW grid the typed
    commands use, so prompt/command/cursor stay aligned whatever monospace
    font the viewer's browser picks (their advances differ slightly)."""
    cols = ([(c, C_USER, ' font-weight="600"') for c in "asttr0@singularity"]
            + [(":", C_GRAY, ""), ("~", C_PATH, ""), ("$", C_GRAY, "")])
    out = []
    for i, (ch, col, extra) in enumerate(cols):
        out.append(f'<text x="{x + i * CW:.1f}" y="{y}" font-family="{MONO}" '
                   f'font-size="{FS}" fill="{col}"{extra}>{esc(ch)}</text>')
    return "".join(out), x + 22 * CW  # 22 cols incl. trailing space

def typed_command(x0, y, cmd, t0, dt):
    """Per-char typing + a block cursor that steps along and disappears."""
    out = [f'<g opacity="0">{reveal(t0 - 0.02)}']
    for i, ch in enumerate(cmd):
        cx = x0 + i * CW
        out.append(f'<text x="{cx:.1f}" y="{y}" font-family="{MONO}" font-size="{FS}" '
                   f'fill="{C_CMD}" opacity="0">{esc(ch)}{reveal(t0 + i * dt, 0.02)}</text>')
    # stepping cursor: discrete x jumps, visible only during the typing window
    n = len(cmd)
    xs = ";".join(f"{x0 + i * CW:.1f}" for i in range(n + 1))
    kt = ";".join(k(t0 + i * dt) for i in range(n + 1))
    t_end = t0 + n * dt
    out.append(
        f'<rect y="{y - FS + 2}" width="{CW:.1f}" height="{FS + 3}" fill="{C_CMD}" opacity="0">'
        f'<animate attributeName="x" values="{xs}" keyTimes="{kt}" calcMode="discrete" '
        f'dur="{T}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0;0;0.85;0.85;0;0" '
        f'keyTimes="0;{k(t0 - 0.01)};{k(t0)};{k(t_end)};{k(t_end + 0.05)};1" '
        f'dur="{T}s" repeatCount="indefinite"/></rect>')
    out.append('</g>')
    return "".join(out)

def out_line(y, spans, t):
    body = "".join(f'<tspan fill="{c}"{extra}>{esc(s)}</tspan>' for s, c, extra in spans)
    return (f'<g opacity="0"><text x="{PAD_X}" y="{y}" font-family="{MONO}" '
            f'font-size="{FS}">{body}</text>{reveal(t)}</g>')

def scan_line(label, value, color=C_VAL, tag="[+]", tagc=C_OK, italic=False):
    dots = "." * (14 - len(label))
    extra = ' font-style="italic"' if italic else ""
    return [(f"{tag} ", tagc, ' font-weight="600"'),
            (f"{label} ", C_LBL, ""),
            (f"{dots} ", C_DIM, ""),
            (value, color, extra)]

y = TOP
# ── line 1: $ whoami ─────────────────────────────────────────────
p1, cx1 = prompt_spans(PAD_X, y)
parts.append(f'<g opacity="0">{p1}{reveal(0.35)}</g>')
parts.append(typed_command(cx1, y, "whoami", 0.55, 0.085))
y += LH
# ── line 2: identity ─────────────────────────────────────────────
parts.append(out_line(y, [("Mohamed Taha Slimani", "#ffffff", ' font-weight="600"'),
                          ("  ·  CS engineering student  ·  Morocco", C_GRAY, "")], 1.35))
y += int(LH * 1.35)
# ── line 3: $ ./asttr0 --scan self ───────────────────────────────
p2, cx2 = prompt_spans(PAD_X, y)
parts.append(f'<g opacity="0">{p2}{reveal(2.05)}</g>')
parts.append(typed_command(cx2, y, "./asttr0 --scan self", 2.25, 0.062))
y += LH
# ── line 4: progress bar ─────────────────────────────────────────
t_bar0, t_bar1 = 3.85, 5.35
bar_x = PAD_X + 20 * CW; bar_w = 300
parts.append(
    f'<g opacity="0">'
    f'<text x="{PAD_X}" y="{y}" font-family="{MONO}" font-size="{FS}" fill="{C_GRAY}">'
    f'scanning subject &#8230;</text>'
    f'<rect x="{bar_x}" y="{y - FS + 3}" width="{bar_w}" height="{FS - 1}" rx="4" fill="#21262d"/>'
    f'<rect x="{bar_x}" y="{y - FS + 3}" height="{FS - 1}" rx="4" fill="url(#scangrad)">'
    f'<animate attributeName="width" values="0;0;{bar_w};{bar_w}" '
    f'keyTimes="0;{k(t_bar0)};{k(t_bar1)};1" dur="{T}s" repeatCount="indefinite"/></rect>'
    f'<g opacity="0"><text x="{bar_x + bar_w + 14}" y="{y}" font-family="{MONO}" '
    f'font-size="{FS}" fill="{C_OK}">100%</text>{reveal(t_bar1)}</g>'
    f'{reveal(t_bar0 - 0.1)}</g>')
y += int(LH * 1.35)
# ── results ──────────────────────────────────────────────────────
results = [
    scan_line("offense",  "web exploitation · recon · bug bounty @ Intigriti"),
    scan_line("defense",  "detection · hardening · WAF internals"),
    scan_line("builds",   "software that closes security gaps"),
    scan_line("arena",    "HackTheBox · Intigriti · CTFs"),
    scan_line("motto",    "“learn how it breaks. build what defends it.”",
              color=C_WARN, tag="[!]", tagc=C_WARN, italic=True),
]
t = 5.75
for spans in results:
    parts.append(out_line(y, spans, t))
    y += LH; t += 0.42
# ── [ok] line ────────────────────────────────────────────────────
parts.append(out_line(y, [("[ok] ", C_OK, ' font-weight="600"'),
                          ("scan complete — no known patch for curiosity", C_GRAY, "")], t + 0.35))
y += int(LH * 1.35)
# ── final prompt + blinking cursor ───────────────────────────────
p3, cx3 = prompt_spans(PAD_X, y)
t_fin = t + 1.0
parts.append(
    f'<g opacity="0">{p3}'
    f'<rect x="{cx3:.1f}" y="{y - FS + 2}" width="{CW:.1f}" height="{FS + 3}" fill="{C_CMD}">'
    f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
    f'dur="1.1s" repeatCount="indefinite"/></rect>'
    f'{reveal(t_fin)}</g>')

body = "\n  ".join(parts)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="animated terminal: whoami — Mohamed Taha Slimani, cybersecurity enthusiast">
  <defs>
    <linearGradient id="scangrad" x1="0" x2="1">
      <stop offset="0%" stop-color="#22d3ee"/><stop offset="55%" stop-color="#7c3aed"/><stop offset="100%" stop-color="#e879f9"/>
    </linearGradient>
    <linearGradient id="sweepgrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.025"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="term"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12"/></clipPath>
    <style>.sweep{{animation:sweep 8s linear infinite}}@keyframes sweep{{0%{{transform:translateY(-70px)}}100%{{transform:translateY({H + 70}px)}}}}@media (prefers-reduced-motion:reduce){{.sweep{{animation:none}}}}</style>
  </defs>
  <!-- window -->
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="#0d1117" stroke="#7c3aed" stroke-opacity="0.55" stroke-width="1.5"/>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="none" stroke="#22d3ee" stroke-opacity="0.12" stroke-width="4"/>
  <!-- title bar -->
  <g clip-path="url(#term)">
    <rect x="1" y="1" width="{W - 2}" height="42" fill="#161b22"/>
    <circle cx="26" cy="22" r="6.5" fill="#ff5f57"/><circle cx="48" cy="22" r="6.5" fill="#febc2e"/><circle cx="70" cy="22" r="6.5" fill="#28c840"/>
    <text x="{W / 2}" y="27" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#8b949e">asttr0@singularity: ~</text>
  </g>
  <!-- session -->
  {body}
  <!-- CRT sweep -->
  <g clip-path="url(#term)"><rect class="sweep" x="1" width="{W - 2}" height="70" fill="url(#sweepgrad)"/></g>
</svg>'''

open("/home/Asttr0/github-profile/assets/whoami.svg", "w").write(svg)
print("wrote assets/whoami.svg", len(svg), "bytes")
