"""
缓存管理器

实现基于TTL的内存缓存。
"""
import time
from typing import Any, Optional, Dict
from hashlib import md5
import json

from .exceptions import CacheError
from .logger import default_logger as logger


class DataCache:
    """数据缓存管理器"""
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        """
        初始化缓存管理器
        
        Args:
            ttl: 缓存过期时间（秒）
            max_size: 最大缓存数量
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"缓存管理器初始化完成，TTL={ttl}秒，最大容量={max_size}")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        生成缓存键
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            缓存键
        """
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return md5(key_str.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
        
        Returns:
            缓存数据，如果不存在或已过期则返回None
        """
        if key not in self._cache:
            return None
        
        cache_item = self._cache[key]
        
        # 检查是否过期
        if time.time() - cache_item['timestamp'] > self.ttl:
            logger.debug(f"缓存过期，删除key: {key}")
            del self._cache[key]
            return None
        
        logger.debug(f"缓存命中，key: {key}")
        return cache_item['data']
    
    def set(self, key: str, data: Any) -> None:
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            data: 缓存数据
        """
        # 检查缓存容量
        if len(self._cache) >= self.max_size:
            self._cleanup()
        
        self._cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.debug(f"缓存设置成功，key: {key}")
    
    def delete(self, key: str) -> bool:
        """
        删除缓存数据
        
        Args:
            key: 缓存键
        
        Returns:
            是否删除成功
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"缓存删除成功，key: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        logger.info("缓存已清空")
    
    def _cleanup(self) -> None:
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if current_time - item['timestamp'] > self.ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        logger.info(f"清理过期缓存，删除{len(expired_keys)}个")
        
        # 如果清理后仍然超过最大容量，删除最旧的缓存
        if len(self._cache) >= self.max_size:
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            delete_count = len(self._cache) - self.max_size + 100
            for key, _ in sorted_items[:delete_count]:
                del self._cache[key]
            logger.info(f"删除最旧缓存{delete_count}个")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        current_time = time.time()
        valid_count = sum(
            1 for item in self._cache.values()
            if current_time - item['timestamp'] <= self.ttl
        )
        
        return {
            'total_count': len(self._cache),
            'valid_count': valid_count,
            'expired_count': len(self._cache) - valid_count,
            'max_size': self.max_size,
            'ttl': self.ttl
        }
    
    def cache_decorator(self, func):
        """
        缓存装饰器
        
        Args:
            func: 被装饰的函数
        
        Returns:
            装饰后的函数
        """
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = self._generate_key(func.__name__, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = self.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            self.set(cache_key, result)
            
            return result
        
        return wrapper
