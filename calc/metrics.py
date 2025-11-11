from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import math
import pandas as pd

from calc.utils import generate_date_range, is_trading_day


def generate_trading_date_range(start_date: str, end_date: str) -> List[str]:
    """生成交易日期列表。"""

    return [
        date
        for date in generate_date_range(start_date, end_date)
        if is_trading_day(date)
    ]


def validate_nav_data(nav_data: List[Dict[str, Any]]) -> bool:
    """校验净值数据是否有效。"""

    if not nav_data:
        return False

    for item in nav_data:
        nav = item.get("nav")
        date = item.get("date")
        if nav is None or nav <= 0:
            return False
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except (TypeError, ValueError):
            return False

    return True


def calculate_period_profit(
    nav_data: List[Dict[str, Any]], initial_capital: float = 1000.0
) -> Dict[str, float]:
    """计算期间收益额及年化收益额。"""

    if not nav_data:
        return {"period_profit": 0.0, "annualized_profit": 0.0}

    start_assets = nav_data[0].get("total_assets", initial_capital)
    end_assets = nav_data[-1].get("total_assets", start_assets)
    period_profit = end_assets - start_assets

    try:
        start_dt = datetime.strptime(nav_data[0]["date"], "%Y-%m-%d")
        end_dt = datetime.strptime(nav_data[-1]["date"], "%Y-%m-%d")
        days = (end_dt - start_dt).days + 1
    except (KeyError, TypeError, ValueError):
        days = 0

    annualized_profit = period_profit * (365 / days) if days > 0 else 0.0

    return {
        "period_profit": round(period_profit, 2),
        "annualized_profit": round(annualized_profit, 2),
    }


def calculate_nav(
    daily_positions: List[Dict[str, Any]], initial_capital: float = 1000.0
) -> List[Dict[str, Any]]:
    """
    计算每日净值

    参数:
        daily_positions: 每日持仓列表 [{date, total_assets, ...}, ...]
        initial_capital: 初始资金（万元），默认1000.0

    返回:
        List[Dict]: 净值数据列表 [{date, nav, total_assets}, ...]

    计算公式:
        单位净值 = total_assets / initial_capital
    """
    nav_data = []

    for daily_data in daily_positions:
        total_assets = daily_data["total_assets"]
        nav = total_assets / initial_capital

        nav_data.append(
            {
                "date": daily_data["date"],
                "nav": round(nav, 4),
                "total_assets": total_assets,
            }
        )

    return nav_data


def get_nav_on_date(nav_data: List[Dict[str, Any]], target_date: str) -> float:
    """
    获取指定日期的净值

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]
        target_date: 目标日期（YYYY-MM-DD）

    返回:
        float: 净值，如果找不到返回None
    """
    for data in nav_data:
        if data["date"] == target_date:
            return data["nav"]
    return None


def calculate_returns(nav_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    计算期间收益率和年化收益率

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        Dict: {
            'period_return': float,      # 期间收益率（%）
            'annualized_return': float,  # 年化收益率（%）
            'start_date': str,
            'end_date': str,
            'days': int
        }

    计算公式:
        1. 期间收益率 = (期末净值 - 期初净值) / 期初净值 × 100%
        2. 年化收益率 = ((1 + 期间收益率/100) ^ (365 / 实际天数)) - 1 × 100%
    """
    if not nav_data or len(nav_data) < 2:
        return {
            "period_return": 0.0,
            "annualized_return": 0.0,
            "start_date": "",
            "end_date": "",
            "days": 0,
        }

    start_nav = nav_data[0]["nav"]
    end_nav = nav_data[-1]["nav"]
    start_date = nav_data[0]["date"]
    end_date = nav_data[-1]["date"]

    # 计算实际天数
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end_dt - start_dt).days + 1

    # 计算期间收益率
    period_return = ((end_nav - start_nav) / start_nav) * 100

    # 计算年化收益率
    if days > 0:
        annualized_return = ((1 + period_return / 100) ** (365 / days) - 1) * 100
    else:
        annualized_return = 0.0

    return {
        "period_return": round(period_return, 2),
        "annualized_return": round(annualized_return, 2),
        "start_date": start_date,
        "end_date": end_date,
        "days": days,
    }


def calculate_daily_returns(nav_data: List[Dict[str, Any]]) -> List[float]:
    """
    计算日收益率序列

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        List[float]: 日收益率列表（小数形式，如0.01表示1%）

    计算公式:
        日收益率 = (当日净值 - 前一日净值) / 前一日净值
    """
    return [ret for _, ret in _get_daily_returns_with_dates(nav_data)]


def _get_daily_returns_with_dates(
    nav_data: List[Dict[str, Any]],
) -> List[Tuple[str, float]]:
    """
    获取日收益率及其对应日期。

    返回:
        List[Tuple[date, return]]
    """
    daily_returns: List[Tuple[str, float]] = []

    for i in range(1, len(nav_data)):
        current = nav_data[i]
        previous = nav_data[i - 1]

        date = current.get("date")
        nav_today = current.get("nav")
        nav_yesterday = previous.get("nav")

        if date is None:
            continue

        try:
            nav_today = float(nav_today)
            nav_yesterday = float(nav_yesterday)
        except (TypeError, ValueError):
            continue

        if nav_yesterday > 0:
            daily_return = (nav_today - nav_yesterday) / nav_yesterday
        else:
            daily_return = 0.0

        daily_returns.append((date, daily_return))

    return daily_returns


def _align_return_series(
    product_series: List[Tuple[str, float]],
    benchmark_returns: List[float],
    benchmark_dates: Optional[List[str]] = None,
    date_range: Optional[Tuple[str, str]] = None,
) -> Tuple[List[float], List[float]]:
    """
    根据日期对齐产品和基准的收益序列。

    返回:
        Tuple[product_returns, benchmark_returns]
    """

    if not product_series or not benchmark_returns:
        return [], []

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    if date_range:
        start_date, end_date = date_range

    def _within_range(date_str: str) -> bool:
        if start_date and date_str < start_date:
            return False
        if end_date and date_str > end_date:
            return False
        return True

    filtered_product = [
        (date, ret) for date, ret in product_series if _within_range(date)
    ]

    if benchmark_dates and len(benchmark_dates) == len(benchmark_returns):
        bench_map: Dict[str, float] = {}
        for date, ret in zip(benchmark_dates, benchmark_returns):
            if not _within_range(date):
                continue
            try:
                ret_val = float(ret)
            except (TypeError, ValueError):
                continue
            if math.isnan(ret_val):
                continue
            bench_map[date] = ret_val

        aligned_product: List[float] = []
        aligned_benchmark: List[float] = []
        for date, ret in filtered_product:
            bench_ret = bench_map.get(date)
            if bench_ret is None:
                continue
            try:
                ret_val = float(ret)
            except (TypeError, ValueError):
                continue
            if math.isnan(ret_val):
                continue
            aligned_product.append(ret_val)
            aligned_benchmark.append(bench_ret)

        if len(aligned_product) >= 1 and len(aligned_product) == len(aligned_benchmark):
            return aligned_product, aligned_benchmark

    # 回退：按原逻辑截取最短长度
    product_values = [ret for _, ret in filtered_product]
    benchmark_values = list(benchmark_returns)

    min_len = min(len(product_values), len(benchmark_values))
    if min_len == 0:
        return [], []

    return product_values[:min_len], benchmark_values[:min_len]


def calculate_max_drawdown(nav_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    计算最大回撤

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        Dict: {
            'max_drawdown': float,      # 最大回撤（%）
            'max_dd_start_date': str,   # 最大回撤开始日期
            'max_dd_end_date': str,     # 最大回撤结束日期
            'peak_date': str,            # 峰值日期
            'peak_nav': float           # 峰值净值
        }
    """
    if not nav_data or len(nav_data) < 2:
        return {
            "max_drawdown": 0.0,
            "max_dd_start_date": "",
            "max_dd_end_date": "",
            "peak_date": "",
            "peak_nav": 0.0,
        }

    max_drawdown = 0.0
    peak_nav = nav_data[0]["nav"]
    peak_date = nav_data[0]["date"]
    max_dd_start_date = ""
    max_dd_end_date = ""
    dd_start_date = ""

    for data in nav_data:
        date = data["date"]
        nav = data["nav"]

        # 更新峰值
        if nav > peak_nav:
            peak_nav = nav
            peak_date = date
            dd_start_date = ""  # 重置回撤开始日期

        # 计算回撤
        if peak_nav > 0:
            drawdown = ((peak_nav - nav) / peak_nav) * 100

            # 记录回撤开始日期
            if drawdown > 0 and not dd_start_date:
                dd_start_date = peak_date

            # 更新最大回撤
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_dd_start_date = dd_start_date if dd_start_date else peak_date
                max_dd_end_date = date

    return {
        "max_drawdown": round(max_drawdown, 2),
        "max_dd_start_date": max_dd_start_date,
        "max_dd_end_date": max_dd_end_date,
        "peak_date": peak_date,
        "peak_nav": peak_nav,
    }


def calculate_daily_drawdowns(nav_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    计算每日回撤序列

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        List[Dict]: [{date, drawdown, peak_nav}, ...]
        回撤值（%），正值表示回撤
    """
    drawdowns = []
    peak_nav = nav_data[0]["nav"] if nav_data else 1.0

    for data in nav_data:
        date = data["date"]
        nav = data["nav"]

        # 更新峰值
        if nav > peak_nav:
            peak_nav = nav

        # 计算回撤
        if peak_nav > 0:
            drawdown = ((peak_nav - nav) / peak_nav) * 100
        else:
            drawdown = 0.0

        drawdowns.append(
            {
                "date": date,
                "drawdown": round(drawdown, 2),
                "peak_nav": peak_nav,
            }
        )

    return drawdowns


def calculate_volatility(nav_data: List[Dict[str, Any]]) -> float:
    """
    计算年化波动率

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        float: 年化波动率（%）
    """
    daily_returns = calculate_daily_returns(nav_data)

    if len(daily_returns) < 2:
        return 0.0

    # 计算标准差
    std_returns = np.std(daily_returns)

    # 年化波动率
    annualized_volatility = std_returns * np.sqrt(252) * 100

    return round(annualized_volatility, 2)


def calculate_sharpe_ratio(
    annualized_return: float, volatility: float, risk_free_rate: float = 0.03
) -> float:
    """
    计算夏普比率

    参数:
        annualized_return: 年化收益率（%）
        volatility: 年化波动率（%）
        risk_free_rate: 无风险收益率（小数形式，默认0.03即3%）

    返回:
        float: 夏普比率
    """
    if volatility == 0:
        return 0.0

    # 转换为小数形式
    annualized_return_decimal = annualized_return / 100
    volatility_decimal = volatility / 100

    sharpe_ratio = (annualized_return_decimal - risk_free_rate) / volatility_decimal

    return round(sharpe_ratio, 2)


def calculate_calmar_ratio(annualized_return: float, max_drawdown: float) -> float:
    """
    计算卡玛比率

    参数:
        annualized_return: 年化收益率（%）
        max_drawdown: 最大回撤（%）

    返回:
        float: 卡玛比率
    """
    if max_drawdown == 0:
        return 0.0

    # 转换为小数形式
    annualized_return_decimal = annualized_return / 100
    max_drawdown_abs = abs(max_drawdown) / 100

    calmar_ratio = annualized_return_decimal / max_drawdown_abs

    return round(calmar_ratio, 2)


def calculate_daily_return_stats(nav_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    计算日收益率统计

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        Dict: {
            'max_daily_return': float,      # 单日最大收益（%）
            'max_daily_loss': float,        # 单日最大亏损（%）
            'max_return_date': str,         # 最大收益日期
            'max_loss_date': str           # 最大亏损日期
        }
    """
    daily_returns = calculate_daily_returns(nav_data)

    if not daily_returns:
        return {
            "max_daily_return": 0.0,
            "max_daily_loss": 0.0,
            "max_return_date": "",
            "max_loss_date": "",
        }

    # 转换为百分比
    daily_returns_pct = [r * 100 for r in daily_returns]

    max_return = max(daily_returns_pct)
    max_loss = min(daily_returns_pct)

    # 找到对应日期（注意索引+1，因为第一个交易日没有日收益率）
    max_return_idx = daily_returns_pct.index(max_return)
    max_loss_idx = daily_returns_pct.index(max_loss)

    max_return_date = nav_data[max_return_idx + 1]["date"]
    max_loss_date = nav_data[max_loss_idx + 1]["date"]

    return {
        "max_daily_return": round(max_return, 2),
        "max_daily_loss": round(max_loss, 2),
        "max_return_date": max_return_date,
        "max_loss_date": max_loss_date,
    }


def calculate_cumulative_returns(
    nav_data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    计算累计收益率序列

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        List[Dict]: [{date, nav, cumulative_return}, ...]
        累计收益率（%）
    """
    cumulative_data = []

    for data in nav_data:
        nav = data["nav"]
        cumulative_return = (nav - 1.0) * 100

        cumulative_data.append(
            {
                "date": data["date"],
                "nav": nav,
                "cumulative_return": round(cumulative_return, 2),
            }
        )

    return cumulative_data


def calculate_weekly_win_rate(nav_data: List[Dict[str, Any]]) -> float:
    """
    计算周胜率

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        float: 周胜率（%）
    """
    if len(nav_data) < 2:
        return 0.0

    # 按周聚合
    weekly_data = {}
    for data in nav_data:
        date = datetime.strptime(data["date"], "%Y-%m-%d")
        week_start = date - timedelta(days=date.weekday())
        week_key = week_start.strftime("%Y-%m-%d")
        if week_key not in weekly_data:
            weekly_data[week_key] = []
        weekly_data[week_key].append(data)

    # 按周键排序
    sorted_weeks = sorted(weekly_data.keys())
    winning_weeks = 0
    total_weeks = 0

    for week_key in sorted_weeks:
        week_data = sorted(weekly_data[week_key], key=lambda x: x["date"])
        week_start_nav = week_data[0]["nav"]  # 该周最早交易日的净值
        week_end_nav = week_data[-1]["nav"]  # 该周最后交易日的净值

        # 计算周内收益率：本周最后NAV - 本周最早NAV
        if week_start_nav > 0:
            week_return = (week_end_nav - week_start_nav) / week_start_nav
            if week_return > 0:
                winning_weeks += 1
            total_weeks += 1

    win_rate = (winning_weeks / total_weeks * 100) if total_weeks > 0 else 0.0
    return round(win_rate, 2)


def calculate_monthly_win_rate(nav_data: List[Dict[str, Any]]) -> float:
    """
    计算月胜率

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        float: 月胜率（%）
    """
    if len(nav_data) < 2:
        return 0.0

    # 按月聚合
    monthly_data = {}
    for data in nav_data:
        date = datetime.strptime(data["date"], "%Y-%m-%d")
        month_key = date.strftime("%Y-%m")

        if month_key not in monthly_data:
            monthly_data[month_key] = []
        monthly_data[month_key].append(data)

    # 计算每月收益率
    winning_months = 0
    total_months = 0

    for month_key, month_data in monthly_data.items():
        if len(month_data) < 2:
            continue

        month_data_sorted = sorted(month_data, key=lambda x: x["date"])
        start_nav = month_data_sorted[0]["nav"]
        end_nav = month_data_sorted[-1]["nav"]

        if start_nav > 0:
            month_return = (end_nav - start_nav) / start_nav
            if month_return > 0:
                winning_months += 1
            total_months += 1

    win_rate = (winning_months / total_months * 100) if total_months > 0 else 0.0

    return round(win_rate, 2)


def calculate_monthly_returns(nav_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    计算月度收益率和月度累计收益率

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]

    返回:
        List[Dict]: [{month, start_nav, end_nav, monthly_return, cumulative_return}, ...]
    """
    if not nav_data:
        return []

    initial_nav = nav_data[0]["nav"]

    # 按月聚合
    monthly_data = {}
    for data in nav_data:
        date = datetime.strptime(data["date"], "%Y-%m-%d")
        month_key = date.strftime("%Y-%m")

        if month_key not in monthly_data:
            monthly_data[month_key] = []
        monthly_data[month_key].append(data)

    monthly_returns = []

    for month_key in sorted(monthly_data.keys()):
        month_data = sorted(monthly_data[month_key], key=lambda x: x["date"])

        if len(month_data) < 2:
            continue

        start_nav = month_data[0]["nav"]
        end_nav = month_data[-1]["nav"]

        # 月度收益率
        monthly_return = (
            ((end_nav - start_nav) / start_nav * 100) if start_nav > 0 else 0.0
        )

        # 月度累计收益率
        cumulative_return = (
            ((end_nav - initial_nav) / initial_nav * 100) if initial_nav > 0 else 0.0
        )

        monthly_returns.append(
            {
                "month": month_key,
                "start_nav": start_nav,
                "end_nav": end_nav,
                "monthly_return": round(monthly_return, 2),
                "cumulative_return": round(cumulative_return, 2),
            }
        )

    return monthly_returns


def _nav_list_to_dataframe(nav_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    将净值字典列表转换为按日期排序的 DataFrame。
    """
    if not nav_data:
        return pd.DataFrame()

    try:
        df = pd.DataFrame(nav_data)
    except ValueError:
        return pd.DataFrame()

    required_columns = {"date", "nav"}
    if not required_columns.issubset(df.columns):
        return pd.DataFrame()

    df = df.dropna(subset=["date", "nav"]).copy()
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").drop_duplicates(subset="date")

    try:
        df["nav"] = df["nav"].astype(float)
    except (TypeError, ValueError):
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
        df = df.dropna(subset=["nav"])

    df = df.set_index("date")
    return df


def _calculate_return_from_series(nav_series: pd.Series) -> float:
    """
    根据净值序列计算区间收益率（%）。
    """
    nav_series = nav_series.dropna()
    if nav_series.empty:
        return 0.0

    start_nav = nav_series.iloc[0]
    end_nav = nav_series.iloc[-1]

    if not np.isfinite(start_nav) or start_nav <= 0:
        return 0.0
    if not np.isfinite(end_nav):
        return 0.0

    return ((end_nav / start_nav) - 1.0) * 100.0


def calculate_beta(
    nav_data: List[Dict[str, Any]],
    benchmark_returns: List[float],
    benchmark_dates: Optional[List[str]] = None,
    date_range: Optional[Tuple[str, str]] = None,
) -> float:
    """
    注意：
      假设 benchmark_returns 与产品收益率序列的日期已对齐
      如果日期不对齐，计算结果可能不准确

    计算β值（Beta）

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]
        benchmark_returns: 基准指数每日收益率序列（小数形式）

    返回:
        float: β值

    计算公式:
        β = Cov(产品收益率, 基准收益率) / Var(基准收益率)
    """
    product_series = _get_daily_returns_with_dates(nav_data)
    if date_range:
        start_date, end_date = date_range
        product_series = [
            (date, ret)
            for date, ret in product_series
            if (start_date is None or date >= start_date)
            and (end_date is None or date <= end_date)
        ]

    product_aligned, benchmark_aligned = _align_return_series(
        product_series,
        benchmark_returns,
        benchmark_dates=benchmark_dates,
        date_range=date_range,
    )

    if len(product_aligned) < 2:
        return 1.0

    cov = np.cov(product_aligned, benchmark_aligned)[0][1]
    var = np.var(benchmark_aligned)

    # 计算β值
    if var > 0:
        beta = cov / var
    else:
        beta = 1.0  # 基准方差为0，返回中性值

    return round(beta, 4)


def calculate_active_return(
    product_period_return: float,
    benchmark_period_return: float,
    days: int,
) -> Dict[str, float]:
    """
    计算主动收益和年化主动收益

    参数:
        product_period_return: 产品期间收益率（%）
        benchmark_period_return: 基准期间收益率（%）
        days: 实际天数

    返回:
        Dict: {
            'active_return': float,          # 主动收益（%）
            'annualized_active_return': float # 年化主动收益（%）
        }

    计算公式:
        主动收益 = 产品收益率 - 基准收益率
        年化主动收益 = 产品年化收益率 - 基准年化收益率
        其中：
        产品年化收益率 = ((1 + 产品期间收益率/100) ^ (365 / 实际天数)) - 1 × 100%
        基准年化收益率 = ((1 + 基准期间收益率/100) ^ (365 / 实际天数)) - 1 × 100%
    """
    # 如果基准收益率为None，返回0
    if benchmark_period_return is None:
        return {
            "active_return": 0.0,
            "annualized_active_return": 0.0,
        }

    # 主动收益
    active_return = product_period_return - benchmark_period_return

    # 年化主动收益（分别年化后相减）
    if days > 0:
        # 分别计算产品和基准的年化收益率
        product_annualized = (
            (1 + product_period_return / 100) ** (365 / days) - 1
        ) * 100
        benchmark_annualized = (
            (1 + benchmark_period_return / 100) ** (365 / days) - 1
        ) * 100
        # 年化主动收益 = 年化产品收益 - 年化基准收益
        annualized_active_return = product_annualized - benchmark_annualized
    else:
        annualized_active_return = 0.0

    return {
        "active_return": round(active_return, 2),
        "annualized_active_return": round(annualized_active_return, 2),
    }


def calculate_tracking_error(
    nav_data: List[Dict[str, Any]],
    benchmark_returns: List[float],
    benchmark_dates: Optional[List[str]] = None,
    date_range: Optional[Tuple[str, str]] = None,
) -> float:
    """
    注意：
      假设 benchmark_returns 与产品收益率序列的日期已对齐
      如果日期不对齐，计算结果可能不准确

    计算跟踪误差（年化）

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]
        benchmark_returns: 基准指数每日收益率序列（小数形式）

    返回:
        float: 跟踪误差（年化，%）

    计算公式:
        跟踪误差 = std(产品收益率 - 基准收益率) × sqrt(252) × 100%
    """
    product_series = _get_daily_returns_with_dates(nav_data)
    if date_range:
        start_date, end_date = date_range
        product_series = [
            (date, ret)
            for date, ret in product_series
            if (start_date is None or date >= start_date)
            and (end_date is None or date <= end_date)
        ]

    product_aligned, benchmark_aligned = _align_return_series(
        product_series,
        benchmark_returns,
        benchmark_dates=benchmark_dates,
        date_range=date_range,
    )

    if len(product_aligned) < 2:
        return 0.0

    excess_returns = [p - b for p, b in zip(product_aligned, benchmark_aligned)]

    tracking_error = np.std(excess_returns) * np.sqrt(252) * 100

    return round(tracking_error, 2)


def calculate_downside_volatility(
    nav_data: List[Dict[str, Any]], target: float = 0.0
) -> float:
    """
    计算下行波动率（年化）

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]
        target: 目标收益率（小数形式，默认0.0即0%）

    返回:
        float: 下行波动率（年化，%）

    计算公式（标准公式）:
        1. 计算 min(0, R_t - target) 对每个收益率
        2. 对结果求平方
        3. 求平均
        4. 开根号
        5. 年化：× sqrt(252) × 100%
    """
    # 获取每日收益率序列
    daily_returns = calculate_daily_returns(nav_data)

    if len(daily_returns) < 2:
        return 0.0

    # 计算下行偏差：min(0, R_t - target)
    downside_deviations = [min(0.0, r - target) for r in daily_returns]

    # 计算下行方差的平均值
    downside_variance = np.mean([d**2 for d in downside_deviations])

    # 开根号得到下行波动率，然后年化
    downside_volatility = np.sqrt(downside_variance) * np.sqrt(252) * 100

    return round(downside_volatility, 2)


def calculate_sortino_ratio(
    annualized_return: float,
    downside_volatility: float,
    risk_free_rate: float = 0.03,
) -> float:
    """
    计算索提诺比率

    参数:
        annualized_return: 年化收益率（%）
        downside_volatility: 下行波动率（%）
        risk_free_rate: 无风险收益率（小数形式，默认0.03即3%）

    返回:
        float: 索提诺比率

    计算公式:
        索提诺比率 = (年化收益率 - 无风险收益率) / 下行波动率
    """
    if downside_volatility == 0:
        return 0.0

    # 转换为小数形式
    annualized_return_decimal = annualized_return / 100
    downside_volatility_decimal = downside_volatility / 100

    # 计算索提诺比率
    sortino_ratio = (
        annualized_return_decimal - risk_free_rate
    ) / downside_volatility_decimal

    return round(sortino_ratio, 2)


def calculate_information_ratio(
    annualized_active_return: float, tracking_error: float
) -> float:
    """
    计算信息比率

    参数:
        annualized_active_return: 年化主动收益（%）
        tracking_error: 跟踪误差（%）

    返回:
        float: 信息比率

    计算公式:
        信息比率 = 年化主动收益 / 跟踪误差
    """
    if tracking_error == 0:
        return 0.0

    # 转换为小数形式
    annualized_active_return_decimal = annualized_active_return / 100
    tracking_error_decimal = tracking_error / 100

    # 计算信息比率
    information_ratio = annualized_active_return_decimal / tracking_error_decimal

    return round(information_ratio, 2)


def calculate_drawdown_recovery_period(
    nav_data: List[Dict[str, Any]],
    max_dd_start_date: str,
    max_dd_end_date: str,
) -> Dict[str, Any]:
    """
    计算最大回撤修复期

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]
        max_dd_start_date: 最大回撤开始日期
        max_dd_end_date: 最大回撤结束日期

    返回:
        Dict: {
            'recovery_period': int,        # 修复期天数（如果已恢复，否则None）
            'recovery_date': str,          # 恢复日期（如果已恢复，否则None）
            'is_recovered': bool,          # 是否已恢复
            'peak_before_dd': float        # 回撤前峰值
        }
    """
    # 找到回撤开始前的峰值
    peak_before_dd = 0.0
    for data in nav_data:
        date = data["date"]
        nav = data["nav"]
        if date < max_dd_start_date:
            if nav > peak_before_dd:
                peak_before_dd = nav
        else:
            break

    # 找到回撤结束时的净值
    dd_end_nav = None
    for data in nav_data:
        if data["date"] == max_dd_end_date:
            dd_end_nav = data["nav"]
            break

    if dd_end_nav is None or peak_before_dd == 0:
        return {
            "recovery_period": None,
            "recovery_date": None,
            "is_recovered": False,
            "peak_before_dd": peak_before_dd,
        }

    # 查找净值恢复到峰值的日期
    recovery_date = None
    for data in nav_data:
        date = data["date"]
        nav = data["nav"]
        if date > max_dd_end_date and nav >= peak_before_dd:
            recovery_date = date
            break

    if recovery_date:
        # 计算修复期
        end_dt = datetime.strptime(max_dd_end_date, "%Y-%m-%d")
        recovery_dt = datetime.strptime(recovery_date, "%Y-%m-%d")
        recovery_period = (recovery_dt - end_dt).days

        return {
            "recovery_period": recovery_period,
            "recovery_date": recovery_date,
            "is_recovered": True,
            "peak_before_dd": peak_before_dd,
        }
    else:
        return {
            "recovery_period": None,
            "recovery_date": None,
            "is_recovered": False,
            "peak_before_dd": peak_before_dd,
        }


def _safe_float(value: Any) -> Optional[float]:
    """
    将输入安全转换为浮点数，过滤None、NaN、无穷大等异常值。
    """
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def _score_metric(
    value: Any,
    bands: List[Tuple[Optional[float], int, str]],
) -> Tuple[int, str]:
    """
    根据阈值区间为指标打分。

    参数:
        value: 指标值
        bands: [(upper_bound, score, label), ...] 按顺序排列，upper_bound为None表示无上限

    返回:
        Tuple[int, str]: (分值, 分组描述)
    """
    val = _safe_float(value)
    if val is None:
        return 1, "数据缺失或无效"

    for upper_bound, score, label in bands:
        if upper_bound is None or val <= upper_bound:
            return score, label

    # 理论上不会触发，保险返回最后一档
    last_score, last_label = bands[-1][1], bands[-1][2]
    return last_score, last_label


def classify_risk_characteristic(
    annualized_return: Optional[float],
    volatility: Optional[float],
    max_drawdown: Optional[float],
    downside_volatility: Optional[float],
    beta: Optional[float],
    tracking_error: Optional[float],
    sharpe_ratio: Optional[float],
    sortino_ratio: Optional[float],
    calmar_ratio: Optional[float],
) -> Dict[str, Any]:
    """
    基于多维指标的实盘风险分级模型。

    模型思路:
        1. 以波动率、最大回撤、下行波动率、Beta、跟踪误差为基础风险因子，各自0/1/2分。
        2. 夏普、索提诺、卡玛等风险调整收益指标作为加减项。
        3. 设置极端阈值的强制升级规则，确保符合合规视角。
    """
    score_breakdown: List[Dict[str, Any]] = []
    base_score = 0

    def add_base_metric(
        name: str,
        value: Optional[float],
        bands: List[Tuple[Optional[float], int, str]],
        description: str,
    ):
        nonlocal base_score
        val = _safe_float(value)
        if val is None:
            score, band_desc = 0, "数据缺失或无效"
        else:
            score, band_desc = _score_metric(val, bands)
            base_score += score
        score_breakdown.append(
            {
                "metric": name,
                "value": value,
                "score": score,
                "band": band_desc,
                "type": "base",
                "description": description,
            }
        )

    add_base_metric(
        "volatility",
        volatility,
        [(10, 0, "≤10%"), (20, 1, "10%-20%"), (None, 2, ">20%")],
        "年化波动率",
    )
    add_base_metric(
        "max_drawdown",
        max_drawdown,
        [(10, 0, "≤10%"), (20, 1, "10%-20%"), (None, 2, ">20%")],
        "最大回撤",
    )
    add_base_metric(
        "downside_volatility",
        downside_volatility,
        [(7, 0, "≤7%"), (14, 1, "7%-14%"), (None, 2, ">14%")],
        "下行年化波动率",
    )
    add_base_metric(
        "beta",
        beta,
        [(0.8, 0, "≤0.8"), (1.2, 1, "0.8-1.2"), (None, 2, ">1.2")],
        "相对市场Beta",
    )
    add_base_metric(
        "tracking_error",
        tracking_error,
        [(6, 0, "≤6%"), (12, 1, "6%-12%"), (None, 2, ">12%")],
        "年化跟踪误差",
    )

    adjustments = 0

    def add_adjustment(
        name: str,
        value: Optional[float],
        thresholds: List[Tuple[Optional[float], int, str]],
        description: str,
    ):
        nonlocal adjustments
        val = _safe_float(value)
        if val is None:
            score, band_desc = 0, "数据缺失或无效"
        else:
            score, band_desc = _score_metric(val, thresholds)
            adjustments += score
        score_breakdown.append(
            {
                "metric": name,
                "value": value,
                "score": score,
                "band": band_desc,
                "type": "adjustment",
                "description": description,
            }
        )

    # 夏普、索提诺、卡玛：高值降低风险评分，低值增加风险评分
    add_adjustment(
        "sharpe_ratio",
        sharpe_ratio,
        [(0.5, 1, "<=0.5"), (1.0, 0, "0.5-1.0"), (None, -1, ">1.0")],
        "夏普比率",
    )
    add_adjustment(
        "sortino_ratio",
        sortino_ratio,
        [(0.7, 1, "<=0.7"), (1.2, 0, "0.7-1.2"), (None, -1, ">1.2")],
        "索提诺比率",
    )
    add_adjustment(
        "calmar_ratio",
        calmar_ratio,
        [(0.5, 1, "<=0.5"), (1.0, 0, "0.5-1.0"), (None, -1, ">1.0")],
        "卡玛比率",
    )

    # 调整项可能带来负分，确保总分不为负
    raw_score = base_score + adjustments
    risk_score = max(0, raw_score)

    # 极端风险触发强制升级
    override_reasons: List[str] = []
    extreme_rules = [
        ("max_drawdown", 30.0, "最大回撤≥30%"),
        ("volatility", 35.0, "年化波动率≥35%"),
        ("downside_volatility", 20.0, "下行波动率≥20%"),
    ]
    metric_map = {
        "volatility": _safe_float(volatility),
        "max_drawdown": _safe_float(max_drawdown),
        "downside_volatility": _safe_float(downside_volatility),
    }
    for metric_name, threshold, reason in extreme_rules:
        value = metric_map.get(metric_name)
        if value is not None and value >= threshold:
            override_reasons.append(reason)

    if override_reasons:
        risk_level = "高风险（进取型）"
    elif risk_score <= 3:
        risk_level = "低风险（稳健型）"
    elif risk_score <= 6:
        risk_level = "中风险（平衡型）"
    else:
        risk_level = "高风险（进取型）"

    # 收益等级（独立于风险打分，用于组合标签）
    return_level = "收益待评估"
    return_level_code: Optional[int] = None
    annualized_ret_val = _safe_float(annualized_return)
    if annualized_ret_val is not None:
        return_bands: List[Tuple[Optional[float], int, str]] = [
            (0.0, 0, "亏损型"),
            (8.0, 1, "低收益"),
            (15.0, 2, "中收益"),
            (None, 3, "高收益"),
        ]
        for upper_bound, band_code, band_label in return_bands:
            if upper_bound is None or annualized_ret_val <= upper_bound:
                return_level_code = band_code
                return_level = band_label
                break

    risk_level_short = {
        "低风险（稳健型）": "低风险",
        "中风险（平衡型）": "中风险",
        "高风险（进取型）": "高风险",
    }.get(risk_level, risk_level)

    if override_reasons:
        combined_level = f"{risk_level_short}高风险预警"
    elif return_level_code is None:
        combined_level = risk_level_short
    else:
        combined_level = f"{risk_level_short}{return_level}"

    return {
        "level": combined_level,
        "risk_level": risk_level,
        "risk_level_short": risk_level_short,
        "return_level": return_level,
        "return_level_code": return_level_code,
        "score": risk_score,
        "base_score": base_score,
        "adjustments": adjustments,
        "score_breakdown": score_breakdown,
        "override_reasons": override_reasons,
        "annualized_return": annualized_return,
    }


def judge_risk_characteristic(annualized_return: float, volatility: float) -> str:
    """
    保留旧接口以兼容历史调用，默认使用基础分类逻辑。
    """
    classification = classify_risk_characteristic(
        annualized_return=annualized_return,
        volatility=volatility,
        max_drawdown=None,
        downside_volatility=None,
        beta=None,
        tracking_error=None,
        sharpe_ratio=None,
        sortino_ratio=None,
        calmar_ratio=None,
    )
    return f"绝对收益风险类型属于 {classification['level']}"


def calculate_period_returns(
    nav_data: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
    benchmark_data: List[Dict[str, Any]] = None,
) -> Dict[str, Dict[str, float]]:
    """
    计算多时间段收益率

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]
        periods: 时间段字典 {'统计期间': (start_date, end_date), ...}
        benchmark_data: 基准指数净值数据列表（可选）

    返回:
        Dict: {
            '统计期间': {
                'product_return': float,      # 产品期间收益率（%）
                'annualized_return': float,   # 产品年化收益率（%）
                'benchmark_return': float,    # 基准期间收益率（%）
                'excess_return': float        # 超额收益率（%）
            },
            ...
        }
    """
    period_returns = {}

    product_df = _nav_list_to_dataframe(nav_data)
    benchmark_df = _nav_list_to_dataframe(benchmark_data or [])

    for period_name, (start_date, end_date) in periods.items():
        if product_df.empty:
            period_returns[period_name] = {
                "product_return": 0.0,
                "annualized_return": 0.0,
                "benchmark_return": 0.0,
                "excess_return": 0.0,
            }
            continue

        period_product_df = product_df.loc[
            (product_df.index >= start_date) & (product_df.index <= end_date)
        ]

        if period_product_df.empty:
            period_returns[period_name] = {
                "product_return": 0.0,
                "annualized_return": 0.0,
                "benchmark_return": 0.0,
                "excess_return": 0.0,
            }
            continue

        product_return = _calculate_return_from_series(period_product_df["nav"])

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_dt - start_dt).days + 1

        if days > 0:
            annualized_return = ((1 + product_return / 100) ** (365 / days) - 1) * 100
        else:
            annualized_return = 0.0

        benchmark_return = 0.0
        if not benchmark_df.empty:
            # 先限制在配置范围内，再按产品日期对齐并填充
            benchmark_period_df = benchmark_df.loc[
                (benchmark_df.index >= start_date) & (benchmark_df.index <= end_date)
            ]
            benchmark_period_df = benchmark_period_df.reindex(
                period_product_df.index
            ).ffill()
            benchmark_period_df = benchmark_period_df.bfill()

            benchmark_nav_series = benchmark_period_df["nav"].dropna()
            if not benchmark_nav_series.empty:
                benchmark_return = _calculate_return_from_series(benchmark_nav_series)

        excess_return = product_return - benchmark_return

        period_returns[period_name] = {
            "product_return": round(product_return, 2),
            "annualized_return": round(annualized_return, 2),
            "benchmark_return": round(benchmark_return, 2),
            "excess_return": round(excess_return, 2),
        }

    return period_returns


def calculate_period_metrics(
    nav_data: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
    risk_free_rate: float = 0.03,
    benchmark_returns: List[float] = None,
    benchmark_period_returns: Dict[str, float] = None,
    benchmark_return_dates: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    计算多时间段的所有指标

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]
        periods: 时间段字典
        risk_free_rate: 无风险收益率（默认0.03）
        benchmark_returns: 基准收益率序列（可选）
        benchmark_period_returns: 基准各时间段收益率（可选）

    返回:
        Dict: {
            '统计期间': {
                'period_return': float,
                'annualized_return': float,
                'volatility': float,
                'max_drawdown': float,
                'sharpe_ratio': float,
                'calmar_ratio': float,
                'tracking_error': float,
                'downside_volatility': float,
                'sortino_ratio': float,
                'information_ratio': float,
                'beta': float,
                'active_return': float,
                'annualized_active_return': float
            },
            ...
        }
    """
    period_metrics = {}

    for period_name, (start_date, end_date) in periods.items():
        # 筛选该时间段的净值数据
        period_nav_data = [
            data for data in nav_data if start_date <= data["date"] <= end_date
        ]

        if len(period_nav_data) < 2:
            period_metrics[period_name] = {
                "period_return": 0.0,
                "annualized_return": 0.0,
                "volatility": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0,
                "calmar_ratio": 0.0,
                "tracking_error": 0.0,
                "downside_volatility": 0.0,
                "sortino_ratio": 0.0,
                "information_ratio": 0.0,
                "beta": 1.0,
                "active_return": 0.0,
                "annualized_active_return": 0.0,
                "max_dd_start_date": "",
                "max_dd_end_date": "",
                "peak_date": "",
                "peak_nav": 0.0,
                "recovery_period": None,
                "recovery_date": None,
                "is_recovered": False,
            }
            continue

        # 计算所有指标
        returns_info = calculate_returns(period_nav_data)
        drawdown_info = calculate_max_drawdown(period_nav_data)
        recovery_info = calculate_drawdown_recovery_period(
            period_nav_data,
            drawdown_info.get("max_dd_start_date", ""),
            drawdown_info.get("max_dd_end_date", ""),
        )
        volatility = calculate_volatility(period_nav_data)
        sharpe_ratio = calculate_sharpe_ratio(
            returns_info["annualized_return"], volatility, risk_free_rate
        )
        calmar_ratio = calculate_calmar_ratio(
            returns_info["annualized_return"], drawdown_info["max_drawdown"]
        )

        # 计算下行波动率
        downside_volatility = calculate_downside_volatility(period_nav_data)

        # 计算索提诺比率
        sortino_ratio = calculate_sortino_ratio(
            returns_info["annualized_return"],
            downside_volatility,
            risk_free_rate,
        )

        # 计算跟踪误差、β值、主动收益（如果有基准数据）
        tracking_error = 0.0
        beta = 1.0
        active_return_info = {"active_return": 0.0, "annualized_active_return": 0.0}

        if benchmark_returns:
            tracking_error = calculate_tracking_error(
                period_nav_data,
                benchmark_returns,
                benchmark_dates=benchmark_return_dates,
                date_range=(start_date, end_date),
            )
            beta = calculate_beta(
                period_nav_data,
                benchmark_returns,
                benchmark_dates=benchmark_return_dates,
                date_range=(start_date, end_date),
            )

        if benchmark_period_returns and period_name in benchmark_period_returns:
            benchmark_ret = benchmark_period_returns[period_name]
            active_return_info = calculate_active_return(
                returns_info["period_return"],
                benchmark_ret,
                returns_info["days"],
            )

        # 计算信息比率
        information_ratio = 0.0
        if tracking_error > 0:
            information_ratio = calculate_information_ratio(
                active_return_info["annualized_active_return"], tracking_error
            )

        period_metrics[period_name] = {
            "period_return": returns_info["period_return"],
            "annualized_return": returns_info["annualized_return"],
            "volatility": volatility,
            "max_drawdown": drawdown_info["max_drawdown"],
            "max_dd_start_date": drawdown_info.get("max_dd_start_date", ""),
            "max_dd_end_date": drawdown_info.get("max_dd_end_date", ""),
            "peak_date": drawdown_info.get("peak_date", ""),
            "peak_nav": drawdown_info.get("peak_nav", 0.0),
            "recovery_period": recovery_info.get("recovery_period"),
            "recovery_date": recovery_info.get("recovery_date"),
            "is_recovered": recovery_info.get("is_recovered", False),
            "sharpe_ratio": sharpe_ratio,
            "calmar_ratio": calmar_ratio,
            "tracking_error": tracking_error,
            "downside_volatility": downside_volatility,
            "sortino_ratio": sortino_ratio,
            "information_ratio": information_ratio,
            "beta": beta,
            "active_return": active_return_info["active_return"],
            "annualized_active_return": active_return_info["annualized_active_return"],
        }

    return period_metrics


def calculate_all_metrics(
    nav_data: List[Dict[str, Any]],
    risk_free_rate: float = 0.03,
    benchmark_returns: List[float] = None,
    benchmark_period_return: float = None,
    benchmark_return_dates: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    计算所有指标

    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]
        risk_free_rate: 无风险收益率（默认0.03）
        benchmark_returns: 基准收益率序列（可选）
        benchmark_period_return: 基准期间收益率（%，可选）

    返回:
        Dict: 包含所有指标的字典
    """
    # 计算收益率
    returns = calculate_returns(nav_data)

    # 计算最大回撤
    drawdown_info = calculate_max_drawdown(nav_data)

    # 计算波动率
    volatility = calculate_volatility(nav_data)

    # 计算夏普比率
    sharpe_ratio = calculate_sharpe_ratio(
        returns["annualized_return"], volatility, risk_free_rate
    )

    # 计算卡玛比率
    calmar_ratio = calculate_calmar_ratio(
        returns["annualized_return"], drawdown_info["max_drawdown"]
    )

    # 计算日收益率统计
    daily_stats = calculate_daily_return_stats(nav_data)

    # 计算周胜率和月胜率
    weekly_win_rate = calculate_weekly_win_rate(nav_data)
    monthly_win_rate = calculate_monthly_win_rate(nav_data)

    # 新增指标计算
    beta = 1.0
    if benchmark_returns:
        beta = calculate_beta(
            nav_data,
            benchmark_returns,
            benchmark_dates=benchmark_return_dates,
        )

    active_return_info = {"active_return": 0.0, "annualized_active_return": 0.0}
    if benchmark_period_return is not None:
        active_return_info = calculate_active_return(
            returns["period_return"],
            benchmark_period_return,
            returns["days"],
        )

    tracking_error = 0.0
    if benchmark_returns:
        tracking_error = calculate_tracking_error(
            nav_data,
            benchmark_returns,
            benchmark_dates=benchmark_return_dates,
        )

    downside_volatility = calculate_downside_volatility(nav_data)

    sortino_ratio = calculate_sortino_ratio(
        returns["annualized_return"], downside_volatility, risk_free_rate
    )

    information_ratio = 0.0
    if tracking_error > 0:
        information_ratio = calculate_information_ratio(
            active_return_info["annualized_active_return"], tracking_error
        )

    # 计算最大回撤修复期
    recovery_info = calculate_drawdown_recovery_period(
        nav_data,
        drawdown_info["max_dd_start_date"],
        drawdown_info["max_dd_end_date"],
    )

    # 判断收益风险特征（多维分类）
    risk_classification = classify_risk_characteristic(
        annualized_return=returns["annualized_return"],
        volatility=volatility,
        max_drawdown=drawdown_info["max_drawdown"],
        downside_volatility=downside_volatility,
        beta=beta,
        tracking_error=tracking_error,
        sharpe_ratio=sharpe_ratio,
        sortino_ratio=sortino_ratio,
        calmar_ratio=calmar_ratio,
    )
    risk_characteristic = f"{risk_classification['level']}"

    return {
        # 原有指标
        "period_return": returns["period_return"],
        "annualized_return": returns["annualized_return"],
        "max_drawdown": drawdown_info["max_drawdown"],
        "volatility": volatility,
        "sharpe_ratio": sharpe_ratio,
        "calmar_ratio": calmar_ratio,
        "max_daily_return": daily_stats["max_daily_return"],
        "max_daily_loss": daily_stats["max_daily_loss"],
        "max_return_date": daily_stats["max_return_date"],
        "max_loss_date": daily_stats["max_loss_date"],
        "weekly_win_rate": weekly_win_rate,
        "monthly_win_rate": monthly_win_rate,
        # 新增指标
        "beta": beta,
        "active_return": active_return_info["active_return"],
        "annualized_active_return": active_return_info["annualized_active_return"],
        "tracking_error": tracking_error,
        "downside_volatility": downside_volatility,
        "sortino_ratio": sortino_ratio,
        "information_ratio": information_ratio,
        "recovery_period": recovery_info["recovery_period"],
        "recovery_date": recovery_info["recovery_date"],
        "is_recovered": recovery_info["is_recovered"],
        "risk_characteristic": risk_characteristic,
        "risk_classification": risk_classification,
        # 日期信息
        "start_date": returns["start_date"],
        "end_date": returns["end_date"],
        "days": returns["days"],
        # 最大回撤相关信息
        "max_dd_start_date": drawdown_info["max_dd_start_date"],
        "max_dd_end_date": drawdown_info["max_dd_end_date"],
        "peak_date": drawdown_info["peak_date"],
        "peak_nav": drawdown_info["peak_nav"],
    }
