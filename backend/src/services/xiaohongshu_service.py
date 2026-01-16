"""
小红书爬虫服务
提供小红书关键词搜索和链接解析功能
"""

import re
import random
import time
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from src.utils.logger import logger
from src.services.config_service import ConfigService


class XiaohongshuService:
    """小红书爬虫服务类"""
    
    def __init__(self):
        """初始化爬虫服务"""
        self.config_service = ConfigService()
        # 随机User-Agent池，模拟不同浏览器
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        ]
        
        # 请求头配置
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Referer': 'https://www.xiaohongshu.com/',
        }
        
        # 请求延迟范围（秒），避免被反爬
        self.delay_range = (1, 3)
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(self.user_agents)
    
    def _get_headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        获取请求头，包含随机User-Agent
        
        Args:
            extra_headers: 额外的请求头
            
        Returns:
            完整的请求头字典
        """
        headers = self.headers.copy()
        headers['User-Agent'] = self._get_random_user_agent()
        
        if extra_headers:
            headers.update(extra_headers)
            
        # 从配置中获取Cookie
        try:
            system_config = self.config_service.get_system_config()
            cookie = system_config.get("xiaohongshu", {}).get("cookie", "")
            if cookie:
                headers['Cookie'] = cookie
                # 暂时移除 X-s 和 X-t，因为对于普通HTML请求可能不需要，且错误的签名可能导致反爬
                # headers['X-s'] = '' 
                # headers['X-t'] = str(int(time.time() * 1000))
        except Exception as e:
            logger.warning(f"获取小红书Cookie失败: {e}")
        
        return headers
    
    def _delay(self):
        """随机延迟，模拟真实用户行为"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        根据关键词搜索小红书内容
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            搜索结果列表，每个结果包含title, cover_url, description, source_url等
        """
        try:
            logger.info(f"开始搜索小红书关键词: {keyword}")
            
            # 构建搜索URL
            search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=54"
            
            # 简单的重试机制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # 发送请求
                    self._delay()
                    headers = self._get_headers()
                    response = requests.get(search_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        break
                    
                    logger.warning(f"搜索请求失败 (尝试 {attempt+1}/{max_retries})，状态码: {response.status_code}")
                    if attempt == max_retries - 1:
                        logger.error("搜索请求多次失败")
                        return []
                        
                except requests.RequestException as e:
                    logger.warning(f"搜索请求异常 (尝试 {attempt+1}/{max_retries}): {str(e)}")
                    if attempt == max_retries - 1:
                        logger.error("搜索请求多次异常")
                        return []
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # LOG: 记录页面基本信息
            logger.info(f"页面响应长度: {len(response.text)}")
            title_tag = soup.title
            if title_tag:
                logger.info(f"页面标题: {title_tag.string}")
            
            # 尝试从 window.__INITIAL_STATE__ 提取数据
            import json
            scripts = soup.find_all('script')
            found_initial_state = False
            
            for script in scripts:
                if script.string and "window.__INITIAL_STATE__" in script.string:
                    found_initial_state = True
                    try:
                        logger.info("找到 window.__INITIAL_STATE__，正在解析...")
                        json_str = script.string.replace("window.__INITIAL_STATE__=", "").replace("undefined", "null")
                        if json_str.strip().endswith(";"):
                            json_str = json_str.strip()[:-1]
                        data = json.loads(json_str)
                        
                        # LOG: 打印顶级键，帮助调试
                        logger.info(f"JSON顶级键: {list(data.keys())}")
                        
                        # 尝试从不同路径查找笔记数据
                        # 路径1: data['note']['items'] (如果存在)
                        # 路径2: data['search']['feeds'] (可能为空)
                        # 路径3: data['search']['notes'] (旧版)
                        
                        items = []
                        if 'note' in data and 'items' in data['note']:
                            logger.info("路径1 (note.items) 存在")
                            items = data['note']['items']
                        elif 'search' in data:
                            if 'notes' in data['search']:
                                logger.info("路径3 (search.notes) 存在")
                                items = data['search']['notes']
                            elif 'feeds' in data['search']:
                                logger.info("路径2 (search.feeds) 存在")
                                items = data['search']['feeds']
                            else:
                                logger.warning(f"search 键存在，但未找到 notes 或 feeds。search keys: {list(data['search'].keys())}")
                        else:
                            logger.warning("未找到 note 或 search 键")
                        
                        logger.info(f"找到 {len(items)} 个潜在笔记项")
                        
                        for item in items:
                            if not isinstance(item, dict):
                                continue
                                
                            # 提取字段
                            title = item.get('title', '') or item.get('display_title', '') or '无标题'
                            desc = item.get('desc', '') or item.get('description', '') or title
                            
                            # 封面图
                            cover = ''
                            if 'cover' in item:
                                cover = item['cover'].get('url', '')
                            elif 'images_list' in item and item['images_list']:
                                cover = item['images_list'][0].get('url', '')
                            
                            # ID和链接
                            note_id = item.get('id', '') or item.get('noteId', '')
                            source_url = f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else ""
                            
                            # 作者
                            user = item.get('user', {})
                            author = user.get('nickname', '') if user else '未知作者'
                            
                            # 点赞
                            likes = item.get('likes', 0) or item.get('interact_info', {}).get('liked_count', 0)
                            
                            if title and cover:
                                results.append({
                                    'title': title,
                                    'cover_url': cover,
                                    'description': desc,
                                    'source_url': source_url,
                                    'author': author,
                                    'likes': int(likes) if likes else 0
                                })
                                
                        if results:
                            logger.info(f"从INITIAL_STATE提取到 {len(results)} 条笔记")
                            return results[:limit]
                        else:
                            logger.warning("解析JSON成功但未提取到有效笔记数据")
                            
                    except Exception as e:
                        logger.warning(f"解析INITIAL_STATE失败: {e}")
            
            if not found_initial_state:
                logger.warning("未找到 window.__INITIAL_STATE__ 脚本标签")
                # 打印部分HTML以便调试（去除敏感信息）
                html_snippet = response.text[:500].replace('\n', ' ')
                logger.info(f"HTML片段: {html_snippet}...")
            
            # 如果从JSON提取失败，尝试旧的DOM解析方法
            logger.info("尝试DOM解析...")
            note_items = soup.find_all('div', class_=re.compile(r'note-item|search-result'))
            logger.info(f"DOM解析找到 {len(note_items)} 个元素")
            
            if not note_items and not results:
                logger.warning("未找到笔记元素")
                return []
                
            for item in note_items[:limit]:
                try:
                    # 提取标题
                    title_tag = item.find('a', class_=re.compile(r'title|note-title'))
                    title = title_tag.get_text(strip=True) if title_tag else "无标题"
                    
                    # 提取封面图
                    img_tag = item.find('img')
                    cover_url = img_tag.get('src', '') if img_tag else ''
                    # 处理懒加载图片
                    if cover_url and cover_url.startswith('//'):
                        cover_url = 'https:' + cover_url
                    
                    # 提取笔记链接
                    link_tag = item.find('a', href=True)
                    source_url = link_tag.get('href', '') if link_tag else ''
                    if source_url and not source_url.startswith('http'):
                        source_url = 'https://www.xiaohongshu.com' + source_url
                    
                    # 提取简介（从图片alt或描述文本中）
                    description = img_tag.get('alt', '') if img_tag else ""
                    if not description:
                        desc_tag = item.find('span', class_=re.compile(r'desc|description'))
                        description = desc_tag.get_text(strip=True) if desc_tag else title[:50]
                    
                    # 提取作者信息（可选）
                    author_tag = item.find('span', class_=re.compile(r'author|user-name'))
                    author = author_tag.get_text(strip=True) if author_tag else None
                    
                    # 提取点赞数（可选）
                    likes_tag = item.find('span', class_=re.compile(r'like|count'))
                    likes_text = likes_tag.get_text(strip=True) if likes_tag else '0'
                    # 从文本中提取数字
                    likes_match = re.search(r'\d+', likes_text)
                    likes = int(likes_match.group()) if likes_match else 0
                    
                    result = {
                        'title': title,
                        'cover_url': cover_url,
                        'description': description,
                        'source_url': source_url,
                        'author': author,
                        'likes': likes
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"解析笔记项失败: {str(e)}")
                    continue
            
            if not results:
                return []
                
            logger.info(f"搜索完成，共获取 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logger.error(f"搜索过程发生错误: {str(e)}")
            return []

    def parse_note_url(self, note_url: str) -> Optional[Dict[str, Any]]:
        """
        解析小红书笔记链接，提取详细信息
        
        Args:
            note_url: 小红书笔记链接
            
        Returns:
            笔记详细信息，包含title, cover_url, description, source_url, images等
        """
        try:
            logger.info(f"开始解析笔记链接: {note_url}")
            
            # 验证URL格式
            if not note_url.startswith('http'):
                if not note_url.startswith('www.'):
                    note_url = 'https://' + note_url
                else:
                    note_url = 'https://' + note_url
            
            # 发送请求
            self._delay()
            headers = self._get_headers()
            response = requests.get(note_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"笔记页面请求失败，状态码: {response.status_code}")
                return None
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 初始化结果字段
            title = ""
            description = ""
            cover_url = ""
            author = ""
            likes = 0
            images = []
            
            # 优先尝试从 window.__INITIAL_STATE__ 提取数据 (这是获取多图和准确信息的最佳方式)
            import json
            scripts = soup.find_all('script')
            initial_state_found = False
            
            for script in scripts:
                if script.string and "window.__INITIAL_STATE__" in script.string:
                    try:
                        logger.info("解析笔记页面 INITIAL_STATE...")
                        json_str = script.string.replace("window.__INITIAL_STATE__=", "").replace("undefined", "null")
                        if json_str.strip().endswith(";"):
                            json_str = json_str.strip()[:-1]
                        data = json.loads(json_str)
                        
                        # 尝试查找笔记数据
                        note_data = None
                        
                        # 路径1: note.note
                        if 'note' in data and 'note' in data['note']:
                            note_data = data['note']['note']
                        # 路径2: note.firstNote
                        elif 'note' in data and 'firstNote' in data['note']:
                            note_data = data['note']['firstNote']
                        # 路径3: note.noteDetailMap (Map结构，需要遍历或用ID)
                        elif 'note' in data and 'noteDetailMap' in data['note']:
                            detail_map = data['note']['noteDetailMap']
                            if detail_map:
                                # 取第一个值
                                temp_data = next(iter(detail_map.values()))
                                # 检查是否包裹在 'note' 字段中 (新版结构 fix)
                                if temp_data and 'note' in temp_data and isinstance(temp_data['note'], dict) and 'title' in temp_data['note']:
                                    note_data = temp_data['note']
                                else:
                                    note_data = temp_data
                        
                        if note_data:
                            initial_state_found = True
                            title = note_data.get('title', '') or note_data.get('display_title', '')
                            description = note_data.get('desc', '') or note_data.get('description', '')
                            
                            # 获取图片列表
                            if 'imageList' in note_data:
                                logger.info(f"Found imageList with {len(note_data['imageList'])} items")
                                images = []
                                for img in note_data['imageList']:
                                    # Try various keys
                                    url = img.get('urlDefault', '') or img.get('url', '') or img.get('infoList', [{}])[0].get('url', '')
                                    if url:
                                        images.append(url)
                            elif 'images_list' in note_data:
                                logger.info(f"Found images_list with {len(note_data['images_list'])} items")
                                images = [img.get('url', '') for img in note_data['images_list']]
                            else:
                                logger.warning("No imageList or images_list found in note_data")
                            
                            # 过滤空链接
                            images = [img for img in images if img]
                            if images:
                                cover_url = images[0]
                                
                            # 获取作者
                            user = note_data.get('user', {})
                            author = user.get('nickname', '')
                            
                            # 获取点赞
                            likes = note_data.get('likes', 0) or note_data.get('interact_info', {}).get('liked_count', 0)
                            
                            logger.info("成功从 INITIAL_STATE 提取笔记详情")
                            break
                            
                    except Exception as e:
                        logger.warning(f"解析笔记 INITIAL_STATE 失败: {e}")
            
            # 如果 JSON 解析失败或缺少关键信息，尝试 Meta 标签和 DOM
            if not title or not initial_state_found:
                logger.info("尝试从 Meta 标签提取信息...")
                
                # Title: 优先 og:title -> title tag
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    title = meta_title.get('content', '')
                if not title:
                    if soup.title:
                        title = soup.title.string.replace(' - 小红书', '')
                
                # Fallback to h1 if still empty (but be careful of nav bars)
                if not title:
                    h1 = soup.find('h1', class_=re.compile(r'title|note-title'))
                    if h1:
                        title = h1.get_text(strip=True)
                
                # Description: og:description -> meta description
                meta_desc = soup.find('meta', property='og:description')
                if meta_desc:
                    description = meta_desc.get('content', '')
                if not description:
                    meta_desc_name = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc_name:
                        description = meta_desc_name.get('content', '')
                
                # Images: og:image (usually only one)
                if not images:
                    meta_image = soup.find('meta', property='og:image')
                    if meta_image:
                        cover_url = meta_image.get('content', '')
                        if cover_url:
                            images.append(cover_url)
                    
                    # Try finding content images
                    content_div = soup.find('div', class_=re.compile(r'content|note-content'))
                    if content_div:
                        img_tags = content_div.find_all('img')
                        for img in img_tags:
                            src = img.get('src', '')
                            if src and src not in images:
                                images.append(src)
            
            # 兜底：如果还是没找到图片，尝试页面所有大图（增强版）
            if not images:
                # 尝试查找 background-image
                div_tags = soup.find_all('div', style=re.compile(r'background-image'))
                for div in div_tags:
                    style = div.get('style', '')
                    match = re.search(r'url\("?([^")]+)"?\)', style)
                    if match:
                        url = match.group(1)
                        if url and ('sns-webpic' in url or 'ci.xiaohongshu.com' in url):
                            if url not in images:
                                images.append(url)

                img_tags = soup.find_all('img')
                for img in img_tags:
                    src = img.get('src', '')
                    # 简单的过滤逻辑，排除头像、图标等小图
                    if src and ('cover' in src or 'sns-webpic' in src or 'ci.xiaohongshu.com' in src):
                         if src not in images:
                            images.append(src)
            
            # 确保 cover_url 存在
            if not cover_url and images:
                cover_url = images[0]
            
            # 处理 URL 协议
            if cover_url and cover_url.startswith('//'):
                cover_url = 'https:' + cover_url
            
            # 规范化所有图片链接
            final_images = []
            for img in images:
                if img.startswith('//'):
                    final_images.append('https:' + img)
                elif img.startswith('http'):
                    final_images.append(img)
            images = final_images
            
            # 如果标题还是为空，使用默认
            if not title:
                title = "无标题笔记"
            
            result = {
                'title': title,
                'cover_url': cover_url,
                'description': description,
                'source_url': note_url,
                'author': author,
                'likes': int(likes) if likes else 0,
                'images': images # 新增图片列表
            }
            
            logger.info(f"笔记解析完成: {title[:30]}... (包含 {len(images)} 张图片)")
            return result
            
        except requests.RequestException as e:
            logger.error(f"笔记链接请求异常: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"解析笔记过程发生错误: {str(e)}")
            return None
    
    def search_or_parse(self, keyword_or_url: str, limit: int = 10) -> Dict[str, Any]:
        """
        统一接口：根据输入自动判断是搜索还是解析
        
        Args:
            keyword_or_url: 关键词或笔记链接
            limit: 搜索结果数量限制
            
        Returns:
            包含success, items, error的响应字典
        """
        # 判断是URL还是关键词
        if self._is_url(keyword_or_url):
            # 链接解析
            result = self.parse_note_url(keyword_or_url)
            if result:
                return {
                    'success': True,
                    'items': [result],
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'items': [],
                    'error': '解析笔记失败，请检查链接是否正确'
                }
        else:
            # 关键词搜索
            results = self.search_by_keyword(keyword_or_url, limit)
            if results:
                return {
                    'success': True,
                    'items': results,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'items': [],
                    'error': '未找到相关内容'
                }
    
    def _is_url(self, text: str) -> bool:
        """
        判断文本是否为URL
        
        Args:
            text: 待判断的文本
            
        Returns:
            True表示是URL，False表示是关键词
        """
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


# 全局实例
xiaohongshu_service = XiaohongshuService()
