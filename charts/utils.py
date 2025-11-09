"""
图表工具函数模块
提供自动计算坐标轴范围的工具函数
"""

from typing import List, Tuple, Union, Optional
from datetime import datetime, timedelta
import numpy as np


def calculate_ylim(
    data_series: List[List[float]],
    start_from_zero: bool = True,
    padding_ratio: float = 0.1,
    allow_negative: bool = False,
    round_to_nice_number: bool = True
) -> Tuple[float, float]:
    """
    基于数据特性自动计算合理的Y轴范围
    
    参数:
        data_series: 数据序列列表，可以是多个序列（用于多系列数据）
                    例如: [[1, 2, 3], [4, 5, 6]] 或 [[1, 2, 3]]
        start_from_zero: 是否从0开始（对于资产规模、份额等通常为True）
        padding_ratio: 边距比例（默认10%，即上下各留10%的空间）
        allow_negative: 是否允许负数范围
        round_to_nice_number: 是否将范围调整为"整齐"的数字（如1000的倍数）
    
    返回:
        tuple: (y_min, y_max) 合理的Y轴范围
    """
    # 合并所有数据序列
    all_values = []
    for series in data_series:
        if series:
            # 过滤掉 None 和 NaN
            valid_values = [v for v in series if v is not None and not np.isnan(v)]
            all_values.extend(valid_values)
    
    # 如果没有有效数据，返回默认范围
    if not all_values:
        if start_from_zero:
            return (0.0, 100.0)
        else:
            return (-10.0, 10.0)
    
    # 计算最小值和最大值
    min_val = min(all_values)
    max_val = max(all_values)
    
    # 如果所有值都相同，添加一些范围
    if min_val == max_val:
        if min_val == 0:
            if start_from_zero:
                y_min = 0.0
                y_max = 100.0
            else:
                y_min = -10.0
                y_max = 10.0
        else:
            center = min_val
            if start_from_zero:
                y_min = max(0, center * 0.9)
            else:
                # 如果允许负数或中心值为负，从负值开始
                if allow_negative or center < 0:
                    y_min = center * 0.9
                else:
                    y_min = max(0, center * 0.9)
            y_max = center * 1.1
    else:
        # 计算数据范围
        data_range = max_val - min_val
        
        # 如果数据范围非常小（接近0），使用绝对值来设置边距
        if data_range < abs(max_val) * 0.01:  # 范围小于最大值的1%
            padding = abs(max_val) * padding_ratio if max_val != 0 else abs(min_val) * padding_ratio if min_val != 0 else 1.0
        else:
            padding = data_range * padding_ratio
        
        # 计算初始范围
        if start_from_zero:
            # 从0开始
            if min_val >= 0:
                y_min = 0.0
                y_max = max_val + padding
            else:
                # 数据有负数，但从0开始
                y_min = 0.0
                y_max = max_val + padding
        else:
            # 不从0开始，根据数据范围计算
            y_min = min_val - padding
            y_max = max_val + padding
            
            # 如果允许负数且数据有负数，确保包含足够的负数范围
            if allow_negative and min_val < 0:
                y_min = min(y_min, min_val - padding)
            # 如果允许负数但数据都是正数，仍然可以从负值开始（为了更好的视觉效果）
            elif allow_negative and min_val >= 0:
                # 确保从负值开始，至少留出 padding 的负值空间
                # 如果最小值很小，使用完整的 padding
                if min_val < padding * 2:
                    y_min = min_val - padding
                else:
                    # 最小值较大时，仍然可以从负值开始
                    # 使用至少 padding 的负值空间，确保取整后仍然是负值
                    y_min = min_val - max(padding, data_range * 0.05)
    
    # 将范围调整为"整齐"的数字
    if round_to_nice_number:
        # 计算数量级
        if y_max > 0:
            magnitude_max = 10 ** np.floor(np.log10(abs(y_max)))
        else:
            magnitude_max = 1.0
        
        if abs(y_min) > 0:
            magnitude_min = 10 ** np.floor(np.log10(abs(y_min)))
        else:
            magnitude_min = magnitude_max
        
        # 使用较大的数量级
        magnitude = max(magnitude_max, magnitude_min) if magnitude_min > 0 else magnitude_max
        
        # 根据数量级选择步长
        if magnitude >= 10000:
            step = 10000  # 万级别
        elif magnitude >= 1000:
            step = 1000  # 千级别
        elif magnitude >= 100:
            step = 100  # 百级别
        elif magnitude >= 10:
            step = 10  # 十级别
        elif magnitude >= 1:
            step = 1  # 个位级别
        elif magnitude >= 0.1:
            step = 0.1  # 十分位
        elif magnitude >= 0.01:
            step = 0.01  # 百分位
        else:
            step = 0.001  # 千分位
        
        # 向上取整到步长的倍数
        if start_from_zero and y_min == 0:
            y_min = 0.0
        else:
            y_min = np.floor(y_min / step) * step
        
        y_max = np.ceil(y_max / step) * step
        
        # 确保最小值不会因为取整而小于0（如果要求从0开始）
        # 但如果允许负数，即使从0开始，如果数据有负数，也应该允许负值
        if start_from_zero and y_min < 0:
            # 检查原始数据是否有负数
            if min_val >= 0:
                # 数据都是正数，强制从0开始
                y_min = 0.0
            # 如果数据有负数，允许负值（因为用户可能希望显示负数部分）
        
        # 如果允许负数且不从0开始，确保取整后仍然从负值开始
        if not start_from_zero and allow_negative:
            # 如果取整后变成了0或正数，但应该从负值开始
            if y_min >= 0:
                # 计算应该使用的负值范围
                if min_val == max_val:
                    # 所有值相同的情况
                    if min_val >= 0:
                        # 数据都是正数，从负值开始（一个步长）
                        y_min = -step
                    else:
                        # 数据是负数，确保从负值开始
                        y_min = np.floor((min_val * 0.9) / step) * step
                else:
                    # 数据有范围
                    if min_val >= 0:
                        # 数据都是正数，但允许负数，从负值开始（一个步长）
                        # 如果最小值大于等于一个步长，可以从负值开始
                        if min_val >= step:
                            y_min = -step
                        elif min_val > 0:
                            # 最小值小于一个步长，但仍然可以从负值开始
                            y_min = -step
                        else:
                            y_min = 0.0
                    else:
                        # 数据有负数，确保包含足够的负数范围
                        # y_min 应该已经是负数了，这里只是确保
                        pass
    
    return (float(y_min), float(y_max))


def calculate_xlim(
    x_data: Union[List[datetime], List[float], List[int]],
    padding_ratio: float = 0.02,
    is_date: Optional[bool] = None
) -> Tuple[Union[datetime, float], Union[datetime, float]]:
    """
    基于数据特性自动计算合理的X轴范围
    
    参数:
        x_data: X轴数据，可以是日期列表或数值列表
        padding_ratio: 边距比例（默认2%，即左右各留2%的空间）
        is_date: 是否强制指定为日期类型（None时自动判断）
    
    返回:
        tuple: (x_min, x_max) 合理的X轴范围
    """
    if not x_data:
        # 如果没有数据，返回默认范围
        if is_date is True or (is_date is None and isinstance(x_data, list) and len(x_data) > 0 and isinstance(x_data[0], datetime)):
            default_date = datetime.now()
            return (default_date - timedelta(days=30), default_date)
        else:
            return (0.0, 100.0)
    
    # 自动判断是否为日期类型
    if is_date is None:
        is_date = isinstance(x_data[0], datetime) if x_data else False
    
    if is_date:
        # 日期类型处理
        valid_dates = [d for d in x_data if d is not None]
        if not valid_dates:
            default_date = datetime.now()
            return (default_date - timedelta(days=30), default_date)
        
        min_date = min(valid_dates)
        max_date = max(valid_dates)
        
        # 计算日期范围（天数）
        date_range = (max_date - min_date).days
        
        # 计算边距（天数）
        if date_range == 0:
            padding_days = 1  # 如果所有日期相同，至少留1天边距
        else:
            padding_days = max(1, int(date_range * padding_ratio))
        
        x_min = min_date - timedelta(days=padding_days)
        x_max = max_date + timedelta(days=padding_days)
        
        return (x_min, x_max)
    else:
        # 数值类型处理
        valid_values = [v for v in x_data if v is not None and not np.isnan(v)]
        if not valid_values:
            return (0.0, 100.0)
        
        min_val = min(valid_values)
        max_val = max(valid_values)
        
        # 如果所有值都相同，添加一些范围
        if min_val == max_val:
            if min_val == 0:
                x_min = -1.0
                x_max = 1.0
            else:
                center = min_val
                x_min = center - abs(center) * 0.1
                x_max = center + abs(center) * 0.1
        else:
            # 计算数据范围
            data_range = max_val - min_val
            
            # 如果数据范围非常小（接近0），使用绝对值来设置边距
            if data_range < abs(max_val) * 0.01:  # 范围小于最大值的1%
                padding = abs(max_val) * padding_ratio if max_val != 0 else abs(min_val) * padding_ratio if min_val != 0 else 1.0
            else:
                padding = data_range * padding_ratio
            
            x_min = min_val - padding
            x_max = max_val + padding
        
        # 对于索引类型的数据（整数），确保边界也是整数
        if all(isinstance(v, int) for v in valid_values):
            x_min = int(np.floor(x_min))
            x_max = int(np.ceil(x_max))
        
        return (float(x_min), float(x_max))


def calculate_date_tick_params(
    dates: List[datetime],
    target_ticks: int = 10
) -> Tuple[List[int], List[str]]:
    """
    计算日期X轴的刻度位置和标签
    
    参数:
        dates: 日期列表
        target_ticks: 目标刻度数量（默认10个）
    
    返回:
        tuple: (tick_indices, tick_labels) 刻度索引和标签列表
    """
    if not dates:
        return ([], [])
    
    n_points = len(dates)
    
    # 计算日期范围（天数）
    start_date = dates[0]
    end_date = dates[-1]
    date_range_days = (end_date - start_date).days
    
    # 根据日期范围决定目标刻度数量
    if date_range_days <= 30:  # 1个月内
        target_ticks = min(8, max(6, n_points // 4))  # 约每4个交易日一个刻度，最少6个
    elif date_range_days <= 90:  # 3个月内
        target_ticks = min(10, max(8, n_points // 9))  # 约每9个交易日一个刻度
    elif date_range_days <= 180:  # 6个月内
        target_ticks = min(12, max(8, n_points // 15))  # 约每15个交易日一个刻度
    elif date_range_days <= 365:  # 1年内
        target_ticks = min(12, max(8, n_points // 30))  # 约每30个交易日一个刻度
    elif date_range_days <= 730:  # 2年内
        target_ticks = min(15, max(10, n_points // 50))  # 约每50个交易日一个刻度
    else:  # 超过2年
        target_ticks = min(15, max(10, n_points // 60))  # 约每60个交易日一个刻度
    
    # 确保目标刻度数量在合理范围内（6-20个）
    target_ticks = max(6, min(20, target_ticks))
    
    # 计算刻度间隔
    tick_interval = max(1, n_points // target_ticks)
    
    # 生成刻度索引
    tick_indices = list(range(0, n_points, tick_interval))
    
    # 确保最后一个日期显示
    if tick_indices[-1] != n_points - 1:
        tick_indices.append(n_points - 1)
    
    # 生成刻度标签
    tick_labels = [dates[i].strftime('%Y-%m-%d') for i in tick_indices]
    
    return (tick_indices, tick_labels)

