"""Redis连接管理模块
提供Redis客户端的单例管理和连接池配置
"""

import logging
import redis
from typing import Optional
from src.utils.config import settings


class RedisManager:
    """Redis连接管理器
    提供单例模式的Redis客户端
    """
    
    _instance: Optional['RedisManager'] = None
    _redis_client: Optional[redis.Redis] = None
    
    def __new__(cls):
        """创建单例实例
        
        Returns:
            RedisManager: 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化Redis连接
        
        Raises:
            redis.RedisError: Redis连接失败时抛出
        """
        # 检查Redis是否启用
        if not settings.REDIS_ENABLED:
            logging.info("Redis已禁用，不初始化连接")
            self._redis_client = None
            return
        
        max_retries = 3
        retry_interval = 1
        
        for attempt in range(max_retries):
            try:
                # 创建Redis客户端，优化连接池配置
                # 简化Redis连接参数，只保留必要参数
                # 避免redis-py 5.0.1不支持的参数导致类型转换错误
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    max_connections=50
                )
                
                # 测试连接
                self._redis_client.ping()
                logging.info(f"Redis连接成功: {settings.REDIS_URL}")
                return
                
            except Exception as e:
                logging.error(f"Redis连接失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_interval)
                else:
                    logging.error("Redis连接重试次数耗尽，无法连接")
                    self._redis_client = None
    
    def get_client(self) -> Optional[redis.Redis]:
        """获取Redis客户端实例
        
        Returns:
            Optional[redis.Redis]: Redis客户端实例
        """
        if self._redis_client is None:
            self._initialize()
        return self._redis_client
    
    def ping(self) -> bool:
        """测试Redis连接
        
        Returns:
            bool: 连接是否正常
        """
        # 如果Redis已禁用，直接返回True
        if not settings.REDIS_ENABLED:
            return True
            
        try:
            client = self.get_client()
            if client:
                return client.ping()
            return False
        except Exception as e:
            logging.error(f"Redis ping失败: {str(e)}")
            return False
    
    def close(self) -> None:
        """关闭Redis连接
        """
        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None
            logging.info("Redis连接已关闭")
    
    def get_status(self) -> str:
        """获取Redis连接状态
        
        Returns:
            str: 连接状态
        """
        # 如果Redis已禁用，返回disabled
        if not settings.REDIS_ENABLED:
            return "disabled"
            
        if self.ping():
            return "connected"
        return "disconnected"


# 创建全局Redis管理器实例
redis_manager = RedisManager()