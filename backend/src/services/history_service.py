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
                        # 处理每个图片URL
                        processed_images = []
                        for img in data["images"]:
                            # 转换为GeneratedImage对象
                            gen_image = GeneratedImage(**img)
                            # 如果图片URL不是http/https开头，转换为前端可访问的URL
                            if gen_image.url and not gen_image.url.startswith("http://") and not gen_image.url.startswith("https://"):
                                # 如果已经是相对路径，直接使用
                                if gen_image.url.startswith("/"):
                                    pass
                                elif "history/" in gen_image.url:
                                    # 转换为相对URL
                                    gen_image.url = f"/{'/'.join(gen_image.url.split('/')[-3:])}"  # 保留history/xxx_images/xxx.png
                                else:
                                    # 直接使用相对路径
                                    gen_image.url = f"/history/{file_path.stem}_images/{img.get('index', 0)}.png"
                            processed_images.append(gen_image)
                        data["images"] = processed_images
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
                    # 处理每个图片URL
                    processed_images = []
                    for img in data["images"]:
                        # 转换为GeneratedImage对象
                        gen_image = GeneratedImage(**img)
                        # 如果图片URL不是http/https开头，转换为前端可访问的URL
                        if gen_image.url and not gen_image.url.startswith("http://") and not gen_image.url.startswith("https://"):
                            # 如果已经是相对路径，直接使用
                            if gen_image.url.startswith("/"):
                                pass
                            elif "history/" in gen_image.url:
                                # 转换为相对URL
                                gen_image.url = f"/{'/'.join(gen_image.url.split('/')[-3:])}"  # 保留history/xxx_images/xxx.png
                            else:
                                # 直接使用相对路径
                                gen_image.url = f"/history/{file_path.stem}_images/{img.get('index', 0)}.png"
                        processed_images.append(gen_image)
                    data["images"] = processed_images
                return HistoryRecord(**data)
        except Exception as e:
            print(f"读取历史记录文件失败 {file_path}: {str(e)}")
            return None
    
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
    
    def _convert_image_path_to_url(self, image_path: str) -> str:
        """
        将图片本地路径转换为前端可访问的URL
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            前端可访问的URL
        """
        # 转换为相对路径，移除绝对路径前缀
        relative_path = Path(image_path).relative_to(Path.cwd())
        # 返回相对URL，前端可以直接访问
        return f"/{relative_path}"
    
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
        
        # 处理图片数据，保存到本地文件夹
        processed_images = []
        from src.utils.image_utils import process_image
        from pathlib import Path
        
        # 创建图片文件夹，使用主题文字命名
        image_dir = self._get_safe_folder_name(history_id, history_data.topic)
        image_dir.mkdir(exist_ok=True)
        
        # 处理每个图片
        for image in history_data.images:
            if image and hasattr(image, 'url') and image.url:
                # 处理图片，保存到本地
                image_path = process_image(image.url, image_dir, f"{image.id}.png" if hasattr(image, 'id') else None)
                if image_path:
                    # 更新图片URL为前端可访问的URL
                    processed_image = image.model_copy()
                    processed_image.url = self._convert_image_path_to_url(image_path)
                    processed_images.append(processed_image)
                else:
                    # 保存失败，保留原有图片数据
                    processed_images.append(image)
            else:
                # 没有URL，直接保存
                processed_images.append(image)
        
        # 创建历史记录对象
        now = datetime.now()
        history_record = HistoryRecord(
            id=history_id,
            topic=history_data.topic,
            platform=history_data.platform,
            outline=history_data.outline,
            images=processed_images,
            status=history_data.status,
            generation_time=history_data.generation_time,
            created_at=now,
            updated_at=now,
            text_model=history_data.text_model,
            image_model=history_data.image_model
        )
        
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
        
        # 处理图片数据
        if "images" in update_dict:
            processed_images = []
            from src.utils.image_utils import process_image, replace_image
            from pathlib import Path
            
            # 创建图片文件夹，使用主题文字命名
            image_dir = self._get_safe_folder_name(history_id, existing_history.topic)
            image_dir.mkdir(exist_ok=True)
            
            # 获取现有图片信息，用于替换逻辑
            existing_images = {img.id: img for img in existing_history.images if hasattr(img, 'id')}
            
            # 处理每个图片
            for image in update_dict["images"]:
                # 转换为GeneratedImage对象
                gen_image = GeneratedImage(**image)
                
                if gen_image.url:
                    # 保存图片到本地文件夹
                    if gen_image.id and gen_image.id in existing_images:
                        # 替换原有图片
                        old_image = existing_images[gen_image.id]
                        if old_image.url:
                            # 使用replace_image函数替换原有图片
                            image_path = replace_image(old_image.url, gen_image.url)
                            if image_path:
                                gen_image.url = self._convert_image_path_to_url(image_path)
                    else:
                        # 新生成图片，保存到本地
                        image_path = process_image(gen_image.url, image_dir, f"{gen_image.id}.png" if gen_image.id else None)
                        if image_path:
                            gen_image.url = self._convert_image_path_to_url(image_path)
                
                processed_images.append(gen_image)
            
            # 更新images字段
            update_dict["images"] = processed_images
        
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
        
        if not file_path.exists():
            return False
        
        try:
            # 读取历史记录，获取相关图片信息
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 提取所有图片URL
            image_urls = []
            if "images" in data:
                image_urls = [img["url"] for img in data["images"] if img.get("url")]
            
            # 删除历史记录文件
            file_path.unlink()
            
            # 删除所有相关的图片文件夹（使用glob匹配）
            import shutil
            for folder_path in self.history_dir.glob(f"{history_id}_*_images"):
                if folder_path.is_dir():
                    shutil.rmtree(folder_path)
            
            # 清理uploads目录中与该历史记录相关的图片
            from pathlib import Path
            uploads_dir = Path(__file__).parent.parent.parent / "uploads"
            if uploads_dir.exists():
                # 检查每个图片URL，删除对应的文件
                for image_url in image_urls:
                    if image_url.startswith("/uploads/"):
                        # 提取文件名
                        file_name = image_url.split("/")[-1]
                        file_path = uploads_dir / file_name
                        if file_path.exists():
                            file_path.unlink()
            
            return True
        except Exception as e:
            print(f"删除历史记录失败 {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
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
