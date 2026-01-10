"""提供商基类
定义所有AI提供商需要实现的接口和通用功能
"""

import abc
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ProviderConfig:
    """提供商配置数据类"""
    name: str
    enabled: bool
    provider_type: str = "text"  # 提供商类型："text" 或 "image"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    api_endpoint: Optional[str] = None  # API端点路径
    max_tokens: int = 2000
    max_output_tokens: int = 8000  # 最大输出令牌数，参考RedInk配置
    temperature: float = 0.7
    timeout: int = 30
    retry_count: int = 3
    headers: Optional[Dict[str, str]] = None
    supported_sizes: Optional[List[str]] = None  # 支持的尺寸列表
    # 参考图片支持配置
    support_reference_image: bool = False
    support_multiple_reference_images: bool = False
    reference_image_field: str = "init_image"


class BaseProvider(abc.ABC):
    """AI提供商基类"""
    
    def __init__(self, config: ProviderConfig):
        """初始化提供商
        
        Args:
            config: 提供商配置
        """
        self.config = config
        self.name = config.name
        self.enabled = config.enabled
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.model = config.model
        self.api_endpoint = config.api_endpoint
        self.max_tokens = config.max_tokens
        self.max_output_tokens = config.max_output_tokens  # 最大输出令牌数
        self.temperature = config.temperature
        self.timeout = config.timeout
        self.retry_count = config.retry_count
        self.headers = config.headers or {}
        self.supported_sizes = config.supported_sizes or []  # 支持的尺寸列表
        self.initialized = False
        
        # 参考图片支持
        self.support_reference_image = getattr(config, 'support_reference_image', False)
        self.support_multiple_reference_images = getattr(config, 'support_multiple_reference_images', False)
        self.reference_image_field = getattr(config, 'reference_image_field', 'init_image')
    
    @abc.abstractmethod
    async def initialize(self) -> bool:
        """初始化提供商
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abc.abstractmethod
    async def test_connection(self) -> bool:
        """测试提供商连接
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    def is_available(self) -> bool:
        """检查提供商是否可用
        
        Returns:
            bool: 是否可用
        """
        return self.enabled and self.initialized
    
    @staticmethod
    def _resolve_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
        """解析配置中的环境变量
        
        Args:
            config: 包含环境变量的配置
            
        Returns:
            Dict[str, Any]: 解析后的配置
        """
        import os
        import re
        resolved = {}
        
        def resolve_value(value):
            """递归解析值中的环境变量"""
            if isinstance(value, str):
                # 使用正则表达式匹配 ${VAR} 格式的环境变量
                pattern = r'\$\{([^}]+)\}'
                
                def replace_match(match):
                    env_key = match.group(1)
                    return os.environ.get(env_key, match.group(0))
                
                return re.sub(pattern, replace_match, value)
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            else:
                return value
        
        for key, value in config.items():
            resolved[key] = resolve_value(value)
        
        return resolved
    
    def get_name(self) -> str:
        """获取提供商名称
        
        Returns:
            str: 提供商名称
        """
        return self.name
    
    def get_config(self) -> ProviderConfig:
        """获取提供商配置
        
        Returns:
            ProviderConfig: 提供商配置
        """
        return self.config