"""
生成相关的数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


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


class GenerationRequest(BaseModel):
    """内容生成请求"""
    topic: str = Field(..., description="生成主题")
    platforms: List[PlatformType] = Field(..., description="目标平台列表")
    text_provider: Optional[str] = Field(default=None, description="文本生成提供商名称")
    options: Optional[Dict[str, Any]] = Field(default=None, description="生成选项")
    
    class Config:
        use_enum_values = True


class ImageRequest(BaseModel):
    """图像生成请求"""
    prompt: str = Field(..., description="图像生成提示词")
    platform: PlatformType = Field(..., description="目标平台")
    count: int = Field(default=1, description="生成图片数量")
    
    class Config:
        use_enum_values = True


class GenerationResult(BaseModel):
    """单个生成结果"""
    platform: PlatformType
    title: str
    content: str
    images: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class GenerationResponse(BaseModel):
    """生成响应"""
    success: bool
    results: List[GenerationResult]
    message: str
    generation_time: float
    history_id: Optional[str] = Field(default=None, description="历史记录ID")
    created_at: datetime = Field(default_factory=datetime.now)


class BatchGenerationRequest(BaseModel):
    """批量生成请求"""
    topics: List[str] = Field(..., description="主题列表")
    platforms: List[PlatformType] = Field(..., description="目标平台列表")
    options: Optional[Dict[str, Any]] = Field(default=None, description="生成选项")
    
    class Config:
        use_enum_values = True


class BatchGenerationResponse(BaseModel):
    """批量生成响应"""
    job_id: str
    status: str
    message: str
    created_at: datetime = Field(default_factory=datetime.now)


class GenerationStatus(BaseModel):
    """生成状态"""
    job_id: str
    status: str  # processing, completed, failed, cancelled
    progress: Dict[str, float] = Field(default_factory=dict)
    total: int = 0
    completed: int = 0
    failed: int = 0
    results: List[GenerationResult] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.now)