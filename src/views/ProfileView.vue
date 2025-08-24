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
            <div class="sub-text">0</div>
          </div>
          <img src="@/assets/images/coin.svg" alt="Иконка 1" class="icon1">
        </div>
      </div>
      <div class="column">
        <div class="text-icon-row">
          <div class="texts">
            <div class="main-text">Всего потрачено</div>
            <div class="sub-text">0</div>
          </div>
          <img src="@/assets/images/coin.svg" alt="Иконка 2" class="icon1">
        </div>
      </div>
      <div class="column">
        <div class="text-icon-row">
          <div class="texts">
            <div class="main-text">Всего заработано</div>
            <div class="sub-text">0</div>
          </div>
          <img src="@/assets/images/coin.svg" alt="Иконка 3" class="icon1">
        </div>
      </div>
    </div>



    <h2 style="color: white; margin: 30px 15px 15px 15px;">История транзакций</h2>


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
  flex: 1;        /* равная ширина колонок */
  max-width: 30%; /* чтобы не растягивались слишком */
}

.text-icon-row {
  display: flex;
  align-items: center;   /* выравнивание по вертикали */
  justify-content: flex-start;
}

.texts {
  display: flex;
  flex-direction: column;
}

.main-text {
  font-size: 0.9em;
  margin: -2px;
  color: #777;
  text-align: center;
}

.sub-text {
  font-size: 0.9em;
  color: white;
  text-align: center;
  font-weight: 600;
  margin: 0;
}

.icon1 {
  width: 18px;
  height: 18px;

}
</style>