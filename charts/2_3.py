"""
期末持仓表格生成
使用 matplotlib 生成期末持仓表格
包含总体摘要、资产明细和负债明细
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
from matplotlib.patches import Rectangle


def plot_end_period_holdings_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 10),
    return_figure: bool = False,
    show_title: bool = True,
    table_fontsize: int = 8,
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
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(
        3, 2, height_ratios=[0.22, 0.4, 0.38], hspace=0.12, wspace=0.1
    )

    # 准备数据
    summary = data.get("summary", {})
    assets = data.get("assets", [])
    liabilities = data.get("liabilities", [])

    # 顶部摘要信息
    summary_ax = fig.add_subplot(gs[0, :])
    summary_ax.axis("off")
    card_specs = [
        ("资产净值", summary.get("asset_net_value", 0.0), "#edf2ff"),
        ("资产总值", summary.get("total_assets", 0.0), "#f3f6ff"),
        ("负债合计", summary.get("total_liabilities", 0.0), "#f8f3ff"),
    ]
    card_width = 0.28
    gap = 0.08
    for idx, (label, value, color) in enumerate(card_specs):
        x0 = idx * (card_width + gap)
        rect = Rectangle(
            (x0, 0.18),
            card_width,
            0.64,
            facecolor=color,
            edgecolor="#d9def2",
            linewidth=1.1,
            zorder=1,
        )
        summary_ax.add_patch(rect)
        summary_ax.text(
            x0 + card_width / 2,
            0.65,
            label,
            ha="center",
            va="center",
            fontsize=table_fontsize,
            color="#495057",
            fontweight="bold",
        )
        summary_ax.text(
            x0 + card_width / 2,
            0.4,
            f"{value:,.2f} 万元",
            ha="center",
            va="center",
            fontsize=table_fontsize,
            color="#1b1f2a",
            fontweight="bold",
        )

    # 构造资产明细表数据
    asset_rows = [["资产名称", "资产市值(万元)", "资产占比(%)"]]
    for asset in assets:
        name = asset.get("name", "")
        market_value = asset.get("market_value", 0.0)
        proportion = asset.get("proportion", 0.0)
        # 特殊名称格式处理
        if "保证金/市值" in name:
            value_str = f"{market_value:,.2f}/{market_value:,.2f}"
        else:
            value_str = f"{market_value:,.2f}"
        asset_rows.append([name, value_str, f"{proportion:.2f}%"])
    if len(asset_rows) == 1:
        asset_rows.append(["无", "0.00", "0.00%"])

    # 构造负债明细表数据
    liability_rows = [["负债名称", "负债市值(万元)", "负债占比(%)"]]
    for liability in liabilities:
        liability_rows.append(
            [
                liability.get("name", ""),
                f"{liability.get('market_value', 0.0):,.2f}",
                f"{liability.get('proportion', 0.0):.2f}%",
            ]
        )
    if len(liability_rows) == 1:
        liability_rows.append(["无", "0.00", "0.00%"])

    # 左侧资产表格
    asset_ax = fig.add_subplot(gs[1:, 0])
    asset_ax.axis("off")
    asset_table = asset_ax.table(
        cellText=asset_rows[1:],
        colLabels=asset_rows[0],
        cellLoc="left",
        loc="center",
        colWidths=[0.46, 0.30, 0.24],
        bbox=[-0.005, -0.06, 1.01, 1.02],
    )
    asset_table.auto_set_font_size(False)
    asset_table.set_fontsize(table_fontsize)
    asset_table.scale(1.04, 1.9)

    for i in range(len(asset_rows)):
        for j in range(3):
            cell = asset_table[(i, j)]
            cell.set_edgecolor("#d9dfee")
            cell.set_linewidth(0.9)
            if i == 0:
                cell.set_facecolor("#edf2ff")
                cell.set_text_props(
                    ha="center",
                    va="center",
                    fontsize=table_fontsize,
                    weight="bold",
                    color="#1b1f2a",
                )
            else:
                if j == 0:
                    cell.set_text_props(ha="left", color="#21242c")
                    cell.set_facecolor("#f6f8fe")
                    cell.PAD = 0.35
                else:
                    align = "right"
                    cell.set_text_props(ha=align, color="#1d2129")
                    row_color = "#ffffff" if i % 2 == 1 else "#f7f9ff"
                    cell.set_facecolor(row_color)

    # 右侧负债表格
    liability_ax = fig.add_subplot(gs[1:, 1])
    liability_ax.axis("off")
    liability_table = liability_ax.table(
        cellText=liability_rows[1:],
        colLabels=liability_rows[0],
        cellLoc="left",
        loc="center",
        colWidths=[0.46, 0.30, 0.24],
        bbox=[-0.005, -0.06, 1.01, 1.02],
    )
    liability_table.auto_set_font_size(False)
    liability_table.set_fontsize(table_fontsize)
    liability_table.scale(1.04, 1.9)

    for i in range(len(liability_rows)):
        for j in range(3):
            cell = liability_table[(i, j)]
            cell.set_edgecolor("#d9dfee")
            cell.set_linewidth(0.9)
            if i == 0:
                cell.set_facecolor("#edf2ff")
                cell.set_text_props(
                    ha="center",
                    va="center",
                    fontsize=table_fontsize,
                    weight="bold",
                    color="#1b1f2a",
                )
            else:
                if j == 0:
                    cell.set_text_props(ha="left", color="#21242c")
                    cell.set_facecolor("#f6f8fe")
                    cell.PAD = 0.35
                else:
                    align = "right"
                    cell.set_text_props(ha=align, color="#1d2129")
                    row_color = "#ffffff" if i % 2 == 1 else "#f7f9ff"
                    cell.set_facecolor(row_color)

    # 底部注释
    fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.07)

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


def _generate_mock_holdings_data() -> Dict[str, Any]:
    """
    生成假数据用于测试期末持仓表格
    返回:
        Dict: 假数据字典
    """
    return {
        "summary": {
            "asset_net_value": 154.55,  # 资产净值（万元）
            "total_assets": 154.61,  # 资产总值（万元）
            "total_liabilities": 0.06,  # 负债合计（万元）
        },
        "assets": [
            {"name": "股票", "market_value": 154.35, "proportion": 99.87},
            {"name": "债券", "market_value": 0.00, "proportion": 0.00},
            {"name": "公募基金", "market_value": 0.00, "proportion": 0.00},
            {"name": "定期存款", "market_value": 0.00, "proportion": 0.00},
            {"name": "逆回购", "market_value": 0.00, "proportion": 0.00},
            {"name": "期货(保证金/市值)", "market_value": 0.00, "proportion": 0.00},
            {"name": "期权市值", "market_value": 0.00, "proportion": 0.00},
            {"name": "理财产品", "market_value": 0.00, "proportion": 0.00},
            {
                "name": "场外衍生品(保证金/市值)",
                "market_value": 0.00,
                "proportion": 0.00,
            },
            {"name": "现金", "market_value": 0.26, "proportion": 0.17},
            {"name": "其他资产", "market_value": 0.00, "proportion": 0.00},
        ],
        "liabilities": [
            {"name": "正回购", "market_value": 0.00, "proportion": 0.00},
            {"name": "短期借款", "market_value": 0.00, "proportion": 0.00},
            {"name": "融资融券", "market_value": 0.00, "proportion": 0.00},
            {"name": "其他负债", "market_value": 0.06, "proportion": 100.00},
        ],
    }


if __name__ == "__main__":
    # 测试表格生成
    print("正在生成期末持仓表格...")
    output_path = plot_end_period_holdings_table()
    print(f"表格已保存到: {output_path}")
