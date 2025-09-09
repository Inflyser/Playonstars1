<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/useUserStore';
import { useWalletStore } from '@/stores/useWalletStore';
import { useWebSocket } from '@/composables/useWebSocket';
import TGLoader from '@/components/ui/TGLoader.vue';
import AppLayout from '@/components/layout/AppLayout.vue';
import { initTelegramWebApp } from '@/utils/telegram';

const userStore = useUserStore();
const walletStore = useWalletStore();
const { connect: connectWebSocket } = useWebSocket();
const isInitialized = ref(false);
const initializationError = ref<string | null>(null);

const initializeApp = async () => {
  try {
    console.log('🚀 Запускаем инициализацию приложения...');
    
    // 1. Инициализируем кошелек
    await walletStore.init();
    
    // 2. Проверяем, находимся ли мы в Telegram
    const isTelegram = initTelegramWebApp();
    console.log('📱 Is Telegram environment:', isTelegram);
    
    // 3. В Telegram среде: загружаем данные и подключаем WebSocket
    if (isTelegram) {
      try {
        // Загружаем данные пользователя
        await userStore.fetchUserData();
        await userStore.fetchBalance();
        
        console.log('✅ Данные пользователя загружены');
      } catch (err) {
        console.error('❌ Ошибка загрузки данных пользователя:', err);
      }
      
      // ВАЖНО: ПОДКЛЮЧАЕМ WEBSOCKET В ЛЮБОМ СЛУЧАЕ, ДАЖЕ ЕСЛИ ДАННЫЕ НЕ ЗАГРУЗИЛИСЬ
      try {
        await connectWebSocket();
        console.log('✅ WebSocket подключен');
      } catch (wsError) {
        console.error('❌ Ошибка подключения WebSocket:', wsError);
      }
    }
    
    isInitialized.value = true;
    console.log('✅ Приложение успешно инициализировано!');
    
  } catch (err) {
    console.error('❌ Критическая ошибка инициализации:', err);
    initializationError.value = 'Не удалось загрузить приложение';
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
      <!-- УБИРАЕМ isLoading ИЗ УСЛОВИЯ -->
      <TGLoader v-if="!initializationError" />
      
      <div v-else-if="initializationError" class="error-state">
        <div class="error-icon">⚠️</div>
        <h3>Initialization Failed</h3>
        <p>{{ initializationError }}</p>
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