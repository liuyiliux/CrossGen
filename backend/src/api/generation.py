"""
内容生成API
提供文本和图像生成相关接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Form, File, UploadFile, Body, Request, Response
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from src.services.generation_service import GenerationService
from src.models.generation import (
    GenerationRequest,
    GenerationResponse,
    BatchGenerationRequest,
    BatchGenerationResponse,
    GenerationStatus,
    PlatformType
)

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_content(
    request: Request,
    topic: Optional[str] = Form(None),
    platform: Optional[str] = Form(None),
    text_provider: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None)
) -> GenerationResponse:
    """单个内容生成请求
    
    支持两种请求格式：
    1. JSON格式：符合GenerationRequest模型
    2. multipart/form-data格式：用于支持文件上传
    """
    
    try:
        # 获取请求内容类型
        content_type = request.headers.get("content-type", "")
        
        reference_images = []
        
        # 如果是JSON请求
        if "application/json" in content_type:
            request_body = await request.json()
            generation_request = GenerationRequest(**request_body)
            # 从JSON请求中提取参考图
            if request_body.get("reference_images"):
                reference_images = request_body.get("reference_images")
        # 如果是表单请求
        elif "multipart/form-data" in content_type:
            # 处理文件上传
            if images:
                # 读取上传的图片并转换为base64
                import base64
                for image in images:
                    image_data = await image.read()
                    base64_image = base64.b64encode(image_data).decode("utf-8")
                    reference_images.append({
                        "type": "image_url",
                        "image_url": f"data:{image.content_type};base64,{base64_image}"
                    })
            
            if not topic or not platform:
                raise HTTPException(status_code=422, detail="请求格式错误，缺少必要参数")
            
            generation_request = GenerationRequest(
                topic=topic,
                platforms=[PlatformType(platform)],
                text_provider=text_provider
            )
        else:
            raise HTTPException(status_code=415, detail="不支持的媒体类型")
        
        service = GenerationService()
        result = await service.generate_single(generation_request, reference_images=reference_images)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/batch", response_model=BatchGenerationResponse)
async def batch_generate(
    request: Request,
    background_tasks: BackgroundTasks,
    topics: Optional[str] = Form(None),
    platforms: Optional[str] = Form(None),
    text_provider: Optional[str] = Form(None),
    reference_images: Optional[List[UploadFile]] = File(None)
) -> BatchGenerationResponse:
    """批量生成请求
    
    支持两种请求格式：
    1. JSON格式：符合BatchGenerationRequest模型
    2. multipart/form-data格式：用于支持文件上传
    """
    
    try:
        # 获取请求内容类型
        content_type = request.headers.get("content-type", "")
        
        ref_images_list = []
        
        # 如果是JSON请求
        if "application/json" in content_type:
            request_body = await request.json()
            batch_request = BatchGenerationRequest(**request_body)
            # 从JSON请求中提取参考图
            if request_body.get("reference_images"):
                ref_images_list = request_body.get("reference_images")
        # 如果是表单请求
        elif "multipart/form-data" in content_type:
            # 处理文件上传
            if reference_images:
                # 读取上传的图片并转换为base64
                import base64
                for image in reference_images:
                    image_data = await image.read()
                    base64_image = base64.b64encode(image_data).decode("utf-8")
                    ref_images_list.append({
                        "type": "image_url",
                        "image_url": f"data:{image.content_type};base64,{base64_image}"
                    })
            
            if not topics or not platforms:
                raise HTTPException(status_code=422, detail="请求格式错误，缺少必要参数")
            
            # 解析JSON字符串
            import json
            topics_list = json.loads(topics)
            platforms_list = json.loads(platforms)
            
            batch_request = BatchGenerationRequest(
                topics=topics_list,
                platforms=platforms_list
            )
        else:
            raise HTTPException(status_code=415, detail="不支持的媒体类型")
        
        service = GenerationService()
        job_id = await service.start_batch_generation(batch_request, background_tasks, reference_images=ref_images_list)
        return BatchGenerationResponse(
            job_id=job_id,
            status="processing",
            message="批量生成任务已启动",
            created_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量生成启动失败: {str(e)}")


@router.get("/batch/{job_id}/status", response_model=GenerationStatus)
async def get_batch_status(job_id: str) -> GenerationStatus:
    """查询批量生成状态"""
    
    try:
        service = GenerationService()
        status = await service.get_batch_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="任务不存在")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询状态失败: {str(e)}")


@router.get("/batch/{job_id}/results")
async def get_batch_results(job_id: str) -> Dict[str, Any]:
    """获取批量生成结果"""
    
    try:
        service = GenerationService()
        results = await service.get_batch_results(job_id)
        if not results:
            raise HTTPException(status_code=404, detail="任务不存在或未完成")
        return {"job_id": job_id, "results": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")


@router.post("/image/regenerate/{image_id}")
async def regenerate_image(image_id: str, prompt: str) -> Dict[str, str]:
    """重新生成单张图片"""
    
    try:
        service = GenerationService()
        new_image_id = await service.regenerate_image(image_id, prompt)
        return {
            "message": "图片重新生成成功",
            "original_image_id": image_id,
            "new_image_id": new_image_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成失败: {str(e)}")


@router.post("/generate/image")
async def generate_single_image(
    history_id: str = Body(..., description="历史记录ID"),
    page_index: int = Body(..., description="页面索引"),
    prompt: str = Body(..., description="生成提示词"),
    image_provider: str = Body(..., description="图像提供商名称"),
    reference_images: List[Dict[str, Any]] = Body(None, description="参考图片列表"),
    use_cover_as_reference: bool = Body(False, description="是否使用封面作为参考图"),
    image_id: Optional[str] = Body(None, description="图片ID，用于替换原有图片")
) -> Dict[str, Any]:
    """生成单张图片"""
    
    try:
        from src.services.history_service import HistoryService
        from src.models.history import HistoryRecordUpdate, GenerationStatus, GeneratedImage
        from src.services.generation_service import GenerationService
        
        # 获取历史记录服务
        history_service = HistoryService()
        
        # 获取历史记录
        history = await history_service.get_history_by_id(history_id)
        if not history:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        
        # 如果使用封面作为参考图，获取封面图
        processed_reference_images = reference_images or []
        if use_cover_as_reference and history.images:
            # 找到封面图（通常是第一张图片或标记为封面）
            cover_image = None
            for img in history.images:
                if img.index == 0:  # 假设封面是 index=0 的图片
                    cover_image = img
                    break
            
            if cover_image and cover_image.url:
                print(f"获取到封面图: {cover_image.url}")
                # 检查封面图URL类型
                if cover_image.url.startswith("http://") or cover_image.url.startswith("https://"):
                    # HTTP URL，下载并转换为 base64
                    import httpx
                    try:
                        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                            response = await client.get(cover_image.url)
                            response.raise_for_status()
                            image_data = response.content
                            import base64
                            base64_image = base64.b64encode(image_data).decode("utf-8")
                            # 尝试从响应头获取 content-type
                            content_type = response.headers.get("content-type", "image/png")
                            processed_reference_images.append({
                                "type": "image_url",
                                "image_url": f"data:{content_type};base64,{base64_image}"
                            })
                            print(f"封面图已转换为 base64 格式，长度: {len(base64_image)}")
                    except Exception as e:
                        print(f"下载封面图失败: {str(e)}")
                else:
                    # 本地相对路径，需要转换为完整的URL或base64
                    from pathlib import Path
                    import base64
                    
                    # 构建完整的文件路径
                    base_dir = Path(__file__).parent.parent.parent
                    image_path = base_dir / cover_image.url.lstrip('/')
                    
                    print(f"封面图本地路径: {image_path}")
                    
                    try:
                        # 读取本地图片并转换为base64
                        with open(image_path, 'rb') as f:
                            image_data = f.read()
                        base64_image = base64.b64encode(image_data).decode("utf-8")
                        # 尝试从文件扩展名获取content-type
                        content_type = "image/png"
                        if image_path.suffix.lower() in ('.jpg', '.jpeg'):
                            content_type = "image/jpeg"
                        elif image_path.suffix.lower() == '.gif':
                            content_type = "image/gif"
                        elif image_path.suffix.lower() == '.webp':
                            content_type = "image/webp"
                        
                        processed_reference_images.append({
                            "type": "image_url",
                            "image_url": f"data:{content_type};base64,{base64_image}"
                        })
                        print(f"封面图已转换为base64格式，长度: {len(base64_image)}")
                    except Exception as e:
                        print(f"读取本地封面图失败: {str(e)}")
                        print(f"尝试读取的文件路径: {image_path}")
                        # 如果读取失败，尝试构建完整的URL
                        full_url = f"http://localhost:8000{cover_image.url}"
                        processed_reference_images.append({
                            "type": "image_url",
                            "image_url": full_url
                        })
                        print(f"封面图已转换为完整URL: {full_url}")
        
        # 更新历史记录状态为image_generating
        await history_service.update_history(
            history_id,
            HistoryRecordUpdate(status=GenerationStatus.IMAGE_GENERATING)
        )
        
        # 生成图片（传递处理后的参考图）
        service = GenerationService()
        result = await service.generate_single_image(prompt, image_provider, processed_reference_images, history_id, page_index, image_id)
        
        print(f"生成图片结果: {result}")
        
        if result.get("success"):
            # 图片生成成功，创建GeneratedImage对象
            generated_image = GeneratedImage(
                id=result.get("image_id") or f"temp_{uuid.uuid4().hex[:8]}",  # 确保id不为None
                index=page_index,
                url=result.get("image_url") or "",  # 确保url不为None
                status="success"
            )
            
            print(f"创建GeneratedImage对象: {generated_image}")
            print(f"当前历史记录中的图片数量: {len(history.images)}")
            print(f"当前历史记录中的图片: {[img.model_dump() for img in history.images]}")
            
            # 更新历史记录，添加生成的图片
            current_images = history.images.copy()
            print(f"当前images副本: {[img.model_dump() for img in current_images]}")
            
            # 检查是否已有该页面的图片，有则更新，无则添加
            updated = False
            for i, img in enumerate(current_images):
                print(f"检查图片 {i}: index={img.index}, page_index={page_index}")
                if img.index == page_index:
                    current_images[i] = generated_image
                    updated = True
                    print(f"已更新图片 {i}，新图片: {generated_image.model_dump()}")
                    break
            
            if not updated:
                current_images.append(generated_image)
                print(f"已添加新图片: {generated_image.model_dump()}")
            
            print(f"更新前历史记录状态: {history.status}")
            print(f"更新后图片列表: {[img.model_dump() for img in current_images]}")
            
            # 更新历史记录状态和图片
            update_result = await history_service.update_history(
                history_id,
                HistoryRecordUpdate(
                    status=GenerationStatus.IMAGE_SUCCESS,
                    images=current_images
                )
            )
            
            print(f"历史记录更新结果: {update_result is not None}")
            if update_result:
                print(f"更新后的历史记录图片数量: {len(update_result.images)}")
                print(f"更新后的历史记录图片: {[img.model_dump() for img in update_result.images]}")
        else:
            # 图片生成失败，更新历史记录状态
            await history_service.update_history(
                history_id,
                HistoryRecordUpdate(status=GenerationStatus.IMAGE_FAILED)
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成图片失败: {str(e)}")


@router.post("/retry/outline/{history_id}")
async def retry_outline(history_id: str) -> Dict[str, Any]:
    """重试大纲生成"""
    
    try:
        from src.services.history_service import HistoryService
        from src.models.history import HistoryRecordUpdate, GenerationStatus, HistoryRecordCreate, Outline, Page
        from src.models.generation import GenerationRequest, PlatformType
        from src.services.generation_service import GenerationService
        
        # 获取历史记录服务
        history_service = HistoryService()
        
        # 获取历史记录
        history = await history_service.get_history_by_id(history_id)
        if not history:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        
        # 创建新的历史记录，状态为outline_generating
        new_history = await history_service.create_history(HistoryRecordCreate(
            topic=history.topic,
            platform=history.platform,
            outline=Outline(
                raw=history.outline.raw,
                pages=[Page(index=0, type="content", content="大纲生成中...")]
            ),
            images=[],
            status=GenerationStatus.OUTLINE_GENERATING,
            generation_time=0,
            text_model=history.text_model,
            image_model=history.image_model
        ))
        
        # 创建生成请求
        generation_request = GenerationRequest(
            topic=history.topic,
            platforms=[PlatformType(history.platform)]
        )
        
        # 执行生成
        service = GenerationService()
        result = await service.generate_single(generation_request)
        
        return {
            "success": True,
            "message": "大纲重试成功",
            "history_id": new_history.id,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"大纲重试失败: {str(e)}")


@router.post("/retry/image/{history_id}")
async def retry_image(
    history_id: str,
    page_index: int = Body(..., description="页面索引"),
    prompt: str = Body(..., description="生成提示词"),
    image_provider: str = Body(..., description="图像提供商名称"),
    use_cover_as_reference: bool = Body(False, description="是否使用封面作为参考图")
) -> Dict[str, Any]:
    """重试图片生成"""
    
    try:
        from src.services.history_service import HistoryService
        from src.models.history import HistoryRecordUpdate, GenerationStatus, GeneratedImage
        from src.services.generation_service import GenerationService
        
        # 获取历史记录服务
        history_service = HistoryService()
        
        # 获取历史记录
        history = await history_service.get_history_by_id(history_id)
        if not history:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        
        # 如果使用封面作为参考图，获取封面图
        processed_reference_images = []
        if use_cover_as_reference and history.images:
            # 找到封面图（通常是第一张图片或标记为封面）
            cover_image = None
            for img in history.images:
                if img.index == 0:  # 假设封面是 index=0 的图片
                    cover_image = img
                    break
            
            if cover_image and cover_image.url:
                print(f"重试接口 - 获取到封面图: {cover_image.url}")
                
                # 检查封面图URL类型
                if cover_image.url.startswith("http://") or cover_image.url.startswith("https://"):
                    # HTTP URL，下载并转换为 base64
                    import httpx
                    try:
                        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                            response = await client.get(cover_image.url)
                            response.raise_for_status()
                            image_data = response.content
                            import base64
                            base64_image = base64.b64encode(image_data).decode("utf-8")
                            # 尝试从响应头获取 content-type
                            content_type = response.headers.get("content-type", "image/png")
                            processed_reference_images.append({
                                "type": "image_url",
                                "image_url": f"data:{content_type};base64,{base64_image}"
                            })
                            print(f"封面图已转换为 base64 格式，长度: {len(base64_image)}")
                    except Exception as e:
                        print(f"下载封面图失败: {str(e)}")
                else:
                    # 本地相对路径，需要转换为完整的URL或base64
                    from pathlib import Path
                    import base64
                    
                    # 构建完整的文件路径
                    base_dir = Path(__file__).parent.parent.parent
                    image_path = base_dir / cover_image.url.lstrip('/')
                    
                    print(f"封面图本地路径: {image_path}")
                    
                    try:
                        # 读取本地图片并转换为base64
                        with open(image_path, 'rb') as f:
                            image_data = f.read()
                        base64_image = base64.b64encode(image_data).decode("utf-8")
                        # 尝试从文件扩展名获取content-type
                        content_type = "image/png"
                        if image_path.suffix.lower() in ('.jpg', '.jpeg'):
                            content_type = "image/jpeg"
                        elif image_path.suffix.lower() == '.gif':
                            content_type = "image/gif"
                        elif image_path.suffix.lower() == '.webp':
                            content_type = "image/webp"
                        
                        processed_reference_images.append({
                            "type": "image_url",
                            "image_url": f"data:{content_type};base64,{base64_image}"
                        })
                        print(f"封面图已转换为base64格式，长度: {len(base64_image)}")
                    except Exception as e:
                        print(f"读取本地封面图失败: {str(e)}")
                        print(f"尝试读取的文件路径: {image_path}")
                        # 如果读取失败，尝试构建完整的URL
                        full_url = f"http://localhost:8000{cover_image.url}"
                        processed_reference_images.append({
                            "type": "image_url",
                            "image_url": full_url
                        })
                        print(f"封面图已转换为完整URL: {full_url}")
        
        # 更新历史记录状态为image_generating
        await history_service.update_history(
            history_id,
            HistoryRecordUpdate(status=GenerationStatus.IMAGE_GENERATING)
        )
        
        # 生成图片（传递处理后的参考图）
        service = GenerationService()
        result = await service.generate_single_image(prompt, image_provider, processed_reference_images)
        
        if result.get("success"):
            # 图片生成成功，创建GeneratedImage对象
            generated_image = GeneratedImage(
                index=page_index,
                url=result.get("image_url") or "",  # 确保url不为None
                status="success"
            )
            
            # 更新历史记录，添加生成的图片
            current_images = history.images.copy()
            
            # 检查是否已有该页面的图片，有则更新，无则添加
            updated = False
            for i, img in enumerate(current_images):
                if img.index == page_index:
                    current_images[i] = generated_image
                    updated = True
                    break
            
            if not updated:
                current_images.append(generated_image)
            
            # 更新历史记录状态和图片
            await history_service.update_history(
                history_id,
                HistoryRecordUpdate(
                    status=GenerationStatus.IMAGE_SUCCESS,
                    images=current_images
                )
            )
        else:
            # 图片生成失败，更新历史记录状态
            await history_service.update_history(
                history_id,
                HistoryRecordUpdate(status=GenerationStatus.IMAGE_FAILED)
            )
        
        return {
            "success": True,
            "message": "图片重试成功",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片重试失败: {str(e)}")


@router.delete("/batch/{job_id}")
async def cancel_batch_generation(job_id: str) -> Dict[str, str]:
    """
    取消批量生成任务
    """
    
    try:
        service = GenerationService()
        success = await service.cancel_batch_generation(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在或无法取消")
        return {"message": "任务已取消", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")


@router.get("/image/download")
async def download_image(url: str):
    """
    图片代理下载
    
    Args:
        url: 原始图片URL
        
    Returns:
        图片内容
    """
    
    try:
        import httpx
        
        # 创建HTTP客户端
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # 发送请求获取图片内容
            response = await client.get(url)
            response.raise_for_status()
            
            # 获取文件类型
            content_type = response.headers.get("content-type", "image/png")
            
            # 返回图片内容
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename={uuid.uuid4()}.png"
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载图片失败: {str(e)}")


@router.get("/image/download-all")
async def download_all_images(image_urls: str):
    """
    打包下载所有图片
    
    Args:
        image_urls: 图片URL列表，JSON格式
        
    Returns:
        ZIP压缩包
    """
    
    try:
        import httpx
        import io
        import zipfile
        import json
        
        # 解析图片URL列表
        urls = json.loads(image_urls)
        if not urls or not isinstance(urls, list):
            raise HTTPException(status_code=400, detail="无效的图片URL列表")
        
        # 创建内存中的ZIP文件
        zip_buffer = io.BytesIO()
        
        # 创建HTTP客户端
        async with httpx.AsyncClient(follow_redirects=True) as client:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # 下载并添加每张图片到ZIP文件
                for index, url in enumerate(urls):
                    try:
                        # 下载图片
                        response = await client.get(url)
                        response.raise_for_status()
                        
                        # 生成文件名
                        filename = f"yiliu_page_{index + 1}.png"
                        
                        # 添加到ZIP文件
                        zip_file.writestr(filename, response.content)
                    except Exception as e:
                        print(f"下载图片失败 {url}: {str(e)}")
                        continue
        
        # 重置文件指针到开始位置
        zip_buffer.seek(0)
        
        # 返回ZIP文件
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=yiliu_images.zip"
            }
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"打包下载失败: {str(e)}")