"""
期间交易图表生成
使用 matplotlib 生成期间交易表格和分组柱状图
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
from matplotlib.patches import Rectangle
import numpy as np



def plot_period_transaction_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 4),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 12
):
    """
    绘制期间交易表格
    
    参数:
        data: 数据字典，格式为：
            {
                'transaction_data': [
                    {
                        'asset_class': '股票',
                        'buy_amount': 1353.91,    # 买入金额(万元)
                        'sell_amount': 1257.53    # 卖出金额(万元)
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
        data = _generate_mock_transaction_data()
    
    # 获取数据
    transaction_data = data.get('transaction_data', [])
    
    # 准备表格数据
    table_data = []
    for item in transaction_data:
        table_data.append([
            item.get('asset_class', ''),
            f"{item.get('buy_amount', 0):.2f}",
            f"{item.get('sell_amount', 0):.2f}"
        ])
    
    # 表头
    headers = ['资产分类', '买入金额(万元)', '卖出金额(万元)']
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 使用类似 4_1.py 的方式：缩小表格，放大字体
    table_width = 0.7   # 表格宽度为图形宽度的70%
    table_total_height = 0.7  # 表格总高度
    table_fontsize = 12  # 字体大小统一为12
    
    # 计算位置（居中）
    table_x = (1 - table_width) / 2
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
    for i in range(len(table_data) + 1):  # +1 包括表头
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor('#f0f0f0')  # 浅灰色背景
                cell.set_text_props(weight='bold', ha='center')
            else:
                # 所有数据行都是白色背景
                cell.set_facecolor('#ffffff')
                
                # 第一列（资产分类）左对齐，数值列右对齐
                if j == 0:
                    cell.set_text_props(ha='center')
                else:
                    cell.set_text_props(ha='center')  # 数值列右对齐
            
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


def plot_period_transaction_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制期间交易分组柱状图
    
    参数:
        data: 数据字典，格式与 plot_period_transaction_table 相同
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
        data = _generate_mock_transaction_data()
    
    # 获取数据
    transaction_data = data.get('transaction_data', [])
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 提取数据用于绘图
    asset_classes = [item['asset_class'] for item in transaction_data]
    buy_amounts = [item['buy_amount'] for item in transaction_data]
    sell_amounts = [item['sell_amount'] for item in transaction_data]
    
    # 设置X轴位置（分组柱状图，两个柱子之间有间隔）
    x = np.arange(len(asset_classes))
    width = 0.35  # 柱子宽度
    gap = 0.1  # 两个柱子之间的间隔
    
    # 绘制柱状图（买入，深蓝色）
    bars1 = ax.bar(x - (width + gap)/2, buy_amounts, width=width, 
                   color='#082868', alpha=0.9, label='买入')
    
    # 绘制柱状图（卖出，浅灰色）
    bars2 = ax.bar(x + (width + gap)/2, sell_amounts, width=width, 
                   color='#808080', alpha=0.7, label='卖出')
    
    # 设置Y轴
    ax.set_ylabel('万元', fontsize=11)
    max_amount = max(max(buy_amounts) if buy_amounts else 0, 
                     max(sell_amounts) if sell_amounts else 0)
    # ax.set_ylim(0, max_amount * 1.1)
    # # 设置Y轴刻度（0, 300, 600, 900, 1200, 1500）
    # ax.set_yticks(np.arange(0, max_amount * 1.1 + 300, 300))
    ax.margins(y=0.1)
    
    # 设置X轴
    ax.set_xticks(x)
    ax.set_xticklabels(asset_classes, rotation=0, ha='center')
    ax.set_xlabel('资产分类', fontsize=11)
    
    # 添加网格线
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
    
    # 图例在顶部中心
    ax.legend(loc='upper center', fontsize=10, ncol=2, frameon=False)
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax.set_title('期间交易', fontsize=12, fontweight='bold', pad=15, loc='left')
    
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


def _generate_mock_transaction_data() -> Dict[str, Any]:
    """
    生成假数据用于测试期间交易
    返回:
        Dict: 假数据字典
    """
    return {
        'transaction_data': [
            {
                'asset_class': '股票',
                'buy_amount': 1353.91,
                'sell_amount': 1257.53
            },
            {
                'asset_class': '基金',
                'buy_amount': 79.19,
                'sell_amount': 79.15
            },
            {
                'asset_class': '逆回购',
                'buy_amount': 66.10,
                'sell_amount': 0.00
            }
        ]
    }


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成期间交易表格和图表...")
    fig1 = plot_period_transaction_table()
    fig2 = plot_period_transaction_chart()
    print("图表生成成功")

