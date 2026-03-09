import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json; charset=utf-8'
  }
})

export const chat = (userId, message) => {
  return api.post('/chat', {
    user_id: userId,
    message
  })
}

export const listMemories = (userId, type = null) => {
  return api.get('/memories', {
    params: { user_id: userId, type }
  })
}

export const getMemory = (memoryId) => {
  return api.get(`/memories/${memoryId}`)
}

export const deleteMemory = (memoryId) => {
  return api.delete(`/memories/${memoryId}`)
}

export const batchDeleteMemories = (memoryIds) => {
  return api.post('/memories/batch-delete', { memory_ids: memoryIds })
}

export const updateMemory = (memoryId, structuredData) => {
  return api.put(`/memories/${memoryId}`, { structured_data: structuredData })
}

export const getRoomStats = (userId, type = null) => {
  return api.get('/stats/rooms', {
    params: { user_id: userId, type }
  })
}

export const getRecentUpdates = (userId, limit = 10, type = null) => {
  return api.get('/stats/recent', {
    params: { user_id: userId, limit, type }
  })
}

export const getTagStats = (userId, type = null) => {
  return api.get('/stats/tags', {
    params: { user_id: userId, type }
  })
}

export const getStats = (userId) => {
  return api.get('/stats', {
    params: { user_id: userId }
  })
}

export default api
