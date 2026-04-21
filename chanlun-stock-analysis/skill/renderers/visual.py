"""
可视化渲染器

生成K线图、中枢、买卖点等可视化图表。
"""
import pandas as pd
from typing import List, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64

from ..models import (
    FractalInfo,
    PenInfo,
    PivotInfo,
    BuySellPoint
)
from ..utils.logger import default_logger as logger
from ..config import ConfigManager


class VisualRenderer:
    """可视化渲染器"""
    
    def __init__(self, config_manager: ConfigManager = None):
        """初始化渲染器"""
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.get()
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        logger.info("可视化渲染器初始化完成")
    
    def render(
        self,
        klines: pd.DataFrame,
        fractals: List[FractalInfo] = None,
        pens: List[PenInfo] = None,
        pivots: List[PivotInfo] = None,
        buy_sell_points: List[BuySellPoint] = None,
        output_format: str = 'base64'
    ) -> Optional[str]:
        """
        渲染K线图
        
        Args:
            klines: K线数据
            fractals: 分型列表
            pens: 笔列表
            pivots: 中枢列表
            buy_sell_points: 买卖点列表
            output_format: 输出格式（base64/png/pdf）
        
        Returns:
            图像数据（base64编码或文件路径）
        """
        logger.info("开始渲染K线图")
        
        # 创建图表
        fig, ax = plt.subplots(
            figsize=self.config.visualization.figure_size,
            dpi=self.config.visualization.dpi
        )
        
        # 绘制K线
        self._draw_klines(ax, klines)
        
        # 绘制分型
        if fractals:
            self._draw_fractals(ax, fractals)
        
        # 绘制笔
        if pens:
            self._draw_pens(ax, pens)
        
        # 绘制中枢
        if pivots:
            self._draw_pivots(ax, pivots)
        
        # 绘制买卖点
        if buy_sell_points:
            self._draw_buy_sell_points(ax, buy_sell_points)
        
        # 设置图表属性
        ax.set_title('缠论分析图', fontsize=16, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价格', fontsize=12)
        ax.grid(self.config.visualization.show_grid)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # 导出图像
        if output_format == 'base64':
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=self.config.visualization.dpi)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            logger.success("K线图渲染完成（base64）")
            return image_base64
        else:
            output_file = f'chanlun_chart.{output_format}'
            plt.savefig(output_file, dpi=self.config.visualization.dpi)
            plt.close()
            logger.success(f"K线图渲染完成（{output_file}）")
            return output_file
    
    def _draw_klines(self, ax, klines: pd.DataFrame):
        """绘制K线"""
        up_color = self.config.visualization.kline_up_color
        down_color = self.config.visualization.kline_down_color
        
        for i, row in klines.iterrows():
            # 判断涨跌
            color = up_color if row['close'] >= row['open'] else down_color
            
            # 绘制实体
            ax.bar(
                row['datetime'],
                abs(row['close'] - row['open']),
                bottom=min(row['open'], row['close']),
                width=0.8,
                color=color,
                alpha=0.8
            )
            
            # 绘制上下影线
            ax.plot(
                [row['datetime'], row['datetime']],
                [row['low'], min(row['open'], row['close'])],
                color=color,
                linewidth=1
            )
            ax.plot(
                [row['datetime'], row['datetime']],
                [max(row['open'], row['close']), row['high']],
                color=color,
                linewidth=1
            )
    
    def _draw_fractals(self, ax, fractals: List[FractalInfo]):
        """绘制分型"""
        for fractal in fractals:
            marker = '^' if fractal.type == 'top' else 'v'
            color = 'red' if fractal.type == 'top' else 'green'
            ax.scatter(
                fractal.datetime,
                fractal.price,
                marker=marker,
                s=100,
                color=color,
                zorder=5
            )
    
    def _draw_pens(self, ax, pens: List[PenInfo]):
        """绘制笔"""
        for pen in pens:
            color = 'red' if pen.direction == 'up' else 'green'
            ax.plot(
                [pen.start.datetime, pen.end.datetime],
                [pen.start.price, pen.end.price],
                color=color,
                linewidth=2,
                alpha=0.6
            )
    
    def _draw_pivots(self, ax, pivots: List[PivotInfo]):
        """绘制中枢"""
        for pivot in pivots:
            # 绘制中枢矩形
            ax.axhspan(
                pivot.low,
                pivot.high,
                alpha=0.2,
                color=self.config.visualization.pivot_color,
                label=f'中枢{pivot.level}'
            )
    
    def _draw_buy_sell_points(self, ax, buy_sell_points: List[BuySellPoint]):
        """绘制买卖点"""
        for point in buy_sell_points:
            if point.is_buy:
                color = self.config.visualization.buy_point_color
                marker = '^'
                offset = -5
            else:
                color = self.config.visualization.sell_point_color
                marker = 'v'
                offset = 5
            
            ax.scatter(
                point.datetime,
                point.price,
                marker=marker,
                s=200,
                color=color,
                zorder=6
            )
            
            # 添加标注
            ax.annotate(
                point.type,
                xy=(point.datetime, point.price),
                xytext=(0, offset),
                textcoords='offset points',
                ha='center',
                fontsize=8,
                color=color
            )
