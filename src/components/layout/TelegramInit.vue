<script setup lang="ts">
import { onMounted, ref, onUnmounted, watch } from 'vue';
import { useTelegram } from '@/composables/useTelegram';

import { useUserStore } from '@/stores/useUserStore';
import { useWalletStore } from '@/stores/useWalletStore';
import { useWebSocket } from '@/composables/useWebSocket';
import TGLoader from '@/components/ui/TGLoader.vue';
import AppLayout from '@/components/layout/AppLayout.vue';
import { initTelegramWebApp, isTelegramWebApp, openTelegramLink, getTelegramInitData } from '@/utils/telegram';


const { initTelegram, fetchUserData, fetchBalance, isLoading, error } = useTelegram();
const userStore = useUserStore();
const walletStore = useWalletStore();
const { connect: connectWebSocket } = useWebSocket();
const isInitialized = ref(false);
const initializationError = ref<string | null>(null);



const initializeApp = async () => {
  try {
    console.log('🚀 Запускаем инициализацию приложения...');
    
    // 1. Самое важное: инициализируем кошелек (он сам проверит возврат из кошелька)
    await walletStore.init();
    
    // 2. Если мы в Telegram — инициализируем данные пользователя
    const isTelegram = initTelegramWebApp();
    if (isTelegram && userStore.user) {
      await userStore.fetchBalance();
      await connectWebSocket();
    }
    
    isInitialized.value = true;
    console.log('✅ Приложение успешно инициализировано!');
    
  } catch (err) {
    console.error('❌ Ошибка инициализации:', err);
    error.value = 'Не удалось загрузить приложение';
  }
};

// ✅ Следим за изменениями авторизации для обновления данных
watch(() => userStore.user, (newUser) => {
  if (newUser && !isInitialized.value) {
    console.log('🔄 User data changed, updating...');
    fetchBalance().catch(err => console.error('Failed to update balance:', err));
  }
});


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