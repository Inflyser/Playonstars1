<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/useUserStore'

const router = useRouter()
const userStore = useUserStore()
const isLoading = ref(false)

onMounted(async () => {
  console.log('App mounted, checking Telegram...')
  
  // Ждем немного и проверяем
  setTimeout(() => {
    const isWebApp = !!window.Telegram?.WebApp
    console.log('Is Telegram WebApp:', isWebApp)
    
    if (isWebApp) {
      console.log('Initializing Telegram app...')
      window.Telegram.WebApp.expand()
      
      // Пытаемся авторизоваться
      userStore.initAuth().then(success => {
        console.log('Auth result:', success)
        
        // Если на странице только для браузера - уходим
        if (window.location.pathname === '/telegram-only') {
          router.push('/')
        }
      })
    } else {
      console.log('Regular browser detected')
      // Если не в Telegram и не на странице telegram-only - редирект
      if (window.location.pathname !== '/telegram-only') {
        console.log('Redirecting to telegram-only page')
        router.push('/telegram-only')
      }
    }
  }, 300)
})
</script>

<template>
  <router-view />
</template>