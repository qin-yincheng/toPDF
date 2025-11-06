# 开发者B详细工作文档

## 职责概述

开发者B负责**计算层与分析层**，是整个系统的业务逻辑核心。主要工作包括：
1. 净值计算（每日净值、单位净值）
2. 收益率计算（期间收益率、年化收益率、日收益率）
3. 风险指标计算（最大回撤、波动率、夏普比率、卡玛比率）
4. **新增**：高级风险指标计算（跟踪误差、下行波动率、索提诺比率、信息比率）
5. **新增**：基准相关指标计算（β值、主动收益、累计超额收益）
6. **新增**：多时间段指标计算（统计期间、近一个月、近三个月等）
7. **新增**：收益风险特征判断
8. **新增**：最大回撤修复期计算
9. **新增**：Brinson归因计算（选择收益、配置收益）
10. **新增**：股票行业归因计算（行业权重、贡献度、选择收益、配置收益）
11. **新增**：股票绩效归因计算（股票权重、贡献度、收益额）
12. **新增**：个股持仓节点计算（TOP1-TOP100）
13. **新增**：期货分类归因计算（股指期货、商品期货、国债期货）
14. **新增**：期货板块归因计算（各板块多空持仓、收益额）
15. **新增**：换手率（年化）计算（各资产类别、各时间段）
16. **新增**：期间交易统计计算（买入金额、卖出金额）
17. 工具函数（日期处理、数据验证）
18. 数据格式转换（为PDF生成准备）

**总工作量**：28小时（Day1: 8h, Day2: 10h, Day3: 10h）（增加时间以覆盖新增归因分析功能）

---

## Day 1 任务详解

### 任务B1：工具函数模块 [2小时]

#### 模块位置
`calc/utils.py`

#### 依赖库
```bash
# 安装交易日历库
pip install pandas-market-calendars
```

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

**功能**：判断是否为交易日（使用交易日历库，包含节假日）

**实现（使用 pandas_market_calendars 库）**：
```python
import pandas_market_calendars as mcal
from datetime import datetime

# 初始化交易日历（中国A股，上海证券交易所）
_calendar = None

def _get_calendar():
    """获取交易日历（单例模式）"""
    global _calendar
    if _calendar is None:
        _calendar = mcal.get_calendar('SSE')  # SSE: 上海证券交易所
    return _calendar

def is_trading_day(date: str) -> bool:
    """
    判断是否为交易日（完整版，包含节假日）
    
    参数:
        date: 日期（YYYY-MM-DD）
    
    返回:
        bool: 是否为交易日
    
    实现逻辑:
        使用 pandas_market_calendars 库判断，自动包含：
        - 周末判断
        - 节假日判断（春节、国庆等）
        - 调休工作日判断
    """
    dt = datetime.strptime(date, '%Y-%m-%d')
    calendar = _get_calendar()
    
    # 获取该日期的交易日历
    schedule = calendar.schedule(start_date=dt, end_date=dt)
    
    # 如果schedule不为空，说明是交易日
    return not schedule.empty
```

##### 3. 获取最近交易日
**函数**：`get_nearest_trading_day()`

**功能**：获取最近的交易日（使用交易日历库）

**实现**：
```python
def get_nearest_trading_day(date: str, direction: str = 'backward') -> str:
    """
    获取最近的交易日（使用交易日历库，自动处理节假日）
    
    参数:
        date: 日期（YYYY-MM-DD）
        direction: 'backward'（向前找）或 'forward'（向后找）
    
    返回:
        str: 最近的交易日（YYYY-MM-DD）
    
    用途:
        处理非交易日，获取可用价格
    """
    dt = datetime.strptime(date, '%Y-%m-%d')
    
    # 如果已经是交易日，直接返回
    if is_trading_day(date):
        return date
    
    # 使用交易日历库获取交易日范围
    calendar = _get_calendar()
    
    if direction == 'backward':
        # 向前找：获取该日期之前的交易日
        end_date = dt - timedelta(days=1)
        schedule = calendar.schedule(start_date=end_date - timedelta(days=30), 
                                    end_date=end_date)
        if not schedule.empty:
            return schedule.index[-1].strftime('%Y-%m-%d')
    else:
        # 向后找：获取该日期之后的交易日
        start_date = dt + timedelta(days=1)
        schedule = calendar.schedule(start_date=start_date, 
                                    end_date=start_date + timedelta(days=30))
        if not schedule.empty:
            return schedule.index[0].strftime('%Y-%m-%d')
    
    # 如果库方法失败，回退到循环方式
    if direction == 'backward':
        while not is_trading_day(dt.strftime('%Y-%m-%d')):
            dt -= timedelta(days=1)
    else:
        while not is_trading_day(dt.strftime('%Y-%m-%d')):
            dt += timedelta(days=1)
    
    return dt.strftime('%Y-%m-%d')

##### 4. 生成交易日范围（新增）
**函数**：`generate_trading_date_range()`

**功能**：生成交易日范围列表（使用交易日历库）

**实现**：
```python
def generate_trading_date_range(start_date: str, end_date: str) -> List[str]:
    """
    生成交易日范围列表（只包含交易日，使用交易日历库）
    
    参数:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）
    
    返回:
        List[str]: 交易日列表，格式 'YYYY-MM-DD'
    
    用途:
        用于计算每日数据时，只处理交易日
    """
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    calendar = _get_calendar()
    schedule = calendar.schedule(start_date=start_dt, end_date=end_dt)
    
    # 转换为日期字符串列表
    trading_dates = [date.strftime('%Y-%m-%d') for date in schedule.index]
    
    return trading_dates
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

##### 14. β值（Beta）计算
**函数**：`calculate_beta()`

**计算公式**（根据模版模块实现.md 1.2.8）：
```
β = Cov(产品收益率, 基准收益率) / Var(基准收益率)
```

**实现**：
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

##### 15. 主动收益计算
**函数**：`calculate_active_return()`

**计算公式**（根据模版模块实现.md 1.2.7）：
```
主动收益 = 产品收益率 - 基准收益率
年化主动收益 = ((1 + 主动收益/100) ^ (365 / 实际天数)) - 1 × 100%
```

**实现**：
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

##### 16. 跟踪误差计算
**函数**：`calculate_tracking_error()`

**计算公式**（根据模版模块实现.md 1.7.1）：
```
跟踪误差 = std(产品收益率 - 基准收益率) × sqrt(252) × 100%
```

**实现**：
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

##### 17. 下行波动率计算
**函数**：`calculate_downside_volatility()`

**计算公式**（根据模版模块实现.md 1.7.1）：
```
下行波动率 = std(负收益率) × sqrt(252) × 100%
```

**实现**：
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

##### 18. 索提诺比率计算
**函数**：`calculate_sortino_ratio()`

**计算公式**（根据模版模块实现.md 1.7.1）：
```
索提诺比率 = (年化收益率 - 无风险收益率) / 下行波动率
```

**实现**：
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

##### 19. 信息比率计算
**函数**：`calculate_information_ratio()`

**计算公式**（根据模版模块实现.md 1.7.1）：
```
信息比率 = 年化主动收益 / 跟踪误差
```

**实现**：
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

##### 20. 最大回撤修复期计算
**函数**：`calculate_drawdown_recovery_period()`

**功能**：计算最大回撤修复期（从回撤结束到净值恢复到峰值的时间）

**实现**：
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

##### 21. 收益风险特征判断
**函数**：`judge_risk_characteristic()`

**功能**：根据收益率和波动率等指标判断收益风险特征（根据模版模块实现.md 1.1）

**实现**：
```python
def judge_risk_characteristic(
    annualized_return: float,
    volatility: float
) -> str:
    """
    判断收益风险特征
    
    参数:
        annualized_return: 年化收益率（%）
        volatility: 年化波动率（%）
    
    返回:
        str: 收益风险特征描述
    
    判断逻辑（根据模版模块实现.md 1.1）:
        - 高收益高风险：年化收益率 > 20% 且 波动率 > 30%
        - 中等收益中等风险：年化收益率 > 10% 且 波动率 < 20%
        - 低收益低风险：其他情况
    """
    if annualized_return > 20 and volatility > 30:
        return "绝对收益风险类型属于 高收益高风险"
    elif annualized_return > 10 and volatility < 20:
        return "绝对收益风险类型属于 中等收益中等风险"
    else:
        return "绝对收益风险类型属于 低收益低风险"
```

##### 22. 多时间段收益率计算
**函数**：`calculate_period_returns()`

**功能**：计算多个时间段的收益率（统计期间、近一个月、近三个月等）（根据模版模块实现.md 1.6）

**实现**：
```python
def calculate_period_returns(
    nav_data: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
    benchmark_data: List[Dict[str, Any]] = None
) -> Dict[str, Dict[str, float]]:
    """
    计算多时间段收益率
    
    参数:
        nav_data: 净值数据列表
        periods: 时间段字典 {
            '统计期间': (start_date, end_date),
            '近一个月': (start_date, end_date),
            '近三个月': (start_date, end_date),
            '近六个月': (start_date, end_date),
            '近一年': (start_date, end_date),
            '今年以来': (start_date, end_date),
            '成立以来': (start_date, end_date)
        }
        benchmark_data: 基准指数净值数据列表（可选）
    
    返回:
        Dict: {
            '统计期间': {
                'product_return': float,      # 产品期间收益率（%）
                'annualized_return': float,   # 产品年化收益率（%）
                'benchmark_return': float,    # 基准期间收益率（%）
                'excess_return': float        # 超额收益率（%）
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
                'product_return': 0.0,
                'annualized_return': 0.0,
                'benchmark_return': 0.0,
                'excess_return': 0.0
            }
            continue
        
        # 计算产品期间收益率
        start_nav = period_nav_data[0]['nav']
        end_nav = period_nav_data[-1]['nav']
        product_return = ((end_nav - start_nav) / start_nav) * 100
        
        # 计算实际天数
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end_dt - start_dt).days + 1
        
        # 计算年化收益率
        if days > 0:
            annualized_return = ((1 + product_return/100) ** (365/days) - 1) * 100
        else:
            annualized_return = 0.0
        
        # 计算基准收益率（如果有基准数据）
        benchmark_return = 0.0
        if benchmark_data:
            period_benchmark_data = [
                data for data in benchmark_data
                if start_date <= data['date'] <= end_date
            ]
            if len(period_benchmark_data) >= 2:
                bench_start_nav = period_benchmark_data[0]['nav']
                bench_end_nav = period_benchmark_data[-1]['nav']
                if bench_start_nav > 0:
                    benchmark_return = ((bench_end_nav - bench_start_nav) / bench_start_nav) * 100
        
        # 计算超额收益率
        excess_return = product_return - benchmark_return
        
        period_returns[period_name] = {
            'product_return': round(product_return, 2),
            'annualized_return': round(annualized_return, 2),
            'benchmark_return': round(benchmark_return, 2),
            'excess_return': round(excess_return, 2)
        }
    
    return period_returns
```

##### 23. 多时间段指标计算（完整版）
**函数**：`calculate_period_metrics()`

**功能**：计算多个时间段的所有指标（收益率、波动率、回撤等）（根据模版模块实现.md 1.7）

**实现**：
```python
def calculate_period_metrics(
    nav_data: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
    risk_free_rate: float = 0.03,
    benchmark_returns: List[float] = None,
    benchmark_period_returns: Dict[str, float] = None
) -> Dict[str, Dict[str, Any]]:
    """
    计算多时间段的所有指标
    
    参数:
        nav_data: 净值数据列表
        periods: 时间段字典
        risk_free_rate: 无风险收益率
        benchmark_returns: 基准收益率序列（可选，用于计算跟踪误差等）
        benchmark_period_returns: 基准各时间段收益率（可选）
    
    返回:
        Dict: {
            '统计期间': {
                'period_return': float,
                'annualized_return': float,
                'volatility': float,
                'max_drawdown': float,
                'sharpe_ratio': float,
                'calmar_ratio': float,
                'tracking_error': float,
                'downside_volatility': float,
                'sortino_ratio': float,
                'information_ratio': float,
                'beta': float,
                'active_return': float,
                'annualized_active_return': float
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
                'information_ratio': 0.0,
                'beta': 1.0,
                'active_return': 0.0,
                'annualized_active_return': 0.0
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
        
        # 计算下行波动率
        downside_volatility = calculate_downside_volatility(period_nav_data)
        
        # 计算索提诺比率
        sortino_ratio = calculate_sortino_ratio(
            returns_info['annualized_return'],
            downside_volatility,
            risk_free_rate
        )
        
        # 计算跟踪误差、β值、主动收益（如果有基准数据）
        tracking_error = 0.0
        beta = 1.0
        active_return_info = {'active_return': 0.0, 'annualized_active_return': 0.0}
        
        if benchmark_returns:
            # 筛选对应时间段的基准收益率
            # 简化：假设基准收益率序列已对齐
            tracking_error = calculate_tracking_error(period_nav_data, benchmark_returns)
            beta = calculate_beta(period_nav_data, benchmark_returns)
        
        if benchmark_period_returns and period_name in benchmark_period_returns:
            benchmark_ret = benchmark_period_returns[period_name]
            active_return_info = calculate_active_return(
                returns_info['period_return'],
                benchmark_ret,
                returns_info['days']
            )
        
        # 计算信息比率
        information_ratio = 0.0
        if tracking_error > 0:
            information_ratio = calculate_information_ratio(
                active_return_info['annualized_active_return'],
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
            'information_ratio': information_ratio,
            'beta': beta,
            'active_return': active_return_info['active_return'],
            'annualized_active_return': active_return_info['annualized_active_return']
        }
    
    return period_metrics
```

##### 24. 综合指标计算（完整版，包含所有新增指标）
**函数**：`calculate_all_metrics()`

**功能**：计算所有指标，返回指标字典（包含所有必需参数）

**实现**：
```python
def calculate_all_metrics(
    nav_data: List[Dict[str, Any]],
    risk_free_rate: float = 0.03,
    benchmark_returns: List[float] = None,
    benchmark_period_return: float = None
) -> Dict[str, Any]:
    """
    计算所有指标（完整版，包含所有新增指标）
    
    参数:
        nav_data: 净值数据列表
        risk_free_rate: 无风险收益率（默认3%）
        benchmark_returns: 基准指数每日收益率序列（可选）
        benchmark_period_return: 基准期间收益率（%，可选）
    
    返回:
        Dict: {
            # 原有指标
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
            
            # 新增指标（根据模版模块实现.md 1.2和1.7）
            'beta': float,                    # β值
            'active_return': float,            # 主动收益（%）
            'annualized_active_return': float, # 年化主动收益（%）
            'tracking_error': float,          # 跟踪误差（%）
            'downside_volatility': float,     # 下行波动率（%）
            'sortino_ratio': float,           # 索提诺比率
            'information_ratio': float,       # 信息比率
            'recovery_period': int,            # 最大回撤修复期（天）
            'recovery_date': str,             # 恢复日期
            'is_recovered': bool,             # 是否已恢复
            'risk_characteristic': str,       # 收益风险特征
            
            # 日期信息
            'start_date': str,
            'end_date': str,
            'days': int
        }
    
    用途:
        供开发者C生成PDF业绩统计表格和产品基本信息
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
    
    # 新增指标计算
    beta = 1.0
    if benchmark_returns:
        beta = calculate_beta(nav_data, benchmark_returns)
    
    active_return_info = {'active_return': 0.0, 'annualized_active_return': 0.0}
    if benchmark_period_return is not None:
        active_return_info = calculate_active_return(
            returns['period_return'],
            benchmark_period_return,
            returns['days']
        )
    
    tracking_error = 0.0
    if benchmark_returns:
        tracking_error = calculate_tracking_error(nav_data, benchmark_returns)
    
    downside_volatility = calculate_downside_volatility(nav_data)
    
    sortino_ratio = calculate_sortino_ratio(
        returns['annualized_return'],
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
    
    # 判断收益风险特征
    risk_characteristic = judge_risk_characteristic(
        returns['annualized_return'],
        volatility
    )
    
    return {
        # 原有指标
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
        'is_recovered': recovery_info['is_recovered'],
        'risk_characteristic': risk_characteristic,
        
        # 日期信息
        'start_date': returns['start_date'],
        'end_date': returns['end_date'],
        'days': returns['days'],
        
        # 最大回撤相关信息
        'max_dd_start_date': drawdown_info['max_dd_start_date'],
        'max_dd_end_date': drawdown_info['max_dd_end_date'],
        'peak_date': drawdown_info['peak_date'],
        'peak_nav': drawdown_info['peak_nav']
    }
```

##### 25. Brinson归因计算
**模块位置**: `calc/attribution.py` (新建)

**功能**: 计算Brinson归因（选择收益和配置收益）（根据模版模块实现.md 4.1）

**需要实现的函数**：

**函数1**：`brinson_attribution()`
```python
def brinson_attribution(
    product_industry_weights: Dict[str, float],
    benchmark_industry_weights: Dict[str, float],
    product_industry_returns: Dict[str, float],
    benchmark_industry_returns: Dict[str, float]
) -> Dict[str, float]:
    """
    计算Brinson归因
    
    参数:
        product_industry_weights: 产品在各行业的权重（小数形式，如0.3表示30%）
            {行业名称: 权重}
        benchmark_industry_weights: 基准在各行业的权重（小数形式）
            {行业名称: 权重}
        product_industry_returns: 产品在各行业的收益率（小数形式）
            {行业名称: 收益率}
        benchmark_industry_returns: 基准在各行业的收益率（小数形式）
            {行业名称: 收益率}
    
    返回:
        Dict: {
            'selection_effect': float,      # 选择收益（小数形式，需要×100转换为%）
            'allocation_effect': float,     # 配置收益（小数形式）
            'total_excess_return': float    # 总超额收益（小数形式）
        }
    
    计算公式（根据模版模块实现.md 4.1.1）:
        配置收益 = Σ((Wp_i - Wb_i) × Rb_i)
        选择收益 = Σ(Wp_i × (Rp_i - Rb_i))
        总超额收益 = 选择收益 + 配置收益
    
    其中:
        Wp_i = 产品在行业i的权重
        Wb_i = 基准在行业i的权重
        Rp_i = 产品在行业i的收益率
        Rb_i = 基准在行业i的收益率
    """
    selection_effect = 0.0
    allocation_effect = 0.0
    
    # 获取所有行业
    all_industries = set(product_industry_weights.keys()) | set(benchmark_industry_weights.keys())
    
    for industry in all_industries:
        # 获取权重（默认0）
        product_weight = product_industry_weights.get(industry, 0.0)
        benchmark_weight = benchmark_industry_weights.get(industry, 0.0)
        
        # 获取收益率（默认0）
        product_return = product_industry_returns.get(industry, 0.0)
        benchmark_return = benchmark_industry_returns.get(industry, 0.0)
        
        # 配置收益 = Σ((行业权重 - 基准行业权重) × 基准行业收益率)
        allocation_effect += (product_weight - benchmark_weight) * benchmark_return
        
        # 选择收益 = Σ(行业权重 × (行业收益率 - 基准行业收益率))
        selection_effect += product_weight * (product_return - benchmark_return)
    
    total_excess_return = selection_effect + allocation_effect
    
    return {
        'selection_effect': round(selection_effect, 6),
        'allocation_effect': round(allocation_effect, 6),
        'total_excess_return': round(total_excess_return, 6)
    }
```

**函数2**：`calculate_brinson_on_date()`
```python
def calculate_brinson_on_date(
    date: str,
    position_details: List[Dict[str, Any]],
    total_assets: float,
    industry_mapping: Dict[str, str],
    benchmark_industry_weights: Dict[str, float] = None,
    benchmark_industry_returns: Dict[str, float] = None
) -> Dict[str, float]:
    """
    计算指定日期的Brinson归因
    
    参数:
        date: 日期（YYYY-MM-DD）
        position_details: 持仓明细列表 [{code, market_value, ...}, ...]（来自开发者A）
        total_assets: 总资产（万元）
        industry_mapping: 股票代码到行业的映射 {股票代码: 行业名称}
        benchmark_industry_weights: 基准行业权重（可选，如果为None则使用默认权重）
        benchmark_industry_returns: 基准行业收益率（可选，如果为None则使用默认收益率）
    
    返回:
        Dict: {
            'selection_effect': float,      # 选择收益（%）
            'allocation_effect': float,     # 配置收益（%）
            'total_excess_return': float    # 总超额收益（%）
        }
    
    注意:
        需要从开发者A获取持仓明细和行业分类数据
        基准行业权重和收益率需要从外部数据源获取（如Tushare或配置）
    """
    # 计算产品行业权重
    product_industry_weights = {}
    product_industry_returns = {}
    
    # 按行业聚合持仓
    industry_positions = {}
    for pos in position_details:
        code = pos['code']
        industry = industry_mapping.get(code, '未知行业')
        if industry not in industry_positions:
            industry_positions[industry] = []
        industry_positions[industry].append(pos)
    
    # 计算每个行业的权重和收益率
    for industry, positions in industry_positions.items():
        # 计算行业权重
        industry_market_value = sum([p['market_value'] for p in positions])
        industry_weight = industry_market_value / total_assets if total_assets > 0 else 0.0
        product_industry_weights[industry] = industry_weight
        
        # 计算行业收益率（简化：使用持仓盈亏比例）
        # 实际应该计算行业整体的期间收益率
        industry_cost = sum([p.get('cost', 0) for p in positions])
        industry_profit = sum([p.get('profit_loss', 0) for p in positions])
        if industry_cost > 0:
            industry_return = industry_profit / industry_cost
        else:
            industry_return = 0.0
        product_industry_returns[industry] = industry_return
    
    # 如果没有提供基准数据，使用默认值（简化处理）
    if benchmark_industry_weights is None:
        benchmark_industry_weights = {industry: 0.0 for industry in product_industry_weights.keys()}
    
    if benchmark_industry_returns is None:
        benchmark_industry_returns = {industry: 0.0 for industry in product_industry_returns.keys()}
    
    # 计算Brinson归因
    brinson_result = brinson_attribution(
        product_industry_weights,
        benchmark_industry_weights,
        product_industry_returns,
        benchmark_industry_returns
    )
    
    # 转换为百分比
    return {
        'selection_effect': round(brinson_result['selection_effect'] * 100, 2),
        'allocation_effect': round(brinson_result['allocation_effect'] * 100, 2),
        'total_excess_return': round(brinson_result['total_excess_return'] * 100, 2)
    }
```

**函数3**：`calculate_daily_brinson_attribution()`
```python
def calculate_daily_brinson_attribution(
    daily_positions: List[Dict[str, Any]],
    industry_mapping: Dict[str, str],
    benchmark_industry_weights: Dict[str, Dict[str, float]] = None,
    benchmark_industry_returns: Dict[str, Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    计算每日的Brinson归因序列
    
    参数:
        daily_positions: 每日持仓列表 [{date, positions, total_assets}, ...]（来自开发者A）
        industry_mapping: 股票代码到行业的映射
        benchmark_industry_weights: 基准每日行业权重（可选）
            {日期: {行业: 权重}}
        benchmark_industry_returns: 基准每日行业收益率（可选）
            {日期: {行业: 收益率}}
    
    返回:
        List[Dict]: [{
            'date': str,
            'selection_effect': float,      # 选择收益（%）
            'allocation_effect': float,     # 配置收益（%）
            'total_excess_return': float    # 总超额收益（%）
        }, ...]
    
    用途:
        用于绘制Brinson归因时序图（模版模块实现.md 4.1）
    """
    daily_brinson = []
    
    for daily_data in daily_positions:
        date = daily_data['date']
        positions = daily_data.get('positions', [])
        total_assets = daily_data.get('total_assets', 0)
        
        # 获取该日期的基准数据（如果有）
        bench_weights = benchmark_industry_weights.get(date) if benchmark_industry_weights else None
        bench_returns = benchmark_industry_returns.get(date) if benchmark_industry_returns else None
        
        # 计算该日期的Brinson归因
        brinson_result = calculate_brinson_on_date(
            date,
            positions,
            total_assets,
            industry_mapping,
            bench_weights,
            bench_returns
        )
        
        daily_brinson.append({
            'date': date,
            **brinson_result
        })
    
    return daily_brinson
```

**函数4**：`calculate_cumulative_brinson_attribution()`
```python
def calculate_cumulative_brinson_attribution(
    daily_brinson: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    计算累计Brinson归因
    
    参数:
        daily_brinson: 每日Brinson归因列表
    
    返回:
        List[Dict]: [{
            'date': str,
            'cumulative_selection': float,      # 累计选择收益（%）
            'cumulative_allocation': float,     # 累计配置收益（%）
            'cumulative_excess_return': float   # 累计超额收益（%）
        }, ...]
    
    用途:
        用于绘制Brinson归因累计收益图（模版模块实现.md 4.1）
    """
    cumulative_brinson = []
    
    cum_selection = 0.0
    cum_allocation = 0.0
    cum_excess = 0.0
    
    for data in daily_brinson:
        cum_selection += data['selection_effect']
        cum_allocation += data['allocation_effect']
        cum_excess += data['total_excess_return']
        
        cumulative_brinson.append({
            'date': data['date'],
            'cumulative_selection': round(cum_selection, 2),
            'cumulative_allocation': round(cum_allocation, 2),
            'cumulative_excess_return': round(cum_excess, 2)
        })
    
    return cumulative_brinson
```

##### 26. 股票行业归因计算
**模块位置**: `calc/attribution.py` (新建)

**功能**: 计算每个行业的归因（权重、贡献度、收益额、选择收益、配置收益）（根据模版模块实现.md 4.2）

**实现**：
```python
def calculate_industry_attribution(
    position_details: List[Dict[str, Any]],
    total_assets: float,
    total_profit: float,
    industry_mapping: Dict[str, str],
    benchmark_industry_weights: Dict[str, float] = None,
    benchmark_industry_returns: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    计算每个行业的归因
    
    参数:
        position_details: 持仓明细列表 [{code, market_value, profit_loss, ...}, ...]（来自开发者A）
        total_assets: 总资产（万元）
        total_profit: 总收益（万元）
        industry_mapping: 股票代码到行业的映射
        benchmark_industry_weights: 基准行业权重（可选）
        benchmark_industry_returns: 基准行业收益率（可选）
    
    返回:
        List[Dict]: [{
            'industry': str,                   # 行业名称
            'weight': float,                   # 权重占净值比（%）
            'contribution': float,              # 贡献度（%）
            'profit': float,                   # 收益额（万元）
            'selection_return': float,         # 选择收益（%）
            'allocation_return': float          # 配置收益（%）
        }, ...]
    
    计算公式（根据模版模块实现.md 4.2.1）:
        行业权重 = 行业市值 / 总资产 × 100%
        贡献度 = 行业收益额 / 总收益 × 100%
        选择收益和配置收益使用Brinson模型计算
    """
    # 按行业聚合持仓
    industry_data = {}
    
    for pos in position_details:
        code = pos['code']
        industry = industry_mapping.get(code, '未知行业')
        
        if industry not in industry_data:
            industry_data[industry] = {
                'market_value': 0.0,
                'profit': 0.0,
                'stocks': []
            }
        
        industry_data[industry]['market_value'] += pos.get('market_value', 0)
        industry_data[industry]['profit'] += pos.get('profit_loss', 0)
        industry_data[industry]['stocks'].append(pos)
    
    # 计算每个行业的归因
    industry_attribution = []
    
    for industry, data in industry_data.items():
        # 计算行业权重
        industry_weight = (data['market_value'] / total_assets * 100) if total_assets > 0 else 0.0
        
        # 计算贡献度
        contribution = (data['profit'] / total_profit * 100) if total_profit > 0 else 0.0
        
        # 计算行业收益率
        industry_cost = sum([s.get('cost', 0) for s in data['stocks']])
        industry_return = (data['profit'] / industry_cost * 100) if industry_cost > 0 else 0.0
        
        # 计算选择收益和配置收益（使用Brinson模型）
        # 简化：假设基准行业权重和收益率已提供
        benchmark_weight = benchmark_industry_weights.get(industry, 0.0) if benchmark_industry_weights else 0.0
        benchmark_return = benchmark_industry_returns.get(industry, 0.0) if benchmark_industry_returns else 0.0
        
        # 配置收益 = (行业权重 - 基准行业权重) × 基准行业收益率
        allocation_return = (industry_weight / 100 - benchmark_weight) * benchmark_return
        
        # 选择收益 = 行业权重 × (行业收益率 - 基准行业收益率)
        selection_return = (industry_weight / 100) * (industry_return - benchmark_return)
        
        industry_attribution.append({
            'industry': industry,
            'weight': round(industry_weight, 2),
            'contribution': round(contribution, 2),
            'profit': round(data['profit'], 2),
            'selection_return': round(selection_return, 2),
            'allocation_return': round(allocation_return, 2)
        })
    
    return industry_attribution
```

##### 27. 股票绩效归因计算
**模块位置**: `calc/attribution.py` (新建)

**功能**: 计算每只股票的绩效（权重、贡献度、收益额）（根据模版模块实现.md 5.1）

**实现**：
```python
def calculate_stock_performance(
    position_details: List[Dict[str, Any]],
    total_assets: float,
    total_profit: float
) -> List[Dict[str, Any]]:
    """
    计算每只股票的绩效
    
    参数:
        position_details: 持仓明细列表 [{code, name, market_value, profit_loss, ...}, ...]（来自开发者A）
        total_assets: 总资产（万元）
        total_profit: 总收益（万元）
    
    返回:
        List[Dict]: [{
            'code': str,              # 股票代码
            'name': str,              # 股票名称
            'weight': float,          # 权重占净值比（%）
            'contribution': float,    # 贡献度（%）
            'profit': float           # 收益额（万元）
        }, ...]
    
    计算公式（根据模版模块实现.md 5.1.1）:
        权重 = 股票市值 / 总资产 × 100%
        贡献度 = 股票收益额 / 总收益 × 100%
    """
    stock_performance = []
    
    for pos in position_details:
        market_value = pos.get('market_value', 0)
        profit = pos.get('profit_loss', 0)
        
        # 计算权重
        weight = (market_value / total_assets * 100) if total_assets > 0 else 0.0
        
        # 计算贡献度
        contribution = (profit / total_profit * 100) if total_profit > 0 else 0.0
        
        stock_performance.append({
            'code': pos.get('code', ''),
            'name': pos.get('name', ''),
            'weight': round(weight, 2),
            'contribution': round(contribution, 2),
            'profit': round(profit, 2)
        })
    
    # 按收益额排序
    stock_performance.sort(key=lambda x: x['profit'], reverse=True)
    
    return stock_performance
```

##### 28. 个股持仓节点计算
**模块位置**: `calc/attribution.py` (新建)

**功能**: 计算持仓节点（TOP1、TOP2、TOP3、TOP5、TOP10、TOP50、TOP100）的市值和占比（根据模版模块实现.md 5.2）

**实现**：
```python
def calculate_position_nodes(
    position_details: List[Dict[str, Any]],
    total_assets: float
) -> List[Dict[str, Any]]:
    """
    计算持仓节点
    
    参数:
        position_details: 持仓明细列表（按市值从大到小排序）
            [{code, market_value, ...}, ...]（来自开发者A）
        total_assets: 总资产（万元）
    
    返回:
        List[Dict]: [{
            'node': str,              # 节点名称（TOP1、TOP2等）
            'market_value': float,    # 累计市值（万元）
            'percentage': float       # 占比（%）
        }, ...]
    
    计算公式（根据模版模块实现.md 5.2.1）:
        TOP N市值 = 前N只股票的累计市值
        TOP N占比 = TOP N市值 / 总资产 × 100%
    """
    # 确保按市值排序
    sorted_positions = sorted(position_details, 
                             key=lambda x: x.get('market_value', 0), 
                             reverse=True)
    
    nodes_config = {
        'TOP1': 1,
        'TOP2': 2,
        'TOP3': 3,
        'TOP5': 5,
        'TOP10': 10,
        'TOP50': 50,
        'TOP100': 100
    }
    
    node_data = []
    
    for node_name, count in nodes_config.items():
        # 取前N只股票
        top_n_stocks = sorted_positions[:count]
        
        # 计算累计市值
        total_mv = sum([s.get('market_value', 0) for s in top_n_stocks])
        
        # 计算占比
        percentage = (total_mv / total_assets * 100) if total_assets > 0 else 0.0
        
        node_data.append({
            'node': node_name,
            'market_value': round(total_mv, 2),
            'percentage': round(percentage, 2)
        })
    
    return node_data
```

##### 29. 期货分类归因计算
**模块位置**: `calc/attribution.py` (新建)

**功能**: 计算期货分类归因（根据模版模块实现.md 5.3）

**实现**：
```python
def calculate_futures_category_attribution(
    futures_transactions: List[Dict[str, Any]],
    net_assets: float,
    initial_capital: float,
    total_profit: float
) -> List[Dict[str, Any]]:
    """
    计算期货分类归因
    
    参数:
        futures_transactions: 期货交易记录列表（来自开发者A）
            [{code, category, direction, amount, profit, fee, ...}, ...]
        net_assets: 资产净值（万元）
        initial_capital: 初始资金（万元）
        total_profit: 总收益（万元）
    
    返回:
        List[Dict]: [{
            'category': str,                  # 资产分类（股指期货、商品期货、国债期货）
            'weight': float,                  # 权重(占净值比%)
            'contribution': float,             # 单位净值增长贡献（%）
            'return': float,                   # 收益率（%）
            'profit_before_fee': float,         # 费前收益额（万元）
            'profit_after_fee': float,         # 费后收益额（万元）
            'contribution_rate': float          # 收益额贡献率（%）
        }, ...]
    
    计算公式（根据模版模块实现.md 5.3.1）:
        权重 = 期货市值 / 资产净值 × 100%
        单位净值增长贡献 = 费后收益额 / 初始资金 × 100%
        收益率 = 收益额 / 期货市值 × 100%
        收益额贡献率 = 费后收益额 / 总收益 × 100%
    """
    # 按分类聚合期货数据
    category_data = {}
    
    for trans in futures_transactions:
        category = trans.get('category', '其他')  # 分类：股指期货、商品期货、国债期货
        direction = trans.get('direction', '')  # 买入或卖出
        
        if category not in category_data:
            category_data[category] = {
                'market_value': 0.0,
                'profit_before_fee': 0.0,
                'fees': 0.0,
                'transactions': []
            }
        
        # 累计市值（简化：使用交易金额）
        category_data[category]['market_value'] += trans.get('amount', 0)
        # 累计收益
        category_data[category]['profit_before_fee'] += trans.get('profit', 0)
        # 累计费用
        category_data[category]['fees'] += trans.get('fee', 0)
        category_data[category]['transactions'].append(trans)
    
    futures_category_data = []
    
    for category, data in category_data.items():
        if data['market_value'] == 0:
            continue
        
        # 计算权重
        weight = (data['market_value'] / net_assets * 100) if net_assets > 0 else 0.0
        
        # 费后收益额
        profit_after_fee = data['profit_before_fee'] - data['fees']
        
        # 计算收益率
        return_rate = (data['profit_before_fee'] / data['market_value'] * 100) if data['market_value'] > 0 else 0.0
        
        # 单位净值增长贡献
        contribution = (profit_after_fee / initial_capital * 100) if initial_capital > 0 else 0.0
        
        # 收益额贡献率
        contribution_rate = (profit_after_fee / total_profit * 100) if total_profit > 0 else 0.0
        
        futures_category_data.append({
            'category': category,
            'weight': round(weight, 2),
            'contribution': round(contribution, 2),
            'return': round(return_rate, 2),
            'profit_before_fee': round(data['profit_before_fee'], 2),
            'profit_after_fee': round(profit_after_fee, 2),
            'contribution_rate': round(contribution_rate, 2)
        })
    
    return futures_category_data
```

##### 30. 期货板块归因计算
**模块位置**: `calc/attribution.py` (新建)

**功能**: 计算期货板块归因（根据模版模块实现.md 5.4）

**实现**：
```python
def calculate_futures_block_attribution(
    futures_transactions: List[Dict[str, Any]],
    date_range: List[str],
    start_date: str,
    end_date: str
) -> List[Dict[str, Any]]:
    """
    计算期货板块归因
    
    参数:
        futures_transactions: 期货交易记录列表（来自开发者A）
            [{code, block, date, direction, quantity, price, amount, profit, ...}, ...]
        date_range: 日期范围列表
        start_date: 开始日期
        end_date: 结束日期
    
    返回:
        List[Dict]: [{
            'block': str,                     # 板块名称
            'avg_long': float,                # 日平均多头持仓（万元）
            'long_profit': float,              # 多头收益额（万元）
            'avg_short': float,               # 日平均空头持仓（万元）
            'short_profit': float,             # 空头收益额（万元）
            'total_profit': float,             # 期间收益额（万元）
            'index_change': float              # 板块指数涨跌（%）
        }, ...]
    
    计算公式（根据模版模块实现.md 5.4.1）:
        日平均多头持仓 = Σ(每日多头持仓) / 天数
        日平均空头持仓 = Σ(每日空头持仓) / 天数
        多头收益额 = 多头持仓的累计盈亏
        空头收益额 = 空头持仓的累计盈亏
    """
    # 按板块聚合期货数据
    block_data = {}
    
    # 按日期和板块聚合
    daily_block_positions = {}  # {日期: {板块: {long: 金额, short: 金额}}}
    
    for trans in futures_transactions:
        date = trans.get('date', '')
        block = trans.get('block', '其他')  # 板块分类
        direction = trans.get('direction', '')  # 买入（多头）或卖出（空头）
        amount = trans.get('amount', 0)
        profit = trans.get('profit', 0)
        
        if date not in daily_block_positions:
            daily_block_positions[date] = {}
        if block not in daily_block_positions[date]:
            daily_block_positions[date][block] = {'long': 0.0, 'short': 0.0, 'long_profit': 0.0, 'short_profit': 0.0}
        
        if direction == '买入':
            daily_block_positions[date][block]['long'] += amount
            daily_block_positions[date][block]['long_profit'] += profit
        elif direction == '卖出':
            daily_block_positions[date][block]['short'] += amount
            daily_block_positions[date][block]['short_profit'] += profit
    
    # 计算每个板块的归因
    block_attribution = []
    
    for block in set([trans.get('block', '其他') for trans in futures_transactions]):
        daily_long = []
        daily_short = []
        total_long_profit = 0.0
        total_short_profit = 0.0
        
        for date in date_range:
            if date in daily_block_positions and block in daily_block_positions[date]:
                block_day_data = daily_block_positions[date][block]
                daily_long.append(block_day_data['long'])
                daily_short.append(block_day_data['short'])
                total_long_profit += block_day_data['long_profit']
                total_short_profit += block_day_data['short_profit']
        
        # 计算日平均持仓
        avg_long = sum(daily_long) / len(daily_long) if daily_long else 0.0
        avg_short = sum(daily_short) / len(daily_short) if daily_short else 0.0
        
        # 期间总收益额
        total_profit = total_long_profit + total_short_profit
        
        # 获取板块指数涨跌（需要从外部数据源获取，这里简化处理）
        index_change = 0.0  # 需要从Tushare或配置获取
        
        block_attribution.append({
            'block': block,
            'avg_long': round(avg_long, 2),
            'long_profit': round(total_long_profit, 2),
            'avg_short': round(avg_short, 2),
            'short_profit': round(total_short_profit, 2),
            'total_profit': round(total_profit, 2),
            'index_change': round(index_change, 2)
        })
    
    return block_attribution
```

##### 31. 换手率（年化）计算
**模块位置**: `calc/trading.py` (新建)

**功能**: 计算各资产类别在各时间段的换手率（年化）（根据模版模块实现.md 6.3）

**实现**：
```python
def calculate_avg_market_value(
    asset_class: str,
    period_start: str,
    period_end: str,
    daily_positions: List[Dict[str, Any]]
) -> float:
    """
    计算期间平均持仓市值
    
    参数:
        asset_class: 资产分类（股票、基金、逆回购）
        period_start: 开始日期
        period_end: 结束日期
        daily_positions: 每日持仓列表（来自开发者A）
    
    返回:
        float: 期间平均持仓市值（万元）
    
    计算公式:
        期间平均持仓市值 = Σ(每日持仓市值) / 天数
    """
    period_daily_data = [
        data for data in daily_positions
        if period_start <= data['date'] <= period_end
    ]
    
    if not period_daily_data:
        return 0.0
    
    # 根据资产分类计算市值
    total_market_value = 0.0
    for daily_data in period_daily_data:
        if asset_class == '股票':
            market_value = daily_data.get('stock_value', 0)
        elif asset_class == '基金':
            # 如果有基金持仓，需要从持仓明细中提取
            # 注意：需要开发者A在持仓数据中标识资产类型，或通过交易记录中的asset_class字段判断
            positions = daily_data.get('positions', {})
            # 简化：假设持仓明细中已经区分了资产类型，或通过其他方式获取
            # 如果无法区分，可以从交易记录中获取该日期该资产类别的持仓
            market_value = daily_data.get('fund_value', 0)  # 如果有基金市值字段
        elif asset_class == '逆回购':
            # 如果有逆回购，需要单独计算
            market_value = daily_data.get('repo_value', 0)
        else:
            market_value = 0.0
        
        total_market_value += market_value
    
    avg_market_value = total_market_value / len(period_daily_data) if period_daily_data else 0.0
    return avg_market_value
```

```python
def calculate_turnover_rate(
    asset_class: str,
    period_start: str,
    period_end: str,
    transactions: List[Dict[str, Any]],
    daily_positions: List[Dict[str, Any]]
) -> float:
    """
    计算换手率（年化）
    
    参数:
        asset_class: 资产分类（股票、基金、逆回购）
        period_start: 开始日期（YYYY-MM-DD）
        period_end: 结束日期（YYYY-MM-DD）
        transactions: 交易记录列表（来自开发者A）
            [{date, code, direction, amount, asset_class, ...}, ...]
        daily_positions: 每日持仓列表（来自开发者A）
    
    返回:
        float: 换手率（年化，%）
    
    计算公式（根据模版模块实现.md 6.3.1）:
        换手率（年化） = (期间交易金额 / 期间平均持仓市值) × (365 / 实际天数) × 100%
    
    注意:
        期间交易金额 = 买入金额 + 卖出金额
        需要从交易记录中筛选对应资产分类的交易
    """
    from datetime import datetime
    
    # 计算期间交易金额
    period_transactions = [
        t for t in transactions
        if period_start <= t.get('date', '') <= period_end
        and t.get('asset_class', '') == asset_class
    ]
    
    buy_amount = sum([
        t.get('amount', 0) / 10000  # 转换为万元
        for t in period_transactions
        if t.get('direction', '') == '买入'
    ])
    
    sell_amount = sum([
        t.get('amount', 0) / 10000  # 转换为万元
        for t in period_transactions
        if t.get('direction', '') == '卖出'
    ])
    
    total_turnover = buy_amount + sell_amount
    
    # 计算期间平均持仓市值
    avg_market_value = calculate_avg_market_value(
        asset_class,
        period_start,
        period_end,
        daily_positions
    )
    
    # 计算实际天数
    start_dt = datetime.strptime(period_start, '%Y-%m-%d')
    end_dt = datetime.strptime(period_end, '%Y-%m-%d')
    days = (end_dt - start_dt).days + 1
    
    # 计算年化换手率
    if avg_market_value > 0 and days > 0:
        turnover_rate = (total_turnover / avg_market_value) * (365 / days) * 100
    else:
        turnover_rate = 0.0
    
    return round(turnover_rate, 2)
```

```python
def calculate_turnover_rates(
    transactions: List[Dict[str, Any]],
    daily_positions: List[Dict[str, Any]],
    periods: Dict[str, Tuple[str, str]],
    asset_classes: List[str] = None
) -> Dict[str, Dict[str, float]]:
    """
    计算各资产类别在各时间段的换手率
    
    参数:
        transactions: 交易记录列表（来自开发者A）
        daily_positions: 每日持仓列表（来自开发者A）
        periods: 时间段字典 {
            '统计期间': (start_date, end_date),
            '近一个月': (start_date, end_date),
            '近三个月': (start_date, end_date),
            '近六个月': (start_date, end_date),
            '今年以来': (start_date, end_date),
            '成立以来': (start_date, end_date)
        }
        asset_classes: 资产分类列表，默认['股票', '基金', '逆回购']
    
    返回:
        Dict: {
            '股票': {
                '统计期间': float,
                '近一个月': float,
                ...
            },
            ...
        }
    
    用途:
        用于生成换手率表格（模版模块实现.md 6.3）
    """
    if asset_classes is None:
        asset_classes = ['股票', '基金', '逆回购']
    
    turnover_data = {}
    
    for asset_class in asset_classes:
        turnover_data[asset_class] = {}
        for period_name, (start_date, end_date) in periods.items():
            turnover_rate = calculate_turnover_rate(
                asset_class,
                start_date,
                end_date,
                transactions,
                daily_positions
            )
            turnover_data[asset_class][period_name] = turnover_rate
    
    return turnover_data
```

##### 32. 期间交易统计计算
**模块位置**: `calc/trading.py` (新建)

**功能**: 计算各类资产的买入和卖出金额（根据模版模块实现.md 6.4）

**实现**：
```python
def calculate_trading_statistics(
    transactions: List[Dict[str, Any]],
    asset_classes: List[str] = None
) -> Dict[str, Dict[str, float]]:
    """
    计算期间交易统计
    
    参数:
        transactions: 交易记录列表（来自开发者A）
            [{date, code, direction, amount, asset_class, ...}, ...]
        asset_classes: 资产分类列表，默认['股票', '基金', '逆回购']
    
    返回:
        Dict: {
            '股票': {
                'buy_amount': float,   # 买入金额（万元）
                'sell_amount': float   # 卖出金额（万元）
            },
            ...
        }
    
    计算公式（根据模版模块实现.md 6.4.1）:
        买入金额 = Σ(买入交易的金额)
        卖出金额 = Σ(卖出交易的金额)
    
    注意:
        金额单位转换为万元
    """
    if asset_classes is None:
        asset_classes = ['股票', '基金', '逆回购']
    
    trading_stats = {}
    
    for asset_class in asset_classes:
        # 筛选该资产分类的交易
        asset_transactions = [
            t for t in transactions
            if t.get('asset_class', '') == asset_class
        ]
        
        # 计算买入金额
        buy_amount = sum([
            t.get('amount', 0) / 10000  # 转换为万元
            for t in asset_transactions
            if t.get('direction', '') == '买入'
        ])
        
        # 计算卖出金额
        sell_amount = sum([
            t.get('amount', 0) / 10000  # 转换为万元
            for t in asset_transactions
            if t.get('direction', '') == '卖出'
        ])
        
        trading_stats[asset_class] = {
            'buy_amount': round(buy_amount, 2),
            'sell_amount': round(sell_amount, 2)
        }
    
    return trading_stats
```

#### 测试要求
- 测试净值计算准确性
- 测试收益率计算（与手动计算对比）
- 测试最大回撤计算（包括峰值更新逻辑）
- 测试波动率计算（使用已知数据验证）
- 测试夏普比率计算（边界情况：波动率为0）
- 测试空数据、单日数据等边界情况
- **测试Brinson归因计算准确性**
- **测试行业归因计算准确性**
- **测试股票绩效归因计算准确性**
- **测试持仓节点计算准确性**
- **测试换手率计算准确性**（各资产类别、各时间段）
- **测试期间交易统计计算准确性**（买入金额、卖出金额）

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

### 任务B4：补充计算函数 [4小时]（增加时间）

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
**函数**：`calculate_period_profit()`

**计算公式**（根据模版模块实现.md 1.2.2）：
```
期间收益 = 期末资产 - 期初资产
年化收益 = 期间收益 × (365 / 实际天数)
```

**实现**：
```python
def calculate_period_profit(
    nav_data: List[Dict[str, Any]],
    initial_capital: float = 1000.0
) -> Dict[str, float]:
    """
    计算期间收益（绝对收益）
    
    参数:
        nav_data: 净值数据列表
        initial_capital: 初始资金（万元），默认1000万
    
    返回:
        Dict: {
            'period_profit': float,      # 期间收益（万元）
            'annualized_profit': float   # 年化收益（万元）
        }
    
    计算公式（根据模版模块实现.md 1.2.2）:
        期间收益 = 期末资产 - 期初资产
        年化收益 = 期间收益 × (365 / 实际天数)
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

##### 4. 基准指数累计收益率计算
**模块位置**: `calc/benchmark.py` (新建)

**功能**: 计算基准指数的累计收益率序列（根据模版模块实现.md 1.4.2）

**实现**：
```python
import pandas as pd
from typing import List, Dict, Any

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

##### 5. 基准指数回撤计算
**模块位置**: `calc/benchmark.py` (新建)

**功能**: 计算基准指数的回撤序列（根据模版模块实现.md 2.1.2）

**实现**：
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

##### 6. 累计超额收益计算
**模块位置**: `calc/benchmark.py` (新建)

**功能**: 计算产品相对基准的累计超额收益（根据模版模块实现.md 1.4.3）

**实现**：
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

##### 7. 基准指数期间收益率计算
**函数**：`calculate_benchmark_period_return()`

**功能**: 计算基准指数的期间收益率（根据模版模块实现.md 1.2.9）

**实现**：
```python
def calculate_benchmark_period_return(
    benchmark_data: pd.DataFrame,
    start_date: str = None,
    end_date: str = None
) -> float:
    """
    计算基准指数期间收益率
    
    参数:
        benchmark_data: 基准指数DataFrame（包含trade_date和close列）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
    
    返回:
        float: 基准期间收益率（%）
    
    计算公式:
        期间收益率 = (期末价格 - 期初价格) / 期初价格 × 100%
    """
    if benchmark_data.empty:
        return 0.0
    
    # 如果指定了日期范围，筛选数据
    if start_date and end_date:
        period_data = benchmark_data[
            (benchmark_data['trade_date'] >= start_date) &
            (benchmark_data['trade_date'] <= end_date)
        ]
        if period_data.empty:
            return 0.0
        initial_price = period_data.iloc[0]['close']
        final_price = period_data.iloc[-1]['close']
    else:
        initial_price = benchmark_data.iloc[0]['close']
        final_price = benchmark_data.iloc[-1]['close']
    
    if initial_price > 0:
        period_return = ((final_price - initial_price) / initial_price) * 100
    else:
        period_return = 0.0
    
    return round(period_return, 2)
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
    将指标数据转换为PDF表格格式（完整版，包含所有新增指标）
    
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
            ['主动收益', 'XX.XX% (年化 XX.XX%)'],
            ['β值', 'XX.XXXX'],
            ['跟踪误差', 'XX.XX%'],
            ['下行波动率', 'XX.XX%'],
            ['索提诺比率', 'XX.XX'],
            ['信息比率', 'XX.XX'],
            ['单日最大收益', 'XX.XX%'],
            ['单日最大亏损', 'XX.XX%'],
            ['周胜率', 'XX.XX%'],
            ['月胜率', 'XX.XX%'],
            ['同期对比', '沪深300: XX.XX%']
        ]
    
    用途:
        供开发者C使用，直接生成PDF业绩统计表格
    
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
    
    # 主动收益（新增）
    active_ret = metrics.get('active_return', 0)
    annualized_active_ret = metrics.get('annualized_active_return', 0)
    if active_ret != 0 or annualized_active_ret != 0:
        table_data.append([
            '主动收益',
            f'{active_ret:.2f}% (年化 {annualized_active_ret:.2f}%)'
        ])
    
    # β值（新增）
    beta = metrics.get('beta', 1.0)
    table_data.append(['β值', f'{beta:.4f}'])
    
    # 跟踪误差（新增）
    tracking_error = metrics.get('tracking_error', 0)
    if tracking_error > 0:
        table_data.append(['跟踪误差', f'{tracking_error:.2f}%'])
    
    # 下行波动率（新增）
    downside_vol = metrics.get('downside_volatility', 0)
    if downside_vol > 0:
        table_data.append(['下行波动率', f'{downside_vol:.2f}%'])
    
    # 索提诺比率（新增）
    sortino = metrics.get('sortino_ratio', 0)
    if sortino != 0:
        table_data.append(['索提诺比率', f'{sortino:.2f}'])
    
    # 信息比率（新增）
    info_ratio = metrics.get('information_ratio', 0)
    if info_ratio != 0:
        table_data.append(['信息比率', f'{info_ratio:.2f}'])
    
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

**格式化函数（多时间段指标）**：

**格式化函数（行业归因）**：

```python
def format_industry_attribution_for_pdf(
    industry_attribution: List[Dict[str, Any]],
    top_n: int = 10
) -> Dict[str, List[List[str]]]:
    """
    将行业归因数据转换为PDF表格格式（根据模版模块实现.md 4.2）
    
    参数:
        industry_attribution: 行业归因列表
        top_n: 取前N名（默认10）
    
    返回:
        Dict: {
            'profit_table': List[List[str]],  # 收益额排名前十表格
            'loss_table': List[List[str]]      # 亏损额排名前十表格
        }
    """
    # 按收益额排序
    sorted_attribution = sorted(industry_attribution, key=lambda x: x['profit'], reverse=True)
    
    # 收益额排名前十
    profit_table = [['行业', '权重占净值比(%)', '贡献度(%)', '收益额(万元)', '选择收益(%)', '配置收益(%)']]
    for data in sorted_attribution[:top_n]:
        profit_table.append([
            data['industry'],
            f"{data['weight']:.2f}",
            f"{data['contribution']:.2f}",
            f"{data['profit']:.2f}",
            f"{data['selection_return']:.2f}",
            f"{data['allocation_return']:.2f}"
        ])
    
    # 亏损额排名前十
    loss_table = [['行业', '权重占净值比(%)', '贡献度(%)', '收益额(万元)', '选择收益(%)', '配置收益(%)']]
    for data in sorted_attribution[-top_n:]:
        loss_table.append([
            data['industry'],
            f"{data['weight']:.2f}",
            f"{data['contribution']:.2f}",
            f"{data['profit']:.2f}",
            f"{data['selection_return']:.2f}",
            f"{data['allocation_return']:.2f}"
        ])
    
    return {
        'profit_table': profit_table,
        'loss_table': loss_table
    }
```

**格式化函数（股票绩效归因）**：

```python
def format_stock_performance_for_pdf(
    stock_performance: List[Dict[str, Any]],
    top_n: int = 10
) -> Dict[str, List[List[str]]]:
    """
    将股票绩效归因数据转换为PDF表格格式（根据模版模块实现.md 5.1）
    
    参数:
        stock_performance: 股票绩效归因列表（已按收益额排序）
        top_n: 取前N名（默认10）
    
    返回:
        Dict: {
            'profit_table': List[List[str]],  # 盈利前十表格
            'loss_table': List[List[str]]      # 亏损前十表格
        }
    """
    # 盈利前十
    profit_table = [['股票代码', '股票名称', '权重占净值比(%)', '贡献度(%)', '收益额(万元)']]
    for stock in stock_performance[:top_n]:
        profit_table.append([
            stock['code'],
            stock['name'],
            f"{stock['weight']:.2f}",
            f"{stock['contribution']:.2f}",
            f"{stock['profit']:.2f}"
        ])
    
    # 亏损前十
    loss_table = [['股票代码', '股票名称', '权重占净值比(%)', '贡献度(%)', '收益额(万元)']]
    for stock in stock_performance[-top_n:]:
        loss_table.append([
            stock['code'],
            stock['name'],
            f"{stock['weight']:.2f}",
            f"{stock['contribution']:.2f}",
            f"{stock['profit']:.2f}"
        ])
    
    return {
        'profit_table': profit_table,
        'loss_table': loss_table
    }
```

**格式化函数（持仓节点）**：

```python
def format_position_nodes_for_pdf(
    position_nodes: List[Dict[str, Any]]
) -> List[List[str]]:
    """
    将持仓节点数据转换为PDF表格格式（根据模版模块实现.md 5.2）
    
    参数:
        position_nodes: 持仓节点列表
    
    返回:
        List[List[str]]: 表格数据
    """
    table_data = [['持仓节点', '市值(万元)', '占比(%)']]
    
    for node in position_nodes:
        table_data.append([
            node['node'],
            f"{node['market_value']:.2f}",
            f"{node['percentage']:.2f}"
        ])
    
    return table_data
```

**格式化函数（期货分类归因）**：

```python
def format_futures_category_for_pdf(
    futures_category_attribution: List[Dict[str, Any]]
) -> List[List[str]]:
    """
    将期货分类归因数据转换为PDF表格格式（根据模版模块实现.md 5.3）
    
    参数:
        futures_category_attribution: 期货分类归因列表
    
    返回:
        List[List[str]]: 表格数据
    """
    table_data = [
        ['资产分类', '权重(占净值比%)', '单位净值增长贡献(%)', 
         '收益率(%)', '费前收益额(万元)', '费后收益额(万元)', '收益额贡献率(%)']
    ]
    
    if not futures_category_attribution:
        table_data.append(['暂无期货持仓', '', '', '', '', '', ''])
        return table_data
    
    for category_data in futures_category_attribution:
        table_data.append([
            category_data['category'],
            f"{category_data['weight']:.2f}",
            f"{category_data['contribution']:.2f}",
            f"{category_data['return']:.2f}",
            f"{category_data['profit_before_fee']:.2f}",
            f"{category_data['profit_after_fee']:.2f}",
            f"{category_data['contribution_rate']:.2f}"
        ])
    
    return table_data
```

**格式化函数（期货板块归因）**：

```python
def format_futures_block_for_pdf(
    futures_block_attribution: List[Dict[str, Any]]
) -> List[List[str]]:
    """
    将期货板块归因数据转换为PDF表格格式（根据模版模块实现.md 5.4）
    
    参数:
        futures_block_attribution: 期货板块归因列表
    
    返回:
        List[List[str]]: 表格数据
    """
    table_data = [
        ['板块', '日平均多头持仓(万元)', '多头收益额(万元)', 
         '日平均空头持仓(万元)', '空头收益额(万元)', 
         '期间收益额(万元)', '板块指数涨跌(%)']
    ]
    
    if not futures_block_attribution:
        table_data.append(['暂无期货持仓', '', '', '', '', '', ''])
        return table_data
    
    for block_data in futures_block_attribution:
        table_data.append([
            block_data['block'],
            f"{block_data['avg_long']:.2f}",
            f"{block_data['long_profit']:.2f}",
            f"{block_data['avg_short']:.2f}",
            f"{block_data['short_profit']:.2f}",
            f"{block_data['total_profit']:.2f}",
            f"{block_data['index_change']:.2f}"
        ])
    
    return table_data
```

**格式化函数（换手率）**：

```python
def format_turnover_rates_for_pdf(
    turnover_rates: Dict[str, Dict[str, float]]
) -> List[List[str]]:
    """
    将换手率数据转换为PDF表格格式（根据模版模块实现.md 6.3）
    
    参数:
        turnover_rates: 换手率数据字典 {
            '股票': {'统计期间': float, '近一个月': float, ...},
            ...
        }
    
    返回:
        List[List[str]]: 表格数据
        [
            ['资产分类', '统计期间(%)', '近一个月(%)', ...],
            ['股票', 'XX.XX', 'XX.XX', ...],
            ...
        ]
    """
    if not turnover_rates:
        return [['资产分类', '统计期间(%)', '近一个月(%)', '近三个月(%)', 
                 '近六个月(%)', '今年以来(%)', '成立以来(%)']]
    
    # 获取时间段列表
    asset_classes = list(turnover_rates.keys())
    if not asset_classes:
        return []
    
    periods = list(turnover_rates[asset_classes[0]].keys())
    
    # 表头
    table_data = [['资产分类'] + [f'{p}(%)' for p in periods]]
    
    # 数据行
    for asset_class in asset_classes:
        row = [asset_class]
        for period in periods:
            rate = turnover_rates[asset_class].get(period, 0)
            row.append(f"{rate:.2f}")
        table_data.append(row)
    
    return table_data
```

**格式化函数（期间交易统计）**：

```python
def format_trading_statistics_for_pdf(
    trading_stats: Dict[str, Dict[str, float]]
) -> List[List[str]]:
    """
    将期间交易统计数据转换为PDF表格格式（根据模版模块实现.md 6.4）
    
    参数:
        trading_stats: 交易统计数据字典 {
            '股票': {'buy_amount': float, 'sell_amount': float},
            ...
        }
    
    返回:
        List[List[str]]: 表格数据
        [
            ['资产分类', '买入金额(万元)', '卖出金额(万元)'],
            ['股票', 'XX.XX', 'XX.XX'],
            ...
        ]
    """
    table_data = [['资产分类', '买入金额(万元)', '卖出金额(万元)']]
    
    if not trading_stats:
        return table_data
    
    for asset_class, stats in trading_stats.items():
        table_data.append([
            asset_class,
            f"{stats.get('buy_amount', 0):.2f}",
            f"{stats.get('sell_amount', 0):.2f}"
        ])
    
    return table_data
```

**格式化函数（多时间段指标）**：

```python
def format_period_metrics_for_pdf(
    period_metrics: Dict[str, Dict[str, Any]]
) -> List[List[str]]:
    """
    将多时间段指标数据转换为PDF表格格式（根据模版模块实现.md 1.7）
    
    参数:
        period_metrics: 多时间段指标字典（来自calculate_period_metrics）
    
    返回:
        List[List[str]]: 表格数据
        [
            ['指标', '统计期间', '近一个月', '近三个月', ...],
            ['收益率(年化)', 'XX.XX%', 'XX.XX%', ...],
            ...
        ]
    
    用途:
        供开发者C生成指标分析表格（模版模块实现.md 1.7）
    """
    if not period_metrics:
        return []
    
    # 获取时间段列表
    periods = list(period_metrics.keys())
    
    # 表头
    table_data = [['指标'] + periods]
    
    # 各项指标
    indicators = [
        ('收益率(年化)', 'annualized_return'),
        ('波动率(年化)', 'volatility'),
        ('跟踪误差(年化)', 'tracking_error'),
        ('下行波动率(年化)', 'downside_volatility'),
        ('夏普比率(年化)', 'sharpe_ratio'),
        ('索提诺比率(年化)', 'sortino_ratio'),
        ('信息比率(年化)', 'information_ratio'),
        ('最大回撤', 'max_drawdown'),
        ('卡玛比率', 'calmar_ratio')
    ]
    
    for indicator_name, indicator_key in indicators:
        row = [indicator_name]
        for period_name in periods:
            value = period_metrics[period_name].get(indicator_key, 0)
            if indicator_key in ['tracking_error', 'downside_volatility']:
                # 跟踪误差和下行波动率，如果没有数据则不显示
                if value > 0:
                    row.append(f'{value:.2f}%')
                else:
                    row.append('-')
            elif indicator_key in ['sharpe_ratio', 'sortino_ratio', 'information_ratio', 'calmar_ratio']:
                # 比率类指标，如果没有数据则不显示
                if value != 0:
                    row.append(f'{value:.2f}')
                else:
                    row.append('-')
            else:
                row.append(f'{value:.2f}%')
        table_data.append(row)
    
    return table_data
```

---

## Day 3 任务详解

### 任务B6：归因分析模块实现 [4小时]（新增）

#### 模块位置
`calc/attribution.py` (新建)

#### 任务内容
根据模版模块实现.md 4.1-5.4部分，实现所有归因分析功能：

1. **Brinson归因计算**（根据模版模块实现.md 4.1）
   - 实现`brinson_attribution()`函数
   - 实现`calculate_brinson_on_date()`函数
   - 实现`calculate_daily_brinson_attribution()`函数
   - 实现`calculate_cumulative_brinson_attribution()`函数

2. **股票行业归因计算**（根据模版模块实现.md 4.2）
   - 实现`calculate_industry_attribution()`函数
   - 计算行业权重、贡献度、收益额、选择收益、配置收益

3. **股票绩效归因计算**（根据模版模块实现.md 5.1）
   - 实现`calculate_stock_performance()`函数
   - 计算股票权重、贡献度、收益额

4. **个股持仓节点计算**（根据模版模块实现.md 5.2）
   - 实现`calculate_position_nodes()`函数
   - 计算TOP1、TOP2、TOP3、TOP5、TOP10、TOP50、TOP100的市值和占比

5. **期货分类归因计算**（根据模版模块实现.md 5.3）
   - 实现`calculate_futures_category_attribution()`函数
   - 计算股指期货、商品期货、国债期货的归因

6. **期货板块归因计算**（根据模版模块实现.md 5.4）
   - 实现`calculate_futures_block_attribution()`函数
   - 计算各板块的多空持仓、收益额、板块指数涨跌

7. **换手率（年化）计算**（根据模版模块实现.md 6.3）
   - 实现`calculate_avg_market_value()`函数（计算期间平均持仓市值）
     - 用于计算各资产类别在指定时间段内的平均持仓市值
     - 需要区分股票、基金、逆回购等不同资产类别
   - 实现`calculate_turnover_rate()`函数（计算单个资产类别的换手率）
     - 计算公式：换手率（年化） = (期间交易金额 / 期间平均持仓市值) × (365 / 实际天数) × 100%
     - 期间交易金额 = 买入金额 + 卖出金额
   - 实现`calculate_turnover_rates()`函数（计算各资产类别在各时间段的换手率）
     - 支持多个时间段：统计期间、近一个月、近三个月、近六个月、今年以来、成立以来
     - 支持多个资产类别：股票、基金、逆回购

8. **期间交易统计计算**（根据模版模块实现.md 6.4）
   - 实现`calculate_trading_statistics()`函数
   - 计算各类资产的买入金额和卖出金额
   - 支持资产分类：股票、基金、逆回购等
   - 金额单位：万元

#### 数据依赖
- 需要从开发者A获取：
  - `position_details`：持仓明细列表（包含code、name、market_value、profit_loss等）
  - `daily_positions`：每日持仓列表
  - `industry_mapping`：股票代码到行业的映射（需要开发者A提供行业分类数据）
  - `futures_transactions`：期货交易记录（如果有期货持仓）
  - `transactions`：交易记录列表（用于换手率和交易统计，需要包含asset_class字段）
- 需要从外部数据源获取（可选）：
  - `benchmark_industry_weights`：基准行业权重
  - `benchmark_industry_returns`：基准行业收益率
  - `futures_block_index_change`：期货板块指数涨跌

#### 注意事项
1. **行业分类标准**：需要确保产品行业分类与基准行业分类标准一致（模版模块实现.md建议使用申万一级行业）
2. **基准数据**：如果无法获取基准数据，可以使用默认值（简化处理）
3. **期货数据**：如果产品没有期货持仓，相关函数应返回空列表或提示信息
4. **数据对齐**：确保产品持仓数据与基准数据的日期对齐
5. **交易记录分类**：需要从开发者A获取包含`asset_class`字段的交易记录，用于区分股票、基金、逆回购等
6. **换手率计算**：需要计算期间平均持仓市值，需要从每日持仓数据中提取对应资产类别的市值

---

### 任务B7：完整测试 [2小时]

#### 测试内容
1. **端到端测试**
   - 从A的模块获取数据
   - 计算所有指标和归因分析
   - 验证计算结果

2. **计算准确性验证**
   - 使用已知数据验证
   - 与手动计算结果对比
   - 验证边界情况
   - **验证Brinson归因计算准确性**
   - **验证行业归因计算准确性**
   - **验证股票绩效归因计算准确性**
   - **验证换手率计算准确性**（各资产类别、各时间段）
   - **验证期间交易统计计算准确性**（买入金额、卖出金额）

3. **性能测试**
   - 测试大量数据下的性能
   - 优化计算速度

---

### 任务B8：性能优化与协助PDF [4小时]（增加时间）

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

**1. 完善指标格式化函数**（所有格式化函数已在Day 2任务B5中定义）：
   - `format_metrics_for_pdf()` - 业绩统计表格（已包含所有新增指标）
   - `format_period_metrics_for_pdf()` - 多时间段指标表格
   - `format_industry_attribution_for_pdf()` - 行业归因表格（新增）
   - `format_stock_performance_for_pdf()` - 股票绩效归因表格（新增）
   - `format_position_nodes_for_pdf()` - 持仓节点表格（新增）
   - `format_futures_category_for_pdf()` - 期货分类归因表格（新增）
   - `format_futures_block_for_pdf()` - 期货板块归因表格（新增）

**2. 验证数据格式**：
   - 确保所有格式化函数输出格式符合PDF表格要求
   - 确保数据格式与模版模块实现.md中的要求一致
   - 与开发者C协调数据格式细节

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

### 14. β值（Beta）
```
β = Cov(产品收益率, 基准收益率) / Var(基准收益率)
```

### 15. 主动收益
```
主动收益 = 产品收益率 - 基准收益率
年化主动收益 = ((1 + 主动收益/100) ^ (365 / 实际天数)) - 1 × 100%
```

### 16. 跟踪误差
```
跟踪误差 = std(产品收益率 - 基准收益率) × sqrt(252) × 100%
```

### 17. 下行波动率
```
下行波动率 = std(负收益率) × sqrt(252) × 100%
```

### 18. 索提诺比率
```
索提诺比率 = (年化收益率 - 无风险收益率) / 下行波动率
```

### 19. 信息比率
```
信息比率 = 年化主动收益 / 跟踪误差
```

### 20. 累计超额收益
```
累计超额收益 = 产品累计收益 - 基准累计收益
```

### 21. 基准指数期间收益率
```
基准期间收益率 = (期末价格 - 期初价格) / 期初价格 × 100%
```

### 22. Brinson归因
```
配置收益 = Σ((Wp_i - Wb_i) × Rb_i)
选择收益 = Σ(Wp_i × (Rp_i - Rb_i))
总超额收益 = 选择收益 + 配置收益

其中：
Wp_i = 产品在行业i的权重
Wb_i = 基准在行业i的权重
Rp_i = 产品在行业i的收益率
Rb_i = 基准在行业i的收益率
```

### 23. 行业权重和贡献度
```
行业权重 = 行业市值 / 总资产 × 100%
贡献度 = 行业收益额 / 总收益 × 100%
```

### 24. 股票权重和贡献度
```
股票权重 = 股票市值 / 总资产 × 100%
贡献度 = 股票收益额 / 总收益 × 100%
```

### 25. 持仓节点
```
TOP N市值 = 前N只股票的累计市值
TOP N占比 = TOP N市值 / 总资产 × 100%
```

### 26. 期货分类归因
```
权重 = 期货市值 / 资产净值 × 100%
单位净值增长贡献 = 费后收益额 / 初始资金 × 100%
收益率 = 收益额 / 期货市值 × 100%
收益额贡献率 = 费后收益额 / 总收益 × 100%
```

### 27. 期货板块归因
```
日平均多头持仓 = Σ(每日多头持仓) / 天数
日平均空头持仓 = Σ(每日空头持仓) / 天数
多头收益额 = 多头持仓的累计盈亏
空头收益额 = 空头持仓的累计盈亏
```

### 28. 换手率（年化）
```
换手率（年化） = (期间交易金额 / 期间平均持仓市值) × (365 / 实际天数) × 100%
期间交易金额 = 买入金额 + 卖出金额
期间平均持仓市值 = Σ(每日持仓市值) / 天数
```

### 29. 期间交易统计
```
买入金额 = Σ(买入交易的金额)
卖出金额 = Σ(卖出交易的金额)
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

#### 2. 指标字典（完整版，包含所有新增指标）
```python
{
    # 原有指标
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
    
    # 新增指标（根据模版模块实现.md 1.2和1.7）
    'beta': float,                    # β值
    'active_return': float,            # 主动收益（%）
    'annualized_active_return': float, # 年化主动收益（%）
    'tracking_error': float,          # 跟踪误差（%）
    'downside_volatility': float,     # 下行波动率（%）
    'sortino_ratio': float,           # 索提诺比率
    'information_ratio': float,       # 信息比率
    'recovery_period': int,            # 最大回撤修复期（天）
    'recovery_date': str,             # 恢复日期
    'is_recovered': bool,             # 是否已恢复
    'risk_characteristic': str,       # 收益风险特征
    'max_dd_start_date': str,         # 最大回撤开始日期
    'max_dd_end_date': str,           # 最大回撤结束日期
    'peak_date': str,                 # 峰值日期
    'peak_nav': float,                # 峰值净值
    
    # 日期信息
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

#### 7. 多时间段收益率字典（新增）
```python
{
    '统计期间': {
        'product_return': float,      # 产品期间收益率（%）
        'annualized_return': float,   # 产品年化收益率（%）
        'benchmark_return': float,    # 基准期间收益率（%）
        'excess_return': float        # 超额收益率（%）
    },
    '近一个月': {...},
    ...
}
```

#### 8. 多时间段指标字典（新增）
```python
{
    '统计期间': {
        'period_return': float,
        'annualized_return': float,
        'volatility': float,
        'max_drawdown': float,
        'sharpe_ratio': float,
        'calmar_ratio': float,
        'tracking_error': float,
        'downside_volatility': float,
        'sortino_ratio': float,
        'information_ratio': float,
        'beta': float,
        'active_return': float,
        'annualized_active_return': float
    },
    '近一个月': {...},
    ...
}
```

#### 9. 基准指数累计收益率列表（新增）
```python
[
    {
        'date': '2024-01-01',
        'cumulative_return': float  # 累计收益率（%）
    },
    ...
]
```

#### 10. 基准指数回撤列表（新增）
```python
[
    {
        'date': '2024-01-01',
        'drawdown': float  # 回撤（%）
    },
    ...
]
```

#### 11. 累计超额收益列表（新增）
```python
[
    {
        'date': '2024-01-01',
        'excess_return': float  # 累计超额收益（%）
    },
    ...
]
```

#### 12. Brinson归因数据（新增）
```python
# 每日Brinson归因
[
    {
        'date': '2024-01-01',
        'selection_effect': float,      # 选择收益（%）
        'allocation_effect': float,     # 配置收益（%）
        'total_excess_return': float    # 总超额收益（%）
    },
    ...
]

# 累计Brinson归因
[
    {
        'date': '2024-01-01',
        'cumulative_selection': float,      # 累计选择收益（%）
        'cumulative_allocation': float,     # 累计配置收益（%）
        'cumulative_excess_return': float   # 累计超额收益（%）
    },
    ...
]
```

#### 13. 行业归因列表（新增）
```python
[
    {
        'industry': str,                   # 行业名称
        'weight': float,                   # 权重占净值比（%）
        'contribution': float,              # 贡献度（%）
        'profit': float,                   # 收益额（万元）
        'selection_return': float,         # 选择收益（%）
        'allocation_return': float          # 配置收益（%）
    },
    ...
]
```

#### 14. 股票绩效归因列表（新增）
```python
[
    {
        'code': str,              # 股票代码
        'name': str,              # 股票名称
        'weight': float,          # 权重占净值比（%）
        'contribution': float,    # 贡献度（%）
        'profit': float           # 收益额（万元）
    },
    ...
]
```

#### 15. 持仓节点数据（新增）
```python
[
    {
        'node': str,              # 节点名称（TOP1、TOP2等）
        'market_value': float,    # 累计市值（万元）
        'percentage': float       # 占比（%）
    },
    ...
]
```

#### 16. 期货分类归因列表（新增）
```python
[
    {
        'category': str,                  # 资产分类（股指期货、商品期货、国债期货）
        'weight': float,                  # 权重(占净值比%)
        'contribution': float,             # 单位净值增长贡献（%）
        'return': float,                   # 收益率（%）
        'profit_before_fee': float,         # 费前收益额（万元）
        'profit_after_fee': float,         # 费后收益额（万元）
        'contribution_rate': float          # 收益额贡献率（%）
    },
    ...
]
```

#### 17. 期货板块归因列表（新增）
```python
[
    {
        'block': str,                     # 板块名称
        'avg_long': float,                # 日平均多头持仓（万元）
        'long_profit': float,              # 多头收益额（万元）
        'avg_short': float,               # 日平均空头持仓（万元）
        'short_profit': float,             # 空头收益额（万元）
        'total_profit': float,             # 期间收益额（万元）
        'index_change': float              # 板块指数涨跌（%）
    },
    ...
]
```

#### 18. 换手率数据（新增）
```python
{
    '股票': {
        '统计期间': float,    # 换手率（%）
        '近一个月': float,
        '近三个月': float,
        '近六个月': float,
        '今年以来': float,
        '成立以来': float
    },
    '基金': {...},
    '逆回购': {...}
}
```

#### 19. 期间交易统计数据（新增）
```python
{
    '股票': {
        'buy_amount': float,   # 买入金额（万元）
        'sell_amount': float   # 卖出金额（万元）
    },
    '基金': {...},
    '逆回购': {...}
}
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
- [ ] **β值计算准确**（与手动计算对比）
- [ ] **主动收益计算准确**
- [ ] **跟踪误差计算准确**
- [ ] **下行波动率计算准确**（只考虑负收益率）
- [ ] **索提诺比率计算准确**
- [ ] **信息比率计算准确**
- [ ] **最大回撤修复期计算准确**
- [ ] **收益风险特征判断正确**
- [ ] **多时间段收益率计算准确**
- [ ] **多时间段指标计算准确**
- [ ] **基准指数累计收益率计算准确**
- [ ] **基准指数回撤计算准确**
- [ ] **累计超额收益计算准确**
- [ ] **Brinson归因计算准确**（选择收益和配置收益）
- [ ] **行业归因计算准确**（行业权重、贡献度、选择收益、配置收益）
- [ ] **股票绩效归因计算准确**（股票权重、贡献度、收益额）
- [ ] **持仓节点计算准确**（TOP1-TOP100市值和占比）
- [ ] **期货分类归因计算准确**（如果有期货持仓）
- [ ] **期货板块归因计算准确**（如果有期货持仓）
- [ ] **换手率计算准确**（各资产类别、各时间段）
- [ ] **期间交易统计计算准确**（买入金额、卖出金额）

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
  - 第1.1节（产品基本信息区域）- 收益风险特征判断逻辑
  - 第1.2节（业绩统计区域）- 收益率、回撤、波动率、夏普比率、卡玛比率、主动收益、β值、同期对比计算公式
  - 第1.4节（单位净值表现）- 基准指数累计收益率、累计超额收益计算
  - 第1.6节（收益分析表格）- 多时间段收益率计算
  - 第1.7节（指标分析表格）- 跟踪误差、下行波动率、索提诺比率、信息比率计算公式，多时间段指标计算
  - 第2.1节（动态回撤图）- 基准回撤计算、最大回撤修复期
  - 第4.1节（Brinson归因）- Brinson归因计算公式和实现逻辑
  - 第4.2节（股票行业归因）- 行业归因计算公式和实现逻辑
  - 第5.1节（股票绩效归因）- 股票绩效归因计算公式和实现逻辑
  - 第5.2节（个股持仓节点）- 持仓节点计算公式和实现逻辑
  - 第5.3节（期货分类归因）- 期货分类归因计算公式和实现逻辑
  - 第5.4节（期货板块归因）- 期货板块归因计算公式和实现逻辑
  - 第6.3节（换手率）- 换手率计算公式和实现逻辑
  - 第6.4节（期间交易统计）- 交易统计计算公式和实现逻辑
  - 第8.3节（指标相关计算）- 具体实现代码
- **项目分析.md**：第3.4节（收益计算模块）
- **任务分配.md**：开发者B的任务清单

---

## 与开发者A的协作接口

### 接收数据
从开发者A的模块接收：
```python
# 基础数据
daily_positions = calculate_daily_positions(transactions, date_range, initial_capital)

# 归因分析所需数据（根据模版模块实现.md 4.1-5.4）
# 1. 持仓明细（用于行业归因、股票绩效归因、持仓节点）
position_details = calculate_positions(transactions, end_date, total_assets)
# 格式：[{code, name, market_value, profit_loss, cost, ...}, ...]

# 2. 行业分类映射（用于Brinson归因、行业归因）
industry_mapping = get_industry_classification(stock_codes)  # 来自开发者A
# 格式：{股票代码: 行业名称}

# 3. 期货交易记录（如果有期货持仓，用于期货归因）
futures_transactions = filter_futures_transactions(transactions)  # 来自开发者A
# 格式：[{code, category, block, date, direction, amount, profit, fee, ...}, ...]

# 4. 交易记录（用于换手率和交易统计）
transactions = read_excel(excel_file_path)  # 来自开发者A
# 格式：DataFrame或List，包含date, code, direction, amount, asset_class等字段

# 5. 总资产和总收益（用于计算权重和贡献度）
total_assets = daily_positions[-1]['total_assets']  # 期末总资产
total_profit = sum([p.get('profit_loss', 0) for p in position_details])  # 总收益

### 输出数据
向开发者C的模块输出：
```python
# 基础数据
nav_data = calculate_nav(daily_positions, initial_capital)
metrics = calculate_all_metrics(
    nav_data, 
    risk_free_rate=0.03,
    benchmark_returns=benchmark_returns,  # 可选
    benchmark_period_return=benchmark_period_return  # 可选
)
drawdowns = calculate_daily_drawdowns(nav_data)
cumulative_returns = calculate_cumulative_returns(nav_data)
monthly_returns = calculate_monthly_returns(nav_data)

# 新增数据（根据模版模块实现.md 1.6和1.7）
period_returns = calculate_period_returns(
    nav_data, 
    periods=periods,
    benchmark_data=benchmark_data  # 可选
)
period_metrics = calculate_period_metrics(
    nav_data,
    periods=periods,
    risk_free_rate=0.03,
    benchmark_returns=benchmark_returns,  # 可选
    benchmark_period_returns=benchmark_period_returns  # 可选
)

# 基准相关数据（根据模版模块实现.md 1.4和2.1）
benchmark_cumulative_returns = calculate_benchmark_cumulative_returns(benchmark_data)
benchmark_drawdowns = calculate_benchmark_drawdowns(benchmark_data)
excess_returns = calculate_cumulative_excess_returns(
    cumulative_returns,
    benchmark_cumulative_returns
)

# 归因分析数据（根据模版模块实现.md 4.1-5.4）
# Brinson归因
daily_brinson = calculate_daily_brinson_attribution(
    daily_positions,
    industry_mapping,
    benchmark_industry_weights,  # 可选
    benchmark_industry_returns   # 可选
)
cumulative_brinson = calculate_cumulative_brinson_attribution(daily_brinson)

# 行业归因
industry_attribution = calculate_industry_attribution(
    position_details,  # 来自开发者A
    total_assets,
    total_profit,
    industry_mapping,
    benchmark_industry_weights,  # 可选
    benchmark_industry_returns   # 可选
)

# 股票绩效归因
stock_performance = calculate_stock_performance(
    position_details,  # 来自开发者A
    total_assets,
    total_profit
)

# 持仓节点
position_nodes = calculate_position_nodes(
    position_details,  # 来自开发者A
    total_assets
)

# 期货分类归因（如果有期货持仓）
futures_category_attribution = calculate_futures_category_attribution(
    futures_transactions,  # 来自开发者A
    net_assets,
    initial_capital,
    total_profit
)

# 期货板块归因（如果有期货持仓）
futures_block_attribution = calculate_futures_block_attribution(
    futures_transactions,  # 来自开发者A
    date_range,
    start_date,
    end_date
)

# 格式化数据（供PDF生成）
formatted_metrics = format_metrics_for_pdf(metrics)
formatted_period_metrics = format_period_metrics_for_pdf(period_metrics)
formatted_industry_attribution = format_industry_attribution_for_pdf(industry_attribution)
formatted_stock_performance = format_stock_performance_for_pdf(stock_performance)
formatted_position_nodes = format_position_nodes_for_pdf(position_nodes)
formatted_futures_category = format_futures_category_for_pdf(futures_category_attribution)
formatted_futures_block = format_futures_block_for_pdf(futures_block_attribution)

# 交易统计数据（根据模版模块实现.md 6.3和6.4）
# 换手率
turnover_rates = calculate_turnover_rates(
    transactions,  # 来自开发者A
    daily_positions,
    periods,
    asset_classes=['股票', '基金', '逆回购']
)

# 期间交易统计
trading_stats = calculate_trading_statistics(
    transactions,  # 来自开发者A
    asset_classes=['股票', '基金', '逆回购']
)

# 格式化数据（供PDF生成）
formatted_turnover_rates = format_turnover_rates_for_pdf(turnover_rates)
formatted_trading_stats = format_trading_statistics_for_pdf(trading_stats)
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

**文档版本**：v3.1（补充换手率和交易统计功能，包含所有新增指标、归因计算和交易统计）  
**创建日期**：2024年  
**最后更新**：2024年  
**更新内容**：
- v2.0: 整合开发者B补充.md的所有内容，根据模版模块实现.md 1.1-1.8部分补充所有缺失指标
- v3.0: 根据模版模块实现.md 4.1-5.4部分补充所有归因分析功能：
  - Brinson归因计算（选择收益、配置收益）
  - 股票行业归因计算（行业权重、贡献度、选择收益、配置收益）
  - 股票绩效归因计算（股票权重、贡献度、收益额）
  - 个股持仓节点计算（TOP1、TOP2、TOP3、TOP5、TOP10、TOP50、TOP100）
  - 期货分类归因计算（股指期货、商品期货、国债期货）
  - 期货板块归因计算（各板块多空持仓、收益额、板块指数涨跌）
- v3.1: 根据模版模块实现.md 6.3-6.4部分补充交易统计功能：
  - 换手率（年化）计算（各资产类别、各时间段）
  - 期间交易统计计算（买入金额、卖出金额）
  - 期间平均持仓市值计算
- 新增格式化函数（行业归因、股票绩效、持仓节点、期货归因、换手率、交易统计）
- 更新职责概述、输出接口规范、计算公式总结和测试检查清单
- 更新Day 3任务，添加换手率和交易统计的实现任务

