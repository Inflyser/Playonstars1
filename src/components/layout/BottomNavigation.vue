<template>
  <nav class="bottom-navigation">
    <button 
      v-for="item in navItems" 
      :key="item.name"
      :class="['nav-item', { active: currentRoute === item.route }]"
      @click="navigateTo(item.route)"
    >
      <img :src="item.image" :alt="item.name" class="nav-image" />
      <span class="nav-label">{{ item.name }}</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// Импортируем изображения ПРАВИЛЬНО
import homeIcon from '@/assets/icons/nav-home.png'
import crashIcon from '@/assets/icons/nav-crash.png'
import casesIcon from '@/assets/icons/nav-cases.png'
import topIcon from '@/assets/icons/nav-top.png'
import profileIcon from '@/assets/icons/nav-profile.png'

const router = useRouter()
const currentRoute = ref(router.currentRoute.value.path)

const navItems = [
  { 
    name: 'Главная', 
    route: '/', 
    image: homeIcon  // Используем импортированное изображение
  },
  { 
    name: 'Краш', 
    route: '/crash', 
    image: crashIcon
  },
  { 
    name: 'Кейсы', 
    route: '/cases', 
    image: casesIcon
  },
  { 
    name: 'Топ', 
    route: '/top', 
    image: topIcon
  },
  { 
    name: 'Профиль', 
    route: '/profile', 
    image: profileIcon
  }
]

const navigateTo = (route: string) => {
  router.push(route)
  currentRoute.value = route
}
</script>

<style scoped>
.bottom-navigation {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  background: rgba(4, 6, 18, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 25px;
  padding: 12px 16px;
  height: 70px;
  min-width: 320px;
  max-width: 500px;
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  z-index: 1000;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  padding: 8px 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 15px;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 6px;
  height: 6px;
  background: #00ff88;
  border-radius: 50%;
  box-shadow: 0 0 10px #00ff88;
}

.nav-image {
  width: 24px;
  height: 24px;
  object-fit: contain;
  margin-bottom: 4px;
  transition: transform 0.3s ease;
}

.nav-item.active .nav-image {
  transform: scale(1.1);
  filter: brightness(1.2);
}

.nav-label {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
}

.nav-item.active .nav-label {
  color: #ffffff;
  font-weight: 600;
}

/* Анимация при наведении */
.nav-item:hover .nav-image {
  transform: translateY(-2px);
}

.nav-item:hover .nav-label {
  color: #ffffff;
}

/* Адаптивность */
@media (max-width: 380px) {
  .bottom-navigation {
    min-width: 300px;
    padding: 10px 12px;
    height: 65px;
  }
  
  .nav-image {
    width: 22px;
    height: 22px;
  }
  
  .nav-label {
    font-size: 10px;
  }
}

@media (max-width: 340px) {
  .bottom-navigation {
    min-width: 280px;
    padding: 8px 10px;
    height: 60px;
  }
  
  .nav-image {
    width: 20px;
    height: 20px;
  }
  
  .nav-label {
    font-size: 9px;
  }
}
</style>