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
        
        # 检查是否是本地相对路径
        if image_url.startswith("/"):
            # 直接返回相对路径，不需要下载
            logger.info(f"检测到本地相对路径 {image_url}，直接返回")
            return image_url
        
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
                image_url = image_data.get("image_url", "")
                return download_image(image_url, save_dir, filename)
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
            elif image_data.startswith("/"):
                # 本地相对路径，直接返回
                logger.info(f"检测到本地相对路径 {image_data}，直接返回")
                return image_data
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
            logger.error(f"原有图片不存在: {old_image_path}")
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


def convert_local_path_to_data_url(file_path: str, base_dir: Path = None) -> Optional[str]:
    """
    将本地文件路径转换为data URL格式
    
    Args:
        file_path: 本地文件路径（可以是相对路径或绝对路径）
        base_dir: 基础目录，用于处理相对路径
        
    Returns:
        data URL字符串（格式：data:image/format;base64,encoded_data），失败返回None
    """
    try:
        # 处理相对路径
        if file_path.startswith("/") or (base_dir and not Path(file_path).is_absolute()):
            if base_dir:
                # 直接使用提供的base_dir拼接路径
                full_path = base_dir / file_path.lstrip("/")
            else:
                # 如果没有提供base_dir，尝试从项目根目录解析
                from pathlib import Path
                project_root = Path(__file__).parent.parent.parent
                if file_path.startswith("/history/"):
                    # history文件夹在backend目录下
                    # 正确处理路径：/history/folder_name_images/filename.png
                    history_path = file_path.lstrip("/history/")
                    # 获取完整的history子路径，包括folder_name_images部分
                    history_subpath = "/".join(history_path.split("/")[:-1])
                    filename = history_path.split("/")[-1]
                    full_path = project_root / "backend" / "history" / history_subpath / filename
                elif file_path.startswith("/uploads/"):
                    # uploads文件夹在项目根目录下
                    uploads_path = file_path.lstrip("/uploads/")
                    uploads_subpath = "/".join(uploads_path.split("/")[:-1])
                    filename = uploads_path.split("/")[-1]
                    full_path = project_root / "uploads" / uploads_subpath / filename
                else:
                    logger.error(f"无法解析文件路径: {file_path}")
                    return None
        else:
            full_path = Path(file_path)
        
        # 检查文件是否存在
        if not full_path.exists():
            logger.error(f"文件不存在: {full_path}")
            # 尝试使用不同的基础目录
            project_root = Path(__file__).parent.parent.parent.parent
            alternative_path = project_root / file_path.lstrip("/")
            if alternative_path.exists():
                logger.info(f"尝试使用备选路径: {alternative_path}")
                full_path = alternative_path
            else:
                logger.error(f"备选路径也不存在: {alternative_path}")
                return None
        
        # 读取文件并转换为base64
        with open(full_path, 'rb') as f:
            file_data = f.read()
        
        # 根据文件扩展名确定MIME类型
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        file_ext = full_path.suffix.lower()
        mime_type = mime_types.get(file_ext, 'image/png')
        
        # 转换为base64并构建data URL
        base64_data = base64.b64encode(file_data).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_data}"
        
        return data_url
    except Exception as e:
        logger.error(f"转换文件路径为data URL失败 {file_path}: {str(e)}", exc_info=True)
        return None
