import { ref } from 'vue'

declare global {
  interface Window {
    Telegram: {
      WebApp: any
    }
  }
}

export const useTelegram = () => {
  const isWebApp = ref(!!window.Telegram?.WebApp)
  const webApp = ref(window.Telegram?.WebApp || null)

  // Добавьте эту функцию ↓
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
    expandApp, // ← Не забудьте экспортировать!
    initTelegramAuth
  }
}