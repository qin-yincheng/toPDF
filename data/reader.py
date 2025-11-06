import os
import logging
from typing import Optional

import pandas as pd


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def convert_excel_to_csv(
    excel_path: str,
    csv_path: str,
    sheet: Optional[object] = 0,
    encoding: str = "utf-8-sig",
) -> None:
    """
    将 Excel 文件转换为 CSV（默认首个工作表，或合并所有工作表）。

    只做纯转换，不做任何清洗、重命名或校验。
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel 文件不存在: {excel_path}")

    logger.info(f"读取 Excel: {excel_path}")

    if sheet is None:
        dfs = pd.read_excel(excel_path, sheet_name=None, engine="openpyxl")
        df = pd.concat(dfs.values(), ignore_index=True)
    else:
        df = pd.read_excel(excel_path, sheet_name=sheet, engine="openpyxl")

    # 尝试仅对“股票代码”列做零填充，避免丢失前导0。
    def _fix_code_series(s: pd.Series) -> pd.Series:
        def fmt(v):
            if pd.isna(v):
                return v
            # 数值类型：直接转int再zfill(6)
            if isinstance(v, (int, float)):
                try:
                    n = int(v)
                    return str(n).zfill(6)
                except Exception:
                    pass
            # 字符串：去除空格、小数尾、提取数字后zfill(6)
            sv = str(v).strip()
            if sv.endswith('.0'):
                sv = sv[:-2]
            digits = ''.join(ch for ch in sv if ch.isdigit())
            if len(digits) == 0:
                return sv
            if len(digits) <= 6:
                return digits.zfill(6)
            return digits
        return s.apply(fmt)

    for cand in ("code", "股票代码", "证券代码", "证券代码/基金代码"):
        if cand in df.columns:
            df[cand] = _fix_code_series(df[cand])
            break

    # 统一显示：数量为整数、金额保留两位小数（如存在这些列）
    def _to_int_str(s: pd.Series) -> pd.Series:
        def fmt(v):
            if pd.isna(v) or v == "":
                return ""
            try:
                return str(int(round(float(v))))
            except Exception:
                return str(v)
        return s.apply(fmt)

    def _to_money_str(s: pd.Series) -> pd.Series:
        def fmt(v):
            if pd.isna(v) or v == "":
                return ""
            try:
                return f"{float(v):.2f}"
            except Exception:
                return str(v)
        return s.apply(fmt)

    for col in ("buy_number", "sell_number"):
        if col in df.columns:
            df[col] = _to_int_str(df[col])

    for col in ("buy_money", "sell_money"):
        if col in df.columns:
            df[col] = _to_money_str(df[col])

    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    df.to_csv(csv_path, index=False, encoding=encoding)
    logger.info(f"已导出 CSV: {csv_path} (rows={len(df)})")


def ensure_csv_from_excel(
    excel_path: str,
    csv_path: str,
    force: bool = False,
    sheet: Optional[object] = 0,
) -> bool:
    """
    确保 CSV 存在且不落后于 Excel；必要时进行转换。
    只负责转换，不读取或验证 CSV 内容。
    """
    if not os.path.exists(excel_path) and not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"既未找到 Excel，也未找到 CSV: excel={excel_path}, csv={csv_path}"
        )

    need_convert = force
    if os.path.exists(excel_path):
        if not os.path.exists(csv_path):
            need_convert = True
        else:
            excel_mtime = os.path.getmtime(excel_path)
            csv_mtime = os.path.getmtime(csv_path)
            need_convert = excel_mtime > csv_mtime

    if need_convert and os.path.exists(excel_path):
        convert_excel_to_csv(excel_path, csv_path, sheet=sheet)
        return True

    return False


# 保留空位：若后续需要统一读取 CSV，可在此新增轻量封装。
