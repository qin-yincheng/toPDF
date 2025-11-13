"""
持股行业分析图表生成
使用 matplotlib 生成持股行业分析图表
包含两个部分：饼图（期末市值占比）、横向柱状图（期间平均市值占产品净资产比）
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from charts.font_config import setup_chinese_font
import numpy as np


# 专业配色方案 - 使用协调、高对比度的颜色（金融报告风格）
# 优化后的配色：更专业、更协调、视觉层次更清晰
PROFESSIONAL_COLORS = [
    '#2E86AB',  # 深蓝色 - 主色调
    '#A23B72',  # 深紫色
    '#F18F01',  # 橙色
    '#6A994E',  # 绿色
    '#C73E1D',  # 深红色
    '#118AB2',  # 天蓝色
    '#BC4749',  # 红色
    '#F77F00',  # 橙黄色
    '#7209B7',  # 紫色
    '#06A77D',  # 青绿色
    '#3A86FF',  # 亮蓝色
    '#073B4C',  # 深蓝黑色
    '#FCBF49',  # 金黄色
    '#8338EC',  # 紫蓝色
    '#FB5607',  # 橙红色
    '#FFBE0B',  # 黄色
    '#06FFA5',  # 青绿色
    '#FF006E',  # 粉红色
]



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
    
    # 如果没有数据，返回空图表
    if not industry_data:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', fontsize=8)
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
    
    # 创建图表，使用更专业的样式
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor('white')
    
    # 使用专业配色方案
    n_colors = len(PROFESSIONAL_COLORS)
    colors = [PROFESSIONAL_COLORS[i % n_colors] for i in range(len(industries))]
    
    # 只显示较大切片的百分比（避免小切片文字拥挤）
    # 设置阈值：只显示占比大于2.5%的切片，提高可读性
    autopct_func = lambda pct: f'{pct:.1f}%' if pct >= 2.5 else ''
    
    # 绘制饼图 - 使用更专业的样式
    # 不使用explode，保持圆形不变形，通过颜色和边框突出显示
    wedges, texts, autotexts = ax.pie(
        proportions,
        labels=None,  # 不显示外部标签
        autopct=autopct_func,  # 只显示较大切片的百分比
        startangle=90,
        colors=colors,
        explode=None,  # 不使用explode，保持完美圆形
        pctdistance=0.75,  # 百分比距离圆心的距离（稍微调近，更清晰）
        shadow=False,  # 不使用阴影，保持简洁
        wedgeprops=dict(
            edgecolor='white', 
            linewidth=3.0,  # 更粗的边框，增加清晰度和层次感
            alpha=1.0  # 完全不透明，颜色更鲜艳
        ),
        textprops={
            'fontsize': 12,  # 增大字体，提高可读性
            'fontweight': 'bold',
            'color': '#ffffff'  # 默认白色，后面会根据背景调整
        }
    )
    
    # 优化百分比文字颜色和样式 - 确保可读性
    for i, (autotext, prop) in enumerate(zip(autotexts, proportions)):
        if prop >= 2.5:  # 只处理显示的百分比
            # 根据背景颜色亮度调整文字颜色
            bg_color = mcolors.to_rgb(colors[i])
            # 使用感知亮度公式（更准确）
            brightness = 0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]
            if brightness > 0.5:
                autotext.set_color('#1a1a1a')  # 深色文字
            else:
                autotext.set_color('#ffffff')  # 白色文字
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)  # 增大字体，提高可读性
    
    # 关键修复：确保饼图绘图区域严格保持正方形
    # 先设置标题和图例，然后手动调整布局确保饼图区域是正方形
    ax.axis('equal')
    ax.set_aspect('equal', adjustable='box')
    
    # 设置标题 - 更大更突出
    if show_title:
        ax.set_title('期末市值占比', fontsize=8, fontweight='bold', 
                    pad=25, loc='center', color='#1a1a1a')
    
    # 优化图例 - 更清晰的布局
    # 只显示主要行业（占比大于1.5%），其余合并，提高可读性
    legend_threshold = 1.5
    legend_items = []
    legend_labels_list = []
    other_prop = 0
    
    for i, (ind, prop) in enumerate(zip(industries, proportions)):
        if prop >= legend_threshold:
            legend_items.append(wedges[i])
            legend_labels_list.append(f"{ind} ({prop:.1f}%)")
        else:
            other_prop += prop
    
    # 如果有小行业，添加"其他"项
    if other_prop > 0.1:
        # 创建一个虚拟的wedge用于图例
        from matplotlib.patches import Patch
        other_patch = Patch(facecolor='#e0e0e0', edgecolor='white', linewidth=2.5)
        legend_items.append(other_patch)
        legend_labels_list.append(f"其他 ({other_prop:.1f}%)")
    
    # 图例布局 - 使用更合理的列数，增大字体
    n_legend_cols = min(len(legend_items), 3)  # 最多3列，更清晰
    legend = ax.legend(legend_items, legend_labels_list,
              title="行业分布",
              loc="upper center",
              bbox_to_anchor=(0.5, -0.10),
              ncol=n_legend_cols,
              frameon=True,
              fontsize=6,  # 统一字体大小
              title_fontsize=8,  # 统一标题字体大小
              framealpha=0.98,
              edgecolor='#d0d0d0',
              facecolor='#fafafa',
              columnspacing=2.0,
              handletextpad=1.2,
              handlelength=1.8,
              borderpad=1.0)
    # 手动设置标题字体粗细（兼容旧版本matplotlib）
    if legend.get_title():
        legend.get_title().set_fontweight('bold')
        legend.get_title().set_color('#1a1a1a')
        legend.get_title().set_fontsize(15)
    
    # 设置图例文字颜色和大小
    for text in legend.get_texts():
        text.set_color('#2c3e50')
        text.set_fontsize(12)
    
    # 关键修复：手动调整布局，确保饼图绘图区域严格保持正方形
    # 不使用tight_layout，因为它会改变宽高比
    fig_width, fig_height = figsize
    fig_aspect = fig_width / fig_height
    
    # 为标题预留空间（顶部，单位：figure高度的分数）
    top_space = 0.15 if show_title else 0.05
    # 为图例预留空间（底部，单位：figure高度的分数）
    bottom_space = 0.22
    
    # 计算可用的绘图区域（单位：figure的分数）
    available_height = 1.0 - top_space - bottom_space
    available_width = 1.0
    
    # 确保绘图区域是正方形
    # 如果figure是正方形，绘图区域也应该是正方形
    if abs(fig_aspect - 1.0) < 0.01:  # figure是正方形（允许小误差）
        # figure是正方形，确保绘图区域也是正方形
        plot_size = min(available_width, available_height)
        left = (1.0 - plot_size) / 2
        bottom = bottom_space
        width = plot_size
        height = plot_size
    else:
        # figure不是正方形，需要调整
        # 计算在figure坐标系中，正方形绘图区域的大小
        plot_width_in_fig = min(available_width, available_height * fig_aspect)
        plot_height_in_fig = plot_width_in_fig / fig_aspect
        
        left = (1.0 - plot_width_in_fig) / 2
        bottom = bottom_space + (available_height - plot_height_in_fig) / 2
        width = plot_width_in_fig
        height = plot_height_in_fig
    
    # 验证参数有效性
    import math
    if any(math.isnan(x) or math.isinf(x) for x in [left, bottom, width, height]):
        # 如果参数无效，使用默认位置
        left, bottom, width, height = 0.1, 0.1, 0.8, 0.8
    # 确保参数在有效范围内
    left = max(0.0, min(1.0, left))
    bottom = max(0.0, min(1.0, bottom))
    width = max(0.1, min(1.0, width))
    height = max(0.1, min(1.0, height))
    
    # 手动设置subplot位置，确保饼图区域是正方形
    ax.set_position([left, bottom, width, height])
    
    # 再次确保饼图是圆形
    ax.axis('equal')
    ax.set_aspect('equal', adjustable='box')
    
    # 如果只需要返回 figure 对象，不保存
    if return_figure:
        return fig
    
    # 如果提供了保存路径，保存图表
    if save_path:
        # 关键修复：不使用bbox_inches='tight'，保持固定宽高比
        # 省略 bbox_inches 参数来保持固定边界（使用默认值）
        plt.savefig(save_path, format='pdf', dpi=300, facecolor='white')
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
    
    # 如果没有数据，返回空图表
    if not industry_data:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', fontsize=8)
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
    
    # 提取数据
    industries = [item['industry'] for item in industry_data]
    proportions = [item['proportion'] for item in industry_data]
    
    # 创建图表，使用更专业的样式
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor('white')
    
    # 使用与饼图协调的专业配色方案
    # 按比例排序后，使用与饼图相同的颜色方案，保持视觉一致性
    # 创建(行业, 比例)对，按比例排序
    industry_prop_pairs = list(zip(industries, proportions))
    sorted_pairs = sorted(industry_prop_pairs, key=lambda x: x[1], reverse=True)
    
    # 使用与饼图相同的颜色方案，按比例分配
    n_colors = len(PROFESSIONAL_COLORS)
    color_map = {}
    for idx, (ind, prop) in enumerate(sorted_pairs):
        # 使用行业名称作为键，避免比例重复的问题
        color_map[ind] = PROFESSIONAL_COLORS[idx % n_colors]
    
    # 为每个行业分配颜色（按原始顺序）
    colors = [color_map[ind] for ind in industries]
    
    # 绘制横向柱状图 - 使用专业配色
    y_pos = np.arange(len(industries))
    bars = ax.barh(y_pos, proportions, color=colors, alpha=0.9, 
                   edgecolor='white', linewidth=2.0)
    
    # 设置Y轴标签 - 优化样式
    ax.set_yticks(y_pos)
    ax.set_yticklabels(industries, fontsize=7, color='#2c3e50', fontweight='normal')
    ax.invert_yaxis()  # 反转Y轴，使第一个行业在顶部
    
    # 设置X轴 - 优化样式
    ax.set_xlabel('占比(%)', fontsize=7, fontweight='bold', color='#1a1a1a', labelpad=15)
    ax.set_xlim(0, max(proportions) * 1.15 if proportions else 20)
    
    # 在柱状图上添加数值标签 - 优化可读性
    max_prop = max(proportions) if proportions else 1
    for i, (bar, prop) in enumerate(zip(bars, proportions)):
        width = bar.get_width()
        # 根据柱子宽度决定标签位置（内部或外部）
        if width < max_prop * 0.08:
            # 小柱子，标签放在外部
            ax.text(width + max_prop * 0.02, bar.get_y() + bar.get_height()/2, 
                    f'{prop:.2f}%',
                    ha='left', va='center', fontsize=7, fontweight='bold', color='#2c3e50')
        else:
            # 大柱子，标签放在内部（白色文字）
            ax.text(width - max_prop * 0.02, bar.get_y() + bar.get_height()/2, 
                    f'{prop:.2f}%',
                    ha='right', va='center', fontsize=7, fontweight='bold', color='white')
    
    # 添加网格线 - 更专业的样式
    ax.grid(True, alpha=0.25, linestyle='-', axis='x', linewidth=0.8, color='#d0d0d0')
    ax.set_axisbelow(True)  # 网格线在柱子后面
    
    # 设置标题 - 更大更突出
    if show_title:
        ax.set_title('期间平均市值占产品净资产比', fontsize=8, fontweight='bold', 
                    pad=30, loc='center', color='#1a1a1a')

    # 优化边框样式
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e0e0e0')
    ax.spines['bottom'].set_color('#e0e0e0')
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)
    
    # 调整布局
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    
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
    
    print("\n所有图表生成完成！")

