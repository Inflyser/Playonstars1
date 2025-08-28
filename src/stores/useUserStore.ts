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
    
    // ✅ ИСПРАВЛЕННАЯ ФУНКЦИЯ - убрана сложная логика
    if (userData.photo_url && telegramUser.value && !telegramUser.value.photo_url) {
      telegramUser.value.photo_url = userData.photo_url;
    }
  }; // ✅ Закрывающая скобка здесь!

  const setTelegramUser = (telegramData: TelegramUser) => {
    telegramUser.value = telegramData;
    
    // ✅ Упрощенная версия
    if (user.value && telegramData.photo_url && !user.value.photo_url) {
      user.value.photo_url = telegramData.photo_url;
    }
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
    // 1. Пробуем из Telegram данных
    if (telegramUser.value?.photo_url) {
      return telegramUser.value.photo_url;
    }
    
    // 2. Пробуем из основного пользователя
    if (user.value?.photo_url) {
      return user.value.photo_url;
    }
    
    // 3. Генерируем на основе username
    const username = telegramUser.value?.username || user.value?.username;
    if (username) {
      return `https://t.me/i/userpic/320/${username}.jpg`;
    }
    
    // 4. Fallback на дефолтную аватарку
    return '/src/assets/images/avatar.jpg';
  });

  const getDisplayName = computed(() => {
    // 1. Сначала username (приоритет)
    const username = telegramUser.value?.username || user.value?.username;
    if (username) {
      return username;
    }
    
    // 2. Затем имя + фамилия
    if (telegramUser.value) {
      const firstName = telegramUser.value.first_name || '';
      const lastName = telegramUser.value.last_name || '';
      if (firstName || lastName) {
        return `${firstName} ${lastName}`.trim();
      }
    }
    
    // 3. Fallback
    return 'User';
  });

  // ✅ Добавляем computed для username отдельно
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