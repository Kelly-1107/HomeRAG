import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import MemoryStatus from '../views/MemoryStatus.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/status',
    name: 'MemoryStatus',
    component: MemoryStatus
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
