from pathlib import Path


# 基本路径（只使用 docs 目录存放数据文件）
ROOT_DIR = Path(__file__).resolve().parent
DOCS_DIR = ROOT_DIR / "docs"

# 数据文件（统一存放在 docs/ 下）
EXCEL_FILE = DOCS_DIR / "交割单_新.xlsx"
CSV_FILE = DOCS_DIR / "交割单_新.csv"  # 完整交割单（2015-2025）

# CSV 编码
CSV_ENCODING = "utf-8-sig"

# 初始资金（单位：元）。用于计算现金/股票占比。
# 可根据实际产品规模调整数值。
INITIAL_CAPITAL = 10_000_000.0

# 成立日期（YYYY-MM-DD）。用于"成立以来"基准收益等统计。
# 若不确定可保留为 None，程序将回退为使用CSV首日。
ESTABLISH_DATE = None

# 报告年份（YYYY）。用于限定报告统计区间。
# 例如设置为 "2015" 则只统计2015年的数据（2015-01-01 至 2015-12-31）
# 设置为 "2024" 则只统计2024年的数据（2024-01-01 至 2024-12-31）
# 设置为 None 则统计所有交易日期
REPORT_YEAR = (
    "2016"  # 可选: "2015", "2016", ..., "2025", None (全部日期会非常密集，可能显示失败)
)

# 持仓计算方法（CRITICAL: 影响净值、回撤、归因等所有指标的准确性）
# - "cost": 成本法 - 使用买入成本计算持仓市值（历史方法，不准确）
# - "market": 市值法 - 使用每日收盘价计算持仓市值（推荐，准确反映市场价值）
# 
# ⚠️ 重要说明:
#   成本法：股票市值 = 持仓股数 × 买入成本
#     优点：无需获取价格数据，计算快速
#     缺点：无法反映市场波动，回撤/归因/风险指标完全错误
#   
#   市值法：股票市值 = 持仓股数 × 当日收盘价
#     优点：准确反映资产真实价值，所有指标计算正确
#     缺点：需要获取历史行情数据（通过Tushare API）
#
# 推荐设置：VALUATION_METHOD = "market"
VALUATION_METHOD = "market"  # 可选: "cost" 或 "market"
