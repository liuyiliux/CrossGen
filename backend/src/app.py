"""
逸流项目后端主应用
FastAPI 应用入口点
"""

import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径，解决模块导入问题
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api import generation, config, health, history, inspiration
from src.utils.config import Settings, settings
from src.utils.logger import setup_logger, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    # 先创建必要的目录，确保日志目录存在
    app_root = Path(__file__).resolve().parent.parent
    
    # 创建必要的目录
    # 日志目录由setup_logger处理
    (app_root / settings.UPLOAD_DIR).mkdir(exist_ok=True)
    (app_root / "history").mkdir(exist_ok=True)
    
    # 配置日志
    setup_logger()
    logger.info("逸流后端服务启动")
    
    # 初始化提供商管理器
    try:
        from src.providers.provider_manager import ProviderManager
        from src.services.generation_service import GenerationService
        provider_manager = ProviderManager()
        await provider_manager.load_providers()
        # 将提供商管理器存储在应用状态中
        app.state.provider_manager = provider_manager
        # 设置为GenerationService的全局提供商管理器
        GenerationService.set_global_provider_manager(provider_manager)
        logger.info("提供商管理器初始化成功")
    except Exception as e:
        logger.error(f"初始化提供商管理器失败: {str(e)}")
    
    # 启动定期清理任务
    import asyncio
    from src.utils.cleanup_utils import start_cleanup_task
    cleanup_task = asyncio.create_task(start_cleanup_task())
    logger.info("定期清理任务启动")
    
    yield
    
    # 关闭时执行
    # 关闭提供商管理器连接
    if hasattr(app.state, 'provider_manager'):
        await app.state.provider_manager.close_all()
        logger.info("提供商管理器连接已关闭")
    
    # 取消定期清理任务
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        logger.info("定期清理任务已取消")
    
    logger.info("逸流后端服务关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    settings = Settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="逸流项目后端 - 多平台图文生成器API",
        lifespan=lifespan
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 静态文件服务
    upload_dir = Path(settings.UPLOAD_DIR)
    if upload_dir.exists():
        app.mount("/" + settings.UPLOAD_DIR, StaticFiles(directory=settings.UPLOAD_DIR), name=settings.UPLOAD_DIR)
    if Path("history").exists():
        app.mount("/history", StaticFiles(directory="history"), name="history")
    
    # 注册路由
    app.include_router(health.router, prefix=settings.API_PREFIX, tags=["健康检查"])
    app.include_router(generation.router, prefix=settings.API_PREFIX, tags=["内容生成"])
    app.include_router(config.router, prefix=settings.API_PREFIX, tags=["配置管理"])
    app.include_router(history.router, prefix=settings.API_PREFIX, tags=["历史记录"])
    app.include_router(inspiration.router, prefix=settings.API_PREFIX, tags=["灵感获取"])
    
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "欢迎使用逸流API",
            "version": settings.APP_VERSION,
            "docs": "/docs"
        }
    
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="逸流后端服务")
    parser.add_argument("--port", type=int, help="服务端口")
    args = parser.parse_args()
    
    settings = Settings()
    
    # 使用命令行指定的端口，如果没有指定则使用配置中的端口
    port = args.port or settings.PORT
    
    uvicorn.run(
        "src.app:app",
        host=settings.HOST,
        port=port,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )