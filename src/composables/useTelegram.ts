import { ref, onMounted } from 'vue'

// Определяем интерфейсы для Telegram WebApp
declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        initDataUnsafe: any;
        expand: () => void;
        ready: () => void;
        // Добавьте другие методы по необходимости
      }
    }
  }
}

export const useTelegram = () => {
  const isWebApp = ref(false)
  const webApp = ref<Window['Telegram']['WebApp'] | null>(null)
  const isInitialized = ref(false)

  const init = () => {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      isWebApp.value = true
      webApp.value = window.Telegram.WebApp
      isInitialized.value = true
      console.log('Telegram WebApp detected and initialized')
    } else {
      isWebApp.value = false
      isInitialized.value = true
      console.log('Regular browser environment')
    }
  }

  onMounted(() => {
    // Даем время для загрузки Telegram скрипта
    setTimeout(init, 300)
  })

  const expandApp = () => {
    if (webApp.value) {
      webApp.value.expand()
      console.log('Telegram WebApp expanded')
    }
  }

  const initTelegramAuth = async (): Promise<boolean> => {
    if (!isWebApp.value || !webApp.value) return false
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
    isInitialized,
    expandApp,
    initTelegramAuth,
    init
  }
}