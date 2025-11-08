"""PDF 报表桥接层。

该模块将计算层产出的原始结果转换成 `charts/` 目录中 图表函数所需的数据结构。
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

import config

from . import (
    attribution,
    benchmark,
    formatter,
    metrics,
    trading,
    utils,
)


def _get_config(name: str, default: Any) -> Any:
    """读取配置模块中的字段，缺失时返回默认值。"""

    return getattr(config, name, default)


def _round_value(value: Any, digits: int = 2) -> float:
    """将输入转换为浮点并保留指定位数。"""

    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return 0.0


def _percentize(value: Any, digits: int = 2) -> float:
    """将小数形式的收益乘以 100。"""

    try:
        return round(float(value) * 100, digits)
    except (TypeError, ValueError):
        return 0.0


def _filter_by_date_range(
    records: Iterable[Dict[str, Any]],
    start: str,
    end: str,
    date_key: str = "date",
) -> List[Dict[str, Any]]:
    """按照日期范围过滤字典列表。"""

    return [
        row
        for row in records
        if start <= str(row.get(date_key, "")) <= end  # 字符串日期已满足排序要求
    ]


# chart1_1 产品表现总览
def build_performance_overview_data(
    nav_data: List[Dict[str, Any]],
    product_info: Optional[Dict[str, Any]] = None,
    risk_free_rate: float = 0.03,
    benchmark_returns: Optional[List[float]] = None,
    benchmark_period_return: Optional[float] = None,
) -> Dict[str, Any]:
    """组装产品表现总览表格所需数据。"""

    if not nav_data:
        return {}

    metrics_all = metrics.calculate_all_metrics(
        nav_data,
        risk_free_rate=risk_free_rate,
        benchmark_returns=benchmark_returns,
        benchmark_period_return=benchmark_period_return,
    )

    info: Dict[str, Any] = {}
    info.update(_get_config("PRODUCT_INFO", {}))
    if product_info:
        info.update(product_info)

    latest = nav_data[-1]
    liabilities = float(info.get("total_liabilities", 0.0) or 0.0)
    current_scale = float(info.get("current_scale", 0.0) or 0.0)
    if current_scale == 0.0:
        current_scale = float(latest.get("total_assets", 0.0) or 0.0)

    return {
        "product_name": info.get("product_name") or info.get("name", ""),
        "establishment_date": info.get("establishment_date", ""),
        "current_scale": _round_value(current_scale),
        "investment_strategy": info.get("investment_strategy", ""),
        "latest_nav_date": latest.get("date", ""),
        "cumulative_nav": _round_value(latest.get("nav", 0.0), 4),
        "unit_nav": _round_value(latest.get("nav", 0.0), 4),
        "same_strategy_ranking": _round_value(
            info.get("same_strategy_ranking", metrics_all.get("information_ratio", 0.0))
        ),
        "total_return": _round_value(metrics_all.get("period_return", 0.0)),
        "total_return_annualized": _round_value(
            metrics_all.get("annualized_return", 0.0)
        ),
        "active_return": _round_value(metrics_all.get("active_return", 0.0)),
        "active_return_annualized": _round_value(
            metrics_all.get("annualized_active_return", 0.0)
        ),
        "max_drawdown": -abs(_round_value(metrics_all.get("max_drawdown", 0.0))),
        "sharpe_ratio": _round_value(metrics_all.get("sharpe_ratio", 0.0)),
        "beta": _round_value(metrics_all.get("beta", 0.0)),
        "absolute_return_risk_type": info.get(
            "absolute_return_risk_type",
            metrics_all.get("risk_characteristic", ""),
        ),
        "active_return_risk_type": info.get(
            "active_return_risk_type",
            metrics_all.get("risk_characteristic", ""),
        ),
        "profitability_under_equivalent_risk": info.get(
            "profitability_under_equivalent_risk", ""
        ),
        "total_liabilities": _round_value(liabilities),
    }


def _format_period_returns_table(
    period_returns: Dict[str, Dict[str, float]],
) -> List[List[str]]:
    header = ["时间段", "组合收益率(%)", "基准收益率(%)", "超额收益率(%)"]
    rows = [header]
    for period, values in period_returns.items():
        rows.append(
            [
                period,
                f"{_round_value(values.get('product_return', 0.0)):.2f}",
                f"{_round_value(values.get('benchmark_return', 0.0)):.2f}",
                f"{_round_value(values.get('excess_return', 0.0)):.2f}",
            ]
        )
    return rows


def _slice_nav_by_period(
    nav_data: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
) -> Dict[str, List[Dict[str, Any]]]:
    return {
        name: _filter_by_date_range(nav_data, start, end)
        for name, (start, end) in periods.items()
    }


# chart1_3 / chart1_4 / chart1_5 / chart1_6
def build_nav_performance_data(
    nav_data: List[Dict[str, Any]],
    periods: Optional[Dict[str, Tuple[str, str]]] = None,
    benchmark_nav_data: Optional[List[Dict[str, Any]]] = None,
    benchmark_returns: Optional[List[float]] = None,
    benchmark_period_returns: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """整合单位净值、日收益、期间收益及指标分析相关数据。"""

    if not nav_data:
        return {}

    periods = periods or _get_config("PERIODS", {})

    product_cumulative = metrics.calculate_cumulative_returns(nav_data)
    benchmark_cumulative: List[Dict[str, Any]] = []
    if benchmark_nav_data:
        benchmark_cumulative = metrics.calculate_cumulative_returns(benchmark_nav_data)

    benchmark_map = {
        item["date"]: item.get("cumulative_return", 0.0)
        for item in benchmark_cumulative
    }
    excess_map = {
        item["date"]: item.get("excess_return", 0.0)
        for item in benchmark.calculate_cumulative_excess_returns(
            product_cumulative, benchmark_cumulative
        )
    }
    nav_series = [
        {
            "date": entry["date"],
            "accumulated_return": entry.get("cumulative_return", 0.0),
            "csi300": benchmark_map.get(entry["date"], 0.0),
            "excess_return": excess_map.get(
                entry["date"], entry.get("cumulative_return", 0.0)
            ),
        }
        for entry in product_cumulative
    ]

    daily_returns = metrics.calculate_daily_returns(nav_data)
    daily_series = []
    for idx, row in enumerate(nav_data[1:], start=1):
        daily_series.append(
            {
                "date": row.get("date", ""),
                "daily_return": _percentize(daily_returns[idx - 1]),
                "cumulative_return": product_cumulative[idx].get(
                    "cumulative_return", 0.0
                ),
            }
        )

    period_returns = metrics.calculate_period_returns(
        nav_data,
        periods,
        benchmark_data=benchmark_nav_data,
    )
    period_metrics = metrics.calculate_period_metrics(
        nav_data,
        periods,
        benchmark_returns=benchmark_returns,
        benchmark_period_returns=benchmark_period_returns,
    )

    return {
        "nav_series": nav_series,
        "daily_returns": daily_series,
        "period_returns": period_returns,
        "period_returns_table": _format_period_returns_table(period_returns),
        "period_metrics": period_metrics,
        "period_metrics_table": formatter.format_period_metrics_for_pdf(period_metrics),
        "period_nav_slices": _slice_nav_by_period(nav_data, periods),
    }


# chart2_1 动态回撤
def build_drawdown_data(
    nav_data: List[Dict[str, Any]],
    benchmark_nav_data: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """生成动态回撤折线与表格数据。"""

    if not nav_data:
        return {}

    product_drawdowns = metrics.calculate_daily_drawdowns(nav_data)
    benchmark_drawdowns = (
        metrics.calculate_daily_drawdowns(benchmark_nav_data)
        if benchmark_nav_data
        else []
    )
    benchmark_map = {
        item["date"]: -abs(item.get("drawdown", 0.0)) for item in benchmark_drawdowns
    }

    series = [
        {
            "date": item.get("date", ""),
            "product_drawdown": -abs(item.get("drawdown", 0.0)),
            "benchmark_drawdown": benchmark_map.get(item.get("date", ""), 0.0),
        }
        for item in product_drawdowns
    ]

    product_max = metrics.calculate_max_drawdown(nav_data)
    benchmark_max = (
        metrics.calculate_max_drawdown(benchmark_nav_data)
        if benchmark_nav_data
        else {
            "max_drawdown": 0.0,
            "max_dd_start_date": "",
            "max_dd_end_date": "",
        }
    )

    product_recovery = metrics.calculate_drawdown_recovery_period(
        nav_data,
        product_max.get("max_dd_start_date", ""),
        product_max.get("max_dd_end_date", ""),
    )
    benchmark_recovery = (
        metrics.calculate_drawdown_recovery_period(
            benchmark_nav_data,
            benchmark_max.get("max_dd_start_date", ""),
            benchmark_max.get("max_dd_end_date", ""),
        )
        if benchmark_nav_data
        else {"recovery_period": None, "recovery_date": None}
    )

    def _format_recovery(data: Dict[str, Any]) -> str:
        if data.get("recovery_period") is None:
            return "-"
        return f"{int(data['recovery_period'])}天 ({data.get('recovery_date', '')})"

    table = {
        "product_max_drawdown": -abs(
            _round_value(product_max.get("max_drawdown", 0.0))
        ),
        "benchmark_max_drawdown": -abs(
            _round_value(benchmark_max.get("max_drawdown", 0.0))
        ),
        "product_dd_start": product_max.get("max_dd_start_date", ""),
        "product_dd_end": product_max.get("max_dd_end_date", ""),
        "benchmark_dd_start": benchmark_max.get("max_dd_start_date", ""),
        "benchmark_dd_end": benchmark_max.get("max_dd_end_date", ""),
        "product_recovery_period": _format_recovery(product_recovery),
        "benchmark_recovery_period": _format_recovery(benchmark_recovery),
    }

    return {"series": series, "table": table}


# chart1_6 指标分析（复用）
def build_indicator_analysis_data(
    period_metrics: Dict[str, Dict[str, Any]],
    nav_data: Optional[List[Dict[str, Any]]] = None,
    periods: Optional[Dict[str, Tuple[str, str]]] = None,
) -> Dict[str, Dict[str, Any]]:
    """根据多时间段指标输出 chart1_6 期望的嵌套结构。"""

    if not period_metrics and nav_data and periods:
        period_metrics = metrics.calculate_period_metrics(nav_data, periods)
    if not period_metrics:
        return {}

    indicator_data: Dict[str, Dict[str, Any]] = {}
    period_order = list(period_metrics.keys())

    def _collect(key: str, sign_negative: bool = False) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for period in period_order:
            value = period_metrics[period].get(key, 0.0)
            value = -abs(value) if sign_negative else value
            result[period] = _round_value(value)
        return result

    indicator_data["*收益率(年化)"] = _collect("annualized_return")
    indicator_data["*波动率(年化)"] = _collect("volatility")
    indicator_data["*跟踪误差(年化)"] = _collect("tracking_error")
    indicator_data["*下行波动率(年化)"] = _collect("downside_volatility")
    indicator_data["*夏普比率(年化)"] = _collect("sharpe_ratio")
    indicator_data["*索提诺比率(年化)"] = _collect("sortino_ratio")
    indicator_data["*信息比率(年化)"] = _collect("information_ratio")
    indicator_data["*最大回撤"] = _collect("max_drawdown", sign_negative=True)
    indicator_data["*卡玛比率"] = _collect("calmar_ratio")

    if nav_data and periods:
        slices = _slice_nav_by_period(nav_data, periods)
        indicator_data["周胜率"] = {}
        indicator_data["月胜率"] = {}
        for period, sliced in slices.items():
            if len(sliced) < 2:
                indicator_data["周胜率"][period] = 0.0
                indicator_data["月胜率"][period] = 0.0
                continue
            indicator_data["周胜率"][period] = _round_value(
                metrics.calculate_weekly_win_rate(sliced)
            )
            indicator_data["月胜率"][period] = _round_value(
                metrics.calculate_monthly_win_rate(sliced)
            )
    else:
        indicator_data["周胜率"] = {period: 0.0 for period in period_order}
        indicator_data["月胜率"] = {period: 0.0 for period in period_order}

    indicator_data["最大回撤期间"] = {period: "-" for period in period_order}
    indicator_data["最大回撤修复期(月)"] = {period: "-" for period in period_order}

    return indicator_data


def _serialize_stock_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "stock_code": entry.get("code", ""),
            "stock_name": entry.get("name", ""),
            "weight_ratio": _round_value(entry.get("weight", 0.0)),
            "contribution": _round_value(entry.get("contribution", 0.0)),
            "profit_amount": _round_value(entry.get("profit", 0.0)),
        }
        for entry in items
    ]


# chart2_3 / chart5_1 / chart5_2
def build_end_holdings_data(
    position_details: List[Dict[str, Any]],
    total_assets: float,
    total_profit: float,
    asset_breakdown: Optional[List[Dict[str, Any]]] = None,
    liability_breakdown: Optional[List[Dict[str, Any]]] = None,
    summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """汇总期末持仓、股票绩效和持仓节点。"""

    stock_performance = attribution.calculate_stock_performance(
        position_details, total_assets, total_profit
    )
    position_nodes = attribution.calculate_position_nodes(
        position_details, total_assets
    )

    assets = asset_breakdown
    if assets is None:
        grouped = defaultdict(float)
        for pos in position_details:
            asset_class = pos.get("asset_class", "股票")
            grouped[asset_class] += float(pos.get("market_value", 0.0) or 0.0)
        assets = [
            {
                "name": name,
                "market_value": _round_value(value),
                "proportion": _round_value(
                    value / total_assets * 100 if total_assets else 0.0
                ),
            }
            for name, value in grouped.items()
        ]

    liabilities = liability_breakdown or []
    if not summary:
        total_liabilities = sum(
            float(item.get("market_value", 0.0) or 0.0) for item in liabilities
        )
        summary = {
            "asset_net_value": _round_value(total_assets - total_liabilities),
            "total_assets": _round_value(total_assets),
            "total_liabilities": _round_value(total_liabilities),
        }

    profit_sorted = sorted(
        stock_performance, key=lambda item: item["profit"], reverse=True
    )
    loss_sorted = sorted(stock_performance, key=lambda item: item["profit"])

    return {
        "holdings_table": {
            "summary": summary,
            "assets": assets,
            "liabilities": liabilities,
        },
        "stock_performance": {
            "profit_data": _serialize_stock_items(profit_sorted[:10]),
            "loss_data": _serialize_stock_items(loss_sorted[:10]),
            "tables": formatter.format_stock_performance_for_pdf(stock_performance),
        },
        "position_nodes": {
            "nodes_data": [
                {
                    "node": item.get("node", ""),
                    "market_value": _round_value(item.get("market_value", 0.0)),
                    "proportion": _round_value(item.get("percentage", 0.0)),
                }
                for item in position_nodes
            ],
            "table": formatter.format_position_nodes_for_pdf(position_nodes),
        },
    }


def _serialize_industry_item(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "industry": entry.get("industry", ""),
        "weight_ratio": _round_value(entry.get("weight", 0.0)),
        "contribution": _round_value(entry.get("contribution", 0.0)),
        "profit_amount": _round_value(entry.get("profit", 0.0)),
        "selection_return": _round_value(entry.get("selection_return", 0.0)),
        "allocation_return": _round_value(entry.get("allocation_return", 0.0)),
    }


# chart3_1 / chart4_2
def build_industry_attribution_data(
    position_details: List[Dict[str, Any]],
    total_assets: float,
    total_profit: float,
    industry_mapping: Dict[str, str],
    benchmark_industry_weights: Optional[Dict[str, float]] = None,
    benchmark_industry_returns: Optional[Dict[str, float]] = None,
    top_n: int = 10,
) -> Dict[str, Any]:
    """整理行业占比及行业归因的所需结构。"""

    industry_attribution = attribution.calculate_industry_attribution(
        position_details,
        total_assets,
        total_profit,
        industry_mapping,
        benchmark_industry_weights=benchmark_industry_weights,
        benchmark_industry_returns=benchmark_industry_returns,
    )

    profit_sorted = sorted(
        industry_attribution, key=lambda item: item["profit"], reverse=True
    )
    loss_sorted = sorted(industry_attribution, key=lambda item: item["profit"])

    industry_data = [
        {
            "industry": item.get("industry", ""),
            "proportion": _round_value(item.get("weight", 0.0)),
            "contribution": _round_value(item.get("contribution", 0.0)),
            "profit": _round_value(item.get("profit", 0.0)),
        }
        for item in industry_attribution
    ]

    return {
        "industry_distribution": {"industry_data": industry_data},
        "industry_tables": formatter.format_industry_attribution_for_pdf(
            industry_attribution, top_n=top_n
        ),
        "industry_profit": {
            "profit_data": [
                _serialize_industry_item(item) for item in profit_sorted[:top_n]
            ],
            "loss_data": [
                _serialize_industry_item(item) for item in loss_sorted[:top_n]
            ],
        },
    }


# chart4_1 Brinson 归因
def build_brinson_data(
    daily_positions: List[Dict[str, Any]],
    industry_mapping: Dict[str, str],
    benchmark_industry_weights: Optional[Dict[str, Dict[str, float]]] = None,
    benchmark_industry_returns: Optional[Dict[str, Dict[str, float]]] = None,
) -> Dict[str, Any]:
    """生成 Brinson 归因折线及表格数据。"""

    daily = attribution.calculate_daily_brinson_attribution(
        daily_positions,
        industry_mapping,
        benchmark_industry_weights=benchmark_industry_weights,
        benchmark_industry_returns=benchmark_industry_returns,
    )
    cumulative = attribution.calculate_cumulative_brinson_attribution(daily)

    series = [
        {
            "date": item.get("date", ""),
            "selection_return": _round_value(item.get("cumulative_selection", 0.0)),
            "allocation_return": _round_value(item.get("cumulative_allocation", 0.0)),
            "total_excess_return": _round_value(
                item.get("cumulative_excess_return", 0.0)
            ),
        }
        for item in cumulative
    ]

    latest = cumulative[-1] if cumulative else {}
    summary_table = [
        ["指标", "数值(%)"],
        [
            "累计选择收益",
            f"{_round_value(latest.get('cumulative_selection', 0.0)):.2f}",
        ],
        [
            "累计配置收益",
            f"{_round_value(latest.get('cumulative_allocation', 0.0)):.2f}",
        ],
        [
            "累计超额收益",
            f"{_round_value(latest.get('cumulative_excess_return', 0.0)):.2f}",
        ],
    ]

    return {
        "daily": daily,
        "series": series,
        "summary_table": summary_table,
    }


# chart6_4 换手率
def build_turnover_data(
    transactions: List[Dict[str, Any]],
    daily_positions: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
    asset_classes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """汇总 chart6_4 所需的换手率表格数据，不做额外单位转换。"""

    turnover_rates = trading.calculate_turnover_rates(
        transactions,
        daily_positions,
        periods,
        asset_classes=asset_classes,
    )
    table = formatter.format_turnover_rates_for_pdf(turnover_rates)
    return {"turnover_rates": turnover_rates, "table": table}


# chart6_5 期间交易（表格部分）
def build_period_transaction_data(
    transactions: List[Dict[str, Any]],
    asset_classes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """整理 chart6_5 所需的期间交易统计，图表时序暂未实现。"""

    trading_stats = trading.calculate_trading_statistics(
        transactions,
        asset_classes=asset_classes,
    )
    table = formatter.format_trading_statistics_for_pdf(trading_stats)
    return {
        "trading_stats": trading_stats,
        "table": table,
        "series": [],
    }


# chart1_2 产品规模总览
def build_scale_overview_data(
    nav_data: List[Dict[str, Any]],
    transactions: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
) -> Dict[str, Any]:
    """
    构建产品规模总览数据
    
    包含资产规模、份额变化、净申购等信息的时序数据
    """
    if not nav_data:
        return {}
    
    # 基于净值数据计算规模变化
    scale_series = []
    for entry in nav_data:
        date = entry.get('date', '')
        total_assets = entry.get('total_assets', 0)
        nav = entry.get('nav', 1.0)
        
        # 估算份额（假设初始份额 = 初始资产）
        initial_assets = nav_data[0].get('total_assets', 1.0)
        shares = total_assets / nav if nav > 0 else 0
        
        scale_series.append({
            'date': date,
            'total_assets': _round_value(total_assets),
            'nav': _round_value(nav),
            'shares': _round_value(shares),
        })
    
    # 计算申赎统计（基于交易记录）
    buy_amount = sum(float(t.get('amount', 0) or 0) for t in transactions if t.get('direction') == '买入')
    sell_amount = sum(float(t.get('amount', 0) or 0) for t in transactions if t.get('direction') == '卖出')
    net_flow = buy_amount - sell_amount
    
    return {
        'scale_series': scale_series,
        'buy_amount': _round_value(buy_amount / 10000),  # 转换为万元
        'sell_amount': _round_value(sell_amount / 10000),
        'net_flow': _round_value(net_flow / 10000),
    }


# chart2_2 / chart2_4 / chart2_5 大类持仓与仓位时序
def build_asset_allocation_series(
    daily_positions: List[Dict[str, Any]],
    position_details: List[Dict[str, Any]],
    total_assets: float,
) -> List[Dict[str, Any]]:
    """
    构建大类资产配置时序数据
    
    从 daily_positions 中提取股票、现金、基金、逆回购等资产类别的时序数据
    """
    if not daily_positions:
        return []
    
    series = []
    for pos in daily_positions:
        date = pos.get('date', '')
        total = float(pos.get('total_assets', 0) or 0)
        
        # 提取各类资产
        stock_value = float(pos.get('stock_value', 0) or 0)
        cash_value = float(pos.get('cash_value', 0) or 0)
        fund_value = float(pos.get('fund_value', 0) or 0)
        repo_value = float(pos.get('repo_value', 0) or 0)
        
        series.append({
            'date': date,
            'total_assets': _round_value(total),
            'stock': _round_value(stock_value),
            'cash': _round_value(cash_value),
            'fund': _round_value(fund_value),
            'repo': _round_value(repo_value),
            'stock_ratio': _round_value(stock_value / total * 100 if total > 0 else 0),
            'cash_ratio': _round_value(cash_value / total * 100 if total > 0 else 0),
            'fund_ratio': _round_value(fund_value / total * 100 if total > 0 else 0),
            'repo_ratio': _round_value(repo_value / total * 100 if total > 0 else 0),
        })
    
    return series


# chart3_2 / chart3_3 行业时序
def build_industry_timeseries(
    daily_positions: List[Dict[str, Any]],
    industry_mapping: Dict[str, str],
    benchmark_industry_weights: Optional[Dict[str, Any]] = None,
    benchmark_industry_returns: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    构建行业配置时序数据
    
    基于每日持仓数据，按行业聚合持仓市值和占比的时序变化
    """
    if not daily_positions:
        return {}
    
    # 从每日持仓中提取行业时序（需要positions字段）
    # 由于当前 daily_positions 可能没有详细持仓，返回空结构
    # 未来可以从 daily_positions 的 positions 字段中提取每日的行业分布
    
    return {
        'timeseries': [],  # 行业权重时序：[{'date': 'YYYY-MM-DD', '金融': 10.5, '医药': 8.2, ...}]
        'deviation_series': [],  # 偏离度时序：[{'date': 'YYYY-MM-DD', '金融': 2.5, '医药': -1.2, ...}]
        'industry_list': [],  # 行业列表
    }


# chart3_4 大类资产绩效归因
def build_asset_class_attribution(
    position_details: List[Dict[str, Any]],
    total_assets: float,
    total_profit: float,
) -> Dict[str, Any]:
    """
    构建大类资产绩效归因数据
    
    按资产类别（股票、债券、基金等）汇总收益贡献
    """
    if not position_details:
        return {}
    
    # 按资产类别汇总
    class_profit = defaultdict(float)
    class_assets = defaultdict(float)
    
    for pos in position_details:
        asset_class = pos.get('asset_class', '股票')
        profit = float(pos.get('profit_loss', 0) or 0)
        market_value = float(pos.get('market_value', 0) or 0)
        
        class_profit[asset_class] += profit
        class_assets[asset_class] += market_value
    
    # 构建归因表格数据
    attribution_data = []
    for asset_class in sorted(class_assets.keys()):
        profit = class_profit[asset_class]
        assets = class_assets[asset_class]
        
        attribution_data.append({
            'asset_class': asset_class,
            'profit': _round_value(profit),
            'market_value': _round_value(assets),
            'return_rate': _round_value(profit / assets * 100 if assets > 0 else 0),
            'profit_contribution': _round_value(profit / total_profit * 100 if total_profit > 0 else 0),
        })
    
    return {
        'attribution_table': attribution_data,
        'total_profit': _round_value(total_profit),
        'total_assets': _round_value(total_assets),
    }


# chart6_5 期间交易图表
def build_period_transaction_timeseries(
    transactions: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
    asset_classes: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    构建期间交易时序数据
    
    按时间聚合交易记录，生成交易量、交易额的时序图表数据
    """
    if not transactions:
        return []
    
    # 按日期聚合交易
    daily_trades = defaultdict(lambda: {'buy_count': 0, 'sell_count': 0, 'buy_amount': 0.0, 'sell_amount': 0.0})
    
    for trade in transactions:
        date = trade.get('date', '')
        direction = trade.get('direction', '')
        amount = abs(float(trade.get('amount', 0) or 0))
        
        if direction == '买入':
            daily_trades[date]['buy_count'] += 1
            daily_trades[date]['buy_amount'] += amount
        elif direction == '卖出':
            daily_trades[date]['sell_count'] += 1
            daily_trades[date]['sell_amount'] += amount
    
    # 转换为列表格式
    series = []
    for date in sorted(daily_trades.keys()):
        trades = daily_trades[date]
        series.append({
            'date': date,
            'buy_count': trades['buy_count'],
            'sell_count': trades['sell_count'],
            'buy_amount': _round_value(trades['buy_amount'] / 10000),  # 转换为万元
            'sell_amount': _round_value(trades['sell_amount'] / 10000),
            'total_trades': trades['buy_count'] + trades['sell_count'],
        })
    
    return series


def build_page1_data(
    nav_data: List[Dict[str, Any]],
    position_details: List[Dict[str, Any]],
    total_assets: float,
    total_profit: float,
    daily_positions: List[Dict[str, Any]],
    transactions: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
    industry_mapping: Dict[str, str],
    product_info: Optional[Dict[str, Any]] = None,
    risk_free_rate: float = 0.03,
    benchmark_nav_data: Optional[List[Dict[str, Any]]] = None,
    benchmark_returns: Optional[List[float]] = None,
    benchmark_period_return: Optional[float] = None,
    benchmark_period_returns: Optional[Dict[str, float]] = None,
    benchmark_industry_weights: Optional[Dict[str, Any]] = None,
    benchmark_industry_returns: Optional[Dict[str, Any]] = None,
    asset_classes: Optional[List[str]] = None,
    asset_breakdown: Optional[List[Dict[str, Any]]] = None,
    liability_breakdown: Optional[List[Dict[str, Any]]] = None,
    holdings_summary: Optional[Dict[str, Any]] = None,
    period_metrics: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    result["performance_overview"] = build_performance_overview_data(
        nav_data,
        product_info=product_info,
        risk_free_rate=risk_free_rate,
        benchmark_returns=benchmark_returns,
        benchmark_period_return=benchmark_period_return,
    )
    result["nav_performance"] = build_nav_performance_data(
        nav_data,
        periods=periods,
        benchmark_nav_data=benchmark_nav_data,
        benchmark_returns=benchmark_returns,
        benchmark_period_returns=benchmark_period_returns,
    )
    result["drawdown"] = build_drawdown_data(
        nav_data,
        benchmark_nav_data=benchmark_nav_data,
    )
    result["indicator_analysis"] = build_indicator_analysis_data(
        period_metrics or {},
        nav_data=nav_data,
        periods=periods,
    )
    result["end_holdings"] = build_end_holdings_data(
        position_details,
        total_assets,
        total_profit,
        asset_breakdown=asset_breakdown,
        liability_breakdown=liability_breakdown,
        summary=holdings_summary,
    )
    result["industry_attribution"] = build_industry_attribution_data(
        position_details,
        total_assets,
        total_profit,
        industry_mapping,
        benchmark_industry_weights=benchmark_industry_weights,
        benchmark_industry_returns=benchmark_industry_returns,
    )
    result["brinson"] = build_brinson_data(
        daily_positions,
        industry_mapping,
        benchmark_industry_weights=benchmark_industry_weights,
        benchmark_industry_returns=benchmark_industry_returns,
    )
    result["turnover"] = build_turnover_data(
        transactions,
        daily_positions,
        periods,
        asset_classes=asset_classes,
    )
    result["period_transaction"] = build_period_transaction_data(
        transactions,
        asset_classes=asset_classes,
    )
    result["scale_overview"] = build_scale_overview_data(
        nav_data,
        transactions,
        periods,
    )
    result["asset_allocation_series"] = build_asset_allocation_series(
        daily_positions,
        position_details,
        total_assets,
    )
    result["industry_timeseries"] = build_industry_timeseries(
        daily_positions,
        industry_mapping,
        benchmark_industry_weights=benchmark_industry_weights,
        benchmark_industry_returns=benchmark_industry_returns,
    )
    result["asset_class_attribution"] = build_asset_class_attribution(
        position_details,
        total_assets,
        total_profit,
    )
    result["period_transaction_series"] = build_period_transaction_timeseries(
        transactions,
        periods,
        asset_classes=asset_classes,
    )
    return result


__all__ = [
    "build_performance_overview_data",
    "build_nav_performance_data",
    "build_drawdown_data",
    "build_indicator_analysis_data",
    "build_end_holdings_data",
    "build_industry_attribution_data",
    "build_brinson_data",
    "build_turnover_data",
    "build_period_transaction_data",
    "build_scale_overview_data",
    "build_asset_allocation_series",
    "build_industry_timeseries",
    "build_asset_class_attribution",
    "build_period_transaction_timeseries",
    "build_page1_data",
]
