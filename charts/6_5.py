"""
期间交易图表生成
使用 matplotlib 生成期间交易表格和分组柱状图
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
from matplotlib.patches import Rectangle
import numpy as np

# 专业配色方案 - 金融报告标准配色
COLOR_PRIMARY = '#2563eb'            # 主色：专业蓝色（买入柱状图）
COLOR_SECONDARY = '#6b7280'           # 次色：专业灰色（卖出柱状图）
COLOR_GRID = '#e5e7eb'                # 网格线颜色 - 更清晰
COLOR_AXIS = '#6b7280'                # 坐标轴颜色 - 更清晰
COLOR_BG_LIGHT = '#ffffff'            # 背景色 - 纯白更专业
# 表格配色（与1_5.py保持一致）
COLOR_TABLE_HEADER = '#eef2fb'        # 表格标题背景（浅灰色）- 与1_5一致
COLOR_TABLE_HEADER_TEXT = '#1f2d3d'   # 表格标题文字颜色（深色）- 与1_5一致
COLOR_TABLE_ROW1 = '#ffffff'          # 表格行1背景（白色）
COLOR_TABLE_ROW2 = '#f6f7fb'         # 表格行2背景（浅灰色斑马纹）- 与1_5一致
COLOR_TABLE_BORDER = '#e2e7f1'       # 表格边框颜色 - 与1_5一致
COLOR_TEXT_PRIMARY = '#1a2233'       # 主要文字颜色 - 与1_5一致
COLOR_TEXT_SECONDARY = '#475569'     # 次要文字颜色



def plot_period_transaction_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 4),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 16
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
    
    # 准备表格数据，优化数字格式化（添加千分位分隔符）
    table_data = []
    for item in transaction_data:
        buy_amount = item.get('buy_amount', 0)
        sell_amount = item.get('sell_amount', 0)
        table_data.append([
            item.get('asset_class', ''),
            f"{buy_amount:,.2f}",  # 添加千分位分隔符
            f"{sell_amount:,.2f}"   # 添加千分位分隔符
        ])
    
    # 表头
    headers = ['资产分类', '买入金额(万元)', '卖出金额(万元)']
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 优化表格尺寸和位置 - 根据figsize动态调整
    is_narrow = figsize[0] < 10
    table_width = 0.96 if is_narrow else 0.97   # 更充分利用空间
    table_total_height = 0.85 if is_narrow else 0.83  # 增加高度利用率，使表格更饱满
    # 根据图表大小动态调整字体，使其更易读和专业
    if figsize[0] >= 20:
        table_fontsize = 18  # 大图表使用大字体
    elif figsize[0] >= 15:
        table_fontsize = 16  # 中等图表
    elif figsize[0] >= 10:
        table_fontsize = 14  # 小图表
    else:
        table_fontsize = 12  # 很窄的图表
    
    # 计算位置（居中，但为标题留出空间）
    table_x = (1 - table_width) / 2  # 居中
    if show_title:
        ax.text(0.5, 0.97, '期间交易', transform=ax.transAxes,
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
    # 根据表格宽度动态调整行高 - 增加行高提升可读性和专业感
    row_scale = 2.2 if is_narrow else 2.5  # 增加行高，使表格更舒适美观
    table.scale(1, row_scale)  # 调整行高，使表格更舒适美观
    
    # 设置表格样式 - 专业配色
    for i in range(len(table_data) + 1):  # +1 包括表头
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i == 0:  # 表头 - 浅灰色背景配深色文字（与1_5一致）
                cell.set_facecolor(COLOR_TABLE_HEADER)
                cell.set_text_props(weight='bold', ha='center', 
                                  fontsize=table_fontsize, 
                                  color=COLOR_TABLE_HEADER_TEXT,
                                  family='sans-serif')
                # 表头边框
                cell.set_edgecolor(COLOR_TABLE_HEADER)
                cell.set_linewidth(0)
            else:
                # 交替行颜色 - 增强对比度
                if (i - 1) % 2 == 0:
                    cell.set_facecolor(COLOR_TABLE_ROW1)
                else:
                    cell.set_facecolor(COLOR_TABLE_ROW2)
                # 所有列居中
                cell.set_text_props(ha='center', fontsize=table_fontsize,
                                  color=COLOR_TEXT_PRIMARY,
                                  family='sans-serif')
                # 数据行边框（与1_5一致）
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
    
    # 根据图表大小动态调整元素尺寸
    is_wide = figsize[0] > 8
    bar_width = 0.4 if is_wide else 0.35  # 适中的柱子宽度
    gap = 0.08 if is_wide else 0.1  # 两个柱子之间的间隔
    
    # 设置X轴位置（分组柱状图，两个柱子之间有间隔）
    x = np.arange(len(asset_classes))
    
    # 优化颜色：使用更专业的蓝色和灰色，与整体风格一致
    color_buy = '#1f3c88'  # 深蓝色，与1_5.py一致，更专业稳重
    color_sell = '#64748b'  # 中性灰蓝色，更柔和专业
    
    # 绘制柱状图（买入，专业深蓝色）
    bars1 = ax.bar(x - (bar_width + gap)/2, buy_amounts, width=bar_width, 
                   color=color_buy, alpha=0.95, label='买入',
                   edgecolor='white', linewidth=1.0, zorder=3)
    
    # 绘制柱状图（卖出，专业灰蓝色）
    bars2 = ax.bar(x + (bar_width + gap)/2, sell_amounts, width=bar_width, 
                   color=color_sell, alpha=0.9, label='卖出',
                   edgecolor='white', linewidth=1.0, zorder=3)
    
    # 设置Y轴 - 优化格式化
    max_amount = max(max(buy_amounts) if buy_amounts else 0, 
                     max(sell_amounts) if sell_amounts else 0)
    
    # 根据图表大小动态调整字体
    label_fontsize = 16 if is_wide else 14  # Y轴标签字体
    tick_fontsize = 14 if is_wide else 12  # 刻度字体
    xlabel_fontsize = 15 if is_wide else 13  # X轴标签字体
    legend_fontsize = 13 if is_wide else 11  # 图例字体
    
    # 根据数值大小决定Y轴标签格式（单位已经是"万元"）
    if max_amount >= 10000:
        # 如果数值很大（>=1万万元=1亿元），使用"百万元"作为单位
        ax.set_ylabel('百万元', fontsize=label_fontsize, color=COLOR_TEXT_PRIMARY, 
                     family='sans-serif', fontweight='medium', labelpad=10)
        # 转换Y轴刻度标签：万元转百万元（除以100）
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/100:,.0f}'))
    elif max_amount >= 1000:
        # 如果数值较大（>=1000万元），使用千分位格式化
        ax.set_ylabel('万元', fontsize=label_fontsize, color=COLOR_TEXT_PRIMARY, 
                     family='sans-serif', fontweight='medium', labelpad=10)
        # 使用千分位格式化
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
    else:
        # 数值较小，保持万元单位
        ax.set_ylabel('万元', fontsize=label_fontsize, color=COLOR_TEXT_PRIMARY, 
                     family='sans-serif', fontweight='medium', labelpad=10)
    
    ax.margins(y=0.12)  # 增加上边距，使图表更舒适
    
    # 设置X轴 - 优化样式
    ax.set_xticks(x)
    ax.set_xticklabels(asset_classes, rotation=0, ha='center', 
                      fontsize=tick_fontsize, color=COLOR_TEXT_PRIMARY, family='sans-serif')
    ax.set_xlabel('资产分类', fontsize=xlabel_fontsize, color=COLOR_TEXT_PRIMARY, 
                  family='sans-serif', fontweight='medium')
    
    # 设置坐标轴样式 - 更专业，只保留必要的边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#b9c2d3')  # 更柔和的边框颜色
    ax.spines['bottom'].set_linewidth(1.2)
    ax.spines['left'].set_color('#b9c2d3')
    ax.spines['left'].set_linewidth(1.2)
    ax.tick_params(colors=COLOR_TEXT_PRIMARY, labelsize=tick_fontsize, 
                  length=6, width=1.2)
    
    # 添加网格线 - 优化样式，更柔和专业
    ax.grid(True, alpha=0.25, linestyle='--', linewidth=0.8, axis='y', 
           color='#b9c2d3', zorder=1)
    ax.set_axisbelow(True)  # 网格线在图表下方
    
    # 设置背景色
    ax.set_facecolor(COLOR_BG_LIGHT)
    fig.patch.set_facecolor('white')
    
    # 图例 - 优化样式，更专业
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.08), 
                      fontsize=legend_fontsize, ncol=2, 
                      frameon=False,  # 无边框，更简洁
                      labelcolor=COLOR_TEXT_PRIMARY)
    for text in legend.get_texts():
        text.set_family('sans-serif')
        text.set_fontweight('medium')
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax.set_title('期间交易', fontsize=12, fontweight='bold', pad=15, loc='left')
    
    # 调整布局 - 优化边距
    plt.tight_layout(pad=1.5)
    
    # 如果只需要返回 figure 对象，不保存
    if return_figure:
        return fig
    
    # 如果提供了保存路径，保存图表为 PDF（矢量格式，高清）
    if save_path:
        plt.savefig(save_path, format='pdf', bbox_inches='tight', 
                   pad_inches=0.2, dpi=300, facecolor=COLOR_BG_LIGHT)
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

