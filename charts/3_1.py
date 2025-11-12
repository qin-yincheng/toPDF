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
    
    # 自动分配颜色（与3_2.py相同的逻辑）
    def generate_unique_colors(n):
        """生成n个不同的颜色"""
        colors_list = []
        # 使用多个colormap来获得更多颜色
        colormaps = [plt.cm.Set3, plt.cm.Pastel1, plt.cm.Pastel2, plt.cm.Set1, 
                     plt.cm.Set2, plt.cm.Dark2, plt.cm.Accent, plt.cm.tab10,
                     plt.cm.tab20, plt.cm.tab20b, plt.cm.tab20c]
        
        color_idx = 0
        for cmap in colormaps:
            if color_idx >= n:
                break
            # 从每个colormap中取颜色，避免重复
            for i in range(cmap.N):
                if color_idx >= n:
                    break
                colors_list.append(cmap(i))
                color_idx += 1
        
        # 如果还不够，使用HSV颜色空间均匀分布
        if len(colors_list) < n:
            remaining = n - len(colors_list)
            for i in range(remaining):
                hue = (i / remaining) % 1.0
                saturation = 0.6 + (i % 3) * 0.1  # 0.6-0.8之间变化
                value = 0.7 + (i % 2) * 0.2  # 0.7-0.9之间变化
                rgb = mcolors.hsv_to_rgb([hue, saturation, value])
                colors_list.append(rgb)
        
        return colors_list[:n]
    
    # 为所有行业自动生成颜色
    unique_colors = generate_unique_colors(len(industries))
    colors = [mcolors.to_hex(color) for color in unique_colors]
    
    # 绘制饼图 - 只显示内部百分比，不显示外部标签
    wedges, texts, autotexts = ax.pie(
        proportions,
        labels=None,  # 不显示外部标签
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        pctdistance=0.75,  # 百分比距离圆心的距离
        wedgeprops=dict(edgecolor='white', linewidth=0),
        textprops={'fontsize': 9, 'fontweight': 'bold'}
    )
    
    # 设置百分比文字颜色
    for i, autotext in enumerate(autotexts):
        # 根据背景颜色调整文字颜色
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
    
    # 如果没有数据，返回空图表
    if not industry_data:
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
    
    # 提取数据
    industries = [item['industry'] for item in industry_data]
    proportions = [item['proportion'] for item in industry_data]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 自动分配颜色（与饼图相同的逻辑）
    def generate_unique_colors(n):
        """生成n个不同的颜色"""
        colors_list = []
        # 使用多个colormap来获得更多颜色
        colormaps = [plt.cm.Set3, plt.cm.Pastel1, plt.cm.Pastel2, plt.cm.Set1, 
                     plt.cm.Set2, plt.cm.Dark2, plt.cm.Accent, plt.cm.tab10,
                     plt.cm.tab20, plt.cm.tab20b, plt.cm.tab20c]
        
        color_idx = 0
        for cmap in colormaps:
            if color_idx >= n:
                break
            # 从每个colormap中取颜色，避免重复
            for i in range(cmap.N):
                if color_idx >= n:
                    break
                colors_list.append(cmap(i))
                color_idx += 1
        
        # 如果还不够，使用HSV颜色空间均匀分布
        if len(colors_list) < n:
            remaining = n - len(colors_list)
            for i in range(remaining):
                hue = (i / remaining) % 1.0
                saturation = 0.6 + (i % 3) * 0.1  # 0.6-0.8之间变化
                value = 0.7 + (i % 2) * 0.2  # 0.7-0.9之间变化
                rgb = mcolors.hsv_to_rgb([hue, saturation, value])
                colors_list.append(rgb)
        
        return colors_list[:n]
    
    # 为所有行业自动生成颜色
    unique_colors = generate_unique_colors(len(industries))
    colors = [mcolors.to_hex(color) for color in unique_colors]
    
    # 绘制横向柱状图（每个柱子使用不同颜色）
    y_pos = np.arange(len(industries))
    bars = ax.barh(y_pos, proportions, color='#082868', alpha=1)
    
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
    ax.grid(True, alpha=0.5, linestyle='--', axis='x')
    
    # 设置标题（左对齐）
    if show_title:
        ax.set_title('期间平均市值占产品净资产比', fontsize=12, fontweight='bold', pad=15, loc='center')
    
    # 添加图例（替代副标题，位置在标题下方，避免重叠）
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#082868', label='前十大行业占比')]
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.07), ncol=1, frameon=True)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 调整布局，为标题和图例留出空间
    plt.tight_layout(rect=[0, 0, 1, 0.9])
    
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

