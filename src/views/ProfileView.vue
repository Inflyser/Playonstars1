<template>
  <div class="home">
    <TelegramHeader />
    <TelegramHeader2 />
    <div class="user-panel">
      <!-- Верхние угловые кнопки -->
      <button class="corner-button top-left">
        <img src="@/assets/icons/settings-icon.svg" alt="Настройки" class="corner-icon" />
      </button>

      <button class="corner-button top-right">
        <img src="@/assets/icons/close-icon.svg" alt="Закрыть" class="corner-icon" />
      </button>

      <!-- Центральный контент -->
      <div class="panel-content">
        <!-- Аватарка -->
        <div class="avatar-container">
          <img src="@/assets/images/avatar.jpg" alt="Аватар" class="user-avatar" />
        </div>

        <!-- Юзернейм -->
        <div class="username1">@username</div>

        <!-- Имя -->
        <div class="name">Иван Иванов</div>
      </div>

      <!-- Нижняя кнопка на всю ширину -->
      <button class="bottom-button">
        <img src="@/assets/images/depicon.svg" alt="Кошелек" class="button-icon" />
        <span>Пополнить</span>
      </button>
    </div>

    <h2 style="color: white; margin: 15px;">Рефералы</h2>

    <InfoPanel
      title="Новичек"
      iconText="5% от чистого дохода"
      leftText="Бронза"
      rightText="15%"
      :progress="15"
    />
    <!-- Плавающая панель навигации -->
    <BottomNavigation />
  </div>
</template>


<script setup lang="ts">
import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import TelegramHeader from '@/components/layout/TelegramHeader.vue'
import TelegramHeader2 from '@/components/layout/TelegramHeader2.vue'
import InfoPanel from '@/components/layout/InfoPanel.vue'
</script>


<style scoped>
.home {
  min-height: 100vh;
  background: #180A24;
  padding-bottom: 80px;
}

.user-panel {
  position: relative;
  width: 90%;
  height: 300px;
  margin: 10px;
  background: linear-gradient(135deg, #1B152F, #180A24);
  border-radius: 20px;
  border: 1px solid #2A2642;
  padding: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* Угловые кнопки */
.corner-button {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid #2A2642;
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
}

.corner-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.top-left {
  top: 12px;
  left: 12px;
}

.top-right {
  top: 12px;
  right: 12px;
}

.corner-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

/* Центральный контент */
.panel-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0 20px 0;
}

.avatar-container {
  margin-bottom: 16px;
}

.user-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: -10px;
}

.username1 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 0px;
  color: #A2A2A2;
}

.name {
  font-size: 18px;
  color: white;
  font-weight: bold;
}

/* Нижняя кнопка */
.bottom-button {
  background: linear-gradient(135deg, #00A6FC, #0088CC);
  color: white;
  border: none;
  border-radius: 18px 18px 18px 18px;
  padding: 16px;
  margin: 0 -15px -15px -15px; /* Растягиваем на всю ширину */
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
}


.button-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
}

/* Адаптивность */
@media (max-width: 768px) {
  .user-panel {
    width: 90%;
    max-width: 320px;
    min-height: 240px;
  }
  
  .user-avatar {
    width: 72px;
    height: 72px;
  }
  
  .username {
    font-size: 13px;
  }
  
  .name {
    font-size: 16px;
  }
  
  .bottom-button {
    padding: 14px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .user-panel {
    width: 95%;
    max-width: 500px;
    min-height: 220px;
    min-height: 50%;
    padding: 15px;
  }
  
  .user-avatar {
    width: 80px;
    height: 80px;
  }
  
  .corner-button {
    width: 28px;
    height: 28px;
  }
  
  .corner-icon {
    width: 14px;
    height: 14px;
  }
  
  .panel-content {
    padding: 30px 0 15px 0;
  }
}
</style>