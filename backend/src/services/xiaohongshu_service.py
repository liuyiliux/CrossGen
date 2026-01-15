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
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
        # 请求头配置
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
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
                # 如果有Cookie，尝试添加其他必要的头部
                headers['X-s'] = '' # 占位，实际可能需要更复杂的签名
                headers['X-t'] = str(int(time.time() * 1000))
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
            笔记详细信息，包含title, cover_url, description, source_url等
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
            
            # 提取标题
            title = ""
            title_tag = soup.find('h1', class_=re.compile(r'title|note-title'))
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            # 提取封面图
            cover_url = ""
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src', '')
                if src and ('cover' in src.lower() or 'note' in src.lower()):
                    cover_url = src
                    if cover_url.startswith('//'):
                        cover_url = 'https:' + cover_url
                    break
            # 如果没有找到封面图，使用第一张图片
            if not cover_url and img_tags:
                src = img_tags[0].get('src', '')
                if src:
                    cover_url = src
                    if cover_url.startswith('//'):
                        cover_url = 'https:' + cover_url
            
            # 提取文案/描述
            description = ""
            desc_tags = soup.find_all('span', class_=re.compile(r'note|content|desc'))
            if desc_tags:
                description = desc_tags[0].get_text(strip=True)
            # 如果没有找到，尝试从div中提取
            if not description:
                content_divs = soup.find_all('div', class_=re.compile(r'content|note'))
                if content_divs:
                    description = content_divs[0].get_text(strip=True, separator=' ')
            
            # 限制描述长度
            if len(description) > 200:
                description = description[:200] + "..."
            
            # 提取作者信息（可选）
            author = None
            author_tags = soup.find_all('span', class_=re.compile(r'author|user|name'))
            if author_tags:
                author = author_tags[0].get_text(strip=True)
            
            # 提取点赞数（可选）
            likes = 0
            like_tags = soup.find_all('span', class_=re.compile(r'like|count|engage'))
            if like_tags:
                likes_text = like_tags[0].get_text(strip=True)
                likes_match = re.search(r'\d+', likes_text)
                likes = int(likes_match.group()) if likes_match else 0
            
            result = {
                'title': title,
                'cover_url': cover_url,
                'description': description,
                'source_url': note_url,
                'author': author,
                'likes': likes
            }
            
            logger.info(f"笔记解析完成: {title[:30]}...")
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
