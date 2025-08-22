<template>
  <nav class="bottom-nav">
    <button 
      v-for="item in navItems" 
      :key="item.name"
      @click="navigateTo(item.route)"
      class="nav-item"
    >
      <span class="nav-icon">{{ item.icon }}</span>
      <span class="nav-label">{{ item.name }}</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const navItems = [
  { name: 'Главная', route: '/', icon: '🏠' },
  { name: 'Краш', route: '/crash', icon: '🎰' },
  { name: 'Кейсы', route: '/cases', icon: '🎁' },
  { name: 'Топ', route: '/top', icon: '🏆' },
  { name: 'Профиль', route: '/profile', icon: '👤' }
]

const navigateTo = (route: string) => {
  router.push(route)
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: #ffffff;
  border-top: 1px solid #e0e0e0;
  padding: 8px 0;
  height: 60px;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
}

.nav-icon {
  font-size: 20px;
  margin-bottom: 2px;
}

.nav-label {
  font-size: 12px;
}
</style>