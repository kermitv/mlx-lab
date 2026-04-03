#!/usr/bin/env python3
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CHARTS_DIR = ROOT / "charts"
ROWS_CSV = DATA_DIR / "rows.csv"
ROUTING_JSON = DATA_DIR / "routing_summary.json"

WIDTH = 1200
HEIGHT = 780
MARGIN_L = 110
MARGIN_R = 40
MARGIN_T = 70
MARGIN_B = 90

LANE_COLORS = {"local": "#0f766e", "frontier": "#c2410c"}
TASK_COLORS = {
    "engineering": "#155e75",
    "tooling": "#1d4ed8",
    "debugging": "#b91c1c",
    "architecture": "#7c3aed",
}
BG = "#f3f1ea"
PANEL = "#fffdf8"
INK = "#111827"
MUTED = "#4b5563"
GRID = "#ddd6c8"
AXIS = "#9ca3af"


def load_rows():
    rows = []
    with ROWS_CSV.open() as fh:
        for row in csv.DictReader(fh):
            row["latency_sec"] = float(row["latency_sec"])
            row["tokens_in"] = int(row["tokens_in"]) if row["tokens_in"] else None
            row["tokens_out"] = int(row["tokens_out"]) if row["tokens_out"] else None
            row["retries_used"] = int(row["retries_used"])
            row["score_accuracy"] = float(row["score_accuracy"])
            row["score_structure"] = float(row["score_structure"])
            row["score_hallucination_risk"] = float(row["score_hallucination_risk"])
            row["score_operational"] = float(row["score_operational"])
            rows.append(row)
    return rows


def load_routing():
    return json.loads(ROUTING_JSON.read_text())


def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_doc(body, title):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<style>
  .title {{ font: 700 30px Georgia, 'Times New Roman', serif; fill: {INK}; }}
  .subtitle {{ font: 500 14px ui-sans-serif, system-ui, -apple-system, sans-serif; fill: {MUTED}; }}
  .axis {{ stroke: {AXIS}; stroke-width: 1.5; }}
  .grid {{ stroke: {GRID}; stroke-width: 1; }}
  .label {{ font: 12px ui-sans-serif, system-ui, -apple-system, sans-serif; fill: #374151; }}
  .small {{ font: 11px ui-sans-serif, system-ui, -apple-system, sans-serif; fill: {MUTED}; }}
  .legend {{ font: 12px ui-sans-serif, system-ui, -apple-system, sans-serif; fill: {INK}; }}
</style>
<rect width="100%" height="100%" fill="{BG}"/>
<rect x="24" y="24" width="{WIDTH-48}" height="{HEIGHT-48}" rx="26" fill="{PANEL}" stroke="#e7e1d6"/>
<text x="{MARGIN_L}" y="38" class="title">{esc(title)}</text>
{body}
</svg>
"""


def write(path, body, title):
    path.write_text(svg_doc(body, title))


def map_x(value, x_min, x_max):
    plot_w = WIDTH - MARGIN_L - MARGIN_R
    return MARGIN_L + (value - x_min) / (x_max - x_min) * plot_w


def map_y(value, y_min, y_max):
    plot_h = HEIGHT - MARGIN_T - MARGIN_B
    return HEIGHT - MARGIN_B - (value - y_min) / (y_max - y_min) * plot_h


def add_axes(x_label, y_label, x_ticks, y_ticks, x_min, x_max, y_min, y_max):
    parts = []
    parts.append(f'<line x1="{MARGIN_L}" y1="{HEIGHT-MARGIN_B}" x2="{WIDTH-MARGIN_R}" y2="{HEIGHT-MARGIN_B}" class="axis"/>')
    parts.append(f'<line x1="{MARGIN_L}" y1="{MARGIN_T}" x2="{MARGIN_L}" y2="{HEIGHT-MARGIN_B}" class="axis"/>')
    for tick in x_ticks:
        x = map_x(tick, x_min, x_max)
        parts.append(f'<line x1="{x:.1f}" y1="{MARGIN_T}" x2="{x:.1f}" y2="{HEIGHT-MARGIN_B}" class="grid"/>')
        parts.append(f'<text x="{x:.1f}" y="{HEIGHT-MARGIN_B+24}" text-anchor="middle" class="label">{esc(tick)}</text>')
    for tick in y_ticks:
        y = map_y(tick, y_min, y_max)
        parts.append(f'<line x1="{MARGIN_L}" y1="{y:.1f}" x2="{WIDTH-MARGIN_R}" y2="{y:.1f}" class="grid"/>')
        parts.append(f'<text x="{MARGIN_L-12}" y="{y+4:.1f}" text-anchor="end" class="label">{esc(tick)}</text>')
    parts.append(f'<text x="{(MARGIN_L + WIDTH - MARGIN_R)/2:.1f}" y="{HEIGHT-28}" text-anchor="middle" class="legend">{esc(x_label)}</text>')
    parts.append(f'<text x="26" y="{(MARGIN_T + HEIGHT - MARGIN_B)/2:.1f}" text-anchor="middle" transform="rotate(-90 26 {(MARGIN_T + HEIGHT - MARGIN_B)/2:.1f})" class="legend">{esc(y_label)}</text>')
    return "".join(parts)


def chart_quality_vs_latency(rows):
    x_min, x_max = 0, 46
    y_min, y_max = 0, 10.5
    parts = [add_axes("Latency (sec)", "Accuracy Score", [5, 10, 20, 30, 40], [0, 2, 4, 6, 8, 10], x_min, x_max, y_min, y_max)]
    for row in rows:
        x = map_x(row["latency_sec"], x_min, x_max)
        y = map_y(row["score_accuracy"], y_min, y_max)
        radius = 8 + min(row["tokens_out"] or 0, 1600) / 250.0
        color = LANE_COLORS[row["lane"]]
        stroke = TASK_COLORS[row["task_class"]]
        dash = "4 3" if row["finish_reason"] not in {"stop", "completed"} else "none"
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{color}" fill-opacity="0.72" stroke="{stroke}" stroke-width="2" stroke-dasharray="{dash}">'
            f'<title>{esc(row["task"])} | {esc(row["model"])} | latency {row["latency_sec"]:.3f}s | accuracy {row["score_accuracy"]:.2f}</title></circle>'
        )
        parts.append(f'<text x="{x+radius+4:.1f}" y="{y-2:.1f}" class="small">{esc(row["model"])}</text>')
    legend_y = 78
    parts.append(f'<text x="{WIDTH-255}" y="{legend_y-18}" class="legend">Lane / outline by task</text>')
    for idx, (lane, color) in enumerate(LANE_COLORS.items()):
        y = legend_y + idx * 24
        parts.append(f'<circle cx="{WIDTH-245}" cy="{y}" r="7" fill="{color}" fill-opacity="0.72" stroke="#111827" stroke-width="1"/>')
        parts.append(f'<text x="{WIDTH-228}" y="{y+4}" class="label">{esc(lane)}</text>')
    for idx, (task_class, color) in enumerate(TASK_COLORS.items()):
        y = legend_y + 60 + idx * 22
        parts.append(f'<rect x="{WIDTH-252}" y="{y-8}" width="14" height="14" fill="white" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{WIDTH-228}" y="{y+4}" class="label">{esc(task_class)}</text>')
    parts.append(f'<text x="{MARGIN_L}" y="{HEIGHT-8}" class="small">Circle size approximates tokens out. Dashed outline marks non-clean finish reasons.</text>')
    write(CHARTS_DIR / "quality_vs_latency.svg", "".join(parts), "Run 4 Quality vs Latency")


def lerp_color(value):
    # 0 -> pale, 10 -> saturated teal
    start = (243, 244, 246)
    end = (15, 118, 110)
    t = max(0.0, min(1.0, value / 10.0))
    rgb = tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))
    return "#%02x%02x%02x" % rgb


def ordered_unique(values):
    seen = set()
    ordered = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def chart_task_model_heatmap(rows):
    tasks = ordered_unique(row["task"] for row in rows)
    models = ordered_unique(row["model"] for row in rows)
    lookup = {(r["task"], r["model"]): r for r in rows}
    cell_w = max(120, min(150, math.floor((WIDTH - 320) / max(len(models), 1))))
    cell_h = 110
    origin_x = 240
    origin_y = 150
    parts = ['<text x="110" y="82" class="subtitle">Accuracy heatmap with finish-state badges</text>']
    for c, model in enumerate(models):
        x = origin_x + c * cell_w + cell_w / 2
        parts.append(f'<text x="{x:.1f}" y="{origin_y-18}" text-anchor="middle" class="label">{esc(model)}</text>')
    for r_idx, task in enumerate(tasks):
        y = origin_y + r_idx * cell_h + cell_h / 2
        parts.append(f'<text x="{origin_x-18}" y="{y+4:.1f}" text-anchor="end" class="label">{esc(task)}</text>')
        for c, model in enumerate(models):
            row = lookup.get((task, model))
            if row is None:
                continue
            x = origin_x + c * cell_w
            y0 = origin_y + r_idx * cell_h
            fill = lerp_color(row["score_accuracy"])
            parts.append(f'<rect x="{x}" y="{y0}" width="{cell_w-8}" height="{cell_h-8}" rx="12" fill="{fill}" stroke="#d1d5db"/>')
            parts.append(f'<text x="{x+18}" y="{y0+35}" class="legend" fill="#111827">{row["score_accuracy"]:.1f}</text>')
            parts.append(f'<text x="{x+18}" y="{y0+58}" class="small">lat {row["latency_sec"]:.1f}s</text>')
            parts.append(f'<text x="{x+18}" y="{y0+78}" class="small">ops {row["score_operational"]:.1f}</text>')
            badge = row["finish_reason"]
            badge_fill = "#dcfce7" if badge in {"stop", "completed"} else "#fef3c7"
            parts.append(f'<rect x="{x+cell_w-72}" y="{y0+16}" width="52" height="20" rx="10" fill="{badge_fill}" stroke="#9ca3af"/>')
            parts.append(f'<text x="{x+cell_w-46}" y="{y0+30}" text-anchor="middle" class="small">{esc(badge)}</text>')
    parts.append(f'<text x="{origin_x}" y="{origin_y + len(tasks)*cell_h + 28}" class="small">Darker teal means higher accuracy. Amber badges indicate length/incomplete finishes.</text>')
    write(CHARTS_DIR / "task_model_heatmap.svg", "".join(parts), "Run 4 Task by Model Heatmap")


def chart_frontier_vs_local_gap(routing):
    task_classes = [item["task_class"] for item in routing]
    origin_x = 170
    origin_y = 120
    row_h = 130
    center_x = 570
    scale = 85
    parts = [
        f'<line x1="{center_x}" y1="{origin_y-20}" x2="{center_x}" y2="{origin_y + len(task_classes)*row_h}" class="axis"/>',
        f'<text x="{center_x-120}" y="{origin_y-42}" class="legend">Local better</text>',
        f'<text x="{center_x+32}" y="{origin_y-42}" class="legend">Frontier better</text>',
    ]
    for idx, item in enumerate(routing):
        y = origin_y + idx * row_h
        q_gap = item["quality_gap_frontier_vs_best_local"]
        o_gap = item["operational_gap_frontier_vs_best_local"]
        parts.append(f'<text x="{origin_x}" y="{y+18}" class="legend">{esc(item["task_class"])}</text>')
        parts.append(f'<text x="{origin_x}" y="{y+40}" class="small">route: {esc(item["recommended_route"])}</text>')
        q_len = q_gap * scale
        o_len = o_gap * scale
        q_x = center_x if q_len >= 0 else center_x + q_len
        o_x = center_x if o_len >= 0 else center_x + o_len
        parts.append(f'<rect x="{q_x:.1f}" y="{y+56}" width="{abs(q_len):.1f}" height="20" fill="#2563eb" rx="8"/>')
        parts.append(f'<text x="{center_x + (q_len if q_len >= 0 else q_len) + (10 if q_len >= 0 else -10):.1f}" y="{y+71}" text-anchor="{"start" if q_len>=0 else "end"}" class="small">quality {q_gap:+.2f}</text>')
        parts.append(f'<rect x="{o_x:.1f}" y="{y+84}" width="{abs(o_len):.1f}" height="20" fill="#d97706" rx="8"/>')
        parts.append(f'<text x="{center_x + (o_len if o_len >= 0 else o_len) + (10 if o_len >= 0 else -10):.1f}" y="{y+99}" text-anchor="{"start" if o_len>=0 else "end"}" class="small">operational {o_gap:+.2f}</text>')
        parts.append(f'<text x="{origin_x+320}" y="{y+116}" class="small">{esc(item["best_local_specialist"])} vs {esc(item["best_frontier"])}</text>')
    parts.append(f'<rect x="{WIDTH-280}" y="{MARGIN_T}" width="14" height="14" fill="#2563eb" rx="3"/><text x="{WIDTH-260}" y="{MARGIN_T+12}" class="label">quality gap</text>')
    parts.append(f'<rect x="{WIDTH-280}" y="{MARGIN_T+24}" width="14" height="14" fill="#d97706" rx="3"/><text x="{WIDTH-260}" y="{MARGIN_T+36}" class="label">operational gap</text>')
    write(CHARTS_DIR / "frontier_vs_local_gap.svg", "".join(parts), "Run 4 Frontier vs Local Gaps by Task Class")


def chart_operational_vs_quality(rows):
    x_min, x_max = 7.0, 10.5
    y_min, y_max = 4.0, 10.5
    parts = [add_axes("Operational Score", "Accuracy Score", [7, 8, 9, 10], [4, 5, 6, 7, 8, 9, 10], x_min, x_max, y_min, y_max)]
    mid_x = map_x(9.0, x_min, x_max)
    mid_y = map_y(8.5, y_min, y_max)
    parts.append(f'<line x1="{mid_x}" y1="{MARGIN_T}" x2="{mid_x}" y2="{HEIGHT-MARGIN_B}" stroke="#9ca3af" stroke-dasharray="5 4"/>')
    parts.append(f'<line x1="{MARGIN_L}" y1="{mid_y}" x2="{WIDTH-MARGIN_R}" y2="{mid_y}" stroke="#9ca3af" stroke-dasharray="5 4"/>')
    labels = [
        (mid_x - 170, MARGIN_T + 24, "High quality, lower ops"),
        (mid_x + 20, MARGIN_T + 24, "High quality, strong ops"),
        (mid_x - 150, HEIGHT - MARGIN_B - 16, "Weak quality, lower ops"),
        (mid_x + 20, HEIGHT - MARGIN_B - 16, "Weak quality, strong ops"),
    ]
    for x, y, text in labels:
        parts.append(f'<text x="{x}" y="{y}" class="small">{esc(text)}</text>')
    for row in rows:
        x = map_x(row["score_operational"], x_min, x_max)
        y = map_y(row["score_accuracy"], y_min, y_max)
        if row["lane"] == "local":
            diamond = [
                (x, y - 10),
                (x + 10, y),
                (x, y + 10),
                (x - 10, y),
            ]
            points = " ".join(f"{px:.1f},{py:.1f}" for px, py in diamond)
            parts.append(f'<polygon points="{points}" fill="{TASK_COLORS[row["task_class"]]}" fill-opacity="0.78" stroke="#111827" stroke-width="1.2"><title>{esc(row["task"])} | {esc(row["model"])}</title></polygon>')
        else:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{TASK_COLORS[row["task_class"]]}" fill-opacity="0.78" stroke="#111827" stroke-width="1.2"><title>{esc(row["task"])} | {esc(row["model"])}</title></circle>')
        parts.append(f'<text x="{x+12:.1f}" y="{y-2:.1f}" class="small">{esc(row["model"])}</text>')
    legend_x = WIDTH - 285
    legend_y = 78
    parts.append(f'<text x="{legend_x}" y="{legend_y-20}" class="legend">Shape / color</text>')
    parts.append(f'<polygon points="{legend_x+8},{legend_y-8} {legend_x+16},{legend_y} {legend_x+8},{legend_y+8} {legend_x},{legend_y}" fill="#9ca3af" stroke="#111827"/><text x="{legend_x+26}" y="{legend_y+4}" class="label">local</text>')
    parts.append(f'<circle cx="{legend_x+8}" cy="{legend_y+26}" r="8" fill="#9ca3af" stroke="#111827"/><text x="{legend_x+26}" y="{legend_y+30}" class="label">frontier</text>')
    for idx, (task_class, color) in enumerate(TASK_COLORS.items()):
        y = legend_y + 60 + idx * 22
        parts.append(f'<rect x="{legend_x}" y="{y-10}" width="14" height="14" fill="{color}" rx="3"/>')
        parts.append(f'<text x="{legend_x+22}" y="{y+2}" class="label">{esc(task_class)}</text>')
    write(CHARTS_DIR / "operational_vs_quality.svg", "".join(parts), "Run 4 Operational vs Quality Quadrants")


def write_readme():
    text = """# Run 4 Charts

This chart set is generated from `benchmarks/run4/data/rows.csv` and `benchmarks/run4/data/routing_summary.json`.

Files:
- `quality_vs_latency.svg`: shows the quality/latency tradeoff by model and task.
- `task_model_heatmap.svg`: shows per-task accuracy across all models with finish-state badges.
- `frontier_vs_local_gap.svg`: shows how much frontier beats or trails the best local result by task class.
- `operational_vs_quality.svg`: shows which results are strongest as unattended defaults versus strongest by answer quality.

Notes:
- The environment did not have plotting libraries installed, so these charts are emitted as dependency-free SVGs.
- These visuals are presentation artifacts derived from the Run 4 data layer; they are not new benchmark evidence.
"""
    (CHARTS_DIR / "README.md").write_text(text)


def main():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    routing = load_routing()
    chart_quality_vs_latency(rows)
    chart_task_model_heatmap(rows)
    chart_frontier_vs_local_gap(routing)
    chart_operational_vs_quality(rows)
    write_readme()


if __name__ == "__main__":
    main()
