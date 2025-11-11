import os
from typing import Dict, List, Optional
import time
from pathlib import Path

import pandas as pd
import tushare as ts

from config import CSV_FILE, INITIAL_CAPITAL, DOCS_DIR, REPORT_YEAR

import os
TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")

# 注意：缓存功能已移除，因为现在使用持仓成本而非收盘价
# CACHE_DIR 定义保留以避免错误，但不再主动创建目录
CACHE_DIR = Path(DOCS_DIR) / ".cache"
# CACHE_DIR.mkdir(exist_ok=True)  # 已注释：不再需要缓存功能


def _ts_code(code: str) -> str:
    """将6位股票代码转为Tushare格式"""
    if code.startswith('6'):
        return f"{code}.SH"
    else:
        return f"{code}.SZ"


def _read_csv(csv_path: str) -> pd.DataFrame:
    """
    读取交割单CSV（pair格式：一行包含买入与卖出信息），并返回DataFrame。
    仅做读取，不做重命名或校验。
    """
    last_err = None
    for enc in ("utf-8-sig", "utf-8", "gbk", "gb2312"):
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            # 规范代码列为6位字符串，避免前导0丢失导致后续无法匹配Tushare结果
            if "code" in df.columns:
                def _norm_code(v):
                    if pd.isna(v):
                        return None
                    s = str(v).strip()
                    if s.endswith('.0'):
                        s = s[:-2]
                    digits = ''.join(ch for ch in s if ch.isdigit())
                    if not digits:
                        return s
                    return digits[-6:].zfill(6)
                df["code"] = df["code"].apply(_norm_code)
            return df
        except UnicodeDecodeError as e:
            last_err = e
            continue
    raise last_err if last_err else RuntimeError("无法读取CSV文件")


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    解析买卖时间列为日期（YYYY-MM-DD）。优先使用 FROM_UNIXTIME 时间列；
    不存在时回退到 start/end 列。若缺失则结果为 NaT。
    """
    # 买入时间
    if "FROM_UNIXTIME(buy_time)" in df.columns:
        b = pd.to_datetime(df["FROM_UNIXTIME(buy_time)"], errors="coerce")
    elif "buy_time" in df.columns:
        b = pd.to_datetime(df["buy_time"], errors="coerce")
    elif "start" in df.columns:
        b = pd.to_datetime(df["start"], errors="coerce")
    else:
        b = pd.to_datetime(pd.Series([pd.NaT] * len(df)))

    # 卖出时间
    if "FROM_UNIXTIME(sell_time)" in df.columns:
        s = pd.to_datetime(df["FROM_UNIXTIME(sell_time)"], errors="coerce")
    elif "sell_time" in df.columns:
        s = pd.to_datetime(df["sell_time"], errors="coerce")
    elif "end" in df.columns:
        s = pd.to_datetime(df["end"], errors="coerce")
    else:
        s = pd.to_datetime(pd.Series([pd.NaT] * len(df)))

    df = df.copy()
    df["buy_dt"] = b
    df["sell_dt"] = s
    df["buy_date"] = b.dt.strftime("%Y-%m-%d")
    df["sell_date"] = s.dt.strftime("%Y-%m-%d")
    return df


def calculate_daily_asset_distribution(
    csv_path: Optional[str] = None,
    initial_capital: Optional[float] = None,
    max_days: Optional[int] = None,
    report_year: Optional[str] = "AUTO",
) -> pd.DataFrame:
    """
    基于交割单（pair格式）计算每日资产分类占比（股票/现金）。

    核心逻辑：
    - 先按天计算每只股票的期末持仓股数（累计买入股数 - 累计卖出股数，卖出当日不计入持仓）。
    - 使用持仓成本计算当日股票市值 = Σ(持仓股数 × 持仓平均成本)。
    - 当日现金 = 初始资金 - 截止当日累计买入金额 + 累计卖出金额。
    - 当日总资产 = 股票市值 + 现金。
    - 占比：股票占比=股票市值/总资产，现金占比=现金/总资产。

    参数:
        csv_path: 交割单CSV路径，默认使用 config.CSV_FILE
        initial_capital: 初始资金（元），默认使用 config.INITIAL_CAPITAL
        max_days: 仅计算前N天的数据，用于加速演示
        report_year: 报告年份（如"2015"），默认使用 config.REPORT_YEAR
                    设置后只返回该年份的数据，但会正确计算期初持仓

    返回:
        pd.DataFrame: 每日资产分布数据，index=date(字符串格式 YYYY-MM-DD)
            columns=['total_assets', 'stock_pct', 'cash_pct']
            - total_assets: 总资产（元），股票市值+现金
            - stock_pct: 股票占比（%）
            - cash_pct: 现金占比（%）
    """
    csv_path = str(csv_path or CSV_FILE)
    ini = float(initial_capital if initial_capital is not None else INITIAL_CAPITAL)
    # report_year="AUTO" 表示使用config配置，None 表示不限制年份
    if report_year == "AUTO":
        report_year = REPORT_YEAR
    if ini <= 0:
        raise ValueError("initial_capital 必须为正数")

    raw = _read_csv(csv_path)
    df = _parse_dates(raw)

    # 注意：价格异常过滤已移至Excel->CSV转换阶段（data/reader.py）
    # 此处直接使用清洗后的CSV数据

    # 准备金额列
    buy_money_col = "buy_money" if "buy_money" in df.columns else None
    sell_money_col = "sell_money" if "sell_money" in df.columns else None
    if buy_money_col is None or sell_money_col is None:
        raise ValueError("CSV缺少 buy_money 或 sell_money 列")

    df[buy_money_col] = pd.to_numeric(df[buy_money_col], errors="coerce").fillna(0.0)
    df[sell_money_col] = pd.to_numeric(df[sell_money_col], errors="coerce").fillna(0.0)
    # 股数列（用于计算持仓股数）
    buy_num_col = "buy_number" if "buy_number" in df.columns else None
    sell_num_col = "sell_number" if "sell_number" in df.columns else None
    if buy_num_col is None or sell_num_col is None:
        raise ValueError("CSV缺少 buy_number 或 sell_number 列")
    df[buy_num_col] = pd.to_numeric(df[buy_num_col], errors="coerce").fillna(0.0)
    df[sell_num_col] = pd.to_numeric(df[sell_num_col], errors="coerce").fillna(0.0)
    # 代码列
    code_col = "code" if "code" in df.columns else None
    if code_col is None:
        raise ValueError("CSV缺少 code 列")

    # 按日聚合买入/卖出金额
    buy_by_day = (
        df.dropna(subset=["buy_dt"])
        .groupby(df["buy_dt"].dt.strftime("%Y-%m-%d"))[buy_money_col]
        .sum()
        .sort_index()
    )
    sell_by_day = (
        df.dropna(subset=["sell_dt"])
        .groupby(df["sell_dt"].dt.strftime("%Y-%m-%d"))[sell_money_col]
        .sum()
        .sort_index()
    )

    # 生成完整日期序列
    # 使用买入和卖出日期的并集，确保所有交易都被统计
    all_dates = pd.to_datetime(list(set(buy_by_day.index).union(set(sell_by_day.index))))
    if len(all_dates) == 0:
        return pd.DataFrame()
    start = all_dates.min().date()
    end = all_dates.max().date()
    date_range = pd.date_range(start=start, end=end, freq="D").strftime("%Y-%m-%d")
    if isinstance(max_days, int) and max_days > 0:
        date_range = date_range[:max_days]

    # 累计买卖金额（按日期对齐）
    cum_buy = buy_by_day.reindex(date_range, fill_value=0.0).cumsum()
    cum_sell = sell_by_day.reindex(date_range, fill_value=0.0).cumsum()

    # 计算每日持仓股数（按股票代码）
    buys_qty = (
        df.dropna(subset=["buy_dt"]).groupby([df["buy_dt"].dt.strftime("%Y-%m-%d"), code_col])[buy_num_col].sum()
    )
    sells_qty = (
        df.dropna(subset=["sell_dt"]).groupby([df["sell_dt"].dt.strftime("%Y-%m-%d"), code_col])[sell_num_col].sum()
    )
    # 透视为日期×代码
    buy_qty_daily = buys_qty.unstack(fill_value=0.0).reindex(date_range, fill_value=0.0)
    sell_qty_daily = sells_qty.unstack(fill_value=0.0).reindex(date_range, fill_value=0.0)
    # 累计到当日（EOD 持仓）
    cum_buy_qty = buy_qty_daily.cumsum()
    cum_sell_qty = sell_qty_daily.cumsum()
    holdings_qty = (cum_buy_qty - cum_sell_qty).clip(lower=0.0)

    # 计算持仓成本（使用简单的金额累加法，与参考脚本一致）
    # 持仓成本 = 累计买入金额 - 已卖出股票的买入成本
    # 
    # 注意：这里按日期和代码聚合卖出金额（但实际上我们需要的是卖出股票的买入成本）
    # 由于交割单是配对格式（每行包含买入和卖出），卖出时减去的是该笔交易的buy_money
    
    # 按日期聚合：买入时增加持仓成本，卖出时减少持仓成本
    sells_cost = (
        df.dropna(subset=["sell_dt"]).groupby(df["sell_dt"].dt.strftime("%Y-%m-%d"))[buy_money_col].sum()
    )
    sells_cost_daily = sells_cost.reindex(date_range, fill_value=0.0)
    
    # 累计持仓成本 = 累计买入 - 累计卖出的买入成本
    cum_position_cost = (buy_by_day.reindex(date_range, fill_value=0.0).cumsum() 
                        - sells_cost_daily.cumsum())
    
    # 股票市值 = 持仓成本（使用买入成本，不使用市价）
    stock_value = cum_position_cost
    # 现金 = 初始资金 - 累计买入金额 + 累计卖出金额
    cash_value = ini - cum_buy + cum_sell
    
    # 修正：如果初始资金设置不足导致现金为负数
    # 需要动态调整初始资金，使现金始终非负
    min_cash = cash_value.min()
    if min_cash < 0:
        # 调整初始资金，确保最小现金为0
        adjustment = -min_cash + 1  # 加1避免刚好为0
        ini_adjusted = ini + adjustment
        cash_value = ini_adjusted - cum_buy + cum_sell
        print(f"  ⚠️ 初始资金 {ini/1e8:.2f}亿 不足，已自动调整为 {ini_adjusted/1e8:.2f}亿")
    
    # 确保现金非负（防止浮点数精度问题）
    cash_value = cash_value.clip(lower=0)
    
    # 总资产
    total_assets = (stock_value + cash_value).replace(0, pd.NA)

    # 占比
    stock_pct = (stock_value / total_assets * 100.0).fillna(0.0).round(4)
    cash_pct = (cash_value / total_assets * 100.0).fillna(0.0).round(4)

    # 构建 DataFrame，date 作为索引
    df_result = pd.DataFrame({
        'date': date_range,
        'total_assets': total_assets.fillna(0.0).round(2),  # 总资产，保留2位小数
        'stock_pct': stock_pct.values,
        'cash_pct': cash_pct.values,
    })
    df_result.set_index('date', inplace=True)
    
    # 如果指定了报告年份，只返回该年份的数据
    if report_year:
        # 筛选该年份的日期
        mask = df_result.index.str.startswith(report_year)
        df_filtered = df_result[mask].copy()
        
        if len(df_filtered) > 0:
            # 检查是否需要前一天的数据作为期初（跨年情况）
            first_date = df_filtered.index[0]
            if first_date.endswith('-01-01'):
                # 这是新年第一天，尝试获取上一年最后一天的数据作为"期初日"
                prev_year = str(int(report_year) - 1)
                prev_last_date = f"{prev_year}-12-31"
                
                if prev_last_date in df_result.index:
                    # 将上一年最后一天添加到结果中，作为期初参考
                    prev_day_data = df_result.loc[[prev_last_date]].copy()
                    # 将日期改为当年1月1日，但数据保持为上一年12月31日的值
                    # 这样期初资产就是上一年的期末资产
                    prev_day_data.index = [first_date]
                    # 用上一年最后一天的数据覆盖当年第一天的数据（如果存在）
                    df_filtered.loc[first_date] = prev_day_data.loc[first_date]
                    print(f"  📅 报告年份限制为 {report_year}年")
                    print(f"  期初资产使用 {prev_last_date} 数据: {prev_day_data.loc[first_date, 'total_assets']/10000:.2f}万元")
                    print(f"  统计区间: {df_filtered.index[0]} 至 {df_filtered.index[-1]}")
                else:
                    print(f"  📅 报告年份限制为 {report_year}年")
                    print(f"  ⚠️  未找到 {prev_last_date} 数据，使用当年第一天数据作为期初")
                    print(f"  统计区间: {df_filtered.index[0]} 至 {df_filtered.index[-1]}")
            else:
                print(f"  📅 报告年份限制为 {report_year}年")
                print(f"  统计区间: {df_filtered.index[0]} 至 {df_filtered.index[-1]}")
            
            return df_filtered
        else:
            print(f"  ⚠️  警告：{report_year}年无交易数据，返回全部数据")
            return df_result
    
    return df_result


def _ts_code(code: str) -> str:
    """将股票代码转换为Tushare格式（6位代码.市场后缀）"""
    code = str(code).zfill(6)
    if code.startswith('6'):
        return f"{code}.SH"
    else:
        return f"{code}.SZ"


def _fetch_close_prices_tushare(codes: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    使用 Tushare API 获取股票收盘价数据（不复权）。
    
    优化策略：
    1. 使用本地缓存，避免重复请求
    2. 按日期批量获取所有股票数据（而不是按股票逐个获取）
    3. Tushare 的 daily 接口支持一次获取多只股票
    
    参数:
        codes: 股票代码列表（6位字符串）
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    返回:
        DataFrame: index=date(YYYY-MM-DD), columns=code(6位), values=close_price
    """
    if not codes:
        return pd.DataFrame()
    
    if not TUSHARE_TOKEN:
        print("  错误：未设置 TUSHARE_TOKEN 环境变量")
        return pd.DataFrame()
    
    # 检查缓存
    cache_key = f"{start_date}_{end_date}"
    cache_file = CACHE_DIR / f"prices_{cache_key}.pkl"
    
    cached_df = None
    if cache_file.exists():
        try:
            print(f"从缓存加载价格数据: {cache_file.name}")
            cached_df = pd.read_pickle(cache_file)
            # 检查缓存是否包含所需的所有股票
            missing_codes = set(codes) - set(cached_df.columns)
            if not missing_codes:
                print(f"  ✓ 缓存命中：{len(codes)} 只股票")
                return cached_df[codes]
            print(f"  缓存中缺少 {len(missing_codes)} 只股票，将增量获取")
        except Exception as e:
            print(f"  警告：读取缓存失败: {e}")
            cached_df = None
    
    # 初始化 Tushare
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    # 转换日期格式为 YYYYMMDD
    start_str = start_date.replace('-', '')
    end_str = end_date.replace('-', '')
    
    # 确定需要获取的股票列表（如果有缓存，只获取缺失的）
    codes_to_fetch = codes
    if cached_df is not None:
        missing_codes = list(set(codes) - set(cached_df.columns))
        if missing_codes:
            codes_to_fetch = missing_codes
            print(f"增量获取 {len(codes_to_fetch)} 只股票的价格数据 ({start_date} 至 {end_date})...")
        else:
            codes_to_fetch = []
    else:
        print(f"获取 {len(codes_to_fetch)} 只股票的收盘价数据 ({start_date} 至 {end_date})...")
    
    all_prices = []
    
    if codes_to_fetch:
        # 优化：根据日期范围动态调整批次大小
        # Tushare 单次最多返回6000条记录，需要根据日期范围计算合适的批次大小
        date_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
        trading_days_estimate = int(date_days * 0.7)  # 估算交易日数（约70%）
        
        # 动态批次大小：确保 batch_size × trading_days ≈ 5000（留出余量）
        if trading_days_estimate > 0:
            batch_size = max(10, min(500, 5000 // trading_days_estimate))
        else:
            batch_size = 500
        
        print(f"  预估交易日: {trading_days_estimate} 天，批次大小: {batch_size} 只/批")
        
        total_batches = (len(codes_to_fetch) + batch_size - 1) // batch_size
        
        for i in range(0, len(codes_to_fetch), batch_size):
            batch_codes = codes_to_fetch[i:i+batch_size]
            ts_codes = [_ts_code(c) for c in batch_codes]
            
            batch_num = i // batch_size + 1
            print(f"  批次 {batch_num}/{total_batches}: 获取 {len(batch_codes)} 只股票...", end='', flush=True)
            
            try:
                # 一次性获取整个批次的所有数据
                df = pro.daily(
                    ts_code=','.join(ts_codes),
                    start_date=start_str,
                    end_date=end_str,
                    fields='ts_code,trade_date,close'
                )
                
                if df is not None and not df.empty:
                    # 检查是否触发6000条限制
                    returned_stocks = df['ts_code'].nunique()
                    if len(df) >= 6000 and returned_stocks < len(batch_codes):
                        print(f" ⚠️  触发6000条限制({returned_stocks}/{len(batch_codes)}只)")
                        # 触发限制，拆分为更小的批次重试
                        missing_codes = set(batch_codes) - set(df['ts_code'].str[:6].unique())
                        if missing_codes:
                            print(f"      重试获取 {len(missing_codes)} 只缺失股票...", end='', flush=True)
                            for missing_code in missing_codes:
                                try:
                                    single_df = pro.daily(
                                        ts_code=_ts_code(missing_code),
                                        start_date=start_str,
                                        end_date=end_str,
                                        fields='ts_code,trade_date,close'
                                    )
                                    if single_df is not None and not single_df.empty:
                                        df = pd.concat([df, single_df], ignore_index=True)
                                    time.sleep(0.1)
                                except:
                                    pass
                            print(f" ✓ 补充完成")
                    
                    # 转换代码格式（去掉市场后缀）
                    df['code'] = df['ts_code'].str[:6]
                    # 转换日期格式
                    df['date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
                    # 只保留需要的列
                    df = df[['date', 'code', 'close']]
                    all_prices.append(df)
                    final_stocks = df['code'].nunique()
                    print(f" ✓ 获取 {len(df)} 条记录 ({final_stocks} 只股票)")
                else:
                    print(" ✗ 无数据")
                
                # API 限流：每分钟最多200次调用，适当延迟
                if batch_num < total_batches:
                    time.sleep(0.3)  # 每批次延迟300ms，确保不超过限流
            
            except Exception as e:
                print(f" ✗ 错误: {e}")
                continue
    
    # 合并新获取的数据和缓存数据
    if all_prices:
        # 新获取的数据
        new_df = pd.concat(all_prices, ignore_index=True)
        new_pivot = new_df.pivot(index='date', columns='code', values='close')
        print(f"  ✓ 新数据：{len(new_pivot)} 个交易日 × {len(new_pivot.columns)} 只股票")
        
        # 与缓存合并
        if cached_df is not None:
            price_pivot = pd.concat([cached_df, new_pivot], axis=1)
            # 去重列（保留新数据）
            price_pivot = price_pivot.loc[:, ~price_pivot.columns.duplicated(keep='last')]
            print(f"  ✓ 合并后：{len(price_pivot)} 个交易日 × {len(price_pivot.columns)} 只股票")
        else:
            price_pivot = new_pivot
    elif cached_df is not None:
        # 没有新数据，只使用缓存
        price_pivot = cached_df
    else:
        print("  错误：未能获取任何价格数据")
        return pd.DataFrame()
    
    # 保存到缓存
    try:
        price_pivot.to_pickle(cache_file)
        print(f"  已缓存到: {cache_file.name}")
    except Exception as e:
        print(f"  警告：缓存保存失败: {e}")
    
    return price_pivot


def _build_price_from_trades(df: pd.DataFrame, codes: List[str], date_range: pd.Index) -> pd.DataFrame:
    """
    从交割单中构建每日价格数据（使用当天最后一笔交易的价格作为收盘价）。
    
    对于高频交易策略，使用实际成交价比Tushare的复权价格更准确。
    
    优化：使用向量化操作，避免逐个股票循环。
    
    参数:
        df: 交割单DataFrame（需包含buy_dt, sell_dt, code, buy_price, sell_price列）
        codes: 需要价格的股票代码列表
        date_range: 日期范围
    
    返回:
        DataFrame: index=date, columns=code, values=price
    """
    # 筛选出需要的股票（一次性完成）
    codes_set = set(codes)
    df_filtered = df[df['code'].isin(codes_set)].copy()
    
    if df_filtered.empty:
        return pd.DataFrame(index=date_range)
    
    # 准备买入价格数据
    buy_data = df_filtered.dropna(subset=['buy_dt']).copy()
    buy_data['date'] = buy_data['buy_dt'].dt.strftime('%Y-%m-%d')
    buy_data['code_str'] = buy_data['code'].astype(str).str.zfill(6)
    
    # 准备卖出价格数据
    sell_data = df_filtered.dropna(subset=['sell_dt']).copy()
    sell_data['date'] = sell_data['sell_dt'].dt.strftime('%Y-%m-%d')
    sell_data['code_str'] = sell_data['code'].astype(str).str.zfill(6)
    
    # 使用groupby一次性获取每天每只股票的最后一笔价格
    if not buy_data.empty:
        # 买入价：每天每只股票的最后一笔
        buy_last = buy_data.groupby(['date', 'code_str'])['buy_price'].last().reset_index()
        buy_pivot = buy_last.pivot(index='date', columns='code_str', values='buy_price')
    else:
        buy_pivot = pd.DataFrame()
    
    if not sell_data.empty:
        # 卖出价：每天每只股票的最后一笔
        sell_last = sell_data.groupby(['date', 'code_str'])['sell_price'].last().reset_index()
        sell_pivot = sell_last.pivot(index='date', columns='code_str', values='sell_price')
    else:
        sell_pivot = pd.DataFrame()
    
    # 合并：卖出价优先（更接近收盘价）
    if not buy_pivot.empty and not sell_pivot.empty:
        price_df = buy_pivot.combine_first(sell_pivot)
        price_df.update(sell_pivot)  # 卖出价覆盖买入价
    elif not sell_pivot.empty:
        price_df = sell_pivot
    elif not buy_pivot.empty:
        price_df = buy_pivot
    else:
        price_df = pd.DataFrame()
    
    # 对齐日期范围
    price_df = price_df.reindex(index=date_range, columns=[str(c).zfill(6) for c in codes])
    price_df.index.name = 'date'
    
    # 前向填充缺失值（使用最近的交易价格）
    price_df = price_df.ffill()
    
    # 如果还有缺失（某些股票在初期没有交易），用后向填充
    price_df = price_df.bfill()
    
    # 如果还有缺失，填0
    price_df = price_df.fillna(0.0)
    
    return price_df
