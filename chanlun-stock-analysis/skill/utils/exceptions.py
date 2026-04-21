"""
缠论股票分析异常类

定义所有自定义异常类，提供清晰的错误信息。
"""


class ChanLunSkillError(Exception):
    """缠论Skill基础异常"""
    pass


class DataFetchError(ChanLunSkillError):
    """数据获取异常"""
    
    def __init__(self, message: str, stock_code: str = None):
        self.stock_code = stock_code
        super().__init__(message)


class AnalysisError(ChanLunSkillError):
    """分析异常"""
    
    def __init__(self, message: str, analysis_type: str = None):
        self.analysis_type = analysis_type
        super().__init__(message)


class InvalidParameterError(ChanLunSkillError):
    """参数无效异常"""
    
    def __init__(self, message: str, parameter_name: str = None, parameter_value: any = None):
        self.parameter_name = parameter_name
        self.parameter_value = parameter_value
        super().__init__(message)


class BacktestError(ChanLunSkillError):
    """回测异常"""
    
    def __init__(self, message: str, stock_code: str = None):
        self.stock_code = stock_code
        super().__init__(message)


class ConfigError(ChanLunSkillError):
    """配置异常"""
    
    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(message)


class CacheError(ChanLunSkillError):
    """缓存异常"""
    pass


class VisualizationError(ChanLunSkillError):
    """可视化异常"""
    pass
