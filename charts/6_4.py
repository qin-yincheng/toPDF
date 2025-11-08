"""
换手率 (年化) 表格生成
使用 matplotlib 生成换手率 (年化) 表格
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


def plot_turnover_rate_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 4),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 12
):
    """
    绘制换手率 (年化) 表格
    
    参数:
        data: 数据字典，格式为：
            {
                'turnover_data': [
                    {
                        'asset_class': '股票',
                        'statistical_period': 4438.91,    # 统计期间(%)
                        'last_month': 5133.34,            # 近一个月(%)
                        'last_three_months': 4444.51,     # 近三个月(%)
                        'last_six_months': 3973.54,       # 近六个月(%)
                        'year_to_date': 2789.61,          # 今年以来(%)
                        'since_inception': 1669.18         # 成立以来(%)
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
        data = _generate_mock_turnover_data()
    
    # 获取数据
    turnover_data = data.get('turnover_data', [])
    
    # 准备表格数据
    table_data = []
    for item in turnover_data:
        table_data.append([
            item.get('asset_class', ''),
            f"{item.get('statistical_period', 0):.2f}",
            f"{item.get('last_month', 0):.2f}",
            f"{item.get('last_three_months', 0):.2f}",
            f"{item.get('last_six_months', 0):.2f}",
            f"{item.get('year_to_date', 0):.2f}",
            f"{item.get('since_inception', 0):.2f}"
        ])
    
    # 表头
    headers = ['资产分类', '统计期间(%)', '近一个月(%)', '近三个月(%)', 
               '近六个月(%)', '今年以来(%)', '成立以来(%)']
    
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
                # 交替行颜色：第一行数据（i=1，股票）白色，第二行（i=2，基金）浅灰，第三行（i=3，逆回购）白色
                if (i - 1) % 2 == 0:  # 第一行和第三行数据（i=1, 3）白色
                    cell.set_facecolor('#ffffff')
                else:  # 第二行数据（i=2）浅灰
                    cell.set_facecolor('#f8f8f8')
                
                # 第一列（资产分类）左对齐，其他列居中对齐
                if j == 0:
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


def _generate_mock_turnover_data() -> Dict[str, Any]:
    """
    生成假数据用于测试换手率 (年化) 表格
    返回:
        Dict: 假数据字典
    """
    return {
        'turnover_data': [
            {
                'asset_class': '股票',
                'statistical_period': 4438.91,
                'last_month': 5133.34,
                'last_three_months': 4444.51,
                'last_six_months': 3973.54,
                'year_to_date': 2789.61,
                'since_inception': 1669.18
            },
            {
                'asset_class': '基金',
                'statistical_period': 450.33,
                'last_month': 2380.34,
                'last_three_months': 769.03,
                'last_six_months': 403.12,
                'year_to_date': 0.00,
                'since_inception': 103.07
            },
            {
                'asset_class': '逆回购',
                'statistical_period': 225.23,
                'last_month': 1190.48,
                'last_three_months': 384.62,
                'last_six_months': 201.61,
                'year_to_date': 2777.78,
                'since_inception': 51.55
            }
        ]
    }


if __name__ == '__main__':
    # 测试表格生成
    print("正在生成换手率 (年化) 表格...")
    fig = plot_turnover_rate_table()
    print("表格生成成功")

