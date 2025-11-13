"""
第一页综合报告生成
将所有图表整合到一页 PDF 中
直接调用各个图表生成函数，获取 figure 对象后统一生成 PDF
"""

from reportlab.lib.pagesizes import A3
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Optional, Dict, Any
import os
import platform
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as backend_pdf


def setup_chinese_fonts() -> None:
    """
    配置ReportLab中文字体（用于PDF文本）
    返回注册成功的字体名称
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        # macOS 系统字体路径
        font_paths = [
            ("/System/Library/Fonts/PingFang.ttc", "PingFang SC"),
            ("/System/Library/Fonts/STHeiti Light.ttc", "STHeiti"),
            ("/System/Library/Fonts/STHeiti Medium.ttc", "STHeiti"),
            ("/Library/Fonts/Songti.ttc", "Songti SC"),
        ]

        for font_path, font_name in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"  ✓ ReportLab 注册字体: {font_name}")
                    return font_name  # 返回成功注册的字体名
                except Exception as e:
                    print(f"  ⚠️  注册字体失败 {font_name}: {e}")

    elif system == "Windows":
        # Windows 系统字体路径
        font_paths = {
            "Microsoft YaHei": "C:/Windows/Fonts/msyh.ttc",
            "SimHei": "C:/Windows/Fonts/simhei.ttf",
            "SimSun": "C:/Windows/Fonts/simsun.ttc",
        }

        for font_name, font_path in font_paths.items():
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"  ✓ ReportLab 注册字体: {font_name}")
                    return font_name  # 返回成功注册的字体名
                except Exception as e:
                    print(f"  ⚠️  注册字体失败 {font_name}: {e}")

    else:  # Linux
        font_paths = {
            "WenQuanYi Micro Hei": "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "Noto Sans CJK SC": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        }

        for font_name, font_path in font_paths.items():
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"  ✓ ReportLab 注册字体: {font_name}")
                    return font_name  # 返回成功注册的字体名
                except Exception as e:
                    print(f"  ⚠️  注册字体失败 {font_name}: {e}")

    # 如果所有字体都失败，返回None
    print(f"  ⚠️  未能注册任何中文字体")
    return None


def figure_to_image(fig, dpi: int = 200, preserve_aspect: bool = False) -> BytesIO:
    """
    将 matplotlib figure 对象转换为 PNG 图片

    参数:
        fig: matplotlib figure 对象
        dpi: 图片分辨率（默认 200）
        preserve_aspect: 是否保持宽高比（用于饼图等需要固定比例的图表）

    返回:
        BytesIO: 图片数据流
    """
    try:
        # 检查 fig 是否是有效的 figure 对象
        if fig is None:
            raise ValueError("figure 对象为 None")
        if not hasattr(fig, "savefig"):
            raise ValueError(
                f"传入的对象不是有效的 matplotlib figure，类型: {type(fig)}"
            )

        img_io = BytesIO()
        if preserve_aspect:
            # 对于需要保持宽高比的图表（如饼图），不使用tight，保持固定边界
            # 省略 bbox_inches 参数来保持固定边界（使用默认值）
            fig.savefig(img_io, format="png", dpi=dpi, facecolor="white")
        else:
            # 对于其他图表，使用tight以节省空间
            fig.savefig(
                img_io, format="png", dpi=dpi, bbox_inches="tight", facecolor="white"
            )
        img_io.seek(0)
        plt.close(fig)  # 关闭 figure 释放内存
        return img_io
    except Exception as e:
        print(f"  转换图片失败: {e}")
        if fig is not None and hasattr(fig, "close"):
            try:
                plt.close(fig)
            except:
                pass
        raise


def draw_header(
    canvas_obj: canvas.Canvas,
    page_width: float,
    page_height: float,
    top_margin: float,
    chinese_font_name: str,
    product_name: Optional[str] = None,
    report_date: Optional[str] = None,
    page_num: Optional[int] = None,
) -> None:
    """
    绘制PDF页眉

    参数:
        canvas_obj: reportlab Canvas 对象
        page_width: 页面宽度（单位：点）
        page_height: 页面高度（单位：点）
        top_margin: 顶部边距（单位：点）
        chinese_font_name: 中文字体名称
        product_name: 产品名称（可选）
        report_date: 报告日期（可选）
        page_num: 页码（可选）
    """
    header_y = page_height - top_margin + 30  # 页眉位置
    margin = 40

    try:
        canvas_obj.setFont(chinese_font_name, 9)
    except:
        canvas_obj.setFont("Helvetica", 9)

    # # 左侧：产品名称或报告标题
    # if product_name:
    #     canvas_obj.drawString(margin, header_y, product_name)
    # else:
    #     canvas_obj.drawString(margin, header_y, "私募基金报告")

    # # 右侧：日期和页码
    # right_text = ""
    # if report_date:
    #     right_text = report_date
    # if page_num is not None:
    #     if right_text:
    #         right_text = f"{right_text}  |  第 {page_num} 页"
    #     else:
    #         right_text = f"第 {page_num} 页"

    # if right_text:
    #     # 计算右对齐位置
    #     canvas_obj.drawRightString(page_width - margin, header_y, right_text)

    # 绘制页眉分隔线
    line_y = header_y
    canvas_obj.setStrokeColorRGB(0, 0, 0)  # 浅灰色
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(margin - 10, line_y, page_width - margin + 10, line_y)


def draw_footer(
    canvas_obj: canvas.Canvas,
    page_width: float,
    bottom_margin: float,
    chinese_font_name: str,
    disclaimer: Optional[str] = None,
    page_num: Optional[int] = None,
    company_info: Optional[str] = None,
) -> None:
    """
    绘制PDF页脚

    参数:
        canvas_obj: reportlab Canvas 对象
        page_width: 页面宽度（单位：点）
        bottom_margin: 底部边距（单位：点）
        chinese_font_name: 中文字体名称
        disclaimer: 免责声明文本（可选）
        page_num: 页码（可选）
        company_info: 公司信息（可选）
    """
    footer_y = bottom_margin
    margin = 40

    try:
        canvas_obj.setFont(chinese_font_name, 8)
    except:
        canvas_obj.setFont("Helvetica", 8)

    # 左侧：免责声明或公司信息
    left_text = disclaimer or "请务必阅读正文后的免责声明"
    if company_info:
        left_text = f"{company_info}  |  {left_text}"
    canvas_obj.drawString(margin, footer_y, left_text)

    # # 右侧：页码
    # if page_num is not None:
    #     page_text = f"第 {page_num} 页"
    #     canvas_obj.drawRightString(page_width - margin, footer_y, page_text)

    # # 绘制页脚分隔线
    # line_y = footer_y + 12
    # canvas_obj.setStrokeColorRGB(0.7, 0.7, 0.7)  # 浅灰色
    # canvas_obj.setLineWidth(0.5)
    # canvas_obj.line(margin, line_y, page_width - margin, line_y)


def insert_figure(
    canvas_obj: canvas.Canvas,
    fig,
    x: float,
    y: float,
    width: float,
    height: float,
    dpi: int = 300,
    title: Optional[str] = None,
    preserve_aspect: bool = False,
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
        preserve_aspect: 是否保持宽高比（用于饼图等需要固定比例的图表）

    返回:
        bool: 是否成功
    """
    try:
        img_io = figure_to_image(fig, dpi=dpi, preserve_aspect=preserve_aspect)
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
    # 配置中文字体并获取字体名称
    chinese_font_name = setup_chinese_fonts()
    if not chinese_font_name:
        chinese_font_name = "Helvetica"  # 后备字体
        print("  ⚠️  使用后备字体 Helvetica（不支持中文）")

    # 导入各个图表生成函数
    import sys

    # 添加项目根目录到路径，以便图表模块可以导入 charts 包
    project_root = os.path.dirname(os.path.dirname(__file__))
    charts_dir = os.path.join(project_root, "charts")
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

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
    c = canvas.Canvas(final_output, pagesize=A3)
    page_width, page_height = A3

    # 定义布局参数（单位：点，1 inch = 72 points）
    margin = 45  # 边距
    top_margin = 80
    bottom_margin = 40

    # 提取产品信息用于页眉
    product_name = None
    report_date = None
    if data:
        # 从 performance_overview 中提取产品名称
        perf_data = safe_get("performance_overview")
        if perf_data and isinstance(perf_data, dict):
            product_name = perf_data.get("product_name")

        # 从 performance_overview 中提取最新净值日期作为报告日期
        if perf_data and isinstance(perf_data, dict):
            latest_nav_date = perf_data.get("latest_nav_date")
            if latest_nav_date:
                report_date = latest_nav_date

    # 绘制页眉
    draw_header(
        canvas_obj=c,
        page_width=page_width,
        page_height=page_height,
        top_margin=top_margin,
        chinese_font_name=chinese_font_name,
        product_name=product_name,
        report_date=report_date,
        page_num=1,
    )

    # 计算可用区域
    usable_width = page_width - 2 * margin
    usable_height = page_height - top_margin - bottom_margin

    # 绘制标题帮助函数
    def draw_section_title(y_top: float, text: str) -> float:
        """在 y_top 处绘制左对齐标题与蓝色竖条，返回内容起始 y 坐标。"""
        try:
            # 使用已注册的中文字体
            c.setFont(chinese_font_name, 16)
        except:
            # 后备字体
            c.setFont("Helvetica-Bold", 16)
        font_size = 16
        # 文本字符高度（中文字符高度约为字体大小的0.85倍）
        text_height = font_size * 0.85
        # 竖条高度与文本高度一致
        bar_height = text_height
        # 确定对齐中心位置（从 y_top 向下偏移，使标题区域居中）
        center_y = y_top - font_size * 0.5
        # 蓝色竖条：以 center_y 为中心
        bar_x = margin - 3
        bar_y = center_y - bar_height / 2
        c.setFillColorRGB(0.1529, 0.2667, 0.8157)
        c.rect(bar_x, bar_y, 1.5, bar_height, fill=1, stroke=0)
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
        "brinson_table": usable_height * 0.18,  # 与柱状图高度一致，保持视觉平衡
        "industry_attribution_profit": usable_height * 0.25,
        "industry_attribution_loss": usable_height * 0.25,
        "industry_attribution_table": usable_height * 0.25,
        "industry_attribution_chart": usable_height * 0.25,
        "stock_attribution_table": usable_height * 0.25,
        "stock_attribution_chart": usable_height * 0.25,
        "stock_holding_nodes_table": usable_height * 0.25,
        "stock_holding_nodes_chart": usable_height * 0.25,
        "turnover_rate_table": usable_height * 0.18,  # 增加高度，使表格更饱满易读
        "period_transaction_table": usable_height
        * 0.28,  # 增加高度，使表格和图表更协调
        "period_transaction_chart": usable_height
        * 0.28,  # 增加高度，使表格和图表更协调
    }

    x_left = margin
    y_cursor = page_height - top_margin  # 从顶部往下排版

    # 分页辅助函数
    page_num = 1  # 当前页码

    def new_page() -> None:
        nonlocal y_cursor, page_num
        # 为当前页添加页脚（包括第一页）
        draw_footer(
            canvas_obj=c,
            page_width=page_width,
            bottom_margin=bottom_margin,
            chinese_font_name=chinese_font_name,
            disclaimer="请务必阅读正文后的免责声明",
            page_num=page_num,
        )
        # 创建新页面
        c.showPage()
        page_num += 1
        # 为新页面添加页眉
        draw_header(
            canvas_obj=c,
            page_width=page_width,
            page_height=page_height,
            top_margin=top_margin,
            chinese_font_name=chinese_font_name,
            product_name=product_name,
            report_date=report_date,
            page_num=page_num,
        )
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
            figsize=(usable_width / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig1, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(usable_width / 72, h / 72),
            show_title=False,
            include_right_table=True,
        )
        insert_figure(c, fig2, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(usable_width / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig3, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(left_w / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig4, x_left, y_cursor - h, left_w, h)
        # 右侧表格
        fig5 = plot_daily_return_table(
            data=safe_get("nav_performance.daily_returns"),
            return_figure=True,
            figsize=(right_w / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig5, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 30  # 增加间距，确保与下一部分分离
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
            figsize=(left_w / 72, h / 72),
        )
        insert_figure(c, fig6, x_left, y_cursor - h, left_w, h)
        fig7 = plot_return_comparison_chart(
            data=safe_get("nav_performance.period_returns"),
            return_figure=True,
            figsize=(right_w / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig7, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 30
    except Exception as e:
        print(f"  收益分析生成失败: {e}")

    # 行6：指标分析（整行）
    try:
        print("  生成指标分析表格...")
        h = row_heights["indicator"] * 1.5
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "指标分析")
        fig8 = plot_indicator_analysis_table(
            data=safe_get("indicator_analysis"),
            return_figure=True,
            figsize=(usable_width / 72, h / 72),
            table_fontsize=8,
            row_height_scale=2.3,
        )
        insert_figure(c, fig8, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(left_w / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig9, x_left, y_cursor - h, left_w, h)
        # 右侧表格
        fig10 = plot_dynamic_drawdown_table(
            data=safe_get("drawdown.table"),
            return_figure=True,
            figsize=(right_w / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig10, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 30
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
            figsize=(usable_width / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig11, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(usable_width / 72, h / 72),
            show_title=False,
            table_fontsize=8,
        )
        insert_figure(c, fig12, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(usable_width / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig13, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(usable_width / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig14, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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

        # 关键修复：确保饼图是正方形，避免变形
        # 饼图必须保持1:1的宽高比才能显示为圆形
        pie_size = min(chart_width, h_charts)  # 取较小值确保是正方形

        # 左侧：饼图 - 使用正方形尺寸
        fig15 = plot_market_value_pie_chart(
            data=safe_get("industry_attribution.end_holdings_distribution"),
            return_figure=True,
            figsize=(pie_size / 72, pie_size / 72),  # 确保宽高相等
            show_title=True,
        )
        # 插入时也使用正方形尺寸，居中显示，并保持宽高比
        pie_x = x_left + (chart_width - pie_size) / 2  # 水平居中
        pie_y = y_cursor - h_charts + (h_charts - pie_size) / 2  # 垂直居中
        insert_figure(c, fig15, pie_x, pie_y, pie_size, pie_size, preserve_aspect=True)

        # 右侧：柱状图 - 可以使用完整宽度
        fig16 = plot_average_market_value_bar_chart(
            data=safe_get("industry_attribution.end_holdings_distribution"),
            return_figure=True,
            figsize=(chart_width / 72, h_charts / 72),
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

        y_cursor -= h_charts + 30
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
                print(
                    f"    第一条数据keys: {list(timeseries_data[0].keys())[:5]}..."
                )  # 只显示前5个key
        else:
            print("    警告: industry_timeseries.timeseries 数据为空")
        fig18 = plot_industry_proportion_timeseries(
            data=timeseries_data,
            return_figure=True,
            figsize=(usable_width / 72, h / 72),
            show_title=True,
        )
        insert_figure(c, fig18, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(usable_width / 72, h / 72),
            show_title=True,
        )
        insert_figure(c, fig19, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(usable_width / 72, h / 72),
            show_title=False,
            table_fontsize=8,
        )
        insert_figure(c, fig20, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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
            figsize=(usable_width / 72, h_line / 72),
            show_title=True,
        )
        insert_figure(c, fig21, x_left, y_cursor - h_line, usable_width, h_line)
        y_cursor -= h_line + 30

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
            figsize=(left_w / 72, h_bottom / 72),
            show_title=True,
        )
        insert_figure(c, fig22, x_left, y_cursor - h_bottom, left_w, h_bottom)

        # 右侧：归因分析表格，使用 brinson 的汇总数据
        # 调整表格尺寸，使其更协调（不再缩小，保持原始比例）
        fig23 = plot_brinson_attribution_table(
            data=safe_get("brinson"),
            return_figure=True,
            figsize=(right_w / 72, h_bottom / 72),
            show_title=True,
            table_fontsize=8,
        )
        insert_figure(
            c, fig23, x_left + left_w + 5, y_cursor - h_bottom, right_w, h_bottom
        )
        y_cursor -= h_bottom + 30
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

        # 左侧表格占60%，右侧图表占40%，使比例更协调
        left_w = usable_width * 0.6
        right_w = usable_width - left_w - 5

        # 第一行：收益额排名前十（表格在左，图表在右）
        # 左侧：收益额表格
        fig24_table = plot_industry_attribution_profit_table(
            data=safe_get("industry_attribution.industry_profit"),
            return_figure=True,
            figsize=(left_w / 72, h / 72),
            show_title=True,
            table_fontsize=8,
        )
        insert_figure(c, fig24_table, x_left, y_cursor - h, left_w, h)

        # 右侧：收益额图表（不显示标题）
        fig24_chart = plot_industry_attribution_profit_chart(
            data=safe_get("industry_attribution.industry_profit"),
            return_figure=True,
            figsize=(right_w / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig24_chart, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 30

        # 第二行：亏损额排名前十（表格在左，图表在右）
        ensure_space(h + 10)
        # 左侧：亏损额表格
        fig25_table = plot_industry_attribution_loss_table(
            data=safe_get("industry_attribution.industry_profit"),
            return_figure=True,
            figsize=(left_w / 72, h / 72),
            show_title=True,
            table_fontsize=8,
        )
        insert_figure(c, fig25_table, x_left, y_cursor - h, left_w, h)

        # 右侧：亏损额图表（不显示标题）
        fig25_chart = plot_industry_attribution_loss_chart(
            data=safe_get("industry_attribution.industry_profit"),
            return_figure=True,
            figsize=(right_w / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig25_chart, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 30
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

        # 左侧表格占48%，右侧图表占52%，使比例更协调平衡
        left_w = usable_width * 0.48
        right_w = usable_width - left_w - 5

        # 第一行：盈利前十（表格在左，图表在右）
        # 左侧：盈利前十表格
        fig26_table = plot_stock_profit_table(
            data=safe_get("end_holdings.stock_performance"),
            return_figure=True,
            figsize=(left_w / 72, h / 72),
            show_title=True,
            table_fontsize=8,
        )
        insert_figure(c, fig26_table, x_left, y_cursor - h, left_w, h)

        # 右侧：盈利前十图表（不显示标题）
        # 计算表格标题占用的高度，使图表与表格内容区域对齐
        # 表格标题在96%位置，表格内容从88%开始，标题占用约8%的高度
        title_height = h * 0.08
        fig26_chart = plot_stock_profit_chart(
            data=safe_get("end_holdings.stock_performance"),
            return_figure=True,
            figsize=(right_w / 72, h / 72),
            show_title=False,
        )
        # 图表向下偏移标题高度，使其与表格内容区域对齐
        insert_figure(
            c, fig26_chart, x_left + left_w + 5, y_cursor - h - title_height, right_w, h
        )
        y_cursor -= h + 30

        # 第二行：亏损前十（表格在左，图表在右）
        ensure_space(h + 10)
        # 左侧：亏损前十表格
        fig27_table = plot_stock_loss_table(
            data=safe_get("end_holdings.stock_performance"),
            return_figure=True,
            figsize=(left_w / 72, h / 72),
            show_title=True,
            table_fontsize=8,
        )
        insert_figure(c, fig27_table, x_left, y_cursor - h, left_w, h)

        # 右侧：亏损前十图表（不显示标题）
        # 计算表格标题占用的高度，使图表与表格内容区域对齐
        # 表格标题在96%位置，表格内容从88%开始，标题占用约8%的高度
        title_height = h * 0.08
        fig27_chart = plot_stock_loss_chart(
            data=safe_get("end_holdings.stock_performance"),
            return_figure=True,
            figsize=(right_w / 72, h / 72),
            show_title=False,
        )
        # 图表向下偏移标题高度，使其与表格内容区域对齐
        insert_figure(
            c, fig27_chart, x_left + left_w + 5, y_cursor - h - title_height, right_w, h
        )
        y_cursor -= h + 30
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
            figsize=(left_w / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig28_chart, x_left, y_cursor - h, left_w, h)

        # 右侧：表格（不显示标题，因为主标题已经在页面顶部）
        fig28_table = plot_stock_holding_nodes_table(
            data=safe_get("end_holdings.position_nodes"),
            return_figure=True,
            figsize=(right_w / 72, h / 72),
            show_title=False,
            table_fontsize=8,
        )
        insert_figure(c, fig28_table, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 30
    except Exception as e:
        print(f"  个股持仓节点图表生成失败: {e}")

    # 换手率 (年化) 部分
    try:
        print("  生成换手率 (年化) 表格...")
        h = row_heights["turnover_rate_table"]
        ensure_space(h + 22 + 10)
        y_cursor = draw_section_title(y_cursor, "换手率 (年化)")

        # 绘制表格（不显示标题，因为已有主标题）
        fig29 = plot_turnover_rate_table(
            data=safe_get("turnover"),
            return_figure=True,
            figsize=(usable_width / 72, h / 72),
            show_title=False,
            table_fontsize=8,
        )
        insert_figure(c, fig29, x_left, y_cursor - h, usable_width, h)
        y_cursor -= h + 30
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

        # 左侧表格占48%，右侧图表占52%，使图表有更多展示空间
        left_w = usable_width * 0.48
        right_w = usable_width - left_w - 5

        # 左侧：表格（不显示标题，因为已有主标题）
        fig30_table = plot_period_transaction_table(
            data=safe_get("period_transaction"),
            return_figure=True,
            figsize=(left_w / 72, h / 72),
            show_title=False,
            table_fontsize=8,
        )
        insert_figure(c, fig30_table, x_left, y_cursor - h, left_w, h)

        # 右侧：图表（不显示标题）
        fig30_chart = plot_period_transaction_chart(
            data=safe_get("period_transaction"),
            return_figure=True,
            figsize=(right_w / 72, h / 72),
            show_title=False,
        )
        insert_figure(c, fig30_chart, x_left + left_w + 5, y_cursor - h, right_w, h)
        y_cursor -= h + 30
    except Exception as e:
        print(f"  期间交易图表生成失败: {e}")

    # 添加最后一页的页脚
    draw_footer(
        canvas_obj=c,
        page_width=page_width,
        bottom_margin=bottom_margin,
        chinese_font_name=chinese_font_name,
        disclaimer="请务必阅读正文后的免责声明",
        page_num=page_num,
    )

    # 保存 PDF
    c.save()

    return final_output


if __name__ == "__main__":
    # 测试生成第一页
    print("正在生成第一页综合报告...")

    # 生成第一页（使用假数据）
    output = generate_page1("第一页综合报告.pdf")
    print(f"\n第一页综合报告已保存到: {output}")
