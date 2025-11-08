"""
股票仓位时序图表生成
使用 matplotlib 生成股票仓位时序图（面积图 + 折线图，双Y轴）
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
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 10


def plot_stock_position_chart(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制股票仓位时序图（面积图 + 折线图，双Y轴）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'stock_position': 100.0,  # 股票仓位（%）
                    'top10': 85.0,            # TOP10（%）
                    'csi300': 1.23            # 沪深300指数
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
        data = _generate_mock_stock_position_data()
    
    # 解析日期和数据
    dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    stock_positions = [d['stock_position'] for d in data]
    top10_values = [d.get('top10', 0) for d in data]
    csi300_values = [d['csi300'] for d in data]
    
    # 创建图表和双Y轴
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    
    # 绘制股票仓位面积图（左Y轴，深灰色填充）
    ax1.fill_between(dates, stock_positions, 0, alpha=1, color='#929aa8', label='股票仓位')
    ax1.set_ylabel('占比', fontsize=11)
    ax1.set_ylim(0, 100)
    ax1.set_yticks([0, 20, 40, 60, 80, 100])
    ax1.set_yticklabels(['0%', '20%', '40%', '60%', '80%', '100%'])
    # 网格线：水平虚线，灰色
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
    ax1.set_xlabel('日期', fontsize=11)
    
    # 绘制TOP10折线图（左Y轴，灰色，带圆形标记）
    if any(top10_values):
        ax1.plot(dates, top10_values, color='#808080', marker='', 
                markersize=4, linewidth=1.5, label='TOP10', alpha=0.7)
    
    # 绘制沪深300折线图（右Y轴，红色，带圆形标记）
    ax2.plot(dates, csi300_values, color='#c12e34', marker='', 
             markersize=4, linewidth=1.5, label='沪深300')
    ax2.set_ylabel('沪深300', fontsize=11)
    ax2.set_ylim(0.9178, 1.2365)
    ax2.set_yticks([0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.2365])
    ax2.set_yticklabels(['0.95', '1', '1.05', '1.1', '1.15', '1.2', '1.2365'])
    
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
               ncol=3, frameon=True)
    
    # 添加标题（如果启用，但这里不显示，由 pages1.py 统一绘制）
    # if show_title:
    #     plt.title('股票仓位时序*', fontsize=16, fontweight='bold', pad=20, loc='left')
    
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


def _generate_mock_stock_position_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试股票仓位时序图
    返回:
        List: 假数据列表
    """
    # 生成日期范围（2024-08-01 到 2025-01-10，每个工作日）
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2025, 1, 10)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        # 跳过周末
        if current_date.weekday() < 5:
            dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    data = []
    
    # 定义关键日期和对应的股票仓位值（精确匹配图片）
    key_dates_stock = [
        (datetime(2024, 8, 1), 100.0),
        (datetime(2024, 9, 12), 15.0),
        (datetime(2024, 9, 24), 100.0),
        (datetime(2024, 10, 9), 60.0),
        (datetime(2024, 10, 17), 100.0),
        (datetime(2024, 10, 25), 80.0),
        (datetime(2024, 11, 4), 100.0),
        (datetime(2024, 11, 12), 60.0),
        (datetime(2024, 11, 20), 100.0),
        (datetime(2024, 11, 28), 80.0),
        (datetime(2024, 12, 6), 100.0),
        (datetime(2024, 12, 16), 80.0),
        (datetime(2024, 12, 24), 5.0),
        (datetime(2025, 1, 2), 100.0),
        (datetime(2025, 1, 10), 50.0),
    ]
    
    # 定义关键日期和对应的沪深300值（精确匹配图片）
    key_dates_csi300 = [
        (datetime(2024, 8, 1), 1.23),
        (datetime(2024, 9, 12), 0.92),
        (datetime(2024, 9, 24), 1.18),
        (datetime(2024, 10, 25), 1.12),
        (datetime(2024, 11, 4), 1.08),
        (datetime(2024, 11, 12), 1.15),
        (datetime(2024, 11, 20), 1.08),
        (datetime(2024, 11, 28), 1.12),
        (datetime(2024, 12, 6), 1.18),
        (datetime(2024, 12, 16), 1.12),
        (datetime(2024, 12, 24), 1.08),
        (datetime(2025, 1, 2), 1.05),
        (datetime(2025, 1, 10), 1.08),
    ]
    
    for i, date_str in enumerate(dates):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # 计算股票仓位（在关键点之间插值）
        stock_position = 100.0
        found = False
        for j in range(len(key_dates_stock) - 1):
            date1, value1 = key_dates_stock[j]
            date2, value2 = key_dates_stock[j + 1]
            if date1 <= date_obj <= date2:
                if date1 == date2:
                    stock_position = value1
                else:
                    progress = (date_obj - date1).days / (date2 - date1).days
                    # 使用平滑插值
                    stock_position = value1 + (value2 - value1) * progress
                found = True
                break
        
        if not found:
            if date_obj < key_dates_stock[0][0]:
                stock_position = key_dates_stock[0][1]
            elif date_obj > key_dates_stock[-1][0]:
                stock_position = key_dates_stock[-1][1]
        
        # 计算沪深300（在关键点之间插值）
        csi300 = 1.23
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
        
        # TOP10数据（大部分时间在85%左右，跟随股票仓位变化）
        top10 = stock_position * 0.85 if stock_position > 50 else stock_position * 0.8
        
        data.append({
            'date': date_str,
            'stock_position': round(stock_position, 1),
            'top10': round(top10, 1),
            'csi300': round(csi300, 4)
        })
    
    return data


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成股票仓位时序图...")
    output_path = plot_stock_position_chart()
    print(f"图表已保存到: {output_path}")

