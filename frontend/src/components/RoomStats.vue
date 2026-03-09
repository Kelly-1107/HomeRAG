<template>
  <div class="p-5 border-b border-gray-200 dark:border-gray-700 h-full min-h-[100px]">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
        {{ type === 'consumption' ? '位置分布' : '房间分布' }} <span class="text-indigo-600 dark:text-indigo-400">({{ stats.length }})</span>
      </h3>
      <button
        v-if="stats.length > 1"
        class="px-3 py-1.5 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200"
        @click="expanded = !expanded"
      >
        {{ expanded ? '收起' : '展开' }}
      </button>
    </div>

    <!-- 房间列表 -->
    <ul class="space-y-2">
      <li
        v-for="(stat, index) in stats"
        :key="stat.room"
        v-show="expanded || index === 0"
        class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        <span class="text-sm font-medium text-gray-800 dark:text-gray-100">{{ stat.room }}</span>
        <span class="px-3 py-1 bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-400 rounded-full text-sm font-semibold">
          {{ stat.count }} {{ type === 'consumption' ? '笔' : '件' }}
        </span>
      </li>
    </ul>

    <p v-if="stats.length === 0" class="text-center py-6 text-gray-500 dark:text-gray-400 text-sm">
      暂无数据
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  stats: { type: Array, default: () => [] },
  type: { type: String, default: 'item' }
})

const expanded = ref(false)
</script>

<style scoped>
/* Tailwind 已处理所有样式 */
</style>
