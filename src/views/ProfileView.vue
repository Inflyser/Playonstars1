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
          <img :src="userStore.getAvatarUrl" class="user-avatar" />
        </div>

        <!-- Юзернейм -->
        <div class="username1">@{{ userStore.user?.username || userStore.telegramUser?.username }}</div>

        <!-- Имя -->
        <div class="name">{{ userStore.getDisplayName }}</div>
      </div>

      <!-- Нижняя кнопка на всю ширину -->
      <button class="bottom-button" @click="navigateToBalance">
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

    <h3 style="color: white; margin: 15px; text-align: center; font-weight: 400;">Уровни реферальной системы</h3>

    <div class="icons-row">
      <div class="icon-block">
        <img src="@/assets/images/icon1.svg" alt="Icon 1" class="icon">
        <p class="icon-title">0</p>
        <p class="icon-subtext">Всего</p>
        <p class="icon-subtext">рефералов</p>
      </div>
      <div class="icon-block">
        <img src="@/assets/images/icon2.svg" alt="Icon 2" class="icon">
        <p class="icon-title">0</p>
        <p class="icon-subtext">Активность</p>
      </div>
      <div class="icon-block">
        <img src="@/assets/images/icon3.svg" alt="Icon 3" class="icon">
        <p class="icon-title">0</p>
        <p class="icon-subtext">Всего</p>
        <p class="icon-subtext">заработано</p>
      </div>
    </div>


    <p style="color: #6A717B; font-size: 14px; margin: 15px;">
      Приглашайте друзей и получайте процент с чистого дохода от их игры! Чем больше
      активных рефералов, тем выше ваш уровень и процент.
    </p>

    <h2 style="color: white; margin: 30px 15px 15px 15px;">Реферальная ссылка</h2>

    <div class="panel">
      <span class="panel-text">t.me/234233424389348934893</span>
      <button class="copy-button" aria-label="Копировать">
        <img src="@/assets/images/copy-icon.svg" alt="Копировать" class="icon-img">
      </button>
    </div>

    <div class="container">
      <div class="column">
        <div class="text-icon-row">
          <div class="texts">
            <div class="main-text">Доступный баланс</div>
            <div class="value-with-icon">
              <span class="icon-title">0</span>
              <img src="@/assets/images/coin.svg" alt="Иконка 1" class="icon1">
            </div>
          </div>
        </div>
      </div>

      <div class="column">
        <div class="text-icon-row">
          <div class="texts">
            <div class="main-text">Всего потрачено</div>
            <div class="value-with-icon">
              <span class="icon-title">0</span>
              <img src="@/assets/images/coin.svg" alt="Иконка 2" class="icon1">
            </div>
          </div>
        </div>
      </div>

      <div class="column">
        <div class="text-icon-row">
          <div class="texts">
            <div class="main-text">Всего заработано</div>
            <div class="value-with-icon">
              <span class="icon-title">0</span>
              <img src="@/assets/images/coin.svg" alt="Иконка 3" class="icon1">
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="icon-text-row">
      <img src="@/assets/images/depicon.svg" alt="Иконка" class="icon-before" />
      <span class="text-after-icon">Нет доступного баланса</span>
    </div>

    <p style="color: #A2A2A2; text-align: center; font-size: 14px;">Зарабатывай, приглашая друзей!</p>



    <h2 style="color: white; margin: 30px 15px 15px 15px;">История транзакций</h2>

    <div class="icon-wrapper">
      <div class="circle-icon-container">
        <img src="@/assets/images/smallicon.svg" alt="Иконка" class="circle-icon" />
      </div>
    </div>

    <div class="icon-text-row"><span class="text-after-icon">Нет транзакций</span></div>
    <p style="color: #A2A2A2; text-align: center; font-size: 14px; margin: 0 0 40px 0;">Ваши транзакции появятся здесь</p>
    


    <!-- Плавающая панель навигации -->
    <BottomNavigation />
  </div>
</template>


<script setup lang="ts">
import { useUserStore } from '@/stores/useUserStore';
import BottomNavigation from '@/components/layout/BottomNavigation.vue'
import TelegramHeader from '@/components/layout/TelegramHeader.vue'
import TelegramHeader2 from '@/components/layout/TelegramHeader2.vue'
import InfoPanel from '@/components/layout/InfoPanel.vue'

import { useRouter } from 'vue-router'

const userStore = useUserStore();

const router = useRouter()

const navigateToBalance = () => {
  router.push('/balance')
}
</script>



<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(to right, #1B152F, #180A24);
  padding-bottom: 80px;
}

.user-panel {
  margin: 0px 0px 0px 2.5%;
  position: relative;
  width: 95%;
  border-radius: 20px;
  border: 1px solid #5440814f;
  padding: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* Угловые кнопки */
.corner-button {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
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


@media (max-width: 480px) {
  .user-panel {
    width: 95%;
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


.icons-row {
  display: flex;
  justify-content: space-around; /* Равномерные отступы между иконками */
  align-items: flex-start;       /* Выровнять блоки по верхнему краю */
  gap: 0px;                     /* Отступы между элементами */
  padding: 10px 30px 20px 30px;
}

.icon-block {
  display: flex;
  flex-direction: column; /* Содержимое внутри блока — вертикально */
  align-items: center;    /* Центрируем по горизонтали */
  max-width: 150px;       /* Ограничиваем ширину для блока */
}

.icon {
  width: 26px;
  height: 26px;
  margin-bottom: 5px;
}

.icon-title {
  color: white;
  font-weight: bold;
  margin: 5px 0 3px;
  text-align: center;
}

.icon-subtext {
  font-size: 0.9em;
  margin: -2px;
  color: #777;
  text-align: center;
}




.panel {
  margin: 0px 0px 20px 2.5%;
  border: 2px solid #5440814f;
  display: flex;
  align-items: center;
  justify-content: space-between; 
  padding: 5px 15px;
  border-radius: 8px;
  width: 95%;
  box-sizing: border-box;
}

.panel-text {
  user-select: text;
  pointer-events: none;
  color: #A2A2A2;
  font-size: 14px;
}

.copy-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-img {
  width: 16px;
  height: 16px;
}


.container {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
}

.column {
  flex: 1;
  max-width: 30%;
}

.text-icon-row {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.texts {
  display: flex;
  flex-direction: column;
  align-items: center; /* Центрируем содержимое */
  text-align: center;
}

.main-text {
  font-size: 0.9em;
  margin-bottom: 5px; /* Отступ между текстом и значением */
  color: #777;
}

.value-with-icon {
  display: flex;
  align-items: center; /* Выравниваем цифру и иконку по центру */
  gap: 4px; /* Расстояние между цифрой и иконкой */
}

.icon-title {
  font-size: 1.1em;
  color: white;
  font-weight: 600;
  margin: 0;
}

.icon1 {
  width: 14px;
  height: 14px;
}




.icon-text-row {
  display: flex;
  align-items: center;     /* Выравнивание по вертикали */
  justify-content: center; /* ← ЦЕНТРИРОВАНИЕ ПО ГОРИЗОНТАЛИ */
  gap: 8px;
  padding: 5px;
  text-align: center;      /* Дополнительное выравнивание текста */
}

.icon-before {
  width: 15px;
  height: 15px;
  flex-shrink: 0;         /* Чтобы иконка не сжималась */
}

.text-after-icon {
  color: white;
  font-size: 16px;
  font-weight: 500;
}




.icon-wrapper {
  margin: 40px 0px 0px 0px;
  display: flex;
  justify-content: center; /* Центрирование по горизонтали */
  align-items: center;     /* Центрирование по вертикали */
  width: 100%;
  height: 100%;            /* Занимает всю высоту родителя */
}

.circle-icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 70px;
  height: 70px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  backdrop-filter: blur(5px);
  /* margin: 0 auto; ← альтернативный способ центрирования */
}

.circle-icon {
  width: 30px;
  height: 30px;
  object-fit: contain;
  filter: brightness(1.2);
}
</style>