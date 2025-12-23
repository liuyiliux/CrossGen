import requests
import json

# 测试生成单张图片API，带参考图片
def test_generate_image():
    url = "http://localhost:8000/api/generate/image"
    headers = {"Content-Type": "application/json"}
    data = {
        "history_id": "test_id",
        "page_index": 0,
        "prompt": "一张猫的图片",
        "image_provider": "siliconflow-Qwen-Image",
        "reference_images": [
            {
                "type": "image_url",
                "image_url": "https://example.com/cat.jpg"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求失败: {str(e)}")

if __name__ == "__main__":
    test_generate_image()
