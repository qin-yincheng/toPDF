# 开发者B详细工作文档

## 职责概述

开发者B负责**计算层与分析层**，是整个系统的业务逻辑核心。主要工作包括：
1. 净值计算（每日净值、单位净值）
2. 收益率计算（期间收益率、年化收益率、日收益率）
3. 风险指标计算（最大回撤、波动率、夏普比率）
4. 工具函数（日期处理、数据验证）
5. 多时间段指标计算
6. 数据格式转换（为PDF生成准备）

**总工作量**：18小时（Day1: 8h, Day2: 6h, Day3: 4h）

---

## Day 1 任务详解

### 任务B1：工具函数模块 [2小时]

#### 模块位置
`calc/utils.py`

#### 详细要求

##### 1. 日期工具函数
**函数**：`generate_date_range()`

**功能**：生成日期范围列表

**实现**：
```python
from datetime import datetime, timedelta
from typing import List

def generate_date_range(start_date: str, end_date: str) -> List[str]:
    """
    生成日期范围列表（包含所有日期，包括周末）
    
    参数:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
    
    返回:
        List[str]: 日期列表，格式 'YYYY-MM-DD'
    
    注意:
        包含所有日期，后续由交易日判断函数过滤
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    return date_list
```

##### 2. 交易日判断
**函数**：`is_trading_day()`

**功能**：判断是否为交易日（简化版本）

**实现**：
```python
def is_trading_day(date: str) -> bool:
    """
    判断是否为交易日（简化版本）
    
    参数:
        date: 日期（YYYY-MM-DD）
    
    返回:
        bool: 是否为交易日
    
    简化逻辑:
        1. 周末不是交易日
        2. 节假日暂时不考虑（MVP版本）
    
    注意:
        完整版本需要维护交易日历，MVP版本只判断周末
    """
    dt = datetime.strptime(date, '%Y-%m-%d')
    weekday = dt.weekday()  # 0=周一, 6=周日
    
    # 周末不是交易日
    if weekday >= 5:  # 周六(5)或周日(6)
        return False
    
    return True
```

##### 3. 获取最近交易日
**函数**：`get_nearest_trading_day()`

**功能**：获取最近的交易日

**实现**：
```python
def get_nearest_trading_day(date: str, direction: str = 'backward') -> str:
    """
    获取最近的交易日
    
    参数:
        date: 日期（YYYY-MM-DD）
        direction: 'backward'（向前找）或 'forward'（向后找）
    
    返回:
        str: 最近的交易日（YYYY-MM-DD）
    
    用途:
        处理非交易日，获取可用价格
    """
    dt = datetime.strptime(date, '%Y-%m-%d')
    
    if is_trading_day(date):
        return date
    
    # 向前找最近的交易日
    if direction == 'backward':
        while not is_trading_day(dt.strftime('%Y-%m-%d')):
            dt -= timedelta(days=1)
    else:
        while not is_trading_day(dt.strftime('%Y-%m-%d')):
            dt += timedelta(days=1)
    
    return dt.strftime('%Y-%m-%d')
```

---

### 任务B2：指标计算模块 [6小时]

#### 模块位置
`calc/metrics.py`

#### 详细要求

##### 1. 净值计算
**函数**：`calculate_nav()`

**计算公式**（根据模版模块实现.md 1.1和1.3）：
```
单位净值 = 总资产 / 初始资金
累计净值 = 单位净值（假设初始净值为1.0）
```

**实现**：
```python
from typing import List, Dict, Any
import numpy as np

def calculate_nav(
    daily_positions: List[Dict[str, Any]], 
    initial_capital: float = 1000.0
) -> List[Dict[str, Any]]:
    """
    计算每日净值
    
    参数:
        daily_positions: 每日持仓列表（来自开发者A）
            [{date, positions, total_assets, stock_value, cash}, ...]
        initial_capital: 初始资金（万元），默认1000万
    
    返回:
        List[Dict]: 净值数据列表
            [{date: str, nav: float, total_assets: float}, ...]
    
    计算公式:
        单位净值 = 总资产 / 初始资金
        假设初始净值为1.0
    
    注意:
        净值保留4位小数
    """
    nav_data = []
    
    for daily_data in daily_positions:
        total_assets = daily_data['total_assets']
        nav = total_assets / initial_capital
        
        nav_data.append({
            'date': daily_data['date'],
            'nav': round(nav, 4),
            'total_assets': total_assets
        })
    
    return nav_data
```

##### 2. 获取指定日期净值
**函数**：`get_nav_on_date()`

**功能**：从净值数据列表中获取指定日期的净值

**实现**：
```python
def get_nav_on_date(nav_data: List[Dict[str, Any]], target_date: str) -> float:
    """
    获取指定日期的净值
    
    参数:
        nav_data: 净值数据列表
        target_date: 目标日期（YYYY-MM-DD）
    
    返回:
        float: 净值，如果找不到返回None
    
    注意:
        如果找不到精确日期，返回最近一个交易日的净值
    """
    for data in nav_data:
        if data['date'] == target_date:
            return data['nav']
    
    # 如果找不到，返回最近一个交易日的净值
    # 简化：返回最后一个净值
    if nav_data:
        return nav_data[-1]['nav']
    
    return None
```

##### 3. 收益率计算
**函数**：`calculate_returns()`

**计算公式**（根据模版模块实现.md 1.2.1）：
```
期间收益率 = (期末净值 - 期初净值) / 期初净值 × 100%
年化收益率 = ((1 + 期间收益率/100) ^ (365 / 实际天数)) - 1 × 100%
```

**实现**：
```python
def calculate_returns(nav_data: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    计算收益率指标
    
    参数:
        nav_data: 净值数据列表
            [{date, nav, total_assets}, ...]
    
    返回:
        Dict: {
            'period_return': float,      # 期间收益率（%）
            'annualized_return': float,  # 年化收益率（%）
            'start_date': str,           # 期初日期
            'end_date': str,             # 期末日期
            'days': int                  # 实际天数
        }
    
    计算公式:
        1. 期间收益率 = (期末净值 - 期初净值) / 期初净值 × 100%
        2. 年化收益率 = ((1 + 期间收益率/100) ^ (365 / 实际天数)) - 1 × 100%
    
    注意:
        - 期初净值：第一个交易日的净值
        - 期末净值：最后一个交易日的净值
        - 实际天数：报告期间的实际天数（不是交易日数）
    """
    if not nav_data or len(nav_data) < 2:
        return {
            'period_return': 0.0,
            'annualized_return': 0.0,
            'start_date': '',
            'end_date': '',
            'days': 0
        }
    
    start_nav = nav_data[0]['nav']
    end_nav = nav_data[-1]['nav']
    start_date = nav_data[0]['date']
    end_date = nav_data[-1]['date']
    
    # 计算实际天数
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    days = (end_dt - start_dt).days + 1  # 包含首尾两天
    
    # 计算期间收益率
    period_return = ((end_nav - start_nav) / start_nav) * 100
    
    # 计算年化收益率
    if days > 0:
        annualized_return = ((1 + period_return/100) ** (365/days) - 1) * 100
    else:
        annualized_return = 0.0
    
    return {
        'period_return': round(period_return, 2),
        'annualized_return': round(annualized_return, 2),
        'start_date': start_date,
        'end_date': end_date,
        'days': days
    }
```

##### 4. 日收益率序列计算
**函数**：`calculate_daily_returns()`

**功能**：计算每日收益率序列（用于波动率计算）

**计算公式**（根据模版模块实现.md 1.2.4）：
```
日收益率 = (当日净值 - 前一日净值) / 前一日净值
```

**实现**：
```python
def calculate_daily_returns(nav_data: List[Dict[str, Any]]) -> List[float]:
    """
    计算日收益率序列
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        List[float]: 日收益率列表（小数形式，如0.01表示1%）
    
    计算公式:
        日收益率 = (当日净值 - 前一日净值) / 前一日净值
    
    注意:
        第一个交易日没有日收益率（返回空列表或跳过）
    """
    daily_returns = []
    
    for i in range(1, len(nav_data)):
        nav_today = nav_data[i]['nav']
        nav_yesterday = nav_data[i-1]['nav']
        
        if nav_yesterday > 0:
            daily_return = (nav_today - nav_yesterday) / nav_yesterday
            daily_returns.append(daily_return)
        else:
            daily_returns.append(0.0)
    
    return daily_returns
```

##### 5. 最大回撤计算
**函数**：`calculate_max_drawdown()`

**计算公式**（根据模版模块实现.md 1.2.3和8.3.1）：
```
最大回撤 = max((峰值 - 当前值) / 峰值 × 100%)
```

**实现**：
```python
def calculate_max_drawdown(nav_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    计算最大回撤
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        Dict: {
            'max_drawdown': float,      # 最大回撤（%）
            'max_dd_start_date': str,   # 最大回撤开始日期
            'max_dd_end_date': str,     # 最大回撤结束日期
            'peak_date': str,            # 峰值日期
            'peak_nav': float           # 峰值净值
        }
    
    计算公式:
        最大回撤 = max((峰值 - 当前值) / 峰值 × 100%)
    
    逻辑:
        1. 维护峰值历史
        2. 计算每个时间点的回撤
        3. 找出最大回撤及其区间
    """
    if not nav_data or len(nav_data) < 2:
        return {
            'max_drawdown': 0.0,
            'max_dd_start_date': '',
            'max_dd_end_date': '',
            'peak_date': '',
            'peak_nav': 0.0
        }
    
    max_drawdown = 0.0
    peak_nav = nav_data[0]['nav']
    peak_date = nav_data[0]['date']
    max_dd_start_date = ''
    max_dd_end_date = ''
    dd_start_date = ''
    
    for data in nav_data:
        date = data['date']
        nav = data['nav']
        
        # 更新峰值
        if nav > peak_nav:
            peak_nav = nav
            peak_date = date
            dd_start_date = ''  # 重置回撤开始日期
        
        # 计算回撤
        if peak_nav > 0:
            drawdown = ((peak_nav - nav) / peak_nav) * 100
            
            # 记录回撤开始日期
            if drawdown > 0 and not dd_start_date:
                dd_start_date = peak_date
            
            # 更新最大回撤
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_dd_start_date = dd_start_date if dd_start_date else peak_date
                max_dd_end_date = date
    
    return {
        'max_drawdown': round(max_drawdown, 2),
        'max_dd_start_date': max_dd_start_date,
        'max_dd_end_date': max_dd_end_date,
        'peak_date': peak_date,
        'peak_nav': peak_nav
    }
```

##### 6. 每日回撤计算
**函数**：`calculate_daily_drawdowns()`

**功能**：计算每日回撤序列（用于绘制回撤图）

**实现**：
```python
def calculate_daily_drawdowns(nav_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    计算每日回撤序列
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        List[Dict]: [{date, drawdown, peak_nav}, ...]
        回撤值（%），正值表示回撤
    
    用途:
        供开发者C绘制回撤图
    """
    drawdowns = []
    peak_nav = nav_data[0]['nav'] if nav_data else 1.0
    
    for data in nav_data:
        date = data['date']
        nav = data['nav']
        
        # 更新峰值
        if nav > peak_nav:
            peak_nav = nav
        
        # 计算回撤
        if peak_nav > 0:
            drawdown = ((peak_nav - nav) / peak_nav) * 100
        else:
            drawdown = 0.0
        
        drawdowns.append({
            'date': date,
            'drawdown': round(drawdown, 2),
            'peak_nav': peak_nav
        })
    
    return drawdowns
```

##### 7. 波动率计算
**函数**：`calculate_volatility()`

**计算公式**（根据模版模块实现.md 1.2.4和8.3.2）：
```
年化波动率 = std(日收益率) × sqrt(252) × 100%
```

**实现**：
```python
def calculate_volatility(nav_data: List[Dict[str, Any]]) -> float:
    """
    计算年化波动率
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        float: 年化波动率（%）
    
    计算公式:
        年化波动率 = std(日收益率) × sqrt(252) × 100%
    
    注意:
        - 252是一年的交易日数
        - 需要先计算日收益率序列
        - 如果数据不足，返回0
    """
    daily_returns = calculate_daily_returns(nav_data)
    
    if len(daily_returns) < 2:
        return 0.0
    
    # 计算标准差
    std_returns = np.std(daily_returns)
    
    # 年化波动率
    annualized_volatility = std_returns * np.sqrt(252) * 100
    
    return round(annualized_volatility, 2)
```

##### 8. 夏普比率计算
**函数**：`calculate_sharpe_ratio()`

**计算公式**（根据模版模块实现.md 1.2.5和8.3.3）：
```
夏普比率 = (年化收益率 - 无风险收益率) / 年化波动率
```

**实现**：
```python
def calculate_sharpe_ratio(
    annualized_return: float, 
    volatility: float, 
    risk_free_rate: float = 0.03
) -> float:
    """
    计算夏普比率
    
    参数:
        annualized_return: 年化收益率（%）
        volatility: 年化波动率（%）
        risk_free_rate: 无风险收益率（小数形式，默认0.03即3%）
    
    返回:
        float: 夏普比率
    
    计算公式:
        夏普比率 = (年化收益率 - 无风险收益率) / 年化波动率
    
    注意:
        - 如果波动率为0，返回0或抛出异常
        - 年化收益率需要转换为小数形式（除以100）
    """
    if volatility == 0:
        return 0.0
    
    # 转换为小数形式
    annualized_return_decimal = annualized_return / 100
    
    sharpe_ratio = (annualized_return_decimal - risk_free_rate) / (volatility / 100)
    
    return round(sharpe_ratio, 2)
```

##### 9. 卡玛比率计算
**函数**：`calculate_calmar_ratio()`

**计算公式**（根据模版模块实现.md 1.2.6和8.3.4）：
```
卡玛比率 = 年化收益率 / 最大回撤（绝对值）
```

**实现**：
```python
def calculate_calmar_ratio(
    annualized_return: float,
    max_drawdown: float
) -> float:
    """
    计算卡玛比率
    
    参数:
        annualized_return: 年化收益率（%）
        max_drawdown: 最大回撤（%）
    
    返回:
        float: 卡玛比率
    
    计算公式:
        卡玛比率 = 年化收益率 / 最大回撤（绝对值）
    
    注意:
        - 如果最大回撤为0，返回0或抛出异常
        - 年化收益率需要转换为小数形式
    """
    if max_drawdown == 0:
        return 0.0
    
    # 转换为小数形式
    annualized_return_decimal = annualized_return / 100
    max_drawdown_abs = abs(max_drawdown) / 100
    
    calmar_ratio = annualized_return_decimal / max_drawdown_abs
    
    return round(calmar_ratio, 2)
```

##### 10. 日收益率统计
**函数**：`calculate_daily_return_stats()`

**功能**：计算单日最大收益、单日最大亏损（根据模版模块实现.md 1.5）

**实现**：
```python
def calculate_daily_return_stats(nav_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    计算日收益率统计
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        Dict: {
            'max_daily_return': float,      # 单日最大收益（%）
            'max_daily_loss': float,        # 单日最大亏损（%）
            'max_return_date': str,         # 最大收益日期
            'max_loss_date': str           # 最大亏损日期
        }
    
    计算公式:
        日收益率 = (当日净值 - 前一日净值) / 前一日净值 × 100%
    """
    daily_returns = calculate_daily_returns(nav_data)
    
    if not daily_returns:
        return {
            'max_daily_return': 0.0,
            'max_daily_loss': 0.0,
            'max_return_date': '',
            'max_loss_date': ''
        }
    
    # 转换为百分比
    daily_returns_pct = [r * 100 for r in daily_returns]
    
    max_return = max(daily_returns_pct)
    max_loss = min(daily_returns_pct)
    
    # 找到对应日期
    max_return_idx = daily_returns_pct.index(max_return)
    max_loss_idx = daily_returns_pct.index(max_loss)
    
    max_return_date = nav_data[max_return_idx + 1]['date']  # +1因为第一个交易日没有日收益率
    max_loss_date = nav_data[max_loss_idx + 1]['date']
    
    return {
        'max_daily_return': round(max_return, 2),
        'max_daily_loss': round(max_loss, 2),
        'max_return_date': max_return_date,
        'max_loss_date': max_loss_date
    }
```

##### 11. 累计收益率计算
**函数**：`calculate_cumulative_returns()`

**计算公式**（根据模版模块实现.md 1.4.1和1.5）：
```
累计收益率 = (单位净值 - 1) × 100%
复权累计收益 = (单位净值 - 1) × 100%
```

**实现**：
```python
def calculate_cumulative_returns(nav_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    计算累计收益率序列
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        List[Dict]: [{date, nav, cumulative_return}, ...]
        累计收益率（%）
    
    计算公式:
        累计收益率 = (单位净值 - 1) × 100%
    
    用途:
        用于绘制净值走势图
    """
    cumulative_data = []
    
    for data in nav_data:
        nav = data['nav']
        cumulative_return = (nav - 1.0) * 100
        
        cumulative_data.append({
            'date': data['date'],
            'nav': nav,
            'cumulative_return': round(cumulative_return, 2)
        })
    
    return cumulative_data
```

##### 12. 周胜率和月胜率计算
**函数**：`calculate_weekly_win_rate()` 和 `calculate_monthly_win_rate()`

**计算公式**（根据模版模块实现.md 8.3.5和8.3.6）：
```
周胜率 = 盈利周数 / 总周数 × 100%
月胜率 = 盈利月数 / 总月数 × 100%
```

**实现**：
```python
def calculate_weekly_win_rate(nav_data: List[Dict[str, Any]]) -> float:
    """
    计算周胜率
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        float: 周胜率（%）
    
    计算公式:
        周胜率 = 盈利周数 / 总周数 × 100%
    
    逻辑:
        1. 按周聚合净值数据
        2. 计算每周的收益率
        3. 统计盈利周数
    """
    from datetime import datetime, timedelta
    
    if len(nav_data) < 2:
        return 0.0
    
    # 按周聚合
    weekly_data = {}
    for data in nav_data:
        date = datetime.strptime(data['date'], '%Y-%m-%d')
        # 获取该周的周一日期作为周标识
        week_start = date - timedelta(days=date.weekday())
        week_key = week_start.strftime('%Y-%m-%d')
        
        if week_key not in weekly_data:
            weekly_data[week_key] = []
        weekly_data[week_key].append(data)
    
    # 计算每周收益率
    winning_weeks = 0
    total_weeks = 0
    
    for week_key, week_data in weekly_data.items():
        if len(week_data) < 2:
            continue
        
        week_data_sorted = sorted(week_data, key=lambda x: x['date'])
        start_nav = week_data_sorted[0]['nav']
        end_nav = week_data_sorted[-1]['nav']
        
        if start_nav > 0:
            week_return = (end_nav - start_nav) / start_nav
            if week_return > 0:
                winning_weeks += 1
            total_weeks += 1
    
    win_rate = (winning_weeks / total_weeks * 100) if total_weeks > 0 else 0.0
    
    return round(win_rate, 2)


def calculate_monthly_win_rate(nav_data: List[Dict[str, Any]]) -> float:
    """
    计算月胜率
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        float: 月胜率（%）
    
    计算公式:
        月胜率 = 盈利月数 / 总月数 × 100%
    """
    from datetime import datetime
    import calendar
    
    if len(nav_data) < 2:
        return 0.0
    
    # 按月聚合
    monthly_data = {}
    for data in nav_data:
        date = datetime.strptime(data['date'], '%Y-%m-%d')
        month_key = date.strftime('%Y-%m')
        
        if month_key not in monthly_data:
            monthly_data[month_key] = []
        monthly_data[month_key].append(data)
    
    # 计算每月收益率
    winning_months = 0
    total_months = 0
    
    for month_key, month_data in monthly_data.items():
        if len(month_data) < 2:
            continue
        
        month_data_sorted = sorted(month_data, key=lambda x: x['date'])
        start_nav = month_data_sorted[0]['nav']
        end_nav = month_data_sorted[-1]['nav']
        
        if start_nav > 0:
            month_return = (end_nav - start_nav) / start_nav
            if month_return > 0:
                winning_months += 1
            total_months += 1
    
    win_rate = (winning_months / total_months * 100) if total_months > 0 else 0.0
    
    return round(win_rate, 2)
```

##### 13. 月度收益率计算
**函数**：`calculate_monthly_returns()`

**功能**：计算月度收益率和月度累计收益率（根据模版模块实现.md 7.1.5）

**实现**：
```python
def calculate_monthly_returns(nav_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    计算月度收益率和累计收益率
    
    参数:
        nav_data: 净值数据列表
    
    返回:
        List[Dict]: [{month, start_nav, end_nav, monthly_return, cumulative_return}, ...]
    
    计算公式:
        月度收益率 = (月末净值 - 月初净值) / 月初净值 × 100%
        月度累计收益率 = (月末净值 - 初始净值) / 初始净值 × 100%
    """
    from datetime import datetime
    
    if not nav_data:
        return []
    
    initial_nav = nav_data[0]['nav']
    
    # 按月聚合
    monthly_data = {}
    for data in nav_data:
        date = datetime.strptime(data['date'], '%Y-%m-%d')
        month_key = date.strftime('%Y-%m')
        
        if month_key not in monthly_data:
            monthly_data[month_key] = []
        monthly_data[month_key].append(data)
    
    monthly_returns = []
    
    for month_key in sorted(monthly_data.keys()):
        month_data = sorted(monthly_data[month_key], key=lambda x: x['date'])
        
        if len(month_data) < 2:
            continue
        
        start_nav = month_data[0]['nav']
        end_nav = month_data[-1]['nav']
        
        # 月度收益率
        monthly_return = ((end_nav - start_nav) / start_nav * 100) if start_nav > 0 else 0.0
        
        # 月度累计收益率
        cumulative_return = ((end_nav - initial_nav) / initial_nav * 100) if initial_nav > 0 else 0.0
        
        monthly_returns.append({
            'month': month_key,
            'start_nav': start_nav,
            'end_nav': end_nav,
            'monthly_return': round(monthly_return, 2),
            'cumulative_return': round(cumulative_return, 2)
        })
    
    return monthly_returns
```

##### 14. 综合指标计算（完整版）
**函数**：`calculate_all_metrics()`

**功能**：计算所有指标，返回指标字典（包含所有必需参数）

**实现**：
```python
def calculate_all_metrics(
    nav_data: List[Dict[str, Any]],
    risk_free_rate: float = 0.03
) -> Dict[str, Any]:
    """
    计算所有指标（完整版，包含所有必需参数）
    
    参数:
        nav_data: 净值数据列表
        risk_free_rate: 无风险收益率（默认3%）
    
    返回:
        Dict: {
            'period_return': float,        # 期间收益率（%）
            'annualized_return': float,    # 年化收益率（%）
            'max_drawdown': float,         # 最大回撤（%）
            'volatility': float,           # 年化波动率（%）
            'sharpe_ratio': float,         # 夏普比率
            'calmar_ratio': float,         # 卡玛比率
            'max_daily_return': float,     # 单日最大收益（%）
            'max_daily_loss': float,       # 单日最大亏损（%）
            'weekly_win_rate': float,      # 周胜率（%）
            'monthly_win_rate': float,     # 月胜率（%）
            'start_date': str,
            'end_date': str,
            'days': int
        }
    
    用途:
        供开发者C生成PDF业绩统计表格
    """
    # 计算收益率
    returns = calculate_returns(nav_data)
    
    # 计算最大回撤
    drawdown_info = calculate_max_drawdown(nav_data)
    
    # 计算波动率
    volatility = calculate_volatility(nav_data)
    
    # 计算夏普比率
    sharpe_ratio = calculate_sharpe_ratio(
        returns['annualized_return'],
        volatility,
        risk_free_rate
    )
    
    # 计算卡玛比率
    calmar_ratio = calculate_calmar_ratio(
        returns['annualized_return'],
        drawdown_info['max_drawdown']
    )
    
    # 计算日收益率统计
    daily_stats = calculate_daily_return_stats(nav_data)
    
    # 计算周胜率和月胜率
    weekly_win_rate = calculate_weekly_win_rate(nav_data)
    monthly_win_rate = calculate_monthly_win_rate(nav_data)
    
    return {
        'period_return': returns['period_return'],
        'annualized_return': returns['annualized_return'],
        'max_drawdown': drawdown_info['max_drawdown'],
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'calmar_ratio': calmar_ratio,
        'max_daily_return': daily_stats['max_daily_return'],
        'max_daily_loss': daily_stats['max_daily_loss'],
        'max_return_date': daily_stats['max_return_date'],
        'max_loss_date': daily_stats['max_loss_date'],
        'weekly_win_rate': weekly_win_rate,
        'monthly_win_rate': monthly_win_rate,
        'start_date': returns['start_date'],
        'end_date': returns['end_date'],
        'days': returns['days']
    }
```

#### 测试要求
- 测试净值计算准确性
- 测试收益率计算（与手动计算对比）
- 测试最大回撤计算（包括峰值更新逻辑）
- 测试波动率计算（使用已知数据验证）
- 测试夏普比率计算（边界情况：波动率为0）
- 测试空数据、单日数据等边界情况

---

## Day 2 任务详解

### 任务B3：集成测试 [2小时]

#### 目标
与开发者A的持仓计算模块集成，确保数据格式匹配

#### 测试内容
1. **数据格式验证**
   - 检查每日持仓数据格式是否符合要求
   - 验证total_assets字段是否正确

2. **计算准确性验证**
   - 手动计算几天的净值，对比程序结果
   - 验证收益率计算是否正确
   - 验证回撤计算逻辑

3. **数据流转测试**
   - 从A的模块获取数据
   - 计算指标
   - 验证输出格式

#### 修复工作
- 修复数据格式不匹配问题
- 修复计算bug
- 优化计算性能

---

### 任务B4：补充计算函数 [2小时]

#### 补充内容

##### 1. 日期范围生成（完善）
```python
def generate_trading_date_range(start_date: str, end_date: str) -> List[str]:
    """
    生成交易日范围列表（只包含交易日）
    
    用途:
        用于计算每日数据时，只处理交易日
    """
    all_dates = generate_date_range(start_date, end_date)
    trading_dates = [d for d in all_dates if is_trading_day(d)]
    return trading_dates
```

##### 2. 数据验证函数
```python
def validate_nav_data(nav_data: List[Dict[str, Any]]) -> bool:
    """
    验证净值数据
    
    验证项:
        1. 净值数据不为空
        2. 净值必须为正数
        3. 日期格式正确
        4. 净值序列单调性检查（可选）
    """
    if not nav_data:
        return False
    
    for data in nav_data:
        if data['nav'] <= 0:
            return False
        # 验证日期格式
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except:
            return False
    
    return True
```

##### 3. 期间收益计算
```python
def calculate_period_profit(
    nav_data: List[Dict[str, Any]],
    initial_capital: float = 1000.0
) -> Dict[str, float]:
    """
    计算期间收益（绝对收益）
    
    计算公式（根据模版模块实现.md 1.2.2）:
        期间收益 = 期末资产 - 期初资产
        年化收益 = 期间收益 × (365 / 实际天数)
    
    返回:
        {
            'period_profit': float,      # 期间收益（万元）
            'annualized_profit': float   # 年化收益（万元）
        }
    """
    if not nav_data:
        return {'period_profit': 0.0, 'annualized_profit': 0.0}
    
    start_assets = nav_data[0]['total_assets']
    end_assets = nav_data[-1]['total_assets']
    period_profit = end_assets - start_assets
    
    # 计算实际天数
    start_date = nav_data[0]['date']
    end_date = nav_data[-1]['date']
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    days = (end_dt - start_dt).days + 1
    
    # 年化收益
    if days > 0:
        annualized_profit = period_profit * (365 / days)
    else:
        annualized_profit = 0.0
    
    return {
        'period_profit': round(period_profit, 2),
        'annualized_profit': round(annualized_profit, 2)
    }
```

---

### 任务B5：代码优化与数据格式准备 [2小时]

#### 代码优化
1. **性能优化**
   - 使用numpy向量化操作
   - 避免重复计算

2. **代码质量**
   - 添加类型注解
   - 完善docstring
   - 遵循PEP 8规范

#### 数据格式准备
**为PDF生成准备指标数据格式化函数**：

```python
def format_metrics_for_pdf(metrics: Dict[str, Any]) -> List[List[str]]:
    """
    将指标数据转换为PDF表格格式（完整版，包含所有参数）
    
    参数:
        metrics: 指标字典（来自calculate_all_metrics，完整版）
    
    返回:
        List[List[str]]: 表格数据
        [
            ['指标名称', '数值'],
            ['期间产品收益率', 'XX.XX% (年化 XX.XX%)'],
            ['期间收益', 'XX.XX万元 (年化 XX.XX万元)'],
            ['最大回撤', 'XX.XX%'],
            ['波动率', 'XX.XX%'],
            ['夏普比率', 'XX.XX'],
            ['卡玛比率', 'XX.XX'],
            ['单日最大收益', 'XX.XX%'],
            ['单日最大亏损', 'XX.XX%'],
            ['周胜率', 'XX.XX%'],
            ['月胜率', 'XX.XX%']
        ]
    
    用途:
        供开发者C使用，直接生成PDF表格
    
    注意:
        根据模版模块实现.md 1.2，业绩统计区域需要包含所有指标
    """
    table_data = []
    
    # 表头
    table_data.append(['指标名称', '数值'])
    
    # 期间产品收益率
    period_ret = metrics.get('period_return', 0)
    annualized_ret = metrics.get('annualized_return', 0)
    table_data.append([
        '期间产品收益率',
        f'{period_ret:.2f}% (年化 {annualized_ret:.2f}%)'
    ])
    
    # 最大回撤
    max_dd = metrics.get('max_drawdown', 0)
    table_data.append(['最大回撤', f'{max_dd:.2f}%'])
    
    # 波动率
    volatility = metrics.get('volatility', 0)
    table_data.append(['波动率', f'{volatility:.2f}%'])
    
    # 夏普比率
    sharpe = metrics.get('sharpe_ratio', 0)
    table_data.append(['夏普比率', f'{sharpe:.2f}'])
    
    # 卡玛比率
    calmar = metrics.get('calmar_ratio', 0)
    table_data.append(['卡玛比率', f'{calmar:.2f}'])
    
    # 单日最大收益
    max_daily_return = metrics.get('max_daily_return', 0)
    max_return_date = metrics.get('max_return_date', '')
    if max_return_date:
        table_data.append(['单日最大收益', f'{max_daily_return:.2f}% ({max_return_date})'])
    else:
        table_data.append(['单日最大收益', f'{max_daily_return:.2f}%'])
    
    # 单日最大亏损
    max_daily_loss = metrics.get('max_daily_loss', 0)
    max_loss_date = metrics.get('max_loss_date', '')
    if max_loss_date:
        table_data.append(['单日最大亏损', f'{max_daily_loss:.2f}% ({max_loss_date})'])
    else:
        table_data.append(['单日最大亏损', f'{max_daily_loss:.2f}%'])
    
    # 周胜率
    weekly_win_rate = metrics.get('weekly_win_rate', 0)
    table_data.append(['周胜率', f'{weekly_win_rate:.2f}%'])
    
    # 月胜率
    monthly_win_rate = metrics.get('monthly_win_rate', 0)
    table_data.append(['月胜率', f'{monthly_win_rate:.2f}%'])
    
    return table_data
```

---

## Day 3 任务详解

### 任务B6：完整测试 [2小时]

#### 测试内容
1. **端到端测试**
   - 从A的模块获取数据
   - 计算所有指标
   - 验证计算结果

2. **计算准确性验证**
   - 使用已知数据验证
   - 与手动计算结果对比
   - 验证边界情况

3. **性能测试**
   - 测试大量数据下的性能
   - 优化计算速度

---

### 任务B7：性能优化与协助PDF [2小时]

#### 性能优化
1. **计算优化**
   - 使用numpy向量化操作
   - 避免重复计算日收益率
   - 实现缓存机制

2. **内存优化**
   - 优化大数据量处理
   - 避免不必要的数据复制

#### 协助PDF数据准备
**完善指标数据格式化函数**，确保数据格式符合C的要求：

```python
def format_metrics_dict_for_pdf(metrics: Dict[str, Any]) -> Dict[str, str]:
    """
    将指标字典转换为格式化字符串字典
    
    返回:
        {
            'period_return': 'XX.XX%',
            'annualized_return': 'XX.XX%',
            'max_drawdown': 'XX.XX%',
            'volatility': 'XX.XX%',
            'sharpe_ratio': 'XX.XX'
        }
    
    用途:
        供开发者C直接使用，插入PDF文本
    """
    return {
        'period_return': f"{metrics.get('period_return', 0):.2f}%",
        'annualized_return': f"{metrics.get('annualized_return', 0):.2f}%",
        'max_drawdown': f"{metrics.get('max_drawdown', 0):.2f}%",
        'volatility': f"{metrics.get('volatility', 0):.2f}%",
        'sharpe_ratio': f"{metrics.get('sharpe_ratio', 0):.2f}"
    }
```

---

## 关键计算公式总结

### 1. 单位净值
```
单位净值 = 总资产 / 初始资金
```

### 2. 期间收益率
```
期间收益率 = (期末净值 - 期初净值) / 期初净值 × 100%
```

### 3. 年化收益率
```
年化收益率 = ((1 + 期间收益率/100) ^ (365 / 实际天数)) - 1 × 100%
```

### 4. 日收益率
```
日收益率 = (当日净值 - 前一日净值) / 前一日净值
```

### 5. 最大回撤
```
最大回撤 = max((峰值 - 当前值) / 峰值 × 100%)
```

### 6. 年化波动率
```
年化波动率 = std(日收益率) × sqrt(252) × 100%
```

### 7. 夏普比率
```
夏普比率 = (年化收益率 - 无风险收益率) / 年化波动率
```

### 8. 卡玛比率
```
卡玛比率 = 年化收益率 / 最大回撤（绝对值）
```

### 9. 累计收益率
```
累计收益率 = (单位净值 - 1) × 100%
复权累计收益 = (单位净值 - 1) × 100%
```

### 10. 周胜率
```
周胜率 = 盈利周数 / 总周数 × 100%
```

### 11. 月胜率
```
月胜率 = 盈利月数 / 总月数 × 100%
```

### 12. 月度收益率
```
月度收益率 = (月末净值 - 月初净值) / 月初净值 × 100%
月度累计收益率 = (月末净值 - 初始净值) / 初始净值 × 100%
```

### 13. 期间收益（绝对收益）
```
期间收益 = 期末资产 - 期初资产
年化收益 = 期间收益 × (365 / 实际天数)
```

---

## 数据接口规范

### 输入接口

#### 1. 每日持仓列表（来自开发者A）
```python
[
    {
        'date': '2024-01-01',
        'positions': {code: {...}},  # 持仓字典
        'total_assets': float,       # 总资产（万元）
        'stock_value': float,         # 股票市值（万元）
        'cash': float                # 现金余额（万元）
    },
    ...
]
```

### 输出接口

#### 1. 净值数据列表
```python
[
    {
        'date': '2024-01-01',
        'nav': float,           # 单位净值
        'total_assets': float   # 总资产（万元）
    },
    ...
]
```

#### 2. 指标字典（完整版）
```python
{
    'period_return': float,        # 期间收益率（%）
    'annualized_return': float,    # 年化收益率（%）
    'max_drawdown': float,         # 最大回撤（%）
    'volatility': float,           # 年化波动率（%）
    'sharpe_ratio': float,         # 夏普比率
    'calmar_ratio': float,         # 卡玛比率
    'max_daily_return': float,     # 单日最大收益（%）
    'max_daily_loss': float,       # 单日最大亏损（%）
    'max_return_date': str,        # 最大收益日期
    'max_loss_date': str,          # 最大亏损日期
    'weekly_win_rate': float,      # 周胜率（%）
    'monthly_win_rate': float,     # 月胜率（%）
    'start_date': str,             # 期初日期
    'end_date': str,               # 期末日期
    'days': int                    # 实际天数
}
```

#### 3. 累计收益率列表
```python
[
    {
        'date': '2024-01-01',
        'nav': float,
        'cumulative_return': float  # 累计收益率（%）
    },
    ...
]
```

#### 4. 月度收益率列表
```python
[
    {
        'month': '2024-01',
        'start_nav': float,
        'end_nav': float,
        'monthly_return': float,      # 月度收益率（%）
        'cumulative_return': float    # 月度累计收益率（%）
    },
    ...
]
```

#### 5. 每日回撤列表
```python
[
    {
        'date': '2024-01-01',
        'drawdown': float,      # 回撤（%）
        'peak_nav': float       # 峰值净值
    },
    ...
]
```

#### 6. 日收益率列表
```python
[0.01, -0.02, 0.015, ...]  # 小数形式，如0.01表示1%
```

---

## AI辅助提示词

### 提示词1：工具函数模块
```
我正在开发一个私募基金报告生成系统，需要实现工具函数模块。

任务要求：
1. 创建 calc/utils.py 模块
2. 实现日期工具函数：
   - generate_date_range() - 生成日期范围列表
   - is_trading_day() - 判断是否为交易日（简化：只判断周末）
   - get_nearest_trading_day() - 获取最近交易日

技术要求：
1. 日期格式统一为 'YYYY-MM-DD'
2. 交易日判断：周末（周六、周日）不是交易日
3. 所有函数必须有类型注解和docstring
4. 遵循PEP 8规范

请帮我实现这些函数。
```

### 提示词2：净值计算
```
我正在开发一个私募基金报告生成系统，需要实现净值计算功能。

任务要求：
1. 在 calc/metrics.py 中实现 calculate_nav() 函数
2. 实现 get_nav_on_date() 函数

计算公式：
单位净值 = 总资产 / 初始资金

输入数据格式：
- daily_positions: [{date, positions, total_assets, ...}, ...]
- initial_capital: float（默认1000.0万元）

输出格式：
- [{date: str, nav: float, total_assets: float}, ...]
- nav保留4位小数

技术要求：
1. 所有函数必须有类型注解和docstring
2. 处理边界情况（空数据、除零等）
3. 遵循PEP 8规范

请帮我实现这些函数。
```

### 提示词3：收益率计算
```
我正在开发一个私募基金报告生成系统，需要实现收益率计算功能。

任务要求：
1. 在 calc/metrics.py 中实现 calculate_returns() 函数
2. 实现 calculate_daily_returns() 函数

计算公式：
1. 期间收益率 = (期末净值 - 期初净值) / 期初净值 × 100%
2. 年化收益率 = ((1 + 期间收益率/100) ^ (365 / 实际天数)) - 1 × 100%
3. 日收益率 = (当日净值 - 前一日净值) / 前一日净值

输入数据格式：
- nav_data: [{date, nav, total_assets}, ...]

输出格式：
- calculate_returns() 返回: {
    'period_return': float,
    'annualized_return': float,
    'start_date': str,
    'end_date': str,
    'days': int
  }
- calculate_daily_returns() 返回: [float, ...]（小数形式）

技术要求：
1. 使用numpy进行数值计算
2. 处理边界情况（数据不足、除零等）
3. 所有函数必须有类型注解和docstring
4. 遵循PEP 8规范

请帮我实现这些函数，确保计算准确。
```

### 提示词4：最大回撤计算
```
我正在开发一个私募基金报告生成系统，需要实现最大回撤计算功能。

任务要求：
1. 在 calc/metrics.py 中实现 calculate_max_drawdown() 函数
2. 实现 calculate_daily_drawdowns() 函数

计算公式：
最大回撤 = max((峰值 - 当前值) / 峰值 × 100%)

计算逻辑：
1. 维护峰值历史（如果当前净值大于峰值，更新峰值）
2. 计算每个时间点的回撤 = (峰值 - 当前净值) / 峰值 × 100%
3. 找出最大回撤及其区间

输入数据格式：
- nav_data: [{date, nav, total_assets}, ...]

输出格式：
- calculate_max_drawdown() 返回: {
    'max_drawdown': float,
    'max_dd_start_date': str,
    'max_dd_end_date': str,
    'peak_date': str,
    'peak_nav': float
  }
- calculate_daily_drawdowns() 返回: [{date, drawdown, peak_nav}, ...]

技术要求：
1. 正确维护峰值历史
2. 准确记录最大回撤区间
3. 所有函数必须有类型注解和docstring
4. 遵循PEP 8规范

请帮我实现这些函数，确保逻辑正确。
```

### 提示词5：波动率和夏普比率计算
```
我正在开发一个私募基金报告生成系统，需要实现波动率和夏普比率计算。

任务要求：
1. 在 calc/metrics.py 中实现 calculate_volatility() 函数
2. 实现 calculate_sharpe_ratio() 函数

计算公式：
1. 年化波动率 = std(日收益率) × sqrt(252) × 100%
2. 夏普比率 = (年化收益率 - 无风险收益率) / 年化波动率

输入数据格式：
- calculate_volatility(): nav_data列表
- calculate_sharpe_ratio(): annualized_return(float), volatility(float), risk_free_rate(float, 默认0.03)

输出格式：
- calculate_volatility() 返回: float（年化波动率%）
- calculate_sharpe_ratio() 返回: float（夏普比率）

技术要求：
1. 使用numpy计算标准差
2. 252是一年的交易日数
3. 处理边界情况（波动率为0、数据不足等）
4. 所有函数必须有类型注解和docstring
5. 遵循PEP 8规范

请帮我实现这些函数。
```

### 提示词6：综合指标计算和格式化
```
我需要实现综合指标计算和数据格式化功能。

任务要求：
1. 实现 calculate_all_metrics() - 计算所有指标
2. 实现 format_metrics_for_pdf() - 格式化指标为PDF表格格式
3. 实现 format_metrics_dict_for_pdf() - 格式化指标为字符串字典

功能：
1. calculate_all_metrics() 整合所有指标计算
2. format_metrics_for_pdf() 返回表格数据（List[List[str]]）
3. format_metrics_dict_for_pdf() 返回格式化字符串字典

输出格式示例：
- 表格格式: [['指标名称', '数值'], ['期间产品收益率', 'XX.XX% (年化 XX.XX%)'], ...]
- 字典格式: {'period_return': 'XX.XX%', 'annualized_return': 'XX.XX%', ...}

技术要求：
1. 数字格式化（保留2位小数）
2. 添加百分号
3. 所有函数必须有类型注解和docstring
4. 遵循PEP 8规范

请帮我实现这些函数。
```

---

## 测试检查清单

### 功能测试
- [ ] 净值计算准确（与手动计算对比）
- [ ] 期间收益率计算准确
- [ ] 年化收益率计算准确
- [ ] 最大回撤计算准确（包括峰值维护）
- [ ] 波动率计算准确（使用已知数据验证）
- [ ] 夏普比率计算准确
- [ ] 日收益率序列计算正确

### 数据验证测试
- [ ] 净值必须为正数
- [ ] 收益率计算逻辑正确
- [ ] 最大回撤不能为负
- [ ] 波动率不能为负
- [ ] 所有数值计算与手动计算结果一致

### 边界情况测试
- [ ] 处理空数据情况
- [ ] 处理单日数据情况
- [ ] 处理净值不变的情况（波动率为0）
- [ ] 处理净值一直上涨的情况（最大回撤为0）
- [ ] 处理除零情况（如波动率为0时的夏普比率）

---

## 注意事项

### 1. 计算精度
- **净值**：保留4位小数
- **收益率、回撤、波动率**：保留2位小数，单位：%
- **夏普比率**：保留2位小数，无单位

### 2. 单位转换
- 收益率、回撤、波动率：计算结果为小数，需要乘以100转换为百分比
- 夏普比率：直接使用小数形式，不转换

### 3. 日期处理
- 统一使用 'YYYY-MM-DD' 格式
- 实际天数 = 期末日期 - 期初日期 + 1（包含首尾两天）
- 交易日判断：MVP版本只判断周末

### 4. 边界情况处理
- **波动率为0**：夏普比率返回0或抛出异常
- **最大回撤为0**：表示净值一直上涨
- **数据不足**：返回默认值或抛出异常
- **除零情况**：必须检查，避免程序崩溃

### 5. 性能优化
- 使用numpy向量化操作计算标准差
- 避免重复计算日收益率序列
- 实现计算结果缓存

### 6. 数据验证
- 净值必须为正数
- 日期格式必须正确
- 数据必须按时间顺序排列

---

## 参考文档

- **模版模块实现.md**：
  - 第1.2节（业绩统计区域）- 收益率、回撤、波动率、夏普比率计算公式
  - 第8.3节（指标相关计算）- 具体实现代码
- **项目分析.md**：第3.4节（收益计算模块）
- **任务分配.md**：开发者B的任务清单

---

## 与开发者A的协作接口

### 接收数据
从开发者A的模块接收：
```python
daily_positions = calculate_daily_positions(transactions, date_range, initial_capital)
```

### 输出数据
向开发者C的模块输出：
```python
nav_data = calculate_nav(daily_positions, initial_capital)
metrics = calculate_all_metrics(nav_data)
drawdowns = calculate_daily_drawdowns(nav_data)
```

---

## 常见问题处理

### Q1: 如果净值数据为空怎么办？
**A**: 返回默认值或抛出异常，记录日志

### Q2: 如果只有一天的数据怎么办？
**A**: 期间收益率和年化收益率为0，波动率为0，最大回撤为0

### Q3: 如果波动率为0，夏普比率怎么计算？
**A**: 返回0或抛出异常（因为分母为0）

### Q4: 最大回撤区间如何确定？
**A**: 记录峰值日期作为回撤开始，记录回撤最大的日期作为回撤结束

---

**文档版本**：v1.0  
**创建日期**：2024年  
**最后更新**：2024年

