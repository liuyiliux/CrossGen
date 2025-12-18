"""
测试配置文件
配置pytest测试环境
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def test_client():
    """创建FastAPI测试客户端
    
    Yields:
        TestClient: FastAPI测试客户端实例
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_generation_request():
    """提供示例生成请求数据
    
    Returns:
        dict: 示例生成请求数据
    """
    return {
        "topic": "秋季显白美甲",
        "platforms": ["xiaohongshu", "douyin"]
    }


@pytest.fixture
def sample_batch_generation_request():
    """提供示例批量生成请求数据
    
    Returns:
        dict: 示例批量生成请求数据
    """
    return {
        "topics": ["秋季显白美甲", "冬季护肤攻略"],
        "platforms": ["xiaohongshu", "wechat"]
    }


@pytest.fixture
def mock_openai_response():
    """提供模拟OpenAI响应数据
    
    Returns:
        dict: 模拟OpenAI响应数据
    """
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1734234567,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "这是生成的内容"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }