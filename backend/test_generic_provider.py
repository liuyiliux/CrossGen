"""
测试通用图像提供商功能
模拟百炼API的响应，验证代码逻辑
"""

import sys
import os
from unittest.mock import AsyncMock, patch

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.providers.base_provider import ProviderConfig
from src.providers.generic_image_provider import GenericImageProvider

async def test_generic_provider():
    """测试通用图像提供商功能"""
    print("=== 开始测试通用图像提供商功能 ===")
    
    # 创建配置
    provider_config = ProviderConfig(
        name="test_bailian",
        enabled=True,
        provider_type="image",
        api_key="test_key",
        base_url="https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        model="z-image-turbo",
        timeout=30,
        retry_count=2
    )
    
    # 添加通用配置（作为对象属性，而不是字典键值对）
    # 使用单行JSON字符串，避免转义问题
    setattr(provider_config, 'request_config', {
        "template": '{"model": "{{ model }}", "input": {"messages": [{"role": "user", "content": [{"text": "{{ prompt }}"}]}]}, "parameters": {"size": "{{ size }}", "prompt_extend": false, "negative_prompt": ""}}',
        "defaults": {
            "size": "1024*1024",
            "n": 1
        },
        "parameter_transforms": {
            "size": "{{ size.replace('x', '*') }}"
        }
    })
    
    setattr(provider_config, 'response_config', {
        "images_path": "$.output.images[*].url",
        "usage_path": "$.usage",
        "error_path": "$.error.message"
    })
    
    setattr(provider_config, 'size_config', {
        "total_pixels": {
            "min": "512*512",
            "max": "2048*2048"
        }
    })
    
    setattr(provider_config, 'supported_sizes', [
        "1024*1024",
        "1120*1440",
        "1440*1120"
    ])
    
    # 创建提供商实例
    provider = GenericImageProvider(provider_config)
    
    # 测试1: 模板渲染
    print("\n测试1: 模板渲染")
    test_params = {
        "model": "z-image-turbo",
        "prompt": "测试图片生成",
        "size": "1024x1024"
    }
    
    try:
        request_body = provider._render_request(test_params)
        print(f"  输入参数: {test_params}")
        print(f"  渲染结果: {request_body}")
        
        # 验证渲染结果
        assert request_body["model"] == "z-image-turbo", f"模型不匹配: {request_body['model']}"
        assert request_body["input"]["messages"][0]["content"][0]["text"] == "测试图片生成", f"提示词不匹配"
        assert request_body["parameters"]["size"] == "1024x1024", f"尺寸不匹配: {request_body['parameters']['size']}"
        print("  ✓ 模板渲染测试通过")
    except Exception as e:
        print(f"  ✗ 模板渲染测试失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试2: 尺寸处理
    print("\n测试2: 尺寸处理")
    
    # 测试x分隔的尺寸转换为*分隔
    try:
        processed_size = provider._process_size("1024x1024")
        print(f"  输入尺寸: 1024x1024")
        print(f"  处理结果: {processed_size}")
        assert processed_size == "1024*1024", f"尺寸转换失败: {processed_size}"
        print("  ✓ 尺寸转换测试通过")
    except Exception as e:
        print(f"  ✗ 尺寸转换测试失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试默认尺寸
    try:
        processed_size = provider._process_size(None)
        print(f"  输入尺寸: None")
        print(f"  处理结果: {processed_size}")
        assert processed_size == "1024*1024", f"默认尺寸失败: {processed_size}"
        print("  ✓ 默认尺寸测试通过")
    except Exception as e:
        print(f"  ✗ 默认尺寸测试失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试3: 尺寸验证
    print("\n测试3: 尺寸验证")
    
    # 测试有效尺寸
    try:
        provider._validate_size("1024*1024")
        print(f"  有效尺寸: 1024*1024 - ✓ 通过")
    except ValueError as e:
        print(f"  有效尺寸: 1024*1024 - ✗ 失败: {e}")
        return
    
    # 测试4: JSONPath解析
    print("\n测试4: JSONPath解析")
    
    # 模拟百炼API响应
    mock_response = {
        "output": {
            "images": [
                {
                    "url": "https://example.com/image1.jpg"
                },
                {
                    "url": "https://example.com/image2.jpg"
                }
            ]
        },
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 0,
            "total_tokens": 100
        }
    }
    
    # 测试提取图像URL
    try:
        images = provider._extract_from_response(mock_response, "$.output.images[*].url", is_list=True)
        print(f"  提取图像URL: {images}")
        assert len(images) == 2, f"提取图像数量失败: {len(images)}"
        assert images[0] == "https://example.com/image1.jpg", f"图像URL不匹配: {images[0]}"
        print("  ✓ 图像URL提取测试通过")
    except Exception as e:
        print(f"  ✗ 图像URL提取测试失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试5: 模拟API调用
    print("\n测试5: 模拟API调用")
    
    try:
        # 初始化提供商
        provider.client = AsyncMock()
        provider.initialized = True
        
        # 模拟HTTP响应（使用更接近实际百炼API的响应结构）
        mock_httpx_response = AsyncMock()
        mock_httpx_response.status_code = 200
        # 修正模拟响应结构，确保与response_config.images_path匹配
        real_mock_response = {
            "output": {
                "images": [
                    {"url": "https://example.com/image1.jpg"},
                    {"url": "https://example.com/image2.jpg"}
                ]
            },
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 0,
                "total_tokens": 100
            }
        }
        mock_httpx_response.json.return_value = real_mock_response
        mock_httpx_response.text = str(real_mock_response)
        mock_httpx_response.headers = {}
        
        provider.client.request.return_value = mock_httpx_response
        
        # 调用generate_image方法
        result = await provider.generate_image(
            prompt="测试图片生成",
            platform="xiaohongshu",
            size="1024x1024"
        )
        
        print(f"  生成结果: {result}")
        assert result["success"] == True, f"生成结果失败: {result}"
        assert len(result["images"]) == 2, f"生成图像数量失败: {len(result['images'])}"
        print("  ✓ 模拟API调用测试通过")
    except Exception as e:
        print(f"  ✗ 模拟API调用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n=== 测试完成 ===")
    print("所有测试通过！通用图像提供商功能正常")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_generic_provider())
