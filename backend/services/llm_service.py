from abc import ABC, abstractmethod
from typing import Optional
import time
import logging

from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)


class BaseLLMService(ABC):
    """可插拔 LLM 接口抽象基类。"""

    @abstractmethod
    async def complete(self, prompt: str, system: Optional[str] = None) -> str:
        """发送 prompt，返回文本响应。"""
        pass

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """生成文本向量。"""
        pass


class DeepSeekLLMService(BaseLLMService):
    """DeepSeek 实现。"""

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            timeout=30.0,  # 30秒超时
            max_retries=2,  # 最多重试2次
        )
        self._model = settings.deepseek_model

    async def complete(self, prompt: str, system: Optional[str] = None) -> str:
        start_time = time.time()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
            )
            elapsed = time.time() - start_time
            logger.info(f"LLM API call took {elapsed:.2f}s")
            return response.choices[0].message.content
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"LLM API error after {elapsed:.2f}s: {e}")
            raise

    async def embed(self, text: str) -> list[float]:
        # DeepSeek 暂不支持 embedding，使用 OpenAI embedding 或返回空向量
        # 这里返回一个简单的占位向量
        return [0.0] * 1536


def get_llm_service() -> BaseLLMService:
    """工厂函数：根据配置返回对应 LLM 实现。"""
    provider = settings.llm_provider
    if provider == "deepseek":
        return DeepSeekLLMService()
    raise ValueError(f"Unsupported LLM provider: {provider}")
