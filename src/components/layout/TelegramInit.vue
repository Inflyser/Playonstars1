<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useTelegram } from '@/composables/useTelegram';
import { useUserStore } from '@/stores/useUserStore';
import { initTelegramWebApp, getTelegramInitData } from '@/utils/telegram';
import TGLoader from '@/components/ui/TGLoader.vue';

const { initTelegram, isLoading, error } = useTelegram();
const userStore = useUserStore();
const isInitialized = ref(false);

onMounted(async () => {
  // Инициализируем Telegram WebApp
  const isTelegram = initTelegramWebApp();
  
  if (isTelegram) {
    const initData = getTelegramInitData();
    
    if (initData) {
      console.log('InitData found, authenticating...');
      const success = await initTelegram(initData);
      
      if (success) {
        isInitialized.value = true;
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
});
</script>