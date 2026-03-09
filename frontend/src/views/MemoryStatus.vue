<template>
  <div class="memory-status">
    <header class="header">
      <h1>Memory Status</h1>
      <p>AI 整理后的记忆状态</p>
    </header>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-label">总记忆数</div>
        <div class="stat-value">{{ stats.total_memories || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">最近记录</div>
        <div class="stat-value">{{ stats.latest_memory_name || '-' }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">最后更新</div>
        <div class="stat-value">{{ formatTime(stats.last_updated_at) }}</div>
      </div>
    </div>

    <div class="memories-section">
      <h2>所有记忆</h2>
      <div class="memory-grid">
        <div v-for="memory in memories" :key="memory.id" class="memory-card">
          <div class="memory-name">{{ memory.name }}</div>
          <div class="memory-location">📍 {{ memory.location }}</div>
          <div class="memory-meta">
            <span class="memory-time">{{ formatTime(memory.updated_at) }}</span>
          </div>
        </div>
        <div v-if="memories.length === 0" class="empty-state">
          暂无记忆
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStats, listMemories } from '../api/memory.js'

const stats = ref({})
const memories = ref([])
const userId = 'user_001'

const loadData = async () => {
  try {
    const [statsRes, memoriesRes] = await Promise.all([
      getStats(userId),
      listMemories(userId)
    ])
    stats.value = statsRes.data
    memories.value = memoriesRes.data
  } catch (err) {
    console.error('加载数据失败', err)
  }
}

const formatTime = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.memory-status {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.header {
  margin-bottom: 40px;
}

.header h1 {
  font-size: 32px;
  font-weight: 600;
  color: #111;
  margin: 0 0 8px 0;
}

.header p {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-bottom: 40px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  padding: 24px;
  transition: all 0.2s;
}

.stat-card:hover {
  border-color: #d0d0d0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-label {
  font-size: 13px;
  color: #888;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #111;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.memories-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: #111;
  margin: 0 0 20px 0;
}

.memory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.memory-card {
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s;
  cursor: default;
}

.memory-card:hover {
  border-color: #d0d0d0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.memory-name {
  font-size: 16px;
  font-weight: 600;
  color: #111;
  margin-bottom: 8px;
}

.memory-location {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}

.memory-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.memory-time {
  font-size: 12px;
  color: #999;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 14px;
}
</style>
