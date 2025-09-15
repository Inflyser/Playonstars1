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

  const updateBalance = async (currency: 'ton' | 'stars', amount: number, operation: 'add' | 'set' = 'add') => {
      if (user.value) {
          // 1. Локальное обновление
          if (currency === 'ton') {
              if (operation === 'add') {
                  user.value.ton_balance += amount;
                  balance.value.ton_balance += amount;
              } else {
                  user.value.ton_balance = amount;
                  balance.value.ton_balance = amount;
              }
          } else {
              if (operation === 'add') {
                  user.value.stars_balance += amount;
                  balance.value.stars_balance += amount;
              } else {
                  user.value.stars_balance = amount;
                  balance.value.stars_balance = amount;
              }
          }
          
          // 2. Синхронизация с сервером
          try {
              const { api } = await import('@/services/api');
              await api.post('/api/user/update-balance', {
                  currency: currency,
                  amount: amount,
                  operation: operation
              });
          } catch (error) {
              console.error('Balance update failed:', error);
              // Если сервер недоступен, оставляем локальные изменения
          }
      }
  };


  const forceRefreshBalance = async (): Promise<UserBalance | null> => {
    try {
      const { api } = await import('@/services/api');

      // Добавляем timestamp для избежания кэширования
      const timestamp = new Date().getTime();
      const response = await api.get(`/api/user/balance?force=${timestamp}`);

      // Обновляем локальное состояние
      setBalance(response.data);

      if (user.value) {
        user.value.ton_balance = response.data.ton_balance;
        user.value.stars_balance = response.data.stars_balance;
      }

      // Сохраняем в localStorage для fallback
      localStorage.setItem('user_balance', JSON.stringify(response.data));
      localStorage.setItem('balance_last_updated', timestamp.toString());

      return response.data;
    } catch (err) {
      console.error('Force refresh balance failed:', err);

      // Пытаемся использовать кэшированные данные
      const cachedBalance = localStorage.getItem('user_balance');
      if (cachedBalance) {
        const balanceData = JSON.parse(cachedBalance);
        setBalance(balanceData);
        return balanceData;
      }

      return null;
    }
  };
  
  const fetchBalance = async (force: boolean = false): Promise<UserBalance | null> => {
    try {
      const { api } = await import('@/services/api');
      
      let response;
      if (force) {
        const timestamp = new Date().getTime();
        response = await api.get(`/api/user/balance?force=${timestamp}`);
      } else {
        response = await api.get('/api/user/balance');
      }
      
      // Обновляем локальное состояние
      setBalance(response.data);
      
      if (user.value) {
        user.value.ton_balance = response.data.ton_balance;
        user.value.stars_balance = response.data.stars_balance;
      }
      
      // Сохраняем время последнего обновления
      localStorage.setItem('balance_last_updated', new Date().getTime().toString());
      
      return response.data;
    } catch (err) {
      console.error('Failed to fetch balance:', err);
      
      // Fallback: используем кэшированные данные
      const cached = localStorage.getItem('user_balance');
      if (cached) {
        const balanceData = JSON.parse(cached);
        setBalance(balanceData);
        return balanceData;
      }
      
      return null;
    }
  };

  const syncBalance = async () => {
     try {
         const { api } = await import('@/services/api');
         const response = await api.post('/api/user/sync-balance');
         
         setBalance(response.data);
         if (user.value) {
             user.value.ton_balance = response.data.ton_balance;
             user.value.stars_balance = response.data.stars_balance;
         }
         
         return response.data;
     } catch (error) {
         console.error('Balance sync failed:', error);
         return null;
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
    syncBalance,
    getAvatarUrl,
    getDisplayName,
    getUsername,
    forceRefreshBalance
  };
});