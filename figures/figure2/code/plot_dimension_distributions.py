# -*- coding: utf-8 -*-

"""
用于绘制 NSFC 遗产研究中“遗产对象—问题取向—方法取向”的综合棒棒糖图。

输入文件：
    1. heritage_object_counts.csv
    2. research_orientation_counts.csv
    3. method_orientation_counts.csv

三个 CSV 文件需要包含以下列：
    heritage_object_counts.csv:
        heritage_object, count, percent

    research_orientation_counts.csv:
        research_orientation, count, percent

    method_orientation_counts.csv:
        method_orientation, count, percent

输出文件：
    1. NSFC_heritage_orientation_distribution_EN.png
    2. NSFC_heritage_orientation_distribution_EN.svg
    3. NSFC_heritage_orientation_distribution_EN.pdf
    4. NSFC_heritage_variable_mapping_EN.csv
    5. NSFC_heritage_orientation_long_table_EN.csv

说明：
    图中所有文字为英文，用于英文期刊投稿。
    代码注释为中文，便于后续修改。
    字体强制使用 Arial。
    横轴从 0 开始，左侧维度标签不再占用负数坐标空间。
    PDF 以 600 dpi 保存；PDF 本身为矢量格式，dpi 主要影响其中可能存在的位图元素。
"""

import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.transforms import blended_transform_factory


# ============================================================
# 1. 路径配置区
# ============================================================

# 修改为你的数据所在文件夹
INPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "inputs" / "fig3_overall_agenda_structure"

# 输出目录
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "reproduced" / "dimension_distributions"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 输入文件
heritage_file = INPUT_DIR / "heritage_object_counts.csv"
research_file = INPUT_DIR / "research_orientation_counts.csv"
method_file = INPUT_DIR / "method_orientation_counts.csv"

# 输出文件
output_png = OUTPUT_DIR / "NSFC_heritage_orientation_distribution_EN.png"
output_svg = OUTPUT_DIR / "NSFC_heritage_orientation_distribution_EN.svg"
output_pdf = OUTPUT_DIR / "NSFC_heritage_orientation_distribution_EN.pdf"

output_mapping_csv = OUTPUT_DIR / "NSFC_heritage_variable_mapping_EN.csv"
output_long_csv = OUTPUT_DIR / "NSFC_heritage_orientation_long_table_EN.csv"


# ============================================================
# 2. 绘图高度自定义配置区
# ============================================================

PLOT_CONFIG = {
    # ---------- 图像尺寸 ----------
    "figure_width": 12.4,
    "figure_height": 7.8,
    "figure_dpi": 300,
    "output_dpi": 600,

    # ---------- 标题控制 ----------
    # 英文期刊正文图件一般可设置为 False，把标题放入 figure caption
    "show_title": False,
    "title": "Distribution of Heritage Objects, Research Orientations, and Methodological Orientations",
    "title_fontsize": 14.2,
    "title_weight": "bold",
    "title_pad": 18,

    # ---------- 坐标轴控制 ----------
    "x_label": "Number of projects",
    "x_label_fontsize": 15,
    "x_label_pad": 8,
    "x_label_weight": "bold",
    "x_tick_fontsize": 12,

    "y_tick_fontsize": 10.2,
    "y_tick_weight": "bold",

    # y 轴分类标签与绘图区之间的距离
    # 数值越小，分类标签越靠近绘图区
    "y_tick_pad": 6,

    # ---------- 分类标签控制 ----------
    "wrap_category_label": True,
    "category_label_wrap_width": 30,

    # ---------- 数值标签控制 ----------
    "show_value_label": True,
    "show_percent_in_value_label": True,
    "value_label_fontsize": 13,
    "value_label_x_offset": 0.8,
    "value_label_color": "#222222",
    "value_label_fontweight": "bold",
    "percent_decimal": 1,

    # ---------- 分区标签控制 ----------
    "show_dimension_label": True,

    # 维度标签使用坐标轴相对位置，而不是数据坐标。
    # 0 表示绘图区最左边界，负数表示在绘图区左侧。
    # 数值越接近 0，维度标签越靠近绘图区；
    # 数值越小，例如 -0.22，维度标签越靠左。
    "dimension_label_axes_x": -0.22,
    "dimension_label_fontsize": 15,
    "dimension_label_weight": "bold",
    "dimension_label_rotation": 90,

    # ---------- 分区标签上下位置微调 ----------
    # 在当前 invert_y_axis=True 的情况下：
    # 负值 = 标签向上移动
    # 正值 = 标签向下移动
    "dimension_label_y_offset": {
        "Heritage object": -0.4,
        "Research orientation": -0.2,
        "Methodological orientation": 2,
    },

    # ---------- 行距与分区间距控制 ----------
    # row_gap 控制同一维度内部类别之间的纵向距离
    # group_gap 控制三个大分区之间的距离
    "row_gap": 2,
    "group_gap": 1.48,

    # ---------- 排序控制 ----------
    # True：每个维度内部按照项目数从小到大排列。
    # 由于后面设置 invert_y_axis=True，因此每组最大值会显示在该组底部。
    # False：保留原始 CSV 文件顺序。
    "sort_within_group": True,

    # ---------- 横轴范围控制 ----------
    # 这里将横轴固定从 0 开始，避免左侧出现负值坐标。
    "x_min": 0,
    "x_max": None,
    "x_right_padding": 13,

    # ---------- 是否反转 y 轴 ----------
    # True：第一组 Heritage object 显示在图的上方。
    "invert_y_axis": True,

    # ---------- 是否显示网格 ----------
    "show_x_grid": True,

    # ---------- 是否显示图例 ----------
    # 当前左侧已有分区标签，一般不需要图例。
    "show_legend": False,

    # ---------- 页面边距控制 ----------
    # 这些参数比 tight_layout 更适合精细控制期刊图件。
    # 如果左侧标签被裁切，增大 left_margin，例如 0.23 或 0.25。
    # 如果左侧空间太宽，减小 left_margin，例如 0.19 或 0.20。
    "left_margin": 0.21,
    "right_margin": 1.02,
    "top_margin": 0.99,
    "bottom_margin": 0.10,

    # ---------- 保存控制 ----------
    "save_png": True,
    "save_svg": True,
    "save_pdf": True,
    "show_plot": True,
}


STYLE_CONFIG = {
    # ---------- 字体控制 ----------
    "font_family": "Arial",

    # ---------- 三个维度的颜色 ----------
    "dimension_color": {
        "Heritage object": "#89B2F4",
        "Research orientation": "#018C94",
        "Methodological orientation": "#764D9C",
    },

    # ---------- 棒棒糖线条控制 ----------
    "line_width": 3,
    "line_alpha": 0.45,

    # ---------- 圆点控制 ----------
    "point_size": 85,
    "point_edgecolor": "white",
    "point_linewidth": 0.8,

    # ---------- 分隔线控制 ----------
    "separator_color": "#BFBFBF",
    "separator_width": 0.8,
    "separator_alpha": 0.3,

    # ---------- 网格线控制 ----------
    "grid_color": "#D9D9D9",
    "grid_width": 0.8,
    "grid_alpha": 0.7,

    # ---------- 坐标轴边框控制 ----------
    "bottom_spine_color": "#333333",
    "bottom_spine_width": 0.8,

    # ---------- 背景色 ----------
    "figure_facecolor": "white",
    "save_facecolor": "white",
}


# ============================================================
# 3. 英文映射表配置区
# ============================================================

# 3.1 维度名称映射
dimension_mapping = {
    "heritage_object": "Heritage object",
    "research_orientation": "Research orientation",
    "method_orientation": "Methodological orientation",
}

# 3.2 列名映射
column_mapping = {
    "count": "Number of projects",
    "percent": "Percentage",
}

# 3.3 遗产对象映射
heritage_object_mapping = {
    "建筑遗产": "Architectural heritage",
    "工业遗产": "Industrial heritage",
    "文化景观与线性遗产": "Cultural landscapes and linear heritage",
    "综合": "Integrated",
    "乡村与农业遗产": "Rural and agricultural heritage",
    "自然遗产": "Natural heritage",
    "非物质与活态遗产": "Intangible and living heritage",
    "考古遗产": "Archaeological heritage",
}

# 3.4 问题取向映射
research_orientation_mapping = {
    "治理参与": "Governance and participation",
    "价值识别": "Value identification",
    "活化再生": "Revitalization and regeneration",
    "保护监测": "Conservation and monitoring",
    "数字记录": "Digital documentation",
    "综合": "Integrated",
    "风险韧性": "Risk and resilience",
}

# 3.5 方法取向映射
method_orientation_mapping = {
    "混合方法": "Mixed methods",
    "模型评价": "Model-based evaluation",
    "空间分析": "Spatial analysis",
    "历史档案": "Historical archives",
    "数字建模": "Digital modeling",
    "社会调查": "Social survey",
    "实验检测": "Experimental testing",
    "智能计算": "Intelligent computing",
}


# ============================================================
# 4. 字体设置函数
# ============================================================

def require_arial_font(font_name="Arial"):
    """
    强制使用 Arial 字体。

    如果本机没有安装 Arial，代码会直接停止。
    这样可以避免 Matplotlib 自动替换字体后导致论文图件字体不统一。
    """
    available_fonts = {f.name for f in fm.fontManager.ttflist}

    if font_name not in available_fonts:
        raise RuntimeError(
            f"未检测到 {font_name} 字体。请先在本机安装 Arial 字体，"
            f"或确认 Matplotlib 可以正确识别该字体。"
        )

    plt.rcParams["font.family"] = font_name
    plt.rcParams["font.sans-serif"] = [font_name]
    plt.rcParams["axes.unicode_minus"] = False

    # SVG 中保留可编辑文本，而不是把文字转成路径
    plt.rcParams["svg.fonttype"] = "none"

    # PDF / PS 中尽量保留可编辑字体
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42


require_arial_font(STYLE_CONFIG["font_family"])


# ============================================================
# 5. 数据读取函数
# ============================================================

def read_csv_safely(path):
    """
    安全读取 CSV 文件。

    默认使用 utf-8-sig 编码，可以兼容 Excel 导出的带 BOM 的 CSV 文件。
    """
    if not path.exists():
        raise FileNotFoundError(f"未找到文件：{path}")

    return pd.read_csv(path, encoding="utf-8-sig")


heritage_df = read_csv_safely(heritage_file)
research_df = read_csv_safely(research_file)
method_df = read_csv_safely(method_file)


# ============================================================
# 6. 数据标准化函数
# ============================================================

def standardize_table(
    df,
    source_column,
    dimension_variable,
    dimension_en,
    category_mapping
):
    """
    将单个统计表转换成长表格式。

    输入表结构示例：
        heritage_object, count, percent

    输出表结构：
        dimension_variable
        dimension_en
        category_cn
        category_en
        count
        percent
    """
    required_cols = {source_column, "count", "percent"}
    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        raise ValueError(
            f"{source_column} 表缺少必要列：{missing_cols}"
        )

    out = df.copy()

    # 清洗分类名称，去除换行符和前后空格
    out[source_column] = (
        out[source_column]
        .astype(str)
        .str.replace("\n", "", regex=False)
        .str.strip()
    )

    out["dimension_variable"] = dimension_variable
    out["dimension_en"] = dimension_en
    out["category_cn"] = out[source_column]
    out["category_en"] = out["category_cn"].map(category_mapping)

    # 检查是否存在没有英文映射的中文类别
    missing_mapping = out.loc[
        out["category_en"].isna(),
        "category_cn"
    ].unique()

    if len(missing_mapping) > 0:
        raise ValueError(
            f"{source_column} 中存在未配置英文映射的类别：{missing_mapping}"
        )

    out = out[
        [
            "dimension_variable",
            "dimension_en",
            "category_cn",
            "category_en",
            "count",
            "percent",
        ]
    ]

    return out


# ============================================================
# 7. 合并三个数据表
# ============================================================

plot_df = pd.concat(
    [
        standardize_table(
            heritage_df,
            source_column="heritage_object",
            dimension_variable="heritage_object",
            dimension_en="Heritage object",
            category_mapping=heritage_object_mapping,
        ),
        standardize_table(
            research_df,
            source_column="research_orientation",
            dimension_variable="research_orientation",
            dimension_en="Research orientation",
            category_mapping=research_orientation_mapping,
        ),
        standardize_table(
            method_df,
            source_column="method_orientation",
            dimension_variable="method_orientation",
            dimension_en="Methodological orientation",
            category_mapping=method_orientation_mapping,
        ),
    ],
    ignore_index=True,
)

plot_df["count"] = plot_df["count"].astype(int)
plot_df["percent"] = plot_df["percent"].astype(float)


# ============================================================
# 8. 导出英文映射表和长表
# ============================================================

mapping_records = []

# 维度级映射
for variable_name, variable_en in dimension_mapping.items():
    mapping_records.append(
        {
            "mapping_level": "dimension",
            "variable_name": variable_name,
            "chinese_label": variable_name,
            "english_label": variable_en,
        }
    )

# 列名级映射
for variable_name, variable_en in column_mapping.items():
    mapping_records.append(
        {
            "mapping_level": "column",
            "variable_name": variable_name,
            "chinese_label": variable_name,
            "english_label": variable_en,
        }
    )

# 类别级映射：遗产对象
for cn, en in heritage_object_mapping.items():
    mapping_records.append(
        {
            "mapping_level": "category",
            "variable_name": "heritage_object",
            "chinese_label": cn,
            "english_label": en,
        }
    )

# 类别级映射：问题取向
for cn, en in research_orientation_mapping.items():
    mapping_records.append(
        {
            "mapping_level": "category",
            "variable_name": "research_orientation",
            "chinese_label": cn,
            "english_label": en,
        }
    )

# 类别级映射：方法取向
for cn, en in method_orientation_mapping.items():
    mapping_records.append(
        {
            "mapping_level": "category",
            "variable_name": "method_orientation",
            "chinese_label": cn,
            "english_label": en,
        }
    )

mapping_df = pd.DataFrame(mapping_records)

mapping_df.to_csv(
    output_mapping_csv,
    index=False,
    encoding="utf-8-sig"
)

plot_df.to_csv(
    output_long_csv,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 9. 构造绘图坐标
# ============================================================

dimension_order = [
    "Heritage object",
    "Research orientation",
    "Methodological orientation",
]

dimension_color = STYLE_CONFIG["dimension_color"]


def wrap_label(label, width=30):
    """
    对过长的英文分类标签进行换行处理。

    width 越小，换行越频繁；
    width 越大，标签越接近单行显示。
    """
    return "\n".join(textwrap.wrap(label, width=width))


y_positions = []
labels = []
values = []
percents = []
groups = []
colors = []

gap = PLOT_CONFIG["group_gap"]
row_gap = PLOT_CONFIG["row_gap"]
y = 0

for dim in dimension_order:
    sub = plot_df.loc[plot_df["dimension_en"] == dim].copy()

    if PLOT_CONFIG["sort_within_group"]:
        sub = sub.sort_values("count", ascending=True)

    for _, row in sub.iterrows():
        y_positions.append(y)

        if PLOT_CONFIG["wrap_category_label"]:
            label = wrap_label(
                row["category_en"],
                width=PLOT_CONFIG["category_label_wrap_width"]
            )
        else:
            label = row["category_en"]

        labels.append(label)
        values.append(row["count"])
        percents.append(row["percent"])
        groups.append(dim)
        colors.append(dimension_color[dim])

        y += row_gap

    y += gap


# ============================================================
# 10. 绘制综合分区棒棒糖图
# ============================================================

fig, ax = plt.subplots(
    figsize=(PLOT_CONFIG["figure_width"], PLOT_CONFIG["figure_height"]),
    dpi=PLOT_CONFIG["figure_dpi"],
    facecolor=STYLE_CONFIG["figure_facecolor"]
)

# 绘制棒棒糖横线
for yi, val, color in zip(y_positions, values, colors):
    ax.hlines(
        y=yi,
        xmin=0,
        xmax=val,
        color=color,
        linewidth=STYLE_CONFIG["line_width"],
        alpha=STYLE_CONFIG["line_alpha"],
    )

# 绘制棒棒糖圆点
ax.scatter(
    values,
    y_positions,
    s=STYLE_CONFIG["point_size"],
    color=colors,
    edgecolor=STYLE_CONFIG["point_edgecolor"],
    linewidth=STYLE_CONFIG["point_linewidth"],
    zorder=3,
)

# 添加数值标签
if PLOT_CONFIG["show_value_label"]:
    for yi, val, pct in zip(y_positions, values, percents):

        if PLOT_CONFIG["show_percent_in_value_label"]:
            label_text = f"{val} ({pct:.{PLOT_CONFIG['percent_decimal']}f}%)"
        else:
            label_text = f"{val}"

        ax.text(
            val + PLOT_CONFIG["value_label_x_offset"],
            yi,
            label_text,
            va="center",
            ha="left",
            fontsize=PLOT_CONFIG["value_label_fontsize"],
            fontweight=PLOT_CONFIG["value_label_fontweight"],
            color=PLOT_CONFIG["value_label_color"],
        )

# 设置 y 轴分类标签
ax.set_yticks(y_positions)
ax.set_yticklabels(
    labels,
    fontsize=PLOT_CONFIG["y_tick_fontsize"]
)

# 控制 y 轴类别标签字重
for label in ax.get_yticklabels():
    label.set_fontweight(PLOT_CONFIG["y_tick_weight"])

# 设置 x 轴标题
ax.set_xlabel(
    PLOT_CONFIG["x_label"],
    fontsize=PLOT_CONFIG["x_label_fontsize"],
    fontweight=PLOT_CONFIG["x_label_weight"],
    labelpad=PLOT_CONFIG["x_label_pad"]
)

# 设置主标题
if PLOT_CONFIG["show_title"]:
    ax.set_title(
        PLOT_CONFIG["title"],
        fontsize=PLOT_CONFIG["title_fontsize"],
        pad=PLOT_CONFIG["title_pad"],
        weight=PLOT_CONFIG["title_weight"],
    )


# ============================================================
# 11. 添加左侧分区标签
# ============================================================

# x 使用坐标轴相对位置，y 使用数据坐标。
# 这样横轴可以从 0 开始，同时维度标签仍然可以放在绘图区左侧。
if PLOT_CONFIG["show_dimension_label"]:
    dimension_label_transform = blended_transform_factory(
        ax.transAxes,
        ax.transData
    )

    for dim in dimension_order:
        ys = [
            yp
            for yp, g in zip(y_positions, groups)
            if g == dim
        ]

        label_y = (
            np.mean(ys)
            + PLOT_CONFIG["dimension_label_y_offset"][dim]
        )

        ax.text(
            PLOT_CONFIG["dimension_label_axes_x"],
            label_y,
            dim,
            transform=dimension_label_transform,
            va="center",
            ha="center",
            fontsize=PLOT_CONFIG["dimension_label_fontsize"],
            weight=PLOT_CONFIG["dimension_label_weight"],
            rotation=PLOT_CONFIG["dimension_label_rotation"],
            color=dimension_color[dim],
            clip_on=False,
        )


# ============================================================
# 12. 添加分区分隔线
# ============================================================

for i in range(len(y_positions) - 1):
    if groups[i] != groups[i + 1]:
        sep_y = (y_positions[i] + y_positions[i + 1]) / 2

        ax.axhline(
            y=sep_y,
            color=STYLE_CONFIG["separator_color"],
            linewidth=STYLE_CONFIG["separator_width"],
            alpha=STYLE_CONFIG["separator_alpha"],
        )


# ============================================================
# 13. 设置横轴范围
# ============================================================

# 横轴从 0 开始，不再为左侧维度标签预留负值空间
max_value = max(values)

x_min = PLOT_CONFIG["x_min"]

x_max = (
    PLOT_CONFIG["x_max"]
    if PLOT_CONFIG["x_max"] is not None
    else max_value + PLOT_CONFIG["x_right_padding"]
)

ax.set_xlim(x_min, x_max)


# ============================================================
# 14. 网格线与坐标轴样式
# ============================================================

# 添加 x 轴网格线
if PLOT_CONFIG["show_x_grid"]:
    ax.grid(
        axis="x",
        color=STYLE_CONFIG["grid_color"],
        linewidth=STYLE_CONFIG["grid_width"],
        alpha=STYLE_CONFIG["grid_alpha"],
    )
    ax.set_axisbelow(True)

# 控制坐标轴边框
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

ax.spines["bottom"].set_color(STYLE_CONFIG["bottom_spine_color"])
ax.spines["bottom"].set_linewidth(STYLE_CONFIG["bottom_spine_width"])

# 控制刻度样式
ax.tick_params(
    axis="y",
    length=0,
    pad=PLOT_CONFIG["y_tick_pad"]
)

ax.tick_params(
    axis="x",
    labelsize=PLOT_CONFIG["x_tick_fontsize"],
    colors="#333333"
)

# 是否反转 y 轴
if PLOT_CONFIG["invert_y_axis"]:
    ax.invert_yaxis()


# ============================================================
# 15. 图例控制
# ============================================================

if PLOT_CONFIG["show_legend"]:
    legend_handles = []

    for dim in dimension_order:
        handle = plt.Line2D(
            [0],
            [0],
            marker="o",
            color=dimension_color[dim],
            label=dim,
            markerfacecolor=dimension_color[dim],
            markersize=7,
            linewidth=2,
        )
        legend_handles.append(handle)

    ax.legend(
        handles=legend_handles,
        frameon=False,
        loc="lower right",
        fontsize=10
    )


# ============================================================
# 16. 手动控制图形边距
# ============================================================

# 不使用 tight_layout，因为 tight_layout 容易重新压缩左侧标签空间。
# 这里用 subplots_adjust 手动控制，更适合论文图件微调。
fig.subplots_adjust(
    left=PLOT_CONFIG["left_margin"],
    right=PLOT_CONFIG["right_margin"],
    top=PLOT_CONFIG["top_margin"],
    bottom=PLOT_CONFIG["bottom_margin"],
)


# ============================================================
# 17. 保存图片
# ============================================================

if PLOT_CONFIG["save_png"]:
    fig.savefig(
        output_png,
        dpi=PLOT_CONFIG["output_dpi"],
        bbox_inches="tight",
        facecolor=STYLE_CONFIG["save_facecolor"],
    )

if PLOT_CONFIG["save_svg"]:
    fig.savefig(
        output_svg,
        bbox_inches="tight",
        facecolor=STYLE_CONFIG["save_facecolor"],
    )

if PLOT_CONFIG["save_pdf"]:
    fig.savefig(
        output_pdf,
        dpi=PLOT_CONFIG["output_dpi"],
        bbox_inches="tight",
        facecolor=STYLE_CONFIG["save_facecolor"],
    )

if PLOT_CONFIG["show_plot"]:
    plt.show()
else:
    plt.close(fig)


# ============================================================
# 18. 输出运行结果
# ============================================================

print(f"PNG saved to: {output_png}")
print(f"SVG saved to: {output_svg}")
print(f"PDF saved to: {output_pdf}")
print(f"Mapping table saved to: {output_mapping_csv}")
print(f"Long-format English table saved to: {output_long_csv}")