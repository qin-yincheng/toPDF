"""
创建包装后的图表生成函数，自动从 page1_data 提取数据
"""

import importlib.util
import os

# 获取charts目录
charts_dir = os.path.join(os.path.dirname(__file__), 'charts')

# 动态导入所有图表模块
def load_chart_module(name):
    spec = importlib.util.spec_from_file_location(f"chart_{name}", os.path.join(charts_dir, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# 加载图表模块
chart1_3 = load_chart_module("1_3")
chart1_4 = load_chart_module("1_4")
chart2_1 = load_chart_module("2_1")

# 包装函数 - 自动提取数据
def plot_nav_performance_wrapped(data=None, **kwargs):
    """包装 plot_nav_performance，从 page1_data 提取 nav_series"""
    if data and isinstance(data, dict):
        nav_data = data.get('nav_performance', {}).get('nav_series', None)
    else:
        nav_data = data
    return chart1_3.plot_nav_performance(data=nav_data, **kwargs)

def plot_daily_return_chart_wrapped(data=None, **kwargs):
    """包装 plot_daily_return_chart，从 page1_data 提取 daily_returns"""
    if data and isinstance(data, dict):
        daily_data = data.get('nav_performance', {}).get('daily_returns', None)
    else:
        daily_data = data
    return chart1_4.plot_daily_return_chart(data=daily_data, **kwargs)

def plot_daily_return_table_wrapped(data=None, **kwargs):
    """包装 plot_daily_return_table，从 page1_data 提取 daily_returns"""
    if data and isinstance(data, dict):
        daily_data = data.get('nav_performance', {}).get('daily_returns', None)
    else:
        daily_data = data
    return chart1_4.plot_daily_return_table(data=daily_data, **kwargs)

def plot_dynamic_drawdown_chart_wrapped(data=None, **kwargs):
    """包装 plot_dynamic_drawdown_chart，从 page1_data 提取 drawdown 数据"""
    if data and isinstance(data, dict):
        drawdown_data = data.get('drawdown', {}).get('drawdown_series', None)
    else:
        drawdown_data = data
    return chart2_1.plot_dynamic_drawdown_chart(data=drawdown_data, **kwargs)

def plot_dynamic_drawdown_table_wrapped(data=None, **kwargs):
    """包装 plot_dynamic_drawdown_table，从 page1_data 提取 drawdown 数据"""
    if data and isinstance(data, dict):
        drawdown_data = data.get('drawdown', {}).get('drawdown_series', None)
    else:
        drawdown_data = data
    return chart2_1.plot_dynamic_drawdown_table(data=drawdown_data, **kwargs)


if __name__ == '__main__':
    # 测试
    from calc.data_provider import get_daily_positions
    from calc.report_bridge import build_page1_data, build_nav_performance_data
    
    # 获取数据
    daily_positions = get_daily_positions(include_positions=False)
    
    # 转换为nav_data
    initial_assets = float(daily_positions[0]['total_assets'])
    nav_data = []
    for pos in daily_positions:
        total_assets = float(pos['total_assets'])
        nav_data.append({
            'date': pos['date'],
            'nav': total_assets / initial_assets,
            'total_assets': total_assets,
        })
    
    # 构建 nav_performance 数据
    nav_perf_data = build_nav_performance_data(nav_data)
    page1_data = {'nav_performance': nav_perf_data}
    
    # 测试包装函数
    print("测试包装函数...")
    fig = plot_nav_performance_wrapped(data=page1_data, return_figure=True, show_title=False)
    print("✓ plot_nav_performance_wrapped 成功")
    
    fig2 = plot_daily_return_chart_wrapped(data=page1_data, return_figure=True, show_title=False)
    print("✓ plot_daily_return_chart_wrapped 成功")
