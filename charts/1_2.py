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
import matplotlib.dates as mdates
from matplotlib.ticker import IndexLocator, FuncFormatter
from datetime import datetime, timedelta
import numpy as np
from calc.utils import is_trading_day
from charts.utils import calculate_ylim, calculate_xlim, calculate_date_tick_params


def setup_chinese_font() -> None:
    """
    配置matplotlib中文字体
    
    支持的字体（按优先级）：
    1. SimHei（黑体）
    2. Microsoft YaHei（微软雅黑）
    3. Arial Unicode MS（如果系统有）
    """
    font_list = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['font.sans-serif'] = font_list
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 10


def plot_scale_overview(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True,
    include_right_table: bool = False,
    table_fontsize: int = 12
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
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_scale_data()
    
    # 解析数据并过滤掉非交易日（节假日）
    dates_raw = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    asset_scale_raw = [d['asset_scale'] for d in data]
    shares_raw = [d.get('shares', 0) for d in data]
    net_subscription_raw = [d.get('net_subscription', 0) for d in data]
    
    # 只保留交易日的数据
    dates = []
    asset_scale = []
    shares = []
    net_subscription = []
    for i, date_obj in enumerate(dates_raw):
        date_str = date_obj.strftime('%Y-%m-%d')
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
        gs = GridSpec(nrows=1, ncols=2, width_ratios=[3.0, 1.1], wspace=0.2, figure=fig)
        ax1 = fig.add_subplot(gs[0, 0])
        table_ax = fig.add_subplot(gs[0, 1])
        table_ax.axis('off')
    else:
        fig, ax1 = plt.subplots(figsize=figsize)
    
    # 左Y轴：资产规模和份额
    color1 = '#082868'  # 深蓝色
    color2 = '#afb0b2'  # 浅灰色
    
    # 设置X轴：使用索引位置，但显示日期标签
    # 这样非交易日之间的间隔会相等（比如星期五到星期一和星期一到星期二的距离相同）
    n_points = len(dates)
    x_indices = list(range(n_points))
    
    # 使用索引位置绘制
    line1 = ax1.plot(x_indices, asset_scale, color=color1, marker='', 
                     markersize=4, linewidth=2, label='资产规模', 
                     markerfacecolor='white', markeredgecolor=color1,
                     markeredgewidth=1.5)
    line2 = ax1.plot(x_indices, shares, color=color2, marker='', 
                     markersize=4, linewidth=2, label='份额', 
                     markerfacecolor='white', markeredgecolor=color2, 
                     markeredgewidth=1.5)
    
    ax1.set_xlabel('日期')
    ax1.set_ylabel('资产规模/份额(万元)', color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    # 基于数据特性自动计算左Y轴范围（资产规模和份额）
    y_min_left, y_max_left = calculate_ylim(
        [asset_scale, shares],
        start_from_zero=False,
        padding_ratio=0.1,
        allow_negative=True,
        round_to_nice_number=True
    )
    # ax1.set_ylim(y_min_left, y_max_left)
    ax1.margins(y=0.1)
    ax1.grid(True, alpha=0.5, linestyle='--')
    
    # 右Y轴：净申购额
    ax2 = ax1.twinx()
    color3 = '#2ca02c'  # 绿色（虽然图例显示绿色，但实际可能是深蓝色）
    # line3 = ax2.plot(x_indices, net_subscription, color=color1, marker='o', 
    #                  markersize=4, linewidth=2, label='净申购额',
    #                  markerfacecolor=color1, markeredgecolor=color1)
    
    ax2.set_ylabel('申购/赎回/净申购赎回(万元)', color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    # 基于数据特性自动计算右Y轴范围（净申购额）
    y_min_right, y_max_right = calculate_ylim(
        [net_subscription],
        start_from_zero=True,
        padding_ratio=0.15,  # 净申购额使用稍大的边距，因为数值较小
        allow_negative=False,
        round_to_nice_number=True
    )
    # ax2.set_ylim(y_min_right, y_max_right)
    ax2.margins(y=0.1)
    
    # 设置标题（如果启用）
    if show_title:
        ax1.set_title('产品规模总览', fontsize=14, fontweight='bold', pad=20)
    


    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # 设置X轴刻度和标签
    # 使用工具函数自动计算合适的刻度间隔
    if n_points > 0:
        # 使用工具函数计算日期刻度参数
        tick_indices, tick_labels = calculate_date_tick_params(dates)
        
        # 设置刻度位置
        ax1.set_xticks(tick_indices)
        
        # 设置刻度标签为对应的日期
        ax1.set_xticklabels(tick_labels, rotation=45, ha='right')
        
        # 使用工具函数自动计算X轴范围（虽然这里用的是索引，但可以设置索引范围）
        x_min, x_max = calculate_xlim(x_indices, padding_ratio=0.02, is_date=False)
        ax1.set_xlim(x_min, x_max)
    else:
        ax1.set_xticks([])
        ax1.set_xticklabels([])
    
    # 合并图例（左Y轴和右Y轴的数据）
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    
    # 添加申购和赎回到图例（虽然不在图表中显示）
    # 为了匹配图例，我们添加这些项但不绘制
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=color1, marker='', markersize=6, 
               linewidth=2, label='资产规模', markerfacecolor='white',
               markeredgecolor=color1, markeredgewidth=1.5),
        Line2D([0], [0], color=color2, marker='', markersize=6, 
               linewidth=2, label='份额', markerfacecolor=color2,
               markeredgecolor=color2, markeredgewidth=1.5),
        Line2D([0], [0], marker='s', color='red', linewidth=0, 
               markersize=8, label='申购'),
        Line2D([0], [0], marker='s', color='yellow', linewidth=0, 
               markersize=8, label='赎回'),
        Line2D([0], [0],  marker='s', color='green', linewidth=0, 
               markersize=8,label='净申购额')
    ]
    
    ax1.legend(handles=legend_elements, loc='upper center', 
               bbox_to_anchor=(0.5, 1.12), ncol=5, frameon=True)
    
    # 如果需要绘制右侧表格
    if include_right_table:
        # 计算指标
        start_scale = float(asset_scale[0]) if len(asset_scale) > 0 else 0.0
        end_scale = float(asset_scale[-1]) if len(asset_scale) > 0 else 0.0
        # 份额按数据可得
        start_shares = float(shares[0]) if len(shares) > 0 else 0.0
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
            ['期初资产规模', f"{start_scale:.2f} 万元"],
            ['期末资产规模', f"{end_scale:.2f} 万元"],
            ['期初产品份额', f"{start_shares:.2f} 万份"],
            ['期末产品份额', f"{end_shares:.2f} 万份"],
            ['期间总申购', f"{total_subscription:.2f} 万元"],
            ['期间总赎回', f"{total_redemption:.2f} 万元"],
        ]

        # 绘制表格
        tbl = table_ax.table(cellText=[[r[0], r[1]] for r in table_data],
                              colLabels=['指标', '数值'],
                              cellLoc='right',
                              colLoc='center',
                              loc='center',
                              bbox=[0.0, 0.05, 1.0, 0.9])
        # 样式
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(table_fontsize)
        # 表头样式
        for j in range(2):
            header_cell = tbl[(0, j)]
            header_cell.set_facecolor('#f0f0f0')
            header_cell.set_text_props(weight='bold', ha='center')
            header_cell.set_edgecolor('#f0f0f0')
            header_cell.set_linewidth(1)
        # 数据行样式
        n_rows = len(table_data) + 1
        for i in range(1, n_rows):
            for j in range(2):
                cell = tbl[(i, j)]
                if j == 0:
                    cell.set_text_props(ha='center')
                else:
                    cell.set_text_props(ha='center')
                cell.set_edgecolor('#f0f0f0')
                cell.set_linewidth(1)
                if i % 2 == 1:
                    cell.set_facecolor('#ffffff')
                else:
                    cell.set_facecolor('#ffffff')

    # 调整布局
    if include_right_table:
        # 使用 GridSpec 时，使用 subplots_adjust 而不是 tight_layout
        # 为图例留出更多空间
        plt.subplots_adjust(left=0.05, right=0.98, top=0.92, bottom=0.1, wspace=0.2)
    else:
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # 顶部留出4%的空间给图例
    
    # 如果只需要返回 figure 对象，不保存
    if return_figure:
        return fig
    
    # 如果提供了保存路径，保存图表为 PDF（矢量格式，高清）
    if save_path:
        plt.savefig(save_path, format='pdf', bbox_inches='tight', dpi=300)
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
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'asset_scale': round(asset_scale[i], 2),
            'shares': round(shares[i], 2),
            'net_subscription': round(net_subscription[i], 3)
        })
    
    return data


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成产品规模总览图...")
    output_path = plot_scale_overview()
    print(f"图表已保存到: {output_path}")

