<template>
  <div class="home">
    <TelegramHeader />




    <!-- Плавающая панель навигации -->
    <BottomNavigation />
  </div>
</template>


<script setup lang="ts">
import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import TelegramHeader from '@/components/layout/TelegramHeader.vue'
</script>


<style scoped>
.home {
  min-height: 100vh;
  background: #180A24;
  padding-bottom: 80px;
}
</style>