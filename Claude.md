# 🧠 项目名称（暂定）
HomeRAG — AI 驱动的空间记忆增强系统

---

# 一、项目使命

HomeRAG 是一个 AI 原生的个人记忆增强实验项目。

目标不是做一个“物品管理系统”，
而是探索：

> 如何让 AI 作为“记忆结构引擎”，
> 将现实世界的碎片化语言，转化为可查询、可推理、可总结的语义知识库。

第一阶段（48小时）专注：
- 家庭空间物品记忆（item）

但系统必须从第一天设计为通用 Memory 引擎，
未来支持：
- 消费记录（奶茶 / 餐厅 / 甜品）
- 情绪记录
- 决策辅助
- 其他记忆类型

---

# 二、核心设计原则

1. AI 是核心逻辑，不是辅助功能
2. 禁止使用硬编码规则做分类
3. 所有意图识别必须走 LLM
4. 所有结构化抽取必须走 LLM
5. 所有回答必须由 LLM 生成
6. 系统必须可扩展为多类型 Memory

---

# 三、技术栈

前端：
- Vue3
- Chat-like 输入界面
- 结构化记忆可视化界面

后端：
- FastAPI

数据库：
- SQLite
- 必须包含 user_id 字段用于数据隔离

向量数据库：
- Chroma

模型：
- 通过 API 接入成熟 LLM（ChatGPT / DeepSeek / Claude）
- 模型层必须可替换

---

# 四、核心数据抽象（必须实现）

统一 Memory 数据模型：

Memory {
    id
    user_id
    raw_text
    type                // item / consumption / emotion / other
    structured_data     // JSON
    embedding
    created_at
    updated_at
}

第一阶段实现 type = item

未来扩展只增加 type，不改变核心结构。

---

# 五、AI 编排流程（Agent Flow）

## 1. 用户输入处理流程

Step 1：Intent Classifier Agent
- 判断：record 还是 query

Step 2A：如果是 record
    → Extraction Agent
    → 输出标准 JSON
    → 存储 structured_data
    → 生成 embedding
    → 存入 Chroma

Step 2B：如果是 query
    → embedding 搜索
    → 结构字段匹配
    → 汇总候选 memory
    → Answer Generator Agent 生成自然语言回复

---

# 六、Item 类型结构规范

Extraction Agent 必须输出稳定 JSON：

{
  "type": "item",
  "name": "",
  "location": "",
  "room": "",
  "attributes": []
}

必须保证 JSON 可解析。
禁止返回自然语言混杂 JSON。

---

# 七、更新判断机制（重要）

当用户输入类似：

“羽绒服现在在衣柜右边”

系统必须：

1. 检查是否已有同名物品
2. 如果存在：
   - 判断是更新而非新增
   - 更新 structured_data
   - 更新 embedding
3. 返回确认说明

---

# 八、可视化要求（必须实现）

系统不仅是聊天工具。

必须提供：

1. 结构化 Memory 表格视图
2. 房间分布统计
3. 最近更新记录
4. 标签聚类统计

可视化数据来源：
- structured_data
- LLM 总结

目标：
让用户看到“AI 整理后的记忆状态”。

---

# 九、Prompt 设计规范

所有 Prompt 必须：

- 明确输出格式
- 明确角色
- 明确禁止多余解释
- 输出 JSON 时不得包含 Markdown 包裹

Prompt 必须单独存放在：

/prompts 目录下

例如：

- classify.txt
- extract_item.txt
- detect_update.txt
- generate_answer.txt

---

# 十、可扩展策略

未来新增类型时：

1. 仅新增 Extraction Prompt
2. 不修改 Memory 主结构
3. 不修改数据库结构
4. 保持 Agent Flow 不变

---

# 十一、自动测试策略

必须包含：

1. Intent 分类单元测试
2. Extraction JSON 格式测试
3. 更新判断逻辑测试
4. API 接口测试

允许 Mock LLM 响应进行测试。

测试重点：
- JSON 是否稳定
- 数据是否正确更新
- embedding 是否正确生成

---

# 十二、开发节奏

48小时目标：

Day 1：
- 数据模型
- Intent 分类
- Item Extraction
- 存储流程

Day 2：
- 向量检索
- Query 生成回答
- 更新判断
- 基础可视化页面

一周内优化：
- 可视化增强
- 统计图表
- README 完善
- Demo 录屏

---

# 十三、Demo 演示路径（必须可复现）

1. 新增 3 个物品
2. 搜索物品
3. 模糊搜索
4. 更新物品位置
5. 查看可视化统计

---

# 十四、禁止事项

- 禁止写死关键词规则
- 禁止跳过 LLM 直接存储
- 禁止将系统做成普通 CRUD 项目

这是一个 AI 原生系统实验。
