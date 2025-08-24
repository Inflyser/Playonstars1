<template>
  <div class="home">
    <TelegramHeader />

    <h1 style="color: #ffffff; margin: 10px;">Страница в разработке</h1>



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
  background: linear-gradient(to right, #1B152F, #180A24);
  padding-bottom: 80px;
}
</style>