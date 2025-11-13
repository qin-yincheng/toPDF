"""
换手率 (年化) 表格生成
使用 matplotlib 生成换手率 (年化) 表格
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
from matplotlib.patches import Rectangle
import numpy as np

# 专业配色方案 - 金融报告标准配色（与1_5.py保持一致）
COLOR_TABLE_HEADER = '#eef2fb'        # 表格标题背景（浅灰色）- 与1_5一致
COLOR_TABLE_HEADER_TEXT = '#1f2d3d'   # 表格标题文字颜色（深色）- 与1_5一致
COLOR_TABLE_ROW1 = '#ffffff'          # 表格行1背景（白色）
COLOR_TABLE_ROW2 = '#f6f7fb'         # 表格行2背景（浅灰色斑马纹）- 与1_5一致
COLOR_TABLE_BORDER = '#e2e7f1'       # 表格边框颜色 - 与1_5一致
COLOR_TEXT_PRIMARY = '#1a2233'       # 主要文字颜色 - 与1_5一致
COLOR_TEXT_SECONDARY = '#475569'     # 次要文字颜色



def plot_turnover_rate_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 4),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 16
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
    
    # 准备表格数据，优化数字格式化
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
        ax.text(0.5, 0.97, '换手率 (年化)', transform=ax.transAxes,
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

