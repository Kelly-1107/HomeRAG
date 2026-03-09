import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_chat_endpoint():
    """测试 /api/chat 接口。"""
    response = client.post("/api/chat", json={
        "user_id": "user_001",
        "message": "我的羽绒服在衣柜右边"
    })

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data


def test_list_memories():
    """测试 /api/memories 接口。"""
    response = client.get("/api/memories", params={
        "user_id": "user_001"
    })

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_room_stats():
    """测试 /api/stats/rooms 接口。"""
    response = client.get("/api/stats/rooms", params={
        "user_id": "user_001"
    })

    assert response.status_code == 200
    assert isinstance(response.json(), list)
