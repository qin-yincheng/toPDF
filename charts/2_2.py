"""
大类持仓时序图表生成
使用 matplotlib 生成 100% 堆叠柱状图
"""

# 添加项目根目录到 Python 路径，以便正确导入模块
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
from datetime import datetime, timedelta
import numpy as np
from calc.utils import is_trading_day
from charts.utils import calculate_xlim, calculate_date_tick_params


def plot_asset_allocation_chart(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True,
):
    """
    绘制大类持仓时序图（100% 堆叠柱状图）

    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'stocks': 85.0,              # 股票占比（%）
                    'funds': 0.0,                # 基金占比（%）
                    'reverse_repurchase': 0.0,   # 逆回购占比（%）
                    'cash': 15.0,                # 现金占比（%）
                    'other_assets': 0.0          # 其他资产占比（%）
                },
                ...
            ]
            如果为None，则使用假数据
        save_path: 保存路径
        figsize: 图表大小（宽，高）
        return_figure: 是否返回 figure 对象
        show_title: 是否显示标题

    返回:
        figure 对象或保存的文件路径
    """
    # 配置中文字体
    setup_chinese_font()

    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_asset_allocation_data()

    # 解析数据并过滤掉非交易日（节假日）
    dates_raw = [datetime.strptime(d["date"], "%Y-%m-%d") for d in data]
    stocks_raw = [d["stocks"] for d in data]
    funds_raw = [d["funds"] for d in data]
    reverse_repurchase_raw = [d["reverse_repurchase"] for d in data]
    cash_raw = [d["cash"] for d in data]
    other_assets_raw = [d["other_assets"] for d in data]

    # 只保留交易日的数据
    dates = []
    stocks = []
    funds = []
    reverse_repurchase = []
    cash = []
    other_assets = []
    for i, date_obj in enumerate(dates_raw):
        date_str = date_obj.strftime("%Y-%m-%d")
        if is_trading_day(date_str):
            dates.append(date_obj)
            stocks.append(stocks_raw[i])
            funds.append(funds_raw[i])
            reverse_repurchase.append(reverse_repurchase_raw[i])
            cash.append(cash_raw[i])
            other_assets.append(other_assets_raw[i])

    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#f7f9fc")
    ax.set_facecolor("white")

    # 定义颜色
    color_stocks = "#2e5aac"  # 蓝色
    color_funds = "#66a15a"  # 绿色
    color_reverse_repurchase = "#f4a340"  # 黄色
    color_cash = "#d64545"  # 红色
    color_other = "#6bb5d8"  # 浅蓝色

    # 计算堆叠位置
    bottom1 = np.array(stocks)
    bottom2 = bottom1 + np.array(funds)
    bottom3 = bottom2 + np.array(reverse_repurchase)
    bottom4 = bottom3 + np.array(cash)

    # 使用数值索引绘制柱状图，使所有柱子之间间隔相等（包括周五到周一）
    x_positions = np.arange(len(dates))
    bar_width = 0.7  # 柱子宽度（数值单位）

    # 绘制堆叠柱状图
    ax.bar(
        x_positions,
        stocks,
        width=bar_width,
        label="股票",
        color=color_stocks,
        edgecolor="white",
        linewidth=0.4,
    )
    ax.bar(
        x_positions,
        funds,
        width=bar_width,
        bottom=bottom1,
        label="基金",
        color=color_funds,
        edgecolor="white",
        linewidth=0.4,
    )
    ax.bar(
        x_positions,
        reverse_repurchase,
        width=bar_width,
        bottom=bottom2,
        label="逆回购",
        color=color_reverse_repurchase,
        edgecolor="white",
        linewidth=0.4,
    )
    ax.bar(
        x_positions,
        cash,
        width=bar_width,
        bottom=bottom3,
        label="现金",
        color=color_cash,
        edgecolor="white",
        linewidth=0.4,
    )
    ax.bar(
        x_positions,
        other_assets,
        width=bar_width,
        bottom=bottom4,
        label="其他资产占比",
        color=color_other,
        edgecolor="white",
        linewidth=0.4,
    )

    # 设置Y轴（图片中Y轴范围是0-120%）
    ax.set_ylabel("占比(%)", color="#333333")
    ax.set_ylim(0, 105)
    ax.set_yticks(np.arange(0, 110, 20))
    ax.tick_params(axis="both", labelcolor="#333333", labelsize=10)
    ax.grid(True, alpha=0.35, linestyle="--", axis="y", color="#d7dce5", linewidth=0.8)

    # 设置X轴（使用数值索引，但显示日期标签）
    ax.set_xlabel("日期")
    # 使用工具函数自动计算合适的刻度间隔
    if len(dates) > 0:
        # 使用工具函数计算日期刻度参数
        tick_indices, tick_labels = calculate_date_tick_params(dates)

        # 设置刻度位置（使用索引位置）
        ax.set_xticks([x_positions[i] for i in tick_indices])

        # 设置刻度标签为对应的日期
        ax.set_xticklabels(tick_labels, rotation=30, ha="right")

        # 使用工具函数自动计算X轴范围
        x_min, x_max = calculate_xlim(x_positions, padding_ratio=0.02, is_date=False)
        ax.set_xlim(x_min, x_max)
    else:
        ax.set_xticks([])
        ax.set_xticklabels([])

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#c7ccd6")
    ax.spines["bottom"].set_color("#c7ccd6")

    # 设置标题（如果启用）
    if show_title:
        ax.set_title(
            "大类持仓时序",
            fontsize=16,
            fontweight="bold",
            pad=22,
            loc="left",
            color="#1f2933",
        )

    # 添加图例（增加与图表的间隔）
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=5,
        frameon=False,
        fontsize=10,
        labelcolor="#333333",
    )

    if dates:
        start_str = dates[0].strftime("%Y-%m-%d")
        end_str = dates[-1].strftime("%Y-%m-%d")
        summary_text = f"区间：{start_str} ~ {end_str}｜样本量：{len(dates)}｜末期股票占比：{stocks[-1]:.1f}%"
        fig.text(
            0.02,
            0.96,
            summary_text,
            fontsize=11,
            color="#4d5766",
            ha="left",
            va="center",
        )

    # 调整布局，为图例留出更多空间
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # 顶部留出4%的空间给图例

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


def _generate_mock_asset_allocation_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试大类持仓时序图
    返回:
        List[Dict]: 假数据列表
    """
    # 生成日期范围：从 2024-08-01 到 2025-01-10
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2025, 1, 10)

    # 定义节假日（2024年8月到2025年1月）
    holidays = [
        datetime(2024, 9, 15),  # 中秋节
        datetime(2024, 9, 16),  # 中秋节
        datetime(2024, 9, 17),  # 中秋节
        datetime(2024, 10, 1),  # 国庆节
        datetime(2024, 10, 2),  # 国庆节
        datetime(2024, 10, 3),  # 国庆节
        datetime(2024, 10, 4),  # 国庆节
        datetime(2024, 10, 5),  # 国庆节
        datetime(2024, 10, 6),  # 国庆节
        datetime(2024, 10, 7),  # 国庆节
        datetime(2025, 1, 1),  # 元旦
    ]

    # 生成工作日日期列表（跳过周末和节假日）
    dates = []
    current_date = start_date
    while current_date <= end_date:
        # 检查是否为工作日（周一到周五，且不是节假日）
        weekday = current_date.weekday()  # 0=Monday, 6=Sunday
        if weekday < 5 and current_date not in holidays:  # 周一到周五，且不是节假日
            dates.append(current_date)
        current_date += timedelta(days=1)

    data = []
    prev_stocks = 90.0  # 用于平滑过渡
    prev_funds = 0.0
    prev_reverse_repurchase = 0.0
    prev_cash = 10.0

    for i, date in enumerate(dates):
        stocks = 0.0
        funds = 0.0
        reverse_repurchase = 0.0
        cash = 0.0
        other_assets = 0.0

        # 根据图片描述的数据趋势生成数据（工作日数据需要平滑过渡）
        if date < datetime(2024, 9, 1):
            # 8月：股票约90-95%，少量现金（偶尔现金可达20%）
            if i == 0 or (i < 5 and np.random.random() < 0.2):  # 8月初偶尔现金较多
                target_stocks = 80.0 + np.random.uniform(0, 5)
            else:
                target_stocks = 90.0 + np.random.uniform(0, 5)
            # 平滑过渡
            stocks = (
                prev_stocks * 0.7 + target_stocks * 0.3 + np.random.uniform(-0.5, 0.5)
            )
            cash = 100 - stocks
        elif date < datetime(2024, 9, 15):
            # 9月初：股票降到约80%
            target_stocks = 80.0 + np.random.uniform(-1, 1)
            stocks = (
                prev_stocks * 0.8 + target_stocks * 0.2 + np.random.uniform(-0.3, 0.3)
            )
            cash = 100 - stocks
        elif date < datetime(2024, 10, 1):
            # 9月中下旬：股票回升到85-90%
            target_stocks = 87.0 + np.random.uniform(-2, 2)
            stocks = (
                prev_stocks * 0.85 + target_stocks * 0.15 + np.random.uniform(-0.3, 0.3)
            )
            cash = 100 - stocks
        elif date < datetime(2024, 12, 15):
            # 10-11月到12月中旬：股票接近100%（95-100%），偶尔有少量现金
            target_stocks = 98.0 + np.random.uniform(-1, 1)
            stocks = (
                prev_stocks * 0.9 + target_stocks * 0.1 + np.random.uniform(-0.2, 0.2)
            )
            cash = 100 - stocks
            # 10月底/11月初偶尔有现金较多的情况（最多20%）
            if date >= datetime(2024, 10, 25) and date <= datetime(2024, 11, 4):
                if np.random.random() < 0.15:  # 15%概率
                    target_stocks = 80.0 + np.random.uniform(0, 5)
                    stocks = prev_stocks * 0.7 + target_stocks * 0.3
                    cash = 100 - stocks
        elif date < datetime(2024, 12, 24):
            # 12月中旬：股票开始下降
            target_stocks = 95.0 + np.random.uniform(-1, 1)
            stocks = (
                prev_stocks * 0.9 + target_stocks * 0.1 + np.random.uniform(-0.2, 0.2)
            )
            cash = 100 - stocks
        elif date < datetime(2024, 12, 28):
            # 12月24日附近：基金出现（约50%），股票大幅下降
            target_stocks = 45.0 + np.random.uniform(-2, 2)
            target_funds = 50.0 + np.random.uniform(-3, 3)
            stocks = (
                prev_stocks * 0.6 + target_stocks * 0.4 + np.random.uniform(-0.5, 0.5)
            )
            funds = prev_funds * 0.5 + target_funds * 0.5 + np.random.uniform(-0.5, 0.5)
            cash = 5.0 + np.random.uniform(0, 3)
            other_assets = 100 - stocks - funds - cash
        elif date < datetime(2025, 1, 5):
            # 1月2日附近：逆回购出现（20-30%）
            target_stocks = 40.0 + np.random.uniform(-3, 3)
            target_funds = 30.0 + np.random.uniform(-3, 3)
            target_reverse_repurchase = 25.0 + np.random.uniform(-3, 3)
            stocks = (
                prev_stocks * 0.7 + target_stocks * 0.3 + np.random.uniform(-0.5, 0.5)
            )
            funds = prev_funds * 0.7 + target_funds * 0.3 + np.random.uniform(-0.5, 0.5)
            reverse_repurchase = (
                prev_reverse_repurchase * 0.5
                + target_reverse_repurchase * 0.5
                + np.random.uniform(-0.5, 0.5)
            )
            cash = 5.0 + np.random.uniform(0, 3)
            other_assets = 100 - stocks - funds - reverse_repurchase - cash
        else:
            # 1月10日：股票60%，基金20%，逆回购10%，现金10%
            target_stocks = 60.0 + np.random.uniform(-2, 2)
            target_funds = 20.0 + np.random.uniform(-1, 1)
            target_reverse_repurchase = 10.0 + np.random.uniform(-1, 1)
            stocks = (
                prev_stocks * 0.8 + target_stocks * 0.2 + np.random.uniform(-0.3, 0.3)
            )
            funds = prev_funds * 0.8 + target_funds * 0.2 + np.random.uniform(-0.3, 0.3)
            reverse_repurchase = (
                prev_reverse_repurchase * 0.8
                + target_reverse_repurchase * 0.2
                + np.random.uniform(-0.3, 0.3)
            )
            cash = 10.0 + np.random.uniform(-1, 1)
            other_assets = 100 - stocks - funds - reverse_repurchase - cash

        # 更新前一个值用于平滑过渡
        prev_stocks = stocks
        prev_funds = funds
        prev_reverse_repurchase = reverse_repurchase
        prev_cash = cash

        # 确保所有值非负
        stocks = max(0, stocks)
        funds = max(0, funds)
        reverse_repurchase = max(0, reverse_repurchase)
        cash = max(0, cash)
        other_assets = max(0, other_assets)

        # 确保其他资产占比很小（通常接近0，除非在特定时期）
        if date < datetime(2024, 12, 24):
            other_assets = 0.0  # 12月24日之前其他资产为0

        # 确保总和不超过100%（归一化处理）
        total = stocks + funds + reverse_repurchase + cash + other_assets
        if total > 100.01:  # 如果总和超过100%，进行归一化
            factor = 100.0 / total
            stocks *= factor
            funds *= factor
            reverse_repurchase *= factor
            cash *= factor
            other_assets *= factor
        elif total < 99.99:  # 如果总和小于100%，调整到100%
            diff = 100.0 - total
            # 按比例分配差值
            if total > 0:
                stocks += diff * (stocks / total)
                funds += diff * (funds / total)
                reverse_repurchase += diff * (reverse_repurchase / total)
                cash += diff * (cash / total)
                other_assets += diff * (other_assets / total)
            else:
                # 如果总和为0，全部设为股票
                stocks = 100.0

        # 最终检查，确保总和不超过100%
        total = stocks + funds + reverse_repurchase + cash + other_assets
        if total > 100.0:
            factor = 100.0 / total
            stocks *= factor
            funds *= factor
            reverse_repurchase *= factor
            cash *= factor
            other_assets *= factor

        data.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "stocks": round(stocks, 2),
                "funds": round(funds, 2),
                "reverse_repurchase": round(reverse_repurchase, 2),
                "cash": round(cash, 2),
                "other_assets": round(max(0, other_assets), 2),
            }
        )

    return data


if __name__ == "__main__":
    # 测试图表生成
    print("正在生成大类持仓时序图...")
    output_path = plot_asset_allocation_chart()
    print(f"图表已保存到: {output_path}")
