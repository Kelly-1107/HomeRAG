#!/usr/bin/env python
"""测试删除 API 的脚本"""
import requests
import json

BASE_URL = "http://127.0.0.1:5175/api"
USER_ID = "user_001"

def test_single_delete():
    """测试单个删除"""
    print("=" * 50)
    print("测试单个删除")
    print("=" * 50)

    # 获取所有记忆
    response = requests.get(f"{BASE_URL}/memories", params={"user_id": USER_ID})
    memories = response.json()
    print(f"当前记忆数量: {len(memories)}")

    if len(memories) == 0:
        print("没有记忆可删除，先添加一条")
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"user_id": USER_ID, "message": "测试物品在测试位置"}
        )
        response = requests.get(f"{BASE_URL}/memories", params={"user_id": USER_ID})
        memories = response.json()

    # 删除第一条
    memory_id = memories[0]['id']
    print(f"删除记忆 ID: {memory_id}")

    response = requests.delete(f"{BASE_URL}/memories/{memory_id}")
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 验证
    response = requests.get(f"{BASE_URL}/memories", params={"user_id": USER_ID})
    remaining = response.json()
    print(f"删除后剩余: {len(remaining)}")
    print()

def test_batch_delete():
    """测试批量删除"""
    print("=" * 50)
    print("测试批量删除")
    print("=" * 50)

    # 获取所有记忆
    response = requests.get(f"{BASE_URL}/memories", params={"user_id": USER_ID})
    memories = response.json()
    print(f"当前记忆数量: {len(memories)}")

    if len(memories) < 2:
        print("记忆不足，先添加几条")
        for i in range(3):
            requests.post(
                f"{BASE_URL}/chat",
                json={"user_id": USER_ID, "message": f"测试物品{i}在位置{i}"}
            )
        response = requests.get(f"{BASE_URL}/memories", params={"user_id": USER_ID})
        memories = response.json()

    # 批量删除前两条
    ids_to_delete = [m['id'] for m in memories[:2]]
    print(f"批量删除 IDs: {ids_to_delete}")

    response = requests.post(
        f"{BASE_URL}/memories/batch-delete",
        json={"memory_ids": ids_to_delete}
    )
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")

    # 验证
    response = requests.get(f"{BASE_URL}/memories", params={"user_id": USER_ID})
    remaining = response.json()
    print(f"删除后剩余: {len(remaining)}")
    print()

def test_delete_not_found():
    """测试删除不存在的记忆"""
    print("=" * 50)
    print("测试删除不存在的记忆")
    print("=" * 50)

    response = requests.delete(f"{BASE_URL}/memories/99999")
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    print()

if __name__ == "__main__":
    try:
        test_single_delete()
        test_batch_delete()
        test_delete_not_found()
        print("✅ 所有测试通过！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
