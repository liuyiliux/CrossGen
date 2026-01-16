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
    
    # 数据库配置 - 从环境变量加载默认值
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_ENABLED: bool = Field(default=True, env="REDIS_ENABLED")
    
    # API 配置
    API_PREFIX: str = Field(default="/api", env="API_PREFIX")
    API_TIMEOUT: int = Field(default=300, env="API_TIMEOUT")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 尝试从system_config.yaml加载配置，覆盖环境变量
        try:
            from pathlib import Path
            import yaml
            
            # 读取system_config.yaml
            config_dir = Path(__file__).parent.parent.parent.parent / "config"
            system_config_file = config_dir / "system_config.yaml"
            
            if system_config_file.exists():
                with open(system_config_file, 'r', encoding='utf-8') as f:
                    system_config = yaml.safe_load(f) or {}
                    
                # 1. Redis 配置
                if "redis" in system_config:
                    redis_config = system_config["redis"]
                    if "enabled" in redis_config:
                        self.REDIS_ENABLED = redis_config["enabled"]
                    if "url" in redis_config:
                        self.REDIS_URL = redis_config["url"]
                    if "password" in redis_config:
                        self.REDIS_PASSWORD = redis_config["password"]

                # 2. 日志配置
                if "logger" in system_config:
                    logger_config = system_config["logger"]
                    if "level" in logger_config:
                        self.LOG_LEVEL = logger_config["level"]
                    if "file_path" in logger_config:
                        self.LOG_FILE = logger_config["file_path"]
                
                # 3. 图片/文件配置
                if "image" in system_config:
                    image_config = system_config["image"]
                    if "save_path" in image_config:
                        self.UPLOAD_DIR = image_config["save_path"]
                    if "max_size" in image_config:
                        # 转换为字符串，保持类型一致
                        self.MAX_FILE_SIZE = str(image_config["max_size"])
                
                # 4. API 配置
                if "api" in system_config:
                    api_config = system_config["api"]
                    if "prefix" in api_config:
                        self.API_PREFIX = api_config["prefix"]
                    if "timeout" in api_config:
                        self.API_TIMEOUT = api_config["timeout"]
                        
        except Exception as e:
            # 如果加载失败，使用默认值
            print(f"加载system_config.yaml失败: {str(e)}")
    
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
    # 使用绝对路径，避免路径解析问题
    LOG_FILE: str = Field(default="logs/app.log", env="LOG_FILE", json_schema_extra={
        "type": "string",
        "description": "日志文件路径（相对于backend目录）"
    })
    
    # 生成配置
    MAX_CONCURRENT_GENERATIONS: int = Field(default=5, env="MAX_CONCURRENT_GENERATIONS")
    GENERATION_TIMEOUT: int = Field(default=300, env="GENERATION_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()