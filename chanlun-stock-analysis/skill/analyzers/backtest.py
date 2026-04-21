"""
回测引擎

执行历史回测，生成回测报告。
"""
import pandas as pd
from typing import List
from datetime import datetime

from ..models import (
    StockCode,
    BacktestConfig,
    BacktestResult,
    BacktestTrade
)
from ..utils.data import get_klines
from ..utils.logger import default_logger as logger
from ..config import ConfigManager


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, config_manager: ConfigManager = None):
        """初始化回测引擎"""
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.get()
        logger.info("回测引擎初始化完成")
    
    async def run(self, config: BacktestConfig) -> BacktestResult:
        """
        执行回测
        
        Args:
            config: 回测配置
        
        Returns:
            回测结果
        """
        logger.info(f"开始回测：{config.stock}，{config.start_date} 至 {config.end_date}")
        
        # 获取历史数据
        klines = await self._get_klines(config)
        
        # 初始化回测状态
        capital = config.initial_capital
        position = 0
        trades = []
        
        # 简化实现：模拟买卖点
        # 实际应用中需要集成缠论分析
        for i in range(len(klines)):
            # 模拟买入信号（每20天买入一次）
            if i % 20 == 0 and position == 0:
                price = klines.iloc[i]['close']
                shares = int(capital * config.max_position_ratio / price)
                cost = shares * price * (1 + config.commission_rate)
                
                if cost <= capital:
                    capital -= cost
                    position = shares
                    trades.append(BacktestTrade(
                        type='buy',
                        datetime=klines.iloc[i]['datetime'],
                        price=price,
                        shares=shares,
                        amount=cost,
                        commission=shares * price * config.commission_rate,
                        reason='模拟买入'
                    ))
            
            # 模拟卖出信号（持仓10天后卖出）
            elif i % 20 == 10 and position > 0:
                price = klines.iloc[i]['close']
                revenue = position * price * (1 - config.commission_rate)
                capital += revenue
                
                trades.append(BacktestTrade(
                    type='sell',
                    datetime=klines.iloc[i]['datetime'],
                    price=price,
                    shares=position,
                    amount=revenue,
                    commission=position * price * config.commission_rate,
                    reason='模拟卖出'
                ))
                position = 0
        
        # 计算统计指标
        result = self._calculate_metrics(config, trades, capital, klines)
        
        logger.success(f"回测完成：总收益率={result.total_return:.2%}")
        return result
    
    async def _get_klines(self, config: BacktestConfig) -> pd.DataFrame:
        """获取K线数据"""
        return get_klines(
            stock_code=config.stock.code,
            market=config.stock.market,
            start_date=config.start_date.strftime('%Y-%m-%d'),
            end_date=config.end_date.strftime('%Y-%m-%d'),
            data_source=self.config.data_source.default,
            tushare_token=self.config.data_source.tushare_token
        )
    
    def _calculate_metrics(
        self,
        config: BacktestConfig,
        trades: List[BacktestTrade],
        final_capital: float,
        klines: pd.DataFrame
    ) -> BacktestResult:
        """计算回测指标"""
        total_return = (final_capital - config.initial_capital) / config.initial_capital
        
        # 计算年化收益率
        days = (config.end_date - config.start_date).days
        annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
        
        # 计算胜率
        win_trades = 0
        loss_trades = 0
        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                if sell_trade.price > buy_trade.price:
                    win_trades += 1
                else:
                    loss_trades += 1
        
        total_trades = win_trades + loss_trades
        win_rate = win_trades / total_trades if total_trades > 0 else 0
        
        # 简化计算最大回撤和夏普比率
        max_drawdown = 0.1  # 简化值
        sharpe_ratio = annual_return / 0.2 if annual_return > 0 else 0  # 简化值
        
        return BacktestResult(
            stock=config.stock,
            start_date=config.start_date,
            end_date=config.end_date,
            initial_capital=config.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annual_return=annual_return,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            trades=trades,
            total_trades=total_trades,
            win_trades=win_trades,
            loss_trades=loss_trades
        )
