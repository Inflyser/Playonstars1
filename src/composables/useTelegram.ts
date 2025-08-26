import { ref } from 'vue';
import { telegramService } from '@/services/telegram.service.ts';
import { useUserStore } from '@/stores/useUserStore.ts';

export function useTelegram() {
  const userStore = useUserStore();
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const initTelegram = async (initData: string) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await telegramService.authTelegram(initData);
      
      if (response.status === 'success') {
        userStore.setUser(response.user);
        localStorage.setItem('telegram_token', initData);
        return true;
      }
      
      return false;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Authentication failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchUserData = async () => {
    try {
      const response = await telegramService.getUserData();
      userStore.setTelegramUser(response.user_data);
    } catch (err) {
      console.error('Failed to fetch user data:', err);
    }
  };

  const fetchBalance = async () => {
    try {
      const balance = await telegramService.getBalance();
      userStore.setBalance(balance);
    } catch (err) {
      console.error('Failed to fetch balance:', err);
    }
  };

  return {
    initTelegram,
    fetchUserData,
    fetchBalance,
    isLoading,
    error
  };
}