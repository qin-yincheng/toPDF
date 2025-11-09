"""
持股行业占比时序图表生成
使用 matplotlib 生成 100% 堆叠柱状图
显示不同行业在不同时间点的占比分布
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
    
    # 解析数据
    dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    
    # 获取所有行业名称（排除'date'键）
    industry_names = [key for key in data[0].keys() if key != 'date']
    
    # 定义行业颜色映射（根据图片描述）
    color_map = {
        '农林牧渔': '#38030d',      # 深红/栗色
        '基础化工': '#28353e',      # 深蓝/海军蓝
        '钢铁': '#5b6c8a',          # 灰蓝色
        '有色金属': '#57557b',      # 深紫色
        '电子': '#d93442',          # 红色
        '汽车': '#7d94c0',          # 浅蓝色
        '家用电器': '#1a6daf',      # 深蓝色
        '食品饮料': '#d87939',      # 橙色
        '纺织服饰': '#e8f5ee',      # 浅绿/薄荷绿
        '轻工制造': '#fff9ed',      # 粉色
        '医药生物': '#bf192f',      # 深红
        '公用事业': '#64999f',      # 青色/蓝绿色
        '交通运输': '#74b4b3',      # 浅蓝绿色
        '房地产': '#c1a1d2',        # 浅紫色
        '商贸零售': '#99b292',      # 橄榄绿
        '社会服务': '#9da983',      # 浅紫灰色
        '银行': '#b09fc9',          # 深黄/金色
        '非银金融': '#b6ac79',      # 深棕/金色
        '综合': '#b0835a',          # 浅棕色
        '建筑材料': '#a38636',       # 深黄/金色
        '建筑装饰': '#d0af22',       # 深紫色
    }
    
    # 为没有定义颜色的行业分配默认颜色
    default_colors = plt.cm.Set3(np.linspace(0, 1, len(industry_names)))
    colors = [color_map.get(ind, default_colors[i % len(default_colors)]) 
              for i, ind in enumerate(industry_names)]
    
    # 提取每个行业的数据
    industry_data = {}
    for industry in industry_names:
        industry_data[industry] = [d.get(industry, 0.0) for d in data]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 使用数值索引绘制柱状图，使所有柱子之间间隔相等
    x_positions = np.arange(len(dates))
    bar_width = 0.8  # 柱子宽度
    
    # 计算堆叠位置
    bottoms = {}
    current_bottom = np.zeros(len(dates))
    
    # 按行业顺序绘制堆叠柱状图
    for i, industry in enumerate(industry_names):
        values = np.array(industry_data[industry])
        ax.bar(x_positions, values, width=bar_width, bottom=current_bottom,
               label=industry, color=colors[i], edgecolor='white', linewidth=0.5)
        current_bottom += values
    
    # 设置Y轴
    ax.set_ylabel('占比(%)', fontsize=11)
    # ax.set_ylim(0, 100)
    # ax.set_yticks([0, 20, 40, 60, 80, 100])
    # ax.set_yticklabels(['0.00%', '20.00%', '40.00%', '60.00%', '80.00%', '100.00%'])
    ax.margins(y=0.1)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # 设置X轴
    ax.set_xlabel('日期', fontsize=11)
    if len(x_positions) > 0:
        ax.set_xlim(x_positions[0] - 0.5, x_positions[-1] + 0.5)
    
    # 设置X轴刻度为日期
    # 根据数据点数量合理设置日期刻度
    if len(dates) <= 30:
        # 数据点较少时，显示所有日期
        ax.set_xticks(x_positions)
        ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in dates], rotation=45, ha='right')
    else:
        # 数据点较多时，每10-15个工作日一个刻度
        tick_interval = max(1, len(dates) // 15)  # 大约显示15个日期标签
        tick_indices = list(range(0, len(dates), tick_interval))
        if tick_indices[-1] != len(dates) - 1:
            tick_indices.append(len(dates) - 1)  # 确保最后一个日期显示
        ax.set_xticks([x_positions[i] for i in tick_indices])
        ax.set_xticklabels([dates[i].strftime('%Y-%m-%d') for i in tick_indices], rotation=45, ha='right')
    
    # 设置标题
    # if show_title:
    #     ax.set_title('持股行业占比时序', fontsize=12, fontweight='bold', pad=15, loc='left')
    
    # 添加图例（在顶部，多列显示）
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), 
              ncol= len(industry_names), frameon=True, fontsize=8)
    
    # # 添加脚注
    # ax.text(0, -0.08, '☆行业因子筛选自申万一级行业', transform=ax.transAxes,
    #         ha='left', va='top', fontsize=8, style='italic')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # 调整布局，为图例和脚注留出空间
    plt.tight_layout(rect=[0, 0.05, 1, 0.90])
    
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

