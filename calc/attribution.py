"""归因分析核心计算模块。"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


def _normalize_weight_mapping(weights: Dict[str, float] | None) -> Dict[str, float]:
    """将权重统一为 0-1 之间的小数。"""
    if not weights:
        return {}

    normalized: Dict[str, float] = {}
    for industry, value in weights.items():
        if value is None:
            continue
        weight = float(value)
        if weight > 1.0:
            weight = weight / 100.0
        normalized[industry] = weight
    return normalized


def _normalize_return_mapping(returns: Dict[str, float] | None) -> Dict[str, float]:
    """将收益率统一为小数形式。"""
    if not returns:
        return {}

    normalized: Dict[str, float] = {}
    for industry, value in returns.items():
        if value is None:
            continue
        ret = float(value)
        if ret > 1.0 or ret < -1.0:
            ret = ret / 100.0
        normalized[industry] = ret
    return normalized


def _extract_benchmark_snapshot(
    benchmark_mapping: Dict[str, Any] | None, date: str
) -> Dict[str, float]:
    """兼容按日期或静态字典的基准输入。"""
    if not benchmark_mapping:
        return {}

    if isinstance(benchmark_mapping, dict):
        snapshot = benchmark_mapping.get(date)
        if isinstance(snapshot, dict):
            return {k: float(v) for k, v in snapshot.items() if v is not None}

        # 如果不是按日期嵌套的结构，则尝试判断是否已是行业->数值
        if all(
            isinstance(value, (int, float)) or value is None
            for value in benchmark_mapping.values()
        ):
            return {k: float(v) for k, v in benchmark_mapping.items() if v is not None}

    return {}


def brinson_attribution(
    product_industry_weights: Dict[str, float],
    benchmark_industry_weights: Dict[str, float],
    product_industry_returns: Dict[str, float],
    benchmark_industry_returns: Dict[str, float],
) -> Dict[str, float]:
    """按 Brinson-Fachler 口径计算归因结果，包含交互项。"""

    product_industry_weights = _normalize_weight_mapping(product_industry_weights)
    benchmark_industry_weights = _normalize_weight_mapping(benchmark_industry_weights)
    product_industry_returns = _normalize_return_mapping(product_industry_returns)
    benchmark_industry_returns = _normalize_return_mapping(benchmark_industry_returns)

    industries: Iterable[str] = (
        set(product_industry_weights)
        | set(benchmark_industry_weights)
        | set(product_industry_returns)
        | set(benchmark_industry_returns)
    )

    benchmark_total_return = sum(
        benchmark_industry_weights.get(industry, 0.0)
        * benchmark_industry_returns.get(industry, 0.0)
        for industry in industries
    )

    selection_raw = 0.0
    allocation = 0.0
    interaction = 0.0

    for industry in industries:
        wp = product_industry_weights.get(industry, 0.0)
        wb = benchmark_industry_weights.get(industry, 0.0)
        rp = product_industry_returns.get(industry, 0.0)
        rb = benchmark_industry_returns.get(industry, 0.0)

        selection_raw += wb * (rp - rb)
        allocation += (wp - wb) * (rb - benchmark_total_return)
        interaction += (wp - wb) * (rp - rb)

    selection_combined = selection_raw + interaction
    total = selection_raw + allocation + interaction

    return {
        "selection_effect": round(selection_raw, 6),
        "allocation_effect": round(allocation, 6),
        "interaction_effect": round(interaction, 6),
        "selection_effect_with_interaction": round(selection_combined, 6),
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
            "interaction_effect": 0.0,
            "total_excess_return": 0.0,
            "selection_effect_with_interaction": 0.0,
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
        net_cash_flow = data["net_cash_flow"]
        denominator = begin_value + 0.5 * net_cash_flow
        if abs(denominator) > 1e-8:
            product_returns[industry] = (
                data["end_value"] - begin_value - net_cash_flow
            ) / denominator
        else:
            product_returns[industry] = 0.0

    benchmark_weights = benchmark_industry_weights or {}
    benchmark_returns = benchmark_industry_returns or {}
    benchmark_weights = _normalize_weight_mapping(benchmark_weights)
    benchmark_returns = _normalize_return_mapping(benchmark_returns)

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
        "interaction_effect": round(brinson_result["interaction_effect"] * 100, 2),
        "selection_effect_with_interaction": round(
            brinson_result["selection_effect_with_interaction"] * 100, 2
        ),
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
                    "interaction_effect": 0.0,
                    "selection_effect_with_interaction": 0.0,
                    "total_excess_return": 0.0,
                }
            )
            continue

        bench_weights = _extract_benchmark_snapshot(benchmark_industry_weights, date)
        bench_returns = _extract_benchmark_snapshot(benchmark_industry_returns, date)

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
    cumulative_interaction = 0.0
    cumulative_selection_with_interaction = 0.0
    cumulative_total = 0.0

    cumulative_results: List[Dict[str, Any]] = []

    for data in daily_brinson:
        cumulative_selection += float(data.get("selection_effect", 0.0))
        cumulative_allocation += float(data.get("allocation_effect", 0.0))
        cumulative_interaction += float(data.get("interaction_effect", 0.0))
        cumulative_selection_with_interaction += float(
            data.get("selection_effect_with_interaction", 0.0)
        )
        cumulative_total += float(data.get("total_excess_return", 0.0))

        cumulative_results.append(
            {
                "date": data.get("date", ""),
                "cumulative_selection": round(cumulative_selection, 2),
                "cumulative_allocation": round(cumulative_allocation, 2),
                "cumulative_interaction": round(cumulative_interaction, 2),
                "cumulative_selection_with_interaction": round(
                    cumulative_selection_with_interaction, 2
                ),
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
    
    注意: 权重和贡献度基于股票资产计算,不包含现金。
    """

    if not position_details:
        return []
    
    # 计算股票总市值和总收益(用于权重和贡献度计算)
    active_positions = [p for p in position_details if p.get("market_value", 0.0) > 0]
    total_stock_value = sum(p.get("market_value", 0.0) for p in active_positions)
    total_stock_profit = sum(p.get("profit_loss", 0.0) for p in position_details)
    
    if total_stock_value <= 0:
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
    benchmark_weights = _normalize_weight_mapping(benchmark_weights)
    benchmark_returns = _normalize_return_mapping(benchmark_returns)

    results: List[Dict[str, Any]] = []

    benchmark_total_return = sum(
        benchmark_weights.get(ind, 0.0) * benchmark_returns.get(ind, 0.0)
        for ind in benchmark_weights
    )

    for industry, data in industry_data.items():
        # 使用股票总市值和总收益作为基准
        weight = data["end_value"] / total_stock_value if total_stock_value > 0 else 0.0
        weight_pct = weight * 100
        contribution_pct = (
            data["profit_loss"] / total_stock_profit * 100 if total_stock_profit != 0 else 0.0
        )

        begin_value = data["begin_value"]
        net_cash_flow = data["net_cash_flow"]
        denominator = begin_value + 0.5 * net_cash_flow
        if abs(denominator) > 1e-8:
            industry_return = (
                data["end_value"] - begin_value - net_cash_flow
            ) / denominator
        else:
            industry_return = 0.0

        benchmark_weight = benchmark_weights.get(industry, 0.0)
        benchmark_return = benchmark_returns.get(industry, 0.0)
        selection_raw = benchmark_weight * (industry_return - benchmark_return)
        allocation = (weight - benchmark_weight) * (
            benchmark_return - benchmark_total_return
        )
        interaction = (weight - benchmark_weight) * (industry_return - benchmark_return)
        selection_with_interaction = selection_raw + interaction

        results.append(
            {
                "industry": industry,
                "weight": round(weight_pct, 4),
                "contribution": round(contribution_pct, 4),
                "profit": round(data["profit_loss"], 2),
                "selection_return": round(selection_raw * 100, 2),
                "allocation_return": round(allocation * 100, 2),
                "interaction_return": round(interaction * 100, 2),
                "selection_return_with_interaction": round(
                    selection_with_interaction * 100, 2
                ),
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
    """计算个股绩效指标。
    
    注意: 权重和贡献度基于股票资产计算,不包含现金。
    """

    if not position_details:
        return []
    
    # 计算股票总市值和总收益(用于权重和贡献度计算)
    active_positions = [p for p in position_details if p.get("market_value", 0.0) > 0]
    total_stock_value = sum(p.get("market_value", 0.0) for p in active_positions)
    total_stock_profit = sum(p.get("profit_loss", 0.0) for p in position_details)
    
    if total_stock_value <= 0:
        return []

    results: List[Dict[str, Any]] = []

    for pos in position_details:
        market_value = float(pos.get("market_value", 0.0))
        profit_loss = float(pos.get("profit_loss", 0.0))
        
        # 使用股票总市值和总收益作为基准
        weight_pct = market_value / total_stock_value * 100 if total_stock_value > 0 else 0.0
        contribution_pct = (
            profit_loss / total_stock_profit * 100 if total_stock_profit != 0 else 0.0
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
    """计算持仓节点数据。
    
    注意: 百分比基于股票资产计算,不包含现金。
    """

    # 只使用期末持仓(market_value > 0)
    active_positions = [p for p in position_details if p.get("market_value", 0.0) > 0]
    total_stock_value = sum(p.get("market_value", 0.0) for p in active_positions)
    
    if not active_positions or total_stock_value <= 0:
        nodes = ["TOP1", "TOP2", "TOP3", "TOP5", "TOP10", "TOP50", "TOP100"]
        return [
            {"node": node, "market_value": 0.0, "percentage": 0.0} for node in nodes
        ]

    sorted_positions = sorted(
        active_positions,
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
        # 使用股票总市值作为基准
        percentage = (
            total_market_value / total_stock_value * 100 if total_stock_value > 0 else 0.0
        )

        results.append(
            {
                "node": node,
                "market_value": round(total_market_value, 2),
                "percentage": round(percentage, 2),
            }
        )

    return results
