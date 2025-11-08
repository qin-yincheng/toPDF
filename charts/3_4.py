"""
大类资产绩效归因表格生成
使用 matplotlib 生成大类资产绩效归因表格
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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


def plot_asset_performance_attribution_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 4),
    return_figure: bool = False,
    show_title: bool = False,
    table_fontsize: int = 12
):
    """
    绘制大类资产绩效归因表格
    
    参数:
        data: 数据字典，格式为：
            {
                'asset_data': [
                    {
                        'asset_class': '股票',
                        'weight_ratio': 61.63,           # 权重占净值比(%)
                        'nav_contribution': 49.87,       # 单位净值增长贡献(%)
                        'return_rate': 45.79,            # 收益率(%)
                        'return_amount': 57.03,          # 收益额(万元)
                        'return_contribution': 100.07    # 收益额贡献率(%)
                    },
                    ...
                ]
            }
            如果为None，则使用假数据
        save_path: 保存路径
        figsize: 图表大小（宽，高）
        return_figure: 是否返回 figure 对象
        show_title: 是否显示标题（默认False，不在图表内显示标题）
        table_fontsize: 表格字体大小
    
    返回:
        figure 对象或保存的文件路径
    """
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_asset_performance_data()
    
    # 获取资产数据
    asset_data = data.get('asset_data', [])
    
    # 准备表格数据
    table_data = []
    for item in asset_data:
        table_data.append([
            item.get('asset_class', ''),
            f"{item.get('weight_ratio', 0):.2f}",
            f"{item.get('nav_contribution', 0):.2f}",
            f"{item.get('return_rate', 0):.2f}",
            f"{item.get('return_amount', 0):.2f}",
            f"{item.get('return_contribution', 0):.2f}"
        ])
    
    # 表头
    headers = ['资产类别', '权重占净值比(%)', '单位净值增长贡献(%)', 
               '收益率(%)', '收益额(万元)', '收益额贡献率(%)']
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 使用类似 4_1.py 的方式：缩小表格，放大字体
    table_width = 1   # 表格宽度为图形宽度的70%
    table_total_height = 0.5  # 表格总高度
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
                # 交替行颜色：第一行数据（i=1）白色，第二行（i=2）浅灰，第三行（i=3）白色
                if (i - 1) % 2 == 0:  # 第一行数据（i=1）白色
                    cell.set_facecolor('#ffffff')
                else:  # 第二行数据（i=2）浅灰
                    cell.set_facecolor('#ffffff')
                
                # 第一列（资产类别）左对齐，其他列居中对齐

                cell.set_text_props(ha='center')
            
            cell.set_edgecolor('#f0f0f0')
            cell.set_linewidth(0.8)
    
    # 不显示标题（根据用户要求）
    # if show_title:
    #     ax.text(0, 0.98, '大类资产绩效归因', transform=ax.transAxes,
    #             ha='left', va='top', fontsize=12, fontweight='bold')
    
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


def _generate_mock_asset_performance_data() -> Dict[str, Any]:
    """
    生成假数据用于测试大类资产绩效归因表格
    返回:
        Dict: 假数据字典
    """
    return {
        'asset_data': [
            {
                'asset_class': '股票',
                'weight_ratio': 61.63,
                'nav_contribution': 49.87,
                'return_rate': 45.79,
                'return_amount': 57.03,
                'return_contribution': 100.07
            },
            {
                'asset_class': '公募基金',
                'weight_ratio': 1.20,
                'nav_contribution': -0.02,
                'return_rate': -0.05,
                'return_amount': -0.04,
                'return_contribution': -0.07
            },
            {
                'asset_class': '逆回购',
                'weight_ratio': 0.26,
                'nav_contribution': 0.00,
                'return_rate': 0.00,
                'return_amount': 0.00,
                'return_contribution': 0.00
            }
        ]
    }


if __name__ == '__main__':
    # 测试表格生成
    print("正在生成大类资产绩效归因表格...")
    output_path = plot_asset_performance_attribution_table()
    print(f"表格已保存到: {output_path}")

