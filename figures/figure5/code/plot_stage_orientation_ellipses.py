# -*- coding: utf-8 -*-
"""
Figure 4b. Stage-wise ellipse map of research orientations in NSFC heritage studies.

图形用途：
    用于结果章节 4.2，展示三个观察时期中问题取向的交融变化。

图形逻辑：
    1. 将七类 research_orientations 映射到二维概念平面；
    2. x 轴表示治理、活化、发展和实践应用取向；
    3. y 轴表示保护、价值识别和知识基础取向；
    4. 每个时期依据问题取向频次计算加权中心和协方差椭圆；
    5. 椭圆范围表示该时期问题取向组合的离散度和交融范围。

本版修改：
    1. 去除 I / II / III 阶段中心点；
    2. 去除阶段中心点之间的箭头轨迹；
    3. 保留三阶段椭圆和图例；
    4. 仍然输出 centroid source data，便于复核，但不在图中显示。
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse


# ============================================================
# 1. 路径设置
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "inputs" / "stage_by_orientation_matrix.csv"

OUT_DIR = ROOT / "outputs" / "reproduced" / "stage_ellipses"
SRC_DIR = OUT_DIR / "source_data"

for folder in [OUT_DIR, SRC_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

FIGURE_STEM = "figure4b_stage_research_orientation_ellipse_map_EN_no_centroid"


# ============================================================
# 2. 标签、颜色与坐标体系
# ============================================================

STAGE_META = {
    "议程形成期": {
        "label": "Agenda formation\n(2008-2012)",
        "short_label": "I",
        "color": "#89B2F4",
        "zorder": 3,
    },
    "对象与方法扩展期": {
        "label": "Object-method expansion\n(2013-2017)",
        "short_label": "II",
        "color": "#018C94",
        "zorder": 4,
    },
    "复合议程增强期": {
        "label": "Compound agendas\n(2018-2024)",
        "short_label": "III",
        "color": "#764D9C",
        "zorder": 5,
    },
}

STAGE_ORDER = [
    "议程形成期",
    "对象与方法扩展期",
    "复合议程增强期",
]

ORIENTATION_LABELS = {
    "价值识别": "Value\nidentification",
    "保护监测": "Conservation\nand monitoring",
    "数字记录": "Digital\ndocumentation",
    "治理参与": "Governance\nand participation",
    "活化再生": "Revitalization\nand regeneration",
    "综合": "Integrated",
    "风险韧性": "Risk and\nresilience",
}

# 二维概念坐标。
# x: 治理、活化、发展和实践应用取向；
# y: 保护、价值识别和知识基础取向。
ORIENTATION_COORDS = {
    "价值识别": (-0.42, 0.78),
    "保护监测": (-0.30, 0.92),
    "数字记录": (0.25, 0.66),
    "治理参与": (0.72, 0.34),
    "活化再生": (0.94, -0.20),
    "综合": (0.03, 0.08),
    "风险韧性": (0.68, -0.55),
}

# 三个概念区是解释性标签，而非独立编码变量。
CONCEPT_ZONE_LABELS = {
    "conservation_value": {
        "label": "Conservation and value\nknowledge base",
        "x": -0.82,
        "y": 0.86,
        "rationale": (
            "Heritage problems dominated by value identification, conservation "
            "monitoring and knowledge-base construction."
        ),
    },
    "use_inspired_science": {
        "label": "Use-inspired\nheritage science",
        "x": 0.82,
        "y": 0.86,
        "rationale": (
            "A conceptual area adapted from use-inspired basic research, where "
            "practical heritage concerns are translated into scientific questions."
        ),
    },
    "governance_regeneration": {
        "label": "Governance and regeneration\norientation",
        "x": 0.82,
        "y": -0.82,
        "rationale": (
            "Heritage problems more strongly connected with regeneration, "
            "governance participation, management and practice-oriented application."
        ),
    },
}


# ============================================================
# 3. 高度自定义绘图参数
# ============================================================

PLOT_CONFIG = {
    # ---------- 字体 ----------
    "font_family": "Arial",
    "strict_font": True,

    # ---------- 画布 ----------
    "figure_width": 8.4,
    "figure_height": 7.6,
    "figure_dpi": 300,
    "output_dpi": 600,
    "background": "white",

    # ---------- 坐标范围 ----------
    "xlim": (-1.24, 1.25),
    "ylim": (-1.08, 1.12),

    # ---------- 轴线与参考线 ----------
    "axis_color": "#333333",
    "axis_linewidth": 0.72,
    "diagonal_color": "#777777",
    "diagonal_linewidth": 0.55,
    "diagonal_alpha": 0.72,
    "diagonal_dash": (0, (4, 3)),

    # ---------- 椭圆 ----------
    "ellipse_confidence_scale": 1.62,
    "ellipse_min_width": 0.34,
    "ellipse_min_height": 0.26,
    "ellipse_fill_alpha": 0.05,
    "ellipse_gradient_layers": 18,
    "ellipse_outline_width": 1.18,
    "ellipse_inner_outline_width": 0.72,
    "ellipse_outline_dash": (0, (5, 3)),
    "ellipse_inner_scales": [0.55, 0.78, 1.0],

    # ---------- 是否显示阶段中心点与轨迹 ----------
    # 本版默认为 False，用于去除 I / II / III 及箭头。
    "show_stage_centroids": False,
    "show_stage_trajectory": False,

    # 即使关闭显示，也保留参数，便于以后恢复。
    "centroid_size": 58,
    "centroid_edgecolor": "white",
    "centroid_linewidth": 0.9,
    "trajectory_color": "#333333",
    "trajectory_alpha": 0.68,
    "trajectory_width": 1.15,
    "trajectory_arrow_scale": 13,

    # ---------- 问题取向锚点 ----------
    "show_orientation_anchors": True,
    "anchor_size_base": 22,
    "anchor_size_scale": 5.8,
    "anchor_alpha": 0.88,
    "anchor_color": "#262626",
    "anchor_edgecolor": "white",
    "anchor_linewidth": 0.6,
    "anchor_label_fontsize": 8.7,
    "anchor_label_color": "#1F1F1F",
    "anchor_label_bbox_alpha": 0.74,

    # ---------- 象限文本 ----------
    "quadrant_label_fontsize": 9.5,
    "quadrant_label_color": "#111111",
    "quadrant_label_weight": "bold",

    # ---------- 图例 ----------
    "legend_fontsize": 9.2,
    "legend_loc": "lower left",
    "legend_frame": True,

    # ---------- 保存 ----------
    "save_png": True,
    "save_pdf": True,
    "save_svg": True,
}


# ============================================================
# 4. 字体与数学工具函数
# ============================================================

def require_arial_font(font_name: str = "Arial", strict: bool = True) -> None:
    """
    设置投稿图件字体。
    strict=True 时，如果系统没有 Arial 则报错。
    """
    available_fonts = {f.name for f in fm.fontManager.ttflist}

    if strict and font_name not in available_fonts:
        raise RuntimeError(
            f"Arial font was not detected by Matplotlib. Please install {font_name}, "
            "or set PLOT_CONFIG['strict_font'] = False."
        )

    mpl.rcParams.update(
        {
            "font.family": font_name,
            "font.sans-serif": [font_name],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": PLOT_CONFIG["background"],
            "savefig.facecolor": PLOT_CONFIG["background"],
        }
    )


def weighted_mean_and_cov(
    points: np.ndarray,
    weights: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    计算加权均值和加权协方差。
    """
    weights = weights.astype(float)

    if weights.sum() <= 0:
        raise ValueError("Weights must sum to a positive value.")

    mean = np.average(points, axis=0, weights=weights)

    centered = points - mean
    cov = (centered * weights[:, None]).T @ centered / weights.sum()

    # 添加极小扰动，避免协方差矩阵奇异。
    cov += np.eye(2) * 1e-4

    return mean, cov


def ellipse_from_cov(mean: np.ndarray, cov: np.ndarray) -> dict[str, float]:
    """
    将协方差矩阵转换为 Matplotlib 椭圆参数。
    """
    vals, vecs = np.linalg.eigh(cov)

    order = vals.argsort()[::-1]
    vals = vals[order]
    vecs = vecs[:, order]

    angle = np.degrees(
        np.arctan2(
            vecs[1, 0],
            vecs[0, 0]
        )
    )

    scale = PLOT_CONFIG["ellipse_confidence_scale"]

    width = max(
        PLOT_CONFIG["ellipse_min_width"],
        2 * scale * np.sqrt(vals[0])
    )

    height = max(
        PLOT_CONFIG["ellipse_min_height"],
        2 * scale * np.sqrt(vals[1])
    )

    return {
        "center_x": float(mean[0]),
        "center_y": float(mean[1]),
        "width": float(width),
        "height": float(height),
        "angle": float(angle),
    }


# ============================================================
# 5. 数据处理与源数据输出
# ============================================================

def load_stage_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    读取 stage × research_orientations 矩阵，并计算椭圆参数。
    """
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    stage_matrix = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    if "stage" not in stage_matrix.columns:
        raise ValueError("Input matrix must contain a `stage` column.")

    stage_matrix = stage_matrix.set_index("stage").reindex(STAGE_ORDER)
    stage_matrix = stage_matrix.loc[:, list(ORIENTATION_COORDS.keys())]

    coords = pd.DataFrame(
        [
            {
                "research_orientation_cn": key,
                "research_orientation_en": ORIENTATION_LABELS[key].replace("\n", " "),
                "x_governance_development": value[0],
                "y_protection_value": value[1],
            }
            for key, value in ORIENTATION_COORDS.items()
        ]
    )

    ellipse_rows = []
    centroid_rows = []

    point_array = np.array(
        [
            ORIENTATION_COORDS[key]
            for key in stage_matrix.columns
        ]
    )

    for stage in STAGE_ORDER:
        weights = stage_matrix.loc[stage].to_numpy(dtype=float)

        mean, cov = weighted_mean_and_cov(
            point_array,
            weights
        )

        params = ellipse_from_cov(
            mean,
            cov
        )

        ellipse_rows.append(
            {
                "stage": stage,
                "stage_en": STAGE_META[stage]["label"].replace("\n", " "),
                "total_projects": int(weights.sum()),
                **params,
            }
        )

        centroid_rows.append(
            {
                "stage": stage,
                "stage_en": STAGE_META[stage]["label"].replace("\n", " "),
                "short_label": STAGE_META[stage]["short_label"],
                "center_x": float(mean[0]),
                "center_y": float(mean[1]),
                "total_projects": int(weights.sum()),
            }
        )

    ellipse_df = pd.DataFrame(ellipse_rows)
    centroid_df = pd.DataFrame(centroid_rows)

    return stage_matrix, coords, ellipse_df, centroid_df


def save_source_data(
    stage_matrix: pd.DataFrame,
    coords: pd.DataFrame,
    ellipse_df: pd.DataFrame,
    centroid_df: pd.DataFrame,
) -> None:
    """
    保存所有支撑图件的源数据。
    """
    stage_matrix.reset_index().to_csv(
        SRC_DIR / "figure4b_stage_by_research_orientation_counts.csv",
        index=False,
        encoding="utf-8-sig",
    )

    coords.to_csv(
        SRC_DIR / "figure4b_research_orientation_coordinate_mapping.csv",
        index=False,
        encoding="utf-8-sig",
    )

    ellipse_df.to_csv(
        SRC_DIR / "figure4b_stage_ellipse_parameters.csv",
        index=False,
        encoding="utf-8-sig",
    )

    centroid_df.to_csv(
        SRC_DIR / "figure4b_stage_centroids_not_drawn.csv",
        index=False,
        encoding="utf-8-sig",
    )

    color_df = pd.DataFrame(
        [
            {
                "stage": key,
                "stage_en": value["label"].replace("\n", " "),
                "short_label": value["short_label"],
                "color": value["color"],
            }
            for key, value in STAGE_META.items()
        ]
    )

    color_df.to_csv(
        SRC_DIR / "figure4b_stage_color_mapping.csv",
        index=False,
        encoding="utf-8-sig",
    )

    concept_zone_df = pd.DataFrame(
        [
            {
                "zone_id": key,
                "zone_label": value["label"].replace("\n", " "),
                "x": value["x"],
                "y": value["y"],
                "rationale": value["rationale"],
            }
            for key, value in CONCEPT_ZONE_LABELS.items()
        ]
    )

    concept_zone_df.to_csv(
        SRC_DIR / "figure4b_concept_zone_labels.csv",
        index=False,
        encoding="utf-8-sig",
    )

    manifest = pd.DataFrame(
        [
            {
                "figure": FIGURE_STEM,
                "panel": "b",
                "description": "Stage-by-orientation count matrix used to construct weighted ellipses",
                "source_data": "source_data/figure4b_stage_by_research_orientation_counts.csv",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "b",
                "description": "Conceptual coordinates assigned to research orientations",
                "source_data": "source_data/figure4b_research_orientation_coordinate_mapping.csv",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "b",
                "description": "Weighted ellipse parameters for the three stages",
                "source_data": "source_data/figure4b_stage_ellipse_parameters.csv",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "b",
                "description": "Weighted centroid coordinates are exported for reproducibility but not drawn",
                "source_data": "source_data/figure4b_stage_centroids_not_drawn.csv",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "b",
                "description": "Explanatory concept-zone labels used in the quadrant plane",
                "source_data": "source_data/figure4b_concept_zone_labels.csv",
            },
        ]
    )

    manifest.to_csv(
        SRC_DIR / "figure4b_source_data_manifest.csv",
        index=False,
        encoding="utf-8-sig",
    )


# ============================================================
# 6. 绘图函数
# ============================================================

def add_soft_ellipse(
    ax,
    params: dict,
    color: str,
    zorder: int
) -> None:
    """
    绘制半透明渐层椭圆和虚线边界。
    """
    layers = PLOT_CONFIG["ellipse_gradient_layers"]

    for i in range(layers, 0, -1):
        scale = i / layers

        alpha = PLOT_CONFIG["ellipse_fill_alpha"] * (scale ** 1.25)

        ellipse = Ellipse(
            (params["center_x"], params["center_y"]),
            width=params["width"] * scale,
            height=params["height"] * scale,
            angle=params["angle"],
            facecolor=color,
            edgecolor="none",
            alpha=alpha,
            zorder=zorder,
        )

        ax.add_patch(ellipse)

    for scale in PLOT_CONFIG["ellipse_inner_scales"]:
        outline = Ellipse(
            (params["center_x"], params["center_y"]),
            width=params["width"] * scale,
            height=params["height"] * scale,
            angle=params["angle"],
            facecolor="none",
            edgecolor=color,
            linewidth=(
                PLOT_CONFIG["ellipse_outline_width"]
                if scale == 1.0
                else PLOT_CONFIG["ellipse_inner_outline_width"]
            ),
            linestyle=PLOT_CONFIG["ellipse_outline_dash"],
            alpha=0.82 if scale == 1.0 else 0.42,
            zorder=zorder + 1,
        )

        ax.add_patch(outline)


def draw_reference_plane(ax) -> None:
    """
    绘制象限参考线与概念标签。
    """
    x0, x1 = PLOT_CONFIG["xlim"]
    y0, y1 = PLOT_CONFIG["ylim"]

    ax.axhline(
        0,
        color=PLOT_CONFIG["axis_color"],
        linewidth=PLOT_CONFIG["axis_linewidth"],
        zorder=1,
    )

    ax.axvline(
        0,
        color=PLOT_CONFIG["axis_color"],
        linewidth=PLOT_CONFIG["axis_linewidth"],
        zorder=1,
    )

    ax.plot(
        [x0, x1],
        [y0, y1],
        color=PLOT_CONFIG["diagonal_color"],
        linewidth=PLOT_CONFIG["diagonal_linewidth"],
        linestyle=PLOT_CONFIG["diagonal_dash"],
        alpha=PLOT_CONFIG["diagonal_alpha"],
        zorder=1,
    )

    ax.plot(
        [x0, x1],
        [y1, y0],
        color=PLOT_CONFIG["diagonal_color"],
        linewidth=PLOT_CONFIG["diagonal_linewidth"],
        linestyle=PLOT_CONFIG["diagonal_dash"],
        alpha=PLOT_CONFIG["diagonal_alpha"],
        zorder=1,
    )

    label_style = {
        "fontsize": PLOT_CONFIG["quadrant_label_fontsize"],
        "color": PLOT_CONFIG["quadrant_label_color"],
        "fontweight": PLOT_CONFIG["quadrant_label_weight"],
        "ha": "center",
        "va": "center",
    }

    for zone in CONCEPT_ZONE_LABELS.values():
        ax.text(
            zone["x"],
            zone["y"],
            zone["label"],
            **label_style,
            zorder=2,
        )

    ax.text(
        0,
        y0 + 0.045,
        "Governance-regeneration orientation",
        ha="center",
        va="bottom",
        fontsize=9.0,
        color="#333333",
        zorder=2,
    )

    ax.text(
        x0 + 0.035,
        0,
        "Protection-value orientation",
        ha="left",
        va="center",
        rotation=90,
        fontsize=9.0,
        color="#333333",
        zorder=2,
    )


def draw_orientation_anchors(
    ax,
    stage_matrix: pd.DataFrame
) -> None:
    """
    绘制问题取向锚点，用于说明椭圆由哪些取向加权形成。
    """
    if not PLOT_CONFIG["show_orientation_anchors"]:
        return

    totals = stage_matrix.sum(axis=0)

    label_offsets = {
        "价值识别": (-0.10, 0.06),
        "保护监测": (-0.12, 0.05),
        "数字记录": (0.10, 0.07),
        "治理参与": (0.10, 0.04),
        "活化再生": (0.12, -0.02),
        "综合": (-0.09, -0.08),
        "风险韧性": (0.10, -0.05),
    }

    for orientation, (x, y) in ORIENTATION_COORDS.items():
        size = (
            PLOT_CONFIG["anchor_size_base"]
            + totals[orientation] * PLOT_CONFIG["anchor_size_scale"]
        )

        ax.scatter(
            [x],
            [y],
            s=size,
            color=PLOT_CONFIG["anchor_color"],
            edgecolor=PLOT_CONFIG["anchor_edgecolor"],
            linewidth=PLOT_CONFIG["anchor_linewidth"],
            alpha=PLOT_CONFIG["anchor_alpha"],
            zorder=8,
        )

        dx, dy = label_offsets[orientation]

        ax.text(
            x + dx,
            y + dy,
            ORIENTATION_LABELS[orientation],
            ha="center",
            va="center",
            fontsize=PLOT_CONFIG["anchor_label_fontsize"],
            color=PLOT_CONFIG["anchor_label_color"],
            bbox={
                "boxstyle": "round,pad=0.20",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": PLOT_CONFIG["anchor_label_bbox_alpha"],
            },
            zorder=9,
        )


def draw_stage_centroids_and_trajectory(
    ax,
    centroid_df: pd.DataFrame
) -> None:
    """
    可选绘制阶段中心点和阶段迁移轨迹。

    本版默认不调用该函数。
    如果以后需要恢复 I / II / III 和箭头，可以将：
        PLOT_CONFIG["show_stage_centroids"] = True
        PLOT_CONFIG["show_stage_trajectory"] = True
    """
    centroid_points = []

    if PLOT_CONFIG["show_stage_centroids"]:
        for stage in STAGE_ORDER:
            meta = STAGE_META[stage]
            row = centroid_df.loc[
                centroid_df["stage"] == stage
            ].iloc[0]

            x = row["center_x"]
            y = row["center_y"]
            centroid_points.append((x, y))

            ax.scatter(
                [x],
                [y],
                s=PLOT_CONFIG["centroid_size"],
                color=meta["color"],
                edgecolor=PLOT_CONFIG["centroid_edgecolor"],
                linewidth=PLOT_CONFIG["centroid_linewidth"],
                zorder=10,
            )

            ax.text(
                x,
                y,
                meta["short_label"],
                ha="center",
                va="center",
                fontsize=8.2,
                fontweight="bold",
                color="white",
                zorder=11,
            )

    if PLOT_CONFIG["show_stage_trajectory"] and len(centroid_points) >= 2:
        for (x0, y0), (x1, y1) in zip(
            centroid_points[:-1],
            centroid_points[1:]
        ):
            ax.annotate(
                "",
                xy=(x1, y1),
                xytext=(x0, y0),
                arrowprops={
                    "arrowstyle": "->",
                    "color": PLOT_CONFIG["trajectory_color"],
                    "lw": PLOT_CONFIG["trajectory_width"],
                    "alpha": PLOT_CONFIG["trajectory_alpha"],
                    "mutation_scale": PLOT_CONFIG["trajectory_arrow_scale"],
                },
                zorder=7,
            )


def draw_figure(
    stage_matrix: pd.DataFrame,
    ellipse_df: pd.DataFrame,
    centroid_df: pd.DataFrame,
) -> plt.Figure:
    """
    绘制最终图件。
    """
    fig, ax = plt.subplots(
        figsize=(
            PLOT_CONFIG["figure_width"],
            PLOT_CONFIG["figure_height"]
        ),
        dpi=PLOT_CONFIG["figure_dpi"],
    )

    fig.patch.set_facecolor(PLOT_CONFIG["background"])
    ax.set_facecolor(PLOT_CONFIG["background"])

    # 绘制参考概念平面。
    draw_reference_plane(ax)

    # 绘制三个时期的协方差椭圆。
    for stage in STAGE_ORDER:
        meta = STAGE_META[stage]

        params = (
            ellipse_df
            .loc[ellipse_df["stage"] == stage]
            .iloc[0]
            .to_dict()
        )

        add_soft_ellipse(
            ax,
            params=params,
            color=meta["color"],
            zorder=meta["zorder"],
        )

    # 绘制问题取向锚点。
    draw_orientation_anchors(
        ax,
        stage_matrix
    )

    # 本版默认不绘制 I / II / III 和箭头。
    # 如需恢复，可将 PLOT_CONFIG 中两个开关改为 True。
    draw_stage_centroids_and_trajectory(
        ax,
        centroid_df
    )

    # 图例仍然保留，用于说明三阶段椭圆颜色。
    handles = [
        Line2D(
            [0],
            [0],
            color=STAGE_META[stage]["color"],
            lw=2.0,
            linestyle=PLOT_CONFIG["ellipse_outline_dash"],
            marker=None,
            label=STAGE_META[stage]["label"],
        )
        for stage in STAGE_ORDER
    ]

    legend = ax.legend(
        handles=handles,
        loc=PLOT_CONFIG["legend_loc"],
        frameon=PLOT_CONFIG["legend_frame"],
        fontsize=PLOT_CONFIG["legend_fontsize"],
        handlelength=2.4,
        borderaxespad=0.0,
    )

    if PLOT_CONFIG["legend_frame"]:
        legend.get_frame().set_facecolor("white")
        legend.get_frame().set_edgecolor("none")
        legend.get_frame().set_alpha(0.86)

    ax.set_xlim(*PLOT_CONFIG["xlim"])
    ax.set_ylim(*PLOT_CONFIG["ylim"])
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    fig.subplots_adjust(
        left=0.04,
        right=0.98,
        top=0.98,
        bottom=0.05
    )

    return fig


# ============================================================
# 7. 主程序
# ============================================================

def main() -> None:
    """
    主程序入口。
    """
    require_arial_font(
        PLOT_CONFIG["font_family"],
        PLOT_CONFIG["strict_font"],
    )

    stage_matrix, coords, ellipse_df, centroid_df = load_stage_data()

    save_source_data(
        stage_matrix,
        coords,
        ellipse_df,
        centroid_df,
    )

    fig = draw_figure(
        stage_matrix,
        ellipse_df,
        centroid_df,
    )

    if PLOT_CONFIG["save_png"]:
        fig.savefig(
            OUT_DIR / f"{FIGURE_STEM}.png",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight",
        )

    if PLOT_CONFIG["save_pdf"]:
        fig.savefig(
            OUT_DIR / f"{FIGURE_STEM}.pdf",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight",
        )

    if PLOT_CONFIG["save_svg"]:
        fig.savefig(
            OUT_DIR / f"{FIGURE_STEM}.svg",
            bbox_inches="tight",
        )

    plt.close(fig)

    print(f"Saved Figure 4b without stage centroid markers to: {OUT_DIR}")


if __name__ == "__main__":
    main()
