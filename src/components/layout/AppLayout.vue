<template>
  <div class="app-layout">
    <TelegramHeader v-if="showHeader" />
    <main class="main-content">
      <slot></slot>
    </main>
    <BottomNavigation v-if="showNavigation" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import TelegramHeader from './TelegramHeader.vue';
import BottomNavigation from './BottomNavigation.vue';

const route = useRoute();

// Показывать header на всех страницах кроме некоторых
const showHeader = computed(() => {
  return !route.meta.hideHeader;
});

// Показывать навигацию на всех страницах кроме некоторых
const showNavigation = computed(() => {
  return !route.meta.hideNavigation;
});
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--tg-theme-bg-color, #ffffff);
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  overflow-y: auto;
}
</style>