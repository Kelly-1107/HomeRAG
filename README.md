# HomeRAG

## AI 驱动的空间记忆增强系统

> 一个基于 Agent Flow 的有状态记忆系统。
> 支持「记录 / 查询 / 更新」完整闭环的 AI 原生应用。

---

## 项目背景

大多数 LLM Demo 是"无状态对话"。

但真实的 C 端 AI 产品，必须具备：

- 持久记忆
- 状态更新能力
- 可解释的行为逻辑
- 可扩展的架构设计

HomeRAG 是一个围绕"状态管理"构建的 AI Memory System。

用户可以用自然语言：

- 记录物品位置
- 更新物品位置
- 查询物品在哪里
- 记录消费体验

系统通过 Agent Flow 进行意图识别、信息抽取、状态管理与回答生成，形成完整闭环。

---

## 核心特性

### 1. 多种记忆类型支持

- **物品记忆 (item)**: 记录家庭物品的位置信息
- **消费记忆 (consumption)**: 记录奶茶、餐厅、甜品等消费体验
- 支持通过 LLM 自动分类记忆类型

### 2. 智能意图识别

- 自动判断用户意图：记录还是查询
- 自动检测更新操作而非重复记录
- 支持批量物品记录

### 3. 向量检索

- 基于 Chroma 的语义向量检索
- 支持模糊查询和语义匹配
- 1024 维 embedding (BGE-large-zh-v1.5)

### 4. 高性能优化

- 异步化和并行化 API 调用
- Embedding LRU 缓存
- 超时和重试机制
- 性能监控中间件

---

## 功能演示

### 1. 记录物品

```
我的黑色羽绒服在卧室衣柜右边
```

→ 已记录「黑色羽绒服」

---

### 2. 更新位置

```
我的黑色羽绒服现在在书房柜子里
```

→ 自动识别为更新操作，更新已有记录

---

### 3. 查询位置

```
黑色羽绒服在哪？
```

→ 黑色羽绒服在书房柜子里。

---

### 4. 记录消费

```
今天喝了杯奈雪的霸气橙子，25元，在万达店
```

→ 已记录「霸气橙子」

---

## 系统架构

```
User Input
    ↓
Intent Classifier Agent
    ↓
┌─────────────────────────────┐
│      Memory Agent           │
│  ┌─────────────────────┐   │
│  │ Type Classifier     │   │  ← 自动识别记忆类型
│  └─────────────────────┘   │
│  ┌─────────────────────┐   │
│  │ Extraction Agent    │   │  ← 结构化数据抽取
│  └─────────────────────┘   │
│  ┌─────────────────────┐   │
│  │ Update Detector     │   │  ← LLM 判断更新
│  └─────────────────────┘   │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│     Storage Layer           │
│  ┌───────────┐ ┌─────────┐  │
│  │  SQLite   │ │ Chroma  │  │
│  │ (结构化)  │ │ (向量)  │  │
│  └───────────┘ └─────────┘  │
└─────────────────────────────┘
    ↓
Answer Generator Agent
    ↓
Response
```

### 设计思想

- Agent 解耦职责
- Prompt 模板化管理
- LLM 只负责「理解与生成」
- 结构化数据由系统管理
- 数据持久化由数据库保证

---

## 技术栈

### Frontend

- Vue 3
- Vite
- Pinia
- Vue Router
- Axios

### Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- asyncio

### Database

- SQLite（结构化记忆存储）
- Chroma（向量语义检索）

### LLM

- DeepSeek (deepseek-chat)
- OpenAI 兼容接口（SiliconFlow）

### Embedding

- BGE-large-zh-v1.5 (1024 维)
- 通过 SiliconFlow API 调用

---

## 项目结构

```
HomeRAG/
├── backend/
│   ├── agents/              # AI Agent 模块
│   │   ├── intent_classifier.py
│   │   ├── extraction_agent.py
│   │   ├── answer_generator.py
│   │   └── memory_agent.py
│   ├── db/                  # 数据库模块
│   │   ├── sqlite.py
│   │   └── chroma.py
│   ├── models/              # 数据模型
│   │   ├── memory.py
│   │   └── schemas.py
│   ├── routers/             # API 路由
│   │   ├── memory.py
│   │   └── stats.py
│   ├── services/            # 服务层
│   │   ├── llm_service.py
│   │   ├── embedding_service.py
│   │   ├── memory_service.py
│   │   └── search_service.py
│   ├── prompts/             # Prompt 模板
│   │   ├── classify.txt
│   │   ├── classify_type.txt
│   │   ├── extract_item.txt
│   │   ├── extract_consumption.txt
│   │   └── generate_answer.txt
│   ├── tests/               # 单元测试
│   ├── config.py
│   └── main.py
├── frontend/
│   └── src/
│       ├── views/
│       │   ├── Home.vue         # 聊天界面
│       │   └── MemoryStatus.vue # 记忆可视化
│       ├── components/
│       ├── stores/
│       ├── router/
│       └── api/
├── scripts/
└── README.md
```

---

## API 接口

### 聊天接口

```bash
POST /api/chat
{
  "user_id": "user_001",
  "message": "我的黑色羽绒服在哪？"
}
```

### 记忆管理

```bash
GET  /api/memories?user_id=user_001
GET  /api/memories/{id}
PUT  /api/memories/{id}
DELETE /api/memories/{id}
POST /api/memories/batch-delete
```

### 统计接口

```bash
GET /api/stats?user_id=user_001
GET /api/stats/rooms?user_id=user_001
GET /api/stats/recent?user_id=user_001
GET /api/stats/tags?user_id=user_001
```

---

## 快速开始

### 1. 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 2. 配置环境变量

创建 `backend/.env` 文件：

```env
# LLM 配置
DEEPSEEK_API_KEY=your_api_key

# Embedding 配置
OPENAI_EMBEDDING_API_KEY=your_api_key

# 可选配置
DEFAULT_USER_ID=user_001
```

### 3. 启动服务

```bash
# 启动后端
cd backend
uvicorn main:app --reload --port 8000

# 启动前端
cd frontend
npm run dev
```

### 4. 访问系统

- 前端: http://localhost:5173
- API 文档: http://localhost:8000/docs

---

## 测试

```bash
cd backend
pytest tests/ -v
```

---

## 性能优化

当前版本已实现以下优化：

| 优化项 | 效果 |
|--------|------|
| 异步化 + 并行化 | 响应时间降低 40-60% |
| Embedding LRU 缓存 | 重复查询节省 2-3s |
| 提示词优化 | 减少 LLM 处理时间 |
| 超时 + 重试 | 避免无限等待 |
| 性能监控中间件 | 精确定位瓶颈 |

---

## 未来扩展方向

- 多用户记忆隔离
- WebSocket 实时交互
- Memory 时间维度版本管理
- 更多记忆类型（情绪记录、决策辅助）
- 标签智能聚类

---

## License

MIT

---

# English Summary

HomeRAG is an AI-powered spatial memory augmentation system built with an agent-based architecture.

Unlike stateless chat demos, it supports:

- Natural language memory recording (items, consumption)
- Intelligent update detection
- Persistent storage with SQLite + Chroma vector search
- Structured state management
- Multiple memory types with automatic classification

The system demonstrates how LLMs can be integrated into real product-oriented architectures:

- **Agent-based Flow**: Intent classification → Extraction → Update detection → Answer generation
- **Async & Parallel**: API calls are parallelized for 40-60% performance improvement
- **Vector Search**: Semantic retrieval using BGE-large-zh-v1.5 embeddings
- **Extensible Design**: Support for multiple memory types (item, consumption, and more)

Built with Vue 3 + FastAPI + SQLite + Chroma, designed for easy extension to other memory types like emotions and decision records.
