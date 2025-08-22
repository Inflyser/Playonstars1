<template>
  <div class="home" style="background: red; color: white; padding: 20px;">
    <h1>🎮 TEST - Play on Stars</h1>
    <p>Если это видно - значит компонент работает!</p>
    <button @click="testClick" style="padding: 10px; background: blue; color: white;">
      Test Button
    </button>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

const testClick = () => {
  console.log('✅ Button clicked!')
  alert('Кнопка работает!')
}

onMounted(() => {
  console.log('🏠 HomeView mounted')
  // Принудительно показываем элемент
  const homeEl = document.querySelector('.home')
  if (homeEl) {
    (homeEl as HTMLElement).style.display = 'block',
    (homeEl as HTMLElement).style.opacity = '1',
    (homeEl as HTMLElement).style.visibility = 'visible'
  }
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: block !important;
  opacity: 1 !important;
  visibility: visible !important;
}
</style>