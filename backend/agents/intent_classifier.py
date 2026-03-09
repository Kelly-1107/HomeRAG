from enum import Enum
import logging

from services.llm_service import BaseLLMService

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    RECORD = "record"  # 记录物品
    QUERY = "query"   # 查询物品


class MemoryType(str, Enum):
    ITEM = "item"          # 物品记录
    CONSUMPTION = "consumption"  # 消费记录


class IntentClassifier:
    """意图分类 Agent。"""

    PROMPT_PATH = "prompts/classify.txt"
    TYPE_PROMPT_PATH = "prompts/classify_type.txt"

    def __init__(self, llm: BaseLLMService):
        self._llm = llm
        # 缓存 prompt 模板（避免重复读取文件）
        with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
            self._prompt_template = f.read()
        with open(self.TYPE_PROMPT_PATH, "r", encoding="utf-8") as f:
            self._type_prompt_template = f.read()

    async def classify(self, user_input: str) -> Intent:
        """
        判断用户意图：
        - record: 记录/更新物品
        - query: 查询物品
        """
        # 使用缓存的 prompt 模板
        prompt = self._prompt_template.replace("{user_input}", user_input)

        # 调用 LLM
        response = await self._llm.complete(prompt)
        response = response.strip().lower()

        # 解析返回结果
        if "query" in response:
            return Intent.QUERY
        else:
            return Intent.RECORD

    async def classify_type(self, user_input: str) -> MemoryType:
        """
        判断记忆类型：
        - item: 物品记录
        - consumption: 消费记录
        """
        prompt = self._type_prompt_template.replace("{user_input}", user_input)

        # 调用 LLM
        response = await self._llm.complete(prompt)
        response = response.strip().lower()

        # 解析返回结果
        if "consumption" in response:
            return MemoryType.CONSUMPTION
        else:
            return MemoryType.ITEM
