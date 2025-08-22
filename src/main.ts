import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/variables.css' 
import './styles/main.css'

const app = createApp(App)
app.use(router)

// Инициализация Telegram WebApp
declare global {
  interface Window {
    Telegram: {
      WebApp: any
    }
  }
}

// После монтирования приложения
app.mount('#app').$nextTick(() => {
  if (window.Telegram?.WebApp) {
    const webApp = window.Telegram.WebApp
    webApp.expand() // Растянуть на весь экран
    webApp.ready() // Сообщить Telegram что приложение готово
    console.log('Telegram WebApp initialized')
  }
})