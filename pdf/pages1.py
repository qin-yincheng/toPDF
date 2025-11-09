"""
第一页综合报告生成
将所有图表整合到一页 PDF 中
直接调用各个图表生成函数，获取 figure 对象后统一生成 PDF
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Optional, Dict, Any
import os
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as backend_pdf


def setup_chinese_fonts() -> None:
    """
    配置中文字体
    """
    font_paths = {
        "SimHei": "C:/Windows/Fonts/simhei.ttf",
        "SimSun": "C:/Windows/Fonts/simsun.ttc",
    }

    for font_name, font_path in font_paths.items():
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
            except Exception as e:
                print(f"注册字体失败 {font_name}: {e}")


def figure_to_image(fig, dpi: int = 200) -> BytesIO:
    """
    将 matplotlib figure 对象转换为 PNG 图片

    参数:
        fig: matplotlib figure 对象
        dpi: 图片分辨率（默认 200）

    返回:
        BytesIO: 图片数据流
    """
    try:
        img_io = BytesIO()
        fig.savefig(
            img_io, format="png", dpi=dpi, bbox_inches="tight", facecolor="white"
        )
        img_io.seek(0)
        plt.close(fig)  # 关闭 figure 释放内存
        return img_io
    except Exception as e:
        print(f"  转换图片失败: {e}")
        plt.close(fig)
        raise


def insert_figure(
    canvas_obj: canvas.Canvas,
    fig,
    x: float,
    y: float,
    width: float,
    height: float,
    dpi: int = 200,
    title: Optional[str] = None,
) -> bool:
    """
    将 matplotlib figure 对象插入到画布中

    参数:
        canvas_obj: reportlab Canvas 对象
        fig: matplotlib figure 对象
        x: X 坐标（单位：点）
        y: Y 坐标（单位：点）
        width: 宽度（单位：点）
        height: 高度（单位：点）
        dpi: 图片分辨率（默认 200）
        title: 标题文本（可选）

    返回:
        bool: 是否成功
    """
    try:
        img_io = figure_to_image(fig, dpi=dpi)
        # 直接绘制图片；标题改由 draw_section_title 统一绘制
        canvas_obj.drawImage(ImageReader(img_io), x, y, width=width, height=height)
        return True
    except Exception as e:
        print(f"插入图表失败: {e}")
        # 绘制占位框
        canvas_obj.rect(x, y, width, height, stroke=1, fill=0)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawString(x + 5, y + height / 2, "图表生成失败")
        return False


def generate_page1(
    output_path: str = "第一页综合报告.pdf", data: Optional[Dict[str, Any]] = None
) -> str:
    """
    生成第一页综合报告，整合所有图表

    参数:
        output_path: 输出 PDF 文件路径
        data: 数据字典，包含所有图表所需的数据（可选）
            如果为 None，各个图表函数会使用假数据

    返回:
        str: 保存的文件路径
    """
    # 配置中文字体
    setup_chinese_fonts()

    # 导入各个图表生成函数
    import sys

    # 添加 charts 目录到路径
    charts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "charts")
    if charts_dir not in sys.path:
        sys.path.insert(0, charts_dir)

    # 直接导入各个模块
    import importlib.util

    # 导入 1_1.py
    spec1 = importlib.util.spec_from_file_location(
        "chart1_1", os.path.join(charts_dir, "1_1.py")
    )
    chart1_1 = importlib.util.module_from_spec(spec1)
    spec1.loader.exec_module(chart1_1)

    # 导入 1_2.py
    spec2 = importlib.util.spec_from_file_location(
        "chart1_2", os.path.join(charts_dir, "1_2.py")
    )
    chart1_2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(chart1_2)

    # 导入 1_3.py
    spec3 = importlib.util.spec_from_file_location(
        "chart1_3", os.path.join(charts_dir, "1_3.py")
    )
    chart1_3 = importlib.util.module_from_spec(spec3)
    spec3.loader.exec_module(chart1_3)

    # 导入 1_4.py
    spec4 = importlib.util.spec_from_file_location(
        "chart1_4", os.path.join(charts_dir, "1_4.py")
    )
    chart1_4 = importlib.util.module_from_spec(spec4)
    spec4.loader.exec_module(chart1_4)

    # 导入 1_5.py
    spec5 = importlib.util.spec_from_file_location(
        "chart1_5", os.path.join(charts_dir, "1_5.py")
    )
    chart1_5 = importlib.util.module_from_spec(spec5)
    spec5.loader.exec_module(chart1_5)

    # 导入 1_6.py
    spec6 = importlib.util.spec_from_file_location(
        "chart1_6", os.path.join(charts_dir, "1_6.py")
    )
    chart1_6 = importlib.util.module_from_spec(spec6)
    spec6.loader.exec_module(chart1_6)

    # 导入 2_1.py
    spec2_1 = importlib.util.spec_from_file_location(
        "chart2_1", os.path.join(charts_dir, "2_1.py")
    )
    chart2_1 = importlib.util.module_from_spec(spec2_1)
    spec2_1.loader.exec_module(chart2_1)

    # 导入 2_2.py
    spec2_2 = importlib.util.spec_from_file_location(
        "chart2_2", os.path.join(charts_dir, "2_2.py")
    )
    chart2_2 = importlib.util.module_from_spec(spec2_2)
    spec2_2.loader.exec_module(chart2_2)

    # 导入 2_3.py
    spec2_3 = importlib.util.spec_from_file_location(
        "chart2_3", os.path.join(charts_dir, "2_3.py")
    )
    chart2_3 = importlib.util.module_from_spec(spec2_3)
    spec2_3.loader.exec_module(chart2_3)

    # 导入 2_4.py
    spec2_4 = importlib.util.spec_from_file_location(
        "chart2_4", os.path.join(charts_dir, "2_4.py")
    )
    chart2_4 = importlib.util.module_from_spec(spec2_4)
    spec2_4.loader.exec_module(chart2_4)

    # 导入 2_5.py
    spec2_5 = importlib.util.spec_from_file_location(
        "chart2_5", os.path.join(charts_dir, "2_5.py")
    )
    chart2_5 = importlib.util.module_from_spec(spec2_5)
    spec2_5.loader.exec_module(chart2_5)

    # 导入 3_1.py
    spec3_1 = importlib.util.spec_from_file_location(
        "chart3_1", os.path.join(charts_dir, "3_1.py")
    )
    chart3_1 = importlib.util.module_from_spec(spec3_1)
    spec3_1.loader.exec_module(chart3_1)

    # 导入 3_2.py
    spec3_2 = importlib.util.spec_from_file_location(
        "chart3_2", os.path.join(charts_dir, "3_2.py")
    )
    chart3_2 = importlib.util.module_from_spec(spec3_2)
    spec3_2.loader.exec_module(chart3_2)

    # 导入 3_3.py
    spec3_3 = importlib.util.spec_from_file_location(
        "chart3_3", os.path.join(charts_dir, "3_3.py")
    )
    chart3_3 = importlib.util.module_from_spec(spec3_3)
    spec3_3.loader.exec_module(chart3_3)

    # 导入 3_4.py
    spec3_4 = importlib.util.spec_from_file_location(
        "chart3_4", os.path.join(charts_dir, "3_4.py")
    )
    chart3_4 = importlib.util.module_from_spec(spec3_4)
    spec3_4.loader.exec_module(chart3_4)

    # 导入 4_1.py
    spec4_1 = importlib.util.spec_from_file_location(
        "chart4_1", os.path.join(charts_dir, "4_1.py")
    )
    chart4_1 = importlib.util.module_from_spec(spec4_1)
    spec4_1.loader.exec_module(chart4_1)

    # 导入 4_2.py
    spec4_2 = importlib.util.spec_from_file_location(
        "chart4_2", os.path.join(charts_dir, "4_2.py")
    )
    chart4_2 = importlib.util.module_from_spec(spec4_2)
    spec4_2.loader.exec_module(chart4_2)

    # 导入 5_1.py
    spec5_1 = importlib.util.spec_from_file_location(
        "chart5_1", os.path.join(charts_dir, "5_1.py")
    )
    chart5_1 = importlib.util.module_from_spec(spec5_1)
    spec5_1.loader.exec_module(chart5_1)

    # 导入 5_2.py
    spec5_2 = importlib.util.spec_from_file_location(
        "chart5_2", os.path.join(charts_dir, "5_2.py")
    )
    chart5_2 = importlib.util.module_from_spec(spec5_2)
    spec5_2.loader.exec_module(chart5_2)

    # 导入 6_4.py
    spec6_4 = importlib.util.spec_from_file_location(
        "chart6_4", os.path.join(charts_dir, "6_4.py")
    )
    chart6_4 = importlib.util.module_from_spec(spec6_4)
    spec6_4.loader.exec_module(chart6_4)

    # 导入 6_5.py
    spec6_5 = importlib.util.spec_from_file_location(
        "chart6_5", os.path.join(charts_dir, "6_5.py")
    )
    chart6_5 = importlib.util.module_from_spec(spec6_5)
    spec6_5.loader.exec_module(chart6_5)

    # 获取函数引用
    plot_performance_overview_table = chart1_1.plot_performance_overview_table
    plot_scale_overview = chart1_2.plot_scale_overview
    plot_nav_performance = chart1_3.plot_nav_performance
    plot_daily_return_chart = chart1_4.plot_daily_return_chart
    plot_daily_return_table = chart1_4.plot_daily_return_table
    plot_return_analysis_table = chart1_5.plot_return_analysis_table
    plot_return_comparison_chart = chart1_5.plot_return_comparison_chart
    plot_indicator_analysis_table = chart1_6.plot_indicator_analysis_table
    plot_dynamic_drawdown_chart = chart2_1.plot_dynamic_drawdown_chart
    plot_dynamic_drawdown_table = chart2_1.plot_dynamic_drawdown_table
    plot_asset_allocation_chart = chart2_2.plot_asset_allocation_chart
    plot_end_period_holdings_table = chart2_3.plot_end_period_holdings_table
    plot_stock_position_chart = chart2_4.plot_stock_position_chart
    plot_liquidity_asset_chart = chart2_5.plot_liquidity_asset_chart
    plot_market_value_pie_chart = chart3_1.plot_market_value_pie_chart
    plot_average_market_value_bar_chart = chart3_1.plot_average_market_value_bar_chart
    plot_industry_holding_table = chart3_1.plot_industry_holding_table
    plot_industry_proportion_timeseries = chart3_2.plot_industry_proportion_timeseries
    plot_industry_deviation_timeseries = chart3_3.plot_industry_deviation_timeseries
    plot_asset_performance_attribution_table = (
        chart3_4.plot_asset_performance_attribution_table
    )
    plot_brinson_attribution = chart4_1.plot_brinson_attribution
    plot_brinson_industry_bar_chart = chart4_1.plot_brinson_industry_bar_chart
    plot_brinson_attribution_table = chart4_1.plot_brinson_attribution_table
    plot_industry_attribution_profit_table = (
        chart4_2.plot_industry_attribution_profit_table
    )
    plot_industry_attribution_profit_chart = (
        chart4_2.plot_industry_attribution_profit_chart
    )
    plot_industry_attribution_loss_table = chart4_2.plot_industry_attribution_loss_table
    plot_industry_attribution_loss_chart = chart4_2.plot_industry_attribution_loss_chart
    plot_stock_profit_table = chart5_1.plot_stock_profit_table
    plot_stock_profit_chart = chart5_1.plot_stock_profit_chart
    plot_stock_loss_table = chart5_1.plot_stock_loss_table
    plot_stock_loss_chart = chart5_1.plot_stock_loss_chart
    plot_stock_holding_nodes_table = chart5_2.plot_stock_holding_nodes_table
    plot_stock_holding_nodes_chart = chart5_2.plot_stock_holding_nodes_chart
    plot_turnover_rate_table = chart6_4.plot_turnover_rate_table
    plot_period_transaction_table = chart6_5.plot_period_transaction_table
    plot_period_transaction_chart = chart6_5.plot_period_transaction_chart

    # 数据提取辅助函数 - 安全地从 page1_data 提取子数据
    def safe_get(path, default=None):
        """从嵌套字典中安全提取数据
        path: 'key' 或 'key.subkey' 或 'key.subkey.item'
        """
        if data is None:
            return default
        keys = path.split(".")
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key, default)
            else:
                return default
            if result is None:
                return default
        return result

    # 处理输出文件占用问题：若原文件被占用，自动改名为 _new
    final_output = output_path
    try:
        # 尝试写入测试并删掉，判断是否可写
        with open(final_output, "wb") as _f:
            pass
        os.remove(final_output)
    except PermissionError:
        base, ext = os.path.splitext(output_path)
        final_output = f"{base}_new{ext}"

    # 创建 PDF 画布
    c = canvas.Canvas(final_output, pagesize=A4)
    page_width, page_height = A4

    # 定义布局参数（单位：点，1 inch = 72 points）
    margin = 20  # 边距
    top_margin = 20
    bottom_margin = 20

    # 计算可用区域
    usable_width = page_width - 2 * margin
    usable_height = page_height - top_margin - bottom_margin

    # 绘制标题帮助函数
    def draw_section_title(y_top: float, text: str) -> float:
        """在 y_top 处绘制左对齐标题与蓝色竖条，返回内容起始 y 坐标。"""
        try:
            c.setFont("SimHei", 8)
        except:
            c.setFont("Helvetica-Bold", 8)
        font_size = 8
        # 文本字符高度（中文字符高度约为字体大小的0.85倍）
        text_height = font_size * 0.85
        # 竖条高度与文本高度一致
        bar_height = text_height
        # 确定对齐中心位置（从 y_top 向下偏移，使标题区域居中）
        center_y = y_top - font_size * 0.5
        # 蓝色竖条：以 center_y 为中心
        bar_x = margin - 3
        bar_y = center_y - bar_height / 2
        c.setFillColorRGB(0.12, 0.47, 0.71)
        c.rect(bar_x, bar_y, 3, bar_height, fill=1, stroke=0)
        # 标题文本：计算基线位置，使文本中心与竖条中心对齐
        # 文本中心在基线上方约字体大小的0.4倍处
        text_baseline = center_y - font_size * 0.4
        c.setFillColorRGB(0, 0, 0)
        c.drawString(margin + 5, text_baseline, text)
        # 内容区域顶边（根据字体大小动态留白）
        return y_top - (font_size + 8)

    # 行高配置（按小标题一行一行分布图片）
    row_heights = {
        "overview": usable_height * 0.18,
        "scale": usable_height * 0.18,
        "nav": usable_height * 0.20,
        "daily": usable_height * 0.18,
        "returns": usable_height * 0.18,
        "indicator": usable_height * 0.18,
        "drawdown": usable_height * 0.18,
        "asset_allocation": usable_height * 0.18,
        "holdings": usable_height * 0.18,
        "stock_position": usable_height * 0.18,
        "liquidity_asset": usable_height * 0.18,
        "industry_pie": usable_height * 0.18,
        "industry_bar": usable_height * 0.18,
        "industry_table": usable_height * 0.18,
        "industry_timeseries": usable_height * 0.20,
        "industry_deviation": usable_height * 0.18,
        "asset_performance": usable_height * 0.15,
        "brinson_attribution": usable_height * 0.18,
        "brinson_industry_bar": usable_height * 0.18,
        "brinson_table": usable_height * 0.15,
        "industry_attribution_profit": usable_height * 0.25,
        "industry_attribution_loss": usable_height * 0.25,
        "industry_attribution_table": usable_height * 0.25,
        "industry_attribution_chart": usable_height * 0.25,
        "stock_attribution_table": usable_height * 0.25,
        "stock_attribution_chart": usable_height * 0.25,
        "stock_holding_nodes_table": usable_height * 0.25,
        "stock_holding_nodes_chart": usable_height * 0.25,
        "turnover_rate_table": usable_height * 0.15,
        "period_transaction_table": usable_height * 0.25,
        "period_transaction_chart": usable_height * 0.25,
    }

    x_left = margin
    y_cursor = page_height - top_margin  # 从顶部往下排版

    # 分页辅助函数
    def new_page() -> None:
        nonlocal y_cursor
        c.showPage()
        y_cursor = page_height - top_margin

    def ensure_space(needed_height: float) -> None:
        """如果当前页剩余空间不足以容纳 needed_height，则自动分页。"""
        nonlocal y_cursor
        safe_bottom = bottom_margin + 10
        if y_cursor - needed_height < safe_bottom:
            new_page()

    print("正在生成图表...")
    # 行1：总体表现（整行）
    try:
        print("  生成总体表现表格...")
        h = row_heights["overview"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "总体表现")
        fig1 = plot_performance_overview_table(
            data=safe_get("performance_overview"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig1, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  总体表现表格生成失败: {e}")

    # 行2：产品规模总览（含右侧表格）
    try:
        print("  生成产品规模总览图表（含右侧表格）...")
        h = row_heights["scale"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "产品规模总览")
        # scale_overview.scale_series 才是图表期望的列表数据
        fig2 = plot_scale_overview(
            data=safe_get("scale_overview.scale_series"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
            include_right_table=True,
            table_fontsize=12,
        )
        insert_figure(c, fig2, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  产品规模总览图表生成失败: {e}")

    # 行3：单位净值表现（整行）
    try:
        print("  生成单位净值表现图表...")
        h = row_heights["nav"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "单位净值表现")
        fig3 = plot_nav_performance(
            data=safe_get("nav_performance.nav_series"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig3, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  单位净值表现图表生成失败: {e}")

    # 行4：日收益表现（同一行，左图右表）
    try:
        print("  生成日收益表现图表...")
        h = row_heights["daily"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "日收益表现")
        # 左图占 70%，右表占 30%
        left_w = usable_width * 0.7
        right_w = usable_width - left_w - 5
        fig4 = plot_daily_return_chart(
            data=safe_get("nav_performance.daily_returns"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig4, x_left, y_cursor - h, left_w, h)
        # 右侧表格
        fig5 = plot_daily_return_table(
            data=safe_get("nav_performance.daily_returns"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig5, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 15  # 增加间距，确保与下一部分分离
    except Exception as e:
        print(f"  日收益表现图表生成失败: {e}")

    # 行5：收益分析（同一行，左表右图）
    try:
        print("  生成收益分析表格与图表...")
        h = row_heights["returns"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "收益分析")
        left_w = usable_width * 0.5
        right_w = usable_width - left_w - 5
        # 恢复原始大小，不再缩小
        # plot_return_analysis_table 期望字典格式，使用 period_returns 而非 period_returns_table
        fig6 = plot_return_analysis_table(
            data=safe_get("nav_performance.period_returns"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h / 72 * 2.54),
        )
        insert_figure(c, fig6, x_left, y_cursor - h, left_w, h)
        fig7 = plot_return_comparison_chart(
            data=safe_get("nav_performance.period_returns"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig7, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  收益分析生成失败: {e}")

    # 行6：指标分析（整行）
    try:
        print("  生成指标分析表格...")
        h = row_heights["indicator"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "指标分析")
        fig8 = plot_indicator_analysis_table(
            data=safe_get("indicator_analysis"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            table_fontsize=12,
            row_height_scale=2.3,
        )
        insert_figure(c, fig8, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  指标分析表格生成失败: {e}")

    # 行7：动态回撤（同一行，左图右表）
    try:
        print("  生成动态回撤图表和表格...")
        h = row_heights["drawdown"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "动态回撤")
        # 左图占 70%，右表占 30%
        left_w = usable_width * 0.7
        right_w = usable_width - left_w - 5
        fig9 = plot_dynamic_drawdown_chart(
            data=safe_get("drawdown.series"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig9, x_left, y_cursor - h, left_w, h)
        # 右侧表格
        fig10 = plot_dynamic_drawdown_table(
            data=safe_get("drawdown.table"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig10, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  动态回撤生成失败: {e}")

    # 行8：大类持仓时序（整行）
    try:
        print("  生成大类持仓时序图表...")
        h = row_heights["asset_allocation"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "大类持仓时序")
        fig11 = plot_asset_allocation_chart(
            data=safe_get("asset_allocation_series"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig11, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  大类持仓时序图表生成失败: {e}")

    # 行9：期末持仓（整行）
    try:
        print("  生成期末持仓表格...")
        h = row_heights["holdings"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "期末持仓")
        # end_holdings.holdings_table 包含 summary, assets, liabilities
        fig12 = plot_end_period_holdings_table(
            data=safe_get("end_holdings.holdings_table"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
            table_fontsize=12,
        )
        insert_figure(c, fig12, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  期末持仓表格生成失败: {e}")

    # 行10：股票仓位时序（整行）
    try:
        print("  生成股票仓位时序图表...")
        h = row_heights["stock_position"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "股票仓位时序")
        fig13 = plot_stock_position_chart(
            data=safe_get("asset_allocation_series"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig13, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  股票仓位时序图表生成失败: {e}")

    # 行11：流动性资产时序（整行）
    try:
        print("  生成流动性资产时序图表...")
        h = row_heights["liquidity_asset"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "流动性资产时序")
        fig14 = plot_liquidity_asset_chart(
            data=safe_get("asset_allocation_series"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig14, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  流动性资产时序图表生成失败: {e}")

    # 持股行业分析部分
    # 行12：持股行业分析 - 饼图（左侧）和柱状图（右侧）
    try:
        print("  生成持股行业分析图表...")
        # 大标题
        h_total = row_heights["industry_pie"] + row_heights["industry_table"] + 30
        ensure_space(h_total + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "持股行业分析")

        # 饼图和柱状图并排显示
        h_charts = row_heights["industry_pie"]
        chart_width = (usable_width - 10) / 2  # 两个图表并排，留10点间距

        # 左侧：饼图
        fig15 = plot_market_value_pie_chart(
            data=safe_get("industry_attribution.end_holdings_distribution"),
            return_figure=True,
            figsize=(chart_width / 72 * 2.54, h_charts / 72 * 2.54),
            show_title=True,
        )
        insert_figure(c, fig15, x_left, y_cursor - h_charts, chart_width, h_charts)

        # 右侧：柱状图
        fig16 = plot_average_market_value_bar_chart(
            data=safe_get("industry_attribution.end_holdings_distribution"),
            return_figure=True,
            figsize=(chart_width / 72 * 2.54, h_charts / 72 * 2.54),
            show_title=True,
        )
        insert_figure(
            c,
            fig16,
            x_left + chart_width + 10,
            y_cursor - h_charts,
            chart_width,
            h_charts,
        )

        y_cursor -= h_charts + 10

        # 行13：持股行业分析 - 表格（整行）
        h_table = row_heights["industry_table"]
        ensure_space(h_table + 10)
        fig17 = plot_industry_holding_table(
            data=safe_get("industry_attribution.industry_tables"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h_table / 72 * 2.54),
            show_title=True,
            table_fontsize=12,
        )
        insert_figure(c, fig17, x_left, y_cursor - h_table, usable_width, h_table)
        y_cursor -= h_table + 10
    except Exception as e:
        import traceback

        print(f"  持股行业分析图表生成失败: {e}")
        traceback.print_exc()

    # 持股行业占比时序部分
    try:
        print("  生成持股行业占比时序图表...")
        h = row_heights["industry_timeseries"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "持股行业占比时序")
        # industry_timeseries.timeseries 才是图表期望的列表数据
        timeseries_data = safe_get("industry_timeseries.timeseries")
        if timeseries_data:
            print(f"    数据条数: {len(timeseries_data)}")
            if len(timeseries_data) > 0:
                print(f"    第一条数据keys: {list(timeseries_data[0].keys())[:5]}...")  # 只显示前5个key
        else:
            print("    警告: industry_timeseries.timeseries 数据为空")
        fig18 = plot_industry_proportion_timeseries(
            data=timeseries_data,
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=True,
        )
        insert_figure(c, fig18, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        import traceback
        print(f"  持股行业占比时序图表生成失败: {e}")
        print(f"  错误详情: {traceback.format_exc()}")

    # 持股行业偏离度时序部分
    try:
        print("  生成持股行业偏离度时序图表...")
        h = row_heights["industry_deviation"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "持股行业偏离度时序")
        # industry_timeseries.deviation_series 用于偏离度图表
        fig19 = plot_industry_deviation_timeseries(
            data=safe_get("industry_timeseries.deviation_series"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=True,
        )
        insert_figure(c, fig19, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  持股行业偏离度时序图表生成失败: {e}")

    # 大类资产绩效归因部分
    try:
        print("  生成大类资产绩效归因表格...")
        h = row_heights["asset_performance"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "大类资产绩效归因")
        fig20 = plot_asset_performance_attribution_table(
            data=safe_get("asset_class_attribution"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
            table_fontsize=12,
        )
        insert_figure(c, fig20, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  大类资产绩效归因表格生成失败: {e}")

    # Brinson归因部分
    try:
        print("  生成Brinson归因图表...")
        # 顶部：折线图（整行）
        h_line = row_heights["brinson_attribution"]
        ensure_space(h_line + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "Brinson归因")
        # brinson.series 包含时序数据
        fig21 = plot_brinson_attribution(
            data=safe_get("brinson.series"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h_line / 72 * 2.54),
            show_title=True,
        )
        insert_figure(c, fig21, x_left, y_cursor - h_line, usable_width, h_line)
        y_cursor -= h_line + 10

        # 底部：柱状图（左侧）和表格（右侧）
        h_bottom = max(
            row_heights["brinson_industry_bar"], row_heights["brinson_table"]
        )
        ensure_space(h_bottom + 10)
        # 左侧柱状图占60%，右侧表格占40%
        left_w = usable_width * 0.6
        right_w = usable_width - left_w - 5

        # 左侧：各行业累计收益率柱状图（可能需要从 brinson 提取特定数据）
        fig22 = plot_brinson_industry_bar_chart(
            data=safe_get("brinson"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h_bottom / 72 * 2.54),
            show_title=True,
        )
        insert_figure(c, fig22, x_left, y_cursor - h_bottom, left_w, h_bottom)

        # 右侧：归因分析表格，使用 brinson 的汇总数据
        fig23 = plot_brinson_attribution_table(
            data=safe_get("brinson"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54 * 0.7, h_bottom / 72 * 2.54 * 0.7),
            show_title=True,
            table_fontsize=12,
        )
        insert_figure(
            c, fig23, x_left + left_w + 5, y_cursor - h_bottom, right_w, h_bottom
        )
        y_cursor -= h_bottom + 10
    except Exception as e:
        print(f"  Brinson归因图表生成失败: {e}")

    # 股票行业归因部分 - 一个标题，调用四个函数
    try:
        print("  生成股票行业归因表格和图表...")
        h = max(
            row_heights["industry_attribution_table"],
            row_heights["industry_attribution_chart"],
        )
        # 计算总高度：标题 + 两行图表
        total_height = h * 2 + 10  # 两行图表 + 中间间距
        ensure_space(total_height + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "股票行业归因")

        # 左侧表格占50%，右侧图表占50%
        left_w = usable_width * 0.5
        right_w = usable_width - left_w - 5

        # 第一行：收益额排名前十（表格在左，图表在右）
        # 左侧：收益额表格
        fig24_table = plot_industry_attribution_profit_table(
            data=safe_get("industry_attribution.industry_profit"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h / 72 * 2.54),
            show_title=True,
            table_fontsize=12,
        )
        insert_figure(c, fig24_table, x_left, y_cursor - h, left_w, h)

        # 右侧：收益额图表（不显示标题）
        fig24_chart = plot_industry_attribution_profit_chart(
            data=safe_get("industry_attribution.industry_profit"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig24_chart, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 10

        # 第二行：亏损额排名前十（表格在左，图表在右）
        ensure_space(h + 10)
        # 左侧：亏损额表格
        fig25_table = plot_industry_attribution_loss_table(
            data=safe_get("industry_attribution.industry_profit"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h / 72 * 2.54),
            show_title=True,
            table_fontsize=12,
        )
        insert_figure(c, fig25_table, x_left, y_cursor - h, left_w, h)

        # 右侧：亏损额图表（不显示标题）
        fig25_chart = plot_industry_attribution_loss_chart(
            data=safe_get("industry_attribution.industry_profit"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig25_chart, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  股票行业归因图表生成失败: {e}")

    # 股票绩效归因部分 - 一个标题，调用四个函数
    try:
        print("  生成股票绩效归因表格和图表...")
        h = max(
            row_heights["stock_attribution_table"],
            row_heights["stock_attribution_chart"],
        )
        # 计算总高度：标题 + 两行图表
        total_height = h * 2 + 10  # 两行图表 + 中间间距
        ensure_space(total_height + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "股票绩效归因")

        # 左侧表格占50%，右侧图表占50%
        left_w = usable_width * 0.5
        right_w = usable_width - left_w - 5

        # 第一行：盈利前十（表格在左，图表在右）
        # 左侧：盈利前十表格
        fig26_table = plot_stock_profit_table(
            data=safe_get("end_holdings.stock_performance"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h / 72 * 2.54),
            show_title=True,
            table_fontsize=12,
        )
        insert_figure(c, fig26_table, x_left, y_cursor - h, left_w, h)

        # 右侧：盈利前十图表（不显示标题）
        fig26_chart = plot_stock_profit_chart(
            data=safe_get("end_holdings.stock_performance"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig26_chart, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 10

        # 第二行：亏损前十（表格在左，图表在右）
        ensure_space(h + 10)
        # 左侧：亏损前十表格
        fig27_table = plot_stock_loss_table(
            data=safe_get("end_holdings.stock_performance"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h / 72 * 2.54),
            show_title=True,
            table_fontsize=12,
        )
        insert_figure(c, fig27_table, x_left, y_cursor - h, left_w, h)

        # 右侧：亏损前十图表（不显示标题）
        fig27_chart = plot_stock_loss_chart(
            data=safe_get("end_holdings.stock_performance"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig27_chart, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  股票绩效归因图表生成失败: {e}")

    # 个股持仓节点部分 - 一个标题，调用两个函数（图表在左，表格在右）
    try:
        print("  生成个股持仓节点表格和图表...")
        h = max(
            row_heights["stock_holding_nodes_table"],
            row_heights["stock_holding_nodes_chart"],
        )
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "个股持仓节点")

        # 左侧图表占50%，右侧表格占50%
        left_w = usable_width * 0.5
        right_w = usable_width - left_w - 5

        # 左侧：图表（不显示标题），使用 end_holdings.position_nodes
        fig28_chart = plot_stock_holding_nodes_chart(
            data=safe_get("end_holdings.position_nodes"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig28_chart, x_left, y_cursor - h, left_w, h)

        # 右侧：表格（不显示标题，因为主标题已经在页面顶部）
        fig28_table = plot_stock_holding_nodes_table(
            data=safe_get("end_holdings.position_nodes"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
            table_fontsize=12,
        )
        insert_figure(c, fig28_table, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  个股持仓节点图表生成失败: {e}")

    # 换手率 (年化) 部分
    try:
        print("  生成换手率 (年化) 表格...")
        h = row_heights["turnover_rate_table"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "换手率 (年化)")

        # 绘制表格
        fig29 = plot_turnover_rate_table(
            data=safe_get("turnover"),
            return_figure=True,
            figsize=(usable_width / 72 * 2.54, h / 72 * 2.54),
            show_title=True,
            table_fontsize=12,
        )
        insert_figure(c, fig29, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  换手率 (年化) 表格生成失败: {e}")

    # 期间交易部分 - 一个标题，调用两个函数（表格在左，图表在右）
    try:
        print("  生成期间交易表格和图表...")
        h = max(
            row_heights["period_transaction_table"],
            row_heights["period_transaction_chart"],
        )
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "期间交易")

        # 左侧表格占50%，右侧图表占50%
        left_w = usable_width * 0.5
        right_w = usable_width - left_w - 5

        # 左侧：表格（显示标题）
        fig30_table = plot_period_transaction_table(
            data=safe_get("period_transaction"),
            return_figure=True,
            figsize=(left_w / 72 * 2.54, h / 72 * 2.54),
            show_title=True,
            table_fontsize=12,
        )
        insert_figure(c, fig30_table, x_left, y_cursor - h, left_w, h)

        # 右侧：图表（不显示标题）
        fig30_chart = plot_period_transaction_chart(
            data=safe_get("period_transaction"),
            return_figure=True,
            figsize=(right_w / 72 * 2.54, h / 72 * 2.54),
            show_title=False,
        )
        insert_figure(c, fig30_chart, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 10
    except Exception as e:
        print(f"  期间交易图表生成失败: {e}")
    
    # 添加页脚
    footer_y = bottom_margin
    c.setFont("Helvetica", 8)
    c.drawString(margin, footer_y, "请务必阅读正文后的免责声明")
    
    # 保存 PDF
    c.save()

    return final_output


if __name__ == "__main__":
    # 测试生成第一页
    print("正在生成第一页综合报告...")

    # 生成第一页（使用假数据）
    output = generate_page1("第一页综合报告.pdf")
    print(f"\n第一页综合报告已保存到: {output}")
