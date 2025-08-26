<script setup lang="ts">
import { onMounted, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '@/composables/useTelegram'
import { useUserStore } from '@/stores/useUserStore'

const router = useRouter()
const { isWebApp, isInitialized } = useTelegram()
const userStore = useUserStore()
const isLoading = ref(true)

// Ждем инициализации Telegram
watch(isInitialized, async (initialized) => {
  if (initialized) {
    await checkTelegramAccess()
    if (isWebApp.value) {
      await userStore.initAuth()
    }
    isLoading.value = false
  }
})

const checkTelegramAccess = async () => {
  const currentPath = router.currentRoute.value.path
  
  if (!isWebApp.value && currentPath !== '/telegram-only') {
    await router.push('/telegram-only')
  }
  
  if (isWebApp.value && currentPath === '/telegram-only') {
    await router.push('/')
  }
}
console.log('App mounted - start') // ← ДОБАВЬТЕ

onMounted(async () => {
  console.log('onMounted called') // ← ДОБАВЬТЕ
  
  setTimeout(async () => {
    console.log('Timeout started') // ← ДОБАВЬТЕ
    
    const isWebApp = !!window.Telegram?.WebApp
    console.log('Is Web App:', isWebApp) // ← ДОБАВЬТЕ
    
    if (isWebApp) {
      console.log('Telegram Web App detected') // ← ДОБАВЬТЕ
      window.Telegram.WebApp.expand()
      await userStore.initAuth()
      if (window.location.pathname === '/telegram-only') {
        router.push('/')
      }
    } else {
      console.log('Regular browser detected') // ← ДОБАВЬТЕ
      if (window.location.pathname !== '/telegram-only') {
        router.push('/telegram-only')
      }
    }
    
    isLoading.value = false
    console.log('Loading finished') // ← ДОБАВЬТЕ
  }, 500)
})
</script>

<template>
  <div v-if="isLoading" class="loading">
    Загрузка...
  </div>
  <router-view v-else />
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