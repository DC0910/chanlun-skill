"""
缠论量化分析系统
基于缠论理论进行股票分析和选股
"""

from .core.types import Fractal, Pen, Segment, Pivot
from .core.analyzer import ChanLunAnalyzer
from .strategy.selector import StockSelector
from .backtest.backtester import Backtester

__version__ = "1.0.0"
__author__ = "ChanLun Quant Team"

__all__ = [
    "Fractal",
    "Pen", 
    "Segment",
    "Pivot",
    "ChanLunAnalyzer",
    "StockSelector",
    "Backtester"
]
