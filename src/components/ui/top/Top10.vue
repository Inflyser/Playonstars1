<template>
  <div class="top-all">
    <div class="top-list">
      <div 
        v-for="user in top10Users" 
        :key="user.id" 
        class="top-item"
        :class="{ 'current-user': isCurrentUser(user.telegram_id) }"
      >
        <div class="rank">
          <span class="rank-number">#{{ user.rank }}</span>
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
        
        <div class="balance-container">
          <img src="/src/assets/images/coin.svg" alt="Stars" class="currency-icon" />
          <span class="balance">{{ formatStars(user.stars_balance) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useTopStore } from '@/stores/useTopStore';
import { useUserStore } from '@/stores/useUserStore';

const topStore = useTopStore();
const userStore = useUserStore();


const top10Users = computed(() => {
  return topStore.topUsers.slice(0, 10);
});

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
/* Стили такие же как в TopAll.vue */
</style>