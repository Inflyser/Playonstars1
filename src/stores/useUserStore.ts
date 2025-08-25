import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useUserStore = defineStore('user', () => {
  const user = ref<any>(null)
  const isAuthenticated = ref(false)

  // Автоматическая авторизация через Telegram
  const initAuth = async (): Promise<boolean> => {
    // Проверяем это Telegram Web App через window
    const isWebApp = !!window.Telegram?.WebApp
    
    if (isWebApp) {
      // Telegram Web App - используем прямую авторизацию
      try {
        const initData = window.Telegram.WebApp.initData
        const response = await fetch('/api/auth/telegram', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ initData })
        })

        if (response.ok) {
          const data = await response.json()
          user.value = data.user
          isAuthenticated.value = true
          return true
        }
        return false
      } catch (error) {
        console.error('Telegram auth error:', error)
        return false
      }
    } else {
      // Веб-версия - проверяем сессию
      try {
        const response = await api.get('/api/auth/check')
        user.value = response.data.user
        isAuthenticated.value = true
        return true
      } catch (error) {
        isAuthenticated.value = false
        return false
      }
    }
  }

  // Получить баланс
  const fetchBalance = async () => {
    try {
      const response = await api.get('/api/user/balance')
      if (user.value) {
        user.value.ton_balance = response.data.ton
        user.value.stars_balance = response.data.stars
      }
      return response.data
    } catch (error) {
      console.error('Balance fetch error:', error)
      return { ton: 0, stars: 0 }
    }
  }

  // Выйти
  const logout = async () => {
    try {
      await api.post('/api/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      user.value = null
      isAuthenticated.value = false
    }
  }

  return {
    user,
    isAuthenticated,
    initAuth,
    fetchBalance,
    logout
  }
})