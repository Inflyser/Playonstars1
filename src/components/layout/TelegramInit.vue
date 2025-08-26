<template>
  <div v-if="!isInitialized">
    <TGLoader v-if="isLoading" />
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useTelegram } from '@/composables/useTelegram';
import { useUserStore } from '@/stores/useUserStore';
import TGLoader from '@/components/ui/TGLoader.vue';

const { initTelegram, isLoading, error } = useTelegram();
const userStore = useUserStore();
const isInitialized = ref(false);

onMounted(async () => {
  // Проверяем, есть ли уже данные Telegram
  if (window.Telegram?.WebApp) {
    const initData = window.Telegram.WebApp.initData;
    
    if (initData) {
      const success = await initTelegram(initData);
      if (success) {
        isInitialized.value = true;
        
        // Загружаем дополнительные данные
        userStore.fetchUserData();
        userStore.fetchBalance();
      }
    }
  } else {
    console.warn('Telegram WebApp not detected');
    isInitialized.value = true;
  }
});
</script>