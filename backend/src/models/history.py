"""
历史记录数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class GenerationStatus(str, Enum):
    """生成状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    PROCESSING = "processing"
    CANCELLED = "cancelled"
    OUTLINE_GENERATING = "outline_generating"
    OUTLINE_SUCCESS = "outline_success"
    OUTLINE_FAILED = "outline_failed"
    IMAGE_GENERATING = "image_generating"
    IMAGE_SUCCESS = "image_success"
    IMAGE_FAILED = "image_failed"


class PlatformType(str, Enum):
    """平台类型枚举"""
    XIAOHONGSHU = "xiaohongshu"
    DOUYIN = "douyin"
    WECHAT = "wechat"
    TOUTIAO = "toutiao"
    
    @classmethod
    def _missing_(cls, value):
        """处理不在枚举中的值，支持动态平台"""
        # 动态创建并返回新的枚举成员
        obj = str.__new__(cls)
        obj._value_ = value
        return obj


class Page(BaseModel):
    """页面数据模型"""
    index: int
    type: str
    content: str


class Outline(BaseModel):
    """大纲数据模型"""
    raw: str
    pages: List[Page]


class GeneratedImage(BaseModel):
    """生成图片数据模型"""
    index: int
    url: str
    status: str
    error: Optional[str] = None


class HistoryRecord(BaseModel):
    """历史记录数据模型"""
    id: str = Field(..., description="唯一标识符")
    topic: str = Field(..., description="生成主题")
    platform: PlatformType = Field(..., description="平台类型")
    outline: Outline = Field(..., description="生成大纲")
    images: List[GeneratedImage] = Field(default_factory=list, description="生成图片")
    status: GenerationStatus = Field(default=GenerationStatus.PROCESSING, description="生成状态")
    generation_time: float = Field(default=0.0, description="生成用时")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    text_model: Optional[str] = Field(default=None, description="使用的文本模型")
    image_model: Optional[str] = Field(default=None, description="使用的图像模型")
    
    class Config:
        use_enum_values = True


class HistoryRecordCreate(BaseModel):
    """创建历史记录请求模型"""
    topic: str = Field(..., description="生成主题")
    platform: PlatformType = Field(..., description="平台类型")
    outline: Outline = Field(..., description="生成大纲")
    images: List[GeneratedImage] = Field(default_factory=list, description="生成图片")
    status: GenerationStatus = Field(default=GenerationStatus.SUCCESS, description="生成状态")
    generation_time: float = Field(default=0.0, description="生成用时")
    text_model: Optional[str] = Field(default=None, description="使用的文本模型")
    image_model: Optional[str] = Field(default=None, description="使用的图像模型")
    
    class Config:
        use_enum_values = True


class HistoryRecordUpdate(BaseModel):
    """更新历史记录请求模型"""
    status: Optional[GenerationStatus] = None
    outline: Optional[Outline] = None
    images: Optional[List[GeneratedImage]] = None
    generation_time: Optional[float] = None
    text_model: Optional[str] = None
    image_model: Optional[str] = None
    
    class Config:
        use_enum_values = True


class HistoryFilter(BaseModel):
    """历史记录筛选模型"""
    keyword: Optional[str] = None
    platform: Optional[PlatformType] = None
    status: Optional[GenerationStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class HistoryListResponse(BaseModel):
    """历史记录列表响应模型"""
    total: int
    items: List[HistoryRecord]
    page: int
    page_size: int
