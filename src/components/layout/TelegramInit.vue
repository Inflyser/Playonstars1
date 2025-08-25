<script setup lang="ts">
import { onMounted } from 'vue'
import { useTelegram } from '@/composables/useTelegram'

const { isWebApp, expandApp } = useTelegram()

onMounted(() => {
  if (isWebApp.value) {
    expandApp()
  }
})
</script>

<template>
  <!-- Компонент-невидимка, ничего не рендерит -->
  <div v-show="false"></div>
</template>