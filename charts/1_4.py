"""
日收益表现图表生成
使用 matplotlib 和 pyecharts 生成柱状图+折线图组合图表和摘要表格（分两个图片）
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

try:
    from pyecharts.charts import Bar, Line, Grid
    from pyecharts import options as opts
    # Table 组件在 pyecharts 2.0.9 中不存在，改用其他方式
    try:
        from pyecharts.components import Table
    except ImportError:
        Table = None
    PYECHARTS_AVAILABLE = True
    try:
        from pyecharts.render import make_snapshot  
        from snapshot_selenium import snapshot
        SNAPSHOT_AVAILABLE = True
    except ImportError:
        SNAPSHOT_AVAILABLE = False
        print("提示: snapshot-selenium 未安装，将只能生成 HTML 文件，无法生成 PNG 图片。")
except ImportError:
    PYECHARTS_AVAILABLE = False
    SNAPSHOT_AVAILABLE = False
    print("警告: pyecharts 未安装，ECharts 功能将不可用。请运行: pip install pyecharts")

# 保留 matplotlib 导入用于兼容
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


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


def plot_daily_return_chart(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制日收益表现折线柱状图（不含表格）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'daily_return': 0.5,      # 日收益率（%）
                    'cumulative_return': -10.0  # 累计收益率（%）
                },
                ...
            ]
            如果为None，则使用假数据
        save_path: 保存路径
        figsize: 图表大小（宽，高）
    
    返回:
        str: 保存的文件路径
    """
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_daily_return_data()
    
    # 解析数据
    dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
    daily_returns = [d['daily_return'] for d in data]
    cumulative_returns = [d.get('cumulative_return', 0) for d in data]
    
    # 计算摘要数据
    max_daily_return = max(daily_returns)
    min_daily_return = min(daily_returns)
    max_return_idx = daily_returns.index(max_daily_return)
    min_return_idx = daily_returns.index(min_daily_return)
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 左Y轴：日收益率（柱状图）
    color_bar = '#082868'  # 深蓝色
    # 减小width以增加柱子之间的间隔
    bar_width = 0.6  # 从1.0减小到0.6，增加间隔
    bars = ax.bar(dates, daily_returns, width=bar_width, alpha=0.7, 
                  color=color_bar, label='日收益率', edgecolor=color_bar, linewidth=0.5)
    
    # 添加零线
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, zorder=0)
    
    ax.set_xlabel('日期')
    ax.set_ylabel('收益率(%)', color='black')
    ax.set_ylim(-12, 12)
    ax.set_yticks([-10, -5, 0, 5, 10])
    ax.tick_params(axis='y', labelcolor='black')
    ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
    
    # 标注最大收益和最大亏损
    # 最大收益标注
    max_date = dates[max_return_idx]
    max_value = max_daily_return
    ax.annotate(
        f'{max_value:.2f}',
        xy=(max_date, max_value),
        xytext=(max_date, max_value + 1.5),
        ha='center',
        va='bottom',
        fontsize=9,
        color=color_bar,
        weight='bold',
        arrowprops=dict(arrowstyle='->', color=color_bar, lw=1.5),
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color_bar, alpha=0.8)
    )
    
    # 最大亏损标注
    min_date = dates[min_return_idx]
    min_value = min_daily_return
    ax.annotate(
        f'{min_value:.2f}',
        xy=(min_date, min_value),
        xytext=(min_date, min_value - 1.5),
        ha='center',
        va='top',
        fontsize=9,
        color=color_bar,
        weight='bold',
        arrowprops=dict(arrowstyle='->', color=color_bar, lw=1.5),
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color_bar, alpha=0.8)
    )
    
    # 右Y轴：累计收益率（折线图）
    ax2 = ax.twinx()
    color_line = '#afb0b2'  # 浅灰色
    line = ax2.plot(dates, cumulative_returns, color=color_line, marker='o', 
                   markersize=3, linewidth=2, label='累计收益率',
                   markerfacecolor='white', markeredgecolor=color_line, markeredgewidth=1.5)
    
    ax2.set_ylabel('累计收益率(%)', color='black')
    # 根据数据动态设置Y轴范围，留出一些空间
    max_cum_value = max(cumulative_returns) if cumulative_returns else 90
    ax2.set_ylim(-20, max(100, max_cum_value + 10))  # 至少到100，或最大值+10
    ax2.set_yticks([-20, 0, 20, 40, 60, 80, 100])  # 包含100的刻度
    ax2.tick_params(axis='y', labelcolor='black')
    
    # 标注累计收益率的最大值点
    # max_cum_idx = cumulative_returns.index(max(cumulative_returns))
    # max_cum_date = dates[max_cum_idx]
    # max_cum_value = max(cumulative_returns)
    # if max_cum_value > 80:  # 如果超过80%，标注
    #     ax2.annotate(
    #         f'{max_cum_value:.2f}%',
    #         xy=(max_cum_date, max_cum_value),
    #         xytext=(max_cum_date, max_cum_value + 5),
    #         ha='center',
    #         va='bottom',
    #         fontsize=9,
    #         color=color_line,
    #         weight='bold',
    #         arrowprops=dict(arrowstyle='->', color=color_line, lw=1.5),
    #         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color_line, alpha=0.8)
    #     )
    
    # 设置标题（如果启用）
    if show_title:
        ax.set_title('日收益表现', fontsize=14, fontweight='bold', pad=20)
    
    # 设置日期格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=15))  # 每15天一个刻度
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # 设置边框：只保留左边框，删除其他边框
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 同时处理右Y轴的边框（只保留右边框）
    ax2.spines['top'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # 设置图例（顶部居中，增加与图表的间隔）
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, 
             loc='upper center', bbox_to_anchor=(0.5, 1.2), 
             ncol=2, frameon=True)
    
    # 调整布局，为图例留出更多空间
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # 顶部留出4%的空间给图例
    
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


def plot_daily_return_table(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (6, 4),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制日收益表现摘要表格
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'daily_return': 0.5,      # 日收益率（%）
                    'cumulative_return': -10.0  # 累计收益率（%）
                },
                ...
            ]
            如果为None，则使用假数据
        save_path: 保存路径
        figsize: 图表大小（宽，高）
    
    返回:
        str: 保存的文件路径
    """
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_daily_return_data()
    
    # 解析数据
    daily_returns = [d['daily_return'] for d in data]
    
    # 计算摘要数据
    max_daily_return = max(daily_returns)
    min_daily_return = min(daily_returns)
    
    # 创建图表（只用于显示表格）
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    
    # 表格数据
    table_data = [
        ['单日最大收益', f'{max_daily_return:.2f}%'],
        ['单日最大亏损', f'{min_daily_return:.2f}%']
    ]
    
    # 创建表格
    table = ax.table(
        cellText=table_data,
        colLabels=None,
        cellLoc='center',
        loc='center',
        bbox=[0.2, 0.4, 0.6, 0.3]
    )
    
    # 设置表格样式
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2.5)
    
    # 设置表格单元格样式
    for i in range(len(table_data)):
        for j in range(2):
            cell = table[(i, j)]
            if j == 0:  # 第一列（标签）
                cell.set_text_props(weight='bold', ha='center', fontsize=12)
                cell.set_facecolor('#ffffff')
            else:  # 第二列（数值）
                cell.set_text_props(ha='center', fontsize=12)
                if i == 0:  # 最大收益，绿色
                    cell.set_text_props(color='black')
                else:  # 最大亏损，红色
                    cell.set_text_props(color='black')
            cell.set_edgecolor('#f0f0f0')
            cell.set_linewidth(1.5)
    
    # 设置标题（如果启用）
    if show_title:
        ax.text(0.5, 0.9, '日收益表现摘要', 
                transform=ax.transAxes,
                fontsize=14, fontweight='bold',
                ha='center', va='top')
    
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


def plot_daily_return_performance(
    data: Optional[List[Dict[str, Any]]] = None,
    chart_path: str = '日收益表现_图表.pdf',
    table_path: str = '日收益表现_表格.pdf',
    figsize_chart: tuple = (16, 8),
    figsize_table: tuple = (6, 4)
) -> Tuple[str, str]:
    """
    绘制日收益表现图（分别生成图表和表格两个图片）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'daily_return': 0.5,      # 日收益率（%）
                    'cumulative_return': -10.0  # 累计收益率（%）
                },
                ...
            ]
            如果为None，则使用假数据
        chart_path: 图表保存路径
        table_path: 表格保存路径
        figsize_chart: 图表大小（宽，高）
        figsize_table: 表格大小（宽，高）
    
    返回:
        Tuple[str, str]: (图表文件路径, 表格文件路径)
    """
    chart_file = plot_daily_return_chart(data=data, save_path=chart_path, figsize=figsize_chart)
    table_file = plot_daily_return_table(data=data, save_path=table_path, figsize=figsize_table)
    
    return chart_file, table_file


def _generate_mock_daily_return_data() -> List[Dict[str, Any]]:
    """
    生成假数据用于测试日收益表现图
    
    返回:
        List[Dict]: 假数据列表
    """
    # 生成日期范围：2024-08-01 到 2025-01-14
    start_date = datetime(2024, 8, 1)
    end_date = datetime(2025, 1, 14)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    n = len(dates)
    
    # 生成日收益率数据
    daily_returns = []
    cumulative_return = -10.0  # 从-10%开始
    
    # 在10月11日附近设置最大收益和最大亏损
    oct_11_index = (datetime(2024, 10, 11) - start_date).days
    
    for i in range(n):
        date = dates[i]
        
        # 基础波动
        base_return = np.random.normal(0, 2)
        
        # 在特定日期设置极值
        if i == oct_11_index:
            # 最大收益
            daily_return = 10.56
        elif i == oct_11_index - 1 or i == oct_11_index + 1:
            # 最大亏损（在最大收益前后）
            daily_return = -11.34
        else:
            # 正常波动
            daily_return = base_return
            # 在9月底到10月初有较大波动
            if (datetime(2024, 9, 25) - start_date).days <= i <= (datetime(2024, 10, 15) - start_date).days:
                daily_return = base_return + np.random.choice([-1, 1]) * np.random.uniform(3, 6)
            # 在12月12日附近有较高收益
            elif (datetime(2024, 12, 10) - start_date).days <= i <= (datetime(2024, 12, 15) - start_date).days:
                daily_return = base_return + np.random.uniform(2, 5)
        
        # 限制范围
        daily_return = max(-15, min(15, daily_return))
        daily_returns.append(daily_return)
        
        # 累计收益率
        cumulative_return += daily_return * 0.1  # 简化计算
        cumulative_return = max(-20, min(90, cumulative_return))
    
    # 重新计算累计收益率，使其更符合描述
    dec_12_index = (datetime(2024, 12, 12) - start_date).days
    cumulative_returns = []
    cum_value = -10.0
    
    for i, daily_ret in enumerate(daily_returns):
        if i == 0:
            cum_value = -10.0
        else:
            # 累计收益率：从-10%开始，逐步增长
            # 9月底到10月初快速上升
            if (datetime(2024, 9, 25) - start_date).days <= i <= (datetime(2024, 10, 15) - start_date).days:
                cum_value += abs(daily_ret) * 0.8  # 快速上升期
            # 10月到12月初持续增长
            elif i <= dec_12_index:
                cum_value += abs(daily_ret) * 0.5 if daily_ret > 0 else daily_ret * 0.3
            # 12月12日达到峰值
            if i == dec_12_index:
                cum_value = 87.76
            # 之后略有下降
            elif i > dec_12_index:
                cum_value -= np.random.uniform(0.3, 1.5)
        
        cum_value = max(-20, min(90, cum_value))
        cumulative_returns.append(cum_value)
    
    # 组装数据
    data = []
    for i, date in enumerate(dates):
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'daily_return': round(daily_returns[i], 2),
            'cumulative_return': round(cumulative_returns[i], 2)
        })
    
    return data


# ==================== pyecharts 版本 ====================

def plot_daily_return_chart_echarts(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: str = '日收益表现_图表_echarts.html',
    html_path: Optional[str] = None,
    width: str = "1600px",
    height: str = "800px"
) -> str:
    """
    使用 ECharts (pyecharts) 绘制日收益表现折线柱状图（不含表格）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'daily_return': 0.5,      # 日收益率（%）
                    'cumulative_return': -10.0  # 累计收益率（%）
                },
                ...
            ]
            如果为None，则使用假数据
        save_path: 保存图片路径（需要 snapshot-selenium）
        html_path: 保存 HTML 文件路径（可选，如果提供则生成 HTML）
        width: 图表宽度
        height: 图表高度
    
    返回:
        str: 保存的文件路径（HTML 或图片）
    """
    if not PYECHARTS_AVAILABLE:
        raise ImportError("pyecharts 未安装，请运行: pip install pyecharts snapshot-selenium")
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_daily_return_data()
    
    # 解析数据
    dates = [d['date'] for d in data]
    daily_returns = [d['daily_return'] for d in data]
    cumulative_returns = [d.get('cumulative_return', 0) for d in data]
    
    # 计算摘要数据用于标注
    max_daily_return = max(daily_returns)
    min_daily_return = min(daily_returns)
    max_return_idx = daily_returns.index(max_daily_return)
    min_return_idx = daily_returns.index(min_daily_return)
    max_cum_return = max(cumulative_returns)
    max_cum_idx = cumulative_returns.index(max_cum_return)
    
    # 创建柱状图（日收益率）- 左Y轴
    bar_chart = (
        Bar(init_opts=opts.InitOpts(
            width=width,
            height=height,
            bg_color="white"
        ))
        .add_xaxis(dates)
        .add_yaxis(
            series_name="日收益率",
            y_axis=daily_returns,
            yaxis_index=0,
            color="#1f77b4",
            label_opts=opts.LabelOpts(is_show=False),
        )
        .extend_axis(
            yaxis=opts.AxisOpts(
                name="累计收益率(%)",
                type_="value",
                min_=0,
                max_=90,
                position="right",
                axislabel_opts=opts.LabelOpts(formatter="{value}%"),
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="日收益表现",
                title_textstyle_opts=opts.TextStyleOpts(
                    font_size=14,
                    font_weight="bold"
                ),
                pos_left="left"
            ),
            legend_opts=opts.LegendOpts(
                pos_top="5%",
                pos_left="center",
                orient="horizontal",
                item_gap=20
            ),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                name="日期",
                axislabel_opts=opts.LabelOpts(
                    rotate=45,
                    interval=15  # 每15个数据点显示一个标签
                ),
                boundary_gap=True,
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="收益率(%)",
                min_=-12,
                max_=12,
                split_number=6,
                axislabel_opts=opts.LabelOpts(formatter="{value}%"),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross"
            )
        )
    )
    
    # 创建折线图（累计收益率）- 右Y轴
    line_chart = (
        Line()
        .add_xaxis(dates)
        .add_yaxis(
            series_name="累计收益率",
            y_axis=cumulative_returns,
            yaxis_index=1,  # 使用第二个Y轴
            color="#d3d3d3",
            symbol="circle",
            symbol_size=6,
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),
        )
    )
    
    # 组合图表
    bar_chart.overlap(line_chart)
    
    # 添加标注（使用 markPoint）- 使用日期字符串作为坐标
    max_date_str = dates[max_return_idx]
    min_date_str = dates[min_return_idx]
    max_cum_date_str = dates[max_cum_idx] if max_cum_return > 80 else None
    
    markpoint_data_max = [
        opts.MarkPointItem(
            name="最大收益",
            coord=[max_date_str, max_daily_return],
            value=f"{max_daily_return:.2f}%",
            itemstyle_opts=opts.ItemStyleOpts(color="#1f77b4")
        )
    ]
    markpoint_data_min = [
        opts.MarkPointItem(
            name="最大亏损",
            coord=[min_date_str, min_daily_return],
            value=f"{min_daily_return:.2f}%",
            itemstyle_opts=opts.ItemStyleOpts(color="#1f77b4")
        )
    ]
    
    # 为柱状图添加标注
    bar_chart.set_series_opts(
        markpoint_opts=opts.MarkPointOpts(data=markpoint_data_max + markpoint_data_min)
    )
    
    # 为折线图添加标注（如果累计收益率超过80%）
    if max_cum_date_str:
        markpoint_data_cum = [
            opts.MarkPointItem(
                name="累计收益峰值",
                coord=[max_cum_date_str, max_cum_return],
                value=f"{max_cum_return:.2f}%",
                itemstyle_opts=opts.ItemStyleOpts(color="#d3d3d3")
            )
        ]
        line_chart.set_series_opts(
            markpoint_opts=opts.MarkPointOpts(data=markpoint_data_cum)
        )
    
    # 重新组合（因为需要更新 markpoint）
    bar_chart.overlap(line_chart)
    
    # 如果提供了 HTML 路径，生成 HTML 文件
    if html_path:
        bar_chart.render(html_path)
        return html_path
    
    # 尝试生成图片（需要 snapshot-selenium）
    if SNAPSHOT_AVAILABLE:
        try:
            make_snapshot(snapshot, bar_chart.render(), save_path)
            return save_path
        except Exception as e:
            # 如果无法生成图片，生成 HTML 文件
            fallback_html = save_path.replace('.png', '.html')
            bar_chart.render(fallback_html)
            print(f"警告: 无法生成图片，已生成 HTML 文件: {fallback_html}")
            print(f"错误信息: {e}")
            return fallback_html
    else:
        # 生成 HTML 文件
        fallback_html = save_path.replace('.png', '.html')
        bar_chart.render(fallback_html)
        print(f"已生成 HTML 文件: {fallback_html}")
        return fallback_html


def plot_daily_return_table_echarts(
    data: Optional[List[Dict[str, Any]]] = None,
    save_path: str = '日收益表现_表格_echarts.html',
    html_path: Optional[str] = None,
    width: str = "600px",
    height: str = "400px"
) -> str:
    """
    使用 ECharts (pyecharts) 生成日收益表现摘要表格
    
    参数:
        data: 数据列表，格式与 plot_daily_return_chart_echarts 相同
        save_path: 保存图片路径（需要 snapshot-selenium）
        html_path: 保存 HTML 文件路径（可选，如果提供则生成 HTML）
        width: 表格宽度
        height: 表格高度
    
    返回:
        str: 保存的文件路径（HTML 或图片）
    """
    if not PYECHARTS_AVAILABLE:
        raise ImportError("pyecharts 未安装，请运行: pip install pyecharts snapshot-selenium")
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_daily_return_data()
    
    # 解析数据
    daily_returns = [d['daily_return'] for d in data]
    
    # 计算摘要数据
    max_daily_return = max(daily_returns)
    min_daily_return = min(daily_returns)
    
    # 创建表格数据
    table_data = [
        ["单日最大收益", f"{max_daily_return:.2f}%"],
        ["单日最大亏损", f"{min_daily_return:.2f}%"]
    ]
    
    # 尝试使用 Table 组件，如果失败则使用 HTML 回退
    html_content_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>日收益表现摘要</title>
        <style>
            body {{ font-family: SimHei, Microsoft YaHei, Arial; }}
            table {{ border-collapse: collapse; margin: 20px auto; width: 400px; }}
            th, td {{ border: 1px solid black; padding: 10px; text-align: center; }}
            th {{ background-color: #f0f0f0; font-weight: bold; }}
            .positive {{ color: green; }}
            .negative {{ color: red; }}
        </style>
    </head>
    <body>
        <h2 style="text-align: center;">日收益表现摘要</h2>
        <table>
            <tr><th>指标</th><th>数值</th></tr>
            <tr><td>单日最大收益</td><td class="positive">{max_daily_return:.2f}%</td></tr>
            <tr><td>单日最大亏损</td><td class="negative">{min_daily_return:.2f}%</td></tr>
        </table>
    </body>
    </html>
    """
    
    # 如果 Table 组件不可用，直接使用 HTML
    if Table is None:
        output_path = html_path if html_path else save_path.replace('.png', '.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content_template)
        print(f"已生成 HTML 文件: {output_path}")
        return output_path
    
    # 尝试使用 Table 组件
    try:
        table_chart = Table()
        table_chart.add(["指标", "数值"], table_data)
    except Exception as e:
        # Table 组件 API 不兼容，使用 HTML 回退
        output_path = html_path if html_path else save_path.replace('.png', '.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content_template)
        print(f"Table 组件不可用，已生成 HTML 文件: {output_path}")
        return output_path
    
    # 如果提供了 HTML 路径，生成 HTML 文件
    if html_path:
        table_chart.render(html_path)
        return html_path
    
    # 尝试生成图片（需要 snapshot-selenium）
    if SNAPSHOT_AVAILABLE:
        try:
            make_snapshot(snapshot, table_chart.render(), save_path)
            return save_path
        except Exception as e:
            # 如果无法生成图片，生成 HTML 文件
            fallback_html = save_path.replace('.png', '.html')
            table_chart.render(fallback_html)
            print(f"警告: 无法生成图片，已生成 HTML 文件: {fallback_html}")
            print(f"错误信息: {e}")
            return fallback_html
    else:
        # 生成 HTML 文件
        fallback_html = save_path.replace('.png', '.html')
        table_chart.render(fallback_html)
        print(f"已生成 HTML 文件: {fallback_html}")
        return fallback_html


def plot_daily_return_performance_echarts(
    data: Optional[List[Dict[str, Any]]] = None,
    chart_path: str = '日收益表现_图表_echarts.html',
    table_path: str = '日收益表现_表格_echarts.html',
    width_chart: str = "1600px",
    height_chart: str = "800px",
    width_table: str = "600px",
    height_table: str = "400px"
) -> Tuple[str, str]:
    """
    使用 ECharts (pyecharts) 绘制日收益表现图（分别生成图表和表格两个文件）
    
    参数:
        data: 数据列表，格式为：
            [
                {
                    'date': '2024-08-01',
                    'daily_return': 0.5,      # 日收益率（%）
                    'cumulative_return': -10.0  # 累计收益率（%）
                },
                ...
            ]
            如果为None，则使用假数据
        chart_path: 图表保存路径
        table_path: 表格保存路径
        width_chart: 图表宽度
        height_chart: 图表高度
        width_table: 表格宽度
        height_table: 表格高度
    
    返回:
        Tuple[str, str]: (图表文件路径, 表格文件路径)
    """
    chart_file = plot_daily_return_chart_echarts(
        data=data, 
        html_path=chart_path,
        width=width_chart,
        height=height_chart
    )
    table_file = plot_daily_return_table_echarts(
        data=data,
        html_path=table_path,
        width=width_table,
        height=height_table
    )
    
    return chart_file, table_file


def html_to_image(
    html_path: str,
    output_path: str,
    width: int = 1600,
    height: int = 800,
    wait_time: int = 2000
) -> str:
    """
    将 ECharts HTML 文件转换为高清图片
    
    参数:
        html_path: HTML 文件路径
        output_path: 图片输出路径（PNG 格式）
        width: 图表宽度（像素）
        height: 图表高度（像素）
        wait_time: 等待图表渲染的时间（毫秒）
    
    返回:
        str: 图片文件路径
    """
    import os
    
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML 文件不存在: {html_path}")
    
    html_abs_path = os.path.abspath(html_path).replace('\\', '/')
    file_url = f'file:///{html_abs_path}'
    
    # 尝试使用 playwright（推荐，质量好）
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.goto(file_url)
            page.wait_for_timeout(wait_time)  # 等待图表渲染
            
            # 截图保存为图片
            page.screenshot(path=output_path, full_page=False, clip={'x': 0, 'y': 0, 'width': width, 'height': height})
            
            browser.close()
            return output_path
            
    except ImportError:
        # 如果 playwright 不可用，尝试使用 selenium
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'--window-size={width},{height}')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(file_url)
            driver.implicitly_wait(wait_time / 1000)  # 转换为秒
            
            # 截图
            driver.save_screenshot(output_path)
            driver.quit()
            
            return output_path
            
        except ImportError:
            # 如果都没有，尝试使用 pyecharts 的 snapshot-selenium
            if SNAPSHOT_AVAILABLE:
                try:
                    # 读取 HTML 内容并直接转换
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    # 使用 make_snapshot 需要 HTML 内容的字符串
                    # 但这个方法主要用于图表对象，对于已有 HTML 文件需要其他方法
                    raise ImportError("snapshot-selenium 主要用于图表对象，不适用于 HTML 文件")
                except Exception as e:
                    raise ImportError(
                        f"无法生成图片: {e}\n"
                        "请安装以下工具之一：\n"
                        "  - playwright: pip install playwright && playwright install chromium\n"
                        "  - selenium: pip install selenium\n"
                        "  - 或使用 pyecharts 的 snapshot-selenium: pip install snapshot-selenium"
                    )
            else:
                raise ImportError(
                    "需要安装截图工具来生成图片。请运行：\n"
                    "  pip install playwright\n"
                    "  然后运行: playwright install chromium\n"
                    "或者: pip install selenium"
                )


def convert_echarts_html_to_images(
    chart_html_path: str,
    table_html_path: str,
    chart_output_path: str = '日收益表现_图表_高清.png',
    table_output_path: str = '日收益表现_表格_高清.png',
    chart_width: int = 1600,
    chart_height: int = 800,
    table_width: int = 600,
    table_height: int = 400
) -> Tuple[str, str]:
    """
    将 ECharts HTML 文件转换为高清图片
    
    参数:
        chart_html_path: 图表 HTML 文件路径
        table_html_path: 表格 HTML 文件路径
        chart_output_path: 图表图片输出路径
        table_output_path: 表格图片输出路径
        chart_width: 图表宽度（像素）
        chart_height: 图表高度（像素）
        table_width: 表格宽度（像素）
        table_height: 表格高度（像素）
    
    返回:
        Tuple[str, str]: (图表图片路径, 表格图片路径)
    """
    chart_img = html_to_image(
        chart_html_path, 
        chart_output_path, 
        width=chart_width, 
        height=chart_height
    )
    table_img = html_to_image(
        table_html_path, 
        table_output_path, 
        width=table_width, 
        height=table_height,
        wait_time=1000  # 表格渲染更快
    )
    
    return chart_img, table_img


if __name__ == '__main__':
    # 测试 matplotlib 图表生成（分别生成两个图片）
    print("正在生成日收益表现图表 (matplotlib)...")
    chart_path, table_path = plot_daily_return_performance()
    print(f"图表已保存到: {chart_path}")
    print(f"表格已保存到: {table_path}")
    
    # 测试 ECharts 图表生成
    if PYECHARTS_AVAILABLE:
        print("\n正在生成日收益表现图表 (ECharts)...")
        chart_path_echarts, table_path_echarts = plot_daily_return_performance_echarts()
        print(f"图表已保存到: {chart_path_echarts}")
        print(f"表格已保存到: {table_path_echarts}")
        
        # 转换为高清图片
        print("\n正在将 HTML 转换为高清图片...")
        try:
            chart_img, table_img = convert_echarts_html_to_images(
                chart_path_echarts,
                table_path_echarts,
                chart_output_path='日收益表现_图表_高清.png',
                table_output_path='日收益表现_表格_高清.png'
            )
            print(f"图表高清图片: {chart_img}")
            print(f"表格高清图片: {table_img}")
        except Exception as e:
            print(f"图片转换失败: {e}")
            print("提示: 请安装 playwright: pip install playwright")
            print("然后运行: playwright install chromium")
    else:
        print("\n跳过 ECharts 测试（pyecharts 未安装）")

