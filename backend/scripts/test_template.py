#!/usr/bin/env python3
"""测试模板渲染"""
import yaml
from jinja2 import Template
from pathlib import Path

# 加载配置
config_path = Path(__file__).parent.parent.parent / "config" / "image_providers.yaml"
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 获取模板
provider_config = config['providers']['百炼-Qwen-Image-Edit']
template_str = provider_config['request_config']['template']

print("=" * 80)
print("原始模板:")
print("=" * 80)
print(template_str)
print()

# 测试数据
test_params = {
    "model": "qwen-image-edit",
    "final_content": [
        {"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
        {"text": "改成短发"}
    ],
    "n": 1,
    "negative_prompt": "",
    "size": "1024*1792"
}

print("=" * 80)
print("测试参数:")
print("=" * 80)
print(test_params)
print()

# 渲染模板
template = Template(template_str)
rendered = template.render(**test_params)

print("=" * 80)
print("渲染后的内容:")
print("=" * 80)
print(rendered)
print()

# 尝试解析为JSON
import json
try:
    result = json.loads(rendered)
    print("=" * 80)
    print("✓ JSON解析成功!")
    print("=" * 80)
    print("解析后的JSON:")
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(result)
except json.JSONDecodeError as e:
    print("=" * 80)
    print("✗ JSON解析失败!")
    print("=" * 80)
    print(f"错误: {e}")
    print(f"错误位置: 行 {e.lineno}, 列 {e.colno}")
    lines = rendered.split('\n')
    if e.lineno <= len(lines):
        error_line = lines[e.lineno-1]
        print(f"错误行: {error_line}")
        start = max(0, e.colno-50)
        end = min(len(error_line), e.colno+50)
        print(f"错误位置附近: '{error_line[start:end]}'")
