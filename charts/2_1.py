"""
动态回撤图表生成
使用 matplotlib 生成动态回撤折线图和汇总表格
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



def plot_dynamic_drawdown_chart(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (12, 6),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制动态回撤折线图
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'product_drawdown': 0.0,      # 产品回撤（%）
                    'benchmark_drawdown': 0.0     # 基准回撤（%）
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
        data = _generate_mock_drawdown_data()
    
    # 解析数据并过滤掉非交易日（节假日）
    dates_raw = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    product_drawdown_raw = [d['product_drawdown'] for d in data]
    benchmark_drawdown_raw = [d.get('benchmark_drawdown', 0) for d in data]
    
    # 只保留交易日的数据
    dates = []
    product_drawdown = []
    benchmark_drawdown = []
    for i, date_obj in enumerate(dates_raw):
        date_str = date_obj.strftime('%Y-%m-%d')
        if is_trading_day(date_str):
            dates.append(date_obj)
            product_drawdown.append(product_drawdown_raw[i])
            benchmark_drawdown.append(benchmark_drawdown_raw[i])
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 设置X轴：使用索引位置，但显示日期标签
    # 这样非交易日之间的间隔会相等（比如星期五到星期一和星期一到星期二的距离相同）
    n_points = len(dates)
    x_indices = list(range(n_points))
    
    # 绘制产品回撤线（蓝色）
    color1 = '#5470c6'  # 深蓝色
    line1 = ax.plot(x_indices, product_drawdown, color=color1, marker='', 
                     markersize=4, linewidth=2, label='阳光安盛多禾一号私募证券投资基金',
                     markerfacecolor='white', markeredgecolor=color1,
                     markeredgewidth=1.5)
    
    # 绘制基准回撤线（绿色）
    color2 = '#91cc75'  # 绿色
    line2 = ax.plot(x_indices, benchmark_drawdown, color=color2, marker='', 
                     markersize=4, linewidth=2, label='沪深300',
                     markerfacecolor='white', markeredgecolor=color2,
                     markeredgewidth=1.5)
    
    # 设置Y轴（回撤从0%到最大回撤）
    max_drawdown = max(max(product_drawdown), max(benchmark_drawdown))
    y_min = min(-25, max_drawdown - 2)  # 留出一些空间
    ax.margins(y=0.1)
    # ax.set_ylim(y_min, 1)
    ax.set_ylabel('回撤(%)', color='black')
    ax.tick_params(axis='y', labelcolor='black')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 设置X轴刻度和标签
    ax.set_xlabel('日期')
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
    
    # 设置标题（如果启用）
    if show_title:
        ax.set_title('动态回撤', fontsize=14, fontweight='bold', pad=20, loc='left')
    

    # 设置边框：只保留左边框，删除其他边框
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # 添加图例（增加与图表的间隔）
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=2, frameon=True)
    
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


def plot_dynamic_drawdown_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (6, 6),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 12
):
    """
    绘制动态回撤汇总表格
    
    参数:
        data: 数据字典，格式为：
            {
                'product_max_drawdown': -23.43,           # 产品最大回撤（%）
                'benchmark_max_drawdown': -12.54,        # 基准最大回撤（%）
                'product_dd_start': '2024-12-12',         # 产品最大回撤开始日期
                'product_dd_end': '2025-01-10',          # 产品最大回撤结束日期
                'benchmark_dd_start': '2024-10-08',      # 基准最大回撤开始日期
                'benchmark_dd_end': '2025-01-13',        # 基准最大回撤结束日期
                'product_recovery_period': '-',          # 产品回撤修复期
                'benchmark_recovery_period': '-'          # 基准回撤修复期
            }
            如果为None，则使用假数据
        save_path: 保存路径
        figsize: 图表大小（宽，高）
        return_figure: 是否返回 figure 对象
        show_title: 是否显示标题
        table_fontsize: 表格字体大小
    
    返回:
        figure 对象或保存的文件路径
    """
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_drawdown_table_data()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 准备表格数据
    table_data = [
        ['产品期间最大回撤', f"{data.get('product_max_drawdown', 0):.2f}%"],
        ['比较基准的最大回撤', f"{data.get('benchmark_max_drawdown', 0):.2f}%"],
        ['产品最大回撤区间', f"自{data.get('product_dd_start', '')} 至{data.get('product_dd_end', '')}"],
        ['比较基准的最大回撤区间', f"自{data.get('benchmark_dd_start', '')} 至{data.get('benchmark_dd_end', '')}"],
        ['产品最大回撤修复期', data.get('product_recovery_period', '-')],
        ['比较基准的最大回撤修复期', data.get('benchmark_recovery_period', '-')],
    ]
    
    # 创建表格
    table = ax.table(
        cellText=table_data,
        colLabels=['指标', '数值'],
        cellLoc='left',
        loc='center',
        bbox=[0.1, 0.1, 1, 0.8]
    )
    
    # 设置表格样式
    table.auto_set_font_size(False)
    table.set_fontsize(table_fontsize)
    table.scale(1, 2.0)
    
    # 设置表头样式
    for i in range(2):
        cell = table[(0, i)]
        cell.set_facecolor('#f0f0f0')  # 浅灰色背景
        cell.set_text_props(weight='bold', ha='center')
        cell.set_edgecolor('#f0f0f0')
        cell.set_linewidth(1)
    
    # 设置数据行样式
    for i in range(1, len(table_data) + 1):
        for j in range(2):
            cell = table[(i, j)]
            # 第一列（指标列）左对齐，第二列（数值列）左对齐
            if j == 0:
                cell.set_text_props(ha='center')
            else:
                cell.set_text_props(ha='center')
            
            # 交替行颜色
            if i % 2 == 0:
                cell.set_facecolor('#ffffff')  # 白色
            else:
                cell.set_facecolor('#ffffff')  # 浅灰色
            
            cell.set_edgecolor('#f0f0f0')
            cell.set_linewidth(1)
    
    # 添加标题（如果启用，但这里不显示，由 pages.py 统一绘制）
    # plt.title('动态回撤', fontsize=16, fontweight='bold', pad=20, loc='left')
    
    # 调整布局
    plt.tight_layout()
    
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


def _generate_mock_drawdown_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试动态回撤图
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
    
    n = len(dates)
    
    # 生成产品回撤数据
    # 从0%开始，9月底开始有回撤，10月中旬达到-15%，12月中旬开始大幅下降，1月初达到-23.43%最低点
    product_drawdown = []
    peak_value = 0.0  # 峰值（回撤为0）
    
    sep_30_index = (datetime(2024, 9, 30) - start_date).days
    oct_11_index = (datetime(2024, 10, 11) - start_date).days
    dec_12_index = (datetime(2024, 12, 12) - start_date).days
    jan_10_index = (datetime(2025, 1, 10) - start_date).days
    
    for i in range(n):
        date = dates[i]
        if i <= sep_30_index:
            # 8月到9月底：相对平缓，接近0%
            value = np.random.normal(0, 1)
            value = max(-2, min(2, value))
        elif i <= oct_11_index:
            # 9月底到10月中旬：快速下降到-15%
            progress = (i - sep_30_index) / (oct_11_index - sep_30_index)
            value = 0 - 15 * progress
            value += np.random.normal(0, 1)
        elif i <= dec_12_index:
            # 10月中旬到12月中旬：略有恢复，然后保持
            progress = (i - oct_11_index) / (dec_12_index - oct_11_index)
            value = -15 + 5 * progress  # 恢复到-10%
            value += np.random.normal(0, 1.5)
        elif i <= jan_10_index:
            # 12月中旬到1月10日：大幅下降到-23.43%
            progress = (i - dec_12_index) / (jan_10_index - dec_12_index)
            value = -10 - 13.43 * progress
            value += np.random.normal(0, 1)
        else:
            # 1月10日后：略有恢复
            progress = (i - jan_10_index) / (n - 1 - jan_10_index)
            value = -23.43 + 2 * progress
            value += np.random.normal(0, 0.5)
        
        value = max(-25, min(2, value))
        product_drawdown.append(value)
    
    # 生成基准（沪深300）回撤数据
    # 相对稳定，在0%到-12%之间波动
    benchmark_drawdown = []
    for i in range(n):
        date = dates[i]
        # 整体趋势：从0%开始，10月初有下降，12月有较大下降
        progress = i / (n - 1)
        base_value = 0
        if i > (datetime(2024, 10, 8) - start_date).days:
            # 10月8日后开始下降
            decline_progress = (i - (datetime(2024, 10, 8) - start_date).days) / (n - 1 - (datetime(2024, 10, 8) - start_date).days)
            base_value = -12.54 * decline_progress * 0.8
        if i > (datetime(2024, 12, 12) - start_date).days:
            # 12月12日后进一步下降
            base_value = -12.54
        
        value = base_value + np.random.normal(0, 1.5)
        value = max(-15, min(2, value))
        benchmark_drawdown.append(value)
    
    # 组装数据
    data = []
    for i, date in enumerate(dates):
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'product_drawdown': round(product_drawdown[i], 2),
            'benchmark_drawdown': round(benchmark_drawdown[i], 2)
        })
    
    return data


def _generate_mock_drawdown_table_data() -> Dict[str, Any]:
    """
    生成假数据用于测试动态回撤表格
    返回:
        Dict: 假数据字典
    """
    return {
        'product_max_drawdown': -23.43,
        'benchmark_max_drawdown': -12.54,
        'product_dd_start': '2024-12-12',
        'product_dd_end': '2025-01-10',
        'benchmark_dd_start': '2024-10-08',
        'benchmark_dd_end': '2025-01-13',
        'product_recovery_period': '-',
        'benchmark_recovery_period': '-'
    }


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成动态回撤图表...")
    output_path = plot_dynamic_drawdown_chart()
    print(f"图表已保存到: {output_path}")
    
    # 测试表格生成
    print("正在生成动态回撤表格...")
    table_path = plot_dynamic_drawdown_table()
    print(f"表格已保存到: {table_path}")

