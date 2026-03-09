from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.sqlite import get_db
from models.schemas import RoomStatsResponse, RecentUpdateResponse
from services.memory_service import MemoryService

router = APIRouter()
memory_service = MemoryService()


@router.get("/stats")
def get_stats(user_id: str, db: Session = Depends(get_db)):
    """获取基础统计信息。"""
    memories = memory_service.list_by_user(db, user_id)
    total_memories = len(memories)

    latest_memory = memory_service.get_latest_memory(db, user_id)
    latest_memory_name = latest_memory.structured_data.get("name") if latest_memory else None
    last_updated_at = latest_memory.updated_at.isoformat() if latest_memory else None

    return {
        "total_memories": total_memories,
        "latest_memory_name": latest_memory_name,
        "last_updated_at": last_updated_at
    }


@router.get("/stats/rooms", response_model=list[RoomStatsResponse])
def get_room_stats(user_id: str, type: str = None, db: Session = Depends(get_db)):
    """
    获取分布统计。
    - item 类型：按 room 字段聚合
    - consumption 类型：按 location 字段聚合
    """
    memories = memory_service.list_by_user(db, user_id, type_filter=type)
    if not memories:
        return []

    room_counts = {}

    for memory in memories:
        if type == "consumption":
            # 消费类型使用 location 字段
            room = memory.structured_data.get("location") or "未分类"
        else:
            # 物品类型使用 room 字段
            room = memory.structured_data.get("room") or "未分类"
        room_counts[room] = room_counts.get(room, 0) + 1

    return [
        RoomStatsResponse(room=room, count=count)
        for room, count in room_counts.items()
    ]


@router.get("/stats/recent", response_model=list[RecentUpdateResponse])
def get_recent_updates(user_id: str, limit: int = 10, type: str = None, db: Session = Depends(get_db)):
    """
    获取最近更新记录。
    按 updated_at 降序排列。
    """
    memories = memory_service.list_by_user(db, user_id, type_filter=type)
    if not memories:
        return []

    # 按更新时间降序排序
    sorted_memories = sorted(memories, key=lambda m: m.updated_at, reverse=True)
    recent = sorted_memories[:limit]

    return [
        RecentUpdateResponse(
            id=m.id,
            name=m.structured_data.get("name", ""),
            location=m.structured_data.get("location", ""),
            updated_at=m.updated_at
        )
        for m in recent
    ]


@router.get("/stats/tags")
def get_tag_stats(user_id: str, type: str = None, db: Session = Depends(get_db)):
    """
    获取标签聚类统计。
    从所有 Memory 的 attributes 字段聚合标签。
    """
    memories = memory_service.list_by_user(db, user_id, type_filter=type)
    if not memories:
        return {}

    tag_counts = {}

    for memory in memories:
        attributes = memory.structured_data.get("attributes") or []  # 处理 None 值
        for tag in attributes:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return tag_counts
