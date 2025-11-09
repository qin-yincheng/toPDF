"""
期末持仓表格生成
使用 matplotlib 生成期末持仓表格
包含总体摘要、资产明细和负债明细
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
from matplotlib.patches import Rectangle
import numpy as np



def plot_end_period_holdings_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 10),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 12
):
    """
    绘制期末持仓表格
    
    参数:
        data: 数据字典，格式为：
            {
                'summary': {
                    'asset_net_value': 154.55,  # 资产净值（万元）
                    'total_assets': 154.61,     # 资产总值（万元）
                    'total_liabilities': 0.06    # 负债合计（万元）
                },
                'assets': [
                    {'name': '股票', 'market_value': 154.35, 'proportion': 99.87},
                    {'name': '债券', 'market_value': 0.00, 'proportion': 0.00},
                    ...
                ],
                'liabilities': [
                    {'name': '正回购', 'market_value': 0.00, 'proportion': 0.00},
                    {'name': '短期借款', 'market_value': 0.00, 'proportion': 0.00},
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
        data = _generate_mock_holdings_data()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 准备数据
    summary = data.get('summary', {})
    assets = data.get('assets', [])
    liabilities = data.get('liabilities', [])
    
    # 准备资产明细数据（包含标题行）
    asset_table_data = [['资产名称', '资产市值(万元)', '资产占比(%)']]
    for asset in assets:
        # 处理期货和场外衍生品的显示格式（保证金/市值）
        name = asset.get('name', '')
        market_value = asset.get('market_value', 0)
        if '保证金/市值' in name:
            # 对于期货和场外衍生品，显示为 "0.00/0.00"
            value_str = f"{market_value:.2f}/{market_value:.2f}"
        else:
            value_str = f"{market_value:.2f}"
        
        asset_table_data.append([
            name,
            value_str,
            f"{asset.get('proportion', 0):.2f}"
        ])
    
    # 如果没有资产数据，添加一行占位数据
    if len(asset_table_data) == 1:
        asset_table_data.append(['无', '0.00', '0.00'])
    
    # 准备负债明细数据（包含标题行）
    liability_table_data = [['负债名称', '负债市值(万元)', '负债占比(%)']]
    for liability in liabilities:
        liability_table_data.append([
            liability.get('name', ''),
            f"{liability.get('market_value', 0):.2f}",
            f"{liability.get('proportion', 0):.2f}"
        ])
    
    # 如果没有负债数据，添加一行占位数据
    if len(liability_table_data) == 1:
        liability_table_data.append(['无', '0.00', '0.00'])
    
    # 计算表格位置（左右并排布局）
    # 顶部显示资产净值
    y_top = 0.98
    net_value_height = 0.07  # 增加高度
    
    # 表格区域（左右并排）
    asset_title_height = 0.05  # 增加高度
    table_y_start = y_top - net_value_height - asset_title_height  # 无缝连接
    table_height = 0.85
    
    # 左侧资产表格（左右表格紧挨着，无间距）
    asset_x = 0.01
    asset_width = 0.49
    
    # 右侧负债表格（紧挨着左侧表格）
    liability_x = 0.50
    liability_width = 0.49
    
    # 绘制顶部资产净值（带浅灰背景，类似表格单元格）
    # 矩形宽度与左右表格总宽度对齐
    total_table_width = asset_width + liability_width
    net_value_x = asset_x
    net_value_text = f"资产净值: {summary.get('asset_net_value', 0):.2f}(万元)"
    # 使用矩形背景，与表格对齐，底部与标题矩形无缝连接
    net_value_rect = Rectangle((net_value_x, y_top - net_value_height), total_table_width, net_value_height, 
                               facecolor='#f0f0f0', edgecolor='#f0f0f0', linewidth=1)
    ax.add_patch(net_value_rect)
    ax.text(net_value_x + total_table_width / 2, y_top - net_value_height / 2, 
            net_value_text,
            ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 绘制左侧资产明细表格（带标题）
    asset_title_y = table_y_start + asset_title_height  # 标题矩形顶部位置
    asset_table_y = table_y_start  # 表格顶部位置，与标题矩形底部无缝连接
    asset_table_height = table_height
    
    # 资产表格标题（带浅灰背景，类似表格单元格）
    # 矩形宽度与表格对齐
    asset_title_text = f"资产总值: {summary.get('total_assets', 0):.2f}(万元)"
    asset_title_rect = Rectangle((asset_x, asset_title_y - asset_title_height), asset_width, asset_title_height,
                                 facecolor='#f0f0f0', edgecolor='#f0f0f0', linewidth=1)
    ax.add_patch(asset_title_rect)
    ax.text(asset_x + asset_width / 2, asset_title_y - asset_title_height / 2,
            asset_title_text,
            ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 资产明细表格
    asset_table = ax.table(
        cellText=asset_table_data[1:],
        colLabels=asset_table_data[0],
        cellLoc='left',
        loc='center',
        bbox=[asset_x, asset_table_y - asset_table_height, asset_width, asset_table_height]
    )
    asset_table.auto_set_font_size(False)
    asset_table.set_fontsize(table_fontsize)
    # 设置列宽：名称列更宽
    asset_table.auto_set_column_width(col=list(range(3)))
    asset_table.scale(1, 1.6)
    
    # 设置资产明细表格样式
    for i in range(len(asset_table_data)):
        for j in range(3):
            cell = asset_table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor('#f0f0f0')
                cell.set_text_props(weight='bold', ha='center')
            else:
                if j == 0:
                    # 资产名称列背景浅灰（所有行）
                    cell.set_facecolor('#f0f0f0')
                    cell.set_text_props(ha='center')
                else:
                    cell.set_text_props(ha='center')
                    # 交替行颜色：第一行数据（i=1）白色，第二行（i=2）浅灰，以此类推
                    # i=1 是奇数，应该是白色；i=2 是偶数，应该是浅灰
                    if (i - 1) % 2 == 0:  # 第一行数据（i=1）白色
                        cell.set_facecolor('#ffffff')
                    else:  # 第二行数据（i=2）浅灰
                        cell.set_facecolor('#f8f8f8')
            cell.set_edgecolor('#f0f0f0')
            cell.set_linewidth(1)
    
    # 绘制右侧负债明细表格（带标题）
    liability_title_y = table_y_start + asset_title_height  # 标题矩形顶部位置，与资产总值对齐
    liability_table_y = table_y_start  # 表格顶部位置，与标题矩形底部无缝连接
    liability_table_height = table_height
    
    # 负债表格标题（带浅灰背景，类似表格单元格）
    # 矩形宽度与表格对齐，与资产总值矩形无缝连接
    liability_title_text = f"负债合计: {summary.get('total_liabilities', 0):.2f}(万元)"
    liability_title_rect = Rectangle((liability_x, liability_title_y - asset_title_height), liability_width, asset_title_height,
                                     facecolor='#f0f0f0', edgecolor='#f0f0f0', linewidth=1)
    ax.add_patch(liability_title_rect)
    ax.text(liability_x + liability_width / 2, liability_title_y - asset_title_height / 2,
            liability_title_text,
            ha='center', va='center', fontsize=12, fontweight='bold')
    
    # 负债明细表格（行高缩小）
    liability_table = ax.table(
        cellText=liability_table_data[1:],
        colLabels=liability_table_data[0],
        cellLoc='left',
        loc='center',
        bbox=[liability_x, liability_table_y - liability_table_height, liability_width, liability_table_height]
    )
    liability_table.auto_set_font_size(False)
    liability_table.set_fontsize(table_fontsize)
    liability_table.scale(1, 1.0)  # 进一步缩小行高
    
    # 设置负债明细表格样式
    for i in range(len(liability_table_data)):
        for j in range(3):
            cell = liability_table[(i, j)]
            if i == 0:  # 表头
                cell.set_facecolor('#f0f0f0')
                cell.set_text_props(weight='bold', ha='center')
            else:
                if j == 0:
                    cell.set_text_props(ha='center')
                else:
                    cell.set_text_props(ha='center')
                # 交替行颜色：第一行数据（i=1）白色，第二行（i=2）浅灰，以此类推
                # i=1 是奇数，应该是白色；i=2 是偶数，应该是浅灰
                if (i - 1) % 2 == 0:  # 第一行数据（i=1）白色
                    cell.set_facecolor('#ffffff')
                else:  # 第二行数据（i=2）浅灰
                    cell.set_facecolor('#f8f8f8')
            cell.set_edgecolor('#f0f0f0')
            cell.set_linewidth(1)
    
    # 添加标题（如果启用，但这里不显示，由 pages.py 统一绘制）
    # plt.title('期末持仓', fontsize=16, fontweight='bold', pad=20, loc='left')
    
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


def _generate_mock_holdings_data() -> Dict[str, Any]:
    """
    生成假数据用于测试期末持仓表格
    返回:
        Dict: 假数据字典
    """
    return {
        'summary': {
            'asset_net_value': 154.55,  # 资产净值（万元）
            'total_assets': 154.61,      # 资产总值（万元）
            'total_liabilities': 0.06     # 负债合计（万元）
        },
        'assets': [
            {'name': '股票', 'market_value': 154.35, 'proportion': 99.87},
            {'name': '债券', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '公募基金', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '定期存款', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '逆回购', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '期货(保证金/市值)', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '期权市值', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '理财产品', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '场外衍生品(保证金/市值)', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '现金', 'market_value': 0.26, 'proportion': 0.17},
            {'name': '其他资产', 'market_value': 0.00, 'proportion': 0.00},
        ],
        'liabilities': [
            {'name': '正回购', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '短期借款', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '融资融券', 'market_value': 0.00, 'proportion': 0.00},
            {'name': '其他负债', 'market_value': 0.06, 'proportion': 100.00},
        ]
    }


if __name__ == '__main__':
    # 测试表格生成
    print("正在生成期末持仓表格...")
    output_path = plot_end_period_holdings_table()
    print(f"表格已保存到: {output_path}")

