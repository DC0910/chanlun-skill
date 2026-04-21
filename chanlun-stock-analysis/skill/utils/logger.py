"""
日志配置工具

使用loguru配置日志系统。
"""
import sys
from pathlib import Path
from loguru import logger


def get_logger(
    log_file: str = "logs/chanlun_skill.log",
    level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "7 days"
):
    """
    获取配置好的logger实例
    
    Args:
        log_file: 日志文件路径
        level: 日志级别
        rotation: 日志文件轮转大小
        retention: 日志保留时间
    
    Returns:
        logger实例
    """
    # 移除默认handler
    logger.remove()
    
    # 添加控制台handler
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 添加文件handler
    logger.add(
        log_file,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=rotation,
        retention=retention,
        encoding='utf-8'
    )
    
    return logger


# 创建默认logger实例
default_logger = get_logger()
