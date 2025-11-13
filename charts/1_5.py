"""
收益分析图表生成
使用 matplotlib 和 pyecharts 生成收益分析表格和产品收益率对比柱状图
"""

from typing import Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from charts.font_config import setup_chinese_font
import numpy as np

try:
    from pyecharts.charts import Bar
    from pyecharts import options as opts
    PYECHARTS_AVAILABLE = True
except ImportError:
    PYECHARTS_AVAILABLE = False
    print("警告: pyecharts 未安装，ECharts 功能将不可用。请运行: pip install pyecharts")



def _draw_card_background(
    ax: plt.Axes,
    *,
    facecolor: str = "#ffffff",
    edgecolor: str = "#dce1eb",
    linewidth: float = 1.4,
    radius: float = 0.018,
    zorder: int = 0
):
    """
    在坐标轴内绘制圆角背景，营造卡片式层次。
    """
    card = FancyBboxPatch(
        (0, 0),
        1,
        1,
        transform=ax.transAxes,
        boxstyle=f"round,pad={radius}",
        linewidth=linewidth,
        facecolor=facecolor,
        edgecolor=edgecolor,
        zorder=zorder
    )
    ax.add_patch(card)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def _generate_mock_return_data() -> Dict[str, Dict[str, float]]:
    """
    生成假数据用于测试收益分析图表
    
    返回:
        Dict: 包含各个时间段的收益率数据
    """
    return {
        '统计期间': {'product_return': 54.59, 'benchmark_return': 10.99, 'excess_return': 43.59},
        '近一个月': {'product_return': -16.15, 'benchmark_return': -2.86, 'excess_return': -13.28},
        '近三个月': {'product_return': 21.78, 'benchmark_return': -3.55, 'excess_return': 25.33},
        '近六个月': {'product_return': 54.59, 'benchmark_return': 10.03, 'excess_return': 44.56},
        '近一年': {'product_return': 42.67, 'benchmark_return': 16.33, 'excess_return': 26.34},
        '今年以来': {'product_return': 0.08, 'benchmark_return': -2.91, 'excess_return': 2.98},
        '成立以来': {'product_return': 31.40, 'benchmark_return': -4.91, 'excess_return': 36.31}
    }


def plot_return_analysis_table(
    data: Optional[Dict[str, Dict[str, float]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (13, 8),
    return_figure: bool = False
):
    """
    绘制收益分析表格（matplotlib版本）
    
    参数:
        data: 数据字典，格式为：
            {
                '统计期间': {'product_return': 54.59, 'benchmark_return': 10.99, 'excess_return': 43.59},
                ...
            }
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
        data = _generate_mock_return_data()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#f5f7fb")
    ax.axis('off')
    _draw_card_background(ax, facecolor="#ffffff", edgecolor="#d6dbe6")
    
    # 准备表格数据 - 使用实际数据中的键而不是硬编码
    # 定义期间的优先顺序（如果存在则按此顺序显示）
    period_order = ['统计期间', '成立以来', '近一年', '近六个月', '近三个月', '近一个月', '今年以来']
    
    # 获取实际存在的期间（按优先顺序）
    periods = [p for p in period_order if p in data]
    # 如果还有其他期间不在优先列表中，也添加进来
    for key in data.keys():
        if key not in periods:
            periods.append(key)
    
    table_data = []
    raw_value_rows: list[list[Optional[float]]] = []
    table_data.append([' ', '组合收益率(%)', '基准收益率(%)', '超额收益率(%)'])  # 表头
    
    for period in periods:
        if period in data:
            row = [
                period,
                f'{data[period]["product_return"]:.2f}%',
                f'{data[period]["benchmark_return"]:.2f}%',
                f'{data[period]["excess_return"]:.2f}%'
            ]
            table_data.append(row)
            raw_value_rows.append([
                None,
                data[period]["product_return"],
                data[period]["benchmark_return"],
                data[period]["excess_return"]
            ])
    
    # 创建表格
    table = ax.table(
        cellText=table_data[1:],  # 数据行
        colLabels=table_data[0],  # 表头
        cellLoc='left',
        loc='upper left',
        bbox=[0.06, 0.1, 0.88, 0.82]
    )
    
    # 设置表格样式
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.05, 2.3)
    
    # 设置表头样式
    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor('#eef2fb')  # 浅灰色背景
        cell.set_text_props(weight='bold', fontsize=8, ha='center', color='#1f2d3d')
        cell.set_edgecolor('#eef2fb')
        cell.set_linewidth(0)
    
    # 设置数据行样式
    for i in range(1, len(table_data)):
        for j in range(4):
            cell = table[(i, j)]
            is_even_row = (i % 2 == 0)
            cell.set_facecolor('#ffffff' if is_even_row else '#f6f7fb')
            if j == 0:
                cell.set_text_props(weight='bold', ha='center', fontsize=8, color='#1a2233')
                cell.PAD = 0.5
            else:
                text_color = '#1a2233'
                if j == 3:
                    value = raw_value_rows[i-1][j]
                    if value is not None:
                        text_color = '#dc4a4a' if value < 0 else '#1f8a70'
                cell.set_text_props(ha='center', fontsize=8, color=text_color)
            cell.set_edgecolor('#e2e7f1')
            cell.set_linewidth(0.6)
            
    
    # 调整布局
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
    
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


def plot_return_comparison_chart(
    data: Optional[Dict[str, Dict[str, float]]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (10, 6),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制产品收益率对比柱状图（matplotlib版本）
    """
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_return_data()
    
    # 准备数据 - 使用实际数据中的键而不是硬编码
    period_order = ['统计期间', '成立以来', '近一年', '近六个月', '近三个月', '近一个月', '今年以来']
    periods = [p for p in period_order if p in data]
    for key in data.keys():
        if key not in periods:
            periods.append(key)
    
    product_returns = [data[p]['product_return'] for p in periods]
    benchmark_returns = [data[p]['benchmark_return'] for p in periods]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 设置柱状图位置
    x = np.arange(len(periods))
    width = 0.38
    gap = 0.06  # 两个柱子之间的间隔
    
    # 绘制柱状图
    color_product = '#1f3c88'
    color_benchmark = '#c5cad8'
    
    bars1 = ax.bar(
        x - (width + gap)/2,
        product_returns,
        width,
        label='产品收益率',
        color=color_product,
        edgecolor='none',
        linewidth=0,
        zorder=3
    )
    bars2 = ax.bar(
        x + (width + gap)/2,
        benchmark_returns,
        width,
        label='沪深300',
        color=color_benchmark,
        edgecolor='none',
        linewidth=0,
        zorder=3
    )
    
    # 设置坐标轴
    ax.set_xlabel('')
    ax.set_ylabel('收益率 (%)', color='#1a2233', fontsize=7, labelpad=6)
    if show_title:
        ax.set_title('产品收益率对比', fontsize=7, fontweight='bold', color='#1a2233', pad=6)
    ax.set_xticks(x)
    ax.set_xticklabels(periods, rotation=0, ha='center', fontsize=7, color='#1a2233')
    ax.tick_params(axis='y', labelsize=7, colors='#1a2233')
    ax.margins(y=0.15)
    ax.grid(True, alpha=0.25, linestyle='--', axis='y', color='#b9c2d3', zorder=1)
    
    # 设置边框：只保留左边框，删除其他边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_color('#b9c2d3')
    ax.spines['left'].set_linewidth(1.2)
    
    # 在零轴位置画一条明显的线
    ax.axhline(y=0, color='#8f97aa', linestyle='-', linewidth=1.2, zorder=2)
    
    # 关键修改：隐藏x轴刻度，显示y轴零刻度
    ax.tick_params(axis='x', which='both', bottom=False)  # 隐藏x轴刻度线
    ax.tick_params(axis='y', which='major', length=6, width=1.2, colors='#1a2233')
    
    # 设置图例
    legend = ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.12),
        ncol=2,
        frameon=False,
        fontsize=6,
        labelcolor='#1a2233'
    )
    for text in legend.get_texts():
        text.set_fontsize(6)
    
    # 添加数值标签
    for bar_group in (bars1, bars2):
        for bar in bar_group:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + (2 if height >= 0 else -2),
                f'{height:.2f}%',
                ha='center',
                va='bottom' if height >= 0 else 'top',
                fontsize=4,
                color='#1a2233'
            )
    
    # 调整布局
    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
    
    if return_figure:
        return fig
    
    if save_path:
        plt.savefig(save_path, format='pdf', bbox_inches='tight', dpi=300)
        plt.close()
        return save_path
    else:
        return fig

def plot_return_analysis_all(
    data: Optional[Dict[str, Dict[str, float]]] = None,
    table_path: str = '收益分析表格.pdf',
    chart_path: str = '产品收益率对比.pdf',
    figsize_table: tuple = (13, 8),
    figsize_chart: tuple = (14, 8)
) -> Tuple[str, str]:
    """
    生成收益分析表格和对比图表（matplotlib版本）
    
    参数:
        data: 数据字典
        table_path: 表格保存路径
        chart_path: 图表保存路径
        figsize_table: 表格大小
        figsize_chart: 图表大小
    
    返回:
        Tuple[str, str]: (表格文件路径, 图表文件路径)
    """
    table_file = plot_return_analysis_table(data=data, save_path=table_path, figsize=figsize_table)
    chart_file = plot_return_comparison_chart(data=data, save_path=chart_path, figsize=figsize_chart)
    
    return table_file, chart_file


# ==================== pyecharts 版本 ====================

def plot_return_analysis_table_echarts(
    data: Optional[Dict[str, Dict[str, float]]] = None,
    html_path: str = '收益分析表格_echarts.html',
    width: str = "1200px",
    height: str = "800px"
) -> str:
    """
    使用 ECharts (pyecharts) 生成收益分析表格
    
    参数:
        data: 数据字典，格式与 plot_return_analysis_table 相同
        html_path: HTML 文件路径
        width: 表格宽度
        height: 表格高度
    
    返回:
        str: HTML 文件路径
    """
    if not PYECHARTS_AVAILABLE:
        raise ImportError("pyecharts 未安装，请运行: pip install pyecharts")
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_return_data()
    
    # 准备表格数据
    periods = ['统计期间', '近一个月', '近三个月', '近六个月', '近一年', '今年以来', '成立以来']
    
    table_rows = []
    for period in periods:
        if period in data:
            row = [
                period,
                f'{data[period]["product_return"]:.2f}%',
                f'{data[period]["benchmark_return"]:.2f}%',
                f'{data[period]["excess_return"]:.2f}%'
            ]
            table_rows.append(row)
    
    # 生成 HTML 表格
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>收益分析表格</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: SimHei, Microsoft YaHei, Arial;
                margin: 20px;
                background-color: white;
            }}
            table {{
                border-collapse: collapse;
                margin: 20px auto;
                width: 90%;
                font-size: 12px;
            }}
            th {{
                background-color: #d3d3d3;
                color: black;
                font-weight: bold;
                padding: 12px;
                border: 1.5px solid black;
                text-align: center;
            }}
            td {{
                padding: 10px;
                border: 1px solid black;
                text-align: center;
            }}
            tr:nth-child(even) {{
                background-color: #f8f8f8;
            }}
            tr:nth-child(odd) {{
                background-color: #ffffff;
            }}
            tr:first-child td {{
                background-color: #f0f0f0;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <table>
            <thead>
                <tr>
                    <th>统计期间</th>
                    <th>组合收益率(%)</th>
                    <th>基准收益率(%)</th>
                    <th>超额收益率(%)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for row in table_rows:
        html_content += f"                <tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>\n"
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # 保存 HTML 文件
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path


def plot_return_comparison_chart_echarts(
    data: Optional[Dict[str, Dict[str, float]]] = None,
    html_path: str = '产品收益率对比_echarts.html',
    width: str = "1600px",
    height: str = "800px"
) -> str:
    """
    使用 ECharts (pyecharts) 生成产品收益率对比柱状图
    
    参数:
        data: 数据字典，格式与 plot_return_analysis_table 相同
        html_path: HTML 文件路径
        width: 图表宽度
        height: 图表高度
    
    返回:
        str: HTML 文件路径
    """
    if not PYECHARTS_AVAILABLE:
        raise ImportError("pyecharts 未安装，请运行: pip install pyecharts")
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_return_data()
    
    # 准备数据
    periods = ['统计期间', '近一个月', '近三个月', '近六个月', '近一年', '今年以来', '成立以来']
    product_returns = [data[p]['product_return'] for p in periods]
    benchmark_returns = [data[p]['benchmark_return'] for p in periods]
    
    # 创建分组柱状图（使用 SVG 渲染器生成矢量图）
    bar_chart = (
        Bar(init_opts=opts.InitOpts(
            width=width,
            height=height,
            bg_color="white",
            renderer="svg"  # 使用 SVG 渲染器生成矢量图
        ))
        .add_xaxis(periods)
        .add_yaxis(
            series_name="产品收益率",
            y_axis=product_returns,
            color="#1f77b4",
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="沪深300",
            y_axis=benchmark_returns,
            color="#d3d3d3",
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="产品收益率对比",
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
                name="时间段",
                axislabel_opts=opts.LabelOpts(rotate=0),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="收益率(%)",
                min_=-20,
                max_=50,
                split_number=7,
                axislabel_opts=opts.LabelOpts(formatter="{value}%"),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="shadow"
            )
        )
    )
    
    # 保存 HTML 文件
    bar_chart.render(html_path)
    return html_path


def plot_return_analysis_all_echarts(
    data: Optional[Dict[str, Dict[str, float]]] = None,
    table_html_path: str = '收益分析表格_echarts.html',
    chart_html_path: str = '产品收益率对比_echarts.html',
    width_table: str = "1200px",
    height_table: str = "800px",
    width_chart: str = "1600px",
    height_chart: str = "800px"
) -> Tuple[str, str]:
    """
    生成收益分析表格和对比图表（ECharts版本）
    
    参数:
        data: 数据字典
        table_html_path: 表格 HTML 路径
        chart_html_path: 图表 HTML 路径
        width_table: 表格宽度
        height_table: 表格高度
        width_chart: 图表宽度
        height_chart: 图表高度
    
    返回:
        Tuple[str, str]: (表格HTML文件路径, 图表HTML文件路径)
    """
    table_file = plot_return_analysis_table_echarts(
        data=data,
        html_path=table_html_path,
        width=width_table,
        height=height_table
    )
    chart_file = plot_return_comparison_chart_echarts(
        data=data,
        html_path=chart_html_path,
        width=width_chart,
        height=height_chart
    )
    
    return table_file, chart_file


def html_to_pdf(
    html_path: str,
    output_path: str,
    width: int = 1600,
    height: int = 800,
    wait_time: int = 2000
) -> str:
    """
    将 HTML 文件转换为高清 PDF（矢量格式）
    
    注意：如果 ECharts 使用 SVG 渲染器（renderer='svg'），
    则生成的 PDF 中的图表是真正的矢量格式，可以无损缩放。
    如果使用 Canvas 渲染器（默认），则 PDF 中的图表是栅格化的。
    
    参数:
        html_path: HTML 文件路径
        output_path: PDF 输出路径
        width: 图表宽度（像素）
        height: 图表高度（像素）
        wait_time: 等待图表渲染的时间（毫秒）
    
    返回:
        str: PDF 文件路径
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
            
            # 生成 PDF（矢量格式，高清）
            page.pdf(
                path=output_path,
                width=f'{width}px',
                height=f'{height}px',
                print_background=True,
                margin={'top': '0px', 'right': '0px', 'bottom': '0px', 'left': '0px'}
            )
            
            browser.close()
            return output_path
            
    except ImportError:
        # 如果 playwright 不可用，尝试使用 selenium + pdfkit
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            import pdfkit
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'--window-size={width},{height}')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(file_url)
            driver.implicitly_wait(wait_time / 1000)  # 转换为秒
            
            # 使用 pdfkit 转换（需要安装 wkhtmltopdf）
            options = {
                'page-size': 'A4',
                'margin-top': '0',
                'margin-right': '0',
                'margin-bottom': '0',
                'margin-left': '0',
                'encoding': "UTF-8",
                'no-outline': None
            }
            pdfkit.from_url(file_url, output_path, options=options)
            driver.quit()
            
            return output_path
            
        except ImportError:
            raise ImportError(
                "需要安装工具来生成 PDF。请运行：\n"
                "  pip install playwright\n"
                "  然后运行: playwright install chromium\n"
                "或者: pip install pdfkit selenium\n"
                "  并安装 wkhtmltopdf: https://wkhtmltopdf.org/downloads.html"
            )


def html_to_image(
    html_path: str,
    output_path: str,
    width: int = 1600,
    height: int = 800,
    wait_time: int = 2000
) -> str:
    """
    将 HTML 文件转换为高清图片
    
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
            
            # 截图保存为图片（高分辨率）
            page.screenshot(path=output_path, full_page=False, clip={'x': 0, 'y': 0, 'width': width, 'height': height})
            
            browser.close()
            return output_path
            
    except ImportError:
        # 如果 playwright 不可用，尝试使用 selenium
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
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
            raise ImportError(
                "需要安装截图工具来生成图片。请运行：\n"
                "  pip install playwright\n"
                "  然后运行: playwright install chromium\n"
                "或者: pip install selenium"
            )


def convert_echarts_to_pdfs(
    table_html_path: str,
    chart_html_path: str,
    table_output_path: str = '收益分析表格_echarts.pdf',
    chart_output_path: str = '产品收益率对比_echarts.pdf',
    table_width: int = 1200,
    table_height: int = 800,
    chart_width: int = 1600,
    chart_height: int = 800
) -> Tuple[str, str]:
    """
    将 ECharts HTML 文件转换为高清 PDF
    
    参数:
        table_html_path: 表格 HTML 文件路径
        chart_html_path: 图表 HTML 文件路径
        table_output_path: 表格 PDF 输出路径
        chart_output_path: 图表 PDF 输出路径
        table_width: 表格宽度（像素）
        table_height: 表格高度（像素）
        chart_width: 图表宽度（像素）
        chart_height: 图表高度（像素）
    
    返回:
        Tuple[str, str]: (表格PDF路径, 图表PDF路径)
    """
    table_pdf = html_to_pdf(
        table_html_path,
        table_output_path,
        width=table_width,
        height=table_height,
        wait_time=1000  # 表格渲染更快
    )
    chart_pdf = html_to_pdf(
        chart_html_path,
        chart_output_path,
        width=chart_width,
        height=chart_height,
        wait_time=2000  # 图表需要更多时间渲染
    )
    
    return table_pdf, chart_pdf


def convert_echarts_to_images(
    table_html_path: str,
    chart_html_path: str,
    table_output_path: str = '收益分析表格_高清.png',
    chart_output_path: str = '产品收益率对比_高清.png',
    table_width: int = 1200,
    table_height: int = 800,
    chart_width: int = 1600,
    chart_height: int = 800
) -> Tuple[str, str]:
    """
    将 ECharts HTML 文件转换为高清图片
    
    参数:
        table_html_path: 表格 HTML 文件路径
        chart_html_path: 图表 HTML 文件路径
        table_output_path: 表格图片输出路径
        chart_output_path: 图表图片输出路径
        table_width: 表格宽度（像素）
        table_height: 表格高度（像素）
        chart_width: 图表宽度（像素）
        chart_height: 图表高度（像素）
    
    返回:
        Tuple[str, str]: (表格图片路径, 图表图片路径)
    """
    table_img = html_to_image(
        table_html_path,
        table_output_path,
        width=table_width,
        height=table_height,
        wait_time=1000  # 表格渲染更快
    )
    chart_img = html_to_image(
        chart_html_path,
        chart_output_path,
        width=chart_width,
        height=chart_height,
        wait_time=2000  # 图表需要更多时间渲染
    )
    
    return table_img, chart_img


if __name__ == '__main__':
    # 测试 matplotlib 版本
    print("正在生成收益分析图表 (matplotlib)...")
    table_path, chart_path = plot_return_analysis_all()
    print(f"表格已保存到: {table_path}")
    print(f"图表已保存到: {chart_path}")
    
    # 测试 ECharts 版本
    if PYECHARTS_AVAILABLE:
        print("\n正在生成收益分析图表 (ECharts HTML)...")
        table_html, chart_html = plot_return_analysis_all_echarts()
        print(f"表格 HTML 已保存到: {table_html}")
        print(f"图表 HTML 已保存到: {chart_html}")
        
        # 转换为高清 PDF
        print("\n正在将 HTML 转换为高清 PDF...")
        try:
            table_pdf, chart_pdf = convert_echarts_to_pdfs(
                table_html,
                chart_html,
                table_output_path='收益分析表格_echarts.pdf',
                chart_output_path='产品收益率对比_echarts.pdf'
            )
            print(f"表格 PDF: {table_pdf}")
            print(f"图表 PDF: {chart_pdf}")
        except Exception as e:
            print(f"PDF 转换失败: {e}")
            print("提示: 请安装 playwright: pip install playwright")
            print("然后运行: playwright install chromium")
    else:
        print("\n跳过 ECharts 测试（pyecharts 未安装）")

