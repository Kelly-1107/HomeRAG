import json
import logging
from typing import Optional

from services.llm_service import BaseLLMService
from models.memory import Memory


logger = logging.getLogger(__name__)


class AnswerGenerator:
    """自然语言回答生成 Agent。"""

    PROMPT_PATH = "prompts/generate_answer.txt"

    def __init__(self, llm: BaseLLMService):
        self._llm = llm
        # 缓存 prompt 模板（避免重复读取文件）
        with open(self.PROMPT_PATH, "r", encoding="utf-8") as f:
            self._prompt_template = f.read()

    async def generate(self, query: str, candidates: list[Memory]) -> str:
        """
        根据检索结果生成自然语言回答。
        """
        # 如果没有找到相关记忆
        if not candidates:
            logger.info(f"No candidates found for query: {query}")
            return "我没有找到相关的物品记录。你可以先告诉我物品的位置。"

        logger.info(f"Generating answer for query: {query} with {len(candidates)} candidates")

        # 将 candidates 转换为上下文
        candidates_text = []
        for memory in candidates:
            data = memory.structured_data
            quantity = data.get('quantity', 1)
            info = f"物品：{data.get('name', '未知')}，数量：{quantity}，位置：{data.get('location', '未知')}，房间：{data.get('room', '未知')}"
            if data.get('attributes'):
                info += f"，属性：{', '.join(data.get('attributes', []))}"
            candidates_text.append(info)

        context = "\n".join(candidates_text)
        logger.info(f"Context for LLM:\n{context}")

        # 使用缓存的 prompt 模板
        prompt = self._prompt_template.replace("{query}", query)
        prompt = prompt.replace("{candidates}", context)

        # 调用 LLM 生成回答
        response = await self._llm.complete(prompt)
        logger.info(f"Generated answer: {response[:100]}...")

        return response.strip()
