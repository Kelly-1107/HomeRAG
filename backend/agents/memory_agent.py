from sqlalchemy.orm import Session
import json
import asyncio
import logging
import traceback

from services.llm_service import get_llm_service
from services.memory_service import MemoryService
from services.embedding_service import EmbeddingService
from services.search_service import SearchService
from agents.intent_classifier import IntentClassifier, Intent
from agents.extraction_agent import ExtractionAgent
from agents.answer_generator import AnswerGenerator
from models.schemas import ChatResponse


logger = logging.getLogger(__name__)


# 单例实例
_agent_instance = None


def get_memory_agent() -> "MemoryAgent":
    """获取 MemoryAgent 单例实例（避免重复初始化）。"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = MemoryAgent()
    return _agent_instance


class MemoryAgent:
    """总编排入口：串联全部 AI Flow。"""

    def __init__(self):
        self._llm = get_llm_service()
        self._memory_service = MemoryService()
        self._embedding_service = EmbeddingService(self._llm)
        self._search_service = SearchService()

        # 初始化各个 Agent
        self._intent_classifier = IntentClassifier(self._llm)
        self._extraction_agent = ExtractionAgent(self._llm)
        self._answer_generator = AnswerGenerator(self._llm)

    async def process(self, db: Session, user_id: str, user_input: str) -> ChatResponse:
        """
        主入口：处理用户输入，返回回复。

        Flow:
        1. intent_classifier -> 判断意图
        2A. record: extraction_agent -> memory_service (create/update)
        2B. query: search_service -> answer_generator
        """
        # Step 1: 意图分类和 embedding 生成并行执行
        intent_task = asyncio.create_task(self._intent_classifier.classify(user_input))
        embedding_task = asyncio.create_task(self._embedding_service.generate(user_input))

        intent, embedding = await asyncio.gather(intent_task, embedding_task)

        if intent == Intent.RECORD:
            # Step 2A: 记录流程
            return await self._handle_record(db, user_id, user_input, embedding)
        else:
            # Step 2B: 查询流程
            return await self._handle_query(db, user_id, user_input, embedding)

    async def _handle_record(self, db: Session, user_id: str,
                       user_input: str, embedding: list[float]) -> ChatResponse:
        """处理记录/更新操作。"""
        # 自动识别 memory_type
        memory_type = await self._intent_classifier.classify_type(user_input)
        logger.info(f"Classified memory type: {memory_type}")

        # 2A-1: 结构化抽取
        extracted = await self._extraction_agent.extract(memory_type, user_input)

        # 检查抽取是否成功
        if extracted is None:
            logger.error(f"Extraction failed for input: {user_input}")
            return ChatResponse(
                reply="抱歉，我无法理解您的输入。请尝试更清晰地描述物品信息。",
                memory_id=None
            )

        # 检查提取结果是否信息量不足（可能是查询而非记录）
        if self._is_insufficient_info(extracted, memory_type):
            # 信息量不足，检查name是否已存在（不依赖向量搜索）
            name = extracted.get("name", "").strip()
            if name:
                # 直接查询数据库，检查是否有同名记录
                existing = self._memory_service.find_by_name(db, user_id, name, memory_type)
                if existing:
                    logger.info(f"Input has insufficient info, found existing record for '{name}', switching to query")
                    return await self._handle_query(db, user_id, user_input, embedding)

            # 如果没有候选记录，继续作为 record 处理（新增）

        # 处理多个物品的情况
        if isinstance(extracted, list):
            # 批量创建多个物品
            created_names = []
            for item_data in extracted:
                name = item_data.get("name")
                # 为每个物品生成独立的 embedding
                item_text = f"{name} {item_data.get('location', '')} {item_data.get('room', '')}"
                item_embedding = await self._embedding_service.generate(item_text)

                memory = self._memory_service.create(
                    db=db,
                    user_id=user_id,
                    raw_text=user_input,
                    memory_type=memory_type,
                    structured_data=item_data,
                    embedding=item_embedding,
                )

                # 写入 Chroma（复用 embedding）
                await self._search_service.upsert_vector(
                    memory_id=memory.id,
                    text=user_input,
                    user_id=user_id,
                    memory_type=memory.type,
                    embedding=item_embedding
                )

                created_names.append(f"{name}（{item_data.get('quantity', 1)}件）")

            reply = f"已记录：{', '.join(created_names)}"
            return ChatResponse(reply=reply, memory_id=None)

        # 单个物品的情况
        name = extracted.get("name")
        quantity = extracted.get("quantity", 1)

        # 使用传入的 embedding 进行向量相似度搜索
        candidates = self._search_service.search(db, user_id, user_input, top_k=3, embedding=embedding)

        # 判断是否为更新操作
        existing = None
        if candidates:
            # 使用 LLM 判断是否为同一物品的更新
            logger.info(f"Checking if update for {len(candidates)} candidates")
            try:
                is_update, target_id = await self._check_if_update(user_input, candidates, extracted, memory_type)
                logger.info(f"Update check result: is_update={is_update}, target_id={target_id}")
                if is_update and target_id:
                    existing = self._memory_service.get_by_id(db, target_id)
                    logger.info(f"Found existing memory: id={existing.id if existing else None}")
            except Exception as e:
                logger.error(f"Error in _check_if_update: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

        if existing:
            # 更新现有记录
            logger.info(f"Updating existing memory: id={existing.id}")
            try:
                await self._memory_service.update(db, existing.id, extracted, raw_text=user_input)
                logger.info(f"Memory service update completed")

                # 更新 Chroma（复用 embedding）
                await self._search_service.upsert_vector(
                    memory_id=existing.id,
                    text=user_input,
                    user_id=user_id,
                    memory_type=existing.type,
                    embedding=embedding
                )
                logger.info(f"Vector upsert completed")
            except Exception as e:
                logger.error(f"Error updating memory: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

            reply = f"已更新「{name}」的信息"
            if quantity > 1:
                reply += f"（数量：{quantity}件）"
            memory_id = existing.id
        else:
            # 新增记录
            memory = self._memory_service.create(
                db=db,
                user_id=user_id,
                raw_text=user_input,
                memory_type=memory_type,
                structured_data=extracted,
                embedding=embedding,
            )

            # 写入 Chroma（复用 embedding）
            await self._search_service.upsert_vector(
                memory_id=memory.id,
                text=user_input,
                user_id=user_id,
                memory_type=memory.type,
                embedding=embedding
            )

            reply = f"已记录「{name}」"
            if quantity > 1:
                reply += f"（数量：{quantity}件）"
            memory_id = memory.id

        return ChatResponse(reply=reply, memory_id=memory_id)

    def _is_insufficient_info(self, extracted: dict, memory_type: str) -> bool:
        """判断提取结果是否信息量不足（可能是查询而非记录）。

        当信息量不足且存在候选记录时，应该转向 query 流程。
        只检查用户明确提供的信息，不依赖从名称猜测的信息。
        """
        name = extracted.get("name", "").strip()
        if not name:
            return True

        if memory_type == "consumption":
            # consumption: 只检查用户明确提供的信息（location/price/rating/attributes）
            # 不检查 category，因为它可能是从 name 猜测的
            return not any([
                extracted.get("location"),
                extracted.get("price", 0) > 0,
                extracted.get("rating"),
                extracted.get("attributes", [])
            ])
        else:
            # item: location/room/attributes 至少有一个非空
            return not any([
                extracted.get("location"),
                extracted.get("room"),
                extracted.get("attributes", [])
            ])

    async def _check_if_update(self, user_input: str, candidates: list, extracted: dict, memory_type: str = "item") -> tuple[bool, int | None]:
        """
        使用 LLM 判断用户输入是否为更新操作。

        Args:
            user_input: 用户输入
            candidates: 候选记录列表
            extracted: 抽取的结构化数据
            memory_type: 记忆类型 (item 或 consumption)

        返回: (是否更新, 目标记录ID)
        """
        if not candidates:
            return False, None

        # 根据 memory_type 构建候选信息
        extracted_name = extracted.get("name")

        candidates_text = []
        for c in candidates:
            if memory_type == "consumption":
                # consumption 类型使用 category 和 location
                text = f"ID:{c.id} | 名称:{c.structured_data.get('name')} | 类别:{c.structured_data.get('category', '')} | 地点:{c.structured_data.get('location', '')}"
            else:
                # item 类型使用 attributes
                text = f"ID:{c.id} | 名称:{c.structured_data.get('name')} | 属性:{','.join(c.structured_data.get('attributes', []))}"
            candidates_text.append(text)
        candidates_summary = "\n".join(candidates_text)

        # 根据不同类型使用不同的判断逻辑
        if memory_type == "consumption":
            prompt = f"""判断用户是在更新已有消费记录还是记录新消费。

用户输入：{user_input}
提取的消费：名称={extracted_name}, 类别={extracted.get('category', '')}, 地点={extracted.get('location', '')}, 价格={extracted.get('price', 0)}

已有记录：
{candidates_summary}

判断规则：
1. 更新条件：名称完全一致 且 类别相同 且 地点相同（或地点都为空）
2. 新增条件：名称不同 或 类别不同 或 地点不同
3. 如有多条匹配，选择ID最大的

输出 JSON（不要包含其他文字）：
{{
  "is_update": true/false,
  "target_id": 记录ID或null,
  "reason": "判断理由"
}}"""
        else:
            extracted_attributes = extracted.get("attributes", [])
            prompt = f"""判断用户是在更新已有物品还是记录新物品。

用户输入：{user_input}
提取的物品：名称={extracted_name}, 属性={extracted_attributes}

已有记录：
{candidates_summary}

判断规则：
1. 更新条件：名称完全一致 且 所有属性完全一致
2. 新增条件：名称不同 或 属性不同
3. 如有多条匹配，选择ID最大的

输出 JSON（不要包含其他文字）：
{{
  "is_update": true/false,
  "target_id": 记录ID或null,
  "reason": "判断理由"
}}"""

        response = await self._llm.complete(prompt)

        try:
            # 尝试清理可能的 markdown 包裹
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            logger.info(f"LLM response for update check: {cleaned_response}")
            result = json.loads(cleaned_response)
            return result.get("is_update", False), result.get("target_id")
        except json.JSONDecodeError as e:
            # 解析失败，记录错误并默认为新增
            logger.error(f"Failed to parse update check response: {response}")
            logger.error(f"JSON decode error: {str(e)}")
            return False, None
        except Exception as e:
            logger.error(f"Unexpected error in update check: {str(e)}")
            logger.error(f"Response was: {response}")
            return False, None

    async def _handle_query(self, db: Session, user_id: str,
                      user_input: str, embedding: list[float]) -> ChatResponse:
        """处理查询操作。"""
        # 2B-1: 使用传入的 embedding 进行向量检索（增加 top_k 以获取更多候选）
        candidates = self._search_service.search(db, user_id, user_input, top_k=10, embedding=embedding)
        logger.info(f"Query search returned {len(candidates)} candidates")
        if candidates:
            candidate_names = [c.structured_data.get('name', 'unknown') for c in candidates]
            logger.info(f"Candidate names: {candidate_names}")

        # 2B-2: 生成回答
        reply = await self._answer_generator.generate(user_input, candidates)

        return ChatResponse(reply=reply, memory_id=None)
