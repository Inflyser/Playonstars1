<template>
  <div class="home">
    <TelegramHeader />
    <div class="top-my">
      <div class="placeholder">
        <img src="@/assets/images/coin.svg" alt="Star" class="placeholder-icon" />
        <h3>Pvp-режим</h3>
        <p>Страница в разработке</p>
      </div>
    </div>
    <BottomNavigation />
  </div>
</template>

<script setup lang="ts">
import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import TelegramHeader from '@/components/layout/TelegramHeader.vue'
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(to right, #1B152F, #180A24);
  padding-bottom: 80px;
}

.top-my {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.placeholder {
  text-align: center;
  color: var(--tg-theme-hint-color, #888888);
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 1rem;
  opacity: 0.5;
}

h3 {
  margin-bottom: 0.5rem;
  color: var(--tg-theme-text-color, #ffffff);
}

p {
  color: var(--tg-theme-hint-color, #888888);
}
</style>