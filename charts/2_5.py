"""
流动性资产时序图表生成
使用 matplotlib 生成流动性资产时序图（面积图 + 折线图，双Y轴）
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
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
from charts.utils import calculate_xlim, calculate_date_tick_params
from calc.utils import is_trading_day



def plot_liquidity_asset_chart(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制流动性资产时序图（面积图 + 折线图，双Y轴）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'liquidity_ratio': 100.0,  # 流动性资产比例（%）
                    'csi300': 0.98             # 沪深300指数
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
        data = _generate_mock_liquidity_data()
    
    # 解析日期和数据并过滤掉非交易日（节假日）
    dates_raw = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    liquidity_ratios_raw = [d['liquidity_ratio'] for d in data]
    csi300_values_raw = [d['csi300'] for d in data]
    
    # 只保留交易日的数据
    dates = []
    liquidity_ratios = []
    csi300_values = []
    for i, date_obj in enumerate(dates_raw):
        date_str = date_obj.strftime('%Y-%m-%d')
        if is_trading_day(date_str):
            dates.append(date_obj)
            liquidity_ratios.append(liquidity_ratios_raw[i])
            csi300_values.append(csi300_values_raw[i])
    
    # 创建图表和双Y轴
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    
    # 设置X轴：使用索引位置，但显示日期标签
    # 这样非交易日之间的间隔会相等（比如星期五到星期一和星期一到星期二的距离相同）
    n_points = len(dates)
    x_indices = list(range(n_points))
    
    # 绘制流动性资产比例面积图（左Y轴，蓝色填充，带圆形标记）
    ax1.fill_between(x_indices, liquidity_ratios, 0, alpha=1, color='#526895', label='流动性资产比例')
    ax1.plot(x_indices, liquidity_ratios, color='#082868', marker='', 
             markersize=4, linewidth=1.5, alpha=1,markerfacecolor='white', markeredgecolor='#082868',
                     markeredgewidth=1.5)
    ax1.set_ylabel('占比(%)', fontsize=11)
    ax1.set_ylim(0.13, 100)
    ax1.set_yticks([0.13, 20, 40, 60, 80, 100])
    ax1.set_yticklabels(['0.13%', '20%', '40%', '60%', '80%', '100%'])
    # 网格线：水平虚线，灰色
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=1, axis='y')
    ax1.set_xlabel('日期', fontsize=11)
    
    # 绘制沪深300折线图（右Y轴，灰色，带圆形标记）
    ax2.plot(x_indices, csi300_values, color='#afb0b2', marker='', 
             markersize=4, linewidth=1.5, label='沪深300',
             markerfacecolor='white', markeredgecolor='#afb0b2',
            markeredgewidth=1.5)
    ax2.set_ylabel('沪深300', fontsize=11)
    
    # 动态计算右Y轴范围（基准净值）
    if csi300_values:
        csi300_min = min(csi300_values)
        csi300_max = max(csi300_values)
        # 添加10%的边距
        y_range = csi300_max - csi300_min
        if y_range > 0:
            padding = y_range * 0.1
            ax2.set_ylim(csi300_min - padding, csi300_max + padding)
        else:
            # 如果所有值相同，设置默认范围
            ax2.set_ylim(csi300_min - 0.1, csi300_max + 0.1)
    
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
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper center', bbox_to_anchor=(0.5, 1.12),
               ncol=2, frameon=True)

    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    # 添加标题（如果启用，但这里不显示，由 pages.py 统一绘制）
    # if show_title:
    #     plt.title('流动性资产时序*', fontsize=16, fontweight='bold', pad=20, loc='left')
    
    # 调整布局
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
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


def _generate_mock_liquidity_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试流动性资产时序图
    返回:
        List: 假数据列表
    """
    # 生成日期范围（2024-08-01 到 2025-01-06，每个工作日）
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2025, 1, 6)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        # 跳过周末
        if current_date.weekday() < 5:
            dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    data = []
    
    # 定义关键日期和对应的流动性资产比例值（精确匹配图片）
    key_dates_liquidity = [
        (datetime(2024, 8, 1), 100.0),
        (datetime(2024, 8, 13), 0.13),
        (datetime(2024, 8, 18), 12.0),
        (datetime(2024, 8, 20), 0.13),
        (datetime(2024, 9, 30), 18.0),
        (datetime(2024, 10, 2), 0.13),
        (datetime(2024, 10, 29), 20.0),
        (datetime(2024, 10, 31), 0.13),
        (datetime(2024, 11, 8), 20.0),
        (datetime(2024, 11, 10), 0.13),
        (datetime(2024, 12, 24), 45.0),
        (datetime(2024, 12, 26), 0.13),
        (datetime(2025, 1, 6), 45.0),
    ]
    
    # 定义关键日期和对应的沪深300值（精确匹配图片）
    key_dates_csi300 = [
        (datetime(2024, 8, 1), 0.98),
        (datetime(2024, 9, 4), 0.95),
        (datetime(2024, 9, 30), 1.24),
        (datetime(2024, 10, 17), 1.15),
        (datetime(2024, 10, 29), 1.18),
        (datetime(2024, 11, 8), 1.12),
        (datetime(2024, 11, 20), 1.15),
        (datetime(2024, 12, 2), 1.10),
        (datetime(2024, 12, 12), 1.08),
        (datetime(2024, 12, 24), 1.08),
        (datetime(2025, 1, 6), 1.10),
    ]
    
    for i, date_str in enumerate(dates):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # 计算流动性资产比例（在关键点之间插值）
        liquidity_ratio = 100.0
        found = False
        for j in range(len(key_dates_liquidity) - 1):
            date1, value1 = key_dates_liquidity[j]
            date2, value2 = key_dates_liquidity[j + 1]
            if date1 <= date_obj <= date2:
                if date1 == date2:
                    liquidity_ratio = value1
                else:
                    progress = (date_obj - date1).days / (date2 - date1).days
                    # 使用平滑插值
                    liquidity_ratio = value1 + (value2 - value1) * progress
                found = True
                break
        
        if not found:
            if date_obj < key_dates_liquidity[0][0]:
                liquidity_ratio = key_dates_liquidity[0][1]
            elif date_obj > key_dates_liquidity[-1][0]:
                liquidity_ratio = key_dates_liquidity[-1][1]
        
        # 计算沪深300（在关键点之间插值）
        csi300 = 0.98
        found = False
        for j in range(len(key_dates_csi300) - 1):
            date1, value1 = key_dates_csi300[j]
            date2, value2 = key_dates_csi300[j + 1]
            if date1 <= date_obj <= date2:
                if date1 == date2:
                    csi300 = value1
                else:
                    progress = (date_obj - date1).days / (date2 - date1).days
                    # 使用平滑插值
                    csi300 = value1 + (value2 - value1) * progress
                found = True
                break
        
        if not found:
            if date_obj < key_dates_csi300[0][0]:
                csi300 = key_dates_csi300[0][1]
            elif date_obj > key_dates_csi300[-1][0]:
                csi300 = key_dates_csi300[-1][1]
        
        data.append({
            'date': date_str,
            'liquidity_ratio': round(liquidity_ratio, 2),
            'csi300': round(csi300, 4)
        })
    
    return data


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成流动性资产时序图...")
    output_path = plot_liquidity_asset_chart()
    print(f"图表已保存到: {output_path}")


