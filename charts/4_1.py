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

# 专业配色方案
COLOR_PRIMARY = '#1e40af'      # 主色：更深的蓝色（选择收益）- 提升对比度
COLOR_SECONDARY = '#64748b'    # 次色：更深的灰色（配置收益）- 提升可读性
COLOR_GRID = '#e2e8f0'         # 网格线颜色 - 更柔和
COLOR_AXIS = '#94a3b8'         # 坐标轴颜色 - 更清晰
COLOR_BG_LIGHT = '#f8fafc'     # 浅色背景 - 更纯净
# 表格颜色（与1_5.py保持一致）
COLOR_TABLE_HEADER = '#eef2fb' # 表格标题背景（浅蓝灰色）
COLOR_TABLE_HEADER_TEXT = '#1f2d3d' # 表格标题文字颜色
COLOR_TABLE_ROW1 = '#ffffff'   # 表格行1背景（偶数行）
COLOR_TABLE_ROW2 = '#f6f7fb'   # 表格行2背景（奇数行，斑马纹）
COLOR_TABLE_BORDER = '#e2e7f1' # 表格边框颜色
COLOR_TEXT_PRIMARY = '#1a2233' # 主要文字颜色
COLOR_TEXT_SECONDARY = '#475569' # 次要文字颜色



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
    
    # 创建图表，设置背景色和更精细的布局
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor(COLOR_BG_LIGHT)
    
    # 设置X轴：使用索引位置，但显示日期标签
    # 这样非交易日之间的间隔会相等（比如星期五到星期一和星期一到星期二的距离相同）
    n_points = len(dates)
    x_indices = list(range(n_points))
    
    # 绘制选择收益折线图（深蓝色，更粗的线条，提升视觉冲击力）
    ax.plot(x_indices, selection_returns, color=COLOR_PRIMARY, marker='', 
            linewidth=3.0, label='选择收益', zorder=3, alpha=0.95)
    
    # 绘制配置收益折线图（中性灰，更粗的线条）
    ax.plot(x_indices, allocation_returns, color=COLOR_SECONDARY, marker='', 
            linewidth=3.0, label='配置收益', zorder=3, alpha=0.95)
    
    # 设置Y轴标签（更大的字体，更好的位置）
    ax.set_ylabel('累计收益率(%)', fontsize=14, color=COLOR_TEXT_PRIMARY, 
                  fontweight='medium', labelpad=12)
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
    
    # 优化边距，给图表更多呼吸空间
    ax.margins(y=0.12, x=0.02)

    # 添加网格线（实线，更清晰，更柔和）
    ax.grid(True, alpha=0.35, linestyle='-', linewidth=0.9, axis='y', 
            color=COLOR_GRID, zorder=0, which='major')
    
    # 设置X轴刻度和标签（更大的字体，更好的间距）
    ax.set_xlabel('日期', fontsize=14, color=COLOR_TEXT_PRIMARY, 
                  fontweight='medium', labelpad=10)
    # 使用工具函数自动计算合适的刻度间隔
    if n_points > 0:
        # 使用工具函数计算日期刻度参数
        tick_indices, tick_labels = calculate_date_tick_params(dates)
        
        # 设置刻度位置
        ax.set_xticks(tick_indices)
        
        # 设置刻度标签为对应的日期（更大的字体，更好的颜色）
        ax.set_xticklabels(tick_labels, rotation=45, ha='right', 
                           fontsize=11, color=COLOR_TEXT_SECONDARY)
        
        # 使用工具函数自动计算X轴范围（虽然这里用的是索引，但可以设置索引范围）
        x_min, x_max = calculate_xlim(x_indices, padding_ratio=0.02, is_date=False)
        ax.set_xlim(x_min, x_max)
    else:
        ax.set_xticks([])
        ax.set_xticklabels([])
    
    # 设置Y轴刻度标签样式（更大的字体，更好的颜色）
    ax.tick_params(axis='y', labelsize=11, colors=COLOR_TEXT_SECONDARY, 
                   length=4, width=1, pad=6)
    ax.tick_params(axis='x', labelsize=11, colors=COLOR_TEXT_SECONDARY, 
                   length=4, width=1, pad=6)
    
    # 优化坐标轴样式（更粗的线条，更清晰）
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_AXIS)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_color(COLOR_AXIS)
    ax.spines['bottom'].set_linewidth(1.2)
    
    # 添加图例（与表格风格协调的专业样式）
    legend = ax.legend(loc='upper right', fontsize=12, 
                      frameon=True, fancybox=False, shadow=False,
                      framealpha=0.98, facecolor='white', 
                      edgecolor=COLOR_TABLE_BORDER, borderpad=1.0,
                      labelspacing=0.8, handlelength=3.0, handletextpad=0.8,
                      columnspacing=1.2)
    legend.get_frame().set_linewidth(0.6)  # 与表格边框线宽一致
    legend.get_frame().set_boxstyle('round,pad=0.5')
    
    # 调整布局（更精细的间距控制）
    plt.tight_layout(pad=2.5, rect=[0, 0, 1, 1])
    
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
    
    # 创建图表，设置背景色
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor(COLOR_BG_LIGHT)
    
    # 设置柱状图位置（优化间距，更合理的布局）
    x = np.arange(len(industries)) * 1.35
    width = 0.48  # 加宽柱子，更饱满
    gap = 0.1
    
    # 绘制分组柱状图（两个柱子并排显示，使用专业配色，更粗的边框）
    bars1 = ax.bar(x - (width + gap)/2, selection_returns, width, 
                   label='选择收益', color=COLOR_PRIMARY, alpha=1, 
                   edgecolor='white', linewidth=0.8, zorder=3)
    bars2 = ax.bar(x + (width + gap)/2, allocation_returns, width,
                   label='配置收益', color=COLOR_SECONDARY, alpha=1,
                   edgecolor='white', linewidth=0.8, zorder=3)
    
    # 添加数据标签（在柱顶显示数值，优化样式）
    all_bar_values = selection_returns + allocation_returns
    max_val = max(all_bar_values) if all_bar_values else 0
    min_val = min(all_bar_values) if all_bar_values else 0
    
    def add_value_labels(bars, ax, max_val, min_val):
        """在柱状图上添加数值标签"""
        for bar in bars:
            height = bar.get_height()
            if abs(height) > 0.1:  # 只显示大于0.1的值
                # 根据数值大小选择格式
                if abs(height) < 10:
                    label_text = f'{height:.1f}%'
                elif abs(height) < 100:
                    label_text = f'{height:.0f}%'
                else:
                    label_text = f'{int(height)}%'
                
                # 计算标签位置（柱顶上方一点）
                offset = max(max_val * 0.02, abs(min_val) * 0.02) if max_val > 0 or min_val < 0 else max_val * 0.02
                y_pos = height + offset if height >= 0 else height - offset
                
                ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                       label_text,
                       ha='center', va='bottom' if height >= 0 else 'top',
                       fontsize=9, color=COLOR_TEXT_PRIMARY, fontweight='medium',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                               edgecolor='none', alpha=0.8) if abs(height) > 50 else None)
    
    add_value_labels(bars1, ax, max_val, min_val)
    add_value_labels(bars2, ax, max_val, min_val)
    
    # 设置Y轴标签（更大的字体，更好的位置）
    ax.set_ylabel('累计收益率(%)', fontsize=14, color=COLOR_TEXT_PRIMARY, 
                  fontweight='medium', labelpad=12)
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

    # 优化边距，给数据标签留出空间
    ax.margins(y=0.2, x=0.03)
    
    # 设置X轴（更大的字体，更好的颜色）
    ax.set_xticks(x)
    ax.set_xticklabels(industries, rotation=45, ha='right', 
                       fontsize=11, color=COLOR_TEXT_SECONDARY)
    
    # 添加网格线（实线，更清晰，更柔和）
    ax.grid(True, alpha=0.35, linestyle='-', linewidth=0.9, axis='y', 
            color=COLOR_GRID, zorder=0, which='major')
    
    # 添加零轴线（更清晰的线条，更柔和的颜色）
    if y_min < 0 < y_max:
        ax.axhline(y=0, color=COLOR_SECONDARY, linewidth=1.3, zorder=2, 
                  linestyle='-', alpha=0.75)
    
    # 设置标题（如果显示，更大的字体）
    if show_title:
        ax.set_title('累计收益率(%)', fontsize=15, fontweight='bold', 
                    pad=18, loc='left', color=COLOR_TEXT_PRIMARY)

    # 优化坐标轴样式（更粗的线条，更清晰）
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_AXIS)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_color(COLOR_AXIS)
    ax.spines['bottom'].set_linewidth(1.2)
    
    # 设置Y轴刻度标签样式（更大的字体，更好的颜色）
    ax.tick_params(axis='y', labelsize=11, colors=COLOR_TEXT_SECONDARY, 
                   length=4, width=1, pad=6)
    ax.tick_params(axis='x', labelsize=11, colors=COLOR_TEXT_SECONDARY, 
                   length=4, width=1, pad=6)
    
    # 添加图例（与表格风格协调的专业样式）
    legend = ax.legend(loc='upper right', fontsize=12, 
                      frameon=True, fancybox=False, shadow=False,
                      framealpha=0.98, facecolor='white', 
                      edgecolor=COLOR_TABLE_BORDER, borderpad=1.0,
                      labelspacing=0.8, handlelength=3.0, handletextpad=0.8,
                      columnspacing=1.2)
    legend.get_frame().set_linewidth(0.6)  # 与表格边框线宽一致
    legend.get_frame().set_boxstyle('round,pad=0.5')
    
    # 调整布局（更精细的间距控制）
    plt.tight_layout(pad=2.5)
    
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
    table_fontsize: int = 16
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
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.axis('off')
    
    # 优化表格尺寸和位置（更合理的比例，适配PDF布局）
    table_width = 0.75  # 稍微加宽，使表格更饱满
    table_total_height = 0.42  # 稍微增高，提高可读性
    title_height = 0.16  # 标题高度相应调整
    
    # 计算位置（居中）
    table_x = (1 - table_width) / 2
    table_y = (1 - table_total_height) / 2
    
    # 绘制标题行（使用与1_5.py一致的颜色方案）
    title_rect = Rectangle((table_x, table_y + table_total_height - title_height), 
                          table_width, title_height,
                          facecolor=COLOR_TABLE_HEADER, 
                          edgecolor=COLOR_TABLE_HEADER,  # 标题行边框与背景色一致
                          linewidth=0,
                          transform=ax.transAxes)
    ax.add_patch(title_rect)
    ax.text(table_x + table_width/2, table_y + table_total_height - title_height/2, 
            '归因分析',
            ha='center', va='center', fontsize=table_fontsize + 2, 
            fontweight='bold', color=COLOR_TABLE_HEADER_TEXT,
            transform=ax.transAxes)
    
    # 绘制数据表格（在标题行下方）
    # 创建自定义对齐的表格数据
    table_data_formatted = []
    for row in table_data:
        # 第一列左对齐，第二列右对齐
        table_data_formatted.append([
            f'  {row[0]}',  # 左对齐：前面加空格
            f'{row[1]}  '   # 右对齐：后面加空格
        ])
    
    table = ax.table(
        cellText=table_data_formatted,
        cellLoc='left',  # 使用左对齐作为基础
        loc='center',
        bbox=[table_x, table_y, table_width, table_total_height - title_height]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(table_fontsize)
    table.scale(1, 1.6)  # 增加行高，更舒适的阅读体验
    
    # 设置表格样式（与1_5.py保持一致）
    for i in range(len(table_data)):
        for j in range(2):
            cell = table[(i, j)]
            # 斑马纹效果（与1_5.py一致：偶数行白色，奇数行浅灰）
            is_even_row = (i % 2 == 0)
            cell.set_facecolor(COLOR_TABLE_ROW1 if is_even_row else COLOR_TABLE_ROW2)
            
            # 设置文字样式和对齐
            if j == 0:
                # 第一列：左对齐，深色文字
                cell.set_text_props(ha='left', weight='medium', 
                                   fontsize=table_fontsize, color=COLOR_TEXT_PRIMARY)
                cell.PAD = 0.15
            else:
                # 第二列：右对齐，深色文字，数值加粗
                cell.set_text_props(ha='right', weight='bold', 
                                   fontsize=table_fontsize, color=COLOR_TEXT_PRIMARY)
                cell.PAD = 0.15
            
            # 设置边框（与1_5.py一致：统一边框颜色和线宽）
            cell.set_edgecolor(COLOR_TABLE_BORDER)
            cell.set_linewidth(0.6)
    
    # 调整布局（更精细的间距）
    plt.tight_layout(pad=2.0)
    
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

