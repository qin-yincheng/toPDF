from datetime import datetime, timedelta
from typing import List
import pandas_market_calendars as mcal

# 交易日历单例
_calendar = None


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
