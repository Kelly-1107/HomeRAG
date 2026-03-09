from sqlalchemy.orm import Session

from models.memory import Memory
from services.memory_service import MemoryService
from services.embedding_service import get_embedding_service
from db.chroma import get_memory_collection


class SearchService:
    """基于 Chroma 向量相似度检索。"""

    def __init__(self):
        self._memory_service = MemoryService()
        self._embedding_service = get_embedding_service()
        self._collection = get_memory_collection()

    def search(self, db: Session, user_id: str,
               query_text: str, top_k: int = 5, embedding: list[float] | None = None) -> list[Memory]:
        """
        基于 Chroma 向量相似度搜索。

        Flow:
        1. 生成 query embedding（如果未提供）
        2. Chroma 相似度搜索（过滤 user_id）
        3. 从 SQLite 批量查询完整 Memory 对象

        Args:
            embedding: 可选的预生成 embedding，避免重复生成

        返回候选 Memory 列表。
        """
        # 1. 生成 query embedding（如果未提供）
        query_embedding = embedding if embedding is not None else self._embedding_service.embed(query_text)

        # 2. Chroma 相似度搜索
        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"user_id": user_id}  # 用户数据隔离
            )
        except Exception as e:
            # Chroma 查询失败，返回空列表
            print(f"Chroma query failed: {e}")
            return []

        # 3. 提取 memory_ids
        if not results['ids'] or not results['ids'][0]:
            return []

        memory_ids = [int(id_str) for id_str in results['ids'][0]]

        # 4. 从 SQLite 批量查询完整 Memory 对象（避免 N+1 查询）
        memories = db.query(Memory).filter(Memory.id.in_(memory_ids)).all()

        # 按照 memory_ids 的顺序排序（保持相似度排序）
        memory_dict = {m.id: m for m in memories}
        ordered_memories = [memory_dict[mid] for mid in memory_ids if mid in memory_dict]

        return ordered_memories

    async def upsert_vector(self, memory_id: int, text: str,
                      user_id: str, memory_type: str, embedding: list[float] | None = None) -> None:
        """
        向 Chroma 写入或更新向量。

        Args:
            embedding: 可选的预生成 embedding，避免重复生成
        """
        if embedding is not None:
            vector_embedding = embedding
        else:
            vector_embedding = await self._embedding_service.embed(text)

        self._collection.upsert(
            ids=[str(memory_id)],
            embeddings=[vector_embedding],
            metadatas=[{"user_id": user_id, "type": memory_type}],
            documents=[text]
        )

    def delete_vector(self, memory_id: int) -> None:
        """从 Chroma 删除向量。"""
        try:
            self._collection.delete(ids=[str(memory_id)])
        except Exception:
            pass  # 忽略不存在的 ID
