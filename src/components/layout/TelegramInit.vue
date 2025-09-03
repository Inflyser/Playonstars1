<template>
  <!-- Показываем загрузчик/ошибку пока не инициализировано -->
  <div v-if="!isInitialized" class="telegram-init-container">
    <TGLoader v-if="isLoading" />
    <div v-else-if="error" class="error-message">
      {{ error }}
      <button @click="retryInit" class="retry-btn">Retry</button>
    </div>
  </div>
  
  <!-- После инициализации показываем основное приложение -->
  <AppLayout v-else>
    <RouterView />
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useTelegram } from '@/composables/useTelegram';
import { initTelegramWebApp, getTelegramInitData } from '@/utils/telegram';
import { useUserStore } from '@/stores/useUserStore';
import { initTonConnect } from '@/services/tonconnect';
import { useWalletStore } from '@/stores/useWalletStore';
import TGLoader from '@/components/ui/TGLoader.vue';
import AppLayout from '@/components/layout/AppLayout.vue';

const { initTelegram, fetchUserData, fetchBalance, isLoading, error } = useTelegram();
const userStore = useUserStore();
const walletStore = useWalletStore();
const isInitialized = ref(false);

const retryInit = async () => {
  console.log('🔄 Retrying initialization...');
  isInitialized.value = false;
  error.value = null;
  await initializeApp();
};

const initializeApp = async () => {
  console.log('🔐 Starting Telegram initialization...');
  
  const isTelegram = initTelegramWebApp();
  console.log('Is Telegram environment:', isTelegram);
  
  if (isTelegram) {
    const initData = getTelegramInitData();
    console.log('InitData available:', !!initData);
    
    if (initData) {
      console.log('🔄 Authenticating with Telegram...');
      const success = await initTelegram(initData);
      
      if (success) {
        console.log('✅ Telegram auth successful');
        
        // ✅ ВАЖНО: ВЫЗЫВАЕМ методы получения данных ПОСЛЕ аутентификации
        console.log('📦 Loading user data...');
        await fetchUserData(); // Вызываем метод из useTelegram()
        
        console.log('💰 Loading balance...');
        await fetchBalance(); // Вызываем метод из useTelegram()
        
        // Инициализируем TonConnect
        console.log('🔗 Initializing TonConnect...');
        await initTonConnect();
        await walletStore.init();
        
        isInitialized.value = true;
        console.log('🎉 App fully initialized');
      } else {
        console.error('❌ Telegram auth failed');
      }
    } else {
      console.warn('⚠️ No initData available');
      // Инициализируем только TonConnect
      await initTonConnect();
      await walletStore.init();
      isInitialized.value = true;
    }
  } else {
    console.log('🌐 Running in browser mode');
    // Инициализируем только TonConnect
    await initTonConnect();
    await walletStore.init();
    isInitialized.value = true;
  }
};

onMounted(async () => {
  await initializeApp();
});


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
</script>


<style scoped>
.telegram-init-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: var(--tg-theme-bg-color, #000000);
}

.error-message {
  color: #ff4757;
  text-align: center;
  padding: 2rem;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #007aff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.retry-btn:hover {
  opacity: 0.9;
}
</style>