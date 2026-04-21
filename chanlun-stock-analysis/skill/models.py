"""
缠论股票分析数据模型

使用Pydantic定义所有核心数据模型，确保类型安全和数据验证。
"""
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ===== 输入模型 =====

class StockCode(BaseModel):
    """股票代码"""
    code: str = Field(..., description="股票代码，如'000001'")
    market: Literal['SH', 'SZ'] = Field(..., description="市场：上海/深圳")
    
    @validator('code')
    def validate_code(cls, v):
        """验证股票代码格式"""
        if not v or not v.isdigit() or len(v) != 6:
            raise ValueError('股票代码必须是6位数字')
        return v
    
    def __str__(self):
        """返回完整股票代码（带市场前缀）"""
        return f"{self.market}{self.code}"


class AnalysisRequest(BaseModel):
    """分析请求"""
    stock: StockCode = Field(..., description="股票代码")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    analysis_type: Literal['position', 'backtest', 'forecast'] = Field(
        'position', 
        description="分析类型：position=位置分析，backtest=回测，forecast=预测"
    )
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """验证日期范围"""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('结束日期不能早于开始日期')
        return v


class BacktestConfig(BaseModel):
    """回测配置"""
    stock: StockCode = Field(..., description="股票代码")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    initial_capital: float = Field(100000, gt=0, description="初始资金")
    commission_rate: float = Field(0.0003, ge=0, description="手续费率")
    slippage: float = Field(0.0, ge=0, description="滑点")
    max_position_ratio: float = Field(0.95, gt=0, le=1, description="最大持仓比例")
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """验证日期范围"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期不能早于开始日期')
        return v


# ===== 输出模型 =====

class FractalInfo(BaseModel):
    """分型信息"""
    type: Literal['top', 'bottom'] = Field(..., description="分型类型：top=顶分型，bottom=底分型")
    position: int = Field(..., ge=0, description="分型位置索引")
    price: float = Field(..., gt=0, description="分型价格")
    datetime: datetime = Field(..., description="分型时间")


class PenInfo(BaseModel):
    """笔信息"""
    start: FractalInfo = Field(..., description="笔的起点")
    end: FractalInfo = Field(..., description="笔的终点")
    direction: Literal['up', 'down'] = Field(..., description="笔的方向：up=向上，down=向下")
    length: float = Field(..., description="笔的长度（价格差）")
    
    @validator('direction')
    def validate_direction(cls, v, values):
        """验证笔的方向与起点终点是否一致"""
        if 'start' in values and 'end' in values:
            if v == 'up' and values['end'].price < values['start'].price:
                raise ValueError('向上笔的终点价格应高于起点')
            if v == 'down' and values['end'].price > values['start'].price:
                raise ValueError('向下笔的终点价格应低于起点')
        return v


class PivotInfo(BaseModel):
    """中枢信息"""
    level: int = Field(..., ge=1, description="中枢级别")
    high: float = Field(..., gt=0, description="中枢上沿")
    low: float = Field(..., gt=0, description="中枢下沿")
    start_index: int = Field(..., ge=0, description="中枢起始索引")
    end_index: int = Field(..., ge=0, description="中枢结束索引")
    segments_count: int = Field(..., ge=3, description="构成中枢的线段数")
    
    @validator('low')
    def validate_range(cls, v, values):
        """验证中枢上下沿"""
        if 'high' in values and v >= values['high']:
            raise ValueError('中枢下沿必须小于上沿')
        return v
    
    @property
    def mid(self) -> float:
        """中枢中轴"""
        return (self.high + self.low) / 2
    
    @property
    def amplitude(self) -> float:
        """中枢振幅"""
        return (self.high - self.low) / self.low


class BuySellPoint(BaseModel):
    """买卖点"""
    type: Literal['buy1', 'buy2', 'buy3', 'sell1', 'sell2', 'sell3'] = Field(
        ..., 
        description="买卖点类型：buy1=第一类买点，buy2=第二类买点，buy3=第三类买点，sell1=第一类卖点，sell2=第二类卖点，sell3=第三类卖点"
    )
    position: int = Field(..., ge=0, description="买卖点位置索引")
    price: float = Field(..., gt=0, description="买卖点价格")
    datetime: datetime = Field(..., description="买卖点时间")
    confidence: float = Field(..., ge=0, le=1, description="置信度，0-1之间")
    description: str = Field(..., description="买卖点描述")
    
    @property
    def is_buy(self) -> bool:
        """是否为买点"""
        return self.type.startswith('buy')
    
    @property
    def point_level(self) -> int:
        """买卖点级别（1、2、3）"""
        return int(self.type[-1])


class PositionAnalysisResult(BaseModel):
    """位置分析结果"""
    stock: StockCode = Field(..., description="股票代码")
    current_position: str = Field(..., description="当前位置描述")
    fractals: List[FractalInfo] = Field(default_factory=list, description="分型列表")
    pens: List[PenInfo] = Field(default_factory=list, description="笔列表")
    pivots: List[PivotInfo] = Field(default_factory=list, description="中枢列表")
    buy_sell_points: List[BuySellPoint] = Field(default_factory=list, description="买卖点列表")
    trend_type: Literal['trend_up', 'trend_down', 'consolidation'] = Field(
        ..., 
        description="趋势类型：trend_up=上升趋势，trend_down=下降趋势，consolidation=盘整"
    )
    risk_level: Literal['low', 'medium', 'high'] = Field(
        ..., 
        description="风险等级：low=低风险，medium=中等风险，high=高风险"
    )
    analysis_time: datetime = Field(default_factory=datetime.now, description="分析时间")
    
    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }


class BacktestTrade(BaseModel):
    """回测交易记录"""
    type: Literal['buy', 'sell'] = Field(..., description="交易类型")
    datetime: datetime = Field(..., description="交易时间")
    price: float = Field(..., gt=0, description="交易价格")
    shares: int = Field(..., gt=0, description="交易股数")
    amount: float = Field(..., gt=0, description="交易金额")
    commission: float = Field(..., ge=0, description="手续费")
    reason: str = Field(..., description="交易原因（买卖点类型）")


class BacktestResult(BaseModel):
    """回测结果"""
    stock: StockCode = Field(..., description="股票代码")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    initial_capital: float = Field(..., gt=0, description="初始资金")
    final_capital: float = Field(..., description="最终资金")
    total_return: float = Field(..., description="总收益率")
    annual_return: float = Field(..., description="年化收益率")
    win_rate: float = Field(..., ge=0, le=1, description="胜率")
    max_drawdown: float = Field(..., ge=0, le=1, description="最大回撤")
    sharpe_ratio: float = Field(..., description="夏普比率")
    trades: List[BacktestTrade] = Field(default_factory=list, description="交易记录")
    total_trades: int = Field(..., ge=0, description="总交易次数")
    win_trades: int = Field(..., ge=0, description="盈利交易次数")
    loss_trades: int = Field(..., ge=0, description="亏损交易次数")
    analysis_time: datetime = Field(default_factory=datetime.now, description="分析时间")
    
    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }


class ForecastScenario(BaseModel):
    """预测场景"""
    description: str = Field(..., description="场景描述")
    probability: float = Field(..., ge=0, le=1, description="发生概率")
    key_levels: List[float] = Field(default_factory=list, description="关键价位")
    signals: List[str] = Field(default_factory=list, description="观察信号")
    target_price: Optional[float] = Field(None, description="目标价位")
    stop_loss: Optional[float] = Field(None, description="止损价位")


class ForecastResult(BaseModel):
    """预测结果"""
    stock: StockCode = Field(..., description="股票代码")
    current_trend: Literal['trend_up', 'trend_down', 'consolidation'] = Field(
        ..., 
        description="当前趋势"
    )
    current_price: float = Field(..., gt=0, description="当前价格")
    scenarios: List[ForecastScenario] = Field(
        default_factory=list, 
        description="未来可能场景"
    )
    risk_assessment: str = Field(..., description="风险评估")
    confidence: float = Field(..., ge=0, le=1, description="预测置信度")
    recommendation: str = Field(..., description="操作建议")
    analysis_time: datetime = Field(default_factory=datetime.now, description="分析时间")
    
    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }


# ===== 响应模型 =====

class SkillResponse(BaseModel):
    """Skill统一响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        """Pydantic配置"""
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @classmethod
    def success_response(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'SkillResponse':
        """创建成功响应"""
        return cls(
            success=True,
            message=message,
            data=data
        )
    
    @classmethod
    def error_response(cls, message: str, error: Optional[str] = None) -> 'SkillResponse':
        """创建错误响应"""
        return cls(
            success=False,
            message=message,
            error=error or message
        )
