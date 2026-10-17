# -*- coding: utf-8 -*-
"""
Figure 5. Timeline map of knowledge-function tags in NSFC heritage studies.

图形用途：
    用于结果章节展示 2008—2024 年间，不同知识功能及其 tag 如何出现、
    延续并发生跨功能连接。

图形逻辑：
    1. 横轴为项目起始年份，显示 2008—2024 年的内部年份；
    2. 淡色背景表示三个观察时期，但节点仍按具体年份定位；
    3. 纵向行表示 8 类知识功能二级维度；
    4. 节点表示某一年、某一知识功能下命中的 tag；
    5. 节点面积表示该 tag 在对应“年份-知识功能”组合中的项目数量；
    6. 半透明年轮表示该 tag 在多个年份或多个知识功能中反复出现；
    7. 连接线表示同一 tag 在时间上的延续，跨行弧线表示知识功能位置发生变化。

说明：
    节点、连接线、颜色映射和图形清单均输出为 source data，便于复核。
"""

from __future__ import annotations

import math
import textwrap
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.legend_handler import HandlerBase
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
from matplotlib.patches import Circle, PathPatch, Rectangle


# ============================================================
# 1. 路径设置
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "inputs" / "analysis_dataset_in_scope.csv"

OUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "reproduced"
FIG_DIR = OUT_DIR / "figures"
SRC_DIR = OUT_DIR / "source_data"
TABLE_DIR = OUT_DIR / "tables"

for folder in [OUT_DIR, FIG_DIR, SRC_DIR, TABLE_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

FIGURE_STEM = "figure5_knowledge_function_timeline_map_EN"
TABLE_STEM = "table3_stage_knowledge_function_profile"


# ============================================================
# 2. 时期、知识功能与标签翻译
# ============================================================

YEAR_RANGE = list(range(2008, 2025))

STAGE_META = {
    "议程形成期": {
        "label": "Agenda formation\nstage",
        "years": "2008-2012",
        "start": 2008,
        "end": 2012,
        "color": "#89B2F4",
    },
    "对象与方法扩展期": {
        "label": "Object and methodological\nexpansion stage",
        "years": "2013-2017",
        "start": 2013,
        "end": 2017,
        "color": "#018C94",
    },
    "复合议程增强期": {
        "label": "Compound agenda\nintensification stage",
        "years": "2018-2024",
        "start": 2018,
        "end": 2024,
        "color": "#764D9C",
    },
}

STAGE_ORDER = list(STAGE_META.keys())

KNOWLEDGE_FUNCTION_ORDER = [
    "记录描述",
    "意义阐释",
    "诊断评价",
    "机制解释",
    "预测模拟",
    "干预决策",
    "工具平台",
    "综合",
]

KNOWLEDGE_FUNCTION_LABELS = {
    "记录描述": "Recording and\ndescription",
    "意义阐释": "Meaning\ninterpretation",
    "诊断评价": "Diagnosis and\nevaluation",
    "机制解释": "Mechanism\nexplanation",
    "预测模拟": "Prediction and\nsimulation",
    "干预决策": "Intervention and\ndecision",
    "工具平台": "Tools and\nplatforms",
    "综合": "Integrated",
}

KNOWLEDGE_FUNCTION_COLORS = {
    "记录描述": "#D65F5F",
    "意义阐释": "#E68A2E",
    "诊断评价": "#D7C600",
    "机制解释": "#3DAA3D",
    "预测模拟": "#10B981",
    "干预决策": "#1BA6C9",
    "工具平台": "#2E73D2",
    "综合": "#6F58C9",
}

TAG_LABELS = {
    "三维建模": "3D modeling",
    "价值评价": "Value assessment",
    "传统延续": "Traditional continuity",
    "保护修复": "Conservation and restoration",
    "信息不足": "Insufficient information",
    "信息平台": "Information platform",
    "公众参与": "Public participation",
    "公众感知": "Public perception",
    "区域保护": "Regional conservation",
    "历史图像": "Historical imagery",
    "参与式调查": "Participatory survey",
    "工业更新": "Industrial renewal",
    "情景模拟": "Scenario simulation",
    "意义阐释": "Meaning interpretation",
    "指标评价": "Indicator evaluation",
    "数字孪生": "Digital twin",
    "数字采集": "Digital acquisition",
    "文旅融合": "Culture-tourism integration",
    "文献档案": "Literature and archives",
    "智能识别": "Intelligent recognition",
    "本体安全": "Fabric safety",
    "机器学习": "Machine learning",
    "材料检测": "Material testing",
    "活化利用": "Revitalization and use",
    "点云测绘": "Point-cloud surveying",
    "理论阐释": "Theoretical interpretation",
    "生态安全": "Ecological security",
    "病害监测": "Deterioration monitoring",
    "知识图谱": "Knowledge graph",
    "社区治理": "Community governance",
    "空间形态": "Spatial morphology",
    "空间治理": "Spatial governance",
    "结构环境检测": "Structural-environmental testing",
    "遥感分析": "Remote sensing",
    "问卷访谈": "Questionnaires and interviews",
    "韧性适应": "Resilience adaptation",
    "预警机制": "Early-warning mechanism",
    "预防保护": "Preventive conservation",
    "风险评价": "Risk assessment",
    "风险预警": "Risk warning",
}


# ============================================================
# 2.1 Knowledge-function-specific tag filters
# ============================================================

# Each tag is assigned to one primary knowledge-function lane. Earlier versions
# used a many-to-many allowlist, which made labels such as "Value assessment" and
# "Literature and archives" appear on several lanes. The timeline map is easier
# to interpret when the lanes are mutually exclusive and cross-functional links
# are shown by edges rather than duplicate tag labels.
FUNCTION_TAG_OWNER_EN = {
    # #0 Recording and description
    "Literature and archives": KNOWLEDGE_FUNCTION_ORDER[0],
    "Historical imagery": KNOWLEDGE_FUNCTION_ORDER[0],
    "Digital acquisition": KNOWLEDGE_FUNCTION_ORDER[0],
    "Point-cloud surveying": KNOWLEDGE_FUNCTION_ORDER[0],
    "3D modeling": KNOWLEDGE_FUNCTION_ORDER[0],
    "Remote sensing": KNOWLEDGE_FUNCTION_ORDER[0],
    "Knowledge graph": KNOWLEDGE_FUNCTION_ORDER[0],

    # #1 Meaning interpretation
    "Meaning interpretation": KNOWLEDGE_FUNCTION_ORDER[1],
    "Theoretical interpretation": KNOWLEDGE_FUNCTION_ORDER[1],
    "Public perception": KNOWLEDGE_FUNCTION_ORDER[1],
    "Traditional continuity": KNOWLEDGE_FUNCTION_ORDER[1],

    # #2 Diagnosis and evaluation
    "Indicator evaluation": KNOWLEDGE_FUNCTION_ORDER[2],
    "Value assessment": KNOWLEDGE_FUNCTION_ORDER[2],
    "Risk assessment": KNOWLEDGE_FUNCTION_ORDER[2],
    "Deterioration monitoring": KNOWLEDGE_FUNCTION_ORDER[2],
    "Material testing": KNOWLEDGE_FUNCTION_ORDER[2],
    "Structural-environmental testing": KNOWLEDGE_FUNCTION_ORDER[2],
    "Fabric safety": KNOWLEDGE_FUNCTION_ORDER[2],
    "Insufficient information": KNOWLEDGE_FUNCTION_ORDER[2],

    # #3 Mechanism explanation
    "Community governance": KNOWLEDGE_FUNCTION_ORDER[3],
    "Public participation": KNOWLEDGE_FUNCTION_ORDER[3],
    "Participatory survey": KNOWLEDGE_FUNCTION_ORDER[3],
    "Questionnaires and interviews": KNOWLEDGE_FUNCTION_ORDER[3],
    "Spatial morphology": KNOWLEDGE_FUNCTION_ORDER[3],
    "Spatial governance": KNOWLEDGE_FUNCTION_ORDER[3],
    "Culture-tourism integration": KNOWLEDGE_FUNCTION_ORDER[3],
    "Ecological security": KNOWLEDGE_FUNCTION_ORDER[3],
    "Resilience adaptation": KNOWLEDGE_FUNCTION_ORDER[3],
    "Industrial renewal": KNOWLEDGE_FUNCTION_ORDER[3],

    # #4 Prediction and simulation
    "Scenario simulation": KNOWLEDGE_FUNCTION_ORDER[4],
    "Risk warning": KNOWLEDGE_FUNCTION_ORDER[4],
    "Early-warning mechanism": KNOWLEDGE_FUNCTION_ORDER[4],
    "Machine learning": KNOWLEDGE_FUNCTION_ORDER[4],

    # #5 Intervention and decision
    "Conservation and restoration": KNOWLEDGE_FUNCTION_ORDER[5],
    "Preventive conservation": KNOWLEDGE_FUNCTION_ORDER[5],
    "Regional conservation": KNOWLEDGE_FUNCTION_ORDER[5],
    "Revitalization and use": KNOWLEDGE_FUNCTION_ORDER[5],

    # #6 Tools and platforms
    "Information platform": KNOWLEDGE_FUNCTION_ORDER[6],
    "Digital twin": KNOWLEDGE_FUNCTION_ORDER[6],
    "Intelligent recognition": KNOWLEDGE_FUNCTION_ORDER[6],
}


def is_tag_valid_for_knowledge_function(function: str, tag_en: str) -> bool:
    tag = str(tag_en).strip()
    return FUNCTION_TAG_OWNER_EN.get(tag) == function


# ============================================================
# 3. 制图参数
# ============================================================

PLOT_CONFIG = {
    # ---------- 字体 ----------
    "font_family": "Arial",
    "strict_font": False,

    # ---------- 画布 ----------
    "figure_width": 17.8,
    "figure_height": 9.2,
    "figure_dpi": 300,
    "output_dpi": 600,
    "background": "white",

    # ---------- 布局 ----------
    "x_left_pad": 0.76,
    "x_right_pad": 1.60,
    "right_label_pad": 0.72,
    "top_padding": 1.48,
    "bottom_padding": 0.62,
    "year_cell_width": 0.84,
    "function_cell_height": 0.64,
    "node_grid_max_cols": 5,
    "year_tick_y": 7.92,
    "year_label_y": 8.05,
    "stage_label_y": 8.31,
    "title_y": 8.82,

    # ---------- 节点 ----------
    "max_display_nodes_per_year_function": 999,
    "enable_collapsed_cells": True,
    "collapse_cell_min_nodes": 5,
    "collapse_cell_min_total_count": 16,
    "collapsed_node_min_size": 620,
    "collapsed_node_size_scale": 1.16,
    "node_size_min": 80,
    "node_size_max": 2400,
    "node_size_exponent": 1.10,
    "ordinary_node_size_min": 20,
    "ordinary_node_size_max": 920,
    "ordinary_node_size_exponent": 1.25,
    "ordinary_tag_total_weight": 0.58,
    "ordinary_active_year_weight": 0.82,
    "node_alpha": 0.93,
    "node_edgecolor": "white",
    "node_linewidth": 0.82,
    "ringed_node_min_count": 2,
    "ringed_node_min_tag_total": 9,
    "ring_layer_alphas": [0.42, 0.31, 0.22],
    "ring_layer_scales": [1.36, 1.12, 0.78],
    "inner_ring_scales": [0.74, 0.52, 0.32],
    "recurrence_ring_alpha": 0.13,
    "bridge_ring_color": "#C04BC9",
    "bridge_ring_alpha": 0.70,
    "bridge_ring_linewidth": 1.15,
    "bridge_tag_total_min": 18,
    "bridge_active_year_min": 5,
    "bridge_count_min": 3,

    # ---------- 行线 ----------
    "lane_linewidth": 1.52,
    "lane_alpha": 0.38,
    "lane_dash_alpha": 0.18,

    # ---------- 连接线 ----------
    "edge_alpha_same_function": 0.28,
    "edge_alpha_cross_function": 0.30,
    "edge_linewidth_base": 0.42,
    "edge_linewidth_scale": 0.54,
    "edge_linewidth_cap": 4.3,
    "edge_arc_height_base": 0.24,
    "edge_arc_height_scale": 0.030,
    "edge_cross_color": "#6F7282",
    "same_year_cross_edge_alpha": 0.18,
    "project_cross_edge_color": "#7A86A3",
    "project_cross_edge_alpha_min": 0.24,
    "project_cross_edge_alpha_max": 0.54,
    "project_cross_edge_linewidth_base": 0.30,
    "project_cross_edge_linewidth_scale": 0.54,
    "project_cross_edge_linewidth_cap": 4.65,
    "project_cross_edge_dash": (0, (3.4, 2.6)),
    "collapsed_inner_node_min_size": 18,
    "collapsed_inner_node_max_size": 42,
    "collapsed_inner_node_alpha": 0.86,

    # ---------- 标签 ----------
    "title_fontsize": 16.5,
    "panel_label_fontsize": 18.0,
    "show_panel_label": False,
    "panel_label": "a",
    "stage_label_fontsize": 8.6,
    "year_label_fontsize": 7.6,
    "function_label_fontsize": 9.8,
    "function_label_weight": "bold",
    "tag_label_fontsize": 6.85,
    "tag_label_color": "#4A2E2E",
    "tag_label_wrap_width": 18,
    "tag_label_bbox_alpha": 0.72,
    "stage_function_label_top_n": 2,
    "label_max_total": 80,
    "label_min_count": 2,
    "label_min_dx": 0.44,
    "label_min_dy": 0.26,
    "label_y_offset": 0.24,
    "label_rank_y_step": 0.18,
    "ring_label_min_visual_count": 12,
    "ring_label_max_total": 24,
    "ring_label_y_offset": 0.31,

    # ---------- 图例 ----------
    "size_legend_fontsize": 7.8,
    "legend_values": [1, 3, 6],
    "annual_ring_legend_color": "#9AA7B2",

    # ---------- 输出 ----------
    "save_png": True,
    "save_pdf": True,
    "save_svg": True,
    "save_tiff": False,
}


# ============================================================
# 4. 通用工具函数
# ============================================================

def require_font(font_name: str = "Arial", strict: bool = False) -> None:
    available_fonts = {font.name for font in fm.fontManager.ttflist}
    font_family = font_name if font_name in available_fonts else "DejaVu Sans"
    if strict and font_name not in available_fonts:
        raise RuntimeError(
            f"{font_name} was not detected by Matplotlib. "
            "Install it or set PLOT_CONFIG['strict_font'] = False."
        )
    mpl.rcParams.update(
        {
            "font.family": font_family,
            "font.sans-serif": [font_family, "Arial", "DejaVu Sans", "sans-serif"],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": PLOT_CONFIG["background"],
            "savefig.facecolor": PLOT_CONFIG["background"],
        }
    )


def split_tags(value: object) -> list[str]:
    if pd.isna(value):
        return []
    text = str(value).replace("；", ";")
    tags = [item.strip() for item in text.split(";")]
    return [item for item in tags if item and item.lower() != "nan"]


def wrap_text(text: str, width: int) -> str:
    return "\n".join(
        textwrap.wrap(
            str(text),
            width=width,
            break_long_words=False,
        )
    )


def infer_stage(year: int) -> str:
    for stage, meta in STAGE_META.items():
        if int(meta["start"]) <= year <= int(meta["end"]):
            return stage
    return ""


def function_y_positions() -> dict[str, float]:
    n = len(KNOWLEDGE_FUNCTION_ORDER)
    return {
        function: float(n - 1 - index)
        for index, function in enumerate(KNOWLEDGE_FUNCTION_ORDER)
    }


def packed_cell_offsets(n: int, width: float, height: float) -> list[tuple[float, float]]:
    if n <= 1:
        return [(0.0, 0.0)]

    cols = int(min(PLOT_CONFIG["node_grid_max_cols"], max(3, math.ceil(math.sqrt(n * 1.35)))))
    rows = int(math.ceil(n / cols))
    xs = np.linspace(-width / 2, width / 2, cols)
    ys = np.linspace(-height / 2, height / 2, rows)
    candidates = [(float(x), float(y)) for y in ys for x in xs]
    candidates = sorted(
        candidates,
        key=lambda item: (
            item[0] ** 2 + item[1] ** 2,
            abs(item[1]),
            abs(item[0]),
        ),
    )
    return candidates[:n]


def node_area_from_count(values: np.ndarray | list[float] | float, max_count: float) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    max_count = max(float(max_count), 1.0)
    scaled = np.power(np.clip(arr / max_count, 0, 1), PLOT_CONFIG["node_size_exponent"])
    return PLOT_CONFIG["node_size_min"] + scaled * (
        PLOT_CONFIG["node_size_max"] - PLOT_CONFIG["node_size_min"]
    )


def ordinary_node_area_from_weight(
    values: np.ndarray | list[float] | float,
    max_weight: float,
    min_weight: float = 0.0,
) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    max_weight = max(float(max_weight), 1.0)
    min_weight = float(min_weight)
    if max_weight <= min_weight:
        max_weight = min_weight + 1.0
    scaled = np.power(
        np.clip((arr - min_weight) / (max_weight - min_weight), 0, 1),
        PLOT_CONFIG["ordinary_node_size_exponent"],
    )
    return PLOT_CONFIG["ordinary_node_size_min"] + scaled * (
        PLOT_CONFIG["ordinary_node_size_max"] - PLOT_CONFIG["ordinary_node_size_min"]
    )


class AnnualRingLegendObject:
    """Legend proxy object for the composite annual-ring node.

    Parameters
    ----------
    facecolor:
        Fill color used in the legend sample. A neutral gray is recommended
        because the real node color is already determined by knowledge function.
    bridge_color:
        Outer ring color for tags spanning multiple knowledge functions.
    bridge:
        Whether to draw the purple bridge outline in the legend sample.
    """

    def __init__(
        self,
        facecolor: str,
        bridge_color: str,
        bridge: bool = False,
    ) -> None:
        self.facecolor = facecolor
        self.bridge_color = bridge_color
        self.bridge = bridge


class HandlerAnnualRing(HandlerBase):
    """Draw an annual-ring node inside a Matplotlib legend.

    The legend glyph mirrors the main plot's composite node:
    1. translucent outer layers;
    2. a central filled circle;
    3. white inner annual rings;
    4. optional purple bridge outline.
    """

    def create_artists(
        self,
        legend,
        orig_handle,
        xdescent,
        ydescent,
        width,
        height,
        fontsize,
        trans,
    ):
        cx = xdescent + width / 2.0
        cy = ydescent + height / 2.0
        radius = min(width, height) * 0.44
        max_outer_scale = max(PLOT_CONFIG["ring_layer_scales"])
        artists = []

        # Outer translucent annual-ring layers. The square-root conversion
        # follows scatter's area scaling, so the legend resembles the main plot.
        for scale, alpha in zip(
            PLOT_CONFIG["ring_layer_scales"],
            PLOT_CONFIG["ring_layer_alphas"],
        ):
            artists.append(
                Circle(
                    (cx, cy),
                    radius * math.sqrt(scale / max_outer_scale),
                    facecolor=orig_handle.facecolor,
                    edgecolor="none",
                    alpha=alpha,
                    transform=trans,
                )
            )

        # Central filled circle.
        artists.append(
            Circle(
                (cx, cy),
                radius * math.sqrt(1.0 / max_outer_scale),
                facecolor=orig_handle.facecolor,
                edgecolor="white",
                linewidth=0.82,
                alpha=0.90,
                transform=trans,
            )
        )

        # Inner white rings.
        for scale in PLOT_CONFIG["inner_ring_scales"]:
            artists.append(
                Circle(
                    (cx, cy),
                    radius * math.sqrt(scale / max_outer_scale),
                    facecolor="none",
                    edgecolor="white",
                    linewidth=0.72,
                    alpha=0.86,
                    transform=trans,
                )
            )

        # Optional purple outline for multi-function / bridge tags.
        if bool(getattr(orig_handle, "bridge", False)):
            artists.append(
                Circle(
                    (cx, cy),
                    radius * 1.04,
                    facecolor="none",
                    edgecolor=orig_handle.bridge_color,
                    linewidth=PLOT_CONFIG["bridge_ring_linewidth"],
                    alpha=PLOT_CONFIG["bridge_ring_alpha"],
                    transform=trans,
                )
            )

        return artists


def edge_width(weight: float) -> float:
    return min(
        PLOT_CONFIG["edge_linewidth_cap"],
        PLOT_CONFIG["edge_linewidth_base"]
        + PLOT_CONFIG["edge_linewidth_scale"] * math.sqrt(max(float(weight), 1.0)),
    )


# ============================================================
# 5. 数据构造
# ============================================================

def load_project_tag_long_table() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    if "scope" in df.columns:
        df = df[df["scope"].astype(str).str.strip().eq("in_scope")].copy()

    required_cols = [
        "start_year_filled",
        "primary_knowledge_function",
        "research_theme_tags",
        "method_tags",
        "agenda_turn_tags",
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    records: list[dict] = []
    for project_index, row in df.iterrows():
        try:
            year = int(float(row["start_year_filled"]))
        except Exception:
            continue
        if year not in YEAR_RANGE:
            continue

        primary_function = str(row["primary_knowledge_function"]).strip()
        if primary_function not in KNOWLEDGE_FUNCTION_ORDER:
            continue

        stage = infer_stage(year)
        if not stage:
            continue

        if primary_function == KNOWLEDGE_FUNCTION_ORDER[7]:
            records.append(
                {
                    "project_index": project_index,
                    "approval_no": row.get("approval_no", ""),
                    "project_title": row.get("project_title", ""),
                    "stage_cn": stage,
                    "stage_en": STAGE_META[stage]["label"],
                    "start_year": year,
                    "primary_knowledge_function_cn": primary_function,
                    "primary_knowledge_function_en": KNOWLEDGE_FUNCTION_LABELS[primary_function].replace("\n", " "),
                    "knowledge_function_cn": primary_function,
                    "knowledge_function_en": KNOWLEDGE_FUNCTION_LABELS[primary_function].replace("\n", " "),
                    "tag_cn": "Integrated synthesis",
                    "tag_en": "Integrated synthesis",
                }
            )

        tags: set[str] = set()
        for col in ["research_theme_tags", "method_tags", "agenda_turn_tags"]:
            tags.update(split_tags(row[col]))

        for tag in sorted(tags):
            tag_en = TAG_LABELS.get(tag, tag)
            owner_function = FUNCTION_TAG_OWNER_EN.get(str(tag_en).strip())
            if owner_function is None:
                continue
            records.append(
                {
                    "project_index": project_index,
                    "approval_no": row.get("approval_no", ""),
                    "project_title": row.get("project_title", ""),
                    "stage_cn": stage,
                    "stage_en": STAGE_META[stage]["label"],
                    "start_year": year,
                    "primary_knowledge_function_cn": primary_function,
                    "primary_knowledge_function_en": KNOWLEDGE_FUNCTION_LABELS[primary_function].replace("\n", " "),
                    "knowledge_function_cn": owner_function,
                    "knowledge_function_en": KNOWLEDGE_FUNCTION_LABELS[owner_function].replace("\n", " "),
                    "tag_cn": tag,
                    "tag_en": tag_en,
                }
            )

    long_df = pd.DataFrame(records)
    long_df.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_project_tag_long_table.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return long_df


def build_nodes(long_df: pd.DataFrame) -> pd.DataFrame:
    if long_df.empty:
        return pd.DataFrame()

    y_positions = function_y_positions()
    counts = (
        long_df.groupby(
            ["start_year", "knowledge_function_cn", "knowledge_function_en", "tag_cn", "tag_en"],
            as_index=False,
        )
        .agg(count=("project_index", "nunique"))
    )
    counts["stage_cn"] = counts["start_year"].astype(int).map(infer_stage)
    counts["stage_en"] = counts["stage_cn"].map(lambda item: STAGE_META[item]["label"])

    tag_stats = (
        counts.groupby("tag_cn", as_index=False)
        .agg(
            tag_total_count=("count", "sum"),
            tag_active_years=("start_year", "nunique"),
            tag_function_count=("knowledge_function_cn", "nunique"),
            tag_first_year=("start_year", "min"),
            tag_last_year=("start_year", "max"),
        )
    )

    node_rows: list[dict] = []
    for year in YEAR_RANGE:
        for function in KNOWLEDGE_FUNCTION_ORDER:
            group = counts[
                counts["start_year"].astype(int).eq(year)
                & counts["knowledge_function_cn"].eq(function)
            ].copy()
            if group.empty:
                continue

            group = group.sort_values(
                ["count", "tag_cn"],
                ascending=[False, True],
            ).reset_index(drop=True)
            offsets = packed_cell_offsets(
                len(group),
                PLOT_CONFIG["year_cell_width"],
                PLOT_CONFIG["function_cell_height"],
            )

            for rank, row in group.iterrows():
                x_offset, y_offset = offsets[rank]
                tag = str(row["tag_cn"])
                stage = infer_stage(year)
                node_rows.append(
                    {
                        "node_id": f"{year}|{function}|{tag}",
                        "stage_cn": stage,
                        "stage_en": STAGE_META[stage]["label"],
                        "start_year": int(year),
                        "knowledge_function_cn": function,
                        "knowledge_function_en": KNOWLEDGE_FUNCTION_LABELS[function].replace("\n", " "),
                        "tag_cn": tag,
                        "tag_en": TAG_LABELS.get(tag, tag),
                        "count": int(row["count"]),
                        "rank_within_year_function": int(rank + 1),
                        "x": float(year) + float(x_offset),
                        "y": y_positions[function] + float(y_offset),
                        "color": KNOWLEDGE_FUNCTION_COLORS[function],
                    }
                )

    nodes_df = pd.DataFrame(node_rows)
    if nodes_df.empty:
        return nodes_df

    nodes_df = nodes_df.merge(tag_stats, on="tag_cn", how="left")
    nodes_df["max_count_in_node_table"] = int(nodes_df["count"].max())
    nodes_df["display_score"] = (
        nodes_df["count"].astype(float) * 3.6
        + np.sqrt(nodes_df["tag_total_count"].astype(float)) * 1.4
        + nodes_df["tag_active_years"].astype(float) * 0.65
        + nodes_df["tag_function_count"].astype(float) * 0.75
    )
    nodes_df["display_rank_in_cell"] = (
        nodes_df.sort_values(
            ["display_score", "count", "tag_total_count", "tag_cn"],
            ascending=[False, False, False, True],
        )
        .groupby(["start_year", "knowledge_function_cn"])
        .cumcount()
        + 1
    )
    nodes_df["is_displayed"] = nodes_df["display_rank_in_cell"].astype(int).le(
        PLOT_CONFIG["max_display_nodes_per_year_function"]
    )
    nodes_df["is_high_centrality_candidate"] = (
        nodes_df["tag_total_count"].astype(int).ge(PLOT_CONFIG["bridge_tag_total_min"])
        & nodes_df["tag_active_years"].astype(int).ge(PLOT_CONFIG["bridge_active_year_min"])
        & nodes_df["count"].astype(int).ge(PLOT_CONFIG["bridge_count_min"])
    )
    nodes_df["bridge_count_contrib"] = np.where(
        nodes_df["is_high_centrality_candidate"],
        nodes_df["count"].astype(float),
        0.0,
    )
    displayed_for_cells = nodes_df[nodes_df["is_displayed"].eq(True)].copy()
    cell_stats = (
        displayed_for_cells
        .groupby(["start_year", "knowledge_function_cn"], as_index=False)
        .agg(
            display_cell_node_count=("node_id", "count"),
            display_cell_total_count=("count", "sum"),
            display_cell_max_count=("count", "max"),
            display_cell_tag_total=("tag_total_count", "sum"),
            display_cell_bridge_count=("is_high_centrality_candidate", "sum"),
            display_cell_bridge_total_count=("bridge_count_contrib", "sum"),
        )
    )
    if not displayed_for_cells.empty:
        bridge_top_source = displayed_for_cells[
            displayed_for_cells["is_high_centrality_candidate"].eq(True)
        ].copy()
        if bridge_top_source.empty:
            bridge_top_source = displayed_for_cells
        top_rows = (
            bridge_top_source
            .sort_values(
                [
                    "start_year",
                    "knowledge_function_cn",
                    "is_high_centrality_candidate",
                    "display_score",
                    "count",
                    "tag_cn",
                ],
                ascending=[True, True, False, False, False, True],
            )
            .drop_duplicates(["start_year", "knowledge_function_cn"], keep="first")
            [["start_year", "knowledge_function_cn", "tag_cn", "tag_en"]]
            .rename(columns={"tag_cn": "display_cell_top_tag_cn", "tag_en": "display_cell_top_tag_en"})
        )
        cell_stats = cell_stats.merge(top_rows, on=["start_year", "knowledge_function_cn"], how="left")

    nodes_df = nodes_df.merge(
        cell_stats,
        on=["start_year", "knowledge_function_cn"],
        how="left",
    )
    for col in [
        "display_cell_node_count",
        "display_cell_total_count",
        "display_cell_max_count",
        "display_cell_tag_total",
        "display_cell_bridge_count",
        "display_cell_bridge_total_count",
    ]:
        nodes_df[col] = nodes_df[col].fillna(0).astype(float)
    nodes_df["is_collapsed_cell"] = (
        bool(PLOT_CONFIG.get("enable_collapsed_cells", False))
        & nodes_df["is_displayed"].eq(True)
        & (
            nodes_df["display_cell_node_count"].ge(PLOT_CONFIG["collapse_cell_min_nodes"])
            | (
                nodes_df["display_cell_node_count"].ge(3)
                & nodes_df["display_cell_total_count"].ge(PLOT_CONFIG["collapse_cell_min_total_count"])
            )
        )
    )
    nodes_df["is_collapsed_bridge_cell"] = (
        nodes_df["is_collapsed_cell"].eq(True)
        & nodes_df["display_cell_bridge_count"].ge(1)
    )
    y_lookup = function_y_positions()
    nodes_df["draw_x"] = np.where(
        nodes_df["is_collapsed_cell"],
        nodes_df["start_year"].astype(float),
        nodes_df["x"].astype(float),
    )
    nodes_df["draw_y"] = np.where(
        nodes_df["is_collapsed_cell"],
        nodes_df["knowledge_function_cn"].map(y_lookup).astype(float),
        nodes_df["y"].astype(float),
    )
    nodes_df["visual_count"] = np.where(
        nodes_df["is_collapsed_cell"],
        np.maximum(
            nodes_df["display_cell_total_count"].astype(float),
            nodes_df["display_cell_max_count"].astype(float),
        ),
        nodes_df["count"].astype(float),
    )
    nodes_df["visual_node_id"] = np.where(
        nodes_df["is_collapsed_cell"],
        (
            nodes_df["start_year"].astype(int).astype(str)
            + "|"
            + nodes_df["knowledge_function_cn"].astype(str)
            + "|__aggregate__"
        ),
        nodes_df["node_id"].astype(str),
    )
    nodes_df["ordinary_visual_weight"] = nodes_df["count"].astype(float)
    nodes_df["is_ringed_node"] = nodes_df["is_high_centrality_candidate"].eq(True)
    nodes_df["is_recurrent_tag"] = (
        nodes_df["tag_active_years"].astype(int).ge(4)
        & nodes_df["tag_total_count"].astype(int).ge(8)
        & nodes_df["count"].astype(int).ge(2)
    )
    nodes_df["is_bridge_tag"] = nodes_df["is_high_centrality_candidate"]
    nodes_df["is_bridge_visual"] = (
        nodes_df["is_high_centrality_candidate"].eq(True)
        | nodes_df["is_collapsed_bridge_cell"].eq(True)
    )
    nodes_df["label_score"] = (
        nodes_df["count"].astype(float) * 3.2
        + np.sqrt(nodes_df["tag_total_count"].astype(float)) * 1.2
        + nodes_df["tag_active_years"].astype(float) * 0.7
        + nodes_df["tag_function_count"].astype(float) * 0.9
    )
    nodes_df["should_label"] = False
    nodes_df["label_rank_stage_function"] = pd.NA
    nodes_df["label_reason"] = ""
    select_labels(nodes_df)
    return nodes_df


def select_labels(nodes_df: pd.DataFrame) -> None:
    shown_nodes = nodes_df[nodes_df["is_displayed"].eq(True)].copy()
    if shown_nodes.empty:
        return

    # 每个“时期 × 知识功能”保留前两名 tag 标签。
    # 若某一时期的某一知识功能没有节点，则该行在该时期保持空白，表示数据中未命中。
    tag_totals = (
        shown_nodes
        .groupby(["stage_cn", "knowledge_function_cn", "tag_cn"], as_index=False)
        .agg(
            stage_function_tag_count=("count", "sum"),
            best_node_score=("label_score", "max"),
            active_years_in_stage=("start_year", "nunique"),
        )
        .sort_values(
            ["stage_cn", "knowledge_function_cn", "stage_function_tag_count", "best_node_score", "tag_cn"],
            ascending=[True, True, False, False, True],
        )
    )
    tag_totals["label_rank_stage_function"] = (
        tag_totals.groupby(["stage_cn", "knowledge_function_cn"]).cumcount() + 1
    )
    top_tags = tag_totals[
        tag_totals["label_rank_stage_function"].le(PLOT_CONFIG["stage_function_label_top_n"])
    ]

    selected_rows: list[dict] = []
    for _, top_tag in top_tags.iterrows():
        candidates = shown_nodes[
            shown_nodes["stage_cn"].eq(top_tag["stage_cn"])
            & shown_nodes["knowledge_function_cn"].eq(top_tag["knowledge_function_cn"])
            & shown_nodes["tag_cn"].eq(top_tag["tag_cn"])
        ].copy()
        if candidates.empty:
            continue
        candidate = candidates.sort_values(
            ["count", "label_score", "start_year"],
            ascending=[False, False, True],
        ).iloc[0]
        selected_rows.append(
            {
                "node_id": str(candidate["node_id"]),
                "rank": int(top_tag["label_rank_stage_function"]),
            }
        )

    selected_rows = selected_rows[: PLOT_CONFIG["label_max_total"]]
    selected_ids = [row["node_id"] for row in selected_rows]
    rank_map = {row["node_id"]: row["rank"] for row in selected_rows}

    mask = nodes_df["node_id"].astype(str).isin(selected_ids)
    nodes_df.loc[mask, "should_label"] = True
    nodes_df.loc[mask, "label_reason"] = "top_tag_within_stage_function"
    nodes_df.loc[mask, "label_rank_stage_function"] = (
        nodes_df.loc[mask, "node_id"].astype(str).map(rank_map)
    )

    ring_label_source = (
        shown_nodes[
            shown_nodes["is_collapsed_cell"].eq(True)
            & shown_nodes["visual_count"].astype(float).ge(PLOT_CONFIG["ring_label_min_visual_count"])
        ]
        .sort_values(["visual_count", "label_score", "display_cell_top_tag_en"], ascending=[False, False, True])
        .drop_duplicates(["start_year", "knowledge_function_cn"], keep="first")
        .head(PLOT_CONFIG["ring_label_max_total"])
    )
    if not ring_label_source.empty:
        ring_ids = ring_label_source["node_id"].astype(str).tolist()
        ring_mask = nodes_df["node_id"].astype(str).isin(ring_ids)
        nodes_df.loc[ring_mask, "should_label"] = True
        nodes_df.loc[ring_mask, "label_reason"] = "high_centrality_ring_node"
        nodes_df.loc[ring_mask & nodes_df["label_rank_stage_function"].isna(), "label_rank_stage_function"] = 1


def build_edges(nodes_df: pd.DataFrame, long_df: pd.DataFrame | None = None) -> pd.DataFrame:
    if nodes_df.empty:
        return pd.DataFrame()

    function_rank = {
        function: index
        for index, function in enumerate(KNOWLEDGE_FUNCTION_ORDER)
    }
    edge_rows: list[dict] = []

    # 同一 tag 在时间上的延续：连接连续出现年份中的主导节点。
    for tag, group in nodes_df.groupby("tag_cn"):
        year_nodes = (
            group.sort_values(["start_year", "count", "tag_total_count"], ascending=[True, False, False])
            .groupby("start_year", as_index=False)
            .head(1)
            .sort_values("start_year")
        )
        if len(year_nodes) < 2:
            continue

        rows = list(year_nodes.to_dict("records"))
        for source, target in zip(rows[:-1], rows[1:]):
            source_function = str(source["knowledge_function_cn"])
            target_function = str(target["knowledge_function_cn"])
            same_function = source_function == target_function
            weight = min(int(source["count"]), int(target["count"]))
            visual_weight = max(
                float(weight),
                math.log1p(float(source.get("tag_total_count", weight))) * 1.45,
            )
            color = source["color"]
            edge_rows.append(
                {
                    "edge_type": "same_tag_temporal_continuity",
                    "tag_cn": tag,
                    "tag_en": source["tag_en"],
                    "source_node_id": source["node_id"],
                    "target_node_id": target["node_id"],
                    "source_year": int(source["start_year"]),
                    "target_year": int(target["start_year"]),
                    "year_gap": int(target["start_year"]) - int(source["start_year"]),
                    "source_function_cn": source_function,
                    "target_function_cn": target_function,
                    "source_function_en": source["knowledge_function_en"],
                    "target_function_en": target["knowledge_function_en"],
                    "source_x": float(source.get("draw_x", source["x"])),
                    "source_y": float(source.get("draw_y", source["y"])),
                    "target_x": float(target.get("draw_x", target["x"])),
                    "target_y": float(target.get("draw_y", target["y"])),
                    "weight": weight,
                    "visual_weight": round(visual_weight, 4),
                    "function_distance": abs(function_rank[source_function] - function_rank[target_function]),
                    "same_function": same_function,
                    "color": color,
                }
            )

    # 同一年内同一 tag 跨知识功能出现：用短弧线表达纵向联系。
    if long_df is not None and not long_df.empty:
        node_lookup = {
            str(row["node_id"]): row
            for row in nodes_df.to_dict("records")
        }
        visual_lookup: dict[str, dict] = {}
        visual_source = nodes_df.sort_values(
            ["is_collapsed_cell", "visual_count", "display_score"],
            ascending=[False, False, False],
        )
        for row in visual_source.to_dict("records"):
            visual_lookup.setdefault(str(row.get("visual_node_id", row["node_id"])), row)
        pair_weights: defaultdict[tuple[str, str], int] = defaultdict(int)
        for (_, _), project_group in long_df.groupby(["project_index", "start_year"]):
            project_tags = (
                project_group[
                    [
                        "start_year",
                        "knowledge_function_cn",
                        "knowledge_function_en",
                        "tag_cn",
                        "tag_en",
                    ]
                ]
                .drop_duplicates()
                .copy()
            )
            if project_tags["knowledge_function_cn"].nunique() < 2:
                continue
            project_tags["node_id"] = project_tags.apply(
                lambda item: f"{int(item['start_year'])}|{item['knowledge_function_cn']}|{item['tag_cn']}",
                axis=1,
            )
            rows = []
            seen_visual_ids: set[str] = set()
            for item in project_tags.to_dict("records"):
                record = node_lookup.get(str(item["node_id"]))
                if not record or not bool(record.get("is_bridge_visual", False)):
                    continue
                visual_id = str(record.get("visual_node_id", record["node_id"]))
                if visual_id in seen_visual_ids:
                    continue
                rows.append(visual_lookup.get(visual_id, record))
                seen_visual_ids.add(visual_id)
            if len(rows) < 2:
                continue
            rows = sorted(
                rows,
                key=lambda item: (
                    function_rank[str(item["knowledge_function_cn"])],
                    str(item["tag_cn"]),
                ),
            )
            for source, target in combinations(rows, 2):
                if source["knowledge_function_cn"] == target["knowledge_function_cn"]:
                    continue
                key = tuple(sorted([
                    str(source.get("visual_node_id", source["node_id"])),
                    str(target.get("visual_node_id", target["node_id"])),
                ]))
                pair_weights[key] += 1

        for (source_id, target_id), weight in pair_weights.items():
            source = visual_lookup.get(source_id)
            target = visual_lookup.get(target_id)
            if not source or not target:
                continue
            source_function = str(source["knowledge_function_cn"])
            target_function = str(target["knowledge_function_cn"])
            visual_weight = max(float(weight), math.sqrt(float(weight)) * 1.35)
            edge_rows.append(
                {
                    "edge_type": "project_cross_function_cooccurrence",
                    "tag_cn": "",
                    "tag_en": "Project-level cross-function co-occurrence",
                    "source_node_id": source_id,
                    "target_node_id": target_id,
                    "source_year": int(source["start_year"]),
                    "target_year": int(target["start_year"]),
                    "year_gap": 0,
                    "source_function_cn": source_function,
                    "target_function_cn": target_function,
                    "source_function_en": source["knowledge_function_en"],
                    "target_function_en": target["knowledge_function_en"],
                    "source_x": float(source.get("draw_x", source["x"])),
                    "source_y": float(source.get("draw_y", source["y"])),
                    "target_x": float(target.get("draw_x", target["x"])),
                    "target_y": float(target.get("draw_y", target["y"])),
                    "weight": int(weight),
                    "visual_weight": round(visual_weight, 4),
                    "function_distance": abs(function_rank[source_function] - function_rank[target_function]),
                    "same_function": False,
                    "color": PLOT_CONFIG["project_cross_edge_color"],
                }
            )

    for (year, tag), group in nodes_df.groupby(["start_year", "tag_cn"]):
        if group["knowledge_function_cn"].nunique() < 2:
            continue
        group = group.sort_values(["count", "knowledge_function_cn"], ascending=[False, True]).head(3)
        rows = list(group.to_dict("records"))
        for source, target in zip(rows[:-1], rows[1:]):
            weight = min(int(source["count"]), int(target["count"]))
            visual_weight = max(
                float(weight),
                math.log1p(float(source.get("tag_total_count", weight))) * 1.10,
            )
            edge_rows.append(
                {
                    "edge_type": "same_tag_same_year_cross_function",
                    "tag_cn": tag,
                    "tag_en": source["tag_en"],
                    "source_node_id": source["node_id"],
                    "target_node_id": target["node_id"],
                    "source_year": int(year),
                    "target_year": int(year),
                    "year_gap": 0,
                    "source_function_cn": source["knowledge_function_cn"],
                    "target_function_cn": target["knowledge_function_cn"],
                    "source_function_en": source["knowledge_function_en"],
                    "target_function_en": target["knowledge_function_en"],
                    "source_x": float(source.get("draw_x", source["x"])),
                    "source_y": float(source.get("draw_y", source["y"])),
                    "target_x": float(target.get("draw_x", target["x"])),
                    "target_y": float(target.get("draw_y", target["y"])),
                    "weight": weight,
                    "visual_weight": round(visual_weight, 4),
                    "function_distance": abs(
                        function_rank[source["knowledge_function_cn"]]
                        - function_rank[target["knowledge_function_cn"]]
                    ),
                    "same_function": False,
                    "color": source["color"],
                }
            )

    edges_df = pd.DataFrame(edge_rows)
    if not edges_df.empty:
        edges_df = edges_df.sort_values(
            ["edge_type", "weight", "year_gap"],
            ascending=[True, False, False],
        ).reset_index(drop=True)
    return edges_df


def save_source_data(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, long_df: pd.DataFrame) -> None:
    long_df.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_project_tag_long_table.csv",
        index=False,
        encoding="utf-8-sig",
    )
    nodes_df.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_nodes.csv",
        index=False,
        encoding="utf-8-sig",
    )
    edges_df.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_edges.csv",
        index=False,
        encoding="utf-8-sig",
    )

    color_df = pd.DataFrame(
        [
            {
                "knowledge_function_cn": function,
                "knowledge_function_en": KNOWLEDGE_FUNCTION_LABELS[function].replace("\n", " "),
                "color": KNOWLEDGE_FUNCTION_COLORS[function],
            }
            for function in KNOWLEDGE_FUNCTION_ORDER
        ]
    )
    color_df.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_knowledge_function_colors.csv",
        index=False,
        encoding="utf-8-sig",
    )

    stage_df = pd.DataFrame(
        [
            {
                "stage_cn": stage,
                "stage_en": meta["label"],
                "years": meta["years"],
                "start": meta["start"],
                "end": meta["end"],
                "color": meta["color"],
            }
            for stage, meta in STAGE_META.items()
        ]
    )
    stage_df.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_stage_mapping.csv",
        index=False,
        encoding="utf-8-sig",
    )

    manifest = pd.DataFrame(
        [
            {
                "figure": FIGURE_STEM,
                "panel": "main",
                "description": "Project-level tag table used to count year-function-tag nodes",
                "source_data": f"source_data/{FIGURE_STEM}_project_tag_long_table.csv",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "main",
                "description": "Year-function-tag nodes with coordinates, counts and label flags",
                "source_data": f"source_data/{FIGURE_STEM}_nodes.csv",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "main",
                "description": "Temporal and cross-function links among repeated tags",
                "source_data": f"source_data/{FIGURE_STEM}_edges.csv",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "main",
                "description": "Knowledge-function color mapping",
                "source_data": f"source_data/{FIGURE_STEM}_knowledge_function_colors.csv",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "main",
                "description": "Stage background mapping used in the timeline",
                "source_data": f"source_data/{FIGURE_STEM}_stage_mapping.csv",
            },
        ]
    )
    manifest.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_source_data_manifest.csv",
        index=False,
        encoding="utf-8-sig",
    )


# ============================================================
# 5.1 生成 Figure 5 对应的论文表格
# ============================================================

def latex_escape(value: object) -> str:
    """Escape special characters for LaTeX table cells."""
    text = "" if pd.isna(value) else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def build_stage_cooccurrence_metrics(long_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate stage-level degree and betweenness centrality for
    knowledge-function tag nodes.

    Nodes are defined as knowledge function + matched tag. Edges are formed
    when two nodes occur in the same project within the same stage.
    """
    metric_rows: list[dict] = []

    for stage, stage_group in long_df.groupby("stage_cn"):
        node_keys: set[tuple[str, str]] = set()
        edge_weights: defaultdict[tuple[tuple[str, str], tuple[str, str]], int] = defaultdict(int)

        for _, project_group in stage_group.groupby("project_index"):
            project_nodes = (
                project_group[["knowledge_function_cn", "tag_cn"]]
                .drop_duplicates()
                .apply(lambda row: (str(row["knowledge_function_cn"]), str(row["tag_cn"])), axis=1)
                .tolist()
            )
            project_nodes = sorted(set(project_nodes))
            node_keys.update(project_nodes)
            for source, target in combinations(project_nodes, 2):
                edge_weights[(source, target)] += 1

        degree_lookup = {node: 0 for node in node_keys}
        weighted_degree_lookup = {node: 0.0 for node in node_keys}
        for source, target in edge_weights:
            degree_lookup[source] += 1
            degree_lookup[target] += 1
        for (source, target), weight in edge_weights.items():
            weighted_degree_lookup[source] += float(weight)
            weighted_degree_lookup[target] += float(weight)

        max_weighted_degree = max(weighted_degree_lookup.values()) if weighted_degree_lookup else 0.0
        centrality_lookup = {
            node: (
                float(weighted_degree_lookup.get(node, 0.0)) / max_weighted_degree
                if max_weighted_degree > 0
                else 0.0
            )
            for node in node_keys
        }

        for function, tag in sorted(node_keys):
            metric_rows.append(
                {
                    "stage_cn": stage,
                    "knowledge_function_cn": function,
                    "tag_cn": tag,
                    "degree": int(degree_lookup.get((function, tag), 0)),
                    "weighted_degree": float(weighted_degree_lookup.get((function, tag), 0.0)),
                    "centrality": float(centrality_lookup.get((function, tag), 0.0)),
                }
            )

    return pd.DataFrame(metric_rows)


def build_stage_term_table(long_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the manuscript table corresponding to Figure 5.

    Each row reports the highest-frequency matched term within one
    stage-by-knowledge-function lane.
    """
    if long_df.empty:
        return pd.DataFrame()

    unique_hits = long_df.drop_duplicates(
        ["project_index", "stage_cn", "start_year", "knowledge_function_cn", "tag_cn"]
    ).copy()

    term_summary = (
        unique_hits
        .groupby(["stage_cn", "knowledge_function_cn", "tag_cn", "tag_en"], as_index=False)
        .agg(
            freq=("project_index", "nunique"),
            begin=("start_year", "min"),
            end=("start_year", "max"),
            active_years=("start_year", "nunique"),
        )
    )

    year_counts = (
        unique_hits
        .groupby(["stage_cn", "knowledge_function_cn", "tag_cn", "start_year"], as_index=False)
        .agg(year_freq=("project_index", "nunique"))
        .sort_values(
            ["stage_cn", "knowledge_function_cn", "tag_cn", "year_freq", "start_year"],
            ascending=[True, True, True, False, True],
        )
        .drop_duplicates(["stage_cn", "knowledge_function_cn", "tag_cn"], keep="first")
        .rename(columns={"start_year": "peak_year"})
    )

    metrics = build_stage_cooccurrence_metrics(unique_hits)
    term_summary = (
        term_summary
        .merge(
            year_counts[["stage_cn", "knowledge_function_cn", "tag_cn", "peak_year"]],
            on=["stage_cn", "knowledge_function_cn", "tag_cn"],
            how="left",
        )
        .merge(
            metrics,
            on=["stage_cn", "knowledge_function_cn", "tag_cn"],
            how="left",
        )
    )
    term_summary["degree"] = term_summary["degree"].fillna(0).astype(int)
    term_summary["centrality"] = term_summary["centrality"].fillna(0.0)

    stage_rank = {stage: index for index, stage in enumerate(STAGE_ORDER)}
    function_rank = {function: index for index, function in enumerate(KNOWLEDGE_FUNCTION_ORDER)}
    term_summary["stage_rank"] = term_summary["stage_cn"].map(stage_rank)
    term_summary["function_rank"] = term_summary["knowledge_function_cn"].map(function_rank)

    representative = (
        term_summary
        .sort_values(
            [
                "stage_rank",
                "function_rank",
                "freq",
                "degree",
                "centrality",
                "tag_en",
            ],
            ascending=[True, True, False, False, False, True],
        )
        .drop_duplicates(["stage_cn", "knowledge_function_cn"], keep="first")
        .sort_values(["stage_rank", "function_rank"])
        .reset_index(drop=True)
    )

    representative["stage_en"] = representative["stage_cn"].map(
        lambda item: f"{STAGE_META[item]['label'].replace(chr(10), ' ')} ({STAGE_META[item]['years'].replace('-', '--')})"
    )
    representative["knowledge_function_en"] = representative["knowledge_function_cn"].map(
        lambda item: KNOWLEDGE_FUNCTION_LABELS[item].replace("\n", " ")
    )
    representative["centrality"] = representative["centrality"].round(3)

    return representative[
        [
            "stage_cn",
            "stage_en",
            "knowledge_function_cn",
            "knowledge_function_en",
            "tag_cn",
            "tag_en",
            "peak_year",
            "freq",
            "begin",
            "end",
            "degree",
            "centrality",
        ]
    ]


def stage_term_table_to_latex(table_df: pd.DataFrame) -> str:
    if table_df.empty:
        return ""

    lines = [
        r"\begin{table}[!htbp]",
        r"\centering",
        r"\caption{Stage-wise knowledge-function terms extracted from the Figure 5 timeline map.}",
        r"\label{tab:stage_knowledge_function_terms}",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{p{2.8cm}p{2.6cm}Xrrrrrr}",
        r"\toprule",
        r"Stage & Knowledge function & Representative term & Peak year & Freq. & Begin & End & Degree & Centrality \\",
        r"\midrule",
    ]

    previous_stage = None
    for _, row in table_df.iterrows():
        stage_text = row["stage_en"]
        if previous_stage is not None and stage_text != previous_stage:
            lines.append(r"\addlinespace")
        previous_stage = stage_text

        lines.append(
            " & ".join(
                [
                    latex_escape(stage_text),
                    latex_escape(row["knowledge_function_en"]),
                    latex_escape(row["tag_en"]),
                    str(int(row["peak_year"])),
                    str(int(row["freq"])),
                    str(int(row["begin"])),
                    str(int(row["end"])),
                    str(int(row["degree"])),
                    f"{float(row['centrality']):.3f}",
                ]
            )
            + r" \\"
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\begin{flushleft}",
            r"\footnotesize Note: Each row reports the highest-frequency matched term within a stage-by-knowledge-function lane. Freq. denotes the number of unique NSFC projects in which the term appears within that lane. Begin and End denote the first and last project start years in which the term appears in the corresponding stage. Degree is the number of directly connected knowledge-function tag nodes in the stage-level project co-occurrence network; centrality is the normalized weighted degree within the same network.",
            r"\end{flushleft}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def save_stage_term_table(long_df: pd.DataFrame) -> pd.DataFrame:
    table_df = build_stage_term_table(long_df)
    table_df.to_csv(
        TABLE_DIR / f"{TABLE_STEM}.csv",
        index=False,
        encoding="utf-8-sig",
    )

    latex_text = stage_term_table_to_latex(table_df)
    (TABLE_DIR / f"{TABLE_STEM}.tex").write_text(latex_text, encoding="utf-8")

    readme = (
        "Table 3 source files generated from Figure 5 data.\n"
        f"- {TABLE_STEM}.csv: source data for the table.\n"
        f"- {TABLE_STEM}.tex: LaTeX table for manuscript use.\n"
        "Metrics: frequency is the number of unique projects; degree and centrality are calculated within each stage.\n"
    )
    (TABLE_DIR / "README_table3.txt").write_text(readme, encoding="utf-8")
    return table_df


def compact_list(items: list[tuple[str, int]], max_items: int = 4) -> str:
    return "; ".join(
        f"{name} ({count})"
        for name, count in items[:max_items]
    )


def compact_centrality_list(items: list[tuple[str, str, float]], max_items: int = 5) -> str:
    return "; ".join(
        f"{tag} [{function}, {centrality:.2f}]"
        for tag, function, centrality in items[:max_items]
    )


def build_stage_profile_table(long_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a manuscript-oriented table for the main text.

    Unlike the detailed keyword-statistics table used in the reference paper,
    this table is organized around this study's stage logic and knowledge-
    function interpretation. The counts are tag-project hits, because Figure 5
    maps matched terms rather than single-label project classes.
    """
    if long_df.empty:
        return pd.DataFrame()

    unique_hits = long_df.drop_duplicates(
        ["project_index", "stage_cn", "knowledge_function_cn", "tag_cn"]
    ).copy()
    stage_rank = {stage: index for index, stage in enumerate(STAGE_ORDER)}
    unique_hits["stage_rank"] = unique_hits["stage_cn"].map(stage_rank)

    function_counts = (
        unique_hits
        .groupby(["stage_cn", "knowledge_function_cn"], as_index=False)
        .agg(tag_project_hits=("project_index", "size"))
    )
    function_counts["knowledge_function_en"] = function_counts["knowledge_function_cn"].map(
        lambda item: KNOWLEDGE_FUNCTION_LABELS[item].replace("\n", " ")
    )

    term_counts = (
        unique_hits
        .groupby(["stage_cn", "tag_en"], as_index=False)
        .agg(tag_project_hits=("project_index", "size"))
    )
    metrics = build_stage_cooccurrence_metrics(unique_hits)
    tag_name_lookup = (
        unique_hits[["tag_cn", "tag_en"]]
        .drop_duplicates()
        .set_index("tag_cn")["tag_en"]
        .to_dict()
    )
    metrics["tag_en"] = metrics["tag_cn"].map(tag_name_lookup)
    metrics["knowledge_function_en"] = metrics["knowledge_function_cn"].map(
        lambda item: KNOWLEDGE_FUNCTION_LABELS[item].replace("\n", " ")
    )

    rows: list[dict] = []
    for stage in STAGE_ORDER:
        stage_label = (
            f"{STAGE_META[stage]['label'].replace(chr(10), ' ')} "
            f"({STAGE_META[stage]['years'].replace('-', '--')})"
        )

        function_items = (
            function_counts[function_counts["stage_cn"].eq(stage)]
            .sort_values(["tag_project_hits", "knowledge_function_en"], ascending=[False, True])
            [["knowledge_function_en", "tag_project_hits"]]
            .itertuples(index=False, name=None)
        )
        term_items = (
            term_counts[term_counts["stage_cn"].eq(stage)]
            .sort_values(["tag_project_hits", "tag_en"], ascending=[False, True])
            [["tag_en", "tag_project_hits"]]
            .itertuples(index=False, name=None)
        )
        centrality_items = (
            metrics[metrics["stage_cn"].eq(stage)]
            .sort_values(["centrality", "degree", "weighted_degree", "tag_en"], ascending=[False, False, False, True])
            [["tag_en", "knowledge_function_en", "centrality"]]
            .itertuples(index=False, name=None)
        )

        rows.append(
            {
                "stage_cn": stage,
                "stage_en": stage_label,
                "dominant_knowledge_functions": compact_list(list(function_items), max_items=4),
                "representative_matched_terms": compact_list(list(term_items), max_items=6),
                "high_centrality_nodes": compact_centrality_list(list(centrality_items), max_items=5),
            }
        )

    return pd.DataFrame(rows)


def stage_profile_table_to_latex(table_df: pd.DataFrame) -> str:
    if table_df.empty:
        return ""

    lines = [
        r"\begin{table*}[!htbp]",
        r"\centering",
        r"\caption{Stage-wise knowledge-function profile and high-centrality tags in NSFC-funded heritage studies.}",
        r"\label{tab:stage_knowledge_function_profile}",
        r"\footnotesize",
        r"\begin{tabularx}{\textwidth}{p{2.9cm}X X X}",
        r"\toprule",
        r"Stage & Dominant knowledge functions & Representative matched terms & High-centrality nodes \\",
        r"\midrule",
    ]

    for _, row in table_df.iterrows():
        lines.append(
            " & ".join(
                [
                    latex_escape(row["stage_en"]),
                    latex_escape(row["dominant_knowledge_functions"]),
                    latex_escape(row["representative_matched_terms"]),
                    latex_escape(row["high_centrality_nodes"]),
                ]
            )
            + r" \\"
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\begin{flushleft}",
            r"\footnotesize Note: Counts in parentheses are tag-project hits derived from the Figure 5 long table. Values in square brackets report the corresponding knowledge function and normalized weighted-degree centrality of the tag node within the stage-level project co-occurrence network. The table summarizes the stage-level knowledge-function structure rather than citation frequencies.",
            r"\end{flushleft}",
            r"\end{table*}",
            "",
        ]
    )
    return "\n".join(lines)


def save_stage_profile_table(long_df: pd.DataFrame) -> pd.DataFrame:
    profile_df = build_stage_profile_table(long_df)
    profile_df.to_csv(
        TABLE_DIR / f"{TABLE_STEM}.csv",
        index=False,
        encoding="utf-8-sig",
    )
    (TABLE_DIR / f"{TABLE_STEM}.tex").write_text(
        stage_profile_table_to_latex(profile_df),
        encoding="utf-8",
    )

    # Keep a detailed source table for auditability, but do not use it as the
    # main manuscript table.
    detailed_df = build_stage_term_table(long_df)
    detailed_df.to_csv(
        TABLE_DIR / f"{TABLE_STEM}_detailed_source.csv",
        index=False,
        encoding="utf-8-sig",
    )

    readme = (
        "Table 3 is adapted to this study rather than copied from the reference keyword table.\n"
        f"- {TABLE_STEM}.tex: manuscript-ready stage-wise knowledge-function profile table.\n"
        f"- {TABLE_STEM}.csv: source data for the manuscript table.\n"
        f"- {TABLE_STEM}_detailed_source.csv: detailed stage-function-term statistics for audit.\n"
        "Counts are tag-project hits from the Figure 5 long table.\n"
    )
    (TABLE_DIR / "README_table3.txt").write_text(readme, encoding="utf-8")
    return profile_df


# ============================================================
# 6. 绘图函数
# ============================================================

def draw_temporal_edge(ax, edge: pd.Series) -> None:
    x0, y0 = float(edge["source_x"]), float(edge["source_y"])
    x1, y1 = float(edge["target_x"]), float(edge["target_y"])
    year_gap = max(float(edge["year_gap"]), 1.0)
    same_function = bool(edge["same_function"])
    function_distance = float(edge["function_distance"])

    dx = x1 - x0
    dy = y1 - y0
    if same_function:
        curve = PLOT_CONFIG["edge_arc_height_base"] + PLOT_CONFIG["edge_arc_height_scale"] * year_gap
        vertices = [
            (x0, y0),
            (x0 + dx * 0.38, y0 + curve),
            (x1 - dx * 0.38, y1 + curve),
            (x1, y1),
        ]
        alpha = PLOT_CONFIG["edge_alpha_same_function"]
    else:
        curve = (
            PLOT_CONFIG["edge_arc_height_base"]
            + PLOT_CONFIG["edge_arc_height_scale"] * year_gap
            + 0.035 * function_distance
        )
        sign = 1 if dy >= 0 else -1
        vertices = [
            (x0, y0),
            (x0 + dx * 0.42, y0 + dy * 0.18 + curve * sign),
            (x1 - dx * 0.42, y1 - dy * 0.18 + curve * sign),
            (x1, y1),
        ]
        alpha = PLOT_CONFIG["edge_alpha_cross_function"]

    path = MplPath(
        vertices,
        [
            MplPath.MOVETO,
            MplPath.CURVE4,
            MplPath.CURVE4,
            MplPath.CURVE4,
        ],
    )
    ax.add_patch(
        PathPatch(
            path,
            facecolor="none",
            edgecolor=str(edge["color"]),
            lw=edge_width(float(edge.get("visual_weight", edge["weight"]))),
            alpha=alpha,
            capstyle="round",
            joinstyle="round",
            zorder=1 if same_function else 2,
        )
    )


def draw_same_year_cross_edge(ax, edge: pd.Series) -> None:
    x0, y0 = float(edge["source_x"]), float(edge["source_y"])
    x1, y1 = float(edge["target_x"]), float(edge["target_y"])
    x_mid = (x0 + x1) / 2 + 0.20
    path = MplPath(
        [
            (x0, y0),
            (x_mid, y0),
            (x_mid, y1),
            (x1, y1),
        ],
        [
            MplPath.MOVETO,
            MplPath.CURVE4,
            MplPath.CURVE4,
            MplPath.CURVE4,
        ],
    )
    ax.add_patch(
        PathPatch(
            path,
            facecolor="none",
            edgecolor=str(edge["color"]),
            lw=max(0.46, edge_width(float(edge.get("visual_weight", edge["weight"]))) * 0.72),
            alpha=PLOT_CONFIG["same_year_cross_edge_alpha"],
            capstyle="round",
            joinstyle="round",
            zorder=1,
        )
    )


def draw_project_cross_function_edge(ax, edge: pd.Series) -> None:
    x0, y0 = float(edge["source_x"]), float(edge["source_y"])
    x1, y1 = float(edge["target_x"]), float(edge["target_y"])
    distance = max(float(edge.get("function_distance", 1)), 1.0)
    dx = x1 - x0
    dy = y1 - y0
    side_shift = 0.16 if x1 >= x0 else -0.16
    curve = 0.10 + 0.030 * distance
    path = MplPath(
        [
            (x0, y0),
            (x0 + dx * 0.35 + side_shift, y0 + dy * 0.18 + curve),
            (x1 - dx * 0.35 + side_shift, y1 - dy * 0.18 - curve),
            (x1, y1),
        ],
        [
            MplPath.MOVETO,
            MplPath.CURVE4,
            MplPath.CURVE4,
            MplPath.CURVE4,
        ],
    )
    weight = float(edge.get("weight", 1))
    lw = min(
        PLOT_CONFIG["project_cross_edge_linewidth_cap"],
        PLOT_CONFIG["project_cross_edge_linewidth_base"]
        + PLOT_CONFIG["project_cross_edge_linewidth_scale"] * math.log1p(max(weight, 1.0)),
    )
    alpha = min(
        PLOT_CONFIG["project_cross_edge_alpha_max"],
        PLOT_CONFIG["project_cross_edge_alpha_min"] + 0.045 * math.log1p(max(weight, 1.0)),
    )
    ax.add_patch(
        PathPatch(
            path,
            facecolor="none",
            edgecolor=PLOT_CONFIG["project_cross_edge_color"],
            lw=lw,
            linestyle=PLOT_CONFIG["project_cross_edge_dash"],
            alpha=alpha,
            capstyle="round",
            joinstyle="round",
            zorder=1.15 + min(weight, 8.0) * 0.012,
        )
    )


def draw_background(ax) -> None:
    y_positions = function_y_positions()
    y_min = min(y_positions.values()) - PLOT_CONFIG["bottom_padding"]
    y_max = max(y_positions.values()) + PLOT_CONFIG["top_padding"]

    # 三个阶段作为背景区间；具体年份仍显示在顶部。
    for stage, meta in STAGE_META.items():
        start = float(meta["start"]) - 0.50
        end = float(meta["end"]) + 0.50
        ax.add_patch(
            Rectangle(
                (start, y_min),
                end - start,
                y_max - y_min + 0.04,
                facecolor=meta["color"],
                edgecolor="none",
                alpha=0.10,
                zorder=0,
            )
        )
        ax.text(
            (float(meta["start"]) + float(meta["end"])) / 2,
            PLOT_CONFIG["stage_label_y"],
            f"{meta['label']}\n({meta['years']})",
            ha="center",
            va="bottom",
            fontsize=PLOT_CONFIG["stage_label_fontsize"],
            color=meta["color"],
            fontweight="bold",
            linespacing=0.92,
            zorder=5,
        )

    # 年份刻度和竖向参考线。
    ax.hlines(
        PLOT_CONFIG["year_tick_y"],
        min(YEAR_RANGE),
        max(YEAR_RANGE),
        color="#C9CED6",
        lw=0.85,
        alpha=0.70,
        zorder=0,
    )
    for year in YEAR_RANGE:
        ax.vlines(
            year,
            y_min,
            PLOT_CONFIG["year_tick_y"] + 0.05,
            color="#D7DBE2",
            lw=0.58,
            alpha=0.55,
            zorder=0,
        )
        ax.vlines(
            year,
            PLOT_CONFIG["year_tick_y"] - 0.05,
            PLOT_CONFIG["year_tick_y"] + 0.05,
            color="#9FA6B2",
            lw=0.72,
            alpha=0.86,
            zorder=1,
        )
        ax.text(
            year,
            PLOT_CONFIG["year_label_y"],
            str(year),
            ha="center",
            va="bottom",
            fontsize=PLOT_CONFIG["year_label_fontsize"],
            color="#40444A",
            rotation=0,
            zorder=5,
        )

    # 知识功能横线和右侧标签。
    x_left = min(YEAR_RANGE) - PLOT_CONFIG["x_left_pad"]
    x_right = max(YEAR_RANGE) + 0.45
    right_label_x = x_right + PLOT_CONFIG["right_label_pad"]
    for index, function in enumerate(KNOWLEDGE_FUNCTION_ORDER):
        y = y_positions[function]
        color = KNOWLEDGE_FUNCTION_COLORS[function]
        ax.hlines(
            y,
            x_left,
            x_right,
            color=color,
            lw=PLOT_CONFIG["lane_linewidth"],
            alpha=PLOT_CONFIG["lane_alpha"],
            zorder=0,
        )
        ax.hlines(
            y,
            x_left,
            x_right,
            color=color,
            lw=0.55,
            alpha=PLOT_CONFIG["lane_dash_alpha"],
            linestyles=(0, (1.8, 3.0)),
            zorder=0,
        )
        ax.text(
            right_label_x,
            y,
            f"#{index} {KNOWLEDGE_FUNCTION_LABELS[function]}",
            ha="left",
            va="center",
            fontsize=PLOT_CONFIG["function_label_fontsize"],
            color=color,
            fontweight=PLOT_CONFIG["function_label_weight"],
            linespacing=1.05,
            zorder=6,
        )

    ax.text(
        min(YEAR_RANGE) - PLOT_CONFIG["x_left_pad"],
        PLOT_CONFIG["title_y"],
        "Knowledge-function tag timeline",
        ha="left",
        va="bottom",
        fontsize=PLOT_CONFIG["title_fontsize"],
        color="#111111",
        fontweight="bold",
        zorder=6,
    )
    if PLOT_CONFIG.get("show_panel_label", False):
        ax.text(
            min(YEAR_RANGE) - PLOT_CONFIG["x_left_pad"],
            PLOT_CONFIG["title_y"] + 0.45,
            PLOT_CONFIG.get("panel_label", "a"),
            ha="left",
            va="bottom",
            fontsize=PLOT_CONFIG["panel_label_fontsize"],
            color="#111111",
            fontweight="bold",
            zorder=6,
        )


def draw_nodes(ax, nodes_df: pd.DataFrame) -> None:
    if nodes_df.empty:
        return

    shown_nodes = nodes_df[nodes_df["is_displayed"].eq(True)].copy()
    if shown_nodes.empty:
        return

    max_count = float(shown_nodes["visual_count"].max())
    collapsed_cells = (
        shown_nodes[shown_nodes["is_collapsed_cell"].eq(True)]
        .sort_values(["display_cell_bridge_total_count", "display_cell_top_tag_cn"], ascending=[False, True])
        .drop_duplicates(["start_year", "knowledge_function_cn"], keep="first")
        .copy()
    )
    collapsed_members = shown_nodes[shown_nodes["is_collapsed_cell"].eq(True)].copy()
    individual_nodes = shown_nodes[shown_nodes["is_collapsed_cell"].ne(True)].copy()
    ordinary_max_weight = (
        float(individual_nodes["ordinary_visual_weight"].max())
        if not individual_nodes.empty
        else 1.0
    )
    ordinary_min_weight = (
        float(individual_nodes["ordinary_visual_weight"].min())
        if not individual_nodes.empty
        else 0.0
    )

    # 重复出现的 tag 先绘制柔和外圈，提示它在多个年份持续活跃。
    recurrent = individual_nodes[individual_nodes["is_recurrent_tag"].eq(True)].copy()
    if not recurrent.empty:
        recurrent_sizes = ordinary_node_area_from_weight(
            recurrent["ordinary_visual_weight"].to_numpy(dtype=float),
            ordinary_max_weight,
            ordinary_min_weight,
        ) * 1.34
        ax.scatter(
            recurrent["draw_x"],
            recurrent["draw_y"],
            s=recurrent_sizes,
            facecolor="none",
            edgecolor=recurrent["color"],
            linewidth=1.05,
            alpha=PLOT_CONFIG["recurrence_ring_alpha"],
            zorder=3,
        )

    # 高频节点绘制为“年轮”式复合节点：外部半透明层表示持续性，
    # 内部白色圆环把多个叠加命中压缩为一个更清晰的节点。
    ringed_nodes = individual_nodes[individual_nodes["is_ringed_node"].eq(True)].copy()
    if not ringed_nodes.empty:
        ringed_sizes = node_area_from_count(ringed_nodes["visual_count"].to_numpy(dtype=float), max_count)
        for scale, alpha in zip(
            PLOT_CONFIG["ring_layer_scales"],
            PLOT_CONFIG["ring_layer_alphas"],
        ):
            ax.scatter(
                ringed_nodes["draw_x"],
                ringed_nodes["draw_y"],
                s=ringed_sizes * scale,
                color=ringed_nodes["color"],
                edgecolor="none",
                alpha=alpha,
                zorder=3.4,
            )
        for scale in PLOT_CONFIG["inner_ring_scales"]:
            ax.scatter(
                ringed_nodes["draw_x"],
                ringed_nodes["draw_y"],
                s=ringed_sizes * scale,
                facecolor="none",
                edgecolor="white",
                linewidth=0.92,
                alpha=0.72,
                zorder=6,
            )

    # 跨多个知识功能的 tag 使用紫色外圈提示其桥接性。
    bridge = individual_nodes[individual_nodes["is_bridge_tag"].eq(True)].copy()
    if not bridge.empty:
        bridge_sizes = node_area_from_count(bridge["visual_count"].to_numpy(dtype=float), max_count) * 1.42
        ax.scatter(
            bridge["draw_x"],
            bridge["draw_y"],
            s=bridge_sizes,
            facecolor="none",
            edgecolor=PLOT_CONFIG["bridge_ring_color"],
            linewidth=PLOT_CONFIG["bridge_ring_linewidth"],
            alpha=PLOT_CONFIG["bridge_ring_alpha"],
            zorder=6.4,
        )

    # 高密度单元格压缩为一个复合年轮节点，避免同一位置多个节点互相覆盖。
    if not collapsed_cells.empty:
        collapsed_sizes = node_area_from_count(
            collapsed_cells["visual_count"].to_numpy(dtype=float),
            max_count,
        )
        collapsed_sizes = np.maximum(
            collapsed_sizes * PLOT_CONFIG["collapsed_node_size_scale"],
            PLOT_CONFIG["collapsed_node_min_size"],
        )
        for scale, alpha in zip(
            PLOT_CONFIG["ring_layer_scales"],
            PLOT_CONFIG["ring_layer_alphas"],
        ):
            ax.scatter(
                collapsed_cells["draw_x"],
                collapsed_cells["draw_y"],
                s=collapsed_sizes * scale,
                color=collapsed_cells["color"],
                edgecolor="none",
                alpha=alpha,
                zorder=4.2,
            )
        ax.scatter(
            collapsed_cells["draw_x"],
            collapsed_cells["draw_y"],
            s=collapsed_sizes,
            color=collapsed_cells["color"],
            edgecolor="white",
            linewidth=1.05,
            alpha=0.88,
            zorder=5.2,
        )
        for node_index, (_, node) in enumerate(collapsed_cells.iterrows()):
            ring_count = int(
                min(
                    max(float(node.get("display_cell_node_count", 3)), 3),
                    10,
                )
            )
            ring_scales = np.linspace(0.86, 0.20, ring_count)
            for scale in ring_scales:
                ax.scatter(
                    [float(node["draw_x"])],
                    [float(node["draw_y"])],
                    s=[collapsed_sizes[node_index] * scale],
                    facecolor="none",
                    edgecolor="white",
                    linewidth=0.86,
                    alpha=0.74,
                    zorder=6.2,
                )
            members = (
                collapsed_members[
                    collapsed_members["start_year"].astype(int).eq(int(node["start_year"]))
                    & collapsed_members["knowledge_function_cn"].eq(node["knowledge_function_cn"])
                ]
                .sort_values(["count", "display_score", "tag_cn"], ascending=[False, False, True])
                .head(12)
                .copy()
            )
            if not members.empty:
                mini_count = len(members)
                angles = np.linspace(0, 2 * np.pi, mini_count, endpoint=False)
                if mini_count == 1:
                    mini_x = np.array([float(node["draw_x"])])
                    mini_y = np.array([float(node["draw_y"])])
                else:
                    orbit_x = 0.040 + min(0.055, 0.0055 * math.sqrt(float(node["visual_count"])))
                    orbit_y = 0.030 + min(0.040, 0.0042 * math.sqrt(float(node["visual_count"])))
                    mini_x = float(node["draw_x"]) + np.cos(angles) * orbit_x
                    mini_y = float(node["draw_y"]) + np.sin(angles) * orbit_y
                member_counts = members["count"].to_numpy(dtype=float)
                if member_counts.max() > member_counts.min():
                    mini_sizes = np.interp(
                        member_counts,
                        (member_counts.min(), member_counts.max()),
                        (
                            PLOT_CONFIG["collapsed_inner_node_min_size"],
                            PLOT_CONFIG["collapsed_inner_node_max_size"],
                        ),
                    )
                else:
                    mini_sizes = np.full(
                        mini_count,
                        (PLOT_CONFIG["collapsed_inner_node_min_size"] + PLOT_CONFIG["collapsed_inner_node_max_size"]) / 2,
                    )
                ax.scatter(
                    mini_x,
                    mini_y,
                    s=mini_sizes,
                    facecolor="white",
                    edgecolor=node["color"],
                    linewidth=0.72,
                    alpha=PLOT_CONFIG["collapsed_inner_node_alpha"],
                    zorder=6.7,
                )
        bridge_collapsed = collapsed_cells[collapsed_cells["is_collapsed_bridge_cell"].eq(True)]
        if not bridge_collapsed.empty:
            bridge_sizes = node_area_from_count(
                bridge_collapsed["visual_count"].to_numpy(dtype=float),
                max_count,
            )
            bridge_sizes = np.maximum(
                bridge_sizes * 1.36,
                PLOT_CONFIG["collapsed_node_min_size"] * 1.12,
            )
            ax.scatter(
                bridge_collapsed["draw_x"],
                bridge_collapsed["draw_y"],
                s=bridge_sizes,
                facecolor="none",
                edgecolor=PLOT_CONFIG["bridge_ring_color"],
                linewidth=1.35,
                alpha=PLOT_CONFIG["bridge_ring_alpha"],
                zorder=6.6,
            )

    for function in KNOWLEDGE_FUNCTION_ORDER:
        sub = individual_nodes[individual_nodes["knowledge_function_cn"].eq(function)].copy()
        if sub.empty:
            continue
        sizes = ordinary_node_area_from_weight(
            sub["ordinary_visual_weight"].to_numpy(dtype=float),
            ordinary_max_weight,
            ordinary_min_weight,
        )
        ax.scatter(
            sub["draw_x"],
            sub["draw_y"],
            s=sizes,
            color=KNOWLEDGE_FUNCTION_COLORS[function],
            edgecolor=PLOT_CONFIG["node_edgecolor"],
            linewidth=PLOT_CONFIG["node_linewidth"],
            alpha=PLOT_CONFIG["node_alpha"],
            zorder=5,
        )


def draw_labels(ax, nodes_df: pd.DataFrame) -> None:
    label_nodes = nodes_df[
        nodes_df["should_label"].eq(True)
        & nodes_df["is_displayed"].eq(True)
    ].copy()
    if label_nodes.empty:
        return

    collapsed_label_nodes = (
        label_nodes[label_nodes["is_collapsed_cell"].eq(True)]
        .sort_values(["visual_count", "label_score", "tag_en"], ascending=[False, False, True])
        .drop_duplicates(["start_year", "knowledge_function_cn"], keep="first")
    )
    individual_label_nodes = label_nodes[label_nodes["is_collapsed_cell"].ne(True)]
    label_nodes = pd.concat([individual_label_nodes, collapsed_label_nodes], ignore_index=True)

    label_nodes = label_nodes.sort_values(["draw_y", "draw_x", "visual_count"], ascending=[False, True, False])
    for _, node in label_nodes.iterrows():
        label_source = node["tag_en"]
        if bool(node.get("is_collapsed_cell", False)) and pd.notna(node.get("display_cell_top_tag_en", pd.NA)):
            label_source = node["display_cell_top_tag_en"]
        label = wrap_text(
            str(label_source),
            PLOT_CONFIG["tag_label_wrap_width"],
        )
        rank = int(node["label_rank_stage_function"]) if pd.notna(node["label_rank_stage_function"]) else 1
        base_offset = (
            PLOT_CONFIG["ring_label_y_offset"]
            if bool(node.get("is_collapsed_cell", False))
            else PLOT_CONFIG["label_y_offset"]
        )
        y_offset = base_offset + (rank - 1) * PLOT_CONFIG["label_rank_y_step"]
        if float(node["draw_y"]) <= 0.15:
            y_offset = base_offset * 0.78
            va = "bottom"
        elif float(node["draw_y"]) < 0.6:
            y_offset = -(
                base_offset
                + (rank - 1) * PLOT_CONFIG["label_rank_y_step"]
            ) * 1.18
            va = "top"
        else:
            va = "bottom"
        ax.text(
            float(node["draw_x"]),
            float(node["draw_y"]) + y_offset,
            label,
            ha="center",
            va=va,
            fontsize=PLOT_CONFIG["tag_label_fontsize"],
            color=PLOT_CONFIG["tag_label_color"],
            bbox={
                "boxstyle": "round,pad=0.17",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": PLOT_CONFIG["tag_label_bbox_alpha"],
            },
            zorder=7,
        )


def draw_size_legend(ax, nodes_df: pd.DataFrame) -> None:
    if nodes_df.empty:
        return

    shown_nodes = nodes_df[nodes_df["is_displayed"].eq(True)].copy()
    if shown_nodes.empty:
        return

    max_count = int(math.ceil(float(shown_nodes["visual_count"].max())))
    values = [
        value
        for value in PLOT_CONFIG["legend_values"]
        if value <= max_count
    ]
    if max_count not in values:
        values.append(max_count)
    values = sorted(set(values))

    handles: list[object] = []
    labels: list[str] = []

    # 1. Node size legend: number of projects represented by a node.
    for value in values:
        marker_area = node_area_from_count([value], max_count)[0]
        handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor="#9AA7B2",
                markeredgecolor="white",
                markersize=math.sqrt(marker_area) / 1.08,
            )
        )
        labels.append(f"{value} project" if value == 1 else f"{value} projects")

    # 2. Annual-ring node legend: recurrent / high-centrality tag.
    annual_ring_handle = AnnualRingLegendObject(
        facecolor=PLOT_CONFIG["annual_ring_legend_color"],
        bridge_color=PLOT_CONFIG["bridge_ring_color"],
        bridge=False,
    )
    handles.append(annual_ring_handle)
    labels.append("annual-ring node\n(recurrent / high-frequency tag)")

    # 3. Annual-ring node with purple outline: tag spanning multiple functions.
    multi_function_handle = AnnualRingLegendObject(
        facecolor=PLOT_CONFIG["annual_ring_legend_color"],
        bridge_color=PLOT_CONFIG["bridge_ring_color"],
        bridge=True,
    )
    handles.append(multi_function_handle)
    labels.append("multi-function tag")

    ax.legend(
        handles=handles,
        labels=labels,
        loc="lower left",
        bbox_to_anchor=(0.012, 0.012),
        frameon=False,
        fontsize=PLOT_CONFIG["size_legend_fontsize"],
        handletextpad=0.65,
        handlelength=1.65,
        handleheight=1.45,
        labelspacing=0.58,
        borderaxespad=0,
        handler_map={AnnualRingLegendObject: HandlerAnnualRing()},
    )


def draw_figure(nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(
        figsize=(PLOT_CONFIG["figure_width"], PLOT_CONFIG["figure_height"]),
        dpi=PLOT_CONFIG["figure_dpi"],
    )
    fig.patch.set_facecolor(PLOT_CONFIG["background"])
    ax.set_facecolor(PLOT_CONFIG["background"])

    draw_background(ax)

    if not edges_df.empty:
        temporal_edges = edges_df[edges_df["edge_type"].eq("same_tag_temporal_continuity")]
        same_year_edges = edges_df[edges_df["edge_type"].eq("same_tag_same_year_cross_function")]
        project_cross_edges = (
            edges_df[edges_df["edge_type"].eq("project_cross_function_cooccurrence")]
            .sort_values(["weight", "function_distance"], ascending=[True, True])
        )

        for _, edge in project_cross_edges.iterrows():
            draw_project_cross_function_edge(ax, edge)
        for _, edge in temporal_edges.iterrows():
            draw_temporal_edge(ax, edge)
        for _, edge in same_year_edges.iterrows():
            draw_same_year_cross_edge(ax, edge)

    draw_nodes(ax, nodes_df)
    draw_labels(ax, nodes_df)
    draw_size_legend(ax, nodes_df)

    y_positions = function_y_positions()
    ax.set_xlim(
        min(YEAR_RANGE) - PLOT_CONFIG["x_left_pad"] - 0.08,
        max(YEAR_RANGE) + PLOT_CONFIG["x_right_pad"] + 2.02,
    )
    ax.set_ylim(
        min(y_positions.values()) - PLOT_CONFIG["bottom_padding"],
        PLOT_CONFIG["title_y"] + 0.82,
    )
    ax.axis("off")
    fig.subplots_adjust(left=0.025, right=0.985, top=0.975, bottom=0.055)
    return fig


def save_figure(fig: plt.Figure) -> None:
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
    if PLOT_CONFIG["save_tiff"]:
        fig.savefig(
            FIG_DIR / f"{FIGURE_STEM}.tiff",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight",
        )


# ============================================================
# 7. 主程序
# ============================================================

def main() -> None:
    require_font(
        PLOT_CONFIG["font_family"],
        PLOT_CONFIG["strict_font"],
    )

    long_df = load_project_tag_long_table()
    nodes_df = build_nodes(long_df)
    edges_df = build_edges(nodes_df, long_df)
    save_source_data(nodes_df, edges_df, long_df)
    table_df = save_stage_profile_table(long_df)

    fig = draw_figure(nodes_df, edges_df)
    save_figure(fig)
    plt.close(fig)

    print(f"Saved Figure 5 timeline map to: {FIG_DIR}")
    print(f"Nodes: {len(nodes_df)}; edges: {len(edges_df)}")
    print(f"Saved Table 3 files to: {TABLE_DIR}; rows: {len(table_df)}")


if __name__ == "__main__":
    main()
