<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/useUserStore'

const router = useRouter()
const userStore = useUserStore()
const isLoading = ref(false) // ← Меняем на false чтобы сразу показать контент

onMounted(async () => {
  console.log('App mounted, checking environment...')
  
  // Немедленная проверка без таймаута
  const isWebApp = !!window.Telegram?.WebApp
  console.log('Is Telegram WebApp:', isWebApp)
  
  if (isWebApp) {
    console.log('Initializing Telegram app...')
    window.Telegram.WebApp.expand()
    
    // Пытаемся авторизоваться
    try {
      await userStore.initAuth()
      console.log('Auth successful')
    } catch (error) {
      console.error('Auth failed:', error)
    }
    
    // Если мы на странице только для браузера - уходим
    if (window.location.pathname === '/telegram-only') {
      router.push('/')
    }
  } else {
    console.log('Regular browser detected')
    // Если не в Telegram и не на странице telegram-only - редирект
    if (window.location.pathname !== '/telegram-only') {
      console.log('Redirecting to telegram-only page')
      router.push('/telegram-only')
    }
  }
})
</script>

<template>
  <router-view />
</template>