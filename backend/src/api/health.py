"""
健康检查API
提供系统状态和健康检查接口
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import time
import psutil
from src.utils.config import settings
from src.utils.redis import redis_manager

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """系统健康检查"""
    
    redis_status = "unknown"
    try:
        redis_status = redis_manager.get_status()
    except Exception:
        redis_status = "disconnected"
    
    # 获取系统信息
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "services": {
            "redis": redis_status,
        },
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_usage_percent": (disk.used / disk.total) * 100
        }
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """就绪检查"""
    
    # 检查关键服务是否就绪
    required_services = []
    
    # 检查Redis（如果启用了）
    if settings.REDIS_ENABLED:
        try:
            if redis_manager.ping():
                required_services.append({"name": "redis", "status": "ready"})
            else:
                required_services.append({"name": "redis", "status": "error", "error": "Connection failed"})
        except Exception as e:
            required_services.append({"name": "redis", "status": "error", "error": str(e)})
    
    all_ready = all(service.get("status") == "ready" for service in required_services)
    
    return {
        "ready": all_ready,
        "services": required_services
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """存活检查"""
    return {"status": "alive"}