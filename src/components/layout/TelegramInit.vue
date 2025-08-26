<template>
  <div v-if="!isInitialized">
    <TGLoader v-if="isLoading" />
    <div v-else-if="error" class="error-message">
      {{ error }}
      <button @click="retryInit" class="retry-btn">Retry</button>
    </div>
    
    <div v-if="connectionStatus" class="connection-status">
      Backend: {{ connectionStatus }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useTelegram } from '@/composables/useTelegram';
import { useUserStore } from '@/stores/useUserStore';
import { checkBackendConnection, checkAuthStatus } from '@/services/healthCheck';
import TGLoader from '@/components/ui/TGLoader.vue';

const { initTelegram, fetchUserData, fetchBalance, isLoading, error } = useTelegram();
const userStore = useUserStore();
const isInitialized = ref(false);
const connectionStatus = ref<string>('checking...');

const checkConnection = async () => {
  const isConnected = await checkBackendConnection();
  connectionStatus.value = isConnected ? 'connected' : 'disconnected';
  return isConnected;
};

const retryInit = async () => {
  isInitialized.value = false;
  error.value = null;
  await initializeApp();
};

const initializeApp = async () => {
  // Сначала проверяем подключение к бекенду
  const isConnected = await checkConnection();
  if (!isConnected) {
    error.value = 'Cannot connect to backend server';
    return;
  }

  // Проверяем, есть ли сохраненный токен
  const token = localStorage.getItem('telegram_token');
  const hasAuth = token ? await checkAuthStatus() : false;

  if (hasAuth) {
    // Если есть валидная сессия, загружаем данные
    await fetchUserData();
    await fetchBalance();
    isInitialized.value = true;
    return;
  }

  // Если в Telegram - пытаемся аутентифицироваться
  if (window.Telegram?.WebApp) {
    const initData = window.Telegram.WebApp.initData;
    if (initData) {
      const success = await initTelegram(initData);
      if (success) {
        isInitialized.value = true;
        await fetchUserData();
        await fetchBalance();
      }
    }
  } else {
    console.log('Running in browser mode');
    isInitialized.value = true;
  }
};

onMounted(async () => {
  await initializeApp();
});
</script>

<style scoped>
.error-message {
  color: #ff4757;
  padding: 1rem;
  text-align: center;
}

.retry-btn {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background: #007aff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.connection-status {
  position: fixed;
  top: 10px;
  right: 10px;
  padding: 0.5rem;
  background: #333;
  color: white;
  border-radius: 4px;
  font-size: 0.8rem;
  z-index: 1000;
}
</style>