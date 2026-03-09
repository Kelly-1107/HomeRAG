from abc import ABC, abstractmethod
import time
import logging
import hashlib
from collections import OrderedDict

from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)


class LRUCache:
    """简单的 LRU 缓存实现。"""

    def __init__(self, capacity: int = 1000):
        self._cache = OrderedDict()
        self._capacity = capacity

    def get(self, key: str):
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._capacity:
            self._cache.popitem(last=False)


class BaseEmbeddingService(ABC):
    """可插拔 Embedding 接口抽象基类。"""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """将文本转换为向量。"""
        pass

    @abstractmethod
    def get_dimensions(self) -> int:
        """返回向量维度。"""
        pass


class OpenAIEmbeddingService(BaseEmbeddingService):
    """OpenAI Embedding 实现（支持中转商）。"""

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.openai_embedding_api_key,
            base_url=settings.openai_embedding_base_url,
            timeout=15.0,  # 15秒超时
            max_retries=2,  # 最多重试2次
        )
        self._model = settings.openai_embedding_model
        self._dimensions = settings.openai_embedding_dimensions
        self._cache = LRUCache(capacity=1000)

    async def embed(self, text: str) -> list[float]:
        """生成文本向量（带缓存）。"""
        # 检查缓存
        cache_key = hashlib.md5(text.encode()).hexdigest()
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.info(f"Embedding cache hit: {text[:50]}")
            return cached

        # 生成 embedding
        start_time = time.time()
        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=text,
            )
            elapsed = time.time() - start_time
            logger.info(f"Embedding API call took {elapsed:.2f}s")

            embedding = response.data[0].embedding

            # 写入缓存
            self._cache.put(cache_key, embedding)

            return embedding
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Embedding API error after {elapsed:.2f}s: {e}")
            raise

    def get_dimensions(self) -> int:
        return self._dimensions


class DeepSeekEmbeddingService(BaseEmbeddingService):
    """DeepSeek Embedding 占位实现（不推荐生产使用）。"""

    async def embed(self, text: str) -> list[float]:
        """返回占位向量。"""
        return [0.0] * 1024

    def get_dimensions(self) -> int:
        return 1024


def get_embedding_service() -> BaseEmbeddingService:
    """工厂函数：根据配置返回对应 Embedding 实现。"""
    provider = settings.embedding_provider
    if provider == "openai":
        return OpenAIEmbeddingService()
    elif provider == "deepseek":
        return DeepSeekEmbeddingService()
    raise ValueError(f"Unsupported embedding provider: {provider}")


# 兼容旧代码的简单封装
class EmbeddingService:
    """文本向量化服务（兼容层）。"""

    def __init__(self, llm=None):
        # 忽略 llm 参数，使用新的 embedding service
        self._service = get_embedding_service()

    async def generate(self, text: str) -> list[float]:
        """将文本转换为向量。"""
        return await self._service.embed(text)
