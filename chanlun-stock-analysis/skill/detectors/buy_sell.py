"""
买卖点检测器

实现缠论买卖点识别算法，包括第一、二、三类买卖点。
"""
from typing import List, Optional, Tuple
from datetime import datetime

from ..models import PivotInfo, BuySellPoint, PenInfo, FractalInfo
from ..utils.logger import default_logger as logger


class BuySellDetector:
    """买卖点检测器"""
    
    def __init__(
        self,
        pivots: List[PivotInfo],
        pens: List[PenInfo],
        fractals: List[FractalInfo]
    ):
        """
        初始化买卖点检测器
        
        Args:
            pivots: 中枢列表
            pens: 笔列表
            fractals: 分型列表
        """
        self.pivots = pivots
        self.pens = pens
        self.fractals = fractals
        logger.info(f"买卖点检测器初始化，中枢数={len(pivots)}，笔数={len(pens)}，分型数={len(fractals)}")
    
    def detect_all(self) -> List[BuySellPoint]:
        """
        检测所有买卖点
        
        Returns:
            买卖点列表
        """
        buy_sell_points = []
        
        # 检测第一类买卖点
        buy_sell_points.extend(self.detect_first_level())
        
        # 检测第二类买卖点
        buy_sell_points.extend(self.detect_second_level())
        
        # 检测第三类买卖点
        buy_sell_points.extend(self.detect_third_level())
        
        # 按位置排序
        buy_sell_points.sort(key=lambda x: x.position)
        
        logger.success(f"检测到{len(buy_sell_points)}个买卖点")
        return buy_sell_points
    
    def detect_first_level(self) -> List[BuySellPoint]:
        """
        检测第一类买卖点（背驰点）
        
        第一类买点：走势离开中枢后出现背驰，形成买点
        第一类卖点：走势离开中枢后出现背驰，形成卖点
        
        Returns:
            第一类买卖点列表
        """
        points = []
        
        if len(self.pivots) < 1 or len(self.pens) < 3:
            return points
        
        for i, pivot in enumerate(self.pivots):
            # 查找离开中枢的笔
            exit_pens = self._find_exit_pens(pivot)
            
            for pen in exit_pens:
                # 检查是否出现背驰
                is_divergence, divergence_strength = self._check_divergence(pen, pivot)
                
                if is_divergence:
                    # 判断是买点还是卖点
                    if pen.direction == 'down':
                        # 向下笔背驰，形成第一类买点
                        point = BuySellPoint(
                            type='buy1',
                            position=pen.end.position,
                            price=pen.end.price,
                            datetime=pen.end.datetime,
                            confidence=self._calculate_confidence(divergence_strength, pivot),
                            description=f"第一类买点：离开中枢后向下背驰，中枢级别={pivot.level}"
                        )
                        points.append(point)
                        logger.debug(f"检测到第一类买点：位置={point.position}，价格={point.price}")
                    
                    elif pen.direction == 'up':
                        # 向上笔背驰，形成第一类卖点
                        point = BuySellPoint(
                            type='sell1',
                            position=pen.end.position,
                            price=pen.end.price,
                            datetime=pen.end.datetime,
                            confidence=self._calculate_confidence(divergence_strength, pivot),
                            description=f"第一类卖点：离开中枢后向上背驰，中枢级别={pivot.level}"
                        )
                        points.append(point)
                        logger.debug(f"检测到第一类卖点：位置={point.position}，价格={point.price}")
        
        return points
    
    def detect_second_level(self) -> List[BuySellPoint]:
        """
        检测第二类买卖点
        
        第二类买点：回拉不破中枢形成的买点
        第二类卖点：回拉不破中枢形成的卖点
        
        Returns:
            第二类买卖点列表
        """
        points = []
        
        if len(self.pivots) < 1 or len(self.pens) < 2:
            return points
        
        for i, pivot in enumerate(self.pivots):
            # 查找回拉中枢的笔
            pullback_pens = self._find_pullback_pens(pivot)
            
            for pen in pullback_pens:
                # 检查是否不破中枢
                is_not_break = self._check_not_break(pen, pivot)
                
                if is_not_break:
                    # 判断是买点还是卖点
                    if pen.direction == 'up':
                        # 向上回拉不破中枢上沿，形成第二类买点
                        point = BuySellPoint(
                            type='buy2',
                            position=pen.end.position,
                            price=pen.end.price,
                            datetime=pen.end.datetime,
                            confidence=0.7,  # 第二类买卖点置信度固定为0.7
                            description=f"第二类买点：向上回拉不破中枢，中枢级别={pivot.level}"
                        )
                        points.append(point)
                        logger.debug(f"检测到第二类买点：位置={point.position}，价格={point.price}")
                    
                    elif pen.direction == 'down':
                        # 向下回拉不破中枢下沿，形成第二类卖点
                        point = BuySellPoint(
                            type='sell2',
                            position=pen.end.position,
                            price=pen.end.price,
                            datetime=pen.end.datetime,
                            confidence=0.7,
                            description=f"第二类卖点：向下回拉不破中枢，中枢级别={pivot.level}"
                        )
                        points.append(point)
                        logger.debug(f"检测到第二类卖点：位置={point.position}，价格={point.price}")
        
        return points
    
    def detect_third_level(self) -> List[BuySellPoint]:
        """
        检测第三类买卖点
        
        第三类买点：新中枢形成后的回拉买点
        第三类卖点：新中枢形成后的回拉卖点
        
        Returns:
            第三类买卖点列表
        """
        points = []
        
        if len(self.pivots) < 2:
            return points
        
        for i in range(1, len(self.pivots)):
            prev_pivot = self.pivots[i - 1]
            curr_pivot = self.pivots[i]
            
            # 检查是否形成新中枢
            is_new_pivot = self._check_new_pivot(prev_pivot, curr_pivot)
            
            if is_new_pivot:
                # 查找回拉笔
                pullback_pens = self._find_pullback_pens(curr_pivot)
                
                for pen in pullback_pens:
                    # 判断是买点还是卖点
                    if pen.direction == 'up' and pen.end.price < curr_pivot.high:
                        # 向上回拉不破新中枢上沿，形成第三类买点
                        point = BuySellPoint(
                            type='buy3',
                            position=pen.end.position,
                            price=pen.end.price,
                            datetime=pen.end.datetime,
                            confidence=0.6,  # 第三类买卖点置信度固定为0.6
                            description=f"第三类买点：新中枢形成后向上回拉，中枢级别={curr_pivot.level}"
                        )
                        points.append(point)
                        logger.debug(f"检测到第三类买点：位置={point.position}，价格={point.price}")
                    
                    elif pen.direction == 'down' and pen.end.price > curr_pivot.low:
                        # 向下回拉不破新中枢下沿，形成第三类卖点
                        point = BuySellPoint(
                            type='sell3',
                            position=pen.end.position,
                            price=pen.end.price,
                            datetime=pen.end.datetime,
                            confidence=0.6,
                            description=f"第三类卖点：新中枢形成后向下回拉，中枢级别={curr_pivot.level}"
                        )
                        points.append(point)
                        logger.debug(f"检测到第三类卖点：位置={point.position}，价格={point.price}")
        
        return points
    
    def _find_exit_pens(self, pivot: PivotInfo) -> List[PenInfo]:
        """
        查找离开中枢的笔
        
        Args:
            pivot: 中枢信息
        
        Returns:
            离开中枢的笔列表
        """
        exit_pens = []
        
        for pen in self.pens:
            # 笔的起点在中枢内，终点在中枢外
            if (pivot.low <= pen.start.price <= pivot.high and
                (pen.end.price > pivot.high or pen.end.price < pivot.low)):
                exit_pens.append(pen)
        
        return exit_pens
    
    def _find_pullback_pens(self, pivot: PivotInfo) -> List[PenInfo]:
        """
        查找回拉中枢的笔
        
        Args:
            pivot: 中枢信息
        
        Returns:
            回拉中枢的笔列表
        """
        pullback_pens = []
        
        for pen in self.pens:
            # 笔的起点在中枢外，终点在中枢内或接近中枢
            if ((pen.start.price > pivot.high or pen.start.price < pivot.low) and
                pivot.low - pivot.amplitude * pivot.low <= pen.end.price <= pivot.high + pivot.amplitude * pivot.low):
                pullback_pens.append(pen)
        
        return pullback_pens
    
    def _check_divergence(
        self,
        pen: PenInfo,
        pivot: PivotInfo
    ) -> Tuple[bool, float]:
        """
        检查是否出现背驰
        
        背驰判断逻辑：
        1. 比较当前笔与前一笔的力度
        2. 如果当前笔力度减弱，则认为出现背驰
        
        Args:
            pen: 笔信息
            pivot: 中枢信息
        
        Returns:
            (是否背驰, 背驰强度)
        """
        # 找到前一笔
        pen_index = -1
        for i, p in enumerate(self.pens):
            if p.end.position == pen.end.position:
                pen_index = i
                break
        
        if pen_index < 1:
            return False, 0.0
        
        prev_pen = self.pens[pen_index - 1]
        
        # 计算笔的力度（长度）
        current_strength = abs(pen.length)
        prev_strength = abs(prev_pen.length)
        
        # 判断背驰
        if current_strength < prev_strength * 0.8:  # 力度减弱20%以上
            divergence_strength = 1 - current_strength / prev_strength
            return True, divergence_strength
        
        return False, 0.0
    
    def _check_not_break(self, pen: PenInfo, pivot: PivotInfo) -> bool:
        """
        检查是否不破中枢
        
        Args:
            pen: 笔信息
            pivot: 中枢信息
        
        Returns:
            是否不破中枢
        """
        if pen.direction == 'up':
            # 向上回拉，不破中枢上沿
            return pen.end.price < pivot.high
        else:
            # 向下回拉，不破中枢下沿
            return pen.end.price > pivot.low
    
    def _check_new_pivot(
        self,
        prev_pivot: PivotInfo,
        curr_pivot: PivotInfo
    ) -> bool:
        """
        检查是否形成新中枢
        
        Args:
            prev_pivot: 前一个中枢
            curr_pivot: 当前中枢
        
        Returns:
            是否形成新中枢
        """
        # 新中枢与前中枢不重叠
        return (curr_pivot.high < prev_pivot.low or
                curr_pivot.low > prev_pivot.high)
    
    def _calculate_confidence(
        self,
        divergence_strength: float,
        pivot: PivotInfo
    ) -> float:
        """
        计算买卖点置信度
        
        置信度计算逻辑：
        1. 基于背驰强度
        2. 基于中枢级别（级别越高，置信度越高）
        
        Args:
            divergence_strength: 背驰强度
            pivot: 中枢信息
        
        Returns:
            置信度（0-1）
        """
        # 基础置信度
        base_confidence = 0.5
        
        # 背驰强度贡献（最大0.3）
        divergence_contribution = min(divergence_strength * 0.5, 0.3)
        
        # 中枢级别贡献（最大0.2）
        level_contribution = min(pivot.level * 0.05, 0.2)
        
        confidence = base_confidence + divergence_contribution + level_contribution
        
        # 限制在0-1之间
        return max(0.0, min(1.0, confidence))
