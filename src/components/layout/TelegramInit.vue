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
  <HomeView v-else>
    <RouterView />
  </HomeView>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useTelegram } from '@/composables/useTelegram';
import { initTelegramWebApp, getTelegramInitData } from '@/utils/telegram';
import TGLoader from '@/components/ui/TGLoader.vue';
import HomeView from '@/views/HomeView.vue';
import { useUserStore } from '@/stores/useUserStore';

const { initTelegram, fetchUserData, fetchBalance, isLoading, error } = useTelegram();
const userStore = useUserStore();
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
        console.log('📦 Loading user data...');
        await fetchUserData();
        console.log('💰 Loading balance...');
        await fetchBalance();
        isInitialized.value = true;
        console.log('🎉 App fully initialized');
      } else {
        console.error('❌ Telegram auth failed');
      }
    } else {
      console.warn('⚠️ No initData available');
      isInitialized.value = true; // Все равно продолжаем
    }
  } else {
    console.log('🌐 Running in browser mode');
    isInitialized.value = true; // Продолжаем в браузере
  }
};

onMounted(async () => {
  await initializeApp();
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
  background: var(--tg-theme-button-color, #007aff);
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