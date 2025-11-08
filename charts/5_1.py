"""
股票绩效归因图表生成
使用 matplotlib 生成股票绩效归因表格和组合图表
包含盈利前十和亏损前十两个部分
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import numpy as np


def setup_chinese_font() -> None:
    """
    配置matplotlib中文字体
    """
    font_list = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['font.sans-serif'] = font_list
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 10


def plot_stock_profit_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 8),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 12
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
    
    # 准备表格数据
    table_data = []
    for item in profit_data:
        table_data.append([
            item.get('stock_code', ''),
            item.get('stock_name', ''),
            f"{item.get('weight_ratio', 0):.2f}",
            f"{item.get('contribution', 0):.2f}",
            f"{item.get('profit_amount', 0):.2f}"
        ])
    
    # 表头
    headers = ['股票代码', '股票名称', '权重占净值比(%)', '贡献度(%)', '收益额(万元)']
    
    # 使用类似 4_1.py 的方式：缩小表格，放大字体
    table_width = 1   # 表格宽度为图形宽度的100%
    table_total_height = 0.7  # 表格总高度
    table_fontsize = 12  # 字体大小统一为12
    
    # 计算位置（左对齐，但为标题留出空间）
    table_x = 0  # 左边距0，使表格左对齐
    if show_title:
        ax.text(0, 0.92, '盈利前十', transform=ax.transAxes,
                ha='left', va='top', fontsize=12, fontweight='bold')
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
                cell.set_text_props(weight='bold', ha='center')
            else:
                # 交替行颜色
                if (i - 1) % 2 == 0:
                    cell.set_facecolor('#ffffff')
                else:
                    cell.set_facecolor('#f8f8f8')
                # 第一列和第二列左对齐，其他列居中
                if j in [0, 1]:
                    cell.set_text_props(ha='center')
                else:
                    cell.set_text_props(ha='center')
            
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


def plot_stock_profit_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
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
    
    # 创建图表和双Y轴
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    
    # 设置 axes 的 zorder，确保 ax2（折线图）在上层
    ax1.set_zorder(1)
    ax2.set_zorder(2)
    # 设置 ax2 的背景透明，这样不会遮挡 ax1 的内容
    ax2.patch.set_visible(False)
    
    # 提取数据用于绘图
    stock_names = [item['stock_name'] for item in profit_data]
    profit_amounts = [item['profit_amount'] for item in profit_data]
    weights = [item['weight_ratio'] for item in profit_data]
    
    # 设置X轴位置
    x = np.arange(len(stock_names))
    
    # 绘制柱状图（收益额，左Y轴，蓝色）- 先绘制，确保在底层
    ax1.bar(x, profit_amounts, width=0.6, color='#5470c6', alpha=1, label='收益额', zorder=1)
    ax1.set_ylabel('收益额(万元)', fontsize=11, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    
    # 设置左Y轴范围
    max_profit = max(profit_amounts) if profit_amounts else 12
    ax1.set_ylim(0, max_profit * 1.1)
    
    # 绘制折线图（权重，右Y轴，绿色）- 后绘制，确保在上层
    ax2.plot(x, weights, color='#91cc75', marker='o', 
             markersize=5, linewidth=2, label='权重', zorder=10)
    ax2.set_ylabel('权重(%)', fontsize=11, color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    
    # 设置右Y轴范围
    max_weight = max(weights) if weights else 7
    ax2.set_ylim(0, max_weight * 1.2)
    
    # 设置X轴
    ax1.set_xticks(x)
    ax1.set_xticklabels(stock_names, rotation=45, ha='right')
    ax1.set_xlabel('股票名称', fontsize=11)
    
    # 添加网格线
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', fontsize=10)
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax1.set_title('盈利前十', fontsize=12, fontweight='bold', pad=15, loc='left')
    
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


def plot_stock_loss_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 8),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 12
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
    
    # 准备表格数据
    table_data = []
    for item in loss_data:
        table_data.append([
            item.get('stock_code', ''),
            item.get('stock_name', ''),
            f"{item.get('weight_ratio', 0):.2f}",
            f"{item.get('contribution', 0):.2f}",
            f"{item.get('profit_amount', 0):.2f}"
        ])
    
    # 表头
    headers = ['股票代码', '股票名称', '权重占净值比(%)', '贡献度(%)', '收益额(万元)']
    
    # 使用类似 4_1.py 的方式：缩小表格，放大字体
    table_width = 1   # 表格宽度为图形宽度的100%
    table_total_height = 0.7  # 表格总高度
    table_fontsize = 12  # 字体大小统一为12
    
    # 计算位置（左对齐，但为标题留出空间）
    table_x = 0  # 左边距0，使表格左对齐
    if show_title:
        ax.text(0, 0.92, '亏损前十', transform=ax.transAxes,
                ha='left', va='top', fontsize=12, fontweight='bold')
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
                cell.set_text_props(weight='bold', ha='center')
            else:
                # 交替行颜色
                if (i - 1) % 2 == 0:
                    cell.set_facecolor('#ffffff')
                else:
                    cell.set_facecolor('#f8f8f8')
                # 第一列和第二列左对齐，其他列居中
                if j in [0, 1]:
                    cell.set_text_props(ha='center')
                else:
                    cell.set_text_props(ha='center')
            
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


def plot_stock_loss_chart(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
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
    
    # 创建图表和双Y轴
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    
    # 设置 axes 的 zorder，确保 ax2（折线图）在上层
    ax1.set_zorder(1)
    ax2.set_zorder(2)
    # 设置 ax2 的背景透明，这样不会遮挡 ax1 的内容
    ax2.patch.set_visible(False)
    
    # 提取数据用于绘图
    stock_names = [item['stock_name'] for item in loss_data]
    profit_amounts = [item['profit_amount'] for item in loss_data]  # 负数表示亏损
    weights = [item['weight_ratio'] for item in loss_data]
    
    # 设置X轴位置
    x = np.arange(len(stock_names))
    
    # 绘制柱状图（收益额，左Y轴，蓝色，负数向下）- 先绘制，确保在底层
    ax1.bar(x, profit_amounts, width=0.6, color='#5470c6', alpha=1, label='收益额', zorder=1)
    ax1.set_ylabel('收益额(万元)', fontsize=11, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    
    # 设置左Y轴范围（负数范围）
    min_profit = min(profit_amounts) if profit_amounts else -5
    max_profit = max(profit_amounts) if profit_amounts else 0
    ax1.set_ylim(min_profit * 1.1, max_profit * 1.1)
    
    # 绘制折线图（权重，右Y轴，绿色）- 后绘制，确保在上层
    ax2.plot(x, weights, color='#91cc75', marker='o', 
             markersize=5, linewidth=2, label='权重', zorder=10)
    ax2.set_ylabel('权重(%)', fontsize=11, color='black')
    ax2.tick_params(axis='y', labelcolor='black')
    
    # 设置右Y轴范围
    max_weight = max(weights) if weights else 3
    ax2.set_ylim(0, max_weight * 1.2)
    
    # 设置X轴
    ax1.set_xticks(x)
    ax1.set_xticklabels(stock_names, rotation=45, ha='right')
    ax1.set_xlabel('股票名称', fontsize=11)
    
    # 添加网格线
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, axis='y')
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', fontsize=10)
    
    # 不显示标题（根据用户要求，标题只在表格上方显示）
    # if show_title:
    #     ax1.set_title('亏损前十', fontsize=12, fontweight='bold', pad=15, loc='left')
    
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

