# -*- coding: utf-8 -*-
"""
Figure 8. Project-level co-occurrence network of LLM-coded research turns.

Purpose
-------
This script revises the former "reshaping agendas" network so that all labels
and layers are consistent with the coding framework used in the manuscript:

    1. Heritage objects                  -> heritage_objects
    2. LLM-coded research turns           -> turn_type
    3. Methodological orientations        -> primary_method_orientation
    4. Knowledge functions                -> primary_knowledge_function
    5. Application contexts               -> derived from project-level tags

The central column now includes all research-turn categories in the coding
manual, rather than only four simplified reshaping agendas. Edge width reports
project-level co-occurrence counts, and edge colour reports source-normalized
co-occurrence strength on a 0-1 scale.

Outputs
-------
    - figure8_research_turn_project_cooccurrence_network_EN.[png/pdf/svg/tiff]
    - figure8_reshaping_agenda_project_cooccurrence_network_EN.[png/pdf/svg/tiff]
      (kept as a compatibility filename for the existing manuscript folder)
    - source-data CSV files for nodes, edges, node layout and context rules
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import math
import re
import textwrap

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgba
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch


# =============================================================================
# 1. Paths
# =============================================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "inputs" / "heritage_llm_coding_results.csv"
OUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "reproduced"
FIG_DIR = OUT_DIR / "figures"
SRC_DIR = OUT_DIR / "source_data"

for folder in (FIG_DIR, SRC_DIR):
    folder.mkdir(parents=True, exist_ok=True)

FIGURE_STEM = "figure8_research_turn_project_cooccurrence_network_EN"
COMPAT_STEM = "figure8_reshaping_agenda_project_cooccurrence_network_EN"


# =============================================================================
# 2. Labels and visual encoding
# =============================================================================

OBJECT_ORDER = [
    "建筑遗产",
    "工业遗产",
    "文化景观与线性遗产",
    "综合",
    "乡村与农业遗产",
    "自然遗产",
    "非物质与活态遗产",
    "考古遗产",
]

OBJECT_EN = {
    "建筑遗产": "Architectural heritage",
    "工业遗产": "Industrial heritage",
    "文化景观与线性遗产": "Cultural landscapes\nand linear heritage",
    "综合": "Integrated",
    "乡村与农业遗产": "Rural and agricultural\nheritage",
    "自然遗产": "Natural heritage",
    "非物质与活态遗产": "Intangible and living\nheritage",
    "考古遗产": "Archaeological\nheritage",
}

TURN_ORDER = [
    "本体保护转向",
    "数字计算转向",
    "空间活化转向",
    "社会文化转向",
    "风险韧性转向",
    "混合转向",
    "传统延续",
]

TURN_EN = {
    "本体保护转向": "Object-conservation\nturn",
    "数字计算转向": "Digital-computational\nturn",
    "空间活化转向": "Spatial activation\nturn",
    "社会文化转向": "Socio-cultural\nturn",
    "风险韧性转向": "Risk-resilience\nturn",
    "混合转向": "Hybrid\nturn",
    "传统延续": "Traditional\ncontinuity",
}

METHOD_ORDER = [
    "混合方法",
    "模型评价",
    "空间分析",
    "历史档案",
    "数字建模",
    "社会调查",
    "实验检测",
    "智能计算",
]

METHOD_EN = {
    "混合方法": "Mixed methods",
    "模型评价": "Model-based evaluation",
    "空间分析": "Spatial analysis",
    "历史档案": "Historical archives",
    "数字建模": "Digital modeling",
    "社会调查": "Social survey",
    "实验检测": "Experimental testing",
    "智能计算": "Intelligent computing",
}

FUNCTION_ORDER = [
    "干预决策",
    "机制解释",
    "诊断评价",
    "意义阐释",
    "工具平台",
    "综合",
    "预测模拟",
    "记录描述",
]

FUNCTION_EN = {
    "干预决策": "Intervention and decision",
    "机制解释": "Mechanism explanation",
    "诊断评价": "Diagnosis and evaluation",
    "意义阐释": "Meaning interpretation",
    "工具平台": "Tools and platforms",
    "综合": "Integrated function",
    "预测模拟": "Prediction and simulation",
    "记录描述": "Recording and description",
}

APPLICATION_CONTEXT_ORDER = [
    "价值阐释",
    "保护干预",
    "数字平台",
    "空间治理",
    "社区参与",
    "文旅融合",
    "风险适应",
]

APPLICATION_CONTEXT_EN = {
    "价值阐释": "Value interpretation",
    "保护干预": "Conservation\nintervention",
    "数字平台": "Digital platforming",
    "空间治理": "Spatial governance",
    "社区参与": "Community\nparticipation",
    "文旅融合": "Culture-tourism\nintegration",
    "风险适应": "Risk adaptation",
}

CATEGORY_COLORS = {
    "object": "#89B2F4",
    "turn": "#018C94",
    "method": "#764D9C",
    "function": "#F2B95E",
    "application": "#DDE6EE",
}

TURN_COLORS = {
    "本体保护转向": "#3A4652",
    "数字计算转向": "#018C94",
    "空间活化转向": "#764D9C",
    "社会文化转向": "#59BFC4",
    "风险韧性转向": "#6F9FE8",
    "混合转向": "#8A8F93",
    "传统延续": "#B9C2CC",
}

FLOW_CMAP = LinearSegmentedColormap.from_list(
    "source_normalized_strength",
    ["#89B2F4", "#018C94", "#764D9C"],
)
FLOW_NORM = Normalize(vmin=0, vmax=1)


# =============================================================================
# 3. Figure configuration
# =============================================================================

PLOT_CONFIG = {
    # Canvas and export
    "fig_width": 13.6,
    "fig_height": 8.7,
    "figure_dpi": 300,
    "output_dpi": 600,
    "font_family": "Arial",
    "strict_arial": False,
    # Axis limits
    "xlim": (-2.18, 2.34),
    "ylim": (-1.10, 1.24),
    # Column x positions
    "object_x": -1.92,
    "turn_x": -0.62,
    "method_x": 0.56,
    "function_x": 0.58,
    "application_x": 1.86,
    # Vertical ranges for each column
    "object_y_top": 0.80,
    "object_y_bottom": -0.72,
    "turn_y_top": 0.82,
    "turn_y_bottom": -0.76,
    "method_y_top": 0.86,
    "method_y_bottom": 0.24,
    "function_y_top": 0.04,
    "function_y_bottom": -0.84,
    "application_y_top": 0.80,
    "application_y_bottom": -0.78,
    # Node sizing
    "object_marker_size": 120,
    "method_marker_base": 120,
    "function_marker_base": 120,
    "application_marker_base": 180,
    "turn_marker_min": 520,
    "turn_marker_max": 1650,
    # Edge styling
    "edge_min_weight": 1,
    "edge_alpha_min": 0.16,
    "edge_alpha_max": 0.58,
    "edge_width_min": 0.45,
    "edge_width_max": 4.0,
    "edge_curve": 0.34,
    # Text styling
    "title_fontsize": 12.6,
    "column_title_fontsize": 10.8,
    "label_fontsize": 7.8,
    "small_label_fontsize": 7.2,
    "turn_count_fontsize": 11.0,
    # Export switches
    "save_png": True,
    "save_pdf": True,
    "save_svg": True,
    "save_tiff": True,
}


# =============================================================================
# 4. Utilities
# =============================================================================

def setup_style() -> None:
    """Configure matplotlib for editable, publication-friendly vector output."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                PLOT_CONFIG["font_family"],
                "Helvetica",
                "DejaVu Sans",
                "Arial Unicode MS",
                "sans-serif",
            ],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def split_tags(value) -> set[str]:
    """Split semicolon/comma-separated Chinese tag fields into a clean set."""
    if pd.isna(value):
        return set()
    parts = re.split(r"[;；,，、]+", str(value))
    return {x.strip() for x in parts if x.strip()}


def wrap_label(text: str, width: int = 20) -> str:
    """Wrap long English labels without changing semantic wording."""
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False))


def normalize_strengths(edges: list[dict]) -> list[dict]:
    """Add source-normalized edge strength to every edge."""
    max_by_source: dict[str, int] = defaultdict(int)
    for edge in edges:
        max_by_source[edge["source"]] = max(max_by_source[edge["source"]], edge["weight"])
    for edge in edges:
        denom = max_by_source.get(edge["source"], 1) or 1
        edge["strength"] = edge["weight"] / denom
    return edges


def load_data() -> pd.DataFrame:
    """Read the full LLM-coded project table and keep in-scope projects."""
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
    df = df[df["scope"].eq("in_scope")].copy()
    return df


# =============================================================================
# 5. Derived application-context rules
# =============================================================================

APPLICATION_CONTEXT_RULES = {
    "价值阐释": {
        "agenda_turn_tags": {"意义阐释"},
        "research_theme_tags": {"价值评价", "理论阐释"},
        "method_tags": {"文献档案", "历史图像"},
        "stakeholder_tags": set(),
    },
    "保护干预": {
        "agenda_turn_tags": {"预防保护", "本体安全"},
        "research_theme_tags": {"保护修复", "病害监测"},
        "method_tags": {"材料检测", "结构环境检测"},
        "stakeholder_tags": {"保护技术人员"},
    },
    "数字平台": {
        "agenda_turn_tags": {"数字孪生", "智能识别"},
        "research_theme_tags": {"信息平台", "数字采集", "智能识别"},
        "method_tags": {"三维建模", "点云测绘", "机器学习", "知识图谱"},
        "stakeholder_tags": set(),
    },
    "空间治理": {
        "agenda_turn_tags": {"空间治理", "活化利用"},
        "research_theme_tags": {"区域保护", "工业更新", "活化利用"},
        "method_tags": {"空间形态", "遥感分析"},
        "stakeholder_tags": {"规划决策部门", "行政管理部门"},
    },
    "社区参与": {
        "agenda_turn_tags": {"公众参与"},
        "research_theme_tags": {"社区治理", "公众感知"},
        "method_tags": {"问卷访谈", "参与式调查"},
        "stakeholder_tags": {"社区居民", "公众消费者", "传承人"},
    },
    "文旅融合": {
        "agenda_turn_tags": {"活化利用"},
        "research_theme_tags": {"文旅融合"},
        "method_tags": set(),
        "stakeholder_tags": {"游客", "企业运营者", "产业部门"},
    },
    "风险适应": {
        "agenda_turn_tags": {"风险预警", "韧性适应"},
        "research_theme_tags": {"风险评价", "生态安全", "预警机制"},
        "method_tags": {"情景模拟"},
        "stakeholder_tags": set(),
    },
}


def derive_application_contexts(row: pd.Series) -> list[str]:
    """Derive application contexts from agenda/theme/method/stakeholder tags."""
    field_sets = {
        "agenda_turn_tags": split_tags(row.get("agenda_turn_tags")),
        "research_theme_tags": split_tags(row.get("research_theme_tags")),
        "method_tags": split_tags(row.get("method_tags")),
        "stakeholder_tags": split_tags(row.get("stakeholder_tags")),
    }
    contexts: list[str] = []
    for context in APPLICATION_CONTEXT_ORDER:
        rules = APPLICATION_CONTEXT_RULES[context]
        matched = any(field_sets[field] & tags for field, tags in rules.items())
        if matched:
            contexts.append(context)
    return contexts


# =============================================================================
# 6. Network source-data construction
# =============================================================================

def node_id(node_type: str, label_cn: str) -> str:
    return f"{node_type}::{label_cn}"


def build_nodes_and_edges(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build project-level nodes and directed co-occurrence edges."""
    node_counts: dict[str, Counter] = {
        "object": Counter(),
        "turn": Counter(),
        "method": Counter(),
        "function": Counter(),
        "application": Counter(),
    }
    edge_counts: Counter[tuple[str, str, str]] = Counter()
    project_rows: list[dict] = []

    for _, row in df.iterrows():
        project_id = row.get("approval_no")
        obj = str(row.get("heritage_objects", "")).strip()
        turn = str(row.get("turn_type", "")).strip()
        method = str(row.get("primary_method_orientation", "")).strip()
        function = str(row.get("primary_knowledge_function", "")).strip()
        contexts = derive_application_contexts(row)

        if not obj or not turn or not method or not function:
            continue

        node_counts["object"][obj] += 1
        node_counts["turn"][turn] += 1
        node_counts["method"][method] += 1
        node_counts["function"][function] += 1
        for context in contexts:
            node_counts["application"][context] += 1

        # Layered evidence flow:
        # object -> research turn -> method/function -> application contexts.
        edge_counts[(node_id("object", obj), node_id("turn", turn), "object_to_turn")] += 1
        edge_counts[(node_id("turn", turn), node_id("method", method), "turn_to_method")] += 1
        edge_counts[(node_id("turn", turn), node_id("function", function), "turn_to_function")] += 1
        for context in contexts:
            edge_counts[(node_id("method", method), node_id("application", context), "method_to_application")] += 1
            edge_counts[(node_id("function", function), node_id("application", context), "function_to_application")] += 1

        project_rows.append(
            {
                "approval_no": project_id,
                "heritage_object": obj,
                "turn_type": turn,
                "methodological_orientation": method,
                "knowledge_function": function,
                "application_contexts": "; ".join(contexts),
            }
        )

    label_maps = {
        "object": OBJECT_EN,
        "turn": TURN_EN,
        "method": METHOD_EN,
        "function": FUNCTION_EN,
        "application": APPLICATION_CONTEXT_EN,
    }

    order_maps = {
        "object": OBJECT_ORDER,
        "turn": TURN_ORDER,
        "method": METHOD_ORDER,
        "function": FUNCTION_ORDER,
        "application": APPLICATION_CONTEXT_ORDER,
    }

    node_rows = []
    for node_type, order in order_maps.items():
        for label_cn in order:
            count = int(node_counts[node_type].get(label_cn, 0))
            if count <= 0 and node_type != "turn":
                continue
            node_rows.append(
                {
                    "node_id": node_id(node_type, label_cn),
                    "node_type": node_type,
                    "label_cn": label_cn,
                    "label_en": label_maps[node_type].get(label_cn, label_cn).replace("\n", " "),
                    "count": count,
                }
            )

    nodes_df = pd.DataFrame(node_rows)
    node_lookup = {
        row["node_id"]: row
        for row in nodes_df.to_dict(orient="records")
    }

    edges = []
    for (source, target, edge_type), weight in edge_counts.items():
        if weight < PLOT_CONFIG["edge_min_weight"]:
            continue
        source_meta = node_lookup.get(source, {})
        target_meta = node_lookup.get(target, {})
        edges.append(
            {
                "source": source,
                "target": target,
                "edge_type": edge_type,
                "weight": int(weight),
                "source_type": source_meta.get("node_type", ""),
                "source_label_cn": source_meta.get("label_cn", ""),
                "source_label_en": source_meta.get("label_en", ""),
                "target_type": target_meta.get("node_type", ""),
                "target_label_cn": target_meta.get("label_cn", ""),
                "target_label_en": target_meta.get("label_en", ""),
            }
        )
    edges = normalize_strengths(edges)

    return nodes_df, pd.DataFrame(edges), pd.DataFrame(project_rows)


# =============================================================================
# 7. Layout
# =============================================================================

def evenly_spaced(labels: list[str], y_top: float, y_bottom: float) -> dict[str, float]:
    if len(labels) == 1:
        return {labels[0]: (y_top + y_bottom) / 2}
    ys = np.linspace(y_top, y_bottom, len(labels))
    return dict(zip(labels, ys))


def build_layout(nodes: pd.DataFrame) -> dict[str, tuple[float, float]]:
    """Build node positions once; all edges are drawn from this same table."""
    layout: dict[str, tuple[float, float]] = {}

    y_object = evenly_spaced(
        [x for x in OBJECT_ORDER if node_id("object", x) in set(nodes["node_id"])],
        PLOT_CONFIG["object_y_top"],
        PLOT_CONFIG["object_y_bottom"],
    )
    y_turn = evenly_spaced(TURN_ORDER, PLOT_CONFIG["turn_y_top"], PLOT_CONFIG["turn_y_bottom"])
    y_method = evenly_spaced(
        [x for x in METHOD_ORDER if node_id("method", x) in set(nodes["node_id"])],
        PLOT_CONFIG["method_y_top"],
        PLOT_CONFIG["method_y_bottom"],
    )
    y_function = evenly_spaced(
        [x for x in FUNCTION_ORDER if node_id("function", x) in set(nodes["node_id"])],
        PLOT_CONFIG["function_y_top"],
        PLOT_CONFIG["function_y_bottom"],
    )
    y_application = evenly_spaced(
        [x for x in APPLICATION_CONTEXT_ORDER if node_id("application", x) in set(nodes["node_id"])],
        PLOT_CONFIG["application_y_top"],
        PLOT_CONFIG["application_y_bottom"],
    )

    for label, y in y_object.items():
        layout[node_id("object", label)] = (PLOT_CONFIG["object_x"], float(y))
    for label, y in y_turn.items():
        layout[node_id("turn", label)] = (PLOT_CONFIG["turn_x"], float(y))
    for label, y in y_method.items():
        layout[node_id("method", label)] = (PLOT_CONFIG["method_x"], float(y))
    for label, y in y_function.items():
        layout[node_id("function", label)] = (PLOT_CONFIG["function_x"], float(y))
    for label, y in y_application.items():
        layout[node_id("application", label)] = (PLOT_CONFIG["application_x"], float(y))

    return layout


def save_source_data(
    nodes: pd.DataFrame,
    edges: pd.DataFrame,
    project_rows: pd.DataFrame,
    layout: dict[str, tuple[float, float]],
) -> None:
    """Export source data for figure audit and later manuscript use."""
    layout_df = pd.DataFrame(
        [
            {"node_id": key, "x": value[0], "y": value[1]}
            for key, value in layout.items()
        ]
    )
    nodes.merge(layout_df, on="node_id", how="left").to_csv(
        SRC_DIR / f"{FIGURE_STEM}_nodes.csv",
        index=False,
        encoding="utf-8-sig",
    )
    edges.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_edges.csv",
        index=False,
        encoding="utf-8-sig",
    )
    project_rows.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_project_level_records.csv",
        index=False,
        encoding="utf-8-sig",
    )
    rules = []
    for context, fields in APPLICATION_CONTEXT_RULES.items():
        for field, tags in fields.items():
            for tag in sorted(tags):
                rules.append(
                    {
                        "application_context_cn": context,
                        "application_context_en": APPLICATION_CONTEXT_EN[context].replace("\n", " "),
                        "source_field": field,
                        "matched_tag": tag,
                    }
                )
    pd.DataFrame(rules).to_csv(
        SRC_DIR / f"{FIGURE_STEM}_application_context_rules.csv",
        index=False,
        encoding="utf-8-sig",
    )
    manifest = pd.DataFrame(
        [
            {
                "figure": FIGURE_STEM,
                "panel": "b",
                "source_data": f"source_data/{FIGURE_STEM}_nodes.csv",
                "description": "Node table with coding-framework labels and plotted coordinates.",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "b",
                "source_data": f"source_data/{FIGURE_STEM}_edges.csv",
                "description": "Directed project-level co-occurrence edges; strength is normalized within each source node.",
            },
            {
                "figure": FIGURE_STEM,
                "panel": "b",
                "source_data": f"source_data/{FIGURE_STEM}_application_context_rules.csv",
                "description": "Rules used to derive application contexts from LLM-coded project tags.",
            },
        ]
    )
    manifest.to_csv(
        SRC_DIR / f"{FIGURE_STEM}_source_data_manifest.csv",
        index=False,
        encoding="utf-8-sig",
    )


# =============================================================================
# 8. Drawing functions
# =============================================================================

def edge_patch(
    p0: tuple[float, float],
    p1: tuple[float, float],
    strength: float,
    weight: int,
    max_weight: int,
    alpha_scale: float = 1.0,
) -> PathPatch:
    """Create a Bezier edge patch between two node centers."""
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    curve = PLOT_CONFIG["edge_curve"]
    c1 = (x0 + dx * curve, y0)
    c2 = (x1 - dx * curve, y1)
    path = MplPath(
        [(x0, y0), c1, c2, (x1, y1)],
        [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4],
    )
    width = PLOT_CONFIG["edge_width_min"] + (
        PLOT_CONFIG["edge_width_max"] - PLOT_CONFIG["edge_width_min"]
    ) * math.sqrt(weight / max_weight)
    alpha = PLOT_CONFIG["edge_alpha_min"] + (
        PLOT_CONFIG["edge_alpha_max"] - PLOT_CONFIG["edge_alpha_min"]
    ) * strength
    color = to_rgba(FLOW_CMAP(FLOW_NORM(strength)), alpha * alpha_scale)
    return PathPatch(
        path,
        facecolor="none",
        edgecolor=color,
        linewidth=width,
        capstyle="round",
        joinstyle="round",
        zorder=1,
    )


def draw_edges(ax, edges: pd.DataFrame, layout: dict[str, tuple[float, float]]) -> None:
    """Draw all edges using the same node coordinates used for node plotting."""
    if edges.empty:
        return
    max_weight = int(edges["weight"].max())
    # Draw weaker edges first.
    for _, edge in edges.sort_values("weight").iterrows():
        source = edge["source"]
        target = edge["target"]
        if source not in layout or target not in layout:
            continue
        patch = edge_patch(
            layout[source],
            layout[target],
            float(edge["strength"]),
            int(edge["weight"]),
            max_weight,
            alpha_scale=0.92,
        )
        ax.add_patch(patch)


def node_size(node_type: str, count: int, max_turn_count: int) -> float:
    """Return marker size for each node family."""
    if node_type == "turn":
        if max_turn_count <= 1:
            return PLOT_CONFIG["turn_marker_min"]
        scale = math.sqrt(max(count, 1) / max_turn_count)
        return PLOT_CONFIG["turn_marker_min"] + (
            PLOT_CONFIG["turn_marker_max"] - PLOT_CONFIG["turn_marker_min"]
        ) * scale
    if node_type == "method":
        return PLOT_CONFIG["method_marker_base"] + 5.2 * count
    if node_type == "function":
        return PLOT_CONFIG["function_marker_base"] + 5.5 * count
    if node_type == "application":
        return PLOT_CONFIG["application_marker_base"] + 3.8 * count
    return PLOT_CONFIG["object_marker_size"] + 3.2 * count


def draw_nodes_and_labels(ax, nodes: pd.DataFrame, layout: dict[str, tuple[float, float]]) -> None:
    """Draw nodes and direct labels."""
    max_turn_count = int(nodes.loc[nodes["node_type"].eq("turn"), "count"].max())

    marker_map = {
        "object": "s",
        "turn": "o",
        "method": "^",
        "function": "D",
        "application": "h",
    }

    # Draw node markers.
    for _, node in nodes.iterrows():
        nid = node["node_id"]
        if nid not in layout:
            continue
        x, y = layout[nid]
        node_type = node["node_type"]
        label_cn = node["label_cn"]
        count = int(node["count"])
        if node_type == "turn":
            color = TURN_COLORS.get(label_cn, CATEGORY_COLORS["turn"])
        else:
            color = CATEGORY_COLORS[node_type]

        ax.scatter(
            [x],
            [y],
            s=node_size(node_type, count, max_turn_count),
            marker=marker_map[node_type],
            color=color,
            edgecolor="white",
            linewidth=0.9,
            alpha=0.96,
            zorder=4 if node_type != "turn" else 5,
        )

        if node_type == "turn":
            ax.text(
                x,
                y,
                str(count),
                ha="center",
                va="center",
                fontsize=PLOT_CONFIG["turn_count_fontsize"],
                fontweight="bold",
                color="white",
                zorder=6,
            )

    # Draw labels after markers for readability.
    for _, node in nodes.iterrows():
        nid = node["node_id"]
        if nid not in layout:
            continue
        x, y = layout[nid]
        node_type = node["node_type"]
        label_cn = node["label_cn"]
        count = int(node["count"])
        label = node["label_en"]
        if node_type != "turn":
            label = f"{label} ({count})"

        if node_type == "object":
            ax.text(
                x - 0.10,
                y,
                wrap_label(label, 22),
                ha="right",
                va="center",
                fontsize=PLOT_CONFIG["label_fontsize"],
                color="#222222",
                zorder=7,
            )
        elif node_type == "turn":
            ax.text(
                x + 0.18,
                y,
                wrap_label(TURN_EN[label_cn].replace("\n", " "), 25),
                ha="left",
                va="center",
                fontsize=PLOT_CONFIG["label_fontsize"],
                fontweight="bold",
                color=TURN_COLORS.get(label_cn, CATEGORY_COLORS["turn"]),
                zorder=7,
            )
        elif node_type in {"method", "function"}:
            ax.text(
                x + 0.08,
                y,
                wrap_label(label, 24),
                ha="left",
                va="center",
                fontsize=PLOT_CONFIG["small_label_fontsize"],
                color="#222222",
                zorder=7,
            )
        elif node_type == "application":
            ax.text(
                x + 0.10,
                y,
                wrap_label(label, 25),
                ha="left",
                va="center",
                fontsize=PLOT_CONFIG["label_fontsize"],
                color="#222222",
                zorder=7,
            )


def draw_column_titles(ax) -> None:
    """Draw manuscript-consistent column titles."""
    title_style = {
        "fontsize": PLOT_CONFIG["column_title_fontsize"],
        "fontweight": "bold",
        "ha": "center",
        "va": "center",
    }
    ax.text(PLOT_CONFIG["object_x"], 1.07, "Heritage objects", color=CATEGORY_COLORS["object"], **title_style)
    ax.text(PLOT_CONFIG["turn_x"], 1.07, "Research\nturns", color=CATEGORY_COLORS["turn"], **title_style)
    ax.text(PLOT_CONFIG["method_x"], 1.07, "Methodological\norientations", color=CATEGORY_COLORS["method"], **title_style)
    ax.text(PLOT_CONFIG["function_x"], 0.13, "Knowledge\nfunctions", color="#C78A34", **title_style)
    ax.text(PLOT_CONFIG["application_x"], 1.07, "Application\ncontexts", color="#5B646E", **title_style)


def draw_legend(ax) -> None:
    """Draw node-shape legend and source-normalized strength colour bar."""
    handles = [
        Line2D([0], [0], marker="s", color="none", markerfacecolor=CATEGORY_COLORS["object"],
               markeredgecolor="white", markersize=8, label="Heritage object"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=CATEGORY_COLORS["turn"],
               markeredgecolor="white", markersize=8, label="Research turn"),
        Line2D([0], [0], marker="^", color="none", markerfacecolor=CATEGORY_COLORS["method"],
               markeredgecolor="white", markersize=8, label="Methodological orientation"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=CATEGORY_COLORS["function"],
               markeredgecolor="white", markersize=8, label="Knowledge function"),
        Line2D([0], [0], marker="h", color="none", markerfacecolor=CATEGORY_COLORS["application"],
               markeredgecolor="white", markersize=9, label="Application context"),
    ]
    ax.legend(
        handles=handles,
        loc="lower left",
        bbox_to_anchor=(0.02, 0.025),
        frameon=False,
        fontsize=7.5,
        ncol=2,
        handletextpad=0.5,
        columnspacing=1.4,
    )
    ax.text(
        0.54,
        0.055,
        "Edge width indicates co-occurrence count; edge colour indicates source-normalized strength.",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=7.4,
        color="#444444",
    )
    cax = ax.inset_axes([0.39, -0.005, 0.30, 0.026], transform=ax.transAxes)
    sm = ScalarMappable(norm=FLOW_NORM, cmap=FLOW_CMAP)
    cb = plt.colorbar(sm, cax=cax, orientation="horizontal")
    cb.set_label("Source-normalized co-occurrence strength (0-1)", fontsize=7.6)
    cb.ax.tick_params(labelsize=7.0, length=2.5, width=0.5)
    cb.outline.set_visible(False)


def draw_figure(nodes: pd.DataFrame, edges: pd.DataFrame, layout: dict[str, tuple[float, float]]) -> plt.Figure:
    """Draw the final network figure."""
    fig, ax = plt.subplots(
        figsize=(PLOT_CONFIG["fig_width"], PLOT_CONFIG["fig_height"]),
        dpi=PLOT_CONFIG["figure_dpi"],
    )
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.text(
        PLOT_CONFIG["xlim"][0] + 0.02,
        PLOT_CONFIG["ylim"][1] - 0.035,
        "Project-level co-occurrence network of research turns",
        ha="left",
        va="top",
        fontsize=PLOT_CONFIG["title_fontsize"],
        fontweight="bold",
        color="#111111",
    )

    draw_column_titles(ax)
    draw_edges(ax, edges, layout)
    draw_nodes_and_labels(ax, nodes, layout)
    draw_legend(ax)

    ax.set_xlim(*PLOT_CONFIG["xlim"])
    ax.set_ylim(*PLOT_CONFIG["ylim"])
    ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.99, top=0.97, bottom=0.09)
    return fig


# =============================================================================
# 9. Main
# =============================================================================

def main() -> None:
    setup_style()
    df = load_data()
    nodes, edges, project_rows = build_nodes_and_edges(df)
    layout = build_layout(nodes)
    save_source_data(nodes, edges, project_rows, layout)

    fig = draw_figure(nodes, edges, layout)

    for stem in (FIGURE_STEM, COMPAT_STEM):
        if PLOT_CONFIG["save_png"]:
            fig.savefig(FIG_DIR / f"{stem}.png", dpi=PLOT_CONFIG["output_dpi"], bbox_inches="tight")
        if PLOT_CONFIG["save_pdf"]:
            fig.savefig(FIG_DIR / f"{stem}.pdf", bbox_inches="tight")
        if PLOT_CONFIG["save_svg"]:
            fig.savefig(FIG_DIR / f"{stem}.svg", bbox_inches="tight")
        if PLOT_CONFIG["save_tiff"]:
            fig.savefig(FIG_DIR / f"{stem}.tiff", dpi=PLOT_CONFIG["output_dpi"], bbox_inches="tight")

    plt.close(fig)
    print(f"Saved revised Figure 8 to: {FIG_DIR}")
    print(f"Nodes: {len(nodes)}; Edges: {len(edges)}")


if __name__ == "__main__":
    main()
