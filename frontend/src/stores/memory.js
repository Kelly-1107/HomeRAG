import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '../api/memory.js'

const CACHE_TTL = 5 * 60 * 1000 // 5分钟缓存
const CACHE_KEY_PREFIX = 'homerag_cache'

function getCacheKey(userId, type, key) {
  return `${CACHE_KEY_PREFIX}:${userId}:${type}:${key}`
}

function getCached(key) {
  try {
    const stored = localStorage.getItem(key)
    if (!stored) return null
    const cached = JSON.parse(stored)
    if (Date.now() < cached.expiresAt) {
      return cached.data
    }
    localStorage.removeItem(key)
  } catch (e) {
    console.error('Cache read error:', e)
  }
  return null
}

function setCached(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify({
      expiresAt: Date.now() + CACHE_TTL,
      data
    }))
  } catch (e) {
    console.error('Cache write error:', e)
  }
}

export const useMemoryStore = defineStore('memory', () => {
  const memories = ref([])
  const roomStats = ref([])
  const recentUpdates = ref([])
  const tagStats = ref({})
  const loading = ref(false)

  const userId = ref('user_001') // 默认用户
  const currentType = ref('item') // 当前显示的记忆类型

  async function fetchMemories() {
    const cacheKey = getCacheKey(userId.value, currentType.value, 'memories')
    const cached = getCached(cacheKey)
    if (cached) {
      memories.value = cached
      return
    }

    loading.value = true
    try {
      const res = await api.listMemories(userId.value, currentType.value)
      memories.value = res.data
      setCached(cacheKey, res.data)
    } finally {
      loading.value = false
    }
  }

  function clearData() {
    memories.value = []
    roomStats.value = []
    recentUpdates.value = []
    tagStats.value = {}
  }

  async function fetchRoomStats() {
    const cacheKey = getCacheKey(userId.value, currentType.value, 'roomStats')
    const cached = getCached(cacheKey)
    if (cached) {
      roomStats.value = cached
      return
    }

    try {
      const res = await api.getRoomStats(userId.value, currentType.value)
      roomStats.value = res.data
      setCached(cacheKey, res.data)
    } catch (error) {
      console.error('fetchRoomStats error:', error)
      roomStats.value = []
    }
  }

  async function fetchRecentUpdates() {
    const cacheKey = getCacheKey(userId.value, currentType.value, 'recentUpdates')
    const cached = getCached(cacheKey)
    if (cached) {
      recentUpdates.value = cached
      return
    }

    try {
      const res = await api.getRecentUpdates(userId.value, 10, currentType.value)
      recentUpdates.value = res.data
      setCached(cacheKey, res.data)
    } catch (error) {
      console.error('fetchRecentUpdates error:', error)
      recentUpdates.value = []
    }
  }

  async function fetchTagStats() {
    const cacheKey = getCacheKey(userId.value, currentType.value, 'tagStats')
    const cached = getCached(cacheKey)
    if (cached) {
      tagStats.value = cached
      return
    }

    try {
      const res = await api.getTagStats(userId.value, currentType.value)
      tagStats.value = res.data
      setCached(cacheKey, res.data)
    } catch (error) {
      console.error('fetchTagStats error:', error)
      tagStats.value = {}
    }
  }

  async function sendMessage(message) {
    try {
      const res = await api.chat(userId.value, message)
      // 发送后刷新数据（不清缓存，下次切换时重新请求）
      await Promise.allSettled([
        fetchMemories(),
        fetchRecentUpdates(),
        fetchRoomStats(),
        fetchTagStats()
      ])
      return res.data
    } catch (error) {
      console.error('sendMessage error:', error)
      throw error
    }
  }

  async function deleteItem(id) {
    await api.deleteMemory(id)
    // 删除后清除当前类型的缓存
    clearTypeCache(currentType.value)
    await Promise.allSettled([
      fetchMemories(),
      fetchRoomStats(),
      fetchRecentUpdates(),
      fetchTagStats()
    ])
  }

  async function deleteItems(ids) {
    await api.batchDeleteMemories(ids)
    // 删除后清除当前类型的缓存
    clearTypeCache(currentType.value)
    await Promise.allSettled([
      fetchMemories(),
      fetchRoomStats(),
      fetchRecentUpdates(),
      fetchTagStats()
    ])
  }

  async function updateItem(id, structuredData) {
    await api.updateMemory(id, structuredData)
    // 更新后清除当前类型的缓存
    clearTypeCache(currentType.value)
    await Promise.allSettled([
      fetchMemories(),
      fetchRoomStats(),
      fetchRecentUpdates(),
      fetchTagStats()
    ])
  }

  function clearTypeCache(type) {
    const keysToRemove = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.includes(`:${type}:`)) {
        keysToRemove.push(key)
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key))
  }

  async function loadAllStats() {
    await Promise.all([
      fetchMemories(),
      fetchRoomStats(),
      fetchRecentUpdates(),
      fetchTagStats()
    ])
  }

  return {
    userId,
    currentType,
    memories,
    roomStats,
    recentUpdates,
    tagStats,
    loading,
    fetchMemories,
    fetchRoomStats,
    fetchRecentUpdates,
    fetchTagStats,
    clearData,
    sendMessage,
    deleteItem,
    deleteItems,
    updateItem,
    loadAllStats
  }
})
