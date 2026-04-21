"""
配置管理模块

实现配置加载和管理功能，支持YAML配置文件和环境变量。
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from pydantic import BaseSettings, Field

from .utils.exceptions import ConfigError
from .utils.logger import default_logger as logger


class DataSourceConfig(BaseSettings):
    """数据源配置"""
    default: str = Field('akshare', description="默认数据源")
    tushare_token: str = Field('', description="Tushare API Token")
    
    class Config:
        env_prefix = 'CHANLUN_'


class AnalysisConfig(BaseSettings):
    """分析参数配置"""
    fractal_confirm_bars: int = Field(3, description="分型确认K线数")
    pen_min_length: float = Field(0.0, description="笔的最小长度")
    pen_allow_contain: bool = Field(True, description="是否允许包含关系")
    segment_min_pens: int = Field(3, description="线段的最小笔数")
    pivot_min_segments: int = Field(3, description="中枢的最小线段数")
    pivot_levels: list = Field(['5', '30', 'D'], description="中枢级别")
    
    class Config:
        env_prefix = 'CHANLUN_'


class BacktestConfig(BaseSettings):
    """回测参数配置"""
    initial_capital: float = Field(100000, description="初始资金")
    commission_rate: float = Field(0.0003, description="手续费率")
    slippage: float = Field(0.0, description="滑点")
    max_position_ratio: float = Field(0.95, description="最大持仓比例")
    
    class Config:
        env_prefix = 'CHANLUN_'


class VisualizationConfig(BaseSettings):
    """可视化配置"""
    figure_size: tuple = Field((16, 9), description="图表大小")
    dpi: int = Field(100, description="DPI")
    show_grid: bool = Field(True, description="是否显示网格")
    kline_up_color: str = Field('red', description="上涨K线颜色")
    kline_down_color: str = Field('green', description="下跌K线颜色")
    pivot_color: str = Field('blue', description="中枢颜色")
    buy_point_color: str = Field('red', description="买点颜色")
    sell_point_color: str = Field('green', description="卖点颜色")
    
    class Config:
        env_prefix = 'CHANLUN_'


class LoggingConfig(BaseSettings):
    """日志配置"""
    level: str = Field('INFO', description="日志级别")
    file: str = Field('logs/chanlun_skill.log', description="日志文件路径")
    rotation: str = Field('10 MB', description="日志文件大小限制")
    retention: str = Field('7 days', description="日志保留时间")
    
    class Config:
        env_prefix = 'CHANLUN_'


class CacheConfig(BaseSettings):
    """缓存配置"""
    enabled: bool = Field(True, description="是否启用缓存")
    type: str = Field('memory', description="缓存类型")
    ttl: int = Field(3600, description="缓存过期时间（秒）")
    redis_host: str = Field('localhost', description="Redis主机")
    redis_port: int = Field(6379, description="Redis端口")
    redis_db: int = Field(0, description="Redis数据库")
    redis_password: str = Field('', description="Redis密码")
    
    class Config:
        env_prefix = 'CHANLUN_'


class SkillConfig(BaseSettings):
    """Skill完整配置"""
    data_source: DataSourceConfig = Field(default_factory=DataSourceConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    
    class Config:
        env_prefix = 'CHANLUN_'


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file or self._find_config_file()
        self._config: Optional[SkillConfig] = None
        logger.info(f"配置管理器初始化，配置文件：{self.config_file}")
    
    def _find_config_file(self) -> str:
        """
        查找配置文件
        
        Returns:
            配置文件路径
        """
        # 查找顺序：
        # 1. 当前目录下的config.yaml
        # 2. skill目录下的config.yaml
        # 3. 默认配置
        
        search_paths = [
            Path.cwd() / 'config.yaml',
            Path(__file__).parent / 'config.yaml',
            Path(__file__).parent.parent / 'skill' / 'config.yaml',
        ]
        
        for path in search_paths:
            if path.exists():
                return str(path)
        
        logger.warning("未找到配置文件，使用默认配置")
        return None
    
    def load(self) -> SkillConfig:
        """
        加载配置
        
        Returns:
            配置对象
        """
        if self._config is not None:
            return self._config
        
        # 从YAML文件加载
        config_dict = {}
        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_dict = yaml.safe_load(f) or {}
                logger.info(f"成功加载配置文件：{self.config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败：{str(e)}")
                raise ConfigError(f"加载配置文件失败：{str(e)}")
        
        # 构建配置对象
        try:
            self._config = self._build_config(config_dict)
            logger.success("配置加载完成")
            return self._config
        except Exception as e:
            logger.error(f"构建配置对象失败：{str(e)}")
            raise ConfigError(f"构建配置对象失败：{str(e)}")
    
    def _build_config(self, config_dict: Dict[str, Any]) -> SkillConfig:
        """
        构建配置对象
        
        Args:
            config_dict: 配置字典
        
        Returns:
            配置对象
        """
        # 数据源配置
        data_source_dict = config_dict.get('data_source', {})
        data_source = DataSourceConfig(
            default=data_source_dict.get('default', 'akshare'),
            tushare_token=data_source_dict.get('tushare', {}).get('token', '')
        )
        
        # 分析参数配置
        analysis_dict = config_dict.get('analysis', {})
        fractal_dict = analysis_dict.get('fractal', {})
        pen_dict = analysis_dict.get('pen', {})
        segment_dict = analysis_dict.get('segment', {})
        pivot_dict = analysis_dict.get('pivot', {})
        
        analysis = AnalysisConfig(
            fractal_confirm_bars=fractal_dict.get('confirm_bars', 3),
            pen_min_length=pen_dict.get('min_length', 0.0),
            pen_allow_contain=pen_dict.get('allow_contain', True),
            segment_min_pens=segment_dict.get('min_pens', 3),
            pivot_min_segments=pivot_dict.get('min_segments', 3),
            pivot_levels=pivot_dict.get('levels', ['5', '30', 'D'])
        )
        
        # 回测配置
        backtest_dict = config_dict.get('backtest', {})
        backtest = BacktestConfig(
            initial_capital=backtest_dict.get('initial_capital', 100000),
            commission_rate=backtest_dict.get('commission_rate', 0.0003),
            slippage=backtest_dict.get('slippage', 0.0),
            max_position_ratio=backtest_dict.get('max_position_ratio', 0.95)
        )
        
        # 可视化配置
        visualization_dict = config_dict.get('visualization', {})
        visualization = VisualizationConfig(
            figure_size=tuple(visualization_dict.get('figure_size', [16, 9])),
            dpi=visualization_dict.get('dpi', 100),
            show_grid=visualization_dict.get('show_grid', True),
            kline_up_color=visualization_dict.get('kline_colors', {}).get('up', 'red'),
            kline_down_color=visualization_dict.get('kline_colors', {}).get('down', 'green'),
            pivot_color=visualization_dict.get('pivot_color', 'blue'),
            buy_point_color=visualization_dict.get('buy_point_color', 'red'),
            sell_point_color=visualization_dict.get('sell_point_color', 'green')
        )
        
        # 日志配置
        logging_dict = config_dict.get('logging', {})
        logging_config = LoggingConfig(
            level=logging_dict.get('level', 'INFO'),
            file=logging_dict.get('file', 'logs/chanlun_skill.log'),
            rotation=logging_dict.get('rotation', '10 MB'),
            retention=logging_dict.get('retention', '7 days')
        )
        
        # 缓存配置
        cache_dict = config_dict.get('cache', {})
        redis_dict = cache_dict.get('redis', {})
        cache = CacheConfig(
            enabled=cache_dict.get('enabled', True),
            type=cache_dict.get('type', 'memory'),
            ttl=cache_dict.get('ttl', 3600),
            redis_host=redis_dict.get('host', 'localhost'),
            redis_port=redis_dict.get('port', 6379),
            redis_db=redis_dict.get('db', 0),
            redis_password=redis_dict.get('password', '')
        )
        
        return SkillConfig(
            data_source=data_source,
            analysis=analysis,
            backtest=backtest,
            visualization=visualization,
            logging=logging_config,
            cache=cache
        )
    
    def get(self) -> SkillConfig:
        """
        获取配置
        
        Returns:
            配置对象
        """
        if self._config is None:
            return self.load()
        return self._config
    
    def reload(self) -> SkillConfig:
        """
        重新加载配置
        
        Returns:
            配置对象
        """
        self._config = None
        return self.load()
    
    def update(self, key: str, value: Any) -> None:
        """
        更新配置项
        
        Args:
            key: 配置键（支持点号分隔，如 'data_source.default'）
            value: 配置值
        """
        config = self.get()
        
        # 解析键路径
        keys = key.split('.')
        obj = config
        
        for k in keys[:-1]:
            obj = getattr(obj, k)
        
        setattr(obj, keys[-1], value)
        logger.info(f"配置已更新：{key} = {value}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典
        
        Returns:
            配置字典
        """
        config = self.get()
        return config.dict()
