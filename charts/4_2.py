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



def plot_industry_attribution_profit_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 8),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 16
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
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
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
    
    # 使用类似 4_1.py 的方式：缩小表格，放大字体
    table_width = 1   # 表格宽度为图形宽度的70%
    table_total_height = 0.7  # 表格总高度
    table_fontsize = 16  # 字体大小统一为16
    
    # 计算位置（左对齐，但为标题留出空间）
    table_x = 0  # 左边距0，使表格左对齐
    if show_title:
        ax.text(0, 0.92, '按照收益额排名前十', transform=ax.transAxes,
                ha='left', va='top', fontsize=16, fontweight='bold')
        # table_y 是表格底部位置，表格高度是 table_total_height
        # 如果希望表格顶部在 0.85，则底部 = 0.85 - table_total_height
        table_y = 0.85 - table_total_height  # 表格顶部在85%，与标题保持合理距离
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
    # table.scale(1, 1.5)  # 调整行高
    
    # 设置表格样式
    for i in range(len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor('#f0f0f0')
                cell.set_text_props(weight='bold', ha='center', fontsize=table_fontsize)
            else:
                # 交替行颜色
                if (i - 1) % 2 == 0:
                    cell.set_facecolor('#ffffff')
                else:
                    cell.set_facecolor('#f8f8f8')
                # 第一列左对齐，其他列居中
                if j == 0:
                    cell.set_text_props(ha='center', fontsize=table_fontsize)
                else:
                    cell.set_text_props(ha='center', fontsize=table_fontsize)
            
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


def plot_industry_attribution_profit_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
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
    
    # 创建图表和双Y轴
    fig, ax1 = plt.subplots(figsize=figsize)
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
    
    # 绘制柱状图（权重%，右Y轴，灰色）- 先绘制，确保在底层
    ax2.bar(x, weights, width=0.65, color='#808080', alpha=1, label='权重', zorder=1)
    
    # 绘制折线图（贡献度%，左Y轴，蓝色）- 后绘制，确保在上层
    ax1.plot(x, contributions, color='#082868', marker='o', 
            markersize=5, linewidth=2, label='贡献度',markerfacecolor='white', markeredgecolor='#082868',
            markeredgewidth=1.5, zorder=10)
    ax1.set_ylabel('贡献度(%)', fontsize=11, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax2.set_ylabel('权重(%)', fontsize=11, color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    
    # 统一两个Y轴的范围，使折线图能正确显示在柱状图上方
    max_contrib = max(contributions) if contributions else 10
    max_weight = max(weights) if weights else 8
    y_max = max(max_contrib, max_weight) * 1.1  # 取两者最大值
    # ax1.set_ylim(0, y_max)
    # ax2.set_ylim(0, y_max)
    ax1.margins(y=0.1)
    ax2.margins(y=0.1)
    
    # 设置X轴：显示所有10个位置，但只显示5个标签（机械设备、石油石化、医药生物、国防军工、社会服务）
    # 这5个行业在原始数据中的索引是：0, 2, 4, 6, 8
    selected_indices = [0, 2, 4, 6, 8]
    selected_industries = [industries[i] for i in selected_indices if i < len(industries)]
    selected_x_positions = [x[i] for i in selected_indices if i < len(x)]
    
    ax1.set_xticks(selected_x_positions)
    ax1.set_xticklabels(selected_industries, rotation=45, ha='right')
    ax1.set_xlabel('行业', fontsize=11)
    
    # 添加网格线
    ax1.grid(True, alpha=0.5, linestyle='--', linewidth=0.5, axis='y')
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', fontsize=10)
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax1.set_title('按照收益额排名前十', fontsize=12, fontweight='bold', pad=15, loc='left')
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
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


def plot_industry_attribution_loss_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 8),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 16
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
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
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
    
    # 使用类似 4_1.py 的方式：缩小表格，放大字体
    table_width = 1   # 表格宽度为图形宽度的70%
    table_total_height = 0.7  # 表格总高度
    table_fontsize = 16  # 字体大小统一为16
    
    # 计算位置（左对齐，但为标题留出空间）
    table_x = 0  # 左边距0，使表格左对齐
    if show_title:
        ax.text(0, 0.92, '按照亏损额排名前十', transform=ax.transAxes,
                ha='left', va='top', fontsize=16, fontweight='bold')
        # table_y 是表格底部位置，表格高度是 table_total_height
        # 如果希望表格顶部在 0.85，则底部 = 0.85 - table_total_height
        table_y = 0.85 - table_total_height  # 表格顶部在85%，与标题保持合理距离
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
    # table.scale(1, 1.5)  # 调整行高
    
    # 设置表格样式
    for i in range(len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor('#f0f0f0')
                cell.set_text_props(weight='bold', ha='center', fontsize=table_fontsize)
            else:
                # 交替行颜色
                if (i - 1) % 2 == 0:
                    cell.set_facecolor('#ffffff')
                else:
                    cell.set_facecolor('#f8f8f8')
                # 第一列左对齐，其他列居中
                if j == 0:
                    cell.set_text_props(ha='center', fontsize=table_fontsize)
                else:
                    cell.set_text_props(ha='center', fontsize=table_fontsize)
            
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


def plot_industry_attribution_loss_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
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
    
    # 创建图表和双Y轴
    fig, ax1 = plt.subplots(figsize=figsize)
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
    
    # 绘制柱状图（权重%，右Y轴，灰色）- 先绘制，确保在底层
    ax2.bar(x, weights, width=0.65, color='#808080', alpha=1, label='权重', zorder=1)
    
    # 绘制折线图（贡献度%，左Y轴，蓝色）- 后绘制，确保在上层
    ax1.plot(x, contributions, color='#082868', marker='o', 
            markersize=5, linewidth=2, label='贡献度', markerfacecolor='white', markeredgecolor='#082868',
            markeredgewidth=1.5, zorder=10)
    ax1.set_ylabel('贡献度(%)', fontsize=11, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax2.set_ylabel('权重(%)', fontsize=11, color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    
    # 统一两个Y轴的范围，使折线图能正确显示在柱状图上方
    min_contrib = min(contributions) if contributions else -2
    max_contrib = max(contributions) if contributions else 0
    max_weight = max(weights) if weights else 8
    # 对于负数范围，需要同时考虑贡献度的最小值和权重的最大值
    y_min = min_contrib * 1.1
    y_max = max(max_contrib, max_weight) * 1.1
    # ax1.set_ylim(y_min, y_max)
    # ax2.set_ylim(0, y_max)  # 权重始终为正数
    ax1.margins(y=0.1)
    ax2.margins(y=0.1)
    # 设置X轴  
    ax1.set_xticks(x)
    ax1.set_xticklabels(industries, rotation=45, ha='right')
    ax1.set_xlabel('行业', fontsize=11)
    
    # 添加网格线
    ax1.grid(True, alpha=0.5, linestyle='--', linewidth=0.5, axis='y')
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', fontsize=10)
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax1.set_title('按照亏损额排名前十', fontsize=12, fontweight='bold', pad=15, loc='left')
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
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

