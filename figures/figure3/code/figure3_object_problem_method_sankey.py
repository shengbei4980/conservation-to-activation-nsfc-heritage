# -*- coding: utf-8 -*-

"""
Figure 3. NSFC 遗产研究中“对象—问题—方法”的桑基图。

本图使用两个项目层面的共现矩阵：
    1. object_by_orientation_matrix.csv
       表示“遗产对象 × 问题取向”的共现关系。

    2. orientation_by_method_matrix.csv
       表示“问题取向 × 方法取向”的共现关系。

图形输出：
    - NSFC_heritage_object_problem_method_sankey_EN.svg
    - NSFC_heritage_object_problem_method_sankey_EN.pdf
    - NSFC_heritage_object_problem_method_sankey_EN.png
    - NSFC_heritage_object_problem_method_sankey_EN.tiff

同时输出：
    - 节点表 nodes
    - 连线表 links
    - 英文翻译后的对象—问题矩阵
    - 英文翻译后的问题—方法矩阵
    - 中文—英文标签映射表

重要修正：
    原代码直接用英文标签作为节点字典 key。
    由于对象列和问题列都可能出现 Integrated，
    会造成同名节点覆盖，导致对象列 Integrated 标签不显示。

    本版代码为每个节点创建唯一 node_id：
        object::Integrated
        problem::Integrated
        method::Mixed methods

    这样即使不同维度下存在同名标签，也不会互相覆盖。
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_hex, to_rgba
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle


# ============================================================
# 1. 路径设置
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = ROOT / "data" / "inputs"
OUTPUT_DIR = ROOT / "outputs" / "reproduced"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OBJECT_PROBLEM_FILE = INPUT_DIR / "object_by_orientation_matrix.csv"
PROBLEM_METHOD_FILE = INPUT_DIR / "orientation_by_method_matrix.csv"

FIGURE_STEM = OUTPUT_DIR / "NSFC_heritage_object_problem_method_sankey_EN"

NODE_CSV = OUTPUT_DIR / "NSFC_heritage_object_problem_method_sankey_nodes.csv"
LINK_CSV = OUTPUT_DIR / "NSFC_heritage_object_problem_method_sankey_links.csv"

OBJECT_PROBLEM_CSV = OUTPUT_DIR / "NSFC_heritage_object_problem_method_matrix_object_problem_EN.csv"
PROBLEM_METHOD_CSV = OUTPUT_DIR / "NSFC_heritage_object_problem_method_matrix_problem_method_EN.csv"
MAPPING_CSV = OUTPUT_DIR / "NSFC_heritage_object_problem_method_mapping_EN.csv"


# ============================================================
# 2. 图形样式、标签与颜色设置
# ============================================================

DIMENSION_COLORS = {
    "object": "#89B2F4",
    "problem": "#018C94",
    "method": "#764D9C",
}

LINK_COLORS = {
    "object-problem": "#89B2F4",
    "problem-method": "#018C94",
}

FLOW_CMAP = LinearSegmentedColormap.from_list(
    "heritage_flow_strength",
    ["#89B2F4", "#018C94", "#764D9C"],
)

FLOW_NORM = Normalize(vmin=0, vmax=1)

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

DIMENSION_LABELS = {
    "object": "Heritage object",
    "problem": "Research orientation",
    "method": "Methodological orientation",
}


# ============================================================
# 3. 图形参数控制区
# ============================================================

FIGURE_CONFIG = {
    # ---------- 画布 ----------
    "fig_width": 12.4,
    "fig_height": 8.2,
    "fig_dpi": 300,
    "output_dpi": 600,

    # ---------- 节点布局 ----------
    "y_top": 0.91,
    "y_bottom": 0.11,
    "node_width": 0.016,
    "node_gap": 0.014,

    # 三列的横向位置
    "x_pos": {
        "object": 0.095,
        "problem": 0.505,
        "method": 0.915,
    },

    # ---------- 标签字体 ----------
    "object_label_fontsize": 10,
    "problem_label_fontsize": 10,
    "method_label_fontsize": 10,
    "label_fontweight": "bold",

    # ---------- 数值字体 ----------
    "count_fontsize": 8,
    "count_color": "#333333",

    # ---------- 标签换行宽度 ----------
    "object_wrap_width": 24,
    "problem_wrap_width": 23,
    "method_wrap_width": 22,

    # ---------- 标签与节点的水平距离 ----------
    "object_label_dx": -0.012,
    "problem_label_dx": 0.010,
    "method_label_dx": -0.012,

    # ---------- 数量与节点的水平距离 ----------
    "object_count_dx": 0.006,
    "problem_count_dx": 0.009,
    "method_count_dx": 0.006,

    # ---------- 是否显示数量 ----------
    "show_object_count": True,
    "show_problem_count": True,
    "show_method_count": True,

    # ---------- 三列标题 ----------
    "title_y": 0.92,
    "column_title_fontsize": 14,
    "column_title_weight": "bold",

    # ---------- 图下注释 ----------
    "show_caption_note": True,
    "caption_note": "Link width represents co-occurrence count; ribbon colour indicates source-normalized flow strength.",
    "caption_x": 0.5,
    "caption_y": 0.060,
    "caption_fontsize": 11,
    "caption_color": "#333333",

    # ---------- 连线强度图例 ----------
    "show_flow_colorbar": True,
    "colorbar_left": 0.35,
    "colorbar_bottom": 0.050,
    "colorbar_width": 0.30,
    "colorbar_height": 0.018,
    "colorbar_label": "Source-normalized flow strength (0-1)",
    "colorbar_labelsize": 9,
    "colorbar_ticksize": 8,
    "colorbar_ticks": [0, 0.2, 0.4, 0.6, 0.8, 1],

    # ---------- 坐标范围 ----------
    "xlim": (0.00, 1.00),
    "ylim": (0.04, 0.975),
}


# ============================================================
# 4. 字体与文本工具函数
# ============================================================

def require_arial_font(font_name: str = "Arial") -> None:
    """
    强制使用 Arial 字体。

    如果 Matplotlib 没有检测到 Arial，则直接报错。
    这样可以避免投稿图件中字体被自动替换。
    """
    available_fonts = {f.name for f in fm.fontManager.ttflist}

    if font_name not in available_fonts:
        raise RuntimeError(
            f"Arial font was not detected by Matplotlib: {font_name}"
        )

    mpl.rcParams.update(
        {
            "font.family": font_name,
            "font.sans-serif": [font_name],
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def wrap_label(label: str, width: int = 22) -> str:
    """
    对较长英文标签进行换行。
    """
    return "\n".join(
        textwrap.wrap(
            str(label),
            width=width,
            break_long_words=False
        )
    )


def make_node_id(node_type: str, label: str) -> str:
    """
    创建唯一节点 ID。

    解决不同维度下同名节点互相覆盖的问题。
    例如：
        object::Integrated
        problem::Integrated
    """
    return f"{node_type}::{label}"


# ============================================================
# 5. 数据读取与预处理
# ============================================================

def read_matrix(path: Path, index_col: str) -> pd.DataFrame:
    """
    读取共现矩阵。

    要求：
        - CSV 中必须包含 index_col 这一列；
        - 其余列为共现类别；
        - 单元格为共现数量。
    """
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_csv(path, encoding="utf-8-sig")

    if index_col not in df.columns:
        raise ValueError(f"Missing index column `{index_col}` in {path}")

    df[index_col] = df[index_col].astype(str).str.strip()

    return df.set_index(index_col).fillna(0).astype(float)


# 读取中文共现矩阵。
object_problem_cn = read_matrix(
    OBJECT_PROBLEM_FILE,
    "heritage_objects"
)

problem_method_cn = read_matrix(
    PROBLEM_METHOD_FILE,
    "research_orientations"
)


# ============================================================
# 6. 节点排序与英文映射
# ============================================================

# 对象按照总流量从大到小排序。
object_order_cn = (
    object_problem_cn.sum(axis=1)
    .sort_values(ascending=False)
    .index.tolist()
)

# 问题按照对象—问题矩阵中的总流量从大到小排序。
problem_order_cn = (
    object_problem_cn.sum(axis=0)
    .sort_values(ascending=False)
    .index.tolist()
)

# 方法按照问题—方法矩阵中的总流量从大到小排序。
method_order_cn = (
    problem_method_cn.sum(axis=0)
    .sort_values(ascending=False)
    .index.tolist()
)

# 重排矩阵。
object_problem_cn = object_problem_cn.loc[
    object_order_cn,
    problem_order_cn
]

problem_method_cn = problem_method_cn.loc[
    problem_order_cn,
    method_order_cn
]

# 中文标签映射为英文标签。
object_order_en = [
    HERITAGE_OBJECT_MAPPING[x]
    for x in object_order_cn
]

problem_order_en = [
    RESEARCH_ORIENTATION_MAPPING[x]
    for x in problem_order_cn
]

method_order_en = [
    METHOD_ORIENTATION_MAPPING[x]
    for x in method_order_cn
]


# ============================================================
# 7. 输出英文版矩阵与映射表
# ============================================================

object_problem_en = object_problem_cn.copy()
object_problem_en.index = object_order_en
object_problem_en.columns = problem_order_en

problem_method_en = problem_method_cn.copy()
problem_method_en.index = problem_order_en
problem_method_en.columns = method_order_en

object_problem_en.to_csv(
    OBJECT_PROBLEM_CSV,
    encoding="utf-8-sig"
)

problem_method_en.to_csv(
    PROBLEM_METHOD_CSV,
    encoding="utf-8-sig"
)

mapping_records = []

for cn, en in HERITAGE_OBJECT_MAPPING.items():
    mapping_records.append(
        {
            "dimension": "heritage_object",
            "label_cn": cn,
            "label_en": en,
        }
    )

for cn, en in RESEARCH_ORIENTATION_MAPPING.items():
    mapping_records.append(
        {
            "dimension": "research_orientation",
            "label_cn": cn,
            "label_en": en,
        }
    )

for cn, en in METHOD_ORIENTATION_MAPPING.items():
    mapping_records.append(
        {
            "dimension": "method_orientation",
            "label_cn": cn,
            "label_en": en,
        }
    )

pd.DataFrame(mapping_records).to_csv(
    MAPPING_CSV,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. 桑基图节点布局计算
# ============================================================

TOTAL_PROJECTS = float(object_problem_cn.values.sum())

if TOTAL_PROJECTS <= 0:
    raise ValueError(
        "The object-problem matrix contains no positive flow."
    )

Y_TOP = FIGURE_CONFIG["y_top"]
Y_BOTTOM = FIGURE_CONFIG["y_bottom"]
NODE_WIDTH = FIGURE_CONFIG["node_width"]
NODE_GAP = FIGURE_CONFIG["node_gap"]
X_POS = FIGURE_CONFIG["x_pos"]


def node_positions(
    labels: list[str],
    values: list[float],
    x: float,
    node_type: str
) -> dict[str, dict[str, float]]:
    """
    计算某一列节点的位置。

    返回的字典以 node_id 为 key，而不是以 label 为 key。
    这样可以避免 Integrated 等同名标签在不同维度之间互相覆盖。
    """
    available_height = (
        Y_TOP
        - Y_BOTTOM
        - NODE_GAP * (len(labels) - 1)
    )

    scale = available_height / sum(values)

    positions = {}
    y_cursor = Y_TOP

    for label, value in zip(labels, values):
        node_id = make_node_id(node_type, label)

        height = value * scale
        y0 = y_cursor - height
        y1 = y_cursor

        positions[node_id] = {
            "node_id": node_id,
            "label": label,
            "x0": x,
            "x1": x + NODE_WIDTH,
            "y0": y0,
            "y1": y1,
            "height": height,
            "value": value,
            "type": node_type,
        }

        y_cursor = y0 - NODE_GAP

    return positions


# 三列节点数量。
object_values = object_problem_cn.sum(axis=1).tolist()
problem_values = object_problem_cn.sum(axis=0).loc[problem_order_cn].tolist()
method_values = problem_method_cn.sum(axis=0).loc[method_order_cn].tolist()

# 三列节点位置。
object_nodes = node_positions(
    object_order_en,
    object_values,
    X_POS["object"],
    "object"
)

problem_nodes = node_positions(
    problem_order_en,
    problem_values,
    X_POS["problem"],
    "problem"
)

method_nodes = node_positions(
    method_order_en,
    method_values,
    X_POS["method"],
    "method"
)

# 合并节点。现在 key 是唯一 node_id，不会再发生同名覆盖。
nodes = {
    **object_nodes,
    **problem_nodes,
    **method_nodes,
}


# ============================================================
# 9. 导出节点表
# ============================================================

node_rows = []

for node_id, info in nodes.items():
    node_rows.append(
        {
            "node_id": node_id,
            "node_label": info["label"],
            "dimension": info["type"],
            "count": int(round(info["value"])),
            "x0": info["x0"],
            "x1": info["x1"],
            "y0": info["y0"],
            "y1": info["y1"],
        }
    )

pd.DataFrame(node_rows).to_csv(
    NODE_CSV,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 10. 连线分段计算
# ============================================================

def segment_tracker(
    node_dict: dict[str, dict[str, float]]
) -> dict[str, float]:
    """
    为每个节点建立一个流量分段游标。

    每条流线会占据节点矩形的一部分高度。
    游标用于记录当前节点还可以从哪里继续分配流线。
    """
    return {
        node_id: info["y1"]
        for node_id, info in node_dict.items()
    }


object_out_cursor = segment_tracker(object_nodes)
problem_in_cursor = segment_tracker(problem_nodes)
problem_out_cursor = segment_tracker(problem_nodes)
method_in_cursor = segment_tracker(method_nodes)

global_scale = (
    Y_TOP
    - Y_BOTTOM
    - NODE_GAP * (
        max(
            len(object_order_en),
            len(problem_order_en),
            len(method_order_en)
        )
        - 1
    )
) / TOTAL_PROJECTS


def take_segment(
    cursor: dict[str, float],
    node_id: str,
    value: float
) -> tuple[float, float]:
    """
    从节点中取出一段高度，用作某条流线在节点上的连接位置。
    """
    height = value * global_scale

    y1 = cursor[node_id]
    y0 = y1 - height

    cursor[node_id] = y0

    return y0, y1


# ============================================================
# 11. 构造连线表
# ============================================================

link_rows = []


# ------------------------------------------------------------
# 11.1 对象 → 问题
# ------------------------------------------------------------

for obj_cn, obj_en in zip(object_order_cn, object_order_en):
    for prob_cn, prob_en in zip(problem_order_cn, problem_order_en):
        value = float(object_problem_cn.loc[obj_cn, prob_cn])

        if value <= 0:
            continue

        source_id = make_node_id("object", obj_en)
        target_id = make_node_id("problem", prob_en)

        source_y0, source_y1 = take_segment(
            object_out_cursor,
            source_id,
            value
        )

        target_y0, target_y1 = take_segment(
            problem_in_cursor,
            target_id,
            value
        )

        link_rows.append(
            {
                "level": "object-problem",
                "source_dimension": "heritage_object",
                "target_dimension": "research_orientation",
                "source_id": source_id,
                "target_id": target_id,
                "source": obj_en,
                "target": prob_en,
                "value": int(value),
                "source_x": object_nodes[source_id]["x1"],
                "target_x": problem_nodes[target_id]["x0"],
                "source_y0": source_y0,
                "source_y1": source_y1,
                "target_y0": target_y0,
                "target_y1": target_y1,
                "color": LINK_COLORS["object-problem"],
            }
        )


# ------------------------------------------------------------
# 11.2 问题 → 方法
# ------------------------------------------------------------

for prob_cn, prob_en in zip(problem_order_cn, problem_order_en):
    for method_cn, method_en in zip(method_order_cn, method_order_en):
        value = float(problem_method_cn.loc[prob_cn, method_cn])

        if value <= 0:
            continue

        source_id = make_node_id("problem", prob_en)
        target_id = make_node_id("method", method_en)

        source_y0, source_y1 = take_segment(
            problem_out_cursor,
            source_id,
            value
        )

        target_y0, target_y1 = take_segment(
            method_in_cursor,
            target_id,
            value
        )

        link_rows.append(
            {
                "level": "problem-method",
                "source_dimension": "research_orientation",
                "target_dimension": "method_orientation",
                "source_id": source_id,
                "target_id": target_id,
                "source": prob_en,
                "target": method_en,
                "value": int(value),
                "source_x": problem_nodes[source_id]["x1"],
                "target_x": method_nodes[target_id]["x0"],
                "source_y0": source_y0,
                "source_y1": source_y1,
                "target_y0": target_y0,
                "target_y1": target_y1,
                "color": LINK_COLORS["problem-method"],
            }
        )

links = pd.DataFrame(link_rows)

if links.empty:
    raise ValueError("No positive links were generated for the Sankey diagram.")

# 源端归一化流向强度：
# 对象—问题层级中，分母为同一遗产对象的全部外流；
# 问题—方法层级中，分母为同一问题取向的全部外流。
# 因而颜色表达的是“该连接在其源节点内部的重要性”，数值范围稳定在 0—1。
source_totals = links.groupby(["level", "source_id"])["value"].transform("sum")
links["flow_strength"] = links["value"] / source_totals
links["flow_strength"] = links["flow_strength"].fillna(0).clip(0, 1)
links["color"] = links["flow_strength"].apply(
    lambda value: to_hex(FLOW_CMAP(FLOW_NORM(float(value))))
)

links.to_csv(
    LINK_CSV,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 12. 绘图函数
# ============================================================

def draw_link(
    ax,
    row: pd.Series,
    alpha: float = 0.33
) -> None:
    """
    绘制一条桑基图流线。

    这里用贝塞尔曲线闭合多边形绘制“有宽度的流”。
    """
    x0 = row["source_x"]
    x1 = row["target_x"]

    y0a, y0b = row["source_y0"], row["source_y1"]
    y1a, y1b = row["target_y0"], row["target_y1"]

    dx = x1 - x0

    # 控制曲线弯曲程度。
    c0 = x0 + dx * 0.48
    c1 = x1 - dx * 0.48

    verts = [
        (x0, y0b),
        (c0, y0b),
        (c1, y1b),
        (x1, y1b),
        (x1, y1a),
        (c1, y1a),
        (c0, y0a),
        (x0, y0a),
        (x0, y0b),
    ]

    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]

    patch = PathPatch(
        MplPath(verts, codes),
        facecolor=to_rgba(row["color"], alpha),
        edgecolor="none",
        zorder=1,
    )

    ax.add_patch(patch)


def add_node(
    ax,
    info: dict[str, float]
) -> None:
    """
    绘制一个节点矩形、节点标签和节点数量。

    三列标签规则：
        object:
            标签在左侧，数量在右侧。

        problem:
            标签在右侧，数量也在右侧，位于标签后方。
            这是本版新增的中间问题取向数量显示。

        method:
            标签在左侧，数量在右侧。
    """
    label = info["label"]
    node_type = info["type"]
    color = DIMENSION_COLORS[node_type]

    rect = Rectangle(
        (info["x0"], info["y0"]),
        NODE_WIDTH,
        info["height"],
        facecolor=color,
        edgecolor="white",
        linewidth=0.8,
        alpha=0.95,
        zorder=4,
    )

    ax.add_patch(rect)

    y = (info["y0"] + info["y1"]) / 2
    count_label = f"{int(round(info['value']))}"

    # --------------------------------------------------------
    # 对象列：标签在节点左侧，数量在节点右侧
    # --------------------------------------------------------
    if node_type == "object":
        ax.text(
            info["x0"] + FIGURE_CONFIG["object_label_dx"],
            y,
            wrap_label(label, FIGURE_CONFIG["object_wrap_width"]),
            ha="right",
            va="center",
            fontsize=FIGURE_CONFIG["object_label_fontsize"],
            fontweight=FIGURE_CONFIG["label_fontweight"],
            color="#111111",
            zorder=20,
            clip_on=False,
        )

        if FIGURE_CONFIG["show_object_count"]:
            ax.text(
                info["x1"] + FIGURE_CONFIG["object_count_dx"],
                y,
                count_label,
                ha="left",
                va="center",
                fontsize=FIGURE_CONFIG["count_fontsize"],
                color=FIGURE_CONFIG["count_color"],
                zorder=20,
                clip_on=False,
            )

    # --------------------------------------------------------
    # 问题列：标签在节点右侧，数量显示在标签右侧
    # --------------------------------------------------------
    elif node_type == "problem":
        label_x = info["x1"] + FIGURE_CONFIG["problem_label_dx"]

        ax.text(
            label_x,
            y,
            wrap_label(label, FIGURE_CONFIG["problem_wrap_width"]),
            ha="left",
            va="center",
            fontsize=FIGURE_CONFIG["problem_label_fontsize"],
            fontweight=FIGURE_CONFIG["label_fontweight"],
            color="#111111",
            zorder=20,
            clip_on=False,
        )

        if FIGURE_CONFIG["show_problem_count"]:
            # 为了避免数量压到标签上，问题列数量放在标签右侧较远位置。
            # 如果你觉得太远或太近，可调 0.128。
            ax.text(
                label_x - 0.05,
                y,
                count_label,
                ha="left",
                va="center",
                fontsize=FIGURE_CONFIG["count_fontsize"],
                color=FIGURE_CONFIG["count_color"],
                zorder=20,
                clip_on=False,
            )

    # --------------------------------------------------------
    # 方法列：标签在节点左侧，数量在节点右侧
    # --------------------------------------------------------
    else:
        ax.text(
            info["x0"] + FIGURE_CONFIG["method_label_dx"],
            y,
            wrap_label(label, FIGURE_CONFIG["method_wrap_width"]),
            ha="right",
            va="center",
            fontsize=FIGURE_CONFIG["method_label_fontsize"],
            fontweight=FIGURE_CONFIG["label_fontweight"],
            color="#111111",
            zorder=20,
            clip_on=False,
        )

        if FIGURE_CONFIG["show_method_count"]:
            ax.text(
                info["x1"] + FIGURE_CONFIG["method_count_dx"],
                y,
                count_label,
                ha="left",
                va="center",
                fontsize=FIGURE_CONFIG["count_fontsize"],
                color=FIGURE_CONFIG["count_color"],
                zorder=20,
                clip_on=False,
            )


# ============================================================
# 13. 正式绘图
# ============================================================

require_arial_font()

fig, ax = plt.subplots(
    figsize=(
        FIGURE_CONFIG["fig_width"],
        FIGURE_CONFIG["fig_height"]
    ),
    dpi=FIGURE_CONFIG["fig_dpi"],
)

ax.set_xlim(*FIGURE_CONFIG["xlim"])
ax.set_ylim(*FIGURE_CONFIG["ylim"])
ax.axis("off")


# ------------------------------------------------------------
# 13.1 绘制连线
# ------------------------------------------------------------

# 先绘制较大的流，避免小流完全被遮挡。
for _, row in links.sort_values("value", ascending=False).iterrows():
    draw_link(
        ax,
        row,
        alpha=0.34 if row["level"] == "object-problem" else 0.31
    )


# ------------------------------------------------------------
# 13.2 绘制节点、标签和数量
# ------------------------------------------------------------

# 先按维度顺序绘制，便于控制图层。
for node_type in ["object", "problem", "method"]:
    for node_id, info in nodes.items():
        if info["type"] == node_type:
            add_node(ax, info)


# ------------------------------------------------------------
# 13.3 绘制三列标题
# ------------------------------------------------------------

title_y = FIGURE_CONFIG["title_y"]

ax.text(
    X_POS["object"] + NODE_WIDTH / 2,
    title_y,
    DIMENSION_LABELS["object"],
    ha="center",
    va="bottom",
    fontsize=FIGURE_CONFIG["column_title_fontsize"],
    fontweight=FIGURE_CONFIG["column_title_weight"],
    color=DIMENSION_COLORS["object"],
    clip_on=False,
)

ax.text(
    X_POS["problem"] + NODE_WIDTH / 2,
    title_y,
    DIMENSION_LABELS["problem"],
    ha="center",
    va="bottom",
    fontsize=FIGURE_CONFIG["column_title_fontsize"],
    fontweight=FIGURE_CONFIG["column_title_weight"],
    color=DIMENSION_COLORS["problem"],
    clip_on=False,
)

ax.text(
    X_POS["method"] + NODE_WIDTH / 2,
    title_y,
    DIMENSION_LABELS["method"],
    ha="center",
    va="bottom",
    fontsize=FIGURE_CONFIG["column_title_fontsize"],
    fontweight=FIGURE_CONFIG["column_title_weight"],
    color=DIMENSION_COLORS["method"],
    clip_on=False,
)


# ------------------------------------------------------------
# 13.4 添加图下注释
# ------------------------------------------------------------

if FIGURE_CONFIG["show_caption_note"]:
    ax.text(
        FIGURE_CONFIG["caption_x"],
        FIGURE_CONFIG["caption_y"],
        FIGURE_CONFIG["caption_note"],
        ha="center",
        va="center",
        fontsize=FIGURE_CONFIG["caption_fontsize"],
        color=FIGURE_CONFIG["caption_color"],
        clip_on=False,
    )


# ------------------------------------------------------------
# 13.5 添加 0—1 流向强度颜色图例
# ------------------------------------------------------------

if FIGURE_CONFIG["show_flow_colorbar"]:
    cax = fig.add_axes(
        [
            FIGURE_CONFIG["colorbar_left"],
            FIGURE_CONFIG["colorbar_bottom"],
            FIGURE_CONFIG["colorbar_width"],
            FIGURE_CONFIG["colorbar_height"],
        ]
    )
    sm = ScalarMappable(norm=FLOW_NORM, cmap=FLOW_CMAP)
    sm.set_array([])
    cbar = fig.colorbar(
        sm,
        cax=cax,
        orientation="horizontal",
        ticks=FIGURE_CONFIG["colorbar_ticks"],
    )
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(
        labelsize=FIGURE_CONFIG["colorbar_ticksize"],
        length=2.5,
        width=0.6,
        pad=2,
        colors="#222222",
    )
    cbar.set_label(
        FIGURE_CONFIG["colorbar_label"],
        fontsize=FIGURE_CONFIG["colorbar_labelsize"],
        color="#222222",
        labelpad=3,
    )


# ============================================================
# 14. 保存图件
# ============================================================

fig.savefig(
    f"{FIGURE_STEM}.svg",
    bbox_inches="tight"
)

fig.savefig(
    f"{FIGURE_STEM}.pdf",
    bbox_inches="tight"
)

fig.savefig(
    f"{FIGURE_STEM}.png",
    dpi=FIGURE_CONFIG["output_dpi"],
    bbox_inches="tight"
)

fig.savefig(
    f"{FIGURE_STEM}.tiff",
    dpi=FIGURE_CONFIG["output_dpi"],
    bbox_inches="tight"
)

plt.close(fig)


# ============================================================
# 15. 输出运行结果与核查提示
# ============================================================

print(f"Saved figure files to: {OUTPUT_DIR}")
print(f"Saved source data: {LINK_CSV.name}, {NODE_CSV.name}")

# 核查 Integrated 是否分别存在于 object 和 problem 中。
node_check = pd.read_csv(NODE_CSV, encoding="utf-8-sig")

print("\nCheck nodes with label = Integrated:")
print(
    node_check[node_check["node_label"] == "Integrated"]
    [["node_id", "node_label", "dimension", "count"]]
)
