"""
股票绩效归因图表生成
使用 matplotlib 生成股票绩效归因表格和组合图表
包含盈利前十和亏损前十两个部分
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
import numpy as np

# 专业配色方案 - 金融报告标准配色（更专业柔和的配色）
COLOR_PRIMARY = '#1f3c88'          # 主色：深蓝色（柱状图-盈利）- 与1_5.py一致，更专业稳重
COLOR_PRIMARY_LOSS = '#dc2626'     # 主色：柔和红色（柱状图-亏损）- 不那么刺眼，更专业
COLOR_SECONDARY = '#0d9488'        # 次色：深青绿色（折线图-盈利）- 更柔和专业
COLOR_SECONDARY_LOSS = '#ea580c'   # 次色：柔和橙色（折线图-亏损）- 更协调
COLOR_GRID = '#e2e8f0'             # 网格线颜色 - 更柔和，与表格边框一致
COLOR_AXIS = '#94a3b8'             # 坐标轴颜色 - 更柔和，不抢夺注意力
COLOR_BG_LIGHT = '#ffffff'         # 背景色 - 纯白更专业
# 表格配色（与1_5.py保持一致）
COLOR_TABLE_HEADER = '#eef2fb'     # 表格标题背景（浅灰色）- 与1_5.py一致
COLOR_TABLE_HEADER_TEXT = '#1f2d3d' # 表格标题文字颜色（深色）- 与1_5.py一致
COLOR_TABLE_ROW1 = '#ffffff'       # 表格行1背景（偶数行）
COLOR_TABLE_ROW2 = '#f6f7fb'       # 表格行2背景（奇数行，斑马纹）- 与1_5.py一致
COLOR_TABLE_BORDER = '#e2e7f1'     # 表格边框颜色 - 与1_5.py一致
COLOR_TEXT_PRIMARY = '#1a2233'     # 主要文字颜色 - 与1_5.py一致
COLOR_TEXT_SECONDARY = '#475569'   # 次要文字颜色
COLOR_ZERO_LINE = '#94a3b8'        # 零线颜色 - 更明显



def plot_stock_profit_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (8, 6),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 16
):
    """
    绘制盈利前十的表格
    
    参数:
        data: 数据字典，格式为：
            {
                'profit_data': [
                    {
                        'stock_code': '002193',
                        'stock_name': '如意集团',
                        'weight_ratio': 0.94,        # 权重占净值比(%)
                        'contribution': 10.21,       # 贡献度(%)
                        'profit_amount': 10.21      # 收益额(万元)
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
        data = _generate_mock_stock_profit_data()
    
    # 获取数据
    profit_data = data.get('profit_data', [])
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 准备表格数据，优化数字格式化
    table_data = []
    for item in profit_data:
        weight_ratio = item.get('weight_ratio', 0)
        contribution = item.get('contribution', 0)
        profit_amount = item.get('profit_amount', 0)
        table_data.append([
            item.get('stock_code', ''),
            item.get('stock_name', ''),
            f"{weight_ratio:.2f}",
            f"{contribution:.2f}",
            f"{profit_amount:,.2f}"  # 添加千分位分隔符
        ])
    
    # 表头
    headers = ['股票代码', '股票名称', '权重占净值比(%)', '贡献度(%)', '收益额(万元)']
    
    # 优化表格尺寸和位置 - 根据figsize动态调整
    # 如果宽度小于10，说明是较窄的表格（在pages.py中），使用更紧凑的布局
    is_narrow = figsize[0] < 10
    table_width = 0.96 if is_narrow else 0.97   # 更充分利用空间
    table_total_height = 0.82 if is_narrow else 0.80  # 增加高度利用率
    table_fontsize = 12 if is_narrow else 13  # 增加字体大小，提升可读性
    
    # 计算位置（居中，但为标题留出空间）
    table_x = (1 - table_width) / 2  # 居中
    if show_title:
        ax.text(0.5, 0.97, '盈利前十', transform=ax.transAxes,
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
            if i == 0:  # 表头 - 浅灰色背景配深色文字（与1_5.py一致）
                cell.set_facecolor(COLOR_TABLE_HEADER)
                cell.set_text_props(weight='bold', ha='center', 
                                  fontsize=table_fontsize, 
                                  color=COLOR_TABLE_HEADER_TEXT,
                                  family='sans-serif')
                # 表头边框与背景色一致，无边框线
                cell.set_edgecolor(COLOR_TABLE_HEADER)
                cell.set_linewidth(0)
            else:
                # 交替行颜色 - 与1_5.py一致
                is_even_row = (i % 2 == 0)
                cell.set_facecolor(COLOR_TABLE_ROW1 if is_even_row else COLOR_TABLE_ROW2)
                # 所有列居中
                cell.set_text_props(ha='center', fontsize=table_fontsize,
                                  color=COLOR_TEXT_PRIMARY,
                                  family='sans-serif')
                # 数据行边框 - 与1_5.py一致
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


def plot_stock_profit_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (9, 6),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制盈利前十的组合图表（柱状图+折线图，双Y轴）
    
    参数:
        data: 数据字典，格式与 plot_stock_profit_table 相同
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
        data = _generate_mock_stock_profit_data()
    
    # 获取数据
    profit_data = data.get('profit_data', [])
    
    # 创建图表和双Y轴，添加浅色背景
    fig, ax1 = plt.subplots(figsize=figsize, facecolor='white')
    ax1.set_facecolor(COLOR_BG_LIGHT)
    ax2 = ax1.twinx()
    
    # 根据图表宽度动态调整元素大小 - 提升可读性
    is_wide = figsize[0] > 10
    bar_width = 0.55 if is_wide else 0.6  # 适中的柱子宽度
    marker_size = 6 if is_wide else 5.5  # 更大的标记
    line_width = 2.5 if is_wide else 2.2  # 更粗的线条
    label_fontsize = 12 if is_wide else 11  # 更大的标签
    tick_fontsize = 10 if is_wide else 9  # 更大的刻度
    legend_fontsize = 10 if is_wide else 9  # 更大的图例
    data_label_fontsize = 8 if is_wide else 7  # 数据标签
    
    # 设置 axes 的 zorder，确保 ax2（折线图）在上层
    ax1.set_zorder(1)
    ax2.set_zorder(2)
    # 设置 ax2 的背景透明，这样不会遮挡 ax1 的内容
    ax2.patch.set_visible(False)
    
    # 提取数据用于绘图 - 修正：折线图应该显示contribution而不是weight_ratio
    stock_names = [item['stock_name'] for item in profit_data]
    profit_amounts = [item['profit_amount'] for item in profit_data]
    contributions = [item['contribution'] for item in profit_data]  # 使用贡献度
    
    # 设置X轴位置
    x = np.arange(len(stock_names))
    
    # 绘制柱状图（收益额，左Y轴，专业深蓝色）- 先绘制，确保在底层
    bars = ax1.bar(x, profit_amounts, width=bar_width, color=COLOR_PRIMARY, 
                   alpha=0.9, label='收益额', zorder=1, 
                   edgecolor='white', linewidth=1.0)
    
    # 添加数据标签 - 优化字体大小和位置，只在顶部显示
    for i, (bar, amount) in enumerate(zip(bars, profit_amounts)):
        height = bar.get_height()
        if height > max(profit_amounts) * 0.05:  # 只显示较大的值，避免拥挤
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{amount:,.0f}',
                    ha='center', va='bottom', fontsize=data_label_fontsize, 
                    color=COLOR_TEXT_PRIMARY, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                             edgecolor=COLOR_PRIMARY, alpha=0.9, linewidth=0.5))
    
    ax1.set_ylabel('收益额(万元)', fontsize=label_fontsize, color=COLOR_TEXT_PRIMARY, 
                  fontweight='medium', labelpad=7)
    ax1.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=tick_fontsize)
    
    # 设置左Y轴范围
    max_profit = max(profit_amounts) if profit_amounts else 12
    ax1.set_ylim(0, max_profit * 1.2)
    
    # 绘制折线图（贡献度，右Y轴，深青绿色）- 后绘制，确保在上层
    line = ax2.plot(x, contributions, color=COLOR_SECONDARY, marker='o', 
                   markersize=marker_size, linewidth=line_width, label='贡献度', zorder=10,
                   markerfacecolor=COLOR_SECONDARY, 
                   markeredgecolor='white', markeredgewidth=1.2,
                   alpha=0.9)
    
    # 添加折线图数据标签 - 只显示关键点，避免拥挤
    max_contrib = max(contributions) if contributions else 0
    for i, (xi, contrib) in enumerate(zip(x, contributions)):
        # 只显示最大值、最小值和中间几个关键点
        if contrib == max_contrib or i % 3 == 0 or contrib < max_contrib * 0.3:
            ax2.text(xi, contrib, f'{contrib:.2f}',
                    ha='center', va='bottom', fontsize=data_label_fontsize,
                    color=COLOR_TEXT_PRIMARY, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                             edgecolor=COLOR_SECONDARY, alpha=0.9, linewidth=0.5))
    
    ax2.set_ylabel('贡献度(%)', fontsize=label_fontsize, color=COLOR_TEXT_PRIMARY, 
                   fontweight='medium', labelpad=7)
    ax2.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=tick_fontsize)
    
    # 设置右Y轴范围
    max_contrib = max(contributions) if contributions else 7
    min_contrib = min(contributions) if contributions else 0
    ax2.set_ylim(min(0, min_contrib * 1.1), max_contrib * 1.2)
    
    # 设置X轴 - 优化标签显示
    ax1.set_xticks(x)
    ax1.set_xticklabels(stock_names, rotation=35, ha='right', fontsize=tick_fontsize,
                       color=COLOR_TEXT_PRIMARY)
    ax1.set_xlabel('股票名称', fontsize=label_fontsize-1, color=COLOR_TEXT_PRIMARY, 
                   fontweight='medium', labelpad=5)
    ax1.tick_params(axis='x', colors=COLOR_TEXT_SECONDARY, labelsize=tick_fontsize)
    
    # 添加专业网格线 - 更柔和
    ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.6, 
            color=COLOR_GRID, axis='y', zorder=0)
    ax1.set_axisbelow(True)
    
    # 优化坐标轴样式
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color(COLOR_AXIS)
    ax1.spines['bottom'].set_color(COLOR_AXIS)
    ax1.spines['left'].set_linewidth(1)
    ax1.spines['bottom'].set_linewidth(1)
    
    # 合并图例 - 优化位置和样式，更专业
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper left', fontsize=legend_fontsize, frameon=True, 
               fancybox=False, shadow=False, framealpha=0.98,
               edgecolor=COLOR_TABLE_BORDER, facecolor='white',
               handlelength=2.0, handletextpad=0.5, columnspacing=1.0,
               borderpad=0.5, labelspacing=0.5)
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax1.set_title('盈利前十', fontsize=12, fontweight='bold', pad=15, loc='left')
    
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


def plot_stock_loss_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (8, 6),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 16
):
    """
    绘制亏损前十的表格
    
    参数:
        data: 数据字典，格式为：
            {
                'loss_data': [
                    {
                        'stock_code': '600543',
                        'stock_name': '莫高股份',
                        'weight_ratio': 1.49,        # 权重占净值比(%)
                        'contribution': -4.67,      # 贡献度(%)
                        'profit_amount': -4.67      # 收益额(万元)，负数表示亏损
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
        data = _generate_mock_stock_loss_data()
    
    # 获取数据
    loss_data = data.get('loss_data', [])
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 准备表格数据，优化数字格式化
    table_data = []
    for item in loss_data:
        weight_ratio = item.get('weight_ratio', 0)
        contribution = item.get('contribution', 0)
        profit_amount = item.get('profit_amount', 0)
        table_data.append([
            item.get('stock_code', ''),
            item.get('stock_name', ''),
            f"{weight_ratio:.2f}",
            f"{contribution:.2f}",
            f"{profit_amount:,.2f}"  # 添加千分位分隔符
        ])
    
    # 表头
    headers = ['股票代码', '股票名称', '权重占净值比(%)', '贡献度(%)', '收益额(万元)']
    
    # 优化表格尺寸和位置 - 根据figsize动态调整
    # 如果宽度小于10，说明是较窄的表格（在pages.py中），使用更紧凑的布局
    is_narrow = figsize[0] < 10
    table_width = 0.95 if is_narrow else 0.96   # 较窄时更充分利用空间
    table_total_height = 0.80 if is_narrow else 0.78  # 较窄时增加高度利用率
    table_fontsize = 11 if is_narrow else 12  # 较窄时使用更小字体
    
    # 计算位置（居中，但为标题留出空间）
    table_x = (1 - table_width) / 2  # 居中
    if show_title:
        ax.text(0.5, 0.96, '亏损前十', transform=ax.transAxes,
                ha='center', va='top', fontsize=15, fontweight='bold',
                color=COLOR_TEXT_PRIMARY)
        # table_y 是表格底部位置，表格高度是 table_total_height
        table_y = 0.88 - table_total_height  # 表格顶部在88%，与标题保持合理距离
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
            if i == 0:  # 表头 - 浅灰色背景配深色文字（与1_5.py一致）
                cell.set_facecolor(COLOR_TABLE_HEADER)
                cell.set_text_props(weight='bold', ha='center', 
                                  fontsize=table_fontsize, 
                                  color=COLOR_TABLE_HEADER_TEXT,
                                  family='sans-serif')
                # 表头边框与背景色一致，无边框线
                cell.set_edgecolor(COLOR_TABLE_HEADER)
                cell.set_linewidth(0)
            else:
                # 交替行颜色 - 与1_5.py一致
                is_even_row = (i % 2 == 0)
                cell.set_facecolor(COLOR_TABLE_ROW1 if is_even_row else COLOR_TABLE_ROW2)
                # 所有列居中
                cell.set_text_props(ha='center', fontsize=table_fontsize,
                                  color=COLOR_TEXT_PRIMARY,
                                  family='sans-serif')
                # 数据行边框 - 与1_5.py一致
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


def plot_stock_loss_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (9, 6),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制亏损前十的组合图表（柱状图+折线图，双Y轴）
    
    参数:
        data: 数据字典，格式与 plot_stock_loss_table 相同
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
        data = _generate_mock_stock_loss_data()
    
    # 获取数据
    loss_data = data.get('loss_data', [])
    
    # 创建图表和双Y轴，添加浅色背景
    fig, ax1 = plt.subplots(figsize=figsize, facecolor='white')
    ax1.set_facecolor(COLOR_BG_LIGHT)
    ax2 = ax1.twinx()
    
    # 根据图表宽度动态调整元素大小 - 提升可读性
    is_wide = figsize[0] > 10
    bar_width = 0.55 if is_wide else 0.6  # 适中的柱子宽度
    marker_size = 6 if is_wide else 5.5  # 更大的标记
    line_width = 2.5 if is_wide else 2.2  # 更粗的线条
    label_fontsize = 12 if is_wide else 11  # 更大的标签
    tick_fontsize = 10 if is_wide else 9  # 更大的刻度
    legend_fontsize = 10 if is_wide else 9  # 更大的图例
    data_label_fontsize = 8 if is_wide else 7  # 数据标签
    
    # 设置 axes 的 zorder，确保 ax2（折线图）在上层
    ax1.set_zorder(1)
    ax2.set_zorder(2)
    # 设置 ax2 的背景透明，这样不会遮挡 ax1 的内容
    ax2.patch.set_visible(False)
    
    # 提取数据用于绘图 - 修正：折线图应该显示contribution而不是weight_ratio
    stock_names = [item['stock_name'] for item in loss_data]
    profit_amounts = [item['profit_amount'] for item in loss_data]  # 负数表示亏损
    contributions = [item['contribution'] for item in loss_data]  # 使用贡献度
    
    # 设置X轴位置
    x = np.arange(len(stock_names))
    
    # 绘制柱状图（收益额，左Y轴，柔和红色，负数向下）- 先绘制，确保在底层
    bars = ax1.bar(x, profit_amounts, width=bar_width, color=COLOR_PRIMARY_LOSS, 
                   alpha=0.9, label='收益额', zorder=1,
                   edgecolor='white', linewidth=1.0)
    
    # 添加数据标签 - 优化字体大小和位置
    min_profit = min(profit_amounts) if profit_amounts else 0
    for i, (bar, amount) in enumerate(zip(bars, profit_amounts)):
        height = bar.get_height()
        # 负数标签显示在柱子下方
        y_pos = height - abs(height) * 0.05 if height < 0 else height
        va_pos = 'top' if height < 0 else 'bottom'
        # 只显示较大的值，避免拥挤
        if abs(height) > abs(min_profit) * 0.1:
            ax1.text(bar.get_x() + bar.get_width()/2., y_pos,
                    f'{amount:,.0f}',
                    ha='center', va=va_pos, fontsize=data_label_fontsize, 
                    color=COLOR_TEXT_PRIMARY, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                             edgecolor=COLOR_PRIMARY_LOSS, alpha=0.9, linewidth=0.5))
    
    ax1.set_ylabel('收益额(万元)', fontsize=label_fontsize, color=COLOR_TEXT_PRIMARY, 
                  fontweight='medium', labelpad=7)
    ax1.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=tick_fontsize)
    
    # 设置左Y轴范围（负数范围）
    min_profit = min(profit_amounts) if profit_amounts else -5
    max_profit = max(profit_amounts) if profit_amounts else 0
    ax1.set_ylim(min_profit * 1.2, max_profit * 1.1)
    
    # 添加零线
    ax1.axhline(y=0, color=COLOR_ZERO_LINE, linestyle='-', linewidth=1.2, 
               zorder=0, alpha=0.8)
    
    # 绘制折线图（贡献度，右Y轴，柔和橙色）- 后绘制，确保在上层
    line = ax2.plot(x, contributions, color=COLOR_SECONDARY_LOSS, marker='o', 
                   markersize=marker_size, linewidth=line_width, label='贡献度', zorder=10,
                   markerfacecolor=COLOR_SECONDARY_LOSS, 
                   markeredgecolor='white', markeredgewidth=1.2,
                   alpha=0.9)
    
    # 添加折线图数据标签 - 只显示关键点
    min_contrib = min(contributions) if contributions else 0
    for i, (xi, contrib) in enumerate(zip(x, contributions)):
        # 只显示最小值、最大值和中间几个关键点
        if contrib == min_contrib or i % 3 == 0 or contrib > min_contrib * 0.7:
            ax2.text(xi, contrib, f'{contrib:.2f}',
                    ha='center', va='top' if contrib < 0 else 'bottom', 
                    fontsize=data_label_fontsize,
                    color=COLOR_TEXT_PRIMARY, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                             edgecolor=COLOR_SECONDARY_LOSS, alpha=0.9, linewidth=0.5))
    
    ax2.set_ylabel('贡献度(%)', fontsize=label_fontsize, color=COLOR_TEXT_PRIMARY, 
                   fontweight='medium', labelpad=7)
    ax2.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=tick_fontsize)
    
    # 设置右Y轴范围（负数范围）
    max_contrib = max(contributions) if contributions else 0
    min_contrib = min(contributions) if contributions else -5
    ax2.set_ylim(min_contrib * 1.2, max(0, max_contrib * 1.1))
    
    # 设置X轴 - 优化标签显示
    ax1.set_xticks(x)
    ax1.set_xticklabels(stock_names, rotation=35, ha='right', fontsize=tick_fontsize,
                       color=COLOR_TEXT_PRIMARY)
    ax1.set_xlabel('股票名称', fontsize=label_fontsize-1, color=COLOR_TEXT_PRIMARY, 
                   fontweight='medium', labelpad=5)
    ax1.tick_params(axis='x', colors=COLOR_TEXT_SECONDARY, labelsize=tick_fontsize)
    
    # 添加专业网格线 - 更柔和
    ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.6, 
            color=COLOR_GRID, axis='y', zorder=0)
    ax1.set_axisbelow(True)
    
    # 优化坐标轴样式
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_color(COLOR_AXIS)
    ax1.spines['bottom'].set_color(COLOR_AXIS)
    ax1.spines['left'].set_linewidth(1)
    ax1.spines['bottom'].set_linewidth(1)
    
    # 合并图例 - 优化位置和样式，更专业
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper left', fontsize=legend_fontsize, frameon=True, 
               fancybox=False, shadow=False, framealpha=0.98,
               edgecolor=COLOR_TABLE_BORDER, facecolor='white',
               handlelength=2.0, handletextpad=0.5, columnspacing=1.0,
               borderpad=0.5, labelspacing=0.5)
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax1.set_title('亏损前十', fontsize=12, fontweight='bold', pad=15, loc='left')
    
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


def _generate_mock_stock_profit_data() -> Dict[str, Any]:
    """
    生成假数据用于测试盈利前十
    返回:
        Dict: 假数据字典
    """
    return {
        'profit_data': [
            {'stock_code': '002193', 'stock_name': '如意集团', 'weight_ratio': 0.94, 
             'contribution': 10.21, 'profit_amount': 10.21},
            {'stock_code': '002629', 'stock_name': '仁智股份', 'weight_ratio': 6.44, 
             'contribution': 8.81, 'profit_amount': 8.81},
            {'stock_code': '002633', 'stock_name': '申科股份', 'weight_ratio': 0.35, 
             'contribution': 4.91, 'profit_amount': 4.91},
            {'stock_code': '002861', 'stock_name': '瀛通通讯', 'weight_ratio': 1.23, 
             'contribution': 3.45, 'profit_amount': 3.45},
            {'stock_code': '002231', 'stock_name': '奥维通信', 'weight_ratio': 0.67, 
             'contribution': 2.89, 'profit_amount': 2.89},
            {'stock_code': '300736', 'stock_name': '百邦科技', 'weight_ratio': 0.45, 
             'contribution': 2.34, 'profit_amount': 2.34},
            {'stock_code': '301295', 'stock_name': '美硕科技', 'weight_ratio': 0.78, 
             'contribution': 1.98, 'profit_amount': 1.98},
            {'stock_code': '301197', 'stock_name': '工大科雅', 'weight_ratio': 0.56, 
             'contribution': 1.67, 'profit_amount': 1.67},
            {'stock_code': '002719', 'stock_name': '麦趣尔', 'weight_ratio': 0.34, 
             'contribution': 1.45, 'profit_amount': 1.45},
            {'stock_code': '300931', 'stock_name': '通用电梯', 'weight_ratio': 0.89, 
             'contribution': 1.23, 'profit_amount': 1.23},
        ]
    }


def _generate_mock_stock_loss_data() -> Dict[str, Any]:
    """
    生成假数据用于测试亏损前十
    返回:
        Dict: 假数据字典
    """
    return {
        'loss_data': [
            {'stock_code': '600543', 'stock_name': '莫高股份', 'weight_ratio': 1.49, 
             'contribution': -4.67, 'profit_amount': -4.67},
            {'stock_code': '001366', 'stock_name': '播恩集团', 'weight_ratio': 2.93, 
             'contribution': -3.61, 'profit_amount': -3.61},
            {'stock_code': '301037', 'stock_name': '保立佳', 'weight_ratio': 1.12, 
             'contribution': -2.22, 'profit_amount': -2.22},
            {'stock_code': '300478', 'stock_name': '杭州高新', 'weight_ratio': 0.89, 
             'contribution': -1.78, 'profit_amount': -1.78},
            {'stock_code': '301040', 'stock_name': '中环海陆', 'weight_ratio': 0.67, 
             'contribution': -1.45, 'profit_amount': -1.45},
            {'stock_code': '002620', 'stock_name': '瑞和股份', 'weight_ratio': 0.56, 
             'contribution': -1.23, 'profit_amount': -1.23},
            {'stock_code': '300749', 'stock_name': '顶固集创', 'weight_ratio': 0.45, 
             'contribution': -0.98, 'profit_amount': -0.98},
            {'stock_code': '002921', 'stock_name': '联诚精密', 'weight_ratio': 0.78, 
             'contribution': -0.76, 'profit_amount': -0.76},
            {'stock_code': '603172', 'stock_name': '万丰股份', 'weight_ratio': 0.34, 
             'contribution': -0.54, 'profit_amount': -0.54},
            {'stock_code': '000929', 'stock_name': '兰州黄河', 'weight_ratio': 0.67, 
             'contribution': -0.32, 'profit_amount': -0.32},
        ]
    }


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成股票绩效归因图表...")
    fig1 = plot_stock_profit_table()
    fig2 = plot_stock_profit_chart()
    fig3 = plot_stock_loss_table()
    fig4 = plot_stock_loss_chart()
    print("图表生成成功")

