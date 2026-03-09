#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""原始测试用例验证"""

import requests
import json
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"
USER_ID = "final_verification"

def test_chat(message: str):
    """发送聊天请求"""
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"user_id": USER_ID, "message": message},
        timeout=30
    )
    return response

print("="*60)
print("原始测试用例验证")
print("="*60)

# 清空之前的测试数据（如果有）
print("\n1. 创建: 我有一件黄色短款皮衣")
r1 = test_chat("我有一件黄色短款皮衣")
print(f"   状态: {r1.status_code}")
print(f"   回复: {r1.json()['reply']}")
assert r1.status_code == 200, "创建失败"

time.sleep(2)

print("\n2. 更新: 床上里有一件黄色短款皮衣 (之前会 500 错误)")
r2 = test_chat("床上里有一件黄色短款皮衣")
print(f"   状态: {r2.status_code}")
print(f"   回复: {r2.json()['reply']}")
assert r2.status_code == 200, "更新失败 - Bug 1 未修复"

time.sleep(2)

print("\n3. 创建: 我有一件黑色羽绒服在衣柜里")
r3 = test_chat("我有一件黑色羽绒服在衣柜里")
print(f"   状态: {r3.status_code}")
print(f"   回复: {r3.json()['reply']}")
assert r3.status_code == 200, "创建失败"

time.sleep(2)

print("\n4. 查询: 我有几件皮衣")
r4 = test_chat("我有几件皮衣")
print(f"   状态: {r4.status_code}")
print(f"   回复: {r4.json()['reply']}")
assert r4.status_code == 200, "查询失败"
assert "皮衣" in r4.json()['reply'], "查询结果不包含皮衣"

time.sleep(2)

print("\n5. 查询: 我有几件外套 (之前只返回部分结果)")
r5 = test_chat("我有几件外套")
print(f"   状态: {r5.status_code}")
print(f"   回复: {r5.json()['reply']}")
assert r5.status_code == 200, "查询失败"
reply = r5.json()['reply']
assert "皮衣" in reply or "黄色" in reply, "查询结果不包含皮衣 - Bug 2 未修复"
assert "羽绒服" in reply or "黑色" in reply, "查询结果不包含羽绒服 - Bug 2 未修复"

print("\n" + "="*60)
print("✅ 所有原始测试用例通过！")
print("="*60)
print("\n验证结果:")
print("  ✅ Bug 1 (500 错误) 已修复")
print("  ✅ Bug 2 (不完整结果) 已修复")
print("  ✅ 所有功能正常工作")
