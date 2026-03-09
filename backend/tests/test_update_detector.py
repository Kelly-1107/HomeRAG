import pytest
from unittest.mock import MagicMock

from agents.update_detector import UpdateDetector


class MockLLMService:
    """Mock LLM 服务，用于测试。"""

    def complete(self, prompt: str, system: str = None) -> str:
        if "更新" in prompt:
            return "update"
        return "new"


def test_update_detector_exists():
    """测试更新判断 - 已存在物品。"""
    llm = MockLLMService()
    detector = UpdateDetector(llm)

    # Mock db session
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = {
        "name": "羽绒服",
        "location": "衣柜左边"
    }

    extracted = {"name": "羽绒服", "location": "衣柜右边"}
    result = detector.is_update(mock_db, "user_001", extracted)

    assert result is True


def test_update_detector_new():
    """测试更新判断 - 新物品。"""
    llm = MockLLMService()
    detector = UpdateDetector(llm)

    # Mock db session - 不存在同名物品
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    extracted = {"name": "新物品"}
    result = detector.is_update(mock_db, "user_001", extracted)

    assert result is False
