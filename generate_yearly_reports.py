#!/usr/bin/env python3
"""
按年批量生成报告

用法:
1. 生成单个年份报告:
   python3 generate_yearly_reports.py 2024

2. 生成多个年份报告:
   python3 generate_yearly_reports.py 2015 2016 2024

3. 生成年份范围报告:
   python3 generate_yearly_reports.py 2015-2024

4. 生成所有年份报告:
   python3 generate_yearly_reports.py all
"""

import sys
import subprocess
from pathlib import Path


def generate_report_for_year(year: str) -> bool:
    """
    为指定年份生成报告
    
    Args:
        year: 年份字符串，如 "2024"
        
    Returns:
        bool: 是否生成成功
    """
    print(f"\n{'=' * 70}")
    print(f"📊 生成 {year} 年报告")
    print(f"{'=' * 70}\n")
    
    # 修改 config.py 中的 REPORT_YEAR 和 CSV_FILE
    config_file = Path(__file__).parent / "config.py"
    with open(config_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 替换 REPORT_YEAR
    import re
    content = re.sub(
        r'REPORT_YEAR\s*=\s*["\']?\w*["\']?',
        f'REPORT_YEAR = "{year}"',
        content
    )
    
    # 使用完整交割单
    content = re.sub(
        r'CSV_FILE\s*=\s*DOCS_DIR\s*/\s*"[^"]*"',
        'CSV_FILE = DOCS_DIR / "交割单.csv"',
        content
    )
    
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    # 运行生成脚本
    try:
        result = subprocess.run(
            ["python3", "generate_report.py"],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True,
            check=True
        )
        print(f"\n✅ {year} 年报告生成成功！\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {year} 年报告生成失败！\n")
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    years = []
    
    for arg in sys.argv[1:]:
        if arg.lower() == "all":
            # 生成所有年份 (2015-2025)
            years = [str(y) for y in range(2015, 2026)]
        elif "-" in arg:
            # 年份范围，如 "2015-2024"
            start, end = arg.split("-")
            years.extend([str(y) for y in range(int(start), int(end) + 1)])
        else:
            # 单个年份
            years.append(arg)
    
    if not years:
        print("❌ 请指定年份！")
        print(__doc__)
        return
    
    print(f"\n准备生成 {len(years)} 个年份的报告: {', '.join(years)}")
    
    success_count = 0
    failed_years = []
    
    for year in years:
        if generate_report_for_year(year):
            success_count += 1
        else:
            failed_years.append(year)
    
    print(f"\n{'=' * 70}")
    print(f"📊 批量生成完成")
    print(f"{'=' * 70}")
    print(f"✅ 成功: {success_count} 个")
    if failed_years:
        print(f"❌ 失败: {len(failed_years)} 个 ({', '.join(failed_years)})")
    print()
    
    # 列出生成的PDF文件
    pdf_files = sorted(Path(__file__).parent.glob("私募基金报告_*.pdf"))
    if pdf_files:
        print("生成的报告文件:")
        for pdf in pdf_files:
            size = pdf.stat().st_size / (1024 * 1024)  # MB
            print(f"  • {pdf.name} ({size:.1f} MB)")


if __name__ == "__main__":
    main()
