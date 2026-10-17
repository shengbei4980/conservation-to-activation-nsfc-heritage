# -*- coding: utf-8 -*-
"""
 Figure 9. Annual distribution of seven research turns in NSFC-funded heritage studies.

The x-axis reports project start year, the y-axis reports the seven plotted
research-turn families, and the z-axis reports the true annual number of
projects assigned to each turn. Annual shares are retained in the source data
for cross-checking but are not used as the plotted z-values.
"""

from __future__ import annotations

from pathlib import Path
import math

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import PolyCollection


# =============================================================================
# 1. Paths
# =============================================================================

# The script lives in ROOT/dinggao/4.3...; deriving paths from __file__ avoids
# PowerShell/terminal encoding problems with Chinese directory names.
OUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "reproduced"
ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "inputs" / "analysis_dataset_in_scope.csv"
FIG_DIR = OUT_DIR / "figures"
SRC_DIR = OUT_DIR / "source_data"

for folder in (FIG_DIR, SRC_DIR):
    folder.mkdir(parents=True, exist_ok=True)

FIGURE_STEM = "figure9_research_turn_annual_distribution_3d_EN"


# =============================================================================
# 2. Coding-framework labels and colours
# =============================================================================

# Keep the Chinese coding labels as Unicode escapes so the source code remains
# robust under Windows console encodings.
OBJECT_CONSERVATION = "\u672c\u4f53\u4fdd\u62a4\u8f6c\u5411"
DIGITAL_COMPUTATIONAL = "\u6570\u5b57\u8ba1\u7b97\u8f6c\u5411"
SPATIAL_ACTIVATION = "\u7a7a\u95f4\u6d3b\u5316\u8f6c\u5411"
SOCIO_CULTURAL = "\u793e\u4f1a\u6587\u5316\u8f6c\u5411"
RISK_RESILIENCE = "\u98ce\u9669\u97e7\u6027\u8f6c\u5411"
HYBRID = "\u6df7\u5408\u8f6c\u5411"
TRADITIONAL_CONTINUITY = "\u4f20\u7edf\u5ef6\u7eed"

TURN_ORDER = [
    TRADITIONAL_CONTINUITY,
    HYBRID,
    OBJECT_CONSERVATION,
    RISK_RESILIENCE,
    DIGITAL_COMPUTATIONAL,
    SOCIO_CULTURAL,
    SPATIAL_ACTIVATION,
]

TURN_EN = {
    OBJECT_CONSERVATION: "Object-conservation\nturn",
    DIGITAL_COMPUTATIONAL: "Digital-computational\nturn",
    SPATIAL_ACTIVATION: "Spatial activation\nturn",
    SOCIO_CULTURAL: "Socio-cultural\nturn",
    RISK_RESILIENCE: "Risk-resilience\nturn",
    HYBRID: "Hybrid\nturn",
    TRADITIONAL_CONTINUITY: "Traditional\ncontinuity",
}

TURN_AXIS_EN = {
    OBJECT_CONSERVATION: "Object-\nconservation",
    DIGITAL_COMPUTATIONAL: "Digital-\ncomputational",
    SPATIAL_ACTIVATION: "Spatial\nactivation",
    SOCIO_CULTURAL: "Socio-\ncultural",
    RISK_RESILIENCE: "Risk-\nresilience",
    HYBRID: "Hybrid",
    TRADITIONAL_CONTINUITY: "Traditional\ncontinuity",
}

# Colour style follows the Figure 6 / Figure 8 family. Category colours stay
# fixed while row positions can be adjusted for visual ordering.
TURN_COLORS = {
    TRADITIONAL_CONTINUITY: "#B9C2CC",
    HYBRID: "#8A8F93",
    OBJECT_CONSERVATION: "#3A4652",
    SOCIO_CULTURAL: "#018C94",
    DIGITAL_COMPUTATIONAL: "#59BFC4",
    RISK_RESILIENCE: "#7DD1CA",
    SPATIAL_ACTIVATION: "#764D9C",
}

STAGE_SPANS = [
    (2008, 2012, "Agenda formation", "#B9C2CC"),
    (2013, 2017, "Object-method expansion", "#018C94"),
    (2018, 2022, "Compound agendas", "#764D9C"),
]


# =============================================================================
# 3. Plot configuration
# =============================================================================

PLOT = {
    "font_family": "Arial",
    "fig_width": 9.4,
    "fig_height": 7.2,
    "figure_dpi": 300,
    "output_dpi": 600,
    "view_elev": 24,
    "view_azim": -58,
    "projection_type": "ortho",
    "x_pad": 0.80,
    "y_pad": 0.72,
    "z_pad": 0.70,
    "ribbon_alpha": 0.18,
    "line_width": 1.85,
    "stem_width": 0.62,
    "stem_alpha": 0.50,
    "grid_color": "#D5DCE2",
    "grid_alpha": 0.78,
    "row_baseline_alpha": 0.18,
    "row_baseline_width": 0.78,
    "pane_alpha": 0.02,
    "axis_label_size": 8.8,
    "tick_label_size": 7.2,
    "category_label_size": 6.3,
    "legend_fontsize": 7.1,
    "title_size": 10.5,
}


# =============================================================================
# 4. Data processing
# =============================================================================

def setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                PLOT["font_family"],
                "Helvetica",
                "DejaVu Sans",
                "Microsoft YaHei",
                "SimHei",
                "sans-serif",
            ],
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "font.size": 7,
        }
    )


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    required = ["scope", "turn_type", "start_year_filled"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[df["scope"].eq("in_scope")].copy()
    df["start_year"] = pd.to_numeric(df["start_year_filled"], errors="coerce").astype("Int64")
    df = df[df["start_year"].notna()].copy()
    df["start_year"] = df["start_year"].astype(int)
    df = df[df["turn_type"].isin(TURN_ORDER)].copy()
    return df


def build_annual_matrices(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    min_year = int(df["start_year"].min())
    max_year = int(df["start_year"].max())
    years = list(range(min_year, max_year + 1))

    counts = (
        df.groupby(["start_year", "turn_type"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=years, columns=TURN_ORDER, fill_value=0)
    )
    annual_totals = counts.sum(axis=1)
    shares = counts.div(annual_totals.replace(0, np.nan), axis=0).fillna(0)

    counts_df = counts.reset_index().rename(columns={"index": "start_year"})
    shares_df = shares.reset_index().rename(columns={"index": "start_year"})

    rows = []
    for year in years:
        total = int(annual_totals.loc[year])
        for turn in TURN_ORDER:
            count = int(counts.loc[year, turn])
            share = float(shares.loc[year, turn])
            rows.append(
                {
                    "start_year": year,
                    "research_turn_cn": turn,
                    "research_turn_en": TURN_EN[turn].replace("\n", " "),
                    "annual_count": count,
                    "annual_total": total,
                    "annual_share": share,
                    "plotted_value": count,
                    "plotted_value_unit": "project_count",
                }
            )
    return counts_df, shares_df, pd.DataFrame(rows)


def save_source_data(counts_df: pd.DataFrame, shares_df: pd.DataFrame, long_df: pd.DataFrame) -> None:
    counts_df.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_annual_counts.csv",
        index=False,
        encoding="utf-8-sig",
    )
    shares_df.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_annual_shares.csv",
        index=False,
        encoding="utf-8-sig",
    )
    long_df.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_long_source_data.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(
        [
            {
                "research_turn_cn": turn,
                "research_turn_en": TURN_EN[turn].replace("\n", " "),
                "axis_label_en": TURN_AXIS_EN[turn].replace("\n", " "),
                "row_position": idx,
                "visual_order": f"{idx + 1} (front-to-back)",
                "color": TURN_COLORS[turn],
            }
            for idx, turn in enumerate(TURN_ORDER)
        ]
    ).to_csv(
        SRC_DIR / f"{FIGURE_STEM}_research_turn_color_mapping.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(
        [
            {
                "front_to_back_order": idx + 1,
                "row_position_y": idx,
                "research_turn_cn": turn,
                "research_turn_en": TURN_EN[turn].replace("\n", " "),
                "axis_label_en": TURN_AXIS_EN[turn].replace("\n", " "),
            }
            for idx, turn in enumerate(TURN_ORDER)
        ]
    ).to_csv(
        SRC_DIR / f"{FIGURE_STEM}_row_order_mapping.csv",
        index=False,
        encoding="utf-8-sig",
    )
    pd.DataFrame(
        [
            {
                "stage": label,
                "start_year": start,
                "end_year": end,
                "color": color,
            }
            for start, end, label, color in STAGE_SPANS
        ]
    ).to_csv(
        SRC_DIR / f"{FIGURE_STEM}_stage_spans.csv",
        index=False,
        encoding="utf-8-sig",
    )


# =============================================================================
# 5. Plotting
# =============================================================================

def add_stage_floor(ax, years: list[int]) -> None:
    """Add subtle floor bands for the three analytical stages."""
    y_min = -0.55
    y_max = len(TURN_ORDER) - 0.45
    z = 0.0
    for start, end, _label, color in STAGE_SPANS:
        x0 = max(start - 0.5, min(years) - 0.5)
        x1 = min(end + 0.5, max(years) + 0.5)
        xx, yy = np.meshgrid([x0, x1], [y_min, y_max])
        zz = np.zeros_like(xx) + z
        ax.plot_surface(
            xx,
            yy,
            zz,
            color=color,
            alpha=0.035,
            linewidth=0,
            shade=False,
            zorder=0,
        )


def draw_3d_distribution(counts_df: pd.DataFrame, shares_df: pd.DataFrame) -> Path:
    setup_style()

    years = counts_df["start_year"].astype(int).tolist()
    x = np.array(years)
    y_positions = np.arange(len(TURN_ORDER))
    max_count = int(counts_df[TURN_ORDER].to_numpy().max())
    z_max = max_count + PLOT["z_pad"]

    fig = plt.figure(
        figsize=(PLOT["fig_width"], PLOT["fig_height"]),
        dpi=PLOT["figure_dpi"],
    )
    ax = fig.add_subplot(111, projection="3d")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_proj_type(PLOT["projection_type"])

    add_stage_floor(ax, years)

    # Draw far rows first and front rows last. With the selected view angle,
    # lower y positions are visually closer to the reader; reversing the draw
    # order prevents back rows from being painted over front rows.
    draw_sequence = list(reversed(list(enumerate(TURN_ORDER))))

    # Subtle row baselines make the y-layer assignment explicit.
    for yi, turn in draw_sequence:
        ax.plot(
            [min(years), max(years)],
            [yi, yi],
            [0, 0],
            color=TURN_COLORS[turn],
            lw=PLOT["row_baseline_width"],
            alpha=PLOT["row_baseline_alpha"],
            zorder=1,
        )

    for yi, turn in draw_sequence:
        color = TURN_COLORS[turn]
        z = counts_df[turn].to_numpy(dtype=float)
        c = counts_df[turn].to_numpy(dtype=float)
        row_zorder = 20 + (len(TURN_ORDER) - yi)

        verts = [(years[0], 0.0)] + list(zip(years, z)) + [(years[-1], 0.0)]
        poly = PolyCollection(
            [verts],
            facecolors=[mpl.colors.to_rgba(color, PLOT["ribbon_alpha"])],
            edgecolors=[mpl.colors.to_rgba(color, 0.22)],
            linewidths=0.45,
        )
        ax.add_collection3d(poly, zs=yi, zdir="y")
        poly.set_zorder(row_zorder)

        ax.plot(
            x,
            np.full_like(x, yi, dtype=float),
            z,
            color=color,
            lw=PLOT["line_width"],
            alpha=0.96,
            zorder=row_zorder + 2,
        )

        marker_sizes = 9 + 12 * np.sqrt(np.maximum(c, 0))
        ax.scatter(
            x,
            np.full_like(x, yi, dtype=float),
            z,
            s=marker_sizes,
            color=color,
            edgecolor="white",
            linewidth=0.55,
            alpha=0.98,
            depthshade=False,
            zorder=row_zorder + 3,
        )

        for xx, zz, cc in zip(x, z, c):
            if cc <= 0 or zz <= 0:
                continue
            ax.plot(
                [xx, xx],
                [yi, yi],
                [0, zz],
                color=color,
                lw=PLOT["stem_width"] + 0.16 * math.sqrt(cc),
                alpha=PLOT["stem_alpha"],
                linestyle="-",
                zorder=row_zorder + 1,
            )

    ax.set_xlim(min(years) - PLOT["x_pad"], max(years) + PLOT["x_pad"])
    ax.set_ylim(-PLOT["y_pad"], len(TURN_ORDER) - 1 + PLOT["y_pad"])
    ax.set_zlim(0, z_max)

    ax.set_xticks(years)
    ax.set_xticklabels(
        [str(y) for y in years],
        rotation=48,
        ha="right",
        fontsize=PLOT["tick_label_size"],
    )
    ax.set_yticks(y_positions)
    ax.set_yticklabels(
        [TURN_AXIS_EN[t] for t in TURN_ORDER],
        fontsize=PLOT["category_label_size"],
    )
    z_ticks = np.arange(0, max_count + 1, 1)
    ax.set_zticks(z_ticks)
    ax.set_zticklabels([str(int(v)) for v in z_ticks], fontsize=PLOT["tick_label_size"])

    ax.set_xlabel("Project start year", labelpad=10, fontsize=PLOT["axis_label_size"])
    ax.set_ylabel("Research turns", labelpad=20, fontsize=PLOT["axis_label_size"])
    ax.set_zlabel("Number of projects", labelpad=8, fontsize=PLOT["axis_label_size"])
    ax.set_title(
        "Annual distribution of research turns in NSFC-funded heritage studies",
        fontsize=PLOT["title_size"],
        fontweight="bold",
        loc="left",
        pad=12,
    )

    ax.view_init(elev=PLOT["view_elev"], azim=PLOT["view_azim"])
    try:
        ax.set_box_aspect((1.75, 1.20, 0.62))
    except Exception:
        pass

    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((1, 1, 1, PLOT["pane_alpha"]))
        axis.pane.set_edgecolor((0.85, 0.88, 0.90, 0.55))
        axis._axinfo["grid"]["color"] = mpl.colors.to_rgba(PLOT["grid_color"], PLOT["grid_alpha"])
        axis._axinfo["grid"]["linewidth"] = 0.45

    legend_handles = [
        Line2D(
            [0],
            [0],
            color=TURN_COLORS[turn],
            marker="o",
            lw=1.7,
            markersize=4.2,
            markeredgecolor="white",
            label=TURN_EN[turn].replace("\n", " "),
        )
        for turn in TURN_ORDER
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper left",
        bbox_to_anchor=(0.02, 0.90),
        frameon=False,
        fontsize=PLOT["legend_fontsize"],
        handlelength=1.6,
        labelspacing=0.55,
    )

    fig.text(
        0.035,
        0.055,
        "Ribbons, stems and markers show annual project counts for seven research-turn families; annual shares are retained in the source data.",
        ha="left",
        va="bottom",
        fontsize=7.4,
        color="#4C5560",
    )

    fig.subplots_adjust(left=0.03, right=0.98, top=0.94, bottom=0.05)

    for ext in ("png", "pdf", "svg", "tiff"):
        path = FIG_DIR / f"{FIGURE_STEM}.{ext}"
        if ext in {"png", "tiff"}:
            fig.savefig(path, dpi=PLOT["output_dpi"], bbox_inches="tight", facecolor="white")
        else:
            fig.savefig(path, bbox_inches="tight", facecolor="white")

    plt.close(fig)
    return FIG_DIR / f"{FIGURE_STEM}.png"


# =============================================================================
# 6. Main
# =============================================================================

def main() -> None:
    df = load_data()
    counts_df, shares_df, long_df = build_annual_matrices(df)
    save_source_data(counts_df, shares_df, long_df)
    out = draw_3d_distribution(counts_df, shares_df)
    print(f"Saved annual 3D research-turn figure to: {out}")
    print(f"Saved source data to: {SRC_DIR}")


if __name__ == "__main__":
    main()
