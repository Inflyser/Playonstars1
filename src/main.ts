import { createApp, onMounted } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/main.css'
import { useWalletStore } from '@/stores/useWalletStore';
const walletStore = useWalletStore();

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)



// Обработка возврата из кошелька
const handleWalletReturn = () => {
  const urlParams = new URLSearchParams(window.location.search);
  
  // Проверяем параметры TonConnect
  if (urlParams.has('tonconnect') || urlParams.has('startattach')) {
    console.log('🔄 TonConnect return detected');
    
    // Даем время на обработку подключения
    setTimeout(() => {
      walletStore.init().catch(console.error);
    }, 2000);
  }
};

// Вызываем при загрузке и изменении URL
onMounted(() => {
  handleWalletReturn();
  
  // Слушаем изменения URL (для SPA)
  window.addEventListener('popstate', handleWalletReturn);
});

// Инициализация после создания app, но до mount


app.mount('#app')