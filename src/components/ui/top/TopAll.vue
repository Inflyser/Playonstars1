<template>
  <div class="top-all">
    <div class="top-list">
      <div 
        v-for="user in topStore.topUsers" 
        :key="user.id" 
        class="top-item"
        :class="{ 'current-user': isCurrentUser(user.telegram_id) }"
      >
        <div class="rank">
          <span class="rank-number">#{{ user.rank }}</span>
        </div>
        
        <div class="user-info">
          <img 
            :src="getSmartAvatarUrl(user)"
            :alt="topStore.getUserDisplayName(user)"
            class="user-avatar"
            @error="handleAvatarError"
          />
          <span class="user-name">{{ topStore.getUserDisplayName(user) }}</span>
        </div>
        
        <div class="balance-container">
          <img src="/src/assets/images/coin.svg" alt="Stars" class="currency-icon" />
          <span class="balance">{{ formatStars(user.stars_balance) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import { onMounted } from 'vue';
import { useTopStore } from '@/stores/useTopStore';
import { useUserStore } from '@/stores/useUserStore';

const topStore = useTopStore();
const userStore = useUserStore();

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

onMounted(() => {
  topStore.fetchTopUsers(100);
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