import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/main.css'

// Создаем приложение
const app = createApp(App)
app.use(router)

// Инициализация Telegram ДО монтирования
if (window.Telegram?.WebApp) {
  const webApp = window.Telegram.WebApp
  webApp.expand()
  webApp.ready()
  console.log('✅ Telegram WebApp initialized')
}

// Монтируем приложение
app.mount('#app')

// Простая проверка после монтирования
console.log('🚀 App mounted successfully')