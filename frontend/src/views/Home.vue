<template>
  <!-- 主容器：响应式布局 -->
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-gray-900 dark:to-gray-800 p-4 md:p-6">
    <!-- 顶部标题 -->
    <header class="text-center mb-6 md:mb-8">
      <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
        HomeRAG
      </h1>
      <p class="text-sm md:text-base text-gray-600 dark:text-gray-400">
        AI 驱动的空间记忆增强系统
      </p>
    </header>

    <!-- 主内容区：桌面端左右布局，移动端上下布局 -->
    <main class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
      <!-- 左侧：对话区 -->
      <section class="flex flex-col bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden h-[600px] lg:h-[calc(100vh-200px)]">
        <!-- 对话标题 -->
        <div class="px-5 py-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          <h2 class="text-lg font-semibold text-gray-800 dark:text-gray-100">对话</h2>
        </div>

        <!-- 消息列表 -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="flex"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[85%] px-4 py-2.5 rounded-2xl transition-all duration-200 markdown-content"
              :class="msg.role === 'user'
                ? 'bg-indigo-600 text-white rounded-br-sm'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-100 rounded-bl-sm'"
              v-html="renderMarkdown(msg.content)"
            >
            </div>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
          <ChatInput @send="handleSend" />
        </div>
      </section>

      <!-- 右侧：记忆信息区 - 固定高度，内部滚动 -->
      <section class="flex flex-col bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden h-[600px] lg:h-[calc(100vh-200px)]">
        <!-- Tab 切换栏 -->
        <div class="flex border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          <button
            @click="switchType('item')"
            class="flex-1 px-4 py-3 text-sm font-medium transition-colors duration-200"
            :class="store.currentType === 'item'
              ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
          >
            物品
          </button>
          <button
            @click="switchType('consumption')"
            class="flex-1 px-4 py-3 text-sm font-medium transition-colors duration-200"
            :class="store.currentType === 'consumption'
              ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
          >
            消费
          </button>
        </div>

        <!-- 内部滚动容器 -->
        <div class="flex-1 overflow-y-auto relative">
          <!-- 加载遮罩 -->
          <div
            v-if="store.loading"
            class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 flex items-center justify-center z-10"
          >
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
          <div class="flex flex-col gap-px bg-gray-200 dark:bg-gray-700">
            <!-- 记忆列表 -->
            <div class="bg-white dark:bg-gray-800">
              <MemoryTable
                :memories="store.memories"
                @delete="store.deleteItem"
                @delete-batch="store.deleteItems"
                @update="store.updateItem"
              />
            </div>

            <!-- 统计信息网格 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-px bg-gray-200 dark:bg-gray-700 items-stretch">
              <!-- 房间分布 -->
              <div class="bg-white dark:bg-gray-800 h-full">
                <RoomStats :stats="store.roomStats" :type="store.currentType" />
              </div>

              <!-- 最近更新 -->
              <div class="bg-white dark:bg-gray-800 h-full">
                <RecentUpdates :updates="store.recentUpdates" />
              </div>
            </div>

            <!-- 标签聚类 -->
            <div class="bg-white dark:bg-gray-800">
              <TagCloud :tags="store.tagStats" />
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marked } from 'marked'
import { useMemoryStore } from '../stores/memory.js'
import ChatInput from '../components/ChatInput.vue'
import MemoryTable from '../components/MemoryTable.vue'
import RoomStats from '../components/RoomStats.vue'
import RecentUpdates from '../components/RecentUpdates.vue'
import TagCloud from '../components/TagCloud.vue'

// 配置 marked
marked.setOptions({
  breaks: true, // 支持换行
  gfm: true // 支持 GitHub Flavored Markdown
})

// Markdown 渲染函数
const renderMarkdown = (content) => {
  return marked.parse(content)
}

const store = useMemoryStore()
const messages = ref([
  { role: 'assistant', content: '你好！我是 HomeRAG，可以帮你记录和查找物品位置。' }
])

onMounted(() => {
  store.loadAllStats()
})

const switchType = async (type) => {
  store.currentType = type
  await store.loadAllStats()
}

const handleSend = async (content) => {
  messages.value.push({ role: 'user', content })

  try {
    const reply = await store.sendMessage(content)
    messages.value.push({ role: 'assistant', content: reply.reply })
  } catch (err) {
    console.error('发送消息失败:', err)
    console.error('错误详情:', err.response?.data || err.message)
    const errorMsg = err.response?.data?.detail || err.message || '未知错误'
    messages.value.push({ role: 'assistant', content: `抱歉，出错了：${errorMsg}` })
  }
}
</script>

<style scoped>
/* 自定义滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}
.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 暗色模式滚动条 */
.dark .overflow-y-auto::-webkit-scrollbar-thumb {
  background: #475569;
}
.dark .overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* Markdown 内容样式 */
.markdown-content :deep(p) {
  margin: 0;
  line-height: 1.6;
}

.markdown-content :deep(strong) {
  font-weight: 700;
}

.markdown-content :deep(em) {
  font-style: italic;
}

.markdown-content :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background: rgba(0, 0, 0, 0.1);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 4px 0;
}

.markdown-content :deep(a) {
  text-decoration: underline;
  opacity: 0.9;
}

.markdown-content :deep(a:hover) {
  opacity: 1;
}
</style>
