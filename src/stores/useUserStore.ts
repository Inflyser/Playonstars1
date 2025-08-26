import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface TelegramUser {
  id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  photo_url?: string;
}

export interface User {
  id: number;
  telegram_id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  ton_balance: number;
  stars_balance: number;
}

export interface UserBalance {
  ton_balance: number;
  stars_balance: number;
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null);
  const telegramUser = ref<TelegramUser | null>(null);
  const balance = ref<UserBalance>({ ton_balance: 0, stars_balance: 0 });

  const setUser = (userData: User) => {
    user.value = userData;
  };

  const setTelegramUser = (telegramData: TelegramUser) => {
    telegramUser.value = telegramData;
  };

  const setBalance = (newBalance: UserBalance) => {
    balance.value = newBalance;
  };

  const updateBalance = (currency: 'ton' | 'stars', amount: number) => {
    if (user.value) {
      if (currency === 'ton') {
        user.value.ton_balance += amount;
        balance.value.ton_balance += amount;
      } else {
        user.value.stars_balance += amount;
        balance.value.stars_balance += amount;
      }
    }
  };

  const clearUser = () => {
    user.value = null;
    telegramUser.value = null;
    balance.value = { ton_balance: 0, stars_balance: 0 };
  };

  // Методы для получения данных
  const fetchUserData = async () => {
    try {
      const { telegramService } = await import('@/services/telegram.service');
      const response = await telegramService.getUserData();
      setTelegramUser(response.user_data);
    } catch (err) {
      console.error('Failed to fetch user data:', err);
    }
  };

  const fetchBalance = async () => {
    try {
      const { telegramService } = await import('@/services/telegram.service');
      const balanceData = await telegramService.getBalance();
      setBalance(balanceData);
    } catch (err) {
      console.error('Failed to fetch balance:', err);
    }
  };

  // Computed properties
  const getAvatarUrl = computed(() => {
    return telegramUser.value?.photo_url || '/src/assets/images/avatar.jpg';
  });

  const getDisplayName = computed(() => {
    if (telegramUser.value) {
      return telegramUser.value.first_name + 
             (telegramUser.value.last_name ? ` ${telegramUser.value.last_name}` : '');
    }
    return user.value?.username || 'User';
  });

  return {
    user,
    telegramUser,
    balance,
    setUser,
    setTelegramUser,
    setBalance,
    updateBalance,
    clearUser,
    fetchUserData, // ✅ Добавляем в возвращаемый объект
    fetchBalance,  // ✅ Добавляем в возвращаемый объект
    getAvatarUrl,
    getDisplayName
  };
});