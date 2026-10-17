# -*- coding: utf-8 -*-
"""Figure 9b: stage-wise project-level output-type presence by research turn."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch


def locate_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


ROOT = locate_project_root()
INPUT_FILE = ROOT / "data" / "inputs" / "analysis_dataset_in_scope.csv"
OUT_DIR = ROOT / "outputs" / "reproduced"
FIG_DIR = OUT_DIR / "figures" / "stage_small_multiples"
SRC_DIR = OUT_DIR / "source_data" / "stage_small_multiples"
FIGURE_STEM = "figure_outcome_pathway_by_stage_research_turn_stacked_bar_EN_labeled_box"

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

STAGE_DEFS = [
    {
        "key": "agenda_formation",
        "label": "Agenda formation\n(2008-2012)",
        "short_label": "Agenda formation",
        "range": (2008, 2012),
        "accent": "#89B2F4",
    },
    {
        "key": "object_method_expansion",
        "label": "Object-method expansion\n(2013-2017)",
        "short_label": "Object-method expansion",
        "range": (2013, 2017),
        "accent": "#018C94",
    },
    {
        "key": "compound_agenda_strengthening",
        "label": "Compound agenda strengthening\n(2018-2022)",
        "short_label": "Compound agenda strengthening",
        "range": (2018, 2022),
        "accent": "#764D9C",
    },
]


FIGURE_CONFIG = {
    "font_family": "Arial",
    "strict_font": False,
    "individual_width": 5.9,
    "individual_height": 3.95,
    "combined_width": 13.2,
    "combined_height": 5.4,
    "dpi": 300,
    "output_dpi": 600,
    "bar_height": 0.62,
    "bar_alpha": 0.90,
    "edgecolor": "white",
    "edgewidth": 0.50,
    "show_segment_labels": True,
    "segment_label_min_value": 2,
    "segment_label_fontsize": 5.6,
    "segment_label_weight": "bold",
    "segment_label_dark": "#26313B",
    "segment_label_light": "white",
    "frame_color": "#31343A",
    "frame_linewidth": 0.78,
    "grid_color": "#E8EDF3",
    "label_color": "#252A30",
    "tick_fontsize": 7.1,
    "axis_label_fontsize": 7.8,
    "title_fontsize": 8.2,
    "total_label_fontsize": 6.8,
    "legend_fontsize": 6.9,
}


def configure_matplotlib() -> None:
    font_name = FIGURE_CONFIG["font_family"]
    available = {f.name for f in fm.fontManager.ttflist}
    if FIGURE_CONFIG["strict_font"] and font_name not in available:
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


def assign_stage(year: float) -> dict[str, object] | None:
    if pd.isna(year):
        return None
    year_int = int(year)
    for stage in STAGE_DEFS:
        start, end = stage["range"]
        if start <= year_int <= end:
            return stage
    return None


def luminance(hex_color: str) -> float:
    r, g, b = to_rgb(hex_color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def label_color_for_segment(hex_color: str) -> str:
    return (
        FIGURE_CONFIG["segment_label_light"]
        if luminance(hex_color) < 0.56
        else FIGURE_CONFIG["segment_label_dark"]
    )


def build_stage_source_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    required = [
        "approval_no",
        "scope",
        "outcome_pathway",
        "turn_type",
        "start_year_filled",
        PATENT_FIELD,
        *[field for _, field in STRUCTURED_OUTPUT_RULES.values()],
    ]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[df["scope"].astype(str).str.strip().eq("in_scope")].copy()
    if len(df) != 142:
        print(f"Warning: expected 142 in-scope projects, found {len(df)}.")

    records: list[dict[str, object]] = []

    for _, row in df.iterrows():
        stage = assign_stage(row["start_year_filled"])
        if stage is None:
            continue

        turn_en = TURN_LABELS.get(str(row["turn_type"]).strip())
        if turn_en is None:
            continue

        for output_cn, output_en, presence_source in iter_project_output_types(row):
            records.append(
                {
                    "approval_no": row["approval_no"],
                    "project_start_year": int(row["start_year_filled"]),
                    "stage_key": stage["key"],
                    "stage": stage["short_label"],
                    "stage_range": f"{stage['range'][0]}-{stage['range'][1]}",
                    "output_type_cn": output_cn,
                    "output_type": output_en,
                    "output_presence_source": presence_source,
                    "turn_type_cn": row["turn_type"],
                    "research_turn": turn_en,
                }
            )

    long_hits = pd.DataFrame(records)
    if long_hits.empty:
        raise ValueError("No stage-wise project-output hits were found.")

    counts = (
        long_hits.groupby(
            [
                "stage_key",
                "stage",
                "stage_range",
                "output_type_cn",
                "output_type",
                "turn_type_cn",
                "research_turn",
            ],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "project_hits"})
    )

    matrix_rows = []
    for stage in STAGE_DEFS:
        stage_counts = counts[counts["stage_key"].eq(stage["key"])]
        pivot = (
            stage_counts.pivot_table(
                index="output_type",
                columns="research_turn",
                values="project_hits",
                aggfunc="sum",
                fill_value=0,
            )
            .reindex(index=OUTCOME_ORDER, columns=TURN_ORDER, fill_value=0)
        )
        pivot["Total"] = pivot.sum(axis=1)
        pivot = pivot.reset_index()
        pivot.insert(0, "stage_range", f"{stage['range'][0]}-{stage['range'][1]}")
        pivot.insert(0, "stage", stage["short_label"])
        pivot.insert(0, "stage_key", stage["key"])
        matrix_rows.append(pivot)

    return counts, pd.concat(matrix_rows, ignore_index=True)


def save_source_data(counts: pd.DataFrame, matrix: pd.DataFrame) -> None:
    counts.to_csv(SRC_DIR / f"{FIGURE_STEM}_long.csv", index=False, encoding="utf-8-sig")
    matrix.to_csv(SRC_DIR / f"{FIGURE_STEM}_matrix.csv", index=False, encoding="utf-8-sig")

    for stage in STAGE_DEFS:
        matrix[matrix["stage_key"].eq(stage["key"])].to_csv(
            SRC_DIR / f"{FIGURE_STEM}_{stage['key']}_matrix.csv",
            index=False,
            encoding="utf-8-sig",
        )

    manifest = pd.DataFrame(
        [
            {
                "figure": FIGURE_STEM,
                "panel": stage["key"],
                "source_data": f"source_data/stage_small_multiples/{FIGURE_STEM}_{stage['key']}_matrix.csv",
                "description": (
                    f"Project-level output-type presence matrix for {stage['short_label']}. "
                    "Structured publication, monograph and award outputs use final-report counts; "
                    "application-oriented outputs use coded output-pathway labels."
                ),
            }
            for stage in STAGE_DEFS
        ]
    )
    manifest.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_source_data_manifest.csv",
        index=False,
        encoding="utf-8-sig",
    )


def get_stage_matrix(matrix: pd.DataFrame, stage_key: str) -> pd.DataFrame:
    sub = matrix[matrix["stage_key"].eq(stage_key)].copy()
    sub = sub.set_index("output_type")[TURN_ORDER + ["Total"]]
    return sub.loc[OUTCOME_ORDER]


def draw_stage_panel(
    ax: plt.Axes,
    stage: dict[str, object],
    stage_matrix: pd.DataFrame,
    max_xlim: int,
    show_y_labels: bool,
) -> None:
    plot_df = stage_matrix[TURN_ORDER]
    totals = stage_matrix["Total"]
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

    for idx, output_type in enumerate(y_labels):
        total = int(totals.loc[output_type])
        if total > 0:
            ax.text(
                total + max_xlim * 0.012,
                idx,
                str(total),
                va="center",
                ha="left",
                fontsize=FIGURE_CONFIG["total_label_fontsize"],
                color=FIGURE_CONFIG["label_color"],
            )

    ax.set_xlim(0, max_xlim)
    ax.set_yticks(y_positions)
    if show_y_labels:
        ax.set_yticklabels(
            y_labels,
            fontsize=FIGURE_CONFIG["tick_fontsize"],
            color=FIGURE_CONFIG["label_color"],
        )
    else:
        ax.set_yticklabels([])
    ax.invert_yaxis()
    ax.grid(axis="x", color=FIGURE_CONFIG["grid_color"], linewidth=0.72)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(FIGURE_CONFIG["frame_color"])
        spine.set_linewidth(FIGURE_CONFIG["frame_linewidth"])
    ax.tick_params(
        axis="x",
        labelsize=FIGURE_CONFIG["tick_fontsize"],
        colors=FIGURE_CONFIG["label_color"],
        length=3.0,
        width=0.65,
    )
    ax.tick_params(axis="y", length=0, colors=FIGURE_CONFIG["label_color"])
    ax.set_title(
        stage["label"],
        loc="left",
        fontsize=FIGURE_CONFIG["title_fontsize"],
        fontweight="bold",
        color=stage["accent"],
        pad=6,
    )


def save_all_formats(fig: plt.Figure, stem: Path) -> None:
    for ext in ["png", "pdf", "svg", "tiff"]:
        kwargs = {"bbox_inches": "tight"}
        if ext in {"png", "tiff"}:
            kwargs["dpi"] = FIGURE_CONFIG["output_dpi"]
        fig.savefig(stem.with_suffix(f".{ext}"), **kwargs)


def draw_combined(matrix: pd.DataFrame) -> plt.Figure:
    max_total = int(matrix["Total"].max())
    max_xlim = int(max_total * 1.20 + 1)

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(FIGURE_CONFIG["combined_width"], FIGURE_CONFIG["combined_height"]),
        dpi=FIGURE_CONFIG["dpi"],
        sharex=True,
    )

    for idx, (ax, stage) in enumerate(zip(axes, STAGE_DEFS)):
        stage_matrix = get_stage_matrix(matrix, stage["key"])
        draw_stage_panel(
            ax=ax,
            stage=stage,
            stage_matrix=stage_matrix,
            max_xlim=max_xlim,
            show_y_labels=(idx == 0),
        )

        if idx == 1:
            ax.set_xlabel(
                "Project-output hits",
                fontsize=FIGURE_CONFIG["axis_label_fontsize"],
                color=FIGURE_CONFIG["label_color"],
            )

    handles = [
        Patch(
            facecolor=TURN_COLORS[turn],
            edgecolor="none",
            label=turn,
            alpha=FIGURE_CONFIG["bar_alpha"],
        )
        for turn in TURN_ORDER
    ]

    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=4,
        frameon=False,
        fontsize=FIGURE_CONFIG["legend_fontsize"],
        bbox_to_anchor=(0.52, -0.02),
    )

    fig.suptitle(
        "Stage-wise output pathways by research turn in NSFC-funded heritage studies",
        x=0.02,
        y=0.99,
        ha="left",
        fontsize=10.4,
        fontweight="bold",
        color=FIGURE_CONFIG["label_color"],
    )
    fig.subplots_adjust(left=0.18, right=0.98, top=0.84, bottom=0.18, wspace=0.18)
    return fig


def draw_individual(matrix: pd.DataFrame, stage: dict[str, object]) -> plt.Figure:
    stage_matrix = get_stage_matrix(matrix, stage["key"])
    max_total = int(stage_matrix["Total"].max())
    max_xlim = int(max_total * 1.24 + 1)

    fig, ax = plt.subplots(
        figsize=(FIGURE_CONFIG["individual_width"], FIGURE_CONFIG["individual_height"]),
        dpi=FIGURE_CONFIG["dpi"],
    )
    draw_stage_panel(
        ax=ax,
        stage=stage,
        stage_matrix=stage_matrix,
        max_xlim=max_xlim,
        show_y_labels=True,
    )
    ax.set_xlabel(
        "Project-output hits",
        fontsize=FIGURE_CONFIG["axis_label_fontsize"],
        color=FIGURE_CONFIG["label_color"],
    )
    fig.subplots_adjust(left=0.38, right=0.96, top=0.86, bottom=0.15)
    return fig


def main() -> None:
    configure_matplotlib()
    counts, matrix = build_stage_source_data()
    save_source_data(counts, matrix)

    combined = draw_combined(matrix)
    save_all_formats(combined, FIG_DIR / FIGURE_STEM)
    plt.close(combined)

    for stage in STAGE_DEFS:
        fig = draw_individual(matrix, stage)
        save_all_formats(fig, FIG_DIR / f"{FIGURE_STEM}_{stage['key']}")
        plt.close(fig)

    print(matrix.to_string(index=False))
    print(f"\nSaved stage-wise figures and source data to: {OUT_DIR}")


if __name__ == "__main__":
    main()
