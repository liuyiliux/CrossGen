"""提供商管理器
管理和选择不同的AI提供商
"""

from typing import Dict, Any, Optional, List
from src.providers.base_provider import BaseProvider, ProviderConfig
from src.providers.openai_provider import OpenAIProvider
from src.providers.siliconflow_provider import SiliconFlowProvider
from src.providers.gemini_provider import GeminiProvider
from src.services.config_service import ConfigService


class ProviderManager:
    """提供商管理器"""
    
    def __init__(self):
        """初始化提供商管理器"""
        self.text_providers: Dict[str, BaseProvider] = {}
        self.image_providers: Dict[str, BaseProvider] = {}
        self.available_text_providers: List[str] = []
        self.available_image_providers: List[str] = []
        self.config_service = ConfigService()
        self.text_platform_mapping = {}
        self.image_platform_mapping = {}
        self.text_loaded = False
        self.image_loaded = False
    
    async def load_text_providers(self, force_reload: bool = False) -> bool:
        """加载文本提供商配置
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            bool: 加载是否成功
        """
        try:
            # 如果已经加载过且不强制重新加载，直接返回
            if self.text_loaded and not force_reload:
                return True
                
            # 获取文本提供商配置
            print("开始加载文本提供商配置...")
            # 清除配置缓存，确保获取最新配置
            self.config_service._text_providers_cache = None
            text_config = self.config_service.get_text_providers()
            providers_config = text_config.get("providers", {})
            
            # 获取平台映射配置
            self.text_platform_mapping = text_config.get("platform_mapping", {})
            print(f"加载到 {len(providers_config)} 个文本提供商配置")
            
            # 清空现有提供商
            self.text_providers.clear()
            self.available_text_providers.clear()
            
            # 注册提供商
            for name, config in providers_config.items():
                print(f"正在注册文本提供商: {name}")
                if await self.register_text_provider(name, config):
                    print(f"文本提供商 {name} 注册成功")
                else:
                    print(f"文本提供商 {name} 注册失败")
            
            self.text_loaded = True
            print(f"文本提供商加载完成，可用提供商数量: {len(self.available_text_providers)}")
            return True
            
        except Exception as e:
            print(f"加载文本提供商配置失败: {str(e)}")
            return False
    
    async def load_image_providers(self, force_reload: bool = False) -> bool:
        """加载图像提供商配置
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            bool: 加载是否成功
        """
        try:
            # 如果已经加载过且不强制重新加载，直接返回
            if self.image_loaded and not force_reload:
                return True
                
            # 获取图像提供商配置
            print("开始加载图像提供商配置...")
            # 清除配置缓存，确保获取最新配置
            self.config_service._image_providers_cache = None
            image_config = self.config_service.get_image_providers()
            providers_config = image_config.get("providers", {})
            
            # 获取平台映射配置
            self.image_platform_mapping = image_config.get("platform_mapping", {})
            print(f"加载到 {len(providers_config)} 个图像提供商配置")
            
            # 清空现有提供商
            self.image_providers.clear()
            self.available_image_providers.clear()
            
            # 注册提供商
            for name, config in providers_config.items():
                print(f"正在注册图像提供商: {name}")
                if await self.register_image_provider(name, config):
                    print(f"图像提供商 {name} 注册成功")
                else:
                    print(f"图像提供商 {name} 注册失败")
            
            self.image_loaded = True
            print(f"图像提供商加载完成，可用提供商数量: {len(self.available_image_providers)}")
            return True
            
        except Exception as e:
            print(f"加载图像提供商配置失败: {str(e)}")
            return False
    
    async def load_providers(self, force_reload: bool = False) -> bool:
        """加载所有提供商配置
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            bool: 加载是否成功
        """
        text_result = await self.load_text_providers(force_reload)
        image_result = await self.load_image_providers(force_reload)
        return text_result and image_result
    
    async def register_text_provider(self, name: str, config: Dict[str, Any]) -> bool:
        """注册文本提供商
        
        Args:
            name: 提供商名称
            config: 提供商配置
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # 创建提供商配置对象
            provider_config = ProviderConfig(
                name=name,
                enabled=config.get("enabled", False),
                provider_type="text",  # 设置为文本提供商
                api_key=config.get("api_key"),
                base_url=config.get("base_url"),
                model=config.get("model"),
                api_endpoint=config.get("api_endpoint"),
                max_tokens=config.get("max_tokens", 2000),
                max_output_tokens=config.get("max_output_tokens", 8000),
                temperature=config.get("temperature", 0.7),
                timeout=config.get("timeout", 30),
                retry_count=config.get("retry_count", 3),
                headers=config.get("headers")
            )
            
            # 根据类型创建提供商实例
            provider_type = config.get("type", "")
            provider = None
            
            if provider_type == "openai":
                provider = OpenAIProvider(provider_config)
            elif provider_type == "siliconflow":
                provider = SiliconFlowProvider(provider_config)
            elif provider_type == "gemini":
                provider = GeminiProvider(provider_config)
            else:
                print(f"不支持的文本提供商类型: {provider_type}")
                return False
            
            # 初始化提供商
            if await provider.initialize():
                self.text_providers[name] = provider
                self.available_text_providers.append(name)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"注册文本提供商 {name} 失败: {str(e)}")
            return False
    
    async def register_image_provider(self, name: str, config: Dict[str, Any]) -> bool:
        """注册图像提供商
        
        Args:
            name: 提供商名称
            config: 提供商配置
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # 初始化提供商
            provider = None
            
            # 根据类型创建提供商实例
            provider_type = config.get("type", "")
            
            # 提取参考图相关配置
            reference_config = {
                "support_reference_image": config.get("support_reference_image", False),
                "reference_image_field": config.get("reference_image_field", "image_urls"),
                "support_multiple_reference_images": config.get("support_multiple_reference_images", False),
                "image_model": config.get("image_model", config.get("model")),
                "image_quality": config.get("image_quality", "standard"),
                "image_style": config.get("image_style", "vivid"),
                "size_config": config.get("size_config", {}),
                "image_parameters": config.get("image_parameters", {})
            }
            
            if provider_type == "openai":
                # 解析supported_sizes字段
                supported_sizes = config.get("supported_sizes", [])
                if isinstance(supported_sizes, str):
                    # 如果是字符串，尝试解析为JSON
                    import json
                    try:
                        supported_sizes = json.loads(supported_sizes)
                    except json.JSONDecodeError:
                        print(f"  警告：supported_sizes字段解析失败，使用默认值")
                        supported_sizes = []
                
                provider_config = ProviderConfig(
                    name=name,
                    enabled=config.get("enabled", False),
                    provider_type="image",  # 设置为图像提供商
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url"),
                    model=config.get("model"),
                    api_endpoint=config.get("api_endpoint"),
                    timeout=config.get("timeout", 30),
                    retry_count=config.get("retry_count", 3),
                    headers=config.get("headers"),
                    supported_sizes=supported_sizes  # 添加支持的尺寸
                )
                # 添加响应配置
                provider_config.response_config = config.get("response_config", {})
                provider = OpenAIProvider(provider_config)
            elif provider_type == "siliconflow":
                # 为SiliconFlow创建ProviderConfig对象
                # 解析supported_sizes字段
                supported_sizes = config.get("supported_sizes", [])
                if isinstance(supported_sizes, str):
                    # 如果是字符串，尝试解析为JSON
                    import json
                    try:
                        supported_sizes = json.loads(supported_sizes)
                    except json.JSONDecodeError:
                        print(f"  警告：supported_sizes字段解析失败，使用默认值")
                        supported_sizes = []
                
                provider_config = ProviderConfig(
                    name=name,
                    enabled=config.get("enabled", True),
                    provider_type="image",  # 设置为图像提供商
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url"),
                    model=config.get("model"),
                    api_endpoint=config.get("api_endpoint"),
                    timeout=config.get("timeout", 30),
                    retry_count=config.get("retry_count", 3),
                    headers=config.get("headers"),
                    supported_sizes=supported_sizes  # 添加支持的尺寸
                )
                # 创建SiliconFlowProvider实例，传递ProviderConfig对象
                provider = SiliconFlowProvider(provider_config)
                # 设置SiliconFlow特有属性
                provider.image_jsonpath = config.get("image_jsonpath", "$.images[*].url")
                provider.return_format = config.get("return_format", "url")
                provider.size_config = config.get("size_config", {})
            elif provider_type == "gemini":
                # 解析supported_sizes字段
                supported_sizes = config.get("supported_sizes", [])
                if isinstance(supported_sizes, str):
                    # 如果是字符串，尝试解析为JSON
                    import json
                    try:
                        supported_sizes = json.loads(supported_sizes)
                    except json.JSONDecodeError:
                        print(f"  警告：supported_sizes字段解析失败，使用默认值")
                        supported_sizes = []
                
                provider_config = ProviderConfig(
                    name=name,
                    enabled=config.get("enabled", True),
                    provider_type="image",  # 设置为图像提供商
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url"),
                    model=config.get("model"),
                    api_endpoint=config.get("api_endpoint"),
                    timeout=config.get("timeout", 30),
                    retry_count=config.get("retry_count", 3),
                    headers=config.get("headers"),
                    supported_sizes=supported_sizes  # 添加支持的尺寸
                )
                # 添加响应配置
                provider_config.response_config = config.get("response_config", {})
                provider = GeminiProvider(provider_config)
            elif provider_type == "generic":
                # 解析supported_sizes字段
                supported_sizes = config.get("supported_sizes", [])
                if isinstance(supported_sizes, str):
                    # 如果是字符串，尝试解析为JSON
                    import json
                    try:
                        supported_sizes = json.loads(supported_sizes)
                    except json.JSONDecodeError:
                        print(f"  警告：supported_sizes字段解析失败，使用默认值")
                        supported_sizes = []
                
                provider_config = ProviderConfig(
                    name=name,
                    enabled=config.get("enabled", True),
                    provider_type="image",  # 显式设置为图像提供商
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url"),
                    model=config.get("model"),
                    timeout=config.get("timeout", 30),
                    retry_count=config.get("retry_count", 3),
                    headers=config.get("headers"),
                    supported_sizes=supported_sizes  # 添加支持的尺寸
                )
                
                # 添加通用配置
                provider_config.request_config = config.get("request_config", {})
                provider_config.response_config = config.get("response_config", {})
                provider_config.size_config = config.get("size_config", {})
                
                # 导入并创建GenericImageProvider实例
                from src.providers.generic_image_provider import GenericImageProvider
                provider = GenericImageProvider(provider_config)
            else:
                print(f"不支持的图像提供商类型: {provider_type}")
                return False
            
            # 初始化提供商
            if await provider.initialize():
                # 保存提供商和其参考图配置
                self.image_providers[name] = {
                    "provider": provider,
                    "reference_config": reference_config
                }
                self.available_image_providers.append(name)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"注册图像提供商 {name} 失败: {str(e)}")
            return False
    
    def get_text_provider(self, name: str) -> Optional[BaseProvider]:
        """获取文本提供商实例
        
        Args:
            name: 提供商名称
            
        Returns:
            Optional[BaseProvider]: 提供商实例
        """
        return self.text_providers.get(name)
    
    def get_image_provider(self, name: str) -> Optional[Dict[str, Any]]:
        """获取图像提供商实例
        
        Args:
            name: 提供商名称
            
        Returns:
            Optional[Dict[str, Any]]: 包含提供商实例和参考图配置的字典
        """
        return self.image_providers.get(name)
    
    def get_available_text_providers(self) -> List[str]:
        """获取可用的文本提供商列表
        
        Returns:
            List[str]: 可用文本提供商列表
        """
        return [name for name, provider in self.text_providers.items() if provider.is_available()]
    
    def get_available_image_providers(self) -> List[str]:
        """获取可用的图像提供商列表
        
        Returns:
            List[str]: 可用图像提供商列表
        """
        return [name for name, provider_info in self.image_providers.items() if provider_info["provider"].is_available()]
    
    def get_text_provider_for_platform(self, platform: str) -> Optional[BaseProvider]:
        """根据平台获取合适的文本提供商
        
        Args:
            platform: 平台名称
            
        Returns:
            Optional[BaseProvider]: 提供商实例
        """
        # 获取平台映射
        mapping = self.text_platform_mapping.get(platform, {})
        primary_provider = mapping.get("primary_provider")
        fallback_provider = mapping.get("fallback_provider")
        
        # 尝试使用主提供商
        if primary_provider and primary_provider in self.text_providers:
            provider = self.text_providers[primary_provider]
            if provider.is_available():
                return provider
        
        # 尝试使用备用提供商
        if fallback_provider and fallback_provider in self.text_providers:
            provider = self.text_providers[fallback_provider]
            if provider.is_available():
                return provider
        
        # 如果没有映射或映射的提供商不可用，使用第一个可用的提供商
        available = self.get_available_text_providers()
        if available:
            return self.text_providers[available[0]]
        
        return None
    
    def get_image_provider_for_platform(self, platform: str) -> Optional[Dict[str, Any]]:
        """根据平台获取合适的图像提供商
        
        Args:
            platform: 平台名称
            
        Returns:
            Optional[Dict[str, Any]]: 包含提供商实例和参考图配置的字典
        """
        # 获取平台映射
        mapping = self.image_platform_mapping.get(platform, {})
        primary_provider = mapping.get("primary_provider")
        fallback_provider = mapping.get("fallback_provider")
        
        # 尝试使用主提供商
        if primary_provider and primary_provider in self.image_providers:
            provider_info = self.image_providers[primary_provider]
            if provider_info["provider"].is_available():
                return provider_info
        
        # 尝试使用备用提供商
        if fallback_provider and fallback_provider in self.image_providers:
            provider_info = self.image_providers[fallback_provider]
            if provider_info["provider"].is_available():
                return provider_info
        
        # 如果没有映射或映射的提供商不可用，使用第一个可用的提供商
        available = self.get_available_image_providers()
        if available:
            return self.image_providers[available[0]]
        
        return None
    
    async def generate_text_for_platform(self, platform: str, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """为指定平台生成文本
        
        Args:
            platform: 平台名称
            prompt: 生成提示词
            **kwargs: 额外参数
            
        Returns:
            Optional[Dict[str, Any]]: 生成结果
        """
        # 获取合适的提供商
        provider = self.get_text_provider_for_platform(platform)
        if not provider:
            print(f"没有可用的文本提供商为平台 {platform} 生成内容")
            return None
        
        # 调用提供商生成文本
        try:
            result = await provider.generate_text(prompt, **kwargs)
            return result
        except Exception as e:
            print(f"调用文本提供商 {provider.name} 失败: {str(e)}")
            return None
    
    async def generate_image_for_platform(self, platform: str, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """为指定平台生成图像
        
        Args:
            platform: 平台名称
            prompt: 生成提示词
            **kwargs: 额外参数
            
        Returns:
            Optional[Dict[str, Any]]: 生成结果
        """
        # 获取合适的提供商
        provider_info = self.get_image_provider_for_platform(platform)
        if not provider_info:
            print(f"没有可用的图像提供商为平台 {platform} 生成内容")
            return None
        
        provider = provider_info["provider"]
        reference_config = provider_info["reference_config"]
        
        # 合并参考图配置和额外参数
        merged_kwargs = {
            **reference_config,
            **kwargs
        }
        
        # 调用提供商生成图像
        try:
            result = await provider.generate_image(prompt, platform, **merged_kwargs)
            return result
        except Exception as e:
            print(f"调用图像提供商 {provider.name} 失败: {str(e)}")
            return None
    
    async def test_all_text_providers(self) -> Dict[str, bool]:
        """测试所有文本提供商连接
        
        Returns:
            Dict[str, bool]: 测试结果
        """
        results = {}
        for name, provider in self.text_providers.items():
            results[name] = await provider.test_connection()
        return results
    
    async def test_all_image_providers(self) -> Dict[str, bool]:
        """测试所有图像提供商连接
        
        Returns:
            Dict[str, bool]: 测试结果
        """
        results = {}
        for name, provider_info in self.image_providers.items():
            results[name] = await provider_info["provider"].test_connection()
        return results
    
    async def test_all_providers(self) -> Dict[str, bool]:
        """测试所有提供商连接
        
        Returns:
            Dict[str, bool]: 测试结果
        """
        results = {}
        results.update(await self.test_all_text_providers())
        results.update(await self.test_all_image_providers())
        return results
    
    async def close_all(self) -> None:
        """关闭所有提供商连接"""
        # 关闭文本提供商
        for provider in self.text_providers.values():
            if hasattr(provider, "close"):
                await provider.close()
        self.text_providers.clear()
        self.available_text_providers.clear()
        
        # 关闭图像提供商
        for provider_info in self.image_providers.values():
            provider = provider_info["provider"]
            if hasattr(provider, "close"):
                await provider.close()
        self.image_providers.clear()
        self.available_image_providers.clear()
    
    def is_text_provider_available(self, name: str) -> bool:
        """检查文本提供商是否可用
        
        Args:
            name: 提供商名称
            
        Returns:
            bool: 是否可用
        """
        provider = self.text_providers.get(name)
        return provider is not None and provider.is_available()
    
    def is_image_provider_available(self, name: str) -> bool:
        """检查图像提供商是否可用
        
        Args:
            name: 提供商名称
            
        Returns:
            bool: 是否可用
        """
        provider_info = self.image_providers.get(name)
        return provider_info is not None and provider_info["provider"].is_available()
    
    def is_provider_available(self, name: str) -> bool:
        """检查提供商是否可用（兼容旧接口）
        
        Args:
            name: 提供商名称
            
        Returns:
            bool: 是否可用
        """
        return self.is_text_provider_available(name) or self.is_image_provider_available(name)
    
    async def test_text_provider_connection(self, config: Dict[str, Any]) -> bool:
        """测试文本提供商连接（使用临时配置）
        
        Args:
            config: 提供商配置
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 解析环境变量
            from src.providers.base_provider import BaseProvider
            resolved_config = BaseProvider._resolve_env_vars(config)
            
            # 创建临时提供商配置
            provider_config = ProviderConfig(
                name=resolved_config.get("name", "temp_text_provider"),
                enabled=True,
                api_key=resolved_config.get("api_key"),
                base_url=resolved_config.get("base_url"),
                model=resolved_config.get("model"),
                api_endpoint=resolved_config.get("api_endpoint"),
                max_tokens=resolved_config.get("max_tokens", 2000),
                max_output_tokens=resolved_config.get("max_output_tokens", 8000),
                temperature=resolved_config.get("temperature", 0.7),
                timeout=resolved_config.get("timeout", 30),
                retry_count=resolved_config.get("retry_count", 3),
                headers=resolved_config.get("headers")
            )
            
            # 根据类型创建提供商实例
            provider_type = resolved_config.get("type", "")
            provider = None
            
            if provider_type == "openai":
                provider = OpenAIProvider(provider_config)
            elif provider_type == "siliconflow":
                provider = SiliconFlowProvider(provider_config)
            elif provider_type == "gemini":
                provider = GeminiProvider(provider_config)
            else:
                raise ValueError(f"不支持的文本提供商类型: {provider_type}")
            
            # 初始化并测试连接
            if await provider.initialize():
                return await provider.test_connection()
            return False
        except Exception as e:
            print(f"测试文本提供商连接失败: {str(e)}")
            return False
    
    async def test_image_provider_connection(self, config: Dict[str, Any]) -> bool:
        """测试图像提供商连接（使用临时配置）
        
        Args:
            config: 提供商配置
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 解析环境变量
            from src.providers.base_provider import BaseProvider
            resolved_config = BaseProvider._resolve_env_vars(config)
            
            # 创建临时提供商实例
            provider = None
            
            # 根据类型创建提供商实例
            provider_type = resolved_config.get("type", "")
            
            if provider_type == "openai":
                provider_config = ProviderConfig(
                    name=resolved_config.get("name", "temp_image_provider"),
                    enabled=True,
                    provider_type="image",  # 显式设置为图像提供商
                    api_key=resolved_config.get("api_key"),
                    base_url=resolved_config.get("base_url"),
                    model=resolved_config.get("model"),
                    api_endpoint=resolved_config.get("api_endpoint"),
                    timeout=resolved_config.get("timeout", 30),
                    retry_count=resolved_config.get("retry_count", 3),
                    headers=resolved_config.get("headers")
                )
                provider = OpenAIProvider(provider_config)
            elif provider_type == "siliconflow":
                # 为SiliconFlow创建配置
                provider_config = ProviderConfig(
                    name=resolved_config.get("name", "temp_image_provider"),
                    enabled=True,
                    provider_type="image",  # 显式设置为图像提供商
                    api_key=resolved_config.get("api_key"),
                    base_url=resolved_config.get("base_url"),
                    model=resolved_config.get("model"),
                    timeout=resolved_config.get("timeout", 30),
                    retry_count=resolved_config.get("retry_count", 3),
                    headers=resolved_config.get("headers")
                )
                provider = SiliconFlowProvider(provider_config)
                # 设置SiliconFlow特定的配置
                provider.image_jsonpath = resolved_config.get("image_jsonpath", "$.images[*].url")
                provider.return_format = resolved_config.get("return_format", "url")
                provider.size_config = resolved_config.get("size_config", {})
            elif provider_type == "gemini":
                provider_config = ProviderConfig(
                    name=resolved_config.get("name", "temp_image_provider"),
                    enabled=True,
                    provider_type="image",  # 显式设置为图像提供商
                    api_key=resolved_config.get("api_key"),
                    base_url=resolved_config.get("base_url"),
                    model=resolved_config.get("model"),
                    api_endpoint=resolved_config.get("api_endpoint"),
                    timeout=resolved_config.get("timeout", 30),
                    retry_count=resolved_config.get("retry_count", 3),
                    headers=resolved_config.get("headers")
                )
                provider = GeminiProvider(provider_config)
            elif provider_type == "generic":
                # 为通用图像提供商创建配置
                provider_config = ProviderConfig(
                    name=resolved_config.get("name", "temp_image_provider"),
                    enabled=True,
                    provider_type="image",  # 显式设置为图像提供商
                    api_key=config.get("api_key"),  # 直接使用原始配置中的api_key，不使用解析后的
                    base_url=resolved_config.get("base_url"),
                    model=resolved_config.get("model"),
                    timeout=resolved_config.get("timeout", 30),
                    retry_count=resolved_config.get("retry_count", 3),
                    headers=resolved_config.get("headers")
                )
                # 添加通用配置
                provider_config.request_config = resolved_config.get("request_config", {})
                provider_config.response_config = resolved_config.get("response_config", {})
                provider_config.size_config = resolved_config.get("size_config", {})
                provider_config.supported_sizes = resolved_config.get("supported_sizes", [])
                
                # 导入GenericImageProvider
                from src.providers.generic_image_provider import GenericImageProvider
                provider = GenericImageProvider(provider_config)
            else:
                raise ValueError(f"不支持的图像提供商类型: {provider_type}")
            
            # 初始化并测试连接
            if await provider.initialize():
                return await provider.test_connection()
            return False
        except Exception as e:
            print(f"测试图像提供商连接失败: {str(e)}")
            return False