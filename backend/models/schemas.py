from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime


# --- Request Schemas ---

class MemoryCreateRequest(BaseModel):
    user_id: str
    raw_text: str


class RecordRequest(BaseModel):
    """Record 流程的请求模型。"""
    user_id: str
    message: str


class MemoryUpdateRequest(BaseModel):
    structured_data: dict


# --- Response Schemas ---

class MemoryResponse(BaseModel):
    id: int
    user_id: str
    raw_text: str
    type: str
    structured_data: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemoryListItem(BaseModel):
    """记忆列表项（用于前端可视化展示）"""
    id: int
    name: str
    quantity: int = 1
    location: str
    room: str = ""  # 默认为空字符串
    attributes: list = []  # 默认为空列表
    raw_text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    memory_id: Optional[int] = None  # 如果是 record 操作，返回 memory_id


class RoomStatsResponse(BaseModel):
    room: str
    count: int


class RecentUpdateResponse(BaseModel):
    id: int
    name: str
    location: str
    updated_at: datetime
