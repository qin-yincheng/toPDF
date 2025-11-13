"""
产品表现总览表格生成
使用 matplotlib 和 pyecharts 生成产品表现总览表格
包含三个部分：总体表现、业绩统计、收益风险特征
"""

from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
from charts.font_config import setup_chinese_font
import numpy as np

try:
    from pyecharts import options as opts
    PYECHARTS_AVAILABLE = True
except ImportError:
    PYECHARTS_AVAILABLE = False
    print("警告: pyecharts 未安装，ECharts 功能将不可用。请运行: pip install pyecharts")



def _generate_mock_performance_data() -> Dict[str, Any]:
    """
    生成假数据用于测试产品表现总览表格
    
    返回:
        Dict: 包含产品表现数据
    """
    return {
        # 总体表现
        'product_name': '私募基金产品',
        'establishment_date': '2023-01-13',
        'current_scale': 154.55,  # 万元
        'investment_strategy': '无',
        
        # 业绩统计
        'latest_nav_date': '2025-01-14',
        'cumulative_nav': 1.3140,
        'unit_nav': 1.3140,
        'same_strategy_ranking': 6.46,  # %
        
        # 收益风险特征
        'total_return': 54.59,  # %
        'total_return_annualized': 122.95,  # %
        'active_return': 43.59,  # %
        'active_return_annualized': 98.18,  # %
        'max_drawdown': -23.43,  # %
        'sharpe_ratio': 2.75,
        'beta': 1.05,
        'absolute_return_risk_type': '属于高收益高风险',
        'active_return_risk_type': '属于高收益高风险',
        'profitability_under_equivalent_risk': '较强'
    }


def plot_performance_overview_table(
    data: Optional[Dict[str, Any]] = None,
    save_path: Optional[str] = None,
    figsize: tuple = (16, 8.5),
    return_figure: bool = False,
    show_title: bool = True
):
    """
    绘制产品表现总览表格（matplotlib版本）
    
    参数:
        data: 数据字典，格式为：
            {
                'product_name': '产品名称',
                'establishment_date': '2023-01-13',
                'current_scale': 154.55,
                'investment_strategy': '无',
                ...
            }
            如果为None，则使用假数据
        save_path: 保存路径
        figsize: 图表大小（宽，高）
    
    返回:
        str: 保存的文件路径
    """
    # 样式配置
    section_configs = {
        'title_fontsize': 22,
        'label_fontsize': 20,
        'value_fontsize': 20,
        'title_color': '#1D3557',
        'label_bg': '#F2F4F7',
        'value_bg': '#FFFFFF',
        'numeric_color': '#2563EB',
        'text_color': '#1F2933',
        'border_color': '#E1E6EF',
        'figure_bg': '#F7F8FB'
    }
    
    layout_config = {
        'col_widths': [0.26, 0.30, 0.36],
        'col_spacing': 0.05,
        'start_x': 0.04,
        'y_start': 0.87,
        'row_height': 0.105,
        'title_height': 0.07
    }
    
    # 配置中文字体
    setup_chinese_font()
    
    # 如果没有提供数据，生成假数据
    if data is None:
        data = _generate_mock_performance_data()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(section_configs['figure_bg'])
    ax.axis('off')
    ax.set_facecolor(section_configs['figure_bg'])
    
    # 准备三个部分的数据
    # 第一部分：总体表现
    section1_data = [
        ['产品名称', data.get('product_name', '')],
        ['成立日期', data.get('establishment_date', '')],
        ['当前规模', f"{data.get('current_scale', 0):.2f}万元"],
        ['投资策略', data.get('investment_strategy', '')]
    ]
    
    # 第二部分：业绩统计
    section2_data = [
        ['最新净值日期', data.get('latest_nav_date', '')],
        ['累计净值', f"{data.get('cumulative_nav', 0):.4f}"],
        ['单位净值', f"{data.get('unit_nav', 0):.4f}"],
        ['同策略收益排名', f"{data.get('same_strategy_ranking', 0):.2f}%"]
    ]
    
    # 第三部分：收益风险特征
    # 注意：前5行的数值需要设置为蓝色，后3行是文本保持黑色
    section3_data = [
        ['统计期间内产品总收益', f"{data.get('total_return', 0):.2f}%(年化 {data.get('total_return_annualized', 0):.2f}%)"],
        ['主动收益', f"{data.get('active_return', 0):.2f}%(年化 {data.get('active_return_annualized', 0):.2f}%)"],
        ['最大回撤', f"{data.get('max_drawdown', 0):.2f}%"],
        ['夏普比率', f"{data.get('sharpe_ratio', 0):.2f}"],
        ['β', f"{data.get('beta', 0):.2f}"],
        ['绝对收益风险类型', data.get('absolute_return_risk_type', '')],
        ['主动收益风险类型', data.get('active_return_risk_type', '')],
        ['同等风险下获利能力', data.get('profitability_under_equivalent_risk', '')]
    ]
    
    # 标记哪些行需要蓝色数值（前5行是数值，后3行是文本）
    section3_numeric_rows = [0, 1, 2, 3, 4]  # 前5行是数值
    
    # 计算每个表格的位置和大小
    col_widths = layout_config['col_widths']
    col_spacing = layout_config['col_spacing']
    start_x = layout_config['start_x']
    y_start = layout_config['y_start']
    row_height = layout_config['row_height']
    title_height = layout_config['title_height']
    
    # 绘制第一部分：总体表现（如果启用标题）
    if show_title:
        section1_title = '总体表现'
        # 绘制蓝色竖条（在标题前）
        rect1 = plt.Rectangle((start_x - 0.02, y_start + 0.01), 0.006, 0.045,
                              facecolor=section_configs['numeric_color'], edgecolor='none')
        ax.add_patch(rect1)
        ax.text(start_x, y_start + title_height, section1_title,
                fontsize=section_configs['title_fontsize'],
                fontweight='bold', color=section_configs['title_color'],
                ha='left', va='center')
    
    table1 = ax.table(
        cellText=section1_data,
        cellLoc='left',
        loc='center',
        bbox=[start_x, y_start - len(section1_data) * row_height,
              col_widths[0], len(section1_data) * row_height]
    )
    table1.auto_set_font_size(False)
    table1.scale(1, 1.5)
    
    # 设置第一部分表格样式
    for i in range(len(section1_data)):
        for j in range(2):
            cell = table1[(i, j)]
            if j == 0:
                cell.set_text_props(ha='left', weight='medium',
                                    fontsize=section_configs['label_fontsize'],
                                    color=section_configs['text_color'])
                cell.set_facecolor(section_configs['label_bg'])
            else:
                cell.set_text_props(ha='left',
                                    fontsize=section_configs['value_fontsize'],
                                    color=section_configs['text_color'])
                cell.set_facecolor(section_configs['value_bg'])
            cell.visible_edges = 'horizontal'
            cell.set_edgecolor(section_configs['border_color'])
            cell.set_linewidth(0.6)
    
    # 绘制第二部分：业绩统计（如果启用标题）
    x2 = start_x + col_widths[0] + col_spacing
    if show_title:
        section2_title = '业绩统计'
        ax.text(x2, y_start + title_height, section2_title,
                fontsize=section_configs['title_fontsize'],
                fontweight='bold', color=section_configs['title_color'],
                ha='left', va='center')
    
    table2 = ax.table(
        cellText=section2_data,
        cellLoc='left',
        loc='center',
        bbox=[x2, y_start - len(section2_data) * row_height,
              col_widths[1], len(section2_data) * row_height]
    )
    table2.auto_set_font_size(False)
    table2.scale(1, 1.5)
    
    # 设置第二部分表格样式
    for i in range(len(section2_data)):
        for j in range(2):
            cell = table2[(i, j)]
            if j == 0:
                cell.set_text_props(ha='left', weight='medium',
                                    fontsize=section_configs['label_fontsize'],
                                    color=section_configs['text_color'])
                cell.set_facecolor(section_configs['label_bg'])
            else:
                cell.set_text_props(ha='right',
                                    fontsize=section_configs['value_fontsize'],
                                    color=section_configs['numeric_color'])
                cell.set_facecolor(section_configs['value_bg'])
            cell.visible_edges = 'horizontal'
            cell.set_edgecolor(section_configs['border_color'])
            cell.set_linewidth(0.6)
    
    # 绘制第三部分：收益风险特征（如果启用标题）
    x3 = x2 + col_widths[1] + col_spacing
    if show_title:
        section3_title = '收益风险特征'
        ax.text(x3, y_start + title_height, section3_title,
                fontsize=section_configs['title_fontsize'],
                fontweight='bold', color=section_configs['title_color'],
                ha='left', va='center')
    
    table3 = ax.table(
        cellText=section3_data,
        cellLoc='left',
        loc='center',
        bbox=[x3, y_start - len(section3_data) * row_height,
              col_widths[2], len(section3_data) * row_height]
    )
    table3.auto_set_font_size(False)
    table3.scale(1, 1.5)
    
    # 设置第三部分表格样式
    for i in range(len(section3_data)):
        for j in range(2):
            cell = table3[(i, j)]
            if j == 0:
                cell.set_text_props(ha='left', weight='medium',
                                    fontsize=section_configs['label_fontsize'],
                                    color=section_configs['text_color'])
                cell.set_facecolor(section_configs['label_bg'])
            else:
                # 前5行的数值设置为蓝色，后3行保持黑色
                if i in section3_numeric_rows:
                    cell.set_text_props(ha='right',
                                        color=section_configs['numeric_color'],
                                        fontsize=section_configs['value_fontsize'])
                else:
                    cell.set_text_props(ha='right',
                                        color=section_configs['text_color'],
                                        fontsize=section_configs['value_fontsize'])
                cell.set_facecolor(section_configs['value_bg'])
            cell.visible_edges = 'horizontal'
            cell.set_edgecolor(section_configs['border_color'])
            cell.set_linewidth(0.6)
    
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


def plot_performance_overview_table_echarts(
    data: Optional[Dict[str, Any]] = None,
    html_path: str = '产品表现总览_echarts.html',
    width: str = "1600px",
    height: str = "800px"
) -> str:
    """
    使用 ECharts (pyecharts) 生成产品表现总览表格
    
    参数:
        data: 数据字典，格式与 plot_performance_overview_table 相同
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
        data = _generate_mock_performance_data()
    
    # 准备三个部分的数据
    section1_data = [
        ['产品名称', data.get('product_name', '')],
        ['成立日期', data.get('establishment_date', '')],
        ['当前规模', f"{data.get('current_scale', 0):.2f}万元"],
        ['投资策略', data.get('investment_strategy', '')]
    ]
    
    section2_data = [
        ['最新净值日期', data.get('latest_nav_date', '')],
        ['累计净值', f"{data.get('cumulative_nav', 0):.4f}"],
        ['单位净值', f"{data.get('unit_nav', 0):.4f}"],
        ['同策略收益排名', f"{data.get('same_strategy_ranking', 0):.2f}%"]
    ]
    
    section3_data = [
        ['统计期间内产品总收益', f"{data.get('total_return', 0):.2f}%(年化 {data.get('total_return_annualized', 0):.2f}%)"],
        ['主动收益', f"{data.get('active_return', 0):.2f}%(年化 {data.get('active_return_annualized', 0):.2f}%)"],
        ['最大回撤', f"{data.get('max_drawdown', 0):.2f}%"],
        ['夏普比率', f"{data.get('sharpe_ratio', 0):.2f}"],
        ['β', f"{data.get('beta', 0):.2f}"],
        ['绝对收益风险类型', data.get('absolute_return_risk_type', '')],
        ['主动收益风险类型', data.get('active_return_risk_type', '')],
        ['同等风险下获利能力', data.get('profitability_under_equivalent_risk', '')]
    ]
    
    # 生成 HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>产品表现总览</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: SimHei, Microsoft YaHei, Arial;
                margin: 0;
                background-color: #F7F8FB;
                color: #1F2933;
            }}
            .wrapper {{
                max-width: 1380px;
                margin: 48px auto;
                padding: 44px 54px;
                background-color: #FFFFFF;
                box-shadow: 0 22px 60px rgba(25, 55, 109, 0.16);
                border-radius: 20px;
            }}
            .container {{
                display: flex;
                gap: 44px;
            }}
            .section {{
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}
            .section-title {{
                font-size: 22px;
                font-weight: 700;
                text-align: center;
                text-align: left;
                position: relative;
                color: #1D3557;
                padding-left: 16px;
            }}
            .section-title::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 50%;
                transform: translateY(-50%);
                width: 6px;
                height: 24px;
                border-radius: 4px;
                background-color: #2563EB;
            }}
            .section-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 20px;
                border: none;
            }}
            .section-table td {{
                padding: 16px 20px;
                border-bottom: 1px solid #E1E6EF;
            }}
            .section-table tbody tr:last-child td {{
                border-bottom: none;
            }}
            .label-cell {{
                background-color: #F2F4F7;
                text-align: left;
                width: 42%;
                font-weight: 500;
            }}
            .value-cell {{
                background-color: #FFFFFF;
                text-align: right;
                width: 58%;
            }}
            .text-left {{
                text-align: left !important;
            }}
            .numeric-value {{
                color: #2563EB;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
            <!-- 第一部分：总体表现 -->
            <div class="section">
                <div class="section-title">总体表现</div>
                <table class="section-table">
"""
    
    # 添加第一部分数据
    for row in section1_data:
        html_content += f"""                    <tr>
                        <td class="label-cell">{row[0]}</td>
                        <td class="value-cell text-left">{row[1]}</td>
                    </tr>
"""
    
    html_content += """                </table>
            </div>
            
            <!-- 第二部分：业绩统计 -->
            <div class="section">
                <div class="section-title">业绩统计</div>
                <table class="section-table">
"""
    
    # 添加第二部分数据
    for row in section2_data:
        html_content += f"""                    <tr>
                        <td class="label-cell">{row[0]}</td>
                        <td class="value-cell numeric-value">{row[1]}</td>
                    </tr>
"""
    
    html_content += """                </table>
            </div>
            
            <!-- 第三部分：收益风险特征 -->
            <div class="section">
                <div class="section-title">收益风险特征</div>
                <table class="section-table">
"""
    
    # 添加第三部分数据（前5行数值为蓝色，后3行保持黑色）
    for i, row in enumerate(section3_data):
        if i < 5:  # 前5行是数值，设置为蓝色
            html_content += f"""                    <tr>
                        <td class="label-cell">{row[0]}</td>
                        <td class="value-cell numeric-value">{row[1]}</td>
                    </tr>
"""
        else:  # 后3行是文本，保持黑色
            html_content += f"""                    <tr>
                        <td class="label-cell">{row[0]}</td>
                        <td class="value-cell">{row[1]}</td>
                    </tr>
"""
    
    html_content += """                </table>
            </div>
        </div>
    </div>
    </body>
    </html>
"""
    
    # 保存 HTML 文件
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path


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


if __name__ == '__main__':
    # 测试 matplotlib 版本
    print("正在生成产品表现总览表格 (matplotlib)...")
    try:
        table_path = plot_performance_overview_table()
        print(f"表格已保存到: {table_path}")
    except PermissionError:
        print("警告: 文件可能正在被其他程序使用，请关闭后重试")
        import time
        time.sleep(1)
        table_path = plot_performance_overview_table(save_path='产品表现总览_new.pdf')
        print(f"表格已保存到: {table_path}")
    
    # 测试 ECharts 版本
    if PYECHARTS_AVAILABLE:
        print("\n正在生成产品表现总览表格 (ECharts HTML)...")
        table_html = plot_performance_overview_table_echarts()
        print(f"表格 HTML 已保存到: {table_html}")
        
        # 转换为高清 PDF
        print("\n正在将 HTML 转换为高清 PDF...")
        try:
            table_pdf = html_to_pdf(
                table_html,
                '产品表现总览_echarts.pdf',
                width=1600,
                height=800,
                wait_time=1000
            )
            print(f"表格 PDF: {table_pdf}")
        except Exception as e:
            print(f"PDF 转换失败: {e}")
            print("提示: 请安装 playwright: pip install playwright")
            print("然后运行: playwright install chromium")
    else:
        print("\n跳过 ECharts 测试（pyecharts 未安装）")

