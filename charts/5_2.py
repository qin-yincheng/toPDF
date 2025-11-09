"""
个股持仓节点图表生成
使用 matplotlib 生成个股持仓节点表格和组合图表
包含表格和双Y轴柱状图
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
import numpy as np



def plot_stock_holding_nodes_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 8),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 12
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
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 准备表格数据
    table_data = []
    for item in nodes_data:
        table_data.append([
            item.get('node', ''),
            f"{item.get('market_value', 0):.2f}",
            f"{item.get('proportion', 0):.2f}"
        ])
    
    # 表头
    headers = ['节点', '市值(万元)', '占比(%)']
    
    # 使用类似 4_1.py 的方式：缩小表格，放大字体
    table_width = 0.7   # 表格宽度为图形宽度的70%
    table_total_height = 0.7  # 表格总高度
    table_fontsize = 12  # 字体大小统一为12
    
    # 计算位置（居中，但为标题留出空间）
    table_x = (1 - table_width) / 2
    if show_title:
        ax.text(0.5, 0.98, '个股持仓节点', transform=ax.transAxes,
                ha='center', va='top', fontsize=12, fontweight='bold')
        table_y = 0.10  # 顶部留出空间给标题
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
    table.scale(1, 1.5)  # 调整行高
    
    # 设置表格样式
    for i in range(len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor('#f0f0f0')  # 浅灰色背景
                cell.set_text_props(weight='bold', ha='center')
            else:
                # 所有数据行都是白色背景
                cell.set_facecolor('#ffffff')
                # 第一列左对齐，其他列居中
                if j == 0:
                    cell.set_text_props(ha='center')
                else:
                    cell.set_text_props(ha='center')
            
            # 细灰色边框
            cell.set_edgecolor('#f0f0f0')
            cell.set_linewidth(0.8)
    
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
    
    # 创建图表和双Y轴
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    
    # 提取数据用于绘图
    nodes = [item['node'] for item in nodes_data]
    market_values = [item['market_value'] for item in nodes_data]
    proportions = [item['proportion'] for item in nodes_data]
    
    # 设置X轴位置（分组柱状图，两个柱子之间有间隔）
    x = np.arange(len(nodes))
    width = 0.4  # 柱子宽度
    gap = 0.05  # 两个柱子之间的间隔
    
    # 绘制柱状图（市值，左Y轴，蓝色）
    bars1 = ax1.bar(x - (width + gap)/2, market_values, width=width, color='#5470c6', alpha=0.7, label='市值')
    ax1.set_ylabel('市值(万元)', fontsize=11, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    
    # 设置左Y轴范围
    max_market_value = max(market_values) if market_values else 180
    # ax1.set_ylim(0, max_market_value * 1.1)
    # # 设置左Y轴刻度（0, 30, 60, 90, 120, 150, 180）
    # ax1.set_yticks(np.arange(0, max_market_value * 1.1 + 30, 30))
    ax1.margins(y=0.1)

    # 绘制柱状图（占比，右Y轴，浅绿色）
    bars2 = ax2.bar(x + (width + gap)/2, proportions, width=width, color='#91cc75', alpha=0.7, label='占比')
    ax2.set_ylabel('占比(%)', fontsize=11, color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    
    # # 设置右Y轴范围（0%到100%）
    # ax2.set_ylim(0, 100)
    # # 设置右Y轴刻度（0%, 20%, 40%, 60%, 80%, 100%）
    # ax2.set_yticks(np.arange(0, 101, 20))
    ax2.margins(y=0.1)
    # 设置X轴
    ax1.set_xticks(x)
    ax1.set_xticklabels(nodes, rotation=0, ha='center')
    ax1.set_xlabel('节点', fontsize=11)
    
    # 添加网格线
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
    
    # 合并图例，位置在顶部中心
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper center', fontsize=10, ncol=2, frameon=False)
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax1.set_title('个股持仓节点', fontsize=12, fontweight='bold', pad=15, loc='left')
    
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

