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
  photo_url?: string;
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

  const fetchBalance = async () => {
    try {
      const { api } = await import('@/services/api');
      const response = await api.get('/api/user/balance');
      
      // ✅ ПРАВИЛЬНЫЙ ФОРМАТ - response.data содержит баланс
      setBalance(response.data);
    } catch (err) {
      console.error('Failed to fetch balance:', err);
    }
  };

  const fetchUserData = async () => {
    try {
      const { telegramService } = await import('@/services/telegram.service');
      const response = await telegramService.getUserData();
      setTelegramUser(response.user_data);
    } catch (err) {
      console.error('Failed to fetch user data:', err);
    }
  };

  const clearUser = () => {
    user.value = null;
    telegramUser.value = null;
    balance.value = { ton_balance: 0, stars_balance: 0 };
  };

  // Computed properties
  const getAvatarUrl = computed(() => {
    if (telegramUser.value?.photo_url) {
      return telegramUser.value.photo_url;
    }
    if (user.value?.photo_url) {
      return user.value.photo_url;
    }
    const username = telegramUser.value?.username || user.value?.username;
    if (username) {
      return `https://t.me/i/userpic/320/${username}.jpg`;
    }
    return '/src/assets/images/avatar.jpg';
  });

  const getDisplayName = computed(() => {
    if (telegramUser.value) {
      const firstName = telegramUser.value.first_name || '';
      const lastName = telegramUser.value.last_name || '';
      if (firstName || lastName) {
        return `${firstName} ${lastName}`.trim();
      }
    }
    if (user.value) {
      const firstName = user.value.first_name || '';
      const lastName = user.value.last_name || '';
      if (firstName || lastName) {
        return `${firstName} ${lastName}`.trim();
      }
    }
    const username = telegramUser.value?.username || user.value?.username;
    if (username) {
      return username;
    }
    return 'User';
  });

  const getUsername = computed(() => {
    return telegramUser.value?.username || user.value?.username || '';
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
    fetchUserData,
    fetchBalance,
    getAvatarUrl,
    getDisplayName,
    getUsername
  };
});