#!/usr/bin/env python3
"""
历史记录图片迁移脚本
将所有历史记录中的图片从base64或远程URL转换为本地文件存储
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.models.history import HistoryRecord, GeneratedImage
from src.utils.image_utils import process_image


def setup_logging():
    """设置日志记录"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    # 创建日志目录
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                log_dir / "migrate_history_images.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("migrate_history_images")


class HistoryImageMigrator:
    """历史记录图片迁移器"""
    
    def __init__(self):
        # 历史记录存储目录
        self.history_dir = Path(__file__).parent / "history"
        # 确保存储目录存在
        self.history_dir.mkdir(exist_ok=True)
        # 日志记录器
        self.logger = setup_logging()
        # 迁移统计
        self.stats = {
            "total_records": 0,
            "processed_records": 0,
            "updated_records": 0,
            "total_images": 0,
            "processed_images": 0,
            "success_images": 0,
            "failed_images": 0
        }
    
    async def run_migration(self):
        """运行迁移"""
        self.logger.info("开始历史记录图片迁移...")
        
        try:
            # 获取所有历史记录文件
            history_files = list(self.history_dir.glob("*.json"))
            self.stats["total_records"] = len(history_files)
            self.logger.info(f"找到 {self.stats['total_records']} 条历史记录")
            
            # 遍历处理每个历史记录
            for file_path in history_files:
                await self.process_history_file(file_path)
            
            # 输出迁移结果
            self.logger.info("\n迁移完成！")
            self.logger.info(f"总记录数: {self.stats['total_records']}")
            self.logger.info(f"处理记录数: {self.stats['processed_records']}")
            self.logger.info(f"更新记录数: {self.stats['updated_records']}")
            self.logger.info(f"总图片数: {self.stats['total_images']}")
            self.logger.info(f"处理图片数: {self.stats['processed_images']}")
            self.logger.info(f"成功图片数: {self.stats['success_images']}")
            self.logger.info(f"失败图片数: {self.stats['failed_images']}")
            
        except Exception as e:
            self.logger.error(f"迁移过程中发生错误: {str(e)}", exc_info=True)
    
    async def process_history_file(self, file_path: Path):
        """处理单个历史记录文件"""
        try:
            self.stats["processed_records"] += 1
            self.logger.info(f"处理记录 {file_path.name} ({self.stats['processed_records']}/{self.stats['total_records']})")
            
            # 读取历史记录
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 转换日期字符串为datetime对象
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            
            # 转换为HistoryRecord对象
            history = HistoryRecord(**data)
            
            # 处理图片
            updated = await self.process_images(history)
            
            # 如果有更新，保存记录
            if updated:
                self.stats["updated_records"] += 1
                await self.save_history(history, file_path)
            
        except Exception as e:
            self.logger.error(f"处理记录文件失败 {file_path}: {str(e)}", exc_info=True)
    
    async def process_images(self, history: HistoryRecord) -> bool:
        """处理历史记录中的图片"""
        updated = False
        
        if not history.images:
            self.logger.debug(f"记录 {history.id} 没有图片")
            return updated
        
        # 更新统计
        self.stats["total_images"] += len(history.images)
        
        # 处理每个图片
        for i, image in enumerate(history.images):
            self.stats["processed_images"] += 1
            
            # 检查图片URL是否已经是本地路径
            if self.is_local_path(image.url):
                self.logger.debug(f"图片 {i+1} 已经是本地路径，跳过处理")
                continue
            
            try:
                # 创建图片文件夹
                image_dir = self.history_dir / f"{history.id}_images"
                image_dir.mkdir(exist_ok=True)
                
                # 处理图片，保存到本地
                self.logger.info(f"处理记录 {history.id} 的图片 {i+1}")
                image_path = process_image(image.url, image_dir, f"{image.index}.png")
                
                if image_path:
                    # 更新图片URL
                    history.images[i].url = image_path
                    updated = True
                    self.stats["success_images"] += 1
                    self.logger.info(f"图片 {i+1} 处理成功，保存到 {image_path}")
                else:
                    self.stats["failed_images"] += 1
                    self.logger.error(f"图片 {i+1} 处理失败")
            
            except Exception as e:
                self.stats["failed_images"] += 1
                self.logger.error(f"处理图片 {i+1} 时发生错误: {str(e)}", exc_info=True)
        
        return updated
    
    def is_local_path(self, url: str) -> bool:
        """检查URL是否为本地路径"""
        # 检查是否为绝对路径
        if Path(url).is_absolute():
            return True
        
        # 检查是否为相对路径（不以http://或https://或data:image/开头）
        if not (url.startswith("http://") or url.startswith("https://") or url.startswith("data:image/")):
            return True
        
        return False
    
    async def save_history(self, history: HistoryRecord, file_path: Path):
        """保存历史记录到文件"""
        try:
            # 更新时间
            history.updated_at = datetime.now()
            
            # 转换为字典
            data = history.model_dump()
            
            # 转换datetime对象为字符串
            data["created_at"] = history.created_at.isoformat()
            data["updated_at"] = history.updated_at.isoformat()
            
            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"记录 {history.id} 保存成功")
        
        except Exception as e:
            self.logger.error(f"保存记录 {history.id} 失败: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # 运行迁移
    migrator = HistoryImageMigrator()
    asyncio.run(migrator.run_migration())