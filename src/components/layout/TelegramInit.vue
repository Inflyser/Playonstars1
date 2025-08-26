<template>
  <div v-if="!isInitialized">
    <TGLoader v-if="isLoading" />
    <div v-else-if="error" class="error-message">
      {{ error }}
      <button @click="retryInit" class="retry-btn">Retry</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useTelegram } from '@/composables/useTelegram';
import { initTelegramWebApp, getTelegramInitData } from '@/utils/telegram';
import TGLoader from '@/components/ui/TGLoader.vue';
import { useUserStore } from '@/stores/useUserStore';

// Используем ВСЕ методы из useTelegram
const { initTelegram, fetchUserData, fetchBalance, isLoading, error } = useTelegram();
const isInitialized = ref(false);
const userStore = useUserStore();

const retryInit = async () => {
  isInitialized.value = false;
  error.value = null;
  await initializeApp();
};

const initializeApp = async () => {
  // Инициализируем Telegram WebApp
  const isTelegram = initTelegramWebApp();
  
  if (isTelegram) {
    const initData = getTelegramInitData();
    
    if (initData) {
      console.log('InitData found, authenticating...');
      const success = await initTelegram(initData);
      
      if (success) {
        isInitialized.value = true;
        // ЗАГРУЖАЕМ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ - это было пропущено!
        await fetchUserData();
        await fetchBalance();
        console.log('Telegram auth successful');
      } else {
        console.error('Telegram auth failed');
      }
    } else {
      console.warn('No initData available');
      isInitialized.value = true;
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
</style>