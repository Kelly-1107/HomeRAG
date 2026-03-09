from sqlalchemy.orm import Session

from services.llm_service import BaseLLMService
from services.memory_service import MemoryService


class UpdateDetector:
    """更新 vs 新增判断 Agent。"""

    PROMPT_PATH = "prompts/detect_update.txt"

    def __init__(self, llm: BaseLLMService):
        self._llm = llm
        self._memory_service = MemoryService()

    def is_update(self, db: Session, user_id: str,
                  extracted_data: dict) -> bool:
        """
        判断是否为更新操作。

        1. 查找同名物品是否存在
        2. 如存在，调用 LLM 确认是否为更新
        """
        # 查找同名物品
        existing = self._memory_service.find_by_name(
            db, user_id, extracted_data.get("name")
        )

        if not existing:
            return False

        # 简化版：直接返回 True（因为找到同名物品即认为是更新）
        # TODO: 后续可接入 LLM 判断具体场景
        return True
