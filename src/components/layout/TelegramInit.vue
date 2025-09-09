<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useTelegram } from '@/composables/useTelegram';
import { initTelegramWebApp, getTelegramInitData } from '@/utils/telegram';
import { useUserStore } from '@/stores/useUserStore';
import { useWalletStore } from '@/stores/useWalletStore';
import { useWebSocket } from '@/composables/useWebSocket';
import TGLoader from '@/components/ui/TGLoader.vue';
import AppLayout from '@/components/layout/AppLayout.vue';

const { initTelegram, fetchUserData, fetchBalance, isLoading, error } = useTelegram();
const userStore = useUserStore();
const walletStore = useWalletStore();
const { connect: connectWebSocket } = useWebSocket();
const isInitialized = ref(false);
const initializationError = ref<string | null>(null);



const retryInit = async () => {
  console.log('🔄 Retrying initialization...');
  isInitialized.value = false;
  initializationError.value = null;
  error.value = null;
  await initializeApp();
};

const initializeApp = async () => {
  console.log('🔐 Starting application initialization...');
  
  try {
    const isTelegram = initTelegramWebApp();
    console.log('📱 Is Telegram environment:', isTelegram);

    // 1. ✅ Инициализируем TonConnect
    console.log('🔗 Initializing TonConnect...');
    await walletStore.init();

    // 2. ✅ Инициализируем Telegram (если в Telegram) - ЭТО ВАЖНО!
    if (isTelegram) {
      const initData = getTelegramInitData();
      console.log('📋 InitData available:', !!initData);
      
      if (initData) {
        console.log('🔐 Authenticating with Telegram...');
        const authSuccess = await initTelegram(initData);
        
        if (!authSuccess) {
          throw new Error('Telegram authentication failed');
        }
      }
    }

    // 3. ✅ Параллельно загружаем пользовательские данные (если авторизованы)
    const loadPromises = [];
    
    if (userStore.user || isTelegram) {
      loadPromises.push(
        fetchUserData().catch(err => 
          console.error('Failed to load user data:', err)
        ),
        fetchBalance().catch(err => 
          console.error('Failed to load balance:', err)
        )
      );
    }

    // 4. ✅ Подключаем WebSocket для реальных обновлений
    if (isTelegram) {
      loadPromises.push(
        connectWebSocket().catch(err =>
          console.error('Failed to connect WebSocket:', err)
        )
      );
    }

    await Promise.all(loadPromises);

    isInitialized.value = true;
    console.log('🎉 Application fully initialized');

  } catch (err) {
    console.error('❌ Initialization failed:', err);
    initializationError.value = err instanceof Error ? err.message : 'Unknown error';
  }
};

onMounted(() => {
  initializeApp();
});
</script>

<template>
  <div class="telegram-init-container">
    <!-- Показываем загрузчик/ошибку пока не инициализировано -->
    <div v-if="!isInitialized" class="init-status">
      <TGLoader v-if="isLoading && !initializationError" />
      
      <div v-else-if="initializationError" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>Initialization Failed</h3>
        <p>{{ initializationError }}</p>
        <button @click="retryInit" class="retry-btn">Try Again</button>
      </div>
      
      <div v-else class="loading-state">
        <div class="loading-spinner"></div>
        <p>Initializing application...</p>
      </div>
    </div>
    
    <!-- После инициализации показываем основное приложение -->
    <AppLayout v-else>
      <RouterView />
    </AppLayout>
  </div>
</template>

<style scoped>
.telegram-init-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.init-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

.error-state {
  text-align: center;
  color: #ff6b6b;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retry-btn {
  margin-top: 16px;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.loading-state {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>