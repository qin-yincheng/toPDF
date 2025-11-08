import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas_market_calendars as mcal

import pandas as pd

from config import CSV_FILE, ESTABLISH_DATE


# 交易日历单例
_calendar = None


def _read_csv_date_range(csv_path: Optional[str] = None) -> Tuple[str, str]:
    """
    从交割单CSV读取首尾日期（根据 start/FROM_UNIXTIME(buy_time) 与 end/FROM_UNIXTIME(sell_time) 列）。
    返回 (min_date, max_date)，格式 YYYY-MM-DD。
    """
    path = str(csv_path or CSV_FILE)
    last_err = None
    for enc in ("utf-8-sig", "utf-8", "gbk", "gb2312"):
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except UnicodeDecodeError as e:
            last_err = e
            continue
    else:
        if last_err:
            raise last_err
        raise RuntimeError("无法读取交割单CSV")

    def parse_col(cols: List[str]) -> pd.Series:
        for c in cols:
            if c in df.columns:
                s = pd.to_datetime(df[c], errors="coerce")
                if s.notna().any():
                    return s
        # fallback: empty series
        return pd.to_datetime(pd.Series([], dtype="datetime64[ns]"))

    buys = parse_col(["FROM_UNIXTIME(buy_time)", "buy_time", "start"])  # 开始时间
    sells = parse_col(["FROM_UNIXTIME(sell_time)", "sell_time", "end"])  # 结束时间
    both = pd.concat([buys.dropna(), sells.dropna()], ignore_index=True)
    if both.empty:
        raise ValueError("交割单中未找到有效的时间列")
    min_date = both.min().strftime("%Y-%m-%d")
    max_date = both.max().strftime("%Y-%m-%d")
    return min_date, max_date


def _fetch_index_daily(index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取指数在[start_date, end_date]区间的日线数据（收盘价）。
    返回 DataFrame，包含列：date(YYYY-MM-DD), close，日期升序。
    """
    try:
        import tushare as ts
    except Exception as e:
        raise RuntimeError("需要安装 tushare 依赖，请先 pip install tushare") from e

    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        raise RuntimeError("未发现环境变量 TUSHARE_TOKEN，请设置后重试")

    ts.set_token(token)
    pro = ts.pro_api()

    s = start_date.replace("-", "")
    e = end_date.replace("-", "")
    df = pro.index_daily(ts_code=index_code, start_date=s, end_date=e)
    if df is None or df.empty:
        raise ValueError(f"区间内无指数数据: {index_code} {start_date}~{end_date}")

    df = df[["trade_date", "close"]].copy()
    df["date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
    df = df.sort_values("date")
    return df[["date", "close"]]


def _get_close_on_or_before(price_df: pd.DataFrame, target: str) -> Optional[float]:
    ser = price_df.set_index("date")["close"]
    if target in ser.index:
        return float(ser.loc[target])
    # 找到 <= target 的最近一个交易日
    dates = ser.index[ser.index <= target]
    if len(dates) == 0:
        return None
    return float(ser.loc[dates.max()])


def _get_close_on_or_after(price_df: pd.DataFrame, target: str) -> Optional[float]:
    ser = price_df.set_index("date")["close"]
    if target in ser.index:
        return float(ser.loc[target])
    dates = ser.index[ser.index >= target]
    if len(dates) == 0:
        return None
    return float(ser.loc[dates.min()])


def _pct(start_close: Optional[float], end_close: Optional[float]) -> Optional[float]:
    if start_close is None or end_close is None or start_close == 0:
        return None
    return round((end_close / start_close - 1.0) * 100.0, 2)


def calculate_index_return(
    csv_path: Optional[str] = None,
    index_code: str = "000300.SH",
    establish_date: Optional[str] = None,
) -> List[Dict[str, float]]:
    """
    读取交割单首尾时间，按“年”为单位计算每年的基准收益字典，并返回列表：
    benchmarks = [benchmark_data_第一年, benchmark_data_第二年, ..., benchmark_data_最后一年]

    每个 benchmark_data 形如：
    {
      "统计期间": x,  # 当年(或首/尾年截断后)起始→该年末 的收益率
      "近一个月": x,  # 以该年末为基准
      "近三个月": x,
      "近六个月": x,
      "近一年": x,
      "今年以来": x,  # 与“统计期间”通常一致（当年年初→该年末）
      "成立以来": x,  # 成立日(或CSV首日)→该年末
    }
    """
    start_csv, end_csv = _read_csv_date_range(csv_path)
    # 取指数数据范围：从 min(establish, start_csv, end_csv-370天) 到 end_csv
    end_dt = datetime.strptime(end_csv, "%Y-%m-%d")
    start_dt = datetime.strptime(start_csv, "%Y-%m-%d")
    min_fetch_dt = start_dt
    # 允许通过参数覆盖；未提供时回退到 config.ESTABLISH_DATE
    eff_establish = establish_date if establish_date else ESTABLISH_DATE
    if eff_establish:
        try:
            est_dt = datetime.strptime(eff_establish, "%Y-%m-%d")
            if est_dt < min_fetch_dt:
                min_fetch_dt = est_dt
        except Exception:
            pass
    # 为了计算“近一年”等窗口，向前取足够缓冲天数
    min_fetch_dt = min_fetch_dt - timedelta(days=370)

    price_df = _fetch_index_daily(index_code=index_code,
                                  start_date=min_fetch_dt.strftime("%Y-%m-%d"),
                                  end_date=end_csv)

    # 计算各时间窗
    def add_days(d: datetime, days: int) -> str:
        return (d + timedelta(days=days)).strftime("%Y-%m-%d")

    # 构造年度列表
    benchmarks: List[Dict[str, float]] = []
    start_year = start_dt.year
    end_year = end_dt.year

    for y in range(start_year, end_year + 1):
        year_start = f"{y}-01-01"
        year_end = f"{y}-12-31"
        # 限制在CSV区间内
        if y == start_year and year_start < start_csv:
            year_start = start_csv
        if y == end_year and year_end > end_csv:
            year_end = end_csv

        y_end_dt = datetime.strptime(year_end, "%Y-%m-%d")
        y_end_close = _get_close_on_or_before(price_df, year_end)
        if y_end_close is None:
            # 该年无有效交易数据，跳过
            continue

        # 统计期间（当年起点→当年末）
        y_start_close = _get_close_on_or_after(price_df, year_start)
        stat_ret = _pct(y_start_close, y_end_close)

        # 回溯窗口（以当年末为锚点）
        m1_start = (y_end_dt - timedelta(days=30)).strftime("%Y-%m-%d")
        m3_start = (y_end_dt - timedelta(days=90)).strftime("%Y-%m-%d")
        m6_start = (y_end_dt - timedelta(days=180)).strftime("%Y-%m-%d")
        y1_start = (y_end_dt - timedelta(days=365)).strftime("%Y-%m-%d")

        m1_ret = _pct(_get_close_on_or_before(price_df, m1_start), y_end_close)
        m3_ret = _pct(_get_close_on_or_before(price_df, m3_start), y_end_close)
        m6_ret = _pct(_get_close_on_or_before(price_df, m6_start), y_end_close)
        y1_ret = _pct(_get_close_on_or_before(price_df, y1_start), y_end_close)

        # 今年以来（当年年初→当年末）
        ytd_ret = stat_ret

        # 成立以来（成立日/CSV首日 → 当年末）
        since_start = (establish_date or ESTABLISH_DATE or start_csv)
        since_ret = _pct(_get_close_on_or_before(price_df, since_start), y_end_close)

        bench: Dict[str, float] = {}
        if stat_ret is not None:
            bench["统计期间"] = stat_ret
        if m1_ret is not None:
            bench["近一个月"] = m1_ret
        if m3_ret is not None:
            bench["近三个月"] = m3_ret
        if m6_ret is not None:
            bench["近六个月"] = m6_ret
        if y1_ret is not None:
            bench["近一年"] = y1_ret
        if ytd_ret is not None:
            bench["今年以来"] = ytd_ret
        if since_ret is not None:
            bench["成立以来"] = since_ret

        benchmarks.append(bench)

    return benchmarks


def compute_index_yearly_unit_nav(
    csv_path: Optional[str] = None,
    index_code: str = "000300.SH",
) -> Dict[int, pd.DataFrame]:
    """
    计算指数按“年”的单位净值序列：
    - 每一年期初单位净值=1（以该年首个可用交易日作为基准日）；
    - 该年每个交易日的单位净值=当日收盘/基准日收盘；
    - 累积收益率= (单位净值-1)×100%，首日为0%。

    范围：使用交割单CSV的首尾日期确定年份范围，并裁剪每年的区间至 [CSV首日, CSV末日]。

    返回：{year: pd.DataFrame}，每个DataFrame包含列：
      - date (YYYY-MM-DD)
      - close (float)
      - nav (float)
      - cum_return_pct (float)
    """
    start_csv, end_csv = _read_csv_date_range(csv_path)
    start_year = int(start_csv[:4])
    end_year = int(end_csv[:4])

    # 为确保年初/年末边界可取到价格，按完整自然年抓取
    fetch_start = f"{start_year}-01-01"
    fetch_end = f"{end_year}-12-31"
    price_df = _fetch_index_daily(index_code=index_code, start_date=fetch_start, end_date=fetch_end)

    result: Dict[int, pd.DataFrame] = {}
    ser = price_df.set_index("date")["close"]

    for y in range(start_year, end_year + 1):
        y_start = f"{y}-01-01"
        y_end = f"{y}-12-31"
        # 裁剪至CSV范围
        if y == start_year and y_start < start_csv:
            y_start = start_csv
        if y == end_year and y_end > end_csv:
            y_end = end_csv

        # 取该年在price_df中的子集
        mask = (price_df["date"] >= y_start) & (price_df["date"] <= y_end)
        sub = price_df.loc[mask].copy()
        if sub.empty:
            continue

        base_close = float(sub.iloc[0]["close"])  # 基准日收盘
        sub["nav"] = sub["close"] / base_close
        sub["cum_return_pct"] = (sub["nav"] - 1.0) * 100.0
        # 仅保留需要的列
        out = sub[["date", "close", "nav", "cum_return_pct"]].reset_index(drop=True)
        result[y] = out

    return result


def _get_calendar():
    """获取交易日历（单例模式）"""
    global _calendar
    if _calendar is None:
        _calendar = mcal.get_calendar("SSE")  # SSE: 上海证券交易所
    return _calendar


def generate_date_range(start_date: str, end_date: str) -> List[str]:
    """
    生成日期范围列表（包含所有日期，包括周末）

    参数:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）

    返回:
        List[str]: 日期列表，格式 'YYYY-MM-DD'
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return date_list


def is_trading_day(date: str) -> bool:
    """
    判断是否为交易日（使用交易日历库，包含节假日）

    参数:
        date: 日期（YYYY-MM-DD）

    返回:
        bool: 是否为交易日
    """
    dt = datetime.strptime(date, "%Y-%m-%d")
    calendar = _get_calendar()

    # 获取该日期的交易日历
    schedule = calendar.schedule(start_date=dt, end_date=dt)

    # 如果schedule不为空，说明是交易日
    return not schedule.empty


def get_nearest_trading_day(date: str, direction: str = "backward") -> str:
    """
    获取最近的交易日（使用交易日历库，自动处理节假日）

    参数:
        date: 日期（YYYY-MM-DD）
        direction: 'backward'（向前找）或 'forward'（向后找）

    返回:
        str: 最近的交易日（YYYY-MM-DD）
    """
    dt = datetime.strptime(date, "%Y-%m-%d")

    # 如果已经是交易日，直接返回
    if is_trading_day(date):
        return date

    calendar = _get_calendar()

    if direction == "backward":
        # 向前找：获取该日期之前的交易日
        end_date = dt - timedelta(days=1)
        schedule = calendar.schedule(
            start_date=end_date - timedelta(days=30), end_date=end_date
        )
        if not schedule.empty:
            return schedule.index[-1].strftime("%Y-%m-%d")
    else:
        # 向后找：获取该日期之后的交易日
        start_date = dt + timedelta(days=1)
        schedule = calendar.schedule(
            start_date=start_date, end_date=start_date + timedelta(days=30)
        )
        if not schedule.empty:
            return schedule.index[0].strftime("%Y-%m-%d")

    # 如果库方法失败，回退到循环方式
    if direction == "backward":
        while not is_trading_day(dt.strftime("%Y-%m-%d")):
            dt -= timedelta(days=1)
    else:
        while not is_trading_day(dt.strftime("%Y-%m-%d")):
            dt += timedelta(days=1)

    return dt.strftime("%Y-%m-%d")


def generate_trading_date_range(start_date: str, end_date: str) -> List[str]:
    """
    生成交易日范围列表（只包含交易日，使用交易日历库）

    参数:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）

    返回:
        List[str]: 交易日列表，格式 'YYYY-MM-DD'
    """
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # 如果开始日期大于结束日期，返回空列表
    if start_dt > end_dt:
        return []

    calendar = _get_calendar()
    schedule = calendar.schedule(start_date=start_dt, end_date=end_dt)

    # 转换为日期字符串列表
    trading_dates = [date.strftime("%Y-%m-%d") for date in schedule.index]

    return trading_dates
