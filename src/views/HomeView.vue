<template>
  <div class="home">
    <!-- Простой заголовок -->
    <header class="header">
      <h1>🎮 Play on Stars</h1>
      <p>Баланс: 1 000 ₽</p>
    </header>

    <!-- Контент -->
    <main class="content">
      <div class="card" @click="$router.push('/crash')">
        <h3>🎰 Crash Game</h3>
        <p>Испытай удачу!</p>
      </div>

      <div class="card" @click="$router.push('/cases')">
        <h3>🎁 Кейсы</h3>
        <p>Открой и выиграй!</p>
      </div>
    </main>

    <!-- Навигация -->
    <BottomNavigation />
  </div>
</template>

<script setup lang="ts">
import BottomNavigation from '@/components/layout/BottomNavigation.vue'
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: #ffffff;
  color: #000000;
  padding-bottom: 60px;
}

.header {
  padding: 20px;
  text-align: center;
  background: #f5f5f5;
}

.header h1 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.header p {
  margin: 0;
  font-size: 16px;
  color: #666;
}

.content {
  padding: 20px;
}

.card {
  background: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  cursor: pointer;
  text-align: center;
}

.card:hover {
  border-color: #007bff;
}

.card h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.card p {
  margin: 0;
  color: #666;
  font-size: 14px;
}
</style>