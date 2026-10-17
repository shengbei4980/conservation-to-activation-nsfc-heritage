# -*- coding: utf-8 -*-
"""Figure 9a: project-level output-type presence by research turn."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.colors import to_rgb


def locate_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


ROOT = locate_project_root()
INPUT_FILE = ROOT / "data" / "inputs" / "analysis_dataset_in_scope.csv"
OUT_DIR = ROOT / "outputs" / "reproduced"
FIG_DIR = OUT_DIR / "figures"
SRC_DIR = OUT_DIR / "source_data"
FIGURE_STEM = "figure_outcome_pathway_by_research_turn_stacked_bar_EN_soft_labeled_box"

FIG_DIR.mkdir(parents=True, exist_ok=True)
SRC_DIR.mkdir(parents=True, exist_ok=True)


TURN_LABELS = {
    "本体保护转向": "Object-conservation turn",
    "数字计算转向": "Digital-computational turn",
    "空间活化转向": "Spatial activation turn",
    "社会文化转向": "Socio-cultural turn",
    "风险韧性转向": "Risk-resilience turn",
    "混合转向": "Hybrid turn",
    "传统延续": "Traditional continuity",
}

TURN_ORDER = [
    "Object-conservation turn",
    "Digital-computational turn",
    "Spatial activation turn",
    "Socio-cultural turn",
    "Risk-resilience turn",
    "Hybrid turn",
    "Traditional continuity",
]

TURN_COLORS = {
    "Object-conservation turn": "#8E9BA7",
    "Digital-computational turn": "#80C9C6",
    "Spatial activation turn": "#BCA8D6",
    "Socio-cultural turn": "#B4DEDC",
    "Risk-resilience turn": "#C5D9F7",
    "Hybrid turn": "#CED5DA",
    "Traditional continuity": "#EDF1F4",
}

OUTCOME_LABELS = {
    "期刊论文": "Journal articles",
    "人才培养": "Researcher training",
    "会议论文": "Conference papers",
    "专著": "Monographs",
    "政策规划": "Policy/planning outputs",
    "软件数据库": "Software/database outputs",
    "获奖": "Awards",
    "标准导则": "Standards/guidelines",
    "专利软著": "Patents/software copyrights",
}

OUTCOME_ORDER = [
    "Journal articles",
    "Researcher training",
    "Conference papers",
    "Monographs",
    "Policy/planning outputs",
    "Software/database outputs",
    "Awards",
    "Standards/guidelines",
    "Patents/software copyrights",
]

STRUCTURED_OUTPUT_RULES = {
    "期刊论文": ("Journal articles", "期刊论文数量"),
    "会议论文": ("Conference papers", "会议论文数量"),
    "专著": ("Monographs", "专著数量"),
    "获奖": ("Awards", "获奖"),
}

CODED_OUTPUT_RULES = {
    "人才培养": "Researcher training",
    "政策规划": "Policy/planning outputs",
    "软件数据库": "Software/database outputs",
    "标准导则": "Standards/guidelines",
}

PATENT_SOFTWARE_TAG = "专利软著"
PATENT_FIELD = "专利"


FIGURE_CONFIG = {
    "width": 8.8,
    "height": 5.35,
    "dpi": 300,
    "output_dpi": 600,
    "font_family": "Arial",
    "strict_font": False,
    "bar_height": 0.66,
    "bar_alpha": 0.88,
    "edgecolor": "white",
    "edgewidth": 0.60,
    "show_segment_labels": True,
    "segment_label_min_value": 3,
    "segment_label_fontsize": 6.2,
    "segment_label_weight": "bold",
    "segment_label_dark": "#27313A",
    "segment_label_light": "white",
    "frame_color": "#363B42",
    "frame_linewidth": 0.85,
    "grid_color": "#E9EEF3",
    "label_color": "#2F353B",
    "title_color": "#171A1E",
    "note_color": "#68727D",
    "title_fontsize": 10.3,
    "axis_label_fontsize": 8.7,
    "tick_fontsize": 8.0,
    "total_label_fontsize": 7.4,
    "legend_fontsize": 7.5,
    "note_fontsize": 7.3,
    "legend_ncol": 2,
}


def configure_matplotlib() -> None:
    font_name = FIGURE_CONFIG["font_family"]
    available_fonts = {f.name for f in fm.fontManager.ttflist}
    if FIGURE_CONFIG["strict_font"] and font_name not in available_fonts:
        raise RuntimeError(f"{font_name} was not detected by Matplotlib.")

    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [font_name, "Helvetica", "DejaVu Sans", "sans-serif"],
            "axes.spines.top": True,
            "axes.spines.right": True,
            "axes.linewidth": FIGURE_CONFIG["frame_linewidth"],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def split_semicolon_tags(value: object) -> list[str]:
    if pd.isna(value):
        return []
    text = str(value).replace("；", ";")
    return [
        item.strip()
        for item in text.split(";")
        if item.strip() and item.strip().lower() not in {"nan", "none", "null"}
    ]


def positive_count(value: object) -> bool:
    number = pd.to_numeric(pd.Series([value]), errors="coerce").fillna(0).iloc[0]
    return float(number) > 0


def iter_project_output_types(row: pd.Series):
    tags = set(split_semicolon_tags(row.get("outcome_pathway", "")))

    for output_cn, (output_en, field) in STRUCTURED_OUTPUT_RULES.items():
        if positive_count(row.get(field, 0)):
            yield output_cn, output_en, "structured_final_report_count"

    for output_cn, output_en in CODED_OUTPUT_RULES.items():
        if output_cn in tags:
            yield output_cn, output_en, "coded_output_pathway_label"

    if positive_count(row.get(PATENT_FIELD, 0)) or PATENT_SOFTWARE_TAG in tags:
        yield (
            PATENT_SOFTWARE_TAG,
            OUTCOME_LABELS[PATENT_SOFTWARE_TAG],
            "structured_patent_count_or_coded_software_label",
        )


def luminance(hex_color: str) -> float:
    r, g, b = to_rgb(hex_color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def label_color_for_segment(hex_color: str) -> str:
    return (
        FIGURE_CONFIG["segment_label_light"]
        if luminance(hex_color) < 0.55
        else FIGURE_CONFIG["segment_label_dark"]
    )


def build_source_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    required_cols = [
        "approval_no",
        "scope",
        "outcome_pathway",
        "turn_type",
        PATENT_FIELD,
        *[field for _, field in STRUCTURED_OUTPUT_RULES.values()],
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[df["scope"].astype(str).str.strip().eq("in_scope")].copy()
    if len(df) != 142:
        print(f"Warning: expected 142 in-scope projects, found {len(df)}.")

    records: list[dict[str, object]] = []

    for _, row in df.iterrows():
        turn_en = TURN_LABELS.get(str(row["turn_type"]).strip())
        if turn_en is None:
            continue

        for output_cn, output_en, presence_source in iter_project_output_types(row):
            records.append(
                {
                    "approval_no": row["approval_no"],
                    "output_type_cn": output_cn,
                    "output_type": output_en,
                    "output_presence_source": presence_source,
                    "turn_type_cn": row["turn_type"],
                    "research_turn": turn_en,
                }
            )

    long_hits = pd.DataFrame(records)
    if long_hits.empty:
        raise ValueError("No project-level output-type hits were found.")

    counts = (
        long_hits.groupby(
            ["output_type_cn", "output_type", "turn_type_cn", "research_turn"],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "project_hits"})
    )

    matrix = (
        counts.pivot_table(
            index="output_type",
            columns="research_turn",
            values="project_hits",
            aggfunc="sum",
            fill_value=0,
        )
        .reindex(index=list(reversed(OUTCOME_ORDER)), columns=TURN_ORDER, fill_value=0)
    )
    matrix["Total"] = matrix.sum(axis=1)

    cn_lookup = counts[["output_type", "output_type_cn"]].drop_duplicates()
    matrix_with_cn = matrix.reset_index().merge(cn_lookup, on="output_type", how="left")
    matrix_with_cn = matrix_with_cn[["output_type_cn", "output_type", *TURN_ORDER, "Total"]]

    return counts, matrix_with_cn


def save_source_data(counts: pd.DataFrame, matrix: pd.DataFrame) -> None:
    counts.to_csv(SRC_DIR / f"{FIGURE_STEM}_long.csv", index=False, encoding="utf-8-sig")
    matrix.to_csv(SRC_DIR / f"{FIGURE_STEM}_matrix.csv", index=False, encoding="utf-8-sig")

    manifest = pd.DataFrame(
        [
            {
                "figure": FIGURE_STEM,
                "panel": "single",
                "source_data": f"source_data/{FIGURE_STEM}_long.csv",
                "description": (
                    "Project-level output-type presence by research turn. "
                    "Structured publication, monograph and award outputs use final-report counts; "
                    "application-oriented outputs use coded output-pathway labels."
                ),
            },
            {
                "figure": FIGURE_STEM,
                "panel": "single",
                "source_data": f"source_data/{FIGURE_STEM}_matrix.csv",
                "description": (
                    "Matrix used for Figure 9a stacked bars. Values are project-level "
                    "output-type hits rather than total output quantities."
                ),
            },
        ]
    )
    manifest.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_source_data_manifest.csv",
        index=False,
        encoding="utf-8-sig",
    )


def draw_figure(matrix: pd.DataFrame) -> plt.Figure:
    plot_df = matrix.set_index("output_type")[TURN_ORDER]
    totals = matrix.set_index("output_type")["Total"]

    fig, ax = plt.subplots(
        figsize=(FIGURE_CONFIG["width"], FIGURE_CONFIG["height"]),
        dpi=FIGURE_CONFIG["dpi"],
    )

    y_labels = list(plot_df.index)
    y_positions = list(range(len(y_labels)))
    left = pd.Series([0] * len(plot_df), index=plot_df.index, dtype=float)

    for turn in TURN_ORDER:
        values = plot_df[turn]
        current_left = left.copy()
        color = TURN_COLORS[turn]
        ax.barh(
            y_positions,
            values,
            left=current_left.values,
            height=FIGURE_CONFIG["bar_height"],
            color=color,
            alpha=FIGURE_CONFIG["bar_alpha"],
            edgecolor=FIGURE_CONFIG["edgecolor"],
            linewidth=FIGURE_CONFIG["edgewidth"],
            label=turn,
        )

        if FIGURE_CONFIG["show_segment_labels"]:
            text_color = label_color_for_segment(color)
            for idx, output_type in enumerate(y_labels):
                value = int(values.loc[output_type])
                if value < FIGURE_CONFIG["segment_label_min_value"]:
                    continue
                x_center = float(current_left.loc[output_type]) + value / 2.0
                ax.text(
                    x_center,
                    idx,
                    str(value),
                    ha="center",
                    va="center",
                    fontsize=FIGURE_CONFIG["segment_label_fontsize"],
                    fontweight=FIGURE_CONFIG["segment_label_weight"],
                    color=text_color,
                    clip_on=True,
                    zorder=5,
                )

        left = left + values

    max_total = int(totals.max())
    for idx, output_type in enumerate(y_labels):
        total = int(totals.loc[output_type])
        ax.text(
            total + max_total * 0.012,
            idx,
            str(total),
            va="center",
            ha="left",
            fontsize=FIGURE_CONFIG["total_label_fontsize"],
            color=FIGURE_CONFIG["label_color"],
        )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(
        y_labels,
        fontsize=FIGURE_CONFIG["tick_fontsize"],
        color=FIGURE_CONFIG["label_color"],
    )
    ax.set_xlabel(
        "Project-output hits",
        fontsize=FIGURE_CONFIG["axis_label_fontsize"],
        color=FIGURE_CONFIG["label_color"],
    )
    ax.set_title(
        "Output pathways by research turn in NSFC-funded heritage studies",
        loc="left",
        fontsize=FIGURE_CONFIG["title_fontsize"],
        fontweight="bold",
        color=FIGURE_CONFIG["title_color"],
        pad=9,
    )
    ax.grid(axis="x", color=FIGURE_CONFIG["grid_color"], linewidth=0.85)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(FIGURE_CONFIG["frame_color"])
        spine.set_linewidth(FIGURE_CONFIG["frame_linewidth"])
    ax.tick_params(
        axis="x",
        labelsize=FIGURE_CONFIG["tick_fontsize"],
        colors=FIGURE_CONFIG["label_color"],
        length=3.2,
        width=0.7,
    )
    ax.tick_params(axis="y", length=0, colors=FIGURE_CONFIG["label_color"])
    ax.set_xlim(0, max_total * 1.18)

    legend = ax.legend(
        ncol=FIGURE_CONFIG["legend_ncol"],
        bbox_to_anchor=(0.0, -0.18, 1.0, 0.12),
        loc="upper left",
        mode="expand",
        frameon=False,
        fontsize=FIGURE_CONFIG["legend_fontsize"],
        handlelength=1.1,
        columnspacing=1.6,
    )
    for text in legend.get_texts():
        text.set_color(FIGURE_CONFIG["label_color"])

    ax.text(
        0,
        -0.30,
        (
            "Bars show project-level output-type hits; structured publication, monograph "
            "and award outputs use final-report counts, while application-oriented outputs "
            "use coded labels."
        ),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FIGURE_CONFIG["note_fontsize"],
        color=FIGURE_CONFIG["note_color"],
    )

    fig.subplots_adjust(left=0.29, right=0.95, top=0.88, bottom=0.28)
    return fig


def save_figure(fig: plt.Figure) -> None:
    for ext in ["png", "pdf", "svg", "tiff"]:
        path = FIG_DIR / f"{FIGURE_STEM}.{ext}"
        save_kwargs = {"bbox_inches": "tight"}
        if ext in {"png", "tiff"}:
            save_kwargs["dpi"] = FIGURE_CONFIG["output_dpi"]
        fig.savefig(path, **save_kwargs)


def main() -> None:
    configure_matplotlib()
    counts, matrix = build_source_data()
    save_source_data(counts, matrix)
    fig = draw_figure(matrix)
    save_figure(fig)
    plt.close(fig)
    print(matrix.to_string(index=False))
    print(f"\nSaved figure and source data to: {OUT_DIR}")


if __name__ == "__main__":
    main()
