<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '@/composables/useTelegram'
import { useUserStore } from '@/stores/useUserStore'

const router = useRouter()
const { isWebApp } = useTelegram()
const userStore = useUserStore()
const isChecking = ref(false) // ← Флаг для избежания циклов

// Проверяем при загрузке
onMounted(async () => {
  await checkTelegramAccess()
  
  if (isWebApp.value) {
    await userStore.initAuth()
  }
})

// Следим за изменениями маршрута
watch(() => router.currentRoute.value.path, async (newPath, oldPath) => {
  // Избегаем редиректов на тот же путь
  if (newPath !== oldPath) {
    await checkTelegramAccess()
  }
})

const checkTelegramAccess = async () => {
  if (isChecking.value) return // ← Защита от рекурсии
  isChecking.value = true
  
  const currentPath = router.currentRoute.value.path
  
  // Если не в Telegram и не на странице telegram-only - редирект
  if (!isWebApp.value && currentPath !== '/telegram-only') {
    await router.push('/telegram-only')
  }
  
  // Если в Telegram и на странице telegram-only - редирект на главную
  if (isWebApp.value && currentPath === '/telegram-only') {
    await router.push('/')
  }
  
  isChecking.value = false
}
</script>