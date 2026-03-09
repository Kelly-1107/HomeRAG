"""
测试物品提取和更新逻辑优化

测试场景：
1. 提取不能无中生有
2. 颜色作为属性
3. 更新判断严格匹配
4. 完整流程测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agents.extraction_agent import ExtractionAgent
from services.llm_service import get_llm_service


def test_extraction_no_hallucination():
    """测试场景1：提取不能无中生有"""
    print("\n=== 测试场景1：提取不能无中生有 ===")

    llm = get_llm_service()
    agent = ExtractionAgent(llm)

    test_cases = [
        {
            "input": "我有一件羽绒服",
            "expected": {
                "name": "羽绒服",
                "location": "",
                "room": "",
                "attributes": [],
                "quantity": 1
            }
        },
        {
            "input": "黑色羽绒服在床下",
            "expected": {
                "name": "羽绒服",
                "location": "床下",
                "room": "",
                "attributes": ["黑色"],
                "quantity": 1
            }
        },
        {
            "input": "羽绒服在卧室的衣柜里",
            "expected": {
                "name": "���绒服",
                "location": "衣柜里",
                "room": "卧室",
                "attributes": [],
                "quantity": 1
            }
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"输入: {case['input']}")
        result = agent.extract(case['input'])
        print(f"输出: {result}")
        print(f"期望: {case['expected']}")

        # 验证关键字段
        if isinstance(result, dict):
            checks = []
            checks.append(("name", result.get("name") == case["expected"]["name"]))
            checks.append(("location", result.get("location") == case["expected"]["location"]))
            checks.append(("room", result.get("room") == case["expected"]["room"]))
            checks.append(("attributes", result.get("attributes") == case["expected"]["attributes"]))

            all_pass = all(check[1] for check in checks)
            print(f"验证结果: {'✓ 通过' if all_pass else '✗ 失败'}")
            for field, passed in checks:
                print(f"  - {field}: {'✓' if passed else '✗'}")
        else:
            print("验证结果: ✗ 失败（返回格式错误）")


def test_color_as_attribute():
    """测试场景2：颜色作为属性"""
    print("\n\n=== 测试场景2：颜色作为属性 ===")

    llm = get_llm_service()
    agent = ExtractionAgent(llm)

    test_cases = [
        "黑色羽绒服",
        "白色保温杯",
        "红色的毛衣在衣柜"
    ]

    for i, input_text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"输入: {input_text}")
        result = agent.extract(input_text)
        print(f"输出: {result}")

        if isinstance(result, dict):
            name = result.get("name", "")
            attributes = result.get("attributes", [])

            # 检查颜色是否在 attributes 中而不是 name 中
            colors = ["黑色", "白色", "红色", "蓝色", "绿色", "黄色"]
            has_color_in_name = any(color in name for color in colors)
            has_color_in_attrs = any(any(color in attr for color in colors) for attr in attributes)

            if not has_color_in_name and has_color_in_attrs:
                print("验证结果: ✓ 通过（颜色在 attributes 中）")
            elif has_color_in_name:
                print("验证结果: ✗ 失败（颜色在 name 中）")
            else:
                print("验证结果: ? 未检测到颜色")


def test_strict_update_matching():
    """测试场景3：更新判断严格匹配（需要手动验证）"""
    print("\n\n=== 测试场景3：更新判断严格匹配 ===")
    print("此测试需要通过实际 API 调用验证，建议手动测试：")
    print("\n步骤：")
    print("1. 记录：'黑色羽绒服在床下'")
    print("2. 记录：'白色羽绒服在衣柜'")
    print("3. 查询：'我有几件羽绒服' → 应返回 2 件")
    print("4. 更新：'黑色羽绒服���在在沙发上' → 应更新第一条记录")
    print("5. 查询：'黑色羽绒服在哪' → 应返回'沙发上'")
    print("6. 记录：'羽绒服在桌子上' → 应创建新记录（属性不匹配）")


if __name__ == "__main__":
    print("开始测试物品提取和更新逻辑优化...")

    try:
        test_extraction_no_hallucination()
        test_color_as_attribute()
        test_strict_update_matching()

        print("\n\n=== 测试完成 ===")
        print("注意：部分测试需要通过实际 API 调用验证")

    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
