"""Generate an SVG bar chart comparing strategy scores."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def load_report(path: Path) -> Dict[str, float]:
    data = json.loads(path.read_text())
    return {name: details["average_score"] for name, details in data.items()}


def build_svg(reports: Dict[str, Dict[str, float]], width: int = 900, height: int = 420) -> str:
    strategies: List[str] = sorted({name for scores in reports.values() for name in scores})
    configs = list(reports.keys())
    margin = 70
    chart_width = width - 2 * margin
    chart_height = height - 2 * margin
    bar_group_width = chart_width / max(1, len(strategies))
    bar_width = bar_group_width / max(1, len(configs)) * 0.7
    y_max = 1.0

    def x_pos(strategy_idx: int, config_idx: int) -> float:
        start = margin + strategy_idx * bar_group_width
        offset = (config_idx + 0.5) * bar_width
        return start + offset

    def y_pos(score: float) -> float:
        return margin + chart_height * (1 - score / y_max)

    elements: List[str] = []
    elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    # Background
    elements.append('<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>')
    # Axes
    elements.append(f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{margin + chart_height}" stroke="#333" stroke-width="2"/>')
    elements.append(f'<line x1="{margin}" y1="{margin + chart_height}" x2="{margin + chart_width}" y2="{margin + chart_height}" stroke="#333" stroke-width="2"/>')

    # Horizontal grid lines
    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        y = y_pos(tick)
        elements.append(f'<line x1="{margin}" y1="{y}" x2="{margin + chart_width}" y2="{y}" stroke="#ccc" stroke-width="1" stroke-dasharray="4 4"/>')
        elements.append(f'<text x="{margin - 10}" y="{y + 5}" text-anchor="end" font-size="14" fill="#555">{tick:.2f}</text>')

    palette = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f"]
    for s_idx, strategy in enumerate(strategies):
        for c_idx, config in enumerate(configs):
            score = reports[config].get(strategy, 0.0)
            x = x_pos(s_idx, c_idx)
            y = y_pos(score)
            bar_h = margin + chart_height - y
            color = palette[c_idx % len(palette)]
            elements.append(
                f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_h}" fill="{color}" opacity="0.85">'
                f'<title>{config}: {score:.2f}</title>'
                f'</rect>'
            )
        label = strategy.replace("_", " ").title()
        elements.append(
            f'<text x="{margin + s_idx * bar_group_width + bar_group_width / 2}" '
            f'y="{margin + chart_height + 30}" text-anchor="middle" font-size="14" fill="#333">{label}</text>'
        )

    # Legend
    legend_x = margin + chart_width - 160
    legend_y = margin + 10
    for idx, config in enumerate(configs):
        color = palette[idx % len(palette)]
        y = legend_y + idx * 24
        label = config.replace("_", " ").title()
        elements.append(f'<rect x="{legend_x}" y="{y}" width="18" height="18" fill="{color}" opacity="0.85"/>')
        elements.append(f'<text x="{legend_x + 25}" y="{y + 14}" font-size="14" fill="#333">{label}</text>')

    elements.append(f'<text x="{width / 2}" y="{margin - 30}" text-anchor="middle" font-size="18" fill="#222">'
                    'Prompt Strategy Performance Across Configurations</text>')
    elements.append(f'<text x="{margin - 50}" y="{margin - 10}" text-anchor="middle" font-size="16" fill="#222" transform="rotate(-90 {margin - 50},{margin - 10})">Average Alignment Score</text>')
    elements.append('</svg>')
    return "\n".join(elements)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reports", nargs="+", required=True, help="Paths to JSON reports")
    parser.add_argument("--labels", nargs="*", help="Optional labels for each report")
    parser.add_argument("--output", type=Path, default=Path("analysis/figures/strategy_scores.svg"))
    args = parser.parse_args()

    labels = args.labels if args.labels else [Path(p).stem for p in args.reports]
    if len(labels) != len(args.reports):
        raise ValueError("Number of labels must match number of reports")

    report_scores: Dict[str, Dict[str, float]] = {}
    for label, path_str in zip(labels, args.reports, strict=True):
        path = Path(path_str)
        report_scores[label] = load_report(path)

    svg = build_svg(report_scores)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg)
    print(f"Saved figure to {args.output}")


if __name__ == "__main__":
    main()
