"""
单位净值表现图表生成
使用 matplotlib 生成多线折线图
"""

# 添加项目根目录到 Python 路径，以便正确导入模块
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
from charts.utils import calculate_xlim, calculate_date_tick_params


def setup_chinese_font() -> None:
    """
    配置matplotlib中文字体
    """
    font_list = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['font.sans-serif'] = font_list
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 10


def plot_nav_performance(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制单位净值表现图（多线折线图）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'accumulated_return': 0.0,      # 复权累计收益（%）
                    'csi300': 0.0,                   # 沪深300（%）
                    'excess_return': 0.0            # 累计超额收益（%）
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
        data = _generate_mock_nav_data()
    
    # 解析数据
    dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    accumulated_return = [d['accumulated_return'] for d in data]
    csi300 = [d.get('csi300', 0) for d in data]
    excess_return = [d.get('excess_return', 0) for d in data]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 设置X轴：使用索引位置，但显示日期标签
    # 这样非交易日之间的间隔会相等（比如星期五到星期一和星期一到星期二的距离相同）
    n_points = len(dates)
    x_indices = list(range(n_points))
    
    # 绘制三条线
    # 1. 复权累计收益：深蓝色，实心圆点
    color1 = '#082868'  # 深蓝色
    line1 = ax.plot(x_indices, accumulated_return, color=color1, marker='', 
                    markersize=4, linewidth=2, label='复权累计收益',
                    markerfacecolor='white', markeredgecolor=color1,
                    markeredgewidth=1.5)
    
    # 2. 沪深300：浅灰色，空心圆点
    color2 = '#afb0b2'  # 浅灰色
    line2 = ax.plot(x_indices, csi300, color=color2, marker='', 
                    markersize=4, linewidth=2, label='沪深300',
                    markerfacecolor='white', markeredgecolor=color2, 
                    markeredgewidth=1.5)
    
    # 3. 累计超额收益：红色，实心圆点
    color3 = '#c12e34'  # 红色
    line3 = ax.plot(x_indices, excess_return, color=color3, marker='', 
                    markersize=4, linewidth=2, label='累计超额收益',
                    markerfacecolor='white', markeredgecolor=color3,
                    markeredgewidth=1.5)
    
    # 设置坐标轴
    ax.set_xlabel('日期')
    ax.set_ylabel('收益率(%)', color='black')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 设置标题（如果启用）
    if show_title:
        ax.set_title('单位净值表现', fontsize=14, fontweight='bold', pad=20)
    
    # 设置X轴刻度和标签
    # 使用工具函数自动计算合适的刻度间隔
    if n_points > 0:
        # 使用工具函数计算日期刻度参数
        tick_indices, tick_labels = calculate_date_tick_params(dates)
        
        # 设置刻度位置
        ax.set_xticks(tick_indices)
        
        # 设置刻度标签为对应的日期
        ax.set_xticklabels(tick_labels, rotation=45, ha='right')
        
        # 使用工具函数自动计算X轴范围（虽然这里用的是索引，但可以设置索引范围）
        x_min, x_max = calculate_xlim(x_indices, padding_ratio=0.02, is_date=False)
        ax.set_xlim(x_min, x_max)
    else:
        ax.set_xticks([])
        ax.set_xticklabels([])

    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 设置图例（顶部居中，增加与图表的间隔）
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), 
              ncol=3, frameon=True)
    
    # 调整布局，为图例留出更多空间
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


def _generate_mock_nav_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试单位净值表现图
    
    返回:
        List[Dict]: 假数据列表
    """
    # 生成日期范围：2024-08-01 到 2025-01-10
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2025, 1, 10)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    n = len(dates)
    
    # 生成复权累计收益数据
    # 从0%开始，9月底开始增长，10月初达到40%，12月6日达到85%峰值，然后下降到45%，1月恢复到55%
    accumulated_return = []
    sep_30_index = (datetime(2024, 9, 30) - start_date).days
    oct_5_index = (datetime(2024, 10, 5) - start_date).days
    dec_6_index = (datetime(2024, 12, 6) - start_date).days
    dec_25_index = (datetime(2024, 12, 25) - start_date).days
    jan_10_index = n - 1
    
    for i in range(n):
        date = dates[i]
        if i <= sep_30_index:
            # 8月到9月底：相对平缓，略负
            value = np.random.normal(-2, 3)
            value = max(-10, min(5, value))
        elif i <= oct_5_index:
            # 9月底到10月初：快速增长到40%
            progress = (i - sep_30_index) / (oct_5_index - sep_30_index)
            target = 40
            value = -2 + (target - (-2)) * progress
            value += np.random.normal(0, 2)
        elif i <= dec_6_index:
            # 10月初到12月6日：继续增长到85%
            progress = (i - oct_5_index) / (dec_6_index - oct_5_index)
            value = 40 + (85 - 40) * progress
            value += np.random.normal(0, 3)
        elif i <= dec_25_index:
            # 12月6日到12月25日：下降到45%
            progress = (i - dec_6_index) / (dec_25_index - dec_6_index)
            value = 85 - (85 - 45) * progress
            value += np.random.normal(0, 3)
        else:
            # 12月25日到1月10日：恢复到55%
            progress = (i - dec_25_index) / (jan_10_index - dec_25_index)
            value = 45 + (55 - 45) * progress
            value += np.random.normal(0, 2)
        
        accumulated_return.append(value)
    
    # 生成沪深300数据（相对稳定，在-5%到20%之间波动）
    csi300 = []
    for i in range(n):
        # 整体趋势：从0%开始，逐步增长到12月初的20%，然后略有下降
        progress = i / (n - 1)
        base_value = 0 + 20 * progress * 0.8  # 增长趋势
        if i > (datetime(2024, 12, 5) - start_date).days:
            # 12月5日后略有下降
            decline_progress = (i - (datetime(2024, 12, 5) - start_date).days) / (n - 1 - (datetime(2024, 12, 5) - start_date).days)
            base_value = 20 - 5 * decline_progress * 0.3
        
        value = base_value + np.random.normal(0, 3)
        value = max(-10, min(25, value))
        csi300.append(value)
    
    # 生成累计超额收益数据（类似复权累计收益，但数值略低）
    excess_return = []
    for i in range(n):
        # 累计超额收益 = 复权累计收益 - 沪深300
        base_value = accumulated_return[i] - csi300[i]
        # 添加一些调整，使其略低于复权累计收益
        value = base_value * 0.9 + np.random.normal(0, 2)
        excess_return.append(value)
    
    # 组装数据
    data = []
    for i, date in enumerate(dates):
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'accumulated_return': round(accumulated_return[i], 2),
            'csi300': round(csi300[i], 2),
            'excess_return': round(excess_return[i], 2)
        })
    
    return data


if __name__ == '__main__':
    # 测试 matplotlib 图表生成
    print("正在生成单位净值表现图...")
    output_path = plot_nav_performance()
    print(f"图表已保存到: {output_path}")

