"""
直接测试图像生成功能
调用GenerationService的generate_single_image方法
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from src.services.generation_service import GenerationService

async def test_direct_image_generation():
    """直接测试图像生成功能"""
    print("=== 开始直接测试图像生成功能 ===")
    
    # 创建GenerationService实例
    service = GenerationService()
    
    # 初始化提供商管理器
    if not await service.initialize_provider_manager():
        print("✗ 提供商管理器初始化失败")
        return
    
    # 测试数据
    prompt = "测试图片生成"
    image_provider = "百炼-z-image-turbo"
    reference_images = None
    
    # 调用generate_single_image方法
    try:
        result = await service.generate_single_image(
            prompt=prompt,
            image_provider=image_provider,
            reference_images=reference_images
        )
        
        # 打印结果
        print(f"响应结果: {result}")
        
        if result.get("success"):
            print(f"✓ 图像生成成功")
            print(f"生成的图像URL: {result.get('images')}")
        else:
            print(f"✗ 图像生成失败，错误信息: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ 图像生成失败，异常信息: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_direct_image_generation())