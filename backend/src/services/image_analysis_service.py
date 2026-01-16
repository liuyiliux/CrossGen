"""
图片分析服务
处理图片分析和提示词生成
"""

import logging
from typing import List, Dict, Any
import base64
import io
from PIL import Image

logger = logging.getLogger(__name__)


class ImageAnalysisService:
    """图片分析服务"""
    
    def __init__(self):
        """初始化图片分析服务"""
        self.provider_manager = None
        
    async def initialize(self):
        """初始化服务，加载模型和提供商"""
        try:
            from src.providers.provider_manager import ProviderManager
            self.provider_manager = ProviderManager()
            await self.provider_manager.load_providers()
            return True
        except Exception as e:
            logger.error(f"初始化图片分析服务失败: {str(e)}")
            return False
    
    async def analyze_image(self, image_data: str, provider_name: str = None) -> Dict[str, Any]:
        """分析图片内容
        
        Args:
            image_data: 图片数据，可以是URL或base64编码
            provider_name: 使用的提供商名称，默认为第一个可用的提供商
            
        Returns:
            Dict[str, Any]: 图片分析结果
        """
        try:
            if not self.provider_manager:
                await self.initialize()
            
            # 获取文本提供商
            if provider_name:
                text_provider = self.provider_manager.text_providers.get(provider_name)
            else:
                # 使用第一个可用的文本提供商
                text_provider = next(iter(self.provider_manager.text_providers.values()), None)
            
            if not text_provider:
                return {
                    "success": False,
                    "error": "未找到可用的文本提供商"
                }
            
            # 构建分析提示词
            analysis_prompt = "请详细描述这张图片的内容，包括主题、风格、色彩、构图等。输出内容将用于生成图片提示词。"
            
            # 构建包含文本和图像的多模态提示
            multimodal_prompt = [
                {
                    "type": "text",
                    "text": analysis_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data
                    }
                }
            ]
            
            # 调用AI API进行图片分析
            result = await text_provider.generate_text(
                multimodal_prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            if result and result.get("success"):
                return {
                    "success": True,
                    "description": result.get("text", ""),
                    "provider": result.get("provider")
                }
            else:
                error_msg = result.get("error", "图片分析失败") if result else "图片分析失败"
                return {
                    "success": False,
                    "error": error_msg
                }
        except Exception as e:
            logger.error(f"分析图片失败: {str(e)}")
            return {
                "success": False,
                "error": f"分析图片失败: {str(e)}"
            }
    
    async def generate_prompt_from_image(self, image_data: str, style: str = None, provider_name: str = None) -> Dict[str, Any]:
        """从图片生成提示词
        
        Args:
            image_data: 图片数据，可以是URL或base64编码
            style: 期望的生成风格，可选
            provider_name: 使用的提供商名称，默认为第一个可用的提供商
            
        Returns:
            Dict[str, Any]: 生成的提示词结果
        """
        try:
            # 首先分析图片
            analysis_result = await self.analyze_image(image_data, provider_name)
            
            if not analysis_result.get("success"):
                return analysis_result
            
            if not self.provider_manager:
                await self.initialize()
            
            # 获取文本提供商
            if provider_name:
                text_provider = self.provider_manager.text_providers.get(provider_name)
            else:
                text_provider = next(iter(self.provider_manager.text_providers.values()), None)
            
            if not text_provider:
                return {
                    "success": False,
                    "error": "未找到可用的文本提供商"
                }
            
            # 构建提示词生成提示
            style_prompt = f"，风格为{style}" if style else ""
            
            prompt = f"请根据以下图片描述生成一个详细的图片生成提示词，用于AI图像生成。提示词应包含主题、风格、色彩、构图等关键信息{style_prompt}。\n\n图片描述：{analysis_result.get('description')}"
            
            # 调用AI API生成提示词
            result = await text_provider.generate_text(
                prompt,
                max_tokens=800,
                temperature=0.7
            )
            
            if result and result.get("success"):
                return {
                    "success": True,
                    "prompt": result.get("text", ""),
                    "description": analysis_result.get("description"),
                    "provider": result.get("provider")
                }
            else:
                error_msg = result.get("error", "提示词生成失败") if result else "提示词生成失败"
                return {
                    "success": False,
                    "error": error_msg
                }
        except Exception as e:
            logger.error(f"从图片生成提示词失败: {str(e)}")
            return {
                "success": False,
                "error": f"从图片生成提示词失败: {str(e)}"
            }
    
    async def generate_prompts_from_images(self, images_data: List[str], style: str = None, provider_name: str = None) -> List[Dict[str, Any]]:
        """从多张图片生成提示词
        
        Args:
            images_data: 图片数据列表，可以是URL或base64编码
            style: 期望的生成风格，可选
            provider_name: 使用的提供商名称，默认为第一个可用的提供商
            
        Returns:
            List[Dict[str, Any]]: 生成的提示词结果列表
        """
        results = []
        
        for image_data in images_data:
            result = await self.generate_prompt_from_image(image_data, style, provider_name)
            results.append(result)
        
        return results
    
    def preprocess_image(self, image_data: str) -> Dict[str, Any]:
        """预处理图片，调整大小和格式
        
        Args:
            image_data: 图片数据，可以是base64编码
            
        Returns:
            Dict[str, Any]: 预处理后的图片数据
        """
        try:
            # 检查是否为base64编码
            if image_data.startswith("data:"):
                # 提取base64数据
                base64_str = image_data.split(",")[1]
                image_bytes = base64.b64decode(base64_str)
                
                # 打开图片
                img = Image.open(io.BytesIO(image_bytes))
                
                # 调整图片大小，最大边不超过1024
                max_size = 1024
                img.thumbnail((max_size, max_size))
                
                # 保存为JPEG
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                
                # 转换为base64
                processed_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                return {
                    "success": True,
                    "image_data": f"data:image/jpeg;base64,{processed_base64}"
                }
            else:
                # 不是base64编码，直接返回
                return {
                    "success": True,
                    "image_data": image_data
                }
        except Exception as e:
            logger.error(f"预处理图片失败: {str(e)}")
            return {
                "success": False,
                "error": f"预处理图片失败: {str(e)}"
            }
