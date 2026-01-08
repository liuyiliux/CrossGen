"""
通用图像提供商实现
通过配置驱动，支持任意API格式的图像生成
"""

from typing import Dict, Any, Optional, List
import httpx
import jsonpath_ng
from jinja2 import Template
from src.providers.base_provider import BaseProvider, ProviderConfig


class GenericImageProvider(BaseProvider):
    """通用图像提供商实现"""
    
    def __init__(self, config: ProviderConfig):
        """初始化通用图像提供商

        Args:
            config: 提供商配置
        """
        super().__init__(config)
        self.client = None
        self.initialized = False

        # 通用配置
        self.request_config = getattr(config, 'request_config', {})
        self.response_config = getattr(config, 'response_config', {})
        self.size_config = getattr(config, 'size_config', {})

        # 支持的尺寸列表
        self.supported_sizes = getattr(config, 'supported_sizes', [])

        # 参考图配置
        self.support_reference_image = getattr(config, 'support_reference_image', False)
        self.reference_image_field = getattr(config, 'reference_image_field', 'image_urls')
        self.support_multiple_reference_images = getattr(config, 'support_multiple_reference_images', False)
        self.max_reference_images = getattr(config, 'max_reference_images', 1)

        # 模板渲染配置
        self.request_template = None
        if self.request_config.get('template'):
            self.request_template = Template(self.request_config['template'])

        # 默认参数
        self.default_params = self.request_config.get('defaults', {})

        # 参数转换规则
        self.parameter_transforms = self.request_config.get('parameter_transforms', {})
    
    async def initialize(self) -> bool:
        """初始化通用图像提供商
        
        Returns:
            bool: 初始化是否成功
        """
        print(f"=== 开始初始化通用图像提供商 ===")
        print(f"提供商: {self.name}")
        print(f"模型: {self.model}")
        print(f"基础URL: {self.base_url}")
        
        if not self.enabled:
            print(f"提供商已禁用，跳过初始化")
            self.initialized = False
            return False
        
        try:
            # 解析环境变量
            resolved_config = self._resolve_env_vars({
                "api_key": self.api_key,
                "base_url": self.base_url,
                "headers": self.headers
            })
            
            # 更新配置
            self.api_key = resolved_config["api_key"]
            self.base_url = resolved_config["base_url"].rstrip("/")
            self.headers = resolved_config["headers"] or {}
            
            # 自动生成Authorization头（如果没有提供）
            if self.api_key and "Authorization" not in self.headers:
                self.headers["Authorization"] = f"Bearer {self.api_key}"
                print(f"自动生成Authorization头")
            
            # 创建HTTP客户端
            self.client = httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True
            )
            
            self.initialized = True
            print(f"初始化成功")
            return True
            
        except Exception as e:
            print(f"初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.initialized = False
            return False
    
    async def test_connection(self, reference_images: list = None) -> bool:
        """测试通用图像提供商连接
        
        Args:
            reference_images: 参考图URL列表（可选）
            
        Returns:
            bool: 连接是否成功
        """
        print(f"\n=== 开始测试通用图像提供商连接 ===")
        print(f"提供商: {self.name}")
        print(f"类型: {type(self).__name__}")
        print(f"模型: {self.model}")
        print(f"基础URL: {self.base_url}")
        
        # 打印参考图信息
        if reference_images and len(reference_images) > 0:
            print(f"使用提供的参考图: {reference_images}")
        else:
            print("未提供参考图，将使用无参考图的测试请求")
        
        if not self.initialized or not self.client:
            print(f"提供商尚未初始化，尝试初始化...")
            if not await self.initialize():
                print(f"初始化失败，连接测试失败")
                return False
        
        try:
            # 构建测试请求参数
            # 优先从supported_sizes获取测试尺寸，否则使用默认逻辑
            test_size = None
            if self.supported_sizes and len(self.supported_sizes) > 0:
                raw_size = self.supported_sizes[0]
                # 检查尺寸格式是否有效
                if isinstance(raw_size, str) and "*" in raw_size:
                    try:
                        parts = raw_size.split("*")
                        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                            test_size = raw_size
                            print(f"  使用支持尺寸列表中的第一个尺寸: {test_size}")
                        else:
                            raise ValueError(f"无效的尺寸值: {raw_size}")
                    except (ValueError, AttributeError) as e:
                        print(f"  尺寸格式无效: {raw_size}，使用默认尺寸")
                else:
                    print(f"  尺寸格式无效: {raw_size}，使用默认尺寸")
            
            # 如果没有获取到尺寸，使用默认逻辑
            if not test_size:
                test_size = self.default_params.get("size", "1024*1024")
                print(f"  使用默认尺寸: {test_size}")
            
            # 构建测试请求参数
            test_params = {
                "model": self.model,
                "prompt": "测试图片生成",
                "size": test_size,
                "n": 1
            }

            # 添加所有默认参数
            for key, value in self.default_params.items():
                if key not in test_params:
                    test_params[key] = value

            # 如果提供了参考图且支持参考图，添加到测试参数中
            if reference_images and len(reference_images) > 0 and self.support_reference_image:
                test_params["reference_images"] = reference_images
                print(f"  已添加 {len(reference_images)} 张参考图到测试请求")
            elif reference_images and len(reference_images) > 0 and not self.support_reference_image:
                print(f"  提供了参考图但提供商不支持参考图，将忽略参考图")
            
            # 处理尺寸
            test_params["size"] = self._process_size(test_params.get("size"))
            
            # 参数转换
            test_params = self._transform_parameters(test_params)
            
            # 渲染测试请求
            request_body = self._render_request(test_params)
            print(f"测试请求体: {request_body}")
            
            # 打印完整Headers，包括API密钥
            print(f"发送请求的完整Headers: {self.headers}")
            # 单独打印Authorization头，方便查看API密钥
            print(f"Authorization头: {self.headers.get('Authorization')}")
            
            # 发送测试请求
            response = await self.client.request(
                method="POST",
                url=self.base_url,
                json=request_body
            )
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应体: {response.text}")
            
            if response.status_code == 200:
                print("✓ 图像生成测试成功")
                return True
            else:
                print(f"✗ 图像生成测试失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def generate_image(self, prompt: str, platform: str, **kwargs) -> Optional[Dict[str, Any]]:
        """生成图像
        
        Args:
            prompt: 生成提示词
            platform: 平台名称
            **kwargs: 额外参数
            
        Returns:
            Optional[Dict[str, Any]]: 生成结果
        """
        print(f"\n=== 开始通用图像生成 ===")
        print(f"提供商: {self.name}")
        print(f"平台: {platform}")
        print(f"提示词: {prompt[:50]}..." if len(prompt) > 50 else f"提示词: {prompt}")
        print(f"参数: {kwargs}")
        
        if not self.initialized or not self.client:
            print(f"提供商不可用，无法生成图像")
            return None
        
        try:
            # 准备请求参数
            request_params = {
                "model": self.model,
                "prompt": prompt,
                "platform": platform,
                **self.default_params,
                **kwargs
            }
            
            # 处理尺寸
            request_params["size"] = self._process_size(request_params.get("size"))
            
            # 参数转换
            request_params = self._transform_parameters(request_params)
            
            # 渲染请求体
            request_body = self._render_request(request_params)
            print(f"最终请求体: {request_body}")
            
            # 发送请求
            response = await self.client.request(
                method="POST",
                url=self.base_url,
                json=request_body
            )
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应体: {response.text}")
            
            # 解析响应
            return self._parse_response(response)
            
        except httpx.HTTPStatusError as e:
            print(f"HTTP错误: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP错误 {e.response.status_code}: {e.response.text}",
                "provider": self.name
            }
        except Exception as e:
            print(f"生成图像失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "provider": self.name
            }
    
    def _process_size(self, size: str) -> str:
        """处理尺寸
        
        Args:
            size: 输入尺寸
            
        Returns:
            str: 处理后的尺寸
        """
        # 如果没有指定尺寸，使用默认值
        if not size:
            size = self.default_params.get("size", "1024*1024")
        
        # 转换尺寸格式（x -> *）
        if "x" in size:
            size = size.replace("x", "*")
        
        # 验证尺寸
        self._validate_size(size)
        
        return size
    
    def _validate_size(self, size: str) -> None:
        """验证尺寸是否符合要求
        
        Args:
            size: 尺寸字符串
            
        Raises:
            ValueError: 尺寸不符合要求时抛出
        """
        # 解析宽高
        try:
            width, height = map(int, size.split("*"))
        except ValueError:
            raise ValueError(f"无效的尺寸格式: {size}，应为 W*H 格式")
        
        # 计算总像素
        total_pixels = width * height
        
        # 验证总像素范围
        total_pixels_config = self.size_config.get("total_pixels", {})
        min_pixels = self._parse_size_str(total_pixels_config.get("min", "512*512"))
        max_pixels = self._parse_size_str(total_pixels_config.get("max", "2048*2048"))
        
        if total_pixels < min_pixels:
            raise ValueError(f"尺寸 {size} 总像素 {total_pixels} 小于最小要求 {min_pixels}")
        if total_pixels > max_pixels:
            raise ValueError(f"尺寸 {size} 总像素 {total_pixels} 大于最大要求 {max_pixels}")
        
        # 检查是否在支持的尺寸列表中
        if self.supported_sizes and size not in self.supported_sizes:
            print(f"警告：尺寸 {size} 不在支持列表中，可能导致生成失败")
    
    def _parse_size_str(self, size_str: str) -> int:
        """解析尺寸字符串，返回总像素数
        
        Args:
            size_str: 尺寸字符串，如 "1024*1024"
            
        Returns:
            int: 总像素数
        """
        width, height = map(int, size_str.split("*"))
        return width * height
    
    def _transform_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """转换参数
        
        Args:
            params: 原始参数
            
        Returns:
            Dict[str, Any]: 转换后的参数
        """
        transformed = params.copy()
        
        # 应用参数转换规则
        for key, transform in self.parameter_transforms.items():
            if key in transformed:
                value = transformed[key]
                # 使用Jinja2模板进行转换
                transform_template = Template(transform)
                transformed_value = transform_template.render({key: value, **params})
                transformed[key] = transformed_value
        
        return transformed
    
    def _render_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """渲染请求体

        Args:
            params: 请求参数
            
        Returns:
            Dict[str, Any]: 渲染后的请求体
        """
        if not self.request_template:
            raise ValueError("未配置请求模板")
        
        # 清理参数中的控制字符，确保JSON有效
        clean_params = {}
        for key, value in params.items():
            if isinstance(value, str):
                # 替换换行符、制表符等控制字符为空格，确保JSON有效
                value = value.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            clean_params[key] = value
        
        # 确保 reference_images 变量存在，避免模板渲染错误
        if 'reference_images' not in clean_params:
            clean_params['reference_images'] = []
        
        # 处理参考图
        has_reference_images = False
        processed_reference_images = []
        
        if clean_params['reference_images']:
            import json
            from src.utils.image_utils import convert_local_path_to_data_url
            from pathlib import Path
            
            # 处理所有参考图
            for i, ref_image in enumerate(clean_params['reference_images'][:self.max_reference_images]):
                ref_image_copy = ref_image.copy()
                # 根据配置的reference_image_field字段名进行转换
                if 'image_url' in ref_image_copy and hasattr(self, 'reference_image_field'):
                    image_url_value = ref_image_copy.pop('image_url')
                    # 检查是否是本地路径，如果是则转换为data URL格式
                    if image_url_value and image_url_value.startswith('/'):
                        print(f"检测到本地路径: {image_url_value}，尝试转换为data URL格式")
                        # 尝试将本地路径转换为data URL
                        try:
                            # 获取项目根目录
                            project_root = Path(__file__).parent.parent.parent.parent
                            full_path = project_root / image_url_value.lstrip('/')
                            print(f"完整文件路径: {full_path}")
                            
                            # 直接读取文件转换为base64，避免调用convert_local_path_to_data_url函数
                            if full_path.exists():
                                print(f"文件存在，开始转换为base64...")
                                with open(full_path, 'rb') as f:
                                    image_data = f.read()
                                import base64
                                base64_image = base64.b64encode(image_data).decode("utf-8")
                                # 确定文件类型
                                content_type = "image/png"
                                if full_path.suffix.lower() in ('.jpg', '.jpeg'):
                                    content_type = "image/jpeg"
                                elif full_path.suffix.lower() == '.gif':
                                    content_type = "image/gif"
                                elif full_path.suffix.lower() == '.webp':
                                    content_type = "image/webp"
                                
                                image_url_value = f"data:{content_type};base64,{base64_image}"
                                print(f"成功转换为base64格式，长度: {len(base64_image)}")
                            else:
                                print(f"文件不存在: {full_path}")
                        except Exception as e:
                            print(f"转换本地路径为data URL失败: {e}，保留原始路径")
                    
                    # 使用配置中指定的字段名（如image），而不是默认的image_urls
                    ref_image_copy[self.reference_image_field] = image_url_value
                    processed_reference_images.append(ref_image_copy)
            
            has_reference_images = len(processed_reference_images) > 0
        
        # 添加辅助变量
        clean_params['has_reference_images'] = has_reference_images
        
        # 直接构建消息内容，避免模板渲染时的JSON格式问题
        if has_reference_images:
            # 构建包含参考图和提示词的消息内容
            import json
            ref_images_json = []
            for img in processed_reference_images:
                ref_images_json.append(json.dumps(img, ensure_ascii=False))
            # 构建完整的内容数组：参考图 + 文本提示词
            if ref_images_json:
                content_array = f"[{','.join(ref_images_json)}, {{\"text\": \"{clean_params.get('prompt', '')}\"}}]"
            else:
                # 如果参考图处理后为空，只包含文本提示词
                content_array = f"[{{\"text\": \"{clean_params.get('prompt', '')}\"}}]"
            clean_params['content_array'] = content_array
        else:
            # 只包含文本提示词
            clean_params['content_array'] = f"[{{\"text\": \"{clean_params.get('prompt', '')}\"}}]"
        
        # 修改模板，使用content_array变量
        # 先获取模板内容
        template_content = self.request_config['template']
        # 替换原来的复杂条件表达式为简单的content_array
        import re
        
        # 使用更灵活的正则表达式，匹配各种模板格式变体
        new_template_content = re.sub(r'"content":\s*\{%\s*if\s+has_reference_images\s+%\}\s*\[\s*\{\{\s*reference_images_0\s*\}\}\s*,\s*\{"text"\s*:\s*"\{\{\s*prompt\s*\}\}"\}\s*\]\s*\{%\s*else\s+%\}\s*\[\s*\{"text"\s*:\s*"\{\{\s*prompt\s*\}\}"\}\s*\]\s*\{%\s*endif\s+%\}', 
                                   '"content": {{ content_array }}', 
                                   template_content, 
                                   flags=re.DOTALL | re.IGNORECASE)
        
        # 使用修改后的模板重新渲染
        from jinja2 import Template
        new_template = Template(new_template_content)
        rendered = new_template.render(**clean_params)
        print(f"渲染后的模板内容: {rendered}")
        
        # 解析为JSON
        import json
        try:
            result = json.loads(rendered)
            print(f"JSON解析成功: {result}")
            return result
        except json.JSONDecodeError as e:
            print(f"JSON解析失败，错误位置: 行 {e.lineno}, 列 {e.colno}, 字符位置 {e.pos}")
            # 打印错误位置附近的内容
            lines = rendered.split('\n')
            error_line = lines[e.lineno-1] if e.lineno <= len(lines) else ''
            print(f"错误行内容: {error_line}")
            if error_line:
                # 打印错误位置前后的字符
                start = max(0, e.colno-20)
                end = min(len(error_line), e.colno+20)
                print(f"错误位置附近: '{error_line[start:end]}'")
            
            # 尝试直接构建请求体作为备用方案
            try:
                print("尝试直接构建请求体...")
                # 解析模板为字典
                base_template = json.loads(template_content)
                # 直接设置content字段
                base_template['input']['messages'][0]['content'] = json.loads(content_array)
                print(f"直接构建请求体成功: {base_template}")
                return base_template
            except Exception as fallback_error:
                print(f"直接构建请求体也失败: {fallback_error}")
                raise
    
    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        """解析响应
        
        Args:
            response: HTTP响应
            
        Returns:
            Dict[str, Any]: 解析后的结果
        """
        response_json = response.json()
        
        # 检查响应状态
        if response.status_code != 200:
            # 提取错误信息
            error_message = self._extract_from_response(response_json, self.response_config.get("error_path"))
            if not error_message:
                error_message = f"请求失败，状态码: {response.status_code}"
            return {
                "success": False,
                "error": error_message,
                "provider": self.name
            }
        
        # 提取图像URL
        images_path = self.response_config.get("images_path", "$.images[*].url")
        images = self._extract_from_response(response_json, images_path, is_list=True)
        
        if not images:
            return {
                "success": False,
                "error": "未能从响应中提取图像URL",
                "provider": self.name
            }
        
        # 提取使用信息
        usage_path = self.response_config.get("usage_path")
        usage = {}
        if usage_path:
            usage = self._extract_from_response(response_json, usage_path)
        
        return {
            "success": True,
            "images": images,
            "usage": usage,
            "model": response_json.get("model", self.model),
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
            print(f"JSONPath解析失败: {str(e)}")
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
