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

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import os

from config import CSV_FILE, INITIAL_CAPITAL
from calc.position import calculate_daily_asset_distribution, _read_csv, _parse_dates

# Tushare token（如果需要）
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")


def get_daily_positions(
    csv_path: Optional[str] = None,
    initial_capital: Optional[float] = None,
    max_days: Optional[int] = None,
    include_positions: bool = False
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
        total_assets_wan = row['total_assets'] / 10000  # 转为万元
        stock_value_wan = total_assets_wan * row['stock_pct'] / 100
        cash_value_wan = total_assets_wan * row['cash_pct'] / 100
        
        # 获取当日持仓明细
        positions = []
        if include_positions and date_str in daily_holdings:
            for code, holding in daily_holdings[date_str].items():
                ts_code = f"{code}.SH" if code.startswith('6') else f"{code}.SZ"
                positions.append({
                    'code': ts_code,
                    'name': holding.get('name', ''),
                    'market_value': round(holding['market_value'] / 10000, 4),  # 万元
                    'quantity': int(holding['quantity']),
                    'avg_cost': round(holding['avg_cost'], 2)
                })
        
        daily_data = {
            'date': date_str,
            'total_assets': round(total_assets_wan, 4),
            'stock_value': round(stock_value_wan, 4),
            'fund_value': 0.0,  # 当前策略只有股票
            'repo_value': 0.0,  # 当前策略只有股票
            'cash_value': round(cash_value_wan, 4),  # 额外提供现金
            'positions': positions
        }
        result.append(daily_data)
    
    return result


def _calculate_daily_holdings(
    csv_path: Optional[str] = None,
    max_days: Optional[int] = None
) -> Dict[str, Dict[str, Dict]]:
    """
    计算每日持仓明细
    
    返回:
        Dict: {日期: {股票代码: {quantity, avg_cost, market_value, name}}}
    """
    df = _read_csv(csv_path or CSV_FILE)
    df = _parse_dates(df)
    
    # 按日期排序
    df = df.sort_values(['buy_dt', 'sell_dt'])
    
    # 获取所有交易日期
    all_dates = set()
    all_dates.update(df[df['buy_dt'].notna()]['buy_dt'].unique())
    all_dates.update(df[df['sell_dt'].notna()]['sell_dt'].unique())
    all_dates = sorted(all_dates)
    
    if max_days:
        all_dates = all_dates[:max_days]
    
    # 逐日计算持仓
    holdings = {}  # {股票代码: {quantity, total_cost, name}}
    daily_holdings = {}
    
    for date in all_dates:
        # 处理当日买入
        buy_trades = df[(df['buy_dt'] == date) & df['buy_number'].notna()]
        for idx, trade in buy_trades.iterrows():
            code = trade['code']
            quantity = int(trade['buy_number'])
            cost = float(trade['buy_money'])
            name = trade.get('name', '')
            
            if code not in holdings:
                holdings[code] = {'quantity': 0, 'total_cost': 0.0, 'name': name}
            
            holdings[code]['quantity'] += quantity
            holdings[code]['total_cost'] += cost
        
        # 处理当日卖出
        sell_trades = df[(df['sell_dt'] == date) & df['sell_number'].notna()]
        for idx, trade in sell_trades.iterrows():
            code = trade['code']
            quantity = int(trade['sell_number'])
            
            if code in holdings:
                # 按比例减少成本
                if holdings[code]['quantity'] > 0:
                    cost_ratio = quantity / holdings[code]['quantity']
                    holdings[code]['total_cost'] *= (1 - cost_ratio)
                holdings[code]['quantity'] -= quantity
                
                # 清空持仓
                if holdings[code]['quantity'] <= 0:
                    del holdings[code]
        
        # 记录当日持仓快照
        if holdings:
            daily_holdings[date] = {}
            for code, holding in holdings.items():
                if holding['quantity'] > 0:
                    avg_cost = holding['total_cost'] / holding['quantity']
                    # 使用交割单的价格作为市值估算（简化）
                    # 实际应该使用收盘价，但这里为简化处理
                    daily_holdings[date][code] = {
                        'quantity': holding['quantity'],
                        'avg_cost': avg_cost,
                        'market_value': holding['total_cost'],  # 简化：使用成本价
                        'name': holding['name']
                    }
    
    return daily_holdings


def get_position_details(
    csv_path: Optional[str] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None
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
    # TODO: 实现期间持仓明细计算
    return {
        'total_assets': 0.0,
        'total_profit': 0.0,
        'position_details': []
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
    codes = sorted(df['code'].dropna().unique())
    
    # 转换为Tushare格式
    ts_codes = [f"{code}.SH" if code.startswith('6') else f"{code}.SZ" for code in codes]
    
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
            batch_codes = ts_codes[i:i+batch_size]
            try:
                # 获取股票行业信息
                info = pro.stock_basic(
                    ts_code=','.join(batch_codes),
                    fields='ts_code,industry'
                )
                if info is not None and not info.empty:
                    for _, row in info.iterrows():
                        industry = row['industry']
                        industry_mapping[row['ts_code']] = industry if pd.notna(industry) else "未分类"
            except Exception as e:
                print(f"  批次 {i//batch_size + 1} 查询失败: {e}")
                continue
    except Exception as e:
        print(f"获取行业映射失败: {e}")
    
    return industry_mapping


def get_transactions(
    csv_path: Optional[str] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None
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
        df = df[df['buy_dt'] >= period_start]
    if period_end:
        df = df[df['sell_dt'] <= period_end]
    
    transactions = []
    
    # 处理买入交易
    for idx, row in df.iterrows():
        if pd.notna(row.get('buy_date')):
            buy_money = pd.to_numeric(row.get('buy_money'), errors='coerce')
            buy_quantity = pd.to_numeric(row.get('buy_number'), errors='coerce')  # 注意是buy_number
            buy_price = pd.to_numeric(row.get('buy_price'), errors='coerce')
            
            if pd.notna(buy_money) and pd.notna(buy_quantity):
                ts_code = f"{row['code']}.SH" if row['code'].startswith('6') else f"{row['code']}.SZ"
                transactions.append({
                    'date': row['buy_date'],
                    'code': ts_code,
                    'name': row.get('name', ''),
                    'asset_class': '股票',
                    'direction': '买入',
                    'price': round(float(buy_price), 2) if pd.notna(buy_price) else 0.0,
                    'quantity': int(buy_quantity),
                    'amount': round(float(buy_money), 2)
                })
        
        # 处理卖出交易
        if pd.notna(row.get('sell_date')):
            sell_money = pd.to_numeric(row.get('sell_money'), errors='coerce')
            sell_quantity = pd.to_numeric(row.get('sell_number'), errors='coerce')  # 注意是sell_number
            sell_price = pd.to_numeric(row.get('sell_price'), errors='coerce')
            
            if pd.notna(sell_money) and pd.notna(sell_quantity):
                ts_code = f"{row['code']}.SH" if row['code'].startswith('6') else f"{row['code']}.SZ"
                transactions.append({
                    'date': row['sell_date'],
                    'code': ts_code,
                    'name': row.get('name', ''),
                    'asset_class': '股票',
                    'direction': '卖出',
                    'price': round(float(sell_price), 2) if pd.notna(sell_price) else 0.0,
                    'quantity': int(sell_quantity),
                    'amount': round(float(sell_money), 2)
                })
    
    # 按日期排序
    transactions.sort(key=lambda x: x['date'])
    
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
        "近六个月": ((end_date - pd.DateOffset(months=6)).strftime("%Y-%m-%d"), max_date),
        "近三个月": ((end_date - pd.DateOffset(months=3)).strftime("%Y-%m-%d"), max_date),
        "近一个月": ((end_date - pd.DateOffset(months=1)).strftime("%Y-%m-%d"), max_date),
    }
    
    return periods


def export_all_data(
    csv_path: Optional[str] = None,
    output_dir: str = "output",
    max_days: Optional[int] = None,
    include_positions: bool = False,
    include_benchmark: bool = True,
    index_code: str = "000300.SH"
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
    daily_positions = get_daily_positions(csv_path, max_days=max_days, include_positions=include_positions)
    daily_file = os.path.join(output_dir, "daily_positions.json")
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(daily_positions, f, ensure_ascii=False, indent=2)
    output_files['daily_positions'] = daily_file
    print(f"  ✓ 已导出 {len(daily_positions)} 天数据到 {daily_file}")
    
    # 2. 导出交易记录
    print("生成交易记录...")
    transactions = get_transactions(csv_path)
    trans_file = os.path.join(output_dir, "transactions.json")
    with open(trans_file, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)
    output_files['transactions'] = trans_file
    print(f"  ✓ 已导出 {len(transactions)} 条交易到 {trans_file}")
    
    # 3. 导出行业映射
    print("生成行业映射...")
    industry_mapping = get_industry_mapping(csv_path)
    industry_file = os.path.join(output_dir, "industry_mapping.json")
    with open(industry_file, 'w', encoding='utf-8') as f:
        json.dump(industry_mapping, f, ensure_ascii=False, indent=2)
    output_files['industry_mapping'] = industry_file
    print(f"  ✓ 已导出 {len(industry_mapping)} 只股票行业信息到 {industry_file}")
    
    # 4. 导出统计区间配置
    print("生成统计区间配置...")
    periods = get_periods_config()
    periods_file = os.path.join(output_dir, "periods_config.json")
    with open(periods_file, 'w', encoding='utf-8') as f:
        json.dump(periods, f, ensure_ascii=False, indent=2)
    output_files['periods_config'] = periods_file
    print(f"  ✓ 已导出统计区间配置到 {periods_file}")
    
    # 5. 导出基准数据（可选）
    if include_benchmark:
        try:
            print(f"生成基准数据（{index_code}）...")
            
            # 5.1 基准日度行情
            benchmark_daily = get_benchmark_daily_data(index_code=index_code, csv_path=csv_path)
            benchmark_daily_file = os.path.join(output_dir, "benchmark_daily_data.csv")
            benchmark_daily.to_csv(benchmark_daily_file, index=False)
            output_files['benchmark_daily_data'] = benchmark_daily_file
            print(f"  ✓ 已导出 {len(benchmark_daily)} 天基准行情到 {benchmark_daily_file}")
            
            # 5.2 基准收益率
            benchmark_returns = get_benchmark_returns(index_code=index_code, csv_path=csv_path, periods=periods)
            benchmark_returns_file = os.path.join(output_dir, "benchmark_returns.json")
            with open(benchmark_returns_file, 'w', encoding='utf-8') as f:
                json.dump(benchmark_returns, f, ensure_ascii=False, indent=2)
            output_files['benchmark_returns'] = benchmark_returns_file
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
                last_date = max([d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d) for d in all_dates])
                
                industry_weights = get_benchmark_industry_weights(index_code=index_code, date=last_date, csv_path=csv_path)
                industry_weights_file = os.path.join(output_dir, "benchmark_industry_weights.json")
                with open(industry_weights_file, 'w', encoding='utf-8') as f:
                    json.dump(industry_weights, f, ensure_ascii=False, indent=2)
                output_files['benchmark_industry_weights'] = industry_weights_file
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
                        csv_path=csv_path
                    )
                    industry_returns_file = os.path.join(output_dir, "benchmark_industry_returns.json")
                    with open(industry_returns_file, 'w', encoding='utf-8') as f:
                        json.dump(industry_returns, f, ensure_ascii=False, indent=2)
                    output_files['benchmark_industry_returns'] = industry_returns_file
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
    csv_path: Optional[str] = None
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
            dates_str = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d) for d in all_dates]
            dates_sorted = sorted(dates_str)
            start_date = start_date or dates_sorted[0]
            end_date = end_date or dates_sorted[-1]
        else:
            raise ValueError("无法从交割单确定日期范围，请手动指定 start_date 和 end_date")
    
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
    periods: Optional[Dict[str, Tuple[str, str]]] = None
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
        "index_code": index_code
    }


def get_benchmark_industry_weights(
    index_code: str = "000300.SH",
    date: Optional[str] = None,
    csv_path: Optional[str] = None
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
            dates_str = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d) for d in all_dates]
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
        code = row['con_code']  # 成分股代码
        weight = float(row['weight'])  # 权重
        
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
    csv_path: Optional[str] = None
) -> Dict[str, float]:
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
            dates_str = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d) for d in all_dates]
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
            from datetime import datetime, timedelta
            check_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=i)).strftime("%Y%m%d")
            df_weight = pro.index_weight(index_code=index_code, trade_date=check_date)
            if not df_weight.empty:
                break
        if df_weight.empty:
            raise ValueError(f"未找到有效的成分股权重数据: {index_code}")
    
    # 获取行业映射
    industry_map = get_industry_mapping(csv_path)
    
    # 获取每只股票的价格数据并计算收益率
    stock_returns = {}
    for code in df_weight['con_code'].unique():
        try:
            df_stock = pro.daily(ts_code=code, start_date=s, end_date=e)
            if not df_stock.empty:
                df_stock = df_stock.sort_values('trade_date')
                start_close = df_stock.iloc[0]['close']
                end_close = df_stock.iloc[-1]['close']
                if start_close > 0:
                    stock_returns[code] = (end_close / start_close - 1.0)
        except:
            continue
    
    # 按行业聚合收益率（权重加权）
    industry_returns = {}
    industry_total_weights = {}
    
    for _, row in df_weight.iterrows():
        code = row['con_code']
        weight = float(row['weight'])
        
        if code not in stock_returns:
            continue
        
        stock_ret = stock_returns[code]
        industry = industry_map.get(code, "其他")
        
        if industry not in industry_returns:
            industry_returns[industry] = 0.0
            industry_total_weights[industry] = 0.0
        
        industry_returns[industry] += stock_ret * weight
        industry_total_weights[industry] += weight
    
    # 计算加权平均收益率
    result = {}
    for industry in industry_returns:
        if industry_total_weights[industry] > 0:
            weighted_return = industry_returns[industry] / industry_total_weights[industry]
            result[industry] = round(weighted_return, 4)  # 保留4位小数
    
    return result
