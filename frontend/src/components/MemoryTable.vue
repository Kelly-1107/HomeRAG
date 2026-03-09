<template>
  <div class="p-5 border-b border-gray-200 dark:border-gray-700">
    <!-- 工具栏 -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-800 dark:text-gray-100">
        记忆列表 <span class="text-indigo-600 dark:text-indigo-400">({{ memories.length }})</span>
      </h3>
      <div class="flex gap-2">
        <button
          v-if="selected.size > 0"
          class="px-4 py-2 bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-400 rounded-lg font-medium hover:bg-red-100 dark:hover:bg-red-900/50 transition-all duration-200 hover:scale-105"
          @click="confirmBatchDelete"
        >
          删除选中 ({{ selected.size }})
        </button>
        <button
          v-if="memories.length > 1"
          class="px-4 py-2 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200"
          @click="expanded = !expanded"
        >
          {{ expanded ? '收起' : '展开' }}
        </button>
      </div>
    </div>

    <!-- 表格 -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700">
            <th class="w-10 pb-3 text-left">
              <input
                type="checkbox"
                :checked="allSelected"
                :indeterminate="someSelected"
                @change="toggleAll"
                class="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
              />
            </th>
            <th class="pb-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">名称</th>
            <th class="pb-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">数量</th>
            <th class="pb-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">位置</th>
            <th class="pb-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">房间</th>
            <th class="pb-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">属性</th>
            <th class="pb-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">操作</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(item, index) in memories" :key="item.id">
            <template v-if="expanded || index === 0">
              <!-- 普通行 -->
              <tr
                v-if="editingId !== item.id"
                class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                :class="{ 'bg-indigo-50 dark:bg-indigo-900/20': selected.has(item.id) }"
              >
                <td class="py-3">
                  <input
                    type="checkbox"
                    :checked="selected.has(item.id)"
                    @change="toggleOne(item.id)"
                    class="w-4 h-4 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                  />
                </td>
                <td class="py-3 text-sm text-gray-900 dark:text-gray-100 font-medium">{{ item.name }}</td>
                <td class="py-3 text-sm text-gray-600 dark:text-gray-400">
                  <span class="px-2 py-1 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 rounded-full text-xs font-semibold">
                    {{ item.quantity || 1 }}
                  </span>
                </td>
                <td class="py-3 text-sm text-gray-600 dark:text-gray-400">{{ item.location }}</td>
                <td class="py-3 text-sm text-gray-600 dark:text-gray-400">{{ item.room }}</td>
                <td class="py-3 text-sm text-gray-600 dark:text-gray-400">{{ formatAttributes(item.attributes) }}</td>
                <td class="py-3">
                  <div class="flex gap-2">
                    <button
                      class="px-3 py-1.5 bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400 rounded-lg text-sm font-medium hover:bg-indigo-200 dark:hover:bg-indigo-900/50 transition-all duration-200 hover:scale-105"
                      @click="startEdit(item)"
                    >
                      编辑
                    </button>
                    <button
                      class="px-3 py-1.5 bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 rounded-lg text-sm font-medium hover:bg-red-200 dark:hover:bg-red-900/50 transition-all duration-200 hover:scale-105"
                      @click="confirmSingleDelete(item)"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>

              <!-- 编辑行 -->
              <tr
                v-else
                class="border-b border-gray-100 dark:border-gray-700 bg-indigo-50 dark:bg-indigo-900/20"
              >
                <td class="py-3"></td>
                <td class="py-3">
                  <input
                    v-model="editForm.name"
                    class="w-full px-3 py-1.5 bg-white dark:bg-gray-700 border border-indigo-300 dark:border-indigo-600 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </td>
                <td class="py-3">
                  <input
                    v-model.number="editForm.quantity"
                    type="number"
                    min="1"
                    class="w-full px-3 py-1.5 bg-white dark:bg-gray-700 border border-indigo-300 dark:border-indigo-600 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </td>
                <td class="py-3">
                  <input
                    v-model="editForm.location"
                    class="w-full px-3 py-1.5 bg-white dark:bg-gray-700 border border-indigo-300 dark:border-indigo-600 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </td>
                <td class="py-3">
                  <input
                    v-model="editForm.room"
                    class="w-full px-3 py-1.5 bg-white dark:bg-gray-700 border border-indigo-300 dark:border-indigo-600 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </td>
                <td class="py-3">
                  <input
                    v-model="editForm.attributesStr"
                    placeholder="用逗号分隔"
                    class="w-full px-3 py-1.5 bg-white dark:bg-gray-700 border border-indigo-300 dark:border-indigo-600 rounded-lg text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </td>
                <td class="py-3">
                  <div class="flex gap-2">
                    <button
                      class="px-3 py-1.5 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 rounded-lg text-sm font-medium hover:bg-green-200 dark:hover:bg-green-900/50 transition-all duration-200 hover:scale-105"
                      @click="saveEdit(item.id)"
                    >
                      保存
                    </button>
                    <button
                      class="px-3 py-1.5 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200"
                      @click="cancelEdit"
                    >
                      取消
                    </button>
                  </div>
                </td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>

    <p v-if="memories.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
      暂无记忆
    </p>

    <!-- 删除确认对话框 -->
    <div
      v-if="dialog.visible"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="dialog.visible = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 min-w-[320px] max-w-md transform transition-all">
        <p class="text-gray-800 dark:text-gray-100 text-base mb-6">{{ dialog.message }}</p>
        <div class="flex justify-end gap-3">
          <button
            class="px-5 py-2.5 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200"
            @click="dialog.visible = false"
          >
            取消
          </button>
          <button
            class="px-5 py-2.5 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-all duration-200 hover:scale-105"
            @click="dialog.onConfirm"
          >
            确认删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

const props = defineProps({
  memories: { type: Array, default: () => [] }
})
const emit = defineEmits(['delete', 'delete-batch', 'update'])

const expanded = ref(false)

const selected = ref(new Set())
const allSelected = computed(() => props.memories.length > 0 && selected.value.size === props.memories.length)
const someSelected = computed(() => selected.value.size > 0 && selected.value.size < props.memories.length)

const toggleAll = (e) => {
  selected.value = e.target.checked ? new Set(props.memories.map(m => m.id)) : new Set()
}
const toggleOne = (id) => {
  const s = new Set(selected.value)
  s.has(id) ? s.delete(id) : s.add(id)
  selected.value = s
}

const dialog = reactive({ visible: false, message: '', onConfirm: null })

const confirmSingleDelete = (item) => {
  dialog.message = `确认删除「${item.name}」？`
  dialog.onConfirm = () => { dialog.visible = false; emit('delete', item.id) }
  dialog.visible = true
}
const confirmBatchDelete = () => {
  dialog.message = `确认删除选中的 ${selected.value.size} 条记忆？`
  dialog.onConfirm = () => {
    dialog.visible = false
    emit('delete-batch', [...selected.value])
    selected.value = new Set()
  }
  dialog.visible = true
}

const editingId = ref(null)
const editForm = ref({ name: '', quantity: 1, location: '', room: '', attributesStr: '' })

const startEdit = (item) => {
  editingId.value = item.id
  editForm.value = {
    name: item.name,
    quantity: item.quantity || 1,
    location: item.location,
    room: item.room,
    attributesStr: (item.attributes || []).join(', ')
  }
}
const cancelEdit = () => { editingId.value = null }
const saveEdit = (id) => {
  const attributes = editForm.value.attributesStr.split(',').map(s => s.trim()).filter(s => s.length > 0)
  emit('update', id, {
    name: editForm.value.name,
    quantity: editForm.value.quantity || 1,
    location: editForm.value.location,
    room: editForm.value.room,
    attributes,
    type: 'item'
  })
  editingId.value = null
}

const formatAttributes = (attrs) => {
  if (!attrs || !Array.isArray(attrs)) return '-'
  return attrs.join(', ')
}
</script>

<style scoped>
/* Tailwind 已处理所有样式 */
</style>
