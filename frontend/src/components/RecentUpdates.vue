<template>
  <div class="p-5 border-b border-gray-200 dark:border-gray-700 h-full min-h-[100px]">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
        最近更新 <span class="text-indigo-600 dark:text-indigo-400">({{ updates.length }})</span>
      </h3>
      <button
        v-if="updates.length > 1"
        class="px-3 py-1.5 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200"
        @click="expanded = !expanded"
      >
        {{ expanded ? '收起' : '展开' }}
      </button>
    </div>

    <!-- 时间线列表 -->
    <ul class="space-y-3">
      <li
        v-for="(item, index) in updates"
        :key="item.id"
        v-show="expanded || index === 0"
        class="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        <!-- 时间线点 -->
        <div class="flex-shrink-0 w-2 h-2 mt-2 bg-indigo-500 rounded-full"></div>

        <!-- 内容 -->
        <div class="flex-1 min-w-0">
          <div class="flex items-baseline justify-between gap-2">
            <span class="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">
              {{ item.name }}
            </span>
            <span class="flex-shrink-0 text-xs text-gray-500 dark:text-gray-400">
              {{ formatTime(item.updated_at) }}
            </span>
          </div>
          <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5 truncate">
            {{ item.location }}
          </p>
        </div>
      </li>
    </ul>

    <p v-if="updates.length === 0" class="text-center py-6 text-gray-500 dark:text-gray-400 text-sm">
      暂无更新
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  updates: { type: Array, default: () => [] }
})

const expanded = ref(false)

const formatTime = (datetime) => {
  if (!datetime) return ''
  return new Date(datetime).toLocaleString('zh-CN')
}
</script>

<style scoped>
/* Tailwind 已处理所有样式 */
</style>
