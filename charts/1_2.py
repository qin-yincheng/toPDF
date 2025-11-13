"""
图表生成模块
使用 matplotlib 生成各种金融分析图表
"""

# 添加项目根目录到 Python 路径，以便正确导入模块
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
import numpy as np
from calc.utils import is_trading_day
from charts.utils import calculate_ylim, calculate_xlim, calculate_date_tick_params


REPORT_STYLE = {
    "font.size": 14,
    "axes.titlesize": 22,
    "axes.titleweight": "bold",
    "axes.labelsize": 16,
    "axes.labelcolor": "#303030",
    "xtick.color": "#4d4d4d",
    "ytick.color": "#4d4d4d",
    "axes.edgecolor": "#d9d9d9",
    "axes.linewidth": 1.0,
    "grid.color": "#e5e5e5",
    "grid.linestyle": "-",
    "grid.linewidth": 1.0,
    "legend.fontsize": 13,
    "figure.facecolor": "white",
}

DEFAULT_FIGSIZE = (15, 8)


def _apply_report_style() -> None:
    rcParams.update(REPORT_STYLE)
    rcParams["axes.spines.top"] = False


def _style_value_table(tbl, table_fontsize: int) -> None:
    header_bg = "#e4ecff"
    stripe_odd = "#f8fbff"
    stripe_even = "#ffffff"
    border_color = "#d3def5"
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(table_fontsize)
    max_row = max(row for row, _ in tbl.get_celld().keys())
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(border_color)
        cell.set_linewidth(1.0)
        if row == 0:
            cell.set_text_props(
                weight="bold",
                ha="center",
                color="#15284c",
                fontsize=table_fontsize + 1,
            )
            cell.set_facecolor(header_bg)
            cell.set_linewidth(1.2)
        else:
            if col == 0:
                cell.set_text_props(
                    ha="left",
                    color="#22375c",
                    fontsize=table_fontsize,
                    fontweight="medium",
                )
            else:
                cell.set_text_props(
                    ha="right",
                    color="#111a2e",
                    fontsize=table_fontsize,
                    fontweight="medium",
                )
            if row % 2 == 1:
                cell.set_facecolor(stripe_odd)
            else:
                cell.set_facecolor(stripe_even)
        # 加粗表格底边
        if row == max_row:
            cell.set_linewidth(1.1)


def plot_scale_overview(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = DEFAULT_FIGSIZE,
    return_figure: bool = False,
    show_title: bool = True,
    include_right_table: bool = False,
    table_fontsize: int = 20,
):
    """
    绘制产品规模总览图（双Y轴折线图）

    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'asset_scale': 100.0,      # 资产规模（万元）
                    'shares': 115.0,            # 份额（万元）
                    'net_subscription': 0.6     # 净申购额（万元）
                },
                ...
            ]
            如果为None，则使用假数据
        save_path: 保存路径
        figsize: 图表大小（宽，高）

    返回:
        str: 保存的文件路径
    """
    # 配置中文字体与统一风格
    from charts.font_config import setup_chinese_font

    setup_chinese_font()
    _apply_report_style()

    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_scale_data()

    # 解析数据并过滤掉非交易日（节假日）
    dates_raw = [datetime.strptime(d["date"], "%Y-%m-%d") for d in data]
    asset_scale_raw = [d["asset_scale"] for d in data]
    shares_raw = [d.get("shares", 0) for d in data]
    net_subscription_raw = [d.get("net_subscription", 0) for d in data]

    # 保存第一天的数据作为"日历期初"（用于表格显示）
    # 这样即使第一天不是交易日（如元旦），也能正确显示期初资产
    calendar_start_asset = asset_scale_raw[0] if len(asset_scale_raw) > 0 else 0.0
    calendar_start_shares = shares_raw[0] if len(shares_raw) > 0 else 0.0

    # 只保留交易日的数据（用于图表绘制）
    dates = []
    asset_scale = []
    shares = []
    net_subscription = []
    for i, date_obj in enumerate(dates_raw):
        date_str = date_obj.strftime("%Y-%m-%d")
        if is_trading_day(date_str):
            dates.append(date_obj)
            asset_scale.append(asset_scale_raw[i])
            shares.append(shares_raw[i])
            net_subscription.append(net_subscription_raw[i])

    # 创建图表
    if include_right_table:
        # 使用 GridSpec 左侧画图，右侧表格
        from matplotlib.gridspec import GridSpec

        fig = plt.figure(figsize=figsize)
        fig.patch.set_facecolor("white")
        gs = GridSpec(
            nrows=1, ncols=2, width_ratios=[3.2, 1.0], wspace=0.15, figure=fig
        )
        ax1 = fig.add_subplot(gs[0, 0])
        table_ax = fig.add_subplot(gs[0, 1])
        table_ax.axis("off")
    else:
        fig, ax1 = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor("white")

    # 左Y轴：资产规模和份额
    color1 = "#0a3475"  # 深蓝色
    color2 = "#7f8a9c"  # 灰蓝色
    bar_color = "#1b998b"

    # 设置X轴：使用索引位置，但显示日期标签
    # 这样非交易日之间的间隔会相等（比如星期五到星期一和星期一到星期二的距离相同）
    n_points = len(dates)
    x_indices = list(range(n_points))

    # 使用索引位置绘制
    ax1.plot(
        x_indices,
        asset_scale,
        color=color1,
        linewidth=3.0,
        label="资产规模",
    )
    ax1.plot(
        x_indices,
        shares,
        color=color2,
        linewidth=2.6,
        linestyle="--",
        label="份额",
    )
    ax1.set_xlabel("日期", labelpad=18)
    ax1.set_ylabel("资产规模 / 份额（万元）", labelpad=18)
    ax1.tick_params(axis="y", labelsize=13, colors="#4d4d4d", pad=10)
    ax1.tick_params(axis="x", labelsize=13, pad=12)
    ax1.set_axisbelow(True)
    for spine in ["left", "bottom"]:
        ax1.spines[spine].set_color("#cfcfcf")
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="y", linestyle="-", linewidth=1.0, alpha=0.5)
    ax1.grid(visible=False, axis="x")

    # 基于数据特性自动计算左Y轴范围（资产规模和份额）
    y_min_left, y_max_left = calculate_ylim(
        [asset_scale, shares],
        start_from_zero=False,
        padding_ratio=0.1,
        allow_negative=True,
        round_to_nice_number=True,
    )
    ax1.set_ylim(y_min_left, y_max_left)

    # 右Y轴：净申购额
    ax2 = ax1.twinx()
    ax2.bar(
        x_indices,
        net_subscription,
        color=bar_color,
        alpha=0.35,
        label="净申购额",
        width=0.6,
        edgecolor="none",
    )

    ax2.set_ylabel("净申购额（万元）", labelpad=18, color="#303030")
    ax2.tick_params(axis="y", labelsize=13, colors="#4d4d4d", pad=10)
    # 基于数据特性自动计算右Y轴范围（净申购额）
    y_min_right, y_max_right = calculate_ylim(
        [net_subscription],
        start_from_zero=True,
        padding_ratio=0.15,  # 净申购额使用稍大的边距，因为数值较小
        allow_negative=False,
        round_to_nice_number=True,
    )
    ax2.set_ylim(y_min_right, y_max_right)
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["right"].set_color("#d9d9d9")
    ax2.spines["right"].set_linewidth(1.0)

    # 设置标题（如果启用）
    if show_title:
        ax1.set_title("产品规模总览", pad=28)
        if n_points > 0:
            subtitle = f"期间：{dates[0].strftime('%Y-%m-%d')} 至 {dates[-1].strftime('%Y-%m-%d')}"
            ax1.text(
                0, 1.05, subtitle, transform=ax1.transAxes, fontsize=13, color="#5c5c5c"
            )
        ax1.text(
            0, 1.02, "单位：万元", transform=ax1.transAxes, fontsize=12, color="#7a7a7a"
        )

    # 设置X轴刻度和标签
    # 使用工具函数自动计算合适的刻度间隔
    if n_points > 0:
        # 使用工具函数计算日期刻度参数
        tick_indices, tick_labels = calculate_date_tick_params(dates)

        # 设置刻度位置
        ax1.set_xticks(tick_indices)

        # 设置刻度标签为对应的日期
        ax1.set_xticklabels(tick_labels, rotation=45, ha="right")

        # 使用工具函数自动计算X轴范围（虽然这里用的是索引，但可以设置索引范围）
        x_min, x_max = calculate_xlim(x_indices, padding_ratio=0.02, is_date=False)
        ax1.set_xlim(x_min, x_max)
    else:
        ax1.set_xticks([])
        ax1.set_xticklabels([])

    # 合并图例（左Y轴和右Y轴的数据）
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    legend_handles = lines1 + lines2
    legend_labels = labels1 + labels2
    legend = ax1.legend(
        legend_handles,
        legend_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=3,
        frameon=False,
        handlelength=2.0,
    )
    for text in legend.get_texts():
        text.set_color("#404040")

    # 如果需要绘制右侧表格
    if include_right_table:
        # 计算指标
        # 期初资产使用"日历期初"（年度第一天），即使不是交易日也要使用
        # 这样可以确保期初资产 = 上一年期末资产，保持跨年数据一致性
        start_scale = float(calendar_start_asset) if calendar_start_asset else 0.0
        start_shares = float(calendar_start_shares) if calendar_start_shares else 0.0

        # 期末资产使用最后一个交易日的数据
        end_scale = float(asset_scale[-1]) if len(asset_scale) > 0 else 0.0
        end_shares = float(shares[-1]) if len(shares) > 0 else 0.0
        # 期间总申购与总赎回（根据净申购额的正负推断）
        # 如果净申购额为正，总申购 = 净申购额，总赎回 = 0
        # 如果净申购额为负，总申购 = 0，总赎回 = 净申购额的绝对值
        net_sub_total = float(np.sum([v for v in net_subscription if v is not None]))
        if net_sub_total >= 0:
            total_subscription = net_sub_total
            total_redemption = 0.0
        else:
            total_subscription = 0.0
            total_redemption = abs(net_sub_total)

        table_data = [
            ["期初资产规模", f"{start_scale:.2f} 万元"],
            ["期末资产规模", f"{end_scale:.2f} 万元"],
            ["期初产品份额", f"{start_shares:.2f} 万份"],
            ["期末产品份额", f"{end_shares:.2f} 万份"],
            ["期间总申购", f"{total_subscription:.2f} 万元"],
            ["期间总赎回", f"{total_redemption:.2f} 万元"],
        ]

        # 绘制表格
        tbl = table_ax.table(
            cellText=[[r[0], r[1]] for r in table_data],
            colLabels=["指标", "数值"],
            cellLoc="center",
            colLoc="center",
            loc="center",
            bbox=[0.05, 0.02, 0.9, 0.9],
        )
        _style_value_table(tbl, table_fontsize)
        table_ax.set_facecolor("#f3f6fd")
        table_ax.set_xlim(0, 1)
        table_ax.set_ylim(0, 1)

    # 调整布局
    if include_right_table:
        plt.subplots_adjust(left=0.07, right=0.94, top=0.86, bottom=0.18, wspace=0.15)
    else:
        plt.subplots_adjust(left=0.08, right=0.96, top=0.86, bottom=0.22)

    # 如果只需要返回 figure 对象，不保存
    if return_figure:
        return fig

    # 如果提供了保存路径，保存图表为 PDF（矢量格式，高清）
    if save_path:
        plt.savefig(save_path, format="pdf", bbox_inches="tight", dpi=300)
        plt.close()
        return save_path
    else:
        # 不保存，返回 figure 对象
        return fig


def _generate_mock_scale_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试产品规模总览图

    返回:
        List[Dict]: 假数据列表
    """
    # 生成日期范围：2024-08-01 到 2025-01-14
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2025, 1, 14)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    # 生成资产规模数据（从100万增长到175万，然后下降到150万）
    n = len(dates)
    asset_scale = []
    base_value = 100
    peak_value = 175
    end_value = 150

    for i, date in enumerate(dates):
        progress = i / (n - 1)
        if progress < 0.7:  # 前70%增长到峰值
            value = base_value + (peak_value - base_value) * (progress / 0.7)
        else:  # 后30%下降
            value = peak_value - (peak_value - end_value) * ((progress - 0.7) / 0.3)
        # 添加一些随机波动
        noise = np.random.normal(0, 2)
        asset_scale.append(max(95, value + noise))

    # 生成份额数据（相对平稳，在115-120万之间）
    shares = [115 + np.random.normal(0, 2) for _ in dates]
    shares = [max(110, min(125, s)) for s in shares]

    # 生成净申购额数据（从10月中旬开始，在0.6-0.8万之间波动）
    net_subscription = []
    oct_11_index = None
    for i, date in enumerate(dates):
        if date >= datetime(2024, 10, 11):
            if oct_11_index is None:
                oct_11_index = i
            value = 0.7 + np.random.normal(0, 0.05)
            net_subscription.append(max(0.6, min(0.8, value)))
        else:
            net_subscription.append(0)

    # 组装数据
    data = []
    for i, date in enumerate(dates):
        data.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "asset_scale": round(asset_scale[i], 2),
                "shares": round(shares[i], 2),
                "net_subscription": round(net_subscription[i], 3),
            }
        )

    return data


if __name__ == "__main__":
    # 测试图表生成
    print("正在生成产品规模总览图...")
    output_path = plot_scale_overview()
    print(f"图表已保存到: {output_path}")
