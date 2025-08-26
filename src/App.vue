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