"""
Brinson归因图表生成
使用 matplotlib 生成 Brinson 归因折线图
显示选择收益和配置收益的累计收益率时序
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
from matplotlib.patches import Rectangle
from datetime import datetime, timedelta
import numpy as np
from charts.utils import calculate_xlim, calculate_date_tick_params
from calc.utils import is_trading_day



def plot_brinson_attribution(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制Brinson归因图表（双折线图）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'selection_return': 0.0,    # 选择收益累计收益率（%）
                    'allocation_return': 0.0   # 配置收益累计收益率（%）
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
        data = _generate_mock_brinson_data()
    
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
    selection_returns_raw = [d['selection_return'] for d in data]
    allocation_returns_raw = [d['allocation_return'] for d in data]
    
    # 只保留交易日的数据
    dates = []
    selection_returns = []
    allocation_returns = []
    for i, date_obj in enumerate(dates_raw):
        date_str = date_obj.strftime('%Y-%m-%d')
        if is_trading_day(date_str):
            dates.append(date_obj)
            selection_returns.append(selection_returns_raw[i])
            allocation_returns.append(allocation_returns_raw[i])
    
    # 如果所有值都为空或相同，返回空图表
    if not dates or not selection_returns or not allocation_returns:
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
    
    # 绘制选择收益折线图（深蓝色，带圆形标记）
    ax.plot(x_indices, selection_returns, color='#082868', marker='', 
            markersize=4, linewidth=1.5, label='选择收益',markerfacecolor='white', markeredgecolor='#082868',
            markeredgewidth=1.5)
    
    # 绘制配置收益折线图（浅灰色，带圆形标记）
    ax.plot(x_indices, allocation_returns, color='#afb0b2', marker='', 
            markersize=4, linewidth=1.5, label='配置收益',markerfacecolor='white', markeredgecolor='#afb0b2',
            markeredgewidth=1.5)
    
    # 设置Y轴
    ax.set_ylabel('累计收益率(%)', fontsize=11)
    # 根据数据范围设置Y轴
    # all_values = selection_returns + allocation_returns
    # if len(all_values) > 0:
    #     min_val = min(all_values)
    #     max_val = max(all_values)
    #     y_min = min(0, min_val - 1)
    #     y_max = max_val + 2
    # else:
    #     y_min = -5
    #     y_max = 5
    # ax.set_ylim(y_min, y_max)
    
    
    
    # # 设置Y轴刻度（0% 到约 40%）
    # y_ticks = np.arange(0, np.ceil(y_max) + 5, 5)
    # ax.set_yticks(y_ticks)
    # ax.set_yticklabels([f'{y:.0f}%' for y in y_ticks])
    
    ax.margins(y=0.1)

    # 添加网格线（水平虚线，灰色）
    ax.grid(True, alpha=0.5, linestyle='--', linewidth=0.5, axis='y')
    
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
    
    # 设置标题
    # if show_title:
    #     ax.set_title('Brinson归因', fontsize=12, fontweight='bold', pad=15, loc='left')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 添加图例（在顶部中心）
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),
              ncol=2, frameon=False, fontsize=10)
    
    # 调整布局，为图例留出空间
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    
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


def _generate_mock_brinson_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试Brinson归因图表
    根据图片描述的趋势生成数据
    返回:
        List[Dict]: 假数据列表
    """
    # 生成日期范围：从 2024-08-01 到 2025-01-10（工作日）
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2025, 1, 10)
    
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
        days_from_start = (date - start_date).days
        
        # 选择收益（Selection Return）的趋势
        if date < datetime(2024, 9, 1):
            # 8月：从0%逐渐上升到11%
            progress = days_from_start / 22.0
            selection = 11.0 * progress
        elif date < datetime(2024, 9, 25):
            # 9月初：从11%下降到8%
            progress = (date - datetime(2024, 9, 1)).days / 24.0
            selection = 11.0 - (11.0 - 8.0) * progress
        elif date < datetime(2024, 10, 15):
            # 9月底到10月中旬：从8%开始上升
            progress = (date - datetime(2024, 9, 25)).days / 20.0
            selection = 8.0 + (12.0 - 8.0) * progress
        elif date < datetime(2024, 11, 5):
            # 10月中旬到11月初：快速上升，从12%到20%
            progress = (date - datetime(2024, 10, 15)).days / 21.0
            selection = 12.0 + (20.0 - 12.0) * progress
        elif date < datetime(2024, 12, 15):
            # 11月初到12月中旬：继续快速上升，从20%到38%
            progress = (date - datetime(2024, 11, 5)).days / 40.0
            selection = 20.0 + (38.0 - 20.0) * progress
        elif date < datetime(2024, 12, 26):
            # 12月中旬到12月底：从38%快速下降到30%
            progress = (date - datetime(2024, 12, 15)).days / 11.0
            selection = 38.0 - (38.0 - 30.0) * progress
        else:
            # 12月底到1月10日：从30%略微恢复到32%
            progress = (date - datetime(2024, 12, 26)).days / 15.0
            selection = 30.0 + (32.0 - 30.0) * progress
        
        # 添加小幅随机波动
        selection += np.random.uniform(-0.5, 0.5)
        selection = max(0, selection)
        
        # 配置收益（Allocation Return）的趋势
        if date < datetime(2024, 8, 5):
            # 8月初：短暂上升到2%
            progress = days_from_start / 4.0
            allocation = 2.0 * progress
        elif date < datetime(2024, 10, 15):
            # 8月5日到10月中旬：保持在0%附近
            allocation = np.random.uniform(-0.5, 0.5)
        elif date < datetime(2024, 12, 15):
            # 10月中旬到12月中旬：逐渐上升，从0%到6%
            progress = (date - datetime(2024, 10, 15)).days / 61.0
            allocation = 0.0 + (6.0 - 0.0) * progress
        elif date < datetime(2025, 1, 5):
            # 12月中旬到1月5日：从6%下降到1-2%
            progress = (date - datetime(2024, 12, 15)).days / 21.0
            allocation = 6.0 - (6.0 - 1.5) * progress
        else:
            # 1月5日到1月10日：下降到接近0%
            progress = (date - datetime(2025, 1, 5)).days / 5.0
            allocation = 1.5 - 1.5 * progress
        
        # 添加小幅随机波动
        allocation += np.random.uniform(-0.2, 0.2)
        allocation = max(0, allocation)
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'selection_return': round(selection, 2),
            'allocation_return': round(allocation, 2)
        })
    
    return data


def plot_brinson_industry_bar_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制各行业累计收益率柱状图（分组柱状图）
    
    参数:
        data: 数据字典，格式为：
            {
                'industry_data': [
                    {
                        'industry': '机械设备',
                        'selection_return': 2.5,    # 选择收益累计收益率（%）
                        'allocation_return': 9.0    # 配置收益累计收益率（%）
                    },
                    ...
                ]
            }
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
        data = _generate_mock_industry_brinson_data()
    
    # 获取行业数据
    industry_data = data.get('industry_data', [])
    
    # 提取数据
    industries = [item['industry'] for item in industry_data]
    selection_returns = [item['selection_return'] for item in industry_data]
    allocation_returns = [item['allocation_return'] for item in industry_data]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 设置柱状图位置（增加每组柱子之间的距离）
    x = np.arange(len(industries)) * 1.25  # 乘以1.5增加间距
    width = 0.4  # 柱子宽度
    gap = 0.07
    
    # 绘制分组柱状图（两个柱子并排显示）
    bars1 = ax.bar(x - (width + gap)/2, selection_returns, width, 
                   label='选择收益', color='#082868', alpha=1)
    bars2 = ax.bar(x + (width + gap)/2, allocation_returns, width,
                   label='配置收益', color='#afb0b2', alpha=1)
    
    # 设置Y轴
    ax.set_ylabel('累计收益率(%)', fontsize=11)
    # 根据数据范围设置Y轴
    all_values = selection_returns + allocation_returns
    if len(all_values) > 0:
        min_val = min(all_values)
        max_val = max(all_values)
        # 确保Y轴范围包含0，并且是2%的倍数（根据图片：-4%到10%）
        y_min = min(-4, int(np.floor(min_val / 2)) * 2)
        y_max = max(10, int(np.ceil(max_val / 2)) * 2)
    else:
        y_min = -4
        y_max = 10
    # ax.set_ylim(y_min, y_max)
    
    # # 设置Y轴刻度（确保包含0，间隔为2%）
    # y_ticks = np.arange(y_min, y_max + 1, 2)
    # # 确保0在刻度列表中（如果不在，添加它）
    # if 0 not in y_ticks:
    #     y_ticks = np.append(y_ticks, 0)
    #     y_ticks = np.sort(y_ticks)
    # ax.set_yticks(y_ticks)
    # ax.set_yticklabels([f'{y:.0f}%' for y in y_ticks])

    ax.margins(y=0.1)
    
    # 设置X轴
    ax.set_xticks(x)
    ax.set_xticklabels(industries, rotation=45, ha='right')
    
    # 添加网格线（先添加，这样零轴线会在网格线之上）
    ax.grid(True, alpha=0.5, linestyle='--', linewidth=0.5, axis='y', zorder=0)
    
    # 添加零轴线（在网格线之后，确保零轴线在最上层，与0%刻度对齐）
    if y_min < 0 < y_max:
        ax.axhline(y=0, color='black', linewidth=1.5, zorder=10, clip_on=False)
    
    # 设置标题
    if show_title:
        ax.set_title('累计收益率(%)', fontsize=12, fontweight='bold', pad=15, loc='left')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 添加图例
    ax.legend(loc='upper right', fontsize=10)
    
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


def plot_brinson_attribution_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (4, 1.2),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 12
):
    """
    绘制归因分析表格
    """
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_attribution_summary_data()
    
    # 准备表格数据
    table_data = [
        ['个股选择收益(%)', f"{data.get('stock_selection_return', 0):.2f}"],
        ['行业配置收益(%)', f"{data.get('industry_allocation_return', 0):.2f}"]
    ]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 方法2：保留标题行，但缩小整体表格
    table_width = 0.6   # 表格宽度为图形宽度的80%
    table_total_height = 0.3  # 表格总高度（包括标题）
    title_height = 0.1  # 标题高度
    
    # 计算位置（居中）
    table_x = (1 - table_width) / 2
    table_y = (1 - table_total_height) / 2
    
    # 绘制标题行
    title_rect = Rectangle((table_x, table_y + table_total_height - title_height), 
                          table_width, title_height,
                          facecolor='#f0f0f0', edgecolor='#f0f0f0', linewidth=0.8,
                          transform=ax.transAxes)
    ax.add_patch(title_rect)
    ax.text(table_x + table_width/2, table_y + table_total_height - title_height/2, 
            '归因分析',
            ha='center', va='center', fontsize=12, fontweight='bold',
            transform=ax.transAxes)
    
    # 绘制数据表格（在标题行下方）
    table = ax.table(
        cellText=table_data,
        cellLoc='center',
        loc='center',
        bbox=[table_x, table_y, table_width, table_total_height - title_height]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(table_fontsize)
    table.scale(1, 1.2)
    
    # 设置表格样式
    for i in range(len(table_data)):
        for j in range(2):
            cell = table[(i, j)]
            if j == 0:
                cell.set_facecolor('#ffffff')
                cell.set_text_props(ha='center', weight='normal')
            else:
                cell.set_facecolor('#ffffff')
                cell.set_text_props(ha='center')
            cell.set_edgecolor('#f0f0f0')
            cell.set_linewidth(0.8)
    
    # 调整布局
    plt.tight_layout()
    
    # 返回逻辑保持不变
    if return_figure:
        return fig
    if save_path:
        plt.savefig(save_path, format='pdf', bbox_inches='tight', dpi=300)
        plt.close()
        return save_path
    else:
        return fig


def _generate_mock_industry_brinson_data() -> Dict[str, Any]:
    """
    生成假数据用于测试各行业累计收益率柱状图
    返回:
        Dict: 假数据字典
    """
    return {
        'industry_data': [
            {'industry': '机械设备', 'selection_return': 2.5, 'allocation_return': 9.0},
            {'industry': '石油石化', 'selection_return': 3.8, 'allocation_return': 2.8},
            {'industry': '环保', 'selection_return': 0.5, 'allocation_return': 6.2},
            {'industry': '纺织服饰', 'selection_return': 5.2, 'allocation_return': 1.5},
            {'industry': '电子', 'selection_return': 7.5, 'allocation_return': -2.5},
            {'industry': '建筑装饰', 'selection_return': 4.2, 'allocation_return': -1.5},
            {'industry': '医药生物', 'selection_return': 3.8, 'allocation_return': -2.0},
            {'industry': '商贸零售', 'selection_return': 1.2, 'allocation_return': 0.8},
            {'industry': '国防军工', 'selection_return': 3.5, 'allocation_return': -1.8},
            {'industry': '房地产', 'selection_return': 0.5, 'allocation_return': 2.2},
        ]
    }


def _generate_mock_attribution_summary_data() -> Dict[str, Any]:
    """
    生成假数据用于测试归因分析表格
    返回:
        Dict: 假数据字典
    """
    return {
        'stock_selection_return': 34.33,
        'industry_allocation_return': -1.04
    }


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成Brinson归因图表...")
    output_path = plot_brinson_attribution()
    print(f"图表已保存到: {output_path}")

