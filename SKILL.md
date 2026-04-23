# OpenClaw Skill 配置文件

## Skill 基本信息

| 属性 | 值 |
|------|------|
| name | chanlun-stock-analysis |
| version | 1.0.0 |
| description | 基于缠论理论的股票分析Skill，提供分型识别、笔线段划分、中枢识别、买卖点判断、历史回测和走势预测功能 |
| author | chanlun-team |
| license | MIT |
| homepage | https://github.com/chanlun/chanlun-stock-analysis |
| keywords | 缠论, 股票分析, 量化交易, 技术分析, 买卖点识别 |

## Skill 元数据

### 入口配置
```yaml
entry:
  main: chanlun_stock_analysis.skill:create_skill
  module: chanlun_stock_analysis
  class: ChanLunSkill
```

### 依赖配置
```yaml
dependencies:
  python: ">=3.8"
  packages:
    - numpy>=1.20.0
    - pandas>=1.3.0
    - matplotlib>=3.4.0
    - tushare>=1.2.0
    - akshare>=1.8.0
```

### 权限配置
```yaml
permissions:
  - name: network
    description: 允许访问网络获取股票数据
  - name: filesystem
    description: 允许读写本地缓存和配置文件
    scope: 
      - ./data/
      - ./cache/
      - ./config/
```

## Skill 功能定义

### 命令列表

#### 1. 股票分析命令
```yaml
command:
  name: analyze
  description: 分析指定股票的缠论结构
  parameters:
    - name: stock_code
      type: string
      required: true
      description: 股票代码，如 '000001.SZ'
    - name: start_date
      type: string
      required: false
      description: 开始日期，格式 'YYYY-MM-DD'
    - name: end_date
      type: string
      required: false
      description: 结束日期，格式 'YYYY-MM-DD'
    - name: level
      type: string
      required: false
      default: 'day'
      description: 分析级别，可选 'day', 'hour', '30min', '5min'
  examples:
    - "分析平安银行最近的缠论结构"
    - "分析000001.SZ从2023-01-01到2023-12-31的日线走势"
```

#### 2. 回测命令
```yaml
command:
  name: backtest
  description: 对指定股票进行历史回测
  parameters:
    - name: stock_code
      type: string
      required: true
      description: 股票代码
    - name: start_date
      type: string
      required: true
      description: 回测开始日期
    - name: end_date
      type: string
      required: true
      description: 回测结束日期
    - name: initial_capital
      type: number
      required: false
      default: 100000
      description: 初始资金
    - name: strategy
      type: string
      required: false
      default: 'chanlun_basic'
      description: 交易策略名称
  examples:
    - "回测平安银行2023年的缠论策略"
    - "用10万初始资金回测000001.SZ从2022到2023的表现"
```

#### 3. 预测命令
```yaml
command:
  name: predict
  description: 基于缠论理论预测未来走势
  parameters:
    - name: stock_code
      type: string
      required: true
      description: 股票代码
    - name: horizon
      type: number
      required: false
      default: 5
      description: 预测时间范围（天）
  examples:
    - "预测平安银行未来一周走势"
    - "分析000001.SZ可能的走势分类"
```

#### 4. 买卖点查询命令
```yaml
command:
  name: signals
  description: 查询指定股票的买卖点信号
  parameters:
    - name: stock_code
      type: string
      required: true
      description: 股票代码
    - name: signal_type
      type: string
      required: false
      default: 'all'
      description: 信号类型，可选 'buy1', 'buy2', 'buy3', 'sell1', 'sell2', 'sell3', 'all'
  examples:
    - "查找平安银行最近的买点"
    - "显示000001.SZ的所有第三类买点"
```

## Skill 配置项

### 默认配置
```yaml
config:
  # 数据源配置
  data_source:
    provider: tushare
    cache_enabled: true
    cache_dir: ./cache
  
  # 分析配置
  analysis:
    # 包含处理严格程度
    strict_containment: true
    # 笔的确认条件
    pen_confirmation: true
    # 线段划分算法
    segment_algorithm: standard
  
  # 可视化配置
  visualization:
    theme: seaborn
    figure_size: [16, 9]
    dpi: 100
    show_fractals: true
    show_pens: true
    show_segments: true
    show_pivots: true
    show_signals: true
  
  # 回测配置
  backtest:
    commission_rate: 0.0003
    slippage: 0.0001
    position_size: 0.9
  
  # 日志配置
  logging:
    level: INFO
    file: ./logs/chanlun_skill.log
```

## Skill 文档

### 使用说明
本Skill基于缠论理论，提供以下核心功能：

1. **缠论结构识别**
   - 自动识别K线分型（顶分型、底分型）
   - 构建笔（相邻顶底分型之间的走势）
   - 划分线段（由笔组成的更高级别走势）
   - 识别中枢（价格重叠区间）

2. **买卖点识别**
   - 第一类买卖点：背驰点
   - 第二类买卖点：回拉确认点
   - 第三类买卖点：新中枢形成后的回拉点

3. **历史回测**
   - 基于缠论买卖点进行历史模拟交易
   - 计算收益率、胜率、最大回撤等指标
   - 生成详细的回测报告

4. **走势预测**
   - 判断当前走势类型（盘整/趋势）
   - 推演未来可能的走势分类
   - 评估预测可靠性

### 使用示例

#### 示例1：分析股票缠论结构
```
用户：分析平安银行最近的缠论结构
Skill：正在分析平安银行(000001.SZ)的日线走势...
       [显示K线图，标注分型、笔、线段、中枢]
       当前处于日线级别上涨趋势，中枢区间[10.5, 11.2]
       最近出现第三类买点，建议关注...
```

#### 示例2：历史回测
```
用户：回测平安银行2023年的缠论策略
Skill：开始回测平安银行2023年数据...
       回测完成！
       总收益率：23.5%
       胜率：65%
       最大回撤：8.2%
       交易次数：15次
       [显示资金曲线和交易明细]
```

#### 示例3：走势预测
```
用户：预测平安银行未来一周走势
Skill：基于当前缠论结构分析...
       当前走势：日线级别上涨趋势
       中枢位置：[10.5, 11.2]
       
       未来走势推演：
       1. 继续上涨（概率60%）：需突破11.5
       2. 回调盘整（概率30%）：关注10.8支撑
       3. 反转下跌（概率10%）：需跌破10.3
       
       关键观察点：11.5（压力）、10.8（支撑）
```

### 注意事项
1. 本Skill仅供研究和学习使用，不构成投资建议
2. 缠论分析需要一定的理论基础，建议先了解缠论基本概念
3. 数据来源于第三方，请关注数据质量和时效性
4. 预测结果仅供参考，市场有风险，投资需谨慎

## Skill 更新日志

### v1.0.0 (2026-04-21)
- 初始版本发布
- 实现缠论核心分析功能
- 实现买卖点识别
- 实现历史回测功能
- 实现走势预测功能
- 集成OpenClaw平台接口

---

**Skill配置文件结束**
