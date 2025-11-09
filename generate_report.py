"""
生成完整的PDF报告

使用真实数据从 data_provider 获取数据，然后生成PDF报告
如果交割单.csv不存在，会自动从交割单.xlsx转换
"""

import os
from pathlib import Path

from calc.data_provider import (
    get_daily_positions,
    get_position_details,
    get_periods_config,
    get_transactions,
    get_industry_mapping,
    get_benchmark_daily_data,
    get_benchmark_returns,
    get_benchmark_industry_weights,
    get_benchmark_industry_returns,
)
from calc.report_bridge import build_page1_data
from pdf.pages1 import generate_page1
from config import DOCS_DIR


def convert_daily_positions_to_nav(daily_positions):
    """
    将 daily_positions 转换为 nav_data 格式

    daily_positions格式: [{"date": "2024-01-01", "total_assets": 1000.0, ...}]
    nav_data格式: [{"date": "2024-01-01", "nav": 1.0, "total_assets": 1000.0}]
    """
    if not daily_positions:
        return []

    # 使用第一天的资产作为基准
    initial_assets = daily_positions[0]["total_assets"]
    if initial_assets == 0:
        initial_assets = 1000.0  # 防止除零

    nav_data = []
    for pos in daily_positions:
        # 将numpy类型转换为Python原生类型
        total_assets = float(pos["total_assets"])
        nav = total_assets / initial_assets

        nav_data.append(
            {
                "date": pos["date"],
                "nav": nav,
                "total_assets": total_assets,
                "stock_value": float(pos.get("stock_value", 0)),
                "cash_value": float(pos.get("cash_value", 0)),
                "fund_value": float(pos.get("fund_value", 0)),
                "repo_value": float(pos.get("repo_value", 0)),
            }
        )

    return nav_data


def convert_benchmark_data_to_nav(benchmark_daily_data):
    """
    将基准日度数据转换为 nav_data 格式

    参数:
        benchmark_daily_data: DataFrame with columns ['trade_date', 'close']

    返回:
        List[Dict]: [{"date": "2024-01-01", "nav": 1.0, ...}]
    """
    if benchmark_daily_data is None or benchmark_daily_data.empty:
        return []

    # 转换日期格式
    import pandas as pd

    df = benchmark_daily_data.copy()
    df["date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")

    # 计算净值（归一化到第一天）
    initial_close = df["close"].iloc[0]
    df["nav"] = df["close"] / initial_close

    # 转换为字典列表
    return df[["date", "nav", "close"]].to_dict("records")


def main():
    """主函数：生成PDF报告"""

    print("=" * 70)
    print("正在生成PDF报告...")
    print("=" * 70)

    # 0. 检查并转换Excel到CSV（如果需要）
    csv_path = os.path.join(DOCS_DIR, "交割单_2024-11-04-2025-11-04.csv")
    xlsx_path = os.path.join(DOCS_DIR, "交割单.xlsx")

    if not os.path.exists(csv_path):
        if os.path.exists(xlsx_path):
            print("\n0️⃣  交割单.csv 不存在，正在从 Excel 转换...")
            try:
                from data.reader import convert_excel_to_csv

                convert_excel_to_csv(xlsx_path, csv_path, sheet="all")
                print(f"   ✓ 已生成: {csv_path}")
            except Exception as e:
                print(f"   ❌ 转换失败: {e}")
                print(f"   💡 请手动运行: python main.py")
                return
        else:
            print(f"\n❌ 错误：找不到交割单数据文件")
            print(f"   请确保以下文件存在：")
            print(f"   - {xlsx_path}")
            print(f"   - {csv_path}")
            return

    # 1. 获取基础数据
    print("\n1️⃣  获取每日持仓数据...")
    daily_positions = get_daily_positions(include_positions=False)
    print(f"   ✓ 获取 {len(daily_positions)} 天数据")

    # 2. 获取统计区间
    print("\n2️⃣  获取统计区间配置...")
    periods = get_periods_config()
    print(f"   ✓ 配置 {len(periods)} 个统计区间")
    for name, (start, end) in periods.items():
        print(f"     • {name}: {start} 至 {end}")

    # 3. 获取交易记录
    print("\n3️⃣  获取交易记录...")
    transactions = get_transactions()
    print(f"   ✓ 获取 {len(transactions)} 笔交易")

    # 4. 获取行业映射
    print("\n4️⃣  获取行业映射...")
    industry_mapping = get_industry_mapping()
    print(f"   ✓ 获取 {len(industry_mapping)} 只股票的行业信息")

    # 5. 获取基准数据
    print("\n5️⃣  获取基准数据（沪深300）...")
    index_code = "000300.SH"
    benchmark_daily_df = get_benchmark_daily_data(index_code)
    benchmark_returns_data = get_benchmark_returns(index_code)
    print(f"   ✓ 基准日度数据: {len(benchmark_daily_df)} 天")

    # 获取最新可用日期（用于行业权重）
    if not daily_positions:
        print("   ⚠️  没有持仓数据，无法继续")
        return

    latest_date = daily_positions[-1]["date"]
    print(f"   ✓ 最新日期: {latest_date}")

    # 尝试获取行业权重和收益（可能失败）
    benchmark_industry_weights = None
    benchmark_industry_returns = None
    try:
        # 使用一个较早的日期（例如2024-11-01）
        weight_date = "2024-11-01"
        benchmark_industry_weights = get_benchmark_industry_weights(
            index_code, weight_date
        )
        print(f"   ✓ 基准行业权重: {len(benchmark_industry_weights)} 个行业")
    except Exception as e:
        print(f"   ⚠️  获取行业权重失败: {e}")

    try:
        # 获取近一年的行业收益
        start_date = "2024-01-01"
        end_date = "2024-11-01"
        benchmark_industry_returns = get_benchmark_industry_returns(
            index_code, start_date, end_date
        )
        print(f"   ✓ 基准行业收益: {len(benchmark_industry_returns)} 个行业")
    except Exception as e:
        print(f"   ⚠️  获取行业收益失败: {e}")

    # 6. 获取持仓明细（使用成立以来的数据）
    print("\n6️⃣  获取持仓明细...")
    period_start, period_end = periods.get(
        "成立以来", (daily_positions[0]["date"], latest_date)
    )
    position_details_result = get_position_details(
        period_start=period_start, period_end=period_end
    )
    position_details = position_details_result.get("position_details", [])
    total_assets = position_details_result.get("total_assets", 0.0)
    total_profit = position_details_result.get("total_profit", 0.0)
    print(f"   ✓ 持仓明细: {len(position_details)} 只")
    print(f"   ✓ 总资产: {total_assets:.2f}万元")
    print(f"   ✓ 总收益: {total_profit:.2f}万元")

    # 7. 数据转换
    print("\n7️⃣  转换数据格式...")
    nav_data = convert_daily_positions_to_nav(daily_positions)
    benchmark_nav_data = convert_benchmark_data_to_nav(benchmark_daily_df)
    print(f"   ✓ 产品净值数据: {len(nav_data)} 天")
    print(f"   ✓ 基准净值数据: {len(benchmark_nav_data)} 天")

    # 8. 构建PDF数据
    print("\n8️⃣  构建PDF数据...")

    # 产品信息
    product_info = {
        "product_name": "私募基金产品",
        "establishment_date": (
            daily_positions[0]["date"] if daily_positions else "2015-01-05"
        ),
        "current_scale": (
            daily_positions[-1]["total_assets"] if daily_positions else 0.0
        ),
        "investment_strategy": "股票多头策略",
    }

    benchmark_period_return = benchmark_returns_data.get("period_returns", {}).get(
        "成立以来"
    )

    page1_data = build_page1_data(
        nav_data=nav_data,
        position_details=position_details,
        total_assets=total_assets,
        total_profit=total_profit,
        daily_positions=daily_positions,
        transactions=transactions,
        periods=periods,
        industry_mapping=industry_mapping,
        product_info=product_info,
        risk_free_rate=0.03,
        benchmark_nav_data=benchmark_nav_data,
        benchmark_returns=benchmark_returns_data.get("daily_returns", []),
        benchmark_period_return=benchmark_period_return,
        benchmark_period_returns=benchmark_returns_data.get("period_returns", {}),
        benchmark_industry_weights=benchmark_industry_weights,
        benchmark_industry_returns=benchmark_industry_returns,
    )
    print(f"   ✓ PDF数据构建完成")

    # 9. 生成PDF
    print("\n9️⃣  生成PDF文件...")
    output_path = "私募基金报告_完整版.pdf"
    result_path = generate_page1(output_path=output_path, data=page1_data)

    print("\n" + "=" * 70)
    print(f"✅ PDF报告已生成: {result_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
