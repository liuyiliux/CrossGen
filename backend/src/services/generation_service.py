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
    """内容生成服务"""
    
    def __init__(self):
        self.active_jobs: Dict[str, GenerationStatus] = {}
        self.provider_manager: Optional[ProviderManager] = None
        self.provider_manager_loaded = False
    
    async def initialize_provider_manager(self) -> bool:
        """初始化提供商管理器
        
        Returns:
            bool: 初始化是否成功
        """
        if self.provider_manager_loaded and self.provider_manager:
            return True
        
        try:
            self.provider_manager = ProviderManager()
            await self.provider_manager.load_providers()
            self.provider_manager_loaded = True
            return True
        except Exception as e:
            print(f"初始化提供商管理器失败: {str(e)}")
            return False
    
    async def generate_single(self, request: GenerationRequest) -> GenerationResponse:
        """生成单个主题的内容"""
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
                        
                        # 简单解析标题和内容
                        lines = generated_text.split("\n")
                        title = lines[0] if lines else f"[{platform.upper()}] {request.topic}"
                        content = "\n".join(lines[1:]) if len(lines) > 1 else generated_text
                        
                        # 解析页面信息，查找<page>标签
                        pages = []
                        if "<page>" in content:
                            print(f"发现<page>标签，开始拆分页面")
                            # 拆分页面
                            page_sections = content.split("<page>")
                            for i, section in enumerate(page_sections):
                                section = section.strip()
                                if section:
                                    pages.append({
                                        "id": f"p{i+1}",
                                        "type": "content",
                                        "content": section
                                    })
                            print(f"页面拆分完成，共 {len(pages)} 页")
                        else:
                            # 如果没有<page>标签，将整个内容作为一页
                            pages.append({
                                "id": "p1",
                                "type": "content",
                                "content": content
                            })
                            print(f"没有发现<page>标签，将内容作为单页处理")
                        
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
                                "pages": pages  # 保存拆分后的页面信息
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
                        # 解析内容中的<page>标签
                        content = result.content
                        
                        # 查找第一个[标签]作为页面类型，没有则默认为content
                        page_type = "content"
                        type_match = re.search(r'\[(\w+)\]', content)
                        if type_match:
                            page_type = type_match.group(1)
                        
                        # 处理单页情况
                        if "<page>" not in content:
                            outline_pages.append(Page(
                                index=page_index,
                                type=page_type,
                                content=content.strip()
                            ))
                            page_index += 1
                        else:
                            # 处理多页情况，分割<page>标签
                            pages = content.split("<page>")
                            for page_content in pages:
                                page_content = page_content.strip()
                                if page_content:
                                    # 查找当前页面的类型
                                    current_type = page_type
                                    type_match = re.search(r'\[(\w+)\]', page_content)
                                    if type_match:
                                        current_type = type_match.group(1)
                                    
                                    outline_pages.append(Page(
                                        index=page_index,
                                        type=current_type,
                                        content=page_content
                                    ))
                                    page_index += 1
                    
                    # 更新历史记录，状态为outline_success
                    final_outline = Outline(
                        raw=f"生成主题: {request.topic}\n平台: {platform_values}",
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
        background_tasks
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
        
        # 启动后台任务
        background_tasks.add_task(
            self._process_batch_generation,
            job_id,
            request
        )
        
        return job_id
    
    async def _process_batch_generation(
        self,
        job_id: str,
        request: BatchGenerationRequest
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
                        
                        response = await self.generate_single(gen_request)
                        
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
    
    async def generate_single_image(self, prompt: str, image_provider: str) -> Dict[str, Any]:
        """生成单张图片
        
        Args:
            prompt: 生成图片的提示词
            image_provider: 使用的图像提供商名称
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        print(f"\n=== 开始生成单张图片 ===")
        print(f"提示词: {prompt[:100]}...")
        print(f"使用提供商: {image_provider}")
        
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
                return {
                    "success": False,
                    "error": f"未找到指定的图像提供商: {image_provider}"
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
            
            # 调用图像生成API
            image_result = await provider.generate_image(
                prompt,
                "general",  # 通用平台
                size="1024x1792",  # 默认尺寸
                n=1  # 生成1张图片
            )
            
            print(f"图像生成结果: {image_result}")
            
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            if image_result and image_result.get("success") and image_result.get("images"):
                # 生成成功
                image_url = image_result["images"][0]
                print(f"图像生成成功，URL: {image_url}")
                return {
                    "success": True,
                    "image_url": image_url,
                    "provider": image_provider,
                    "model": provider.model,
                    "generation_time": generation_time
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