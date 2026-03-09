<template>
  <div class="p-5">
    <!-- 标题栏 -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
        标签聚类 <span class="text-indigo-600 dark:text-indigo-400">({{ tagList.length }})</span>
      </h3>
      <button
        v-if="needsToggle"
        class="px-3 py-1.5 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200"
        @click="expanded = !expanded"
      >
        {{ expanded ? '收起' : '展开' }}
      </button>
    </div>

    <!-- 标签云 - 横向滚动 pill 样式 -->
    <div
      ref="tagsContainer"
      class="flex flex-wrap gap-2 transition-all duration-300"
      :class="{ 'max-h-12 overflow-hidden': !expanded && needsToggle }"
    >
      <span
        v-for="item in tagList"
        :key="item.tag"
        class="tag inline-flex items-center px-4 py-2 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded-full text-sm font-medium hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-all duration-200 hover:scale-105 cursor-default"
        :style="{ fontSize: getFontSize(item.count) }"
      >
        {{ item.tag }}
        <span class="ml-1.5 px-1.5 py-0.5 bg-indigo-200 dark:bg-indigo-800 text-indigo-800 dark:text-indigo-300 rounded-full text-xs font-semibold">
          {{ item.count }}
        </span>
      </span>
    </div>

    <p v-if="tagList.length === 0" class="text-center py-6 text-gray-500 dark:text-gray-400 text-sm">
      暂无标签
    </p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'

const props = defineProps({
  tags: { type: Object, default: () => ({}) }
})

const expanded = ref(false)
const tagsContainer = ref(null)
const needsToggle = ref(false)

const tagList = computed(() => {
  return Object.entries(props.tags).map(([tag, count]) => ({ tag, count }))
})

const getFontSize = (count) => {
  const minSize = 12
  const maxSize = 24
  const base = Math.min(count, 10) / 10
  return `${minSize + base * (maxSize - minSize)}px`
}

const checkOverflow = async () => {
  await nextTick()
  if (!tagsContainer.value || tagList.value.length === 0) {
    needsToggle.value = false
    return
  }

  // 临时展开以测量真实高度
  const wasExpanded = expanded.value
  expanded.value = true
  await nextTick()

  const container = tagsContainer.value
  const firstTag = container.querySelector('.tag')

  if (!firstTag) {
    needsToggle.value = false
    return
  }

  // 获取第一个标签的底部位置
  const firstTagBottom = firstTag.offsetTop + firstTag.offsetHeight

  // 检查是否有标签的顶部位置超过第一行
  const tags = container.querySelectorAll('.tag')
  let hasMultipleLines = false

  for (let i = 1; i < tags.length; i++) {
    if (tags[i].offsetTop >= firstTagBottom) {
      hasMultipleLines = true
      break
    }
  }

  needsToggle.value = hasMultipleLines
  expanded.value = wasExpanded
}

onMounted(() => {
  checkOverflow()
})

watch(() => props.tags, () => {
  checkOverflow()
}, { deep: true })
</script>

<style scoped>
/* Tailwind 已处理所有样式 */
</style>
