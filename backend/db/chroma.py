import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings

# Chroma 客户端（持久化）
_client = None


def get_chroma_client():
    """获取 Chroma 客户端单例。"""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    return _client


def get_memory_collection():
    """获取 memory collection。"""
    client = get_chroma_client()
    return client.get_or_create_collection(name="memories")
