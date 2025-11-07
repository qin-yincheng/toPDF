"""交易统计模块的核心函数。"""

from datetime import datetime
from typing import Any, Dict, List, Optional


def calculate_avg_market_value(
    asset_class: str,
    period_start: str,
    period_end: str,
    daily_positions: List[Dict[str, Any]],
) -> float:
    """计算指定资产类别在期间内的平均持仓市值。"""

    period_data = [
        data
        for data in daily_positions
        if period_start <= data.get("date", "") <= period_end
    ]

    if not period_data:
        return 0.0

    field_mapping = {
        "股票": "stock_value",
        "基金": "fund_value",
        "逆回购": "repo_value",
    }

    field_name = field_mapping.get(asset_class)
    total_value = 0.0

    for item in period_data:
        if field_name is None:
            value = 0.0
        else:
            value = item.get(field_name, 0.0) or 0.0
        total_value += float(value)

    return total_value / len(period_data)


def calculate_turnover_rate(
    asset_class: str,
    period_start: str,
    period_end: str,
    transactions: List[Dict[str, Any]],
    daily_positions: List[Dict[str, Any]],
) -> float:
    """计算指定资产类别在期间内的年化换手率。"""

    period_transactions = [
        txn
        for txn in transactions
        if period_start <= txn.get("date", "") <= period_end
        and txn.get("asset_class") == asset_class
    ]

    buy_amount = sum(
        (txn.get("amount", 0.0) or 0.0) / 10000
        for txn in period_transactions
        if txn.get("direction") == "买入"
    )
    sell_amount = sum(
        (txn.get("amount", 0.0) or 0.0) / 10000
        for txn in period_transactions
        if txn.get("direction") == "卖出"
    )

    total_turnover = buy_amount + sell_amount

    avg_market_value = calculate_avg_market_value(
        asset_class, period_start, period_end, daily_positions
    )

    try:
        start_dt = datetime.strptime(period_start, "%Y-%m-%d")
        end_dt = datetime.strptime(period_end, "%Y-%m-%d")
    except ValueError:
        return 0.0

    days = (end_dt - start_dt).days + 1

    if avg_market_value <= 0 or days <= 0:
        return 0.0

    turnover_rate = (total_turnover / avg_market_value) * (365 / days) * 100
    return round(turnover_rate, 2)


def calculate_turnover_rates(
    transactions: List[Dict[str, Any]],
    daily_positions: List[Dict[str, Any]],
    periods: Dict[str, Any],
    asset_classes: Optional[List[str]] = None,
) -> Dict[str, Dict[str, float]]:
    """批量计算各资产类别在不同时间段的换手率。"""

    if asset_classes is None:
        asset_classes = ["股票", "基金", "逆回购"]

    turnover_data: Dict[str, Dict[str, float]] = {}

    for asset_class in asset_classes:
        turnover_data[asset_class] = {}
        for period_name, period_range in periods.items():
            if not isinstance(period_range, (list, tuple)) or len(period_range) != 2:
                turnover = 0.0
            else:
                start_date, end_date = period_range
                turnover = calculate_turnover_rate(
                    asset_class,
                    start_date,
                    end_date,
                    transactions,
                    daily_positions,
                )
            turnover_data[asset_class][period_name] = turnover

    return turnover_data


def calculate_trading_statistics(
    transactions: List[Dict[str, Any]],
    asset_classes: Optional[List[str]] = None,
) -> Dict[str, Dict[str, float]]:
    """统计各资产类别的买入和卖出金额。"""

    if asset_classes is None:
        asset_classes = ["股票", "基金", "逆回购"]

    stats: Dict[str, Dict[str, float]] = {}

    for asset_class in asset_classes:
        asset_transactions = [
            txn for txn in transactions if txn.get("asset_class") == asset_class
        ]

        buy_amount = sum(
            (txn.get("amount", 0.0) or 0.0) / 10000
            for txn in asset_transactions
            if txn.get("direction") == "买入"
        )
        sell_amount = sum(
            (txn.get("amount", 0.0) or 0.0) / 10000
            for txn in asset_transactions
            if txn.get("direction") == "卖出"
        )

        stats[asset_class] = {
            "buy_amount": round(buy_amount, 2),
            "sell_amount": round(sell_amount, 2),
        }

    return stats


