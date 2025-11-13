"""
持股行业占比时序图表生成
使用 matplotlib 生成 100% 堆叠柱状图
显示不同行业在不同时间点的占比分布
"""

# 添加项目根目录到 Python 路径，以便正确导入模块
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from charts.font_config import setup_chinese_font
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
from calc.utils import is_trading_day
from charts.utils import calculate_xlim, calculate_date_tick_params



def plot_industry_proportion_timeseries(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制持股行业占比时序图（100% 堆叠柱状图）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    '农林牧渔': 2.5,      # 各行业占比（%）
                    '基础化工': 15.3,
                    '钢铁': 3.2,
                    '有色金属': 5.1,
                    '电子': 12.8,
                    '汽车': 4.5,
                    '家用电器': 3.2,
                    '食品饮料': 8.9,
                    '纺织服饰': 2.1,
                    '轻工制造': 6.4,
                    '医药生物': 7.8,
                    '公用事业': 2.3,
                    '交通运输': 3.5,
                    '房地产': 4.2,
                    '商贸零售': 5.6,
                    '社会服务': 2.8,
                    '银行': 3.1,
                    '非银金融': 2.4,
                    '综合': 1.2,
                    '建筑材料': 3.7,
                    '建筑装饰': 4.1,
                    # ... 其他行业
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
        data = _generate_mock_industry_timeseries_data()
    
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
    
    # 解析数据并过滤掉非交易日（节假日）
    dates_raw = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    
    # 获取所有行业名称（排除'date'键）
    # 需要从原始数据获取，因为过滤后可能为空
    if not data or len(data) == 0:
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
    
    industry_names = [key for key in data[0].keys() if key != 'date']
    
    # 只保留交易日的数据
    dates = []
    filtered_data = []
    for i, date_obj in enumerate(dates_raw):
        date_str = date_obj.strftime('%Y-%m-%d')
        if is_trading_day(date_str):
            dates.append(date_obj)
            filtered_data.append(data[i])
    
    # 检查过滤后的数据是否为空
    if not filtered_data or len(filtered_data) == 0:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, '暂无交易日数据', ha='center', va='center', fontsize=14)
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
    
    # 使用过滤后的数据
    data = filtered_data
    
    # 定义行业颜色映射 - 使用高对比度专业配色
    color_map = {
        '农林牧渔': '#2ca02c',      # 绿色
        '基础化工': '#1f77b4',      # 蓝色
        '钢铁': '#7f7f7f',          # 灰色
        '有色金属': '#9467bd',      # 紫色
        '电子': '#d62728',          # 红色
        '汽车': '#17becf',          # 青色
        '家用电器': '#ff7f0e',      # 橙色
        '食品饮料': '#e377c2',      # 粉色
        '纺织服饰': '#8c564b',      # 棕色
        '轻工制造': '#bcbd22',      # 黄绿色
        '医药生物': '#d62728',      # 红色（与电子区分）
        '公用事业': '#9467bd',      # 紫色
        '交通运输': '#17becf',      # 青色
        '房地产': '#e377c2',        # 粉色
        '商贸零售': '#2ca02c',      # 绿色
        '社会服务': '#bcbd22',      # 黄绿色
        '银行': '#ff7f0e',          # 橙色
        '非银金融': '#ffbb78',      # 浅橙色
        '综合': '#8c564b',          # 棕色
        '建筑材料': '#7f7f7f',       # 灰色
        '建筑装饰': '#aec7e8',       # 浅蓝色
        '电力设备': '#1f77b4',       # 蓝色
        '元件': '#ff7f0e',          # 橙色
        '电气设备': '#2ca02c',       # 绿色
        '机床制造': '#9467bd',       # 紫色
        '化学制药': '#d62728',       # 红色
        '纺织机械': '#17becf',       # 青色
        '汽车配件': '#e377c2',       # 粉色
        '专用机械': '#8c564b',       # 棕色
    }
    
    # 为没有定义颜色的行业分配默认颜色 - 使用专业配色方案
    professional_palette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
        '#c49c94', '#f7b6d3', '#c7c7c7', '#dbdb8d', '#9edae5'
    ]
    
    # 获取所有未定义颜色的行业
    undefined_industries = [ind for ind in industry_names if ind not in color_map]
    if undefined_industries:
        # 为未定义的行业分配专业配色
        for i, industry in enumerate(undefined_industries):
            color_map[industry] = professional_palette[i % len(professional_palette)]
    
    # 为所有行业分配颜色
    colors = [color_map.get(ind, '#808080') for ind in industry_names]
    
    # 对每个日期的数据进行归一化，确保总和为100%
    for day_data in data:
        # 计算该日期所有行业的占比总和
        total = sum([day_data.get(industry, 0.0) for industry in industry_names])
        if total > 0:
            # 如果总和不为100%，进行归一化
            if abs(total - 100.0) > 0.01:  # 允许0.01%的误差
                factor = 100.0 / total
                for industry in industry_names:
                    # 确保所有行业都有值，即使原来不存在也要设置
                    original_value = day_data.get(industry, 0.0)
                    day_data[industry] = round(original_value * factor, 2)
        else:
            # 如果总和为0，说明数据有问题，将所有行业设为0
            for industry in industry_names:
                day_data[industry] = 0.0
    
    # 提取每个行业的数据
    industry_data = {}
    for industry in industry_names:
        industry_data[industry] = [d.get(industry, 0.0) for d in data]
    
    # 过滤掉占比始终为0或很小的行业（减少图例混乱）
    # 只保留在至少一个时间点占比大于0.1%的行业
    active_industries = []
    for industry in industry_names:
        max_value = max(industry_data[industry]) if industry_data[industry] else 0.0
        if max_value > 3:  # 至少有一个时间点占比大于0.1%
            active_industries.append(industry)
    
    # 如果没有活跃行业，使用所有行业
    if not active_industries:
        active_industries = industry_names
    
    # 创建图表 - 使用更专业的样式
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor('white')
    
    # 使用数值索引绘制柱状图，使所有柱子之间间隔相等
    x_positions = np.arange(len(dates))
    bar_width = 0.8  # 柱子宽度
    
    # 计算堆叠位置
    current_bottom = np.zeros(len(dates))
    
    # 按行业顺序绘制堆叠柱状图（只绘制活跃行业）
    # 按平均占比排序，确保大占比行业在底部（更稳定）
    # 使用平均占比而不是最大占比，能更准确地反映行业的整体重要性
    active_industries_sorted = sorted(active_industries, 
                                      key=lambda ind: np.mean(industry_data[ind]) if industry_data[ind] else 0.0, 
                                      reverse=True)
    
    for i, industry in enumerate(active_industries_sorted):
        values = np.array(industry_data[industry])
        # 获取该行业在原始列表中的索引，用于颜色
        original_idx = industry_names.index(industry) if industry in industry_names else i
        ax.bar(x_positions, values, width=bar_width, bottom=current_bottom,
               label=industry, color=colors[original_idx], edgecolor='white', linewidth=0.8, alpha=0.9)
        current_bottom += values
    
    # 补齐残差到100%：活跃行业外的占比合并到“其他”
    # current_bottom 为活跃行业累计占比，单位为百分比
    residual = np.maximum(0, 100 - current_bottom)
    if np.any(residual > 0.001):
        ax.bar(
            x_positions,
            residual,
            width=bar_width,
            bottom=current_bottom,
            label='其他',
            color='#e0e0e0',
            edgecolor='white',
            linewidth=0.8,
            alpha=0.9
        )
    
    # 设置Y轴 - 优化样式
    ax.set_ylabel('占比(%)', fontsize=13, fontweight='bold', color='#1a1a1a', labelpad=12)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels(['0.00%', '20.00%', '40.00%', '60.00%', '80.00%', '100.00%'],
                       fontsize=11, color='#2c3e50')
    ax.grid(True, alpha=0.3, linestyle='-', axis='y', linewidth=0.8, color='#d0d0d0')
    ax.set_axisbelow(True)  # 网格线在柱子后面
    
    # 设置X轴刻度和标签 - 优化样式
    ax.set_xlabel('日期', fontsize=13, fontweight='bold', color='#1a1a1a', labelpad=12)
    # 使用工具函数自动计算合适的刻度间隔
    if len(dates) > 0:
        # 使用工具函数计算日期刻度参数
        tick_indices, tick_labels = calculate_date_tick_params(dates)
        
        # 设置刻度位置（使用索引位置）
        ax.set_xticks([x_positions[i] for i in tick_indices])
        
        # 设置刻度标签为对应的日期 - 优化可读性
        ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=10, color='#2c3e50')
        
        # 使用工具函数自动计算X轴范围（虽然这里用的是索引，但可以设置索引范围）
        x_min, x_max = calculate_xlim(x_positions, padding_ratio=0.02, is_date=False)
        ax.set_xlim(x_min, x_max)
    else:
        ax.set_xticks([])
        ax.set_xticklabels([])
    
    # 设置标题 - 恢复并优化
    if show_title:
        ax.set_title('持股行业占比时序', fontsize=17, fontweight='bold', 
                    pad=25, loc='center', color='#1a1a1a')
    
    # 优化图例 - 增大字体，优化布局，提高可读性
    # 只显示前15个主要行业，其余合并到"其他"
    max_legend_items = 15
    if len(active_industries_sorted) > max_legend_items:
        # 只显示前max_legend_items个行业
        legend_industries = active_industries_sorted[:max_legend_items]
        # 为图例创建对应的颜色
        legend_colors = [colors[industry_names.index(ind)] if ind in industry_names 
                        else '#808080' for ind in legend_industries]
        legend_handles = [plt.Rectangle((0,0),1,1, facecolor=color, edgecolor='white', linewidth=1.0)
                         for color in legend_colors]
        legend = ax.legend(legend_handles, legend_industries,
                 loc='upper center', bbox_to_anchor=(0.5, -0.12),
                 ncol=5, frameon=True, fontsize=11,  # 增大字体
                 title='主要行业分布', title_fontsize=14,  # 增大标题字体
                 framealpha=0.98, edgecolor='#c0c0c0',
                 facecolor='#f8f8f8',
                 columnspacing=1.5, handletextpad=0.8,
                 handlelength=1.5, borderpad=0.8)
        # 手动设置标题字体粗细（兼容旧版本matplotlib）
        if legend.get_title():
            legend.get_title().set_fontweight('bold')
            legend.get_title().set_color('#1a1a1a')
            legend.get_title().set_fontsize(14)
    else:
        # 行业数量不多，显示所有
        legend_colors = [colors[industry_names.index(ind)] if ind in industry_names 
                        else '#808080' for ind in active_industries_sorted]
        legend_handles = [plt.Rectangle((0,0),1,1, facecolor=color, edgecolor='white', linewidth=1.0)
                         for color in legend_colors]
        n_legend_cols = min(len(active_industries_sorted), 5)  # 最多5列
        legend = ax.legend(legend_handles, active_industries_sorted,
                 loc='upper center', bbox_to_anchor=(0.5, -0.12),
                 ncol=n_legend_cols, frameon=True, fontsize=11,  # 增大字体
                 title='行业分布', title_fontsize=14,  # 增大标题字体
                 framealpha=0.98, edgecolor='#c0c0c0',
                 facecolor='#f8f8f8',
                 columnspacing=1.5, handletextpad=0.8,
                 handlelength=1.5, borderpad=0.8)
        # 手动设置标题字体粗细（兼容旧版本matplotlib）
        if legend.get_title():
            legend.get_title().set_fontweight('bold')
            legend.get_title().set_color('#1a1a1a')
            legend.get_title().set_fontsize(14)
    
    # 设置图例文字颜色
    for text in legend.get_texts():
        text.set_color('#2c3e50')
        text.set_fontsize(11)
    
    # # 添加脚注
    # ax.text(0, -0.08, '☆行业因子筛选自申万一级行业', transform=ax.transAxes,
    #         ha='left', va='top', fontsize=8, style='italic')
    
    # 优化边框样式
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e0e0e0')
    ax.spines['bottom'].set_color('#e0e0e0')
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)
    
    # 调整布局，为底部图例留出更多空间
    plt.tight_layout(rect=[0, 0.15, 1, 0.98])
    
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


def _generate_mock_industry_timeseries_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试持股行业占比时序图
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
    
    # 定义行业列表
    industries = [
        '农林牧渔', '基础化工', '钢铁', '有色金属', '电子', '汽车',
        '家用电器', '食品饮料', '纺织服饰', '轻工制造', '医药生物',
        '公用事业', '交通运输', '房地产', '商贸零售', '社会服务',
        '银行', '非银金融', '综合', '建筑材料', '建筑装饰'
    ]
    
    # 为每个日期生成数据
    for i, date in enumerate(dates):
        row = {'date': date.strftime('%Y-%m-%d')}
        
        # 根据时间段设置不同的行业占比趋势
        if date < datetime(2024, 9, 1):
            # 8月：电子和基础化工占比较高
            proportions = {
                '电子': 15.0 + np.random.uniform(-2, 2),
                '基础化工': 18.0 + np.random.uniform(-2, 2),
                '轻工制造': 8.0 + np.random.uniform(-1, 1),
                '医药生物': 10.0 + np.random.uniform(-1, 1),
                '食品饮料': 12.0 + np.random.uniform(-1, 1),
                '汽车': 6.0 + np.random.uniform(-1, 1),
                '家用电器': 5.0 + np.random.uniform(-0.5, 0.5),
                '建筑材料': 4.0 + np.random.uniform(-0.5, 0.5),
                '建筑装饰': 5.0 + np.random.uniform(-0.5, 0.5),
                '商贸零售': 6.0 + np.random.uniform(-0.5, 0.5),
                '交通运输': 4.0 + np.random.uniform(-0.5, 0.5),
                '房地产': 3.0 + np.random.uniform(-0.5, 0.5),
                '银行': 2.0 + np.random.uniform(-0.5, 0.5),
                '非银金融': 1.5 + np.random.uniform(-0.3, 0.3),
                '其他': 0.5  # 其他行业
            }
        elif date < datetime(2024, 10, 15):
            # 9月到10月中旬：轻工制造和医药生物占比上升
            proportions = {
                '电子': 10.0 + np.random.uniform(-1, 1),
                '基础化工': 12.0 + np.random.uniform(-1, 1),
                '轻工制造': 15.0 + np.random.uniform(-2, 2),
                '医药生物': 14.0 + np.random.uniform(-2, 2),
                '食品饮料': 10.0 + np.random.uniform(-1, 1),
                '汽车': 5.0 + np.random.uniform(-0.5, 0.5),
                '家用电器': 4.0 + np.random.uniform(-0.5, 0.5),
                '建筑材料': 5.0 + np.random.uniform(-0.5, 0.5),
                '建筑装饰': 6.0 + np.random.uniform(-0.5, 0.5),
                '商贸零售': 7.0 + np.random.uniform(-0.5, 0.5),
                '交通运输': 4.0 + np.random.uniform(-0.5, 0.5),
                '房地产': 3.0 + np.random.uniform(-0.5, 0.5),
                '银行': 3.0 + np.random.uniform(-0.5, 0.5),
                '非银金融': 2.0 + np.random.uniform(-0.3, 0.3),
                '其他': 0.5
            }
        elif date < datetime(2024, 12, 15):
            # 10月中旬到12月中旬：各行业相对均衡
            proportions = {
                '电子': 8.0 + np.random.uniform(-1, 1),
                '基础化工': 10.0 + np.random.uniform(-1, 1),
                '轻工制造': 10.0 + np.random.uniform(-1, 1),
                '医药生物': 9.0 + np.random.uniform(-1, 1),
                '食品饮料': 9.0 + np.random.uniform(-1, 1),
                '汽车': 6.0 + np.random.uniform(-0.5, 0.5),
                '家用电器': 5.0 + np.random.uniform(-0.5, 0.5),
                '建筑材料': 6.0 + np.random.uniform(-0.5, 0.5),
                '建筑装饰': 7.0 + np.random.uniform(-0.5, 0.5),
                '商贸零售': 8.0 + np.random.uniform(-0.5, 0.5),
                '交通运输': 5.0 + np.random.uniform(-0.5, 0.5),
                '房地产': 4.0 + np.random.uniform(-0.5, 0.5),
                '银行': 4.0 + np.random.uniform(-0.5, 0.5),
                '非银金融': 3.0 + np.random.uniform(-0.3, 0.3),
                '其他': 0.5
            }
        else:
            # 12月中旬到1月：非银金融和银行占比大幅上升
            proportions = {
                '电子': 5.0 + np.random.uniform(-1, 1),
                '基础化工': 6.0 + np.random.uniform(-1, 1),
                '轻工制造': 5.0 + np.random.uniform(-1, 1),
                '医药生物': 4.0 + np.random.uniform(-0.5, 0.5),
                '食品饮料': 4.0 + np.random.uniform(-0.5, 0.5),
                '汽车': 3.0 + np.random.uniform(-0.5, 0.5),
                '家用电器': 2.0 + np.random.uniform(-0.5, 0.5),
                '建筑材料': 3.0 + np.random.uniform(-0.5, 0.5),
                '建筑装饰': 4.0 + np.random.uniform(-0.5, 0.5),
                '商贸零售': 4.0 + np.random.uniform(-0.5, 0.5),
                '交通运输': 2.0 + np.random.uniform(-0.5, 0.5),
                '房地产': 2.0 + np.random.uniform(-0.5, 0.5),
                '银行': 25.0 + np.random.uniform(-3, 3),
                '非银金融': 30.0 + np.random.uniform(-3, 3),
                '其他': 0.5
            }
        
        # 为所有行业分配占比
        total_used = sum(proportions.values())
        remaining = 100.0 - total_used
        
        # 将剩余部分分配给其他小行业
        small_industries = ['农林牧渔', '钢铁', '有色金属', '纺织服饰', 
                           '公用事业', '社会服务', '综合']
        per_small = remaining / len(small_industries) if small_industries else 0
        
        for industry in industries:
            if industry in proportions:
                row[industry] = max(0, proportions[industry])
            elif industry in small_industries:
                row[industry] = max(0, per_small + np.random.uniform(-0.2, 0.2))
            else:
                row[industry] = max(0, np.random.uniform(0.5, 2.0))
        
        # 归一化确保总和为100%
        total = sum([row[ind] for ind in industries])
        if total > 0:
            factor = 100.0 / total
            for industry in industries:
                row[industry] = round(row[industry] * factor, 2)
        
        data.append(row)
    
    return data


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成持股行业占比时序图...")
    output_path = plot_industry_proportion_timeseries()
    print(f"图表已保存到: {output_path}")

