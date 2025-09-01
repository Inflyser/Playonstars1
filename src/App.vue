<template>
  <TelegramInit />
</template>

<script setup lang="ts">
// НИКАКОЙ логики инициализации здесь!
// Все переносим в TelegramInit.vue
</script>

<script lang="ts">
import TelegramInit from '@/components/layout/TelegramInit.vue';

export default {
  components: {
    TelegramInit
  }
}
</script>