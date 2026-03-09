import pytest
import json
from unittest.mock import MagicMock

from agents.extraction_agent import ExtractionAgent


class MockLLMService:
    """Mock LLM 服务，用于测试。"""

    def complete(self, prompt: str, system: str = None) -> str:
        # Mock 返回标准 JSON
        return json.dumps({
            "type": "item",
            "name": "羽绒服",
            "location": "衣柜右边",
            "room": "卧室",
            "attributes": ["黑色", "冬季"]
        })


def test_extraction_agent():
    """测试结构化抽取。"""
    llm = MockLLMService()
    agent = ExtractionAgent(llm)

    result = agent.extract("我的黑色羽绒服在卧室衣柜右边")

    assert result["type"] == "item"
    assert result["name"] == "羽绒服"
    assert result["location"] == "衣柜右边"
    assert result["room"] == "卧室"
    assert "黑色" in result["attributes"]
