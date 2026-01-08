"""
内容生成服务
处理文本和图像生成逻辑
"""

import asyncio
import uuid
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from src.models.generation import (
    GenerationRequest,
    GenerationResponse,
    BatchGenerationRequest,
    BatchGenerationResponse,
    GenerationStatus,
    GenerationResult,
    PlatformType
)
from src.providers.provider_manager import ProviderManager


class GenerationService:
    """内容生成服务 - 单例模式"""
    
    # 类变量，保存单例实例
    _instance = None
    # 锁，确保线程安全
    _lock = asyncio.Lock()
    _initialized = False
    # 全局提供商管理器实例
    _global_provider_manager = None
    
    def __new__(cls):
        """创建单例实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set_global_provider_manager(cls, provider_manager: ProviderManager):
        """设置全局提供商管理器实例
        
        Args:
            provider_manager: 提供商管理器实例
        """
        cls._global_provider_manager = provider_manager
        # 如果单例已经初始化，更新其提供商管理器
        if cls._instance is not None and hasattr(cls._instance, 'provider_manager'):
            cls._instance.provider_manager = provider_manager
            cls._instance.provider_manager_loaded = True
    
    def __init__(self):
        """初始化内容生成服务"""
        # 只初始化一次
        if not GenerationService._initialized:
            self.active_jobs: Dict[str, GenerationStatus] = {}
            self.provider_manager: Optional[ProviderManager] = None
            self.provider_manager_loaded = False
            self.image_analysis_service: Optional[Any] = None
            GenerationService._initialized = True
    
    async def initialize_provider_manager(self) -> bool:
        """
        初始化提供商管理器
        
        Returns:
            bool: 初始化是否成功
        """
        if self.provider_manager_loaded and self.provider_manager:
            return True
        
        async with self._lock:
            # 双重检查，避免并发问题
            if self.provider_manager_loaded and self.provider_manager:
                return True
                
            try:
                # 优先使用全局提供商管理器
                if self._global_provider_manager:
                    self.provider_manager = self._global_provider_manager
                    self.provider_manager_loaded = True
                    print("使用全局提供商管理器实例")
                    print(f"  可用图像提供商: {self.provider_manager.available_image_providers}")
                else:
                    # 全局提供商管理器不存在，创建新实例
                    self.provider_manager = ProviderManager()
                    await self.provider_manager.load_providers()
                    self.provider_manager_loaded = True
                    print("创建新的提供商管理器实例")
                    print(f"  可用图像提供商: {self.provider_manager.available_image_providers}")
                
                # 初始化图片分析服务
                from src.services.image_analysis_service import ImageAnalysisService
                self.image_analysis_service = ImageAnalysisService()
                await self.image_analysis_service.initialize()
                
                return True
            except Exception as e:
                print(f"初始化提供商管理器失败: {str(e)}")
                return False
    
    async def generate_single(self, request: GenerationRequest, reference_images: List[str] = None) -> GenerationResponse:
        """生成单个主题的内容
        
        Args:
            request: 生成请求
            reference_images: 参考图列表，base64编码或URL
            
        Returns:
            GenerationResponse: 生成结果
        """
        start_time = datetime.now()
        
        try:
            results = []
            history_record_id = None
            history_service = None
            
            # 处理平台类型，确保是字符串
            platform_values = []
            for p in request.platforms:
                if hasattr(p, 'value'):
                    platform_values.append(p.value)
                else:
                    platform_values.append(str(p))
            
            # 创建历史记录服务实例
            from src.services.history_service import HistoryService
            from src.models.history import HistoryRecordCreate, Outline, Page, GenerationStatus
            history_service = HistoryService()
            
            # 初始化提供商管理器
            if not await self.initialize_provider_manager():
                # 如果提供商管理器初始化失败，回退到模拟生成
                # 创建初始历史记录，状态为outline_generating
                initial_outline = Outline(
                    raw=f"生成主题: {request.topic}\n平台: {platform_values}",
                    pages=[Page(index=0, type="content", content="大纲生成中...")]
                )
                
                # 确保平台类型是字符串
                first_platform = request.platforms[0]
                first_platform_str = first_platform.value if hasattr(first_platform, 'value') else str(first_platform)
                
                # 创建历史记录，状态为outline_generating
                history_record = await history_service.create_history(HistoryRecordCreate(
                    topic=request.topic,
                    platform=first_platform_str,
                    outline=initial_outline,
                    images=[],
                    status=GenerationStatus.OUTLINE_GENERATING,
                    generation_time=0,
                    text_model=request.text_provider,
                    image_model=request.image_provider
                ))
                history_record_id = history_record.id
                
                # 模拟大纲生成
                await asyncio.sleep(1.0)
                
                for platform in request.platforms:
                    await asyncio.sleep(0.5)  # 模拟API调用
                    
                    # 确保平台类型是字符串
                    platform_str = platform.value if hasattr(platform, 'value') else str(platform)
                    
                    result = GenerationResult(
                        platform=platform,
                        title=f"[{platform_str.upper()}] {request.topic}",
                        content=f"这是为{platform_str}平台生成的内容：{request.topic}",
                        images=[],
                        metadata={"generation_method": "mock"}
                    )
                    results.append(result)
                
                # 更新历史记录状态为outline_success
                if history_record_id:
                    await history_service.update_history(
                        history_record_id,
                        HistoryRecordUpdate(status=GenerationStatus.OUTLINE_SUCCESS)
                    )
            else:
                # 使用实际的AI API生成
                # 创建初始历史记录，状态为outline_generating
                initial_outline = Outline(
                    raw=f"生成主题: {request.topic}\n平台: {platform_values}",
                    pages=[Page(index=0, type="content", content="大纲生成中...")]
                )
                
                # 确保平台类型是字符串
                first_platform = request.platforms[0]
                first_platform_str = first_platform.value if hasattr(first_platform, 'value') else str(first_platform)
                
                # 创建历史记录，状态为outline_generating
                history_record = await history_service.create_history(HistoryRecordCreate(
                    topic=request.topic,
                    platform=first_platform_str,
                    outline=initial_outline,
                    images=[],
                    status=GenerationStatus.OUTLINE_GENERATING,
                    generation_time=0,
                    text_model=request.text_provider,
                    image_model=request.image_provider
                ))
                history_record_id = history_record.id
                
                for platform in request.platforms:
                    print(f"\n=== 开始为平台 {platform} 生成内容 ===")
                    print(f"主题: {request.topic}")
                    
                    # 获取平台模板
                    config_service = self.provider_manager.config_service
                    templates = config_service.get_platform_templates()
                    print(f"获取到的模板配置: {templates.keys()}")
                    
                    # 检查平台类型，确保是字符串类型
                    platform_str = platform.value if hasattr(platform, 'value') else str(platform)
                    print(f"处理后的平台名称: {platform_str}")
                    
                    # 获取平台模板配置
                    platform_templates = templates.get("platform_templates", {})
                    print(f"平台模板配置: {list(platform_templates.keys())}")
                    
                    # 获取当前平台的模板
                    current_platform_template = platform_templates.get(platform_str, {})
                    outline_template = current_platform_template.get("outline_template")
                    
                    # 构建生成提示词
                    if outline_template:
                        print(f"使用平台大纲模板: {outline_template[:100]}...")
                        # 替换模板变量
                        prompt = outline_template.format(
                            topic=request.topic,
                            title_requirements="吸引人的标题",
                            section_structure="清晰的结构",
                            text_style="适合平台的风格",
                            video_duration="30秒"
                        )
                    else:
                        # 使用默认提示词
                        prompt = f"为{platform_str}平台生成关于{request.topic}的内容"
                        print(f"使用默认提示词: {prompt}")
                        print(f"未找到平台 {platform_str} 的大纲模板，可用模板平台: {list(platform_templates.keys())}")
                    
                    # 如果有参考图片，使用图片分析服务生成提示词
                    if reference_images:
                        print(f"使用参考图生成提示词: {len(reference_images)}张")
                        
                        # 从参考图片生成提示词
                        prompt_results = await self.image_analysis_service.generate_prompts_from_images(reference_images)
                        
                        # 提取生成的提示词
                        generated_prompts = []
                        for result in prompt_results:
                            if result.get("success"):
                                generated_prompts.append(result.get("prompt"))
                        
                        if generated_prompts:
                            # 将生成的提示词添加到原始提示词中
                            prompt += f"\n\n参考图片生成的提示词:\n{chr(10).join(generated_prompts)}"
                    
                    # 获取当前使用的提供商
                    # 优先使用请求中指定的提供商
                    provider = None
                    if request.text_provider:
                        # 尝试直接通过字典访问获取提供商
                        provider = self.provider_manager.text_providers.get(request.text_provider)
                        print(f"使用请求指定的提供商: {request.text_provider}")
                        
                        # 针对中文提供商名称可能的编码问题，添加备用逻辑
                        if not provider:
                            # 遍历可用的提供商，查找匹配的提供商
                            for provider_name in self.provider_manager.text_providers.keys():
                                if provider_name == request.text_provider:
                                    provider = self.provider_manager.text_providers[provider_name]
                                    break
                            
                            # 如果仍然没有找到，尝试模糊匹配提供商名称
                            if not provider:
                                for provider_name in self.provider_manager.text_providers.keys():
                                    if request.text_provider in provider_name or provider_name in request.text_provider:
                                        provider = self.provider_manager.text_providers[provider_name]
                                        print(f"使用模糊匹配的提供商: {provider_name}")
                                        break
                    
                    # 如果没有指定提供商或指定的提供商不存在，使用平台映射的提供商
                    if not provider:
                        provider = self.provider_manager.get_text_provider_for_platform(platform)
                        print(f"使用平台映射的提供商: {provider.name if provider else '未找到'}")
                    
                    if provider:
                        print(f"提供商地址: {provider.base_url}")
                    
                    # 调用AI API生成文本（大纲）
                    print(f"\n=== 开始生成大纲 ===")
                    
                    # 检查provider是否存在
                    if not provider:
                        error_msg = f"未找到适合平台 {platform} 的文本提供商"
                        print(f"错误: {error_msg}")
                        raise Exception(error_msg)
                    
                    print(f"使用提供商: {provider.name}")
                    print(f"请求参数: 提示词长度={len(prompt)}, max_tokens=2000, temperature=0.7")
                    
                    # 构建包含参考图的完整提示
                    full_prompt = [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                    
                    # 如果有参考图，添加到提示中
                    if reference_images:
                        print(f"使用参考图: {len(reference_images)}张")
                        for img in reference_images:
                            full_prompt.append({
                                "type": "image_url",
                                "image_url": img
                            })
                    
                    # 如果有参考图，将参考图添加到提示中
                    if reference_images:
                        # 构建包含文本和图像的多模态提示
                        multimodal_prompt = [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                        
                        # 添加参考图
                        for img in reference_images:
                            multimodal_prompt.append(img)
                        
                        ai_result = await provider.generate_text(
                            multimodal_prompt,
                            max_tokens=2000,
                            temperature=0.7
                        )
                    else:
                        # 纯文本提示
                        ai_result = await provider.generate_text(
                            prompt,
                            max_tokens=2000,
                            temperature=0.7
                        )
                    
                    # 打印大纲生成的响应
                    print(f"大纲生成响应: {ai_result}")
                    
                    if ai_result and ai_result.get("success"):
                        print(f"AI生成成功，使用提供商: {ai_result.get('provider')}")
                        # 解析AI生成结果
                        generated_text = ai_result.get("text", "")
                        print(f"生成的文本内容: {generated_text[:200]}...")
                        
                        # 解析AI返回的内容，处理页面拆分
                        print(f"开始解析页面内容")
                        
                        # 解析AI生成的内容，提取总标题、总文案和多个图片提示词
                        def parse_generated_content(generated_text):
                            # 初始化结果
                            title = ""
                            copywriting = ""
                            image_prompts = []
                            
                            # 查找总标题 - 使用更灵活的正则表达式，不依赖换行符
                            title_match = re.search(r'【标题】：(.*?)(?=【文案】：|【图片提示词】：|$)', generated_text, re.DOTALL)
                            if title_match:
                                title = title_match.group(1).strip()
                            
                            # 查找总文案 - 使用更灵活的正则表达式，不依赖换行符
                            copywriting_match = re.search(r'【文案】：(.*?)(?=【标题】：|【图片提示词】：|$)', generated_text, re.DOTALL)
                            if copywriting_match:
                                copywriting = copywriting_match.group(1).strip()
                            
                            # 提取所有图片提示词部分（从第一个【图片提示词】：开始）
                            image_prompts_section = generated_text
                            image_start_match = re.search(r'【图片提示词】：', generated_text)
                            if image_start_match:
                                image_prompts_section = generated_text[image_start_match.start():]
                            
                            # 按<page>标签分割图片提示词
                            page_sections = image_prompts_section.split('<page>')
                            
                            for section in page_sections:
                                section = section.strip()
                                if not section:
                                    continue
                                
                                # 提取当前页面的图片提示词
                                image_prompt_match = re.search(r'【图片提示词】：(.*?)(?=\n<page>|$)', section, re.DOTALL)
                                if image_prompt_match:
                                    image_prompt = image_prompt_match.group(1).strip()
                                    if image_prompt:
                                        image_prompts.append(image_prompt)
                            
                            return title, copywriting, image_prompts
                        
                        # 使用解析函数提取内容
                        title, copywriting, image_prompts = parse_generated_content(generated_text)
                        
                        # 使用完整的生成文本作为content
                        content = generated_text
                        
                        # 生成简单标题
                        if not title:
                            title = f"[{platform.upper()}] {request.topic}"
                        
                        # 创建页面列表
                        pages = []
                        for i, image_prompt in enumerate(image_prompts):
                            pages.append({
                                "id": f"p{i+1}",
                                "type": "content",
                                "content": image_prompt,
                                "image_prompt": image_prompt
                            })
                        
                        print(f"页面拆分完成，共 {len(pages)} 页")
                        
                        # 只生成文本内容，不生成图像
                        # 图像生成只在专门的图像生成接口中调用
                        result = GenerationResult(
                            platform=platform,
                            title=title.strip(),
                            content=content.strip(),
                            images=[],
                            metadata={
                                "generation_method": "ai",
                                "provider": ai_result.get("provider"),
                                "model": ai_result.get("model"),
                                "usage": ai_result.get("usage", {}),
                                "pages": pages,  # 保存拆分后的页面信息
                                "copywriting": copywriting.strip()  # 保存总文案
                            }
                        )
                        print(f"文本生成完成，不自动生成图像")
                        
                        # 将结果添加到列表
                        results.append(result)
                    else:
                        # 如果AI生成失败，回退到模拟生成
                        error_msg = ai_result.get('error') if ai_result else '未知错误'
                        print(f"AI生成失败，使用回退模式: {error_msg}")
                        await asyncio.sleep(0.5)
                        result = GenerationResult(
                            platform=platform,
                            title=f"[{platform.upper()}] {request.topic}",
                            content=f"这是为{platform}平台生成的内容：{request.topic}",
                            images=[],
                            metadata={"generation_method": "fallback", "error": error_msg}
                        )
                        results.append(result)
                    
                    print(f"=== 平台 {platform} 生成完成 ===")
                
                # 大纲生成成功，更新历史记录状态
                if results and history_record_id:
                    # 解析最终大纲数据
                    outline_pages = []
                    page_index = 0
                    
                    for result in results:
                        # 使用之前已经提取好的title、copywriting和image_prompts
                        title = result.title.strip()
                        copywriting = result.metadata.get("copywriting", "").strip()
                        pages_data = result.metadata.get("pages", [])
                        
                        # 直接使用metadata中的pages数据构建outline_pages
                        for page_data in pages_data:
                            outline_pages.append(Page(
                                index=page_index,
                                type=page_data.get("type", "content"),
                                content=page_data.get("content", "").strip(),
                                image_prompt=page_data.get("image_prompt", "").strip()
                            ))
                            page_index += 1
                    
                    # 更新历史记录，状态为outline_success
                    final_outline = Outline(
                        raw=result.content.strip(),
                        title=title,
                        copywriting=copywriting,
                        pages=outline_pages
                    )
                    
                    from src.models.history import HistoryRecordUpdate
                    await history_service.update_history(
                        history_record_id,
                        HistoryRecordUpdate(
                            status=GenerationStatus.OUTLINE_SUCCESS,
                            outline=final_outline
                        )
                    )
            
            # 计算生成时间
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            # 根据实际生成阶段更新历史记录状态
            from src.models.history import HistoryRecordUpdate
            if results and history_record_id:
                history_service = HistoryService()
                
                # 只有在生成了图片或者完成了所有生成步骤后，才更新为SUCCESS
                # 否则保持OUTLINE_SUCCESS状态，让用户可以区分大纲生成和完整生成
                # 这里我们检查是否需要生成图片
                needs_image_generation = True  # 默认需要生成图片
                
                # 检查是否已经完成了图片生成
                # 如果没有图片生成需求，或者图片已经生成完成，才更新为SUCCESS
                # 否则保持OUTLINE_SUCCESS状态
                # 暂时注释掉自动更新为SUCCESS的逻辑，让用户可以在历史记录中看到大纲生成成功的状态
                # await history_service.update_history(
                #     history_record_id,
                #     HistoryRecordUpdate(
                #         status=GenerationStatus.SUCCESS,
                #         generation_time=generation_time
                #     )
                # )
                # 保持OUTLINE_SUCCESS状态
                pass
            
            return GenerationResponse(
                success=True,
                results=results,
                message="生成成功",
                generation_time=generation_time,
                history_id=history_record_id
            )
            
        except Exception as e:
            print(f"生成单个主题失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return GenerationResponse(
                success=False,
                results=[],
                message=f"生成失败: {str(e)}",
                generation_time=0
            )
    
    async def start_batch_generation(
        self, 
        request: BatchGenerationRequest,
        background_tasks,
        reference_images: List = None
    ) -> str:
        """启动批量生成任务"""
        job_id = str(uuid.uuid4())
        
        # 创建任务状态
        status = GenerationStatus(
            job_id=job_id,
            status="processing",
            progress={},
            total=len(request.topics) * len(request.platforms),
            completed=0,
            failed=0,
            created_at=datetime.now()
        )
        
        self.active_jobs[job_id] = status
        
        # 启动后台任务，传入参考图
        background_tasks.add_task(
            self._process_batch_generation,
            job_id,
            request,
            reference_images or []
        )
        
        return job_id
    
    async def _process_batch_generation(
        self,
        job_id: str,
        request: BatchGenerationRequest,
        reference_images: List = None
    ):
        """处理批量生成任务"""
        try:
            results = []
            total_tasks = len(request.topics) * len(request.platforms)
            
            for i, topic in enumerate(request.topics):
                for platform in request.platforms:
                    try:
                        # 生成单个内容
                        gen_request = GenerationRequest(
                            topic=topic,
                            platforms=[platform],
                            options=request.options
                        )
                        
                        response = await self.generate_single(gen_request, reference_images=reference_images or [])
                        
                        if response.success and response.results:
                            results.extend(response.results)
                            self.active_jobs[job_id].completed += 1
                        else:
                            self.active_jobs[job_id].failed += 1
                        
                        # 更新进度
                        progress = ((i * len(request.platforms) + 
                                   len(request.platforms)) / total_tasks) * 100
                        self.active_jobs[job_id].progress["overall"] = progress
                        self.active_jobs[job_id].updated_at = datetime.now()
                        
                        # 模拟异步处理延迟
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        self.active_jobs[job_id].failed += 1
                        print(f"生成失败: {str(e)}")
            
            # 更新最终状态
            if self.active_jobs[job_id]:
                self.active_jobs[job_id].status = "completed"
                self.active_jobs[job_id].results = results
                self.active_jobs[job_id].updated_at = datetime.now()
                
        except Exception as e:
            if self.active_jobs.get(job_id):
                self.active_jobs[job_id].status = "failed"
                self.active_jobs[job_id].updated_at = datetime.now()
            print(f"批量生成任务失败: {str(e)}")
    
    async def get_batch_status(self, job_id: str) -> Optional[GenerationStatus]:
        """获取批量生成状态"""
        return self.active_jobs.get(job_id)
    
    async def get_batch_results(self, job_id: str) -> Optional[List[GenerationResult]]:
        """获取批量生成结果"""
        status = self.active_jobs.get(job_id)
        if status and status.status == "completed":
            return status.results
        return None

    async def generate_single_image(self, prompt: str, image_provider: str, reference_images: List[Dict[str, Any]] = None, history_id: Optional[str] = None, page_index: Optional[int] = None, image_id: Optional[str] = None) -> Dict[str, Any]:
        """
        生成单张图片
        
        Args:
            prompt: 生成图片的提示词
            image_provider: 使用的图像提供商名称
            reference_images: 参考图片列表，base64编码或URL
            history_id: 历史记录ID，用于保存图片到指定目录
            page_index: 页面索引，用于命名图片
            image_id: 图片ID，用于替换原有图片
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        print(f"\n=== 开始生成单张图片 ===")
        print(f"提示词: {prompt[:100]}...")
        print(f"使用提供商: {image_provider}")
        print(f"历史记录ID: {history_id}")
        print(f"页面索引: {page_index}")
        print(f"图片ID: {image_id}")
        
        # 添加参考图片处理日志
        if reference_images:
            print(f"收到参考图片数量: {len(reference_images)}")
            for i, img in enumerate(reference_images):
                if isinstance(img, dict):
                    img_type = img.get('type', 'unknown')
                    print(f"  参考图片 {i+1} 类型: {img_type}")
                    if img_type == 'image_url':
                        img_url = img.get('image_url', '')
                        print(f"  参考图片 {i+1} URL: {img_url[:100]}...")
                else:
                    print(f"  参考图片 {i+1} 格式: {type(img)}")
        else:
            print("未收到参考图片")

        start_time = datetime.now()

        try:
            # 初始化提供商管理器
            if not await self.initialize_provider_manager():
                print("提供商管理器未初始化，无法生成图片")
                return {
                    "success": False,
                    "error": "提供商管理器未初始化"
                }
            
            # 获取指定的图像提供商
            provider_config = self.provider_manager.image_providers.get(image_provider)
            if not provider_config:
                print(f"未找到指定的图像提供商: {image_provider}")
                print(f"当前可用的图像提供商: {list(self.provider_manager.image_providers.keys())}")
                # 尝试重新加载提供商配置
                print("尝试重新加载提供商配置...")
                await self.provider_manager.load_image_providers(force_reload=True)
                # 再次尝试获取
                provider_config = self.provider_manager.image_providers.get(image_provider)
                if not provider_config:
                    return {
                        "success": False,
                        "error": f"未找到指定的图像提供商: {image_provider}。可用的提供商: {list(self.provider_manager.image_providers.keys())}"
                    }
            
            provider = provider_config["provider"]
            if not provider.is_available():
                print(f"图像提供商 {image_provider} 不可用")
                return {
                    "success": False,
                    "error": f"图像提供商 {image_provider} 不可用"
                }
            
            print(f"提供商地址: {provider.base_url}")
            print(f"使用模型: {provider.model}")
            
            # 准备图像生成参数
            generation_params = {
                "prompt": prompt,
                "platform": "general",
                "size": "1024x1792",
                "n": 1
            }
            
            # 如果有参考图片，添加到生成参数中
            if reference_images:
                generation_params["reference_images"] = reference_images
                print(f"传递 {len(reference_images)} 张参考图片到图像生成API")
            
            # 调用图像生成API
            image_result = await provider.generate_image(**generation_params)

            print(f"图像生成结果: {image_result}")

            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()

            if image_result and image_result.get("success") and image_result.get("images"):
                # 生成成功
                generated_image_data = image_result["images"][0]
                print(f"图像生成成功")
                
                # 保存图片到本地文件夹
                from src.utils.image_utils import process_image, replace_image
                from pathlib import Path
                import uuid
                
                image_path = None
                
                # 确定保存目录
                if history_id:
                    # 保存到历史记录对应的图片目录
                    save_dir = Path(__file__).parent.parent.parent / "history" / f"{history_id}_images"
                else:
                    # 保存到默认上传目录，但添加前缀，便于清理
                    from uuid import uuid4
                    temp_prefix = f"temp_{uuid4().hex[:8]}"
                    save_dir = Path(__file__).parent.parent.parent / "uploads" / temp_prefix
                
                # 确保保存目录存在
                save_dir.mkdir(exist_ok=True, parents=True)
                
                # 生成文件名
                if image_id:
                    # 替换原有图片，使用相同的文件名
                    filename = f"{image_id}.png"
                else:
                    # 新生成图片，生成唯一文件名
                    filename = f"{uuid.uuid4()}.png"
                
                # 处理生成的图片
                if generated_image_data.startswith("http://") or generated_image_data.startswith("https://"):
                    # URL类型，下载保存
                    if image_id and history_id:
                        # 替换原有图片
                        old_image_path = str(save_dir / filename)
                        image_path = replace_image(old_image_path, generated_image_data)
                    else:
                        # 新保存图片
                        image_path = process_image(generated_image_data, save_dir, filename)
                elif generated_image_data.startswith("data:image/"):
                    # Base64类型，解码保存
                    image_path = process_image(generated_image_data, save_dir, filename)
                else:
                    # 其他格式，尝试处理为相对URL
                    # 生成完整的文件路径
                    save_path = save_dir / filename
                    # 将生成的数据写入文件
                    with open(save_path, 'wb') as f:
                        if isinstance(generated_image_data, bytes):
                            f.write(generated_image_data)
                        else:
                            f.write(generated_image_data.encode('utf-8'))
                    # 返回相对URL
                    if history_id:
                        # 历史记录图片，返回 /history/xxx_images/filename.png 格式
                        image_path = f"/history/{save_dir.name}/{filename}"
                    else:
                        # 上传图片，返回 /uploads/temp_xxx/filename.png 格式
                        image_path = f"/uploads/{save_dir.name}/{filename}"
                
                # 生成成功，返回结果
                print(f"图片保存成功，路径: {image_path}")
                return {
                    "success": True,
                    "image_url": image_path,
                    "image_id": image_id or filename.split('.')[0],
                    "provider": image_provider,
                    "generation_time": generation_time,
                    "images": image_result.get("images", [])
                }
            else:
                # 生成失败
                error_msg = image_result.get("error", "图像生成失败")
                print(f"图像生成失败: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "provider": image_provider,
                    "generation_time": generation_time
                }

        except Exception as e:
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            print(f"生成单张图片异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"生成图片异常: {str(e)}",
                "generation_time": generation_time
            }
        finally:
            print("=== 单张图片生成结束 ===")
    
    async def regenerate_image(self, image_id: str, prompt: str) -> str:
        """重新生成单张图片"""
        # 模拟图片重新生成
        await asyncio.sleep(1.0)
        new_image_id = f"regen_{uuid.uuid4().hex[:8]}"
        return new_image_id
    
    async def cancel_batch_generation(self, job_id: str) -> bool:
        """取消批量生成任务"""
        if job_id in self.active_jobs:
            self.active_jobs[job_id].status = "cancelled"
            self.active_jobs[job_id].updated_at = datetime.now()
            return True
        return False