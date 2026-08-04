#!/usr/bin/env python3
"""Generate Asttr0's animated, self-hosted contribution telemetry panel."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

USER = "Asttr0"
CONTRIBUTIONS_URL = f"https://github.com/users/{USER}/contributions"
ROOT = Path(__file__).resolve().parent.parent


class ContributionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.days: list[dict] = []
        self.by_id: dict[str, dict] = {}
        self.tooltip_for: str | None = None
        self.tooltip_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = (values.get("class") or "").split()
        if tag == "td" and "ContributionCalendar-day" in classes and values.get("data-date"):
            day = {
                "date": values["data-date"],
                "count": 0,
                "level": int(values.get("data-level") or 0),
            }
            self.days.append(day)
            if values.get("id"):
                self.by_id[values["id"]] = day
        elif tag == "tool-tip" and values.get("for"):
            self.tooltip_for = values["for"]
            self.tooltip_text = []

    def handle_data(self, data: str) -> None:
        if self.tooltip_for:
            self.tooltip_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "tool-tip" or not self.tooltip_for:
            return
        match = re.search(r"([\d,]+) contribution", " ".join(self.tooltip_text), re.I)
        if match and self.tooltip_for in self.by_id:
            self.by_id[self.tooltip_for]["count"] = int(match.group(1).replace(",", ""))
        self.tooltip_for = None
        self.tooltip_text = []


def load_data(source: str | None) -> dict:
    if source:
        return json.loads(Path(source).read_text(encoding="utf-8"))
    request = urllib.request.Request(CONTRIBUTIONS_URL, headers={"User-Agent": "Asttr0-profile-readme"})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    parser = ContributionParser()
    parser.feed(body)
    if not parser.days:
        raise RuntimeError("GitHub returned no contribution calendar cells")
    return {
        "contributions": parser.days,
        "total": {"lastYear": sum(int(day["count"]) for day in parser.days)},
    }


def streak(days: list[dict]) -> int:
    ordered = sorted(days, key=lambda item: item["date"])
    if ordered and ordered[-1]["count"] == 0:
        ordered = ordered[:-1]
    run = 0
    for day in reversed(ordered):
        if day["count"] == 0:
            break
        run += 1
    return run


def render(data: dict) -> str:
    days = sorted(data["contributions"], key=lambda item: item["date"])
    first = dt.date.fromisoformat(days[0]["date"])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    cells = []
    months = []
    seen_months: set[tuple[int, int]] = set()
    colors = ["#151321", "#24304a", "#155e75", "#0891b2", "#67e8f9"]

    cell, gap, left, top = 11, 4, 48, 64
    for day in days:
        date = dt.date.fromisoformat(day["date"])
        delta = (date - start).days
        week, row = delta // 7, (date.weekday() + 1) % 7
        x, y = left + week * (cell + gap), top + row * (cell + gap)
        level = max(0, min(int(day.get("level", 0)), 4))
        delay = min(3.5, 0.035 * week + 0.05 * row)
        cells.append(
            f'<rect class="cell l{level}" x="{x}" y="{y}" width="{cell}" height="{cell}" '
            f'rx="3" fill="{colors[level]}" style="animation-delay:{delay:.2f}s">'
            f'<title>{html.escape(day["date"])}: {int(day["count"])} contributions</title></rect>'
        )
        key = (date.year, date.month)
        if key not in seen_months and date.day <= 7:
            seen_months.add(key)
            months.append(f'<text x="{x}" y="51" class="axis">{date.strftime("%b")}</text>')

    weeks = max((dt.date.fromisoformat(day["date"]) - start).days // 7 for day in days) + 1
    width = left + weeks * (cell + gap) + 24
    height = 215
    total = int(data.get("total", {}).get("lastYear", sum(int(day["count"]) for day in days)))
    active = sum(1 for day in days if int(day["count"]) > 0)
    current = streak(days)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Asttr0 GitHub contribution telemetry">
  <defs>
    <linearGradient id="panel" x1="0" x2="1"><stop stop-color="#0d1117"/><stop offset="1" stop-color="#100d1d"/></linearGradient>
    <linearGradient id="scan" x1="0" x2="1"><stop stop-color="#22d3ee" stop-opacity="0"/><stop offset=".5" stop-color="#22d3ee" stop-opacity=".3"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <clipPath id="body"><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="12"/></clipPath>
    <style>
      text{{font-family:ui-monospace,'JetBrains Mono','Fira Code',Menlo,Consolas,monospace}}
      .axis{{fill:#6b7280;font-size:10px}} .metric{{fill:#e6edf3;font-size:12px;font-weight:700}} .dim{{fill:#7d8590;font-size:11px}}
      .cell{{opacity:0;transform-box:fill-box;transform-origin:center;animation:boot .45s cubic-bezier(.2,.8,.2,1) both}}
      .l3,.l4{{filter:url(#glow)}}
      .sweep{{animation:sweep 5.5s ease-in-out infinite}}
      @keyframes boot{{0%{{opacity:0;transform:scale(.15)}}70%{{opacity:1;transform:scale(1.15)}}100%{{opacity:1;transform:scale(1)}}}}
      @keyframes sweep{{0%,18%{{transform:translateX(-180px);opacity:0}}35%{{opacity:1}}72%,100%{{transform:translateX({width+180}px);opacity:0}}}}
      @media (prefers-reduced-motion:reduce){{.cell{{opacity:1;animation:none}}.sweep{{display:none}}}}
    </style>
  </defs>
  <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="12" fill="url(#panel)" stroke="#30363d"/>
  <g clip-path="url(#body)">
    <rect x="1" y="1" width="{width-2}" height="32" fill="#161b22"/>
    <circle cx="18" cy="17" r="5" fill="#ff5f57"/><circle cx="36" cy="17" r="5" fill="#febc2e"/><circle cx="54" cy="17" r="5" fill="#28c840"/>
    <text x="{width/2:.1f}" y="21" text-anchor="middle" class="dim">asttr0@singularity: ~$ ./telemetry --year</text>
    {''.join(months)}
    <text x="11" y="82" class="axis">MON</text><text x="11" y="112" class="axis">WED</text><text x="11" y="142" class="axis">FRI</text>
    {''.join(cells)}
    <rect class="sweep" x="0" y="50" width="150" height="116" fill="url(#scan)"/>
  </g>
  <text x="{left}" y="191" class="metric">{total:,} CONTRIBUTIONS // LAST 365 DAYS</text>
  <text x="{width-28}" y="191" text-anchor="end" class="dim">ACTIVE DAYS  <tspan class="metric">{active}</tspan>   //   CURRENT STREAK  <tspan class="metric">{current}D</tspan></text>
</svg>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="optional saved API response")
    parser.add_argument("--output", default=str(ROOT / "assets" / "contributions.svg"))
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(load_data(args.input)), encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
