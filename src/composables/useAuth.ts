import { ref } from 'vue';
import { useUserStore } from '@/stores/useUserStore.ts';
import { useTelegram } from './useTelegram';

export function useAuth() {
  const userStore = useUserStore();
  const { initTelegram } = useTelegram();
  const isAuthenticated = ref(false);

  const checkAuth = async () => {
    const token = localStorage.getItem('telegram_token');
    if (token && !userStore.user) {
      const success = await initTelegram(token);
      isAuthenticated.value = success;
      return success;
    }
    isAuthenticated.value = !!userStore.user;
    return isAuthenticated.value;
  };

  const logout = () => {
    userStore.clearUser();
    localStorage.removeItem('telegram_token');
    isAuthenticated.value = false;
  };

  return {
    isAuthenticated,
    checkAuth,
    logout
  };
}