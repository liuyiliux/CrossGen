"""
灵感获取API
提供小红书内容搜索和链接解析接口
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx

from src.services.xiaohongshu_service import XiaohongshuService
from src.utils.logger import logger

router = APIRouter(prefix="/inspiration", tags=["inspiration"])

# 初始化小红书服务
xhs_service = XiaohongshuService()


class InspirationItem(BaseModel):
    """灵感搜索结果项"""
    title: str = Field(..., description="标题")
    cover_url: str = Field(..., description="封面图URL")
    description: str = Field(..., description="描述")
    source_url: str = Field(..., description="来源链接")
    author: Optional[str] = Field(None, description="作者")
    likes: Optional[int] = Field(None, description="点赞数")


class InspirationRequest(BaseModel):
    """灵感搜索请求"""
    keyword: str = Field(..., min_length=1, max_length=100, description="搜索关键词")


class InspirationParseRequest(BaseModel):
    """灵感链接解析请求"""
    url: str = Field(..., min_length=5, max_length=500, description="小红书笔记链接")


class InspirationResponse(BaseModel):
    """灵感搜索响应"""
    success: bool = Field(..., description="是否成功")
    items: List[InspirationItem] = Field(default_factory=list, description="结果列表")
    total: int = Field(default=0, description="总数量")
    message: Optional[str] = Field(None, description="提示消息")


class InspirationParseResponse(BaseModel):
    """灵感链接解析响应"""
    success: bool = Field(..., description="是否成功")
    item: Optional[InspirationItem] = Field(None, description="解析结果")
    message: Optional[str] = Field(None, description="提示消息")


@router.post("/search", response_model=InspirationResponse)
async def search_inspiration(request: Request, data: InspirationRequest) -> InspirationResponse:
    """
    关键词搜索小红书内容
    
    Args:
        data: 搜索请求，包含关键词
        
    Returns:
        InspirationResponse: 搜索结果
    """
    try:
        logger.info(f"收到灵感搜索请求: {data.keyword}")
        
        # 调用小红书服务搜索
        results = xhs_service.search_by_keyword(data.keyword, limit=20)
        
        if not results:
            return InspirationResponse(
                success=True,
                items=[],
                total=0,
                message=f"未找到与'{data.keyword}'相关的内容"
            )
        
        return InspirationResponse(
            success=True,
            items=results,
            total=len(results),
            message=f"找到{len(results)}个相关内容"
        )
        
    except Exception as e:
        logger.error(f"灵感搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/parse", response_model=InspirationParseResponse)
async def parse_inspiration(request: Request, data: InspirationParseRequest) -> InspirationParseResponse:
    """
    解析小红书笔记链接
    
    Args:
        data: 解析请求，包含笔记URL
        
    Returns:
        InspirationParseResponse: 解析结果
    """
    try:
        logger.info(f"收到灵感解析请求: {data.url}")
        
        # 验证URL格式
        if not data.url.startswith('http'):
            if data.url.startswith('/'):
                data.url = f"https://www.xiaohongshu.com{data.url}"
            else:
                return InspirationParseResponse(
                    success=False,
                    item=None,
                    message="请输入有效的小红书笔记链接"
                )
        
        # 调用小红书服务解析
        result = xhs_service.parse_note_url(data.url)
        
        if not result:
            return InspirationParseResponse(
                success=False,
                item=None,
                message="解析失败，请检查链接是否正确"
            )
        
        # 转换为InspirationItem格式
        item = InspirationItem(
            title=result.get('title', ''),
            cover_url=result.get('cover_url', ''),
            description=result.get('description', ''),
            source_url=result.get('source_url', ''),
            author=result.get('author'),
            likes=result.get('likes')
        )
        
        return InspirationParseResponse(
            success=True,
            item=item,
            message="解析成功"
        )
        
    except Exception as e:
        logger.error(f"灵感解析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "inspiration-api"
    }
