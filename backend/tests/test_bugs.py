#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试脚本：复现 Bug 1 和 Bug 2"""

import requests
import json
import time
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_bugs"

def test_chat(message: str, description: str):
    """发送聊天请求并打印结果"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"输入: {message}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"user_id": USER_ID, "message": message},
            timeout=30
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功 ({elapsed:.1f}s)")
            print(f"回复: {result['reply']}")
            if result.get('memory_id'):
                print(f"Memory ID: {result['memory_id']}")
        else:
            print(f"❌ 失败 (HTTP {response.status_code})")
            print(f"错误: {response.text}")

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 异常 ({elapsed:.1f}s)")
        print(f"错��: {str(e)}")

def main():
    print("开始测试 HomeRAG Bug 修复")
    print(f"User ID: {USER_ID}")

    # 测试 1: 创建物品（应该成功）
    test_chat(
        "我有一件黄色短款皮衣",
        "Bug 1 - 创建物品（基线测试）"
    )

    time.sleep(2)

    # 测试 2: 更新物品位置（Bug 1 - 之前会 500 错误）
    test_chat(
        "床上里有一件黄色短款皮衣",
        "Bug 1 - 更新物品位置（之前 500 错误）"
    )

    time.sleep(2)

    # 测试 3: 创建另一件外套
    test_chat(
        "我有一件黑色羽绒服在衣柜里",
        "Bug 2 准备 - 创建羽绒服"
    )

    time.sleep(2)

    # 测试 4: 查询单个物品（应该成功）
    test_chat(
        "我有几件皮衣",
        "Bug 2 - 查询皮衣（基线测试）"
    )

    time.sleep(2)

    # 测试 5: 查询类别（Bug 2 - 之前只返回部分结果）
    test_chat(
        "我有几件外套",
        "Bug 2 - 查询外套类别（之前不完整）"
    )

    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
