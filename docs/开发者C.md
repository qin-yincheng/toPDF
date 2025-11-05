# 开发者C详细工作文档

## 职责概述

开发者C负责**展示层**，是整个系统的最终输出接口。主要工作包括：
1. 图表生成（matplotlib）- 3个核心图表
2. PDF生成（reportlab）- 2页报告
3. 页面布局和样式设计
4. 中文字体配置
5. 图表与PDF的集成

**总工作量**：18小时（Day1: 8h, Day2: 6h, Day3: 4h）

---

## Day 1 任务详解

### 任务C1：环境准备 [2小时]

#### 模块位置
项目根目录和配置文件

#### 详细要求

##### 1. 创建项目结构
确保以下目录和文件存在：
```
toPDF/
├── charts/
│   └── generator.py      # 图表生成模块（待创建）
├── pdf/
│   ├── generator.py     # PDF生成主类（待创建）
│   └── pages.py          # 页面生成函数（待创建）
├── requirements.txt      # 依赖列表（需要更新）
└── config.py             # 配置文件（由A创建，C需要读取）
```

##### 2. 配置 requirements.txt
```txt
pandas>=1.5.0
openpyxl>=3.0.0
matplotlib>=3.5.0
reportlab>=3.6.0
numpy>=1.20.0
```

##### 3. 测试matplotlib和reportlab
**测试脚本**：
```python
# 测试matplotlib中文字体
import matplotlib.pyplot as plt
import matplotlib

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 测试图表
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_title('测试中文标题')
plt.savefig('test_chart.png', dpi=300)
print("matplotlib测试成功")

# 测试reportlab
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

c = canvas.Canvas("test.pdf", pagesize=A4)
c.drawString(100, 750, "测试中文")
c.save()
print("reportlab测试成功")
```

---

### 任务C2：图表基础框架 [6小时]

#### 模块位置
`charts/generator.py`

#### 详细要求

##### 1. 图表基础配置
**函数**：`setup_chinese_font()`

**功能**：配置matplotlib中文字体

**实现**：
```python
import matplotlib.pyplot as plt
import matplotlib
from typing import Optional

def setup_chinese_font() -> None:
    """
    配置matplotlib中文字体
    
    支持的字体（按优先级）：
    1. SimHei（黑体）
    2. Microsoft YaHei（微软雅黑）
    3. Arial Unicode MS（如果系统有）
    
    注意:
        Windows系统通常有SimHei和Microsoft YaHei
        Mac系统可能需要安装中文字体
    """
    # 设置字体列表（按优先级）
    font_list = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS', 'DejaVu Sans']
    
    plt.rcParams['font.sans-serif'] = font_list
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
    # 设置默认字体大小
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9
```

##### 2. 净值走势图
**函数**：`plot_nav_trend()`

**功能**：绘制单位净值走势图

**参考模版**：模版模块实现.md 1.4节

**实现**：
```python
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def plot_nav_trend(
    nav_data: List[Dict[str, Any]], 
    save_path: str = 'nav_trend.png',
    figsize: tuple = (12, 6)
) -> str:
    """
    绘制净值走势图
    
    参数:
        nav_data: 净值数据列表
            [{date: str, nav: float, total_assets: float}, ...]
        save_path: 保存路径
        figsize: 图片大小（宽，高）
    
    返回:
        str: 保存的图片文件路径
    
    图表要求:
        1. X轴：日期
        2. Y轴：单位净值
        3. 折线图，蓝色实线
        4. 标题："单位净值走势"
        5. 网格线
        6. 图例（如果有）
        7. 日期格式化为 YYYY-MM-DD
        8. DPI=300，保存为PNG格式
    """
    setup_chinese_font()
    
    # 提取数据
    dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in nav_data]
    navs = [d['nav'] for d in nav_data]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制折线图
    ax.plot(dates, navs, 'b-', linewidth=2, label='单位净值')
    
    # 设置标题和标签
    ax.set_title('单位净值走势', fontsize=14, fontweight='bold')
    ax.set_xlabel('日期', fontsize=11)
    ax.set_ylabel('单位净值', fontsize=11)
    
    # 格式化日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    
    # 添加网格
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加图例
    ax.legend(loc='best')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return save_path
```

##### 3. 回撤图
**函数**：`plot_drawdown()`

**功能**：绘制动态回撤图

**参考模版**：模版模块实现.md 2.1节

**实现**：
```python
def plot_drawdown(
    drawdown_data: List[Dict[str, Any]],
    save_path: str = 'drawdown.png',
    figsize: tuple = (12, 6)
) -> str:
    """
    绘制动态回撤图
    
    参数:
        drawdown_data: 回撤数据列表（来自开发者B的calculate_daily_drawdowns）
            [{date: str, drawdown: float, peak_nav: float}, ...]
        save_path: 保存路径
        figsize: 图片大小
    
    返回:
        str: 保存的图片文件路径
    
    图表要求:
        1. X轴：日期
        2. Y轴：回撤百分比（%）
        3. 折线图，蓝色实线
        4. 填充区域（alpha=0.3）
        5. 标题："动态回撤"
        6. Y轴反转（回撤向下显示）
        7. 网格线
        8. DPI=300
    """
    setup_chinese_font()
    
    # 提取数据
    dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in drawdown_data]
    drawdowns = [d['drawdown'] for d in drawdown_data]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    # 绘制折线图
    ax.plot(dates, drawdowns, 'b-', linewidth=2, label='产品回撤')
    
    # 填充区域
    ax.fill_between(dates, drawdowns, 0, alpha=0.3, color='blue')
    
    # 设置标题和标签
    ax.set_title('动态回撤', fontsize=14, fontweight='bold')
    ax.set_xlabel('日期', fontsize=11)
    ax.set_ylabel('回撤(%)', fontsize=11)
    
    # Y轴反转（回撤向下显示）
    ax.invert_yaxis()
    
    # 格式化日期
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    
    # 添加网格
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加图例
    ax.legend(loc='best')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return save_path
```

##### 4. 持仓分布图
**函数**：`plot_position_distribution()`

**功能**：绘制持仓分布图（饼图或横向柱状图）

**参考模版**：模版模块实现.md（行业分布饼图思路）

**实现**：
```python
def plot_position_distribution(
    positions: Dict[str, Dict[str, Any]],
    save_path: str = 'position_distribution.png',
    figsize: tuple = (10, 6),
    chart_type: str = 'bar'  # 'bar' 或 'pie'
) -> str:
    """
    绘制持仓分布图
    
    参数:
        positions: 持仓字典
            {code: {'quantity': float, 'market_value': float, ...}, ...}
        save_path: 保存路径
        figsize: 图片大小
        chart_type: 图表类型，'bar'（横向柱状图）或 'pie'（饼图）
    
    返回:
        str: 保存的图片文件路径
    
    图表要求:
        1. 显示持仓占比（持仓市值 / 总市值）
        2. 横向柱状图或饼图
        3. 标题："持仓分布"
        4. 显示前10大持仓（如果持仓数量多）
        5. DPI=300
    """
    setup_chinese_font()
    
    # 计算总市值
    total_value = sum([pos.get('market_value', 0) for pos in positions.values()])
    
    if total_value == 0:
        # 创建空图表
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, '暂无持仓数据', ha='center', va='center', fontsize=14)
        ax.set_title('持仓分布', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    
    # 计算持仓占比并排序
    position_list = []
    for code, pos_data in positions.items():
        market_value = pos_data.get('market_value', 0)
        percentage = (market_value / total_value * 100) if total_value > 0 else 0
        position_list.append({
            'code': code,
            'market_value': market_value,
            'percentage': percentage
        })
    
    # 按市值排序
    position_list.sort(key=lambda x: x['market_value'], reverse=True)
    
    # 只显示前10大持仓
    display_count = min(10, len(position_list))
    top_positions = position_list[:display_count]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=figsize)
    
    if chart_type == 'bar':
        # 横向柱状图
        codes = [p['code'] for p in top_positions]
        percentages = [p['percentage'] for p in top_positions]
        
        bars = ax.barh(range(len(codes)), percentages, color='steelblue', alpha=0.7)
        
        # 设置Y轴标签
        ax.set_yticks(range(len(codes)))
        ax.set_yticklabels(codes)
        
        # 设置标签
        ax.set_xlabel('持仓占比(%)', fontsize=11)
        ax.set_title('持仓分布', fontsize=14, fontweight='bold')
        
        # 添加数值标签
        for i, (bar, pct) in enumerate(zip(bars, percentages)):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{pct:.2f}%', ha='left', va='center')
        
        ax.grid(True, axis='x', alpha=0.3)
        
    else:
        # 饼图
        labels = [p['code'] for p in top_positions]
        sizes = [p['percentage'] for p in top_positions]
        
        # 如果有其他持仓，添加"其他"项
        if len(position_list) > display_count:
            other_value = sum([p['percentage'] for p in position_list[display_count:]])
            labels.append('其他')
            sizes.append(other_value)
        
        # 创建饼图
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 9}
        )
        
        ax.set_title('持仓分布', fontsize=14, fontweight='bold')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return save_path
```

#### 测试要求
- 使用mock数据测试每个图表函数
- 验证中文显示正常
- 验证图片保存成功
- 验证DPI=300

---

## Day 2 任务详解

### 任务C3：图表完成 [3小时]

#### 目标
与真实数据集成，完成所有图表

#### 详细要求

##### 1. 与真实数据集成
- 从开发者B获取净值数据
- 从开发者B获取回撤数据
- 从开发者A获取持仓数据
- 测试数据格式匹配

##### 2. 优化图表样式
**优化点**：
- 调整颜色方案
- 优化图例位置
- 调整字体大小
- 优化日期标签显示（避免重叠）

**示例优化**：
```python
# 优化日期标签显示
from matplotlib.dates import WeekdayLocator, DayLocator

# 设置日期刻度
ax.xaxis.set_major_locator(WeekdayLocator(interval=2))  # 每2周显示一次
ax.xaxis.set_minor_locator(DayLocator())
```

##### 3. 处理边界情况
- 数据为空的情况
- 数据点过少的情况（少于2个点）
- 持仓数量为0的情况

---

### 任务C4：PDF生成基础 [3小时]

#### 模块位置
`pdf/generator.py` 和 `pdf/pages.py`

#### 详细要求

##### 1. PDF生成主类
**文件**：`pdf/generator.py`

**类**：`PDFGenerator`

**实现**：
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, PageBreak, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import List, Callable, Optional
import os

class PDFGenerator:
    """
    PDF生成器主类
    
    功能:
        1. 管理PDF文档
        2. 配置中文字体
        3. 添加页面
        4. 保存PDF
    """
    
    def __init__(self, output_path: str, page_size: tuple = A4):
        """
        初始化PDF生成器
        
        参数:
            output_path: 输出PDF文件路径
            page_size: 页面大小（默认A4）
        """
        self.output_path = output_path
        self.page_size = page_size
        self.story = []  # 存储所有元素
        
        # 配置中文字体
        self._setup_chinese_fonts()
        
        # 创建文档
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
    
    def _setup_chinese_fonts(self) -> None:
        """
        配置中文字体
        
        支持的字体:
        - SimHei（黑体）：用于标题
        - SimSun（宋体）：用于正文
        
        注意:
            需要确保系统中有这些字体文件
            Windows系统通常有这些字体
        """
        # 字体路径（Windows系统）
        font_paths = {
            'SimHei': 'C:/Windows/Fonts/simhei.ttf',
            'SimSun': 'C:/Windows/Fonts/simsun.ttc',
        }
        
        # 尝试注册字体
        for font_name, font_path in font_paths.items():
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"成功注册字体: {font_name}")
                except Exception as e:
                    print(f"注册字体失败 {font_name}: {e}")
        
        # 如果注册失败，使用默认字体
        if 'SimHei' not in pdfmetrics.getRegisteredFontNames():
            print("警告: 无法注册中文字体，将使用默认字体")
    
    def add_element(self, element) -> None:
        """
        添加元素到PDF
        
        参数:
            element: reportlab元素（Table, Paragraph, Image等）
        """
        self.story.append(element)
    
    def add_spacer(self, height: float) -> None:
        """
        添加空白间距
        
        参数:
            height: 高度（单位：cm）
        """
        self.story.append(Spacer(1, height*cm))
    
    def add_page_break(self) -> None:
        """
        添加分页符
        """
        self.story.append(PageBreak())
    
    def save(self) -> str:
        """
        保存PDF文件
        
        返回:
            str: 保存的文件路径
        """
        self.doc.build(self.story)
        return self.output_path
```

##### 2. 页面生成函数
**文件**：`pdf/pages.py`

**函数**：`generate_page1_metrics()` 和 `generate_page2_positions()`

**实现框架**：
```python
from reportlab.platypus import Table, TableStyle, Paragraph, Image
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from typing import Dict, List, Any

def generate_page1_metrics(
    generator: 'PDFGenerator',
    metrics: Dict[str, Any],
    nav_data: List[Dict[str, Any]],
    chart_path: str
) -> None:
    """
    生成第一页：业绩统计
    
    参数:
        generator: PDFGenerator实例
        metrics: 指标字典（来自开发者B）
        nav_data: 净值数据列表
        chart_path: 净值走势图路径
    
    页面内容:
        1. 产品基本信息（标题）
        2. 业绩统计表格
        3. 净值走势图
    """
    styles = getSampleStyleSheet()
    
    # 1. 标题
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1  # 居中
    )
    title = Paragraph('产品业绩统计', title_style)
    generator.add_element(title)
    generator.add_spacer(0.5)
    
    # 2. 业绩统计表格
    table_data = [
        ['指标名称', '数值'],
        ['期间产品收益率', f"{metrics.get('period_return', 0):.2f}% (年化 {metrics.get('annualized_return', 0):.2f}%)"],
        ['最大回撤', f"{metrics.get('max_drawdown', 0):.2f}%"],
        ['波动率', f"{metrics.get('volatility', 0):.2f}%"],
        ['夏普比率', f"{metrics.get('sharpe_ratio', 0):.2f}"]
    ]
    
    table = Table(table_data, colWidths=[6*cm, 6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    generator.add_element(table)
    generator.add_spacer(1)
    
    # 3. 净值走势图
    if os.path.exists(chart_path):
        img = Image(chart_path, width=16*cm, height=8*cm)
        generator.add_element(img)
    
    generator.add_page_break()


def generate_page2_positions(
    generator: 'PDFGenerator',
    positions: Dict[str, Dict[str, Any]],
    drawdown_chart_path: str,
    position_chart_path: str
) -> None:
    """
    生成第二页：持仓明细
    
    参数:
        generator: PDFGenerator实例
        positions: 持仓字典（来自开发者A）
        drawdown_chart_path: 回撤图路径
        position_chart_path: 持仓分布图路径
    
    页面内容:
        1. 持仓明细表格
        2. 回撤图
        3. 持仓分布图
    """
    styles = getSampleStyleSheet()
    
    # 1. 标题
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1
    )
    title = Paragraph('持仓明细', title_style)
    generator.add_element(title)
    generator.add_spacer(0.5)
    
    # 2. 持仓明细表格
    table_data = [
        ['股票代码', '持仓数量', '持仓成本(万元)', '持仓市值(万元)', '持仓占比(%)']
    ]
    
    # 按市值排序
    sorted_positions = sorted(
        positions.items(),
        key=lambda x: x[1].get('market_value', 0),
        reverse=True
    )
    
    # 计算总市值
    total_value = sum([pos.get('market_value', 0) for pos in positions.values()])
    
    # 添加数据行
    for code, pos_data in sorted_positions[:20]:  # 只显示前20只
        market_value = pos_data.get('market_value', 0)
        percentage = (market_value / total_value * 100) if total_value > 0 else 0
        
        table_data.append([
            code,
            f"{pos_data.get('quantity', 0):.0f}",
            f"{pos_data.get('cost', 0):.2f}",
            f"{market_value:.2f}",
            f"{percentage:.2f}"
        ])
    
    table = Table(table_data, colWidths=[2*cm, 2.5*cm, 3*cm, 3*cm, 2.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
    ]))
    
    generator.add_element(table)
    generator.add_spacer(1)
    
    # 3. 回撤图
    if os.path.exists(drawdown_chart_path):
        img = Image(drawdown_chart_path, width=16*cm, height=8*cm)
        generator.add_element(img)
        generator.add_spacer(0.5)
    
    # 4. 持仓分布图
    if os.path.exists(position_chart_path):
        img = Image(position_chart_path, width=16*cm, height=8*cm)
        generator.add_element(img)
```

---

## Day 3 任务详解

### 任务C5：PDF页面完成 [3小时]

#### 目标
完成PDF页面的所有内容，优化布局

#### 详细要求

##### 1. 完善第一页内容
- 产品基本信息（产品名称、净值日期等，从config.py读取）
- 业绩统计表格（完整格式化）
- 净值走势图（调整大小和位置）

##### 2. 完善第二页内容
- 持仓明细表格（完整数据，处理分页）
- 回撤图（调整大小和位置）
- 持仓分布图（调整大小和位置）

##### 3. 优化页面布局
**布局优化点**：
- 调整元素间距
- 调整表格列宽
- 调整图表大小
- 确保内容不超出页面

**示例优化代码**：
```python
# 动态调整表格列宽
def calculate_table_widths(num_cols: int, total_width: float = 16*cm) -> List[float]:
    """
    计算表格列宽
    
    参数:
        num_cols: 列数
        total_width: 总宽度（cm）
    
    返回:
        List[float]: 每列宽度列表
    """
    col_width = total_width / num_cols
    return [col_width] * num_cols
```

##### 4. 处理表格分页
如果持仓明细表格过长，需要处理分页：
```python
from reportlab.platypus import KeepTogether

# 使用KeepTogether保持表格完整性（如果可能）
# 如果表格太长，reportlab会自动分页
table = Table(table_data, ...)
# reportlab会自动处理分页
```

---

### 任务C6：最终优化与测试 [2小时]

#### 目标
最终优化和集成测试

#### 详细要求

##### 1. PDF样式优化
- 统一字体大小
- 统一颜色方案
- 优化表格样式
- 优化图表大小

##### 2. 图表大小调整
根据PDF页面大小调整图表：
- 净值走势图：16cm × 8cm
- 回撤图：16cm × 8cm
- 持仓分布图：16cm × 8cm

##### 3. 最终测试
- 测试完整流程（从数据到PDF）
- 验证中文显示
- 验证图表插入
- 验证表格显示
- 验证PDF生成成功

##### 4. 与主程序集成测试
- 与main.py集成
- 测试命令行参数
- 测试错误处理

---

## 关键图表要求总结

### 1. 净值走势图（单位净值走势）
**参考模版**：模版模块实现.md 1.4节

**要求**：
- 折线图
- X轴：日期
- Y轴：单位净值
- 标题："单位净值走势"
- 蓝色实线，线宽2
- 网格线
- DPI=300

### 2. 回撤图（动态回撤）
**参考模版**：模版模块实现.md 2.1节

**要求**：
- 折线图 + 填充区域
- X轴：日期
- Y轴：回撤百分比（%）
- 标题："动态回撤"
- Y轴反转（回撤向下显示）
- 填充区域alpha=0.3
- DPI=300

### 3. 持仓分布图
**参考模版**：模版模块实现.md（行业分布思路）

**要求**：
- 横向柱状图或饼图
- 显示持仓占比（%）
- 标题："持仓分布"
- 显示前10大持仓
- DPI=300

---

## PDF生成要求总结

### 第一页：业绩统计
**内容**：
1. 产品基本信息（标题）
2. 业绩统计表格：
   - 期间产品收益率（年化）
   - 最大回撤
   - 波动率
   - 夏普比率
3. 净值走势图

### 第二页：持仓明细
**内容**：
1. 持仓明细表格：
   - 股票代码
   - 持仓数量
   - 持仓成本（万元）
   - 持仓市值（万元）
   - 持仓占比（%）
2. 回撤图
3. 持仓分布图

---

## 数据接口规范

### 输入接口

#### 1. 净值数据（来自开发者B）
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

#### 2. 回撤数据（来自开发者B）
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

#### 3. 持仓数据（来自开发者A）
```python
{
    'code': {
        'quantity': float,      # 持仓数量
        'cost': float,          # 持仓成本（万元）
        'market_value': float   # 持仓市值（万元）
    },
    ...
}
```

#### 4. 指标数据（来自开发者B）
```python
{
    'period_return': float,        # 期间收益率（%）
    'annualized_return': float,  # 年化收益率（%）
    'max_drawdown': float,       # 最大回撤（%）
    'volatility': float,         # 年化波动率（%）
    'sharpe_ratio': float        # 夏普比率
}
```

---

## AI辅助提示词

### 提示词1：图表基础配置和中文字体
```
我正在开发一个私募基金报告生成系统，需要配置matplotlib中文字体。

任务要求：
1. 创建 setup_chinese_font() 函数
2. 配置中文字体支持（SimHei, Microsoft YaHei等）
3. 解决负号显示问题

技术要求：
1. 支持Windows和Mac系统
2. 设置合理的默认字体大小
3. 所有函数必须有类型注解和docstring
4. 遵循PEP 8规范

请帮我实现这个函数。
```

### 提示词2：净值走势图
```
我正在开发一个私募基金报告生成系统，需要绘制净值走势图。

任务要求：
1. 在 charts/generator.py 中实现 plot_nav_trend() 函数
2. 绘制单位净值走势折线图

图表要求：
1. X轴：日期（YYYY-MM-DD格式）
2. Y轴：单位净值
3. 折线图，蓝色实线，线宽2
4. 标题："单位净值走势"，字体大小14，加粗
5. 网格线，透明度0.3
6. 日期标签旋转45度
7. 保存为PNG格式，DPI=300
8. 图片大小：12×6英寸

输入数据格式：
- nav_data: [{date: str, nav: float, total_assets: float}, ...]

技术要求：
1. 使用matplotlib
2. 配置中文字体
3. 所有函数必须有类型注解和docstring
4. 遵循PEP 8规范

请帮我实现这个函数。
```

### 提示词3：回撤图
```
我正在开发一个私募基金报告生成系统，需要绘制动态回撤图。

任务要求：
1. 在 charts/generator.py 中实现 plot_drawdown() 函数
2. 绘制动态回撤折线图（带填充区域）

图表要求：
1. X轴：日期
2. Y轴：回撤百分比（%）
3. 折线图，蓝色实线，线宽2
4. 填充区域（fill_between），alpha=0.3，蓝色
5. 标题："动态回撤"，字体大小14，加粗
6. Y轴反转（invert_yaxis），回撤向下显示
7. 网格线
8. 保存为PNG格式，DPI=300
9. 图片大小：12×6英寸

输入数据格式：
- drawdown_data: [{date: str, drawdown: float, peak_nav: float}, ...]

技术要求：
1. 使用matplotlib
2. 配置中文字体
3. 所有函数必须有类型注解和docstring
4. 遵循PEP 8规范

请帮我实现这个函数。
```

### 提示词4：持仓分布图
```
我正在开发一个私募基金报告生成系统，需要绘制持仓分布图。

任务要求：
1. 在 charts/generator.py 中实现 plot_position_distribution() 函数
2. 绘制持仓分布图（横向柱状图或饼图）

图表要求：
1. 显示持仓占比（持仓市值 / 总市值 × 100%）
2. 横向柱状图或饼图（可配置）
3. 标题："持仓分布"，字体大小14，加粗
4. 只显示前10大持仓（如果持仓数量多）
5. 添加数值标签（百分比）
6. 保存为PNG格式，DPI=300
7. 图片大小：10×6英寸

输入数据格式：
- positions: {code: {'quantity': float, 'market_value': float, ...}, ...}

技术要求：
1. 使用matplotlib
2. 配置中文字体
3. 处理空持仓情况
4. 所有函数必须有类型注解和docstring
5. 遵循PEP 8规范

请帮我实现这个函数。
```

### 提示词5：PDF生成主类
```
我正在开发一个私募基金报告生成系统，需要创建PDF生成主类。

任务要求：
1. 在 pdf/generator.py 中实现 PDFGenerator 类
2. 管理PDF文档生成

功能要求：
1. 初始化PDF文档（A4大小）
2. 配置中文字体（SimHei, SimSun）
3. 添加元素（Table, Paragraph, Image等）
4. 添加空白间距
5. 添加分页符
6. 保存PDF文件

技术要求：
1. 使用reportlab
2. 支持中文字体注册
3. 设置合理的页面边距（2cm）
4. 所有方法必须有类型注解和docstring
5. 遵循PEP 8规范

请帮我实现这个类。
```

### 提示词6：PDF页面生成函数
```
我正在开发一个私募基金报告生成系统，需要实现PDF页面生成函数。

任务要求：
1. 在 pdf/pages.py 中实现 generate_page1_metrics() 函数
2. 在 pdf/pages.py 中实现 generate_page2_positions() 函数

第一页要求：
1. 产品基本信息（标题）
2. 业绩统计表格（使用reportlab Table）
3. 插入净值走势图（使用reportlab Image）

第二页要求：
1. 持仓明细表格（使用reportlab Table）
2. 插入回撤图（使用reportlab Image）
3. 插入持仓分布图（使用reportlab Image）

表格样式要求：
1. 表头：灰色背景，白色文字
2. 数据行：米色背景
3. 边框：黑色，1pt
4. 字体：SimHei（表头），SimSun（数据）
5. 对齐：居中

输入数据格式：
- metrics: {'period_return': float, 'annualized_return': float, ...}
- nav_data: [{date, nav, total_assets}, ...]
- positions: {code: {...}, ...}
- chart_paths: str（图片路径）

技术要求：
1. 使用reportlab的Table和TableStyle
2. 使用reportlab的Image插入图片
3. 图片大小：16cm × 8cm
4. 所有函数必须有类型注解和docstring
5. 遵循PEP 8规范

请帮我实现这些函数。
```

---

## 测试检查清单

### 功能测试
- [ ] 图表生成成功（3个图表）
- [ ] 图表中文显示正常
- [ ] 图表保存成功（PNG格式，DPI=300）
- [ ] PDF生成成功
- [ ] PDF中文显示正常
- [ ] PDF表格显示正常
- [ ] PDF图表插入正常
- [ ] PDF页面布局合理

### 数据验证测试
- [ ] 图表数据格式匹配
- [ ] PDF数据格式匹配
- [ ] 空数据情况处理
- [ ] 数据点过少情况处理

### 边界情况测试
- [ ] 处理空持仓情况
- [ ] 处理单日数据情况
- [ ] 处理图表路径不存在的情况
- [ ] 处理中文字体缺失的情况

---

## 注意事项

### 1. 中文字体配置
- **Windows系统**：通常有SimHei和SimSun字体
- **Mac系统**：可能需要安装中文字体
- **字体路径**：Windows在 `C:/Windows/Fonts/`
- **字体注册**：使用reportlab的TTFont注册字体

### 2. 图表保存
- **格式**：PNG格式
- **DPI**：300（高质量）
- **bbox_inches**：'tight'（去除多余空白）
- **关闭图表**：使用 `plt.close()` 释放内存

### 3. PDF生成
- **页面大小**：A4（210mm × 297mm）
- **边距**：2cm（上下左右）
- **图片大小**：根据页面宽度调整（16cm × 8cm）
- **表格列宽**：根据列数动态计算

### 4. 布局优化
- **元素间距**：使用Spacer控制
- **表格列宽**：根据内容动态调整
- **图表大小**：确保不超出页面
- **分页处理**：reportlab自动处理分页

### 5. 性能优化
- **图表内存**：及时关闭图表释放内存
- **图片缓存**：避免重复生成相同图表
- **PDF构建**：使用story列表，最后统一构建

### 6. 错误处理
- **字体缺失**：提供降级方案（使用默认字体）
- **图片不存在**：检查文件是否存在再插入
- **数据为空**：显示提示信息

---

## 参考文档

- **模版模块实现.md**：
  - 第1.4节（单位净值表现）- 净值走势图要求
  - 第2.1节（动态回撤图）- 回撤图要求
  - 第3.6节（PDF生成模块）- PDF生成要求
- **项目分析.md**：第3.6节（PDF生成模块）
- **任务分配.md**：开发者C的任务清单

---

## 与开发者A和B的协作接口

### 接收数据
从开发者B接收：
```python
nav_data = calculate_nav(daily_positions, initial_capital)
metrics = calculate_all_metrics(nav_data)
drawdowns = calculate_daily_drawdowns(nav_data)
```

从开发者A接收：
```python
positions = calculate_positions(transactions, end_date)
```

### 输出数据
向主程序输出：
```python
chart1 = plot_nav_trend(nav_data, 'nav_trend.png')
chart2 = plot_drawdown(drawdowns, 'drawdown.png')
chart3 = plot_position_distribution(positions, 'positions.png')

pdf = PDFGenerator('report.pdf')
generate_page1_metrics(pdf, metrics, nav_data, chart1)
generate_page2_positions(pdf, positions, chart2, chart3)
pdf.save()
```

---

## 常见问题处理

### Q1: 中文字体显示乱码怎么办？
**A**: 
1. 检查系统是否安装了中文字体
2. 检查字体路径是否正确
3. 如果无法注册中文字体，使用默认字体（可能显示乱码，需要告知用户）

### Q2: 图表太大，超出PDF页面怎么办？
**A**: 调整图片大小参数，确保宽度不超过页面宽度（约16cm）

### Q3: 表格数据太多，分页显示不好看怎么办？
**A**: reportlab会自动处理分页，但可以：
1. 限制显示的行数（如只显示前20只股票）
2. 调整表格字体大小
3. 使用更紧凑的布局

### Q4: 图表保存失败怎么办？
**A**: 
1. 检查保存路径是否有效
2. 检查是否有写入权限
3. 检查磁盘空间是否充足

---

**文档版本**：v1.0  
**创建日期**：2024年  
**最后更新**：2024年

