<template>
  <nav class="bottom-navigation">
    <button 
      v-for="item in navItems" 
      :key="item.name"
      :class="['nav-item', { active: currentRoute === item.route }]"
      @click="navigateTo(item.route)"
    >
      <span class="nav-icon">{{ item.icon }}</span>
      <span class="nav-label">{{ item.name }}</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentRoute = ref(router.currentRoute.value.path)

const navItems = [
  { name: 'Главная', route: '/', icon: '🏠' },
  { name: 'Краш', route: '/crash', icon: '🎰' },
  { name: 'Кейсы', route: '/cases', icon: '🎁' },
  { name: 'Топ', route: '/top', icon: '🏆' },
  { name: 'Профиль', route: '/profile', icon: '👤' }
]

const navigateTo = (route: string) => {
  router.push(route)
  currentRoute.value = route
}
</script>

<style scoped>
.bottom-navigation {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 8px 0;
  height: 70px;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-item.active {
  color: #667eea;
}

.nav-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.nav-label {
  font-size: 12px;
  font-weight: 500;
}
</style>