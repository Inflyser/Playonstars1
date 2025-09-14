<template>
  <div class="top-all">
    <div class="top-list">
      <div 
        v-for="(user, index) in myTopUsers" 
        :key="user.id" 
        class="top-item"
        :class="{ 'current-user': isCurrentUser(user.telegram_id) }"
      >
        <div class="rank">
          <span class="rank-number">#{{ index + 1 }}</span>
        </div>
        
        <div class="user-info">
          <img 
            :src="getSmartAvatarUrl(user)"
            :alt="getUserDisplayName(user)"
            class="user-avatar"
            @error="handleAvatarError"
          />
          <span class="user-name">{{ getUserDisplayName(user) }}</span>
        </div>
        
        <div class="balance-container">
          <img src="/src/assets/images/coin.svg" alt="Stars" class="currency-icon" />
          <span class="balance">{{ formatStars(user.stars_balance) }}</span>
        </div>
      </div>

      <!-- Сообщения о состоянии -->
      <div v-if="loading" class="loading">
        Загрузка рефералов...
      </div>

      <div v-if="!loading && myTopUsers.length === 0" class="no-referrals">
        <p>У вас пока нет рефералов</p>
        <p class="hint">Приглашайте друзей и получайте бонусы!</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/stores/useUserStore';
import { api } from '@/services/api';

const userStore = useUserStore();
const loading = ref(false);
const referrals = ref<any[]>([]);

// Комбинированный список: я + мои рефералы
const myTopUsers = computed(() => {
  const result = [];
  
  // Добавляем текущего пользователя первым
  if (userStore.user) {
    result.push({
      ...userStore.user,
      rank: 1 // Будет перезаписано индексом
    });
  }
  
  // Добавляем рефералов
  referrals.value.forEach(ref => {
    result.push(ref);
  });
  
  // Сортируем по балансу (как в общем топе)
  return result.sort((a, b) => b.stars_balance - a.stars_balance);
});

const getSmartAvatarUrl = (user: any) => {
  // Если есть нормальный photo_url - используем
  if (user.photo_url && !user.photo_url.includes('/320/null')) {
    return user.photo_url;
  }
  
  // Генерируем через username если есть
  if (user.username) {
    return `https://t.me/i/userpic/320/${user.username}.jpg`;
  }
  
  // Дефолтная аватарка
  return '/src/assets/images/avatar.jpg';
};

const getUserDisplayName = (user: any) => {
  if (user.first_name && user.last_name) {
    return `${user.first_name} ${user.last_name}`;
  }
  if (user.first_name) {
    return user.first_name;
  }
  if (user.username) {
    return `@${user.username}`;
  }
  return `User #${user.telegram_id}`;
};

const isCurrentUser = (telegramId: number) => {
  return userStore.user?.telegram_id === telegramId;
};

const formatStars = (balance: number) => {
  return new Intl.NumberFormat('ru-RU').format(balance);
};

const handleAvatarError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.src = '/src/assets/images/avatar.jpg';
};

const fetchMyReferrals = async () => {
  try {
    loading.value = true;
    const response = await api.get('/api/user/my-referrals');
    referrals.value = response.data.referrals || [];
  } catch (error) {
    console.error('Ошибка загрузки рефералов:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  if (userStore.user) {
    fetchMyReferrals();
  }
});
</script>

<style scoped>
.top-all {
  padding: 1rem 0;
}

.top-list {
  background: transparent;
  border-radius: 12px;
  overflow: hidden;
}

.top-item {
  margin-left: 10px;
  margin-right: 10px;
  background-color: #1D1131;
  display: grid;
  grid-template-columns: 50px 1fr auto;
  align-items: center;
  padding: 0.75rem 1rem;
  margin-bottom: 8px;
  border-radius: 8px;
  border: 1px solid #25213C; 
}

.top-item:last-child {
  margin-bottom: 0;
}

.top-item.current-user {
  border-left: 3px solid #7e57c2;
}

.rank {
  text-align: center;
  font-weight: 600;
  font-size: 1.1rem;
}

.rank-number {
  display: inline-block;
  min-width: 25px;
  text-align: center;
  font-weight: bold;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 500;
  color: #ffffff;
  font-size: 0.95rem;
}

.balance-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(126, 87, 194, 0.15);
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
}

.currency-icon {
  width: 18px;
  height: 18px;
}

.balance {
  font-weight: 700;
  color: #7e57c2;
  font-size: 0.95rem;
}

/* Адаптивность для мобильных */
@media (max-width: 480px) {
  .top-item {
    grid-template-columns: 40px 1fr auto;
    padding: 0.6rem 0.8rem;
  }
  
  .user-avatar {
    width: 32px;
    height: 32px;
  }
  
  .user-name {
    font-size: 0.9rem;
  }
  
  .balance-container {
    padding: 0.3rem 0.6rem;
  }
  
  .currency-icon {
    width: 16px;
    height: 16px;
  }
  
  .balance {
    font-size: 0.9rem;
  }
  
  .rank {
    font-size: 1rem;
  }
}
</style>