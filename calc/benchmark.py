from typing import Any, Dict, List, Optional

import pandas as pd


def calculate_benchmark_cumulative_returns(
    benchmark_df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """计算基准累计收益率序列。"""

    if benchmark_df is None or benchmark_df.empty:
        return []

    initial_price = float(benchmark_df.iloc[0]["close"] or 0)
    if initial_price == 0:
        return [
            {
                "date": str(row["trade_date"]),
                "cumulative_return": 0.0,
            }
            for _, row in benchmark_df.iterrows()
        ]

    cumulative = []
    for _, row in benchmark_df.iterrows():
        price = float(row["close"] or 0)
        value = ((price - initial_price) / initial_price) * 100
        cumulative.append(
            {"date": str(row["trade_date"]), "cumulative_return": round(value, 2)}
        )

    return cumulative


def calculate_benchmark_drawdowns(
    benchmark_df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """计算基准回撤序列。"""

    if benchmark_df is None or benchmark_df.empty:
        return []

    drawdowns: List[Dict[str, Any]] = []
    peak_price = float(benchmark_df.iloc[0]["close"] or 0)

    for _, row in benchmark_df.iterrows():
        price = float(row["close"] or 0)
        if price > peak_price:
            peak_price = price
        if peak_price == 0:
            drawdown = 0.0
        else:
            drawdown = ((peak_price - price) / peak_price) * 100
        drawdowns.append(
            {"date": str(row["trade_date"]), "drawdown": round(drawdown, 2)}
        )

    return drawdowns


def calculate_cumulative_excess_returns(
    product_cumulative: List[Dict[str, Any]],
    benchmark_cumulative: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """计算累计超额收益序列。"""

    benchmark_map = {
        item["date"]: item.get("cumulative_return", 0.0)
        for item in benchmark_cumulative
    }

    excess_returns: List[Dict[str, Any]] = []
    for item in product_cumulative:
        date = item.get("date")
        product_value = item.get("cumulative_return", 0.0)
        benchmark_value = benchmark_map.get(date, 0.0)
        excess_returns.append(
            {
                "date": date,
                "excess_return": round(product_value - benchmark_value, 2),
            }
        )

    return excess_returns


def calculate_benchmark_period_return(
    benchmark_df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> float:
    """计算基准期间收益率。"""

    if benchmark_df is None or benchmark_df.empty:
        return 0.0

    df = benchmark_df
    if start_date is not None:
        df = df[df["trade_date"] >= start_date]
    if end_date is not None:
        df = df[df["trade_date"] <= end_date]

    if df.empty:
        return 0.0

    initial_price = float(df.iloc[0]["close"] or 0)
    final_price = float(df.iloc[-1]["close"] or 0)

    if initial_price == 0:
        return 0.0

    period_return = ((final_price - initial_price) / initial_price) * 100

    return round(period_return, 2)
