<template>
  <div class="flex gap-2">
    <input
      v-model="message"
      type="text"
      placeholder="输入物品信息或问题..."
      class="flex-1 px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
      @keyup.enter="send"
    />
    <button
      @click="send"
      :disabled="!message.trim()"
      class="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95"
    >
      发送
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['send'])
const message = ref('')

const send = () => {
  if (!message.value.trim()) return
  emit('send', message.value)
  message.value = ''
}
</script>

<style scoped>
/* Tailwind 已处理所有样式 */
</style>
