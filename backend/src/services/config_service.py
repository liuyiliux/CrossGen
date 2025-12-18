"""
配置管理服务
处理平台模板和提供商配置
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.utils.config import settings


class ConfigService:
    """配置管理服务"""
    
    def __init__(self):
        # 使用基于当前文件的绝对路径来定位配置目录
        self.base_dir = Path(__file__).parent.parent.parent.parent  # backend/src/services -> backend -> yiliu
        self.config_dir = self.base_dir / "config"
        
        # 实际配置文件路径
        self.platform_templates_file = self.config_dir / "platform_templates.yaml"
        self.text_providers_file = self.config_dir / "text_providers.yaml"
        self.image_providers_file = self.config_dir / "image_providers.yaml"
        
        # 示例配置文件路径
        self.text_providers_example_file = self.config_dir / "text_providers.yaml.example"
        self.image_providers_example_file = self.config_dir / "image_providers.yaml.example"
        
        self._platform_templates_cache = None
        self._text_providers_cache = None
        self._image_providers_cache = None
    
    def get_platform_templates(self) -> Dict[str, Any]:
        """获取平台模板配置"""
        if self._platform_templates_cache is None:
            self._platform_templates_cache = self._load_yaml(
                self.platform_templates_file, {}
            )
        return self._platform_templates_cache
    
    def get_platform_template(self, platform: str) -> Optional[Dict[str, Any]]:
        """获取指定平台模板"""
        templates = self.get_platform_templates()
        platform_templates = templates.get("platform_templates", {})
        return platform_templates.get(platform)
    
    def update_platform_template(self, platform: str, template: Dict[str, Any]) -> bool:
        """更新平台模板配置"""
        try:
            templates = self.get_platform_templates()
            if "platform_templates" not in templates:
                templates["platform_templates"] = {}
            
            templates["platform_templates"][platform] = template
            self._save_yaml(self.platform_templates_file, templates)
            
            # 清除缓存
            self._platform_templates_cache = None
            return True
            
        except Exception as e:
            print(f"更新平台模板失败: {str(e)}")
            return False
    
    def delete_platform_template(self, platform: str) -> bool:
        """删除平台模板配置"""
        try:
            templates = self.get_platform_templates()
            if "platform_templates" in templates and platform in templates["platform_templates"]:
                del templates["platform_templates"][platform]
                self._save_yaml(self.platform_templates_file, templates)
                
                # 清除缓存
                self._platform_templates_cache = None
                return True
            return False
            
        except Exception as e:
            print(f"删除平台模板失败: {str(e)}")
            return False
    
    def get_text_providers(self) -> Dict[str, Any]:
        """获取文本生成提供商配置"""
        if self._text_providers_cache is None:
            # 如果实际配置文件不存在，尝试从示例文件加载
            if not self.text_providers_file.exists() and self.text_providers_example_file.exists():
                self._text_providers_cache = self._load_yaml(
                    self.text_providers_example_file, {"providers": {}}
                )
            else:
                self._text_providers_cache = self._load_yaml(
                    self.text_providers_file, {"providers": {}}
                )
        return self._text_providers_cache
    
    def get_image_providers(self) -> Dict[str, Any]:
        """获取图像生成提供商配置"""
        if self._image_providers_cache is None:
            # 如果实际配置文件不存在，尝试从示例文件加载
            if not self.image_providers_file.exists() and self.image_providers_example_file.exists():
                providers_config = self._load_yaml(
                    self.image_providers_example_file, {"providers": {}}
                )
            else:
                providers_config = self._load_yaml(
                    self.image_providers_file, {"providers": {}}
                )
            
            # 解析所有提供商的supported_sizes字段
            import json
            providers = providers_config.get("providers", {})
            for provider_name, provider_config in providers.items():
                supported_sizes = provider_config.get("supported_sizes")
                if isinstance(supported_sizes, str):
                    try:
                        provider_config["supported_sizes"] = json.loads(supported_sizes)
                    except json.JSONDecodeError:
                        # 如果解析失败，使用默认空数组
                        provider_config["supported_sizes"] = []
                elif supported_sizes is None:
                    provider_config["supported_sizes"] = []
            
            self._image_providers_cache = providers_config
        return self._image_providers_cache
    
    def update_text_provider(self, provider_name: str, config: Dict[str, Any]) -> bool:
        """更新文本提供商配置"""
        try:
            providers = self.get_text_providers()
            if "providers" not in providers:
                providers["providers"] = {}
            
            # 检查是否需要重命名
            new_name = config.get("name")
            if new_name and new_name != provider_name:
                # 重命名逻辑：删除旧名称，添加新名称
                if provider_name in providers["providers"]:
                    # 删除旧配置
                    del providers["providers"][provider_name]
                # 使用新名称保存配置
                providers["providers"][new_name] = config
            else:
                # 不需要重命名，直接更新
                providers["providers"][provider_name] = config
            
            self._save_yaml(self.text_providers_file, providers)
            
            # 清除缓存
            self._text_providers_cache = None
            return True
            
        except Exception as e:
            print(f"更新文本提供商配置失败: {str(e)}")
            return False
    
    def delete_text_provider(self, provider_name: str) -> bool:
        """删除文本提供商配置"""
        try:
            providers = self.get_text_providers()
            if "providers" in providers and provider_name in providers["providers"]:
                del providers["providers"][provider_name]
                self._save_yaml(self.text_providers_file, providers)
                
                # 清除缓存
                self._text_providers_cache = None
                return True
            return False
            
        except Exception as e:
            print(f"删除文本提供商配置失败: {str(e)}")
            return False
    
    def update_image_provider(self, provider_name: str, config: Dict[str, Any]) -> bool:
        """更新图像提供商配置"""
        try:
            providers = self.get_image_providers()
            if "providers" not in providers:
                providers["providers"] = {}
            
            # 检查是否需要重命名
            new_name = config.get("name")
            if new_name and new_name != provider_name:
                # 重命名逻辑：删除旧名称，添加新名称
                if provider_name in providers["providers"]:
                    # 删除旧配置
                    del providers["providers"][provider_name]
                # 使用新名称保存配置
                providers["providers"][new_name] = config
            else:
                # 不需要重命名，直接更新
                providers["providers"][provider_name] = config
            
            self._save_yaml(self.image_providers_file, providers)
            
            # 清除缓存
            self._image_providers_cache = None
            return True
            
        except Exception as e:
            print(f"更新图像提供商配置失败: {str(e)}")
            return False
    
    def delete_image_provider(self, provider_name: str) -> bool:
        """删除图像提供商配置"""
        try:
            providers = self.get_image_providers()
            if "providers" in providers and provider_name in providers["providers"]:
                del providers["providers"][provider_name]
                self._save_yaml(self.image_providers_file, providers)
                
                # 清除缓存
                self._image_providers_cache = None
                return True
            return False
            
        except Exception as e:
            print(f"删除图像提供商配置失败: {str(e)}")
            return False
    
    def reload_config(self) -> bool:
        """重新加载配置文件"""
        try:
            # 清除所有缓存
            self._platform_templates_cache = None
            self._text_providers_cache = None
            self._image_providers_cache = None
            
            # 重新加载配置
            self.get_platform_templates()
            self.get_text_providers()
            self.get_image_providers()
            return True
            
        except Exception as e:
            print(f"重新加载配置失败: {str(e)}")
            return False
    
    def export_all_config(self) -> Dict[str, Any]:
        """导出所有配置"""
        return {
            "platform_templates": self.get_platform_templates(),
            "text_providers": self.get_text_providers(),
            "image_providers": self.get_image_providers(),
            "exported_at": self.get_current_time()
        }
    
    def get_current_time(self) -> str:
        """获取当前时间字符串"""
        return datetime.now().isoformat()
    
    def _load_yaml(self, file_path: Path, default: Any) -> Any:
        """加载YAML文件"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or default
            return default
        except Exception as e:
            print(f"加载YAML文件失败 {file_path}: {str(e)}")
            return default
    
    def _save_yaml(self, file_path: Path, data: Any) -> bool:
        """保存YAML文件"""
        try:
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            return True
            
        except Exception as e:
            print(f"保存YAML文件失败 {file_path}: {str(e)}")
            return False