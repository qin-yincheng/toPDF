# 开发者A详细工作文档

## 职责概述

开发者A负责**数据层与API集成**，是整个系统的数据基础。主要工作包括：
1. 交割单Excel数据读取和解析
2. 持仓计算（数量、成本、市值）
3. 价格数据获取（MVP版本使用mock数据）
4. 每日持仓数据计算
5. 数据验证和格式转换
6. 配置文件设计
7. 主程序集成

**总工作量**：18小时（Day1: 8h, Day2: 6h, Day3: 4h）

---

## Day 1 任务详解

### 任务A1：交割单读取模块 [4小时]

#### 模块位置
`data/reader.py`

#### 详细要求

##### 1. Excel文件读取
**功能**：读取交割单Excel文件，解析交易记录

**必需字段**（根据项目分析.md）：
- `交易日期`：日期格式（YYYY-MM-DD 或 YYYY/MM/DD）
- `股票代码`：6位数字代码（如：000001）
- `股票名称`：股票中文名称（可能缺失）
- `交易方向`：买入/卖出（或：B/S、买/卖等变体）
- `成交数量`：交易的股数（整数）
- `成交价格`：每股成交价格（浮点数）
- `成交金额`：成交数量 × 成交价格（浮点数）
- `手续费`：交易产生的费用（浮点数）
- `印花税`：卖出时产生的税费（浮点数，买入时通常为0）

**实现要点**：
```python
import pandas as pd
from typing import List, Dict, Any
import logging

def read_excel(file_path: str) -> pd.DataFrame:
    """
    读取交割单Excel文件
    
    参数:
        file_path: Excel文件路径
    
    返回:
        DataFrame，包含标准化的交易记录
        列：date, code, name, direction, quantity, price, amount, fee, stamp_tax
    
    异常处理:
        - 文件不存在
        - 编码问题（GBK/UTF-8）
        - 日期格式解析失败
        - 必需字段缺失
    """
    # 1. 读取Excel（处理多个工作表的情况）
    # 2. 日期格式转换（pd.to_datetime）
    # 3. 数据清洗（去除空行、异常值）
    # 4. 字段名标准化（统一列名）
    # 5. 交易方向标准化（买入/卖出）
    # 6. 数据类型转换（数量、价格、金额等）
    # 7. 数据验证（调用validate_data）
```

##### 2. 数据清洗
**清洗规则**：
- 去除空行（所有字段都为空）
- 去除必需字段缺失的行（date, code, direction, quantity, price）
- 处理日期格式不统一的情况
- 统一交易方向字段（买入/买/B → '买入'，卖出/卖/S → '卖出'）
- 处理数量、价格、金额的异常值（负数、0等）

##### 3. 数据验证
**验证函数**：
```python
def validate_data(df: pd.DataFrame) -> bool:
    """
    验证数据格式和逻辑
    
    验证项：
    1. 必需字段是否存在
    2. 日期格式是否正确（YYYY-MM-DD）
    3. 股票代码格式（6位数字）
    4. 交易方向是否有效（买入/卖出）
    5. 成交数量是否为正数
    6. 成交价格是否为正数
    7. 成交金额是否等于数量×价格（允许小误差）
    8. 持仓数量不能为负（卖出数量不能超过持仓）
    
    返回:
        bool: 数据是否有效
    
    异常:
        如果数据无效，记录错误日志并抛出异常
    """
```

**验证逻辑**（持仓数量验证）：
```python
# 按股票代码分组，按日期排序
# 计算每个时间点的持仓数量
# 检查是否有负数持仓（卖出超过持仓）
for stock_code in df['code'].unique():
    stock_df = df[df['code'] == stock_code].sort_values('date')
    position = 0
    for _, row in stock_df.iterrows():
        if row['direction'] == '买入':
            position += row['quantity']
        else:
            position -= row['quantity']
        if position < 0:
            raise ValueError(f"股票{stock_code}在{row['date']}持仓为负")
```

##### 4. 输出格式
**标准化的DataFrame格式**：
```python
columns = [
    'date',        # str, 'YYYY-MM-DD'
    'code',        # str, 6位数字
    'name',        # str, 股票名称
    'direction',   # str, '买入' 或 '卖出'
    'quantity',    # float, 数量（股）
    'price',       # float, 价格（元）
    'amount',      # float, 金额（元）
    'fee',         # float, 手续费（元）
    'stamp_tax'    # float, 印花税（元）
]
```

#### 测试要求
- 测试正常数据读取
- 测试日期格式不统一
- 测试交易方向变体（买/买入/B等）
- 测试缺失字段处理
- 测试持仓为负的异常情况

---

### 任务A2：持仓计算模块 [4小时]

#### 模块位置
`calc/position.py`

#### 详细要求

##### 1. 持仓数量计算
**函数**：`calculate_position_quantity()`

**计算公式**（根据模版模块实现.md 8.1.1）：
```
持仓数量 = Σ(买入数量) - Σ(卖出数量)
```

**实现**：
```python
def calculate_position_quantity(
    transactions: pd.DataFrame, 
    stock_code: str, 
    end_date: str
) -> float:
    """
    计算指定股票在指定日期的持仓数量
    
    参数:
        transactions: 交易记录DataFrame
        stock_code: 股票代码
        end_date: 结束日期（YYYY-MM-DD）
    
    返回:
        float: 持仓数量（股）
    
    逻辑:
        1. 筛选该股票在end_date之前的交易
        2. 买入：增加持仓数量
        3. 卖出：减少持仓数量
    """
```

##### 2. 持仓成本计算（加权平均法）
**函数**：`calculate_position_cost()`

**计算公式**（根据模版模块实现.md 8.1.2和项目分析.md 3.2.1）：
```
持仓成本 = Σ(买入金额 + 买入手续费)
平均成本 = 持仓成本 / 持仓数量
```

**注意**：使用加权平均法，不是FIFO法

**实现**：
```python
def calculate_position_cost(
    transactions: pd.DataFrame,
    stock_code: str,
    end_date: str
) -> float:
    """
    计算指定股票在指定日期的持仓成本（加权平均法）
    
    参数:
        transactions: 交易记录DataFrame
        stock_code: 股票代码
        end_date: 结束日期
    
    返回:
        float: 持仓成本（元），转换为万元
    
    计算公式:
        持仓成本 = Σ(买入金额 + 买入手续费)
        注意：只计算买入，卖出不减少成本（卖出时成本已实现）
    
    单位转换:
        返回时转换为万元（除以10000）
    """
    # 筛选买入交易
    buy_trans = transactions[
        (transactions['code'] == stock_code) &
        (transactions['date'] <= end_date) &
        (transactions['direction'] == '买入')
    ]
    
    # 计算总成本
    total_cost = (buy_trans['amount'].sum() + buy_trans['fee'].sum()) / 10000
    return total_cost
```

##### 3. 持仓市值计算
**函数**：`calculate_position_value()`

**计算公式**（根据模版模块实现.md 8.1.3）：
```
持仓市值 = 当前价格 × 持仓数量
```

**实现**：
```python
def calculate_position_value(
    stock_code: str,
    quantity: float,
    date: str
) -> float:
    """
    计算指定股票在指定日期的持仓市值
    
    参数:
        stock_code: 股票代码
        quantity: 持仓数量（股）
        date: 日期（YYYY-MM-DD）
    
    返回:
        float: 持仓市值（万元）
    
    注意:
        调用get_stock_price()获取价格
        单位转换：元 → 万元
    """
    price = get_stock_price(stock_code, date)  # 元/股
    market_value = (price * quantity) / 10000  # 转换为万元
    return market_value
```

##### 4. 平均成本单价计算
**函数**：`calculate_avg_cost()`

**计算公式**（根据模版模块实现.md 8.1.2）：
```
平均成本单价 = 持仓成本 / 持仓数量
```

**实现**：
```python
def calculate_avg_cost(
    transactions: pd.DataFrame,
    stock_code: str,
    end_date: str
) -> float:
    """
    计算指定股票的平均成本单价
    
    参数:
        transactions: 交易记录DataFrame
        stock_code: 股票代码
        end_date: 结束日期
    
    返回:
        float: 平均成本单价（元/股）
    
    计算公式:
        平均成本单价 = 持仓成本 / 持仓数量
    
    注意:
        如果持仓数量为0，返回0
    """
    quantity = calculate_position_quantity(transactions, stock_code, end_date)
    if quantity == 0:
        return 0.0
    
    cost = calculate_position_cost(transactions, stock_code, end_date)
    # cost是万元，quantity是股，需要转换
    avg_cost = (cost * 10000) / quantity  # 转换为元/股
    return avg_cost
```

##### 5. 盈亏金额和盈亏比例计算
**函数**：`calculate_profit_loss()`

**计算公式**（根据模版模块实现.md 7.1.1）：
```
盈亏金额 = 持仓市值 - 持仓成本
盈亏比例 = 盈亏金额 / 持仓成本 × 100%
```

**实现**：
```python
def calculate_profit_loss(
    market_value: float,
    cost: float
) -> Dict[str, float]:
    """
    计算盈亏金额和盈亏比例
    
    参数:
        market_value: 持仓市值（万元）
        cost: 持仓成本（万元）
    
    返回:
        Dict: {
            'profit_loss': float,      # 盈亏金额（万元）
            'profit_loss_pct': float   # 盈亏比例（%）
        }
    
    计算公式:
        盈亏金额 = 持仓市值 - 持仓成本
        盈亏比例 = 盈亏金额 / 持仓成本 × 100%
    
    注意:
        如果成本为0，盈亏比例为0
    """
    profit_loss = market_value - cost
    profit_loss_pct = (profit_loss / cost * 100) if cost > 0 else 0.0
    
    return {
        'profit_loss': round(profit_loss, 2),
        'profit_loss_pct': round(profit_loss_pct, 2)
    }
```

##### 6. 持仓占比计算
**函数**：`calculate_position_percentage()`

**计算公式**（根据模版模块实现.md 7.1.1）：
```
持仓占比 = 该股票市值 / 总资产 × 100%
```

**实现**：
```python
def calculate_position_percentage(
    market_value: float,
    total_assets: float
) -> float:
    """
    计算持仓占比
    
    参数:
        market_value: 该股票持仓市值（万元）
        total_assets: 总资产（万元）
    
    返回:
        float: 持仓占比（%）
    
    计算公式:
        持仓占比 = 该股票市值 / 总资产 × 100%
    """
    if total_assets == 0:
        return 0.0
    
    percentage = (market_value / total_assets) * 100
    return round(percentage, 2)
```

##### 7. 计算指定日期的持仓（完整版）
**函数**：`calculate_positions()`

**输出格式**（根据模版模块实现.md 7.1.1）：
```python
{
    'code': {
        'quantity': float,          # 持仓数量（股）
        'cost': float,              # 持仓成本（万元）
        'avg_cost': float,          # 平均成本单价（元/股）
        'market_value': float,      # 持仓市值（万元）
        'profit_loss': float,       # 盈亏金额（万元）
        'profit_loss_pct': float,  # 盈亏比例（%）
        'position_pct': float,     # 持仓占比（%）
        'name': str                # 股票名称
    }
}
```

**实现**：
```python
def calculate_positions(
    transactions: pd.DataFrame,
    end_date: str,
    total_assets: float = None
) -> Dict[str, Dict[str, Any]]:
    """
    计算指定日期的所有持仓（完整版，包含所有参数）
    
    参数:
        transactions: 交易记录DataFrame
        end_date: 结束日期（YYYY-MM-DD）
        total_assets: 总资产（万元），如果不提供则计算
    
    返回:
        Dict: {code: {quantity, cost, avg_cost, market_value, profit_loss, profit_loss_pct, position_pct, name}}
    
    逻辑:
        1. 获取所有有持仓的股票代码
        2. 对每只股票计算所有参数
        3. 过滤掉持仓数量为0的股票
    """
    positions = {}
    stock_codes = transactions['code'].unique()
    
    # 计算总资产（如果不提供）
    if total_assets is None:
        total_stock_value = 0
        for code in stock_codes:
            quantity = calculate_position_quantity(transactions, code, end_date)
            if quantity > 0:
                market_value = calculate_position_value(code, quantity, end_date)
                total_stock_value += market_value
        # 简化：假设现金为0，总资产=股票市值
        total_assets = total_stock_value
    
    for code in stock_codes:
        quantity = calculate_position_quantity(transactions, code, end_date)
        if quantity > 0:  # 只保留有持仓的股票
            cost = calculate_position_cost(transactions, code, end_date)
            avg_cost = calculate_avg_cost(transactions, code, end_date)
            market_value = calculate_position_value(code, quantity, end_date)
            
            # 计算盈亏
            profit_info = calculate_profit_loss(market_value, cost)
            
            # 计算持仓占比
            position_pct = calculate_position_percentage(market_value, total_assets)
            
            # 获取股票名称（从交易记录中提取）
            stock_name = transactions[transactions['code'] == code]['name'].iloc[0] if 'name' in transactions.columns else '未知'
            
            positions[code] = {
                'quantity': quantity,
                'cost': cost,
                'avg_cost': avg_cost,
                'market_value': market_value,
                'profit_loss': profit_info['profit_loss'],
                'profit_loss_pct': profit_info['profit_loss_pct'],
                'position_pct': position_pct,
                'name': stock_name
            }
    
    return positions
```

##### 8. 已实现收益计算
**函数**：`calculate_realized_profit()`

**计算公式**（根据模版模块实现.md 8.2.1）：
```
已实现收益 = Σ(卖出金额 - 卖出成本 - 手续费 - 印花税)
卖出成本 = 平均成本单价 × 卖出数量
```

**实现**：
```python
def calculate_realized_profit(
    transactions: pd.DataFrame,
    end_date: str
) -> float:
    """
    计算指定日期前的已实现收益
    
    参数:
        transactions: 交易记录DataFrame
        end_date: 结束日期（YYYY-MM-DD）
    
    返回:
        float: 已实现收益（万元）
    
    计算公式:
        对于每笔卖出交易：
        卖出成本 = 平均成本单价 × 卖出数量
        已实现盈亏 = 卖出金额 - 卖出成本 - 手续费 - 印花税
        已实现收益 = Σ(已实现盈亏)
    
    注意:
        需要在卖出时计算当时的平均成本
    """
    realized_profit = 0.0
    
    # 按股票代码分组处理
    for stock_code in transactions['code'].unique():
        stock_trans = transactions[
            (transactions['code'] == stock_code) &
            (transactions['date'] <= end_date)
        ].sort_values('date')
        
        # 维护持仓状态
        current_quantity = 0
        current_cost = 0.0  # 万元
        
        for _, trans in stock_trans.iterrows():
            if trans['direction'] == '买入':
                # 买入：增加持仓
                buy_amount = trans['amount'] / 10000  # 转换为万元
                buy_fee = trans['fee'] / 10000  # 转换为万元
                current_cost += buy_amount + buy_fee
                current_quantity += trans['quantity']
            elif trans['direction'] == '卖出':
                # 卖出：计算已实现收益
                if current_quantity > 0:
                    # 计算平均成本单价
                    avg_cost_per_share = (current_cost * 10000) / current_quantity  # 元/股
                    
                    # 计算卖出成本
                    sell_quantity = trans['quantity']
                    sell_cost = (avg_cost_per_share * sell_quantity) / 10000  # 转换为万元
                    
                    # 计算已实现盈亏
                    sell_amount = trans['amount'] / 10000  # 转换为万元
                    sell_fee = trans['fee'] / 10000  # 转换为万元
                    stamp_tax = trans.get('stamp_tax', 0) / 10000  # 转换为万元
                    
                    profit = sell_amount - sell_cost - sell_fee - stamp_tax
                    realized_profit += profit
                    
                    # 更新持仓（减少）
                    current_quantity -= sell_quantity
                    current_cost -= sell_cost  # 减少成本
    
    return round(realized_profit, 2)
```

##### 9. 未实现收益计算
**函数**：`calculate_unrealized_profit()`

**计算公式**（根据模版模块实现.md 8.2.2）：
```
未实现收益 = Σ(持仓市值 - 持仓成本)
```

**实现**：
```python
def calculate_unrealized_profit(
    positions: Dict[str, Dict[str, Any]]
) -> float:
    """
    计算未实现收益
    
    参数:
        positions: 持仓字典（包含cost和market_value）
    
    返回:
        float: 未实现收益（万元）
    
    计算公式:
        未实现收益 = Σ(持仓市值 - 持仓成本)
    
    注意:
        未实现收益是浮动盈亏，持仓未卖出
    """
    unrealized_profit = 0.0
    
    for code, pos_data in positions.items():
        market_value = pos_data.get('market_value', 0)
        cost = pos_data.get('cost', 0)
        unrealized_profit += (market_value - cost)
    
    return round(unrealized_profit, 2)
```

##### 10. 每日持仓计算
**函数**：`calculate_daily_positions()`

**用途**：为开发者B的指标计算提供每日数据

**输出格式**（根据任务分配.md和模版模块实现.md）：
```python
[
    {
        'date': '2024-01-01',
        'positions': {code: {quantity, cost, avg_cost, market_value, profit_loss, profit_loss_pct, position_pct, name}},  # 完整持仓字典
        'total_assets': float,       # 总资产（万元）
        'stock_value': float,        # 股票市值（万元）
        'cash': float,              # 现金余额（万元）
        'realized_profit': float,    # 已实现收益（万元）
        'unrealized_profit': float   # 未实现收益（万元）
    },
    ...
]
```

**计算公式**（根据模版模块实现.md 1.3.2）：
```
总资产 = 持仓市值 + 现金余额
现金余额 = 初始资金 + 已实现收益 - 总投入
```

**实现**：
```python
def calculate_daily_positions(
    transactions: pd.DataFrame,
    date_range: List[str],
    initial_capital: float = 1000.0
) -> List[Dict[str, Any]]:
    """
    计算每日持仓和资产（完整版）
    
    参数:
        transactions: 交易记录DataFrame
        date_range: 日期列表（YYYY-MM-DD格式）
        initial_capital: 初始资金（万元），默认1000万
    
    返回:
        List[Dict]: 每日持仓数据（包含所有参数）
    
    逻辑:
        1. 对每个日期计算持仓（包含所有参数）
        2. 计算持仓市值总和
        3. 计算现金余额（初始资金 - 总买入金额 + 总卖出金额）
        4. 计算总资产 = 持仓市值 + 现金
        5. 计算已实现收益和未实现收益
    """
    daily_data = []
    
    for date in date_range:
        # 计算持仓（完整版，包含所有参数）
        # 先计算总资产用于计算持仓占比
        temp_positions = {}
        total_stock_value_temp = 0
        for code in transactions['code'].unique():
            quantity = calculate_position_quantity(transactions, code, date)
            if quantity > 0:
                market_value = calculate_position_value(code, quantity, date)
                total_stock_value_temp += market_value
                temp_positions[code] = market_value
        
        # 计算现金余额
        buy_amount = transactions[
            (transactions['date'] <= date) & 
            (transactions['direction'] == '买入')
        ]['amount'].sum() / 10000  # 转换为万元
        
        sell_amount = transactions[
            (transactions['date'] <= date) & 
            (transactions['direction'] == '卖出')
        ]['amount'].sum() / 10000  # 转换为万元
        
        # 考虑手续费
        buy_fee = transactions[
            (transactions['date'] <= date) & 
            (transactions['direction'] == '买入')
        ]['fee'].sum() / 10000  # 转换为万元
        
        sell_fee = transactions[
            (transactions['date'] <= date) & 
            (transactions['direction'] == '卖出')
        ]['fee'].sum() / 10000  # 转换为万元
        
        stamp_tax = transactions[
            (transactions['date'] <= date) & 
            (transactions['direction'] == '卖出')
        ]['stamp_tax'].sum() / 10000  # 转换为万元
        
        cash = initial_capital - buy_amount - buy_fee + sell_amount - sell_fee - stamp_tax
        total_assets = total_stock_value_temp + cash
        
        # 计算完整持仓（包含所有参数）
        positions = calculate_positions(transactions, date, total_assets)
        
        # 计算已实现收益
        realized_profit = calculate_realized_profit(transactions, date)
        
        # 计算未实现收益
        unrealized_profit = calculate_unrealized_profit(positions)
        
        daily_data.append({
            'date': date,
            'positions': positions,
            'total_assets': total_assets,
            'stock_value': total_stock_value_temp,
            'cash': cash,
            'realized_profit': realized_profit,
            'unrealized_profit': unrealized_profit
        })
    
    return daily_data
```

##### 6. 价格获取（Mock版本）
**函数**：`get_stock_price()`

**MVP版本要求**：不使用Tushare API，使用简单mock数据

**实现方案**（选择一种）：
```python
def get_stock_price(stock_code: str, date: str) -> float:
    """
    获取股票价格（Mock版本）
    
    参数:
        stock_code: 股票代码
        date: 日期（YYYY-MM-DD）
    
    返回:
        float: 价格（元/股）
    
    Mock方案（选择一种）：
    1. 固定价格：返回10.0（所有股票统一价格）
    2. 基于代码：根据股票代码生成固定价格（如：int(code) % 100）
    3. 随机价格：使用随机数生成（10-50元之间）
    4. 基于交易记录：使用该股票最近一次交易价格
    
    推荐方案4：使用最近一次交易价格
    """
    # 方案4实现（推荐）
    # 从transactions中查找该股票在date之前最近一次交易价格
    # 如果没有，返回默认价格10.0
```

**非交易日处理**：
- 如果date是周末或节假日，返回最近一个交易日的价格
- 可以使用前一日的价格

#### 测试要求
- 测试单只股票多次买入的持仓计算
- 测试买入后卖出的持仓计算
- 测试持仓成本加权平均计算
- 测试每日持仓数据生成
- 测试价格获取（包括非交易日）

---

## Day 2 任务详解

### 任务A3：集成测试 [2小时]

#### 目标
与开发者B的指标计算模块集成，确保数据格式匹配

#### 测试内容
1. **数据格式验证**
   - 检查每日持仓数据格式是否符合B的接口要求
   - 验证日期格式、数据类型

2. **数据准确性验证**
   - 手动计算几笔交易的持仓，对比程序结果
   - 验证持仓成本计算是否正确

3. **边界情况测试**
   - 空持仓情况
   - 单只股票情况
   - 大量交易数据性能测试

#### 修复工作
- 修复数据格式不匹配问题
- 优化持仓计算性能（使用pandas向量化）

---

### 任务A4：价格数据Mock优化 [2小时]

#### 优化内容

##### 1. 价格缓存机制
```python
# 实现简单的价格缓存
_price_cache = {}  # {(code, date): price}

def get_stock_price(stock_code: str, date: str) -> float:
    """带缓存的价格获取"""
    cache_key = (stock_code, date)
    if cache_key in _price_cache:
        return _price_cache[cache_key]
    
    # 计算价格
    price = _calculate_price(stock_code, date)
    _price_cache[cache_key] = price
    return price
```

##### 2. 非交易日处理
```python
def get_nearest_trading_day(date: str) -> str:
    """
    获取最近的交易日
    
    逻辑:
        1. 如果是工作日，返回该日期
        2. 如果是周末，返回上一个周五
        3. 如果是节假日，返回上一个交易日
    """
    # 简化实现：只处理周末
    from datetime import datetime, timedelta
    dt = datetime.strptime(date, '%Y-%m-%d')
    weekday = dt.weekday()
    
    if weekday == 5:  # 周六
        return (dt - timedelta(days=1)).strftime('%Y-%m-%d')
    elif weekday == 6:  # 周日
        return (dt - timedelta(days=2)).strftime('%Y-%m-%d')
    else:
        return date
```

##### 3. 价格获取优化
- 批量获取价格（减少重复计算）
- 使用最近交易价格（更真实）

---

### 任务A5：代码优化与数据格式准备 [2小时]

#### 代码优化
1. **性能优化**
   - 使用pandas向量化操作替代循环
   - 使用索引加速查询

2. **代码质量**
   - 添加类型注解
   - 完善docstring
   - 遵循PEP 8规范

#### 数据格式准备
**为PDF生成准备数据格式转换函数**：

```python
def format_positions_for_pdf(positions: Dict[str, Dict]) -> List[List[str]]:
    """
    将持仓数据转换为PDF表格格式（完整版，包含所有参数）
    
    参数:
        positions: 持仓字典（完整版，包含所有参数）
    
    返回:
        List[List[str]]: 表格数据，每行是一个列表
        [['股票代码', '股票名称', '持仓数量', '持仓成本(万元)', '持仓市值(万元)', 
          '盈亏金额(万元)', '盈亏比例(%)', '持仓占比(%)'], ...]
    
    用途:
        供开发者C使用，直接生成PDF表格
    
    注意:
        根据模版模块实现.md 7.1.1，持仓明细表需要包含所有字段
    """
    table_data = []
    
    # 表头（根据模版模块实现.md 7.1.1）
    table_data.append([
        '股票代码', '股票名称', '持仓数量', 
        '持仓成本(万元)', '持仓市值(万元)', 
        '盈亏金额(万元)', '盈亏比例(%)', '持仓占比(%)'
    ])
    
    # 数据行
    for code, data in positions.items():
        table_data.append([
            code,
            data.get('name', '未知'),
            f"{data['quantity']:.0f}",
            f"{data['cost']:.2f}",
            f"{data['market_value']:.2f}",
            f"{data.get('profit_loss', 0):.2f}",
            f"{data.get('profit_loss_pct', 0):.2f}",
            f"{data.get('position_pct', 0):.2f}"
        ])
    
    # 添加合计行（根据模版模块实现.md 7.1.1）
    total_cost = sum([p.get('cost', 0) for p in positions.values()])
    total_market_value = sum([p.get('market_value', 0) for p in positions.values()])
    total_profit_loss = sum([p.get('profit_loss', 0) for p in positions.values()])
    total_quantity = sum([p.get('quantity', 0) for p in positions.values()])
    
    table_data.append([
        '合计', '', f"{total_quantity:.0f}",
        f"{total_cost:.2f}",
        f"{total_market_value:.2f}",
        f"{total_profit_loss:.2f}",
        f"{total_profit_loss/total_cost*100:.2f}" if total_cost > 0 else '0.00',
        '100.00'
    ])
    
    return table_data
```

---

## Day 3 任务详解

### 任务A6：配置文件 [1小时]

#### 模块位置
`config.py`

#### 配置内容
```python
# 产品基本信息
PRODUCT_NAME = "XX私募证券投资基金"
ESTABLISH_DATE = "2024-01-01"  # 产品成立日期
INITIAL_CAPITAL = 1000.0  # 初始资金（万元）

# 报告参数
REPORT_YEAR = 2024  # 报告年份
REPORT_START_DATE = "2024-01-01"
REPORT_END_DATE = "2024-12-31"

# 数据文件路径
EXCEL_FILE_PATH = "交割单.xlsx"
OUTPUT_PDF_PATH = "report.pdf"

# 其他配置
RISK_FREE_RATE = 0.03  # 无风险收益率（3%）
```

---

### 任务A7：主程序集成 [2小时]

#### 模块位置
`main.py`

#### 功能要求
1. **整合所有模块**
   ```python
   from data.reader import read_excel, validate_data
   from calc.position import calculate_positions, calculate_daily_positions
   from calc.metrics import calculate_nav, calculate_returns  # B的模块
   from charts.generator import plot_nav_trend  # C的模块
   from pdf.generator import PDFGenerator  # C的模块
   ```

2. **命令行参数**
   ```python
   import argparse
   
   parser = argparse.ArgumentParser(description='生成私募基金年度报告')
   parser.add_argument('--excel', default='交割单.xlsx', help='交割单文件路径')
   parser.add_argument('--year', type=int, default=2024, help='报告年份')
   parser.add_argument('--output', default='report.pdf', help='输出PDF路径')
   ```

3. **错误处理**
   - 文件不存在
   - 数据格式错误
   - 计算异常

4. **日志记录**
   - 记录关键步骤
   - 记录错误信息

---

### 任务A8：协助PDF数据准备 [1小时]

#### 工作内容
1. **测试数据流转**
   - 确保持仓数据能正确传递给开发者C
   - 验证数据格式是否符合C的要求

2. **数据格式转换函数**
   - 完善`format_positions_for_pdf()`函数
   - 确保数据格式与PDF表格需求匹配

---

## 关键计算公式总结

### 1. 持仓数量
```
持仓数量 = Σ(买入数量) - Σ(卖出数量)
```

### 2. 持仓成本（加权平均法）
```
持仓成本 = Σ(买入金额 + 买入手续费)
平均成本单价 = 持仓成本 / 持仓数量（元/股）
```

### 3. 持仓市值
```
持仓市值 = 当前价格 × 持仓数量
```

### 4. 盈亏金额和盈亏比例
```
盈亏金额 = 持仓市值 - 持仓成本
盈亏比例 = 盈亏金额 / 持仓成本 × 100%
```

### 5. 持仓占比
```
持仓占比 = 该股票市值 / 总资产 × 100%
```

### 6. 总资产
```
总资产 = 持仓市值 + 现金余额
现金余额 = 初始资金 - 总买入金额 - 买入手续费 + 总卖出金额 - 卖出手续费 - 印花税
```

### 7. 已实现收益
```
已实现收益 = Σ(卖出金额 - 卖出成本 - 手续费 - 印花税)
卖出成本 = 平均成本单价 × 卖出数量
```

### 8. 未实现收益
```
未实现收益 = Σ(持仓市值 - 持仓成本)
```

### 9. 单位净值（供B使用）
```
单位净值 = 总资产 / 初始资金
```

---

## 数据接口规范

### 输入接口
**交割单Excel文件**：
- 文件格式：`.xlsx`
- 必需字段：交易日期、股票代码、交易方向、成交数量、成交价格、成交金额、手续费、印花税

### 输出接口

#### 1. 交易记录DataFrame
```python
columns = ['date', 'code', 'name', 'direction', 'quantity', 'price', 'amount', 'fee', 'stamp_tax']
```

#### 2. 持仓字典（完整版）
```python
{
    'code': {
        'quantity': float,          # 持仓数量（股）
        'cost': float,              # 持仓成本（万元）
        'avg_cost': float,          # 平均成本单价（元/股）
        'market_value': float,      # 持仓市值（万元）
        'profit_loss': float,       # 盈亏金额（万元）
        'profit_loss_pct': float,  # 盈亏比例（%）
        'position_pct': float,     # 持仓占比（%）
        'name': str                # 股票名称
    }
}
```

#### 3. 每日持仓列表（完整版）
```python
[
    {
        'date': '2024-01-01',
        'positions': {code: {...}},      # 完整持仓字典（包含所有参数）
        'total_assets': float,          # 总资产（万元）
        'stock_value': float,            # 股票市值（万元）
        'cash': float,                  # 现金余额（万元）
        'realized_profit': float,        # 已实现收益（万元）
        'unrealized_profit': float      # 未实现收益（万元）
    },
    ...
]
```

---

## AI辅助提示词

### 提示词1：交割单读取模块
```
我正在开发一个私募基金报告生成系统，需要实现交割单Excel读取模块。

任务要求：
1. 创建 data/reader.py 模块
2. 实现 read_excel() 函数，读取Excel文件
3. 实现 validate_data() 函数，验证数据格式

Excel文件字段（可能的中文列名）：
- 交易日期（可能是：日期、交易时间等）
- 股票代码（6位数字）
- 股票名称（可能缺失）
- 交易方向（可能是：买入/卖出、买/卖、B/S等）
- 成交数量（股数）
- 成交价格（元/股）
- 成交金额（元）
- 手续费（元）
- 印花税（元，卖出时才有）

技术要求：
1. 使用pandas读取Excel
2. 处理编码问题（GBK/UTF-8）
3. 统一日期格式为 'YYYY-MM-DD'
4. 统一交易方向为 '买入'/'卖出'
5. 数据清洗：去除空行、异常值
6. 数据验证：检查必需字段、格式、逻辑（持仓不能为负）

输出格式：
DataFrame，列名：date, code, name, direction, quantity, price, amount, fee, stamp_tax

请帮我实现这个模块，代码要健壮，包含异常处理。
```

### 提示词2：持仓计算模块（完整版）
```
我正在开发一个私募基金报告生成系统，需要实现持仓计算模块。

任务要求：
1. 创建 calc/position.py 模块
2. 实现以下函数：
   - calculate_position_quantity() - 计算持仓数量
   - calculate_position_cost() - 计算持仓成本（加权平均法）
   - calculate_avg_cost() - 计算平均成本单价
   - calculate_position_value() - 计算持仓市值
   - calculate_profit_loss() - 计算盈亏金额和盈亏比例
   - calculate_position_percentage() - 计算持仓占比
   - calculate_realized_profit() - 计算已实现收益
   - calculate_unrealized_profit() - 计算未实现收益
   - calculate_positions() - 计算指定日期的所有持仓（完整版）
   - calculate_daily_positions() - 计算每日持仓（完整版）

计算公式：
1. 持仓数量 = Σ(买入数量) - Σ(卖出数量)
2. 持仓成本 = Σ(买入金额 + 买入手续费)（只计算买入，卖出不减少成本）
3. 平均成本单价 = 持仓成本 / 持仓数量（元/股）
4. 持仓市值 = 当前价格 × 持仓数量
5. 盈亏金额 = 持仓市值 - 持仓成本
6. 盈亏比例 = 盈亏金额 / 持仓成本 × 100%
7. 持仓占比 = 该股票市值 / 总资产 × 100%
8. 已实现收益 = Σ(卖出金额 - 卖出成本 - 手续费 - 印花税)
9. 未实现收益 = Σ(持仓市值 - 持仓成本)
10. 总资产 = 持仓市值 + 现金余额
11. 现金余额 = 初始资金 - 总买入金额 - 买入手续费 + 总卖出金额 - 卖出手续费 - 印花税

输入数据格式：
- transactions: DataFrame，包含列：date, code, name, direction, quantity, price, amount, fee, stamp_tax

输出格式：
- 持仓字典（完整版）：{code: {quantity, cost, avg_cost, market_value, profit_loss, profit_loss_pct, position_pct, name}}
- 每日持仓列表（完整版）：[{date, positions, total_assets, stock_value, cash, realized_profit, unrealized_profit}, ...]

价格获取：
- 实现 get_stock_price() 函数（Mock版本）
- 方案：使用该股票最近一次交易价格，如果没有则返回10.0

技术要求：
1. 所有金额单位：万元（除平均成本单价为元/股）
2. 使用加权平均法计算持仓成本（不是FIFO）
3. 处理非交易日（使用最近交易日价格）
4. 所有函数必须有类型注解和docstring
5. 遵循PEP 8规范

请帮我实现这些函数，确保计算准确，包含所有必需参数。
```

### 提示词3：数据验证和优化
```
我正在优化持仓计算模块，需要：

1. 实现数据验证函数
   - 验证持仓数量不能为负
   - 验证总资产 = 持仓市值 + 现金
   - 验证数据格式

2. 优化性能
   - 使用pandas向量化操作替代循环
   - 实现价格缓存机制
   - 批量计算优化

3. 实现数据格式转换函数
   - format_positions_for_pdf() - 将持仓数据转换为PDF表格格式
   - 输出格式：List[List[str]]，每行是一个列表

请帮我实现这些功能。
```

### 提示词4：主程序集成
```
我需要创建主程序 main.py，整合所有模块。

模块依赖：
- data.reader: read_excel, validate_data
- calc.position: calculate_positions, calculate_daily_positions
- calc.metrics: calculate_nav, calculate_returns（开发者B的模块）
- charts.generator: plot_nav_trend（开发者C的模块）
- pdf.generator: PDFGenerator（开发者C的模块）

功能要求：
1. 读取配置文件 config.py
2. 读取交割单Excel
3. 计算持仓和每日数据
4. 调用B的模块计算指标
5. 调用C的模块生成图表和PDF
6. 实现命令行参数解析
7. 实现错误处理和日志记录

请帮我实现主程序，代码要清晰，包含完整的错误处理。
```

---

## 测试检查清单

### 功能测试
- [ ] Excel文件读取成功
- [ ] 数据清洗正确（空行、异常值处理）
- [ ] 数据验证通过（格式、逻辑）
- [ ] 持仓数量计算准确
- [ ] 持仓成本计算准确（加权平均法）
- [ ] 持仓市值计算准确
- [ ] 每日持仓数据生成正确
- [ ] 价格获取正常（包括非交易日）

### 数据验证测试
- [ ] 持仓数量 = 买入数量 - 卖出数量
- [ ] 持仓成本 = 所有买入金额 + 手续费
- [ ] 总资产 = 持仓市值 + 现金余额
- [ ] 持仓数量不能为负

### 边界情况测试
- [ ] 空持仓情况
- [ ] 单只股票情况
- [ ] 大量交易数据性能
- [ ] 非交易日价格获取
- [ ] 数据缺失情况

---

## 注意事项

### 1. 持仓成本计算
- **重要**：使用加权平均法，不是FIFO
- 只计算买入的成本，卖出不减少成本（卖出时成本已实现）
- 成本包含手续费

### 2. 单位转换
- Excel中的金额单位是**元**
- 计算后转换为**万元**（除以10000）
- 持仓数量单位是**股**（不转换）

### 3. 日期处理
- 统一使用 'YYYY-MM-DD' 格式
- 处理非交易日（周末、节假日）
- 按时间顺序处理交易

### 4. 数据验证
- 持仓数量不能为负（卖出不能超过持仓）
- 总资产必须等于持仓市值 + 现金
- 所有数值必须为正数（除盈亏可能为负）

### 5. 性能优化
- 使用pandas向量化操作
- 实现价格缓存
- 避免重复计算

---

## 参考文档

- **模版模块实现.md**：第8.1节（持仓相关计算）
- **项目分析.md**：第3.1节（数据读取模块）、第3.2节（持仓计算模块）
- **任务分配.md**：开发者A的任务清单

---

**文档版本**：v1.0  
**创建日期**：2024年  
**最后更新**：2024年

