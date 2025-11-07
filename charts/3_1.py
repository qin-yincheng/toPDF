"""
持股行业分析图表生成
使用 matplotlib 生成持股行业分析图表
包含三个部分：饼图（期末市值占比）、横向柱状图（期间平均市值占产品净资产比）、数据表格（期末持股行业风格）
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from typing import Dict, Any, Optional


def plot_market_value_pie_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 8),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制期末市值占比饼图 - 简化清晰版本
    """
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_industry_data()
    
    # 获取行业数据
    industry_data = data.get('industry_data', [])
    
    # 提取数据
    industries = [item['industry'] for item in industry_data]
    proportions = [item['proportion'] for item in industry_data]
    
    # 按比例排序，让大的切片在前面
    sorted_indices = np.argsort(proportions)[::-1]
    industries = [industries[i] for i in sorted_indices]
    proportions = [proportions[i] for i in sorted_indices]
    
    # 计算总和，如果不足100%，添加"其他行业"
    total_proportion = sum(proportions)
    if total_proportion < 100.0:
        remaining = 100.0 - total_proportion
        if remaining > 0.1:  # 只有剩余比例大于0.1%才显示
            industries.append('其他行业')
            proportions.append(remaining)
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 定义颜色映射（根据你的图片调整）
    color_map = {
        '食品饮料': '#1F497D',
        '建筑装饰': '#BFBFBF', 
        '轻工制造': '#C00000',
        '基础化工': '#FFC000',
        '商贸零售': '#70AD47',
        '电力设备': '#4472C4',
        '建筑材料': '#00B0F0',
        '纺织服饰': '#0070C0',
        '其他行业': '#7030A0'
    }
    
    colors = [color_map.get(ind, '#808080') for ind in industries]
    
    # 绘制饼图 - 只显示内部百分比，不显示外部标签
    wedges, texts, autotexts = ax.pie(
        proportions,
        labels=None,  # 不显示外部标签
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        pctdistance=0.75,  # 百分比距离圆心的距离
        wedgeprops=dict(edgecolor='white', linewidth=1),
        textprops={'fontsize': 9, 'fontweight': 'bold'}
    )
    
    # 设置百分比文字颜色
    for i, autotext in enumerate(autotexts):
        # 根据背景颜色调整文字颜色
        if industries[i] in ['食品饮料', '电力设备', '纺织服饰', '其他行业']:
            autotext.set_color('white')
        else:
            autotext.set_color('black')
    
    ax.axis('equal')
    
    # 设置标题（左对齐，避免与图例重叠）
    if show_title:
        ax.set_title('期末市值占比', fontsize=12, fontweight='bold', pad=15, loc='center')
    
    # 在图表右侧添加简洁图例
    legend_labels = [f"{ind} ({prop:.1f}%)" for ind, prop in zip(industries, proportions)]
    ax.legend(wedges, legend_labels,
              title="行业分布",
              loc="center left",
              bbox_to_anchor=(1.05, 0, 0.5, 1),
              fontsize=10,
              title_fontsize=11)
    
    # 调整布局，为图例留出空间（右侧留出20%空间给图例）
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    # 如果只需要返回 figure 对象，不保存
    if return_figure:
        return fig
    
    # 如果提供了保存路径，保存图表
    if save_path:
        plt.savefig(save_path, format='pdf', bbox_inches='tight', dpi=300)
        plt.close()
        return save_path
    else:
        return fig

def plot_average_market_value_bar_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (8, 6),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制期间平均市值占产品净资产比横向柱状图
    
    参数:
        data: 数据字典，格式与 plot_market_value_pie_chart 相同
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
        data = _generate_mock_industry_data()
    
    # 获取行业数据
    industry_data = data.get('industry_data', [])
    
    # 提取数据
    industries = [item['industry'] for item in industry_data]
    proportions = [item['proportion'] for item in industry_data]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制横向柱状图
    y_pos = np.arange(len(industries))
    bars = ax.barh(y_pos, proportions, color='#1f77b4', alpha=0.7)
    
    # 设置Y轴标签
    ax.set_yticks(y_pos)
    ax.set_yticklabels(industries)
    ax.invert_yaxis()  # 反转Y轴，使第一个行业在顶部
    
    # 设置X轴
    ax.set_xlabel('占比(%)', fontsize=10)
    ax.set_xlim(0, max(proportions) * 1.1 if proportions else 20)
    
    # 在柱状图上添加数值标签
    for i, (bar, prop) in enumerate(zip(bars, proportions)):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f'{prop:.2f}%',
                ha='left', va='center', fontsize=9)
    
    # 添加网格线
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')
    
    # 设置标题（左对齐）
    if show_title:
        ax.set_title('期间平均市值占产品净资产比', fontsize=12, fontweight='bold', pad=15, loc='center')
        # 添加副标题（在标题下方，避免重叠）
        ax.text(0.5, 1.02, '前十大行业占比', transform=ax.transAxes,
                ha='center', va='bottom', fontsize=9, style='italic')
    
    # 调整布局，为标题和副标题留出空间
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


def plot_industry_holding_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 12
):
    """
    绘制期末持股行业风格数据表格
    
    参数:
        data: 数据字典，格式为：
            {
                'industry_data': [
                    {
                        'industry': '食品饮料',
                        'combined_pe': -21.79,      # 组合PE
                        'combined_pb': 2.01,        # 组合PB
                        'industry_avg_pe': 21.10,    # 行业平均PE
                        'industry_avg_pb': 4.65,    # 行业平均PB
                        'market_value': 30.55,     # 持仓市值(万元)
                        'proportion': 19.80         # 占比(%)
                    },
                    ...
                ]
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
        data = _generate_mock_industry_data()
    
    # 获取行业数据
    industry_data = data.get('industry_data', [])
    
    # 准备表格数据
    table_data = []
    for item in industry_data:
        table_data.append([
            item.get('industry', ''),
            f"{item.get('combined_pe', 0):.2f}",
            f"{item.get('combined_pb', 0):.2f}",
            f"{item.get('industry_avg_pe', 0):.2f}",
            f"{item.get('industry_avg_pb', 0):.2f}",
            f"{item.get('market_value', 0):.2f}",
            f"{item.get('proportion', 0):.2f}"
        ])
    
    # 表头
    headers = ['分类', '组合PE', '组合PB', '行业平均PE', '行业平均PB', '持仓市值(万元)', '占比(%)']
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 使用类似 4_1.py 的方式：缩小表格，放大字体
    table_width = 0.7   # 表格宽度为图形宽度的70%
    table_total_height = 0.7  # 表格总高度
    table_fontsize = 12  # 字体大小统一为12
    
    # 计算位置（居中，但为标题和脚注留出空间）
    table_x = (1 - table_width) / 2
    table_y = 0.15  # 底部留15%给脚注，顶部留15%给标题
    
    # 绘制表格
    table = ax.table(
        cellText=table_data,
        colLabels=headers,
        cellLoc='center',
        loc='center',
        bbox=[table_x, table_y, table_width, table_total_height]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(table_fontsize)
    table.scale(1, 1.5)  # 调整行高
    
    # 设置表格样式
    for i in range(len(table_data) + 1):  # +1 包括表头
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor('#e8e8e8')
                cell.set_text_props(weight='bold', ha='center')
            else:
                # 交替行颜色
                if (i - 1) % 2 == 0:
                    cell.set_facecolor('#ffffff')
                else:
                    cell.set_facecolor('#f8f8f8')
                cell.set_text_props(ha='center')
            cell.set_edgecolor('black')
            cell.set_linewidth(0.8)
    
    # 设置标题（在顶部，左对齐）
    if show_title:
        ax.text(0, 0.98, '期末持股行业风格', transform=ax.transAxes,
                ha='left', va='top', fontsize=12, fontweight='bold')
    
    # 添加脚注（在底部，左对齐）
    ax.text(0, 0.02, '☆行业因子筛选自申万一级行业', transform=ax.transAxes,
            ha='left', va='bottom', fontsize=8, style='italic')
    
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


def _generate_mock_industry_data() -> Dict[str, Any]:
    """
    生成假数据用于测试持股行业分析图表
    返回:
        Dict: 假数据字典
    """
    return {
        'industry_data': [
            {
                'industry': '食品饮料',
                'combined_pe': -21.79,
                'combined_pb': 2.01,
                'industry_avg_pe': 21.10,
                'industry_avg_pb': 4.65,
                'market_value': 30.55,
                'proportion': 19.80
            },
            {
                'industry': '建筑装饰',
                'combined_pe': -13.72,
                'combined_pb': 1.68,
                'industry_avg_pe': 9.58,
                'industry_avg_pb': 0.78,
                'market_value': 23.71,
                'proportion': 15.36
            },
            {
                'industry': '轻工制造',
                'combined_pe': -53.84,
                'combined_pb': 1.76,
                'industry_avg_pe': 28.43,
                'industry_avg_pb': 1.86,
                'market_value': 22.46,
                'proportion': 14.55
            },
            {
                'industry': '基础化工',
                'combined_pe': -40.05,
                'combined_pb': 2.46,
                'industry_avg_pe': 29.19,
                'industry_avg_pb': 1.82,
                'market_value': 15.94,
                'proportion': 10.32
            },
            {
                'industry': '商贸零售',
                'combined_pe': -7266.27,
                'combined_pb': 31.70,
                'industry_avg_pe': 56.81,
                'industry_avg_pb': 1.69,
                'market_value': 15.69,
                'proportion': 10.16
            },
            {
                'industry': '电力设备',
                'combined_pe': -11.96,
                'combined_pb': 1.27,
                'industry_avg_pe': 46.96,
                'industry_avg_pb': 2.37,
                'market_value': 15.44,
                'proportion': 10.00
            },
            {
                'industry': '建筑材料',
                'combined_pe': -4.63,
                'combined_pb': 3.45,
                'industry_avg_pe': 34.76,
                'industry_avg_pb': 1.02,
                'market_value': 15.33,
                'proportion': 9.93
            },
            {
                'industry': '纺织服饰',
                'combined_pe': -11.37,
                'combined_pb': 3.83,
                'industry_avg_pe': 21.76,
                'industry_avg_pb': 1.72,
                'market_value': 15.24,
                'proportion': 9.87
            }
        ]
    }


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成持股行业分析图表...")
    
    # 测试饼图
    print("  生成饼图...")
    fig1 = plot_market_value_pie_chart()
    print(f"  饼图已生成")
    
    # 测试柱状图
    print("  生成柱状图...")
    fig2 = plot_average_market_value_bar_chart()
    print(f"  柱状图已生成")
    
    # 测试表格
    print("  生成表格...")
    fig3 = plot_industry_holding_table()
    print(f"  表格已生成")
    
    print("\n所有图表生成完成！")

