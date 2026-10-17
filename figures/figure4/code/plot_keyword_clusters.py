# -*- coding: utf-8 -*-

"""
NSFC 遗产研究三个编码维度的关键词聚类图。

本脚本分别生成三个关键词聚类图：

    a) Heritage object indicators and their hit keywords
       遗产对象二级指标及其命中关键词

    b) Research orientation indicators and their hit keywords
       研究问题取向二级指标及其命中关键词

    c) Methodological orientation indicators and their hit keywords
       方法取向二级指标及其命中关键词

图形逻辑：
    1. 每一个大簇对应一个二级指标；
    2. 大节点表示二级指标；
    3. 小节点表示 LLM 结构化抽取出的关键词标签；
    4. 节点大小表示该指标或关键词出现的项目数量；
    5. 二级指标—关键词边表示项目级命中关系；
    6. 关键词—关键词边表示同一二级指标内部关键词共现关系。

本版优化重点：
    1. 修正参数改动不明显的问题：
       原因是原代码使用自动坐标范围，会抵消 cluster_layout_scale 的视觉效果。
       本版增加 use_fixed_axis_limits=True，使整体紧凑度参数真实生效。

    2. 修正 cluster_layout_scale 误设为负数的问题：
       cluster_layout_scale 必须为正数。数值越小，簇中心越紧凑。

    3. 增大每个簇的背景圆：
       让每个簇有更大的视觉承载空间，可以显示更多关键词信息。

    4. 簇内部关键词节点更松弛：
       关键词节点围绕中心节点分布更舒展，减少重叠。

    5. 绘图参数高度自定义：
       主要调节集中在 PLOT_CONFIG 中。

输出内容：
    1. 三张关键词聚类图：SVG / PDF / PNG / TIFF
    2. 每张图对应的节点数据
    3. 每张图对应的“二级指标—关键词”边数据
    4. 每张图对应的“关键词—关键词”共现边数据
    5. 图件 manifest 文件
    6. 英文图注文本
"""

from __future__ import annotations

import hashlib
import math
import textwrap
from collections import Counter
from itertools import combinations
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.patches import Ellipse


# ============================================================
# 1. 路径设置
# ============================================================

# 项目根目录。
ROOT = Path(__file__).resolve().parents[1]

# 输入数据文件。
DATA_FILE = ROOT / "data" / "inputs" / "base_analysis_dataset" / "analysis_dataset_in_scope.csv"

# 输出目录。
# 本版按照用户指定，直接输出到：
# E:\NC\框架\5.6纪导框架\heritage_research_agenda\heritage_research_agenda\制图\figure3\figure聚类修
OUT_DIR = ROOT / "outputs" / "reproduced"

# 图像文件直接保存在 OUT_DIR 根目录下，不再放入 figures 子文件夹。
FIG_DIR = OUT_DIR

# 源数据仍单独放入 source_data 子文件夹，避免 CSV 与图像文件混在一起。
SRC_DIR = OUT_DIR / "source_data"

for folder in [OUT_DIR, SRC_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. 高度自定义绘图参数
# ============================================================

PLOT_CONFIG = {
    # ========================================================
    # 字体
    # ========================================================
    "font_family": "Arial",
    "strict_font": True,

    # ========================================================
    # 画布
    # ========================================================
    "figure_width": 11.2,
    "figure_height": 7.6,
    "figure_dpi": 300,
    "output_dpi": 600,
    "background": "white",

    # ========================================================
    # 整体簇布局控制
    # ========================================================
    # 必须为正数。
    # 数值越小，簇中心越靠近；数值越大，簇之间越分散。
    # 推荐范围：0.66–0.88。
    "cluster_layout_scale": 0.88,

    # 横向和纵向压缩比例。
    "cluster_x_scale": 1.02,
    "cluster_y_scale": 0.98,

    # 是否使用固定坐标范围。
    # True：cluster_layout_scale 的视觉效果会明显生效。
    # False：自动坐标范围会抵消整体缩放效果。
    "use_fixed_axis_limits": True,

    # 固定坐标范围。
    # 如果簇被裁切，适当放大范围；
    # 如果图太空，缩小范围。
    "fixed_xlim": (-1.95, 1.95),
    "fixed_ylim": (-1.60, 1.60),

    # ========================================================
    # 簇内部松弛度
    # ========================================================
    # 控制关键词节点离中心节点的距离。
    # 数值越大，每个簇内部越松弛。
    "keyword_ring_base": 0.34,
    "keyword_ring_step": 0.085,
    "keyword_ring_cycle": 3,

    # y 方向环形压缩。
    # 越接近 1，簇越圆；越小，簇越扁。
    "keyword_ring_y_scale": 0.92,

    # 稳定扰动，防止关键词节点完全重叠。
    "keyword_jitter_scale": 0.038,

    # ========================================================
    # 簇背景圆 / 椭圆
    # ========================================================
    "show_cluster_background": True,

    # 背景圆透明度。
    "cluster_ellipse_alpha": 0.080,

    # 控制每个簇背景圆的大小。
    # 数值越大，背景圆越大。
    "cluster_ellipse_width_scale": 1.34,
    "cluster_ellipse_height_scale": 1.34,

    # 最小背景圆尺寸。
    # 调大后，小簇也会有更大的视觉承载空间。
    "cluster_ellipse_min_width": 0.72,
    "cluster_ellipse_min_height": 0.58,

    # 是否强制背景更接近圆形。
    "force_round_cluster_background": False,

    # ========================================================
    # 节点大小
    # ========================================================
    # 关键词节点大小。
    "keyword_node_size_base": 28,
    "keyword_node_size_scale": 5.2,
    "keyword_node_size_max": 245,

    # 二级指标中心节点大小。
    "category_node_size_base": 960,
    "category_node_size_scale": 2.8,
    "category_node_size_max": 1450,

    # 节点样式。
    "keyword_node_alpha": 0.94,
    "category_node_alpha": 0.97,
    "node_edgecolor": "white",
    "keyword_node_linewidth": 0.55,
    "category_node_linewidth": 1.00,

    # ========================================================
    # 边样式
    # ========================================================
    "keyword_keyword_edge_color": "#C9CED6",
    "keyword_keyword_edge_alpha": 0.4,
    "keyword_keyword_edge_width_base": 0.14,
    "keyword_keyword_edge_width_scale": 0.10,
    "keyword_keyword_edge_weight_cap": 8,

    "category_keyword_edge_alpha": 0.6,
    "category_keyword_edge_width_base": 0.20,
    "category_keyword_edge_width_scale": 0.12,
    "category_keyword_edge_weight_cap": 10,

    # ========================================================
    # 簇标签
    # ========================================================
    "show_cluster_labels": False,
    "show_cluster_index": True,

    "cluster_label_fontsize": 8.8,
    "cluster_label_fontweight": "bold",
    "cluster_label_wrap_width": 24,

    # 簇标签距离中心节点的高度。
    "cluster_label_y_offset": 0.40,

    # 簇标签底框。
    "cluster_label_bbox": True,
    "cluster_label_bbox_facecolor": "white",
    "cluster_label_bbox_alpha": 0.68,
    "cluster_label_bbox_edgecolor": "none",
    "cluster_label_bbox_pad": 0.25,

    # 中心节点标签。
    "show_center_node_labels": True,
    "center_node_label_fontsize": 11,
    "center_node_label_wrap_width": 11,
    "center_node_label_color": "#111111",
    "center_node_label_fontweight": "bold",

    # ========================================================
    # 关键词标签
    # ========================================================
    "show_keyword_labels": True,

    # 每个簇显示多少个关键词。
    # 想显示更多信息可设为 5 或 6；
    # 如果过挤，改成 3 或 4。
    "keyword_labels_per_cluster": 2,

    "keyword_label_fontsize": 6,
    "keyword_label_wrap_width": 15,
    "keyword_label_color": "#9B2D30",
    "keyword_label_use_cluster_color": True,
    "keyword_label_lightness_cap": 0.62,
    "keyword_label_fontweight_threshold": 8,

    # 关键词标签相对关键词节点的纵向偏移。
    "keyword_label_radial_offset": 0.12,
    "keyword_label_min_y_gap": 0.075,

    # 关键词标签底框。
    "keyword_label_bbox": True,
    "keyword_label_bbox_facecolor": "white",
    "keyword_label_bbox_alpha": 0.76,
    "keyword_label_bbox_edgecolor": "none",
    "keyword_label_bbox_pad": 0.32,

    # ========================================================
    # 子图编号与标题
    # ========================================================
    "show_panel_label": False,
    "panel_label_fontsize": 13,
    "panel_label_fontweight": "bold",

    "show_dimension_title": True,
    "dimension_title_fontsize": 13,
    "dimension_title_fontweight": "bold",
    "dimension_title_y": 0.985,

    # ========================================================
    # 自动坐标模式下的留白
    # use_fixed_axis_limits=True 时，这两个参数不主导图形缩放。
    # ========================================================
    "pad_x": 0.28,
    "pad_y": 0.28,

    # ========================================================
    # 保存
    # ========================================================
    "save_svg": True,
    "save_pdf": True,
    "save_png": True,
    "save_tiff": True,
    "show_plot": False,
}


# ============================================================
# 3. 图形颜色设置
# ============================================================

# 三个编码维度的主色。
DIMENSION_COLORS = {
    "heritage_object": "#89B2F4",
    "research_orientation": "#018C94",
    "method_orientation": "#764D9C",
}

# 簇调色板。
CLUSTER_PALETTE = [
    "#D65F5F",  # red
    "#E68A2E",  # orange
    "#D7C600",  # yellow
    "#3DAA3D",  # green
    "#10B981",  # teal-green
    "#1BA6C9",  # cyan
    "#2E73D2",  # blue
    "#6F58C9",  # purple
    "#B34FA3",  # magenta
    "#8C6D31",  # brown
]


# ============================================================
# 4. 字体与通用工具函数
# ============================================================

def require_arial_font(font_name: str = "Arial", strict: bool = True) -> None:
    """
    设置绘图字体。

    参数：
        font_name:
            字体名称。英文期刊图件建议使用 Arial。

        strict:
            True 表示如果未检测到 Arial 就直接报错；
            False 表示允许 Matplotlib 自动回退到其他字体。
    """
    available_fonts = {f.name for f in fm.fontManager.ttflist}

    if strict and font_name not in available_fonts:
        raise RuntimeError(
            f"Arial font was not detected by Matplotlib. Please install {font_name}, "
            f"or set PLOT_CONFIG['strict_font'] = False."
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


def stable_jitter(key: str, scale: float = 0.10) -> tuple[float, float]:
    """
    为节点生成稳定扰动。

    作用：
        1. 减少关键词节点重叠；
        2. 保证每次运行时同一个关键词位置基本一致。
    """
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()

    a = int(digest[:8], 16) / 0xFFFFFFFF
    b = int(digest[8:16], 16) / 0xFFFFFFFF

    angle = a * 2 * math.pi
    radius = scale * (0.35 + 0.65 * b)

    return math.cos(angle) * radius, math.sin(angle) * radius


def wrap_label(label: str, width: int = 18) -> str:
    """
    对英文标签进行换行。
    """
    return "\n".join(
        textwrap.wrap(
            str(label),
            width=width,
            break_long_words=False
        )
    )


def readable_cluster_text_color(color: str) -> str:
    """
    将关键词标签设为所属簇的同色系颜色，并压低过亮颜色的明度。
    """

    if not PLOT_CONFIG["keyword_label_use_cluster_color"]:
        return PLOT_CONFIG["keyword_label_color"]

    r, g, b = mpl.colors.to_rgb(color)
    h, saturation, value = mpl.colors.rgb_to_hsv((r, g, b))

    # HSV 的 value 对可读性更敏感；黄色等高亮颜色在白底上需要压暗。
    value_cap = PLOT_CONFIG["keyword_label_lightness_cap"]
    adjusted = mpl.colors.hsv_to_rgb(
        (
            h,
            max(saturation, 0.72),
            min(value, value_cap),
        )
    )

    return mpl.colors.to_hex(adjusted)


CENTER_LABEL_ALIASES = {
    "Architectural heritage": "Architectural\nheritage",
    "Industrial heritage": "Industrial\nheritage",
    "Cultural landscapes and linear heritage": "Cultural landscapes\n& linear heritage",
    "Rural and agricultural heritage": "Rural & agricultural\nheritage",
    "Intangible and living heritage": "Intangible & living\nheritage",
    "Archaeological heritage": "Archaeological\nheritage",
    "Governance and participation": "Governance\n& participation",
    "Value identification": "Value\nidentification",
    "Revitalization and regeneration": "Revitalization\n& regeneration",
    "Conservation and monitoring": "Conservation\n& monitoring",
    "Digital documentation": "Digital\ndocumentation",
    "Risk and resilience": "Risk\n& resilience",
    "Model-based evaluation": "Model-based\nevaluation",
    "Historical archives": "Historical\narchives",
    "Digital modeling": "Digital\nmodeling",
    "Experimental testing": "Experimental\ntesting",
    "Intelligent computing": "Intelligent\ncomputing",
}


def center_label_text(index: int, label: str) -> str:
    """
    生成中心节点内部的二级指标标签。
    """

    alias = CENTER_LABEL_ALIASES.get(label, label)
    wrapped_parts = []

    for part in alias.split("\n"):
        wrapped_parts.extend(
            textwrap.wrap(
                part,
                width=PLOT_CONFIG["center_node_label_wrap_width"],
                break_long_words=False,
            )
        )

    return "\n".join(wrapped_parts)


def split_tags(value: object) -> list[str]:
    """
    拆分 LLM 抽取出的标签字段。

    支持英文分号 ; 和中文分号 ；。
    自动去除空值和“信息不足”。
    """
    if pd.isna(value):
        return []

    tags = [
        item.strip()
        for item in str(value).replace("；", ";").split(";")
        if item.strip()
    ]

    return [
        tag
        for tag in tags
        if tag != "信息不足"
    ]


# ============================================================
# 5. 标签映射表
# ============================================================

HERITAGE_OBJECT_MAPPING = {
    "建筑遗产": "Architectural heritage",
    "工业遗产": "Industrial heritage",
    "文化景观与线性遗产": "Cultural landscapes and linear heritage",
    "综合": "Integrated",
    "乡村与农业遗产": "Rural and agricultural heritage",
    "自然遗产": "Natural heritage",
    "非物质与活态遗产": "Intangible and living heritage",
    "考古遗产": "Archaeological heritage",
}

RESEARCH_ORIENTATION_MAPPING = {
    "治理参与": "Governance and participation",
    "价值识别": "Value identification",
    "活化再生": "Revitalization and regeneration",
    "保护监测": "Conservation and monitoring",
    "数字记录": "Digital documentation",
    "综合": "Integrated",
    "风险韧性": "Risk and resilience",
}

METHOD_ORIENTATION_MAPPING = {
    "混合方法": "Mixed methods",
    "模型评价": "Model-based evaluation",
    "空间分析": "Spatial analysis",
    "历史档案": "Historical archives",
    "数字建模": "Digital modeling",
    "社会调查": "Social survey",
    "实验检测": "Experimental testing",
    "智能计算": "Intelligent computing",
}

HERITAGE_TAG_MAPPING = {
    "历史建筑": "Historic buildings",
    "文化景观": "Cultural landscape",
    "历史街区": "Historic districts",
    "传统村落": "Traditional villages",
    "工业设施": "Industrial facilities",
    "线性廊道": "Linear corridors",
    "非遗实践": "Intangible heritage practices",
    "风景名胜区": "Scenic and historic areas",
    "工业城市遗存": "Industrial urban remains",
    "自然与双重遗产": "Natural and mixed heritage",
    "考古遗址": "Archaeological sites",
    "传统知识": "Traditional knowledge",
    "农业文化遗产": "Agricultural heritage systems",
    "石窟土遗址": "Grotto and earthen sites",
}

RESEARCH_TAG_MAPPING = {
    "保护修复": "Conservation and restoration",
    "价值评价": "Value assessment",
    "活化利用": "Revitalization and use",
    "理论阐释": "Theoretical interpretation",
    "社区治理": "Community governance",
    "公众感知": "Public perception",
    "文旅融合": "Culture-tourism integration",
    "信息平台": "Information platform",
    "区域保护": "Regional conservation",
    "数字采集": "Digital acquisition",
    "风险评价": "Risk assessment",
    "工业更新": "Industrial regeneration",
    "病害监测": "Deterioration monitoring",
    "生态安全": "Ecological security",
    "预警机制": "Early warning mechanism",
    "智能识别": "Intelligent identification",
}

METHOD_TAG_MAPPING = {
    "文献档案": "Literature and archives",
    "指标评价": "Indicator evaluation",
    "空间形态": "Spatial morphology",
    "问卷访谈": "Questionnaires and interviews",
    "遥感分析": "Remote sensing analysis",
    "情景模拟": "Scenario simulation",
    "三维建模": "Three-dimensional modeling",
    "历史图像": "Historical imagery",
    "结构环境检测": "Structural-environmental testing",
    "点云测绘": "Point-cloud surveying",
    "材料检测": "Material testing",
    "机器学习": "Machine learning",
    "参与式调查": "Participatory survey",
    "知识图谱": "Knowledge graph",
}


# ============================================================
# 6. 三张图的配置
# ============================================================

FIGURE_CONFIGS = [
    {
        "panel": "a",
        "dimension_key": "heritage_object",
        "dimension_title": "Heritage objects",
        "category_col": "heritage_objects",
        "tag_col": "heritage_object_tags",
        "category_map": HERITAGE_OBJECT_MAPPING,
        "tag_map": HERITAGE_TAG_MAPPING,
        "base_color": DIMENSION_COLORS["heritage_object"],
        "stem": "figure3c_heritage_object_keyword_clusters_EN_optimized_final",
        "max_keywords_per_cluster": 10,
    },
    {
        "panel": "b",
        "dimension_key": "research_orientation",
        "dimension_title": "Research orientations",
        "category_col": "research_orientations",
        "tag_col": "research_theme_tags",
        "category_map": RESEARCH_ORIENTATION_MAPPING,
        "tag_map": RESEARCH_TAG_MAPPING,
        "base_color": DIMENSION_COLORS["research_orientation"],
        "stem": "figure3c_research_orientation_keyword_clusters_EN_optimized_final",
        "max_keywords_per_cluster": 11,
    },
    {
        "panel": "c",
        "dimension_key": "method_orientation",
        "dimension_title": "Methodological orientations",
        "category_col": "primary_method_orientation",
        "tag_col": "method_tags",
        "category_map": METHOD_ORIENTATION_MAPPING,
        "tag_map": METHOD_TAG_MAPPING,
        "base_color": DIMENSION_COLORS["method_orientation"],
        "stem": "figure3c_method_keyword_clusters_EN_optimized_final",
        "max_keywords_per_cluster": 10,
        "keyword_labels_per_cluster_override": 4,
        "deduplicate_keyword_labels_across_clusters": True,
    },
]


# ============================================================
# 7. 数据构造函数
# ============================================================

def prepare_cluster_data(
    df: pd.DataFrame,
    category_col: str,
    tag_col: str,
    category_map: dict[str, str],
    tag_map: dict[str, str],
    max_keywords_per_cluster: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    """
    为某一编码维度构造聚类图所需的节点表和边表。

    返回：
        node_df:
            二级指标节点和关键词节点。

        edge_df:
            二级指标—关键词边。

        keyword_edge_df:
            同一二级指标内部的关键词—关键词共现边。

        category_order:
            二级指标排序。
    """

    category_counts = (
        df[category_col]
        .dropna()
        .astype(str)
        .str.strip()
        .value_counts()
    )

    category_order = [
        cat
        for cat in category_counts.index
        if cat in category_map
    ]

    category_tag_counter: Counter[tuple[str, str]] = Counter()
    keyword_pair_counter: Counter[tuple[str, str, str]] = Counter()

    for _, row in df.iterrows():
        category = str(row.get(category_col, "")).strip()

        if category not in category_map:
            continue

        tags = [
            tag
            for tag in split_tags(row.get(tag_col))
            if tag in tag_map
        ]

        tags = sorted(set(tags))

        for tag in tags:
            category_tag_counter[(category, tag)] += 1

        for tag_a, tag_b in combinations(tags, 2):
            keyword_pair_counter[(category, tag_a, tag_b)] += 1

    edge_rows = []
    selected_tags_by_category: dict[str, set[str]] = {}

    for category in category_order:
        category_tags = [
            (tag, count)
            for (cat, tag), count in category_tag_counter.items()
            if cat == category
        ]

        category_tags = sorted(
            category_tags,
            key=lambda x: (-x[1], tag_map[x[0]])
        )

        selected = category_tags[:max_keywords_per_cluster]

        selected_tags_by_category[category] = {
            tag
            for tag, _ in selected
        }

        for tag, count in selected:
            edge_rows.append(
                {
                    "category_cn": category,
                    "category_en": category_map[category],
                    "keyword_cn": tag,
                    "keyword_en": tag_map[tag],
                    "count": int(count),
                    "category_total": int(category_counts[category]),
                    "share_within_category": count / category_counts[category],
                }
            )

    keyword_edges = []

    for (category, tag_a, tag_b), count in keyword_pair_counter.items():
        if category not in selected_tags_by_category:
            continue

        if tag_a not in selected_tags_by_category[category]:
            continue

        if tag_b not in selected_tags_by_category[category]:
            continue

        if count < 2:
            continue

        keyword_edges.append(
            {
                "category_cn": category,
                "category_en": category_map[category],
                "keyword_a_cn": tag_a,
                "keyword_a_en": tag_map[tag_a],
                "keyword_b_cn": tag_b,
                "keyword_b_en": tag_map[tag_b],
                "count": int(count),
            }
        )

    category_nodes = [
        {
            "node_type": "category",
            "category_cn": category,
            "category_en": category_map[category],
            "keyword_cn": "",
            "keyword_en": "",
            "count": int(category_counts[category]),
        }
        for category in category_order
    ]

    keyword_nodes = [
        {
            "node_type": "keyword",
            "category_cn": row["category_cn"],
            "category_en": row["category_en"],
            "keyword_cn": row["keyword_cn"],
            "keyword_en": row["keyword_en"],
            "count": int(row["count"]),
        }
        for row in edge_rows
    ]

    node_df = pd.DataFrame(category_nodes + keyword_nodes)
    edge_df = pd.DataFrame(edge_rows)
    keyword_edge_df = pd.DataFrame(keyword_edges)

    return node_df, edge_df, keyword_edge_df, category_order


# ============================================================
# 8. 布局函数
# ============================================================

def cluster_centres(n_clusters: int) -> dict[int, tuple[float, float]]:
    """
    生成紧凑型簇中心布局。

    注意：
        cluster_layout_scale 必须为正数。
        这个参数需要配合 use_fixed_axis_limits=True 才能明显生效。
    """

    scale = PLOT_CONFIG["cluster_layout_scale"]
    x_scale = PLOT_CONFIG["cluster_x_scale"]
    y_scale = PLOT_CONFIG["cluster_y_scale"]

    if scale <= 0:
        raise ValueError(
            "PLOT_CONFIG['cluster_layout_scale'] 必须为正数。"
            "例如可设为 0.66、0.72、0.80 或 0.88，不能设为负数。"
        )

    if n_clusters == 7:
        coords = [
            (0.00, 0.00),
            (1.05, 0.52),
            (1.05, -0.52),
            (0.00, -0.96),
            (-1.05, -0.52),
            (-1.05, 0.52),
            (0.00, 0.96),
        ]

    elif n_clusters == 8:
        coords = [
            (0.00, 0.00),
            (1.02, 0.52),
            (1.02, -0.52),
            (0.00, -0.98),
            (-1.02, -0.52),
            (-1.02, 0.52),
            (0.00, 0.98),
            (1.38, 0.00),
        ]

    else:
        coords = []

        for i in range(n_clusters):
            angle = 2 * math.pi * i / n_clusters
            coords.append(
                (
                    1.05 * math.cos(angle),
                    0.86 * math.sin(angle),
                )
            )

    coords = [
        (
            x * scale * x_scale,
            y * scale * y_scale,
        )
        for x, y in coords
    ]

    return {
        i: coords[i]
        for i in range(n_clusters)
    }


def build_graph(
    node_df: pd.DataFrame,
    edge_df: pd.DataFrame,
    keyword_edge_df: pd.DataFrame,
    category_order: list[str],
    category_map: dict[str, str],
) -> tuple[nx.Graph, dict[str, tuple[float, float]], dict[str, str], dict[str, int]]:
    """
    构造 NetworkX 图对象和节点坐标。

    图中节点：
        C::二级指标
            二级指标中心节点。

        K::二级指标::关键词
            关键词节点。

    图中边：
        category_keyword
            二级指标—关键词关系。

        keyword_keyword
            同一二级指标内关键词共现关系。
    """

    G = nx.Graph()
    node_cluster = {}
    node_count = {}

    centres = cluster_centres(len(category_order))
    pos = {}

    # 添加二级指标中心节点。
    for i, category in enumerate(category_order):
        cat_node = f"C::{category}"

        G.add_node(
            cat_node,
            label=category_map[category],
            node_type="category"
        )

        node_cluster[cat_node] = category

        node_count[cat_node] = int(
            node_df.loc[
                (node_df["node_type"] == "category")
                & (node_df["category_cn"] == category),
                "count"
            ].iloc[0]
        )

        pos[cat_node] = centres[i]

    # 添加关键词节点。
    for category in category_order:
        cx, cy = centres[category_order.index(category)]

        sub = (
            edge_df.loc[edge_df["category_cn"] == category]
            .sort_values(["count", "keyword_en"], ascending=[False, True])
            .reset_index(drop=True)
        )

        n_keywords = max(1, len(sub))

        angle_offset = (
            int(hashlib.md5(category.encode("utf-8")).hexdigest()[:6], 16)
            / 0xFFFFFF
            * 2
            * math.pi
        )

        for j, row in sub.iterrows():
            keyword = row["keyword_cn"]

            cat_node = f"C::{category}"
            kw_node = f"K::{category}::{keyword}"

            G.add_node(
                kw_node,
                label=row["keyword_en"],
                node_type="keyword"
            )

            G.add_edge(
                cat_node,
                kw_node,
                weight=float(row["count"]),
                edge_type="category_keyword"
            )

            node_cluster[kw_node] = category
            node_count[kw_node] = int(row["count"])

            angle = angle_offset + 2 * math.pi * j / n_keywords

            ring = (
                PLOT_CONFIG["keyword_ring_base"]
                + PLOT_CONFIG["keyword_ring_step"]
                * (j % PLOT_CONFIG["keyword_ring_cycle"])
            )

            jx, jy = stable_jitter(
                f"{category}-{keyword}",
                scale=PLOT_CONFIG["keyword_jitter_scale"]
            )

            pos[kw_node] = (
                cx + math.cos(angle) * ring + jx,
                cy + math.sin(angle) * ring * PLOT_CONFIG["keyword_ring_y_scale"] + jy,
            )

    # 添加关键词—关键词共现边。
    if not keyword_edge_df.empty:
        for _, row in keyword_edge_df.iterrows():
            category = row["category_cn"]

            a = f"K::{category}::{row['keyword_a_cn']}"
            b = f"K::{category}::{row['keyword_b_cn']}"

            if a in G and b in G:
                G.add_edge(
                    a,
                    b,
                    weight=float(row["count"]),
                    edge_type="keyword_keyword"
                )

    return G, pos, node_cluster, node_count


# ============================================================
# 9. 绘图函数
# ============================================================

def draw_cluster_backgrounds(
    ax,
    G: nx.Graph,
    pos: dict[str, tuple[float, float]],
    node_cluster: dict[str, str],
    category_order: list[str],
    category_color: dict[str, str],
) -> None:
    """
    绘制每个簇的半透明背景圆 / 椭圆。

    本版特点：
        1. 每个簇的背景圆更大；
        2. 小簇也有稳定的最小背景圆；
        3. 可强制背景近似圆形。
    """

    if not PLOT_CONFIG["show_cluster_background"]:
        return

    for category in category_order:
        cat_node = f"C::{category}"

        nodes = [
            node
            for node in G.nodes
            if node_cluster[node] == category
        ]

        pts = np.array([
            pos[node]
            for node in nodes
        ])

        cx, cy = pos[cat_node]

        width = max(
            PLOT_CONFIG["cluster_ellipse_min_width"],
            2
            * np.abs(pts[:, 0] - cx).max()
            * PLOT_CONFIG["cluster_ellipse_width_scale"]
        )

        height = max(
            PLOT_CONFIG["cluster_ellipse_min_height"],
            2
            * np.abs(pts[:, 1] - cy).max()
            * PLOT_CONFIG["cluster_ellipse_height_scale"]
        )

        if PLOT_CONFIG["force_round_cluster_background"]:
            diameter = max(width, height)
            width = diameter
            height = diameter

        ellipse = Ellipse(
            (cx, cy),
            width=width,
            height=height,
            angle=0,
            facecolor=category_color[category],
            edgecolor="none",
            alpha=PLOT_CONFIG["cluster_ellipse_alpha"],
            zorder=0,
        )

        ax.add_patch(ellipse)


def draw_edges(
    ax,
    G: nx.Graph,
    pos: dict[str, tuple[float, float]],
    node_cluster: dict[str, str],
    category_color: dict[str, str],
) -> None:
    """
    绘制两类边：
        1. 关键词—关键词共现边；
        2. 二级指标—关键词边。
    """

    # 关键词—关键词共现边。
    for u, v, data in G.edges(data=True):
        if data.get("edge_type") != "keyword_keyword":
            continue

        x0, y0 = pos[u]
        x1, y1 = pos[v]

        weight = min(
            data["weight"],
            PLOT_CONFIG["keyword_keyword_edge_weight_cap"]
        )

        ax.plot(
            [x0, x1],
            [y0, y1],
            color=PLOT_CONFIG["keyword_keyword_edge_color"],
            lw=(
                PLOT_CONFIG["keyword_keyword_edge_width_base"]
                + PLOT_CONFIG["keyword_keyword_edge_width_scale"] * weight
            ),
            alpha=PLOT_CONFIG["keyword_keyword_edge_alpha"],
            zorder=1,
        )

    # 二级指标—关键词边。
    for u, v, data in G.edges(data=True):
        if data.get("edge_type") != "category_keyword":
            continue

        category = (
            node_cluster[u]
            if G.nodes[u]["node_type"] == "category"
            else node_cluster[v]
        )

        x0, y0 = pos[u]
        x1, y1 = pos[v]

        weight = min(
            data["weight"],
            PLOT_CONFIG["category_keyword_edge_weight_cap"]
        )

        ax.plot(
            [x0, x1],
            [y0, y1],
            color=category_color[category],
            lw=(
                PLOT_CONFIG["category_keyword_edge_width_base"]
                + PLOT_CONFIG["category_keyword_edge_width_scale"] * weight
            ),
            alpha=PLOT_CONFIG["category_keyword_edge_alpha"],
            zorder=2,
        )


def draw_nodes(
    ax,
    G: nx.Graph,
    pos: dict[str, tuple[float, float]],
    node_cluster: dict[str, str],
    node_count: dict[str, int],
    category_order: list[str],
    category_color: dict[str, str],
) -> None:
    """
    绘制关键词节点和二级指标中心节点。
    """

    # 关键词节点。
    for category in category_order:
        kw_nodes = [
            node
            for node in G.nodes
            if node_cluster[node] == category
            and G.nodes[node]["node_type"] == "keyword"
        ]

        sizes = [
            min(
                PLOT_CONFIG["keyword_node_size_base"]
                + node_count[node] * PLOT_CONFIG["keyword_node_size_scale"],
                PLOT_CONFIG["keyword_node_size_max"]
            )
            for node in kw_nodes
        ]

        ax.scatter(
            [pos[node][0] for node in kw_nodes],
            [pos[node][1] for node in kw_nodes],
            s=sizes,
            color=category_color[category],
            edgecolor=PLOT_CONFIG["node_edgecolor"],
            linewidth=PLOT_CONFIG["keyword_node_linewidth"],
            alpha=PLOT_CONFIG["keyword_node_alpha"],
            zorder=4,
        )

    # 二级指标中心节点。
    for i, category in enumerate(category_order):
        cat_node = f"C::{category}"

        size = min(
            PLOT_CONFIG["category_node_size_base"]
            + node_count[cat_node] * PLOT_CONFIG["category_node_size_scale"],
            PLOT_CONFIG["category_node_size_max"]
        )

        ax.scatter(
            [pos[cat_node][0]],
            [pos[cat_node][1]],
            s=size,
            color=category_color[category],
            edgecolor=PLOT_CONFIG["node_edgecolor"],
            linewidth=PLOT_CONFIG["category_node_linewidth"],
            alpha=PLOT_CONFIG["category_node_alpha"],
            zorder=5,
        )

        if PLOT_CONFIG["show_center_node_labels"]:
            ax.text(
                pos[cat_node][0],
                pos[cat_node][1],
                center_label_text(
                    i,
                    G.nodes[cat_node]["label"]
                ),
                ha="center",
                va="center",
                fontsize=PLOT_CONFIG["center_node_label_fontsize"],
                color=PLOT_CONFIG["center_node_label_color"],
                fontweight=PLOT_CONFIG["center_node_label_fontweight"],
                linespacing=0.88,
                zorder=9,
            )


def draw_cluster_labels(
    ax,
    G: nx.Graph,
    pos: dict[str, tuple[float, float]],
    category_order: list[str],
    category_map: dict[str, str],
    category_color: dict[str, str],
) -> None:
    """
    绘制每个簇的二级指标标签。
    """

    if not PLOT_CONFIG["show_cluster_labels"]:
        return

    if PLOT_CONFIG["cluster_label_bbox"]:
        bbox = {
            "boxstyle": f"round,pad={PLOT_CONFIG['cluster_label_bbox_pad']}",
            "facecolor": PLOT_CONFIG["cluster_label_bbox_facecolor"],
            "edgecolor": PLOT_CONFIG["cluster_label_bbox_edgecolor"],
            "alpha": PLOT_CONFIG["cluster_label_bbox_alpha"],
        }
    else:
        bbox = None

    for i, category in enumerate(category_order):
        cat_node = f"C::{category}"
        x, y = pos[cat_node]

        if PLOT_CONFIG["show_cluster_index"]:
            label = f"#{i} {category_map[category]}"
        else:
            label = category_map[category]

        ax.text(
            x,
            y + PLOT_CONFIG["cluster_label_y_offset"],
            wrap_label(
                label,
                PLOT_CONFIG["cluster_label_wrap_width"]
            ),
            color=category_color[category],
            fontsize=PLOT_CONFIG["cluster_label_fontsize"],
            fontweight=PLOT_CONFIG["cluster_label_fontweight"],
            ha="center",
            va="bottom",
            bbox=bbox,
            zorder=8,
        )


def keyword_nodes_for_category(
    G: nx.Graph,
    node_cluster: dict[str, str],
    node_count: dict[str, int],
    category: str,
) -> list[str]:
    """
    Return keyword nodes in one cluster, sorted by within-cluster frequency.
    """

    nodes = [
        node
        for node in G.nodes
        if node_cluster[node] == category
        and G.nodes[node]["node_type"] == "keyword"
    ]

    return sorted(
        nodes,
        key=lambda node: (
            -node_count[node],
            str(G.nodes[node]["label"]),
        ),
    )


def select_keyword_label_nodes(
    G: nx.Graph,
    node_cluster: dict[str, str],
    node_count: dict[str, int],
    category_order: list[str],
    labels_per_cluster: int,
    deduplicate_across_clusters: bool,
) -> dict[str, list[str]]:
    """
    Select keyword labels for each cluster.

    Methodological tags often co-occur across several method clusters.  When
    deduplication is enabled, repeated labels are assigned to the cluster where
    they are most specific, measured by their share of the cluster's total hits;
    remaining slots are then filled by the strongest unused labels.
    """

    candidates_by_category = {
        category: keyword_nodes_for_category(
            G,
            node_cluster,
            node_count,
            category,
        )
        for category in category_order
    }

    if not deduplicate_across_clusters:
        return {
            category: candidates[:labels_per_cluster]
            for category, candidates in candidates_by_category.items()
        }

    category_totals = {
        category: max(1, node_count.get(f"C::{category}", 1))
        for category in category_order
    }

    label_records: dict[str, list[tuple[float, int, str, str]]] = {}
    for category, candidates in candidates_by_category.items():
        for node in candidates:
            label = str(G.nodes[node]["label"])
            share = node_count[node] / category_totals[category]
            label_records.setdefault(label, []).append(
                (
                    share,
                    node_count[node],
                    category,
                    node,
                )
            )

    label_owner: dict[str, str] = {}
    for label, records in label_records.items():
        records = sorted(
            records,
            key=lambda item: (
                -item[0],
                -item[1],
                str(item[2]),
            ),
        )
        label_owner[label] = records[0][2]

    selected: dict[str, list[str]] = {category: [] for category in category_order}
    used_labels: set[str] = set()

    # First pass: cluster-specific labels, judged by within-cluster share.
    for category in category_order:
        for node in candidates_by_category[category]:
            label = str(G.nodes[node]["label"])
            if label_owner.get(label) != category or label in used_labels:
                continue

            selected[category].append(node)
            used_labels.add(label)

            if len(selected[category]) >= labels_per_cluster:
                break

    # Second pass: strongest remaining labels that have not appeared elsewhere.
    for category in category_order:
        if len(selected[category]) >= labels_per_cluster:
            continue

        for node in candidates_by_category[category]:
            label = str(G.nodes[node]["label"])
            if node in selected[category] or label in used_labels:
                continue

            selected[category].append(node)
            used_labels.add(label)

            if len(selected[category]) >= labels_per_cluster:
                break

    return selected


def draw_keyword_labels(
    ax,
    G: nx.Graph,
    pos: dict[str, tuple[float, float]],
    node_cluster: dict[str, str],
    node_count: dict[str, int],
    category_order: list[str],
    category_color: dict[str, str],
    labels_per_cluster: int | None = None,
    deduplicate_across_clusters: bool = False,
) -> None:
    """
    绘制每个簇内最重要的关键词标签。
    """

    if not PLOT_CONFIG["show_keyword_labels"]:
        return

    if PLOT_CONFIG["keyword_label_bbox"]:
        bbox = {
            "boxstyle": f"round,pad={PLOT_CONFIG['keyword_label_bbox_pad']}",
            "facecolor": PLOT_CONFIG["keyword_label_bbox_facecolor"],
            "edgecolor": PLOT_CONFIG["keyword_label_bbox_edgecolor"],
            "alpha": PLOT_CONFIG["keyword_label_bbox_alpha"],
        }
    else:
        bbox = None

    occupied_boxes: list[tuple[float, float, float, float]] = []

    def estimate_box(text: str, x: float, y: float) -> tuple[float, float, float, float]:
        lines = text.split("\n")
        line_width = max((len(line) for line in lines), default=1)
        width = max(0.16, min(0.46, line_width * 0.014))
        height = 0.042 * max(1, len(lines)) + 0.030
        return (
            x - width / 2,
            x + width / 2,
            y - height / 2,
            y + height / 2,
        )

    def overlaps(box: tuple[float, float, float, float]) -> bool:
        x0, x1, y0, y1 = box
        for ox0, ox1, oy0, oy1 in occupied_boxes:
            if x0 < ox1 and x1 > ox0 and y0 < oy1 and y1 > oy0:
                return True
        return False

    for i, category in enumerate(category_order):
        cat_node = f"C::{category}"
        cx, cy = pos[cat_node]
        label_box = estimate_box(
            center_label_text(
                i,
                G.nodes[cat_node]["label"]
            ),
            cx,
            cy,
        )

        x0, x1, y0, y1 = label_box
        occupied_boxes.append(
            (
                x0 - 0.05,
                x1 + 0.05,
                y0 - 0.04,
                y1 + 0.04,
            )
        )

    label_limit = (
        labels_per_cluster
        if labels_per_cluster is not None
        else PLOT_CONFIG["keyword_labels_per_cluster"]
    )
    selected_nodes_by_category = select_keyword_label_nodes(
        G=G,
        node_cluster=node_cluster,
        node_count=node_count,
        category_order=category_order,
        labels_per_cluster=label_limit,
        deduplicate_across_clusters=deduplicate_across_clusters,
    )

    for category in category_order:
        cat_node = f"C::{category}"
        cx, cy = pos[cat_node]
        label_color = readable_cluster_text_color(
            category_color[category]
        )

        for node in selected_nodes_by_category[category]:
            x, y = pos[node]
            dx = x - cx
            dy = y - cy
            distance = math.hypot(dx, dy)

            if distance < 1e-9:
                ux, uy = 0.0, 1.0
            else:
                ux, uy = dx / distance, dy / distance

            radial_offset = PLOT_CONFIG["keyword_label_radial_offset"]
            base_x = x + ux * radial_offset
            base_y = y + uy * radial_offset

            label = wrap_label(
                G.nodes[node]["label"],
                PLOT_CONFIG["keyword_label_wrap_width"]
            )

            px, py = -uy, ux
            label_x, label_y = base_x, base_y

            for attempt in range(12):
                step = (attempt + 1) // 2
                direction = -1 if attempt % 2 == 0 else 1
                shift = direction * step * PLOT_CONFIG["keyword_label_min_y_gap"]
                trial_x = base_x + px * shift
                trial_y = base_y + py * shift
                trial_box = estimate_box(label, trial_x, trial_y)

                if not overlaps(trial_box):
                    label_x, label_y = trial_x, trial_y
                    occupied_boxes.append(trial_box)
                    break
            else:
                occupied_boxes.append(
                    estimate_box(label, label_x, label_y)
                )

            ha = "left" if ux > 0.18 else "right" if ux < -0.18 else "center"

            ax.text(
                label_x,
                label_y,
                label,
                ha=ha,
                va="center",
                fontsize=PLOT_CONFIG["keyword_label_fontsize"],
                color=label_color,
                fontweight=(
                    "bold"
                    if node_count[node] >= PLOT_CONFIG["keyword_label_fontweight_threshold"]
                    else "normal"
                ),
                bbox=bbox,
                zorder=7,
            )


def draw_cluster_map(
    df: pd.DataFrame,
    config: dict,
) -> list[dict]:
    """
    绘制某一个维度的关键词聚类图。
    """

    node_df, edge_df, keyword_edge_df, category_order = prepare_cluster_data(
        df=df,
        category_col=config["category_col"],
        tag_col=config["tag_col"],
        category_map=config["category_map"],
        tag_map=config["tag_map"],
        max_keywords_per_cluster=config["max_keywords_per_cluster"],
    )

    stem = config["stem"]

    # 输出源数据。
    node_df.to_csv(
        SRC_DIR / f"{stem}_nodes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    edge_df.to_csv(
        SRC_DIR / f"{stem}_category_keyword_edges.csv",
        index=False,
        encoding="utf-8-sig"
    )

    keyword_edge_df.to_csv(
        SRC_DIR / f"{stem}_keyword_cooccurrence_edges.csv",
        index=False,
        encoding="utf-8-sig"
    )

    G, pos, node_cluster, node_count = build_graph(
        node_df=node_df,
        edge_df=edge_df,
        keyword_edge_df=keyword_edge_df,
        category_order=category_order,
        category_map=config["category_map"],
    )

    category_color = {
        category: CLUSTER_PALETTE[i % len(CLUSTER_PALETTE)]
        for i, category in enumerate(category_order)
    }

    fig, ax = plt.subplots(
        figsize=(
            PLOT_CONFIG["figure_width"],
            PLOT_CONFIG["figure_height"]
        ),
        dpi=PLOT_CONFIG["figure_dpi"],
    )

    ax.set_facecolor(PLOT_CONFIG["background"])
    ax.axis("off")

    draw_cluster_backgrounds(
        ax,
        G,
        pos,
        node_cluster,
        category_order,
        category_color,
    )

    draw_edges(
        ax,
        G,
        pos,
        node_cluster,
        category_color,
    )

    draw_nodes(
        ax,
        G,
        pos,
        node_cluster,
        node_count,
        category_order,
        category_color,
    )

    draw_cluster_labels(
        ax,
        G,
        pos,
        category_order,
        config["category_map"],
        category_color,
    )

    draw_keyword_labels(
        ax,
        G,
        pos,
        node_cluster,
        node_count,
        category_order,
        category_color,
        labels_per_cluster=config.get("keyword_labels_per_cluster_override"),
        deduplicate_across_clusters=config.get(
            "deduplicate_keyword_labels_across_clusters",
            False,
        ),
    )

    # --------------------------------------------------------
    # 画布范围设置
    # --------------------------------------------------------

    xs = [
        xy[0]
        for xy in pos.values()
    ]

    ys = [
        xy[1]
        for xy in pos.values()
    ]

    if PLOT_CONFIG["use_fixed_axis_limits"]:
        # 固定坐标范围。
        # 这样 cluster_layout_scale / cluster_x_scale / cluster_y_scale 的改动
        # 才会在视觉上真实生效。
        ax.set_xlim(*PLOT_CONFIG["fixed_xlim"])
        ax.set_ylim(*PLOT_CONFIG["fixed_ylim"])

    else:
        # 自动坐标范围。
        # 注意：自动范围会抵消整体缩放参数的视觉效果。
        pad_x = PLOT_CONFIG["pad_x"]
        pad_y = PLOT_CONFIG["pad_y"]

        ax.set_xlim(
            min(xs) - pad_x,
            max(xs) + pad_x
        )

        ax.set_ylim(
            min(ys) - pad_y,
            max(ys) + pad_y
        )

    ax.set_aspect(
        "equal",
        adjustable="box"
    )

    # 子图编号。
    if PLOT_CONFIG["show_panel_label"]:
        if PLOT_CONFIG["use_fixed_axis_limits"]:
            panel_x = PLOT_CONFIG["fixed_xlim"][0] + 0.05
            panel_y = PLOT_CONFIG["fixed_ylim"][1] - 0.05
        else:
            panel_x = min(xs) - PLOT_CONFIG["pad_x"] * 0.78
            panel_y = max(ys) + PLOT_CONFIG["pad_y"] * 0.60

        ax.text(
            panel_x,
            panel_y,
            f"{config['panel']})",
            fontsize=PLOT_CONFIG["panel_label_fontsize"],
            fontweight=PLOT_CONFIG["panel_label_fontweight"],
            ha="left",
            va="top",
            color="#111111",
        )

    # 维度标题。
    if PLOT_CONFIG["show_dimension_title"]:
        ax.text(
            0.5,
            PLOT_CONFIG["dimension_title_y"],
            config["dimension_title"],
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=PLOT_CONFIG["dimension_title_fontsize"],
            fontweight=PLOT_CONFIG["dimension_title_fontweight"],
            color=config["base_color"],
        )

    # 保存图件。
    if PLOT_CONFIG["save_svg"]:
        fig.savefig(
            FIG_DIR / f"{stem}.svg",
            bbox_inches="tight"
        )

    if PLOT_CONFIG["save_pdf"]:
        fig.savefig(
            FIG_DIR / f"{stem}.pdf",
            bbox_inches="tight"
        )

    if PLOT_CONFIG["save_png"]:
        fig.savefig(
            FIG_DIR / f"{stem}.png",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight"
        )

    if PLOT_CONFIG["save_tiff"]:
        fig.savefig(
            FIG_DIR / f"{stem}.tiff",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight"
        )

    if PLOT_CONFIG["show_plot"]:
        plt.show()
    else:
        plt.close(fig)

    manifest_rows = [
        {
            "figure": stem,
            "file_type": "figure",
            "path": f"{stem}.svg",
            "description": "Editable vector figure",
        },
        {
            "figure": stem,
            "file_type": "source_data",
            "path": f"source_data/{stem}_nodes.csv",
            "description": "Cluster and keyword nodes",
        },
        {
            "figure": stem,
            "file_type": "source_data",
            "path": f"source_data/{stem}_category_keyword_edges.csv",
            "description": "Indicator-keyword project-level edges",
        },
        {
            "figure": stem,
            "file_type": "source_data",
            "path": f"source_data/{stem}_keyword_cooccurrence_edges.csv",
            "description": "Within-indicator keyword co-occurrence edges",
        },
    ]

    return manifest_rows


# ============================================================
# 10. 主程序
# ============================================================

def main() -> None:
    """
    主程序入口。
    """

    require_arial_font(
        PLOT_CONFIG["font_family"],
        strict=PLOT_CONFIG["strict_font"],
    )

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Input data file not found: {DATA_FILE}"
        )

    df = pd.read_csv(
        DATA_FILE,
        encoding="utf-8-sig"
    )

    # 如果存在 scope 字段，则仅保留 in_scope 项目。
    if "scope" in df.columns:
        df = df[
            df["scope"]
            .astype(str)
            .str.strip()
            .eq("in_scope")
        ].copy()

    manifest = []

    for config in FIGURE_CONFIGS:
        manifest.extend(
            draw_cluster_map(
                df,
                config
            )
        )

    pd.DataFrame(manifest).to_csv(
        OUT_DIR / "figure3c_keyword_cluster_manifest_optimized_final.csv",
        index=False,
        encoding="utf-8-sig",
    )

    caption = (
        "Figure X. Keyword-cluster maps for the three coding dimensions of NSFC "
        "heritage research. Each cluster represents a second-level indicator, and "
        "small nodes represent LLM-extracted hit keywords. Node size denotes the "
        "number of projects in which the indicator or keyword appears; edges denote "
        "project-level associations between indicators and hit keywords, with faint "
        "within-cluster edges marking keyword co-occurrence."
    )

    (
        OUT_DIR / "figure3c_keyword_cluster_caption_EN_optimized_final.txt"
    ).write_text(
        caption,
        encoding="utf-8"
    )

    # 输出关键参数，便于确认当前运行的是新参数。
    print("Current key plot parameters:")
    print(f"  cluster_layout_scale = {PLOT_CONFIG['cluster_layout_scale']}")
    print(f"  use_fixed_axis_limits = {PLOT_CONFIG['use_fixed_axis_limits']}")
    print(f"  fixed_xlim = {PLOT_CONFIG['fixed_xlim']}")
    print(f"  fixed_ylim = {PLOT_CONFIG['fixed_ylim']}")
    print(f"  cluster_ellipse_min_width = {PLOT_CONFIG['cluster_ellipse_min_width']}")
    print(f"  cluster_ellipse_min_height = {PLOT_CONFIG['cluster_ellipse_min_height']}")
    print(f"  keyword_labels_per_cluster = {PLOT_CONFIG['keyword_labels_per_cluster']}")

    print(f"Saved optimized figures directly to: {FIG_DIR}")
    print(f"Saved source data to: {SRC_DIR}")
    print(f"Saved manifest and caption to: {OUT_DIR}")


if __name__ == "__main__":
    main()
