# 缠论股票分析 Skill 使用指南

## 快速开始

### 1. 安装

```bash
cd chanlun-stock-analysis
pip install -r requirements.txt
pip install -e .
```

### 2. 配置

编辑 `skill/config.yaml` 文件，配置数据源：

```yaml
data_source:
  default: akshare  # 或 tushare
  tushare:
    token: "your_tushare_token"  # 如果使用tushare
```

### 3. 使用示例

#### 位置分析

```python
import asyncio
from skill.main import ChanLunStockAnalysisSkill

async def main():
    skill = ChanLunStockAnalysisSkill()
    
    # 分析股票位置
    result = await skill.execute({
        'command': '分析 000001 缠论位置'
    })
    
    print(result.message)
    print(result.data['text'])

asyncio.run(main())
```

#### 历史回测

```python
import asyncio
from skill.main import ChanLunStockAnalysisSkill

async def main():
    skill = ChanLunStockAnalysisSkill()
    
    # 回测股票
    result = await skill.execute({
        'command': '回测 000001 2023-01-01 2023-12-31'
    })
    
    print(result.message)
    print(result.data['text'])

asyncio.run(main())
```

#### 走势预测

```python
import asyncio
from skill.main import ChanLunStockAnalysisSkill

async def main():
    skill = ChanLunStockAnalysisSkill()
    
    # 预测走势
    result = await skill.execute({
        'command': '预测 000001 走势'
    })
    
    print(result.message)
    print(result.data['text'])

asyncio.run(main())
```

## 命令格式

### 位置分析
```
分析 [股票代码] 缠论位置
```
- 股票代码：6位数字
- 示例：`分析 000001 缠论位置`

### 历史回测
```
回测 [股票代码] [开始日期] [结束日期]
```
- 股票代码：6位数字
- 日期格式：YYYY-MM-DD、YYYY/MM/DD、YYYYMMDD
- 示例：`回测 000001 2023-01-01 2023-12-31`

### 走势预测
```
预测 [股票代码] 走势
```
- 股票代码：6位数字
- 示例：`预测 000001 走势`

## 缠论概念说明

### 分型
- **顶分型**：相邻三根K线中，中间K线的高点和低点都是最高的
- **底分型**：相邻三根K线中，中间K线的高点和低点都是最低的

### 笔
连接相邻顶底分型的线段，是缠论分析的基本单位。

### 线段
由至少3笔组成，代表更高级别的走势。

### 中枢
由至少3段连续的线段重叠区域构成，是缠论的核心概念。

### 买卖点
- **第一类买点**：走势离开中枢后出现背驰，形成买点
- **第二类买点**：回拉不破中枢形成的买点
- **第三类买点**：新中枢形成后的回拉买点
- **卖点**：与买点对称

## 配置说明

### 数据源配置
```yaml
data_source:
  default: akshare  # 或 tushare
  tushare:
    token: "your_token"
```

### 分析参数配置
```yaml
analysis:
  fractal:
    confirm_bars: 3  # 分型确认K线数
  pen:
    min_length: 0.0  # 笔的最小长度
    allow_contain: true  # 是否允许包含关系
  segment:
    min_pens: 3  # 线段的最小笔数
  pivot:
    min_segments: 3  # 中枢的最小线段数
    levels: ["5", "30", "D"]  # 中枢级别
```

### 回测参数配置
```yaml
backtest:
  initial_capital: 100000  # 初始资金
  commission_rate: 0.0003  # 手续费率
  slippage: 0.0  # 滑点
  max_position_ratio: 0.95  # 最大持仓比例
```

### 可视化配置
```yaml
visualization:
  figure_size: [16, 9]  # 图表大小
  dpi: 100  # DPI
  show_grid: true  # 是否显示网格
  kline_colors:
    up: "red"  # 上涨K线颜色
    down: "green"  # 下跌K线颜色
  pivot_color: "blue"  # 中枢颜色
  buy_point_color: "red"  # 买点颜色
  sell_point_color: "green"  # 卖点颜色
```

## 注意事项

1. **数据源**：推荐使用akshare（免费），tushare需要申请token
2. **市场判断**：系统会自动判断股票市场（SH/SZ）
3. **日期范围**：回测时确保日期范围合理，不要超过当前日期
4. **风险提示**：缠论分析仅供参考，不构成投资建议

## 常见问题

### Q: 如何获取tushare token？
A: 访问 https://tushare.pro/ 注册账号后获取

### Q: 为什么获取数据失败？
A: 检查网络连接和数据源配置，尝试切换数据源

### Q: 如何调整分析参数？
A: 修改config.yaml文件中的analysis部分

### Q: 支持哪些K线周期？
A: 支持日线（D）、周线（W）、月线（M）、分钟线（5/15/30/60）
