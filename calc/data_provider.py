"""
开发者A数据提供接口

本模块实现了将内部数据转换为符合《开发者A需提供的数据接口说明》的标准格式。
所有数据格式严格遵循文档要求，确保与开发者B的对接顺利。

主要接口：
1. get_daily_positions() - 每日持仓序列
2. get_position_details() - 期间持仓明细
3. get_industry_mapping() - 行业映射
4. get_transactions() - 交易记录
5. get_periods_config() - 统计区间配置
6. get_benchmark_daily_data() - 基准日度行情
7. get_benchmark_returns() - 基准收益率（日度和期间）
8. get_benchmark_industry_weights() - 基准行业权重
9. get_benchmark_industry_returns() - 基准行业收益率
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import os

from config import CSV_FILE, INITIAL_CAPITAL
from collections import defaultdict

from calc.position import (
    calculate_daily_asset_distribution,
    _read_csv,
    _parse_dates,
    _ts_code,
)

# Tushare token（如果需要）
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")


def get_daily_positions(
    csv_path: Optional[str] = None,
    initial_capital: Optional[float] = None,
    max_days: Optional[int] = None,
    include_positions: bool = False,
) -> List[Dict]:
    """
    获取每日持仓序列数据

    返回格式符合文档要求的 daily_positions 结构：
    - date: YYYY-MM-DD
    - total_assets: 总资产（万元）
    - stock_value: 股票市值（万元）
    - fund_value: 基金市值（万元，当前为0）
    - repo_value: 逆回购市值（万元，当前为0）
    - positions: 当日持仓列表

    参数:
        csv_path: 交割单CSV路径
        initial_capital: 初始资金（元）
        max_days: 仅计算前N天
        include_positions: 是否包含详细持仓列表（计算密集，默认False）

    返回:
        List[Dict]: 每日持仓数据列表
    """
    # 获取资产分布数据
    asset_df = calculate_daily_asset_distribution(csv_path, initial_capital, max_days)

    # 如果需要持仓明细，计算每日持仓
    daily_holdings = {}
    if include_positions:
        daily_holdings = _calculate_daily_holdings(csv_path, max_days)

    # 转换为万元
    result = []
    for date_str, row in asset_df.iterrows():
        total_assets_wan = row["total_assets"] / 10000  # 转为万元
        stock_value_wan = total_assets_wan * row["stock_pct"] / 100
        cash_value_wan = total_assets_wan * row["cash_pct"] / 100

        # 获取当日持仓明细
        positions = []
        if include_positions and date_str in daily_holdings:
            for code, holding in daily_holdings[date_str].items():
                ts_code = f"{code}.SH" if code.startswith("6") else f"{code}.SZ"
                positions.append(
                    {
                        "code": ts_code,
                        "name": holding.get("name", ""),
                        "market_value": round(
                            float(holding.get("market_value", 0.0)) / 10000, 4
                        ),
                        "previous_market_value": round(
                            float(holding.get("previous_market_value", 0.0)) / 10000, 4
                        ),
                        "begin_market_value": round(
                            float(holding.get("begin_market_value", 0.0)) / 10000, 4
                        ),
                        "net_cash_flow": round(
                            float(holding.get("net_cash_flow", 0.0)) / 10000, 4
                        ),
                        "quantity": int(holding.get("quantity", 0) or 0),
                        "avg_cost": round(
                            float(holding.get("avg_cost", 0.0) or 0.0), 4
                        ),
                        "close_price": round(
                            float(holding.get("close_price", 0.0) or 0.0), 4
                        ),
                    }
                )

        daily_data = {
            "date": date_str,
            "total_assets": round(total_assets_wan, 4),
            "stock_value": round(stock_value_wan, 4),
            "fund_value": 0.0,  # 当前策略只有股票
            "repo_value": 0.0,  # 当前策略只有股票
            "cash_value": round(cash_value_wan, 4),  # 额外提供现金
            "positions": positions,
        }
        result.append(daily_data)

    return result


def _calculate_daily_holdings(
    csv_path: Optional[str] = None,
    max_days: Optional[int] = None,
) -> Dict[str, Dict[str, Dict]]:
    """
    计算每日持仓明细（含期初、市值、净现金流等信息）

    返回:
        Dict: {
            日期: {
                股票代码(6位字符串): {
                    quantity: 持股数量,
                    avg_cost: 持仓平均成本(元),
                    market_value: 当日持仓市值(按成本价计算)(元),
                    previous_market_value: 前一交易日持仓市值(元),
                    net_cash_flow: 当日净现金流(元，买入为正),
                    close_price: 持仓成本价(元),
                    name: 股票名称
                }
            }
        }
    """
    df = _read_csv(csv_path or CSV_FILE)
    if df.empty:
        return {}

    df = _parse_dates(df)
    df = df.sort_values(["buy_dt", "sell_dt"])

    # 规范代码为6位字符串
    if "code" not in df.columns:
        return {}
    df["code"] = df["code"].astype(str).str.zfill(6)

    buy_dates = df["buy_dt"].dropna()
    sell_dates = df["sell_dt"].dropna()

    if buy_dates.empty and sell_dates.empty:
        return {}

    start_date = min(
        [
            d
            for d in [
                buy_dates.min() if not buy_dates.empty else None,
                sell_dates.min() if not sell_dates.empty else None,
            ]
            if d is not None
        ]
    )
    end_date = max(
        [
            d
            for d in [
                buy_dates.max() if not buy_dates.empty else None,
                sell_dates.max() if not sell_dates.empty else None,
            ]
            if d is not None
        ]
    )

    if start_date is None or end_date is None:
        return {}

    date_index = pd.date_range(
        start=start_date.normalize(), end=end_date.normalize(), freq="D"
    )
    if isinstance(max_days, int) and max_days > 0:
        date_index = date_index[:max_days]

    date_strs = [d.strftime("%Y-%m-%d") for d in date_index]
    if not date_strs:
        return {}

    codes = sorted(df["code"].dropna().unique().tolist())
    
    # 不再需要获取收盘价，直接使用持仓成本计算市值

    buy_df = df[df["buy_dt"].notna()].copy()
    buy_df["date"] = buy_df["buy_dt"].dt.strftime("%Y-%m-%d")
    sell_df = df[df["sell_dt"].notna()].copy()
    sell_df["date"] = sell_df["sell_dt"].dt.strftime("%Y-%m-%d")

    buy_groups = dict(tuple(buy_df.groupby("date"))) if not buy_df.empty else {}
    sell_groups = dict(tuple(sell_df.groupby("date"))) if not sell_df.empty else {}

    holdings: Dict[str, Dict[str, Any]] = {}
    name_map: Dict[str, str] = {}
    prev_market_values: Dict[str, float] = {code: 0.0 for code in codes}
    avg_cost_map: Dict[str, float] = {code: 0.0 for code in codes}

    daily_holdings: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for date_str in date_strs:
        daily_net_cash = defaultdict(float)

        # 处理买入
        if date_str in buy_groups:
            for _, trade in buy_groups[date_str].iterrows():
                code = str(trade.get("code", "")).zfill(6)
                if not code:
                    continue
                quantity_raw = trade.get("buy_number", 0)
                if pd.isna(quantity_raw):
                    quantity = 0
                else:
                    quantity = int(float(quantity_raw))
                cost = float(trade.get("buy_money", 0.0) or 0.0)
                name = trade.get("name", "") or ""

                if quantity <= 0:
                    continue

                entry = holdings.setdefault(
                    code, {"quantity": 0, "total_cost": 0.0, "name": name}
                )
                if not entry.get("name") and name:
                    entry["name"] = name
                entry["quantity"] += quantity
                entry["total_cost"] += cost

                daily_net_cash[code] += cost
                name_map[code] = entry["name"]

        # 处理卖出
        if date_str in sell_groups:
            for _, trade in sell_groups[date_str].iterrows():
                code = str(trade.get("code", "")).zfill(6)
                if not code:
                    continue
                quantity_raw = trade.get("sell_number", 0)
                if pd.isna(quantity_raw):
                    quantity = 0
                else:
                    quantity = int(float(quantity_raw))
                amount = float(trade.get("sell_money", 0.0) or 0.0)
                name = trade.get("name", "") or ""

                if quantity <= 0:
                    continue

                entry = holdings.setdefault(
                    code, {"quantity": 0, "total_cost": 0.0, "name": name}
                )
                if not entry.get("name") and name:
                    entry["name"] = name

                current_qty = entry["quantity"]
                if current_qty > 0:
                    avg_cost = entry["total_cost"] / current_qty if current_qty else 0.0
                    reduction = avg_cost * quantity
                    entry["total_cost"] = max(entry["total_cost"] - reduction, 0.0)
                entry["quantity"] = max(current_qty - quantity, 0)

                daily_net_cash[code] -= amount
                name_map[code] = entry["name"]

        snapshot_codes = {
            code for code, value in prev_market_values.items() if value > 0
        }
        snapshot_codes.update(holdings.keys())
        snapshot_codes.update(
            code for code, flow in daily_net_cash.items() if abs(flow) > 1e-8
        )

        if not snapshot_codes:
            # 即使没有持仓，也需要清空前值以免延续到下一日
            for code in prev_market_values.keys():
                prev_market_values[code] = 0.0
            continue

        day_snapshot: Dict[str, Dict[str, Any]] = {}

        for code in snapshot_codes:
            entry = holdings.get(
                code, {"quantity": 0, "total_cost": 0.0, "name": name_map.get(code, "")}
            )
            quantity = int(entry.get("quantity", 0) or 0)
            total_cost = float(entry.get("total_cost", 0.0) or 0.0)
            name = entry.get("name") or name_map.get(code, "") or ""

            avg_cost = (
                total_cost / quantity if quantity > 0 else avg_cost_map.get(code, 0.0)
            )
            avg_cost_map[code] = avg_cost

            # 直接使用持仓成本作为价格，不再使用收盘价
            price = avg_cost

            market_value = float(quantity) * price
            previous_value = prev_market_values.get(code, 0.0)
            net_cash = daily_net_cash.get(code, 0.0)

            day_snapshot[code] = {
                "quantity": quantity,
                "avg_cost": avg_cost,
                "market_value": market_value,
                "previous_market_value": previous_value,
                "begin_market_value": previous_value,
                "net_cash_flow": net_cash,
                "close_price": price,  # 保持字段名，但值为持仓成本
                "name": name,
            }

        # 更新前一日市值
        for code in prev_market_values.keys():
            prev_market_values[code] = day_snapshot.get(code, {}).get(
                "market_value", 0.0
            )

        daily_holdings[date_str] = day_snapshot

    return daily_holdings


def get_position_details(
    csv_path: Optional[str] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
) -> Dict:
    """
    获取期间持仓明细和汇总值

    返回格式符合文档要求的 position_details 结构。

    参数:
        csv_path: 交割单CSV路径
        period_start: 统计期间开始日期 (YYYY-MM-DD)
        period_end: 统计期间结束日期 (YYYY-MM-DD)

    返回:
        Dict: 包含 total_assets、total_profit、position_details
    """
    # 获取每日资产数据（不需要详细持仓）
    daily_data = get_daily_positions(csv_path=csv_path, include_positions=False)

    if not daily_data:
        return {"total_assets": 0.0, "total_profit": 0.0, "position_details": []}

    # 如果没有指定期间，使用全部数据
    if not period_start:
        period_start = daily_data[0]["date"]
    if not period_end:
        period_end = daily_data[-1]["date"]

    # 筛选期间内的数据
    period_data = [d for d in daily_data if period_start <= d["date"] <= period_end]

    if not period_data:
        return {"total_assets": 0.0, "total_profit": 0.0, "position_details": []}

    # 获取期初和期末数据
    start_day = period_data[0]
    end_day = period_data[-1]

    # 计算期间总收益
    start_assets = start_day["total_assets"]
    end_assets = end_day["total_assets"]
    total_profit = end_assets - start_assets

    # 获取期间内的交易记录
    transactions = get_transactions(
        csv_path=csv_path, period_start=period_start, period_end=period_end
    )

    # 按股票代码汇总交易数据
    stock_data: Dict[str, Dict[str, Any]] = {}
    for trans in transactions:
        ts_code = trans["code"]
        clean_code = ts_code.split(".")[0]
        entry = stock_data.setdefault(
            clean_code,
            {
                "code": clean_code,
                "ts_code": ts_code,
                "name": trans.get("name", ""),
                "buy_amount": 0.0,
                "sell_amount": 0.0,
                "buy_quantity": 0,
                "sell_quantity": 0,
            },
        )

        if not entry["name"] and trans.get("name"):
            entry["name"] = trans["name"]

        amount = trans["amount"] / 10000  # 转为万元
        quantity = trans["quantity"]

        if trans["direction"] == "买入":
            entry["buy_amount"] += amount
            entry["buy_quantity"] += quantity
        else:
            entry["sell_amount"] += amount
            entry["sell_quantity"] += quantity

    # 获取股票名称（从Tushare）
    if TUSHARE_TOKEN and stock_data:
        try:
            import tushare as ts

            ts.set_token(TUSHARE_TOKEN)
            pro = ts.pro_api()

            # 获取所有代码
            ts_codes = [
                item["ts_code"] for item in stock_data.values() if item.get("ts_code")
            ]

            # 批量查询股票名称
            batch_size = 300
            for i in range(0, len(ts_codes), batch_size):
                batch_codes = ts_codes[i : i + batch_size]
                try:
                    info = pro.stock_basic(
                        ts_code=",".join(batch_codes), fields="ts_code,name"
                    )
                    if info is not None and not info.empty:
                        for _, row in info.iterrows():
                            ts_code = row["ts_code"]
                            if pd.isna(ts_code):
                                continue
                            clean_code = ts_code.split(".")[0]
                            if clean_code in stock_data and pd.notna(row["name"]):
                                stock_data[clean_code]["name"] = row["name"]
                except:
                    pass
        except:
            pass

    # 基于每日持仓估算期初/期末市值与净现金流
    daily_holdings_all = _calculate_daily_holdings(csv_path=csv_path)
    period_index = pd.date_range(start=period_start, end=period_end, freq="D")
    period_dates = [d.strftime("%Y-%m-%d") for d in period_index]

    begin_values: Dict[str, float] = {}
    end_values: Dict[str, float] = {}
    cash_flow_map: Dict[str, float] = {}
    name_map: Dict[str, str] = {}

    for date_str in period_dates:
        day_holdings = daily_holdings_all.get(date_str)
        if not day_holdings:
            continue
        for code, info in day_holdings.items():
            name = info.get("name", "") or name_map.get(code, "")
            if name:
                name_map[code] = name

            previous_value = (
                float(info.get("previous_market_value", 0.0) or 0.0) / 10000
            )
            if code not in begin_values:
                begin_values[code] = previous_value

            market_value = float(info.get("market_value", 0.0) or 0.0) / 10000
            end_values[code] = market_value

            net_flow = float(info.get("net_cash_flow", 0.0) or 0.0) / 10000
            if abs(net_flow) > 1e-8:
                cash_flow_map[code] = cash_flow_map.get(code, 0.0) + net_flow

    transaction_map = {code: data for code, data in stock_data.items()}

    codes_set = (
        set(begin_values.keys())
        | set(end_values.keys())
        | set(cash_flow_map.keys())
        | set(transaction_map.keys())
    )

    position_details: List[Dict[str, Any]] = []
    for code in sorted(codes_set):
        trans_entry = transaction_map.get(code, {})
        ts_code = trans_entry.get("ts_code") or _ts_code(code)
        name = name_map.get(code) or trans_entry.get("name", "") or ""

        begin_value = begin_values.get(code, 0.0)
        end_value = end_values.get(code, 0.0)

        if code in cash_flow_map:
            net_flow = cash_flow_map[code]
        else:
            net_flow = trans_entry.get("buy_amount", 0.0) - trans_entry.get(
                "sell_amount", 0.0
            )

        profit_loss = end_value - begin_value - net_flow

        if abs(begin_value) < 1e-6 and abs(end_value) < 1e-6 and abs(net_flow) < 1e-6:
            continue

        position_details.append(
            {
                "code": ts_code,
                "name": name,
                "market_value": round(end_value, 4),
                "profit_loss": round(profit_loss, 4),
                "previous_market_value": round(begin_value, 4),
                "begin_market_value": round(begin_value, 4),
                "net_cash_flow": round(net_flow, 4),
            }
        )

    return {
        "total_assets": round(end_assets, 4),
        "total_profit": round(total_profit, 4),
        "position_details": position_details,
    }


def get_industry_mapping(csv_path: Optional[str] = None) -> Dict[str, str]:
    """
    获取行业映射

    返回格式: { "股票代码": "行业名称" }

    参数:
        csv_path: 交割单CSV路径

    返回:
        Dict: 股票代码到行业名称的映射
    """
    if not TUSHARE_TOKEN:
        return {}

    # 读取交割单获取所有股票代码
    df = _read_csv(csv_path or CSV_FILE)
    codes = sorted(df["code"].dropna().unique())

    # 转换为Tushare格式
    ts_codes = [
        f"{code}.SH" if code.startswith("6") else f"{code}.SZ" for code in codes
    ]

    # 从Tushare获取行业信息
    try:
        import tushare as ts

        ts.set_token(TUSHARE_TOKEN)
        pro = ts.pro_api()
    except ImportError:
        print("警告：未安装 tushare，无法获取行业映射")
        return {}

    industry_mapping = {}

    try:
        # 批量查询股票基本信息（每次最多300只）
        batch_size = 300
        for i in range(0, len(ts_codes), batch_size):
            batch_codes = ts_codes[i : i + batch_size]
            try:
                # 获取股票行业信息
                info = pro.stock_basic(
                    ts_code=",".join(batch_codes), fields="ts_code,industry"
                )
                if info is not None and not info.empty:
                    for _, row in info.iterrows():
                        industry = row["industry"]
                        industry_mapping[row["ts_code"]] = (
                            industry if pd.notna(industry) else "未分类"
                        )
            except Exception as e:
                print(f"  批次 {i//batch_size + 1} 查询失败: {e}")
                continue
    except Exception as e:
        print(f"获取行业映射失败: {e}")

    return industry_mapping


def get_transactions(
    csv_path: Optional[str] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
) -> List[Dict]:
    """
    获取交易记录

    返回格式符合文档要求的 transactions 结构：
    - date: YYYY-MM-DD
    - code: 股票代码
    - asset_class: 资产类别（"股票"）
    - direction: 交易方向（"买入"/"卖出"）
    - price: 成交价格（元）
    - quantity: 成交数量（股）
    - amount: 成交金额（元）

    参数:
        csv_path: 交割单CSV路径
        period_start: 开始日期
        period_end: 结束日期

    返回:
        List[Dict]: 交易记录列表
    """
    df = _read_csv(csv_path or CSV_FILE)
    df = _parse_dates(df)

    # 过滤日期范围
    if period_start:
        df = df[df["buy_dt"] >= period_start]
    if period_end:
        df = df[df["sell_dt"] <= period_end]

    transactions = []

    # 处理买入交易
    for idx, row in df.iterrows():
        if pd.notna(row.get("buy_date")):
            buy_money = pd.to_numeric(row.get("buy_money"), errors="coerce")
            buy_quantity = pd.to_numeric(
                row.get("buy_number"), errors="coerce"
            )  # 注意是buy_number
            buy_price = pd.to_numeric(row.get("buy_price"), errors="coerce")

            if pd.notna(buy_money) and pd.notna(buy_quantity):
                ts_code = (
                    f"{row['code']}.SH"
                    if row["code"].startswith("6")
                    else f"{row['code']}.SZ"
                )
                transactions.append(
                    {
                        "date": row["buy_date"],
                        "code": ts_code,
                        "name": row.get("name", ""),
                        "asset_class": "股票",
                        "direction": "买入",
                        "price": (
                            round(float(buy_price), 2) if pd.notna(buy_price) else 0.0
                        ),
                        "quantity": int(buy_quantity),
                        "amount": round(float(buy_money), 2),
                    }
                )

        # 处理卖出交易
        if pd.notna(row.get("sell_date")):
            sell_money = pd.to_numeric(row.get("sell_money"), errors="coerce")
            sell_quantity = pd.to_numeric(
                row.get("sell_number"), errors="coerce"
            )  # 注意是sell_number
            sell_price = pd.to_numeric(row.get("sell_price"), errors="coerce")

            if pd.notna(sell_money) and pd.notna(sell_quantity):
                ts_code = (
                    f"{row['code']}.SH"
                    if row["code"].startswith("6")
                    else f"{row['code']}.SZ"
                )
                transactions.append(
                    {
                        "date": row["sell_date"],
                        "code": ts_code,
                        "name": row.get("name", ""),
                        "asset_class": "股票",
                        "direction": "卖出",
                        "price": (
                            round(float(sell_price), 2) if pd.notna(sell_price) else 0.0
                        ),
                        "quantity": int(sell_quantity),
                        "amount": round(float(sell_money), 2),
                    }
                )

    # 按日期排序
    transactions.sort(key=lambda x: x["date"])

    return transactions


def get_periods_config() -> Dict[str, Tuple[str, str]]:
    """
    获取统计区间配置

    返回格式: { "统计期间": ("起始日", "结束日") }

    返回:
        Dict: 统计期间配置
    """
    # 从交割单读取日期范围
    from calc.utils import _read_csv_date_range

    try:
        min_date, max_date = _read_csv_date_range()
    except:
        min_date, max_date = "2015-01-05", "2025-11-05"

    # 计算常用统计期间
    end_date = pd.to_datetime(max_date)

    periods = {
        "成立以来": (min_date, max_date),
        "近一年": ((end_date - pd.DateOffset(years=1)).strftime("%Y-%m-%d"), max_date),
        "近六个月": (
            (end_date - pd.DateOffset(months=6)).strftime("%Y-%m-%d"),
            max_date,
        ),
        "近三个月": (
            (end_date - pd.DateOffset(months=3)).strftime("%Y-%m-%d"),
            max_date,
        ),
        "近一个月": (
            (end_date - pd.DateOffset(months=1)).strftime("%Y-%m-%d"),
            max_date,
        ),
    }

    return periods


def export_all_data(
    csv_path: Optional[str] = None,
    output_dir: str = "output",
    max_days: Optional[int] = None,
    include_positions: bool = False,
    include_benchmark: bool = True,
    index_code: str = "000300.SH",
) -> Dict[str, str]:
    """
    导出所有数据到JSON文件

    参数:
        csv_path: 交割单CSV路径
        output_dir: 输出目录
        max_days: 仅处理前N天
        include_positions: 是否包含详细持仓列表（计算密集）
        include_benchmark: 是否包含基准数据（需要 tushare）
        index_code: 基准指数代码（默认沪深300）

    返回:
        Dict: 各文件的输出路径
    """
    import json
    import os

    os.makedirs(output_dir, exist_ok=True)

    output_files = {}

    # 1. 导出每日持仓序列
    print("生成每日持仓序列...")
    daily_positions = get_daily_positions(
        csv_path, max_days=max_days, include_positions=include_positions
    )
    daily_file = os.path.join(output_dir, "daily_positions.json")
    with open(daily_file, "w", encoding="utf-8") as f:
        json.dump(daily_positions, f, ensure_ascii=False, indent=2)
    output_files["daily_positions"] = daily_file
    print(f"  ✓ 已导出 {len(daily_positions)} 天数据到 {daily_file}")

    # 2. 导出交易记录
    print("生成交易记录...")
    transactions = get_transactions(csv_path)
    trans_file = os.path.join(output_dir, "transactions.json")
    with open(trans_file, "w", encoding="utf-8") as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)
    output_files["transactions"] = trans_file
    print(f"  ✓ 已导出 {len(transactions)} 条交易到 {trans_file}")

    # 3. 导出行业映射
    print("生成行业映射...")
    industry_mapping = get_industry_mapping(csv_path)
    industry_file = os.path.join(output_dir, "industry_mapping.json")
    with open(industry_file, "w", encoding="utf-8") as f:
        json.dump(industry_mapping, f, ensure_ascii=False, indent=2)
    output_files["industry_mapping"] = industry_file
    print(f"  ✓ 已导出 {len(industry_mapping)} 只股票行业信息到 {industry_file}")

    # 4. 导出统计区间配置
    print("生成统计区间配置...")
    periods = get_periods_config()
    periods_file = os.path.join(output_dir, "periods_config.json")
    with open(periods_file, "w", encoding="utf-8") as f:
        json.dump(periods, f, ensure_ascii=False, indent=2)
    output_files["periods_config"] = periods_file
    print(f"  ✓ 已导出统计区间配置到 {periods_file}")

    # 5. 导出基准数据（可选）
    if include_benchmark:
        try:
            print(f"生成基准数据（{index_code}）...")

            # 5.1 基准日度行情
            benchmark_daily = get_benchmark_daily_data(
                index_code=index_code, csv_path=csv_path
            )
            benchmark_daily_file = os.path.join(output_dir, "benchmark_daily_data.csv")
            benchmark_daily.to_csv(benchmark_daily_file, index=False)
            output_files["benchmark_daily_data"] = benchmark_daily_file
            print(
                f"  ✓ 已导出 {len(benchmark_daily)} 天基准行情到 {benchmark_daily_file}"
            )

            # 5.2 基准收益率
            benchmark_returns = get_benchmark_returns(
                index_code=index_code, csv_path=csv_path, periods=periods
            )
            benchmark_returns_file = os.path.join(output_dir, "benchmark_returns.json")
            with open(benchmark_returns_file, "w", encoding="utf-8") as f:
                json.dump(benchmark_returns, f, ensure_ascii=False, indent=2)
            output_files["benchmark_returns"] = benchmark_returns_file
            print(f"  ✓ 已导出基准收益率到 {benchmark_returns_file}")

            # 5.3 基准行业权重
            try:
                # 使用交割单最后一天的日期
                df_csv = _read_csv(csv_path or CSV_FILE)
                df_dates = _parse_dates(df_csv)
                all_dates = []
                if "buy_date" in df_dates.columns:
                    all_dates.extend(df_dates["buy_date"].dropna().tolist())
                if "sell_date" in df_dates.columns:
                    all_dates.extend(df_dates["sell_date"].dropna().tolist())
                last_date = max(
                    [
                        d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
                        for d in all_dates
                    ]
                )

                industry_weights = get_benchmark_industry_weights(
                    index_code=index_code, date=last_date, csv_path=csv_path
                )
                industry_weights_file = os.path.join(
                    output_dir, "benchmark_industry_weights.json"
                )
                with open(industry_weights_file, "w", encoding="utf-8") as f:
                    json.dump(industry_weights, f, ensure_ascii=False, indent=2)
                output_files["benchmark_industry_weights"] = industry_weights_file
                print(f"  ✓ 已导出基准行业权重到 {industry_weights_file}")
            except Exception as e:
                print(f"  ⚠️  基准行业权重导出失败: {e}")

            # 5.4 基准行业收益率（仅导出"成立以来"期间）
            try:
                period_start, period_end = periods.get("成立以来", (None, None))
                if period_start and period_end:
                    industry_returns = get_benchmark_industry_returns(
                        index_code=index_code,
                        start_date=period_start,
                        end_date=period_end,
                        csv_path=csv_path,
                    )
                    industry_returns_file = os.path.join(
                        output_dir, "benchmark_industry_returns.json"
                    )
                    with open(industry_returns_file, "w", encoding="utf-8") as f:
                        json.dump(industry_returns, f, ensure_ascii=False, indent=2)
                    output_files["benchmark_industry_returns"] = industry_returns_file
                    print(f"  ✓ 已导出基准行业收益率到 {industry_returns_file}")
            except Exception as e:
                print(f"  ⚠️  基准行业收益率导出失败: {e}")

        except Exception as e:
            print(f"  ⚠️  基准数据导出失败: {e}")
            print(f"     （可能需要设置 TUSHARE_TOKEN 环境变量）")

    return output_files


def get_benchmark_daily_data(
    index_code: str = "000300.SH",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    csv_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    获取基准指数的日度行情数据

    符合《开发者A提供数据.md》第7节要求：
    - 返回 DataFrame，包含 trade_date 和 close 列
    - trade_date 格式为 YYYYMMDD
    - close 为收盘价

    参数:
        index_code: 指数代码（默认沪深300: 000300.SH）
        start_date: 开始日期 YYYY-MM-DD（默认使用交割单起始日期）
        end_date: 结束日期 YYYY-MM-DD（默认使用交割单结束日期）
        csv_path: 交割单路径（用于自动确定日期范围）

    返回:
        DataFrame 包含列:
        - trade_date: 交易日期 YYYYMMDD（字符串）
        - close: 收盘价（浮点数）

    示例:
        >>> df = get_benchmark_daily_data("000300.SH")
        >>> print(df.head())
           trade_date    close
        0    20150105  3350.12
        1    20150106  3400.23
    """
    try:
        import tushare as ts
    except ImportError:
        raise RuntimeError("需要安装 tushare: pip install tushare")

    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        raise RuntimeError("请设置环境变量 TUSHARE_TOKEN")

    # 如果未指定日期范围，从交割单获取
    if not start_date or not end_date:
        df_csv = _read_csv(csv_path or CSV_FILE)
        df_dates = _parse_dates(df_csv)

        # 从 buy_date 和 sell_date 列获取所有日期
        all_dates = []
        if "buy_date" in df_dates.columns:
            all_dates.extend(df_dates["buy_date"].dropna().tolist())
        if "sell_date" in df_dates.columns:
            all_dates.extend(df_dates["sell_date"].dropna().tolist())

        if all_dates:
            # 转换为字符串格式
            dates_str = [
                d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
                for d in all_dates
            ]
            dates_sorted = sorted(dates_str)
            start_date = start_date or dates_sorted[0]
            end_date = end_date or dates_sorted[-1]
        else:
            raise ValueError(
                "无法从交割单确定日期范围，请手动指定 start_date 和 end_date"
            )

    # 转换为 YYYYMMDD 格式
    s = start_date.replace("-", "")
    e = end_date.replace("-", "")

    # 调用 tushare API
    ts.set_token(token)
    pro = ts.pro_api()

    df = pro.index_daily(ts_code=index_code, start_date=s, end_date=e)
    if df is None or df.empty:
        raise ValueError(f"未获取到指数数据: {index_code} {start_date}~{end_date}")

    # 返回标准格式（trade_date 保持 YYYYMMDD，close 为收盘价）
    result = df[["trade_date", "close"]].copy()
    result = result.sort_values("trade_date").reset_index(drop=True)

    return result


def get_benchmark_returns(
    index_code: str = "000300.SH",
    csv_path: Optional[str] = None,
    periods: Optional[Dict[str, Tuple[str, str]]] = None,
) -> Dict:
    """
    获取基准指数的收益率数据

    符合《开发者A提供数据.md》第7节要求，返回：
    1. benchmark_daily_returns: 日度收益率列表（与产品日收益对齐）
    2. benchmark_period_returns: 各统计期间收益率字典

    参数:
        index_code: 指数代码（默认沪深300）
        csv_path: 交割单路径
        periods: 统计区间配置（默认使用 get_periods_config()）

    返回:
        字典包含:
        {
            "daily_returns": [0.012, -0.008, ...],  # 日度收益率（小数）
            "period_returns": {                      # 期间收益率（百分比）
                "成立以来": 125.6,
                "近一年": 15.3,
                "近六个月": 8.2,
                ...
            },
            "daily_dates": ["2015-01-05", ...],     # 对应的日期
            "index_code": "000300.SH"
        }

    示例:
        >>> returns = get_benchmark_returns()
        >>> print(f"日度收益率样本: {returns['daily_returns'][:3]}")
        >>> print(f"近一年收益: {returns['period_returns']['近一年']}%")
    """
    # 获取日度行情
    df_daily = get_benchmark_daily_data(index_code=index_code, csv_path=csv_path)

    # 计算日度收益率
    df_daily["date"] = pd.to_datetime(df_daily["trade_date"]).dt.strftime("%Y-%m-%d")
    df_daily = df_daily.sort_values("date").reset_index(drop=True)
    df_daily["return"] = df_daily["close"].pct_change()

    # 日度收益率列表（小数格式）
    daily_returns = df_daily["return"].fillna(0.0).tolist()
    daily_dates = df_daily["date"].tolist()

    # 计算期间收益率
    if periods is None:
        periods = get_periods_config()

    period_returns = {}
    price_dict = dict(zip(df_daily["date"], df_daily["close"]))

    def get_close(date: str) -> Optional[float]:
        """获取指定日期或之前最近的收盘价"""
        if date in price_dict:
            return price_dict[date]
        # 找最近的前一个交易日
        dates = [d for d in price_dict.keys() if d <= date]
        if dates:
            return price_dict[max(dates)]
        return None

    for period_name, (start, end) in periods.items():
        start_close = get_close(start)
        end_close = get_close(end)

        if start_close and end_close and start_close > 0:
            ret_pct = round((end_close / start_close - 1.0) * 100.0, 2)
            period_returns[period_name] = ret_pct
        else:
            period_returns[period_name] = None

    return {
        "daily_returns": daily_returns,
        "period_returns": period_returns,
        "daily_dates": daily_dates,
        "index_code": index_code,
    }


def get_benchmark_industry_weights(
    index_code: str = "000300.SH",
    date: Optional[str] = None,
    csv_path: Optional[str] = None,
) -> Dict[str, float]:
    """
    获取基准指数的行业权重分布

    符合《开发者A提供数据.md》第4节要求。
    通过获取指数成分股及其权重，结合股票行业映射，计算各行业的权重占比。

    参数:
        index_code: 指数代码（默认沪深300）
        date: 查询日期 YYYY-MM-DD（默认最近交易日）
        csv_path: 交割单路径（用于获取默认日期）

    返回:
        Dict[str, float]: {"行业名称": 权重%}
        例如: {"食品饮料": 5.2, "银行": 12.3, ...}

    示例:
        >>> weights = get_benchmark_industry_weights("000300.SH", "2024-11-01")
        >>> print(weights)
        {'银行': 12.5, '食品饮料': 5.8, '非银金融': 8.3, ...}

    注意:
        - 需要 TUSHARE_TOKEN 环境变量
        - 权重已按行业聚合
        - 未分类股票归入"其他"
    """
    try:
        import tushare as ts
    except ImportError:
        raise RuntimeError("需要安装 tushare: pip install tushare")

    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        raise RuntimeError("请设置环境变量 TUSHARE_TOKEN")

    # 确定查询日期
    if not date:
        df_csv = _read_csv(csv_path or CSV_FILE)
        df_dates = _parse_dates(df_csv)

        all_dates = []
        if "buy_date" in df_dates.columns:
            all_dates.extend(df_dates["buy_date"].dropna().tolist())
        if "sell_date" in df_dates.columns:
            all_dates.extend(df_dates["sell_date"].dropna().tolist())

        if all_dates:
            dates_str = [
                d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
                for d in all_dates
            ]
            date = max(dates_str)
        else:
            raise ValueError("无法从交割单确定日期，请手动指定 date 参数")

    # 转换为 YYYYMMDD
    query_date = date.replace("-", "")

    # 获取指数成分股权重
    ts.set_token(token)
    pro = ts.pro_api()

    df_weight = pro.index_weight(index_code=index_code, trade_date=query_date)
    if df_weight is None or df_weight.empty:
        raise ValueError(f"未获取到指数成分权重: {index_code} {date}")

    # 获取行业映射
    industry_map = get_industry_mapping(csv_path)

    # 计算行业权重
    industry_weights = {}
    total_weight = 0.0
    unmapped_weight = 0.0

    for _, row in df_weight.iterrows():
        code = row["con_code"]  # 成分股代码
        weight = float(row["weight"])  # 权重

        # 查找行业
        industry = industry_map.get(code, "其他")

        if industry == "其他" or industry == "未分类":
            unmapped_weight += weight
        else:
            industry_weights[industry] = industry_weights.get(industry, 0.0) + weight

        total_weight += weight

    # 添加未分类权重
    if unmapped_weight > 0:
        industry_weights["其他"] = unmapped_weight

    # 四舍五入
    industry_weights = {k: round(v, 2) for k, v in industry_weights.items()}

    return industry_weights


def get_benchmark_industry_returns(
    index_code: str = "000300.SH",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    csv_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    获取基准指数各行业的期间收益率

    符合《开发者A提供数据.md》第4节要求。
    通过计算各行业成分股的加权平均收益率，得到行业层面的收益。

    参数:
        index_code: 指数代码（默认沪深300）
        start_date: 开始日期 YYYY-MM-DD（默认交割单起始日期）
        end_date: 结束日期 YYYY-MM-DD（默认交割单结束日期）
        csv_path: 交割单路径

    返回:
        Dict[str, float]: {"行业名称": 收益率（小数）}
        例如: {"食品饮料": 0.125, "银行": -0.023, ...}
        注意：返回小数格式（0.125 = 12.5%）

    示例:
        >>> returns = get_benchmark_industry_returns(
        ...     "000300.SH", "2024-01-01", "2024-12-31"
        ... )
        >>> print({k: f"{v*100:.2f}%" for k, v in returns.items()})
        {'银行': '-2.3%', '食品饮料': '12.5%', ...}

    注意:
        - 需要 TUSHARE_TOKEN 环境变量
        - 收益率为小数格式（符合文档要求）
        - 基于成分股权重计算加权平均收益
    """
    try:
        import tushare as ts
    except ImportError:
        raise RuntimeError("需要安装 tushare: pip install tushare")

    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        raise RuntimeError("请设置环境变量 TUSHARE_TOKEN")

    # 确定日期范围
    if not start_date or not end_date:
        df_csv = _read_csv(csv_path or CSV_FILE)
        df_dates = _parse_dates(df_csv)

        all_dates = []
        if "buy_date" in df_dates.columns:
            all_dates.extend(df_dates["buy_date"].dropna().tolist())
        if "sell_date" in df_dates.columns:
            all_dates.extend(df_dates["sell_date"].dropna().tolist())

        if all_dates:
            dates_str = [
                d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
                for d in all_dates
            ]
            dates_sorted = sorted(dates_str)
            start_date = start_date or dates_sorted[0]
            end_date = end_date or dates_sorted[-1]
        else:
            raise ValueError("无法从交割单确定日期范围")

    # 转换为 YYYYMMDD
    s = start_date.replace("-", "")
    e = end_date.replace("-", "")

    # 获取期末的成分股权重
    ts.set_token(token)
    pro = ts.pro_api()

    df_weight = pro.index_weight(index_code=index_code, trade_date=e)
    if df_weight is None or df_weight.empty:
        # 尝试获取最近一个交易日的权重
        df_daily = pro.index_daily(ts_code=index_code, start_date=e, end_date=e)
        if df_daily.empty:
            raise ValueError(f"未获取到指数数据: {index_code} {end_date}")
        # 向前查找最近的权重数据
        for i in range(30):  # 最多回溯30天
            check_date = (
                datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=i)
            ).strftime("%Y%m%d")
            df_weight = pro.index_weight(index_code=index_code, trade_date=check_date)
            if not df_weight.empty:
                break
        if df_weight.empty:
            raise ValueError(f"未找到有效的成分股权重数据: {index_code}")

    # 获取行业映射
    industry_map = get_industry_mapping(csv_path)

    # 聚合器
    industry_total_weights: Dict[str, float] = defaultdict(float)
    period_weighted_returns: Dict[str, float] = defaultdict(float)
    daily_weighted_returns: Dict[str, Dict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )

    unique_codes = df_weight["con_code"].dropna().unique().tolist()

    for code in unique_codes:
        weight_rows = df_weight[df_weight["con_code"] == code]
        if weight_rows.empty:
            continue
        weight = float(weight_rows.iloc[0]["weight"])
        if weight <= 0:
            continue

        industry = industry_map.get(code, "其他")
        industry_total_weights[industry] += weight

        try:
            df_stock = pro.daily(ts_code=code, start_date=s, end_date=e)
        except Exception:
            continue

        if df_stock is None or df_stock.empty:
            continue

        df_stock = df_stock.sort_values("trade_date")
        df_stock["pct_change"] = df_stock["close"].pct_change()

        start_close = df_stock.iloc[0]["close"]
        end_close = df_stock.iloc[-1]["close"]
        if start_close > 0:
            period_return = end_close / start_close - 1.0
            period_weighted_returns[industry] += period_return * weight

        for _, row in df_stock.iterrows():
            daily_ret = row.get("pct_change")
            if pd.isna(daily_ret):
                continue
            trade_date = row["trade_date"]
            try:
                date_str = datetime.strptime(trade_date, "%Y%m%d").strftime("%Y-%m-%d")
            except ValueError:
                date_str = trade_date
            daily_weighted_returns[date_str][industry] += float(daily_ret) * weight

    period_returns: Dict[str, float] = {}
    for industry, weighted_value in period_weighted_returns.items():
        total_weight = industry_total_weights.get(industry, 0.0)
        if total_weight > 0:
            period_returns[industry] = round(weighted_value / total_weight, 4)

    daily_returns: Dict[str, Dict[str, float]] = {}
    for date in sorted(daily_weighted_returns.keys()):
        industry_values: Dict[str, float] = {}
        for industry, weighted_value in daily_weighted_returns[date].items():
            total_weight = industry_total_weights.get(industry, 0.0)
            if total_weight > 0:
                industry_values[industry] = round(weighted_value / total_weight, 6)
        if industry_values:
            daily_returns[date] = industry_values

    return {
        "period_returns": period_returns,
        "daily_returns": daily_returns,
    }
