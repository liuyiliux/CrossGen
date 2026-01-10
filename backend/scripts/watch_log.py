#!/usr/bin/env python3
"""
实时监控日志文件
使用方法: python backend/scripts/watch_log.py
或者: powershell -ExecutionPolicy Bypass -File backend/scripts/watch_log.ps1
"""
import sys
import time
from pathlib import Path

# 获取日志文件路径
log_file = Path(__file__).parent.parent.parent / "backend" / "logs" / "app.log"

if not log_file.exists():
    print(f"日志文件不存在: {log_file}")
    sys.exit(1)

print(f"开始监控日志文件: {log_file}")
print("按 Ctrl+C 退出\n")

try:
    # 从文件末尾开始读取
    with open(log_file, 'r', encoding='utf-8') as f:
        # 移动到文件末尾
        f.seek(0, 2)

        while True:
            # 读取新内容
            line = f.readline()
            if line:
                # 确保在Windows上正确显示中文
                print(line.rstrip(), flush=True)
            else:
                # 如果没有新内容，等待一会儿
                time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n停止监控日志文件")
    sys.exit(0)
