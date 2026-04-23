# 缠论股票分析 Skill 技术设计文档

## 1. 文档信息

| 项目 | 内容 |
|------|------|
| 功能名称 | chanlun-stock-analysis |
| 版本 | v1.0.0 |
| 创建日期 | 2026-04-21 |
| 文档状态 | 待审核 |
| 对应需求文档 | spec.md v1.0.0 |

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw Platform                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   ChanLunStockAnalysisSkill                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Skill Interface Layer                    │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Command   │  │   Result   │  │   Config   │     │   │
│  │  │  Parser    │  │  Formatter │  │  Manager   │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Business Logic Layer                     │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  Position  │  │  Backtest  │  │  Forecast  │     │   │
│  │  │  Analyzer  │  │  Engine    │  │  Engine    │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Core Integration Layer                   │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │  ChanLun   │  │  BuySell   │  │   Visual   │     │   │
│  │  │  Analyzer  │  │  Detector  │  │  Renderer  │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Existing ChanLun System                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Fractal  │  │   Pen    │  │ Segment  │  │  Pivot   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │Analyzer  │  │ Selector │  │Backtester│                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data & Infrastructure                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ DataSrc  │  │  Cache   │  │  Logger  │                 │
│  │(Tushare) │  │  Manager │  │  System  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 层次 | 模块 | 职责 |
|------|------|------|
| 接口层 | CommandParser | 解析用户自然语言命令，提取股票代码、分析类型等参数 |
| 接口层 | ResultFormatter | 格式化分析结果，生成文本、图表等输出 |
| 接口层 | ConfigManager | 管理skill配置，包括数据源、分析参数等 |
| 业务层 | PositionAnalyzer | 分析股票在缠论中的位置（中枢、买卖点等） |
| 业务层 | BacktestEngine | 执行历史回测，生成回测报告 |
| 业务层 | ForecastEngine | 基于缠论理论预测未来走势 |
| 核心层 | ChanLunAnalyzer | 封装现有缠论分析器，提供统一接口 |
| 核心层 | BuySellDetector | 识别第一、二、三类买卖点 |
| 核心层 | VisualRenderer | 可视化缠论元素（K线、中枢、买卖点等） |

## 3. 技术选型

### 3.1 核心技术栈

| 技术领域 | 技术选型 | 版本要求 | 选型理由 |
|---------|---------|---------|---------|
| 编程语言 | Python | >=3.8 | 兼容现有系统，丰富的量化库生态 |
| OpenClaw SDK | openclaw-sdk | >=1.0.0 | OpenClaw官方skill开发SDK |
| 数据处理 | pandas | >=1.3.0 | 复用现有依赖，强大的数据处理能力 |
| 数值计算 | numpy | >=1.21.0 | 复用现有依赖，高性能数值计算 |
| 可视化 | matplotlib | >=3.4.0 | 复用现有依赖，灵活的绑图能力 |
| 数据源 | tushare/akshare | >=1.2.0 | 复用现有依赖，A股数据获取 |
| 缓存 | redis | >=3.5.0 | 可选，用于缓存分析结果 |
| 日志 | loguru | >=0.6.0 | 简洁强大的日志库 |
| 配置管理 | pydantic | >=1.8.0 | 数据验证和配置管理 |
| 异步支持 | asyncio | 内置 | 提升并发性能 |

### 3.2 OpenClaw Skill规范

遵循OpenClaw skill开发规范，需要实现以下接口：

```python
from openclaw_sdk import Skill, SkillMetadata, SkillContext, SkillResponse

class ChanLunStockAnalysisSkill(Skill):
    """缠论股票分析Skill"""

    @classmethod
    def metadata(cls) -> SkillMetadata:
        """返回skill元数据"""
        pass

    async def execute(self, context: SkillContext) -> SkillResponse:
        """执行skill主逻辑"""
        pass

    async def validate(self, context: SkillContext) -> bool:
        """验证输入参数"""
        pass
```

## 4. 数据模型设计

### 4.1 核心数据结构

```python
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

# ===== 输入模型 =====

class StockCode(BaseModel):
    """股票代码"""
    code: str = Field(..., description="股票代码，如'000001'")
    market: Literal['SH', 'SZ'] = Field(..., description="市场：上海/深圳")

class AnalysisRequest(BaseModel):
    """分析请求"""
    stock: StockCode
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    analysis_type: Literal['position', 'backtest', 'forecast'] = 'position'

class BacktestConfig(BaseModel):
    """回测配置"""
    stock: StockCode
    start_date: datetime
    end_date: datetime
    initial_capital: float = Field(100000, gt=0)
    commission_rate: float = Field(0.0003, ge=0)
    slippage: float = Field(0.0, ge=0)

# ===== 输出模型 =====

class FractalInfo(BaseModel):
    """分型信息"""
    type: Literal['top', 'bottom']
    position: int
    price: float
    datetime: datetime

class PenInfo(BaseModel):
    """笔信息"""
    start: FractalInfo
    end: FractalInfo
    direction: Literal['up', 'down']
    length: float

class PivotInfo(BaseModel):
    """中枢信息"""
    level: int
    high: float
    low: float
    start_index: int
    end_index: int
    segments_count: int

class BuySellPoint(BaseModel):
    """买卖点"""
    type: Literal['buy1', 'buy2', 'buy3', 'sell1', 'sell2', 'sell3']
    position: int
    price: float
    datetime: datetime
    confidence: float = Field(..., ge=0, le=1)
    description: str

class PositionAnalysisResult(BaseModel):
    """位置分析结果"""
    stock: StockCode
    current_position: str  # 当前位置描述
    fractals: List[FractalInfo]
    pens: List[PenInfo]
    pivots: List[PivotInfo]
    buy_sell_points: List[BuySellPoint]
    trend_type: Literal['trend_up', 'trend_down', 'consolidation']
    risk_level: Literal['low', 'medium', 'high']

class BacktestTrade(BaseModel):
    """回测交易记录"""
    datetime: datetime
    type: Literal['buy', 'sell']
    price: float
    shares: int
    amount: float
    reason: str  # 交易原因（买卖点类型）

class BacktestResult(BaseModel):
    """回测结果"""
    config: BacktestConfig
    trades: List[BacktestTrade]
    total_return: float
    annual_return: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float
    final_capital: float

class ForecastScenario(BaseModel):
    """预测场景"""
    description: str
    probability: float
    key_levels: List[float]  # 关键价位
    signals: List[str]  # 观察信号

class ForecastResult(BaseModel):
    """预测结果"""
    stock: StockCode
    current_trend: str
    scenarios: List[ForecastScenario]
    risk_assessment: str
    confidence: float

class SkillResponse(BaseModel):
    """Skill统一响应"""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None
```

### 4.2 数据流向图

```
用户命令 → CommandParser → AnalysisRequest
                              ↓
                         PositionAnalyzer
                              ↓
                    ChanLunAnalyzer (现有)
                              ↓
                    BuySellDetector
                              ↓
                    PositionAnalysisResult
                              ↓
                    VisualRenderer
                              ↓
                    ResultFormatter → 用户界面
```

## 5. 接口设计

### 5.1 Skill主接口

```python
class ChanLunStockAnalysisSkill(Skill):
    """缠论股票分析Skill主类"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.command_parser = CommandParser()
        self.position_analyzer = PositionAnalyzer()
        self.backtest_engine = BacktestEngine()
        self.forecast_engine = ForecastEngine()
        self.result_formatter = ResultFormatter()

    @classmethod
    def metadata(cls) -> SkillMetadata:
        """Skill元数据"""
        return SkillMetadata(
            name="chanlun-stock-analysis",
            version="1.0.0",
            description="基于缠论理论的股票分析工具",
            author="ChanLun Quant Team",
            commands=[
                "分析 [股票代码] 缠论位置",
                "回测 [股票代码] [开始日期] [结束日期]",
                "预测 [股票代码] 走势"
            ],
            permissions=["stock_data:read"]
        )

    async def execute(self, context: SkillContext) -> SkillResponse:
        """执行主逻辑"""
        try:
            # 1. 解析命令
            request = self.command_parser.parse(context.user_input)

            # 2. 根据分析类型执行不同逻辑
            if request.analysis_type == 'position':
                result = await self.position_analyzer.analyze(request)
            elif request.analysis_type == 'backtest':
                result = await self.backtest_engine.run(request)
            elif request.analysis_type == 'forecast':
                result = await self.forecast_engine.forecast(request)

            # 3. 格式化输出
            output = self.result_formatter.format(result)

            return SkillResponse(
                success=True,
                message="分析完成",
                data=output
            )
        except Exception as e:
            return SkillResponse(
                success=False,
                message="分析失败",
                error=str(e)
            )
```

### 5.2 核心分析接口

```python
class PositionAnalyzer:
    """位置分析器"""

    async def analyze(self, request: AnalysisRequest) -> PositionAnalysisResult:
        """分析股票在缠论中的位置"""
        # 1. 获取K线数据
        klines = await self._get_klines(request.stock, request.start_date, request.end_date)

        # 2. 调用现有缠论分析器
        analyzer = ChanLunAnalyzer(klines)
        fractals = analyzer.get_fractals()
        pens = analyzer.get_pens()
        segments = analyzer.get_segments()
        pivots = analyzer.get_pivots()

        # 3. 识别买卖点
        buy_sell_points = self._detect_buy_sell_points(pivots, segments)

        # 4. 判断当前趋势
        trend_type = self._analyze_trend(pivots, segments)

        # 5. 评估风险
        risk_level = self._assess_risk(pivots, buy_sell_points)

        return PositionAnalysisResult(
            stock=request.stock,
            current_position=self._describe_position(pivots, buy_sell_points),
            fractals=fractals,
            pens=pens,
            pivots=pivots,
            buy_sell_points=buy_sell_points,
            trend_type=trend_type,
            risk_level=risk_level
        )

    def _detect_buy_sell_points(self, pivots, segments) -> List[BuySellPoint]:
        """识别买卖点"""
        detector = BuySellDetector(pivots, segments)
        return detector.detect_all()

class BuySellDetector:
    """买卖点检测器"""

    def detect_all(self) -> List[BuySellPoint]:
        """检测所有买卖点"""
        points = []
        points.extend(self._detect_first_points())
        points.extend(self._detect_second_points())
        points.extend(self._detect_third_points())
        return sorted(points, key=lambda x: x.position)

    def _detect_first_points(self) -> List[BuySellPoint]:
        """检测第一类买卖点（背驰点）"""
        # 实现背驰检测逻辑
        pass

    def _detect_second_points(self) -> List[BuySellPoint]:
        """检测第二类买卖点"""
        # 实现第二买卖点检测逻辑
        pass

    def _detect_third_points(self) -> List[BuySellPoint]:
        """检测第三类买卖点"""
        # 实现第三买卖点检测逻辑
        pass
```

### 5.3 回测接口

```python
class BacktestEngine:
    """回测引擎"""

    async def run(self, config: BacktestConfig) -> BacktestResult:
        """执行回测"""
        # 1. 获取历史数据
        klines = await self._get_klines(
            config.stock,
            config.start_date,
            config.end_date
        )

        # 2. 初始化回测状态
        capital = config.initial_capital
        position = 0  # 持仓数量
        trades = []

        # 3. 遍历历史数据
        for i in range(len(klines)):
            # 分析当前位置
            analyzer = ChanLunAnalyzer(klines[:i+1])
            buy_sell_points = BuySellDetector(
                analyzer.get_pivots(),
                analyzer.get_segments()
            ).detect_all()

            # 检查是否有信号
            for point in buy_sell_points:
                if point.position == i:
                    if point.type.startswith('buy') and position == 0:
                        # 买入
                        shares, cost = self._execute_buy(
                            capital, klines[i], config
                        )
                        position = shares
                        capital -= cost
                        trades.append(BacktestTrade(...))
                    elif point.type.startswith('sell') and position > 0:
                        # 卖出
                        revenue = self._execute_sell(
                            position, klines[i], config
                        )
                        capital += revenue
                        trades.append(BacktestTrade(...))
                        position = 0

        # 4. 计算统计指标
        return self._calculate_metrics(config, trades, capital)

    def _calculate_metrics(self, config, trades, final_capital) -> BacktestResult:
        """计算回测指标"""
        total_return = (final_capital - config.initial_capital) / config.initial_capital
        # 计算其他指标...
        return BacktestResult(...)
```

### 5.4 预测接口

```python
class ForecastEngine:
    """走势预测引擎"""

    async def forecast(self, request: AnalysisRequest) -> ForecastResult:
        """预测未来走势"""
        # 1. 获取历史数据
        klines = await self._get_klines(request.stock)

        # 2. 分析当前走势
        analyzer = ChanLunAnalyzer(klines)
        pivots = analyzer.get_pivots()
        segments = analyzer.get_segments()

        # 3. 判断走势类型
        trend_type = self._classify_trend(pivots, segments)

        # 4. 推演未来走势
        scenarios = self._deduce_scenarios(pivots, segments, trend_type)

        # 5. 评估风险
        risk = self._assess_risk(scenarios)

        return ForecastResult(
            stock=request.stock,
            current_trend=trend_type,
            scenarios=scenarios,
            risk_assessment=risk,
            confidence=self._calculate_confidence(scenarios)
        )

    def _deduce_scenarios(self, pivots, segments, trend_type) -> List[ForecastScenario]:
        """推演未来可能的走势"""
        scenarios = []

        if trend_type == 'trend_up':
            # 上升趋势：可能继续、可能转折
            scenarios.append(ForecastScenario(
                description="延续上升趋势，形成新中枢",
                probability=0.6,
                key_levels=[...],
                signals=["关注是否出现背驰"]
            ))
            scenarios.append(ForecastScenario(
                description="趋势转折，形成第一卖点",
                probability=0.3,
                key_levels=[...],
                signals=["关注背驰信号"]
            ))
        # 其他情况...

        return scenarios
```

## 6. 可视化设计

### 6.1 图表类型

| 图表类型 | 用途 | 关键元素 |
|---------|------|---------|
| K线图+标注 | 展示缠论元素 | K线、分型标记、笔连线、中枢矩形、买卖点标记 |
| 资金曲线图 | 回测结果展示 | 资金随时间变化曲线 |
| 收益分布图 | 回测统计分析 | 收益率直方图、风险指标 |
| 走势推演图 | 预测结果展示 | 当前走势+未来可能路径 |

### 6.2 可视化接口

```python
class VisualRenderer:
    """可视化渲染器"""

    def render_position_analysis(self, result: PositionAnalysisResult) -> str:
        """渲染位置分析结果"""
        fig, ax = plt.subplots(figsize=(14, 8))

        # 1. 绘制K线
        self._draw_klines(ax, result.klines)

        # 2. 标注分型
        self._mark_fractals(ax, result.fractals)

        # 3. 绘制笔
        self._draw_pens(ax, result.pens)

        # 4. 绘制中枢
        self._draw_pivots(ax, result.pivots)

        # 5. 标注买卖点
        self._mark_buy_sell_points(ax, result.buy_sell_points)

        # 6. 添加图例和标题
        ax.set_title(f"{result.stock.code} 缠论分析")
        ax.legend()

        # 返回base64编码的图片
        return self._fig_to_base64(fig)

    def _draw_pivots(self, ax, pivots: List[PivotInfo]):
        """绘制中枢矩形"""
        for pivot in pivots:
            rect = plt.Rectangle(
                (pivot.start_index, pivot.low),
                pivot.end_index - pivot.start_index,
                pivot.high - pivot.low,
                fill=True,
                alpha=0.3,
                color='yellow',
                label=f'中枢{pivot.level}'
            )
            ax.add_patch(rect)

    def _mark_buy_sell_points(self, ax, points: List[BuySellPoint]):
        """标注买卖点"""
        for point in points:
            marker = '^' if point.type.startswith('buy') else 'v'
            color = 'red' if point.type.startswith('buy') else 'green'
            ax.scatter(
                point.position, point.price,
                marker=marker, s=200, c=color,
                label=point.type, zorder=5
            )
            ax.annotate(
                f"{point.type}\n置信度:{point.confidence:.2f}",
                (point.position, point.price),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center'
            )
```

## 7. 配置管理

### 7.1 配置文件结构

```yaml
# config.yaml
skill:
  name: chanlun-stock-analysis
  version: 1.0.0

data_source:
  provider: tushare  # tushare 或 akshare
  token: ${TUSHARE_TOKEN}
  cache_enabled: true
  cache_ttl: 3600  # 缓存1小时

analysis:
  min_pen_length: 3  # 最小笔长度
  pivot_level: 1  # 默认中枢级别
  confidence_threshold: 0.6  # 买卖点置信度阈值

backtest:
  default_initial_capital: 100000
  commission_rate: 0.0003
  slippage: 0.0

visualization:
  figure_size: [14, 8]
  dpi: 100
  style: seaborn

logging:
  level: INFO
  file: logs/chanlun_skill.log
```

### 7.2 配置加载

```python
from pydantic import BaseSettings

class SkillConfig(BaseSettings):
    """Skill配置"""

    # 数据源配置
    data_provider: str = 'tushare'
    data_token: str
    cache_enabled: bool = True
    cache_ttl: int = 3600

    # 分析参数
    min_pen_length: int = 3
    pivot_level: int = 1
    confidence_threshold: float = 0.6

    # 回测参数
    default_initial_capital: float = 100000
    commission_rate: float = 0.0003
    slippage: float = 0.0

    class Config:
        env_prefix = 'CHANLUN_'  # 环境变量前缀
```

## 8. 异常处理

### 8.1 异常类型定义

```python
class ChanLunSkillError(Exception):
    """Skill基础异常"""
    pass

class DataFetchError(ChanLunSkillError):
    """数据获取异常"""
    pass

class AnalysisError(ChanLunSkillError):
    """分析异常"""
    pass

class InvalidParameterError(ChanLunSkillError):
    """参数无效异常"""
    pass

class BacktestError(ChanLunSkillError):
    """回测异常"""
    pass
```

### 8.2 异常处理策略

| 异常类型 | 处理策略 | 用户提示 |
|---------|---------|---------|
| DataFetchError | 重试3次，记录日志 | "数据获取失败，请检查网络或稍后重试" |
| InvalidParameterError | 直接返回错误 | "参数无效：{具体错误}" |
| AnalysisError | 记录日志，返回部分结果 | "分析过程中出现异常，部分结果可能不准确" |
| BacktestError | 终止回测，返回已执行部分 | "回测执行失败：{具体错误}" |

## 9. 性能优化

### 9.1 缓存策略

```python
from functools import lru_cache
import hashlib

class DataCache:
    """数据缓存管理器"""

    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self._cache = {}

    async def get_klines(self, stock: StockCode, start: datetime, end: datetime):
        """获取K线数据（带缓存）"""
        cache_key = self._make_key(stock, start, end)

        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.ttl:
                return cached_data

        # 从数据源获取
        data = await self._fetch_from_source(stock, start, end)
        self._cache[cache_key] = (data, time.time())
        return data

    def _make_key(self, stock, start, end) -> str:
        """生成缓存键"""
        key_str = f"{stock.code}_{start}_{end}"
        return hashlib.md5(key_str.encode()).hexdigest()
```

### 9.2 异步处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncAnalyzer:
    """异步分析器"""

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def analyze_batch(self, stocks: List[StockCode]) -> List[PositionAnalysisResult]:
        """批量分析多只股票"""
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                self.executor,
                self.position_analyzer.analyze,
                stock
            )
            for stock in stocks
        ]
        return await asyncio.gather(*tasks)
```

## 10. 测试策略

### 10.1 单元测试

```python
import pytest
from unittest.mock import Mock, patch

class TestPositionAnalyzer:
    """位置分析器测试"""

    @pytest.fixture
    def analyzer(self):
        return PositionAnalyzer()

    def test_fractal_detection(self, analyzer):
        """测试分型识别"""
        # 准备测试数据
        klines = self._create_test_klines()

        # 执行分析
        result = analyzer.analyze(klines)

        # 验证结果
        assert len(result.fractals) > 0
        assert all(f.type in ['top', 'bottom'] for f in result.fractals)

    def test_buy_point_detection(self, analyzer):
        """测试买点识别"""
        # 准备包含第一买点的测试数据
        klines = self._create_klines_with_buy_point()

        result = analyzer.analyze(klines)

        # 验证识别到买点
        buy_points = [p for p in result.buy_sell_points if p.type.startswith('buy')]
        assert len(buy_points) > 0
        assert any(p.type == 'buy1' for p in buy_points)
```

### 10.2 集成测试

```python
class TestChanLunSkill:
    """Skill集成测试"""

    @pytest.mark.asyncio
    async def test_skill_execution(self):
        """测试skill完整执行流程"""
        skill = ChanLunStockAnalysisSkill()
        context = SkillContext(
            user_input="分析 000001 缠论位置"
        )

        response = await skill.execute(context)

        assert response.success
        assert response.data is not None
        assert 'position' in response.data

    @pytest.mark.asyncio
    async def test_backtest_flow(self):
        """测试回测完整流程"""
        skill = ChanLunStockAnalysisSkill()
        context = SkillContext(
            user_input="回测 000001 2023-01-01 2023-12-31"
        )

        response = await skill.execute(context)

        assert response.success
        assert 'total_return' in response.data
        assert 'trades' in response.data
```

## 11. 部署方案

### 11.1 目录结构

```
chanlun-stock-analysis/
├── skill/
│   ├── __init__.py
│   ├── main.py                 # Skill入口
│   ├── config.yaml             # 配置文件
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── position.py         # 位置分析
│   │   ├── backtest.py         # 回测引擎
│   │   └── forecast.py         # 预测引擎
│   ├── detectors/
│   │   ├── __init__.py
│   │   └── buy_sell.py         # 买卖点检测
│   ├── parsers/
│   │   ├── __init__.py
│   │   └── command.py          # 命令解析
│   ├── renderers/
│   │   ├── __init__.py
│   │   └── visual.py           # 可视化
│   └── utils/
│       ├── __init__.py
│       ├── data.py             # 数据获取
│       └── cache.py            # 缓存管理
├── tests/
│   ├── test_position.py
│   ├── test_backtest.py
│   └── test_forecast.py
├── docs/
│   ├── user_guide.md
│   └── api_reference.md
├── requirements.txt
├── setup.py
└── README.md
```

### 11.2 安装脚本

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name='chanlun-stock-analysis',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'openclaw-sdk>=1.0.0',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'matplotlib>=3.4.0',
        'tushare>=1.2.0',
        'pydantic>=1.8.0',
        'loguru>=0.6.0',
    ],
    entry_points={
        'openclaw.skills': [
            'chanlun = skill.main:ChanLunStockAnalysisSkill'
        ]
    }
)
```

## 12. 安全考虑

### 12.1 数据安全
- 不存储用户敏感信息
- 数据传输使用HTTPS
- 本地缓存数据加密存储

### 12.2 输入验证
- 严格验证股票代码格式
- 限制日期范围合理性
- 防止SQL注入等攻击

### 12.3 权限控制
- 仅申请必要的数据读取权限
- 不申请交易执行权限
- 遵循最小权限原则

## 13. 监控与日志

### 13.1 日志规范

```python
from loguru import logger

# 配置日志
logger.add(
    "logs/chanlun_skill.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# 使用示例
logger.info(f"开始分析股票: {stock_code}")
logger.success(f"分析完成，识别到{len(buy_points)}个买卖点")
logger.warning(f"数据缺失: {missing_dates}")
logger.error(f"分析失败: {error}")
```

### 13.2 性能监控

```python
import time
from functools import wraps

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} 执行耗时: {duration:.2f}秒")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败，耗时: {duration:.2f}秒，错误: {e}")
            raise
    return wrapper
```

---

**文档结束**
