"""
历史记录API
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.models.history import (
    HistoryRecord,
    HistoryRecordCreate,
    HistoryRecordUpdate,
    HistoryFilter,
    HistoryListResponse
)
from src.services.history_service import HistoryService

router = APIRouter()


@router.get("/history")
async def get_history(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    platform: Optional[str] = Query(None, description="平台类型"),
    status: Optional[str] = Query(None, description="生成状态"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
) -> Dict[str, Any]:
    """
    获取历史记录列表
    
    Args:
        keyword: 搜索关键词
        platform: 平台类型
        status: 生成状态
        start_date: 开始日期
        end_date: 结束日期
        page: 页码
        page_size: 每页数量
        
    Returns:
        历史记录列表和分页信息
    """
    # 创建筛选参数
    filter_params = HistoryFilter(
        keyword=keyword,
        platform=platform,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    # 调用服务获取历史记录
    service = HistoryService()
    result = await service.get_history_list(filter_params, page, page_size)
    
    return result


@router.get("/history/{history_id}")
async def get_history_detail(history_id: str) -> HistoryRecord:
    """
    获取历史记录详情
    
    Args:
        history_id: 历史记录ID
        
    Returns:
        历史记录详情
    """
    service = HistoryService()
    history = await service.get_history_by_id(history_id)
    
    if not history:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    
    return history


@router.post("/history")
async def create_history(history_data: HistoryRecordCreate) -> HistoryRecord:
    """
    创建历史记录
    
    Args:
        history_data: 历史记录数据
        
    Returns:
        创建的历史记录
    """
    service = HistoryService()
    return await service.create_history(history_data)


@router.put("/history/{history_id}")
async def update_history(
    history_id: str,
    update_data: HistoryRecordUpdate
) -> HistoryRecord:
    """
    更新历史记录
    
    Args:
        history_id: 历史记录ID
        update_data: 更新数据
        
    Returns:
        更新后的历史记录
    """
    service = HistoryService()
    updated_history = await service.update_history(history_id, update_data)
    
    if not updated_history:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    
    return updated_history


@router.delete("/history/{history_id}")
async def delete_history(history_id: str) -> Dict[str, bool]:
    """
    删除历史记录
    
    Args:
        history_id: 历史记录ID
        
    Returns:
        删除是否成功
    """
    service = HistoryService()
    success = await service.delete_history(history_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    
    return {"success": success}


@router.delete("/history")
async def batch_delete_history(history_ids: List[str] = Body(..., description="历史记录ID列表")) -> Dict[str, int]:
    """
    批量删除历史记录
    
    Args:
        history_ids: 历史记录ID列表
        
    Returns:
        删除成功的数量
    """
    service = HistoryService()
    success_count = await service.batch_delete_history(history_ids)
    
    return {"success_count": success_count}


@router.get("/history/{history_id}/download")
async def download_history(history_id: str):
    """
    下载历史记录
    
    Args:
        history_id: 历史记录ID
        
    Returns:
        历史记录数据
    """
    service = HistoryService()
    result = await service.download_history(history_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    
    return result
