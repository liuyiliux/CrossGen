"""
API测试用例
测试主要API端点
"""

from fastapi.testclient import TestClient
import pytest


def test_health_check(test_client: TestClient):
    """测试健康检查端点
    
    Args:
        test_client: FastAPI测试客户端
    """
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "services" in response.json()
    assert "system" in response.json()


def test_ready_check(test_client: TestClient):
    """测试就绪检查端点
    
    Args:
        test_client: FastAPI测试客户端
    """
    response = test_client.get("/health/ready")
    assert response.status_code == 200
    assert "ready" in response.json()
    assert "services" in response.json()


def test_live_check(test_client: TestClient):
    """测试存活检查端点
    
    Args:
        test_client: FastAPI测试客户端
    """
    response = test_client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_root_endpoint(test_client: TestClient):
    """测试根端点
    
    Args:
        test_client: FastAPI测试客户端
    """
    response = test_client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()
    assert "docs" in response.json()


def test_generate_single(test_client: TestClient, sample_generation_request):
    """测试单个内容生成端点
    
    Args:
        test_client: FastAPI测试客户端
        sample_generation_request: 示例生成请求数据
    """
    response = test_client.post("/api/generate", json=sample_generation_request)
    assert response.status_code == 200
    assert "success" in response.json()
    assert "results" in response.json()
    assert "message" in response.json()
    assert "generation_time" in response.json()


def test_batch_generate(test_client: TestClient, sample_batch_generation_request):
    """测试批量生成端点
    
    Args:
        test_client: FastAPI测试客户端
        sample_batch_generation_request: 示例批量生成请求数据
    """
    response = test_client.post("/api/batch", json=sample_batch_generation_request)
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert "status" in response.json()
    assert "message" in response.json()


def test_get_platform_templates(test_client: TestClient):
    """测试获取平台模板端点
    
    Args:
        test_client: FastAPI测试客户端
    """
    response = test_client.get("/api/config/templates")
    assert response.status_code == 200
    assert "templates" in response.json()


def test_get_text_providers(test_client: TestClient):
    """测试获取文本提供商端点
    
    Args:
        test_client: FastAPI测试客户端
    """
    response = test_client.get("/api/config/providers/text")
    assert response.status_code == 200
    assert "providers" in response.json()


def test_get_image_providers(test_client: TestClient):
    """测试获取图像提供商端点
    
    Args:
        test_client: FastAPI测试客户端
    """
    response = test_client.get("/api/config/providers/image")
    assert response.status_code == 200
    assert "providers" in response.json()
