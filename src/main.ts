import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/main.css'

const app = createApp(App)
app.use(router)
app.mount('#app')

// Инициализацию Telegram лучше перенести в App.vue

// Инициализируем Telegram после монтирования
app.mount('#app').$nextTick(() => {
  const { init } = useTelegram()
  init()
})