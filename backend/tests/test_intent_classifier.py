import pytest
from unittest.mock import MagicMock

from agents.intent_classifier import IntentClassifier, Intent


class MockLLMService:
    """Mock LLM 服务，用于测试。"""

    def complete(self, prompt: str, system: str = None) -> str:
        # Mock 返回值
        if "记录" in prompt or "羽绒服" in prompt:
            return "record"
        if "在哪" in prompt or "找" in prompt:
            return "query"
        return "query"


def test_intent_classifier_record():
    """测试意图分类 - 记录。"""
    llm = MockLLMService()
    classifier = IntentClassifier(llm)

    result = classifier.classify("我的羽绒服在衣柜右边")
    assert result == Intent.RECORD


def test_intent_classifier_query():
    """测试意图分类 - 查询。"""
    llm = MockLLMService()
    classifier = IntentClassifier(llm)

    result = classifier.classify("我的羽绒服在哪？")
    assert result == Intent.QUERY
