from pathlib import Path


# 基本路径（只使用 docs 目录存放数据文件）
ROOT_DIR = Path(__file__).resolve().parent
DOCS_DIR = ROOT_DIR / "docs"

# 数据文件（统一存放在 docs/ 下）
EXCEL_FILE = DOCS_DIR / "交割单.xlsx"
CSV_FILE = DOCS_DIR / "交割单.csv"

# CSV 编码
CSV_ENCODING = "utf-8-sig"
