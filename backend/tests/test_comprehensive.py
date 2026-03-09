#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""综合测试：验证所有功能"""

import requests
import json
import time
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"
USER_ID = "comprehensive_test"

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
            return True
        else:
            print(f"❌ 失败 (HTTP {response.status_code})")
            print(f"错误: {response.text}")
            return False

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ 异常 ({elapsed:.1f}s)")
        print(f"错误: {str(e)}")
        return False

def main():
    print("="*60)
    print("HomeRAG 综合功能测试")
    print(f"User ID: {USER_ID}")
    print("="*60)

    results = []

    # 测试 1: 创建物品
    results.append(("创建物品", test_chat(
        "我有一件红色连衣裙在卧室衣柜",
        "创建新物品"
    )))
    time.sleep(2)

    # 测试 2: 创建另一件物品
    results.append(("创建物品2", test_chat(
        "我有一件蓝色牛仔裤在客厅沙发上",
        "创建第二件物品"
    )))
    time.sleep(2)

    # 测试 3: 更新物品位置
    results.append(("更新位置", test_chat(
        "红色连衣裙现在在床上",
        "更新物品位置"
    )))
    time.sleep(2)

    # 测试 4: 查询单个物品
    results.append(("查询单个", test_chat(
        "我的红色连衣裙在哪里",
        "查询单个物品位置"
    )))
    time.sleep(2)

    # 测试 5: 查询类别
    results.append(("查询类别", test_chat(
        "我有几件衣服",
        "查询类别（应返回所有衣服）"
    )))
    time.sleep(2)

    # 测试 6: 模糊查询
    results.append(("模糊查询", test_chat(
        "我有什么裤子",
        "模糊查询"
    )))

    # 打印测试结果摘要
    print(f"\n{'='*60}")
    print("测试结果摘要")
    print(f"{'='*60}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    exit(main())
