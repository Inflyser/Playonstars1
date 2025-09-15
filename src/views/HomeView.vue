<template>
  <div class="home">
    <TelegramHeader />
    <TelegramHeader2 />

    <!-- Основной контент - две большие кнопки -->
    <main class="main-content">
      <div class="action-cards">
        <!-- Space Monkey карточка -->
        <button class="action-card space-monkey-card" @click="PageCrash">
          <!-- Слой 4: Цветной фон -->
          <div class="card-color-bg"></div>

          <!-- Слой 3: Фоновая картинка -->
          <img src="@/assets/images/space-monkey-bg.svg" alt="Фон" class="card-bg-image" />

          <!-- Слой 2: Основная картинка -->
          <img src="@/assets/images/space-monkey-character.svg" alt="Space Monkey" class="card-main-image" />

          <!-- Слой 1: Текст -->
          <div class="card-content">
            <h3>{{ t('logo_place_bet') }}</h3>
            <p>{{ t('place_bet') }}</p>
          </div>
        </button>
      
        <!-- PvP арена карточка -->
        <button class="action-card pvp-arena-card" @click="PagePvp">
          <!-- Слой 4: Цветной фон -->
          <div class="card-color-bg"></div>

          <!-- Слой 3: Фоновая картинка -->
          <img src="@/assets/images/pvp-arena-bg.svg" alt="Фон" class="card-bg-image" />

          <!-- Слой 2: Основная картинка -->
          <img src="@/assets/images/pvp-arena-character.svg" alt="PvP Арена" class="card-main-image" />

          <!-- Слой 1: Текст -->
          <div class="card-content">
            <h3>{{ t('logo_place_bet1') }}</h3>
            <p>{{ t('place_bet1') }}</p>
          </div>
        </button>

        <button class="action-card admin-penel-card" @click="goToAdmin">
          <!-- Слой 4: Цветной фон -->
          <div class="card-color-bg"></div>

          <!-- Слой 1: Текст -->
          <div class="card-content">
            <h3>Админ панель ⚙️</h3>
         
          </div>
        </button>
      </div>
    </main>

    <!-- Плавающая панель навигации -->
    <BottomNavigation />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/useUserStore'
import { computed, ref, onMounted } from 'vue'
import { api } from '@/services/api'

import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import TelegramHeader from '@/components/layout/TelegramHeader.vue'
import TelegramHeader2 from '@/components/layout/TelegramHeader2.vue'
import { useRouter } from 'vue-router'

const { t, locale } = useI18n()
const userStore = useUserStore()
const router = useRouter()

const adminStatus = ref(false)

// Комбинированная проверка - из localStorage и из API
const showAdminButton = computed(() => {
  return localStorage.getItem('admin_token') === 'authenticated' || adminStatus.value
})

// Проверяем статус админа при загрузке
onMounted(async () => {
  await checkAdminStatus()
})

const checkAdminStatus = async () => {
  try {
    const response = await api.get('/api/admin/check-status')
    adminStatus.value = response.data.isAdmin
    
    // Если админ - сохраняем в localStorage
    if (adminStatus.value) {
      localStorage.setItem('admin_token', 'authenticated')
    }
  } catch (error) {
    console.error('Ошибка проверки админ-статуса:', error)
    adminStatus.value = false
  }
}

const goToAdmin = () => {
  router.push('/admin')
}

const PageCrash = () => {
  router.push('/crash')
}

const PagePvp = () => {
  router.push('/pvp')
}

const changeLanguage = (lang: string) => {
  locale.value = lang
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(to right, #1B152F, #180A24);
  padding-bottom: 80px;
}

.admin-btn {
  background: linear-gradient(135deg, #ff4757, #ff3742);
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
}

.main-content {
  padding: 0 16px;
}

.action-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.action-card {
  position: relative;
  border-radius: 20px;
  overflow: hidden; 
  cursor: pointer;
  height: 150px;
  transition: all 0.3s ease;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
}

/* Слой 4: Цветной фон */
.card-color-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.space-monkey-card .card-color-bg {
  background: #00A051; /* Синий градиент */
}

.pvp-arena-card .card-color-bg {
  background: #F8A820 /* Красный градиент */
}

.admin-penel-card .card-color-bg {
  background: #ff5133 /* Красный градиент */
}

/* Слой 3: Фоновая картинка */
.card-bg-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 2;
}

/* Слой 2: Основная картинка */
.card-main-image {
  position: absolute;
  right: -10px; /* Выступает за правый край */
  bottom: -10px; /* Выступает за нижний край */
  height: 120%; /* Значительно больше кнопки */
  width: auto;
  object-fit: contain;
  z-index: 3;
  transition: all 0.3s ease;
  filter: drop-shadow(0 5px 20px rgba(0, 0, 0, 0.6));
  transform-origin: right bottom; /* Точка трансформации */
}


/* Слой 1: Текст */
.card-content {
  position: relative;
  z-index: 4;
  padding: 15px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: left;
}

.card-content h3 {
  margin: 35px 0 12px 0;
  font-size: 30px;
  font-weight: bold;
  color: #ffffff;
}

.card-content p {
  margin: 0px 0px 5px 0px;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  max-width: 60%;
  line-height: 1;
}

@media (max-width: 480px) {
  .action-card {
    height: 150px;
  }
  
  .card-content {
    padding: 20px;
  }
  
  .card-content h3 {
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  .card-content p {
    font-size: 14px;
    max-width: 70%;
  }
  
  .card-main-image {
    right: 15px;
    bottom: 15px;
    height: 70%;
  }
}

@media (max-width: 480px) {
  .card-main-image {
    height: 120%;
    right: 0px;
    bottom: -32px;
  }
}
</style>