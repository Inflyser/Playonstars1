import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/variables.css' 
import './styles/main.css'

// Инициализация Telegram WebApp
declare global {
  interface Window {
    Telegram: {
      WebApp: any
    }
  }
}

if (window.Telegram?.WebApp) {
  console.log('📱 Telegram WebApp detected')
  const webApp = window.Telegram.WebApp
  webApp.expand() // Растягиваем на весь экран
  webApp.ready() // Говорим Telegram что готовы
  console.log('✅ Telegram WebApp initialized')
  
  // Применяем тему Telegram сразу
  document.body.style.backgroundColor = webApp.themeParams?.bg_color || '#ffffff'
  document.body.style.color = webApp.themeParams?.text_color || '#222222'
} else {
  console.log('🌐 Running in browser mode')
}

const app = createApp(App)
app.use(router)
app.mount('#app')