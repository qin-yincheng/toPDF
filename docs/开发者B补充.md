# 开发者B工作补充文档

## 说明
本文档基于模版模块实现.md的前六部分内容，补充开发者B缺失的指标计算功能。

---

## 一、缺失的关键指标计算

### 1. β值（Beta）计算
**模块位置**: `calc/metrics.py` (补充)

**功能**: 计算产品相对基准的β值

**需要实现的函数**:
```python
def calculate_beta(
    nav_data: List[Dict[str, Any]],
    benchmark_returns: List[float]
) -> float:
    """
    计算β值（Beta）
    
    参数:
        nav_data: 净值数据列表 [{date, nav, ...}, ...]
        benchmark_returns: 基准指数每日收益率序列（小数形式）
    
    返回:
        float: β值
    
    计算公式:
        β = Cov(产品收益率, 基准收益率) / Var(基准收益率)
    
    注意:
        需要确保产品收益率和基准收益率的日期对齐
        如果数据不足，返回1.0（中性）
    """
    import numpy as np
    
    # 计算产品每日收益率
    product_returns = calculate_daily_returns(nav_data)
    
    # 确保长度一致
    min_len = min(len(product_returns), len(benchmark_returns))
    if min_len < 2:
        return 1.0  # 数据不足，返回中性值
    
    product_returns = product_returns[:min_len]
    benchmark_returns = benchmark_returns[:min_len]
    
    # 计算协方差和方差
    cov = np.cov(product_returns, benchmark_returns)[0][1]
    var = np.var(benchmark_returns)
    
    # 计算β值
    if var > 0:
        beta = cov / var
    else:
        beta = 1.0  # 基准方差为0，返回中性值
    
    return round(beta, 4)
```

---

### 2. 主动收益计算
**模块位置**: `calc/metrics.py` (补充)

**功能**: 计算产品相对基准的主动收益

**需要实现的函数**:
```python
def calculate_active_return(
    product_period_return: float,
    benchmark_period_return: float,
    days: int
) -> Dict[str, float]:
    """
    计算主动收益
    
    参数:
        product_period_return: 产品期间收益率（%）
        benchmark_period_return: 基准期间收益率（%）
        days: 实际天数
    
    返回:
        Dict: {
            'active_return': float,          # 主动收益（%）
            'annualized_active_return': float # 年化主动收益（%）
        }
    
    计算公式:
        主动收益 = 产品收益率 - 基准收益率
        年化主动收益 = ((1 + 主动收益/100) ^ (365 / 实际天数)) - 1 × 100%
    """
    active_return = product_period_return - benchmark_period_return
    
    # 年化主动收益
    if days > 0:
        annualized_active_return = ((1 + active_return/100) ** (365/days) - 1) * 100
    else:
        annualized_active_return = 0.0
    
    return {
        'active_return': round(active_return, 2),
        'annualized_active_return': round(annualized_active_return, 2)
    }
```

---

### 3. 跟踪误差计算
**模块位置**: `calc/metrics.py` (补充)

**功能**: 计算产品相对基准的跟踪误差

**需要实现的函数**:
```python
def calculate_tracking_error(
    nav_data: List[Dict[str, Any]],
    benchmark_returns: List[float]
) -> float:
    """
    计算跟踪误差（年化）
    
    参数:
        nav_data: 净值数据列表
        benchmark_returns: 基准指数每日收益率序列（小数形式）
    
    返回:
        float: 跟踪误差（年化，%）
    
    计算公式:
        跟踪误差 = std(产品收益率 - 基准收益率) × sqrt(252) × 100%
    
    注意:
        跟踪误差衡量产品与基准的偏离程度
    """
    import numpy as np
    
    # 计算产品每日收益率
    product_returns = calculate_daily_returns(nav_data)
    
    # 确保长度一致
    min_len = min(len(product_returns), len(benchmark_returns))
    if min_len < 2:
        return 0.0
    
    product_returns = product_returns[:min_len]
    benchmark_returns = benchmark_returns[:min_len]
    
    # 计算超额收益率（产品收益率 - 基准收益率）
    excess_returns = [p - b for p, b in zip(product_returns, benchmark_returns)]
    
    # 计算跟踪误差
    tracking_error = np.std(excess_returns) * np.sqrt(252) * 100
    
    return round(tracking_error, 2)
```

---

### 4. 下行波动率计算
**模块位置**: `calc/metrics.py` (补充)

**功能**: 计算下行波动率（只考虑负收益率的波动率）

**需要实现的函数**:
```python
def calculate_downside_volatility(
    nav_data: List[Dict[str, Any]]
) -> float:
    """
    计算下行波动率（年化）
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        float: 下行波动率（年化，%）
    
    计算公式:
        下行波动率 = std(负收益率) × sqrt(252) × 100%
    
    注意:
        只考虑负收益率，用于计算索提诺比率
        如果没有负收益率，返回0
    """
    import numpy as np
    
    # 计算每日收益率
    daily_returns = calculate_daily_returns(nav_data)
    
    # 筛选负收益率
    negative_returns = [r for r in daily_returns if r < 0]
    
    if len(negative_returns) < 2:
        return 0.0
    
    # 计算下行波动率
    downside_volatility = np.std(negative_returns) * np.sqrt(252) * 100
    
    return round(downside_volatility, 2)
```

---

### 5. 索提诺比率计算
**模块位置**: `calc/metrics.py` (补充)

**功能**: 计算索提诺比率（使用下行波动率的夏普比率）

**需要实现的函数**:
```python
def calculate_sortino_ratio(
    annualized_return: float,
    downside_volatility: float,
    risk_free_rate: float = 0.03
) -> float:
    """
    计算索提诺比率
    
    参数:
        annualized_return: 年化收益率（%）
        downside_volatility: 下行波动率（%）
        risk_free_rate: 无风险收益率（小数形式，默认0.03）
    
    返回:
        float: 索提诺比率
    
    计算公式:
        索提诺比率 = (年化收益率 - 无风险收益率) / 下行波动率
    
    注意:
        如果下行波动率为0，返回0或抛出异常
    """
    if downside_volatility == 0:
        return 0.0
    
    # 转换为小数形式
    annualized_return_decimal = annualized_return / 100
    downside_volatility_decimal = downside_volatility / 100
    
    sortino_ratio = (annualized_return_decimal - risk_free_rate) / downside_volatility_decimal
    
    return round(sortino_ratio, 2)
```

---

### 6. 信息比率计算
**模块位置**: `calc/metrics.py` (补充)

**功能**: 计算信息比率（超额收益与跟踪误差的比值）

**需要实现的函数**:
```python
def calculate_information_ratio(
    annualized_active_return: float,
    tracking_error: float
) -> float:
    """
    计算信息比率
    
    参数:
        annualized_active_return: 年化主动收益（%）
        tracking_error: 跟踪误差（%）
    
    返回:
        float: 信息比率
    
    计算公式:
        信息比率 = 年化主动收益 / 跟踪误差
    
    注意:
        如果跟踪误差为0，返回0或抛出异常
    """
    if tracking_error == 0:
        return 0.0
    
    # 转换为小数形式
    annualized_active_return_decimal = annualized_active_return / 100
    tracking_error_decimal = tracking_error / 100
    
    information_ratio = annualized_active_return_decimal / tracking_error_decimal
    
    return round(information_ratio, 2)
```

---

### 7. 最大回撤修复期计算
**模块位置**: `calc/metrics.py` (补充)

**功能**: 计算最大回撤修复期（从回撤结束到净值恢复到峰值的时间）

**需要实现的函数**:
```python
def calculate_drawdown_recovery_period(
    nav_data: List[Dict[str, Any]],
    max_dd_start_date: str,
    max_dd_end_date: str
) -> Dict[str, Any]:
    """
    计算最大回撤修复期
    
    参数:
        nav_data: 净值数据列表
        max_dd_start_date: 最大回撤开始日期
        max_dd_end_date: 最大回撤结束日期
    
    返回:
        Dict: {
            'recovery_period': int,        # 修复期天数（如果已恢复）
            'recovery_date': str,          # 恢复日期（如果已恢复）
            'is_recovered': bool,          # 是否已恢复
            'peak_before_dd': float        # 回撤前峰值
        }
    
    计算逻辑:
        1. 找到回撤开始前的峰值
        2. 找到回撤结束时的净值
        3. 查找净值恢复到峰值的日期
        4. 计算修复期 = 恢复日期 - 回撤结束日期
    """
    from datetime import datetime
    
    # 找到回撤开始前的峰值
    peak_before_dd = 0.0
    for data in nav_data:
        date = data['date']
        nav = data['nav']
        if date < max_dd_start_date:
            if nav > peak_before_dd:
                peak_before_dd = nav
        else:
            break
    
    # 找到回撤结束时的净值
    dd_end_nav = None
    for data in nav_data:
        if data['date'] == max_dd_end_date:
            dd_end_nav = data['nav']
            break
    
    if dd_end_nav is None or peak_before_dd == 0:
        return {
            'recovery_period': None,
            'recovery_date': None,
            'is_recovered': False,
            'peak_before_dd': peak_before_dd
        }
    
    # 查找净值恢复到峰值的日期
    recovery_date = None
    for data in nav_data:
        date = data['date']
        nav = data['nav']
        if date > max_dd_end_date and nav >= peak_before_dd:
            recovery_date = date
            break
    
    if recovery_date:
        # 计算修复期
        end_dt = datetime.strptime(max_dd_end_date, '%Y-%m-%d')
        recovery_dt = datetime.strptime(recovery_date, '%Y-%m-%d')
        recovery_period = (recovery_dt - end_dt).days
        
        return {
            'recovery_period': recovery_period,
            'recovery_date': recovery_date,
            'is_recovered': True,
            'peak_before_dd': peak_before_dd
        }
    else:
        return {
            'recovery_period': None,
            'recovery_date': None,
            'is_recovered': False,
            'peak_before_dd': peak_before_dd
        }
```

---

## 二、多时间段指标计算

### 1. 多时间段收益率计算
**模块位置**: `calc/metrics.py` (补充)

**功能**: 计算多个时间段的收益率（统计期间、近一个月、近三个月等）

**需要实现的函数**:
```python
def calculate_period_returns(
    nav_data: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]]
) -> Dict[str, Dict[str, float]]:
    """
    计算多时间段收益率
    
    参数:
        nav_data: 净值数据列表
        periods: 时间段字典 {
            '统计期间': (start_date, end_date),
            '近一个月': (start_date, end_date),
            '近三个月': (start_date, end_date),
            ...
        }
    
    返回:
        Dict: {
            '统计期间': {
                'period_return': float,
                'annualized_return': float
            },
            ...
        }
    
    用途:
        用于收益分析表格（模版模块实现.md 1.6）
    """
    from datetime import datetime
    
    period_returns = {}
    
    for period_name, (start_date, end_date) in periods.items():
        # 获取该时间段的净值数据
        period_nav_data = [
            data for data in nav_data
            if start_date <= data['date'] <= end_date
        ]
        
        if len(period_nav_data) < 2:
            period_returns[period_name] = {
                'period_return': 0.0,
                'annualized_return': 0.0
            }
            continue
        
        # 计算期间收益率
        start_nav = period_nav_data[0]['nav']
        end_nav = period_nav_data[-1]['nav']
        period_return = ((end_nav - start_nav) / start_nav) * 100
        
        # 计算实际天数
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end_dt - start_dt).days + 1
        
        # 计算年化收益率
        if days > 0:
            annualized_return = ((1 + period_return/100) ** (365/days) - 1) * 100
        else:
            annualized_return = 0.0
        
        period_returns[period_name] = {
            'period_return': round(period_return, 2),
            'annualized_return': round(annualized_return, 2)
        }
    
    return period_returns
```

---

### 2. 多时间段指标计算（完整版）
**模块位置**: `calc/metrics.py` (补充)

**功能**: 计算多个时间段的所有指标（收益率、波动率、回撤等）

**需要实现的函数**:
```python
def calculate_period_metrics(
    nav_data: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
    risk_free_rate: float = 0.03,
    benchmark_returns: List[float] = None
) -> Dict[str, Dict[str, Any]]:
    """
    计算多时间段的所有指标
    
    参数:
        nav_data: 净值数据列表
        periods: 时间段字典
        risk_free_rate: 无风险收益率
        benchmark_returns: 基准收益率序列（可选）
    
    返回:
        Dict: {
            '统计期间': {
                'period_return': float,
                'annualized_return': float,
                'volatility': float,
                'max_drawdown': float,
                'sharpe_ratio': float,
                ...
            },
            ...
        }
    
    用途:
        用于指标分析表格（模版模块实现.md 1.7）
    """
    period_metrics = {}
    
    for period_name, (start_date, end_date) in periods.items():
        # 获取该时间段的净值数据
        period_nav_data = [
            data for data in nav_data
            if start_date <= data['date'] <= end_date
        ]
        
        if len(period_nav_data) < 2:
            period_metrics[period_name] = {
                'period_return': 0.0,
                'annualized_return': 0.0,
                'volatility': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'calmar_ratio': 0.0,
                'tracking_error': 0.0,
                'downside_volatility': 0.0,
                'sortino_ratio': 0.0,
                'information_ratio': 0.0
            }
            continue
        
        # 计算所有指标
        returns_info = calculate_returns(period_nav_data)
        drawdown_info = calculate_max_drawdown(period_nav_data)
        volatility = calculate_volatility(period_nav_data)
        sharpe_ratio = calculate_sharpe_ratio(
            returns_info['annualized_return'],
            volatility,
            risk_free_rate
        )
        calmar_ratio = calculate_calmar_ratio(
            returns_info['annualized_return'],
            drawdown_info['max_drawdown']
        )
        
        # 计算跟踪误差（如果有基准数据）
        tracking_error = 0.0
        if benchmark_returns:
            # 需要筛选对应时间段的基准收益率
            # 简化：假设基准收益率序列已对齐
            tracking_error = calculate_tracking_error(period_nav_data, benchmark_returns)
        
        # 计算下行波动率
        downside_volatility = calculate_downside_volatility(period_nav_data)
        
        # 计算索提诺比率
        sortino_ratio = calculate_sortino_ratio(
            returns_info['annualized_return'],
            downside_volatility,
            risk_free_rate
        )
        
        # 计算信息比率（需要主动收益）
        information_ratio = 0.0
        if benchmark_returns and tracking_error > 0:
            # 计算基准期间收益率
            # 简化：假设已计算
            active_return = calculate_active_return(
                returns_info['period_return'],
                0.0,  # 基准收益率需要单独计算
                returns_info['days']
            )
            information_ratio = calculate_information_ratio(
                active_return['annualized_active_return'],
                tracking_error
            )
        
        period_metrics[period_name] = {
            'period_return': returns_info['period_return'],
            'annualized_return': returns_info['annualized_return'],
            'volatility': volatility,
            'max_drawdown': drawdown_info['max_drawdown'],
            'sharpe_ratio': sharpe_ratio,
            'calmar_ratio': calmar_ratio,
            'tracking_error': tracking_error,
            'downside_volatility': downside_volatility,
            'sortino_ratio': sortino_ratio,
            'information_ratio': information_ratio
        }
    
    return period_metrics
```

---

## 三、基准指数相关计算

### 1. 基准指数累计收益率计算
**模块位置**: `calc/benchmark.py` (新建)

**功能**: 计算基准指数的累计收益率序列

**需要实现的函数**:
```python
def calculate_benchmark_cumulative_returns(
    benchmark_data: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    计算基准指数累计收益率序列
    
    参数:
        benchmark_data: 基准指数DataFrame（包含trade_date和close列）
    
    返回:
        List[Dict]: [{
            'date': str,
            'cumulative_return': float  # 累计收益率（%）
        }, ...]
    
    计算公式:
        累计收益率 = (当前价格 - 初始价格) / 初始价格 × 100%
    """
    if benchmark_data.empty:
        return []
    
    initial_price = benchmark_data.iloc[0]['close']
    cumulative_data = []
    
    for _, row in benchmark_data.iterrows():
        date = row['trade_date']
        price = row['close']
        
        cumulative_return = ((price - initial_price) / initial_price) * 100
        
        cumulative_data.append({
            'date': date,
            'cumulative_return': round(cumulative_return, 2)
        })
    
    return cumulative_data
```

---

### 2. 基准指数回撤计算
**模块位置**: `calc/benchmark.py` (新建)

**功能**: 计算基准指数的回撤序列

**需要实现的函数**:
```python
def calculate_benchmark_drawdowns(
    benchmark_data: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    计算基准指数回撤序列
    
    参数:
        benchmark_data: 基准指数DataFrame
    
    返回:
        List[Dict]: [{
            'date': str,
            'drawdown': float  # 回撤（%）
        }, ...]
    
    计算公式:
        回撤 = (峰值 - 当前值) / 峰值 × 100%
    """
    if benchmark_data.empty:
        return []
    
    drawdowns = []
    peak_price = benchmark_data.iloc[0]['close']
    
    for _, row in benchmark_data.iterrows():
        date = row['trade_date']
        price = row['close']
        
        # 更新峰值
        if price > peak_price:
            peak_price = price
        
        # 计算回撤
        if peak_price > 0:
            drawdown = ((peak_price - price) / peak_price) * 100
        else:
            drawdown = 0.0
        
        drawdowns.append({
            'date': date,
            'drawdown': round(drawdown, 2)
        })
    
    return drawdowns
```

---

### 3. 累计超额收益计算
**模块位置**: `calc/benchmark.py` (新建)

**功能**: 计算产品相对基准的累计超额收益

**需要实现的函数**:
```python
def calculate_cumulative_excess_returns(
    product_cumulative_returns: List[Dict[str, Any]],
    benchmark_cumulative_returns: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    计算累计超额收益
    
    参数:
        product_cumulative_returns: 产品累计收益率列表 [{date, cumulative_return}, ...]
        benchmark_cumulative_returns: 基准累计收益率列表 [{date, cumulative_return}, ...]
    
    返回:
        List[Dict]: [{
            'date': str,
            'excess_return': float  # 累计超额收益（%）
        }, ...]
    
    计算公式:
        累计超额收益 = 产品累计收益 - 基准累计收益
    """
    # 建立日期映射
    benchmark_dict = {item['date']: item['cumulative_return'] 
                     for item in benchmark_cumulative_returns}
    
    excess_returns = []
    
    for product_data in product_cumulative_returns:
        date = product_data['date']
        product_ret = product_data['cumulative_return']
        
        # 获取对应日期的基准收益
        benchmark_ret = benchmark_dict.get(date, 0.0)
        
        excess_return = product_ret - benchmark_ret
        
        excess_returns.append({
            'date': date,
            'excess_return': round(excess_return, 2)
        })
    
    return excess_returns
```

---

## 四、数据输出格式补充

### 1. 更新calculate_all_metrics()函数
需要包含所有新增指标：

```python
def calculate_all_metrics(
    nav_data: List[Dict[str, Any]],
    risk_free_rate: float = 0.03,
    benchmark_returns: List[float] = None,
    benchmark_period_return: float = None
) -> Dict[str, Any]:
    """
    计算所有指标（完整版，包含新增指标）
    
    返回:
        Dict: {
            # 原有指标
            'period_return': float,
            'annualized_return': float,
            'max_drawdown': float,
            'volatility': float,
            'sharpe_ratio': float,
            'calmar_ratio': float,
            ...
            
            # 新增指标
            'beta': float,                    # β值
            'active_return': float,            # 主动收益（%）
            'annualized_active_return': float, # 年化主动收益（%）
            'tracking_error': float,          # 跟踪误差（%）
            'downside_volatility': float,     # 下行波动率（%）
            'sortino_ratio': float,           # 索提诺比率
            'information_ratio': float,       # 信息比率
            'recovery_period': int,            # 最大回撤修复期（天）
            'recovery_date': str,             # 恢复日期
            'is_recovered': bool              # 是否已恢复
        }
    """
    # 原有计算...
    
    # 新增指标计算
    beta = 1.0
    if benchmark_returns:
        beta = calculate_beta(nav_data, benchmark_returns)
    
    active_return_info = {'active_return': 0.0, 'annualized_active_return': 0.0}
    if benchmark_period_return is not None:
        returns_info = calculate_returns(nav_data)
        active_return_info = calculate_active_return(
            returns_info['period_return'],
            benchmark_period_return,
            returns_info['days']
        )
    
    tracking_error = 0.0
    if benchmark_returns:
        tracking_error = calculate_tracking_error(nav_data, benchmark_returns)
    
    downside_volatility = calculate_downside_volatility(nav_data)
    
    volatility = calculate_volatility(nav_data)
    returns_info = calculate_returns(nav_data)
    drawdown_info = calculate_max_drawdown(nav_data)
    
    sortino_ratio = calculate_sortino_ratio(
        returns_info['annualized_return'],
        downside_volatility,
        risk_free_rate
    )
    
    information_ratio = 0.0
    if tracking_error > 0:
        information_ratio = calculate_information_ratio(
            active_return_info['annualized_active_return'],
            tracking_error
        )
    
    # 计算最大回撤修复期
    recovery_info = calculate_drawdown_recovery_period(
        nav_data,
        drawdown_info['max_dd_start_date'],
        drawdown_info['max_dd_end_date']
    )
    
    return {
        # 原有指标
        'period_return': returns_info['period_return'],
        'annualized_return': returns_info['annualized_return'],
        'max_drawdown': drawdown_info['max_drawdown'],
        'volatility': volatility,
        'sharpe_ratio': calculate_sharpe_ratio(
            returns_info['annualized_return'],
            volatility,
            risk_free_rate
        ),
        'calmar_ratio': calculate_calmar_ratio(
            returns_info['annualized_return'],
            drawdown_info['max_drawdown']
        ),
        # 新增指标
        'beta': beta,
        'active_return': active_return_info['active_return'],
        'annualized_active_return': active_return_info['annualized_active_return'],
        'tracking_error': tracking_error,
        'downside_volatility': downside_volatility,
        'sortino_ratio': sortino_ratio,
        'information_ratio': information_ratio,
        'recovery_period': recovery_info['recovery_period'],
        'recovery_date': recovery_info['recovery_date'],
        'is_recovered': recovery_info['is_recovered']
    }
```

---

### 2. 格式化函数补充
更新`format_metrics_for_pdf()`函数，包含新增指标：

```python
def format_metrics_for_pdf(metrics: Dict[str, Any]) -> List[List[str]]:
    """
    将指标数据转换为PDF表格格式（包含新增指标）
    """
    table_data = []
    table_data.append(['指标名称', '数值'])
    
    # 原有指标...
    
    # 新增指标
    if 'beta' in metrics:
        table_data.append(['β值', f"{metrics['beta']:.4f}"])
    
    if 'active_return' in metrics:
        table_data.append([
            '主动收益',
            f"{metrics['active_return']:.2f}% (年化 {metrics['annualized_active_return']:.2f}%)"
        ])
    
    if 'tracking_error' in metrics:
        table_data.append(['跟踪误差', f"{metrics['tracking_error']:.2f}%"])
    
    if 'downside_volatility' in metrics:
        table_data.append(['下行波动率', f"{metrics['downside_volatility']:.2f}%"])
    
    if 'sortino_ratio' in metrics:
        table_data.append(['索提诺比率', f"{metrics['sortino_ratio']:.2f}"])
    
    if 'information_ratio' in metrics:
        table_data.append(['信息比率', f"{metrics['information_ratio']:.2f}"])
    
    return table_data
```

---

## 五、任务优先级

### 高优先级（必须实现）
1. ✅ β值计算
2. ✅ 主动收益计算
3. ✅ 跟踪误差计算
4. ✅ 下行波动率计算
5. ✅ 索提诺比率计算
6. ✅ 信息比率计算
7. ✅ 多时间段指标计算

### 中优先级（重要功能）
8. ⚠️ 最大回撤修复期计算
9. ⚠️ 基准指数累计收益率计算
10. ⚠️ 基准指数回撤计算
11. ⚠️ 累计超额收益计算

---

## 六、注意事项

1. **基准数据依赖**: 新增指标大部分需要基准指数数据，需要与开发者A协调获取
2. **数据对齐**: 确保产品收益率和基准收益率序列的日期对齐
3. **边界处理**: 所有新增函数都要处理边界情况（数据不足、除零等）
4. **性能考虑**: 多时间段计算时避免重复计算，使用缓存机制

---

**文档版本**: v1.0  
**创建日期**: 2024年  
**最后更新**: 2024年

