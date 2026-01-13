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
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # 使用绝对路径配置日志文件
    log_file = log_dir / "app.log"

    # 获取根日志器
    root_logger = logging.getLogger()

    # 清除已存在的处理器，避免重复添加
    if root_logger.handlers:
        root_logger.handlers.clear()

    # 配置根日志器
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # 创建格式化器
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 添加文件处理器
    file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # 设置第三方库日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


# 创建并导出一个默认日志器，供其他模块使用
logger = logging.getLogger("app")

# 确保app日志器继承根日志器的配置
logger.setLevel(logging.INFO)
logger.propagate = True  # 确保日志传递给父日志器，这样就能使用根日志器的处理器

# 打印日志配置信息，方便调试
print(f"日志文件位置: {Path(__file__).parent.parent.parent / 'logs' / 'app.log'}")
print(f"日志级别: {settings.LOG_LEVEL}")
print(f"根日志处理器数量: {len(logging.getLogger().handlers)}")