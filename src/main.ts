import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/main.css'

console.log('🚀 Starting app...')

// Простая инициализация Telegram
if (window.Telegram?.WebApp) {
  console.log('📱 Telegram detected')
  window.Telegram.WebApp.expand()
  window.Telegram.WebApp.ready()
}

const app = createApp(App)

// Проверка роутера
console.log('🛣️ Router:', router)
app.use(router)

app.mount('#app')
console.log('✅ App mounted')