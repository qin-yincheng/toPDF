import os
import logging
from typing import Optional
from pathlib import Path

import pandas as pd

from config import DOCS_DIR


logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def convert_excel_to_csv(
    excel_path: str,
    csv_path: str,
    sheet: Optional[object] = 0,
    encoding: str = "utf-8-sig",
) -> None:
    """将 Excel 文件转换为 CSV"""
    logger.info(f"读取 Excel: {excel_path}")
    
    if sheet == "all":
        dfs = []
        xls = pd.ExcelFile(excel_path, engine="openpyxl")
        for sname in xls.sheet_names:
            df_tmp = pd.read_excel(xls, sheet_name=sname)
            dfs.append(df_tmp)
        df = pd.concat(dfs, ignore_index=True)
    else:
        df = pd.read_excel(excel_path, sheet_name=sheet, engine="openpyxl")

    # 修复股票代码前导0
    def _fix_code_series(s: pd.Series) -> pd.Series:
        def fmt(v):
            if pd.isna(v):
                return v
            if isinstance(v, (int, float)):
                try:
                    return str(int(v)).zfill(6)
                except Exception:
                    pass
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

    for col in df.columns:
        if 'code' in col.lower() or col in ('code', '股票代码'):
            df[col] = _fix_code_series(df[col])

    # 格式化数量和金额列
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
    """确保 CSV 存在且不落后于 Excel"""
    excel_p = Path(excel_path)
    csv_p = Path(csv_path)

    if not excel_p.exists():
        raise FileNotFoundError(f"Excel文件不存在: {excel_path}")

    need_convert = False
    if force:
        need_convert = True
    elif not csv_p.exists():
        need_convert = True
    else:
        excel_mtime = excel_p.stat().st_mtime
        csv_mtime = csv_p.stat().st_mtime
        if excel_mtime > csv_mtime:
            need_convert = True

    if need_convert:
        convert_excel_to_csv(excel_path, csv_path, sheet=sheet)
        return True
    return False
