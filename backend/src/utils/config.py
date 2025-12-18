"""
配置管理模块
使用 Pydantic Settings 管理应用配置
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基础配置
    APP_NAME: str = "Yiliu Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # 数据库配置
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_ENABLED: bool = Field(default=True, env="REDIS_ENABLED")
    
    # 安全配置
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # OpenAI 配置
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    
    # Anthropic 配置
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_BASE_URL: str = Field(default="https://api.anthropic.com", env="ANTHROPIC_BASE_URL")
    ANTHROPIC_MODEL: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    
    # Stable Diffusion 配置
    SD_API_KEY: Optional[str] = Field(default=None, env="SD_API_KEY")
    SD_BASE_URL: str = Field(default="http://localhost:7860/sdapi/v1", env="SD_BASE_URL")
    SD_MODEL: str = Field(default="stable-diffusion-xl", env="SD_MODEL")
    
    # 文件存储配置
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: str = Field(default="10MB", env="MAX_FILE_SIZE")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE")
    
    # 生成配置
    MAX_CONCURRENT_GENERATIONS: int = Field(default=5, env="MAX_CONCURRENT_GENERATIONS")
    GENERATION_TIMEOUT: int = Field(default=300, env="GENERATION_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()