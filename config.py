from pathlib import Path


# 基本路径（只使用 docs 目录存放数据文件）
ROOT_DIR = Path(__file__).resolve().parent
DOCS_DIR = ROOT_DIR / "docs"

# 数据文件（统一存放在 docs/ 下）
EXCEL_FILE = DOCS_DIR / "交割单.xlsx"
CSV_FILE = DOCS_DIR / "交割单.csv"  # 完整交割单（2015-2025）
<<<<<<< HEAD
# CSV_FILE = DOCS_DIR / "交割单.csv"  # 仅2015年数据
=======
>>>>>>> 31f1318a7673739343402c777b3c6550057e36a6

# CSV 编码
CSV_ENCODING = "utf-8-sig"

# 初始资金（单位：元）。用于计算现金/股票占比。
# 可根据实际产品规模调整数值。
INITIAL_CAPITAL = 10_000_000.0

# 成立日期（YYYY-MM-DD）。用于"成立以来"基准收益等统计。
# 若不确定可保留为 None，程序将回退为使用CSV首日。
ESTABLISH_DATE = "2015-01-05"

# 报告年份（YYYY）。用于限定报告统计区间。
# 例如设置为 "2015" 则只统计2015年的数据（2015-01-01 至 2015-12-31）
# 设置为 "2024" 则只统计2024年的数据（2024-01-01 至 2024-12-31）
# 设置为 None 则统计所有交易日期
REPORT_YEAR = "2023"  # 可选: "2015", "2016", ..., "2025", None (全部日期会非常密集，可能显示失败)
