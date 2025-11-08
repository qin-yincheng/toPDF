from data.reader import convert_excel_to_csv
from config import EXCEL_FILE, CSV_FILE, DOCS_DIR


def main() -> None:
    # 始终在 docs 目录工作；不存在则创建
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # 每次执行都强制从 Excel 转换并覆盖 CSV
    if not EXCEL_FILE.exists():
        print(f"缺少Excel源文件：{EXCEL_FILE}。请将交割单放在 docs/ 目录后重试。")
        return

    try:
        convert_excel_to_csv(str(EXCEL_FILE), str(CSV_FILE))
        print(f"已覆盖生成 CSV：{CSV_FILE}")
    except Exception as e:
        print(f"转换失败：{e}")
        return

    # 轻量回显：行数统计（不解析内容、不做校验）
    try:
        with open(CSV_FILE, "rb") as f:
            rows = sum(1 for _ in f)
        if rows > 0:
            rows -= 1
        print(f"CSV行数（不含表头）：{rows}")
    except Exception as e:
        print(f"CSV检查失败：{e}")


if __name__ == "__main__":
    main()
