<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'

const isTelegram = ref(false)
const isMounted = ref(false)

onMounted(() => {
  console.log('🚀 App mounted')
  
  if (window.Telegram?.WebApp) {
    isTelegram.value = true
    console.log('✅ Telegram detected')
    
    // Принудительно применяем стили
    document.documentElement.style.setProperty('--tg-theme-bg-color', '#ffffff')
    document.documentElement.style.setProperty('--tg-theme-text-color', '#222222')
    
    // Гарантируем видимость
    document.body.style.opacity = '1'
    document.body.style.visibility = 'visible'
  }
  
  isMounted.value = true
})
</script>

<template>
  <div id="app" :style="{ opacity: isMounted ? 1 : 0 }">
    <RouterView v-if="isMounted" />
    <div v-else class="loading">Загрузка...</div>
  </div>
</template>

<style>
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 18px;
}
</style>