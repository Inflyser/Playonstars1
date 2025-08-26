import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref<any>(null)
  const isAuthenticated = ref(false)

  // Пока просто заглушка
  const initAuth = async (): Promise<boolean> => {
    console.log('Auth function called')
    return false
  }

  // Заглушка для баланса
  const fetchBalance = async () => {
    console.log('Fetch balance called')
    return { ton: 0, stars: 0 }
  }

  // Заглушка для выхода
  const logout = async () => {
    console.log('Logout called')
  }

  return {
    user,
    isAuthenticated,
    initAuth,
    fetchBalance,
    logout
  }
})