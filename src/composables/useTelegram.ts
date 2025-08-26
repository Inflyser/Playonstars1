import { ref, onMounted } from 'vue'

export const useTelegram = () => {
  const isWebApp = ref(false)
  const webApp = ref<any>(null)
  const isInitialized = ref(false)

  const init = () => {
    // Нахуй типы, просто работаем
    if (window.Telegram?.WebApp) {
      isWebApp.value = true
      webApp.value = window.Telegram.WebApp
      isInitialized.value = true
      console.log('Telegram detected, initData:', window.Telegram.WebApp.initData)
    } else {
      isWebApp.value = false
      isInitialized.value = true
      console.log('Not in Telegram')
    }
  }

  onMounted(() => {
    // Даем время на загрузку
    setTimeout(init, 500)
  })

  const expandApp = () => {
    if (webApp.value) {
      webApp.value.expand()
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