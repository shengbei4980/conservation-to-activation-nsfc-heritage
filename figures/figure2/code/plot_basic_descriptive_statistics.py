# -*- coding: utf-8 -*-
"""
Compact scientific bar charts for NSFC-funded heritage research projects.

功能说明：
1. 生成“小图式”科研制图风格的竖直柱状图：
   - Project type distribution
   - Application / discipline code distribution

2. 输出三类图：
   - 上下排列合并图
   - Project type 单图
   - Application code 单图

3. 本版本关键修整：
   - 取消合并图中的 a / b 面板编号
   - Application code 的 x 轴只显示 NSFC 代码，例如 E08、D01、C16
   - Application code 的完整英文学科名称放在图下方的简单文字图例中
   - 不再使用表格型图例
   - 加大 x 轴、y 轴、标题、柱顶数字字号
   - 保留科研小图风格：封闭坐标框、浅网格、低饱和统一柱色
   - 输出 PNG / PDF / SVG，便于论文、PPT、AI 后期编辑

4. NSFC 申请代码中英映射：
   E08 建筑与土木工程 -> Architecture and Civil Engineering
   D01 地理科学 -> Geography
   C16 林学与草学 -> Forestry and Grassland Science
   G04 宏观管理与政策 -> Macro-Management and Policy
   G03 经济科学 -> Economic Sciences
   D07 环境地球科学 -> Environmental Geosciences
   F02 计算机科学 -> Computer Science
   C03 生态学 -> Ecology

输入文件要求：
1. project_type_counts.csv
   至少包含列：
   project_type, count, percent

2. discipline_code_counts.csv
   至少包含列：
   discipline_code, count, percent
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
import shutil
import textwrap
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager as fm
from matplotlib.ticker import MaxNLocator


# ============================================================
# 一、路径配置
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = ROOT / "data" / "inputs"
OUTPUT_DIR = ROOT / "outputs" / "reproduced" / "descriptive_statistics"
FIG_DIR = OUTPUT_DIR / "figures"
SRC_DIR = OUTPUT_DIR / "source_data"

PROJECT_TYPE_FILE = INPUT_DIR / "project_type_counts.csv"
DISCIPLINE_CODE_FILE = INPUT_DIR / "discipline_code_counts.csv"

OUTPUT_STEM_COMBINED = "NSFC_heritage_basic_descriptive_statistics_compact_EN"
OUTPUT_STEM_PROJECT_TYPE = "NSFC_heritage_project_type_compact_EN"
OUTPUT_STEM_DISCIPLINE_CODE = "NSFC_heritage_application_code_compact_EN"


# ============================================================
# 二、科研小图风格参数
# ============================================================

PLOT_CONFIG: dict[str, Any] = {
    # --------------------------------------------------------
    # 字体设置
    # --------------------------------------------------------
    # 英文论文图推荐 Arial。
    # 想更接近部分期刊的 serif 风格，可改为 "Times New Roman"。
    # 使用中文标签时，建议改为 "Microsoft YaHei" 或 "SimHei"。
    "font_family": "Arial",

    # True：找不到指定字体则报错。
    # False：找不到指定字体时继续运行。
    "strict_font": False,

    # --------------------------------------------------------
    # 输出设置
    # --------------------------------------------------------
    "figure_dpi": 300,
    "output_dpi": 600,
    "background": "white",

    "save_png": True,
    "save_pdf": True,
    "save_svg": True,

    # --------------------------------------------------------
    # 图尺寸
    # --------------------------------------------------------
    # 合并图：上下两个 compact panels。
    # 下方需要容纳 Application-code mapping，因此合并图高度适当增加。
    "combined_figure_width": 7.2,
    "combined_figure_height": 7.2,

    # Project type 单图
    "single_project_figure_width": 4.4,
    "single_project_figure_height": 3.3,

    # Application code 单图：下方需要容纳简单文字型图例，因此高度适当增加。
    "single_discipline_figure_width": 7.6,
    "single_discipline_figure_height": 4.35,

    # --------------------------------------------------------
    # 柱状图设置
    # --------------------------------------------------------
    "bar_width": 0.58,
    "bar_alpha": 0.95,
    "bar_linewidth": 0.55,

    # --------------------------------------------------------
    # 坐标轴范围
    # --------------------------------------------------------
    # 柱顶预留空间，避免数值标签顶到边框。
    "y_upper_ratio": 1.20,

    # 合并图是否使用统一 y 轴。
    # True：两个 panel 共享上限，便于比较。
    # False：每个 panel 自适应，更紧凑。
    "use_common_y_axis_for_combined": False,

    # 柱顶数值标签与柱子的距离。
    "value_label_gap_ratio": 0.018,

    # --------------------------------------------------------
    # 文字大小
    # --------------------------------------------------------
    "title_fontsize": 13.0,
    "axis_label_fontsize": 12.0,

    # 分开控制 x 轴和 y 轴字号。
    "x_tick_fontsize": 11.0,
    "y_tick_fontsize": 11.0,

    "value_fontsize": 10.5,

    "title_fontweight": "bold",
    "axis_label_fontweight": "bold",
    "tick_fontweight": "normal",
    "value_fontweight": "normal",

    # y 轴标题。
    "y_label": "Projects",

    # --------------------------------------------------------
    # 标签模式
    # --------------------------------------------------------
    # Project type 标签：
    # "short" -> Young Sci. Fund / General / Regional / Key
    # "full"  -> Young Scientists Fund / General Program 等
    "project_label_mode": "short",

    # Discipline code 标签：
    # 此处推荐 code_only，因为完整名称放在下方简单文字图例中。
    # 可选：
    # "code_only"         -> E08
    # "code_en_short"     -> E08 + 简短英文映射
    # "code_en_multiline" -> E08 + 完整英文映射
    "discipline_label_mode_for_plot": "code_only",

    # 标签换行宽度。
    "project_label_wrap_width": 12,
    "discipline_label_wrap_width": 14,

    # x 轴标签旋转角度。
    "x_tick_rotation": 0,
    "x_tick_ha": "center",

    # --------------------------------------------------------
    # 坐标轴与网格
    # --------------------------------------------------------
    "y_axis_integer": True,
    "show_y_grid": True,
    "y_grid_color": "#D7DDE2",
    "y_grid_alpha": 0.35,
    "y_grid_linewidth": 0.45,
    "y_grid_linestyle": "--",

    # 是否显示封闭坐标框。
    # True：类似示例图，小图四周都有边框。
    "boxed_axes": True,

    "spine_color": "#333333",
    "spine_linewidth": 0.75,

    # 刻度线设置
    "tick_direction": "out",
    "tick_length": 3.0,
    "tick_width": 0.70,

    # --------------------------------------------------------
    # 数值标签
    # --------------------------------------------------------
    "show_value_labels": True,

    # 可选：
    # "count"         -> 66
    # "percent"       -> 46.5%
    # "count_percent" -> 66 (46.5%)
    #
    # 小图建议 count，更干净。
    "value_label_mode": "count",
    "percent_decimals": 1,

    # --------------------------------------------------------
    # 面板编号
    # --------------------------------------------------------
    # 取消 a / b 显示。
    "show_panel_label": False,

    # 保留参数，但默认不使用。
    "panel_label_x": -0.16,
    "panel_label_y": 1.08,
    "panel_label_fontsize": 12.0,

    # --------------------------------------------------------
    # 标题位置
    # --------------------------------------------------------
    "title_pad": 9,

    # --------------------------------------------------------
    # 合并图布局
    # --------------------------------------------------------
    # combined_bottom 需要给下方简单文字图例预留空间。
    "combined_left": 0.13,
    "combined_right": 0.985,
    "combined_top": 0.93,
    "combined_bottom": 0.24,
    "combined_hspace": 0.72,

    # --------------------------------------------------------
    # 单图布局
    # --------------------------------------------------------
    "single_left": 0.17,
    "single_right": 0.975,
    "single_top": 0.82,
    "single_bottom_project": 0.23,

    # Application code 单图下方需要简单文字图例，因此 bottom 稍大。
    "single_bottom_discipline": 0.40,

    # --------------------------------------------------------
    # Application-code simple legend 设置
    # --------------------------------------------------------
    "show_discipline_legend": True,
    "discipline_legend_title": "Application-code mapping",

    # 简单文字图例字号
    "discipline_legend_title_fontsize": 10.5,
    "discipline_legend_fontsize": 9.2,

    # 图例标题位置，相对于 Application code 坐标轴。
    "discipline_legend_title_x": 0.015,
    "discipline_legend_title_y": -0.20,

    # 左右两列图例的位置，相对于 Application code 坐标轴。
    "discipline_legend_left_x": 0.015,
    "discipline_legend_right_x": 0.53,
    "discipline_legend_text_y": -0.31,

    # 图例中学科英文名称自动换行宽度。
    "discipline_legend_wrap_width": 36,

    # 图例列数：
    # 1 -> 单列
    # 2 -> 左右两列
    "discipline_legend_columns": 2,

    # 行距
    "discipline_legend_linespacing": 1.25,
}


# ============================================================
# 三、颜色系统
# ============================================================

STYLE_CONFIG: dict[str, str] = {
    # --------------------------------------------------------
    # 统一主色
    # --------------------------------------------------------
    # 这是最主要的柱子颜色。
    # 可替换：
    # "#0F6B6E" 深青绿
    # "#B0B9B7" 灰绿色
    # "#8AA6A3" 低饱和青灰
    # "#4E79A7" 学术蓝
    "bar_color": "#8AA6A3",

    # 柱子边框色
    "bar_edgecolor": "#2F3B3A",

    # 文字颜色
    "text_color": "#1F1F1F",
    "muted_text_color": "#2F2F2F",

    # 面板编号颜色；当前 show_panel_label=False，所以不显示。
    "panel_label_color": "#111111",

    # 背景
    "background": "white",
}


# ============================================================
# 四、排序设置
# ============================================================

SORT_CONFIG: dict[str, str] = {
    # 可选：
    # "count_descending" -> 从高到低
    # "count_ascending"  -> 从低到高
    # "fixed_order"      -> 使用映射表中的固定顺序
    "project_type_sort_mode": "count_descending",
    "discipline_code_sort_mode": "count_descending",
}


# ============================================================
# 五、项目类型英文映射
# ============================================================

PROJECT_TYPE_META: dict[str, dict[str, str]] = {
    "青年科学基金项目": {
        "en": "Young Scientists Fund",
        "short": "Young Sci.\nFund",
    },
    "面上项目": {
        "en": "General Program",
        "short": "General",
    },
    "地区科学基金项目": {
        "en": "Regional Science Fund",
        "short": "Regional",
    },
    "重点项目": {
        "en": "Key Program",
        "short": "Key",
    },
}


# ============================================================
# 六、NSFC 申请代码中英映射
# ============================================================

DISCIPLINE_CODE_META = OrderedDict(
    [
        (
            "E08",
            {
                "zh": "建筑与土木工程",
                "en": "Architecture and Civil Engineering",
                "short": "Arch. & Civil Eng.",
                "en_nsfc_code_list": "Architecture and civil engineering",
            },
        ),
        (
            "D01",
            {
                "zh": "地理科学",
                "en": "Geography",
                "short": "Geography",
                "en_nsfc_code_list": "Geography",
            },
        ),
        (
            "C16",
            {
                "zh": "林学与草学",
                "en": "Forestry and Grassland Science",
                "short": "Forestry & Grassland",
                "en_nsfc_code_list": "Forestry and Grass Science",
            },
        ),
        (
            "G04",
            {
                "zh": "宏观管理与政策",
                "en": "Macro-Management and Policy",
                "short": "Macro-Mgmt. & Policy",
                "en_nsfc_code_list": "Macro-management and Policy",
            },
        ),
        (
            "G03",
            {
                "zh": "经济科学",
                "en": "Economic Sciences",
                "short": "Economic Sci.",
                "en_nsfc_code_list": "Economic Sciences",
            },
        ),
        (
            "D07",
            {
                "zh": "环境地球科学",
                "en": "Environmental Geosciences",
                "short": "Environ. Geosci.",
                "en_nsfc_code_list": "Environmental Geosciences",
            },
        ),
        (
            "F02",
            {
                "zh": "计算机科学",
                "en": "Computer Science",
                "short": "Computer Sci.",
                "en_nsfc_code_list": "Computer Science",
            },
        ),
        (
            "C03",
            {
                "zh": "生态学",
                "en": "Ecology",
                "short": "Ecology",
                "en_nsfc_code_list": "Ecology",
            },
        ),
    ]
)


DISCIPLINE_LABEL_CONFIG: dict[str, Any] = {
    # "publication"：推荐用于论文图表。
    # "nsfc_code_list"：更接近 NSFC 英文申请代码列表写法。
    "translation_variant": "publication",

    # 是否打印映射表。
    "print_mapping_table": True,

    # 是否保存映射表。
    "save_mapping_table": True,
}


# ============================================================
# 七、字体与全局样式
# ============================================================

def require_font() -> None:
    """检查并设置 Matplotlib 字体。"""
    available_fonts = {font.name for font in fm.fontManager.ttflist}
    font_name = PLOT_CONFIG["font_family"]

    if PLOT_CONFIG["strict_font"] and font_name not in available_fonts:
        raise RuntimeError(
            f"{font_name} was not detected by Matplotlib. "
            f"请安装 {font_name}，或将 PLOT_CONFIG['strict_font'] 设置为 False。"
        )

    mpl.rcParams.update(
        {
            "font.family": font_name,
            "font.sans-serif": [font_name],
            "axes.unicode_minus": False,

            # 矢量图字体设置，便于 AI / Inkscape / Illustrator 后期编辑。
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,

            # 统一背景。
            "figure.facecolor": PLOT_CONFIG["background"],
            "axes.facecolor": PLOT_CONFIG["background"],
            "savefig.facecolor": PLOT_CONFIG["background"],
        }
    )


# ============================================================
# 八、文本与标签函数
# ============================================================

def wrap_text(text: str, width: int) -> str:
    """英文标签自动换行。"""
    text = str(text)

    if not text:
        return text

    return "\n".join(
        textwrap.wrap(
            text,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def wrap_multiline_text(text: str, width: int) -> str:
    """保留已有换行，并对每一行再次换行。"""
    return "\n".join(wrap_text(part, width) for part in str(text).split("\n"))


def format_value_label(count: int, percent: float) -> str:
    """格式化柱顶数值标签。"""
    mode = PLOT_CONFIG["value_label_mode"]
    decimals = PLOT_CONFIG["percent_decimals"]

    if mode == "percent":
        return f"{percent:.{decimals}f}%"

    if mode == "count_percent":
        return f"{count}\n({percent:.{decimals}f}%)"

    return f"{count}"


# ============================================================
# 九、项目类型标签函数
# ============================================================

def get_project_type_en(project_type: str) -> str:
    """返回项目类型英文全称。"""
    project_type = str(project_type).strip()
    return PROJECT_TYPE_META.get(project_type, {}).get("en", project_type)


def get_project_type_short(project_type: str) -> str:
    """返回项目类型短标签，适合小图。"""
    project_type = str(project_type).strip()
    return PROJECT_TYPE_META.get(project_type, {}).get("short", project_type)


def build_project_type_plot_label(project_type: str) -> str:
    """根据配置生成项目类型图上标签。"""
    if PLOT_CONFIG["project_label_mode"] == "full":
        return get_project_type_en(project_type)

    return get_project_type_short(project_type)


# ============================================================
# 十、NSFC 学科代码标签函数
# ============================================================

def get_discipline_en(code: str) -> str:
    """根据 NSFC 代码返回英文名称。"""
    code = str(code).strip()

    if code not in DISCIPLINE_CODE_META:
        return code

    variant = DISCIPLINE_LABEL_CONFIG["translation_variant"]

    if variant == "nsfc_code_list":
        return DISCIPLINE_CODE_META[code]["en_nsfc_code_list"]

    return DISCIPLINE_CODE_META[code]["en"]


def get_discipline_zh(code: str) -> str:
    """根据 NSFC 代码返回中文名称。"""
    code = str(code).strip()

    if code not in DISCIPLINE_CODE_META:
        return code

    return DISCIPLINE_CODE_META[code]["zh"]


def get_discipline_short(code: str) -> str:
    """根据 NSFC 代码返回适合小图显示的英文短标签。"""
    code = str(code).strip()

    if code not in DISCIPLINE_CODE_META:
        return code

    return DISCIPLINE_CODE_META[code]["short"]


def build_discipline_plot_label(code: str) -> str:
    """
    生成学科代码图上标签。

    可选模式：
    - code_only：只显示 E08
    - code_en_short：显示 E08 + 简短英文映射
    - code_en_multiline：显示 E08 + 完整英文名称
    """
    code = str(code).strip()

    if code not in DISCIPLINE_CODE_META:
        return code

    mode = PLOT_CONFIG["discipline_label_mode_for_plot"]

    if mode == "code_en_multiline":
        return f"{code}\n{get_discipline_en(code)}"

    if mode == "code_en_short":
        return f"{code}\n{get_discipline_short(code)}"

    return code


def make_discipline_mapping_table() -> pd.DataFrame:
    """生成 NSFC 学科代码中英映射表。"""
    records = []

    for code, meta in DISCIPLINE_CODE_META.items():
        records.append(
            {
                "discipline_code": code,
                "discipline_name_zh": meta["zh"],
                "discipline_name_en": meta["en"],
                "discipline_name_en_short": meta["short"].replace("\n", " "),
                "discipline_name_en_nsfc_code_list": meta["en_nsfc_code_list"],
                "plot_label": build_discipline_plot_label(code).replace("\n", " | "),
            }
        )

    return pd.DataFrame(records)


def print_discipline_mapping_table() -> None:
    """在控制台打印 NSFC 学科代码映射表。"""
    if not DISCIPLINE_LABEL_CONFIG["print_mapping_table"]:
        return

    mapping_df = make_discipline_mapping_table()

    print("\nNSFC discipline-code mapping:")
    print(mapping_df.to_string(index=False))
    print()


def validate_discipline_codes(
    df: pd.DataFrame,
    code_col: str = "discipline_code",
) -> None:
    """检查输入数据中的 NSFC 代码是否都已配置映射。"""
    input_codes = set(df[code_col].astype(str).str.strip())
    mapped_codes = set(DISCIPLINE_CODE_META.keys())
    missing_codes = sorted(input_codes - mapped_codes)

    if missing_codes:
        raise ValueError(
            "以下 NSFC 申请代码尚未配置中英映射，请先补充 DISCIPLINE_CODE_META："
            + ", ".join(missing_codes)
        )


# ============================================================
# 十一、数据读取、排序与保存
# ============================================================

def sort_count_table(df: pd.DataFrame, category_col: str) -> pd.DataFrame:
    """根据配置对数据排序。"""
    if category_col == "project_type":
        sort_mode = SORT_CONFIG["project_type_sort_mode"]
    elif category_col == "discipline_code":
        sort_mode = SORT_CONFIG["discipline_code_sort_mode"]
    else:
        sort_mode = "count_descending"

    if category_col == "discipline_code" and sort_mode == "fixed_order":
        fixed_order = list(DISCIPLINE_CODE_META.keys())
        df["_fixed_order"] = pd.Categorical(
            df[category_col],
            categories=fixed_order,
            ordered=True,
        )
        return (
            df.sort_values("_fixed_order")
            .drop(columns="_fixed_order")
            .reset_index(drop=True)
        )

    if sort_mode == "count_ascending":
        return df.sort_values("count", ascending=True).reset_index(drop=True)

    return df.sort_values("count", ascending=False).reset_index(drop=True)


def load_count_table(
    path: Path,
    category_col: str,
) -> pd.DataFrame:
    """读取计数表并生成绘图标签。"""
    if not path.exists():
        raise FileNotFoundError(f"输入文件不存在：{path}")

    df = pd.read_csv(path, encoding="utf-8-sig")

    required_cols = {category_col, "count", "percent"}
    missing_cols = required_cols - set(df.columns)

    if missing_cols:
        raise ValueError(
            f"{path.name} 缺少必要列：{', '.join(sorted(missing_cols))}"
        )

    df[category_col] = df[category_col].astype(str).str.strip()
    df["count"] = df["count"].astype(int)
    df["percent"] = df["percent"].astype(float)

    if category_col == "project_type":
        df["project_type_en"] = df[category_col].map(get_project_type_en)
        df["project_type_short"] = df[category_col].map(get_project_type_short)
        df["project_type_plot_label"] = df[category_col].map(
            build_project_type_plot_label
        )

    elif category_col == "discipline_code":
        validate_discipline_codes(df, code_col=category_col)

        df["discipline_name_zh"] = df[category_col].map(get_discipline_zh)
        df["discipline_name_en"] = df[category_col].map(get_discipline_en)
        df["discipline_name_en_short"] = df[category_col].map(get_discipline_short)
        df["discipline_code_plot_label"] = df[category_col].map(
            build_discipline_plot_label
        )

        print_discipline_mapping_table()

    df = sort_count_table(df, category_col)
    return df


def save_source_data(project_df: pd.DataFrame, discipline_df: pd.DataFrame) -> None:
    """保存源数据、长表、manifest、原始数据副本和映射表。"""
    project_out = project_df.sort_values("count", ascending=False).copy()
    discipline_out = discipline_df.sort_values("count", ascending=False).copy()

    project_out.to_csv(
        SRC_DIR / "basic_stats_project_type_counts_compact.csv",
        index=False,
        encoding="utf-8-sig",
    )

    discipline_out.to_csv(
        SRC_DIR / "basic_stats_discipline_code_counts_compact.csv",
        index=False,
        encoding="utf-8-sig",
    )

    long_df = pd.concat(
        [
            project_out.rename(
                columns={
                    "project_type": "category",
                    "project_type_en": "category_en",
                    "project_type_plot_label": "plot_label",
                }
            ).assign(panel="Project type", dimension="Project type")[
                [
                    "panel",
                    "dimension",
                    "category",
                    "category_en",
                    "plot_label",
                    "count",
                    "percent",
                ]
            ],
            discipline_out.rename(
                columns={
                    "discipline_code": "category",
                    "discipline_name_en": "category_en",
                    "discipline_code_plot_label": "plot_label",
                }
            ).assign(panel="Application code", dimension="Application code")[
                [
                    "panel",
                    "dimension",
                    "category",
                    "category_en",
                    "plot_label",
                    "count",
                    "percent",
                ]
            ],
        ],
        ignore_index=True,
    )

    long_df.to_csv(
        SRC_DIR / "basic_descriptive_statistics_compact_long_table.csv",
        index=False,
        encoding="utf-8-sig",
    )

    manifest = pd.DataFrame(
        [
            {
                "figure": OUTPUT_STEM_COMBINED,
                "panel": "Project type",
                "description": "Compact vertical bar chart of NSFC project types",
                "source_data": "source_data/basic_stats_project_type_counts_compact.csv",
            },
            {
                "figure": OUTPUT_STEM_COMBINED,
                "panel": "Application code",
                "description": "Compact vertical bar chart of NSFC application codes",
                "source_data": "source_data/basic_stats_discipline_code_counts_compact.csv",
            },
            {
                "figure": OUTPUT_STEM_PROJECT_TYPE,
                "panel": "single",
                "description": "Single compact vertical bar chart of NSFC project types",
                "source_data": "source_data/basic_stats_project_type_counts_compact.csv",
            },
            {
                "figure": OUTPUT_STEM_DISCIPLINE_CODE,
                "panel": "single",
                "description": "Single compact vertical bar chart of NSFC application codes",
                "source_data": "source_data/basic_stats_discipline_code_counts_compact.csv",
            },
        ]
    )

    manifest.to_csv(
        SRC_DIR / "basic_descriptive_statistics_compact_manifest.csv",
        index=False,
        encoding="utf-8-sig",
    )

    if DISCIPLINE_LABEL_CONFIG["save_mapping_table"]:
        make_discipline_mapping_table().to_csv(
            SRC_DIR / "nsfc_discipline_code_mapping_zh_en.csv",
            index=False,
            encoding="utf-8-sig",
        )

    shutil.copy2(PROJECT_TYPE_FILE, SRC_DIR / "raw_project_type_counts.csv")
    shutil.copy2(DISCIPLINE_CODE_FILE, SRC_DIR / "raw_discipline_code_counts.csv")


# ============================================================
# 十二、绘图辅助函数
# ============================================================

def calculate_y_max(df: pd.DataFrame) -> float:
    """计算单图 y 轴上限。"""
    return float(df["count"].max()) * float(PLOT_CONFIG["y_upper_ratio"])


def calculate_common_y_max(
    project_df: pd.DataFrame,
    discipline_df: pd.DataFrame,
) -> float:
    """计算合并图统一 y 轴上限。"""
    max_count = max(
        float(project_df["count"].max()),
        float(discipline_df["count"].max()),
    )
    return max_count * float(PLOT_CONFIG["y_upper_ratio"])


def add_value_labels(
    ax: plt.Axes,
    bars,
    counts: pd.Series,
    percents: pd.Series,
    y_max: float,
) -> None:
    """添加柱顶数值标签。"""
    if not PLOT_CONFIG["show_value_labels"]:
        return

    gap = y_max * float(PLOT_CONFIG["value_label_gap_ratio"])

    for bar, count, percent in zip(bars, counts, percents):
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()

        ax.text(
            x,
            y + gap,
            format_value_label(int(count), float(percent)),
            ha="center",
            va="bottom",
            fontsize=PLOT_CONFIG["value_fontsize"],
            fontweight=PLOT_CONFIG["value_fontweight"],
            color=STYLE_CONFIG["text_color"],
            clip_on=False,
            zorder=5,
        )


def style_compact_axis(ax: plt.Axes, y_max: float) -> None:
    """设置 compact scientific panel 样式。"""
    ax.set_ylim(0, y_max)
    ax.set_axisbelow(True)

    if PLOT_CONFIG["y_axis_integer"]:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    if PLOT_CONFIG["show_y_grid"]:
        ax.yaxis.grid(
            True,
            color=PLOT_CONFIG["y_grid_color"],
            alpha=PLOT_CONFIG["y_grid_alpha"],
            linestyle=PLOT_CONFIG["y_grid_linestyle"],
            linewidth=PLOT_CONFIG["y_grid_linewidth"],
            zorder=0,
        )

    ax.xaxis.grid(False)

    if PLOT_CONFIG["boxed_axes"]:
        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_visible(True)
            ax.spines[spine].set_color(PLOT_CONFIG["spine_color"])
            ax.spines[spine].set_linewidth(PLOT_CONFIG["spine_linewidth"])
    else:
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_visible(True)
            ax.spines[spine].set_color(PLOT_CONFIG["spine_color"])
            ax.spines[spine].set_linewidth(PLOT_CONFIG["spine_linewidth"])

    ax.tick_params(
        axis="y",
        direction=PLOT_CONFIG["tick_direction"],
        length=PLOT_CONFIG["tick_length"],
        width=PLOT_CONFIG["tick_width"],
        colors=STYLE_CONFIG["muted_text_color"],
        labelsize=PLOT_CONFIG["y_tick_fontsize"],
    )

    ax.tick_params(
        axis="x",
        direction=PLOT_CONFIG["tick_direction"],
        length=PLOT_CONFIG["tick_length"],
        width=PLOT_CONFIG["tick_width"],
        colors=STYLE_CONFIG["muted_text_color"],
        labelsize=PLOT_CONFIG["x_tick_fontsize"],
    )


def draw_compact_bar_chart(
    ax: plt.Axes,
    df: pd.DataFrame,
    label_col: str,
    title: str,
    y_max: float,
    label_wrap_width: int,
    panel_label: str | None = None,
) -> None:
    """绘制 compact vertical bar chart。"""
    x = np.arange(len(df))

    labels = [
        wrap_multiline_text(label, label_wrap_width)
        for label in df[label_col]
    ]

    bars = ax.bar(
        x,
        df["count"],
        width=PLOT_CONFIG["bar_width"],
        color=STYLE_CONFIG["bar_color"],
        alpha=PLOT_CONFIG["bar_alpha"],
        edgecolor=STYLE_CONFIG["bar_edgecolor"],
        linewidth=PLOT_CONFIG["bar_linewidth"],
        zorder=3,
    )

    add_value_labels(
        ax=ax,
        bars=bars,
        counts=df["count"],
        percents=df["percent"],
        y_max=y_max,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        labels,
        fontsize=PLOT_CONFIG["x_tick_fontsize"],
        fontweight=PLOT_CONFIG["tick_fontweight"],
        rotation=PLOT_CONFIG["x_tick_rotation"],
        ha=PLOT_CONFIG["x_tick_ha"],
        color=STYLE_CONFIG["text_color"],
    )

    ax.set_ylabel(
        PLOT_CONFIG["y_label"],
        fontsize=PLOT_CONFIG["axis_label_fontsize"],
        fontweight=PLOT_CONFIG["axis_label_fontweight"],
        color=STYLE_CONFIG["text_color"],
        labelpad=6,
    )

    ax.set_title(
        title,
        loc="center",
        fontsize=PLOT_CONFIG["title_fontsize"],
        fontweight=PLOT_CONFIG["title_fontweight"],
        color=STYLE_CONFIG["text_color"],
        pad=PLOT_CONFIG["title_pad"],
    )

    style_compact_axis(ax, y_max=y_max)

    if PLOT_CONFIG["show_panel_label"] and panel_label is not None:
        ax.text(
            PLOT_CONFIG["panel_label_x"],
            PLOT_CONFIG["panel_label_y"],
            panel_label,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=PLOT_CONFIG["panel_label_fontsize"],
            fontweight="bold",
            color=STYLE_CONFIG["panel_label_color"],
        )


def make_simple_discipline_legend_lines(codes: list[str]) -> tuple[str, str]:
    """
    生成简单文字型 Application-code mapping 图例。

    输出为左右两列文本，不使用表格、不使用边框。
    示例：
    E08 = Architecture and Civil Engineering
    D01 = Geography
    """
    unique_codes = []

    for code in codes:
        code = str(code).strip()
        if code not in unique_codes:
            unique_codes.append(code)

    legend_items = []

    for code in unique_codes:
        discipline_name = get_discipline_en(code)
        wrapped_name = wrap_text(
            discipline_name,
            PLOT_CONFIG["discipline_legend_wrap_width"],
        )

        # 名称换行后，后续行缩进，图例更整齐。
        wrapped_name = wrapped_name.replace("\n", "\n      ")
        legend_items.append(f"{code} = {wrapped_name}")

    if PLOT_CONFIG["discipline_legend_columns"] == 1:
        return "\n".join(legend_items), ""

    split_index = int(np.ceil(len(legend_items) / 2))
    left_text = "\n".join(legend_items[:split_index])
    right_text = "\n".join(legend_items[split_index:])

    return left_text, right_text


def add_discipline_mapping_legend(
    ax: plt.Axes,
    discipline_codes: pd.Series,
) -> None:
    """
    在 Application code 图下方添加简单文字型学科代码说明。

    注意：
    - 不使用表格；
    - 不使用边框；
    - x 轴只保留代码；
    - 完整英文名称用简洁文字图例说明。
    """
    if not PLOT_CONFIG.get("show_discipline_legend", True):
        return

    codes = discipline_codes.astype(str).tolist()
    left_text, right_text = make_simple_discipline_legend_lines(codes)

    ax.text(
        PLOT_CONFIG["discipline_legend_title_x"],
        PLOT_CONFIG["discipline_legend_title_y"],
        PLOT_CONFIG["discipline_legend_title"],
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=PLOT_CONFIG["discipline_legend_title_fontsize"],
        fontweight="bold",
        color=STYLE_CONFIG["text_color"],
        clip_on=False,
    )

    ax.text(
        PLOT_CONFIG["discipline_legend_left_x"],
        PLOT_CONFIG["discipline_legend_text_y"],
        left_text,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=PLOT_CONFIG["discipline_legend_fontsize"],
        fontweight="normal",
        color=STYLE_CONFIG["text_color"],
        linespacing=PLOT_CONFIG["discipline_legend_linespacing"],
        clip_on=False,
    )

    if right_text:
        ax.text(
            PLOT_CONFIG["discipline_legend_right_x"],
            PLOT_CONFIG["discipline_legend_text_y"],
            right_text,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=PLOT_CONFIG["discipline_legend_fontsize"],
            fontweight="normal",
            color=STYLE_CONFIG["text_color"],
            linespacing=PLOT_CONFIG["discipline_legend_linespacing"],
            clip_on=False,
        )


def save_figure(fig: plt.Figure, output_stem: str) -> None:
    """保存图像。"""
    if PLOT_CONFIG["save_png"]:
        fig.savefig(
            FIG_DIR / f"{output_stem}.png",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight",
        )

    if PLOT_CONFIG["save_pdf"]:
        fig.savefig(
            FIG_DIR / f"{output_stem}.pdf",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight",
        )

    if PLOT_CONFIG["save_svg"]:
        fig.savefig(
            FIG_DIR / f"{output_stem}.svg",
            dpi=PLOT_CONFIG["output_dpi"],
            bbox_inches="tight",
        )


# ============================================================
# 十三、合并图与单图
# ============================================================

def plot_combined_compact_figure(
    project_df: pd.DataFrame,
    discipline_df: pd.DataFrame,
) -> None:
    """绘制上下排列的 compact 合并图。"""
    if PLOT_CONFIG["use_common_y_axis_for_combined"]:
        project_y_max = calculate_common_y_max(project_df, discipline_df)
        discipline_y_max = project_y_max
    else:
        project_y_max = calculate_y_max(project_df)
        discipline_y_max = calculate_y_max(discipline_df)

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(
            PLOT_CONFIG["combined_figure_width"],
            PLOT_CONFIG["combined_figure_height"],
        ),
        dpi=PLOT_CONFIG["figure_dpi"],
        gridspec_kw={
            "height_ratios": [1.0, 1.0],
            "hspace": PLOT_CONFIG["combined_hspace"],
        },
    )

    fig.patch.set_facecolor(PLOT_CONFIG["background"])

    draw_compact_bar_chart(
        ax=axes[0],
        df=project_df,
        label_col="project_type_plot_label",
        title="Project type",
        y_max=project_y_max,
        label_wrap_width=PLOT_CONFIG["project_label_wrap_width"],
        panel_label=None,
    )

    draw_compact_bar_chart(
        ax=axes[1],
        df=discipline_df,
        label_col="discipline_code_plot_label",
        title="Application code",
        y_max=discipline_y_max,
        label_wrap_width=PLOT_CONFIG["discipline_label_wrap_width"],
        panel_label=None,
    )

    add_discipline_mapping_legend(
        ax=axes[1],
        discipline_codes=discipline_df["discipline_code"],
    )

    plt.subplots_adjust(
        left=PLOT_CONFIG["combined_left"],
        right=PLOT_CONFIG["combined_right"],
        top=PLOT_CONFIG["combined_top"],
        bottom=PLOT_CONFIG["combined_bottom"],
        hspace=PLOT_CONFIG["combined_hspace"],
    )

    save_figure(fig, OUTPUT_STEM_COMBINED)
    plt.close(fig)


def plot_single_project_type_figure(project_df: pd.DataFrame) -> None:
    """绘制 Project type compact 单图。"""
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(
            PLOT_CONFIG["single_project_figure_width"],
            PLOT_CONFIG["single_project_figure_height"],
        ),
        dpi=PLOT_CONFIG["figure_dpi"],
    )

    fig.patch.set_facecolor(PLOT_CONFIG["background"])

    draw_compact_bar_chart(
        ax=ax,
        df=project_df,
        label_col="project_type_plot_label",
        title="Project type",
        y_max=calculate_y_max(project_df),
        label_wrap_width=PLOT_CONFIG["project_label_wrap_width"],
        panel_label=None,
    )

    plt.subplots_adjust(
        left=PLOT_CONFIG["single_left"],
        right=PLOT_CONFIG["single_right"],
        top=PLOT_CONFIG["single_top"],
        bottom=PLOT_CONFIG["single_bottom_project"],
    )

    save_figure(fig, OUTPUT_STEM_PROJECT_TYPE)
    plt.close(fig)


def plot_single_discipline_code_figure(discipline_df: pd.DataFrame) -> None:
    """绘制 Application code compact 单图。"""
    fig, ax = plt.subplots(
        1,
        1,
        figsize=(
            PLOT_CONFIG["single_discipline_figure_width"],
            PLOT_CONFIG["single_discipline_figure_height"],
        ),
        dpi=PLOT_CONFIG["figure_dpi"],
    )

    fig.patch.set_facecolor(PLOT_CONFIG["background"])

    draw_compact_bar_chart(
        ax=ax,
        df=discipline_df,
        label_col="discipline_code_plot_label",
        title="Application code",
        y_max=calculate_y_max(discipline_df),
        label_wrap_width=PLOT_CONFIG["discipline_label_wrap_width"],
        panel_label=None,
    )

    add_discipline_mapping_legend(
        ax=ax,
        discipline_codes=discipline_df["discipline_code"],
    )

    plt.subplots_adjust(
        left=PLOT_CONFIG["single_left"],
        right=PLOT_CONFIG["single_right"],
        top=PLOT_CONFIG["single_top"],
        bottom=PLOT_CONFIG["single_bottom_discipline"],
    )

    save_figure(fig, OUTPUT_STEM_DISCIPLINE_CODE)
    plt.close(fig)


# ============================================================
# 十四、主函数
# ============================================================

def main() -> None:
    """主程序：读取数据、保存数据、绘图并导出。"""
    for folder in [OUTPUT_DIR, FIG_DIR, SRC_DIR]:
        folder.mkdir(parents=True, exist_ok=True)

    require_font()

    project_df = load_count_table(
        path=PROJECT_TYPE_FILE,
        category_col="project_type",
    )

    discipline_df = load_count_table(
        path=DISCIPLINE_CODE_FILE,
        category_col="discipline_code",
    )

    save_source_data(
        project_df=project_df,
        discipline_df=discipline_df,
    )

    plot_combined_compact_figure(
        project_df=project_df,
        discipline_df=discipline_df,
    )

    plot_single_project_type_figure(project_df=project_df)
    plot_single_discipline_code_figure(discipline_df=discipline_df)

    print(f"Saved compact figures and source data to: {OUTPUT_DIR}")
    print(f"Figure directory: {FIG_DIR}")
    print(f"Source-data directory: {SRC_DIR}")
    print("\nGenerated figures:")
    print(f"- {OUTPUT_STEM_COMBINED}.png / .pdf / .svg")
    print(f"- {OUTPUT_STEM_PROJECT_TYPE}.png / .pdf / .svg")
    print(f"- {OUTPUT_STEM_DISCIPLINE_CODE}.png / .pdf / .svg")


if __name__ == "__main__":
    main()