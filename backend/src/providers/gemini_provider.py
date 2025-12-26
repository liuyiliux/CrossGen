"""Gemini提供商实现
实现Gemini API的图像生成功能
"""

from typing import Dict, Any, Optional, List
import httpx
from src.providers.base_provider import BaseProvider, ProviderConfig


class GeminiProvider(BaseProvider):
    """Gemini提供商实现"""
    
    def __init__(self, config: ProviderConfig):
        """初始化Gemini提供商
        
        Args:
            config: 提供商配置
        """
        super().__init__(config)
        self.client = None
        # 从原始配置中获取size_config，而不是从ProviderConfig对象
        self.size_config = {}
    
    async def initialize(self) -> bool:
        """初始化Gemini提供商
        
        Returns:
            bool: 初始化是否成功
        """
        print(f"\n=== 开始初始化Gemini提供商 ===")
        print(f"提供商名称: {self.name}")
        print(f"是否启用: {self.enabled}")
        
        if not self.enabled:
            print(f"提供商已禁用，跳过初始化")
            return False
        
        try:
            # 打印初始配置
            print(f"初始配置:")
            print(f"  API Key: {self.api_key[:10]}..." if self.api_key else "  API Key: 未设置")
            print(f"  Base URL: {self.base_url}")
            print(f"  Headers: {self.headers}")
            print(f"  Timeout: {self.timeout}秒")
            
            # 解析环境变量
            print(f"\n1. 解析环境变量...")
            resolved_config = self._resolve_env_vars({
                "api_key": self.api_key,
                "base_url": self.base_url,
                "headers": self.headers
            })
            
            # 更新配置
            self.api_key = resolved_config["api_key"]
            self.base_url = resolved_config["base_url"].rstrip("/")  # 移除末尾斜杠
            self.headers = resolved_config["headers"] or {}
            
            # 自动生成Authorization头
            if self.api_key:
                self.headers["Authorization"] = f"Bearer {self.api_key}"
                print(f"  API Key: {self.api_key[:10]}...")
                print(f"  自动生成Authorization头")
            
            # 打印解析后的配置
            print(f"\n2. 解析后的配置:")
            print(f"  API Key: {self.api_key[:10]}..." if self.api_key else "  API Key: 未设置")
            print(f"  Base URL: {self.base_url}")
            print(f"  Headers: {self.headers}")
            print(f"  Timeout: {self.timeout}秒")
            print(f"  支持的尺寸: {self.supported_sizes}")
            
            # 创建HTTP客户端
            print(f"\n3. 创建HTTP客户端...")
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            print(f"客户端配置:")
            print(f"  Base URL: {self.client.base_url}")
            print(f"  Headers: {dict(self.client.headers)}")
            print(f"  Timeout: {self.client.timeout}")
            
            self.initialized = True
            print(f"\n=== 初始化成功 ===")
            return True
            
        except Exception as e:
            print(f"\n=== 初始化失败 ===")
            print(f"错误信息: {str(e)}")
            import traceback
            traceback.print_exc()
            self.initialized = False
            return False
    
    async def test_connection(self) -> bool:
        """测试Gemini连接
        
        Returns:
            bool: 连接是否成功
        """
        print(f"\n=== 开始测试Gemini连接 ===")
        print(f"提供商: {self.name}")
        print(f"类型: {type(self).__name__}")
        print(f"模型: {self.model}")
        print(f"基础URL: {self.base_url}")
        print(f"超时: {self.timeout}秒")
        
        if not self.initialized or not self.client:
            print(f"提供商尚未初始化，尝试初始化...")
            if not await self.initialize():
                print(f"初始化失败，连接测试失败")
                return False
        
        # 打印实际使用的HTTP客户端配置
        print(f"实际使用的Headers: {dict(self.client.headers)}")
        print(f"实际使用的Base URL: {self.client.base_url}")
        
        try:
            # 1. 首先尝试使用/models端点测试（Gemini接口）
            print(f"\n1. 尝试使用/models端点测试...")
            models_url = f"/models"
            full_url = f"{self.base_url}{models_url}"
            
            print(f"请求URL: {full_url}")
            print(f"请求方法: GET")
            print(f"请求头: {dict(self.client.headers)}")
            
            response = await self.client.get(f"{models_url}")
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✓ /models端点测试成功")
                print(f"=== 测试结束 ===")
                return True
        except Exception as e:
            print(f"✗ 使用/models端点测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        try:
            # 2. 如果/models端点失败，尝试使用简单的生成内容请求测试
            print(f"\n2. 尝试使用生成内容请求测试...")
            test_prompt = "测试连接"
            request_body = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": test_prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 10
                }
            }
            
            endpoint = f"/models/{self.model}:generateContent"
            full_url = f"{self.base_url}{endpoint}"
            
            print(f"请求URL: {full_url}")
            print(f"请求方法: POST")
            print(f"请求头: {dict(self.client.headers)}")
            print(f"请求体: {request_body}")
            
            response = await self.client.post(f"{endpoint}", json=request_body)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                print("✓ 生成内容请求测试成功")
                print(f"=== 测试结束 ===")
                return True
        except Exception as e:
            print(f"✗ 使用生成内容请求测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"=== 测试结束，连接失败 ===")
        return False
    
    async def generate_text(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """生成文本
        
        Args:
            prompt: 生成提示词
            **kwargs: 额外参数
            
        Returns:
            Optional[Dict[str, Any]]: 生成结果
        """
        if not self.is_available() or not self.client:
            return None
        
        try:
            # 构建请求参数
            request_body = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            # 发送请求，使用配置的API端点或默认值
            endpoint = self.api_endpoint or f"/models/{self.model}:generateContent"
            response = await self.client.post(endpoint, json=request_body)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "text": result["candidates"][0]["content"]["parts"][0]["text"],
                "usage": result.get("usageMetadata", {}),
                "model": result.get("model", self.model),
                "provider": self.name
            }
            
        except Exception as e:
            print(f"Gemini生成文本失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.name
            }
    
    async def generate_image(self, prompt: str, platform: str, **kwargs) -> Optional[Dict[str, Any]]:
        """生成图像
        
        Args:
            prompt: 生成提示词
            platform: 平台名称
            **kwargs: 额外参数，包括参考图等
            
        Returns:
            Optional[Dict[str, Any]]: 生成结果
        """
        print(f"\n=== 开始Gemini图像生成 ===")
        print(f"提供商: {self.name}")
        print(f"平台: {platform}")
        print(f"提示词: {prompt[:50]}..." if len(prompt) > 50 else f"提示词: {prompt}")
        print(f"参数: {kwargs}")
        
        if not self.is_available() or not self.client:
            print(f"提供商不可用，无法生成图像")
            return None
        
        try:
            # 获取平台尺寸配置
            platform_sizes = kwargs.get("size_config", {}).get(platform, ["1024x1024"])
            size = kwargs.get("size", platform_sizes[0])
            print(f"\n1. 构建请求参数:")
            print(f"  平台: {platform}")
            print(f"  尺寸: {size}")
            print(f"  模型: {self.model}")
            print(f"  响应MIME类型: image/png")
            print(f"  纵横比: {size.replace('x', ':')}")
            
            # 构建请求参数
            request_body = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "image/png",
                    "aspectRatio": size.replace("x", ":"),
                    "quality": "high"
                }
            }
            
            # 处理参考图
            reference_images = kwargs.get("reference_images", [])
            if reference_images and kwargs.get("support_reference_image", False):
                print(f"  处理参考图: {len(reference_images)}张")
                # 支持多图参考的模型使用所有参考图
                if kwargs.get("support_multiple_reference_images", False):
                    for i, img in enumerate(reference_images):
                        request_body["contents"][0]["parts"].append({
                            "inlineData": {
                                "mimeType": "image/jpeg",
                                "data": img[:20] + "..." + img[-20:] if len(img) > 40 else img
                            }
                        })
                        print(f"    参考图{i+1}: {img[:20]}..." if len(img) > 40 else f"    参考图{i+1}: {img}")
                # 不支持多图参考的模型只使用第一个参考图
                else:
                    request_body["contents"][0]["parts"].append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": reference_images[0]
                        }
                    })
                    print(f"    参考图: {reference_images[0][:20]}..." if len(reference_images[0]) > 40 else f"    参考图: {reference_images[0]}")
            
            # 发送请求
            # 统一使用配置的model字段
            endpoint = f"/models/{self.model}:generateContent"
            full_url = f"{self.base_url}{endpoint}"
            
            print(f"\n2. 发送图像生成请求:")
            print(f"  请求URL: {full_url}")
            print(f"  请求方法: POST")
            print(f"  请求头: {dict(self.client.headers)}")
            print(f"  请求体: {request_body}")
            
            response = await self.client.post(f"{endpoint}", json=request_body)
            
            print(f"\n3. 处理响应:")
            print(f"  响应状态码: {response.status_code}")
            print(f"  响应头: {dict(response.headers)}")
            
            # 尝试解析响应体
            response_text = response.text
            try:
                response_json = response.json()
                print(f"  响应体: {response_json}")
            except:
                print(f"  响应体: {response_text}")
            
            response.raise_for_status()
            
            result = response.json()
            
            # 提取图像数据
            images = []
            if result.get("candidates"):
                for candidate in result["candidates"]:
                    if candidate.get("content") and candidate["content"].get("parts"):
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part:
                                images.append(part["inlineData"]["data"])
            
            print(f"\n4. 生成结果:")
            print(f"  成功生成 {len(images)} 张图片")
            print(f"  模型: {result.get('model', self.model)}")
            print(f"  使用率: {result.get('usageMetadata', {})}")
            
            return {
                "success": True,
                "images": images,
                "usage": result.get("usageMetadata", {}),
                "model": result.get("model", self.model),
                "provider": self.name
            }
            
        except httpx.HTTPStatusError as e:
            print(f"\n5. 图像生成失败 - HTTP错误:")
            print(f"  状态码: {e.response.status_code}")
            print(f"  错误响应: {e.response.text}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"HTTP错误 {e.response.status_code}: {e.response.text}",
                "provider": self.name
            }
        except Exception as e:
            print(f"\n5. 图像生成失败 - 其他错误:")
            print(f"  错误类型: {type(e).__name__}")
            print(f"  错误信息: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "provider": self.name
            }
    
    async def close(self) -> None:
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()
            self.client = None
            self.initialized = False
    
    def __del__(self):
        """析构函数，确保客户端关闭"""
        if hasattr(self, 'client') and self.client:
            import asyncio
            try:
                asyncio.create_task(self.close())
            except:
                pass
