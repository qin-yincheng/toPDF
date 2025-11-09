"""PDF 数据格式化函数。"""

from typing import Any, Dict, List


def _fmt(value: Any) -> str:
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def format_metrics_for_pdf(metrics: Dict[str, Any]) -> List[List[str]]:
    table = [["指标名称", "数值"]]
    period_return = _fmt(metrics.get("period_return", 0.0))
    annualized_return = _fmt(metrics.get("annualized_return", 0.0))
    table.append(
        [
            "期间产品收益率",
            f"{period_return}% (年化 {annualized_return}%)",
        ]
    )
    table.append(["最大回撤", f"{_fmt(metrics.get('max_drawdown', 0.0))}%"])
    table.append(["波动率", f"{_fmt(metrics.get('volatility', 0.0))}%"])
    table.append(["夏普比率", _fmt(metrics.get("sharpe_ratio", 0.0))])
    table.append(["卡玛比率", _fmt(metrics.get("calmar_ratio", 0.0))])
    active_return = _fmt(metrics.get("active_return", 0.0))
    annualized_active_return = _fmt(metrics.get("annualized_active_return", 0.0))
    table.append(
        [
            "主动收益",
            f"{active_return}% (年化 {annualized_active_return}%)",
        ]
    )
    table.append(["β值", _fmt(metrics.get("beta", 0.0))])
    table.append(
        [
            "跟踪误差",
            f"{_fmt(metrics.get('tracking_error', 0.0))}%",
        ]
    )
    table.append(
        [
            "下行波动率",
            f"{_fmt(metrics.get('downside_volatility', 0.0))}%",
        ]
    )
    table.append(["索提诺比率", _fmt(metrics.get("sortino_ratio", 0.0))])
    table.append(["信息比率", _fmt(metrics.get("information_ratio", 0.0))])
    max_return_date = metrics.get("max_return_date", "")
    table.append(
        [
            "单日最大收益",
            f"{_fmt(metrics.get('max_daily_return', 0.0))}% ({max_return_date})",
        ]
    )
    max_loss_date = metrics.get("max_loss_date", "")
    table.append(
        [
            "单日最大亏损",
            f"{_fmt(metrics.get('max_daily_loss', 0.0))}% ({max_loss_date})",
        ]
    )
    table.append(
        [
            "周胜率",
            f"{_fmt(metrics.get('weekly_win_rate', 0.0))}%",
        ]
    )
    table.append(
        [
            "月胜率",
            f"{_fmt(metrics.get('monthly_win_rate', 0.0))}%",
        ]
    )
    table.append(
        [
            "最大回撤修复期",
            f"{metrics.get('recovery_period', 0)}天 ({metrics.get('recovery_date', '')})",
        ]
    )
    table.append(["收益风险特征", metrics.get("risk_characteristic", "")])
    return table


def format_period_metrics_for_pdf(
    period_metrics: Dict[str, Dict[str, Any]],
) -> List[List[str]]:
    header = ["指标"] + list(period_metrics.keys())
    rows = [header]
    items = [
        ("年化收益率", "annualized_return", True),
        ("年化波动率", "volatility", True),
        ("跟踪误差", "tracking_error", True),
        ("下行波动率", "downside_volatility", True),
        ("夏普比率", "sharpe_ratio", False),
        ("索提诺比率", "sortino_ratio", False),
        ("信息比率", "information_ratio", False),
        ("最大回撤", "max_drawdown", True),
        ("卡玛比率", "calmar_ratio", False),
    ]
    for title, key, is_percent in items:
        row = [title]
        for period in period_metrics:
            value = period_metrics[period].get(key)
            if value is None:
                row.append("-")
            else:
                string_value = (
                    f"{float(value):.2f}" if isinstance(value, (int, float)) else "0.00"
                )
                row.append(f"{string_value}%" if is_percent else string_value)
        rows.append(row)
    return rows


def format_industry_attribution_for_pdf(
    industry_attribution: List[Dict[str, Any]],
    top_n: int = 10,
) -> Dict[str, List[List[str]]]:
    """按收益额输出行业归因的盈利和亏损表。"""
    header = [
        "行业",
        "权重占净值比(%)",
        "贡献度(%)",
        "收益额(万元)",
        "选择收益(%)",
        "配置收益(%)",
        "交互收益(%)",
    ]
    sorted_items = sorted(
        industry_attribution, key=lambda item: item["profit"], reverse=True
    )
    profit_table = [header]
    for item in sorted_items[:top_n]:
        profit_table.append(
            [
                item["industry"],
                f"{item['weight']:.2f}",
                f"{item['contribution']:.2f}",
                f"{item['profit']:.2f}",
                f"{item['selection_return']:.2f}",
                f"{item['allocation_return']:.2f}",
                f"{item.get('interaction_return', 0.0):.2f}",
            ]
        )
    loss_table = [header]
    for item in sorted(industry_attribution, key=lambda entry: entry["profit"])[:top_n]:
        loss_table.append(
            [
                item["industry"],
                f"{item['weight']:.2f}",
                f"{item['contribution']:.2f}",
                f"{item['profit']:.2f}",
                f"{item['selection_return']:.2f}",
                f"{item['allocation_return']:.2f}",
                f"{item.get('interaction_return', 0.0):.2f}",
            ]
        )
    return {"profit_table": profit_table, "loss_table": loss_table}


def format_stock_performance_for_pdf(
    stock_performance: List[Dict[str, Any]],
    top_n: int = 10,
) -> Dict[str, List[List[str]]]:
    """输出股票绩效的盈利与亏损表。"""
    header = ["股票代码", "股票名称", "权重占净值比(%)", "贡献度(%)", "收益额(万元)"]
    profit_table = [header]
    for item in stock_performance[:top_n]:
        profit_table.append(
            [
                item["code"],
                item["name"],
                f"{item['weight']:.2f}",
                f"{item['contribution']:.2f}",
                f"{item['profit']:.2f}",
            ]
        )
    loss_table = [header]
    for item in stock_performance[-top_n:]:
        loss_table.append(
            [
                item["code"],
                item["name"],
                f"{item['weight']:.2f}",
                f"{item['contribution']:.2f}",
                f"{item['profit']:.2f}",
            ]
        )
    return {"profit_table": profit_table, "loss_table": loss_table}


def format_position_nodes_for_pdf(
    position_nodes: List[Dict[str, Any]],
) -> List[List[str]]:
    """按顺序格式化持仓节点列表。"""
    table = [["持仓节点", "市值(万元)", "占比(%)"]]
    for item in position_nodes:
        table.append(
            [
                item["node"],
                f"{item['market_value']:.2f}",
                f"{item['percentage']:.2f}",
            ]
        )
    return table


def format_turnover_rates_for_pdf(
    turnover_rates: Dict[str, Dict[str, float]],
) -> List[List[str]]:
    """格式化各资产类别的换手率。"""
    if not turnover_rates:
        return [["资产分类"]]
    periods = list(next(iter(turnover_rates.values())).keys())
    table = [["资产分类"] + [f"{period}(%)" for period in periods]]
    for asset_class, values in turnover_rates.items():
        row = [asset_class]
        for period in periods:
            row.append(f"{values[period]:.2f}")
        table.append(row)
    return table


def format_trading_statistics_for_pdf(
    trading_stats: Dict[str, Dict[str, float]],
) -> List[List[str]]:
    """格式化各资产类别的交易金额。"""
    table = [["资产分类", "买入金额(万元)", "卖出金额(万元)"]]
    for asset_class, values in trading_stats.items():
        table.append(
            [
                asset_class,
                f"{values['buy_amount']:.2f}",
                f"{values['sell_amount']:.2f}",
            ]
        )
    return table
