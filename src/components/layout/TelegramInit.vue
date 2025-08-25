<script setup lang="ts">
import { onMounted } from 'vue'
import { useTelegram } from '@/composables/useTelegram'

const { isWebApp, expandApp } = useTelegram()

onMounted(() => {
  if (isWebApp) {
    expandApp()
    
  }
})
</script>

<template>
  <div v-if="isWebApp" class="telegram-init">
    <!-- Инициализация Telegram Web App -->
  </div>
</template>