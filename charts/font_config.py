"""
跨平台中文字体配置模块
自动检测操作系统并设置合适的中文字体
"""

import platform
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findSystemFonts, FontManager


def get_available_fonts():
    """获取系统中所有可用的字体"""
    font_manager = FontManager()
    available_fonts = set()
    for font in font_manager.ttflist:
        available_fonts.add(font.name)
    return available_fonts


def setup_chinese_font() -> None:
    """
    配置matplotlib中文字体，支持跨平台
    优先级：
    - macOS: PingFang SC > Heiti SC > STHeiti > Arial Unicode MS
    - Windows: Microsoft YaHei > SimHei > SimSun
    - Linux: WenQuanYi Micro Hei > Droid Sans Fallback > Noto Sans CJK
    """
    system = platform.system()
    available_fonts = get_available_fonts()

    # 根据操作系统设置字体优先级
    if system == "Darwin":  # macOS
        font_candidates = [
            "PingFang SC",  # macOS 默认中文字体（最佳）
            "PingFang HK",  # 香港版苹方
            "PingFang TC",  # 繁体版苹方
            "Heiti SC",  # 黑体-简（macOS）
            "Heiti TC",  # 黑体-繁
            "STHeiti",  # 华文黑体
            "Songti SC",  # 宋体-简
            "STSong",  # 华文宋体
            "Arial Unicode MS",  # 包含中文的 Arial
        ]
    elif system == "Windows":
        font_candidates = [
            "Microsoft YaHei",  # 微软雅黑（最佳）
            "SimHei",  # 黑体
            "SimSun",  # 宋体
            "KaiTi",  # 楷体
        ]
    else:  # Linux
        font_candidates = [
            "WenQuanYi Micro Hei",  # 文泉驿微米黑
            "WenQuanYi Zen Hei",  # 文泉驿正黑
            "Droid Sans Fallback",  # Android 字体
            "Noto Sans CJK SC",  # Google Noto 字体
            "Noto Sans CJK",
        ]

    # 找到第一个可用的字体
    selected_font = None
    for font in font_candidates:
        if font in available_fonts:
            selected_font = font
            print(f"  ✓ 使用字体: {font}")
            break

    if not selected_font:
        # 如果没有找到推荐字体，尝试查找任何包含 "CJK" 或中文名称的字体
        for font in available_fonts:
            if any(
                keyword in font
                for keyword in ["CJK", "Chinese", "黑体", "宋体", "微软"]
            ):
                selected_font = font
                print(f"  ⚠️  使用备用字体: {font}")
                break

    # 设置字体
    if selected_font:
        plt.rcParams["font.sans-serif"] = [selected_font, "DejaVu Sans"]
    else:
        # 最后的后备方案：使用通用字体列表
        print(f"  ⚠️  未找到合适的中文字体，使用默认配置")
        plt.rcParams["font.sans-serif"] = [
            "PingFang SC",
            "Microsoft YaHei",
            "SimHei",
            "Arial Unicode MS",
            "DejaVu Sans",
        ]

    # 其他字体配置
    plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 10
    plt.rcParams["axes.labelsize"] = 7
    plt.rcParams["xtick.labelsize"] = 6
    plt.rcParams["ytick.labelsize"] = 6
    plt.rcParams["legend.fontsize"] = 10

    # 专门为PDF优化的字体设置
    plt.rcParams["pdf.fonttype"] = 42  # 最重要：输出TrueType字体
    plt.rcParams["ps.fonttype"] = 42  # PostScript也使用TrueType


def test_chinese_font():
    """测试中文字体是否正常显示"""
    import matplotlib.pyplot as plt
    import numpy as np

    setup_chinese_font()

    fig, ax = plt.subplots(figsize=(10, 6))

    # 测试文本
    test_texts = [
        "中文字体测试 Chinese Font Test",
        "数字：0123456789",
        "符号：+-×÷=≠≈∑∫",
        "产品净值表现",
        "收益率分析",
        "持仓明细",
    ]

    y_positions = np.linspace(0.8, 0.2, len(test_texts))

    for text, y in zip(test_texts, y_positions):
        ax.text(
            0.5,
            y,
            text,
            fontsize=14,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("中文字体显示测试", fontsize=18, fontweight="bold")

    plt.tight_layout()
    test_path = "font_test.png"
    plt.savefig(test_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"\n字体测试图片已保存: {test_path}")
    print("请打开图片检查中文是否正常显示")

    return test_path


if __name__ == "__main__":
    print("=" * 60)
    print("检测系统字体...")
    print("=" * 60)

    system = platform.system()
    print(f"操作系统: {system}")

    print("\n可用的中文相关字体:")
    available = get_available_fonts()
    chinese_fonts = [
        f
        for f in sorted(available)
        if any(
            keyword in f
            for keyword in [
                "CJK",
                "Chinese",
                "PingFang",
                "Heiti",
                "Songti",
                "SimHei",
                "SimSun",
                "Microsoft",
                "YaHei",
                "KaiTi",
                "WenQuanYi",
                "Noto",
                "Droid",
                "Arial Unicode",
            ]
        )
    ]

    if chinese_fonts:
        for font in chinese_fonts:
            print(f"  • {font}")
    else:
        print("  ⚠️  未找到中文字体")

    print("\n" + "=" * 60)
    print("生成字体测试图片...")
    print("=" * 60)
    test_chinese_font()
