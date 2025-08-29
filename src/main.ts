import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/main.css'


const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)


// Инициализация после создания app, но до mount
declare global {
  interface Window {
    Telegram: any;
  }
}

app.mount('#app')