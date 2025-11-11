from pathlib import Path


# 基本路径（只使用 docs 目录存放数据文件）
ROOT_DIR = Path(__file__).resolve().parent
DOCS_DIR = ROOT_DIR / "docs"

# 数据文件（统一存放在 docs/ 下）
EXCEL_FILE = DOCS_DIR / "交割单.xlsx"
# CSV_FILE = DOCS_DIR / "交割单.csv"
CSV_FILE = DOCS_DIR / "交割单_2024-11-04-2025-11-04.csv"

# CSV 编码
CSV_ENCODING = "utf-8-sig"

# 初始资金（单位：元）。用于计算现金/股票占比。
# 可根据实际产品规模调整数值。
INITIAL_CAPITAL = 3_000_000_000.0  # 30亿元（基于交易数据分析得出的最小充足资金）

# 成立日期（YYYY-MM-DD）。用于"成立以来"基准收益等统计。
# 若不确定可保留为 None，程序将回退为使用CSV首日。
ESTABLISH_DATE = None
