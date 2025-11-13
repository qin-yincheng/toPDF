"""
股票行业归因图表生成
使用 matplotlib 生成股票行业归因表格和组合图表
包含收益额排名前十和亏损额排名前十两个部分
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
from matplotlib.patches import Rectangle
import numpy as np

# 专业金融报告配色方案 - 与1_5.py保持一致
COLOR_PRIMARY = '#1e40af'          # 主色：深蓝色（折线图）- 更专业稳重的蓝色
COLOR_SECONDARY = '#64748b'        # 次色：中性灰蓝色（柱状图）- 更柔和的灰色
COLOR_GRID = '#f1f5f9'             # 网格线颜色 - 非常柔和，几乎不可见但有用
COLOR_AXIS = '#cbd5e1'             # 坐标轴颜色 - 更淡，不抢夺注意力
COLOR_BG_LIGHT = '#ffffff'         # 纯白背景
COLOR_TABLE_HEADER = '#eef2fb'     # 表格标题背景 - 浅灰色背景（与1_5.py一致）
COLOR_TABLE_HEADER_TEXT = '#1f2d3d' # 表格标题文字 - 深色（与1_5.py一致）
COLOR_TABLE_ROW1 = '#ffffff'       # 表格行1背景 - 白色（偶数行）
COLOR_TABLE_ROW2 = '#f6f7fb'       # 表格行2背景（斑马纹）- 浅灰色（奇数行，与1_5.py一致）
COLOR_TABLE_BORDER = '#e2e7f1'     # 表格边框颜色 - 与1_5.py一致
COLOR_TEXT_PRIMARY = '#1a2233'     # 主要文字颜色 - 与1_5.py一致
COLOR_TEXT_SECONDARY = '#475569'   # 次要文字颜色 - 中等灰色
COLOR_HIGHLIGHT = '#3b82f6'        # 高亮色 - 用于重要数据



def plot_industry_attribution_profit_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 7),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 8
):
    """
    绘制按照收益额排名前十的表格
    
    参数:
        data: 数据字典，格式为：
            {
                'profit_data': [
                    {
                        'industry': '机械设备',
                        'weight_ratio': 3.92,        # 权重占净值比(%)
                        'contribution': 10.78,       # 贡献度(%)
                        'profit_amount': 12.87,      # 收益额(万元)
                        'selection_return': 2.76,    # 选择收益(%)
                        'allocation_return': 9.11    # 配置收益(%)
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
        data = _generate_mock_profit_data()
    
    # 获取数据
    profit_data = data.get('profit_data', [])
    
    # 创建图表，设置背景色
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor(COLOR_BG_LIGHT)
    ax.axis('off')
    
    # 准备表格数据
    table_data = []
    for item in profit_data:
        table_data.append([
            item.get('industry', ''),
            f"{item.get('weight_ratio', 0):.2f}",
            f"{item.get('contribution', 0):.2f}",
            f"{item.get('profit_amount', 0):.2f}",
            f"{item.get('selection_return', 0):.2f}",
            f"{item.get('allocation_return', 0):.2f}",
            f"{item.get('interaction_return', 0):.2f}",
        ])
    
    # 表头
    headers = ['行业', '权重占净值比(%)', '贡献度(%)', '收益额(万元)', 
               '选择收益(%)', '配置收益(%)', '交互收益(%)']
    
    # 优化表格尺寸和字体 - 更专业的比例
    table_width = 0.96   # 表格宽度，留出适当的左右边距
    table_total_height = 0.75  # 表格高度，更合理的比例
    # 如果需要自适应字体，可在外部传入
    
    # 计算位置（居中，留出边距）
    table_x = 0.02  # 左边距
    if show_title:
        # 标题放在axes外部
        title_text = ax.text(0.5, 1.02, '按照收益额排名前十', transform=ax.transAxes,
                ha='center', va='bottom', fontsize=8, fontweight='bold',
                color=COLOR_TEXT_PRIMARY, family='sans-serif')
        # 表格在axes中居中，留出上下边距
        table_y = (1 - table_total_height) / 2 + 0.05  # 稍微上移，为标题留空间
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
    table.scale(1, 1.6)  # 更合理的行高比例，不会显得太稀疏
    
    # 设置表格样式 - 精致专业
    for i in range(len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor(COLOR_TABLE_HEADER)
                cell.set_text_props(weight='bold', ha='center', 
                                   fontsize=table_fontsize, 
                                   color=COLOR_TABLE_HEADER_TEXT)
                cell.set_edgecolor(COLOR_TABLE_HEADER)  # 表头边框与背景色一致（与1_5.py一致）
                cell.set_linewidth(0)  # 表头无边框（与1_5.py一致）
                cell.set_height(0.08)  # 表头稍微高一点
            else:
                # 交替行颜色 - 微妙但清晰
                if (i - 1) % 2 == 0:
                    cell.set_facecolor(COLOR_TABLE_ROW1)
                else:
                    cell.set_facecolor(COLOR_TABLE_ROW2)
                # 所有列居中
                cell.set_text_props(ha='center', fontsize=table_fontsize,
                                   color=COLOR_TEXT_PRIMARY, weight='normal')
            
            # 精致的边框 - 与1_5.py保持一致
            cell.set_edgecolor(COLOR_TABLE_BORDER)
            cell.set_linewidth(0.6)  # 边框宽度与1_5.py一致
    
    # 调整布局 - 更合理的边距
    plt.tight_layout()
    plt.subplots_adjust(left=0.08, right=0.95, top=0.88, bottom=0.15, hspace=0.3)
    
    # 标题已经设置好了，不需要重新定位
    
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


def plot_industry_attribution_profit_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 7),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制按照收益额排名前十的组合图表（折线图+柱状图，双Y轴）
    
    参数:
        data: 数据字典，格式与 plot_industry_attribution_profit_table 相同
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
        data = _generate_mock_profit_data()
    
    # 获取数据
    profit_data = data.get('profit_data', [])
    
    # 创建图表和双Y轴，设置背景色
    fig, ax1 = plt.subplots(figsize=figsize, facecolor='white')
    ax1.set_facecolor(COLOR_BG_LIGHT)
    ax2 = ax1.twinx()
    
    # 设置 axes 的 zorder，确保 ax1（折线图）在上层
    ax1.set_zorder(2)
    ax2.set_zorder(1)
    # 设置 ax1 的背景透明，这样不会遮挡 ax2 的内容
    ax1.patch.set_visible(False)
    
    # 提取所有10个行业的数据用于绘图
    industries = [item['industry'] for item in profit_data]
    contributions = [item['contribution'] for item in profit_data]
    weights = [item['weight_ratio'] for item in profit_data]
    
    # 设置X轴位置（10个柱子）
    x = np.arange(len(industries))
    # 计算合适的柱宽 - 根据柱子数量动态调整，让柱子更宽更舒适
    # 对于10个柱子，使用0.6-0.7的宽度比较合适
    if len(industries) > 0:
        bar_width = min(0.7, max(0.5, 0.8 - len(industries) * 0.02))
    else:
        bar_width = 0.7
    
    # 绘制柱状图（权重%，右Y轴）- 先绘制，确保在底层
    # 使用更柔和的灰色，与1_5.py风格一致
    bars = ax2.bar(x, weights, width=bar_width, color='#c5cad8', alpha=0.85, 
            label='权重', zorder=1, edgecolor='white', linewidth=1.0)
    
    # 绘制折线图（贡献度%，左Y轴）- 后绘制，确保在上层
    # 使用更专业的深蓝色，与1_5.py风格一致
    line = ax1.plot(x, contributions, color='#1f3c88', marker='o', 
            markersize=8, linewidth=1, label='贡献度',
            markerfacecolor='white', markeredgecolor='#1f3c88',
            markeredgewidth=1, zorder=10, alpha=1.0)
    
    # 优化Y轴标签样式 - 专业清晰
    ax1.set_ylabel('贡献度(%)', fontsize=7, color=COLOR_TEXT_PRIMARY, 
                   fontweight='bold', labelpad=10)
    ax1.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=7, 
                    width=0.8, length=4)
    ax2.set_ylabel('权重(%)', fontsize=7, color=COLOR_TEXT_PRIMARY, 
                   fontweight='bold', labelpad=10)
    ax2.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=7,
                    width=0.8, length=4)
    
    # 设置Y轴范围，让图表有适当的呼吸空间
    max_contrib = max(contributions) if contributions else 10
    max_weight = max(weights) if weights else 8
    y_max = max(max_contrib, max_weight) * 1.12
    ax1.set_ylim(bottom=0, top=y_max)
    ax2.set_ylim(bottom=0, top=y_max)
    
    # 设置X轴：显示所有标签，适当旋转以避免重叠
    ax1.set_xticks(x)
    # 根据标签数量和长度决定是否旋转
    # 如果标签数量>=8或平均标签长度>4，则旋转45度
    avg_label_len = np.mean([len(label) for label in industries]) if industries else 0
    rotation = 45 if (len(industries) >= 8 or avg_label_len > 4) else 0
    
    ax1.set_xticklabels(industries, fontsize=7, color=COLOR_TEXT_SECONDARY, 
                        rotation=rotation, ha='right' if rotation > 0 else 'center',
                        rotation_mode='anchor')
    ax1.set_xlabel('', fontsize=0)  # 不显示X轴标题
    
    # 设置X轴范围，让柱子不贴边，留出适当的边距
    x_margin = 0.5
    ax1.set_xlim(-x_margin, len(industries) - 1 + x_margin)
    
    # 优化网格线样式 - 与1_5.py风格一致
    ax1.grid(True, alpha=0.25, linestyle='--', linewidth=0.5, 
            color='#b9c2d3', axis='y', zorder=1, which='major')
    ax1.set_axisbelow(True)  # 网格线在图表元素下方
    
    # 优化坐标轴样式 - 与1_5.py风格一致
    for spine in ax1.spines.values():
        spine.set_color('#b9c2d3')  # 使用与1_5.py相同的坐标轴颜色
        spine.set_linewidth(1)
    for spine in ax2.spines.values():
        spine.set_color('#b9c2d3')
        spine.set_linewidth(1)
    
    # 优化图例样式 - 更精致
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', fontsize=6, frameon=True,
               fancybox=False, shadow=False, framealpha=0.95,
               edgecolor=COLOR_TABLE_BORDER, facecolor='white',
               borderpad=0.8, labelspacing=0.6, handlelength=2.5)
    
    # 隐藏顶部和右侧边框
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # 添加标题
    if show_title:
        ax1.text(0.5, 1.02, '按照收益额排名前十', transform=ax1.transAxes,
                ha='center', va='bottom', fontsize=8, fontweight='bold',
                color=COLOR_TEXT_PRIMARY, family='sans-serif')
    
    # 调整布局 - 更合理的边距，与表格对齐
    plt.tight_layout()
    plt.subplots_adjust(left=0.10, right=0.90, top=0.88, bottom=0.20 if rotation > 0 else 0.15)
    
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


def plot_industry_attribution_loss_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 7),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 8
):
    """
    绘制按照亏损额排名前十的表格
    
    参数:
        data: 数据字典，格式为：
            {
                'loss_data': [
                    {
                        'industry': '农林牧渔',
                        'weight_ratio': 2.96,        # 权重占净值比(%)
                        'contribution': -1.94,      # 贡献度(%)
                        'profit_amount': -3.61,     # 收益额(万元)，负数表示亏损
                        'selection_return': -0.47,  # 选择收益(%)
                        'allocation_return': -1.20  # 配置收益(%)
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
        data = _generate_mock_loss_data()
    
    # 获取数据
    loss_data = data.get('loss_data', [])
    
    # 创建图表，设置背景色
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor(COLOR_BG_LIGHT)
    ax.axis('off')
    
    # 准备表格数据
    table_data = []
    for item in loss_data:
        table_data.append([
            item.get('industry', ''),
            f"{item.get('weight_ratio', 0):.2f}",
            f"{item.get('contribution', 0):.2f}",
            f"{item.get('profit_amount', 0):.2f}",
            f"{item.get('selection_return', 0):.2f}",
            f"{item.get('allocation_return', 0):.2f}",
            f"{item.get('interaction_return', 0):.2f}",
        ])
    
    # 表头
    headers = ['行业', '权重占净值比(%)', '贡献度(%)', '收益额(万元)', 
               '选择收益(%)', '配置收益(%)', '交互收益(%)']
    
    # 优化表格尺寸和字体 - 更专业的比例
    table_width = 0.96   # 表格宽度，留出适当的左右边距
    table_total_height = 0.75  # 表格高度，更合理的比例
    # 如果需要自适应字体，可在外部传入
    
    # 计算位置（居中，留出边距）
    table_x = 0.02  # 左边距
    if show_title:
        # 标题放在axes外部
        title_text = ax.text(0.5, 1.02, '按照亏损额排名前十', transform=ax.transAxes,
                ha='center', va='bottom', fontsize=8, fontweight='bold',
                color=COLOR_TEXT_PRIMARY, family='sans-serif')
        # 表格在axes中居中，留出上下边距
        table_y = (1 - table_total_height) / 2 + 0.05  # 稍微上移，为标题留空间
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
    table.scale(1, 1.6)  # 更合理的行高比例，不会显得太稀疏
    
    # 设置表格样式 - 精致专业
    for i in range(len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor(COLOR_TABLE_HEADER)
                cell.set_text_props(weight='bold', ha='center', 
                                   fontsize=table_fontsize, 
                                   color=COLOR_TABLE_HEADER_TEXT)
                cell.set_edgecolor(COLOR_TABLE_HEADER)  # 表头边框与背景色一致（与1_5.py一致）
                cell.set_linewidth(0)  # 表头无边框（与1_5.py一致）
                cell.set_height(0.08)  # 表头稍微高一点
            else:
                # 交替行颜色 - 微妙但清晰
                if (i - 1) % 2 == 0:
                    cell.set_facecolor(COLOR_TABLE_ROW1)
                else:
                    cell.set_facecolor(COLOR_TABLE_ROW2)
                # 所有列居中
                cell.set_text_props(ha='center', fontsize=table_fontsize,
                                   color=COLOR_TEXT_PRIMARY, weight='normal')
            
            # 精致的边框 - 与1_5.py保持一致
            cell.set_edgecolor(COLOR_TABLE_BORDER)
            cell.set_linewidth(0.6)  # 边框宽度与1_5.py一致
    
    # 调整布局 - 更合理的边距
    plt.tight_layout()
    plt.subplots_adjust(left=0.08, right=0.95, top=0.88, bottom=0.15, hspace=0.3)
    
    # 标题已经设置好了，不需要重新定位
    
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


def plot_industry_attribution_loss_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (14, 7),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制按照亏损额排名前十的组合图表（折线图+柱状图，双Y轴）
    
    参数:
        data: 数据字典，格式与 plot_industry_attribution_loss_table 相同
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
        data = _generate_mock_loss_data()
    
    # 获取数据
    loss_data = data.get('loss_data', [])
    
    # 创建图表和双Y轴，设置背景色
    fig, ax1 = plt.subplots(figsize=figsize, facecolor='white')
    ax1.set_facecolor(COLOR_BG_LIGHT)
    ax2 = ax1.twinx()
    
    # 设置 axes 的 zorder，确保 ax1（折线图）在上层
    ax1.set_zorder(2)
    ax2.set_zorder(1)
    # 设置 ax1 的背景透明，这样不会遮挡 ax2 的内容
    ax1.patch.set_visible(False)
    
    # 提取数据用于绘图
    industries = [item['industry'] for item in loss_data]
    contributions = [item['contribution'] for item in loss_data]
    weights = [item['weight_ratio'] for item in loss_data]
    
    # 设置X轴位置
    x = np.arange(len(industries))
    # 计算合适的柱宽 - 根据柱子数量动态调整，让柱子更宽更舒适
    # 对于10个柱子，使用0.6-0.7的宽度比较合适
    if len(industries) > 0:
        bar_width = min(0.7, max(0.5, 0.8 - len(industries) * 0.02))
    else:
        bar_width = 0.7
    
    # 绘制柱状图（权重%，右Y轴）- 先绘制，确保在底层
    # 使用更柔和的灰色，与1_5.py风格一致
    bars = ax2.bar(x, weights, width=bar_width, color='#c5cad8', alpha=0.85, 
            label='权重', zorder=1, edgecolor='white', linewidth=1.0)
    
    # 绘制折线图（贡献度%，左Y轴）- 后绘制，确保在上层
    # 使用更专业的深蓝色，与1_5.py风格一致
    line = ax1.plot(x, contributions, color='#1f3c88', marker='o', 
            markersize=8, linewidth=1, label='贡献度',
            markerfacecolor='white', markeredgecolor='#1f3c88',
            markeredgewidth=1, zorder=10, alpha=1.0)
    
    # 优化Y轴标签样式 - 专业清晰
    ax1.set_ylabel('贡献度(%)', fontsize=7, color=COLOR_TEXT_PRIMARY, 
                   fontweight='bold', labelpad=10)
    ax1.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=7, 
                    width=0.8, length=4)
    ax2.set_ylabel('权重(%)', fontsize=7, color=COLOR_TEXT_PRIMARY, 
                   fontweight='bold', labelpad=10)
    ax2.tick_params(axis='y', labelcolor=COLOR_TEXT_PRIMARY, labelsize=7,
                    width=0.8, length=4)
    
    # 设置Y轴范围，让图表有适当的呼吸空间（负数范围）
    min_contrib = min(contributions) if contributions else -2
    max_contrib = max(contributions) if contributions else 0
    max_weight = max(weights) if weights else 8
    # 对于负数范围，需要同时考虑贡献度的最小值和权重的最大值
    y_min = min_contrib * 1.15 if min_contrib < 0 else 0
    y_max = max(max_contrib, max_weight) * 1.12
    ax1.set_ylim(bottom=y_min, top=y_max)
    ax2.set_ylim(bottom=y_min, top=y_max)
    
    # 设置X轴：显示所有标签，适当旋转以避免重叠
    ax1.set_xticks(x)
    # 根据标签数量和长度决定是否旋转
    # 如果标签数量>=8或平均标签长度>4，则旋转45度
    avg_label_len = np.mean([len(label) for label in industries]) if industries else 0
    rotation = 45 if (len(industries) >= 8 or avg_label_len > 4) else 0
    
    ax1.set_xticklabels(industries, fontsize=7, color=COLOR_TEXT_SECONDARY, 
                        rotation=rotation, ha='right' if rotation > 0 else 'center',
                        rotation_mode='anchor')
    ax1.set_xlabel('', fontsize=0)  # 不显示X轴标题
    
    # 设置X轴范围，让柱子不贴边，留出适当的边距
    x_margin = 0.5
    ax1.set_xlim(-x_margin, len(industries) - 1 + x_margin)
    
    # 优化网格线样式 - 与1_5.py风格一致
    ax1.grid(True, alpha=0.25, linestyle='--', linewidth=0.5, 
            color='#b9c2d3', axis='y', zorder=1, which='major')
    ax1.set_axisbelow(True)  # 网格线在图表元素下方
    
    # 添加零线（对于负数范围很重要）- 与1_5.py风格一致
    if min_contrib < 0:
        ax1.axhline(y=0, color='#8f97aa', linestyle='-', linewidth=1, 
                   alpha=1.0, zorder=2)
    
    # 优化坐标轴样式 - 与1_5.py风格一致
    for spine in ax1.spines.values():
        spine.set_color('#b9c2d3')  # 使用与1_5.py相同的坐标轴颜色
        spine.set_linewidth(1)
    for spine in ax2.spines.values():
        spine.set_color('#b9c2d3')
        spine.set_linewidth(1)
    
    # 优化图例样式 - 更精致
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', fontsize=6, frameon=True,
               fancybox=False, shadow=False, framealpha=0.95,
               edgecolor=COLOR_TABLE_BORDER, facecolor='white',
               borderpad=0.8, labelspacing=0.6, handlelength=2.5)
    
    # 隐藏顶部和右侧边框
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # 添加标题
    if show_title:
        ax1.text(0.5, 1.02, '按照亏损额排名前十', transform=ax1.transAxes,
                ha='center', va='bottom', fontsize=8, fontweight='bold',
                color=COLOR_TEXT_PRIMARY, family='sans-serif')
    
    # 调整布局 - 更合理的边距，与表格对齐
    plt.tight_layout()
    plt.subplots_adjust(left=0.10, right=0.90, top=0.88, bottom=0.20 if rotation > 0 else 0.15)
    
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


def _generate_mock_profit_data() -> Dict[str, Any]:
    """
    生成假数据用于测试收益额排名前十
    返回:
        Dict: 假数据字典
    """
    return {
        'profit_data': [
            {'industry': '机械设备', 'weight_ratio': 3.92, 'contribution': 10.78, 
             'profit_amount': 12.87, 'selection_return': 2.76, 'allocation_return': 9.11, 'interaction_return': 1.05},
            {'industry': '纺织服饰', 'weight_ratio': 3.12, 'contribution': 7.41, 
             'profit_amount': 11.67, 'selection_return': 4.97, 'allocation_return': 1.47, 'interaction_return': 0.32},
            {'industry': '石油石化', 'weight_ratio': 6.46, 'contribution': 7.59, 
             'profit_amount': 8.81, 'selection_return': 3.68, 'allocation_return': 2.92, 'interaction_return': 0.45},
            {'industry': '电子', 'weight_ratio': 7.30, 'contribution': 5.59, 
             'profit_amount': 8.24, 'selection_return': 7.35, 'allocation_return': -3.45, 'interaction_return': -0.85},
            {'industry': '医药生物', 'weight_ratio': 6.32, 'contribution': 4.31, 
             'profit_amount': 5.24, 'selection_return': 3.45, 'allocation_return': -1.67, 'interaction_return': 0.58},
            {'industry': '环保', 'weight_ratio': 8.52, 'contribution': 4.26, 
             'profit_amount': 4.85, 'selection_return': 0.24, 'allocation_return': 6.30, 'interaction_return': 0.42},
            {'industry': '国防军工', 'weight_ratio': 1.93, 'contribution': 2.36, 
             'profit_amount': 3.41, 'selection_return': 2.79, 'allocation_return': -1.12, 'interaction_return': 0.61},
            {'industry': '商贸零售', 'weight_ratio': 6.52, 'contribution': 2.26, 
             'profit_amount': 2.15, 'selection_return': 1.11, 'allocation_return': 0.57, 'interaction_return': 0.18},
            {'industry': '社会服务', 'weight_ratio': 0.80, 'contribution': 1.10, 
             'profit_amount': 2.02, 'selection_return': 0.50, 'allocation_return': 0.46, 'interaction_return': 0.09},
            {'industry': '电力设备', 'weight_ratio': 2.17, 'contribution': 1.66, 
             'profit_amount': 1.97, 'selection_return': -0.27, 'allocation_return': -1.24, 'interaction_return': -0.15},
        ]
    }


def _generate_mock_loss_data() -> Dict[str, Any]:
    """
    生成假数据用于测试亏损额排名前十
    返回:
        Dict: 假数据字典
    """
    return {
        'loss_data': [
            {'industry': '农林牧渔', 'weight_ratio': 2.96, 'contribution': -1.94, 
             'profit_amount': -3.61, 'selection_return': -0.47, 'allocation_return': -1.20, 'interaction_return': -0.28},
            {'industry': '基础化工', 'weight_ratio': 8.86, 'contribution': -0.92, 
             'profit_amount': -3.00, 'selection_return': 0.07, 'allocation_return': -1.77, 'interaction_return': -0.19},
            {'industry': '食品饮料', 'weight_ratio': 5.94, 'contribution': -0.36, 
             'profit_amount': -2.42, 'selection_return': 0.10, 'allocation_return': -0.53, 'interaction_return': -0.11},
            {'industry': '轻工制造', 'weight_ratio': 3.57, 'contribution': -0.33, 
             'profit_amount': -0.71, 'selection_return': 3.71, 'allocation_return': -4.34, 'interaction_return': -0.42},
            {'industry': '家用电器', 'weight_ratio': 0.18, 'contribution': -0.31, 
             'profit_amount': -0.50, 'selection_return': -0.19, 'allocation_return': -0.85, 'interaction_return': -0.07},
            {'industry': '汽车', 'weight_ratio': 4.52, 'contribution': -0.01, 
             'profit_amount': -0.04, 'selection_return': 3.66, 'allocation_return': -4.35, 'interaction_return': -0.41},
        ]
    }


if __name__ == '__main__':
    # 测试图表生成
    print("正在生成股票行业归因图表...")
    fig1 = plot_industry_attribution_profit_table()
    fig2 = plot_industry_attribution_profit_chart()
    fig3 = plot_industry_attribution_loss_table()
    fig4 = plot_industry_attribution_loss_chart()
    print("图表生成成功")

