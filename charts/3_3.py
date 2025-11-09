"""
持股行业偏离度时序图表生成
使用 matplotlib 生成持股行业偏离度时序折线图
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



def plot_industry_deviation_timeseries(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制持股行业偏离度时序图（折线图）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'deviation': 3.23  # 偏离度（%）
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
        data = _generate_mock_deviation_data()
    
    # 如果没有数据或数据为空，返回空图表
    if not data:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', fontsize=14)
        ax.axis('off')
        if return_figure:
            plt.close(fig)
            return fig
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return save_path
        plt.show()
        return None
    
    # 解析日期和数据并过滤掉非交易日（节假日）
    dates_raw = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    deviations_raw = [d['deviation'] for d in data]
    
    # 只保留交易日的数据
    dates = []
    deviations = []
    for i, date_obj in enumerate(dates_raw):
        date_str = date_obj.strftime('%Y-%m-%d')
        if is_trading_day(date_str):
            dates.append(date_obj)
            deviations.append(deviations_raw[i])
    
    # 如果数据为空，返回空图表
    if not dates or not deviations:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', fontsize=14)
        ax.axis('off')
        if return_figure:
            plt.close(fig)
            return fig
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return save_path
        plt.show()
        return None
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 设置X轴：使用索引位置，但显示日期标签
    # 这样非交易日之间的间隔会相等（比如星期五到星期一和星期一到星期二的距离相同）
    n_points = len(dates)
    x_indices = list(range(n_points))
    
    # 绘制折线图（蓝色，带圆形标记）
    ax.plot(x_indices, deviations, color='#4682B4', marker='', 
            markersize=4, linewidth=1.5, label='持股行业偏离度')
    
    # 设置Y轴
    ax.set_ylabel('占比(%)', fontsize=11)
    # 根据数据范围设置Y轴
    min_val = min(deviations)
    max_val = max(deviations)
    y_min = max(0, min_val - 0.2)
    y_max = max_val + 0.2
    # ax.set_ylim(y_min, y_max)
    ax.margins(y=0.1)
    
    # 设置Y轴刻度（根据图片描述：3.23%, 3.50%, 4.00%, 4.50%, 5.00%, 5.50%, 6.00%, 6.32%）
    # 动态生成合适的刻度
    y_range = y_max - y_min
    if y_range < 1:
        # 小范围，使用0.5%间隔
        y_ticks = np.arange(np.floor(y_min * 2) / 2, np.ceil(y_max * 2) / 2 + 0.5, 0.5)
    else:
        # 较大范围，使用1%间隔
        y_ticks = np.arange(np.floor(y_min), np.ceil(y_max) + 1, 1)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([f'{y:.2f}%' for y in y_ticks])
    
    # 添加网格线
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
    
    # 设置X轴刻度和标签
    ax.set_xlabel('日期', fontsize=11)
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
    
    # # 设置标题
    # if show_title:
    #     ax.set_title('持股行业偏离度时序', fontsize=12, fontweight='bold', pad=15, loc='left')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 添加图例（在顶部中心）
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),
              ncol=1, frameon=False, fontsize=10)
    
    # # 添加脚注
    # if show_title:
    #     # 左下角脚注
    #     ax.text(0, -0.08, '☆行业因子筛选自申万一级行业', transform=ax.transAxes,
    #             ha='left', va='top', fontsize=8, style='italic')
    #     # 右下角脚注
    #     ax.text(1, -0.08, '产品相对基准的所有行业偏离度绝对值的平均值', transform=ax.transAxes,
    #             ha='right', va='top', fontsize=8, style='italic')
    
    # 调整布局，为图例和脚注留出空间
    plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    
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


def _generate_mock_deviation_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试持股行业偏离度时序图
    根据图片描述的趋势生成数据
    返回:
        List[Dict]: 假数据列表
    """
    # 生成日期范围：从 2024-08-01 到 2025-01-07（工作日）
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2025, 1, 7)
    
    # 定义节假日
    holidays = [
        datetime(2024, 9, 15),   # 中秋节
        datetime(2024, 9, 16),   # 中秋节
        datetime(2024, 9, 17),   # 中秋节
        datetime(2024, 10, 1),   # 国庆节
        datetime(2024, 10, 2),   # 国庆节
        datetime(2024, 10, 3),   # 国庆节
        datetime(2024, 10, 4),   # 国庆节
        datetime(2024, 10, 5),   # 国庆节
        datetime(2024, 10, 6),   # 国庆节
        datetime(2024, 10, 7),   # 国庆节
        datetime(2025, 1, 1),    # 元旦
    ]
    
    # 生成工作日日期列表
    dates = []
    current_date = start_date
    while current_date <= end_date:
        weekday = current_date.weekday()
        if weekday < 5 and current_date not in holidays:
            dates.append(current_date)
        current_date += timedelta(days=1)
    
    data = []
    
    # 根据图片描述的趋势生成数据
    for i, date in enumerate(dates):
        # 计算从开始日期的天数
        days_from_start = (date - start_date).days
        
        if date < datetime(2024, 8, 12):
            # 8月1日到8月12日：从3.23%快速上升到4.8%
            progress = days_from_start / 11.0
            deviation = 3.23 + (4.8 - 3.23) * progress
        elif date < datetime(2024, 9, 23):
            # 8月12日到9月23日：在4.8%到5.0%之间波动，9月23日达到5.4%
            progress = (date - datetime(2024, 8, 12)).days / 42.0
            base = 4.8 + (5.4 - 4.8) * progress
            deviation = base + np.random.uniform(-0.1, 0.1)
        elif date < datetime(2024, 10, 9):
            # 9月23日到10月9日：从5.4%下降到4.6%
            progress = (date - datetime(2024, 9, 23)).days / 16.0
            deviation = 5.4 - (5.4 - 4.6) * progress
        elif date < datetime(2024, 11, 18):
            # 10月9日到11月18日：在3.7%到5.0%之间波动，11月18日达到5.4%
            progress = (date - datetime(2024, 10, 9)).days / 40.0
            base = 4.6 + (5.4 - 4.6) * progress
            deviation = base + np.random.uniform(-0.3, 0.3)
        elif date < datetime(2024, 12, 17):
            # 11月18日到12月17日：从5.4%波动，然后快速上升到6.3%
            progress = (date - datetime(2024, 11, 18)).days / 29.0
            if progress < 0.7:
                # 前70%时间：在5.4%附近波动
                deviation = 5.4 + np.random.uniform(-0.2, 0.2)
            else:
                # 后30%时间：快速上升到6.3%
                sub_progress = (progress - 0.7) / 0.3
                deviation = 5.4 + (6.3 - 5.4) * sub_progress
        elif date < datetime(2024, 12, 26):
            # 12月17日到12月26日：从6.3%快速下降到4.7%
            progress = (date - datetime(2024, 12, 17)).days / 9.0
            deviation = 6.3 - (6.3 - 4.7) * progress
        else:
            # 12月26日到1月7日：在4.7%到5.0%之间波动
            deviation = 4.7 + np.random.uniform(0, 0.3)
        
        # 添加小幅随机波动
        deviation += np.random.uniform(-0.05, 0.05)
        
        # 确保在合理范围内
        deviation = max(3.0, min(6.5, deviation))
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'deviation': round(deviation, 2)
        })
    
    return data


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成持股行业偏离度时序图...")
    output_path = plot_industry_deviation_timeseries()
    print(f"图表已保存到: {output_path}")

