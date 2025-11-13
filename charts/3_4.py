"""
大类资产绩效归因表格生成
使用 matplotlib 生成大类资产绩效归因表格
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
from matplotlib.patches import Rectangle
import numpy as np


def plot_asset_performance_attribution_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 4),
    return_figure: bool = False,
    show_title: bool = False,
    table_fontsize: int = 16,
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
    asset_data = data.get("asset_data", [])

    # 准备表格数据
    table_data = []
    for item in asset_data:
        table_data.append(
            [
                item.get("asset_class", ""),
                f"{item.get('weight_ratio', 0):.2f}",
                f"{item.get('nav_contribution', 0):.2f}",
                f"{item.get('return_rate', 0):.2f}",
                f"{item.get('return_amount', 0):.2f}",
                f"{item.get('return_contribution', 0):.2f}",
            ]
        )

    # 表头
    headers = [
        "资产类别",
        "权重占净值比(%)",
        "单位净值增长贡献(%)",
        "收益率(%)",
        "收益额(万元)",
        "收益额贡献率(%)",
    ]

    # 创建图表，设置专业背景色
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#f5f7fb")  # 浅灰蓝色背景
    ax.axis("off")

    # 表格尺寸和字体设置
    table_width = 1.0  # 表格宽度
    table_total_height = 0.5  # 表格总高度
    table_fontsize = 15  # 数据行字体大小

    # 计算位置（居中）
    table_x = (1 - table_width) / 2
    table_y = (1 - table_total_height) / 2

    # 绘制表格
    table = ax.table(
        cellText=table_data,
        colLabels=headers,
        cellLoc="center",
        loc="center",
        bbox=[table_x, table_y, table_width, table_total_height],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(table_fontsize)
    table.scale(1, 1.8)  # 增加行高，使表格更舒适

    # 专业表格样式配置
    header_bg = "#eef2fb"  # 表头背景：浅灰色背景
    stripe_odd = "#f6f7fb"  # 奇数行：浅灰蓝色
    stripe_even = "#ffffff"  # 偶数行：白色
    border_color = "#e2e7f1"  # 边框颜色

    # 设置表格样式
    max_row = len(table_data)  # 最大行数（不包括表头）
    for i in range(len(table_data) + 1):  # +1 包括表头
        for j in range(len(headers)):
            cell = table[(i, j)]

            if i == 0:  # 表头
                cell.set_facecolor(header_bg)
                cell.set_text_props(
                    weight="bold",
                    ha="center",
                    color="#1f2d3d",  # 深色文字
                    fontsize=table_fontsize + 1,  # 表头字体大1号
                )
                cell.set_edgecolor(header_bg)  # 与背景相同
                cell.set_linewidth(0)  # 表头无边框
            else:  # 数据行
                # 交替行颜色
                if (i - 1) % 2 == 0:  # 奇数行（i=1, 3, 5...）
                    cell.set_facecolor(stripe_odd)
                else:  # 偶数行（i=2, 4, 6...）
                    cell.set_facecolor(stripe_even)

                # 第一列（资产类别）左对齐，其他列右对齐（便于数值对比）
                if j == 0:
                    cell.set_text_props(
                        ha="left",
                        color="#1a2233",  # 深色文字
                        fontsize=table_fontsize,
                        fontweight="medium",
                    )
                else:
                    cell.set_text_props(
                        ha="right",  # 数值列右对齐
                        color="#1a2233",  # 深色文字
                        fontsize=table_fontsize,
                        fontweight="medium",
                    )

                cell.set_edgecolor(border_color)
                cell.set_linewidth(0.6)  # 统一边框宽度

    # 不显示标题（根据用户要求）
    # if show_title:
    #     ax.text(0, 0.98, '大类资产绩效归因', transform=ax.transAxes,
    #             ha='left', va='top', fontsize=12, fontweight='bold')

    # 调整布局，确保表格居中且美观
    plt.tight_layout(pad=1.0)

    # 如果只需要返回 figure 对象，不保存
    if return_figure:
        return fig

    # 如果提供了保存路径，保存图表为 PDF（矢量格式，高清）
    if save_path:
        plt.savefig(save_path, format="pdf", bbox_inches="tight", dpi=300)
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
        "asset_data": [
            {
                "asset_class": "股票",
                "weight_ratio": 61.63,
                "nav_contribution": 49.87,
                "return_rate": 45.79,
                "return_amount": 57.03,
                "return_contribution": 100.07,
            },
            {
                "asset_class": "公募基金",
                "weight_ratio": 1.20,
                "nav_contribution": -0.02,
                "return_rate": -0.05,
                "return_amount": -0.04,
                "return_contribution": -0.07,
            },
            {
                "asset_class": "逆回购",
                "weight_ratio": 0.26,
                "nav_contribution": 0.00,
                "return_rate": 0.00,
                "return_amount": 0.00,
                "return_contribution": 0.00,
            },
        ]
    }


if __name__ == "__main__":
    # 测试表格生成
    print("正在生成大类资产绩效归因表格...")
    output_path = plot_asset_performance_attribution_table()
    print(f"表格已保存到: {output_path}")
