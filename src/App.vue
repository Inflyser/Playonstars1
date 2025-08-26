<template>
  <AppLayout>
    <TelegramInit />
    <RouterView />
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/components/layout/AppLayout.vue';
import TelegramInit from '@/components/layout/TelegramInit.vue';
</script>