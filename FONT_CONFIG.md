# 字体配置说明

## 问题描述

在跨平台开发中（Mac 和 Windows），PDF 生成的图表左上角中文可能显示为黑色方块。这是因为不同操作系统使用不同的字体系统。

## 解决方案

项目已实现跨平台字体自动检测和配置：

### 1. 统一字体配置模块

所有图表文件导入统一的字体配置：

```python
from charts.font_config import setup_chinese_font
```

### 2. 字体优先级

**macOS:**
1. PingFang SC（苹方-简体，最佳）
2. PingFang HK（苹方-香港）
3. PingFang TC（苹方-繁体）
4. Heiti SC（黑体-简）
5. Heiti TC（黑体-繁）
6. STHeiti（华文黑体）
7. Songti SC（宋体-简）
8. STSong（华文宋体）
9. Arial Unicode MS

**Windows:**
1. Microsoft YaHei（微软雅黑，最佳）
2. SimHei（黑体）
3. SimSun（宋体）
4. KaiTi（楷体）

**Linux:**
1. WenQuanYi Micro Hei（文泉驿微米黑）
2. WenQuanYi Zen Hei（文泉驿正黑）
3. Droid Sans Fallback
4. Noto Sans CJK SC
5. Noto Sans CJK

### 3. 自动检测机制

`font_config.py` 会：
1. 检测当前操作系统
2. 获取系统所有可用字体
3. 按优先级选择第一个可用的中文字体
4. 如果未找到推荐字体，会搜索包含 "CJK" 或中文关键字的字体
5. 在生成 PDF 时打印使用的字体名称

## 测试字体配置

运行字体测试脚本：

```bash
python3 charts/font_config.py
```

这会：
- 显示系统可用的所有中文相关字体
- 显示将使用的字体
- 生成测试图片 `font_test.png`

## 验证 PDF 中的中文显示

生成 PDF 后检查：

1. **图表标题**: 例如 "产品净值表现"
2. **坐标轴标签**: 例如 "收益率(%)"、"日期"
3. **图例**: 例如 "成立以来"、"近一年"
4. **表格内容**: 例如 "期末持仓"、"股票"、"现金"

如果仍有方块出现：

1. 检查终端输出中 "✓ 使用字体" 的信息
2. 运行 `python3 charts/font_config.py` 查看可用字体
3. 如果系统缺少中文字体，需要安装

## 安装中文字体

### macOS

系统自带中文字体，通常无需额外安装。如果确实需要：

```bash
# 检查 PingFang 字体
ls /System/Library/Fonts/ | grep -i pingfang
ls /System/Library/Fonts/ | grep -i heiti
```

### Windows

1. 微软雅黑（Microsoft YaHei）- Windows Vista+ 自带
2. 黑体（SimHei）- Windows XP+ 自带
3. 如缺失，从控制面板 → 字体 安装

### Linux (Ubuntu/Debian)

```bash
# 安装文泉驿字体
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei

# 或安装 Google Noto 字体
sudo apt-get install fonts-noto-cjk
```

## matplotlib 和 ReportLab 字体

项目使用两个 PDF 库：

1. **matplotlib**: 用于生成图表（图像）
   - 配置：`charts/font_config.py`
   - 控制：图表中的所有中文文本
   
2. **ReportLab**: 用于组合 PDF 页面
   - 配置：`pdf/pages.py` 中的 `setup_chinese_fonts()`
   - 控制：PDF 直接文本（标题等）

两者都已配置跨平台字体支持。

## 故障排查

### 问题1: 仍显示方块

**原因**: 系统缺少合适的中文字体

**解决**:
1. 运行 `python3 charts/font_config.py` 查看可用字体
2. 安装推荐的中文字体（见上方）
3. 清除 matplotlib 字体缓存：
   ```bash
   rm -rf ~/.matplotlib/fontlist*.json
   ```

### 问题2: Mac 和 Windows 生成的 PDF 样式不同

**原因**: 使用了不同的字体（正常现象）

**说明**:
- Mac 使用 PingFang SC（苹方）- 更现代、细腻
- Windows 使用 Microsoft YaHei（微软雅黑）- 更粗、传统
- 这是预期行为，两者都能正常显示中文

### 问题3: 字体太细/太粗

**调整**: 在 `charts/font_config.py` 中修改 `plt.rcParams` 配置：

```python
plt.rcParams['font.size'] = 12          # 调整基础字体大小
plt.rcParams['axes.titlesize'] = 16     # 调整标题大小
plt.rcParams['font.weight'] = 'normal'  # 'light', 'normal', 'bold'
```

## 技术细节

### 字体检测流程

```python
# 1. 检测操作系统
system = platform.system()  # 'Darwin', 'Windows', 'Linux'

# 2. 获取所有系统字体
from matplotlib.font_manager import FontManager
font_manager = FontManager()
available_fonts = [font.name for font in font_manager.ttflist]

# 3. 按优先级匹配
for font in font_candidates:
    if font in available_fonts:
        selected_font = font
        break

# 4. 应用到 matplotlib
plt.rcParams['font.sans-serif'] = [selected_font, 'DejaVu Sans']
```

### 字体文件路径

**macOS:**
- 系统字体: `/System/Library/Fonts/`
- 用户字体: `~/Library/Fonts/`
- PingFang: `/System/Library/Fonts/PingFang.ttc`
- STHeiti: `/System/Library/Fonts/STHeiti Light.ttc`

**Windows:**
- 系统字体: `C:\Windows\Fonts\`
- Microsoft YaHei: `C:\Windows\Fonts\msyh.ttc`
- SimHei: `C:\Windows\Fonts\simhei.ttf`

**Linux:**
- 系统字体: `/usr/share/fonts/`
- WenQuanYi: `/usr/share/fonts/truetype/wqy/`
- Noto: `/usr/share/fonts/opentype/noto/`

## 更新记录

- **2025-11-09**: 实现跨平台字体自动检测
  - 创建统一的 `font_config.py` 模块
  - 更新所有 21 个图表文件
  - 更新 `pdf/pages.py` 的 ReportLab 配置
  - 修复 PDF 标题文本使用正确的中文字体
  - 添加字体测试工具
  - 支持 macOS、Windows、Linux

## 参考资源

- [Matplotlib 字体配置](https://matplotlib.org/stable/tutorials/text/text_props.html)
- [ReportLab 中文支持](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [macOS 字体手册](https://support.apple.com/en-us/HT201749)
- [文泉驿项目](http://wenq.org/)
- [Google Noto Fonts](https://www.google.com/get/noto/)
