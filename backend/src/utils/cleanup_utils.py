"""
清理工具模块
定期清理临时文件和未使用的图片
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# 设置日志记录器
logger = logging.getLogger("cleanup_utils")


async def start_cleanup_task():
    """
    启动定期清理任务
    """
    logger.info("定期清理任务开始")
    
    try:
        while True:
            # 执行清理操作
            await cleanup_uploads()
            await cleanup_history()
            
            # 每小时执行一次清理
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("定期清理任务被取消")
    except Exception as e:
        logger.error(f"定期清理任务发生错误: {str(e)}", exc_info=True)


async def cleanup_uploads():
    """
    清理 uploads 目录中的临时文件
    """
    uploads_dir = Path(__file__).parent.parent.parent / "uploads"
    
    if not uploads_dir.exists():
        return
    
    logger.info(f"开始清理 uploads 目录: {uploads_dir}")
    
    # 遍历 uploads 目录中的所有文件和文件夹
    for item in uploads_dir.iterdir():
        try:
            if item.is_dir():
                # 检查是否是临时文件夹（以 temp_ 开头）
                if item.name.startswith("temp_"):
                    # 检查文件夹创建时间
                    created_time = datetime.fromtimestamp(item.stat().st_ctime)
                    # 如果文件夹超过24小时，删除
                    if datetime.now() - created_time > timedelta(hours=24):
                        shutil.rmtree(item)
                        logger.info(f"删除临时文件夹: {item}")
            elif item.is_file():
                # 检查文件创建时间
                created_time = datetime.fromtimestamp(item.stat().st_ctime)
                # 如果文件超过7天，删除
                if datetime.now() - created_time > timedelta(days=7):
                    item.unlink()
                    logger.info(f"删除过期文件: {item}")
        except Exception as e:
            logger.error(f"清理 {item} 时发生错误: {str(e)}", exc_info=True)
    
    logger.info("uploads 目录清理完成")


async def cleanup_history():
    """
    清理 history 目录中的孤立文件
    """
    history_dir = Path(__file__).parent.parent.parent / "history"
    
    if not history_dir.exists():
        return
    
    logger.info(f"开始清理 history 目录: {history_dir}")
    
    # 获取所有 .json 文件的 ID
    json_files = list(history_dir.glob("*.json"))
    history_ids = [file.stem for file in json_files]
    
    # 遍历所有图片文件夹
    for folder in history_dir.iterdir():
        if folder.is_dir() and folder.name.endswith("_images"):
            # 提取历史记录 ID（文件夹名格式: {history_id}_xxx_images）
            parts = folder.name.split("_")
            if len(parts) >= 3:
                # 重新组合历史记录 ID，因为文件夹名可能包含下划线
                history_id = "_".join(parts[:-2])
                
                # 检查历史记录 ID 是否存在对应的 .json 文件
                if history_id not in history_ids:
                    # 没有对应的 .json 文件，删除图片文件夹
                    shutil.rmtree(folder)
                    logger.info(f"删除孤立的图片文件夹: {folder}")
    
    logger.info("history 目录清理完成")
