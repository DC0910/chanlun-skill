"""
位置分析器

分析股票当前在缠论中的位置（中枢、买卖点等）。
"""
import pandas as pd
from typing import List, Optional
from datetime import datetime

from ..models import (
    StockCode,
    AnalysisRequest,
    PositionAnalysisResult,
    FractalInfo,
    PenInfo,
    PivotInfo,
    BuySellPoint
)
from ..utils.data import get_klines
from ..utils.logger import default_logger as logger
from ..detectors.buy_sell import BuySellDetector
from ..config import ConfigManager


class PositionAnalyzer:
    """位置分析器"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        初始化位置分析器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.get()
        logger.info("位置分析器初始化完成")
    
    async def analyze(self, request: AnalysisRequest) -> PositionAnalysisResult:
        """
        分析股票位置
        
        Args:
            request: 分析请求
        
        Returns:
            位置分析结果
        """
        logger.info(f"开始分析股票位置：{request.stock}")
        
        # 1. 获取K线数据
        klines = await self._get_klines(request)
        
        # 2. 识别分型
        fractals = self._identify_fractals(klines)
        logger.info(f"识别到{len(fractals)}个分型")
        
        # 3. 识别笔
        pens = self._identify_pens(fractals, klines)
        logger.info(f"识别到{len(pens)}笔")
        
        # 4. 识别线段
        segments = self._identify_segments(pens)
        logger.info(f"识别到{len(segments)}个线段")
        
        # 5. 识别中枢
        pivots = self._identify_pivots(segments, klines)
        logger.info(f"识别到{len(pivots)}个中枢")
        
        # 6. 检测买卖点
        detector = BuySellDetector(pivots, pens, fractals)
        buy_sell_points = detector.detect_all()
        logger.info(f"检测到{len(buy_sell_points)}个买卖点")
        
        # 7. 判断趋势类型
        trend_type = self._classify_trend(pivots, pens)
        
        # 8. 评估风险等级
        risk_level = self._assess_risk(pivots, buy_sell_points, trend_type)
        
        # 9. 生成当前位置描述
        current_position = self._generate_position_description(
            pivots, buy_sell_points, trend_type, klines
        )
        
        result = PositionAnalysisResult(
            stock=request.stock,
            current_position=current_position,
            fractals=fractals,
            pens=pens,
            pivots=pivots,
            buy_sell_points=buy_sell_points,
            trend_type=trend_type,
            risk_level=risk_level
        )
        
        logger.success(f"位置分析完成：{request.stock}")
        return result
    
    async def _get_klines(self, request: AnalysisRequest) -> pd.DataFrame:
        """获取K线数据"""
        start_date = request.start_date.strftime('%Y-%m-%d') if request.start_date else None
        end_date = request.end_date.strftime('%Y-%m-%d') if request.end_date else None
        
        return get_klines(
            stock_code=request.stock.code,
            market=request.stock.market,
            start_date=start_date,
            end_date=end_date,
            data_source=self.config.data_source.default,
            tushare_token=self.config.data_source.tushare_token
        )
    
    def _identify_fractals(self, klines: pd.DataFrame) -> List[FractalInfo]:
        """
        识别分型
        
        分型识别逻辑：
        1. 顶分型：相邻三根K线中，中间K线的高点和低点都是最高的
        2. 底分型：相邻三根K线中，中间K线的高点和低点都是最低的
        
        Args:
            klines: K线数据
        
        Returns:
            分型列表
        """
        fractals = []
        confirm_bars = self.config.analysis.fractal_confirm_bars
        
        for i in range(confirm_bars, len(klines) - confirm_bars):
            # 检查顶分型
            is_top = True
            for j in range(1, confirm_bars + 1):
                if (klines.iloc[i]['high'] <= klines.iloc[i - j]['high'] or
                    klines.iloc[i]['high'] <= klines.iloc[i + j]['high']):
                    is_top = False
                    break
            
            if is_top:
                fractals.append(FractalInfo(
                    type='top',
                    position=i,
                    price=klines.iloc[i]['high'],
                    datetime=klines.iloc[i]['datetime']
                ))
                continue
            
            # 检查底分型
            is_bottom = True
            for j in range(1, confirm_bars + 1):
                if (klines.iloc[i]['low'] >= klines.iloc[i - j]['low'] or
                    klines.iloc[i]['low'] >= klines.iloc[i + j]['low']):
                    is_bottom = False
                    break
            
            if is_bottom:
                fractals.append(FractalInfo(
                    type='bottom',
                    position=i,
                    price=klines.iloc[i]['low'],
                    datetime=klines.iloc[i]['datetime']
                ))
        
        return fractals
    
    def _identify_pens(
        self,
        fractals: List[FractalInfo],
        klines: pd.DataFrame
    ) -> List[PenInfo]:
        """
        识别笔
        
        笔识别逻辑：
        1. 连接相邻的顶底分型
        2. 笔的长度必须满足最小要求
        
        Args:
            fractals: 分型列表
            klines: K线数据
        
        Returns:
            笔列表
        """
        pens = []
        min_length = self.config.analysis.pen_min_length
        
        if len(fractals) < 2:
            return pens
        
        # 连接相邻分型
        for i in range(len(fractals) - 1):
            start = fractals[i]
            end = fractals[i + 1]
            
            # 顶底分型必须交替出现
            if start.type == end.type:
                continue
            
            # 计算笔的长度
            length = abs(end.price - start.price)
            
            # 检查最小长度
            if length < min_length:
                continue
            
            # 确定笔的方向
            direction = 'up' if end.price > start.price else 'down'
            
            pens.append(PenInfo(
                start=start,
                end=end,
                direction=direction,
                length=length
            ))
        
        return pens
    
    def _identify_segments(self, pens: List[PenInfo]) -> List[PenInfo]:
        """
        识别线段
        
        线段识别逻辑：
        1. 线段由至少3笔组成
        2. 线段代表更高级别的走势
        
        Args:
            pens: 笔列表
        
        Returns:
            线段列表（简化实现，返回笔列表）
        """
        # 简化实现：直接返回笔列表
        # 实际应用中需要实现更复杂的线段识别算法
        return pens
    
    def _identify_pivots(
        self,
        segments: List[PenInfo],
        klines: pd.DataFrame
    ) -> List[PivotInfo]:
        """
        识别中枢
        
        中枢识别逻辑：
        1. 中枢由至少3段连续的线段重叠区域构成
        2. 计算重叠区域的上下沿
        
        Args:
            segments: 线段列表
            klines: K线数据
        
        Returns:
            中枢列表
        """
        pivots = []
        min_segments = self.config.analysis.pivot_min_segments
        
        if len(segments) < min_segments:
            return pivots
        
        # 滑动窗口识别中枢
        for i in range(len(segments) - min_segments + 1):
            window_segments = segments[i:i + min_segments]
            
            # 计算重叠区域
            overlap_high = min(seg.end.price if seg.direction == 'up' else seg.start.price
                              for seg in window_segments)
            overlap_low = max(seg.end.price if seg.direction == 'down' else seg.start.price
                             for seg in window_segments)
            
            # 检查是否有重叠
            if overlap_high > overlap_low:
                pivots.append(PivotInfo(
                    level=1,  # 默认级别为1
                    high=overlap_high,
                    low=overlap_low,
                    start_index=window_segments[0].start.position,
                    end_index=window_segments[-1].end.position,
                    segments_count=min_segments
                ))
        
        return pivots
    
    def _classify_trend(
        self,
        pivots: List[PivotInfo],
        pens: List[PenInfo]
    ) -> str:
        """
        判断趋势类型
        
        Args:
            pivots: 中枢列表
            pens: 笔列表
        
        Returns:
            趋势类型：trend_up, trend_down, consolidation
        """
        if len(pens) < 2:
            return 'consolidation'
        
        # 比较最近几笔的方向
        recent_pens = pens[-5:] if len(pens) >= 5 else pens
        up_count = sum(1 for pen in recent_pens if pen.direction == 'up')
        down_count = len(recent_pens) - up_count
        
        if up_count > down_count * 1.5:
            return 'trend_up'
        elif down_count > up_count * 1.5:
            return 'trend_down'
        else:
            return 'consolidation'
    
    def _assess_risk(
        self,
        pivots: List[PivotInfo],
        buy_sell_points: List[BuySellPoint],
        trend_type: str
    ) -> str:
        """
        评估风险等级
        
        Args:
            pivots: 中枢列表
            buy_sell_points: 买卖点列表
            trend_type: 趋势类型
        
        Returns:
            风险等级：low, medium, high
        """
        # 基于趋势类型和买卖点数量评估风险
        if trend_type == 'consolidation':
            return 'medium'
        
        # 检查最近的买卖点
        if buy_sell_points:
            recent_point = buy_sell_points[-1]
            if recent_point.confidence > 0.8:
                return 'low'
            elif recent_point.confidence > 0.6:
                return 'medium'
        
        return 'high'
    
    def _generate_position_description(
        self,
        pivots: List[PivotInfo],
        buy_sell_points: List[BuySellPoint],
        trend_type: str,
        klines: pd.DataFrame
    ) -> str:
        """
        生成当前位置描述
        
        Args:
            pivots: 中枢列表
            buy_sell_points: 买卖点列表
            trend_type: 趋势类型
            klines: K线数据
        
        Returns:
            位置描述
        """
        current_price = klines.iloc[-1]['close']
        
        # 趋势描述
        trend_desc = {
            'trend_up': '上升趋势',
            'trend_down': '下降趋势',
            'consolidation': '盘整'
        }[trend_type]
        
        # 中枢描述
        pivot_desc = ""
        if pivots:
            latest_pivot = pivots[-1]
            if latest_pivot.low <= current_price <= latest_pivot.high:
                pivot_desc = f"，当前在中枢内（{latest_pivot.low:.2f}-{latest_pivot.high:.2f}）"
            elif current_price > latest_pivot.high:
                pivot_desc = f"，当前在中枢上方（中枢上沿={latest_pivot.high:.2f}）"
            else:
                pivot_desc = f"，当前在中枢下方（中枢下沿={latest_pivot.low:.2f}）"
        
        # 买卖点描述
        point_desc = ""
        if buy_sell_points:
            recent_point = buy_sell_points[-1]
            point_type = {
                'buy1': '第一类买点',
                'buy2': '第二类买点',
                'buy3': '第三类买点',
                'sell1': '第一类卖点',
                'sell2': '第二类卖点',
                'sell3': '第三类卖点'
            }[recent_point.type]
            point_desc = f"，最近出现{point_type}（置信度={recent_point.confidence:.2f}）"
        
        return f"当前处于{trend_desc}{pivot_desc}{point_desc}，当前价格={current_price:.2f}"
