from datetime import datetime
import json
from sqlalchemy.orm import Session
from typing import Optional

from models.memory import Memory
from services.embedding_service import get_embedding_service
from db.chroma import get_memory_collection


class MemoryService:
    """Memory 纯数据操作层（不含 AI 逻辑）。"""

    def __init__(self):
        self._embedding_service = get_embedding_service()
        self._collection = get_memory_collection()

    def create(self, db: Session, user_id: str, raw_text: str,
               memory_type: str, structured_data: dict,
               embedding: Optional[list[float]] = None) -> Memory:
        """新增 Memory 记录。"""
        # 序列化 embedding 为 JSON 字符串
        embedding_str = json.dumps(embedding) if embedding else None

        memory = Memory(
            user_id=user_id,
            raw_text=raw_text,
            type=memory_type,
            structured_data=structured_data,
            embedding=embedding_str,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(memory)
        db.commit()
        db.refresh(memory)

        return memory

    async def update(self, db: Session, memory_id: int,
               structured_data: dict, raw_text: Optional[str] = None) -> Optional[Memory]:
        """更新 Memory 的结构化数据。"""
        memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if not memory:
            return None

        memory.structured_data = structured_data
        if raw_text:
            memory.raw_text = raw_text

            # 重新生成 embedding 并更新 Chroma
            embedding = await self._embedding_service.embed(raw_text)
            memory.embedding = json.dumps(embedding)

            self._collection.upsert(
                ids=[str(memory_id)],
                embeddings=[embedding],
                metadatas=[{"user_id": memory.user_id, "type": memory.type}],
                documents=[raw_text]
            )

        memory.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(memory)
        return memory

    def delete(self, db: Session, memory_id: int) -> bool:
        """删除 Memory 记录。"""
        memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if not memory:
            return False

        # 同步删除 Chroma
        try:
            self._collection.delete(ids=[str(memory_id)])
        except Exception:
            pass

        db.delete(memory)
        db.commit()
        return True

    def delete_batch(self, db: Session, memory_ids: list[int]) -> dict:
        """批量删除 Memory 记录。

        Returns:
            dict: {"deleted": int, "not_found": int}
        """
        deleted_count = 0
        not_found_count = 0
        deleted_ids = []  # 记录成功删除的 ID

        for memory_id in memory_ids:
            memory = db.query(Memory).filter(Memory.id == memory_id).first()
            if memory:
                db.delete(memory)
                deleted_count += 1
                deleted_ids.append(str(memory_id))
            else:
                not_found_count += 1

        db.commit()

        # 批量删除 Chroma
        if deleted_ids:
            try:
                self._collection.delete(ids=deleted_ids)
            except Exception:
                pass

        return {"deleted": deleted_count, "not_found": not_found_count}

    def get_by_id(self, db: Session, memory_id: int) -> Optional[Memory]:
        """按 ID 查询。"""
        return db.query(Memory).filter(Memory.id == memory_id).first()

    def list_by_user(self, db: Session, user_id: str, type_filter: str = None) -> list[Memory]:
        """查询用户所有 Memory。"""
        query = db.query(Memory).filter(Memory.user_id == user_id)
        if type_filter:
            query = query.filter(Memory.type == type_filter)
        return query.all()

    def find_by_name(self, db: Session, user_id: str, name: str, memory_type: str = None) -> list:
        """根据name模糊搜索用户的记忆记录。

        Args:
            db: 数据库会话
            user_id: 用户ID
            name: 物品名称（支持模糊匹配）
            memory_type: 可选的记忆类型过滤

        Returns:
            匹配的 Memory 记录列表
        """
        query = db.query(Memory).filter(Memory.user_id == user_id)
        if memory_type:
            query = query.filter(Memory.type == memory_type)

        # 模糊匹配 name（不区分大小写）
        name_lower = name.lower()
        memories = query.all()
        matches = []
        for memory in memories:
            stored_name = memory.structured_data.get("name", "")
            if stored_name.lower() == name_lower or name_lower in stored_name.lower():
                matches.append(memory)

        return matches

    def get_latest_memory(self, db: Session, user_id: str) -> Optional[Memory]:
        """获取最近更新的记忆。"""
        return db.query(Memory).filter(Memory.user_id == user_id).order_by(Memory.updated_at.desc()).first()
