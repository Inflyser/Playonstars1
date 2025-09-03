import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/main.css'
import { connector } from '@/services/tonconnect';

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)



if (window.Telegram?.WebApp) {
  // Проверяем параметры URL для TonConnect
  const urlParams = new URLSearchParams(window.location.search);
  const tonconnectData = urlParams.get('tonconnect');
  
  if (tonconnectData) {
    console.log('TonConnect deep link detected');
    // Автоматически обрабатываем подключение
    connector.connect({
      universalLink: window.location.href,
      bridgeUrl: 'https://bridge.tonapi.io/bridge'
    });
  }
}

// Инициализация после создания app, но до mount


app.mount('#app')