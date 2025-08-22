<template>
  <div id="app">
    <RouterView v-if="isMounted" />
    <div v-else class="loading">
      Загрузка... {{ loadState }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'

const isMounted = ref(false)
const loadState = ref('starting')

onMounted(() => {
  console.log('🔄 App.vue mounted')
  loadState.value = 'checking telegram'
  
  if (window.Telegram?.WebApp) {
    console.log('✅ Telegram WebApp found')
    const webApp = window.Telegram.WebApp
    webApp.expand()
    webApp.ready()
    loadState.value = 'telegram ready'
  } else {
    console.log('🌐 Running in browser')
    loadState.value = 'browser mode'
  }
  
  isMounted.value = true
  loadState.value = 'complete'
})
</script>

<style>
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 18px;
  color: #000;
  background: #fff;
}
</style>