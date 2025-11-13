"""
个股持仓节点图表生成
使用 matplotlib 生成个股持仓节点表格和组合图表
包含表格和双Y轴柱状图
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
import numpy as np

# 专业配色方案 - 金融报告标准配色（与1_5.py保持一致）
COLOR_PRIMARY = '#2563eb'          # 主色：专业蓝色（市值柱状图）
COLOR_SECONDARY = '#059669'        # 次色：专业绿色（占比柱状图）
COLOR_GRID = '#e5e7eb'             # 网格线颜色 - 更清晰
COLOR_AXIS = '#6b7280'             # 坐标轴颜色 - 更清晰
COLOR_BG_LIGHT = '#f8fafc'         # 背景色 - 浅色更专业
# 表格配色（与1_5.py保持一致）
COLOR_TABLE_HEADER = '#eef2fb'     # 表格标题背景（浅蓝色）
COLOR_TABLE_HEADER_TEXT = '#1f2d3d' # 表格标题文字颜色（深色）
COLOR_TABLE_ROW1 = '#ffffff'       # 表格行1背景（偶数行）
COLOR_TABLE_ROW2 = '#f6f7fb'       # 表格行2背景（奇数行，与1_5.py一致）
COLOR_TABLE_BORDER = '#e2e7f1'     # 表格边框颜色（与1_5.py一致）
COLOR_TEXT_PRIMARY = '#1a2233'     # 主要文字颜色（与1_5.py一致）
COLOR_TEXT_SECONDARY = '#475569'   # 次要文字颜色



def plot_stock_holding_nodes_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 8),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 16
):
    """
    绘制个股持仓节点表格
    
    参数:
        data: 数据字典，格式为：
            {
                'nodes_data': [
                    {
                        'node': 'TOP1',
                        'market_value': 23.71,    # 市值(万元)
                        'proportion': 15.36        # 占比(%)
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
        data = _generate_mock_nodes_data()
    
    # 获取数据
    nodes_data = data.get('nodes_data', [])
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.axis('off')
    
    # 准备表格数据，优化数字格式化
    table_data = []
    for item in nodes_data:
        market_value = item.get('market_value', 0)
        proportion = item.get('proportion', 0)
        table_data.append([
            item.get('node', ''),
            f"{market_value:,.2f}" if market_value >= 1000 else f"{market_value:.2f}",  # 大数字添加千分位
            f"{proportion:.2f}"
        ])
    
    # 表头
    headers = ['节点', '市值(万元)', '占比(%)']
    
    # 优化表格尺寸和位置 - 根据figsize动态调整
    is_narrow = figsize[0] < 10
    table_width = 0.96 if is_narrow else 0.97   # 更充分利用空间
    table_total_height = 0.82 if is_narrow else 0.80  # 增加高度利用率
    table_fontsize = 12 if is_narrow else 13  # 根据宽度动态调整字体大小
    
    # 计算位置（居中，但为标题留出空间）
    table_x = (1 - table_width) / 2  # 居中
    if show_title:
        ax.text(0.5, 0.97, '个股持仓节点', transform=ax.transAxes,
                ha='center', va='top', fontsize=16, fontweight='bold', 
                color=COLOR_TEXT_PRIMARY, family='sans-serif')
        # table_y 是表格底部位置，表格高度是 table_total_height
        table_y = 0.89 - table_total_height  # 表格顶部在89%，与标题保持合理距离
    else:
        table_y = (1 - table_total_height) / 2
    
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
    # 根据表格宽度动态调整行高 - 增加行高提升可读性
    row_scale = 1.8 if is_narrow else 2.0
    table.scale(1, row_scale)  # 调整行高，使表格更舒适美观
    
    # 设置表格样式 - 专业配色（与1_5.py保持一致）
    for i in range(len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i == 0:  # 表头 - 浅蓝色背景配深色文字（与1_5.py一致）
                cell.set_facecolor(COLOR_TABLE_HEADER)
                cell.set_text_props(weight='bold', ha='center', 
                                  fontsize=table_fontsize, 
                                  color=COLOR_TABLE_HEADER_TEXT,
                                  family='sans-serif')
                # 表头边框（与1_5.py一致）
                cell.set_edgecolor(COLOR_TABLE_HEADER)
                cell.set_linewidth(0)
            else:
                # 交替行颜色（与1_5.py一致：偶数行白色，奇数行浅灰）
                is_even_row = (i % 2 == 0)
                if is_even_row:
                    cell.set_facecolor(COLOR_TABLE_ROW1)
                else:
                    cell.set_facecolor(COLOR_TABLE_ROW2)
                # 所有列居中
                cell.set_text_props(ha='center', fontsize=table_fontsize,
                                  color=COLOR_TEXT_PRIMARY,
                                  family='sans-serif')
                # 数据行边框（与1_5.py一致）
                cell.set_edgecolor(COLOR_TABLE_BORDER)
                cell.set_linewidth(0.6)
    
    # 调整布局 - 优化边距
    plt.tight_layout(pad=1.5)
    
    # 如果只需要返回 figure 对象，不保存
    if return_figure:
        return fig
    
    # 如果提供了保存路径，保存图表为 PDF（矢量格式，高清）
    if save_path:
        plt.savefig(save_path, format='pdf', bbox_inches='tight', 
                   pad_inches=0.2, dpi=300)
        plt.close()
        return save_path
    else:
        # 不保存，返回 figure 对象
        return fig


def plot_stock_holding_nodes_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制个股持仓节点组合图表（双Y轴柱状图）
    
    参数:
        data: 数据字典，格式与 plot_stock_holding_nodes_table 相同
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
        data = _generate_mock_nodes_data()
    
    # 获取数据
    nodes_data = data.get('nodes_data', [])
    
    # 创建图表和双Y轴，添加浅色背景
    fig, ax1 = plt.subplots(figsize=figsize, facecolor='white')
    ax1.set_facecolor(COLOR_BG_LIGHT)
    ax2 = ax1.twinx()
    
    # 根据图表宽度动态调整元素大小 - 提升可读性
    is_wide = figsize[0] > 10
    bar_width = 0.55 if is_wide else 0.6  # 适中的柱子宽度
    label_fontsize = 12 if is_wide else 11  # 更大的标签
    tick_fontsize = 10 if is_wide else 9  # 更大的刻度
    legend_fontsize = 10 if is_wide else 9  # 更大的图例
    data_label_fontsize = 8 if is_wide else 7  # 数据标签
    
    # 设置 axes 的 zorder，确保 ax2（占比柱状图）在上层
    ax1.set_zorder(1)
    ax2.set_zorder(2)
    # 设置 ax2 的背景透明，这样不会遮挡 ax1 的内容
    ax2.patch.set_visible(False)
    
    # 提取数据用于绘图
    nodes = [item['node'] for item in nodes_data]
    market_values = [item['market_value'] for item in nodes_data]
    proportions = [item['proportion'] for item in nodes_data]
    
    # 设置X轴位置（分组柱状图，两个柱子之间有间隔）
    x = np.arange(len(nodes))
    gap = 0.05  # 两个柱子之间的间隔
    
    # 绘制柱状图（市值，左Y轴，专业蓝色）- 先绘制，确保在底层
    bars1 = ax1.bar(x - (bar_width + gap)/2, market_values, width=bar_width, 
                   color=COLOR_PRIMARY, alpha=0.85, label='市值', zorder=1,
                   edgecolor='white', linewidth=1.2)
    
    # 添加数据标签 - 优化字体大小和位置，只在顶部显示
    max_market_value = max(market_values) if market_values else 0
    for i, (bar, value) in enumerate(zip(bars1, market_values)):
        height = bar.get_height()
        if height > max_market_value * 0.05:  # 只显示较大的值，避免拥挤
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:,.0f}' if value >= 1000 else f'{value:.0f}',
                    ha='center', va='bottom', fontsize=data_label_fontsize, 
                    color=COLOR_TEXT_PRIMARY, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                             edgecolor=COLOR_PRIMARY, alpha=0.9, linewidth=0.5))
    
    ax1.set_ylabel('市值(万元)', fontsize=label_fontsize, color=COLOR_TEXT_PRIMARY, 
                  fontweight='medium', labelpad=7)
    ax1.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=tick_fontsize)
    
    # 设置左Y轴范围
    max_market_value = max(market_values) if market_values else 180
    ax1.set_ylim(0, max_market_value * 1.15)
    ax1.margins(y=0.05)

    # 绘制柱状图（占比，右Y轴，专业绿色）- 后绘制，确保在上层
    bars2 = ax2.bar(x + (bar_width + gap)/2, proportions, width=bar_width, 
                   color=COLOR_SECONDARY, alpha=0.85, label='占比', zorder=10,
                   edgecolor='white', linewidth=1.2)
    
    # 添加数据标签 - 优化字体大小和位置
    max_proportion = max(proportions) if proportions else 0
    for i, (bar, prop) in enumerate(zip(bars2, proportions)):
        height = bar.get_height()
        if height > max_proportion * 0.05:  # 只显示较大的值，避免拥挤
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{prop:.1f}%',
                    ha='center', va='bottom', fontsize=data_label_fontsize, 
                    color=COLOR_TEXT_PRIMARY, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                             edgecolor=COLOR_SECONDARY, alpha=0.9, linewidth=0.5))
    
    ax2.set_ylabel('占比(%)', fontsize=label_fontsize, color=COLOR_TEXT_PRIMARY, 
                   fontweight='medium', labelpad=7)
    ax2.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=tick_fontsize)
    
    # 设置右Y轴范围
    max_proportion = max(proportions) if proportions else 100
    ax2.set_ylim(0, max_proportion * 1.15)
    ax2.margins(y=0.05)
    
    # 设置X轴 - 优化标签显示
    ax1.set_xticks(x)
    ax1.set_xticklabels(nodes, rotation=0, ha='center', fontsize=tick_fontsize,
                       color=COLOR_TEXT_PRIMARY)
    ax1.set_xlabel('节点', fontsize=label_fontsize-1, color=COLOR_TEXT_PRIMARY, 
                   fontweight='medium', labelpad=5)
    ax1.tick_params(axis='x', colors=COLOR_TEXT_SECONDARY, labelsize=tick_fontsize)
    
    # 添加专业网格线 - 与1_5.py风格保持一致（更柔和）
    ax1.grid(True, alpha=0.25, linestyle='--', linewidth=0.8, 
            color='#b9c2d3', axis='y', zorder=0)
    ax1.set_axisbelow(True)
    
    # 优化坐标轴样式 - 与1_5.py风格保持一致
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color('#b9c2d3')
    ax1.spines['bottom'].set_color('#b9c2d3')
    ax1.spines['left'].set_linewidth(1.2)
    ax1.spines['bottom'].set_linewidth(1.2)
    
    # 合并图例 - 优化位置和样式，更专业（与整体风格协调）
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper left', fontsize=legend_fontsize, frameon=True, 
               fancybox=False, shadow=False, framealpha=0.95,
               edgecolor='#e2e7f1', facecolor='white',
               handlelength=2.0, handletextpad=0.5, columnspacing=1.0,
               borderpad=0.5, labelspacing=0.5)
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax1.set_title('个股持仓节点', fontsize=12, fontweight='bold', pad=15, loc='left')
    
    # 调整布局 - 优化边距，使图表更紧凑
    plt.tight_layout(pad=1.2)
    
    # 如果只需要返回 figure 对象，不保存
    if return_figure:
        return fig
    
    # 如果提供了保存路径，保存图表为 PDF（矢量格式，高清）
    if save_path:
        plt.savefig(save_path, format='pdf', bbox_inches='tight', 
                   pad_inches=0.2, dpi=300)
        plt.close()
        return save_path
    else:
        # 不保存，返回 figure 对象
        return fig


def _generate_mock_nodes_data() -> Dict[str, Any]:
    """
    生成假数据用于测试个股持仓节点
    返回:
        Dict: 假数据字典
    """
    return {
        'nodes_data': [
            {'node': 'TOP1', 'market_value': 23.71, 'proportion': 15.36},
            {'node': 'TOP2', 'market_value': 46.17, 'proportion': 29.91},
            {'node': 'TOP3', 'market_value': 62.11, 'proportion': 40.24},
            {'node': 'TOP5', 'market_value': 93.23, 'proportion': 60.40},
            {'node': 'TOP10', 'market_value': 154.35, 'proportion': 100.00},
            {'node': 'TOP50', 'market_value': 154.35, 'proportion': 100.00},
            {'node': 'TOP100', 'market_value': 154.35, 'proportion': 100.00},
        ]
    }


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成个股持仓节点图表...")
    fig1 = plot_stock_holding_nodes_table()
    fig2 = plot_stock_holding_nodes_chart()
    print("图表生成成功")

