<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTelegram } from '@/composables/useTelegram'
import { useUserStore } from '@/stores/useUserStore'

const router = useRouter()
const { isWebApp } = useTelegram()
const userStore = useUserStore()

// Проверяем при загрузке
onMounted(async () => {
  checkTelegramAccess()
  
  if (isWebApp.value) {
    await userStore.initAuth()
  }
})

// Следим за изменениями маршрута
watch(() => router.currentRoute.value.path, (newPath) => {
  checkTelegramAccess()
})

const checkTelegramAccess = () => {
  // Если не в Telegram и не на странице telegram-only - редирект
  if (!isWebApp.value && router.currentRoute.value.path !== '/telegram-only') {
    router.push('/telegram-only')
    return
  }
  
  // Если в Telegram и на странице telegram-only - редирект на главную
  if (isWebApp.value && router.currentRoute.value.path === '/telegram-only') {
    router.push('/')
    return
  }
}
</script>