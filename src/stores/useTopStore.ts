import { defineStore } from 'pinia';
import { ref } from 'vue';
import { topService, type TopUser } from '@/services/top.service';

export const useTopStore = defineStore('top', () => {
  const topUsers = ref<TopUser[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const fetchTopUsers = async (limit: number = 100) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      const response = await topService.getTopUsers(limit);
      topUsers.value = response.users;
      
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load top users';
      console.error('Error fetching top users:', err);
    } finally {
      isLoading.value = false;
    }
  };

  // ✅ ДОБАВЛЯЕМ эту функцию!
  const getUserDisplayName = (user: TopUser): string => {
    if (user.first_name) {
      return user.first_name + (user.last_name ? ` ${user.last_name}` : '');
    }
    return user.username || 'User';
  };

  // Добавляем метод для получения топа рефералов (заглушка)
  const fetchReferralTop = async () => {
    try {
      isLoading.value = true;
      // Заглушка - возвращаем пустой массив
      topUsers.value = [];
    } catch (err: any) {
      error.value = 'Referral top is not available yet';
    } finally {
      isLoading.value = false;
    }
  };

  return {
    topUsers,
    isLoading,
    error,
    fetchTopUsers,
    fetchReferralTop,
    getUserDisplayName // ✅ Теперь она есть!
  };
});