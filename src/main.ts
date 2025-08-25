import { createApp } from 'vue'
import { createPinia } from 'pinia' // ← ДОБАВЬТЕ ЭТОТ ИМПОРТ
import App from './App.vue'
import router from './router'
import './styles/main.css'

const app = createApp(App)
const pinia = createPinia() // ← СОЗДАЙТЕ Pinia

app.use(pinia) // ← УСТАНОВИТЕ Pinia ПЕРЕД router
app.use(router)
app.mount('#app')