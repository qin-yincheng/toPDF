# 私募基金报告生成系统

基于交割单数据自动生成私募基金报告，提供标准化数据接口。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置环境变量
export TUSHARE_TOKEN="your_token_here"

# 3. 生成交割单 CSV
python main.py

# 4. 运行完整数据流演示
python -m demo.show_data_flow
```

## 项目结构

```
toPDF/
├── calc/
│   └── data_provider.py  ⭐ 统一数据接口（9个标准接口）
├── data/                  数据层：Excel → CSV
├── demo/                  示例和演示
│   └── show_data_flow.py  ⭐ 完整数据流演示
├── docs/                  文档和原始数据
│   ├── 开发者A提供数据.md  接口规范
│   └── 数据接口使用示例.md  使用指南
└── main.py               ⭐ 主程序：生成 CSV
```

## 核心功能

### ✅ 开发者A（数据层）- 已完成

**标准化数据接口**（完全符合 `docs/开发者A提供数据.md` 规范）
   - Excel 交割单读取
   - 数据标准化（代码补零、金额格式化）
   - CSV 导出

2. **持仓计算**
   - 每日持仓数量计算
   - 股票市值计算（Tushare API）
   - 现金占比计算
   - 总资产统计
3. **数据接口** - 9个标准接口（完全符合《开发者A提供数据.md》）
   - 每日持仓序列 / 期间持仓明细 / 行业映射 / 交易记录
   - 统计区间配置 / 基准日度行情 / 基准收益率
   - 基准行业权重 / 基准行业收益率

4. **指标计算** - 待开发（开发者B）
5. **图表生成** - 待开发（开发者C）
6. **PDF 生成** - 待开发（开发者C）

## 📖 API 使用示例

详细示例见 [`docs/数据接口使用示例.md`](docs/数据接口使用示例.md)

```python
from calc.data_provider import (
    get_daily_positions, get_position_details,
    get_benchmark_returns, get_benchmark_industry_weights
)

# 每日持仓: {"date": "2024-12-31", "total_assets": 2263.44, ...}
daily_data = get_daily_positions()

# 基准收益率: {"period_returns": {"成立以来": 27.07, ...}}
returns = get_benchmark_returns("000300.SH")

# 基准行业权重: {"银行": 11.31, "白酒": 7.82, ...}
weights = get_benchmark_industry_weights("000300.SH", "2024-11-01")
```

## ⚙️ 配置

**Tushare Token**（必需）
```bash
export TUSHARE_TOKEN="your_token"  # 访问 https://tushare.pro 注册
```

**config.py** - 自动配置，无需修改
```python
INITIAL_CAPITAL = 10_000_000.0  # 初始资金（元）
ESTABLISH_DATE = None           # 自动从数据推断
```

**数据单位**
- 资产/市值/收益：**万元**
- 交易金额：**元**
- 日期：**YYYY-MM-DD**

## 📊 数据说明

**输入**：`docs/交割单.xlsx`（必需列：code, buy/sell_time, buy/sell_price, buy/sell_number, buy/sell_money）

**输出**：
- `docs/交割单.csv` - 79203条交易记录
- `demo/daily_asset_distribution.csv` - 3958天资产分布

**缓存**：`docs/.cache/` - 价格数据自动缓存（清除：`rm -rf docs/.cache`）

## 🧪 测试

```bash
# 完整流程（推荐）
python -m demo.show_data_flow

# 数据转换
python main.py  # 生成交割单.csv

# 资产分布
python -m demo.generate_distribution_csv
```

## 📚 文档

- [接口规范](docs/开发者A提供数据.md) - 7项数据接口要求
- [使用示例](docs/数据接口使用示例.md) - 详细API调用示例
- [任务分配](docs/任务分配.md) - 开发者分工

## ❓ 常见问题

**Q: 持仓明细为空？**  
A: 默认关闭。需要时：`get_daily_positions(include_positions=True)`

**Q: 行业信息缺失？**  
A: 设置环境变量：`export TUSHARE_TOKEN="your_token"`

**Q: 如何添加统计区间？**  
A: 修改 `calc/data_provider.py` 的 `get_periods_config()`

## 🛠️ 技术栈

Python 3.8+ | pandas | tushare | matplotlib | reportlab
