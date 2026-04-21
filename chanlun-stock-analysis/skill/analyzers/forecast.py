"""
预测引擎

基于缠论理论预测未来走势。
"""
from typing import List

from ..models import (
    StockCode,
    AnalysisRequest,
    ForecastResult,
    ForecastScenario
)
from ..utils.logger import default_logger as logger
from ..config import ConfigManager
from .position import PositionAnalyzer


class ForecastEngine:
    """预测引擎"""
    
    def __init__(self, config_manager: ConfigManager = None):
        """初始化预测引擎"""
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.get()
        self.position_analyzer = PositionAnalyzer(config_manager)
        logger.info("预测引擎初始化完成")
    
    async def forecast(self, request: AnalysisRequest) -> ForecastResult:
        """
        预测未来走势
        
        Args:
            request: 分析请求
        
        Returns:
            预测结果
        """
        logger.info(f"开始预测走势：{request.stock}")
        
        # 1. 分析当前位置
        position_result = await self.position_analyzer.analyze(request)
        
        # 2. 判断走势类型
        trend_type = position_result.trend_type
        
        # 3. 推演未来走势
        scenarios = self._deduce_scenarios(
            position_result.pivots,
            position_result.pens,
            trend_type
        )
        
        # 4. 评估风险
        risk_assessment = self._assess_risk(scenarios, trend_type)
        
        # 5. 计算置信度
        confidence = self._calculate_confidence(scenarios)
        
        # 6. 生成操作建议
        recommendation = self._generate_recommendation(
            trend_type,
            scenarios,
            position_result.buy_sell_points
        )
        
        # 获取当前价格
        current_price = position_result.pens[-1].end.price if position_result.pens else 0
        
        result = ForecastResult(
            stock=request.stock,
            current_trend=trend_type,
            current_price=current_price,
            scenarios=scenarios,
            risk_assessment=risk_assessment,
            confidence=confidence,
            recommendation=recommendation
        )
        
        logger.success(f"预测完成：{request.stock}")
        return result
    
    def _deduce_scenarios(
        self,
        pivots,
        pens,
        trend_type: str
    ) -> List[ForecastScenario]:
        """推演未来可能的走势"""
        scenarios = []
        
        if trend_type == 'trend_up':
            scenarios.append(ForecastScenario(
                description="延续上升趋势，形成新中枢",
                probability=0.6,
                key_levels=[pens[-1].end.price * 1.1] if pens else [],
                signals=["关注是否出现背驰", "观察新中枢形成"],
                target_price=pens[-1].end.price * 1.15 if pens else None,
                stop_loss=pens[-1].end.price * 0.95 if pens else None
            ))
            scenarios.append(ForecastScenario(
                description="趋势转折，形成顶部",
                probability=0.3,
                key_levels=[pens[-1].end.price * 0.95] if pens else [],
                signals=["关注顶分型形成", "观察背驰信号"],
                target_price=None,
                stop_loss=None
            ))
            scenarios.append(ForecastScenario(
                description="进入盘整，形成新中枢",
                probability=0.1,
                key_levels=[pens[-1].end.price] if pens else [],
                signals=["观察中枢震荡"],
                target_price=None,
                stop_loss=None
            ))
        
        elif trend_type == 'trend_down':
            scenarios.append(ForecastScenario(
                description="延续下降趋势，形成新中枢",
                probability=0.6,
                key_levels=[pens[-1].end.price * 0.9] if pens else [],
                signals=["关注是否出现背驰", "观察新中枢形成"],
                target_price=pens[-1].end.price * 0.85 if pens else None,
                stop_loss=pens[-1].end.price * 1.05 if pens else None
            ))
            scenarios.append(ForecastScenario(
                description="趋势转折，形成底部",
                probability=0.3,
                key_levels=[pens[-1].end.price * 1.05] if pens else [],
                signals=["关注底分型形成", "观察背驰信号"],
                target_price=None,
                stop_loss=None
            ))
            scenarios.append(ForecastScenario(
                description="进入盘整，形成新中枢",
                probability=0.1,
                key_levels=[pens[-1].end.price] if pens else [],
                signals=["观察中枢震荡"],
                target_price=None,
                stop_loss=None
            ))
        
        else:  # consolidation
            scenarios.append(ForecastScenario(
                description="继续盘整，中枢延伸",
                probability=0.5,
                key_levels=[],
                signals=["观察中枢突破方向"],
                target_price=None,
                stop_loss=None
            ))
            scenarios.append(ForecastScenario(
                description="向上突破中枢",
                probability=0.25,
                key_levels=[],
                signals=["关注向上突破力度"],
                target_price=None,
                stop_loss=None
            ))
            scenarios.append(ForecastScenario(
                description="向下突破中枢",
                probability=0.25,
                key_levels=[],
                signals=["关注向下突破力度"],
                target_price=None,
                stop_loss=None
            ))
        
        return scenarios
    
    def _assess_risk(self, scenarios: List[ForecastScenario], trend_type: str) -> str:
        """评估风险"""
        if trend_type == 'consolidation':
            return "当前处于盘整状态，风险中等，建议观望或轻仓操作"
        
        # 找到最高概率场景
        max_prob_scenario = max(scenarios, key=lambda x: x.probability)
        
        if max_prob_scenario.probability > 0.7:
            return f"趋势明确，风险较低，{max_prob_scenario.description}"
        elif max_prob_scenario.probability > 0.5:
            return f"趋势较明确，风险中等，{max_prob_scenario.description}"
        else:
            return "趋势不明确，风险较高，建议谨慎操作"
    
    def _calculate_confidence(self, scenarios: List[ForecastScenario]) -> float:
        """计算预测置信度"""
        if not scenarios:
            return 0.0
        
        # 基于最高概率场景计算置信度
        max_prob = max(s.probability for s in scenarios)
        return max_prob
    
    def _generate_recommendation(
        self,
        trend_type: str,
        scenarios: List[ForecastScenario],
        buy_sell_points
    ) -> str:
        """生成操作建议"""
        # 检查最近的买卖点
        if buy_sell_points:
            recent_point = buy_sell_points[-1]
            if recent_point.is_buy and recent_point.confidence > 0.7:
                return f"建议买入，{recent_point.description}"
            elif not recent_point.is_buy and recent_point.confidence > 0.7:
                return f"建议卖出，{recent_point.description}"
        
        # 基于趋势类型给出建议
        if trend_type == 'trend_up':
            return "上升趋势中，建议持有或逢低买入"
        elif trend_type == 'trend_down':
            return "下降趋势中，建议观望或减仓"
        else:
            return "盘整状态中，建议观望，等待趋势明确"
