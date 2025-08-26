import { ref, onMounted } from 'vue'

declare global {
  interface Window {
    Telegram: {
      WebApp: any
    }
  }
}

export const useTelegram = () => {
  const isWebApp = ref(false)
  const webApp = ref<any>(null)
  const isInitialized = ref(false)

  // Ждем инициализации Telegram
  onMounted(() => {
    const checkTelegram = () => {
      if (window.Telegram?.WebApp) {
        isWebApp.value = true
        webApp.value = window.Telegram.WebApp
        isInitialized.value = true
      } else {
        // Проверяем еще раз через небольшой интервал
        setTimeout(checkTelegram, 100)
      }
    }
    
    checkTelegram()
  })

  const expandApp = () => {
    if (webApp.value) {
      webApp.value.expand()
    }
  }

  const initTelegramAuth = async (): Promise<boolean> => {
    if (!isWebApp.value) return false
    try {
      const initData = webApp.value.initData
      const response = await fetch('/api/auth/telegram', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ initData })
      })
      return response.ok
    } catch (error) {
      console.error('Telegram auth error:', error)
      return false
    }
  }

  return {
    isWebApp,
    webApp,
    isInitialized, // ← Добавляем флаг инициализации
    expandApp,
    initTelegramAuth
  }
}