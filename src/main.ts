import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/main.css'
import { createI18n } from 'vue-i18n'
import ru from './locales/ru.json'
import en from './locales/en.json'
import cn from './locales/cn.json'

// Создаем экземпляр i18n
const i18n = createI18n({
  legacy: false, // ✅ Важно для Vue 3
  locale: 'ru', // язык по умолчанию
  fallbackLocale: 'en', // фолбэк язык
  messages: {
    ru,
    en, 
    cn
  },
  globalInjection: true // ✅ Для глобального $t в шаблонах
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)



app.mount('#app')