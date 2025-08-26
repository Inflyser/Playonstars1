import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api.ts'

export const useUserStore = defineStore('user', () => {
  const user = ref<any>(null)
  const isAuthenticated = ref(false)

  const initAuth = async (): Promise<boolean> => {
    // Просто ебнем проверку как есть
    const isWebApp = !!window.Telegram?.WebApp
    
    if (isWebApp) {
      try {
        // Без всяких проверок, нахуй typescript
        const initData = window.Telegram.WebApp.initData
        console.log('Telegram initData:', initData)
        
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
      // Для браузера
      try {
        if (window.location.pathname !== '/telegram-only') {
          const response = await api.get('/api/auth/check')
          user.value = response.data.user
          isAuthenticated.value = true
          return true
        }
        return false
      } catch (error) {
        isAuthenticated.value = false
        return false
      }
    }
  }

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