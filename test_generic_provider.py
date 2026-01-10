#!/usr/bin/env python3
"""
测试通用图像提供商的模板渲染功能
"""

import sys
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('backend'))

from src.providers.generic_image_provider import GenericImageProvider
from src.providers.base_provider import ProviderConfig
import yaml
import json

# 读取配置文件
def load_config():
    with open('config/image_providers.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def test_template_rendering():
    """测试模板渲染功能"""
    print("=== 测试通用图像提供商模板渲染 ===")
    
    # 加载配置
    config = load_config()
    provider_config = config['providers']['百炼-Qwen-Image-Edit']
    
    # 创建ProviderConfig对象
    provider_cfg = ProviderConfig(
        name=provider_config['name'],
        enabled=provider_config['enabled'],
        provider_type='image',
        api_key=provider_config['api_key'],
        base_url=provider_config['base_url'],
        model=provider_config['model'],
        timeout=provider_config['timeout'],
        retry_count=provider_config['retry_count'],
        headers=provider_config['headers'],
        supported_sizes=provider_config['supported_sizes'],
        support_reference_image=provider_config['support_reference_image'],
        support_multiple_reference_images=provider_config['support_multiple_reference_images'],
        reference_image_field=provider_config['reference_image_field']
    )
    
    # 添加通用配置
    provider_cfg.request_config = provider_config['request_config']
    provider_cfg.response_config = provider_config['response_config']
    provider_cfg.size_config = provider_config['size_config']
    
    # 创建提供商实例
    provider = GenericImageProvider(provider_cfg)
    
    # 模拟参考图
    reference_images = [
        {
            'type': 'image_url',
            'image_url': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
        }
    ]
    
    # 测试渲染请求
    params = {
        'model': provider_config['model'],
        'prompt': '测试图片生成',
        'size': '1024*1024',
        'reference_images': reference_images
    }
    
    # 直接调用_render_request方法测试
    import asyncio
    
    async def test_render():
        # 初始化提供商
        await provider.initialize()
        
        # 模拟内部处理逻辑
        provider._render_request(params)
        
    asyncio.run(test_render())

if __name__ == '__main__':
    test_template_rendering()
