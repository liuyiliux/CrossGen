"""SiliconFlow提供商实现
实现SiliconFlow API的图像生成功能
"""

from typing import Dict, Any, Optional, List
import httpx
import jsonpath_ng
from src.providers.base_provider import BaseProvider, ProviderConfig


class SiliconFlowProvider(BaseProvider):
    """SiliconFlow提供商实现"""
    
    def __init__(self, config: ProviderConfig):
        """初始化SiliconFlow提供商
        
        Args:
            config: 提供商配置
        """
        super().__init__(config)
        self.client = None
        self.image_jsonpath = "$.images[*].url"  # 默认值
        self.return_format = "url"  # 默认值
        self.size_config = {}  # 默认值
    
    async def initialize(self) -> bool:
        """初始化SiliconFlow提供商
        
        Returns:
            bool: 初始化是否成功
        """
        print(f"=== 开始初始化SiliconFlow提供商 ===")
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
            
            # 解析环境变量
            print(f"\n解析环境变量...")
            resolved_config = self._resolve_env_vars({
                "api_key": self.api_key,
                "base_url": self.base_url,
                "headers": self.headers
            })
            
            # 打印解析后的配置
            self.api_key = resolved_config["api_key"]
            # 移除base_url末尾的斜杠，避免双斜杠问题
            self.base_url = resolved_config["base_url"].rstrip("/")
            self.headers = resolved_config["headers"] or {}
            
            # 自动生成Authorization头（如果没有提供）
            if self.api_key:
                # 优先使用直接提供的API密钥生成Authorization头
                self.headers["Authorization"] = f"Bearer {self.api_key}"
                print(f"自动生成Authorization头")
            
            print(f"\n解析后的配置:")
            print(f"  API Key: {self.api_key[:10]}..." if self.api_key else "  API Key: 未设置")
            print(f"  Base URL: {self.base_url}")
            print(f"  Headers: {self.headers}")
            print(f"  支持的尺寸: {self.supported_sizes}")
            
            # 创建HTTP客户端，不设置base_url，避免自动添加斜杠
            print(f"\n创建HTTP客户端...")
            self.client = httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True  # 启用自动跟随重定向
            )
            
            print(f"HTTP客户端创建成功")
            print(f"客户端Base URL: 未设置")
            print(f"客户端Headers: {dict(self.client.headers)}")
            print(f"客户端Timeout: {self.client.timeout}")
            
            self.initialized = True
            print(f"初始化成功")
            return True
            
        except Exception as e:
            print(f"初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.initialized = False
            return False
    
    async def test_connection(self) -> bool:
        """测试SiliconFlow连接
        
        Returns:
            bool: 连接是否成功
        """
        print(f"\n=== 开始测试SiliconFlow连接 ===")
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
            # 1. 直接使用用户配置的Base URL进行图像生成测试，不拼接路径
            print(f"\n1. 直接使用配置的Base URL测试图像生成...")
            test_prompt = "测试图片生成"
            request_body = {
                "model": self.model,
                "prompt": test_prompt,
                "n": 1,
                "size": "1024x1024",
                "response_format": self.return_format
            }
            
            print(f"请求URL: {self.base_url}")
            print(f"请求方法: POST")
            print(f"请求头: {dict(self.client.headers)}")
            print(f"请求体: {request_body}")
            
            # 使用client.request方法直接发送请求，避免base_url和路径拼接问题
            response = await self.client.request(
                method="POST",
                url=self.base_url,
                json=request_body
            )
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应体: {response.text}")
            
            if response.status_code == 200:
                print("✓ 图像生成测试成功")
                print(f"=== 测试结束 ===")
                return True
        except Exception as e:
            print(f"✗ 图像生成测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"=== 测试结束，连接失败 ===")
        return False
    
    async def generate_image(self, prompt: str, platform: str, **kwargs) -> Optional[Dict[str, Any]]:
        """生成图像
        
        Args:
            prompt: 生成提示词
            platform: 平台名称
            **kwargs: 额外参数，包括参考图等
            
        Returns:
            Optional[Dict[str, Any]]: 生成结果
        """
        print(f"\n=== 开始SiliconFlow图像生成 ===")
        print(f"提供商: {self.name}")
        print(f"平台: {platform}")
        print(f"提示词: {prompt[:50]}..." if len(prompt) > 50 else f"提示词: {prompt}")
        print(f"参数: {kwargs}")
        
        if not self.is_available() or not self.client:
            print(f"提供商不可用，无法生成图像")
            return None
        
        try:
            # 获取平台尺寸配置
            platform_sizes = self.size_config.get(platform, ["1024x1024"])
            size = kwargs.get("size", platform_sizes[0])
            print(f"\n1. 构建请求参数:")
            print(f"  平台: {platform}")
            print(f"  尺寸: {size}")
            print(f"  模型: {self.model}")
            print(f"  返回格式: {kwargs.get('response_format', self.return_format)}")
            
            # 直接使用用户配置的模型，不进行回退
            model = self.model
            
            # 构建请求参数，符合SiliconFlow API规范
            request_body = {
                "model": model,
                "prompt": prompt
            }
            
            # 根据API文档，使用正确的参数名
            # 检查尺寸是否在支持列表中
            final_size = size
            if self.supported_sizes and final_size not in self.supported_sizes:
                # 如果尺寸不在支持列表中，使用默认尺寸
                if model in ["Qwen/Qwen-Image"]:
                    final_size = "1056x1584"  # Qwen-Image默认竖版尺寸
                elif model in ["Kwai-Kolors/Kolors"]:
                    final_size = "1024x1024"  # Kolors默认尺寸
                else:
                    final_size = "1024x1024"  # 默认尺寸
                print(f"  警告：尺寸 {size} 不在支持列表中，使用默认尺寸: {final_size}")
            
            if model in ["Qwen/Qwen-Image", "Kwai-Kolors/Kolors"]:
                # Qwen-Image模型使用image_size参数
                request_body["image_size"] = final_size
            else:
                request_body["size"] = final_size
            
            # 仅对Kolors模型添加batch_size参数
            if model == "Kwai-Kolors/Kolors":
                request_body["batch_size"] = kwargs.get("n", 1)
            # 对于Qwen-Image模型，n参数不适用
            elif "n" in kwargs:
                request_body["n"] = kwargs["n"]
            
            # 根据模型类型调整参数
            if model == "Qwen/Qwen-Image":
                # Qwen-Image模型使用cfg参数，不支持guidance_scale
                if kwargs.get("image_parameters"):
                    image_params = kwargs.get("image_parameters", {})
                    # 转换参数名
                    if "guidance_scale" in image_params:
                        image_params["cfg"] = image_params.pop("guidance_scale")
                    request_body.update(image_params)
            else:
                # 其他模型使用原参数
                if kwargs.get("image_parameters"):
                    request_body.update(kwargs.get("image_parameters"))
            
            # Qwen-Image模型不支持response_format参数，会直接返回URL
            if model != "Qwen/Qwen-Image" and kwargs.get("response_format"):
                request_body["response_format"] = kwargs.get("response_format", self.return_format)
            
            # 处理参考图
            reference_images = kwargs.get("reference_images", [])
            if reference_images and kwargs.get("support_reference_image", False):
                print(f"  处理参考图: {reference_images}")
                # 支持多图参考的模型使用所有参考图
                if kwargs.get("support_multiple_reference_images", False):
                    request_body[kwargs.get("reference_image_field", "init_images")] = reference_images
                # 不支持多图参考的模型只使用第一个参考图
                else:
                    request_body[kwargs.get("reference_image_field", "init_image")] = reference_images[0]
            
            print(f"  最终请求体: {request_body}")
            
            # 发送请求
            # 使用client.request方法直接发送完整URL
            print(f"\n2. 发送图像生成请求:")
            print(f"  请求URL: {self.base_url}")
            print(f"  请求方法: POST")
            print(f"  请求头: {dict(self.client.headers)}")
            print(f"  请求体: {request_body}")
            
            # 使用client.request方法直接发送请求，指定完整URL
            response = await self.client.request(
                method="POST",
                url=self.base_url,
                json=request_body
            )
            
            print(f"\n3. 处理响应:")
            print(f"  响应状态码: {response.status_code}")
            print(f"  响应头: {dict(response.headers)}")
            print(f"  响应体: {response.text}")
            
            # 直接检查HTTP状态，不进行重试
            response.raise_for_status()
            
            result = response.json()
            print(f"  解析后的响应体: {result}")
            
            # 使用JSONPath提取图像URL或Base64数据
            print(f"\n4. 提取图像数据:")
            print(f"  使用JSONPath: {self.image_jsonpath}")
            
            image_matches = jsonpath_ng.parse(self.image_jsonpath).find(result)
            print(f"  匹配结果: {image_matches}")
            
            images = [match.value for match in image_matches]
            print(f"  提取到的图像: {images}")
            
            print(f"\n5. 生成结果:")
            print(f"  成功生成 {len(images)} 张图片")
            
            return {
                "success": True,
                "images": images,
                "usage": result.get("usage", {}),
                "model": result.get("model", self.model),
                "provider": self.name,
                "seed": result.get("seed"),
                "timings": result.get("timings", {})
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
