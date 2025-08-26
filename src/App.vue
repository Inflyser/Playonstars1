<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Простая функция для теста запроса
const testBackend = async () => {
  try {
    console.log('Testing backend connection...')
    const response = await fetch('https://playonstars.onrender.com/api/test')
    const data = await response.text()
    console.log('Backend response:', data)
  } catch (error) {
    console.error('Backend error:', error)
  }
}

onMounted(() => {
  console.log('App mounted, checking environment...')
  
  // Тестируем бекенд
  testBackend()
  
  const isTelegram = !!window.Telegram?.WebApp
  console.log('Is Telegram:', isTelegram)
  
  if (isTelegram) {
    console.log('We are in Telegram!')
    if (window.location.pathname === '/telegram-only') {
      router.push('/')
    }
  } else {
    console.log('We are in browser')
    if (window.location.pathname !== '/telegram-only') {
      router.push('/telegram-only')
    }
  }
})
</script>

<template>
  <router-view />
</template>