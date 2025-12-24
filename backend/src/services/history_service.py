"""
历史记录服务
处理历史记录的存储和检索
"""

import json
import uuid
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from src.models.history import (
    HistoryRecord,
    HistoryRecordCreate,
    HistoryRecordUpdate,
    HistoryFilter,
    GeneratedImage
)


class HistoryService:
    """历史记录服务"""
    
    def __init__(self):
        # 历史记录存储目录
        self.history_dir = Path(__file__).parent.parent.parent / "history"
        # 确保存储目录存在
        self.history_dir.mkdir(exist_ok=True)
        # 文件锁，防止并发写入
        self._lock = asyncio.Lock()
    
    async def get_history_list(
        self, 
        filter_params: Optional[HistoryFilter] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取历史记录列表
        
        Args:
            filter_params: 筛选参数
            page: 页码
            page_size: 每页数量
            
        Returns:
            历史记录列表和分页信息
        """
        # 获取所有历史记录文件
        history_files = list(self.history_dir.glob("*.json"))
        
        # 读取并解析所有历史记录
        history_records = []
        for file_path in history_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 转换日期字符串为datetime对象
                    data["created_at"] = datetime.fromisoformat(data["created_at"])
                    data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                    # 转换images字段的字典列表为GeneratedImage对象列表
                    if "images" in data:
                        data["images"] = [GeneratedImage(**img) for img in data["images"]]
                    history_records.append(HistoryRecord(**data))
            except Exception as e:
                print(f"读取历史记录文件失败 {file_path}: {str(e)}")
        
        # 应用筛选条件
        filtered_records = self._apply_filter(history_records, filter_params)
        
        # 按创建时间降序排序
        filtered_records.sort(key=lambda x: x.created_at, reverse=True)
        
        # 分页处理
        total = len(filtered_records)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_records = filtered_records[start:end]
        
        return {
            "total": total,
            "items": paginated_records,
            "page": page,
            "page_size": page_size
        }
    
    async def get_history_by_id(self, history_id: str) -> Optional[HistoryRecord]:
        """
        根据ID获取历史记录详情
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            历史记录详情，不存在则返回None
        """
        file_path = self.history_dir / f"{history_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 转换日期字符串为datetime对象
                data["created_at"] = datetime.fromisoformat(data["created_at"])
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                # 转换images字段的字典列表为GeneratedImage对象列表
                if "images" in data:
                    data["images"] = [GeneratedImage(**img) for img in data["images"]]
                return HistoryRecord(**data)
        except Exception as e:
            print(f"读取历史记录文件失败 {file_path}: {str(e)}")
            return None
    
    async def create_history(self, history_data: HistoryRecordCreate) -> HistoryRecord:
        """
        创建历史记录
        
        Args:
            history_data: 历史记录数据
            
        Returns:
            创建的历史记录
        """
        # 生成唯一ID
        history_id = str(uuid.uuid4())
        
        # 创建历史记录对象
        now = datetime.now()
        history_record = HistoryRecord(
            id=history_id,
            topic=history_data.topic,
            platform=history_data.platform,
            outline=history_data.outline,
            images=history_data.images,
            status=history_data.status,
            generation_time=history_data.generation_time,
            created_at=now,
            updated_at=now,
            text_model=history_data.text_model,
            image_model=history_data.image_model
        )
        
        # 创建图片文件夹
        image_dir = self.history_dir / f"{history_id}_images"
        image_dir.mkdir(exist_ok=True)
        
        # 写入文件
        await self._write_history(history_record)
        
        return history_record
    
    async def update_history(
        self, 
        history_id: str,
        update_data: HistoryRecordUpdate
    ) -> Optional[HistoryRecord]:
        """
        更新历史记录
        
        Args:
            history_id: 历史记录ID
            update_data: 更新数据
            
        Returns:
            更新后的历史记录，不存在则返回None
        """
        # 获取现有历史记录
        existing_history = await self.get_history_by_id(history_id)
        if not existing_history:
            return None
        
        # 更新字段
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 转换images字段的字典列表为GeneratedImage对象列表（如果存在）
        if "images" in update_dict:
            update_dict["images"] = [GeneratedImage(**img) for img in update_dict["images"]]
        
        updated_history = existing_history.model_copy(update=update_dict)
        updated_history.updated_at = datetime.now()
        
        # 写入文件
        await self._write_history(updated_history)
        
        return updated_history
    
    async def delete_history(self, history_id: str) -> bool:
        """
        删除历史记录
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            删除是否成功
        """
        file_path = self.history_dir / f"{history_id}.json"
        image_dir = self.history_dir / f"{history_id}_images"
        
        if not file_path.exists():
            return False
        
        try:
            # 删除历史记录文件
            file_path.unlink()
            
            # 删除图片文件夹（如果存在）
            if image_dir.exists():
                import shutil
                shutil.rmtree(image_dir)
            
            return True
        except Exception as e:
            print(f"删除历史记录失败 {file_path}: {str(e)}")
            return False
    
    async def batch_delete_history(self, history_ids: List[str]) -> int:
        """
        批量删除历史记录
        
        Args:
            history_ids: 历史记录ID列表
            
        Returns:
            删除成功的数量
        """
        success_count = 0
        for history_id in history_ids:
            if await self.delete_history(history_id):
                success_count += 1
        
        return success_count
    
    async def download_history(self, history_id: str) -> Optional[Dict[str, Any]]:
        """
        下载历史记录
        
        Args:
            history_id: 历史记录ID
            
        Returns:
            历史记录数据，不存在则返回None
        """
        # 获取历史记录
        history = await self.get_history_by_id(history_id)
        if not history:
            return None
        
        # 转换为字典并返回
        return history.model_dump()
    
    def _apply_filter(
        self, 
        records: List[HistoryRecord], 
        filter_params: Optional[HistoryFilter]
    ) -> List[HistoryRecord]:
        """
        应用筛选条件
        
        Args:
            records: 原始历史记录列表
            filter_params: 筛选参数
            
        Returns:
            筛选后的历史记录列表
        """
        if not filter_params:
            return records
        
        filtered = []
        for record in records:
            match = True
            
            # 关键词筛选
            if filter_params.keyword:
                if filter_params.keyword.lower() not in record.topic.lower():
                    match = False
            
            # 平台筛选
            if filter_params.platform:
                if record.platform != filter_params.platform:
                    match = False
            
            # 状态筛选
            if filter_params.status:
                if record.status != filter_params.status:
                    match = False
            
            # 日期范围筛选
            if filter_params.start_date:
                if record.created_at < filter_params.start_date:
                    match = False
            
            if filter_params.end_date:
                if record.created_at > filter_params.end_date:
                    match = False
            
            if match:
                filtered.append(record)
        
        return filtered
    
    async def _write_history(self, history_record: HistoryRecord) -> None:
        """
        写入历史记录到文件
        
        Args:
            history_record: 历史记录对象
        """
        async with self._lock:
            file_path = self.history_dir / f"{history_record.id}.json"
            
            try:
                # 转换datetime对象为字符串
                data = history_record.model_dump()
                data["created_at"] = history_record.created_at.isoformat()
                data["updated_at"] = history_record.updated_at.isoformat()
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"写入历史记录文件失败 {file_path}: {str(e)}")
                raise
