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
    path: '/pvp',
    name: 'Cases',
    component: () => import('../views/CasesView.vue')
  },
  {
    path: '/top',
    name: 'Top',
    component: () => import('../views/TopView.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue')
  },
  {
    path: '/balance',
    name: 'Balance',
    component: () => import('../views/BalanceViewTon.vue')
  },
  {
    path: '/telegram-only',
    name: 'telegram-only',
    component: () => import('@/views/LoginView.vue')
  },
  {
    path: '/admin-login',
    name: 'AdminLogin',
    component: () => import('../views/AdminLogin.vue')
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router