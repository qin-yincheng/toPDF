# 表格字体大小影响因素分析

## 已发现的影响因素

### 1. **全局字体大小设置** ⚠️
**位置**: `charts/font_config.py` 第88行
```python
plt.rcParams['font.size'] = 14
```
**影响**: 如果单元格的字体大小没有被明确设置，可能会使用这个全局默认值（14px）

**解决方案**: 
- ✅ 已通过 `apply_table_font()` 函数为每个单元格明确设置字体大小
- ✅ 所有表格函数都使用 `table_fontsize=16` 参数

### 2. **`set_text_props()` 调用覆盖字体大小** ⚠️⚠️
**问题**: 在调用 `apply_table_font()` 之后，如果又调用了 `cell.set_text_props()` 但没有指定 `fontsize` 参数，可能会覆盖之前设置的字体大小。

**影响位置**:
- `charts/1_2.py` - 第251, 260, 262行
- `charts/4_1.py` - 第498, 501行
- `charts/4_2.py` - 第116, 125, 127, 360, 369, 371行
- `charts/5_1.py` - 第111, 120, 122, 344, 353, 355行
- `charts/5_2.py` - 第105, 111, 113行
- `charts/6_4.py` - 第109, 119, 121行
- `charts/6_5.py` - 第100, 107, 109行
- `charts/2_3.py` - 第172, 177, 179行
- `charts/3_4.py` - 第107, 117行
- `charts/2_1.py` - 第228, 238, 240行
- `charts/1_1.py` - 第158, 161, 189, 192, 220, 225, 227行
- `charts/1_6.py` - 第241, 254行

**解决方案**: 
- ✅ 已添加 `reapply_table_font_after_styling()` 函数
- ⚠️ 需要在所有 `set_text_props()` 调用之后再次调用字体设置函数

### 3. **表格缩放 (`table.scale()`)** ✅
**影响**: `table.scale()` 只影响表格的行高和列宽，**不会影响字体大小**

**已使用的位置**:
- 大部分表格都使用了 `table.scale(1, 1.5)` 或类似值来调整行高
- 这是正常的，不影响字体大小

### 4. **图表大小 (`figsize`)** ✅
**影响**: 图表大小会影响字体在视觉上的显示效果，但不会改变实际的字体大小（点数）

**已使用的位置**:
- 所有表格函数都有 `figsize` 参数
- 在 `pdf/pages.py` 中调用时，会根据页面布局动态计算 `figsize`

### 5. **DPI 设置** ✅
**影响**: DPI 只影响输出图片的分辨率，不会改变字体大小

**已使用的位置**:
- 所有保存操作都使用 `dpi=300` 或 `dpi=200`
- 这是正常的，不影响字体大小

## 推荐修复方案

### 方案1: 在所有 `set_text_props()` 之后重新应用字体大小
在设置表格样式之后，调用 `reapply_table_font_after_styling()` 函数：

```python
apply_table_font(table, fontsize=table_fontsize)
# ... 设置表格样式 ...
for cell in cells:
    cell.set_text_props(weight='bold', ha='center')
# 重新应用字体大小，确保不被覆盖
reapply_table_font_after_styling(table, fontsize=table_fontsize)
```

### 方案2: 在 `set_text_props()` 中明确指定 `fontsize`
在所有 `set_text_props()` 调用中都明确指定 `fontsize` 参数：

```python
cell.set_text_props(weight='bold', ha='center', fontsize=table_fontsize)
```

### 方案3: 修改 `apply_table_font()` 调用顺序
将 `apply_table_font()` 的调用放在所有样式设置之后：

```python
# 先设置样式
for cell in cells:
    cell.set_text_props(weight='bold', ha='center')
# 最后应用字体大小
apply_table_font(table, fontsize=table_fontsize)
```

## 当前状态

✅ **已修复**:
- 所有表格函数都使用 `table_fontsize=16` 参数
- 所有表格都使用 `apply_table_font()` 函数
- `charts/1_4.py` 中的硬编码字体大小已修复

⚠️ **需要检查**:
- 在 `apply_table_font()` 之后调用 `set_text_props()` 的地方，可能会覆盖字体大小
- 建议在所有样式设置之后再次调用字体设置函数

## 测试建议

1. 生成PDF后，检查所有表格的字体大小是否统一为16px
2. 如果发现某些表格字体仍然较小，检查是否在 `apply_table_font()` 之后又调用了 `set_text_props()`
3. 使用PDF阅读器的测量工具验证字体大小

