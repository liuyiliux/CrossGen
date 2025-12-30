"""
图片处理工具模块
处理图片下载、存储和管理
"""

import os
import uuid
import requests
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import base64
from io import BytesIO
from PIL import Image

# 设置日志记录器
logger = logging.getLogger("image_utils")


def download_image(image_url: str, save_dir: Path, filename: Optional[str] = None) -> Optional[str]:
    """
    下载图片到本地文件夹
    
    Args:
        image_url: 图片URL
        save_dir: 保存目录
        filename: 文件名，默认为UUID生成
        
    Returns:
        保存的图片路径，失败返回None
    """
    try:
        # 检查是否是base64编码的图片URL
        if image_url.startswith("data:image/"):
            # 直接调用save_base64_image处理
            return save_base64_image(image_url, save_dir, filename)
        
        # 检查是否是本地服务器URL，避免循环下载
        local_server_urls = [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "https://localhost:8000",
            "https://127.0.0.1:8000"
        ]
        
        # 检查是否是本地服务器URL
        is_local_url = any(image_url.startswith(url) for url in local_server_urls)
        if is_local_url:
            # 如果是本地服务器URL，直接返回相对路径，不进行下载
            # 提取相对路径
            relative_path = image_url.replace("http://localhost:8000", "").replace("http://127.0.0.1:8000", "").replace("https://localhost:8000", "").replace("https://127.0.0.1:8000", "")
            logger.info(f"检测到本地服务器URL {image_url}，直接返回相对路径 {relative_path}")
            return relative_path
        
        # 创建保存目录
        save_dir.mkdir(exist_ok=True)
        
        # 生成文件名
        if not filename:
            file_ext = image_url.split('.')[-1].lower()
            if len(file_ext) > 5:
                file_ext = 'png'  # 默认使用png格式
            filename = f"{uuid.uuid4()}.{file_ext}"
        
        # 保存路径
        save_path = save_dir / filename
        
        # 下载图片
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # 保存图片
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        # 返回相对URL，便于前端访问
        # 判断是否是历史记录目录
        if 'history' in str(save_dir):
            # 历史记录图片，返回 /history/xxx_images/filename.png 格式
            return f"/history/{save_dir.name}/{filename}"
        else:
            # 上传图片，返回 /uploads/temp_xxx/filename.png 格式
            return f"/uploads/{save_dir.name}/{filename}"
    except requests.exceptions.RequestException as e:
        logger.error(f"下载图片失败 {image_url}: 请求错误 - {str(e)}", exc_info=True)
        return None
    except IOError as e:
        logger.error(f"下载图片失败 {image_url}: IO错误 - {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"下载图片失败 {image_url}: 未知错误 - {str(e)}", exc_info=True)
        return None


def save_base64_image(base64_str: str, save_dir: Path, filename: Optional[str] = None) -> Optional[str]:
    """
    保存base64编码的图片到本地文件夹
    
    Args:
        base64_str: base64编码的图片
        save_dir: 保存目录
        filename: 文件名，默认为UUID生成
        
    Returns:
        保存的图片路径，失败返回None
    """
    try:
        # 创建保存目录
        save_dir.mkdir(exist_ok=True)
        
        # 生成文件名
        if not filename:
            filename = f"{uuid.uuid4()}.png"  # 默认使用png格式
        
        # 保存路径
        save_path = save_dir / filename
        
        # 处理base64字符串
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        # 解码并保存图片
        img_data = base64.b64decode(base64_str)
        with open(save_path, 'wb') as f:
            f.write(img_data)
        
        # 返回相对URL，便于前端访问
        # 判断是否是历史记录目录
        if 'history' in str(save_dir):
            # 历史记录图片，返回 /history/xxx_images/filename.png 格式
            return f"/history/{save_dir.name}/{filename}"
        else:
            # 上传图片，返回 /uploads/temp_xxx/filename.png 格式
            return f"/uploads/{save_dir.name}/{filename}"
    except base64.binascii.Error as e:
        logger.error(f"保存base64图片失败: Base64解码错误 - {str(e)}", exc_info=True)
        return None
    except IOError as e:
        logger.error(f"保存base64图片失败: IO错误 - {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"保存base64图片失败: 未知错误 - {str(e)}", exc_info=True)
        return None


def process_image(image_data: str or Dict[str, Any], save_dir: Path, filename: Optional[str] = None) -> Optional[str]:
    """
    处理图片数据，根据类型保存到本地文件夹
    
    Args:
        image_data: 图片数据，可以是URL、base64字符串或包含type和url的字典
        save_dir: 保存目录
        filename: 文件名，默认为UUID生成
        
    Returns:
        保存的图片路径，失败返回None
    """
    try:
        if isinstance(image_data, dict):
            # 处理字典类型，如 {"type": "image_url", "image_url": "http://example.com/image.jpg"}
            if image_data.get("type") == "image_url":
                return download_image(image_data.get("image_url", ""), save_dir, filename)
            else:
                logger.warning(f"不支持的图片数据类型: {image_data.get('type')}")
                return None
        elif isinstance(image_data, str):
            # 处理字符串类型
            if image_data.startswith("http://") or image_data.startswith("https://"):
                # URL类型
                return download_image(image_data, save_dir, filename)
            elif image_data.startswith("data:image/"):
                # Base64类型
                return save_base64_image(image_data, save_dir, filename)
            else:
                logger.warning(f"不支持的图片字符串格式: {image_data[:50]}...")
                return None
        else:
            logger.warning(f"不支持的图片数据类型: {type(image_data)}")
            return None
    except Exception as e:
        logger.error(f"处理图片失败: {str(e)}", exc_info=True)
        return None


def replace_image(old_image_path: str, new_image_url: str) -> Optional[str]:
    """
    替换原有图片
    
    Args:
        old_image_path: 原有图片路径
        new_image_url: 新图片URL
        
    Returns:
        新图片路径，失败返回None
    """
    try:
        old_path = Path(old_image_path)
        if not old_path.exists():
            print(f"原有图片不存在: {old_image_path}")
            return None
        
        # 检查是否是本地服务器URL，避免循环下载
        local_server_urls = [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "https://localhost:8000",
            "https://127.0.0.1:8000"
        ]
        
        # 检查是否是本地服务器URL
        is_local_url = any(new_image_url.startswith(url) for url in local_server_urls)
        if is_local_url:
            # 如果是本地服务器URL，直接返回相对路径，不进行下载和替换
            # 提取相对路径
            relative_path = new_image_url.replace("http://localhost:8000", "").replace("http://127.0.0.1:8000", "").replace("https://localhost:8000", "").replace("https://127.0.0.1:8000", "")
            logger.info(f"检测到本地服务器URL {new_image_url}，直接返回相对路径 {relative_path}")
            return relative_path
        
        # 下载新图片，替换原有图片
        response = requests.get(new_image_url, timeout=30)
        response.raise_for_status()
        
        # 替换图片
        with open(old_path, 'wb') as f:
            f.write(response.content)
        
        # 返回相对URL，便于前端访问
        old_path = Path(old_image_path)
        # 判断是否是历史记录目录
        if 'history' in str(old_path):
            # 历史记录图片，返回 /history/xxx_images/filename.png 格式
            return f"/history/{old_path.parent.name}/{old_path.name}"
        else:
            # 上传图片，返回 /uploads/temp_xxx/filename.png 格式
            return f"/uploads/{old_path.parent.name}/{old_path.name}"
    except requests.exceptions.RequestException as e:
        logger.error(f"替换图片失败 {old_image_path}: 请求错误 - {str(e)}", exc_info=True)
        return None
    except IOError as e:
        logger.error(f"替换图片失败 {old_image_path}: IO错误 - {str(e)}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"替换图片失败 {old_image_path}: 未知错误 - {str(e)}", exc_info=True)
        return None
