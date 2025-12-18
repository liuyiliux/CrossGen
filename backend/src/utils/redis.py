"""Redis连接管理模块
提供Redis客户端的单例管理和连接池配置
"""

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
            print("Redis已禁用，不初始化连接")
            self._redis_client = None
            return
            
        try:
            # 创建Redis客户端
            self._redis_client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                health_check_interval=30,  # 30秒健康检查一次
                socket_keepalive=True,
                socket_keepalive_options={
                    'tcp_keepidle': 60,
                    'tcp_keepintvl': 10,
                    'tcp_keepcnt': 3
                }
            )
            
            # 测试连接
            self._redis_client.ping()
            print(f"Redis连接成功: {settings.REDIS_URL}")
            
        except Exception as e:
            print(f"Redis连接失败: {str(e)}")
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
            print(f"Redis ping失败: {str(e)}")
            return False
    
    def close(self) -> None:
        """关闭Redis连接
        """
        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None
            print("Redis连接已关闭")
    
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