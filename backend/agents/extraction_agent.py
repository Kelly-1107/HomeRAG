import json
import logging
from typing import Optional

from services.llm_service import BaseLLMService


logger = logging.getLogger(__name__)


class ExtractionAgent:
    """结构化抽取 Agent（支持多类型）。"""

    # Prompt 文件映射
    PROMPT_PATHS = {
        "item": "prompts/extract_item.txt",
        "consumption": "prompts/extract_consumption.txt",
    }

    def __init__(self, llm: BaseLLMService):
        self._llm = llm
        # 缓存所有 prompt 模板（避免重复读取文件）
        self._prompt_templates = {}
        for memory_type, path in self.PROMPT_PATHS.items():
            with open(path, "r", encoding="utf-8") as f:
                self._prompt_templates[memory_type] = f.read()

    async def extract(self, memory_type: str, user_input: str) -> Optional[dict | list[dict]]:
        """
        从自然语言中抽取结构化 JSON。

        Args:
            memory_type: 记忆类型（item / consumption / emotion / other）
            user_input: 用户输入的自然语言

        返回格式：
        单个记录：
        {
            "name": "...",
            "location": "...",
            ...
        }

        多个记录：
        [
            {...},
            {...}
        ]

        注意：返回的 JSON 不包含 type 字段，type 由调用方管理。
        """
        # 获取缓存的 prompt 模板
        prompt_template = self._prompt_templates.get(memory_type)
        if not prompt_template:
            raise ValueError(f"Unsupported memory type: {memory_type}")

        # 替换占位符
        prompt = prompt_template.replace("{user_input}", user_input)

        # 调用 LLM
        response = await self._llm.complete(prompt)

        # 解析 JSON
        try:
            # 尝试提取 JSON（可能 LLM 返回了带 markdown 包裹的内容）
            content = response.strip()
            if content.startswith("```"):
                # 移除 markdown 代码块
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])

            logger.info(f"Parsing extraction response: {content[:200]}...")
            result = json.loads(content)

            # 移除 type 字段（如果 LLM 返回了）
            if isinstance(result, dict):
                result.pop("type", None)
                # 为 item 类型确保 quantity 字段存在
                if memory_type == "item" and "quantity" not in result:
                    result["quantity"] = 1
            elif isinstance(result, list):
                for item in result:
                    item.pop("type", None)
                    # 为 item 类型确保 quantity 字段存在
                    if memory_type == "item" and "quantity" not in item:
                        item["quantity"] = 1

            logger.info(f"Extraction successful: {result}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction response: {response}")
            logger.error(f"JSON decode error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in extraction: {str(e)}")
            logger.error(f"Response was: {response}")
            return None
