"""
结果格式化器

格式化分析结果，生成文本和图表结合的友好展示。
"""
from typing import Dict, Any

from ..models import (
    PositionAnalysisResult,
    BacktestResult,
    ForecastResult,
    SkillResponse
)
from ..utils.logger import default_logger as logger


class ResultFormatter:
    """结果格式化器"""
    
    def __init__(self):
        """初始化格式化器"""
        logger.info("结果格式化器初始化完成")
    
    def format_position_result(self, result: PositionAnalysisResult) -> str:
        """
        格式化位置分析结果
        
        Args:
            result: 位置分析结果
        
        Returns:
            格式化后的文本
        """
        text = f"""
【缠论位置分析报告】

股票代码：{result.stock}
分析时间：{result.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}

【当前位置】
{result.current_position}

【趋势判断】
趋势类型：{self._get_trend_desc(result.trend_type)}
风险等级：{self._get_risk_desc(result.risk_level)}

【缠论元素统计】
- 分型数量：{len(result.fractals)}
- 笔数量：{len(result.pens)}
- 中枢数量：{len(result.pivots)}
- 买卖点数量：{len(result.buy_sell_points)}

【买卖点详情】
{self._format_buy_sell_points(result.buy_sell_points)}

【缠论概念说明】
{self._get_chanlun_concepts()}
"""
        return text.strip()
    
    def format_backtest_result(self, result: BacktestResult) -> str:
        """
        格式化回测结果
        
        Args:
            result: 回测结果
        
        Returns:
            格式化后的文本
        """
        text = f"""
【缠论回测报告】

股票代码：{result.stock}
回测区间：{result.start_date.strftime('%Y-%m-%d')} 至 {result.end_date.strftime('%Y-%m-%d')}
分析时间：{result.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}

【资金情况】
初始资金：{result.initial_capital:,.2f} 元
最终资金：{result.final_capital:,.2f} 元
总收益率：{result.total_return:.2%}
年化收益率：{result.annual_return:.2%}

【交易统计】
总交易次数：{result.total_trades}
盈利次数：{result.win_trades}
亏损次数：{result.loss_trades}
胜率：{result.win_rate:.2%}

【风险指标】
最大回撤：{result.max_drawdown:.2%}
夏普比率：{result.sharpe_ratio:.2f}

【交易明细】
{self._format_trades(result.trades[:10])}  # 只显示前10条
"""
        return text.strip()
    
    def format_forecast_result(self, result: ForecastResult) -> str:
        """
        格式化预测结果
        
        Args:
            result: 预测结果
        
        Returns:
            格式化后的文本
        """
        text = f"""
【缠论走势预测报告】

股票代码：{result.stock}
当前价格：{result.current_price:.2f}
当前趋势：{self._get_trend_desc(result.current_trend)}
分析时间：{result.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}

【未来走势推演】
{self._format_scenarios(result.scenarios)}

【风险评估】
{result.risk_assessment}

【预测置信度】
{result.confidence:.2%}

【操作建议】
{result.recommendation}

【缠论概念说明】
{self._get_chanlun_concepts()}
"""
        return text.strip()
    
    def _get_trend_desc(self, trend_type: str) -> str:
        """获取趋势描述"""
        trend_map = {
            'trend_up': '上升趋势',
            'trend_down': '下降趋势',
            'consolidation': '盘整'
        }
        return trend_map.get(trend_type, '未知')
    
    def _get_risk_desc(self, risk_level: str) -> str:
        """获取风险描述"""
        risk_map = {
            'low': '低风险',
            'medium': '中等风险',
            'high': '高风险'
        }
        return risk_map.get(risk_level, '未知')
    
    def _format_buy_sell_points(self, buy_sell_points) -> str:
        """格式化买卖点"""
        if not buy_sell_points:
            return "暂无买卖点"
        
        lines = []
        for point in buy_sell_points:
            point_type = {
                'buy1': '第一类买点',
                'buy2': '第二类买点',
                'buy3': '第三类买点',
                'sell1': '第一类卖点',
                'sell2': '第二类卖点',
                'sell3': '第三类卖点'
            }[point.type]
            
            lines.append(
                f"- {point_type}：价格={point.price:.2f}，"
                f"时间={point.datetime.strftime('%Y-%m-%d')}，"
                f"置信度={point.confidence:.2%}"
            )
        
        return '\n'.join(lines)
    
    def _format_trades(self, trades) -> str:
        """格式化交易记录"""
        if not trades:
            return "暂无交易记录"
        
        lines = []
        for trade in trades:
            lines.append(
                f"- {trade.type.upper()}：价格={trade.price:.2f}，"
                f"数量={trade.shares}，"
                f"金额={trade.amount:,.2f}，"
                f"时间={trade.datetime.strftime('%Y-%m-%d')}"
            )
        
        return '\n'.join(lines)
    
    def _format_scenarios(self, scenarios) -> str:
        """格式化预测场景"""
        if not scenarios:
            return "暂无预测场景"
        
        lines = []
        for i, scenario in enumerate(scenarios, 1):
            lines.append(f"\n场景{i}：{scenario.description}")
            lines.append(f"  概率：{scenario.probability:.2%}")
            if scenario.key_levels:
                lines.append(f"  关键价位：{', '.join(f'{x:.2f}' for x in scenario.key_levels)}")
            if scenario.signals:
                lines.append(f"  观察信号：{', '.join(scenario.signals)}")
            if scenario.target_price:
                lines.append(f"  目标价位：{scenario.target_price:.2f}")
            if scenario.stop_loss:
                lines.append(f"  止损价位：{scenario.stop_loss:.2f}")
        
        return '\n'.join(lines)
    
    def _get_chanlun_concepts(self) -> str:
        """获取缠论概念说明"""
        return """
【缠论核心概念】
1. 分型：相邻三根K线形成的顶底结构
2. 笔：连接相邻顶底分型的线段
3. 线段：由至少3笔组成的更高级别走势
4. 中枢：由至少3段线段重叠区域构成
5. 买卖点：基于背驰和中枢形成的交易信号

【买卖点说明】
- 第一类买点：走势离开中枢后向下背驰
- 第二类买点：回拉不破中枢形成的买点
- 第三类买点：新中枢形成后的回拉买点
- 卖点与买点对称
"""
