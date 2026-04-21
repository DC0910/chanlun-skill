"""
缠论股票分析 Skill 主类

实现OpenClaw Skill接口，集成所有模块。
"""
from typing import Dict, Any
import asyncio

from .models import (
    StockCode,
    AnalysisRequest,
    BacktestConfig,
    SkillResponse
)
from .config import ConfigManager
from .parsers.command import CommandParser
from .analyzers.position import PositionAnalyzer
from .analyzers.backtest import BacktestEngine
from .analyzers.forecast import ForecastEngine
from .formatters.result import ResultFormatter
from .utils.exceptions import ChanLunSkillError, InvalidParameterError
from .utils.logger import default_logger as logger


class ChanLunStockAnalysisSkill:
    """
    缠论股票分析Skill
    
    基于缠论理论分析股票位置、回测历史数据、预测未来走势。
    """
    
    def __init__(self):
        """初始化Skill"""
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化各模块
        self.command_parser = CommandParser()
        self.position_analyzer = PositionAnalyzer(self.config_manager)
        self.backtest_engine = BacktestEngine(self.config_manager)
        self.forecast_engine = ForecastEngine(self.config_manager)
        self.result_formatter = ResultFormatter()
        
        logger.info("缠论股票分析Skill初始化完成")
    
    @classmethod
    def metadata(cls) -> Dict[str, Any]:
        """
        返回Skill元数据
        
        Returns:
            元数据字典
        """
        return {
            'name': 'chanlun-stock-analysis',
            'version': '1.0.0',
            'description': '基于缠论理论的股票分析Skill',
            'author': 'ChanLun Team',
            'commands': [
                {
                    'name': 'position',
                    'description': '分析股票缠论位置',
                    'usage': '分析 [股票代码] 缠论位置',
                    'example': '分析 000001 缠论位置'
                },
                {
                    'name': 'backtest',
                    'description': '回测股票历史数据',
                    'usage': '回测 [股票代码] [开始日期] [结束日期]',
                    'example': '回测 000001 2023-01-01 2023-12-31'
                },
                {
                    'name': 'forecast',
                    'description': '预测股票未来走势',
                    'usage': '预测 [股票代码] 走势',
                    'example': '预测 000001 走势'
                }
            ],
            'permissions': [
                'data.read'  # 只需要数据读取权限
            ],
            'tags': ['stock', 'analysis', 'chanlun', 'trading']
        }
    
    async def execute(self, context: Dict[str, Any]) -> SkillResponse:
        """
        执行Skill主逻辑
        
        Args:
            context: 执行上下文，包含command等参数
        
        Returns:
            Skill响应
        """
        try:
            # 获取命令
            command = context.get('command', '')
            if not command:
                return SkillResponse.error_response(
                    "命令不能为空",
                    "请提供有效的命令，例如：分析 000001 缠论位置"
                )
            
            logger.info(f"开始执行命令：{command}")
            
            # 解析命令
            parsed = self.command_parser.parse(command)
            
            # 根据分析类型执行相应分析
            analysis_type = parsed['analysis_type']
            
            if analysis_type == 'position':
                result = await self._execute_position_analysis(parsed)
            elif analysis_type == 'backtest':
                result = await self._execute_backtest(parsed)
            elif analysis_type == 'forecast':
                result = await self._execute_forecast(parsed)
            else:
                return SkillResponse.error_response(
                    f"不支持的分析类型：{analysis_type}",
                    "支持的分析类型：position、backtest、forecast"
                )
            
            logger.success(f"命令执行成功：{command}")
            return result
        
        except InvalidParameterError as e:
            logger.error(f"参数错误：{str(e)}")
            return SkillResponse.error_response(
                f"参数错误：{str(e)}",
                str(e)
            )
        
        except ChanLunSkillError as e:
            logger.error(f"Skill执行错误：{str(e)}")
            return SkillResponse.error_response(
                f"执行失败：{str(e)}",
                str(e)
            )
        
        except Exception as e:
            logger.error(f"未知错误：{str(e)}")
            return SkillResponse.error_response(
                f"执行失败：{str(e)}",
                str(e)
            )
    
    async def validate(self, context: Dict[str, Any]) -> bool:
        """
        验证输入参数
        
        Args:
            context: 执行上下文
        
        Returns:
            是否有效
        """
        command = context.get('command', '')
        if not command:
            return False
        
        try:
            self.command_parser.parse(command)
            return True
        except Exception:
            return False
    
    async def _execute_position_analysis(self, parsed: Dict[str, Any]) -> SkillResponse:
        """执行位置分析"""
        # 构建分析请求
        request = AnalysisRequest(
            stock=parsed['stock'],
            start_date=parsed.get('start_date'),
            end_date=parsed.get('end_date'),
            analysis_type='position'
        )
        
        # 执行分析
        result = await self.position_analyzer.analyze(request)
        
        # 格式化结果
        formatted_text = self.result_formatter.format_position_result(result)
        
        return SkillResponse.success_response(
            "位置分析完成",
            {
                'text': formatted_text,
                'result': result.dict()
            }
        )
    
    async def _execute_backtest(self, parsed: Dict[str, Any]) -> SkillResponse:
        """执行回测"""
        # 构建回测配置
        config = BacktestConfig(
            stock=parsed['stock'],
            start_date=parsed['start_date'],
            end_date=parsed['end_date'],
            initial_capital=self.config_manager.get().backtest.initial_capital,
            commission_rate=self.config_manager.get().backtest.commission_rate,
            slippage=self.config_manager.get().backtest.slippage
        )
        
        # 执行回测
        result = await self.backtest_engine.run(config)
        
        # 格式化结果
        formatted_text = self.result_formatter.format_backtest_result(result)
        
        return SkillResponse.success_response(
            "回测完成",
            {
                'text': formatted_text,
                'result': result.dict()
            }
        )
    
    async def _execute_forecast(self, parsed: Dict[str, Any]) -> SkillResponse:
        """执行预测"""
        # 构建分析请求
        request = AnalysisRequest(
            stock=parsed['stock'],
            start_date=parsed.get('start_date'),
            end_date=parsed.get('end_date'),
            analysis_type='forecast'
        )
        
        # 执行预测
        result = await self.forecast_engine.forecast(request)
        
        # 格式化结果
        formatted_text = self.result_formatter.format_forecast_result(result)
        
        return SkillResponse.success_response(
            "预测完成",
            {
                'text': formatted_text,
                'result': result.dict()
            }
        )
    
    def get_help(self) -> str:
        """
        获取帮助信息
        
        Returns:
            帮助信息
        """
        return self.command_parser.get_help()


# 用于OpenClaw注册的入口函数
def create_skill():
    """创建Skill实例"""
    return ChanLunStockAnalysisSkill()
