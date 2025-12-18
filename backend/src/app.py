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

from src.api import generation, config, health, history
from src.utils.config import Settings
from src.utils.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("逸流后端服务启动")
    
    # 创建必要的目录
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    # 关闭时执行
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
    if Path("uploads").exists():
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    
    # 注册路由
    app.include_router(health.router, prefix="/api", tags=["健康检查"])
    app.include_router(generation.router, prefix="/api", tags=["内容生成"])
    app.include_router(config.router, prefix="/api", tags=["配置管理"])
    app.include_router(history.router, prefix="/api", tags=["历史记录"])
    
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
    
    settings = Settings()
    uvicorn.run(
        "src.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )