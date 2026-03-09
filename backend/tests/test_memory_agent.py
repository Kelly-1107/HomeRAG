import pytest
from unittest.mock import MagicMock, patch

from agents.memory_agent import MemoryAgent


@patch("agents.memory_agent.get_llm_service")
def test_memory_agent_record_flow(mock_get_llm):
    """测试 MemoryAgent 记录流程。"""
    # Mock LLM 服务
    mock_llm = MagicMock()
    mock_llm.complete.return_value = "record"
    mock_llm.embed.return_value = [0.1] * 1536
    mock_get_llm.return_value = mock_llm

    agent = MemoryAgent()

    # Mock db session
    mock_db = MagicMock()

    result = agent.process(mock_db, "user_001", "我的羽绒服在衣柜右边")

    assert result.reply is not None
    assert "羽绒服" in result.reply


@patch("agents.memory_agent.get_llm_service")
def test_memory_agent_query_flow(mock_get_llm):
    """测试 MemoryAgent 查询流程。"""
    # Mock LLM 服务
    mock_llm = MagicMock()
    mock_llm.complete.return_value = "query"
    mock_llm.embed.return_value = [0.1] * 1536
    mock_get_llm.return_value = mock_llm

    agent = MemoryAgent()

    # Mock db session
    mock_db = MagicMock()

    result = agent.process(mock_db, "user_001", "我的羽绒服在哪？")

    assert result.reply is not None
