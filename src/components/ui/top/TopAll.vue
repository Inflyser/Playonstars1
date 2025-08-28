<template>
  <div class="top-all">
    <div class="top-list">
      <div class="top-item header">
        <div class="rank">#</div>
        <div class="user">Игрок</div>
        <div class="balance">Звезды</div>
      </div>
      
      <div 
        v-for="user in topStore.topUsers" 
        :key="user.id" 
        class="top-item"
        :class="{ 'current-user': isCurrentUser(user.telegram_id) }"
      >
        <div class="rank">
          <span class="rank-number">{{ user.rank }}</span>
        </div>
        
        <div class="user-info">
          <img 
            :src="user.photo_url" 
            :alt="topStore.getUserDisplayName(user)"
            class="user-avatar"
            @error="handleAvatarError"
          />
          <span class="user-name">{{ topStore.getUserDisplayName(user) }}</span>
        </div>
        
        <div class="balance">
          {{ formatStars(user.stars_balance) }}
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
  background: var(--tg-theme-secondary-bg-color, #1a1a2e);
  border-radius: 12px;
  overflow: hidden;
}

.top-item {
  display: grid;
  grid-template-columns: 60px 1fr 100px;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--tg-theme-hint-color, #2d2d4d);
}

.top-item.header {
  background: var(--tg-theme-button-color, #7e57c2);
  color: var(--tg-theme-button-text-color, #ffffff);
  font-weight: 600;
}

.top-item:last-child {
  border-bottom: none;
}

.top-item.current-user {
  background: rgba(126, 87, 194, 0.1);
  border-left: 4px solid var(--tg-theme-button-color, #7e57c2);
}

.rank {
  text-align: center;
  font-weight: 600;
}

.rank-number {
  display: inline-block;
  width: 30px;
  height: 30px;
  line-height: 30px;
  border-radius: 50%;
  background: var(--tg-theme-button-color, #7e57c2);
  color: var(--tg-theme-button-text-color, #ffffff);
}

.top-item.header .rank-number {
  background: transparent;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 500;
  color: var(--tg-theme-text-color, #ffffff);
}

.balance {
  text-align: right;
  font-weight: 600;
  color: var(--tg-theme-button-color, #7e57c2);
}
</style>