"""
配置管理API
提供配置查看和更新接口
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import yaml
from pathlib import Path

from src.services.config_service import ConfigService

router = APIRouter()


@router.get("/config/templates")
async def get_platform_templates() -> Dict[str, Any]:
    """获取平台模板配置"""
    
    try:
        service = ConfigService()
        templates = service.get_platform_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板配置失败: {str(e)}")


@router.get("/config/template/{platform}")
async def get_platform_template(platform: str) -> Dict[str, Any]:
    """获取指定平台模板"""
    
    try:
        service = ConfigService()
        template = service.get_platform_template(platform)
        if not template:
            raise HTTPException(status_code=404, detail=f"平台 {platform} 不存在")
        return {"platform": platform, "template": template}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}")


@router.post("/config/template/{platform}")
async def update_platform_template(
    platform: str, 
    template: Dict[str, Any]
) -> Dict[str, str]:
    """更新平台模板配置"""
    
    try:
        service = ConfigService()
        success = service.update_platform_template(platform, template)
        if not success:
            raise HTTPException(status_code=400, detail="模板配置无效")
        return {"message": "模板更新成功", "platform": platform}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新模板失败: {str(e)}")


@router.delete("/config/template/{platform}")
async def delete_platform_template(
    platform: str
) -> Dict[str, str]:
    """删除平台模板配置"""
    
    try:
        service = ConfigService()
        success = service.delete_platform_template(platform)
        if not success:
            raise HTTPException(status_code=404, detail=f"平台 {platform} 不存在或已被删除")
        return {"message": "模板删除成功", "platform": platform}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除模板失败: {str(e)}")


@router.get("/config/providers/text")
async def get_text_providers() -> Dict[str, Any]:
    """获取文本生成提供商配置"""
    
    try:
        service = ConfigService()
        providers = service.get_text_providers()
        return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文本提供商配置失败: {str(e)}")


@router.get("/config/providers/image")
async def get_image_providers() -> Dict[str, Any]:
    """获取图像生成提供商配置"""
    
    try:
        service = ConfigService()
        providers = service.get_image_providers()
        return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图像提供商配置失败: {str(e)}")


@router.get("/config/providers/video")
async def get_video_providers() -> Dict[str, Any]:
    """获取视频生成提供商配置"""
    try:
        # 目前不支持视频生成，返回空列表
        return {"providers": {"providers": {}}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取视频提供商配置失败: {str(e)}")


@router.post("/config/provider/text/{provider_name}")
async def update_text_provider(
    provider_name: str,
    config: Dict[str, Any]
) -> Dict[str, str]:
    """更新文本提供商配置"""
    
    try:
        service = ConfigService()
        success = service.update_text_provider(provider_name, config)
        if not success:
            raise HTTPException(status_code=400, detail="提供商配置无效")
        return {"message": "文本提供商配置更新成功", "provider": provider_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新文本提供商失败: {str(e)}")


@router.delete("/config/provider/text/{provider_name}")
async def delete_text_provider(
    provider_name: str
) -> Dict[str, str]:
    """删除文本提供商配置"""
    
    try:
        service = ConfigService()
        success = service.delete_text_provider(provider_name)
        if not success:
            raise HTTPException(status_code=404, detail="提供商不存在")
        return {"message": "文本提供商删除成功", "provider": provider_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文本提供商失败: {str(e)}")


@router.post("/config/provider/image/{provider_name}")
async def update_image_provider(
    provider_name: str,
    config: Dict[str, Any]
) -> Dict[str, str]:
    """更新图像提供商配置"""
    
    try:
        service = ConfigService()
        success = service.update_image_provider(provider_name, config)
        if not success:
            raise HTTPException(status_code=400, detail="提供商配置无效")
        return {"message": "图像提供商配置更新成功", "provider": provider_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新图像提供商失败: {str(e)}")


@router.delete("/config/provider/image/{provider_name}")
async def delete_image_provider(
    provider_name: str
) -> Dict[str, str]:
    """删除图像提供商配置"""
    
    try:
        service = ConfigService()
        success = service.delete_image_provider(provider_name)
        if not success:
            raise HTTPException(status_code=404, detail="提供商不存在")
        return {"message": "图像提供商删除成功", "provider": provider_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除图像提供商失败: {str(e)}")

@router.post("/config/provider/test/{provider_type}/{provider_name}")
async def test_provider_connection(
    provider_type: str,
    provider_name: str
) -> Dict[str, bool]:
    """测试现有提供商连接"""
    
    try:
        # 获取提供商管理器
        from src.providers.provider_manager import ProviderManager
        from src.services.config_service import ConfigService
        
        provider_manager = ProviderManager()
        config_service = ConfigService()
        
        # 获取提供商配置
        provider_config = None
        if provider_type == "text":
            text_config = config_service.get_text_providers()
            provider_config = text_config.get("providers", {}).get(provider_name)
        elif provider_type == "image":
            image_config = config_service.get_image_providers()
            provider_config = image_config.get("providers", {}).get(provider_name)
        else:
            raise HTTPException(status_code=400, detail="无效的提供商类型")
        
        if not provider_config:
            raise HTTPException(status_code=404, detail=f"{provider_type}提供商不存在")
        
        # 使用配置测试连接
        if provider_type == "text":
            result = await provider_manager.test_text_provider_connection(provider_config)
            return {"success": result}
        elif provider_type == "image":
            result = await provider_manager.test_image_provider_connection(provider_config)
            return {"success": result}
        else:
            raise HTTPException(status_code=400, detail="无效的提供商类型")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试连接失败: {str(e)}")


@router.post("/config/provider/test/{provider_type}")
async def test_provider_connection_with_config(
    provider_type: str,
    provider_config: Dict[str, Any]
) -> Dict[str, bool]:
    """使用提供的配置测试提供商连接"""
    
    try:
        # 获取提供商管理器
        from src.providers.provider_manager import ProviderManager
        provider_manager = ProviderManager()
        
        # 测试连接
        if provider_type == "text":
            # 测试文本提供商
            result = await provider_manager.test_text_provider_connection(provider_config)
            return {"success": result}
        elif provider_type == "image":
            # 测试图像提供商
            result = await provider_manager.test_image_provider_connection(provider_config)
            return {"success": result}
        else:
            raise HTTPException(status_code=400, detail="无效的提供商类型")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试连接失败: {str(e)}")


@router.post("/config/reload")
async def reload_config() -> Dict[str, str]:
    """重新加载配置文件"""
    
    try:
        service = ConfigService()
        service.reload_config()
        return {"message": "配置重新加载成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新加载配置失败: {str(e)}")


@router.get("/config/export")
async def export_config() -> Dict[str, Any]:
    """导出当前配置"""
    
    try:
        service = ConfigService()
        config = service.export_all_config()
        return {"config": config, "exported_at": service.get_current_time()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出配置失败: {str(e)}")