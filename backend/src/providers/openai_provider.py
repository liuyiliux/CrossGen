"""OpenAI提供商实现
实现OpenAI API的文本生成功能
"""

import logging
from typing import Dict, Any, Optional, List
import httpx
import json
import jsonpath_ng
from src.providers.base_provider import BaseProvider, ProviderConfig

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """OpenAI提供商实现"""
    
    def __init__(self, config: ProviderConfig):
        """初始化OpenAI提供商
        
        Args:
            config: 提供商配置
        """
        super().__init__(config)
        self.provider_type = config.provider_type  # 添加提供商类型属性
        self.client = None
        # 响应配置，支持JSONPath提取图像，与通用提供商保持一致
        self.response_config = getattr(config, 'response_config', {
            'images_path': '$.data[*].url',
            'error_path': '$.error.message',
            'response_format': 'url'
        })
    
    async def initialize(self) -> bool:
        """初始化OpenAI提供商
        
        Returns:
            bool: 初始化是否成功
        """
        logger.info(f"\n=== 开始初始化OpenAI提供商 ===")
        logger.info(f"提供商名称: {self.name}")
        logger.info(f"是否启用: {self.enabled}")
        
        if not self.enabled:
            logger.info(f"提供商已禁用，跳过初始化")
            return False
        
        try:
            # 打印初始配置
            logger.info(f"初始配置:")
            logger.info(f"  API Key: {self.api_key[:10]}..." if self.api_key else "  API Key: 未设置")
            logger.info(f"  Base URL: {self.base_url}")
            logger.info(f"  Headers: {self.headers}")
            logger.info(f"  Timeout: {self.timeout}秒")
            
            # 解析环境变量
            logger.info(f"\n1. 解析环境变量...")
            resolved_config = self._resolve_env_vars({
                "api_key": self.api_key,
                "base_url": self.base_url,
                "headers": self.headers
            })
            
            # 更新配置
            self.api_key = resolved_config["api_key"]
            # 移除base_url末尾的斜杠，避免双斜杠问题
            self.base_url = resolved_config["base_url"].rstrip("/")
            
            # 自动生成Authorization头（如果没有提供）
            self.headers = resolved_config["headers"] or {}
            if self.api_key:
                # 优先使用直接提供的API密钥生成Authorization头
                self.headers["Authorization"] = f"Bearer {self.api_key}"
                logger.info(f"自动生成Authorization头")
            
            # 打印解析后的配置
            logger.info(f"\n2. 解析后的配置:")
            logger.info(f"  API Key: {self.api_key[:10]}..." if self.api_key else "  API Key: 未设置")
            logger.info(f"  Base URL: {self.base_url}")
            logger.info(f"  Headers: {self.headers}")
            logger.info(f"  Timeout: {self.timeout}秒")
            logger.info(f"  支持的尺寸: {self.supported_sizes}")
            
            # 创建HTTP客户端
            logger.info(f"\n3. 创建HTTP客户端...")
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            logger.info(f"客户端配置:")
            logger.info(f"  Base URL: {self.client.base_url}")
            logger.info(f"  Headers: {dict(self.client.headers)}")
            logger.info(f"  Timeout: {self.client.timeout}")
            
            self.initialized = True
            logger.info(f"\n=== 初始化成功 ===")
            return True
            
        except Exception as e:
            logger.error(f"\n=== 初始化失败 ===")
            logger.error(f"错误信息: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.initialized = False
            return False
    
    async def test_connection(self) -> bool:
        """测试OpenAI连接
        
        Returns:
            bool: 连接是否成功
        """
        if not self.initialized or not self.client:
            if not await self.initialize():
                return False
        
        logger.info(f"\n=== 开始测试OpenAI连接 ===")
        logger.info(f"提供商: {self.name}")
        logger.info(f"类型: {type(self).__name__}")
        logger.info(f"提供商类型: {self.provider_type}")
        logger.info(f"模型: {self.model}")
        logger.info(f"基础URL: {self.base_url}")
        logger.info(f"API端点: {self.api_endpoint}")
        logger.info(f"超时: {self.timeout}秒")
        logger.info(f"自动生成的请求头: {self.headers}")
        
        try:
            # 1. 首先尝试使用/models端点测试（标准OpenAI接口）
            logger.info(f"\n1. 尝试使用/models端点测试...")
            response = await self.client.get("/models")
            logger.info(f"请求URL: {self.base_url}/models")
            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text[:500]}...")
            if response.status_code == 200:
                logger.info("✓ /models端点测试成功")
                return True
        except Exception as e:
            logger.error(f"✗ 使用/models端点测试失败: {str(e)}")
        
        try:
            # 2. 根据提供商类型使用不同的测试请求
            logger.info(f"\n2. 根据提供商类型使用不同的测试请求...")
            
            if self.provider_type == "image":
                # 图像生成提供商测试
                test_prompt = "一只可爱的小猫，高清，真实感"
                
                # 从配置中获取支持的尺寸，如果没有则使用默认值
                test_size = "1024x1024"
                if self.supported_sizes and len(self.supported_sizes) > 0:
                    test_size = self.supported_sizes[0]
                
                request_body = {
                    "model": self.model,
                    "prompt": test_prompt,
                    "n": 1,
                    "size": test_size
                }
                
                endpoint = self.api_endpoint or "/v1/images/generations"
                logger.info(f"请求类型: 图像生成测试")
            else:
                # 文本生成提供商测试
                test_prompt = "你好，这是一个连接测试"
                request_body = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "你是一个AI助手"},
                        {"role": "user", "content": test_prompt}
                    ],
                    "max_tokens": 10,
                    "temperature": 0.1
                }
                
                endpoint = self.api_endpoint or "/v1/chat/completions"
                logger.info(f"请求类型: 文本生成测试")
            
            # 确保endpoint以斜杠开头
            if not endpoint.startswith('/'):
                endpoint = f"/{endpoint}"
            full_url = f"{self.base_url}{endpoint}"
            
            logger.info(f"请求URL: {full_url}")
            logger.info(f"请求方法: POST")
            logger.info(f"请求头: {self.headers}")
            logger.debug(f"请求体: {json.dumps(request_body, indent=2)}")
            
            # 确保使用最新的headers创建新的客户端（如果需要）
            if not self.client or self.client.headers != self.headers:
                await self.client.aclose()
                self.client = httpx.AsyncClient(
                    base_url=self.base_url,
                    headers=self.headers,
                    timeout=self.timeout
                )
            
            response = await self.client.post(endpoint, json=request_body)
            
            logger.info(f"响应状态码: {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")
            logger.debug(f"响应内容: {response.text}")
            
            # 检查响应状态码和响应格式
            if response.status_code == 200:
                result = response.json()
                if self.provider_type == "image":
                    # 图像生成响应检查
                    if result.get("data") and isinstance(result["data"], list) and len(result["data"]) > 0:
                        logger.info("✓ 图像生成测试成功")
                        return True
                else:
                    # 文本生成响应检查
                    if result.get("choices") and isinstance(result["choices"], list) and len(result["choices"]) > 0:
                        logger.info("✓ 文本生成测试成功")
                        return True
            
            logger.error(f"✗ 请求测试失败")
            return False
        except Exception as e:
            logger.error(f"✗ 测试OpenAI连接失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
        finally:
            logger.info("=== 测试结束 ===")
    
    async def generate_text(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """生成文本
        
        Args:
            prompt: 生成提示词，支持纯文本或包含文本和图像的数组格式
            **kwargs: 额外参数
            
        Returns:
            Optional[Dict[str, Any]]: 生成结果
        """
        if not self.is_available() or not self.client:
            return None
        
        try:
            # 获取模型名称，用于特殊处理
            model_name = kwargs.get("model", self.model)
            logger.info(f"\n=== 开始发送文本生成请求 ===")
            logger.info(f"使用模型: {model_name}")
            
            # 构建用户消息内容
            user_content = []
            
            # 检测prompt类型，支持多模态输入
            if isinstance(prompt, str):
                # 纯文本输入，保持向后兼容
                logger.info(f"纯文本输入: {prompt[:50]}..." if len(prompt) > 50 else f"纯文本输入: {prompt}")
                user_content = prompt
            elif isinstance(prompt, list):
                # 多模态输入，包含文本和图像
                logger.info(f"多模态输入，包含 {len(prompt)} 个元素")
                for item in prompt:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            logger.info(f"文本元素: {item['text'][:50]}..." if len(item['text']) > 50 else f"文本元素: {item['text']}")
                            user_content.append(item)
                        elif item.get("type") == "image_url":
                            image_url = item['image_url']
                            if isinstance(image_url, dict):
                                url = image_url.get("url", "")
                                logger.info(f"图像元素: {url[:50]}..." if len(url) > 50 else f"图像元素: {url}")
                                user_content.append(item)
                            elif isinstance(image_url, str):
                                logger.info(f"图像元素: {image_url[:50]}..." if len(image_url) > 50 else f"图像元素: {image_url}")
                                user_content.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_url
                                    }
                                })
            
            # 构建请求参数
            request_body = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的内容生成助手"
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                "max_tokens": kwargs.get("max_tokens", kwargs.get("max_output_tokens", self.max_output_tokens)),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", 0.9),
                "frequency_penalty": kwargs.get("frequency_penalty", 0),
                "presence_penalty": kwargs.get("presence_penalty", 0)
            }
            
            # 发送请求，使用配置的API端点或默认值
            endpoint = self.api_endpoint or "/v1/chat/completions"
            # 确保endpoint以斜杠开头
            if not endpoint.startswith('/'):
                endpoint = f"/{endpoint}"
            
            # 打印请求日志
            logger.info(f"基础URL: {self.base_url}")
            logger.info(f"API端点: {endpoint}")
            logger.info(f"完整URL: {self.base_url}{endpoint}")
            logger.debug(f"请求头: {json.dumps(dict(self.headers), indent=2)}")
            logger.debug(f"请求体: {json.dumps(request_body, ensure_ascii=False)}")
            
            response = await self.client.post(endpoint, json=request_body)
            
            # 打印响应日志
            logger.info(f"\n=== 接收文本生成响应 ===")
            logger.info(f"响应状态码: {response.status_code}")
            logger.debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
            
            # 先获取原始响应文本，以便调试
            response_text = response.text
            logger.debug(f"响应体原始文本: {response_text}")
            
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"响应体JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            return {
                "success": True,
                "text": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model", model_name),
                "provider": self.name
            }
            
        except Exception as e:
            logger.error(f"\n=== 文本生成请求失败 ===")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误信息: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}",
                "provider": self.name,
                "model": model_name
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
        if not self.is_available() or not self.client:
            logger.error(f"OpenAI提供商不可用，无法生成图像")
            return None
        
        try:
            # 获取平台尺寸配置
            platform_sizes = kwargs.get("size_config", {}).get(platform, ["1024x1024"])
            size = kwargs.get("size", platform_sizes[0])
            
            # 优先使用请求中的response_format，否则使用配置中的，最后使用默认值
            response_format = kwargs.get("response_format", self.response_config.get("response_format", "url"))
            
            # 构建请求参数
            request_body = {
                "model": self.model,  # 统一使用配置的model字段
                "prompt": prompt,
                "n": kwargs.get("n", 1),
                "size": size,
                "quality": kwargs.get("image_quality", "standard"),
                "response_format": response_format
            }
            
            # 处理参考图
            reference_images = kwargs.get("reference_images", [])
            if reference_images and self.support_reference_image:
                # 提取参考图的URL
                reference_image_urls = []
                for ref_image in reference_images:
                    if isinstance(ref_image, dict) and "image_url" in ref_image:
                        reference_image_urls.append(ref_image["image_url"])
                # 支持多图参考的模型使用所有参考图
                if self.support_multiple_reference_images:
                    request_body[self.reference_image_field] = reference_image_urls
                # 不支持多图参考的模型只使用第一个参考图
                elif reference_image_urls:
                    request_body[self.reference_image_field] = reference_image_urls[0]
            
            # 发送请求，使用配置的API端点或默认值
            endpoint = self.api_endpoint or "/v1/images/generations"
            # 确保endpoint以斜杠开头
            if not endpoint.startswith('/'):
                endpoint = f"/{endpoint}"
            
            # 打印请求日志
            logger.info(f"\n=== 开始发送图像生成请求 ===")
            logger.info(f"提供商: {self.name}")
            logger.info(f"平台: {platform}")
            logger.info(f"基础URL: {self.base_url}")
            logger.info(f"API端点: {endpoint}")
            logger.info(f"完整URL: {self.base_url}{endpoint}")
            logger.debug(f"请求头: {json.dumps(dict(self.headers), indent=2)}")
            logger.debug(f"请求体: {json.dumps(request_body, ensure_ascii=False, indent=2)}")
            
            response = await self.client.post(endpoint, json=request_body)
            
            # 打印响应日志
            logger.info(f"\n=== 接收图像生成响应 ===")
            logger.info(f"响应状态码: {response.status_code}")
            logger.debug(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
            
            # 尝试解析响应体
            response_text = response.text
            try:
                response_json = response.json()
                logger.debug(f"响应体: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            except:
                logger.debug(f"响应体: {response_text}")
            
            response.raise_for_status()
            
            result = response.json()
            
            # 提取图像，直接使用配置的JSONPath，与通用提供商保持一致
            images = []
            # 优先使用请求中的response_format，否则使用配置中的，最后使用默认值
            response_format = kwargs.get("response_format", self.response_config.get("response_format", "url"))
            
            # 直接使用配置的images_path提取图像，不做任何字段映射
            images_path = self.response_config.get("images_path", "$.data[*].url")
            
            logger.info(f"使用JSONPath提取图像: {images_path}")
            logger.info(f"响应格式: {response_format}")
            
            # 直接使用JSONPath提取图像，与通用提供商保持一致
            images = self._extract_from_response(result, images_path, is_list=True)
            
            # 处理base64数据
            if response_format == "base64" and images:
                processed_images = []
                for img in images:
                    if img and isinstance(img, str):
                        # 如果是base64数据，转换为data URL格式
                        if not img.startswith('data:'):
                            img = f"data:image/png;base64,{img}"
                        processed_images.append(img)
                    else:
                        processed_images.append(img)
                images = processed_images
            
            logger.info(f"最终提取到 {len(images)} 张图像")
            
            logger.info(f"\n=== 图像生成成功 ===")
            logger.info(f"成功生成 {len(images)} 张图像")
            logger.info(f"使用模型: {result.get('model', self.model)}")
            logger.info(f"返回格式: {response_format}")
            
            return {
                "success": True,
                "images": images,
                "usage": result.get("usage", {}),
                "model": result.get("model", self.model),
                "provider": self.name,
                "seed": result.get("seed"),
                "response_format": response_format
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"\n=== 图像生成请求失败 - HTTP错误 ===")
            logger.error(f"状态码: {e.response.status_code}")
            logger.error(f"错误信息: {str(e)}")
            logger.debug(f"响应头: {json.dumps(dict(e.response.headers), indent=2)}")
            logger.debug(f"响应体: {e.response.text}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": f"HTTP错误 {e.response.status_code}: {e.response.text}",
                "provider": self.name
            }
        except Exception as e:
            logger.error(f"\n=== 图像生成请求失败 - 其他错误 ===")
            logger.error(f"错误类型: {type(e).__name__}")
            logger.error(f"错误信息: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "provider": self.name
            }
    
    def _extract_from_response(self, response: Dict[str, Any], path: str, is_list: bool = False) -> Any:
        """从响应中提取字段
        
        Args:
            response: 响应JSON
            path: JSONPath路径
            is_list: 是否返回列表
            
        Returns:
            Any: 提取的值
        """
        if not path:
            return None
        
        try:
            expr = jsonpath_ng.parse(path)
            matches = expr.find(response)
            
            if is_list:
                return [match.value for match in matches]
            elif matches:
                return matches[0].value
            else:
                return None
        except Exception as e:
            logger.error(f"JSONPath解析失败: {str(e)}")
            return None
    
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