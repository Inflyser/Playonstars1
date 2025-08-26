<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/useUserStore'
import { useTelegram } from '@/composables/useTelegram'

const router = useRouter()
const userStore = useUserStore()
const { isWebApp, isInitialized } = useTelegram()
const isLoading = ref(true)

onMounted(async () => {
  console.log('App mounted, checking environment...')
  
  // Ждем инициализации Telegram
  const checkInit = () => {
    if (isInitialized.value) {
      console.log('Is Telegram WebApp:', isWebApp.value)
      
      if (isWebApp.value) {
        handleTelegramApp()
      } else {
        handleBrowser()
      }
      isLoading.value = false
    } else {
      setTimeout(checkInit, 100)
    }
  }
  
  checkInit()
})

const handleTelegramApp = async () => {
  console.log('Initializing Telegram app...')
  
  try {
    await userStore.initAuth()
    console.log('Auth successful')
    
    // Если на странице только для браузера - уходим
    if (window.location.pathname === '/telegram-only') {
      router.push('/')
    }
  } catch (error) {
    console.error('Auth failed:', error)
  }
}

const handleBrowser = () => {
  console.log('Regular browser detected')
  // Если не в Telegram и не на странице telegram-only - редирект
  if (window.location.pathname !== '/telegram-only') {
    console.log('Redirecting to telegram-only page')
    router.push('/telegram-only')
  }
}
</script>

<template>
  <router-view />
</template>