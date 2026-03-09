#!/usr/bin/env python3
"""
数据迁移脚本：将现有 SQLite 数据的向量写入 Chroma

使用方法：
    cd backend
    python ../scripts/migrate_to_chroma.py
"""

import sys
import os

# 添加 backend 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from db.sqlite import get_db
from db.chroma import get_memory_collection
from services.embedding_service import get_embedding_service
from models.memory import Memory


def migrate():
    """迁移历史数据到 Chroma。"""
    print("开始迁移数据到 Chroma...")

    # 初始化服务
    embedding_service = get_embedding_service()
    collection = get_memory_collection()
    db = next(get_db())

    # 查询所有记录
    memories = db.query(Memory).all()
    total = len(memories)

    if total == 0:
        print("没有需要迁移的数据")
        return

    print(f"找到 {total} 条记录，开始迁移...")

    success_count = 0
    error_count = 0

    for i, memory in enumerate(memories, 1):
        try:
            # 生成 embedding
            text = memory.raw_text
            embedding = embedding_service.embed(text)

            # 写入 Chroma
            collection.upsert(
                ids=[str(memory.id)],
                embeddings=[embedding],
                metadatas=[{"user_id": memory.user_id, "type": memory.type}],
                documents=[text]
            )

            success_count += 1
            print(f"[{i}/{total}] 成功迁移 ID={memory.id}: {memory.structured_data.get('name', 'N/A')}")

        except Exception as e:
            error_count += 1
            print(f"[{i}/{total}] 迁移失败 ID={memory.id}: {e}")

    print(f"\n迁移完成！")
    print(f"成功: {success_count} 条")
    print(f"失败: {error_count} 条")


if __name__ == "__main__":
    migrate()
