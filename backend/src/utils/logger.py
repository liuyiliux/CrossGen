"""
日志配置模块
设置应用日志格式和处理器
"""

import logging
import sys
from pathlib import Path
from .config import settings


def setup_logger() -> None:
    """设置应用日志"""
    
    # 创建日志目录
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 使用绝对路径配置日志文件
    log_file = log_dir / "app.log"
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file), encoding="utf-8")
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)