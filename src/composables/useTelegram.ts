import { ref, onMounted } from 'vue'

export const useTelegram = () => {
  const webApp = ref<any>(null)
  const user = ref<any>(null)
  const isReady = ref(false)

  const init = () => {
    if (window.Telegram?.WebApp) {
      webApp.value = window.Telegram.WebApp
      user.value = webApp.value.initDataUnsafe?.user
      webApp.value.expand()
      webApp.value.ready()
      isReady.value = true
      console.log('Telegram user:', user.value)
    }
  }

  onMounted(() => {
    // Ждем немного перед инициализацией
    setTimeout(init, 100)
  })

  return {
    webApp,
    user,
    isReady,
    init
  }
}