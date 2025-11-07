"""
流动性资产时序图表生成
使用 matplotlib 生成流动性资产时序图（面积图 + 折线图，双Y轴）
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np


def setup_chinese_font() -> None:
    """
    配置matplotlib中文字体
    """
    font_list = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['font.sans-serif'] = font_list
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9


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
    
    # 解析日期和数据
    dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    liquidity_ratios = [d['liquidity_ratio'] for d in data]
    csi300_values = [d['csi300'] for d in data]
    
    # 创建图表和双Y轴
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    
    # 绘制流动性资产比例面积图（左Y轴，蓝色填充，带圆形标记）
    ax1.fill_between(dates, liquidity_ratios, 0, alpha=0.6, color='#0066CC', label='流动性资产比例')
    ax1.plot(dates, liquidity_ratios, color='#0066CC', marker='o', 
             markersize=4, linewidth=1.5, alpha=0.8)
    ax1.set_ylabel('占比(%)', fontsize=11)
    ax1.set_ylim(0.13, 100)
    ax1.set_yticks([0.13, 20, 40, 60, 80, 100])
    ax1.set_yticklabels(['0.13%', '20%', '40%', '60%', '80%', '100%'])
    # 网格线：水平虚线，灰色
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
    ax1.set_xlabel('日期', fontsize=11)
    
    # 绘制沪深300折线图（右Y轴，灰色，带圆形标记）
    ax2.plot(dates, csi300_values, color='#808080', marker='o', 
             markersize=4, linewidth=1.5, label='沪深300')
    ax2.set_ylabel('沪深300', fontsize=11)
    ax2.set_ylim(0.92, 1.24)
    ax2.set_yticks([0.92, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.24])
    ax2.set_yticklabels(['0.92', '0.95', '1', '1.05', '1.1', '1.15', '1.2', '1.24'])
    
    # 设置X轴日期格式
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 设置X轴范围
    ax1.set_xlim(dates[0], dates[-1])
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper center', bbox_to_anchor=(0.5, 1.12),
               ncol=2, frameon=True)
    
    # 添加标题（如果启用，但这里不显示，由 pages1.py 统一绘制）
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


