<script setup lang="ts">
import { onMounted, ref, onUnmounted } from 'vue';
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

// ✅ Обработчик глубоких ссылок TonConnect
const handleWalletReturn = () => {
  const urlParams = new URLSearchParams(window.location.search);
  
  console.log('🔍 Checking URL params for wallet return:', {
    tonconnect: urlParams.has('tonconnect'),
    startattach: urlParams.has('startattach'),
    ref: urlParams.get('ref')
  });
  
  // Проверяем параметры TonConnect
  if (urlParams.has('tonconnect') || urlParams.has('startattach')) {
    console.log('🔄 TonConnect return detected - initializing wallet');
    
    // Очищаем URL чтобы избежать повторной обработки
    const cleanUrl = window.location.origin + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl);
    
    // Даем время на обработку подключения
    setTimeout(() => {
      walletStore.init().then(() => {
        console.log('✅ Wallet initialized after return');
      }).catch((err) => {
        console.error('❌ Failed to init wallet after return:', err);
      });
    }, 1500);
  }
};

const retryInit = async () => {
  console.log('🔄 Retrying initialization...');
  isInitialized.value = false;
  error.value = null;
  await initializeApp();
};

const initializeApp = async () => {
  console.log('🔐 Starting Telegram initialization...');
  
  // ✅ Сначала проверяем возврат из кошелька
  handleWalletReturn();
  
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
        
        // ✅ Параллельно загружаем данные
        await Promise.all([
          (async () => {
            try {
              console.log('📦 Loading user data...');
              await fetchUserData();
            } catch (err) {
              console.error('Failed to load user data:', err);
            }
          })(),
          
          (async () => {
            try {
              console.log('💰 Loading balance...');
              await fetchBalance();
            } catch (err) {
              console.error('Failed to load balance:', err);
            }
          })(),
          
          (async () => {
            try {
              console.log('🔗 Initializing TonConnect...');
              await initTonConnect();
              await walletStore.init();
            } catch (err) {
              console.error('Failed to init TonConnect:', err);
            }
          })()
        ]);
        
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
  // ✅ Слушаем изменения URL
  window.addEventListener('popstate', handleWalletReturn);
  
  // ✅ Запускаем инициализацию
  await initializeApp();
});

onUnmounted(() => {
  // ✅ Убираем обработчик при размонтировании
  window.removeEventListener('popstate', handleWalletReturn);
});
</script>

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