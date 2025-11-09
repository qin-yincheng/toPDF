"""归因分析核心计算模块。"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def brinson_attribution(
    product_industry_weights: Dict[str, float],
    benchmark_industry_weights: Dict[str, float],
    product_industry_returns: Dict[str, float],
    benchmark_industry_returns: Dict[str, float],
) -> Dict[str, float]:
    """计算 Brinson 归因结果。

    参数均为小数形式，缺失行业按 0 处理。
    """

    industries: Iterable[str] = (
        set(product_industry_weights)
        | set(benchmark_industry_weights)
        | set(product_industry_returns)
        | set(benchmark_industry_returns)
    )

    selection = 0.0
    allocation = 0.0

    for industry in industries:
        wp = product_industry_weights.get(industry, 0.0)
        wb = benchmark_industry_weights.get(industry, 0.0)
        rp = product_industry_returns.get(industry, 0.0)
        rb = benchmark_industry_returns.get(industry, 0.0)

        selection += wp * (rp - rb)
        allocation += (wp - wb) * rb

    total = selection + allocation

    return {
        "selection_effect": round(selection, 6),
        "allocation_effect": round(allocation, 6),
        "total_excess_return": round(total, 6),
    }


def calculate_brinson_on_date(
    date: str,
    position_details: List[Dict[str, Any]],
    total_assets: float,
    industry_mapping: Dict[str, str],
    benchmark_industry_weights: Dict[str, float] | None = None,
    benchmark_industry_returns: Dict[str, float] | None = None,
) -> Dict[str, float]:
    """计算指定日期的 Brinson 归因（百分比形式）。

    注意：Brinson 模型需要使用同一统计期间的收益率。为保证准确性，
    position_details 中应包含以下字段（需与开发者 A 对齐）：

    - ``previous_market_value`` 或 ``begin_market_value``：期初市值（万元）
    - ``market_value``：期末市值（万元）
    - ``net_cash_flow``：期间净流入（万元，买入为正，卖出为负），可选

    若缺失期初市值，则对应行业收益率将退化为 0，仅提供占位结果。
    """

    if not position_details or total_assets <= 0:
        return {
            "selection_effect": 0.0,
            "allocation_effect": 0.0,
            "total_excess_return": 0.0,
        }

    industry_data: Dict[str, Dict[str, float]] = {}
    missing_begin_value = False

    for pos in position_details:
        code = pos.get("code", "")
        industry = industry_mapping.get(code, "未知行业")
        market_value = float(pos.get("market_value", 0.0))
        begin_value = float(
            pos.get("previous_market_value") or pos.get("begin_market_value") or 0.0
        )
        net_cash_flow = float(pos.get("net_cash_flow", 0.0))

        if begin_value <= 0:
            missing_begin_value = True

        data = industry_data.setdefault(
            industry,
            {
                "begin_value": 0.0,
                "end_value": 0.0,
                "net_cash_flow": 0.0,
            },
        )
        data["begin_value"] += begin_value
        data["end_value"] += market_value
        data["net_cash_flow"] += net_cash_flow

    product_weights: Dict[str, float] = {}
    product_returns: Dict[str, float] = {}

    for industry, data in industry_data.items():
        weight = data["end_value"] / total_assets if total_assets > 0 else 0.0
        product_weights[industry] = weight

        begin_value = data["begin_value"]
        if begin_value > 0:
            net_cash_flow = data["net_cash_flow"]
            product_returns[industry] = (
                data["end_value"] - begin_value - net_cash_flow
            ) / begin_value
        else:
            product_returns[industry] = 0.0

    benchmark_weights = benchmark_industry_weights or {}
    benchmark_returns = benchmark_industry_returns or {}

    brinson_result = brinson_attribution(
        product_weights,
        benchmark_weights,
        product_returns,
        benchmark_returns,
    )

    if missing_begin_value:
        # NOTE: 需与开发者 A 对齐，确保提供期初市值或日度行业收益率。
        # 当前返回值中收益率部分可能退化为 0，仅供兜底展示，不建议用于正式分析。
        pass

    return {
        "selection_effect": round(brinson_result["selection_effect"] * 100, 2),
        "allocation_effect": round(brinson_result["allocation_effect"] * 100, 2),
        "total_excess_return": round(brinson_result["total_excess_return"] * 100, 2),
    }


def calculate_daily_brinson_attribution(
    daily_positions: List[Dict[str, Any]],
    industry_mapping: Dict[str, str],
    benchmark_industry_weights: Dict[str, Dict[str, float]] | None = None,
    benchmark_industry_returns: Dict[str, Dict[str, float]] | None = None,
) -> List[Dict[str, Any]]:
    """计算每日 Brinson 归因序列。"""

    if not daily_positions:
        return []

    results: List[Dict[str, Any]] = []

    for daily_data in daily_positions:
        date = daily_data.get("date", "")
        positions_raw = daily_data.get("positions")
        if isinstance(positions_raw, dict):
            positions = list(positions_raw.values())
        else:
            positions = positions_raw or []

        total_assets = float(daily_data.get("total_assets", 0.0) or 0.0)
        if total_assets <= 0 and positions:
            total_assets = sum(float(pos.get("market_value", 0.0)) for pos in positions)

        if not positions or total_assets <= 0:
            results.append(
                {
                    "date": date,
                    "selection_effect": 0.0,
                    "allocation_effect": 0.0,
                    "total_excess_return": 0.0,
                }
            )
            continue

        bench_weights = (
            benchmark_industry_weights.get(date) if benchmark_industry_weights else None
        )
        bench_returns = (
            benchmark_industry_returns.get(date) if benchmark_industry_returns else None
        )

        result = calculate_brinson_on_date(
            date,
            positions,
            total_assets,
            industry_mapping,
            bench_weights,
            bench_returns,
        )

        results.append({"date": date, **result})

    return results


def calculate_cumulative_brinson_attribution(
    daily_brinson: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """根据每日归因结果计算累计值。"""

    if not daily_brinson:
        return []

    cumulative_selection = 0.0
    cumulative_allocation = 0.0
    cumulative_total = 0.0

    cumulative_results: List[Dict[str, Any]] = []

    for data in daily_brinson:
        cumulative_selection += float(data.get("selection_effect", 0.0))
        cumulative_allocation += float(data.get("allocation_effect", 0.0))
        cumulative_total += float(data.get("total_excess_return", 0.0))

        cumulative_results.append(
            {
                "date": data.get("date", ""),
                "cumulative_selection": round(cumulative_selection, 2),
                "cumulative_allocation": round(cumulative_allocation, 2),
                "cumulative_excess_return": round(cumulative_total, 2),
            }
        )

    return cumulative_results


def calculate_industry_attribution(
    position_details: List[Dict[str, Any]],
    total_assets: float,
    total_profit: float,
    industry_mapping: Dict[str, str],
    benchmark_industry_weights: Dict[str, float] | None = None,
    benchmark_industry_returns: Dict[str, float] | None = None,
) -> List[Dict[str, Any]]:
    """计算行业层面的归因结果。

    为保证 Brinson 模型的期间一致性，position_details 中建议补充：
    - ``previous_market_value``/``begin_market_value``：期间期初行业市值（万元）
    - ``net_cash_flow``：期间净流入（万元），买入为正，卖出为负

    若缺少期初市值，则该行业收益率退化为 0，仅用于占位展示。
    """

    if not position_details or total_assets <= 0:
        return []

    industry_data: Dict[str, Dict[str, float]] = {}
    missing_begin_value = False

    for pos in position_details:
        code = pos.get("code", "")
        industry = industry_mapping.get(code, "未知行业")
        market_value = float(pos.get("market_value", 0.0))
        begin_value = float(
            pos.get("previous_market_value") or pos.get("begin_market_value") or 0.0
        )
        net_cash_flow = float(pos.get("net_cash_flow", 0.0))
        profit_loss = float(pos.get("profit_loss", 0.0))

        data = industry_data.setdefault(
            industry,
            {
                "begin_value": 0.0,
                "end_value": 0.0,
                "net_cash_flow": 0.0,
                "profit_loss": 0.0,
            },
        )
        data["begin_value"] += begin_value
        data["end_value"] += market_value
        data["net_cash_flow"] += net_cash_flow
        data["profit_loss"] += profit_loss

        if begin_value <= 0:
            missing_begin_value = True

    benchmark_weights = benchmark_industry_weights or {}
    benchmark_returns = benchmark_industry_returns or {}

    results: List[Dict[str, Any]] = []

    for industry, data in industry_data.items():
        weight = data["end_value"] / total_assets if total_assets > 0 else 0.0
        weight_pct = weight * 100
        contribution_pct = (
            data["profit_loss"] / total_profit * 100 if total_profit != 0 else 0.0
        )

        industry_return = 0.0
        begin_value = data["begin_value"]
        if begin_value > 0:
            net_cash_flow = data["net_cash_flow"]
            industry_return = (
                data["end_value"] - begin_value - net_cash_flow
            ) / begin_value
        elif begin_value == 0 and data["end_value"] == 0:
            industry_return = 0.0

        benchmark_weight = benchmark_weights.get(industry, 0.0)
        benchmark_return = benchmark_returns.get(industry, 0.0)

        allocation = (weight - benchmark_weight) * benchmark_return
        selection = weight * (industry_return - benchmark_return)

        results.append(
            {
                "industry": industry,
                "weight": round(weight_pct, 4),
                "contribution": round(contribution_pct, 4),
                "profit": round(data["profit_loss"], 2),
                "selection_return": round(selection * 100, 2),
                "allocation_return": round(allocation * 100, 2),
            }
        )

    if missing_begin_value:
        # NOTE: 需与开发者 A 对齐行业期初市值/净流入字段，缺失时收益率将退化为 0。
        pass

    results.sort(key=lambda item: item["profit"], reverse=True)
    return results


def calculate_stock_performance(
    position_details: List[Dict[str, Any]],
    total_assets: float,
    total_profit: float,
) -> List[Dict[str, Any]]:
    """计算个股绩效指标。"""

    if not position_details or total_assets <= 0:
        return []

    results: List[Dict[str, Any]] = []

    for pos in position_details:
        market_value = float(pos.get("market_value", 0.0))
        profit_loss = float(pos.get("profit_loss", 0.0))
        weight_pct = market_value / total_assets * 100 if total_assets > 0 else 0.0
        contribution_pct = (
            profit_loss / total_profit * 100 if total_profit != 0 else 0.0
        )

        results.append(
            {
                "code": pos.get("code", ""),
                "name": pos.get("name", ""),
                "weight": round(weight_pct, 4),
                "contribution": round(contribution_pct, 4),
                "profit": round(profit_loss, 2),
            }
        )

    results.sort(key=lambda item: item["profit"], reverse=True)
    return results


def calculate_position_nodes(
    position_details: List[Dict[str, Any]],
    total_assets: float,
) -> List[Dict[str, Any]]:
    """计算持仓节点数据。"""

    if not position_details or total_assets <= 0:
        nodes = ["TOP1", "TOP2", "TOP3", "TOP5", "TOP10", "TOP50", "TOP100"]
        return [
            {"node": node, "market_value": 0.0, "percentage": 0.0} for node in nodes
        ]

    sorted_positions = sorted(
        position_details,
        key=lambda pos: float(pos.get("market_value", 0.0)),
        reverse=True,
    )

    node_limits = {
        "TOP1": 1,
        "TOP2": 2,
        "TOP3": 3,
        "TOP5": 5,
        "TOP10": 10,
        "TOP50": 50,
        "TOP100": 100,
    }

    results: List[Dict[str, Any]] = []

    for node, count in node_limits.items():
        top_positions = sorted_positions[:count]
        total_market_value = sum(
            float(pos.get("market_value", 0.0)) for pos in top_positions
        )
        percentage = (
            total_market_value / total_assets * 100 if total_assets > 0 else 0.0
        )

        results.append(
            {
                "node": node,
                "market_value": round(total_market_value, 2),
                "percentage": round(percentage, 2),
            }
        )

    return results
