"""
命令解析器

解析用户自然语言命令，提取股票代码、分析类型等参数。
"""
import re
from typing import Optional, Dict, Any
from datetime import datetime

from ..models import StockCode, AnalysisRequest, BacktestConfig
from ..utils.exceptions import InvalidParameterError
from ..utils.logger import default_logger as logger


class CommandParser:
    """命令解析器"""
    
    # 命令模式
    PATTERNS = {
        # 位置分析：分析 000001 缠论位置
        'position': re.compile(
            r'分析\s+(?P<code>\d{6})\s*(?P<market>SH|SZ)?\s*缠论位置',
            re.IGNORECASE
        ),
        # 回测：回测 000001 2023-01-01 2023-12-31
        'backtest': re.compile(
            r'回测\s+(?P<code>\d{6})\s*(?P<market>SH|SZ)?\s+(?P<start_date>\d{4}[-/]?\d{2}[-/]?\d{2})\s+(?P<end_date>\d{4}[-/]?\d{2}[-/]?\d{2})',
            re.IGNORECASE
        ),
        # 预测：预测 000001 走势
        'forecast': re.compile(
            r'预测\s+(?P<code>\d{6})\s*(?P<market>SH|SZ)?\s*走势',
            re.IGNORECASE
        ),
        # 简化命令：分析 000001
        'simple_position': re.compile(
            r'分析\s+(?P<code>\d{6})\s*(?P<market>SH|SZ)?',
            re.IGNORECASE
        ),
    }
    
    def __init__(self):
        """初始化命令解析器"""
        logger.info("命令解析器初始化完成")
    
    def parse(self, command: str) -> Dict[str, Any]:
        """
        解析命令
        
        Args:
            command: 用户输入的命令
        
        Returns:
            解析结果字典，包含：
            - analysis_type: 分析类型（position/backtest/forecast）
            - stock: StockCode对象
            - start_date: 开始日期（可选）
            - end_date: 结束日期（可选）
        
        Raises:
            InvalidParameterError: 命令格式错误
        """
        logger.info(f"开始解析命令：{command}")
        
        # 去除首尾空格
        command = command.strip()
        
        # 尝试匹配各种命令模式
        for cmd_type, pattern in self.PATTERNS.items():
            match = pattern.search(command)
            if match:
                logger.debug(f"命令匹配成功，类型：{cmd_type}")
                return self._parse_match(cmd_type, match)
        
        # 没有匹配到任何模式
        logger.error(f"无法识别的命令格式：{command}")
        raise InvalidParameterError(
            f"无法识别的命令格式。支持的命令格式：\n"
            f"1. 分析 [股票代码] 缠论位置\n"
            f"2. 回测 [股票代码] [开始日期] [结束日期]\n"
            f"3. 预测 [股票代码] 走势",
            parameter_name='command',
            parameter_value=command
        )
    
    def _parse_match(self, cmd_type: str, match: re.Match) -> Dict[str, Any]:
        """
        解析匹配结果
        
        Args:
            cmd_type: 命令类型
            match: 正则匹配对象
        
        Returns:
            解析结果字典
        """
        groups = match.groupdict()
        
        # 解析股票代码
        stock_code = groups.get('code')
        market = groups.get('market', 'SZ')  # 默认深圳市场
        
        # 自动判断市场
        if not groups.get('market'):
            market = self._infer_market(stock_code)
        
        stock = StockCode(code=stock_code, market=market)
        
        result = {
            'stock': stock,
            'analysis_type': 'position' if cmd_type in ['position', 'simple_position'] else cmd_type
        }
        
        # 解析日期（回测命令）
        if cmd_type == 'backtest':
            start_date = self._parse_date(groups.get('start_date'))
            end_date = self._parse_date(groups.get('end_date'))
            result['start_date'] = start_date
            result['end_date'] = end_date
        
        logger.success(f"命令解析成功：{result}")
        return result
    
    def _infer_market(self, stock_code: str) -> str:
        """
        根据股票代码推断市场
        
        Args:
            stock_code: 股票代码
        
        Returns:
            市场代码（SH或SZ）
        """
        # 上海市场：600xxx, 601xxx, 603xxx, 688xxx
        if stock_code.startswith(('600', '601', '603', '688')):
            return 'SH'
        # 深圳市场：000xxx, 001xxx, 002xxx, 003xxx, 300xxx
        else:
            return 'SZ'
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串（支持YYYY-MM-DD、YYYY/MM/DD、YYYYMMDD格式）
        
        Returns:
            datetime对象
        
        Raises:
            InvalidParameterError: 日期格式错误
        """
        if not date_str:
            return None
        
        # 尝试多种日期格式
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y%m%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.error(f"无法解析日期：{date_str}")
        raise InvalidParameterError(
            f"日期格式错误，支持的格式：YYYY-MM-DD、YYYY/MM/DD、YYYYMMDD",
            parameter_name='date',
            parameter_value=date_str
        )
    
    def validate_stock_code(self, stock_code: str) -> bool:
        """
        验证股票代码格式
        
        Args:
            stock_code: 股票代码
        
        Returns:
            是否有效
        """
        if not stock_code or not stock_code.isdigit() or len(stock_code) != 6:
            return False
        return True
    
    def validate_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> bool:
        """
        验证日期范围
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            是否有效
        """
        if not start_date or not end_date:
            return False
        
        if end_date < start_date:
            return False
        
        # 不能超过当前日期
        if end_date > datetime.now():
            return False
        
        return True
    
    def get_help(self) -> str:
        """
        获取命令帮助信息
        
        Returns:
            帮助信息
        """
        return """
缠论股票分析命令帮助：

1. 位置分析
   命令格式：分析 [股票代码] 缠论位置
   示例：分析 000001 缠论位置
   说明：分析股票当前在缠论中的位置，包括中枢、买卖点等

2. 历史回测
   命令格式：回测 [股票代码] [开始日期] [结束日期]
   示例：回测 000001 2023-01-01 2023-12-31
   说明：基于缠论买卖点进行历史数据回测

3. 走势预测
   命令格式：预测 [股票代码] 走势
   示例：预测 000001 走势
   说明：结合缠论理论预测股票未来走势

注意事项：
- 股票代码为6位数字
- 市场代码可选（SH=上海，SZ=深圳），默认自动判断
- 日期格式支持：YYYY-MM-DD、YYYY/MM/DD、YYYYMMDD
"""
