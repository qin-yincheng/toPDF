# 开发者A工作补充文档

## 说明
本文档基于模版模块实现.md的前六部分内容，补充开发者A缺失的功能和数据计算。

---

## 一、缺失的关键数据获取

### 1. 行业分类数据获取
**模块位置**: `data/industry.py` (新建)

**功能**: 从Tushare获取股票的行业分类信息

**需要实现的函数**:
```python
def get_stock_industry(stock_code: str) -> str:
    """
    获取股票行业分类
    
    参数:
        stock_code: 股票代码（6位数字）
    
    返回:
        str: 行业分类名称（如："银行"、"计算机"等）
    
    实现:
        MVP版本：使用mock数据或固定映射
        完整版本：调用Tushare API (stock_company或stock_basic)
    
    注意:
        需要建立行业映射表，确保与申万一级行业标准一致
    """
    # MVP版本：使用简单映射
    industry_mapping = {
        '000001': '银行',
        '000002': '房地产',
        # ... 更多映射
    }
    return industry_mapping.get(stock_code, '未知行业')
```

**批量获取函数**:
```python
def batch_get_industry_mapping(stock_codes: List[str]) -> Dict[str, str]:
    """
    批量获取股票行业分类
    
    参数:
        stock_codes: 股票代码列表
    
    返回:
        Dict: {code: industry_name}
    
    用途:
        为持仓明细和行业分析提供行业分类数据
    """
    industry_map = {}
    for code in stock_codes:
        industry_map[code] = get_stock_industry(code)
    return industry_map
```

---

### 2. 基准指数数据获取
**模块位置**: `data/benchmark.py` (新建)

**功能**: 获取基准指数（如沪深300）的每日数据

**需要实现的函数**:
```python
def get_benchmark_data(
    index_code: str = '000300.SH',  # 沪深300
    start_date: str = None,
    end_date: str = None
) -> pd.DataFrame:
    """
    获取基准指数数据
    
    参数:
        index_code: 指数代码（默认沪深300）
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
    
    返回:
        DataFrame: 包含列 ['trade_date', 'close', 'open', 'high', 'low']
    
    实现:
        MVP版本：使用mock数据（固定增长率或随机波动）
        完整版本：调用Tushare API (index_daily)
    
    用途:
        用于计算基准收益率、β值、主动收益等
    """
    # MVP版本：生成mock数据
    dates = generate_date_range(start_date, end_date)
    initial_price = 3000.0  # 假设初始点位
    
    mock_data = []
    for i, date in enumerate(dates):
        # 模拟指数涨跌（简单随机）
        daily_change = np.random.normal(0, 0.02)  # 2%标准差
        price = initial_price * (1 + daily_change) ** i
        mock_data.append({
            'trade_date': date,
            'close': price,
            'open': price * 0.99,
            'high': price * 1.01,
            'low': price * 0.98
        })
    
    return pd.DataFrame(mock_data)
```

**计算基准收益率函数**:
```python
def calculate_benchmark_returns(
    benchmark_data: pd.DataFrame,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """
    计算基准指数收益率
    
    返回:
        Dict: {
            'period_return': float,      # 期间收益率（%）
            'annualized_return': float,  # 年化收益率（%）
            'daily_returns': List[float] # 每日收益率序列
        }
    """
    if benchmark_data.empty:
        return {'period_return': 0.0, 'annualized_return': 0.0, 'daily_returns': []}
    
    # 计算期间收益率
    initial_price = benchmark_data.iloc[0]['close']
    final_price = benchmark_data.iloc[-1]['close']
    period_return = (final_price - initial_price) / initial_price * 100
    
    # 计算每日收益率
    daily_returns = []
    for i in range(1, len(benchmark_data)):
        ret = (benchmark_data.iloc[i]['close'] - benchmark_data.iloc[i-1]['close']) / \
              benchmark_data.iloc[i-1]['close']
        daily_returns.append(ret)
    
    # 计算年化收益率
    days = len(benchmark_data)
    if days > 0:
        annualized_return = ((1 + period_return/100) ** (365/days) - 1) * 100
    else:
        annualized_return = 0.0
    
    return {
        'period_return': round(period_return, 2),
        'annualized_return': round(annualized_return, 2),
        'daily_returns': daily_returns
    }
```

---

### 3. 申购赎回数据识别
**模块位置**: `calc/position.py` (补充)

**功能**: 从交割单中识别申购和赎回记录

**需要实现的函数**:
```python
def identify_subscription_redemption(
    transactions: pd.DataFrame
) -> Dict[str, Any]:
    """
    识别申购和赎回记录
    
    参数:
        transactions: 交易记录DataFrame
    
    返回:
        Dict: {
            'subscriptions': List[Dict],  # 申购记录列表
            'redemptions': List[Dict],    # 赎回记录列表
            'total_subscription': float,  # 总申购金额（万元）
            'total_redemption': float      # 总赎回金额（万元）
        }
    
    识别逻辑:
        MVP版本：如果交割单中有特殊标记字段，识别申购/赎回
        如果没有，返回空列表和0值
    
    注意:
        申购/赎回通常不是股票交易，可能是资金进出记录
        需要根据实际交割单格式调整识别逻辑
    """
    subscriptions = []
    redemptions = []
    
    # MVP版本：假设没有申购赎回数据
    # 完整版本：根据交割单中的特殊字段识别
    
    # 示例：如果有'交易类型'字段
    # if '交易类型' in transactions.columns:
    #     subs = transactions[transactions['交易类型'] == '申购']
    #     reds = transactions[transactions['交易类型'] == '赎回']
    
    total_subscription = 0.0  # 万元
    total_redemption = 0.0    # 万元
    
    return {
        'subscriptions': subscriptions,
        'redemptions': redemptions,
        'total_subscription': total_subscription,
        'total_redemption': total_redemption
    }
```

---

## 二、缺失的持仓计算功能

### 1. 产品份额计算
**模块位置**: `calc/position.py` (补充)

**功能**: 计算产品份额（如果产品有份额概念）

**需要实现的函数**:
```python
def calculate_product_shares(
    daily_positions: List[Dict[str, Any]],
    initial_capital: float = 1000.0
) -> List[Dict[str, Any]]:
    """
    计算每日产品份额
    
    参数:
        daily_positions: 每日持仓列表（来自calculate_daily_positions）
        initial_capital: 初始资金（万元）
    
    返回:
        List[Dict]: [{date, shares, nav}, ...]
        shares: 产品份额（万份）
        nav: 单位净值
    
    计算公式:
        单位净值 = 总资产 / 初始资金
        产品份额 = 总资产 / 单位净值 = 初始资金（简化）
        或：产品份额 = 总资产 / 单位净值
    
    注意:
        如果产品没有份额概念，份额可以等于初始资金（固定）
    """
    shares_data = []
    
    for daily_data in daily_positions:
        date = daily_data['date']
        total_assets = daily_data['total_assets']
        
        # 计算单位净值
        nav = total_assets / initial_capital if initial_capital > 0 else 1.0
        
        # 计算份额（简化：假设份额等于初始资金，或等于总资产/净值）
        if nav > 0:
            shares = total_assets / nav
        else:
            shares = initial_capital
        
        shares_data.append({
            'date': date,
            'shares': round(shares, 2),  # 万份
            'nav': round(nav, 4)
        })
    
    return shares_data
```

---

### 2. 资产分类计算
**模块位置**: `calc/position.py` (补充)

**功能**: 计算每日资产分类（股票、基金、逆回购、现金等）

**需要实现的函数**:
```python
def calculate_asset_distribution(
    daily_positions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    计算每日资产分布
    
    参数:
        daily_positions: 每日持仓列表
    
    返回:
        List[Dict]: [{
            'date': str,
            'stock_value': float,      # 股票市值（万元）
            'fund_value': float,       # 基金市值（万元）
            'repo_value': float,       # 逆回购（万元）
            'cash': float,            # 现金（万元）
            'other_value': float,      # 其他资产（万元）
            'total_assets': float,     # 总资产（万元）
            'stock_pct': float,        # 股票占比（%）
            'fund_pct': float,         # 基金占比（%）
            'repo_pct': float,         # 逆回购占比（%）
            'cash_pct': float,         # 现金占比（%）
            'other_pct': float         # 其他资产占比（%）
        }, ...]
    
    计算公式:
        股票市值 = 所有持仓股票的市值总和
        基金市值 = 0（如果有基金持仓需要单独计算）
        逆回购 = 0（如果有逆回购需要单独计算）
        现金 = cash余额
        其他资产 = 0
        总资产 = 股票市值 + 基金市值 + 逆回购 + 现金 + 其他资产
        各资产占比 = 各资产市值 / 总资产 × 100%
    """
    asset_distribution = []
    
    for daily_data in daily_positions:
        date = daily_data['date']
        stock_value = daily_data.get('stock_value', 0)
        cash = daily_data.get('cash', 0)
        total_assets = daily_data.get('total_assets', 0)
        
        # MVP版本：假设只有股票和现金
        fund_value = 0.0
        repo_value = 0.0
        other_value = 0.0
        
        # 计算占比
        if total_assets > 0:
            stock_pct = (stock_value / total_assets) * 100
            fund_pct = (fund_value / total_assets) * 100
            repo_pct = (repo_value / total_assets) * 100
            cash_pct = (cash / total_assets) * 100
            other_pct = (other_value / total_assets) * 100
        else:
            stock_pct = fund_pct = repo_pct = cash_pct = other_pct = 0.0
        
        asset_distribution.append({
            'date': date,
            'stock_value': round(stock_value, 2),
            'fund_value': round(fund_value, 2),
            'repo_value': round(repo_value, 2),
            'cash': round(cash, 2),
            'other_value': round(other_value, 2),
            'total_assets': round(total_assets, 2),
            'stock_pct': round(stock_pct, 2),
            'fund_pct': round(fund_pct, 2),
            'repo_pct': round(repo_pct, 2),
            'cash_pct': round(cash_pct, 2),
            'other_pct': round(other_pct, 2)
        })
    
    return asset_distribution
```

---

### 3. 股票仓位计算
**模块位置**: `calc/position.py` (补充)

**功能**: 计算每日股票仓位（股票市值占总资产比例）

**需要实现的函数**:
```python
def calculate_stock_position(
    daily_positions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    计算每日股票仓位
    
    参数:
        daily_positions: 每日持仓列表
    
    返回:
        List[Dict]: [{
            'date': str,
            'stock_position': float,    # 股票仓位（%）
            'total_assets': float       # 总资产（万元）
        }, ...]
    
    计算公式:
        股票仓位 = 股票市值 / 总资产 × 100%
    """
    position_data = []
    
    for daily_data in daily_positions:
        date = daily_data['date']
        stock_value = daily_data.get('stock_value', 0)
        total_assets = daily_data.get('total_assets', 0)
        
        if total_assets > 0:
            stock_position = (stock_value / total_assets) * 100
        else:
            stock_position = 0.0
        
        position_data.append({
            'date': date,
            'stock_position': round(stock_position, 2),
            'total_assets': total_assets
        })
    
    return position_data
```

---

### 4. TOP10仓位计算
**模块位置**: `calc/position.py` (补充)

**功能**: 计算每日前十大持仓的累计市值占比

**需要实现的函数**:
```python
def calculate_top10_position(
    daily_positions: List[Dict[str, Any]],
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    计算每日TOP N持仓占比
    
    参数:
        daily_positions: 每日持仓列表
        top_n: 前N大持仓（默认10）
    
    返回:
        List[Dict]: [{
            'date': str,
            'top10_value': float,      # TOP10持仓市值（万元）
            'top10_pct': float          # TOP10持仓占比（%）
        }, ...]
    
    计算公式:
        TOP10市值 = 前十大持仓股票的市值总和
        TOP10占比 = TOP10市值 / 总资产 × 100%
    """
    top10_data = []
    
    for daily_data in daily_positions:
        date = daily_data['date']
        positions = daily_data.get('positions', {})
        total_assets = daily_data.get('total_assets', 0)
        
        # 按市值排序，取前N大
        position_list = []
        for code, pos_data in positions.items():
            market_value = pos_data.get('market_value', 0)
            position_list.append((code, market_value))
        
        # 排序
        position_list.sort(key=lambda x: x[1], reverse=True)
        
        # 取前N大
        top_n_positions = position_list[:top_n]
        top_n_value = sum([mv for _, mv in top_n_positions])
        
        # 计算占比
        if total_assets > 0:
            top_n_pct = (top_n_value / total_assets) * 100
        else:
            top_n_pct = 0.0
        
        top10_data.append({
            'date': date,
            f'top{top_n}_value': round(top_n_value, 2),
            f'top{top_n}_pct': round(top_n_pct, 2)
        })
    
    return top10_data
```

---

### 5. 流动性资产计算
**模块位置**: `calc/position.py` (补充)

**功能**: 计算每日流动性资产比例

**需要实现的函数**:
```python
def calculate_liquidity_ratio(
    daily_positions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    计算每日流动性资产比例
    
    参数:
        daily_positions: 每日持仓列表
    
    返回:
        List[Dict]: [{
            'date': str,
            'liquidity_assets': float,   # 流动性资产（万元）
            'liquidity_ratio': float    # 流动性资产比例（%）
        }, ...]
    
    计算公式:
        流动性资产 = 现金 + 逆回购 + 其他可快速变现资产
        流动性资产比例 = 流动性资产 / 总资产 × 100%
    
    注意:
        MVP版本：流动性资产 = 现金（假设没有逆回购和其他流动性资产）
    """
    liquidity_data = []
    
    for daily_data in daily_positions:
        date = daily_data['date']
        cash = daily_data.get('cash', 0)
        total_assets = daily_data.get('total_assets', 0)
        
        # MVP版本：流动性资产 = 现金
        repo_value = 0.0  # 逆回购
        other_liquid = 0.0  # 其他流动性资产
        liquidity_assets = cash + repo_value + other_liquid
        
        # 计算比例
        if total_assets > 0:
            liquidity_ratio = (liquidity_assets / total_assets) * 100
        else:
            liquidity_ratio = 0.0
        
        liquidity_data.append({
            'date': date,
            'liquidity_assets': round(liquidity_assets, 2),
            'liquidity_ratio': round(liquidity_ratio, 2)
        })
    
    return liquidity_data
```

---

## 三、行业分析相关计算

### 1. 行业分布计算
**模块位置**: `calc/industry.py` (新建)

**功能**: 计算持仓的行业分布

**需要实现的函数**:
```python
def calculate_industry_distribution(
    positions: Dict[str, Dict[str, Any]],
    industry_mapping: Dict[str, str]
) -> Dict[str, Dict[str, Any]]:
    """
    计算持仓行业分布
    
    参数:
        positions: 持仓字典 {code: {quantity, market_value, ...}}
        industry_mapping: 行业映射 {code: industry_name}
    
    返回:
        Dict: {
            'industry_name': {
                'market_value': float,      # 行业持仓市值（万元）
                'percentage': float,         # 行业占比（%）
                'stocks': List[str]          # 该行业下的股票代码列表
            }
        }
    
    计算公式:
        行业市值 = Σ(该行业下所有股票的持仓市值)
        行业占比 = 行业市值 / 总资产 × 100%
    """
    from calc.position import calculate_positions
    
    industry_dist = {}
    total_value = sum([pos.get('market_value', 0) for pos in positions.values()])
    
    for code, pos_data in positions.items():
        industry = industry_mapping.get(code, '未知行业')
        market_value = pos_data.get('market_value', 0)
        
        if industry not in industry_dist:
            industry_dist[industry] = {
                'market_value': 0.0,
                'percentage': 0.0,
                'stocks': []
            }
        
        industry_dist[industry]['market_value'] += market_value
        industry_dist[industry]['stocks'].append(code)
    
    # 计算占比
    for industry, data in industry_dist.items():
        if total_value > 0:
            data['percentage'] = (data['market_value'] / total_value) * 100
        else:
            data['percentage'] = 0.0
        data['market_value'] = round(data['market_value'], 2)
        data['percentage'] = round(data['percentage'], 2)
    
    return industry_dist
```

---

### 2. 每日行业占比时序
**模块位置**: `calc/industry.py` (新建)

**功能**: 计算每日各行业的持仓占比时序

**需要实现的函数**:
```python
def calculate_daily_industry_distribution(
    daily_positions: List[Dict[str, Any]],
    industry_mapping: Dict[str, str]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    计算每日行业分布时序
    
    参数:
        daily_positions: 每日持仓列表
        industry_mapping: 行业映射
    
    返回:
        Dict: {
            'industry_name': [
                {'date': str, 'percentage': float, 'market_value': float},
                ...
            ]
        }
    
    用途:
        用于绘制行业占比时序图
    """
    industry_time_series = {}
    
    for daily_data in daily_positions:
        date = daily_data['date']
        positions = daily_data.get('positions', {})
        total_assets = daily_data.get('total_assets', 0)
        
        # 按行业聚合
        industry_dist = {}
        for code, pos_data in positions.items():
            industry = industry_mapping.get(code, '未知行业')
            market_value = pos_data.get('market_value', 0)
            
            if industry not in industry_dist:
                industry_dist[industry] = 0.0
            industry_dist[industry] += market_value
        
        # 计算占比并添加到时序
        for industry, mv in industry_dist.items():
            if industry not in industry_time_series:
                industry_time_series[industry] = []
            
            if total_assets > 0:
                pct = (mv / total_assets) * 100
            else:
                pct = 0.0
            
            industry_time_series[industry].append({
                'date': date,
                'percentage': round(pct, 2),
                'market_value': round(mv, 2)
            })
    
    return industry_time_series
```

---

### 3. 行业偏离度计算
**模块位置**: `calc/industry.py` (新建)

**功能**: 计算产品相对基准的行业偏离度

**需要实现的函数**:
```python
def calculate_industry_deviation(
    product_industry_dist: Dict[str, float],
    benchmark_industry_dist: Dict[str, float]
) -> float:
    """
    计算行业偏离度
    
    参数:
        product_industry_dist: 产品行业分布 {industry: percentage}
        benchmark_industry_dist: 基准行业分布 {industry: percentage}
    
    返回:
        float: 行业偏离度（%）
    
    计算公式:
        行业偏离度 = Σ|产品行业占比 - 基准行业占比| / 行业数量 × 100%
        或：行业偏离度 = Σ|产品行业占比 - 基准行业占比| / 2
    
    注意:
        需要获取基准指数的行业分布（需要外部数据或配置）
    """
    all_industries = set(product_industry_dist.keys()) | set(benchmark_industry_dist.keys())
    
    if not all_industries:
        return 0.0
    
    total_deviation = 0.0
    for industry in all_industries:
        product_pct = product_industry_dist.get(industry, 0)
        benchmark_pct = benchmark_industry_dist.get(industry, 0)
        deviation = abs(product_pct - benchmark_pct)
        total_deviation += deviation
    
    # 平均偏离度
    avg_deviation = total_deviation / len(all_industries)
    
    return round(avg_deviation, 2)
```

---

## 四、交易统计相关计算

### 1. 换手率计算
**模块位置**: `calc/trading.py` (新建)

**功能**: 计算各资产类别的换手率

**需要实现的函数**:
```python
def calculate_turnover(
    transactions: pd.DataFrame,
    daily_positions: List[Dict[str, Any]],
    asset_class: str = '股票',
    start_date: str = None,
    end_date: str = None
) -> float:
    """
    计算换手率（年化）
    
    参数:
        transactions: 交易记录DataFrame
        daily_positions: 每日持仓列表
        asset_class: 资产类别（'股票'、'基金'、'逆回购'等）
        start_date: 开始日期
        end_date: 结束日期
    
    返回:
        float: 换手率（年化，%）
    
    计算公式:
        换手率 = (期间交易金额 / 期间平均持仓市值) × (365 / 实际天数) × 100%
    
    注意:
        期间交易金额 = 买入金额 + 卖出金额
        期间平均持仓市值 = 每日持仓市值的平均值
    """
    # 筛选该资产类别的交易
    if asset_class == '股票':
        asset_trans = transactions[
            (transactions['date'] >= start_date) & 
            (transactions['date'] <= end_date)
        ]
    else:
        # 其他资产类别需要单独处理
        asset_trans = pd.DataFrame()
    
    # 计算期间交易金额
    buy_amount = asset_trans[asset_trans['direction'] == '买入']['amount'].sum() / 10000  # 万元
    sell_amount = asset_trans[asset_trans['direction'] == '卖出']['amount'].sum() / 10000  # 万元
    total_turnover = buy_amount + sell_amount
    
    # 计算期间平均持仓市值
    market_values = []
    for daily_data in daily_positions:
        if start_date <= daily_data['date'] <= end_date:
            if asset_class == '股票':
                market_values.append(daily_data.get('stock_value', 0))
            else:
                market_values.append(0)
    
    if not market_values:
        return 0.0
    
    avg_market_value = sum(market_values) / len(market_values)
    
    # 计算实际天数
    from datetime import datetime
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    days = (end_dt - start_dt).days + 1
    
    # 计算年化换手率
    if avg_market_value > 0 and days > 0:
        turnover_rate = (total_turnover / avg_market_value) * (365 / days) * 100
    else:
        turnover_rate = 0.0
    
    return round(turnover_rate, 2)
```

---

### 2. 交易统计计算
**模块位置**: `calc/trading.py` (新建)

**功能**: 统计各类资产的买入和卖出金额

**需要实现的函数**:
```python
def calculate_trading_statistics(
    transactions: pd.DataFrame,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Dict[str, float]]:
    """
    计算交易统计
    
    参数:
        transactions: 交易记录DataFrame
        start_date: 开始日期
        end_date: 结束日期
    
    返回:
        Dict: {
            '股票': {
                'buy_amount': float,      # 买入金额（万元）
                'sell_amount': float      # 卖出金额（万元）
            },
            '基金': {...},
            '逆回购': {...}
        }
    
    用途:
        用于绘制交易统计图表
    """
    trading_stats = {}
    
    # 筛选日期范围内的交易
    period_trans = transactions[
        (transactions['date'] >= start_date) & 
        (transactions['date'] <= end_date)
    ]
    
    # MVP版本：假设只有股票交易
    stock_trans = period_trans  # 所有交易都视为股票交易
    
    buy_amount = stock_trans[stock_trans['direction'] == '买入']['amount'].sum() / 10000  # 万元
    sell_amount = stock_trans[stock_trans['direction'] == '卖出']['amount'].sum() / 10000  # 万元
    
    trading_stats['股票'] = {
        'buy_amount': round(buy_amount, 2),
        'sell_amount': round(sell_amount, 2)
    }
    
    # 其他资产类别（MVP版本设为0）
    trading_stats['基金'] = {'buy_amount': 0.0, 'sell_amount': 0.0}
    trading_stats['逆回购'] = {'buy_amount': 0.0, 'sell_amount': 0.0}
    
    return trading_stats
```

---

## 五、数据输出格式补充

### 1. 为开发者B提供的数据格式
开发者A需要确保`calculate_daily_positions()`的输出包含以下字段：
- `date`: 日期
- `positions`: 持仓字典（完整版）
- `total_assets`: 总资产（万元）
- `stock_value`: 股票市值（万元）
- `cash`: 现金余额（万元）
- `realized_profit`: 已实现收益（万元）
- `unrealized_profit`: 未实现收益（万元）

### 2. 为开发者C提供的数据格式
需要新增以下数据格式转换函数：

```python
def format_asset_distribution_for_pdf(
    asset_distribution: List[Dict[str, Any]]
) -> List[List[str]]:
    """
    将资产分布数据转换为PDF表格格式
    """
    # 实现表格数据格式化
    pass

def format_industry_distribution_for_pdf(
    industry_dist: Dict[str, Dict[str, Any]]
) -> List[List[str]]:
    """
    将行业分布数据转换为PDF表格格式
    """
    # 实现表格数据格式化
    pass
```

---

## 六、配置项补充

在`config.py`中需要添加：
```python
# 基准指数配置
BENCHMARK_INDEX_CODE = '000300.SH'  # 沪深300
BENCHMARK_INDEX_NAME = '沪深300'

# 行业分类配置
INDUSTRY_CLASSIFICATION = '申万一级'  # 行业分类标准

# 数据源配置
USE_MOCK_DATA = True  # MVP版本使用mock数据
TUSHARE_TOKEN = ''    # Tushare API Token（如果有）
```

---

## 七、任务优先级

### 高优先级（必须实现）
1. ✅ 行业分类数据获取（Mock版本）
2. ✅ 基准指数数据获取（Mock版本）
3. ✅ 资产分类计算
4. ✅ 股票仓位计算
5. ✅ 行业分布计算

### 中优先级（重要功能）
6. ⚠️ 每日行业占比时序
7. ⚠️ TOP10仓位计算
8. ⚠️ 流动性资产计算

### 低优先级（可选功能）
9. ⚠️ 申购赎回识别
10. ⚠️ 换手率计算（可在后续版本实现）
11. ⚠️ 行业偏离度计算（需要基准行业分布数据）

---

## 八、注意事项

1. **Mock数据策略**: MVP版本使用简单mock数据，确保功能完整，后续再接入真实API
2. **数据格式统一**: 所有金额单位统一为万元，比例统一为百分比
3. **性能考虑**: 批量计算时使用pandas向量化操作，避免循环
4. **错误处理**: 所有函数都要处理边界情况（空数据、除零等）

---

**文档版本**: v1.0  
**创建日期**: 2024年  
**最后更新**: 2024年

