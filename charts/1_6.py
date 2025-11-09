"""
指标分析表格生成
使用 matplotlib 生成指标分析表格
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font

try:
    from pyecharts.charts import Bar
    from pyecharts import options as opts
    PYECHARTS_AVAILABLE = True
except ImportError:
    PYECHARTS_AVAILABLE = False
    print("警告: pyecharts 未安装，ECharts 功能将不可用。请运行: pip install pyecharts")



def _generate_mock_indicator_data() -> Dict[str, Dict[str, Any]]:
    """
    生成假数据用于测试指标分析表格
    
    返回:
        Dict: 包含各个指标的各个时间段数据
    """
    return {
        '*收益率(年化)': {
            '统计期间': 122.95,
            '近一个月': -192.21,
            '近三个月': 87.12,
            '近六个月': 109.18,
            '近一年': 122.95,
            '今年以来': 0.16,
            '成立以来': 62.59
        },
        '*波动率(年化)': {
            '统计期间': 35.23,
            '近一个月': 45.67,
            '近三个月': 38.92,
            '近六个月': 36.45,
            '近一年': 35.23,
            '今年以来': 40.12,
            '成立以来': 28.56
        },
        '*跟踪误差(年化)': {
            '统计期间': 32.45,
            '近一个月': 42.18,
            '近三个月': 35.67,
            '近六个月': 33.89,
            '近一年': 32.45,
            '今年以来': 37.23,
            '成立以来': 25.34
        },
        '*下行波动率(年化)': {
            '统计期间': 28.34,
            '近一个月': 38.45,
            '近三个月': 31.23,
            '近六个月': 29.56,
            '近一年': 28.34,
            '今年以来': 32.67,
            '成立以来': 22.45
        },
        '*夏普比率(年化)': {
            '统计期间': 3.49,
            '近一个月': -4.21,
            '近三个月': 2.24,
            '近六个月': 3.00,
            '近一年': 3.49,
            '今年以来': 0.00,
            '成立以来': 2.19
        },
        '*索提诺比率(年化)': {
            '统计期间': 4.34,
            '近一个月': -4.99,
            '近三个月': 2.79,
            '近六个月': 3.69,
            '近一年': 4.34,
            '今年以来': 0.00,
            '成立以来': 2.79
        },
        '*信息比率(年化)': {
            '统计期间': 3.79,
            '近一个月': -4.56,
            '近三个月': 2.44,
            '近六个月': 3.22,
            '近一年': 3.79,
            '今年以来': 0.00,
            '成立以来': 2.47
        },
        '*最大回撤': {
            '统计期间': -23.43,
            '近一个月': -23.43,
            '近三个月': -18.67,
            '近六个月': -23.43,
            '近一年': -23.43,
            '今年以来': -23.43,
            '成立以来': -23.43
        },
        '最大回撤期间': {
            '统计期间': '2024-12-12\n至2025-01-10',
            '近一个月': '2024-12-12\n至2025-01-10',
            '近三个月': '2024-12-12\n至2025-01-10',
            '近六个月': '2024-12-12\n至2025-01-10',
            '近一年': '2024-12-12\n至2025-01-10',
            '今年以来': '2024-12-12\n至2025-01-10',
            '成立以来': '2024-12-12\n至2025-01-10'
        },
        '最大回撤修复期(月)': {
            '统计期间': '-',
            '近一个月': '-',
            '近三个月': '-',
            '近六个月': '-',
            '近一年': '-',
            '今年以来': '-',
            '成立以来': '-'
        },
        '*卡玛比率': {
            '统计期间': 5.25,
            '近一个月': -8.20,
            '近三个月': 4.67,
            '近六个月': 4.66,
            '近一年': 5.25,
            '今年以来': -0.01,
            '成立以来': 2.67
        },
        '周胜率': {
            '统计期间': 0.65,
            '近一个月': 0.20,
            '近三个月': 0.58,
            '近六个月': 0.62,
            '近一年': 0.65,
            '今年以来': 0.50,
            '成立以来': 0.60
        },
        '月胜率': {
            '统计期间': 0.80,
            '近一个月': 0.00,
            '近三个月': 0.67,
            '近六个月': 0.75,
            '近一年': 0.80,
            '今年以来': 0.50,
            '成立以来': 0.75
        }
    }


def plot_indicator_analysis_table(
    data: Optional[Dict[str, Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (18, 10),
    return_figure: bool = False,
    table_fontsize: int = 12,
    row_height_scale: float = 2.2
):
    """
    绘制指标分析表格（matplotlib版本）
    
    参数:
        data: 数据字典，格式为：
            {
                '*收益率(年化)': {
                    '统计期间': 122.95, '近一个月': -192.21, ...
                },
                ...
            }
            如果为None，则使用假数据
        save_path: 保存路径
        figsize: 图表大小（宽，高）
        return_figure: 是否返回 figure 对象
        table_fontsize: 表格字体大小
        row_height_scale: 行高缩放比例
    
    返回:
        str: 保存的文件路径或 figure 对象
    """
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_indicator_data()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 准备表格数据
    periods = ['统计期间', '近一个月', '近三个月', '近六个月', '近一年', '今年以来', '成立以来']
    indicators = [
        '*收益率(年化)', '*波动率(年化)', '*跟踪误差(年化)', '*下行波动率(年化)',
        '*夏普比率(年化)', '*索提诺比率(年化)', '*信息比率(年化)', '*最大回撤',
        '最大回撤期间', '最大回撤修复期(月)', '*卡玛比率', '周胜率', '月胜率'
    ]
    
    # 构建表格数据
    table_data = []
    # 表头
    header = ['指标'] + periods
    table_data.append(header)
    
    # 数据行
    for indicator in indicators:
        row = [indicator]
        for period in periods:
            if indicator in data and period in data[indicator]:
                value = data[indicator][period]
                if isinstance(value, (int, float)):
                    # 判断是否需要添加百分号
                    if '收益率' in indicator or '波动率' in indicator or '跟踪误差' in indicator or '下行波动率' in indicator or '最大回撤' in indicator:
                        row.append(f'{value:.2f}%')
                    elif '胜率' in indicator:
                        row.append(f'{value:.2f}')
                    else:
                        row.append(f'{value:.2f}')
                else:
                    # 处理换行符，matplotlib 表格不支持换行，使用空格分隔
                    row.append(str(value).replace('\n', ' '))
            else:
                row.append('-')
        table_data.append(row)
    
    # 创建表格
    table = ax.table(
        cellText=table_data[1:],  # 数据行
        colLabels=table_data[0],  # 表头
        cellLoc='center',
        loc='center',
        bbox=[0, 0, 1, 1]
    )
    
    # 设置表格样式
    table.auto_set_font_size(False)
    table.set_fontsize(table_fontsize)
    table.scale(1, row_height_scale)
    
    # 设置表头样式
    for i in range(len(table_data[0])):
        cell = table[(0, i)]
        cell.set_facecolor('#f0f0f0')  # 浅灰色背景
        cell.set_text_props(weight='bold', ha='center')
        cell.set_edgecolor('#f0f0f0')
        cell.set_linewidth(1)
    
    # 设置数据行样式
    for i in range(1, len(table_data)):
        for j in range(len(table_data[0])):
            cell = table[(i, j)]
            # 第一列（指标列）左对齐，其他列右对齐
            # if j == 0:
            #     cell.set_text_props(ha='center', weight='bold')
            #     cell.set_facecolor('#ffffff')  # 浅灰色背景
            # else:
            cell.set_text_props(ha='center')
            # 交替行颜色
            if (i - 1) % 2 == 0:
                cell.set_facecolor('#ffffff')  # 白色
            else:
                cell.set_facecolor('#f8f8f8')  # 浅灰色
            cell.set_edgecolor('#f0f0f0')
            cell.set_linewidth(1)
    
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


if __name__ == '__main__':
    # 测试表格生成
    print("正在生成指标分析表格...")
    fig = plot_indicator_analysis_table(return_figure=True)
    plt.show()
    plt.close()

