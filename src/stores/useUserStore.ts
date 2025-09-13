import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface TelegramUser {
  id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  photo_url?: string;
  language?: string;
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
  language: string; // Добавляем язык пользователя
}

export interface UserBalance {
  ton_balance: number;
  stars_balance: number;
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null);
  const telegramUser = ref<TelegramUser | null>(null);
  const balance = ref<UserBalance>({ ton_balance: 0, stars_balance: 0 });
  const currentLanguage = ref('ru'); // Язык по умолчанию

  const setUser = (userData: User) => {
    user.value = userData;
    // Устанавливаем язык из данных пользователя
    if (userData.language) {
      currentLanguage.value = userData.language;
    }
  };

  const setTelegramUser = (telegramData: TelegramUser) => {
    telegramUser.value = telegramData;
    // Устанавливаем язык из Telegram пользователя
    if (telegramData.language) {
      currentLanguage.value = telegramData.language;
    }
  };

  const setBalance = (newBalance: UserBalance) => {
    balance.value = newBalance;
  };

  // Метод для установки языка
  const setLanguage = async (lang: string) => {
    try {
      currentLanguage.value = lang;
      
      // Обновляем язык у пользователя, если он есть
      if (user.value) {
        user.value.language = lang;
      }
      
      // Сохраняем язык на сервере
      const { api } = await import('@/services/api');
      await api.post('/api/user/language', { language: lang });
      
      // Отправляем событие о смене языка
      window.dispatchEvent(new CustomEvent('language-changed', { 
        detail: { language: lang } 
      }));
      
      return true;
    } catch (error) {
      console.error('Failed to set language:', error);
      // Восстанавливаем предыдущий язык в случае ошибки
      if (user.value?.language) {
        currentLanguage.value = user.value.language;
      }
      throw error;
    }
  };

  // Метод для загрузки языка из БД
  const loadLanguage = async () => {
    try {
      const { api } = await import('@/services/api');
      const response = await api.get('/api/user/language');
      
      if (response.data.language) {
        currentLanguage.value = response.data.language;
        
        // Обновляем язык у пользователя, если он есть
        if (user.value) {
          user.value.language = response.data.language;
        }
      }
      
      return currentLanguage.value;
    } catch (error) {
      console.error('Failed to load language:', error);
      return currentLanguage.value;
    }
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
  
  const fetchBalance = async () => {
      try {
          const { api } = await import('@/services/api');
          const response = await api.get('/api/user/balance');
          
          // Обновляем локальное состояние
          setBalance(response.data);
          
          // Также обновляем у пользователя
          if (user.value) {
              user.value.ton_balance = response.data.ton_balance;
              user.value.stars_balance = response.data.stars_balance;
          }
      } catch (err) {
          console.error('Failed to fetch balance:', err);
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
      
      // Загружаем язык после получения данных пользователя
      await loadLanguage();
    } catch (err) {
      console.error('Failed to fetch user data:', err);
    }
  };

  const clearUser = () => {
    user.value = null;
    telegramUser.value = null;
    balance.value = { ton_balance: 0, stars_balance: 0 };
    currentLanguage.value = 'ru'; // Сбрасываем язык
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

  // Computed property для текущего языка
  const getCurrentLanguage = computed(() => currentLanguage.value);

  return {
    user,
    telegramUser,
    balance,
    currentLanguage: getCurrentLanguage, // Экспортируем как computed
    setUser,
    setTelegramUser,
    setBalance,
    setLanguage, // Добавляем метод установки языка
    loadLanguage, // Добавляем метод загрузки языка
    updateBalance,
    clearUser,
    fetchUserData,
    fetchBalance,
    syncBalance,
    getAvatarUrl,
    getDisplayName,
    getUsername
  };
});