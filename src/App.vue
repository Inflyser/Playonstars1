<template>
  <div :class="['app', { 'tg-theme': isTelegram }]">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'

const isTelegram = ref(false)

onMounted(() => {
  // Проверяем что мы в Telegram
  if (window.Telegram?.WebApp) {
    isTelegram.value = true
    document.documentElement.style.setProperty('--tg-theme-bg-color', '#ffffff')
    document.documentElement.style.setProperty('--tg-theme-text-color', '#222222')
  }
})
</script>

<style>
.app {
  min-height: 100vh;
  transition: background-color 0.3s ease;
}

.tg-theme {
  background: var(--tg-theme-bg-color, #ffffff);
  color: var(--tg-theme-text-color, #222222);
}
</style>