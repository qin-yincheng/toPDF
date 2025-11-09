# 私募基金报告生成系统

基于交割单数据自动生成私募基金分析报告（PDF），包含完整的数据处理、指标计算和图表生成功能。

## ✨ 功能特性

- 📊 **16种专业图表**：涵盖收益分析、持仓分析、归因分析等
- 📈 **9个标准数据接口**：完全符合规范
- 🎯 **自动化处理**：从交割单到PDF报告一键生成
- 💾 **智能缓存**：价格数据本地缓存，避免重复请求
- 🔄 **实时计算**：支持自定义统计区间和基准指数

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone <repository-url>
cd toPDF

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置 Tushare Token（必需）
export TUSHARE_TOKEN="your_token_here"
# 注册地址：https://tushare.pro

# 4. 准备数据
# generate_report.py 会自动检测并转换 Excel 文件
# 确保 docs/交割单.xlsx 或 docs/交割单.csv 存在即可

# 5. 生成PDF报告
python generate_report.py
```

**输出**：`私募基金报告_完整版.pdf`（约6.3MB，16页完整报告）

**📝 注意**：
- ✅ `generate_report.py` 会自动检查并转换 Excel 文件
- ✅ 如果 CSV 已存在，直接使用，不会重复转换
- ✅ 支持直接提供 CSV 或 Excel 文件

## 📁 项目结构

```
toPDF/
├── calc/                          # 核心计算模块
│   ├── data_provider.py           # ⭐ 9个标准数据接口
│   ├── report_bridge.py           # ⭐ PDF数据构建器（16个数据集）
│   ├── attribution.py             # 绩效归因计算
│   ├── metrics.py                 # 风险收益指标
│   ├── position.py                # 持仓计算引擎
│   ├── trading.py                 # 交易统计
│   ├── utils.py                   # 工具函数
│   └── formatter.py               # 数据格式化
│
├── charts/                        # 图表生成模块（16个）
│   ├── 1_1.py                     # 总体表现表格
│   ├── 1_2.py                     # 产品规模总览
│   ├── 1_3.py                     # 单位净值表现
│   ├── 1_4.py                     # 日收益表现
│   ├── 1_5.py                     # 收益分析
│   ├── 1_6.py                     # 指标分析
│   ├── 1_7.py                     # 动态回撤
│   ├── 2_1.py                     # 大类持仓时序
│   ├── 2_2.py                     # 股票仓位时序
│   ├── 2_3.py                     # 期末持仓表格
│   ├── 2_4.py                     # 流动性资产时序
│   ├── 3_1.py                     # 持股行业分析（饼图/柱状图/表格）
│   ├── 3_2.py                     # 持股行业占比时序
│   ├── 3_3.py                     # 持股行业偏离度时序
│   ├── 3_4.py                     # 大类资产绩效归因
│   ├── 4_1.py                     # Brinson归因
│   ├── 4_2.py                     # 股票行业归因
│   ├── 5_1.py                     # 股票绩效归因
│   ├── 5_2.py                     # 个股持仓节点
│   ├── 6_4.py                     # 换手率表格
│   └── 6_5.py                     # 期间交易
│
├── pdf/                           # PDF生成模块
│   └── pages.py                   # ⭐ 页面布局和图表组装
│
├── data/                          # 数据处理模块
│   └── reader.py                  # Excel/CSV读取和转换
│
├── docs/                          # 文档和原始数据
│   ├── 交割单.csv                 # ⭐ 交易数据（79203条）
│   ├── 开发者A.md                 # 接口规范
│   ├── 开发者A补充.md             # 补充说明
│   └── 模版模块实现.md            # 实现文档
│
├── demo/                          # 演示和示例
│   └── daily_asset_distribution.csv  # 每日资产分布
│
├── config.py                      # ⭐ 全局配置
├── generate_report.py             # ⭐ PDF生成入口（包含自动转换）
└── requirements.txt               # 依赖列表
```

## 🔄 运行流程

### 完整流程图

```
交割单.csv
    ↓
┌──────────────────────────────────────────┐
│  1. 数据读取与处理 (data_provider.py)    │
│  - 解析交割单（79,203笔交易）             │
│  - 计算每日持仓（3,958天）                │
│  - 获取行业映射（3,667只股票）            │
│  - 获取基准数据（沪深300）                │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  2. 指标计算 (attribution/metrics)       │
│  - 收益率计算（成立以来+5个区间）         │
│  - 风险指标（波动率/夏普/最大回撤）       │
│  - 归因分析（Brinson/行业/个股）         │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  3. 数据构建 (report_bridge.py)          │
│  - 构建16个数据集                        │
│  - 格式化为图表所需格式                  │
│  - 数据验证和补全                        │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  4. 图表生成 (charts/*.py)               │
│  - 生成16种图表（matplotlib）            │
│  - 自动处理空数据                        │
│  - 统一样式和字体                        │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  5. PDF组装 (pdf/pages.py)               │
│  - 页面布局和排版                        │
│  - 图表嵌入和缩放                        │
│  - 生成最终PDF文件                       │
└──────────────────────────────────────────┘
    ↓
私募基金报告_完整版.pdf (6.3MB)
```

### 详细步骤说明

#### 步骤1：数据获取（`calc/data_provider.py`）

**9个标准数据接口**：

```python
# 1. 每日持仓序列
daily_positions = get_daily_positions()
# 返回：3958天数据，每天包含 total_assets, cash, stocks 等

# 2. 期间持仓明细  
position_details = get_position_details(
    period_start="2015-01-05",
    period_end="2025-11-05"
)
# 返回：3761只股票明细，含市值、收益、现金流

# 3. 行业映射
industry_mapping = get_industry_mapping()
# 返回：{股票代码: 行业名称} 字典，3667只股票

# 4. 交易记录
transactions = get_transactions()
# 返回：79203笔交易记录

# 5. 统计区间配置
periods = get_periods_config()
# 返回：5个区间（成立以来、近一年、近六月、近三月、近一月）

# 6-7. 基准数据
benchmark_daily = get_benchmark_daily_data("000300.SH")
benchmark_returns = get_benchmark_returns("000300.SH", periods)
# 沪深300的日度行情和区间收益率

# 8-9. 基准行业数据
industry_weights = get_benchmark_industry_weights("000300.SH", date)
industry_returns = get_benchmark_industry_returns("000300.SH", period_start, period_end)
# 基准行业收益包含按期间与按日两种格式：
# {
#     "period_returns": {"银行": 0.0321, ...},
#     "daily_returns": {"2024-11-04": {"银行": 0.0012, ...}, ...}
# }
```

#### 步骤2：数据构建（`calc/report_bridge.py`）

**16个数据构建函数**，每个对应一组图表：

```python
# 收益与风险分析（7个）
build_overall_performance_data()      # 总体表现
build_scale_overview_data()           # 规模总览
build_nav_performance_data()          # 净值表现
build_daily_return_performance_data() # 日收益
build_period_returns_data()           # 区间收益
build_metrics_data()                  # 风险指标
build_drawdown_data()                 # 回撤分析

# 持仓分析（5个）
build_asset_allocation_series()       # 大类资产配置
build_end_holdings_data()             # 期末持仓
build_stock_position_series()         # 股票仓位
build_liquidity_series()              # 流动性资产
build_industry_attribution_data()     # 行业分析

# 归因分析（2个）
build_asset_class_attribution()       # 大类资产归因
build_brinson_data()                  # Brinson归因

# 交易分析（2个）
build_turnover_data()                 # 换手率
build_period_transaction_data()       # 期间交易
```

#### 步骤3：图表生成（`charts/*.py`）

每个图表模块包含：
- 数据验证和空值处理
- matplotlib 图表绘制
- 统一的中文字体配置
- 返回 figure 对象或保存为文件

```python
# 示例：生成收益分析图表
from charts.1_5 import plot_return_analysis_table

fig = plot_return_analysis_table(
    data=period_returns_data,
    return_figure=True,
    figsize=(16, 8)
)
```

#### 步骤4：PDF生成（`pdf/pages.py`）

**页面布局策略**：
- A4横向（297mm × 210mm）
- 页边距：左右各20mm，上下各15mm
- 自动分页：根据图表高度计算剩余空间
- 图表自适应缩放

```python
# 核心流程
def generate_pdf_pages(c, data, ...):
    # 1. 设置页面和字体
    # 2. 遍历16个图表模块
    # 3. 检查页面剩余空间
    # 4. 自动分页和图表插入
    # 5. 保存PDF文件
```
## 📖 核心API使用

### 数据接口层（data_provider.py）

详细示例见 [`docs/数据接口使用示例.md`](docs/数据接口使用示例.md)

```python
from calc.data_provider import (
    get_daily_positions,
    get_position_details,
    get_benchmark_returns,
    get_benchmark_industry_weights
)

# 获取每日持仓数据
daily_data = get_daily_positions()
# 返回：[
#   {"date": "2015-01-05", "total_assets": 1601.53, "cash": 1600.00, ...},
#   ...  # 3958天
# ]

# 获取期间持仓明细
details = get_position_details(
    period_start="2024-01-01",
    period_end="2024-12-31"
)
# 返回：{
#   "total_assets": 324898.33,
#   "total_profit": 323297.42,
#   "position_details": [...]  # 持仓明细列表
# }

# 获取基准收益率
returns = get_benchmark_returns("000300.SH")
# 返回：{"period_returns": {"成立以来": 27.07, "近一年": 5.23, ...}}

# 获取基准行业权重
weights = get_benchmark_industry_weights("000300.SH", "2024-11-01")
# 返回：{"银行": 11.31, "白酒": 7.82, ...}
```

### 报告生成层（report_bridge.py）

```python
from calc.report_bridge import (
    build_period_returns_data,
    build_asset_allocation_series,
    build_brinson_data
)

# 构建收益分析数据
returns_data = build_period_returns_data(
    daily_positions=daily_positions,
    benchmark_data=benchmark_data,
    periods=periods
)

# 构建资产配置数据
allocation_data = build_asset_allocation_series(
    daily_positions=daily_positions
)

# 构建Brinson归因数据
brinson_data = build_brinson_data(
    daily_positions=daily_positions,
    industry_mapping=industry_mapping,
    benchmark_industry_weights=weights,
    benchmark_industry_returns=returns
)
```

### PDF生成

```python
from pdf.generator import generate_pdf_report

# 一键生成完整PDF报告
generate_pdf_report(
    output_path="私募基金报告_完整版.pdf",
    csv_path="docs/交割单.csv",
    benchmark_code="000300.SH"
)
```

## ⚙️ 配置说明

### 环境变量

```bash
# Tushare Token（必需）- 用于获取股票价格和基准数据
export TUSHARE_TOKEN="your_token_here"
# 注册地址：https://tushare.pro/register

# 可选：自定义配置
export INITIAL_CAPITAL=10000000  # 初始资金（元）
```

### config.py 配置

```python
# 全局配置（通常无需修改）
DOCS_DIR = "docs"                    # 文档目录
INITIAL_CAPITAL = 10_000_000.0       # 初始资金10万元（单位：元）
ESTABLISH_DATE = None                # 自动从数据推断
BENCHMARK_CODE = "000300.SH"         # 默认基准：沪深300
```

### 数据格式要求

**输入文件**：`docs/交割单.csv`

必需列：
- `code`：股票代码（6位数字，如 000001）
- `buy_time`/`sell_time`：交易时间（YYYY-MM-DD HH:MM:SS）
- `buy_price`/`sell_price`：交易价格（元）
- `buy_number`/`sell_number`：交易数量（股）
- `buy_money`/`sell_money`：交易金额（元）

**数据单位约定**：
- 💰 资产/市值/收益：**万元**
- 💵 交易金额：**元**
- 📅 日期：**YYYY-MM-DD**
- 📊 百分比：**%**（如 15.6 表示 15.6%）

## 📊 数据说明

### 输入数据

| 文件 | 说明 | 规模 |
|------|------|------|
| `docs/交割单.csv` | 交易记录 | 79,203笔交易 |
| Tushare API | 股票行情 | 3,768只股票 |
| Tushare API | 基准数据 | 沪深300（2,634天） |

### 输出数据

| 文件 | 说明 | 大小 |
|------|------|------|
| `私募基金报告_完整版.pdf` | 完整分析报告 | 6.3MB，16页 |
| `demo/daily_asset_distribution.csv` | 每日资产分布 | 3,958行 |

### 缓存机制

```bash
docs/.cache/
├── prices_2015-01-05_2025-11-05.pkl  # 价格数据缓存
└── industry_mapping.pkl               # 行业映射缓存

# 清除缓存
rm -rf docs/.cache

# 缓存自动更新条件：
# 1. 日期范围变化
# 2. 缓存文件不存在
# 3. 数据超过30天未更新
```

## 🎨 图表列表

报告包含16种专业图表：

### 1. 收益与风险（7个图表）
- 📊 总体表现表格：关键指标汇总
- 📈 产品规模总览：资产规模时序
- 📉 单位净值表现：净值走势对比基准
- 📊 日收益表现：日收益率分布
- 📋 收益分析表格：多区间收益对比
- 📊 指标分析表格：风险收益指标
- 📉 动态回撤：最大回撤可视化

### 2. 持仓分析（5个图表）
- 📊 大类持仓时序：股票/债券/现金配置
- 📋 期末持仓表格：资产负债汇总
- 📈 股票仓位时序：股票仓位变化
- 📊 流动性资产时序：流动性监控
- 🥧 持股行业分析：行业分布饼图+柱状图+表格

### 3. 时序分析（2个图表）
- 📈 持股行业占比时序：行业配置堆叠图
- 📉 持股行业偏离度：相对基准偏离

### 4. 归因分析（4个图表）
- 📊 大类资产绩效归因：资产类别贡献
- 📈 Brinson归因：选择收益+配置收益
- 📊 股票行业归因：行业收益排名（盈利TOP10+亏损TOP10）
- 📊 股票绩效归因：个股收益排名（盈利TOP10+亏损TOP10）

### 5. 个股与交易（3个图表）
- 📊 个股持仓节点：持仓规模分布
- 📋 换手率表格：年化换手率
- 📊 期间交易：买卖金额统计

## 🧪 测试与演示

```bash
# 1. 快速测试（推荐）
python generate_report.py
# 一键生成完整PDF报告，自动处理Excel转换

# 2. 数据接口测试
python -c "
from calc.data_provider import get_daily_positions
data = get_daily_positions()
print(f'获取 {len(data)} 天数据')
print(f'最新日期: {data[-1][\"date\"]}')
print(f'总资产: {data[-1][\"total_assets\"]:.2f} 万元')
"

# 3. 生成每日资产分布CSV
python -m demo.generate_distribution_csv
```

## � 故障排查

### 常见问题

**Q1: `ModuleNotFoundError: No module named 'tushare'`**
```bash
pip install -r requirements.txt
```

**Q2: `TushareException: 请设置TOKEN`**
```bash
export TUSHARE_TOKEN="your_token"
# 或在代码中：ts.set_token("your_token")
```

**Q3: PDF中图表显示为空或"暂无数据"**

原因：数据缺失或计算异常

解决方案：
```bash
# 1. 检查数据文件
ls -lh docs/交割单.csv

# 2. 清除缓存重新生成
rm -rf docs/.cache
python generate_report.py

# 3. 检查日志
python generate_report.py 2>&1 | grep "失败"
```

**Q4: `list index out of range` 或其他数据错误**

可能原因：
- 交割单数据格式不正确
- 日期范围问题
- 网络问题导致价格数据获取失败

解决方案：
```bash
# 1. 验证数据格式
python -c "
import pandas as pd
df = pd.read_csv('docs/交割单.csv', encoding='utf-8-sig')
print(df.head())
print(df.columns.tolist())
"

# 2. 重新获取价格数据
rm -rf docs/.cache
python generate_report.py
```

**Q5: 图表中文显示为方框**

系统缺少中文字体，代码会自动尝试以下字体：
- SimHei（黑体）
- Microsoft YaHei（微软雅黑）
- Arial Unicode MS
- DejaVu Sans

如仍有问题，安装中文字体即可。

## 🔧 开发指南

### 添加新图表

1. **创建图表模块**（如 `charts/new_chart.py`）：
```python
def plot_new_chart(data, return_figure=False, figsize=(16, 8)):
    """新图表生成函数"""
    setup_chinese_font()
    
    # 数据验证
    if not data:
        return empty_chart("暂无数据")
    
    # 绘制图表
    fig, ax = plt.subplots(figsize=figsize)
    # ... 绘图代码 ...
    
    if return_figure:
        return fig
```

2. **添加数据构建器**（在 `calc/report_bridge.py`）：
```python
def build_new_chart_data(daily_positions, ...):
    """构建新图表所需数据"""
    # 数据计算和格式化
    return {
        "chart_data": [...],
        "summary": {...}
    }
```

3. **集成到PDF**（在 `pdf/pages.py`）：
```python
from charts.new_chart import plot_new_chart

# 在 generate_pdf_pages 中添加
fig_new = plot_new_chart(
    data=safe_get('new_chart_data'),
    return_figure=True
)
insert_figure(c, fig_new, x, y, width, height)
```

### 修改统计区间

编辑 `calc/data_provider.py` 的 `get_periods_config()`：

```python
def get_periods_config(csv_path=None):
    # 添加自定义区间
    periods = {
        "成立以来": (establish_date, latest_date),
        "近一年": (year_ago, latest_date),
        "近两年": (two_years_ago, latest_date),  # 新增
        "自定义": ("2023-01-01", "2023-12-31"),  # 新增
    }
    return periods
```

### 更换基准指数

```python
# 方法1：环境变量
export BENCHMARK_CODE="000905.SH"  # 中证500

# 方法2：代码修改 config.py
BENCHMARK_CODE = "399006.SZ"  # 创业板指
```

支持的指数：
- `000300.SH` - 沪深300
- `000905.SH` - 中证500  
- `000852.SH` - 中证1000
- `399006.SZ` - 创业板指
- `000001.SH` - 上证指数

## 🎨 跨平台字体配置

项目支持 **macOS、Windows、Linux** 跨平台中文显示，自动检测并使用最佳字体。

### 字体自动选择

**macOS**：PingFang SC → PingFang HK → Heiti SC → STHeiti  
**Windows**：Microsoft YaHei → SimHei → SimSun  
**Linux**：WenQuanYi Micro Hei → Noto Sans CJK

### 测试字体配置

```bash
# 查看系统可用字体和当前配置
python3 charts/font_config.py
```

会生成 `font_test.png` 测试图片，检查中文是否正常显示。

### 问题排查

**问题**：PDF 中图表左上角中文显示为黑色方块

**原因**：系统缺少中文字体或 matplotlib 未正确配置

**解决方案**：

1. **macOS**（通常自带）：
   ```bash
   # 检查字体
   ls /System/Library/Fonts/ | grep -i pingfang
   ```

2. **Windows**：确保已安装微软雅黑（Windows Vista+ 自带）

3. **Linux (Ubuntu/Debian)**：
   ```bash
   # 安装文泉驿字体
   sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei
   
   # 或安装 Google Noto 字体
   sudo apt-get install fonts-noto-cjk
   ```

4. **清除字体缓存**（如果更新字体后仍有问题）：
   ```bash
   rm -rf ~/.matplotlib/fontlist*.json
   ```

5. **验证修复**：重新生成 PDF 并检查图表

📖 **详细说明**：参见 [字体配置文档](docs/FONT_CONFIG.md)

## 📋 相关文档

- [接口规范](docs/开发者A.md) - 数据接口详细说明
- [补充说明](docs/开发者A补充.md) - 额外需求和说明
- [模版实现](docs/模版模块实现.md) - 实现细节文档
- [任务分配](docs/任务分配.md) - 开发者分工
- [字体配置](docs/FONT_CONFIG.md) - 跨平台字体配置说明

## 🛠️ 技术栈

- **Python 3.8+**
- **pandas** - 数据处理
- **tushare** - 金融数据API
- **matplotlib** - 图表绘制
- **reportlab** - PDF生成
- **numpy** - 数值计算

## 📝 开发日志

### v1.1.0 (2025-11-09)

✅ **跨平台字体支持**
- 实现自动字体检测（macOS/Windows/Linux）
- 创建统一的字体配置模块 `font_config.py`
- 更新所有21个图表文件使用统一配置
- 添加字体测试工具
- 修复 Mac 上中文显示为方块的问题

🐛 **Bug 修复**
- 修复期末持仓显示"100%证券"应为"100%现金"的问题
- 优化资产分类逻辑（直接计算股票和现金）

### v1.0.0 (2025-11-08)

✅ **完成所有功能模块**
- 实现9个标准数据接口（100%符合规范）
- 实现16种图表生成模块
- 完成PDF自动生成功能
- 修复所有图表渲染问题
- 添加完善的空数据处理

📊 **性能指标**
- 处理79,203笔交易记录
- 计算3,958天持仓数据
- 追踪3,761只股票持仓
- 生成6.3MB完整PDF报告
- 运行时间：约30-60秒（首次），5-10秒（有缓存）

🎯 **质量保证**
- 所有16个图表模块正常工作
- 空数据场景自动处理
- 数据单位统一（万元）
- 日期格式标准化
- 中文字体跨平台适配

## 📄 许可证

MIT License

## 👥 贡献者

- 开发者A - 数据层实现
- 开发者B - 计算层实现  
- 开发者C - 图表与PDF生成
