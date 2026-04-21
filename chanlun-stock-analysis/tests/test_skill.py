"""
缠论股票分析 Skill 测试
"""
import pytest
from datetime import datetime

from skill.models import StockCode, AnalysisRequest, BacktestConfig
from skill.parsers.command import CommandParser
from skill.config import ConfigManager


def test_stock_code():
    """测试股票代码模型"""
    stock = StockCode(code='000001', market='SZ')
    assert stock.code == '000001'
    assert stock.market == 'SZ'
    assert str(stock) == 'SZ000001'


def test_stock_code_validation():
    """测试股票代码验证"""
    with pytest.raises(ValueError):
        StockCode(code='123', market='SZ')  # 不是6位数字
    
    with pytest.raises(ValueError):
        StockCode(code='abcdef', market='SZ')  # 不是数字


def test_analysis_request():
    """测试分析请求模型"""
    stock = StockCode(code='000001', market='SZ')
    request = AnalysisRequest(
        stock=stock,
        analysis_type='position'
    )
    assert request.stock.code == '000001'
    assert request.analysis_type == 'position'


def test_backtest_config():
    """测试回测配置模型"""
    stock = StockCode(code='000001', market='SZ')
    config = BacktestConfig(
        stock=stock,
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31),
        initial_capital=100000
    )
    assert config.initial_capital == 100000
    assert config.commission_rate == 0.0003


def test_command_parser():
    """测试命令解析器"""
    parser = CommandParser()
    
    # 测试位置分析命令
    result = parser.parse('分析 000001 缠论位置')
    assert result['analysis_type'] == 'position'
    assert result['stock'].code == '000001'
    
    # 测试回测命令
    result = parser.parse('回测 000001 2023-01-01 2023-12-31')
    assert result['analysis_type'] == 'backtest'
    assert result['stock'].code == '000001'
    
    # 测试预测命令
    result = parser.parse('预测 000001 走势')
    assert result['analysis_type'] == 'forecast'
    assert result['stock'].code == '000001'


def test_config_manager():
    """测试配置管理器"""
    manager = ConfigManager()
    config = manager.get()
    
    assert config.data_source.default in ['tushare', 'akshare']
    assert config.backtest.initial_capital > 0
    assert config.cache.ttl > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
