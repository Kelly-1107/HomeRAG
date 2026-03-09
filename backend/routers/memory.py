from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import traceback

from db.sqlite import get_db
from models.schemas import (
    ChatRequest,
    ChatResponse,
    MemoryCreateRequest,
    MemoryResponse,
    MemoryUpdateRequest,
    RecordRequest,
    MemoryListItem,
)
from agents.memory_agent import MemoryAgent, get_memory_agent
from services.memory_service import MemoryService

router = APIRouter()
logger = logging.getLogger(__name__)


class BatchDeleteRequest(BaseModel):
    memory_ids: list[int]


@router.post("/memory", response_model=ChatResponse)
async def record_memory(
    request: RecordRequest,
    db: Session = Depends(get_db),
    agent: MemoryAgent = Depends(get_memory_agent)
):
    """
    Record 流程端点：
    - 接收 user_id 和 message
    - 复用 MemoryAgent 的 record 逻辑
    - 返回确认消息
    """
    return await agent.process(db, request.user_id, request.message)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    agent: MemoryAgent = Depends(get_memory_agent)
):
    """
    处理用户聊天输入：
    - 意图分类 -> 记录或查询
    - 返回自然语言回复
    """
    try:
        logger.info(f"Processing chat request: user_id={request.user_id}, message={request.message}")
        result = await agent.process(db, request.user_id, request.message)
        logger.info(f"Chat request completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@router.get("/memories", response_model=list[MemoryListItem])
def list_memories(user_id: str, type: str = None, db: Session = Depends(get_db)):
    """列出用户所有记忆（用于前端可视化展示）"""
    memories = MemoryService().list_by_user(db, user_id, type_filter=type)
    result = []
    for memory in memories:
        result.append(MemoryListItem(
            id=memory.id,
            name=memory.structured_data.get("name", ""),
            quantity=memory.structured_data.get("quantity", 1),
            location=memory.structured_data.get("location", ""),
            room=memory.structured_data.get("room") or "",  # 处理 None 值
            attributes=memory.structured_data.get("attributes") or [],  # 处理 None 值
            raw_text=memory.raw_text,
            created_at=memory.created_at,
            updated_at=memory.updated_at,
        ))
    return result


@router.get("/memories/{memory_id}", response_model=MemoryResponse)
def get_memory(memory_id: int, db: Session = Depends(get_db)):
    """获取单条记忆详情。"""
    service = MemoryService()
    memory = service.get_by_id(db, memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.put("/memories/{memory_id}", response_model=MemoryListItem)
async def update_memory(memory_id: int, request: MemoryUpdateRequest, db: Session = Depends(get_db)):
    """更新记忆的结构化数据。"""
    service = MemoryService()
    memory = await service.update(db, memory_id, request.structured_data)
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryListItem(
        id=memory.id,
        name=memory.structured_data.get("name", ""),
        quantity=memory.structured_data.get("quantity", 1),
        location=memory.structured_data.get("location", ""),
        room=memory.structured_data.get("room") or "",  # 处理 None 值
        attributes=memory.structured_data.get("attributes") or [],  # 处理 None 值
        raw_text=memory.raw_text,
        created_at=memory.created_at,
        updated_at=memory.updated_at,
    )



@router.delete("/memories/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    """删除记忆。"""
    service = MemoryService()
    success = service.delete(db, memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted"}


@router.post("/memories/batch-delete")
def batch_delete_memories(request: BatchDeleteRequest, db: Session = Depends(get_db)):
    """批量删除记忆。"""
    service = MemoryService()
    result = service.delete_batch(db, request.memory_ids)
    return {
        "status": "completed",
        "deleted": result["deleted"],
        "not_found": result["not_found"]
    }
