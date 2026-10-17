# -*- coding: utf-8 -*-
"""
Figure 4. Annual distribution of NSFC heritage research orientations.

图形用途：
    用于结果章节 4.2，展示不同项目起始年份中 NSFC 遗产研究
    问题取向（research_orientations）的年度构成。

图形逻辑：
    1. x 轴为项目起始年份 start_year_filled；
    2. y 轴为项目数量；
    3. 每个堆积柱的总高度表示该年度项目总量；
    4. 堆积颜色表示不同 research_orientations；
    5. 折线表示年度项目总量，用于强化时间变化趋势。

输出内容：
    - PNG / PDF / SVG 图件；
    - 年度问题取向计数表；
    - 年度问题取向占比表；
    - 年度项目总量表；
    - 颜色映射表；
    - source-data manifest。
"""

from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator


# ============================================================
# 1. 路径设置
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "inputs" / "analysis_dataset_in_scope.csv"

OUTPUT_DIR = ROOT / "outputs" / "reproduced" / "annual_stacked_bars"
FIG_DIR = OUTPUT_DIR / "figures"
SRC_DIR = OUTPUT_DIR / "source_data"

for folder in [OUTPUT_DIR, FIG_DIR, SRC_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

FIGURE_STEM = "figure4_annual_research_orientation_stacked_bar_EN"


# ============================================================
# 2. 标签、颜色与阶段设置
# ============================================================

RESEARCH_ORIENTATION_MAPPING = {
    "治理参与": "Governance and participation",
    "价值识别": "Value identification",
    "活化再生": "Revitalization and regeneration",
    "保护监测": "Conservation and monitoring",
    "数字记录": "Digital documentation",
    "综合": "Integrated",
    "风险韧性": "Risk and resilience",
}

# 柱形颜色采用单一蓝色层级，避免与 Figure 4b 的阶段椭圆色产生竞争。
# 颜色由浅到深对应从价值识别、保护监测到数字、治理、活化和风险议题的递进。
# 综合类使用冷灰蓝，作为跨议题项目的中性补充。
ORIENTATION_COLORS = {
    "价值识别": "#DCE8F5",
    "保护监测": "#BFD2E8",
    "数字记录": "#8FB4E3",
    "治理参与": "#5C8FD2",
    "活化再生": "#3F6699",
    "风险韧性": "#27415F",
    "综合": "#8A929B",
}

ORIENTATION_ORDER = [
    "价值识别",
    "保护监测",
    "数字记录",
    "治理参与",
    "活化再生",
    "风险韧性",
    "综合",
]

STAGE_BANDS = [
    {
        "start": 2008,
        "end": 2012,
        "label": "Agenda formation",
        "color": "#89B2F4",
    },
    {
        "start": 2013,
        "end": 2017,
        "label": "Object-method expansion",
        "color": "#018C94",
    },
    {
        "start": 2018,
        "end": 2024,
        "label": "Compound agendas",
        "color": "#764D9C",
    },
]


# ============================================================
# 3. 高度自定义制图参数
# ============================================================

PLOT_CONFIG = {
    # ---------- 字体 ----------
    "font_family": "Arial",
    "strict_font": True,

    # ---------- 画布 ----------
    "figure_width": 12.0,
    "figure_height": 6.2,
    "figure_dpi": 300,
    "output_dpi": 600,
    "background": "white",

    # ---------- 柱形 ----------
    "bar_width": 0.74,
    "bar_alpha": 0.94,
    "bar_edgecolor": "white",
    "bar_linewidth": 0.55,

    # ---------- 总量趋势线 ----------
    "show_total_line": True,
    "total_line_color": "#333333",
    "total_line_width": 2.2,
    "total_marker_size": 4.8,
    "total_marker_edgecolor": "white",
    "total_marker_edgewidth": 0.8,

    # ---------- 阶段背景 ----------
    "show_stage_bands": True,
    "stage_band_alpha": 0.085,
    "stage_label_fontsize": 9.4,
    "stage_label_color": "#4A4A4A",
    "stage_label_y_offset": 0.96,

    # ---------- 轴与网格 ----------
    "x_label": "Project start year",
    "y_label": "Number of projects",
    "axis_label_fontsize": 12,
    "tick_fontsize": 10,
    "x_tick_rotation": 45,
    "grid_color": "#D9D9D9",
    "grid_alpha": 0.52,
    "grid_linewidth": 0.8,
    "spine_color": "#333333",
    "spine_linewidth": 0.9,
    "y_top_padding": 3,

    # ---------- 图例 ----------
    "legend_ncol": 4,
    "legend_fontsize": 9.2,
    "legend_title": "Research orientation",
    "legend_title_fontsize": 9.8,
    "legend_frame": False,
    "legend_y": -0.20,

    # ---------- 图内标注 ----------
    "show_total_labels": False,
    "total_label_fontsize": 8.2,
    "total_label_color": "#333333",

    # ---------- 保存 ----------
    "save_png": True,
    "save_pdf": True,
    "save_svg": True,
}


# ============================================================
# 4. 字体与通用工具函数
# ============================================================

def require_arial_font(font_name: str = "Arial", strict: bool = True) -> None:
    """
    设置投稿图件字体。strict=True 时，如果系统没有 Arial 则报错。
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


def wrap_label(label: str, width: int = 18) -> str:
    """
    对英文标签进行换行，避免图例过长。
    """
    return "\n".join(
        textwrap.wrap(
            str(label),
            width=width,
            break_long_words=False,
        )
    )


# ============================================================
# 5. 数据处理
# ============================================================

def load_and_prepare_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    读取项目级数据，并生成年度问题取向计数、占比和总量表。
    """
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    needed = ["start_year_filled", "research_orientations"]
    missing = [col for col in needed if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    work = df.loc[:, needed].copy()
    work = work.dropna(subset=["start_year_filled", "research_orientations"])
    work["start_year"] = work["start_year_filled"].astype(float).astype(int)
    work["research_orientations"] = work["research_orientations"].astype(str).str.strip()

    work = work.loc[work["research_orientations"].isin(ORIENTATION_ORDER)].copy()

    min_year = int(work["start_year"].min())
    max_year = int(work["start_year"].max())
    years = list(range(min_year, max_year + 1))

    count_table = (
        work
        .groupby(["start_year", "research_orientations"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=years, fill_value=0)
        .reindex(columns=ORIENTATION_ORDER, fill_value=0)
    )

    total_table = count_table.sum(axis=1).rename("total_projects").reset_index()
    total_table = total_table.rename(columns={"index": "start_year"})

    percent_table = count_table.div(count_table.sum(axis=1).replace(0, np.nan), axis=0) * 100
    percent_table = percent_table.fillna(0)

    return count_table, percent_table, total_table


def save_source_data(
    count_table: pd.DataFrame,
    percent_table: pd.DataFrame,
    total_table: pd.DataFrame,
) -> None:
    """
    输出图件源数据，便于后续审稿或复现。
    """
    count_out = count_table.reset_index().rename(columns={"index": "start_year"})
    percent_out = percent_table.reset_index().rename(columns={"index": "start_year"})

    count_out.to_csv(
        SRC_DIR / "figure4_annual_research_orientation_counts.csv",
        index=False,
        encoding="utf-8-sig",
    )
    percent_out.to_csv(
        SRC_DIR / "figure4_annual_research_orientation_percent.csv",
        index=False,
        encoding="utf-8-sig",
    )
    total_table.to_csv(
        SRC_DIR / "figure4_annual_total_project_counts.csv",
        index=False,
        encoding="utf-8-sig",
    )

    color_mapping = pd.DataFrame(
        [
            {
                "research_orientation_cn": key,
                "research_orientation_en": RESEARCH_ORIENTATION_MAPPING[key],
                "color": ORIENTATION_COLORS[key],
            }
            for key in ORIENTATION_ORDER
        ]
    )
    color_mapping.to_csv(
        SRC_DIR / "figure4_research_orientation_color_mapping.csv",
        index=False,
        encoding="utf-8-sig",
    )

    manifest = pd.DataFrame(
        [
            {
                "figure": FIGURE_STEM,
                "panel": "main",
                "description": "Annual stacked counts of NSFC heritage research orientations by project start year",
                "source_data": "source_data/figure4_annual_research_orientation_counts.csv",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "main",
                "description": "Annual total number of NSFC heritage research projects",
                "source_data": "source_data/figure4_annual_total_project_counts.csv",
            },
        ]
    )
    manifest.to_csv(
        SRC_DIR / "figure4_source_data_manifest.csv",
        index=False,
        encoding="utf-8-sig",
    )


# ============================================================
# 6. 绘图函数
# ============================================================

def draw_stage_bands(ax, years: list[int], y_max: float) -> None:
    """
    绘制三个观察阶段的浅色背景，辅助读者理解时间比较框架。
    """
    if not PLOT_CONFIG["show_stage_bands"]:
        return

    for band in STAGE_BANDS:
        start = max(band["start"], min(years))
        end = min(band["end"], max(years))
        if start > end:
            continue

        ax.axvspan(
            start - 0.5,
            end + 0.5,
            color=band["color"],
            alpha=PLOT_CONFIG["stage_band_alpha"],
            zorder=0,
            linewidth=0,
        )

        ax.text(
            (start + end) / 2,
            y_max * PLOT_CONFIG["stage_label_y_offset"],
            band["label"],
            ha="center",
            va="top",
            fontsize=PLOT_CONFIG["stage_label_fontsize"],
            color=PLOT_CONFIG["stage_label_color"],
            fontweight="bold",
            zorder=5,
        )


def draw_stacked_bar(count_table: pd.DataFrame, total_table: pd.DataFrame) -> plt.Figure:
    """
    绘制年度堆积柱图。
    """
    years = count_table.index.astype(int).tolist()
    totals = total_table["total_projects"].to_numpy()
    y_max = max(totals) + PLOT_CONFIG["y_top_padding"]

    fig, ax = plt.subplots(
        figsize=(PLOT_CONFIG["figure_width"], PLOT_CONFIG["figure_height"]),
        dpi=PLOT_CONFIG["figure_dpi"],
    )
    fig.patch.set_facecolor(PLOT_CONFIG["background"])
    ax.set_facecolor(PLOT_CONFIG["background"])

    draw_stage_bands(ax, years, y_max)

    bottom = np.zeros(len(years))

    # 堆积顺序采用从较基础的价值、保护到治理、活化、数字和风险的逻辑，
    # 但图例仍按 ORIENTATION_ORDER 输出。
    stack_order = [
        "价值识别",
        "保护监测",
        "数字记录",
        "治理参与",
        "活化再生",
        "风险韧性",
        "综合",
    ]

    for orientation in stack_order:
        values = count_table[orientation].to_numpy()
        ax.bar(
            years,
            values,
            bottom=bottom,
            width=PLOT_CONFIG["bar_width"],
            color=ORIENTATION_COLORS[orientation],
            alpha=PLOT_CONFIG["bar_alpha"],
            edgecolor=PLOT_CONFIG["bar_edgecolor"],
            linewidth=PLOT_CONFIG["bar_linewidth"],
            label=RESEARCH_ORIENTATION_MAPPING[orientation],
            zorder=3,
        )
        bottom += values

    if PLOT_CONFIG["show_total_line"]:
        ax.plot(
            years,
            totals,
            color=PLOT_CONFIG["total_line_color"],
            linewidth=PLOT_CONFIG["total_line_width"],
            marker="o",
            markersize=PLOT_CONFIG["total_marker_size"],
            markeredgecolor=PLOT_CONFIG["total_marker_edgecolor"],
            markeredgewidth=PLOT_CONFIG["total_marker_edgewidth"],
            zorder=6,
            label="Total projects",
        )

    if PLOT_CONFIG["show_total_labels"]:
        for year, total in zip(years, totals):
            ax.text(
                year,
                total + 0.35,
                str(int(total)),
                ha="center",
                va="bottom",
                fontsize=PLOT_CONFIG["total_label_fontsize"],
                color=PLOT_CONFIG["total_label_color"],
                zorder=7,
            )

    ax.set_xlim(min(years) - 0.75, max(years) + 0.75)
    ax.set_ylim(0, y_max)
    ax.set_xticks(years)
    ax.set_xticklabels(
        years,
        rotation=PLOT_CONFIG["x_tick_rotation"],
        ha="right",
        fontsize=PLOT_CONFIG["tick_fontsize"],
    )
    ax.tick_params(axis="y", labelsize=PLOT_CONFIG["tick_fontsize"])
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    ax.set_xlabel(
        PLOT_CONFIG["x_label"],
        fontsize=PLOT_CONFIG["axis_label_fontsize"],
        fontweight="bold",
        labelpad=8,
    )
    ax.set_ylabel(
        PLOT_CONFIG["y_label"],
        fontsize=PLOT_CONFIG["axis_label_fontsize"],
        fontweight="bold",
        labelpad=8,
    )

    ax.yaxis.grid(
        True,
        color=PLOT_CONFIG["grid_color"],
        alpha=PLOT_CONFIG["grid_alpha"],
        linewidth=PLOT_CONFIG["grid_linewidth"],
        zorder=1,
    )
    ax.xaxis.grid(False)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(PLOT_CONFIG["spine_color"])
        ax.spines[spine].set_linewidth(PLOT_CONFIG["spine_linewidth"])

    # 手动构造图例，保证顺序稳定。
    legend_handles = [
        Patch(
            facecolor=ORIENTATION_COLORS[item],
            edgecolor="none",
            label=wrap_label(RESEARCH_ORIENTATION_MAPPING[item], 25),
        )
        for item in ORIENTATION_ORDER
    ]

    if PLOT_CONFIG["show_total_line"]:
        legend_handles.append(
            Line2D(
                [0],
                [0],
                color=PLOT_CONFIG["total_line_color"],
                lw=PLOT_CONFIG["total_line_width"],
                marker="o",
                markersize=PLOT_CONFIG["total_marker_size"],
                label="Total projects",
            )
        )

    legend = ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, PLOT_CONFIG["legend_y"]),
        ncol=PLOT_CONFIG["legend_ncol"],
        frameon=PLOT_CONFIG["legend_frame"],
        fontsize=PLOT_CONFIG["legend_fontsize"],
        title=PLOT_CONFIG["legend_title"],
        title_fontsize=PLOT_CONFIG["legend_title_fontsize"],
        handlelength=1.2,
        columnspacing=1.5,
        handletextpad=0.5,
    )
    legend.get_title().set_fontweight("bold")

    fig.subplots_adjust(left=0.075, right=0.985, top=0.94, bottom=0.285)

    return fig


# ============================================================
# 7. 主程序
# ============================================================

def main() -> None:
    require_arial_font(
        PLOT_CONFIG["font_family"],
        PLOT_CONFIG["strict_font"],
    )

    count_table, percent_table, total_table = load_and_prepare_data()
    save_source_data(count_table, percent_table, total_table)

    fig = draw_stacked_bar(count_table, total_table)

    if PLOT_CONFIG["save_png"]:
        fig.savefig(
            FIG_DIR / f"{FIGURE_STEM}.png",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight",
        )

    if PLOT_CONFIG["save_pdf"]:
        fig.savefig(
            FIG_DIR / f"{FIGURE_STEM}.pdf",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight",
        )

    if PLOT_CONFIG["save_svg"]:
        fig.savefig(
            FIG_DIR / f"{FIGURE_STEM}.svg",
            bbox_inches="tight",
        )

    plt.close(fig)

    print(f"Saved Figure 4 stacked bar chart to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
