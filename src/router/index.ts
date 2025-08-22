import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/crash',
    name: 'Crash',
    component: () => import('../views/CrashGameView.vue')
  },
  {
    path: '/cases',
    name: 'Cases',
    component: () => import('../views/CrashGameView.vue')
  },
  {
    path: '/top',
    name: 'Top',
    component: () => import('../views/CrashGameView.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/CrashGameView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router