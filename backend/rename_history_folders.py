#!/usr/bin/env python3
"""
历史记录文件夹重命名脚本
将现有历史记录图片文件夹重命名为包含主题文字的格式
"""

import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import shutil

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.models.history import HistoryRecord


class HistoryFolderRenamer:
    """历史记录文件夹重命名器"""
    
    def __init__(self):
        # 历史记录存储目录
        self.history_dir = Path(__file__).parent / "history"
        # 确保存储目录存在
        self.history_dir.mkdir(exist_ok=True)
        # 设置日志
        self._setup_logging()
        # 重命名统计
        self.stats = {
            "total_records": 0,
            "processed_records": 0,
            "renamed_folders": 0,
            "failed_renames": 0,
            "no_folder_records": 0
        }
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.history_dir.parent / "logs" / "rename_history_folders.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("history_folder_renamer")
    
    def _get_safe_folder_name(self, history_id: str, topic: str) -> Path:
        """
        获取安全的文件夹名称
        
        Args:
            history_id: 历史记录ID
            topic: 历史记录主题
            
        Returns:
            安全的文件夹路径
        """
        # 清理主题文字，移除非法字符
        safe_topic = "".join(c for c in topic if c.isalnum() or c in "-_ ").strip()
        # 截断超长主题
        max_topic_length = 50
        if len(safe_topic) > max_topic_length:
            safe_topic = safe_topic[:max_topic_length] + "..."
        # 生成文件夹名称
        folder_name = f"{history_id}_{safe_topic}_images"
        return self.history_dir / folder_name
    
    async def run_rename(self):
        """运行重命名"""
        self.logger.info("开始重命名历史记录文件夹...")
        
        try:
            # 获取所有历史记录文件
            history_files = list(self.history_dir.glob("*.json"))
            self.stats["total_records"] = len(history_files)
            self.logger.info(f"找到 {self.stats['total_records']} 条历史记录")
            
            # 遍历处理每个历史记录
            for file_path in history_files:
                await self.process_history_file(file_path)
            
            # 输出重命名结果
            self.logger.info("\n重命名完成！")
            self.logger.info(f"总记录数: {self.stats['total_records']}")
            self.logger.info(f"处理记录数: {self.stats['processed_records']}")
            self.logger.info(f"重命名文件夹数: {self.stats['renamed_folders']}")
            self.logger.info(f"重命名失败数: {self.stats['failed_renames']}")
            self.logger.info(f"无文件夹记录数: {self.stats['no_folder_records']}")
            
        except Exception as e:
            self.logger.error(f"重命名过程中发生错误: {str(e)}", exc_info=True)
    
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
            
            # 查找旧文件夹
            old_folders = list(self.history_dir.glob(f"{history.id}_images"))
            
            if not old_folders:
                self.stats["no_folder_records"] += 1
                self.logger.debug(f"记录 {history.id} 没有对应的图片文件夹")
                return
            
            # 获取新文件夹名称
            new_folder = self._get_safe_folder_name(history.id, history.topic)
            
            # 重命名每个旧文件夹
            for old_folder in old_folders:
                if old_folder == new_folder:
                    self.logger.debug(f"文件夹 {old_folder.name} 已经是正确的名称，跳过")
                    continue
                
                try:
                    # 检查新文件夹是否已存在
                    if new_folder.exists():
                        # 如果已存在，创建一个唯一的名称
                        unique_suffix = 1
                        while new_folder.exists():
                            unique_new_folder = new_folder.parent / f"{new_folder.stem}_{unique_suffix}{new_folder.suffix}"
                            unique_suffix += 1
                        new_folder = unique_new_folder
                    
                    # 重命名文件夹
                    old_folder.rename(new_folder)
                    self.stats["renamed_folders"] += 1
                    self.logger.info(f"成功重命名文件夹: {old_folder.name} -> {new_folder.name}")
                
                except OSError as e:
                    self.stats["failed_renames"] += 1
                    self.logger.error(f"重命名文件夹失败 {old_folder.name} -> {new_folder.name}: {str(e)}", exc_info=True)
                except Exception as e:
                    self.stats["failed_renames"] += 1
                    self.logger.error(f"重命名文件夹时发生未知错误 {old_folder.name} -> {new_folder.name}: {str(e)}", exc_info=True)
            
        except Exception as e:
            self.logger.error(f"处理记录文件失败 {file_path}: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # 运行重命名
    renamer = HistoryFolderRenamer()
    asyncio.run(renamer.run_rename())